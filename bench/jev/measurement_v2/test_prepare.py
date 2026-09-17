import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from . import prepare as p, run
from bench.jev.angle_lab import native as n


class PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Path(os.environ['JCODE_SCRATCH_DIR'])/'jev-squad-dev-v2.0-20260917.json'
        cls.artifacts=p.assemble(*p.select(cls.source))

    def test_exact_source_regeneration_and_unique_panels(self):
        for name,value in self.artifacts.items():
            self.assertEqual(value,n.strict_loads((p.HERE/'fixtures'/name).read_bytes()))
        rows=self.artifacts['sources.json']; gold=self.artifacts['gold.json']
        self.assertEqual(len({r['normalized_sha256'] for r in rows}),300)
        self.assertEqual(len({r['official_qa_id'] for r in rows}),300)
        self.assertEqual(sum(g['expected']=='no_match' for g in gold.values()),25)
        self.assertEqual(sum(g['lane']=='verifier' and g['expected']=='no' for g in gold.values()),100)
        self.assertEqual(sum(g['lane']=='verifier' and g['expected']=='yes' for g in gold.values()),100)

    def test_raw_coverage_exact_spans_and_semantic_case_binding(self):
        by_id={r['id']:r for r in self.artifacts['sources.json']}
        for entry in self.artifacts['packs.json']:
            pack=entry['pack']
            self.assertLessEqual(len(n.canonical(pack['state'])),24000)
            self.assertEqual(len(pack['questions']),25)
            for qid,question in pack['questions'].items():
                source=by_id[qid]; raw=source['context'].encode()
                self.assertIn('state.cases.'+qid,question['instructions'])
                expected_question = source['question'] if entry['lane']=='flat' else json.dumps(source['question'],ensure_ascii=False)
                self.assertIn(expected_question,question['instructions'])
                state=pack['state']['cases'][qid]
                if entry['lane']=='flat':
                    self.assertEqual(''.join(state['windows'].values()).encode(),raw)
                    self.assertEqual(set(question['criteria']),set(state['windows'])|{'no_match'})
                else:
                    self.assertEqual(state.encode(),raw)
                for w in source['windows']:
                    self.assertEqual(raw[w['start_byte']:w['end_byte']],w['text'].encode())
                self.assertNotIn(source['official_qa_id'],n.canonical(pack).decode())
            self.assertNotIn('is_impossible',n.canonical(pack).decode())
            self.assertNotIn('answer_start',n.canonical(pack).decode())
        self.assertEqual(len(self.artifacts['packs.json']),12)
        self.assertEqual(len(run.packs()),12)

    def test_unicode_offsets_are_not_character_offsets(self):
        text='😀 alpha βeta target'
        span=p.answer_span(text,{'answer_start':text.index('target'),'text':'target'})
        self.assertEqual(text.encode()[span['start_byte']:span['end_byte']],b'target')
        self.assertGreater(span['start_byte'],text.index('target'))
        with self.assertRaisesRegex(ValueError,'source mismatch'):
            p.answer_span(text,{'answer_start':span['start_byte'],'text':'target'})

    def test_all_annotations_must_share_one_window(self):
        text='first '+('x '*150)+'last'
        row={'context':text,'windows':p.windows(text),'is_impossible':False,
             'answers':[{'answer_start':0,'text':'first'},{'answer_start':text.index('last'),'text':'last'}]}
        self.assertIsNone(p.flat_label(row))
        row['answers']=[{'answer_start':0,'text':'first'}]
        self.assertEqual(p.flat_label(row),'w0')
        text='first '+('x '*150)+'first'
        row.update(context=text,windows=p.windows(text))
        self.assertIsNone(p.flat_label(row))

    def test_cross_boundary_answer_is_not_arbitrarily_assigned(self):
        text='a '*240
        ws=p.windows(text); boundary=ws[0]['end_byte']
        row={'context':text,'windows':ws,'is_impossible':False,
             'answers':[{'answer_start':boundary-2,'text':text[boundary-2:boundary+2]}]}
        self.assertIsNone(p.flat_label(row))
        unicode=' 😀 data\n'*100
        self.assertEqual(''.join(w['text'] for w in p.windows(unicode)),unicode)

    def test_forged_fixture_and_default_live_admission(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as root:
            path=Path(root)/'packs.json'
            path.write_bytes(n.canonical(self.artifacts['packs.json']))
            campaign=SimpleNamespace(frozen={str(path):n.sha(path.read_bytes())},stopped=False)
            n.Campaign.check_frozen(campaign)
            malformed=copy.deepcopy(self.artifacts['packs.json'])
            malformed[0]['pack']['questions']['invented']=malformed[0]['pack']['questions'].pop('f000')
            path.write_bytes(n.canonical(malformed))
            with self.assertRaisesRegex(n.Stop,'frozen_source_changed'):
                n.Campaign.check_frozen(campaign)
            self.assertTrue(campaign.stopped)
        with patch.object(run,'HERE',Path('/nonexistent')):
            with self.assertRaises(FileNotFoundError): run.packs()
        process=subprocess.run([sys.executable,'-B','-m','bench.jev.measurement_v2.run'],capture_output=True,text=True,timeout=10)
        self.assertEqual(process.returncode,0)
        self.assertEqual(n.strict_loads(process.stdout)['provider_calls'],0)

    def test_existing_output_not_overwritten(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as root:
            output=Path(root)/'fixture'; output.mkdir(); sentinel=output/'keep'; sentinel.write_text('keep')
            with self.assertRaises(FileExistsError): p.prepare(self.source,output)
            self.assertEqual(sentinel.read_text(),'keep')


if __name__=='__main__': unittest.main()
