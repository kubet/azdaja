import copy
import importlib.util
import mmap
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

run_spec = importlib.util.spec_from_file_location("suite_run", HERE / "run.py")
suite = importlib.util.module_from_spec(run_spec)
assert run_spec.loader is not None
run_spec.loader.exec_module(suite)

verify_spec = importlib.util.spec_from_file_location("suite_verify", HERE / "verify.py")
verifier = importlib.util.module_from_spec(verify_spec)
assert verify_spec.loader is not None
verify_spec.loader.exec_module(verifier)


def count_occurrences(data: mmap.mmap, needle: bytes) -> int:
    count = 0
    offset = 0
    while True:
        found = data.find(needle, offset)
        if found < 0:
            return count
        count += 1
        offset = found + len(needle)


class SuiteHarnessTests(unittest.TestCase):
    def test_intent_and_output_guards_are_reused(self):
        with self.assertRaises(PermissionError):
            suite.repo.validate_intent(False)
        suite.repo.validate_intent(True)
        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "receipt.json"
            existing.write_text("old")
            with self.assertRaises(FileExistsError):
                suite.repo.ensure_outputs_available([existing], False)

    def test_response_rejects_each_answer_constant(self):
        generic = '```python\nFINAL(answer)\n```'
        for name in suite.SCENARIOS:
            suite.validate_response(name, generic)
            for forbidden in suite.SCENARIOS[name]["forbidden"]:
                with self.assertRaises(ValueError):
                    suite.validate_response(name, generic + forbidden)

    def test_build_fixture_has_expected_duplicate_sensitive_count(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "build.log"
            digest = suite.write_build_fixture(path)
            self.assertTrue(suite.repo.is_sha256(digest))
            self.assertEqual(path.stat().st_size, suite.repo.INPUT_BYTES)
            with path.open("rb") as handle:
                data = mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ)
                try:
                    self.assertEqual(
                        count_occurrences(data, b" level=ERROR target=payments::retry "), 13
                    )
                finally:
                    data.close()

    def test_catalog_fixture_has_three_matches_and_one_final_color(self):
        question = suite.SCENARIOS["catalog"]["question"]
        self.assertIn("Find the final record", question)
        self.assertIn("item field is SKU-4821", question)
        self.assertIn("Reply exactly as Color: VALUE", question)
        self.assertEqual(suite.SCENARIOS["catalog"]["expected"], "Color: cerulean")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.txt"
            suite.write_catalog_fixture(path)
            with path.open("rb") as handle:
                data = mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ)
                try:
                    self.assertEqual(
                        count_occurrences(data, b"item=SKU-4821"), 3
                    )
                    self.assertEqual(count_occurrences(data, b"color=cerulean"), 1)
                finally:
                    data.close()

    def test_source_manifest_hash_tamper_fails(self):
        manifest = suite.source_manifest()
        verifier.validate_source_manifest(manifest)
        tampered = copy.deepcopy(manifest)
        tampered[-1]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            verifier.validate_source_manifest(tampered)

    def test_receipt_schema_tamper_fails_early(self):
        with self.assertRaisesRegex(ValueError, "schema keys mismatch"):
            verifier.validate_receipt({"schema": "wrong"})


if __name__ == "__main__":
    unittest.main()
