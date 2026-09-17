import contextlib
import io
import math
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bench.jev.second_reader import large_run as r
from bench.jev.angle_lab import native as n


def one():
    return {'state': {'records': {'r0005': 'Date: example'}},
            'questions': {'r0005': {'type': 'noul', 'instructions': 'Is state.records.r0005 ham?'}}}


class LargeRunTests(unittest.TestCase):
    def test_default_is_provider_free(self):
        with patch.object(r, 'packs', side_effect=AssertionError('must not load')), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(r.main([]), 0)

    def test_packs_cover_source_and_canonical_crossing_order(self):
        rows = r.packs()
        self.assertEqual(len(rows), 112)
        self.assertEqual(sum(len(p['questions']) for _, p in rows), 17469)
        crossing = rows[63][1]
        self.assertEqual(next(iter(crossing['questions'])), 'r10000')
        self.assertIn('r9913', crossing['questions'])
        for _, pack in rows:
            r.validate_pack(pack)
            self.assertLessEqual(len(n.canonical(dict(pack, model=r.MODEL))), r.MAX_REQUEST)

    def test_pack_rejects_missing_record_extra_kind_and_byte_cap(self):
        mutations = [lambda p: p['state']['records'].clear(),
                     lambda p: p['questions']['r0005'].update(type='choice'),
                     lambda p: p['state']['records'].update(r0005='x'*r.MAX_STATE)]
        for mutate in mutations:
            p = one(); mutate(p)
            with self.assertRaises(n.Stop): r.validate_pack(p)

    def campaign(self, parent):
        binary = Path('/usr/bin/false').resolve()
        return r.Campaign(binary, Path(parent)/'receipt', {str(binary): n.sha(binary.read_bytes())}, authorized=True)

    def result(self, p, probability=.75, tokens=10):
        body = {'model': r.MODEL, 'answers': {'r0005': {'type':'noul','noul':probability}},
                'usage': {'input_tokens':tokens,'output_tokens':2},
                '_azdaja': {'request_sha256':n.sha(n.canonical(dict(p,model=r.MODEL))), 'elapsed_ms':10}}
        return {'observation':body,'stats':{'provider_requests':1,'known_input_tokens':tokens,'unknown_input_usage_requests':0}}

    def test_live_typed_path_checks_reentry_and_complete_usage(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            c=self.campaign(tmp); p=one(); result=self.result(p)
            with patch.object(c,'load'), patch.object(c,'cell',side_effect=[n.canonical(result),n.canonical(result['observation'])]) as cell:
                self.assertEqual(c.typed('pack-001',p),result['observation'])
            self.assertEqual(cell.call_count,2)
            self.assertEqual(c.receipt['confirmed_typed_requests'],1)
            self.assertEqual(c.receipt['known_typed_input_tokens'],10)
            self.assertEqual(c.receipt['typed_unknown_usage'],0)
            self.assertEqual(c.receipt['typed_unknown_output_usage'],0)
            self.assertFalse(c.stopped)

    def test_budget_crossing_accounts_attempt_then_poison_no_reentry(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            c=self.campaign(tmp); p=one(); result=self.result(p,tokens=r.MAX_INPUT+1)
            with patch.object(c,'load'), patch.object(c,'cell',return_value=n.canonical(result)) as cell:
                with self.assertRaisesRegex(n.Stop,'input_budget_crossed'): c.typed('pack-001',p)
                with self.assertRaisesRegex(n.Stop,'session_stopped'): c.typed('pack-002',p)
                self.assertEqual(cell.call_count,1)
            self.assertEqual(c.receipt['known_typed_input_tokens'],r.MAX_INPUT+1)
            self.assertEqual(c.receipt['known_typed_output_tokens'],2)

    def test_native_failed_call_preserves_known_usage_and_stops(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            c=self.campaign(tmp)
            result={'failure':'budget crossing','stats':{'provider_requests':1,'known_input_tokens':r.MAX_INPUT+1,'unknown_input_usage_requests':0}}
            with patch.object(c,'load'), patch.object(c,'cell',return_value=n.canonical(result)):
                with self.assertRaisesRegex(n.Stop,'typed_contract_or_resource_failure'): c.typed('pack-001',one())
            self.assertEqual(c.receipt['known_typed_input_tokens'],r.MAX_INPUT+1)
            self.assertEqual(c.receipt['typed_unknown_output_usage'],1)
            self.assertTrue(c.stopped)

    def test_invalid_probability_or_swapped_request_never_enters_reentry(self):
        for mutation in ('bool','out_of_range','request'):
            with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
                c=self.campaign(tmp); result=self.result(one())
                if mutation=='request': result['observation']['_azdaja']['request_sha256']='0'*64
                else: result['observation']['answers']['r0005']['noul']=True if mutation=='bool' else 1.1
                with patch.object(c,'load'),patch.object(c,'cell',return_value=n.canonical(result)) as cell:
                    with self.assertRaisesRegex(n.Stop,'answer_domain|typed_identity'): c.typed('pack-001',one())
                    self.assertEqual(cell.call_count,1)
                self.assertTrue(c.stopped)

    def test_configuration_writes_disabled_transport_and_no_generator(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            c=self.campaign(tmp)
            text=(c.work/'config.toml').read_text()
            self.assertIn('enabled=false',text)
            self.assertIn('sub_llm_cmd="/usr/bin/false"',text)
            self.assertIn('max_questions_per_cell=255',text)
            with self.assertRaisesRegex(n.Stop,'generative_disabled'): c.generate('forbidden',one())

    def test_live_exercise_cannot_silently_take_offline_branch(self):
        class Fake:
            def __init__(self): self.receipt={}; self.typed_names=[]
            def start(self): pass
            def load(self,*a): pass
            def checkpoint(self): pass
            def typed(self,name,pack): self.typed_names.append(name); return {'answers':{}}
            def configure(self,*a): pass
            def save(self,*a): pass
            def cell(self,name,code):
                self.assert_name=name
                return n.canonical({'complete':True,'attempts_in_reduction':0})
        c=Fake()
        with contextlib.redirect_stdout(io.StringIO()): r.exercise(c,[('pack-001',one()),('pack-002',one())],True)
        self.assertEqual(c.typed_names,['pack-001','pack-002'])
        self.assertEqual([x['status'] for x in c.receipt['panel_rows']],['completed','completed'])
        self.assertEqual(c.assert_name,'final-reduction')

    def test_cli_requires_explicit_live_acknowledgement_before_campaign(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            with patch.object(r,'packs',return_value=[]),patch.object(r,'inventory',return_value={}),patch.object(r,'Campaign',side_effect=AssertionError('no admission')),contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    r.main(['--live','--azdaja','/usr/bin/false','--output',str(Path(tmp)/'new')])
                self.assertEqual(error.exception.code,2)


if __name__=='__main__': unittest.main()
