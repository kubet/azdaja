import copy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import audit
import run


class ReceiptAuditTests(unittest.TestCase):
    def setUp(self):
        self.fixture_path = run.HERE / "fixtures.json"
        self.fixtures, self.fixture_hash = run.load_fixtures(self.fixture_path)
        self.receipt_path = run.HERE / "results/pilot-alias-20260916.json"
        self.receipt = json.loads(self.receipt_path.read_text())
        self.binary = Path(os.environ.get("AZDAJA_BINARY", "target/debug/azdaja")).resolve()
        self.scratch = Path(os.environ.get("JCODE_SCRATCH_DIR", str(Path.home() / ".jcode/scratch")))
        for target in ("socket.create_connection", "adapter.Client.evaluate"):
            guard = patch(target, side_effect=AssertionError("live inference forbidden"))
            guard.start()
            self.addCleanup(guard.stop)

    def test_actual_failed_receipts_replay_without_inference(self):
        for filename, code in (("pilot-20260916.json", "http_400"),
                               ("pilot-alias-20260916.json", "response_model_mismatch")):
            receipt = json.loads((run.HERE / "results" / filename).read_text())
            result = audit.verify(receipt, self.fixtures, self.fixture_hash)
            self.assertEqual(result["error_code"], code)
            self.assertEqual(result["stages"][0]["summary"]["observed"], 0)
            self.assertEqual(len(result["calls"]), 1)

    def test_tampering_fails_at_specific_identity_or_replay_check(self):
        mutations = [
            (lambda r: r.update(fixture_sha256="0" * 64), "receipt fixture identity mismatch"),
            (lambda r: r.update(policy_sha256="0" * 64), "receipt policy identity mismatch"),
            (lambda r: r.update(protocol_sha256="0" * 64), "receipt protocol identity mismatch"),
            (lambda r: r.update(source_revision="--help"), "invalid receipt revision"),
            (lambda r: r["implementation_sha256"].update(**{"run.py": "0" * 64}), "historical implementation identity mismatch"),
            (lambda r: r["calls"][0].update(state_sha256="0" * 64), "receipt request identity mismatch"),
            (lambda r: r["calls"][0]["metrics"].update(request_sha256="0" * 64), "receipt transport request mismatch"),
            (lambda r: r["calls"][0]["metrics"].update(worker_source_sha256="0" * 64), "receipt transport request mismatch"),
            (lambda r: r["stages"][0]["summary"].update(correct=6), "receipt replay disagrees with recorded result"),
            (lambda r: r.update(usage_complete=True), "receipt completeness or promotion mismatch"),
            (lambda r: r.update(production_promotion=True), "receipt completeness or promotion mismatch"),
            (lambda r: r.update(reported_input_tokens=100), "receipt usage total mismatch"),
            (lambda r: r.update(model_resolution_policy_sha256="0" * 64), "receipt model policy identity mismatch"),
        ]
        for mutate, message in mutations:
            receipt = copy.deepcopy(self.receipt)
            mutate(receipt)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, "^" + message + "$"):
                audit.verify(receipt, self.fixtures, self.fixture_hash)

    def test_extra_post_stop_call_and_missing_call_are_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["calls"].append(copy.deepcopy(receipt["calls"][0]))
        with self.assertRaisesRegex(ValueError, "^receipt contains calls after stopping condition$"):
            audit.verify(receipt, self.fixtures, self.fixture_hash)
        receipt["calls"] = []
        with self.assertRaisesRegex(ValueError, "^receipt ends before declared stopping condition$"):
            audit.verify(receipt, self.fixtures, self.fixture_hash)

    def test_strict_real_projection_does_not_turn_missing_judgments_into_success(self):
        with self.assertRaisesRegex(ValueError, "^evaluator rejected custody$"):
            audit.project(self.receipt_path, self.fixture_path, self.binary, self.scratch)

    def test_real_partial_projection_preserves_all_66_packs_and_two_duplicate_controls(self):
        artifact = audit.project(self.receipt_path, self.fixture_path, self.binary, self.scratch, audit_only=True)
        result = artifact["evaluation"]
        self.assertTrue(artifact["receipt_replay_consistent"])
        self.assertFalse(artifact["semantic_efficacy_established"])
        self.assertFalse(result["complete"])
        self.assertEqual(result["occurrences"], 68)
        self.assertEqual(result["unique_judged"], 0)
        self.assertEqual(result["raw_counts"], {"supported": 0, "contradicted": 0, "insufficient": 0, "unjudged": 68})
        self.assertEqual(result["unjudged_occurrences"], list(range(68)))
        self.assertEqual(len(result["ledger"]), 68)
        self.assertEqual(artifact["source"][0]["raw"], artifact["source"][-2]["raw"])
        self.assertEqual(artifact["source"][65]["raw"], artifact["source"][-1]["raw"])
        for case, row in zip(self.fixtures["cases"], artifact["source"]):
            self.assertEqual(json.loads(row["raw"]), {"claim": case["claim"], "evidence": case["evidence"]})
        self.assertEqual(artifact["manifest"]["entries"], [])


if __name__ == "__main__":
    unittest.main()
