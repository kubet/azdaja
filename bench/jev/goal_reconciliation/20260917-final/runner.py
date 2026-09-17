"""One bounded, provider-free reconciliation of CLOSED Jev campaigns."""
from pathlib import Path
import email.policy
from email.parser import BytesParser
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path('/Users/vukasinkubet/dev/azdaja')
SCRATCH = Path(os.environ['JCODE_SCRATCH_DIR'])
OUT = Path(tempfile.mkdtemp(prefix='jev-final-goal-reconciliation-', dir=SCRATCH))
HOME = OUT / 'isolated-home'
HOME.mkdir(mode=0o700)
BINARY = SCRATCH / 'jev-ingest-native-e75d836-azdaja'
EXPECTED = '13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32'
ENV = {'PATH': os.environ['PATH'], 'HOME': str(HOME), 'JCODE_SCRATCH_DIR': str(SCRATCH),
       'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': str(ROOT), 'AZDAJA_BINARY': str(BINARY)}
sha = lambda raw: hashlib.sha256(raw).hexdigest()
load = lambda p: json.loads(p.read_bytes())
report = {'schema': 'azdaja.final_goal_reconciliation.v1', 'status': 'running',
          'new_inference_requests': 0, 'no_provider_or_sender_discovery': True,
          'closed_live_panels_reopened': False, 'full_rust_suite_rerun': False,
          'checks': []}

def save():
    (OUT / 'CHECKS.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')

def run(name, argv, expected=0, timeout=240):
    started = time.monotonic()
    p = subprocess.run(argv, cwd=ROOT, env=ENV, capture_output=True, timeout=timeout)
    (OUT / (name + '.stdout')).write_bytes(p.stdout)
    (OUT / (name + '.stderr')).write_bytes(p.stderr)
    report['checks'].append({'name': name, 'argv': argv, 'exit': p.returncode,
                            'expected_exit': expected, 'seconds': time.monotonic() - started,
                            'stdout_sha256': sha(p.stdout), 'stderr_sha256': sha(p.stderr)})
    save()
    assert p.returncode == expected, (name, p.returncode, p.stderr[-1500:].decode(errors='replace'))
    print(json.dumps({'check': name, 'exit': p.returncode}), flush=True)
    return p

def cli(name, module, *args, **kwargs):
    return run(name, [sys.executable, '-B', '-m', module, *map(str, args)], **kwargs)

def verify_inventory(rel):
    p = ROOT / rel
    data = load(p)
    if isinstance(data['files'], dict):
        rows = [(ROOT / k, v) for k, v in data['files'].items()]
    else:
        rows = [(p.parent / r['path'], r) for r in data['files']]
    for path, row in rows:
        raw = path.read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], str(path)
    return {'manifest': rel, 'sha256': sha(p.read_bytes()), 'files': len(rows)}

