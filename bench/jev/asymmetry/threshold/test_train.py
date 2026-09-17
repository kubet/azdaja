import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("threshold_train", HERE / "train.py")
TRAIN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TRAIN)


class ThresholdTrainingTests(unittest.TestCase):
    def test_inclusive_p_equals_threshold_semantics(self):
        rows = [
            {"id": "ham", "p_ham": 0.50, "gold_ham": True},
            {"id": "spam", "p_ham": 0.50, "gold_ham": False},
        ]
        result = TRAIN.score(rows, 50)
        self.assertEqual(result["false_positive_ids"], ["spam"])
        self.assertEqual(result["false_negative_ids"], [])

    def test_ties_choose_closest_then_larger_threshold(self):
        rows = [
            {"id": "ham", "p_ham": 0.80, "gold_ham": True},
            {"id": "spam", "p_ham": 0.20, "gold_ham": False},
        ]
        selected, candidates = TRAIN.select(rows)
        self.assertEqual(len(candidates), 101)
        self.assertEqual(selected["threshold"], "0.50")
        self.assertEqual(selected["total_fp_fn"], 0)

        # Equal loss at .49 and .51 is equally close in this symmetric fixture,
        # so the larger threshold must win.
        rows = [
            {"id": "ham", "p_ham": 0.49, "gold_ham": True},
            {"id": "spam", "p_ham": 0.50, "gold_ham": False},
        ]
        selected, _ = TRAIN.select(rows)
        self.assertEqual(selected["threshold"], "0.51")

    def test_real_row645_freeze_is_227_rows_and_reproducible(self):
        rows = TRAIN.load_training_rows(TRAIN.DEFAULT_RESULT)
        selected, candidates = TRAIN.select(rows)
        self.assertEqual(len(rows), 227)
        self.assertEqual(selected["threshold"], "0.74")
        self.assertEqual(selected["total_fp_fn"], 3)
        self.assertEqual(sum(c["total_fp_fn"] == 3 for c in candidates), 8)
        with tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR")) as directory:
            output = Path(directory) / "freeze.json"
            freeze = TRAIN.train(output_path=output)
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved, freeze)
            self.assertEqual(saved["training_inputs"]["row645_result"]["sha256"],
                             TRAIN.sha256_file(TRAIN.DEFAULT_RESULT))
            self.assertFalse(saved["transfer_guardrails"]["row651_applied"])

    def test_hostile_training_rows_refused(self):
        original = json.loads(TRAIN.DEFAULT_RESULT.read_text())
        for field, value in (("p_ham", True), ("p_ham", float("nan")),
                             ("p_ham", 1.01), ("gold_ham", 1),
                             ("id", original["occurrence_ledger"][1]["id"])):
            altered = json.loads(json.dumps(original))
            altered["occurrence_ledger"][0][field] = value
            with tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR")) as tmp:
                p = Path(tmp) / "train.json"
                p.write_text(json.dumps(altered))
                with self.assertRaises(ValueError):
                    TRAIN.load_training_rows(p)

    def test_existing_and_dangling_freeze_never_overwritten(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR")) as tmp:
            p = Path(tmp) / "freeze.json"
            p.write_bytes(b"preserve")
            with self.assertRaises(FileExistsError):
                TRAIN.train(output_path=p)
            self.assertEqual(p.read_bytes(), b"preserve")
            link = Path(tmp) / "dangling.json"
            link.symlink_to(Path(tmp) / "absent")
            with self.assertRaises(FileExistsError):
                TRAIN.train(output_path=link)
            self.assertFalse((Path(tmp) / "absent").exists())


if __name__ == "__main__":
    unittest.main()
