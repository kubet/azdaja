import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import unittest

from . import run as r

PRIOR = r.ROOT / 'bench/jev/angle_lab/results/run1-stopped'


class ContinuationTests(unittest.TestCase):
    def test_predecessor_is_exact_stopped_setup_not_quality_rerun(self):
        receipt, body = r.predecessor(PRIOR)
        self.assertEqual(receipt['confirmed_typed_requests'], 1)
        self.assertEqual(len(body['answers']), 20)
        self.assertEqual(receipt['generative_trace']['entered_turns'], 0)

    def test_unknown_usage_or_entered_turn_prevents_admission(self):
        for field, value in [('typed_unknown_usage', 1), ('logical_llm_calls', 0),
                             ('known_typed_input_tokens', 0), ('status', 'completed')]:
            with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
                d = Path(directory)
                for p in PRIOR.iterdir():
                    shutil.copyfile(p, d / p.name)
                receipt = json.loads((d / 'receipt.json').read_text())
                receipt[field] = value
                (d / 'receipt.json').write_text(json.dumps(receipt))
                with self.assertRaisesRegex(r.n.Stop, 'predecessor_not_declared_setup_failure'):
                    r.predecessor(d)

    def test_mutated_question_cannot_reuse_calibration(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            d = Path(directory)
            for p in PRIOR.iterdir():
                shutil.copyfile(p, d / p.name)
            req = json.loads((d / 'calibration-request.json').read_text())
            req['state'] = 'changed evidence'
            (d / 'calibration-request.json').write_text(json.dumps(req))
            with self.assertRaisesRegex(r.n.Stop, 'predecessor_binding_or_threshold'):
                r.predecessor(d)

    def binary(self):
        name = os.environ.get('AZDAJA_ANGLE_BINARY')
        if not name:
            self.skipTest('explicit actual binary is required')
        return Path(name)

    def instance(self, d):
        state = d / 'state'; state.mkdir(mode=0o700)
        return r.Continuation(self.binary(), d / 'output',
            {PRIOR / 'receipt.json': r.n.sha((PRIOR / 'receipt.json').read_bytes())},
            PRIOR, state, time.time())

    def test_actual_reentry_carries_usage_without_new_call(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            c = self.instance(Path(directory))
            try:
                c.start()
                body = c.typed('calibration', r.gate.calibration())
                self.assertEqual(body, c.carried)
                self.assertEqual(c.receipt['typed_calls_started'], 0)
                self.assertEqual(c.receipt['logical_llm_calls'], 0)
                total = c.receipt['cumulative_including_stopped_predecessor']
                self.assertEqual(total['confirmed_typed_requests'], 1)
                self.assertEqual(total['known_typed_input_tokens'], 3261)
                self.assertEqual(total['logical_llm_calls'], 1)
                c.configure(True)
                self.assertIn('max_input_tokens_per_cell=1496739\n', (c.work/'config.toml').read_text())
            finally:
                c.finish('stopped' if c.stopped else 'offline_verified')
            self.assertEqual(c.receipt['cleanup_exit'], 0)

    def test_cumulative_caps_refuse_before_transport(self):
        for method, count, error in [('typed', 23, 'cumulative_typed_attempt_budget'),
                                     ('generate', 11, 'cumulative_generative_budget')]:
            with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
                c = self.instance(Path(directory))
                field = 'typed_calls_started' if method == 'typed' else 'logical_llm_calls'
                c.receipt[field] = count
                with self.assertRaisesRegex(r.n.Stop, error):
                    getattr(c, method)('no-call', {})
                self.assertTrue(c.stopped)
                self.assertEqual(c.receipt['events'], [])

    def test_original_elapsed_time_is_not_reset(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            c = self.instance(Path(directory))
            c.origin_start = time.time() - r.n.MAX_SECONDS - 1
            with self.assertRaisesRegex(r.n.Stop, 'original_campaign_deadline'):
                c.left()


if __name__ == '__main__':
    unittest.main()
