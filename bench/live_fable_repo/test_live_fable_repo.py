import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

run_spec = importlib.util.spec_from_file_location("live_run", HERE / "run.py")
harness = importlib.util.module_from_spec(run_spec)
assert run_spec.loader is not None
run_spec.loader.exec_module(harness)

verify_spec = importlib.util.spec_from_file_location("live_verify", HERE / "verify.py")
verifier = importlib.util.module_from_spec(verify_spec)
assert verify_spec.loader is not None
verify_spec.loader.exec_module(verifier)


class IntentAndOutputTests(unittest.TestCase):
    def test_acknowledgement_refusal(self):
        with self.assertRaisesRegex(PermissionError, "--yes-run-inference"):
            harness.validate_intent(False)
        harness.validate_intent(True)

    def test_overwrite_refusal_and_force(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "receipt.json"
            summary = Path(directory) / "summary.md"
            receipt.write_text("old")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                harness.ensure_outputs_available([receipt, summary], force=False)
            harness.ensure_outputs_available([receipt, summary], force=True)

    def test_model_response_must_be_generic_program(self):
        harness.validate_model_response('```python\nFINAL(path + "|" + ticket)\n```')
        for response in (
            harness.EXPECTED,
            f'```python\nFINAL("{harness.TICKET}")\n```',
            "plain explanation",
        ):
            with self.assertRaises(ValueError):
                harness.validate_model_response(response)

    def test_fixture_generator_is_exact_and_unique(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture"
            digest = harness.write_fixture(path)
            self.assertEqual(path.stat().st_size, harness.INPUT_BYTES)
            self.assertTrue(harness.is_sha256(digest))
            data = path.read_bytes()
            self.assertEqual(data.count(b"AZDAJA_RELEASE_BLOCKER="), 1)
            self.assertEqual(data.count(harness.TICKET.encode()), 1)


class VerifierUnitTests(unittest.TestCase):
    def test_source_manifest_is_scoped_to_live_runtime_and_verifier(self):
        paths = harness.source_paths()
        self.assertIn("bench/live_fable_repo/run.py", paths)
        self.assertIn("bench/live_fable_repo/verify.py", paths)
        for unrelated in {
            "tests/product_50mb.rs",
            "bench/product_50mb/reproduce.py",
            "bench/product_50mb/verify.py",
        }:
            self.assertNotIn(unrelated, paths)

    def test_receipt_schema_tamper_fails_before_external_checks(self):
        with self.assertRaisesRegex(ValueError, "schema keys mismatch"):
            verifier.validate_receipt({"schema": "bad"})

    def test_source_hash_tamper(self):
        manifest = harness.source_manifest()
        verifier.validate_source_manifest(manifest)
        tampered = copy.deepcopy(manifest)
        tampered[0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            verifier.validate_source_manifest(tampered)

    def test_command_schema_and_exit_code_tamper(self):
        good = {
            "argv": ["command"],
            "env": {},
            "elapsed_seconds": 1.0,
            "exit_code": 0,
            "output_sha256": "a" * 64,
        }
        verifier.validate_command(good, "command")
        bad = copy.deepcopy(good)
        bad["exit_code"] = 1
        with self.assertRaisesRegex(ValueError, "nonzero exit code"):
            verifier.validate_command(bad, "command")

    def test_model_response_hash_tamper_is_detectable(self):
        response = '```python\nFINAL(path + "|" + ticket)\n```'
        recorded = {"text": response, "sha256": harness.sha256_bytes(response.encode())}
        self.assertEqual(recorded["sha256"], harness.sha256_bytes(recorded["text"].encode()))
        recorded["text"] += "tamper"
        self.assertNotEqual(recorded["sha256"], harness.sha256_bytes(recorded["text"].encode()))


if __name__ == "__main__":
    unittest.main()
