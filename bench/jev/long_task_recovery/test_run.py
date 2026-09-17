import contextlib
import io
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from bench.jev.long_task_recovery import run as r


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR'], prefix='long-recovery-test-')
        self.root = Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()

    def test_exact_predecessor_retains_both_failed_unknown_usage_requests(self):
        prior = r.predecessor()
        self.assertEqual(list(prior), list(r.base.ARMS))
        self.assertEqual({a: math.floor(2100 - s) for a, s in prior.items()},
                         {'generative': 2038, 'optional_typed': 2036})

    def test_changed_predecessor_artifact_and_rehashed_inventory_rejected(self):
        dst = self.root / 'prior'
        shutil.copytree(r.PREVIOUS, dst)
        (dst / 'generative/stdout.txt').write_text('{}')
        with mock.patch.object(r, 'PREVIOUS', dst), self.assertRaisesRegex(r.base.Stop, 'artifacts_changed'):
            r.predecessor()
        inv = r.base.loads((dst / 'RETENTION.json').read_bytes())
        inv['files']['generative/stdout.txt'] = r.base.sha(b'{}')
        (dst / 'RETENTION.json').write_bytes(r.base.canonical(inv))
        with mock.patch.object(r, 'PREVIOUS', dst), self.assertRaisesRegex(r.base.Stop, 'retention_changed'):
            r.predecessor()

    def test_default_actual_public_cli_is_provider_free_outside_repo(self):
        p = subprocess.run([sys.executable, '-B', str(r.HERE / 'run.py')], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(r.base.loads(p.stdout)['provider_calls'], 0)

    def test_unacknowledged_never_checks_seal_or_runs_arm(self):
        with mock.patch.object(r, 'check_seal') as seal, mock.patch.object(r.base, 'run_arm') as arm:
            with self.assertRaisesRegex(r.base.Stop, 'explicit_live_arguments'):
                r.main(['--live', '--binary', sys.executable])
        seal.assert_not_called()
        arm.assert_not_called()

    def exercise(self, cleanup=False, overrun=False):
        method = self.root / 'method'; method.mkdir()
        output = self.root / 'output'
        limits = []
        def arm(binary, name, destination, private, **kwargs):
            destination.mkdir()
            limits.append(r.base.SECONDS)
            result = {'status': 'completed_outputs_pending_scoring',
                      'workflow_seconds': r.base.SECONDS + 1 if overrun else 1.0}
            if cleanup:
                result.update(status='stopped', cleanup_error='synthetic')
            return result
        argv = ['--live', '--acknowledge-provider-calls', '--binary', sys.executable,
                '--output', str(output), '--auth-file', str(self.root/'not-read'), '--attached-file', str(self.root/'not-read')]
        with mock.patch.object(r, 'HERE', method), mock.patch.object(r, 'check_seal', return_value='a'*64), \
             mock.patch.object(r.base, 'run_arm', side_effect=arm), \
             mock.patch.dict(os.environ, {'JCODE_SCRATCH_DIR': str(self.root)}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(r.main(argv), 0)
            second = self.root/'second'; argv[argv.index('--output')+1] = str(second)
            with self.assertRaises(FileExistsError):
                r.main(argv)
        self.assertEqual(r.base.SECONDS, 2100)
        self.assertFalse(second.exists())
        return limits, r.base.loads((output/'terminal.json').read_bytes())

    def test_exact_remaining_budgets_exclusive_marker_and_prior_time_retained(self):
        limits, terminal = self.exercise()
        self.assertEqual(limits, [2038, 2036])
        self.assertTrue(terminal['all_completed'])
        for arm, seconds in r.predecessor().items():
            self.assertEqual(terminal['cumulative_workflow_seconds'][arm], seconds + 1)
        self.assertTrue(terminal['cumulative_usage_is_lower_bound'])

    def test_failed_cleanup_stops_before_second_arm(self):
        limits, terminal = self.exercise(cleanup=True)
        self.assertEqual(limits, [2038])
        self.assertFalse(terminal['all_completed'])

    def test_cumulative_deadline_cannot_be_completed(self):
        _, terminal = self.exercise(overrun=True)
        self.assertFalse(terminal['all_completed'])
        self.assertEqual(set(terminal['arms'].values()), {'stopped'})

    def test_inventory_binds_methods_runtime_and_predecessor(self):
        inv = r.inventory(Path(sys.executable))
        for name in ('bench/jev/long_task_recovery/run.py', 'bench/jev/long_task_recovery/AMENDMENT.md',
                     'bench/jev/long_task/run.py', 'bench/jev/long_task/task.txt', 'src/lib.rs'):
            self.assertIn(name, inv['files'])
        self.assertEqual(inv['remaining_seconds'], {'generative': 2038, 'optional_typed': 2036})


if __name__ == '__main__':
    unittest.main()
