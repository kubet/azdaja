import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("proof_bundle_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(verify)


class ProofBundleVerifierTests(unittest.TestCase):
    def test_declared_bundle_artifacts_exist_before_generation(self):
        builder = verify.import_module("proof_manifest_builder", HERE / "build_manifest.py")
        for relative in builder.ARTIFACT_ROLES:
            path = ROOT / relative
            self.assertTrue(path.is_file() and not path.is_symlink(), relative)

    def test_original_manifest_and_experiment_inputs_remain_byte_exact(self):
        original = HERE / "historical/manifest-cc442345.json"
        self.assertEqual(verify.sha256(original),
                         "8d75cd97eb868b4721017327b950b5516e4155a1ed6ece64d647be6ca5c6ee99")
        manifest = json.loads(original.read_text())
        self.assertEqual(manifest["source_commit"], "cc442345ef47cc62eb5d22b07a918eab9111766d")
        immutable_roles = {"live_receipt", "provider_free_receipt", "live_receipt_index",
                           "provider_free_receipt_index", "fixture_specification", "expected_invariants",
                           "live_receipt_verifier", "provider_free_receipt_verifier"}
        matched = set()
        for record in manifest["artifacts"]:
            if record["role"] in immutable_roles:
                self.assertEqual(verify.sha256(ROOT / record["path"]), record["sha256"], record["path"])
                matched.add(record["role"])
        self.assertEqual(matched, immutable_roles)
        self.assertEqual(verify.sha256(HERE / "historical/verify-cc442345.py.txt"),
                         "187b8e6b97ee144d6ced3256bfdb4b63fe789ee2b7a4b2add66efe9005c716b7")

    def test_historical_source_is_complete_and_missing_receipt_entries_still_fail(self):
        receipt = json.loads((ROOT / "bench/results/live-fable-suite.json").read_text())
        checker = verify.import_module("historical_live_check", ROOT / "bench/live_fable_suite/verify.py")
        with verify.historical_source(receipt["source"]["commit"], ROOT) as snapshot:
            self.assertFalse((snapshot / "src/judge.rs").exists())
            self.assertEqual(checker.validate_receipt(receipt, root=snapshot), {"source": True, "binary": False})
            bad = copy.deepcopy(receipt)
            bad["source"]["files"].pop()
            with self.assertRaisesRegex(ValueError, "source manifest length mismatch"):
                checker.validate_receipt(bad, root=snapshot)
            bad = copy.deepcopy(receipt)
            bad["source"]["files"][0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                checker.validate_receipt(bad, root=snapshot)

    def test_unknown_historical_commit_fails_before_snapshot(self):
        with self.assertRaisesRegex(ValueError, "historical source commit unavailable"):
            with verify.historical_source("0" * 40, ROOT):
                self.fail("unknown commit yielded a snapshot")

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

    def test_reviewer_command_prints_the_documented_result_shape(self):
        completed = subprocess.run(
            [str(HERE / "run.sh")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(result["schema"], "azdaja.first_party_proof_verification.v1")
        self.assertRegex(result["bundle_source_commit"], r"^[0-9a-f]{40}$")

        documented = copy.deepcopy(result)
        documented["bundle_source_commit"] = "<40-hex-source-commit>"
        expected_line = json.dumps(documented, sort_keys=True)
        guide = (HERE / "README.md").read_text()
        self.assertIn(f"```json\n{expected_line}\n```", guide)

    def test_reviewer_clone_recipe_is_copy_paste_complete(self):
        guide = (HERE / "README.md").read_text()
        recipe = """```sh
git clone https://github.com/kubet/azdaja.git
cd azdaja
./proof/reproduction/run.sh
```"""
        self.assertIn(recipe, guide)
        self.assertIn("git fetch --unshallow", guide)
        self.assertIn("A nonzero exit means the evidence was not verified.", guide)


if __name__ == "__main__":
    unittest.main()
