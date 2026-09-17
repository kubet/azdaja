"""One bounded provider-free whole-result reconciliation. No live campaign modes."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path('/Users/vukasinkubet/dev/azdaja')
S = Path(os.environ['JCODE_SCRATCH_DIR'])
OUT = Path(tempfile.mkdtemp(prefix='jev-postfinal-reconciled-', dir=S))
HOME = OUT / 'home'
HOME.mkdir()
OLD = S / 'jev-ingest-native-e75d836-azdaja'
CURRENT = S / 'jev-solo-repair-target/debug/azdaja'
FAILED = S / 'jev-postfinal-reconciliation-9jfa5_sr'
sha = lambda data: hashlib.sha256(data).hexdigest()
assert sha(OLD.read_bytes()) == '13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32'
assert sha(CURRENT.read_bytes()) == '7b321d4e56295a2b54d1a3a1a1dcd3eb6b52f5f826bd83bf88e36b2f13a4a681'
ENV = {'PATH': os.environ['PATH'], 'HOME': str(HOME), 'JCODE_SCRATCH_DIR': str(S),
       'PYTHONPATH': str(ROOT), 'PYTHONDONTWRITEBYTECODE': '1', 'AZDAJA_BINARY': str(OLD)}
status_before = subprocess.check_output(['git', 'status', '--porcelain=v1', '-uall'], cwd=ROOT)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
report = {'schema': 'azdaja.postfinal_alias_reconciliation.v2', 'head': head,
          'new_provider_calls': 0, 'studies_reopened': False, 'status': 'running', 'checks': [],
          'current_cli_sha256': sha(CURRENT.read_bytes()), 'historical_native_sha256': sha(OLD.read_bytes()),
          'binary_scope': 'Current CLI only for disposable installed acceptance. Exact frozen historical CLI for sealed native sampling tests.',
          'prior_failed_check': {'head': '10f25303196a2c98e4bf758cefe0c25bb85e0442', 'tests': 209, 'passed': 208, 'errors': 1,
              'reason': 'Frozen mocked duplicate-marker witness encountered the correctly expired production deadline first.',
              'raw_report_status_was_stale_running': True,
              'files': {p.name: sha(p.read_bytes()) for p in FAILED.iterdir() if p.is_file()}},
          'clock_adapter': {'path': 'bench/jev/goal_reconciliation/test_continuation_clock.py',
              'sha256': sha((ROOT/'bench/jev/goal_reconciliation/test_continuation_clock.py').read_bytes()),
              'scope': 'Only the inherited mocked duplicate-marker witness uses STARTED+1. Production and sealed source unchanged; separate expired-admission tests run.'}}

def save():
    (OUT/'report.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')

def run(name, argv, expected=0):
    t = time.monotonic()
    p = subprocess.run(list(map(str, argv)), cwd=ROOT, env=ENV, capture_output=True, timeout=180)
    (OUT/(name+'.stdout')).write_bytes(p.stdout)
    (OUT/(name+'.stderr')).write_bytes(p.stderr)
    report['checks'].append({'name': name, 'argv': list(map(str, argv)), 'exit': p.returncode,
        'expected_exit': expected, 'seconds': time.monotonic()-t,
        'stdout_sha256': sha(p.stdout), 'stderr_sha256': sha(p.stderr)})
    save()
    print(json.dumps({'check': name, 'exit': p.returncode}), flush=True)
    assert p.returncode == expected, (name, p.stderr[-4000:].decode(errors='replace'))
    return p

py = [sys.executable, '-B', '-m']
try:
    old = json.loads((ROOT/'bench/jev/goal_reconciliation/20260917-final/CHECKS.json').read_text())
    modules = old['offline_tests']['modules']
    modules = ['bench.jev.goal_reconciliation.test_continuation_clock' if x == 'bench.jev.asymmetry.baseline.test_continue' else x for x in modules]
    modules += ['bench.jev.audit_sampling.test_estimator', 'bench.jev.audit_sampling.test_run',
                'bench.jev.audit_sampling.test_replay', 'bench.jev.audit_sampling.test_portable',
                'bench.jev.long_task_salvage.test_extract', 'bench.jev.long_task_salvage.test_replay',
                'bench.jev.long_task_salvage.test_verify']
    p = run('mapped-boundary-tests', py+['unittest']+modules+['-v'])
    count = re.search(rb'Ran (\d+) tests', p.stderr)
    assert count and int(count[1]) == 211 and p.stderr.rstrip().endswith(b'OK')
    report['offline_tests'] = {'modules': modules, 'passed': 211, 'failed': 0, 'clock_adapter_explicit': True}
    run('installed-current', [sys.executable, '-B', ROOT/'bench/jev/results/six-angle-acceptance-20260917/installed-credentials/runner.py', '--azdaja', CURRENT, '--output', OUT/'installed-current'])
    installed = json.loads((OUT/'installed-current/receipt.json').read_text())
    assert installed['status'] == 'passed' and len(installed['checks']) == 23
    assert installed['provider_calls'] == installed['native_transport_attempts'] == 0
    report['installed_current'] = installed
    run('angle-public', py+['bench.jev.angle_analysis.report', '--output', OUT/'angle.json'])
    run('measurement-public', py+['bench.jev.measurement_audit', '--output', OUT/'measurement.json'])
    run('calibration-public', py+['bench.jev.row651_labels.audit', '--output', OUT/'calibration.json'])
    run('second-reader-large', py+['bench.jev.second_reader.replay_large', 'bench/jev/second_reader/results/row651-live-20260917'])
    run('second-reader-policy', py+['bench.jev.second_reader.replay_policy', 'bench/jev/second_reader/results/policy-live-20260917'])
    paired = py+['bench.jev.asymmetry.baseline.replay', '--receipt-dir', 'bench/jev/asymmetry/baseline/results/continued-20260917']
    run('paired-public', paired+['--output', OUT/'paired.json'])
    run('criteria-public', py+['bench.jev.asymmetry.criteria.grade', '--receipt-dir', 'bench/jev/asymmetry/criteria/results/native-20260917', '--output', OUT/'criteria.json'])
    run('threshold-public', py+['bench.jev.asymmetry.threshold.transfer', '--output', 'bench/jev/asymmetry/threshold/transfer-result.json', '--replay'])
    run('fp-analysis-public', py+['bench.jev.asymmetry.fp_analysis.analyze', '--output-dir', OUT/'fp-analysis'])
    equality = json.loads((ROOT/'bench/jev/goal_reconciliation/20260917-final/OUTPUT-EQUALITY.json').read_text())
    for row in equality:
        fresh, retained = (OUT/row['fresh_output']).read_bytes(), (ROOT/row['retained_path']).read_bytes()
        assert fresh == retained and sha(fresh) == row['sha256']
    report['output_equality'] = equality
    before = (OUT/'paired.json').read_bytes()
    run('paired-existing-output-refusal', paired+['--output', OUT/'paired.json'], expected=1)
    assert (OUT/'paired.json').read_bytes() == before
    target = OUT/'not-created'
    dangling = OUT/'dangling.json'
    dangling.symlink_to(target)
    run('paired-dangling-output-refusal', paired+['--output', dangling], expected=1)
    assert dangling.is_symlink() and not target.exists()
    run('sampling-public', py+['bench.jev.audit_sampling.replay', '--output', OUT/'sampling.json'])
    run('long-public', py+['bench.jev.long_task_salvage.verify'])
    assert subprocess.check_output(['git', 'status', '--porcelain=v1', '-uall'], cwd=ROOT) == status_before
    report.update(status='passed', git_status_unchanged=True)
except BaseException as e:
    report.update(status='failed', failure=type(e).__name__+': '+str(e))
    raise
finally:
    save()
    print(json.dumps({'out': str(OUT), 'status': report['status'], 'checks': len(report['checks']), 'new_provider_calls': 0}), flush=True)