try:
    assert sha(BINARY.read_bytes()) == EXPECTED
    report['binary_sha256'] = EXPECTED
    report['source_head'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    changed = subprocess.check_output(['git', 'diff', '--name-only', 'e75d83660660e5e9fb199a3c00a7c5905df42f5b', '--',
        'src', 'tests', 'Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml', 'release', 'site', '.github'], cwd=ROOT, text=True)
    assert not changed.strip(), changed
    report['accepted_runtime_packaging_and_release_inputs_unchanged'] = True
    manifests = ['bench/jev/asymmetry/RETENTION-20260917.json',
                 'bench/jev/results/six-angle-acceptance-20260917/RETENTION.json',
                 'bench/jev/goal_reconciliation/20260917/RETENTION.json']
    report['retention_before'] = [verify_inventory(p) for p in manifests]
    save()
    modules = []
    for folder in ['bench/jev/angle_analysis', 'bench/jev/row651_labels',
                   'bench/jev/measurement_followthrough', 'bench/jev/second_reader', 'bench/jev/asymmetry']:
        modules.extend('.'.join(p.relative_to(ROOT).with_suffix('').parts)
                       for p in sorted((ROOT / folder).rglob('test*.py')) if 'results' not in p.parts)
    modules.append('bench.jev.test_measurement_audit')
    tested = run('mapped-offline-tests', [sys.executable, '-B', '-m', 'unittest', *modules, '-v'])
    match = re.search(rb'Ran (\d+) tests?', tested.stderr)
    assert match and b'\nOK' in tested.stderr and b'skipped=' not in tested.stderr
    report['offline_tests'] = {'passed': int(match[1]), 'skipped': 0, 'modules': modules}
    run('installed-credential-workflow', [sys.executable, '-B', str(ROOT / 'bench/jev/results/six-angle-acceptance-20260917/installed-credentials/runner.py'),
        '--azdaja', str(BINARY), '--output', str(OUT / 'installed-credentials')])
    installed = load(OUT / 'installed-credentials/receipt.json')
    assert installed['status'] == 'passed' and installed['native_transport_attempts'] == 0
    assert len(installed['checks']) == 23 and installed['synthetic_attachment_removed'] and installed['private_install_removed']
    report['installed_public_commands'] = 23
    cli('angle-public', 'bench.jev.angle_analysis.report', '--output', OUT / 'angle.json')
    cli('measurement-public', 'bench.jev.measurement_audit', '--output', OUT / 'measurement.json')
    cli('calibration-public', 'bench.jev.row651_labels.audit', '--output', OUT / 'calibration.json')
    cli('second-reader-large', 'bench.jev.second_reader.replay_large', 'bench/jev/second_reader/results/row651-live-20260917')
    cli('second-reader-policy', 'bench.jev.second_reader.replay_policy', 'bench/jev/second_reader/results/policy-live-20260917')
    paired_args = ['--receipt-dir', 'bench/jev/asymmetry/baseline/results/continued-20260917', '--output']
    cli('paired-public', 'bench.jev.asymmetry.baseline.replay', *paired_args, OUT / 'paired.json')
    assert (OUT / 'paired.json').read_bytes() == (ROOT / 'bench/jev/asymmetry/baseline/results/paired-20260917.json').read_bytes()
    cli('criteria-public', 'bench.jev.asymmetry.criteria.grade', '--receipt-dir',
        'bench/jev/asymmetry/criteria/results/native-20260917', '--output', OUT / 'criteria.json')
    assert (OUT / 'criteria.json').read_bytes() == (ROOT / 'bench/jev/asymmetry/criteria/results/grade-20260917.json').read_bytes()
    cli('threshold-public', 'bench.jev.asymmetry.threshold.transfer', '--output',
        'bench/jev/asymmetry/threshold/transfer-result.json', '--replay')
    cli('fp-analysis-public', 'bench.jev.asymmetry.fp_analysis.analyze', '--output-dir', OUT / 'fp-analysis')
    for name in ['analysis.json', 'errors.jsonl']:
        assert (OUT / 'fp-analysis' / name).read_bytes() == (ROOT / 'bench/jev/asymmetry/fp_analysis' / name).read_bytes(), name
    before = (OUT / 'paired.json').read_bytes()
    cli('existing-output-refusal', 'bench.jev.asymmetry.baseline.replay', *paired_args, OUT / 'paired.json', expected=1)
    assert (OUT / 'paired.json').read_bytes() == before
    target, link = OUT / 'absent-target', OUT / 'dangling-output'
    link.symlink_to(target)
    cli('dangling-output-refusal', 'bench.jev.asymmetry.baseline.replay', *paired_args, link, expected=1)
    assert not target.exists() and link.is_symlink()
    provider = ROOT / 'bench/jev/asymmetry/provider_report'
    status = load(provider / 'delivery-status.json')
    raw = (provider / 'UNSENT.eml').read_bytes()
    message = BytesParser(policy=email.policy.default).parsebytes(raw)
    attachments = {p.get_filename(): p.get_payload(decode=True) for p in message.iter_attachments()}
    assert sha(raw) == status['email_sha256'] and message.get('From') is None
    assert message['To'] == status['recipient'] and len(attachments) == 5
    for name, data in attachments.items():
        assert data == (provider / 'prepared' / name).read_bytes() and sha(data) == status['attachments'][name]
    assert status['status'] == 'prepared_not_sent' and not status['sender_selected']
    report['provider_report'] = {'attachments_verified': 5, 'sent': False, 'delivery_blocked_on_sender': True,
                                 'email_sha256': sha(raw), 'no_mail_accounts_reinspected': True}
    report['retention_after'] = [verify_inventory(p) for p in manifests]
    assert report['retention_before'] == report['retention_after']
    report['frozen_results_unchanged'] = True
    report['observed'] = {'angles': load(OUT / 'angle.json')['decisions'],
                         'measurement': load(OUT / 'measurement.json')['checks'],
                         'row651_metrics': {k:v for k,v in load(OUT / 'calibration.json')['metrics'].items() if not k.endswith('_ids')},
                         'paired_report_sha256': sha(before), 'criteria_report_sha256': sha((OUT / 'criteria.json').read_bytes())}
    report['status'] = 'passed'
except BaseException as exc:
    report['status'] = 'failed'
    report['error'] = type(exc).__name__ + ': ' + str(exc)
    save()
    raise
finally:
    save()
    print(json.dumps({'out': str(OUT), 'status': report['status'], 'new_inference_requests': 0,
                      'checks': len(report['checks'])}), flush=True)
