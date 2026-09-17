"""Actual private-install credential acceptance. Synthetic keys only, no inference."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import time

p = argparse.ArgumentParser()
p.add_argument('--azdaja', required=True)
p.add_argument('--output', required=True)
a = p.parse_args()
binary = Path(a.azdaja).resolve(strict=True)
out = Path(a.output)
out.mkdir(exist_ok=False)
home = out / 'private home with spaces'
home.mkdir()
state = out / 'credential state'
config = out / 'config.toml'
name = 'AZDAJA_INSTALLED_TEST_CREDENTIAL'
first = 'apikey_' + 'SYNTHETIC_INSTALLED_FIRST_0123456789abcdef'
second = 'apikey_' + 'SYNTHETIC_INSTALLED_SECOND_fedcba9876543210'
env = {'PATH': '/usr/bin:/bin', 'HOME': str(home), 'AZDAJA_HOME': str(state), 'AZDAJA_CONFIG': str(config)}
record = {'schema': 'azdaja.installed_credential_acceptance.v1', 'status': 'running', 'provider_calls': 0,
          'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(), 'synthetic_credentials_only': True, 'checks': []}
installed = home / '.claude/skills/azdaja/azdaja'
sid = None

def save():
    (out / 'receipt.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')

def call(label, args, data=None, overrides=None, expected=0, executable=None):
    started = time.monotonic()
    result = subprocess.run([str(executable or installed)] + args, input=data, text=True,
                            env=dict(env, **(overrides or {})), cwd=out, capture_output=True, timeout=30)
    assert first not in result.stdout + result.stderr and second not in result.stdout + result.stderr
    assert result.returncode == expected, (label, result.returncode, result.stderr[:500])
    raw = result.stdout + '\n[stderr]\n' + result.stderr
    (out / (label + '.log')).write_text(raw)
    record['checks'].append({'name': label, 'exit': result.returncode, 'seconds': time.monotonic() - started,
                             'log_sha256': hashlib.sha256(raw.encode()).hexdigest()})
    save()
    return result.stdout

def jcall(label, args, **kwargs):
    return json.loads(call(label, args, **kwargs))

def configure(enabled):
    config.write_text('sub_llm_cmd="/usr/bin/false"\n[judge]\nenabled=' + str(enabled).lower() + '\nkey_env="' + name + '"\n')

try:
    configure(False)
    call('private-install', ['install', 'claude'], executable=binary)
    assert installed.is_file() and hashlib.sha256(installed.read_bytes()).hexdigest() == record['binary_sha256']
    # Installation may initialize its own state. Select a fresh root to test discovery without initialization.
    state = out / 'fresh credential state'
    env['AZDAJA_HOME'] = str(state)
    caps = jcall('caps-before-attachment', ['doctor', '--caps'])
    assert caps['typed_judgments']['typesafe_compiled'] is True
    assert caps['typed_judgments']['credentials_checked'] is False and not state.exists()
    absent = jcall('status-before-attachment', ['jev', 'status', '--key-env', name])
    assert absent['source'] == 'absent' and not state.exists()
    config_bytes = config.read_bytes()
    jcall('attach-from-stdin', ['jev', 'attach', '--stdin', '--key-env', name], data=first)
    keyfile = state / 'credentials' / (hashlib.sha256(name.encode()).hexdigest() + '.key')
    assert keyfile.read_text() == first and config.read_bytes() == config_bytes
    for path, mode in [(state, 0o700), (state/'credentials', 0o700), (keyfile, 0o600)]:
        assert stat.S_IMODE(path.stat().st_mode) == mode
    current = jcall('fresh-process-persistent-status', ['jev', 'status', '--key-env', name])
    assert current['source'] == 'attached_file' and current['fingerprint'] == hashlib.sha256(first.encode()).hexdigest()[:12]
    override = jcall('environment-wins', ['jev', 'status', '--key-env', name], overrides={name: second})
    assert override['source'] == 'environment' and override['fingerprint'] == hashlib.sha256(second.encode()).hexdigest()[:12]
    call('replacement-needs-opt-in', ['jev', 'attach', '--stdin', '--key-env', name], data=second, expected=2)
    assert keyfile.read_text() == first
    jcall('explicit-replacement', ['jev', 'attach', '--stdin', '--replace', '--key-env', name], data=second)
    assert keyfile.read_text() == second
    doctor = jcall('doctor-local-attachment', ['doctor', 'jev'])
    assert doctor['source'] == 'attached_file' and doctor['configured_enabled'] is False
    assert doctor['provider_readiness_checked'] is False
    sid = call('start-persistent-session', ['start']).strip()
    # All valid synthetic credentials are in the request state. Even an activation/precedence
    # regression must hit the credential-leak guard instead of contacting the fixed provider.
    code = ('error = None\ntry:\n    judge_many(' + repr(first+' '+second) + ', {"q":{"type":"noul","instructions":"Is it present?"}})\n'
            'except Exception as e:\n    error = str(e)\nFINAL({"error":error,"stats":judge_stats()})\n')
    cases = [('default-disabled', False, {}, 'judge_many is disabled; the host must explicitly enable [judge]'),
             ('attached-resolution-before-transport', True, {}, 'judge: credential leakage refused'),
             ('invalid-environment-no-fallback', True, {name: 'invalid value'}, 'judge: invalid credential syntax'),
             ('environment-resolution-before-transport', True, {name: first}, 'judge: credential leakage refused')]
    for label, enabled, overrides, expected_error in cases:
        configure(enabled)
        call(label+'-exec', ['exec', sid], data=code, overrides=overrides)
        result = jcall(label+'-final', ['final', sid])
        assert expected_error in result['error'] and result['stats']['attempts'] == 0
    call('kill-session', ['kill', sid])
    sid = None
    assert jcall('detach-persistent-file', ['jev', 'detach', '--key-env', name])['removed'] is True
    assert not keyfile.exists()
    assert jcall('status-after-detach', ['jev', 'status', '--key-env', name])['source'] == 'absent'
    assert jcall('idempotent-detach', ['jev', 'detach', '--key-env', name])['removed'] is False
    call('private-uninstall', ['uninstall', 'claude'])
    assert not installed.exists()
    assert not list((state/'credentials').glob('*.key')) and not list((state/'credentials').glob('.pending-*'))
    record.update(status='passed', private_install_removed=True, synthetic_attachment_removed=True,
                  persistent_restart_verified=True, private_file_modes_verified=True, config_unchanged_by_attach=True,
                  native_transport_attempts=0)
except BaseException as error:
    record.update(status='failed', failure=type(error).__name__+': '+str(error))
    raise
finally:
    if sid and installed.exists():
        subprocess.run([str(installed), 'kill', sid], env=env, cwd=out, capture_output=True, timeout=30)
    save()
print(json.dumps({k: record[k] for k in ('status','provider_calls','native_transport_attempts','binary_sha256')}))
