import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import validate


HERE = Path(__file__).resolve().parent


class DeltaPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        bench = Path(self.temp.name) / "bench"
        self.delta = bench / "delta"
        oolong = bench / "oolong"
        self.delta.mkdir(parents=True)
        oolong.mkdir(parents=True)
        for name in ("plan.json", "prompt.txt", "candidate-prefix.txt"):
            shutil.copyfile(HERE / name, self.delta / name)
        source_oolong = HERE.parent / "oolong"
        for name in ("context-131072.txt", "row-645.json"):
            shutil.copyfile(source_oolong / name, oolong / name)
        self.plan_path = self.delta / "plan.json"
        self.plan = json.loads(self.plan_path.read_text())

    def tearDown(self):
        self.temp.cleanup()

    def write(self, plan):
        self.plan_path.write_text(json.dumps(plan, sort_keys=True))

    def assert_blocked(self, mutate):
        plan = copy.deepcopy(self.plan)
        mutate(plan)
        self.write(plan)
        with self.assertRaises(validate.PlanError):
            validate.validate(self.plan_path)

    def test_valid_plan(self):
        result = validate.validate(self.plan_path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["selected_records"], 227)
        self.assertEqual(result["unique_decision_evidence"], 226)
        self.assertEqual(result["maximum_candidate_inner_attempts_per_harness"], 1)

    def test_model_and_reasoning_are_luna_low_only(self):
        self.assert_blocked(lambda p: p["model"].__setitem__("codex", "gpt-5.4-mini"))
        self.assert_blocked(lambda p: p["model"].__setitem__("outer_reasoning", "high"))

    def test_no_retry_and_one_inner_attempt_are_exact(self):
        self.assert_blocked(lambda p: p["execution"].__setitem__("retry", True))
        self.assert_blocked(lambda p: p["execution"].__setitem__("candidate_inner_attempt_ceiling", 2))
        self.assert_blocked(lambda p: p["execution"].__setitem__("candidate_config_max_calls_per_cell", 2))
        self.assert_blocked(lambda p: p["execution"].__setitem__("candidate_transaction_ceiling", 2))

    def test_compact_shard_contract_is_exact(self):
        self.assert_blocked(lambda p: p["execution"].__setitem__("max_unique_items_per_shard", 80))
        self.assert_blocked(lambda p: p["execution"].__setitem__("workers", 12))

    def test_schedule_is_two_parallel_harness_pairs(self):
        self.assert_blocked(lambda p: p["execution"].__setitem__("parallel_groups", [["codex/native"]]))

    def test_prompt_and_fixture_hashes_are_bound(self):
        self.assert_blocked(lambda p: p["prompts"].__setitem__("shared_sha256", "0" * 64))
        self.assert_blocked(lambda p: p["fixture"].__setitem__("context_sha256", "0" * 64))

    def test_quality_and_efficiency_gates_are_required(self):
        self.assert_blocked(lambda p: p["gates"].__setitem__("quality_first", False))
        self.assert_blocked(lambda p: p["gates"].__setitem__("candidate_outer_tokens_must_be_lower", False))
        self.assert_blocked(lambda p: p["gates"].__setitem__("candidate_total_tokens_must_be_lower", False))
        self.assert_blocked(lambda p: p["gates"].__setitem__("candidate_wall_seconds_must_be_lower", False))

    def test_extra_keys_fail_closed(self):
        self.assert_blocked(lambda p: p.__setitem__("notes", "not allowed"))


if __name__ == "__main__":
    unittest.main()
