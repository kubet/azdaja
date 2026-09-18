import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from . import primitives as p


class PrimitiveCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR"))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = self.root / "data"
        shutil.copytree(p.DATA, self.data)

    def change(self, name, edit):
        value = p.load(self.data / name)
        edit(value)
        (self.data / name).write_text(json.dumps(value))
        seal = p.load(self.data / "RETENTION.json")
        seal["files"][name] = p.sha((self.data / name).read_bytes())
        (self.data / "RETENTION.json").write_text(json.dumps(seal))

    def test_retained_results_preserve_semantic_disagreement_and_limits(self):
        with mock.patch("socket.socket", side_effect=AssertionError("network forbidden")):
            report = p.verify()
        self.assertEqual(report["answers"]["has_workaround"]["noul"], 0.47)
        self.assertEqual(report["answers"]["route"]["choice"], "workaround")
        self.assertEqual(report["answers"]["severity"]["score"], 1)
        self.assertFalse(report["semantic_generalization_established"])
        self.assertFalse(report["billing_known"])
        self.assertEqual(report["usage"]["known_input_tokens"], 468)
        self.assertEqual(report["usage"]["known_output_tokens"], 77)

    def test_every_changed_artifact_and_incomplete_inventory_refused(self):
        for name in p.FILES:
            path = self.data / name
            before = path.read_bytes()
            path.write_bytes(before + b"\n")
            with self.subTest(name=name), self.assertRaises(ValueError):
                p.verify(self.data)
            path.write_bytes(before)
        seal = p.load(self.data / "RETENTION.json")
        seal["files"].pop("live.stderr")
        (self.data / "RETENTION.json").write_text(json.dumps(seal))
        with self.assertRaisesRegex(ValueError, "inventory"):
            p.verify(self.data)

    def test_score_domain_legend_and_expectation_refused_even_rehashed(self):
        name = "job/000000.result.json"
        original = (self.data / name).read_bytes()
        for key, value in [("legend", {"0": "invented"}), ("score", 0.5),
                           ("probabilities", {"0": 0.1, "1": 1, "2": 0})]:
            (self.data / name).write_bytes(original)
            self.change(name, lambda item: item["observation"]["answers"]["severity"].update({key: value}))
            with self.subTest(key=key), self.assertRaises(ValueError):
                p.verify(self.data)

    def test_native_identity_and_usage_refused_even_rehashed(self):
        name = "job/000000.result.json"
        self.change(name, lambda item: item["observation"]["_azdaja"].update(request_sha256="0" * 64))
        with self.assertRaisesRegex(ValueError, "binding"):
            p.verify(self.data)
        shutil.copyfile(p.DATA / name, self.data / name)
        self.change(name, lambda item: item["stats"].update(known_output_tokens=0))
        with self.assertRaisesRegex(ValueError, "usage"):
            p.verify(self.data)

    def test_symlinks_duplicate_keys_and_nonfinite_values_refused(self):
        target = self.data / "plan.jsonl"
        saved = self.root / "plan"
        target.rename(saved)
        target.symlink_to(saved)
        with self.assertRaisesRegex(ValueError, "unsafe"):
            p.verify(self.data)
        for raw in ['{"x":0,"x":1}', '{"x":NaN}', '{"x":Infinity}']:
            path = self.root / "bad.json"
            path.write_text(raw)
            with self.assertRaises(ValueError):
                p.load(path)

    def test_replay_rejects_before_binary_or_credentials_on_changed_result(self):
        (self.data / "job/000000.result.json").write_text("{}")
        with mock.patch.object(p.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                p.native_replay(Path("/not-a-binary"), self.data)
            run.assert_not_called()

    def test_public_default_is_portable_and_only_verifies(self):
        env = {"PATH": os.environ.get("PATH", ""), "HOME": str(self.root / "absent")}
        result = subprocess.run([sys.executable, "-B", str(Path(p.__file__).resolve())],
                                cwd=self.root, env=env, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["new_provider_calls"], 0)
        self.assertNotIn("current_native_replay", report)
        self.assertFalse((self.root / "absent").exists())


if __name__ == "__main__":
    unittest.main()
