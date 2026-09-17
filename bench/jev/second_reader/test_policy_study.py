import math
import unittest

from . import policy_study as study


class PolicyStudyTests(unittest.TestCase):
    def test_complete_ids_and_same_state_are_deterministic(self):
        a, b = study.packs(), study.packs()
        self.assertEqual(a, b)
        self.assertEqual(sum(len(p["state"]["records"]) for p in a), 227)
        self.assertEqual(sum(len(p["questions"]) for p in a), 681)
        self.assertEqual(len(a), 11)
        for pack in a:
            self.assertLessEqual(len(pack["state"]["records"]), 21)
            self.assertLessEqual(len(study.canonical(pack["state"])), 24000)
            for qid, q in pack["questions"].items():
                _, rid = qid.split("_", 1)
                self.assertIn(f"state.records.{rid}", q["instructions"])
                self.assertNotIn("gold", q["instructions"].lower())
                self.assertNotIn("prediction", q["instructions"].lower())

    def test_variants_have_same_state_and_no_inference_fields(self):
        for pack in study.packs():
            self.assertNotIn("gold", pack["state"])
            self.assertNotIn("predictions", pack["state"])
            for rid in pack["state"]["records"]:
                self.assertEqual({f"v{v}_{rid}" for v in range(3)} & set(pack["questions"]), {f"v{v}_{rid}" for v in range(3)})

    def test_invalid_coverage_and_values_fail(self):
        with self.assertRaisesRegex(ValueError, "coverage"):
            study.validate_values({}, ["r0001"])
        for bad in (True, math.nan, -0.1, 1.1):
            with self.assertRaisesRegex(ValueError, "finite"):
                study.validate_values({"r0001": bad}, ["r0001"])

    def test_adjudication_replaces_only_four_and_preserves_wording(self):
        rows = [(f"r{i:04d}", "Date: May 1\\n") for i in range(1, 5)]
        pack = study.adjudication_pack(rows, [q for q, _ in rows])
        self.assertEqual(set(pack["questions"]), {f"original_r{i:04d}" for i in range(1, 5)})
        self.assertEqual(pack["questions"]["original_r0001"]["instructions"], study._question(0, "r0001")["instructions"])
        ledger = {f"r{i:04d}": bool(i % 2) for i in range(1, 6)}
        agreement = {"r0001": True}
        fresh = {f"r{i:04d}": bool(i % 2) for i in range(2, 6)}
        self.assertEqual(study.detached_adjudication_grade(agreement, fresh, ledger)["fullpanel_accuracy"], 1.0)

        gold = {"r0001": True, "r0002": False, "r0003": True}
        obs = {f"v{v}": {f"r{n:04d}": p for n, p in enumerate(row, 1)} for v, row in enumerate(((.9, .1, .8), (.8, .2, .7), (.6, .4, .3)))}
        report = study.detached_grade(obs, gold)
        self.assertEqual(set(report["variants"]), {"v0", "v1", "v2"})
        self.assertEqual(report["variants"]["v0"]["fp"], 0)
        self.assertEqual(report["variants"]["v2"]["fn"], 1)
        self.assertEqual(report["majority_vote"]["accuracy"], 1.0)
        self.assertEqual(report["unanimity"]["coverage"], 2 / 3)
        self.assertEqual(report["exact_vote_disagreement_ids"], ["r0003"])

    def test_v0_is_exact_prior_instructions_not_merely_similar(self):
        from bench.jev.angle_lab.gate.prepare_grade import request
        rows=study.selected_records()[:4]
        old=request(rows)
        for qid,_ in rows:
            self.assertEqual(study._question(0,qid),old['questions'][qid])
            self.assertEqual(study._question(None,qid),old['questions'][qid])

    def test_full_panel_adjudication_keeps_shared_errors_and_rejects_invalid_inputs(self):
        gold={str(i):False for i in range(227)}
        agreed={str(i):i<5 for i in range(223)}
        fresh={str(i):False for i in range(223,227)}
        result=study.detached_adjudication_grade(agreed,fresh,gold)
        self.assertEqual(result['correct'],222)
        self.assertEqual(result['retained_agreement_errors'],5)
        self.assertEqual(result['adjudicated_errors'],0)
        self.assertFalse(result['approval'])
        with self.assertRaises(ValueError): study.detached_adjudication_grade(dict(agreed,**{'223':False}),fresh,gold)
        with self.assertRaises(ValueError): study.detached_adjudication_grade(agreed,dict(fresh,**{'223':'no'}),gold)
        with self.assertRaises(ValueError): study.detached_adjudication_grade(agreed,fresh,dict(gold,**{'0':'false'}))

    def test_all_three_variants_and_strict_gold_required(self):
        obs={f'v{i}':{'a':.8} for i in range(3)}
        with self.assertRaises(ValueError): study.detached_grade(obs,{'a':'false'})
        with self.assertRaises(ValueError): study.detached_grade({'v0':obs['v0']},{'a':True})


if __name__ == "__main__":
    unittest.main()
