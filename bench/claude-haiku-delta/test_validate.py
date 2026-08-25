#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

BENCH = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("claude_delta_validate", BENCH / "validate.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("validator import failed")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
RUNNER_SPEC = importlib.util.spec_from_file_location("claude_delta_runner", BENCH / "run.py")
if RUNNER_SPEC is None or RUNNER_SPEC.loader is None:
    raise RuntimeError("runner import failed")
RUNNER = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(RUNNER)


class ClaudeHaikuDeltaValidationTests(unittest.TestCase):
    def test_frozen_five_pair_result_passes_every_gate(self) -> None:
        summary = VALIDATOR.validate()
        self.assertEqual(summary["pairs"], 5)
        self.assertEqual(summary["native_correct"], 4)
        self.assertEqual(summary["candidate_correct"], 5)
        self.assertEqual(summary["native_median_uncached"], 11904)
        self.assertEqual(summary["candidate_median_uncached"], 10027)
        self.assertEqual(summary["privacy_scan"], "passed")
        self.assertEqual(summary["hash_bindings"], "passed")

    def test_gate_raises_instead_of_accepting_false(self) -> None:
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.require(False, "expected failure")

    def test_runner_recomputes_the_frozen_v2_summary(self) -> None:
        result = json.loads((BENCH / "results/v1-result.json").read_text(encoding="utf-8"))
        summary = RUNNER.build_summary(result["rows"])
        for key in (
            "schema",
            "pairs",
            "native_correct",
            "candidate_correct",
            "native_mean_uncached",
            "candidate_mean_uncached",
            "native_median_uncached",
            "candidate_median_uncached",
            "native_mean_wall_seconds",
            "candidate_mean_wall_seconds",
            "native_median_wall_seconds",
            "candidate_median_wall_seconds",
            "native_mean_turns",
            "candidate_mean_turns",
            "candidate_exactly_one_successful_inner_each",
            "resolved_candidate_inner_model",
            "uncached_reduction_percent",
            "wall_reduction_percent",
        ):
            self.assertEqual(summary[key], result[key], key)

    def test_runner_records_a_timeout_instead_of_crashing(self) -> None:
        campaign = Path(tempfile.mkdtemp(prefix="claude-delta-timeout-test-"))
        try:
            timeout = subprocess.TimeoutExpired(cmd=["claude"], timeout=RUNNER.TIMEOUT)
            with mock.patch.object(RUNNER.subprocess, "run", side_effect=timeout):
                row = RUNNER.run_arm(campaign, 1, "native")
            self.assertEqual(row["returncode"], 124)
            self.assertTrue(row["timed_out"])
            self.assertEqual(row["parse_error"], "TimeoutExpired")
            self.assertIsNone(row["answer"])
            self.assertFalse(row["correct"])
            self.assertEqual(row["result_text"], "")
        finally:
            shutil.rmtree(campaign, ignore_errors=True)

    def test_runner_labels_a_missing_exact_answer_contract(self) -> None:
        campaign = Path(tempfile.mkdtemp(prefix="claude-delta-answer-contract-test-"))
        envelope = {
            "result": "I finished without the required final answer line.",
            "num_turns": 1,
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }
        completed = subprocess.CompletedProcess(
            ["claude"],
            0,
            json.dumps(envelope).encode("utf-8"),
            b"",
        )
        try:
            with mock.patch.object(RUNNER.subprocess, "run", return_value=completed):
                row = RUNNER.run_arm(campaign, 1, "native")
            self.assertEqual(row["returncode"], 0)
            self.assertFalse(row["timed_out"])
            self.assertEqual(row["parse_error"], "AnswerContractError")
            self.assertIsNone(row["answer"])
            self.assertFalse(row["correct"])
            self.assertEqual(row["result_text"], "")
        finally:
            shutil.rmtree(campaign, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
