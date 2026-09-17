import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from bench.jev.span_selection import kernel as k
from bench.jev.span_selection import run as r


def report(correct=18, false_selection=False, n=18):
    rows = [{'id': f's{i+1:02d}', 'correct': i < correct,
             'false_selection_for_unresolved': false_selection and i == n-1} for i in range(n)]
    return {'observed': n, 'correct': sum(x['correct'] for x in rows), 'unjudged': 18-n, 'rows': rows}


def base_receipt():
    return {'events': [], 'known_typed_input_tokens': 0, 'typed_cells_started': 0, 'typed_questions': 0,
            'typed_attempts_with_unknown_usage': 0, 'confirmed_typed_requests': 0,
            'logical_llm_calls': 0, 'typed_rows': [], 'baseline_rows': []}


class RunnerTests(unittest.TestCase):
    def test_occupied_and_dangling_output_are_rejected_before_key_or_child(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            root = Path(tmp)
            occupied = root / 'occupied'
            occupied.mkdir()
            marker = occupied / 'kept'
            marker.write_text('unchanged')
            dangling = root / 'dangling'
            dangling.symlink_to(root / 'missing')
            for path in (occupied, dangling):
                with patch.object(r, 'read_key') as key, patch.object(r.subprocess, 'run') as child:
                    with self.assertRaises(FileExistsError):
                        r.run(['--live', '--azdaja', '/bin/false', '--scratch', str(root),
                               '--output', str(path), '--key-file', str(root/'not-a-key')])
                    key.assert_not_called()
                    child.assert_not_called()
            self.assertEqual(marker.read_text(), 'unchanged')
            self.assertTrue(dangling.is_symlink())
            self.assertFalse((root/'missing').exists())

    def test_credential_source_is_not_deleted_and_symlinks_are_refused(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            path = Path(tmp) / 'caller-secret'
            path.write_text('deliberately invalid synthetic credential')
            path.chmod(0o600)
            with self.assertRaisesRegex(r.Stop, 'credential_format'):
                r.read_key(path)
            self.assertTrue(path.exists())
            link = Path(tmp) / 'alias'
            link.symlink_to(path)
            with self.assertRaisesRegex(r.Stop, 'credential_file_policy'):
                r.read_key(link)
            path.chmod(0o644)
            with self.assertRaisesRegex(r.Stop, 'credential_file_policy'):
                r.read_key(path)

    def test_progressive_stop_is_cumulative_and_keeps_partial_unknown(self):
        self.assertIsNone(r.semantic_stop(report(5, n=6)))
        self.assertEqual(r.semantic_stop(report(10, n=12)), 'quality_bar_unreachable')
        self.assertEqual(r.semantic_stop(report(5, True, 6)), 'false_selection_for_unresolved')
        partial = r.final_quality(report(5, n=6), report(6, n=6), {'typed':[1], 'baseline':[3]})
        self.assertFalse(partial['complete_panel'])
        self.assertIsNone(partial['quality_bar_passed'])
        self.assertIsNone(partial['observed_benefit_bar_passed'])

    def test_complete_bar_rejects_losses_and_slow_ties(self):
        times = {'typed':[1,1,1], 'baseline':[3,3,3]}
        good = r.final_quality(report(), report(), times)
        self.assertTrue(good['quality_bar_passed'])
        self.assertTrue(good['observed_benefit_bar_passed'])
        self.assertFalse(good['general_advantage_established'])
        self.assertFalse(r.final_quality(report(17), report(), times)['quality_bar_passed'])
        self.assertFalse(r.final_quality(report(), report(), {'typed':[4]*3,'baseline':[3]*3})['observed_benefit_bar_passed'])
        with self.assertRaisesRegex(r.Stop, 'invalid_block_timing'):
            r.final_quality(report(), report(), {'typed':[1]*3,'baseline':[0]*3})

    def test_trace_distinguishes_logical_requests_and_physical_attempts(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            path = Path(tmp) / 'trace.jsonl'
            self.assertEqual(r.trace_summary(path)['physical_attempt_events'], 0)
            a = dict(event='model_attempt', request_id='synthetic', attempt=1, entered_turn=1,
                     model=None, provider=None, outcome='failed')
            b = dict(a, attempt=2, entered_turn=2, outcome='succeeded',model=r.GENERATOR,provider='OpenAI')
            path.write_text('\n'.join(json.dumps(x) for x in (a,b)))
            observed = r.trace_summary(path)
            self.assertEqual(observed['physical_attempt_events'], 2)
            self.assertEqual(observed['logical_request_ids'], 1)
            self.assertEqual(observed['entered_turns'], 2)
            self.assertEqual(observed['failed_identity_unknown_events'],1)
            self.assertEqual(observed['observed_models'],[r.GENERATOR])
            path.write_text('\n'.join(json.dumps(x) for x in (a,b,b)))
            with self.assertRaisesRegex(r.Stop, 'generative_transport_attempt_cap'):
                r.trace_summary(path)
            setup=dict(a)
            for optional in ('entered_turn','model','provider'):
                del setup[optional]
            after_setup=dict(b,entered_turn=1)
            path.write_text('\n'.join(json.dumps(x) for x in (setup,after_setup)))
            observed=r.trace_summary(path)
            self.assertEqual(observed['physical_attempt_events'],2)
            self.assertEqual(observed['setup_attempts'],1)
            self.assertEqual(observed['entered_turns'],1)

    def native(self, root, receipt=None, key=None):
        work, out = root/'work', root/'out'
        work.mkdir();out.mkdir()
        return r.Native(Path('/bin/false'), work, out, receipt or base_receipt(), {}, key)

    def test_deadline_and_call_caps_reject_before_process(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            n = self.native(Path(tmp))
            n.start = time.monotonic() - r.MAX_SECONDS - 1
            with patch.object(r.subprocess, 'run') as child:
                with self.assertRaisesRegex(r.Stop, 'campaign_deadline'):
                    n.command(['start'])
                child.assert_not_called()
            self.assertTrue(n.stopped)
            with self.assertRaisesRegex(r.Stop, 'session_stopped'):
                n.command(['final','old'])
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            n = self.native(Path(tmp))
            n.receipt['typed_cells_started'] = 3
            n.receipt['logical_llm_calls'] = 3
            with patch.object(r.subprocess, 'run') as child:
                with self.assertRaisesRegex(r.Stop, 'typed_call_question_budget'):
                    n.typed('extra', {'tasks':[]})
                with self.assertRaisesRegex(r.Stop, 'generative_call_budget'):
                    n.generate('extra', {'tasks':[]})
                child.assert_not_called()

    def test_timeout_poisoning_does_not_adopt_old_state(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            n = self.native(Path(tmp))
            with patch.object(r.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['local-only'], 1)) as child:
                with self.assertRaises(subprocess.TimeoutExpired):
                    n.command(['exec','fake'])
                with self.assertRaisesRegex(r.Stop, 'session_stopped'):
                    n.command(['final','fake'])
                self.assertEqual(child.call_count, 1)

    def test_changed_method_stops_before_transport(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            root=Path(tmp);n=self.native(root)
            path=root/'frozen.py';path.write_text('original')
            n.frozen[path]=r.digest(path);path.write_text('modified')
            with patch.object(r.subprocess,'run') as child:
                with self.assertRaisesRegex(r.Stop,'frozen_input_changed'):
                    n.command(['exec','fake'])
                child.assert_not_called()

    def test_public_fixture_source_and_gold_before_inference(self):
        inp=k.strict_loads((r.HERE/'fixtures/inputs.json').read_text())
        gold=k.strict_loads((r.HERE/'fixtures/gold.json').read_text())
        k.verify_git_sources(inp,r.ROOT)
        k.validate_gold(k.prepare(inp),gold)
        self.assertEqual([sum(t['block']==i for t in inp['tasks']) for i in (1,2,3)],[6,6,6])

    def test_crossing_usage_survives_but_never_becomes_eligible_rows(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            root=Path(tmp); n=self.native(root)
            inp=k.strict_loads((r.HERE/'fixtures/inputs.json').read_text())
            pack={'tasks': k.prepare(inp)['tasks'][:6]}
            n.receipt['known_typed_input_tokens']=r.TOKEN_CAP-1
            result={'failed':'known token budget crossing','stats':{'provider_requests':1,
                    'known_input_tokens':2,'unknown_input_usage_requests':0}}
            with patch.object(n,'load'), patch.object(n,'cell',return_value=json.dumps(result)) as cell:
                with self.assertRaisesRegex(r.Stop,'typed_contract_or_resource_failure'):
                    n.typed('crossing',pack)
                self.assertEqual(cell.call_count,1)
            self.assertEqual(n.receipt['known_typed_input_tokens'],r.TOKEN_CAP+1)
            self.assertEqual(n.receipt['typed_attempts_with_unknown_usage'],0)
            self.assertEqual(n.receipt['confirmed_typed_requests'],1)
            self.assertEqual(n.receipt['typed_rows'],[])
            self.assertTrue((n.out/'crossing-observation.json').is_file())


@unittest.skipUnless(os.environ.get('AZDAJA_BINARY'), 'set AZDAJA_BINARY for actual native public-interface checks')
class ActualNativeTests(unittest.TestCase):
    def test_unicode_duplicate_occurrences_wrong_choice_and_invalid_id(self):
        binary=Path(os.environ['AZDAJA_BINARY']).resolve(strict=True)
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            root=Path(tmp); work=root/'work'; out=root/'out';work.mkdir();out.mkdir()
            receipt=base_receipt()
            n=r.Native(binary,work,out,receipt,{binary:r.digest(binary)})
            try:
                n.sid=n.command(['start'])
                n.cell('init','retained_results = {}\nretained_observations = {}\nFINAL("ready")\n')
                text='The default is `café`. The example is `wrong`. Repeat `café`.'
                source={'path':'synthetic.txt','commit':k.PUBLIC_SOURCE,'start_line':1,'end_line':1,
                        'text':text,'sha256':k.sha(text.encode())}
                pack={'tasks':[{'id':'s01','question':'Which default?','source':source,
                               'candidates':k.candidates(text,'quoted_literal')}]}
                candidates=pack['tasks'][0]['candidates']
                for i in (0,1,2):
                    actual=n.project('choice'+str(i),pack,{'s01':candidates[i]['id']})[0]
                    self.assertEqual(actual['value'],candidates[i]['text'])
                    self.assertEqual(actual['start'],candidates[i]['start'])
                    self.assertEqual(actual['byte_start'],candidates[i]['byte_start'])
                self.assertEqual(json.loads((out/'choice1-table.json').read_text())['rows'][0]['value'],'wrong')
                before=len(receipt['events'])
                with self.assertRaises(ValueError):
                    n.project('invalid',pack,{'s01':'missing-id'})
                self.assertEqual(len(receipt['events']),before)
                self.assertEqual(receipt['typed_cells_started'],0)
                self.assertEqual(receipt['logical_llm_calls'],0)
            finally:
                n.close()
            self.assertEqual(receipt['cleanup_exit'],0)


if __name__ == '__main__':
    unittest.main()
