import json
from pathlib import Path
import unittest

from . import audit


class DiagnosticAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.audit()

    def test_is_offline_and_rejected_batch_is_not_25_failures(self):
        self.assertEqual(self.report["provider_calls"], 0)
        self.assertEqual(self.report["credential_reads"], 0)
        rejected = self.report["rejected_flat02"]
        self.assertEqual(rejected["batch_questions"], 25)
        self.assertEqual(rejected["failed_response_count"], 0)
        self.assertEqual(len(rejected["unjudged_ids"]), 25)
        self.assertFalse(rejected["raw_body_retained"])
        self.assertFalse(rejected["exact_cause_recoverable"])

    def test_all_retained_successful_typed_bodies_are_complete_distributions(self):
        aggregate = self.report["retained_success_audit"]["aggregate"]
        self.assertEqual(aggregate["successful_typed_observations"], 11)
        self.assertEqual(aggregate["successful_typed_questions"], 275)
        self.assertEqual(aggregate["choice_questions"], 75)
        self.assertEqual(aggregate["noul_questions"], 200)
        self.assertTrue(aggregate["all_retained_choice_sums_within_rust_tolerance"])
        self.assertTrue(aggregate["all_retained_choice_domains_exact"])
        self.assertTrue(aggregate["all_retained_choice_winners_argmax"])
        self.assertEqual(aggregate["option_cardinalities"], {3: 5, 4: 70})
        self.assertGreaterEqual(aggregate["winner_gap_min"], 0)
        self.assertGreater(aggregate["sum_tolerance_margin_min"], 0)

    def test_source_inventory_covers_native_validator_sections(self):
        requirements = self.report["source_requirements"]
        self.assertGreaterEqual(len(requirements), 10)
        self.assertTrue(all(row["source_text_present"] for row in requirements))
        source = Path(audit.ROOT / "src/judge.rs").read_text()
        for needle in (
            "judge: probabilities must sum to one",
            "judge: answer IDs do not cover questions exactly",
            "judge: response byte limit exceeded",
            "judge: credential leakage refused",
        ):
            self.assertIn(needle, source)

    def test_report_is_json_serializable_without_raw_rejected_body(self):
        encoded = json.dumps(self.report)
        self.assertNotIn('"raw_body"', encoded)
        self.assertNotIn('"raw_response"', encoded)


if __name__ == "__main__":
    unittest.main()
