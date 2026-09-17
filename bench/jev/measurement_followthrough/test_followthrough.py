import copy
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from . import evidence as e, run, report
from bench.jev.angle_lab import native as n
from bench.jev.measurement_v2 import report as old_report


class FollowthroughTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR'])
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'receipt'
        self.path.mkdir()
        for p in e.PREDECESSOR.iterdir():
            if p.is_file(): shutil.copyfile(p,self.path/p.name)

    def change(self, name, mutation):
        path=self.path/name
        value=e.load(path); mutation(value); path.write_bytes(n.canonical(value)+b'\n')

    def read(self):
        return e.read_run(self.path,e.ORIGINAL_ORDER)

    def test_actual_rejection_keeps_known_input_and_unknown_output(self):
        result=self.read()
        self.assertEqual(len(result['labels']['typed']),25)
        self.assertEqual(len(result['labels']['generative']),50)
        self.assertEqual(result['totals']['known_typed_input_tokens'],17705)
        self.assertEqual(result['totals']['typed_unknown_output_usage'],1)
        self.assertEqual(len(result['failures'][0]['unjudged_ids']),25)
        with self.assertRaisesRegex(ValueError,'receipt usage mismatch'):
            old_report.verify(self.path)

    def test_removing_failed_usage_cannot_shrink_cost(self):
        self.change('receipt.json',lambda r:r.update(known_typed_input_tokens=8739))
        with self.assertRaisesRegex(ValueError,'receipt accounting known_typed_input_tokens'): self.read()

    def test_forged_completion_and_failed_promotion_reject(self):
        self.change('receipt.json',lambda r:r.update(status='completed'))
        with self.assertRaisesRegex(ValueError,'false completion'): self.read()

    def test_repeated_or_missing_attempt_rejects(self):
        self.change('receipt.json',lambda r:r['benchmark_rows'].append(copy.deepcopy(r['benchmark_rows'][0])))
        with self.assertRaisesRegex(ValueError,'attempt order or repeat'): self.read()

    def test_rehashed_typed_state_swap_rejects(self):
        self.change('flat-01-typed-request.json',lambda r:r.update(state='changed'))
        with self.assertRaisesRegex(ValueError,'typed request binding'): self.read()

    def test_instruction_mutation_is_not_matched_evidence(self):
        self.change('flat-01-generative-prompt.json',lambda r:r.update(instruction='changed'))
        with self.assertRaisesRegex(ValueError,'generative prompt binding'): self.read()

    def test_failed_observation_cannot_appear_completed(self):
        def mutate(r):
            event=r['benchmark_rows'][-1]
            event['status']='completed';event['native_call']=r['calls'][-1]
        self.change('receipt.json',mutate)
        with self.assertRaisesRegex(ValueError,'failed observation promoted'): self.read()

    def test_missing_body_and_trace_swap_reject(self):
        (self.path/'flat-01-typed-observation.json').unlink()
        with self.assertRaisesRegex(ValueError,'missing completed observation'): self.read()

    def test_continuation_keeps_original_arm_order_and_has_no_repeat(self):
        previous=e.predecessor()
        rows=run.remaining_rows()
        order=[(r['name'],arm) for i,r in enumerate(rows) for arm in (
            ('typed','generative') if i%2==0 else ('generative','typed'))]
        self.assertEqual(order,e.CONTINUATION_ORDER)
        self.assertEqual(len(order),20)
        self.assertFalse(set(order).intersection(previous['order']))
        self.assertTrue(all(name.startswith('verifier-') for name,_ in order[:16]))

    def test_partial_panel_never_passes_even_perfect_observed_answers(self):
        prior=self.read()
        gold=e.load(e.ORIGINAL/'fixtures/gold.json')
        prior['labels']['typed']={q:gold[q]['expected'] for q in prior['labels']['typed']}
        result=report.summarize([prior])
        lane=result['lanes']['flat']
        self.assertFalse(lane['full_panel_complete'])
        self.assertFalse(lane['quality_bar_passed'])
        self.assertFalse(lane['quality_and_speed_benefit_bar_passed'])
        self.assertEqual(result['cumulative_totals']['known_typed_input_tokens'],17705)
        self.assertFalse(result['typed_output_usage_complete'])
        with self.assertRaisesRegex(ValueError,'repeat across campaigns'): report.summarize([prior,prior])

    def test_caps_include_predecessor_before_any_native_call(self):
        previous=e.predecessor()
        binary=Path(os.environ['JCODE_SCRATCH_DIR'])/'jev-ingest-native-e75d836-azdaja'
        output=Path(self.temp.name)/'campaign'
        campaign=run.Continuation(binary,output,{str(binary):e.BINARY_SHA},previous=previous,authorized=True)
        self.assertIn('max_input_tokens_per_cell=1482295', (campaign.work/'config.toml').read_text())
        campaign.receipt['typed_calls_started']=10
        with patch.object(n.Campaign,'typed',side_effect=AssertionError('must not enter')):
            with self.assertRaisesRegex(n.Stop,'cumulative_typed_cap'): campaign.typed('untouched',{})
        self.assertTrue(campaign.stopped)

    def test_default_cli_and_existing_output_are_provider_free(self):
        process=subprocess.run([sys.executable,'-B','-m','bench.jev.measurement_followthrough.run'],capture_output=True,text=True,timeout=10)
        self.assertEqual(process.returncode,0)
        self.assertEqual(n.strict_loads(process.stdout)['provider_calls'],0)
        output=Path(self.temp.name)/'keep';output.write_bytes(b'unchanged')
        # Default report command must not overwrite any existing or dangling path.
        with patch.object(report,'combined',return_value={'safe':True}), patch.object(sys,'argv',['report','--output',str(output)]):
            with self.assertRaises(FileExistsError): report.main()
        self.assertEqual(output.read_bytes(),b'unchanged')
        link=Path(self.temp.name)/'dangling';link.symlink_to(Path(self.temp.name)/'absent')
        with patch.object(report,'combined',return_value={'safe':True}), patch.object(sys,'argv',['report','--output',str(link)]):
            with self.assertRaises(FileExistsError): report.main()
        self.assertFalse(link.exists())


if __name__=='__main__': unittest.main()
