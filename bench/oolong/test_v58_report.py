from __future__ import annotations
import importlib.util,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("oolong_v58_report_under_test",HERE/"v58_report.py");assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=m;SPEC.loader.exec_module(m)

def case(execution=25,strict=24,gate=True):
    jobs=[];rows=[];n=0
    for arm in m.run.ARMS:
        for i in range(26):
            n+=1;rid=f"r{n}";jobs.append({"run_id":rid,"fixture_id":f"f-{arm}-{i}","arm":arm,"ordinal":n})
            ok=True;correct=True
            if arm=="jcode-azdaja":ok=i<execution;correct=i<strict
            rows.append({"run_id":rid,"fixture_id":f"f-{arm}-{i}","arm":arm,"execution_ordinal":n,"execution_success":ok,"strict_correct":correct})
    terminal={"validated":True,"integrity_gate":gate,"route_gate":gate,"leak_gate":gate,"credential_cleanup_gate":gate}
    scores={"record_type":"oolong_v58_scores","campaign":"v58-low-candidate-first-v1","schedule_id":"s","candidate_sha256":m.run.CANDIDATE_SHA256,"terminal_receipt":terminal,"scores":rows}
    return scores,{"schedule_id":"s","jobs":jobs}
SCORE_SPEC=importlib.util.spec_from_file_location("oolong_v58_score_under_test",HERE/"v58_score.py");assert SCORE_SPEC and SCORE_SPEC.loader
score=importlib.util.module_from_spec(SCORE_SPEC);sys.modules[SCORE_SPEC.name]=score;SCORE_SPEC.loader.exec_module(score)
class ReportTests(unittest.TestCase):
    def test_strict_correct_allows_only_optional_single_lf(self):
        self.assertTrue(score.strict_correct("Label: spam","Label: spam"));self.assertTrue(score.strict_correct("Label: spam\n","Label: spam"))
        for bad in (" Label: spam","Label: spam ","Label: spam\r\n","Label: spam\n\n","Label: spam\t"):
            self.assertFalse(score.strict_correct(bad,"Label: spam"),repr(bad))
    def test_25_24_passes(self):self.assertTrue(m.build_report(*case())["gates"]["continuation_pass"])
    def test_24_execution_fails(self):self.assertFalse(m.build_report(*case(execution=24))["gates"]["continuation_pass"])
    def test_23_exact_fails(self):self.assertFalse(m.build_report(*case(strict=23))["gates"]["continuation_pass"])
    def test_any_integrity_gate_fails(self):self.assertFalse(m.build_report(*case(gate=False))["gates"]["continuation_pass"])
    def test_score_inference_execution_mismatch_rejected(self):
        scores,schedule=case();inference=[{"run_id":r["run_id"],"fixture_id":r["fixture_id"],"arm":r["arm"],"execution_ordinal":r["execution_ordinal"],"execution_success":r["execution_success"]} for r in scores["scores"]]
        inference[-1]["execution_success"]=not inference[-1]["execution_success"]
        with self.assertRaises(m.ReportError):m.build_report(scores,schedule,inference)

    def test_no_downstream_authorization(self):
        auth=m.build_report(*case())["authorization"];self.assertEqual(auth,{**auth,"rah_authorized":False,"publication_authorized":False,"release_authorized":False})
    def test_strict_requires_execution(self):
        report=m.build_report(*case(execution=25,strict=26));self.assertEqual(report["metrics"]["jcode-azdaja"]["strict_exact_n"],25)
if __name__=="__main__":unittest.main()
