"""Synthetic oracle controls for receipt plumbing, never evidence of Jev quality.

The actual CLI, adapter validation, policy, replay, and Monty evaluator run here.
Only the credential reader and HTTP transport are replaced. No worker or socket
may run, and the test-owned receipts are temporary rather than live evidence.
"""
from collections import Counter
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import adapter
import audit
import run
from test_run import answer


class CompleteReceiptTests(unittest.TestCase):
    def setUp(self):
        self.fixture_path = run.HERE / "fixtures.json"
        self.fixtures, self.fixture_hash = run.load_fixtures(self.fixture_path)
        self.binary = Path(os.environ.get("AZDAJA_BINARY", "target/debug/azdaja")).resolve(strict=True)
        self.scratch = Path(os.environ.get("JCODE_SCRATCH_DIR", str(Path.home() / ".jcode/scratch")))
        self.scratch.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="jev-synthetic-replay-", dir=self.scratch)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.lookup = {(case["claim"], case["evidence"]): case for case in self.fixtures["cases"]}
        self.assertEqual(len(self.lookup), 66)
        self.sent = []
        self.client = None

        original_popen = subprocess.Popen

        def guarded_popen(argv, *args, **kwargs):
            allowed_git = argv[0] == "git" and argv[1] in ("show", "status", "rev-parse")
            allowed_evaluator = Path(argv[0]) == self.binary
            if not (allowed_git or allowed_evaluator):
                raise AssertionError("unapproved child, including any adapter worker")
            return original_popen(argv, *args, **kwargs)

        guards = [
            patch.dict(os.environ, {
                "PATH": os.defpath, "JCODE_SCRATCH_DIR": str(self.scratch),
                "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0",
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            }, clear=True),
            patch("socket.create_connection", side_effect=AssertionError("network forbidden")),
            patch("socket.socket.connect", side_effect=AssertionError("network forbidden")),
            patch("http.client.HTTPSConnection", side_effect=AssertionError("HTTP forbidden")),
            patch("subprocess.Popen", side_effect=guarded_popen),
        ]
        for guard in guards:
            guard.start()
            self.addCleanup(guard.stop)

    def control_receipt(self, *, mutate=None, alias=False, input_tokens=10,
                        key="OFFLINE_CONTROL_NOT_A_PROVIDER_CREDENTIAL"):
        """Exercise the real CLI with explicitly oracle-supplied response bytes."""
        returned_model = "jev-offline-control"

        def transport(payload, *_):
            request = json.loads(payload)
            self.sent.append(request)
            answers = {}
            for qid, record in zip(request["questions"], request["state"]["records"]):
                evidence = record["evidence"]
                padding = "\n\n" + run.POLICY["s4_padding"]
                if evidence.endswith(padding):
                    evidence = evidence[:-len(padding)]
                case = self.lookup[(record["claim"], evidence)]
                value = answer(case["expected"])
                answers[qid] = mutate(case, value) if mutate else value
            return adapter.canonical_bytes({"model": returned_model, "answers": answers,
                "usage": {"input_tokens": input_tokens, "output_tokens": 1}})

        def factory(**kwargs):
            self.client = adapter.Client(**kwargs, transport=transport)
            return self.client

        path = self.root / "synthetic-control.json"
        argv = ["--live", "--model", "jev-latest" if alias else returned_model, "--receipt", str(path)]
        if alias:
            argv += ["--allow-resolved-model", returned_model]
        with patch.object(run, "read_key", return_value=key), \
                patch.object(run, "Client", side_effect=factory), patch("sys.stdout", new_callable=io.StringIO):
            code = run.main(argv)
        receipt = json.loads(path.read_text())
        receipt["evidence_origin"] = "offline_synthetic_oracle_transport_not_provider_evidence"
        path.write_text(json.dumps(receipt))
        self.assertEqual(len(self.sent), self.client._attempt)
        self.assertFalse(receipt["production_promotion"])
        return code, path, receipt

    def project(self, path, *, audit_only=False):
        return audit.project(path, self.fixture_path, self.binary, self.scratch, audit_only=audit_only)

    def test_complete_exact_model_control_replays_and_counts_every_occurrence(self):
        code, path, receipt = self.control_receipt()
        self.assertEqual(code, 0)
        self.assertEqual(receipt["status"], "semantic_screen_passed")
        self.assertEqual(len(self.sent), 79)
        self.assertEqual(receipt["baseline"]["status"], "not_run")
        artifact = self.project(path)
        result = artifact["evaluation"]
        self.assertFalse(artifact["semantic_efficacy_established"])
        self.assertTrue(result["complete"])
        self.assertEqual(result["unique_judged"], 66)
        self.assertEqual(result["occurrences"], 68)
        self.assertEqual(result["raw_counts"], {"supported": 23, "contradicted": 22, "insufficient": 23, "unjudged": 0})
        self.assertEqual(result["accepted_counts"], {"supported": 23, "contradicted": 22, "insufficient": 23})
        self.assertEqual(len(artifact["manifest"]["entries"]), 66)
        self.assertEqual([row["occurrence"] for row in result["ledger"]], list(range(68)))

    def test_complete_coverage_does_not_turn_abstentions_into_accepted_answers(self):
        abstained = {case["id"] for index, case in enumerate(self.fixtures["cases"]) if index % 2 == 0}
        def mutate(case, value):
            return answer(value["choice"], 0.8, 0.7) if case["id"] in abstained else value
        code, path, receipt = self.control_receipt(mutate=mutate)
        self.assertEqual(code, 0)
        self.assertEqual([stage["summary"]["accepted"] for stage in receipt["stages"][:3]], [3, 15, 15])
        artifact = self.project(path)
        result = artifact["evaluation"]
        cases = self.fixtures["cases"]
        expanded = cases + [cases[0], cases[-1]]
        expected = Counter(case["expected"] for case in expanded if case["id"] not in abstained)
        self.assertTrue(result["complete"])
        self.assertFalse(artifact["semantic_efficacy_established"])
        self.assertEqual(result["accepted_counts"], dict(expected))
        self.assertEqual(sum(result["accepted_counts"].values()), 34)
        self.assertEqual(len(artifact["manifest"]["entries"]), 66)
        for row, case in zip(result["ledger"], expanded):
            self.assertEqual(row["label"], case["expected"])
            self.assertEqual(row["accepted"], case["id"] not in abstained)

    def test_alias_control_pins_and_replays_without_changing_wire_alias(self):
        code, path, receipt = self.control_receipt(alias=True)
        self.assertEqual(code, 0)
        self.assertEqual({request["model"] for request in self.sent}, {"jev-latest"})
        self.assertEqual(self.client.resolved_model, "jev-offline-control")
        self.assertEqual({event["metrics"]["resolved_model_pin"] for event in receipt["calls"]}, {"jev-offline-control"})
        self.assertTrue(self.project(path)["evaluation"]["complete"])

    def test_semantic_stop_preserves_wrong_label_without_oracle_repair(self):
        case = next(case for case in self.fixtures["cases"] if case["id"] == "c01")
        wrong = next(label for label in run.LABELS if label != case["expected"])
        code, path, receipt = self.control_receipt(mutate=lambda case, value: answer(wrong) if case["id"] == "c01" else value)
        self.assertEqual(code, 2)
        self.assertEqual(receipt["stop_reason"], "incorrect_auto_accepted_decision")
        self.assertEqual(len(self.sent), 7)
        with self.assertRaisesRegex(ValueError, "^evaluator rejected custody$"):
            self.project(path)
        artifact = self.project(path, audit_only=True)
        row = next(row for row in artifact["manifest"]["entries"] if row["case_id"] == "c01")
        self.assertEqual(row["label"], wrong)
        self.assertTrue(row["accepted"])
        self.assertFalse(artifact["evaluation"]["complete"])
        self.assertFalse(artifact["semantic_efficacy_established"])
        self.assertEqual(artifact["evaluation"]["raw_counts"]["unjudged"], 60)

    def test_crossing_response_usage_is_retained_but_not_projected_as_eligible(self):
        code, path, receipt = self.control_receipt(input_tokens=600000)
        self.assertEqual(code, 2)
        self.assertEqual(receipt["error_code"], "reported_token_budget_exceeded")
        self.assertEqual(len(self.sent), 2)
        self.assertEqual(receipt["reported_input_tokens"], 1200000)
        self.assertIn("response", receipt["calls"][1])
        self.assertEqual(receipt["stages"][0]["summary"]["observed"], 1)
        artifact = self.project(path, audit_only=True)
        self.assertEqual([row["case_id"] for row in artifact["manifest"]["entries"]], ["s01"])
        self.assertEqual(artifact["evaluation"]["raw_counts"], {"supported": 2, "contradicted": 0, "insufficient": 0, "unjudged": 66})
        self.assertFalse(artifact["evaluation"]["complete"])

    def test_completed_receipt_cannot_erase_transport_evidence(self):
        _, _, receipt = self.control_receipt()
        for replacement in ({}, None, [], False, 0, "", "omit"):
            changed = copy.deepcopy(receipt)
            if replacement == "omit":
                changed["calls"][0].pop("metrics")
            else:
                changed["calls"][0]["metrics"] = replacement
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, "^receipt transport evidence missing$"):
                audit.verify(changed, self.fixtures, self.fixture_hash)

    def assert_budget_crossing_rejected(self, *, alias=False):
        _, _, receipt = self.control_receipt(alias=alias)
        changed = copy.deepcopy(receipt)
        delta = adapter.Limits().max_input_tokens
        changed["calls"][0]["response"]["usage"]["input_tokens"] += delta
        changed["reported_input_tokens"] += delta
        raw = adapter.canonical_bytes(changed["calls"][0]["response"])
        changed["calls"][0]["metrics"].update(response_bytes=len(raw), response_sha256=audit.sha(raw))
        changed["input_cost_estimate_usd_vendor_rate"] = changed["reported_input_tokens"] * 0.042 / 1000000
        for event in changed["calls"]:
            event["metrics"]["cumulative_reported_input_tokens"] += delta
        with self.assertRaisesRegex(ValueError, "^completed receipt exceeds resource envelope$"):
            audit.verify(changed, self.fixtures, self.fixture_hash)

    def test_completed_receipt_cannot_hide_a_reported_token_budget_crossing(self):
        self.assert_budget_crossing_rejected()

    def test_alias_cannot_bind_on_a_completed_but_over_budget_first_response(self):
        self.assert_budget_crossing_rejected(alias=True)

    def test_exact_reported_token_limit_remains_eligible(self):
        _, _, receipt = self.control_receipt()
        delta = adapter.Limits().max_input_tokens - receipt["reported_input_tokens"]
        receipt["calls"][0]["response"]["usage"]["input_tokens"] += delta
        receipt["reported_input_tokens"] += delta
        raw = adapter.canonical_bytes(receipt["calls"][0]["response"])
        receipt["calls"][0]["metrics"].update(response_bytes=len(raw), response_sha256=audit.sha(raw))
        receipt["input_cost_estimate_usd_vendor_rate"] = receipt["reported_input_tokens"] * 0.042 / 1000000
        for event in receipt["calls"]:
            event["metrics"]["cumulative_reported_input_tokens"] += delta
        result = audit.verify(receipt, self.fixtures, self.fixture_hash)
        self.assertEqual(result["status"], "semantic_screen_passed")

    def test_genuine_preflight_failure_needs_no_fabricated_transport_metrics(self):
        # This synthetic token deliberately occurs in the question instructions.
        # Assert the intended guard, not just any exception from a short token.
        code, path, receipt = self.control_receipt(key="Classify")
        self.assertEqual(code, 2)
        self.assertEqual(receipt["error_code"], "credential_in_request_state")
        self.assertEqual(len(self.sent), 0)
        self.assertEqual(len(receipt["calls"]), 1)
        self.assertNotIn("metrics", receipt["calls"][0])
        result = self.project(path, audit_only=True)["evaluation"]
        self.assertFalse(result["complete"])
        self.assertEqual(result["raw_counts"]["unjudged"], 68)

    def test_transport_metric_mutations_fail_at_specific_contract_checks(self):
        _, _, receipt = self.control_receipt()
        changes = [
            ({"attempt": True}, "receipt transport request mismatch"),
            ({"estimated_input_tokens": 0}, "receipt transport request mismatch"),
            ({"response_bytes": -1}, "invalid receipt transport metrics"),
            ({"response_bytes": True}, "invalid receipt transport metrics"),
            ({"latency_ms": True}, "invalid receipt transport metrics"),
            ({"latency_ms": float("nan")}, "invalid receipt transport metrics"),
            ({"response_sha256": "invalid"}, "receipt response evidence missing"),
            ({"response_bytes": None}, "receipt response accounting mismatch"),
            ({"cumulative_reported_input_tokens": 0}, "receipt response accounting mismatch"),
            ({"returned_model": "jev-another-control"}, "receipt returned model mismatch"),
        ]
        for fields, code in changes:
            changed = copy.deepcopy(receipt)
            changed["calls"][0]["metrics"].update(fields)
            with self.subTest(fields=fields), self.assertRaisesRegex(ValueError, "^" + code + "$"):
                audit.verify(changed, self.fixtures, self.fixture_hash)

    def test_failed_http_receipt_cannot_erase_its_attempted_transport_evidence(self):
        receipt = json.loads((run.HERE / "results/pilot-alias-20260916.json").read_text())
        receipt["calls"][0]["metrics"] = {}
        with self.assertRaisesRegex(ValueError, "^receipt transport evidence missing$"):
            audit.verify(receipt, self.fixtures, self.fixture_hash)

    def test_historical_git_reads_disable_lazy_fetch_and_do_not_inherit_credentials(self):
        _, _, receipt = self.control_receipt()
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "synthetic_environment_marker"}), \
                patch.object(audit.subprocess, "check_output", wraps=subprocess.check_output) as execute:
            audit.verify(receipt, self.fixtures, self.fixture_hash)
        self.assertEqual(execute.call_count, 2)
        for call in execute.call_args_list:
            self.assertEqual(call.args[0][:2], ["git", "show"])
            self.assertEqual(call.kwargs["env"], {
                "PATH": os.defpath, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0",
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            })

    def test_receipt_cannot_claim_different_thresholds_or_fabricated_custody(self):
        _, _, receipt = self.control_receipt()
        changed = copy.deepcopy(receipt)
        changed["acceptance_policy"]["selected_probability_min"] = 0
        with self.assertRaisesRegex(ValueError, "^receipt acceptance policy mismatch$"):
            audit.verify(changed, self.fixtures, self.fixture_hash)
        changed = copy.deepcopy(receipt)
        changed["custody"] = {"status": "passed"}
        with self.assertRaisesRegex(ValueError, "^receipt replay disagrees with recorded result$"):
            audit.verify(changed, self.fixtures, self.fixture_hash)


if __name__ == "__main__":
    unittest.main()
