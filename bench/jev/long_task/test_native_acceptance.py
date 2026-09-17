"""Stdlib unit tests for the public-solo acceptance harness, no model service."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("native_acceptance", HERE / "native_acceptance.py")
acceptance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(acceptance)
SCRATCH = Path(os.environ.get("JCODE_SCRATCH_DIR", str(Path.home() / ".jcode/scratch")))


class NativeAcceptanceTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="native-acceptance-test-", dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def test_environment_is_allowlist_not_parent_copy(self):
        poison = {"TYPESAFE_API_KEY": "synthetic-not-a-credential",
                  "OPENAI_API_KEY": "synthetic-not-a-credential",
                  "JCODE_SOCKET": "/synthetic/socket", "XDG_RUNTIME_DIR": "/synthetic/runtime",
                  "AZDAJA_CONFIG": "/synthetic/config", "RLM_DEPTH": "9",
                  "PYTHONPATH": "/synthetic/python", "AZDAJA_CODE_PROVIDER": "synthetic"}
        with mock.patch.dict(os.environ, poison):
            env = acceptance.isolated_environment(self.path)
        self.assertTrue(set(poison).difference({"AZDAJA_CONFIG"}).isdisjoint(env))
        self.assertEqual(env["AZDAJA_CONFIG"], str(self.path / "config.toml"))
        self.assertEqual((self.path / "home").stat().st_mode & 0o777, 0o700)

    def test_stub_drains_large_stdin_and_retains_exact_bytes(self):
        stub = self.path / "stub.py"
        acceptance.private_write(stub, acceptance.STUB.encode())
        prompt = b"full synthetic prompt\n" + b"x" * (1024 * 1024) + "\nUnicode: \u03bb\n".encode()
        retained = self.path / "prompt.txt"
        code = "FINAL({'synthetic':42})"
        result = subprocess.run([sys.executable, str(stub), str(retained), code],
                                input=prompt, capture_output=True, check=True, timeout=10,
                                env=acceptance.isolated_environment(self.path))
        self.assertEqual(retained.read_bytes(), prompt)
        self.assertEqual(result.stdout, ("```python\n" + code + "\n```\n").encode())
        self.assertEqual(result.stderr, b"")

    def test_output_is_exclusive_before_binary_execution(self):
        with self.assertRaises(FileExistsError):
            acceptance.accept(Path("/synthetic/not-executed"), None, self.path)

    def test_private_writes_never_overwrite(self):
        target = self.path / "artifact"
        acceptance.private_write(target, b"original")
        with self.assertRaises(FileExistsError):
            acceptance.private_write(target, b"replacement")
        self.assertEqual(target.read_bytes(), b"original")
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)

    def stats(self):
        return dict.fromkeys(acceptance.ZERO_FIELDS, 0) | {
            "enabled": True, "transport_available": True, "poisoned": False,
            "input_usage_complete": True, "output_usage_complete": True}

    def test_stats_require_all_zero_host_counters_and_actual_transport(self):
        stats = self.stats()
        self.assertTrue(acceptance.zero_stats(stats, True))
        for field in acceptance.ZERO_FIELDS:
            for invalid in (1, False, None):
                self.assertFalse(acceptance.zero_stats(stats | {field: invalid}, True), field)
            incomplete = dict(stats)
            del incomplete[field]
            self.assertFalse(acceptance.zero_stats(incomplete, True), field)
        self.assertFalse(acceptance.zero_stats(stats, False))
        self.assertTrue(acceptance.zero_stats(stats | {"transport_available": False}, False))

    def test_trace_parser_retains_runtime_not_framing(self):
        row = {"event": "solo_runtime", "outcome": "succeeded", "judge_cells": [self.stats()]}
        text = "=== host trace ===\n{not json\n" + json.dumps(row) + "\n=== end ===\n"
        self.assertEqual(acceptance.json_rows(text), [row])

    def test_corpus_resolves_from_script_not_working_directory(self):
        self.assertTrue(acceptance.CORPUS.is_absolute())
        data = json.loads(acceptance.CORPUS.read_bytes())
        self.assertEqual([c["id"] for c in data["contracts"]], ["d%03d" % i for i in range(102)])


if __name__ == "__main__":
    unittest.main()
