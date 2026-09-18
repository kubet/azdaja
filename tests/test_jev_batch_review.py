import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / "examples" / "jev_batch_review.py"

class BatchReviewTests(unittest.TestCase):
    def run_prepare(self, out, question, *files):
        return subprocess.run([sys.executable, str(SCRIPT), "prepare", "--question", question, "--output", str(out), *map(str, files)], capture_output=True, text=True)

    def test_exact_utf8_byte_coverage_and_audit_fields(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR")) as td:
            root = Path(td); src = root / "long.txt"; out = root / "plan"
            data = ("žlutý řádek\n" * 12000).encode()
            src.write_bytes(data)
            r = self.run_prepare(out, "Does this source window contain the requested fact?", src)
            self.assertEqual(r.returncode, 0, r.stderr)
            rows = [json.loads(x) for x in (out / "plan.jsonl").read_text().splitlines()]
            rebuilt = b"".join(x["state"]["text"].encode() for x in rows)
            self.assertEqual(rebuilt, data)
            self.assertEqual([(x["state"]["start_byte"], x["state"]["end_byte"]) for x in rows], [(0, rows[0]["state"]["end_byte"])] + [(rows[i-1]["state"]["end_byte"], rows[i]["state"]["end_byte"]) for i in range(1, len(rows))])
            self.assertTrue(all(len((json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n").encode()) <= 65536 for x in rows))
            self.assertEqual(json.loads((out / "sources.json").read_text())[0]["source_sha256"], hashlib.sha256(data).hexdigest())
            self.assertIn("Does this source window", rows[0]["questions"]["match"]["instructions"])
            self.assertIn("only this source window", rows[0]["questions"]["match"]["instructions"])

    def test_same_basenames_get_distinct_stable_ids(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR")) as td:
            root = Path(td); a = root / "a"; b = root / "b"; a.mkdir(); b.mkdir()
            (a / "same.txt").write_text("one\n"); (b / "same.txt").write_text("two\n")
            out = root / "out"; self.assertEqual(self.run_prepare(out, "Q", a / "same.txt", b / "same.txt").returncode, 0)
            ids = [json.loads(x)["id"] for x in (out / "plan.jsonl").read_text().splitlines()]
            self.assertEqual(ids, ["000000-000000", "000001-000000"])

    def test_escaped_text_stays_bounded_and_long_question_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR")) as td:
            root = Path(td); src = root / "escaped.txt"
            src.write_bytes(('\\"\\\\\n' * 20000).encode())
            out = root / "out"
            self.assertEqual(self.run_prepare(out, "Q" * 4096, src).returncode, 0)
            for line in (out / "plan.jsonl").read_bytes().splitlines(True):
                self.assertLessEqual(len(line), 65536)
            self.assertNotEqual(self.run_prepare(root / "too-long", "Q" * 4097, src).returncode, 0)

    def test_refuses_bad_inputs_duplicate_and_overwrite(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR")) as td:
            root = Path(td); good = root / "good"; good.write_text("ok")
            for name, content in [("empty", b""), ("binary", b"a\0b")]:
                p = root / name; p.write_bytes(content)
                self.assertNotEqual(self.run_prepare(root / (name + "-out"), "Q", p).returncode, 0)
            self.assertNotEqual(self.run_prepare(root / "dup", "Q", good, good).returncode, 0)
            existing = root / "existing"; existing.mkdir(); self.assertNotEqual(self.run_prepare(existing, "Q", good).returncode, 0)
            link = root / "link"; link.symlink_to(good); self.assertNotEqual(self.run_prepare(root / "link-out", "Q", link).returncode, 0)



class ReportTests(unittest.TestCase):
    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('review', SCRIPT)
        self.review = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.review)
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = self.root / 'plan'
        self.job = self.root / 'job'
        self.job.mkdir()
        # Multiple chunks plus a distinct occurrence of exactly the same file text.
        data = ('Clause é 🐉 requires consent.\n' * 3000).encode()
        files=[]
        for i in range(2):
            d=self.root/str(i); d.mkdir(); p=d/'same.txt'; p.write_bytes(data); files.append(str(p))
        self.review.prepare('Does this contain an assignment restriction?', self.plan, files)
        self.rows = [json.loads(l) for l in (self.plan/'plan.jsonl').read_bytes().splitlines()]
        self.manifest = {'schema':'azdaja.judge_batch.job.v1','binding':{
            'input_sha256': hashlib.sha256((self.plan/'plan.jsonl').read_bytes()).hexdigest(),
            'config': {'model':'jev-latest'},
            'requests': [{'id':r['id'],'request_sha256':self.request_hash(r)} for r in self.rows]}}
        self.save(self.job/'manifest.json', self.manifest)
    def save(self,path,value): path.write_text(json.dumps(value,ensure_ascii=False))
    def request_hash(self,r):
        return self.review._canonical_hash({'model':'jev-latest','state':r['state'],'questions':r['questions']})
    def record(self,index,p=0.8):
        row=self.rows[index]
        intent={'schema':'azdaja.judge_batch.intent.v1','index':index,'id':row['id'],'request_sha256':self.request_hash(row)}
        self.save(self.job/f'{index:06}.intent.json',intent)
        record={'schema':'azdaja.judge_batch.result.v1','intent':intent,'status':'completed','observation':{
            'model':'jev-test','answers':{'match':{'type':'noul','noul':p}},'_azdaja':{'request_sha256':intent['request_sha256']}}}
        self.save(self.job/f'{index:06}.result.json',record)
        return record
    def output(self):
        p=self.root/'review.jsonl'
        self.review.report(self.plan,self.job,p)
        return [json.loads(l) for l in p.read_bytes().splitlines()]
    def test_complete_actual_shape_preserves_every_source_byte_and_occurrence(self):
        for i in range(len(self.rows)): self.record(i)
        rows=self.output()
        self.assertEqual(len(rows),len(self.rows))
        self.assertEqual([r['text'] for r in rows],[r['state']['text'] for r in self.rows])
        self.assertTrue(all(r['p']==0.8 and r['raw_answer']=={'type':'noul','noul':0.8} for r in rows))
        self.assertTrue(all(self.temp.name not in r['source_name'] for r in rows))
        self.assertEqual((self.root/'review.jsonl').stat().st_mode & 0o777,0o600)
    def test_partial_does_not_omit_unknown_or_unattempted_windows(self):
        self.record(0)
        failed=self.record(1); failed['status']='failed'; failed['observation']=None
        self.save(self.job/'000001.result.json',failed)
        self.record(2); (self.job/'000002.result.json').unlink()
        rows=self.output()
        self.assertEqual([r['status'] for r in rows[:4]],['completed','unknown','unknown_inflight','pending'])
        self.assertTrue(all(r['p'] is None for r in rows[1:]))
    def test_invalid_probability_and_boolean_index_rejected(self):
        for value in [True,-0.1,1.1,float('nan'),float('inf')]:
            self.record(0,value)
            with self.assertRaises(ValueError): self.output()
        good=self.record(0); good['intent']['index']=False
        self.save(self.job/'000000.result.json',good)
        with self.assertRaises(ValueError): self.output()
    def test_wrong_wire_hash_and_swapped_id_rejected(self):
        r=self.record(0)
        r['intent']['request_sha256']=self.review._canonical_hash(self.rows[0])
        self.save(self.job/'000000.result.json',r)
        with self.assertRaises(ValueError): self.output()
        r=self.record(0); r['intent']['id']=self.rows[1]['id']
        self.save(self.job/'000000.result.json',r)
        with self.assertRaises(ValueError): self.output()
    def test_rehashed_plan_text_cannot_bypass_original_source_bytes(self):
        self.rows[0]['state']['text']='X'+self.rows[0]['state']['text'][1:]
        data=b''.join(self.review._encode(r)+b'\n' for r in self.rows)
        (self.plan/'plan.jsonl').write_bytes(data)
        self.manifest['binding']['input_sha256']=hashlib.sha256(data).hexdigest()
        self.save(self.job/'manifest.json',self.manifest)
        with self.assertRaises(ValueError): self.output()
    def test_missing_intent_duplicate_json_key_and_output_links_rejected(self):
        self.record(0); (self.job/'000000.intent.json').unlink()
        with self.assertRaises(ValueError): self.output()
        r=self.record(0)
        (self.job/'000000.result.json').write_text('{"schema":"bad","schema":"bad"}')
        with self.assertRaises(ValueError): self.output()
        self.record(0); p=self.root/'review.jsonl'; p.symlink_to(self.root/'missing')
        with self.assertRaises(ValueError): self.output()
        self.assertFalse((self.root/'missing').exists())
    def test_symlinked_provider_result_rejected(self):
        self.record(0); p=self.job/'000000.result.json'; q=self.root/'foreign'; p.rename(q); p.symlink_to(q)
        with self.assertRaises((OSError,ValueError)): self.output()
    def test_one_multibyte_character_and_final_newline_do_not_make_extra_requests(self):
        for i,text in enumerate(['🐉','é','hello\n  ']):
            p=self.root/f'tiny{i}';p.write_text(text)
            out=self.root/f'tiny-plan{i}'
            self.review.prepare('Q',out,[str(p)])
            rows=(out/'plan.jsonl').read_bytes().splitlines()
            self.assertEqual(len(rows),1)
            self.assertEqual(json.loads(rows[0])['state']['text'],text)

if __name__ == '__main__':
    unittest.main()
