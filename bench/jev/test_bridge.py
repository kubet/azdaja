import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import bridge
from adapter import AdapterError


def sample():
    rows = [
        {"occurrence": 0, "case_id": "a", "raw": '{"claim":"café","evidence":"oui"}'},
        {"occurrence": 1, "case_id": "a", "raw": '{"claim":"café","evidence":"oui"}'},
        {"occurrence": 2, "case_id": "b", "raw": '{"claim":"x","evidence":"y"}'},
    ]
    text = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    entries = [{"case_id": r["case_id"], "payload_sha256": hashlib.sha256(r["raw"].encode()).hexdigest(),
                "label": "supported", "accepted": True} for r in (rows[0], rows[2])]
    return text, {"schema_version": 1, "source_sha256": hashlib.sha256(text.encode()).hexdigest(), "entries": entries}


class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary = Path(os.environ.get("AZDAJA_BINARY", "target/debug/azdaja")).resolve()
        if not cls.binary.is_file():
            raise RuntimeError("S0 requires the actual built Azdaja binary, no skipped custody tests")
        cls.scratch = Path(os.environ.get("JCODE_SCRATCH_DIR", str(Path.home() / ".jcode/scratch")))
        cls.scratch.mkdir(parents=True, exist_ok=True)

    def evaluate(self, text, manifest, audit=False):
        return bridge.evaluate(self.binary, text, manifest, self.scratch, audit_only=audit)

    def rejected_inside_evaluator(self, text, manifest, reason):
        observed = []
        original = bridge._run
        def capture(binary, args, *a, **kw):
            result = original(binary, args, *a, **kw)
            observed.append((args[0], result))
            return result
        with patch.object(bridge, "_run", side_effect=capture):
            with self.assertRaisesRegex(ValueError, "^evaluator rejected custody$"):
                self.evaluate(text, manifest)
        failed_execs = [r for name, r in observed if name == "exec" and r.returncode != 0]
        self.assertEqual(len(failed_execs), 1)
        self.assertIn(reason.encode(), failed_execs[0].stdout + failed_execs[0].stderr)
        self.assertEqual(observed[-1][0], "kill")
        self.assertEqual(observed[-1][1].returncode, 0)

    def test_actual_counts_unicode_and_duplicate_expansion(self):
        text, manifest = sample()
        result = self.evaluate(text, manifest)
        self.assertTrue(result["complete"])
        self.assertEqual(result["occurrences"], 3)
        self.assertEqual(result["unique_judged"], 2)
        self.assertEqual(result["source_sha256"], hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(result["raw_counts"], {"supported": 3, "contradicted": 0, "insufficient": 0, "unjudged": 0})
        self.assertEqual(result["accepted_counts"], {"supported": 3, "contradicted": 0, "insufficient": 0})
        self.assertEqual([r["occurrence"] for r in result["ledger"]], [0, 1, 2])
        self.assertEqual([r["case_id"] for r in result["ledger"]], ["a", "a", "b"])
        self.assertEqual([r["payload_sha256"] for r in result["ledger"]],
                         [manifest["entries"][0]["payload_sha256"]] * 2 + [manifest["entries"][1]["payload_sha256"]])

    def test_raw_and_accepted_label_counts_are_distinct(self):
        text, manifest = sample()
        manifest["entries"][0].update(label="contradicted", accepted=False)
        manifest["entries"][1].update(label="insufficient", accepted=True)
        result = self.evaluate(text, manifest)
        self.assertEqual(result["raw_counts"], {"supported": 0, "contradicted": 2, "insufficient": 1, "unjudged": 0})
        self.assertEqual(result["accepted_counts"], {"supported": 0, "contradicted": 0, "insufficient": 1})

    def test_source_hash_recomputed_inside_evaluator(self):
        text, manifest = sample()
        manifest["source_sha256"] = "0" * 64
        self.rejected_inside_evaluator(text, manifest, "source hash mismatch")

    def test_payload_hash_recomputed_inside_evaluator(self):
        text, manifest = sample()
        manifest["entries"][0]["payload_sha256"] = "0" * 64
        self.rejected_inside_evaluator(text, manifest, "payload hash mismatch")

    def test_changed_duplicate_rejected_inside_evaluator(self):
        text, manifest = sample()
        rows = json.loads(text)
        rows[1]["raw"] = "changed"
        text = json.dumps(rows)
        manifest["source_sha256"] = hashlib.sha256(text.encode()).hexdigest()
        self.rejected_inside_evaluator(text, manifest, "duplicate content changed")

    def test_occurrence_order_rejected_inside_evaluator(self):
        text, manifest = sample()
        rows = json.loads(text)
        rows[1]["occurrence"] = 0
        text = json.dumps(rows)
        manifest["source_sha256"] = hashlib.sha256(text.encode()).hexdigest()
        self.rejected_inside_evaluator(text, manifest, "source order mismatch")

    def test_duplicate_and_extra_manifest_entries_rejected_inside_evaluator(self):
        for extra in (False, True):
            text, manifest = sample()
            entry = dict(manifest["entries"][0])
            if extra:
                entry["case_id"] = "unknown"
            manifest["entries"].append(entry)
            with self.subTest(extra=extra):
                self.rejected_inside_evaluator(text, manifest, "extra manifest entry" if extra else "duplicate manifest entry")

    def test_missing_strict_fails_but_real_partial_keeps_all_known_occurrences(self):
        text, manifest = sample()
        manifest["entries"].pop()
        self.rejected_inside_evaluator(text, manifest, "incomplete judgment")
        result = self.evaluate(text, manifest, audit=True)
        self.assertFalse(result["complete"])
        self.assertEqual(result["unjudged_occurrences"], [2])
        self.assertEqual(result["occurrences"], 3)
        self.assertEqual(result["unique_judged"], 1)
        self.assertEqual(result["raw_counts"], {"supported": 2, "contradicted": 0, "insufficient": 0, "unjudged": 1})
        self.assertEqual(result["accepted_counts"]["supported"], 2)
        self.assertEqual([r["label"] for r in result["ledger"]], ["supported", "supported", "unjudged"])
        self.assertFalse(result["ledger"][2]["accepted"])

    def test_empty_source_has_exact_vacuous_accounting(self):
        manifest = {"schema_version": 1, "source_sha256": hashlib.sha256(b"[]").hexdigest(), "entries": []}
        result = self.evaluate("[]", manifest)
        self.assertTrue(result["complete"])
        self.assertEqual(result["occurrences"], 0)
        self.assertEqual(result["ledger"], [])
        self.assertEqual(sum(result["raw_counts"].values()), 0)

    def test_ambiguous_source_json_rejected_before_execution(self):
        text, manifest = sample()
        ambiguous = text.replace('"occurrence":0', '"occurrence":9,"occurrence":0', 1)
        with patch.object(bridge, "_run") as mocked:
            with self.assertRaisesRegex(AdapterError, "^duplicate_json_key$"):
                self.evaluate(ambiguous, manifest)
            mocked.assert_not_called()

    def test_invalid_judgment_shapes_rejected_before_execution(self):
        text, manifest = sample()
        for changes in ({"accepted": 1}, {"label": "bad"}, {"payload_sha256": "G" * 64}):
            bad = copy.deepcopy(manifest)
            bad["entries"][0].update(changes)
            with self.subTest(changes=changes), patch.object(bridge, "_run") as mocked:
                with self.assertRaisesRegex(ValueError, "^invalid judgment$"):
                    self.evaluate(text, bad)
                mocked.assert_not_called()

    def test_process_environment_and_private_files_are_isolated(self):
        text, manifest = sample()
        real_run = bridge.subprocess.run
        environments = []
        def capture(argv, **kwargs):
            env = kwargs["env"]
            environments.append(env)
            self.assertNotIn("TYPESAFE_API_KEY", env)
            self.assertNotIn("HTTPS_PROXY", env)
            self.assertNotIn("PYTHONPATH", env)
            config = Path(env["AZDAJA_CONFIG"])
            self.assertEqual(config.stat().st_mode & 0o777, 0o600)
            self.assertEqual(config.parent.stat().st_mode & 0o777, 0o700)
            self.assertIn("/usr/bin/false", config.read_text())
            for filename in ("source.json", "manifest.json"):
                self.assertEqual((config.parent / filename).stat().st_mode & 0o777, 0o600)
            return real_run(argv, **kwargs)
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "dummy-do-not-forward", "HTTPS_PROXY": "https://invalid"}), patch.object(bridge.subprocess, "run", side_effect=capture):
            self.evaluate(text, manifest)
        self.assertEqual(len(environments), 6)
        self.assertFalse(Path(environments[0]["AZDAJA_CONFIG"]).parent.exists())


if __name__ == "__main__":
    unittest.main()
