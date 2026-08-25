#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

BENCH = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("claude_delta_validate", BENCH / "validate.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("validator import failed")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


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


if __name__ == "__main__":
    unittest.main()
