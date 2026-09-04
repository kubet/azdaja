import hashlib
import importlib.util
import io
import tarfile
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "audit", Path(__file__).with_name("audit-third-party-notice-inputs.py")
)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class AuditInputTests(unittest.TestCase):
    def archive(self, files):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w:gz") as archive:
            for name, data in files.items():
                info = tarfile.TarInfo(name)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
        return output.getvalue()

    def test_archive_evidence_hashes_all_named_legal_variants(self):
        manifest = b'\n'.join(
            [
                b"[package]",
                b'name = "demo"',
                b'version = "1.0.0"',
                b'license = "MIT OR Apache-2.0"',
                b'license-file = "docs/COPYING.extra"',
                b"",
            ]
        )
        data = self.archive(
            {
                "demo-1.0.0/Cargo.toml": manifest,
                "demo-1.0.0/COPYRIGHT": b"copyright\n",
                "demo-1.0.0/LICENSE-MIT": b"mit\n",
                "demo-1.0.0/docs/COPYING.extra": b"copying\n",
                "demo-1.0.0/vendor/UNLICENSE": b"unlicense\n",
            }
        )
        result = AUDIT.archive_evidence(data, "demo", "1.0.0")
        self.assertEqual(result["license"], "MIT OR Apache-2.0")
        self.assertEqual(result["manifest_sha256"], hashlib.sha256(manifest).hexdigest())
        self.assertEqual(
            [item["path"] for item in result["license_files"]],
            ["COPYRIGHT", "LICENSE-MIT", "docs/COPYING.extra", "vendor/UNLICENSE"],
        )
        self.assertEqual(result["license_files"][0]["bytes"], len(b"copyright\n"))

    def test_archive_rejects_traversal_missing_license_and_identity(self):
        traversal = self.archive(
            {
                "demo-1.0.0/Cargo.toml": b"[package]\nlicense = \"MIT\"\n",
                "demo-1.0.0/../LICENSE": b"x",
            }
        )
        with self.assertRaisesRegex(ValueError, "escapes package root"):
            AUDIT.archive_evidence(traversal, "demo", "1.0.0")

        missing = self.archive(
            {
                "demo-1.0.0/Cargo.toml": (
                    b"[package]\nname = \"demo\"\nversion = \"1.0.0\"\n"
                    b"license-file = \"COPYING\"\n"
                )
            }
        )
        with self.assertRaisesRegex(ValueError, "declared legal file"):
            AUDIT.archive_evidence(missing, "demo", "1.0.0")

        missing_identity = self.archive(
            {
                "demo-1.0.0/Cargo.toml": b"[package]\nlicense = \"MIT\"\n",
                "demo-1.0.0/LICENSE": b"legal\n",
            }
        )
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            AUDIT.archive_evidence(missing_identity, "demo", "1.0.0")

    def test_lock_registry_record_requires_valid_unique_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            lockfile = Path(directory) / "Cargo.lock"
            lockfile.write_text(
                'version = 4\n\n[[package]]\nname = "demo"\nversion = "1"\n'
                'source = "registry+https://github.com/rust-lang/crates.io-index"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "malformed registry checksum"):
                AUDIT.lock_records(lockfile)

            record = (
                '[[package]]\nname = "demo"\nversion = "1"\n'
                'source = "registry+https://github.com/rust-lang/crates.io-index"\n'
                f'checksum = "{"0" * 64}"\n'
            )
            lockfile.write_text(f"version = 4\n\n{record}\n{record}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ambiguous name/version"):
                AUDIT.lock_records(lockfile)

            local = (
                '[[package]]\nname = "demo"\nversion = "1"\n\n'
            )
            lockfile.write_text(f"version = 4\n\n{record}\n{local}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ambiguous name/version"):
                AUDIT.lock_records(lockfile)

    def test_tree_parser_preserves_build_and_proc_macro_records(self):
        text = "\n".join(
            [
                "azdaja v0.1.14 (/checkout)",
                "normal-dep v1.0.0",
                "build-only v2.0.0",
                "macro-crate v3.0.0 (proc-macro)",
                "normal-dep v1.0.0 (*)",
            ]
        )
        self.assertEqual(
            AUDIT.parse_tree(text, "azdaja"),
            {
                ("normal-dep", "1.0.0"),
                ("build-only", "2.0.0"),
                ("macro-crate", "3.0.0"),
            },
        )

    def test_archive_lookup_rejects_checksum_drift_and_ambiguity(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            first = cache / "registry-one"
            first.mkdir()
            archive = first / "demo-1.0.0.crate"
            archive.write_bytes(b"crate bytes")
            checksum = hashlib.sha256(b"crate bytes").hexdigest()
            self.assertEqual(
                AUDIT.find_archive(cache, "demo", "1.0.0", checksum),
                b"crate bytes",
            )
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                AUDIT.find_archive(cache, "demo", "1.0.0", "0" * 64)

            second = cache / "registry-two"
            second.mkdir()
            (second / archive.name).write_bytes(b"crate bytes")
            with self.assertRaisesRegex(ValueError, "expected one regular archive"):
                AUDIT.find_archive(cache, "demo", "1.0.0", checksum)

    def test_atomic_writer_rejects_symlink_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text("original", encoding="utf-8")
            link = root / "manifest.json"
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "non-symlink"):
                AUDIT.write_atomic(link, "replacement")
            self.assertEqual(target.read_text(encoding="utf-8"), "original")


if __name__ == "__main__":
    unittest.main()
