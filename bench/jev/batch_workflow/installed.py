#!/usr/bin/env python3
"""Exercise a disposable installed optional-Jev workflow with retained observations.

No provider credentials are read and no new inference is admitted. This is current
binary lifecycle acceptance, not a new model-quality or transport measurement.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

if __package__:
    from . import replay as retained
    from . import primitives
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import replay as retained
    import primitives


def require(ok, label):
    if not ok:
        raise ValueError(label)


def private_copy(source, destination):
    destination.mkdir(mode=0o700)
    for path in sorted(source.iterdir()):
        require(path.is_file() and not path.is_symlink(), 'unsafe retained job')
        target = destination / path.name
        with target.open('xb') as out:
            out.write(path.read_bytes())
        target.chmod(0o600)


def inventory(path):
    return {p.name: retained.sha(p) for p in path.iterdir() if p.name != '.lock'}


def run(binary, output):
    binary = binary.resolve(strict=True)
    require(binary.is_file(), 'binary must be a file')
    require(not os.path.lexists(output), 'output exists')
    output.mkdir(mode=0o700)
    output = output.resolve()
    home = output / 'private home'
    home.mkdir(mode=0o700)
    state = output / 'private state'
    config = output / 'config.toml'
    installed = home / '.claude/skills/azdaja/azdaja'
    key_name = 'AZDAJA_INSTALL_ACCEPTANCE_KEY'
    first = 'apikey_SYNTHETIC_INSTALL_ONLY_0123456789abcdef'
    second = 'apikey_SYNTHETIC_ENV_ONLY_fedcba9876543210'
    env = {'HOME': str(home), 'PATH': '/usr/bin:/bin',
           'AZDAJA_HOME': str(state), 'AZDAJA_CONFIG': str(config)}
    receipt = {'schema': 'azdaja.batch.installed_acceptance.v1', 'status': 'running',
               'binary_sha256': retained.sha(binary), 'new_provider_calls': 0,
               'scope': 'current private installation, optionality, retained-job replay and export',
               'synthetic_credentials_only': True, 'checks': []}
    session = None

    def call(label, args, expected=0, data=None, overrides=None, executable=None):
        start = time.monotonic()
        p = subprocess.run([str(executable or installed)] + [str(a) for a in args],
                           input=data, text=True, capture_output=True, timeout=30,
                           cwd=output, env=dict(env, **(overrides or {})))
        require(first not in p.stdout + p.stderr and second not in p.stdout + p.stderr,
                label + ': synthetic secret leaked')
        receipt['checks'].append({'name': label, 'exit': p.returncode,
                                  'seconds': time.monotonic() - start,
                                  'stdout_sha256': hashlib.sha256(p.stdout.encode()).hexdigest(),
                                  'stderr_sha256': hashlib.sha256(p.stderr.encode()).hexdigest()})
        require(p.returncode == expected, label + ': unexpected exit')
        return p.stdout

    def jcall(label, args, **kwargs):
        return json.loads(call(label, args, **kwargs))

    def configure(judge):
        lines = ['sub_llm_cmd="/usr/bin/false"', '[judge]']
        for k, v in judge.items():
            if v is not None:
                lines.append(k + '=' + json.dumps(v))
        config.write_text('\n'.join(lines) + '\n')

    try:
        configure({'enabled': False, 'key_env': key_name})
        call('install-private', ['install', 'claude'], executable=binary)
        require(retained.sha(installed) == receipt['binary_sha256'], 'installed bytes differ')
        # A fresh root distinguishes discovery from installer initialization.
        state = output / 'fresh state'
        env['AZDAJA_HOME'] = str(state)
        caps = jcall('static-discovery', ['doctor', '--caps'])
        receipt['typesafe_compiled'] = caps['typed_judgments']['typesafe_compiled']
        require(not state.exists() and not caps['typed_judgments']['credentials_checked'],
                'discovery probed or initialized credentials')
        before = config.read_bytes()
        jcall('stdin-attach', ['jev', 'attach', '--stdin', '--key-env', key_name], data=first)
        key_path = state / 'credentials' / (hashlib.sha256(key_name.encode()).hexdigest() + '.key')
        require(config.read_bytes() == before, 'attachment changed opt-in')
        require(stat.S_IMODE(key_path.stat().st_mode) == 0o600, 'unsafe credential mode')
        status = jcall('restart-status', ['jev', 'status', '--key-env', key_name])
        require(status['source'] == 'attached_file', 'attachment not persistent')
        status = jcall('environment-precedence', ['jev', 'status', '--key-env', key_name],
                       overrides={key_name: second})
        require(status['source'] == 'environment' and status['fingerprint'] == hashlib.sha256(second.encode()).hexdigest()[:12],
                'wrong precedence')
        doctor = jcall('local-readiness', ['doctor', 'jev'])
        require(doctor['configured_enabled'] is False and doctor['provider_readiness_checked'] is False,
                'attachment enabled or probed provider')
        guarded = output / 'guarded.jsonl'
        guarded.write_text(json.dumps({'id': 'guard', 'state': first + ' ' + second,
                          'questions': {'q': {'type': 'noul', 'instructions': 'Is text supplied?'}}}) + '\n')
        check = jcall('attached-offline-plan', ['jev', 'batch', '--input', guarded])
        require(check['provider_requests'] == 0 and not check['execution_enabled'], 'preflight executed')
        call('attached-still-disabled', ['jev', 'batch', '--input', guarded,
                       '--execute', '--output', output/'forbidden-job', '--max-requests', '1',
                       '--max-input-tokens', '100', '--max-seconds', '10'], expected=2)
        require(not (output/'forbidden-job').exists(), 'disabled batch created a job')
        # Even an opt-in regression hits the native leakage guard, not a provider.
        session = call('ordinary-session-start', ['start']).strip()
        call('ordinary-session-exec', ['exec', session], data='FINAL(6 * 7)\n')
        require(jcall('ordinary-session-final', ['final', session]) == 42, 'ordinary workflow changed')
        call('ordinary-session-kill', ['kill', session])
        session = None
        jcall('detach', ['jev', 'detach', '--key-env', key_name])
        require(not key_path.exists(), 'attachment survived detach')
        require(jcall('detached-status', ['jev', 'status', '--key-env', key_name])['source'] == 'absent',
                'detached key remains active')

        replay = retained.replay(output/'reconstructed')
        manifest = retained.load(retained.RESULTS/'job/manifest.json')
        configure(manifest['binding']['config'])
        private_copy(retained.RESULTS/'job', output/'completed-job')
        job = output/'completed-job'
        before = inventory(job)
        limits = manifest['binding']['limits']
        args = ['jev', 'batch', '--input', output/'reconstructed/plan/plan.jsonl', '--execute', '--resume',
                '--output', job, '--max-requests', str(limits['max_requests']),
                '--max-input-tokens', str(limits['max_input_tokens']), '--max-seconds', str(limits['max_seconds'])]
        completed = jcall('completed-no-key-resume', args)
        require(completed['status'] == 'completed' and completed['new_requests'] == 0 and
                completed['records']['completed'] == 138 and before == inventory(job), 'completed replay changed work')
        private_copy(retained.RESULTS/'job', output/'ambiguous-job')
        ambiguous = output/'ambiguous-job'
        (ambiguous/'000137.result.json').unlink()
        args[args.index('--output') + 1] = ambiguous
        stopped = jcall('ambiguous-no-key-resume', args, expected=1)
        require(stopped['stop_reason'] == 'ambiguous_inflight_request' and stopped['new_requests'] == 0 and
                stopped['records']['completed'] == 137, 'ambiguous job retried or miscounted')
        # This is a labeled synthetic failure envelope, not a new provider result.
        # Native injected-transport tests separately exercise creation of failures.
        private_copy(retained.RESULTS/'job', output/'synthetic-failed-job')
        failed = output/'synthetic-failed-job'
        path = failed/'000137.result.json'
        record = retained.load(path)
        record.update(status='failed', observation=None, failure={'kind': 'http_status', 'status': 429})
        record['stats'].update(successful_requests=0, failed_attempts=1, cached_requests=0, poisoned=True)
        path.write_text(json.dumps(record))
        args[args.index('--output') + 1] = failed
        failure = jcall('synthetic-failure-no-key-resume', args, expected=1)
        require(failure['last_failure'] == record['failure'] and failure['new_requests'] == 0 and
                failure['records']['completed'] == 137, 'safe failure diagnostic lost')
        record.pop('failure')
        path.write_text(json.dumps(record))
        legacy = jcall('legacy-failure-no-key-resume', args, expected=1)
        require(legacy['last_failure'] == {'kind': 'not_recorded'} and legacy['new_requests'] == 0,
                'legacy failure invented a cause or retried')
        record['failure'] = {'kind': 'transport', 'unexpected': 'not permitted'}
        path.write_text(json.dumps(record))
        call('malformed-diagnostic-refused', args, expected=2)
        spec = importlib.util.spec_from_file_location('installed_batch_export', retained.EXAMPLE)
        example = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(example)
        example.report(output/'reconstructed/plan', job, output/'review.jsonl')
        require(retained.sha(output/'review.jsonl') == replay['review_sha256'], 'native/export boundary changed')
        example.report(output/'reconstructed/plan', ambiguous, output/'partial-review.jsonl')
        partial = [json.loads(line) for line in (output/'partial-review.jsonl').read_text().splitlines()]
        require(len(partial) == 138 and sum(row['status'] == 'completed' for row in partial) == 137,
                'partial export lost source coverage')
        receipt['primitive_replay'] = primitives.native_replay(installed)
        receipt['checks'].append({'name': 'three-primitives-no-key-resume', 'exit': 0,
                                  'new_requests': 0, 'completed': 1, 'questions': 3})
        queue = retained.ROOT / 'examples/jev_review_queue.py'
        for label, source_job in [('completed-review-queue', job), ('partial-review-queue', ambiguous)]:
            target = output / (label + '.html')
            call(label, [queue, '--plan', output/'reconstructed/plan',
                         '--job', source_job, '--output', target], executable=Path(sys.executable))
            require(target.is_file() and stat.S_IMODE(target.stat().st_mode) == 0o600,
                    'review queue missing or unsafe')
            receipt.setdefault('review_queues', {})[label] = retained.sha(target)
        call('uninstall-private', ['uninstall', 'claude'])
        require(not installed.exists(), 'uninstall retained private binary')
        receipt.update(status='passed', completed_windows=138, partial_windows=138,
                       failure_fixture_is_synthetic=True,
                       completed_resume_new_requests=0, ambiguous_resume_new_requests=0,
                       review_sha256=replay['review_sha256'], source_bytes=replay['source_bytes'],
                       private_install_removed=True, synthetic_attachment_removed=True)
    except BaseException:
        receipt['status'] = 'failed'
        raise
    finally:
        # Only artifacts created under this exclusively-owned output are cleaned.
        cleanup = []
        if session and installed.exists():
            cleanup.append(['kill', session])
        if installed.exists():
            cleanup.extend([['jev', 'detach', '--key-env', key_name], ['uninstall', 'claude']])
        for args in cleanup:
            try:
                p = subprocess.run([str(installed)] + args, env=env, cwd=output,
                                   capture_output=True, timeout=30)
                ok = p.returncode == 0
            except (OSError, subprocess.SubprocessError):
                ok = False
            receipt.setdefault('failure_cleanup', []).append({'operation': args[0], 'completed': ok})
            if not ok:
                receipt['status'] = 'failed'
        with (output/'receipt.json').open('x') as f:
            json.dump(receipt, f, sort_keys=True, indent=2)
            f.write('\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = run(args.binary, args.output)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('error: installed acceptance failed (' + type(error).__name__ + ')', file=sys.stderr)
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
