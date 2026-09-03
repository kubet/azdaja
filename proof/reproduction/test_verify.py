import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("proof_bundle_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(verify)


class ProofBundleVerifierTests(unittest.TestCase):
    def test_current_bundle_verifies_when_manifest_exists(self):
        manifest = HERE / "manifest.json"
        if not manifest.exists():
            self.skipTest("manifest is generated after the implementation commit")
        result = verify.verify(manifest)
        self.assertEqual(result["live_fable"]["exact_results"], 3)
        self.assertEqual(result["provider_free"]["surviving_sessions"], 0)
        self.assertEqual(result["classification"], "narrow first-party reproducible evidence")

    def test_artifact_hash_tamper_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "evidence.txt"
            artifact.write_text("evidence\n")
            records = [
                {
                    "path": "evidence.txt",
                    "role": "test_evidence",
                    "bytes": artifact.stat().st_size,
                    "sha256": verify.sha256(artifact),
                }
            ]
            verify.validate_artifacts(records, root)
            tampered = copy.deepcopy(records)
            tampered[0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "artifact hash mismatch"):
                verify.validate_artifacts(tampered, root)

    def test_artifact_size_tamper_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "evidence.txt"
            artifact.write_text("evidence\n")
            records = [
                {
                    "path": "evidence.txt",
                    "role": "test_evidence",
                    "bytes": artifact.stat().st_size + 1,
                    "sha256": verify.sha256(artifact),
                }
            ]
            with self.assertRaisesRegex(ValueError, "artifact size mismatch"):
                verify.validate_artifacts(records, root)

    def test_path_escape_and_duplicate_paths_fail(self):
        with self.assertRaisesRegex(ValueError, "unsafe"):
            verify.safe_relative_path("../receipt.json", "receipt")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "evidence.txt"
            artifact.write_text("evidence\n")
            record = {
                "path": "evidence.txt",
                "role": "test_evidence",
                "bytes": artifact.stat().st_size,
                "sha256": verify.sha256(artifact),
            }
            with self.assertRaisesRegex(ValueError, "unique and sorted"):
                verify.validate_artifacts([record, copy.deepcopy(record)], root)

    def test_manifest_unknown_key_fails(self):
        value = {"a": 1, "unexpected": 2}
        with self.assertRaisesRegex(ValueError, "keys mismatch"):
            verify.exact_dict(value, {"a"}, "fixture")

    def test_expected_invariants_are_json_objects(self):
        for relative in (
            "expected/invariants.json",
            "fixtures/spec.json",
            "receipts/fable/index.json",
            "receipts/provider-free/index.json",
        ):
            self.assertIsInstance(json.loads((HERE / relative).read_text()), dict)


if __name__ == "__main__":
    unittest.main()
