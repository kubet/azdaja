import os
import stat
import tempfile
import unittest
from pathlib import Path

import run


class DeltaRunnerContractTests(unittest.TestCase):
    def test_fixture_is_large_compact_clear_and_exact(self):
        validated = run.FIXTURE.validate()
        self.assertEqual(validated["context_sha256"], "d09d8b823db598a53a2fa405448ae1b08f1f2f64650f7a3f09af98d7135284eb")
        self.assertEqual(validated["context_bytes"], 1_306_076)
        self.assertEqual(validated["total_records"], 306)
        self.assertEqual(validated["selected_records"], 226)
        self.assertEqual(validated["unique_decision_evidence"], 226)
        self.assertEqual(validated["expected_answer"], 149)
        self.assertLess(validated["compact_evidence_bytes"], 65_536)

    def test_primary_uncached_formula_is_exact(self):
        usage = {
            "input": 100,
            "output": 7,
            "reasoning": 3,
            "cache": {"read": 40, "write": 5},
        }
        self.assertEqual(run.usage_uncached_total(usage), 75)
        self.assertEqual(run.usage_gross_total(usage), 115)
        usage["cache"]["read"] = 101
        with self.assertRaises(ValueError):
            run.usage_uncached_total(usage)
        self.assertEqual(run.integer_delta(10, 7), 3)
        self.assertIsNone(run.integer_delta(None, 7))

    def test_candidate_cell_has_one_pinned_semantic_call(self):
        for model in ("gpt-5.6-luna", "openai/gpt-5.6-luna"):
            cell = run.candidate_cell(model)
            self.assertEqual(cell.count("llm_batch("), 1)
            self.assertIn("workers=6", cell)
            self.assertIn(f'model="{model}"', cell)
            self.assertEqual(cell.count("FINAL("), 1)
            self.assertIn('FINAL("Answer: " + str(ham))', cell)

    def test_driver_is_owner_executable_and_one_lifecycle(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            work = root / "work"
            work.mkdir(mode=0o700)
            home = root / "home"
            xdg = root / "xdg"
            binary = home / ".agents/skills/azdaja/azdaja"
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"fake")
            binary.chmod(0o500)
            env = {"HOME": str(home), "XDG_CONFIG_HOME": str(xdg)}
            run.write_candidate_driver(work, env, "codex")
            driver = work / "azdaja-evaluate"
            text = driver.read_text()
            self.assertEqual(stat.S_IMODE(driver.stat().st_mode), 0o500)
            for command in (
                '"$AZDAJA" start',
                '"$AZDAJA" load "$sid"',
                '"$AZDAJA" exec "$sid"',
                '"$AZDAJA" final "$sid"',
                '"$AZDAJA" kill "$sid"',
            ):
                self.assertEqual(text.count(command), 1)
            self.assertEqual(text.count("llm_batch("), 1)
            self.assertIn(f"AZDAJA={binary}", text)
            self.assertEqual(driver.stat().st_uid, os.getuid())


if __name__ == "__main__":
    unittest.main()
