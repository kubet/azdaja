"""Offline tests of the actual progressive experiment policy, not model quality."""
import copy
import io
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run
from adapter import AdapterError, canonical_bytes


def fixtures():
    cases = []
    for split, count in (("smoke", 6), ("challenge", 30), ("holdout", 30)):
        for i in range(count):
            cases.append({"id": f"{split}-{i}", "split": split, "family": "offline",
                          "claim": f"claim-{split}-{i}", "evidence": f"evidence-{split}-{i}",
                          "expected": run.LABELS[i % 3], "rationale": "gold-must-not-be-sent"})
    return {"schema_version": 1, "task": "synthetic test of harness only", "cases": cases}


def answer(label, p=0.99, confidence=0.96):
    return {"type": "choice", "choice": label, "confidence": confidence,
            "probabilities": {k: p if k == label else (1 - p) / 2 for k in run.LABELS}}


class FakeClient:
    """Oracle is deliberately only a control-flow fixture, never efficacy evidence."""
    def __init__(self, data, mutate=None, failure=None):
        self.lookup = {c["claim"]: c["expected"] for c in data["cases"]}
        self.mutate = mutate
        self.failure = failure
        self.calls = []

    def evaluate(self, state, questions):
        self.calls.append((state, questions))
        if self.failure == len(self.calls):
            raise AdapterError("injected transport failure")
        answers = {}
        for i, record in enumerate(state["records"]):
            a = answer(self.lookup[record["claim"]])
            if self.mutate:
                a = self.mutate(len(self.calls), record, a)
            answers[f"q{i}"] = a
        return {"response": {"model": "fixture-only", "answers": answers,
                             "usage": {"input_tokens": 1, "output_tokens": 1}},
                "metrics": {"attempt": len(self.calls), "latency_ms": 0,
                            "request_bytes": 1, "response_bytes": 1, "estimated_input_tokens": 1}}


