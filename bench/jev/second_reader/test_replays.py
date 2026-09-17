"""Mutation tests on private copies of real terminal receipts. Never infer."""
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from bench.jev.angle_lab import native as n
from . import replay_large as large, replay_policy as policy

HERE=Path(__file__).resolve().parent


def load(path): return n.strict_loads(path.read_bytes())
def save(path, obj): path.write_bytes(n.canonical(obj)+b'\n')


class RetainedReplayTests(unittest.TestCase):
    def copy(self, name):
        tmp=tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR'))
        self.addCleanup(tmp.cleanup)
        target=Path(tmp.name)/'copy'
        shutil.copytree(HERE/'results'/name,target,ignore=shutil.ignore_patterns('private-work'))
        return target

    def test_actual_full_row_negative_result_and_usage_replays(self):
        report=large.replay(HERE/'results/row651-live-20260917')
        self.assertEqual(report['ham_count'],9245)
        self.assertEqual(report['official_count'],8638)
        self.assertEqual(report['observed_occurrences'],17469)
        self.assertFalse(report['exact_task_pass'])
        self.assertEqual(report['known_input_tokens'],2749030)
        self.assertEqual(report['known_output_tokens'],357302)
        self.assertAlmostEqual(report['sum_noul'],9287.38)

    def test_false_native_win_rejected_even_with_matching_summary(self):
        folder=self.copy('row651-live-20260917')
        reduction=load(folder/'final-reduction.json');reduction['ham']=8638;reduction['answer']='Answer: 8638'
        save(folder/'final-reduction.json',reduction)
        receipt=load(folder/'receipt.json');receipt['native_reduction']=reduction;save(folder/'receipt.json',receipt)
        with self.assertRaisesRegex(ValueError,'reduction count'):large.replay(folder)

    def test_swapped_source_cannot_be_rehashed_into_coverage(self):
        folder=self.copy('row651-live-20260917')
        path=folder/'pack-001-request.json';request=load(path)
        first=next(iter(request['state']['records']));request['state']['records'][first]='different source'
        save(path,request)
        with self.assertRaisesRegex(ValueError,'request/source equality'):large.replay(folder)

    def test_impossible_wall_speed_rejected(self):
        folder=self.copy('row651-live-20260917')
        receipt=load(folder/'receipt.json');receipt['elapsed_seconds']=.001;save(folder/'receipt.json',receipt)
        with self.assertRaisesRegex(ValueError,'impossible wall time'):large.replay(folder)

    def test_actual_policy_gain_and_ensemble_non_gain_replay(self):
        report=policy.replay(HERE/'results/policy-live-20260917')
        self.assertEqual(report['adjudication']['correct'],222)
        self.assertEqual(report['adjudication']['baseline_correct'],220)
        self.assertEqual(report['adjudication']['retained_agreement_errors'],5)
        self.assertFalse(report['adjudication']['approval'])
        self.assertEqual(len(report['phrasing']['majority_vote']['errors']),8)
        self.assertEqual(len(report['phrasing']['unanimity']['errors']),6)
        self.assertEqual(report['known_input_tokens'],73841)

    def test_rehashed_boolean_probability_is_not_semantic_evidence(self):
        folder=self.copy('policy-live-20260917')
        path=folder/'phrasing-01-observation.json';result=load(path)
        first=next(iter(result['observation']['answers']));result['observation']['answers'][first]['noul']=True
        save(path,result)
        receipt=load(folder/'receipt.json');receipt['panel_rows'][1]['response_sha256']=n.sha(n.canonical(result['observation']));save(folder/'receipt.json',receipt)
        with self.assertRaisesRegex(ValueError,'noul domain'):policy.replay(folder)

    def test_blind_adjudication_input_cannot_gain_gold_after_rehash(self):
        folder=self.copy('policy-live-20260917')
        path=folder/'adjudication-prompt.json';prompt=load(path);prompt['payload']['state']['gold']='all spam';save(path,prompt)
        with self.assertRaisesRegex(ValueError,'source equality'):policy.replay(folder)

    def test_missing_large_pack_is_not_a_complete_answer(self):
        folder=self.copy('row651-live-20260917');(folder/'pack-112-observation.json').unlink()
        with self.assertRaisesRegex(ValueError,'missing observation'):large.replay(folder)


if __name__=='__main__':unittest.main()
