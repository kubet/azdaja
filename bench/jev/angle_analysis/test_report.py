import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from . import report as r


class ReportTests(unittest.TestCase):
    def copy_results(self, directory):
        target = Path(directory)/'results'
        shutil.copytree(r.RESULTS,target)
        return target

    def change(self, directory, name, mutate):
        path = directory/'continuation-completed'/name
        value = r.load(path); mutate(value)
        raw = r.n.canonical(value)+b'\n'; path.write_bytes(raw)
        index = directory/'continuation-retention.json'
        retained = r.load(index)
        for entry in retained['files']:
            if entry['path']==name:
                entry.update(bytes=len(raw),sha256=r.n.sha(raw))
        index.write_bytes(r.n.canonical(retained)+b'\n')

    def test_actual_retained_result_is_negative_and_usage_is_complete(self):
        report = r.verify()
        self.assertTrue(report['replay_consistent'])
        self.assertFalse(report['general_quality_advantage_established'])
        self.assertEqual(report['typed_requests_replayed'],10)
        self.assertEqual(report['successful_generative_calls_replayed'],9)
        self.assertEqual(report['totals']['known_typed_input_tokens'],56094)
        self.assertEqual(report['generative_usage']['input_tokens']['known_total'],44254)
        self.assertEqual(report['semantic_outcomes']['memory']['typed_ranking']['correct'],3)

    def test_rehashed_false_win_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            d = self.copy_results(directory)
            def mutate(value):
                value['quality_bar_passed']=True
                value['typed']['predicted_ham']=132
                value['typed']['exact_task_answer']=True
            self.change(d,'gate-result.json',mutate)
            with self.assertRaisesRegex(ValueError,'derived output mismatch: gate-result.json'):
                r.verify(d)

    def test_rehashed_unmatched_baseline_state_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            d = self.copy_results(directory)
            self.change(d,'gate-1-direct-prompt.json',lambda v:v['payload'].update(state='different source'))
            with self.assertRaisesRegex(ValueError,'generative input mismatch'):
                r.verify(d)

    def test_rehashed_invalid_probability_is_not_a_judgment(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            d = self.copy_results(directory)
            def mutate(value):
                answers=value['observation']['answers']
                answers[next(iter(answers))]['noul']=True
            self.change(d,'gate-1-typed-observation.json',mutate)
            with self.assertRaisesRegex(ValueError,'invalid probability'):
                r.verify(d)

    def test_rehashed_receipt_cannot_erase_reported_usage(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            d = self.copy_results(directory)
            def mutate(value):
                for call in value['calls']:
                    if call['arm']=='typed':call['known_input_tokens']=0
            self.change(d,'receipt.json',mutate)
            with self.assertRaisesRegex(ValueError,'call usage accounting'):
                r.verify(d)

    def test_missing_source_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            d = self.copy_results(directory)
            (d/'continuation-completed/gate-1-typed-request.json').unlink()
            with self.assertRaisesRegex(ValueError,'artifact coverage'):
                r.verify(d)

    def test_public_cli_refuses_existing_or_dangling_output(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            d=Path(directory); existing=d/'existing.json'; existing.write_text('preserved')
            dangling=d/'dangling.json'; dangling.symlink_to(d/'no-target')
            for output in (existing,dangling):
                p=subprocess.run([sys.executable,'-B','-m','bench.jev.angle_analysis.report','--output',str(output)],
                                 cwd=r.ROOT,text=True,capture_output=True,timeout=15)
                self.assertNotEqual(p.returncode,0)
                self.assertIn('FileExistsError',p.stderr)
            self.assertEqual(existing.read_text(),'preserved')
            self.assertFalse((d/'no-target').exists())


if __name__=='__main__':
    unittest.main()