class RunnerTests(unittest.TestCase):
    def test_requests_never_contain_gold_or_metadata(self):
        cases = fixtures()["cases"][:6]
        for variant in ("ordinary", "reverse", "padding", "batch"):
            state, questions = run.request_for(cases, variant)
            self.assertEqual(set(state), {"records"})
            for original, record in zip(cases, state["records"]):
                self.assertEqual(set(record), {"claim", "evidence"})
                self.assertEqual(record["claim"], original["claim"])
                self.assertIn(original["evidence"], record["evidence"])
            raw = canonical_bytes({"state": state, "questions": questions})
            self.assertNotIn(b"gold-must-not-be-sent", raw)
            self.assertNotIn(b'"expected"', raw)
            self.assertNotIn(b'"split"', raw)
            self.assertEqual(list(questions), [f"q{i}" for i in range(6)])
            for i, q in enumerate(questions.values()):
                self.assertIn(f"records[{i}].claim", q["instructions"])
                self.assertIn(f"records[{i}].evidence", q["instructions"])

    def test_option_reversal_changes_serialized_transport_order(self):
        case = fixtures()["cases"][:1]
        ordinary = run.request_for(case)[1]
        reverse = run.request_for(case, "reverse")[1]
        self.assertEqual(list(ordinary["q0"]["criteria"]), list(reversed(reverse["q0"]["criteria"])))
        self.assertNotEqual(canonical_bytes(ordinary), canonical_bytes(reverse))

    def test_frozen_acceptance_boundary(self):
        self.assertTrue(run.accepted(answer("supported", 0.98, 0.90)))
        self.assertFalse(run.accepted(answer("supported", 0.979999, 0.99)))
        self.assertFalse(run.accepted(answer("supported", 0.99, 0.899999)))
        self.assertFalse(run.accepted(answer("insufficient", 0.8, 0.95)))

    def test_full_pipeline_control_flow_uses_79_requests_not_84(self):
        data = fixtures()
        client = FakeClient(data)
        result = run.run_campaign(client, data, {})
        self.assertEqual(result["status"], "semantic_screen_passed")
        self.assertEqual(len(client.calls), 79)
        self.assertEqual([s["status"] for s in result["stages"]], ["passed"] * 4)
        self.assertEqual(len(client.calls[-1][0]["records"]), 6)
        self.assertEqual(result["baseline"]["status"], "not_run")

    def test_smoke_stops_after_first_error(self):
        data = fixtures()
        client = FakeClient(data, mutate=lambda n, r, a: answer("contradicted") if n == 1 else a)
        result = run.run_campaign(client, data, {})
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(result["stop_reason"], "smoke_label_error")
        self.assertEqual(result["stages"][0]["summary"]["unobserved"], 5)
        self.assertEqual(len(result["stages"]), 1)

    def test_high_confidence_challenge_error_stops_no_holdout(self):
        data = fixtures()
        client = FakeClient(data, mutate=lambda n, r, a: answer("contradicted") if n == 7 else a)
        result = run.run_campaign(client, data, {})
        self.assertEqual(len(client.calls), 7)
        self.assertEqual(result["stop_reason"], "incorrect_auto_accepted_decision")
        self.assertEqual(result["stages"][1]["summary"]["observed"], 1)
        self.assertEqual(result["stages"][1]["summary"]["unobserved"], 29)
        self.assertEqual(len(result["stages"]), 2)

    def test_raw_accuracy_unreachable_stops_after_four_low_confidence_errors(self):
        def mutate(n, record, a):
            if n > 6:
                wrong = run.LABELS[(run.LABELS.index(a["choice"]) + 1) % 3]
                return answer(wrong, 0.7, 0.5)
            return a
        data = fixtures()
        client = FakeClient(data, mutate=mutate)
        result = run.run_campaign(client, data, {})
        self.assertEqual(len(client.calls), 10)
        self.assertEqual(result["stop_reason"], "raw_accuracy_bar_unreachable")

    def test_coverage_unreachable_stops_at_sixteen_abstentions(self):
        data = fixtures()
        client = FakeClient(data, mutate=lambda n, r, a: answer(a["choice"], 0.8, 0.7) if n > 6 else a)
        result = run.run_campaign(client, data, {})
        self.assertEqual(len(client.calls), 22)
        self.assertEqual(result["stop_reason"], "coverage_bar_unreachable")
        self.assertEqual(result["stages"][1]["summary"]["correct"], 16)
        self.assertEqual(result["stages"][1]["summary"]["accepted"], 0)

    def test_transport_failure_durable_and_no_retry(self):
        data = fixtures()
        client = FakeClient(data, failure=2)
        snapshots = []
        result = run.run_campaign(client, data, {}, lambda r: snapshots.append(copy.deepcopy(r)))
        self.assertEqual(len(client.calls), 2)
        self.assertEqual(result["stop_reason"], "adapter_error")
        self.assertEqual(result["calls"][1]["status"], "failed")
        self.assertTrue(any(s["calls"] and s["calls"][-1]["status"] == "attempting" for s in snapshots))
        self.assertEqual(result["stages"][0]["summary"]["observed"], 1)

    def test_invariance_failure_blocks_further_calls(self):
        data = fixtures()
        client = FakeClient(data, mutate=lambda n, r, a: answer("contradicted", 0.7, 0.5) if n == 67 else a)
        result = run.run_campaign(client, data, {})
        self.assertEqual(len(client.calls), 67)
        self.assertEqual(result["stop_reason"], "metamorphic_label_change")

    def test_crossing_failure_keeps_response_and_usage_without_claiming_pass(self):
        response = {"model": "fixture-only", "answers": {"q0": answer("supported")},
                    "usage": {"input_tokens": 101, "output_tokens": 1}}
        metrics = {"attempt": 1, "cumulative_reported_input_tokens": 101, "response_sha256": "f" * 64}
        class Crossing:
            def evaluate(self, state, questions):
                raise AdapterError("budget_input_tokens_exceeded", response=response, metrics=metrics)
        snapshots = []
        result = run.run_campaign(Crossing(), fixtures(), {}, lambda r: snapshots.append(copy.deepcopy(r)))
        self.assertEqual(result["error_code"], "budget_input_tokens_exceeded")
        self.assertEqual(result["calls"][0]["response"], response)
        self.assertEqual(result["calls"][0]["metrics"], metrics)
        self.assertNotIn("judgments", result["calls"][0])
        self.assertEqual(result["stages"][0]["summary"]["unobserved"], 6)
        self.assertEqual(snapshots[-1]["calls"][0]["status"], "failed")

    def test_interrupt_is_durable_and_does_not_start_next_call(self):
        class Interrupt:
            calls = 0
            def evaluate(self, state, questions):
                self.calls += 1
                raise KeyboardInterrupt
        client = Interrupt()
        snapshots = []
        result = run.run_campaign(client, fixtures(), {}, lambda r: snapshots.append(copy.deepcopy(r)))
        self.assertEqual(client.calls, 1)
        self.assertEqual(result["status"], "interrupted")
        self.assertEqual(result["calls"][0]["status"], "interrupted")
        self.assertEqual(result["stages"][0]["summary"]["observed"], 0)
        self.assertEqual(snapshots[-1], result)

    def test_pair_reporting_distinguishes_flips_from_correctness_and_missing_pairs(self):
        rows = [{"id": "c05", "answer": answer("contradicted"), "correct": False},
                {"id": "c06", "answer": answer("supported"), "correct": False}]
        result = run.pair_summary(rows)
        self.assertEqual(result["observed_pairs"], 1)
        self.assertEqual(result["unobserved_pairs"], 2)
        self.assertEqual(result["flip_rate_observed"], 1)
        self.assertEqual(result["both_correct_rate_observed"], 0)
        self.assertEqual(result["pairs"][0]["individual_errors"], 2)
        self.assertFalse(result["independent_extra_observations"])

    def test_invariance_rejects_same_wrong_label_becoming_auto_accepted(self):
        data = fixtures()
        def mutate(n, record, a):
            if n == 7:
                return answer("contradicted", 0.7, 0.5)
            if n == 67:
                return answer("contradicted", 0.99, 0.96)
            return a
        client = FakeClient(data, mutate=mutate)
        result = run.run_campaign(client, data, {})
        self.assertEqual(len(client.calls), 67)
        self.assertEqual(result["stop_reason"], "incorrect_auto_accepted_decision")

    def test_invariance_measures_application_acceptance_not_just_labels(self):
        data = fixtures()
        client = FakeClient(data, mutate=lambda n, r, a: answer(a["choice"], 0.7, 0.5) if n == 67 else a)
        result = run.run_campaign(client, data, {})
        self.assertEqual(result["stop_reason"], "metamorphic_acceptance_change")

    def test_exact_risk_bound_and_small_sample_warning(self):
        self.assertIsNone(run.error_upper_bound(0, 0))
        self.assertAlmostEqual(run.error_upper_bound(0, 30), 0.0950338529, places=9)
        self.assertGreater(run.error_upper_bound(0, 298), 0.01)
        self.assertLess(run.error_upper_bound(0, 299), 0.01)
        p = run.error_upper_bound(1, 30)
        self.assertAlmostEqual((1 - p) ** 30 + 30 * p * (1 - p) ** 29, 0.05)
        self.assertEqual(run.error_upper_bound(30, 30), 1)

    def test_fixture_schema_and_duplicate_rejections(self):
        data = fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixtures.json"
            path.write_text(json.dumps(data))
            loaded, hash_ = run.load_fixtures(path)
            self.assertEqual(len(loaded["cases"]), 66)
            self.assertEqual(len(hash_), 64)
            for mut in (lambda d: d["cases"].pop(),
                        lambda d: d["cases"][1].update(id=d["cases"][0]["id"]),
                        lambda d: d["cases"][0].update(expected="unlisted"),
                        lambda d: d["cases"][0].update(extra="forbidden")):
                bad = copy.deepcopy(data)
                mut(bad)
                path.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    run.load_fixtures(path)

    def test_key_file_private_nonsymlink_and_not_environment_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "key"
            path.write_text("synthetic-private-value\n")
            path.chmod(0o600)
            self.assertEqual(run.read_key(path), "synthetic-private-value")
            path.chmod(0o644)
            with self.assertRaises(ValueError): run.read_key(path)
            path.chmod(0o600)
            link = Path(tmp) / "link"
            link.symlink_to(path)
            with self.assertRaises(OSError): run.read_key(link)
            fifo = Path(tmp) / "fifo"
            os.mkfifo(fifo, 0o600)
            with self.assertRaises(ValueError): run.read_key(fifo)

    def test_checkpoint_exclusive_and_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            save = run.checkpoint_writer(path)
            save({"status": "running"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError): run.checkpoint_writer(path)
            save({"status": "stopped"})
            self.assertEqual(json.loads(path.read_text()), {"status": "stopped"})

    def test_default_cli_makes_no_client_or_credential_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixtures.json"
            path.write_text(json.dumps(fixtures()))
            with patch.object(run, "Client", side_effect=AssertionError("network forbidden")), \
                 patch.object(run, "read_key", side_effect=AssertionError("key read forbidden")), \
                 patch("sys.stdout", new_callable=io.StringIO) as out:
                self.assertEqual(run.main(["--fixtures", str(path)]), 0)
            self.assertEqual(json.loads(out.getvalue())["network_calls"], 0)


if __name__ == "__main__":
    unittest.main()
