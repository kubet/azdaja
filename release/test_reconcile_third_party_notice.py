import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC = importlib.util.spec_from_file_location(
    "notice_reconciliation", HERE / "reconcile-third-party-notice.py"
)
assert SPEC and SPEC.loader
RECONCILE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RECONCILE)


class NoticeReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.notice = ROOT / "THIRD-PARTY-NOTICES.md"
        self.manifest = HERE / "third-party-notice-inputs.json"
        self.lockfile = ROOT / "Cargo.lock"

    def test_current_inputs_reconcile_but_binding_remains_blocked(self):
        result = RECONCILE.reconcile(self.notice, self.manifest, self.lockfile)
        self.assertEqual(result["status"], RECONCILE.STATUS)
        self.assertEqual(result["packages_inventory_matched"], 191)
        self.assertEqual(result["legal_file_records_checked"], 314)
        self.assertEqual(result["unique_legal_hash_headings_found"], 126)
        self.assertEqual(result["manifest_only_records_matched"], 13)
        self.assertFalse(result["notice_binding_current"])
        self.assertEqual(
            result["authorization"],
            "does not authorize a notice binding or publication change",
        )

    def test_notice_inventory_and_legal_hash_tampering_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notice = root / "notice.md"
            text = self.notice.read_text(encoding="utf-8")
            notice.write_text(
                text.replace("| `ahash` | `0.8.12` |", "| `ahash-tampered` | `0.8.12` |", 1),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "inventory identity mismatch"):
                RECONCILE.reconcile(notice, self.manifest, self.lockfile)

            document = json.loads(self.manifest.read_text(encoding="utf-8"))
            digest = document["packages"][0]["license_files"][0]["sha256"]
            notice.write_text(text.replace(digest, "f" * 64), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing reviewed legal text hashes"):
                RECONCILE.reconcile(notice, self.manifest, self.lockfile)

            notice.write_text(
                text.replace(
                    "| `monty 0.0.21` | 756 /",
                    "| `monty-tampered 0.0.21` | 756 /",
                    1,
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "manifest-only notice identity mismatch"):
                RECONCILE.reconcile(notice, self.manifest, self.lockfile)

    def test_manifest_target_and_checksum_tampering_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.json"
            document = json.loads(self.manifest.read_text(encoding="utf-8"))
            document["target_counts"]["aarch64-apple-darwin"] = 188
            manifest.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "target counts mismatch"):
                RECONCILE.reconcile(self.notice, manifest, self.lockfile)

            document = json.loads(self.manifest.read_text(encoding="utf-8"))
            document["packages"][0]["archive_sha256"] = "0" * 64
            manifest.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "archive checksum drift"):
                RECONCILE.reconcile(self.notice, manifest, self.lockfile)

            document = json.loads(self.manifest.read_text(encoding="utf-8"))
            document["claim"] = "complete legal verification"
            manifest.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "claim boundary mismatch"):
                RECONCILE.reconcile(self.notice, manifest, self.lockfile)

            document = json.loads(self.manifest.read_text(encoding="utf-8"))
            document["packages"][0]["license_files"][0]["path"] = "../LICENSE"
            manifest.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "legal file metadata"):
                RECONCILE.reconcile(self.notice, manifest, self.lockfile)

    def test_inventory_parser_normalizes_additive_license_syntax(self):
        text = "\n".join(
            [
                RECONCILE.HISTORICAL_START,
                "| `one` | `1` | `MIT` | targets |",
                RECONCILE.HISTORICAL_END,
                RECONCILE.ADDITIVE_START,
                '| `two` | `2` | `license = "Apache-2.0"` | targets | evidence |',
                RECONCILE.ADDITIVE_END,
            ]
        )
        self.assertEqual(
            RECONCILE.inventory_rows(text),
            {("one", "1"): "MIT", ("two", "2"): "Apache-2.0"},
        )

    def test_atomic_writer_rejects_symlink_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text("original", encoding="utf-8")
            link = root / "output.json"
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "non-symlink"):
                RECONCILE.write_atomic(link, "replacement")
            self.assertEqual(target.read_text(encoding="utf-8"), "original")


if __name__ == "__main__":
    unittest.main()
