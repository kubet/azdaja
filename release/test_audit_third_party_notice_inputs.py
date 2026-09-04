import hashlib
import io
import tarfile
import tempfile
import unittest
from pathlib import Path
import importlib.util

SPEC = importlib.util.spec_from_file_location("audit", Path(__file__).with_name("audit-third-party-notice-inputs.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
evidence, lock_records = MODULE.evidence, MODULE.lock_records

class AuditInputTests(unittest.TestCase):
    def archive(self, files):
        out = io.BytesIO()
        with tarfile.open(fileobj=out, mode="w:gz") as t:
            for name, data in files.items():
                info = tarfile.TarInfo(name); info.size = len(data); t.addfile(info, io.BytesIO(data))
        return out.getvalue()

    def test_synthetic_archive_license_file_and_hash(self):
        data = self.archive({"demo-1.0.0/Cargo.toml": b'[package]\nlicense = "MIT"\nlicense_file = "COPYING"\n', "demo-1.0.0/COPYING": b"legal\n"})
        result = evidence(data, "demo", "1.0.0")
        self.assertEqual(result["license"], "MIT")
        self.assertEqual(result["license_files"][0]["sha256"], hashlib.sha256(b"legal\n").hexdigest())

    def test_malformed_license_path_fails_closed(self):
        data = self.archive({"demo-1.0.0/Cargo.toml": b'[package]\nlicense_file = "../LICENSE"\n', "demo-1.0.0/LICENSE": b"x"})
        with self.assertRaises(ValueError): evidence(data, "demo", "1.0.0")

    def test_lock_registry_record_requires_checksum(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "Cargo.lock"; p.write_text('[[package]]\nname = "demo"\nversion = "1"\nsource = "registry+https://github.com/rust-lang/crates.io-index"\n')
            with self.assertRaises(ValueError): lock_records(p)

if __name__ == "__main__": unittest.main()
