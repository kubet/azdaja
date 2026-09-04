import importlib.util
import tempfile
import unittest
from pathlib import Path
from typing import Optional, Tuple

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "verify_third_party_notices", HERE / "verify-third-party-notices.py"
)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class NoticeProvenanceTests(unittest.TestCase):
    def fixture(
        self, directory: str, *, digest: Optional[str] = None
    ) -> Tuple[Path, Path]:
        root = Path(directory)
        lockfile = root / "Cargo.lock"
        lockfile.write_bytes(b"current lock bytes\n")
        bound = digest or VERIFY.sha256(lockfile)
        notice = root / "THIRD-PARTY-NOTICES.md"
        notice.write_text(
            f"# Notices\n\n- Bound inputs: `Cargo.lock` SHA-256 `{bound}`; audit metadata.\n",
            encoding="utf-8",
        )
        return notice, lockfile

    def test_matching_lock_binding_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            notice, lockfile = self.fixture(directory)
            result = VERIFY.verify(notice, lockfile)
            self.assertEqual(result["status"], "current")
            self.assertEqual(result["cargo_lock_sha256"], VERIFY.sha256(lockfile))

    def test_stale_lock_binding_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            notice, lockfile = self.fixture(directory, digest="0" * 64)
            with self.assertRaisesRegex(ValueError, "Cargo.lock hash mismatch"):
                VERIFY.verify(notice, lockfile)

    def test_missing_or_duplicate_binding_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            notice, lockfile = self.fixture(directory)
            binding = notice.read_text(encoding="utf-8").splitlines()[-1]
            notice.write_text("# Notices\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly one"):
                VERIFY.verify(notice, lockfile)
            notice.write_text(f"{binding}\n{binding}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly one"):
                VERIFY.verify(notice, lockfile)

    def test_symlinked_inputs_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notice, lockfile = self.fixture(directory)
            link = root / "notice-link.md"
            link.symlink_to(notice)
            with self.assertRaisesRegex(ValueError, "symlinked"):
                VERIFY.verify(link, lockfile)


if __name__ == "__main__":
    unittest.main()
