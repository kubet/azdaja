import json
import math
import sys
import unittest
from pathlib import Path

REVIEW = Path(__file__).resolve().parent
ROOT = REVIEW.parents[3]
sys.path.insert(0, str(REVIEW))

from metrics import (  # noqa: E402
    agreement_table,
    brier_score,
    positive_probability_ece,
    summarize,
    top_label_ece,
)


class FixedPanelMetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / "bench/jev/row645_labels/result.json").read_text())
        cls.records = cls.source["occurrence_ledger"]

    def test_brier_matches_retained_official_result(self):
        self.assertEqual(len(self.records), 227)
        self.assertTrue(math.isclose(brier_score(self.records), self.source["brier_score"], rel_tol=0, abs_tol=1e-15))

    def test_positive_probability_five_bins_match_declared_official_bins(self):
        measured = positive_probability_ece(self.records, 5)
        self.assertEqual([bucket["count"] for bucket in measured["bins"]], [76, 8, 5, 7, 131])
        for measured_bucket, official_bucket in zip(measured["bins"], self.source["reliability_bins"]):
            self.assertEqual(measured_bucket["count"], official_bucket["n"])
            self.assertTrue(math.isclose(measured_bucket["mean_probability"], official_bucket["mean_p_ham"], abs_tol=1e-15))
            self.assertTrue(math.isclose(measured_bucket["observed_positive_rate"], official_bucket["observed_ham_fraction"], abs_tol=1e-15))

    def test_ten_equal_width_bins_are_predeclared_and_cover_panel(self):
        measured = positive_probability_ece(self.records, 10)
        self.assertEqual(len(measured["bins"]), 10)
        self.assertEqual([bucket["count"] for bucket in measured["bins"]], [71, 5, 4, 4, 4, 1, 1, 6, 9, 122])
        self.assertTrue(math.isclose(measured["ece"], 0.06766519823788547, abs_tol=1e-15))
        self.assertEqual(measured["bins"][0]["interval"], "[0.0, 0.1)")
        self.assertEqual(measured["bins"][-1]["interval"], "[0.9, 1.0]")
        self.assertEqual(measured["binning"], "equal width; [lower, upper) except final [lower, 1.0]")

    def test_top_label_ece_is_distinct_from_positive_probability_ece(self):
        positive = top_label_ece(self.records, 5)
        probability = positive_probability_ece(self.records, 5)
        self.assertNotEqual(positive["definition"], probability["definition"])
        self.assertEqual(sum(bucket["count"] for bucket in positive["bins"]), 227)

    def test_agreement_disagreement_and_hypothetical_oracle_summary(self):
        measured = agreement_table(self.records)
        self.assertEqual(measured["agreement_count"], 223)
        self.assertEqual(measured["disagreement_count"], 4)
        self.assertEqual(len(measured["agreement_error_ids"]), 5)
        self.assertEqual(len(measured["disagreement_error_ids"]), 0)
        self.assertEqual(
            measured["agreement_error_ids"],
            ["r0044", "r0503", "r1383", "r1394", "r1747"],
        )
        oracle = measured["hypothetical_oracle_ceiling_if_all_disagreements_resolved"]
        self.assertTrue(oracle["hypothetical"])
        self.assertEqual(oracle["resolved_disagreements"], 4)
        self.assertEqual(oracle["remaining_errors"], 5)
        self.assertTrue(math.isclose(oracle["accuracy_ceiling"], 222 / 227))

    def test_summary_contains_both_ece_families(self):
        measured = summarize(self.records)
        self.assertEqual(measured["n"], 227)
        self.assertEqual(set(measured["positive_probability_ece"]), {"5", "10"})
        self.assertEqual(set(measured["top_label_ece"]), {"5", "10"})

    def test_all_disagree_has_none_agreement_rate(self):
        records = [
            {"id": "a", "p_ham": 0.9, "gold_ham": True, "typed_ham": True, "direct_ham": False},
            {"id": "b", "p_ham": 0.1, "gold_ham": False, "typed_ham": False, "direct_ham": True},
        ]
        measured = agreement_table(records)
        self.assertEqual(measured["agreement_count"], 0)
        self.assertEqual(measured["disagreement_count"], 2)
        self.assertIsNone(measured["actual_error_floor_on_agreement"]["rate_among_agreements"])
        self.assertEqual(measured["hypothetical_oracle_ceiling_if_all_disagreements_resolved"]["remaining_errors"], 0)

    def test_validation_rejects_bad_probability_types_finiteness_ids_and_threshold(self):
        valid = {"id": "x", "p_ham": 0.9, "gold_ham": True, "typed_ham": True, "direct_ham": True}
        with self.assertRaises(TypeError):
            brier_score([{**valid, "p_ham": True}])
        with self.assertRaises(ValueError):
            brier_score([{**valid, "p_ham": float("nan")}])
        with self.assertRaises(ValueError):
            brier_score([{**valid, "p_ham": float("inf")}])
        with self.assertRaises(ValueError):
            brier_score([valid, dict(valid)])
        with self.assertRaises(ValueError):
            brier_score([{**valid, "p_ham": 0.1, "typed_ham": True}])
        with self.assertRaises(TypeError):
            brier_score([{**valid, "direct_ham": 1}])

    def test_validation_rejects_bool_string_gold(self):
        valid = {"id": "x", "p_ham": 0.9, "gold_ham": True, "typed_ham": True, "direct_ham": True}
        for value in ("true", "false", "1", "0"):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    brier_score([{**valid, "gold_ham": value}])


if __name__ == "__main__":
    unittest.main()
