from __future__ import annotations
import hashlib
import importlib.util
import json
import os
import sys
import inspect
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("oolong_v58_under_test",HERE/"v58_run.py")
assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=m;SPEC.loader.exec_module(m)


def fake_suite(tmp: Path) -> m.PublicSuite:
    fixtures=[]
    for i in range(26):
        fid=f"fixture-{i:02d}";row=tmp/f"{fid}.json";ctx=tmp/f"{fid}.txt";row.write_text("{}\n");ctx.write_text("context\n")
        lf=m.legacy.Fixture(row_path=row,context_path=ctx,metadata={"question":"Give your final answer in the form 'Label: answer'."},expected_kind="",expected_value="",expected_canonical="",row_sha256=f"r{i}",context_sha256=f"c{i}",context_bytes=8,context_chars=8,context_lines=1)
        fixtures.append(m.PublicFixture(fid,row,ctx,lf.metadata["question"],f"r{i}",f"c{i}",lf))
    return m.PublicSuite(tmp/"manifest.json",m.PUBLIC_MANIFEST_SHA256,{},tuple(fixtures))


class V58RunTests(unittest.TestCase):
    def test_candidate_first_schedule_geometry(self):
        with tempfile.TemporaryDirectory() as td:
            schedule=m.build_schedule(fake_suite(Path(td)),{"sha256":m.CANDIDATE_SHA256},{"jcode":{},"prime-agent":{},"azdaja":{}})
        jobs=schedule["jobs"]
        self.assertEqual(len(jobs),78);self.assertEqual([j["ordinal"] for j in jobs],list(range(1,79)))
        self.assertTrue(all(j["arm"]=="jcode-azdaja" for j in jobs[:10]))
        self.assertTrue(all(j["arm"]!="jcode-azdaja" for j in jobs[10:30]))
        self.assertTrue(all(j["arm"]=="jcode-azdaja" for j in jobs[30:46]))
        self.assertTrue(all(j["arm"]!="jcode-azdaja" for j in jobs[46:]))
        pairs={(j["fixture_id"],j["arm"]) for j in jobs}
        self.assertEqual(len(pairs),78)
        first={j["fixture_id"] for j in jobs[:10]}
        self.assertEqual({j["fixture_id"] for j in jobs[10:30]},first)
        rest={j["fixture_id"] for j in jobs[30:46]}
        self.assertEqual({j["fixture_id"] for j in jobs[46:]},rest)
        self.assertEqual(len({j["run_id"] for j in jobs}),78)

    def test_recognition_is_question_derived_and_exact(self):
        q="Give your final answer in the form 'Label: answer' where answer is spam or ham."
        for good in ("Label: spam","Label: spam\n"):
            self.assertTrue(m.gold_blind_recognized(q,good))
        for bad in ("label: spam"," Label: spam","Label: spam ","Label: spam\r\n","Label: spam\nextra","spam","Label: a:b","Label: späm",""):
            self.assertFalse(m.gold_blind_recognized(q,bad),repr(bad))
        self.assertFalse(m.gold_blind_recognized("What is it?","Label: spam"))
        self.assertFalse(m.gold_blind_recognized(q+" Also form 'User: answer'.","Label: spam"))

    def test_checkpoint_boundaries_and_execution_coupling(self):
        q={f"f{i}":"Give your final answer in the form 'User: answer'." for i in range(10)}
        schedule={"checkpoint_policy":m.CHECKPOINT_POLICY}
        rows=[{"arm":"jcode-azdaja","fixture_id":f"f{i}","execution_success":i<8,"response":"User: 1\n" if i<7 else "bad"} for i in range(10)]
        got=m.checkpoint_summary(rows,schedule,q);self.assertTrue(got["passed"]);self.assertEqual((got["execution_n"],got["recognition_n"]),(8,7))
        rows[7]["execution_success"]=False;self.assertFalse(m.checkpoint_summary(rows,schedule,q)["passed"])
        rows[7]["execution_success"]=True;rows[6]["response"]="User: 1 \n";self.assertFalse(m.checkpoint_summary(rows,schedule,q)["passed"])

    def test_checkpoint_abort_is_sealed_and_refused(self):
        schedule={"schedule_id":"s","checkpoint_policy":m.CHECKPOINT_POLICY}
        questions={f"f{i}":"Give your final answer in the form 'User: [X]'." for i in range(10)}
        rows=[{"arm":"jcode-azdaja","fixture_id":f"f{i}","execution_success":i<7,"response":"User: 1\n" if i<7 else ""} for i in range(10)]
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);os.chmod(root,0o700);marker=root/"checkpoint.json"
            with self.assertRaises(m.CheckpointAbort):m.enforce_checkpoint_startup(rows,schedule,questions,marker)
            self.assertEqual(json.loads(marker.read_text())["status"],"abort")
            with self.assertRaises(m.CheckpointAbort):m.enforce_checkpoint_startup(rows,schedule,questions,marker)

    def test_optional_adapter_exact_response_contract(self):
        parameter=inspect.signature(m.legacy.run_one).parameters["return_exact_response"]
        self.assertIs(parameter.default,False)
        self.assertEqual(m.legacy.extract_final_exact("jcode-azdaja","Label: x\n"),"Label: x\n")

    def test_exact_final_never_strips(self):
        self.assertEqual(m.exact_final("jcode-azdaja","Label: spam\n"),"Label: spam\n")
        j=json.dumps({"type":"done","text":"User: 4\n"})+"\n";self.assertEqual(m.exact_final("jcode-native",j),"User: 4\n")
        large=(json.dumps({"type":"trace","payload":"x"*(2<<20)})+"\n"+j);self.assertEqual(m.exact_final("jcode-native",large),"User: 4\n")
        p=json.dumps({"type":"message_end","message":{"role":"assistant","content":[{"type":"text","text":"Label: ham\n"}]}})+"\n";self.assertEqual(m.exact_final("prime-agent",p),"Label: ham\n")

    def test_atomic_json_is_create_once_and_private(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);os.chmod(root,0o700);p=root/"x.json";m.atomic_json(p,{"b":2,"a":1})
            self.assertEqual(p.read_bytes(),b'{"a":1,"b":2}\n');self.assertEqual(p.stat().st_mode&0o777,0o600)
            with self.assertRaises(m.V58Error):m.atomic_json(p,{"x":1})

    def test_trailing_row_missing_done_is_recovered_without_rerun(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);os.chmod(root,0o700);output=root/"rows.jsonl";claims=root/"claims";claims.mkdir(mode=0o700)
            ex={"jcode":{"id":"j"},"prime-agent":{"id":"p"},"azdaja":{"id":"a"}};job={"ordinal":1,"run_id":"r","fixture_id":"f","row_sha256":"rh","context_sha256":"ch","arm":"prime-agent"};schedule={"schedule_id":"s","configuration":{"controller":{"sha256":"c"},"executables":ex},"jobs":[job]}
            row={"record_type":"inference","schedule_id":"s","run_id":"r","fixture_id":"f","row_sha256":"rh","context_sha256":"ch","execution_ordinal":1,"repetition":1,"arm":"prime-agent","candidate_sha256":m.CANDIDATE_SHA256,"controller_sha256":"c","model":m.MODEL,"reasoning":m.REASONING,"executables":m.legacy.expected_row_executables("prime-agent",ex),"scoring_status":"deferred","score":None,"success":None,"execution_success":True,"response":"Label: x\n"}
            m.atomic_json(claims/"r.json",{"schedule_id":"s","run_id":"r","ordinal":1});m.append_row(output,row)
            self.assertTrue(m.recover_trailing_done(output,schedule,claims));self.assertTrue((claims/"r.done.json").exists());self.assertFalse(m.recover_trailing_done(output,schedule,claims))

    def test_prefix_rejects_orphan_claim(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);os.chmod(root,0o700);output=root/"rows.jsonl";claims=root/"claims";claims.mkdir(mode=0o700)
            schedule={"schedule_id":"s","configuration":{"controller":{"sha256":"c"}},"jobs":[{"ordinal":1,"run_id":"r","fixture_id":"f","arm":"jcode-azdaja"}]}
            m.atomic_json(claims/"r.json",{"schedule_id":"s","run_id":"r","ordinal":1})
            with self.assertRaises(m.V58Error):m.validate_prefix(output,schedule,claims)


if __name__=="__main__":unittest.main()
