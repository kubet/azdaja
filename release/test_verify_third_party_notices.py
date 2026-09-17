"""Acceptance and mutation tests through the actual public verifier CLI, offline."""
import copy
import hashlib
import importlib.util
import json
import subprocess
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC = importlib.util.spec_from_file_location("verify", HERE / "verify-third-party-notices.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class NoticeProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads((HERE / "current-third-party-notice.json").read_bytes())
        cls.notice = (ROOT / "THIRD-PARTY-NOTICES.md").read_bytes()

    def cli(self, *, notice=None, index=None, lock=None, cache=None, reason=None):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            args = [sys.executable, str(HERE / "verify-third-party-notices.py")]
            for flag, raw in (("notice", notice), ("index", index), ("lockfile", lock)):
                if raw is not None:
                    path = temp / flag
                    path.write_bytes(raw)
                    args += ["--" + flag, str(path)]
            if cache is not None:
                args += ["--cache", str(cache)]
            result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
            if reason is None:
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(reason, result.stderr)
            print(f"REJECTED [{reason}]", flush=True)

    def altered_index(self, change, reason):
        doc = copy.deepcopy(self.index)
        change(doc)
        self.cli(index=VERIFY.BUILD.audit.render(doc).encode(), reason=reason)

    def test_public_verifier_and_legacy_flags_accept_exact_generated_artifacts(self):
        result = self.cli(notice=self.notice,
                          index=(HERE / "current-third-party-notice.json").read_bytes(),
                          lock=(ROOT / "Cargo.lock").read_bytes())
        self.assertEqual(result["feature_union_records"], {"default": 191, "typesafe": 242})
        self.assertEqual(result["named_legal_files"], 402)
        self.assertEqual(result["status"], "current")

    def test_wrong_lock_and_notice_binding_are_rejected(self):
        self.cli(lock=(ROOT / "Cargo.lock").read_bytes() + b"\n# mutation\n",
                 reason="supplied lock differs from project lock")
        digest = self.index["cargo_lock_sha256"].encode()
        self.cli(notice=self.notice.replace(digest, b"0" * 64, 1), reason="notice binding")
        self.altered_index(lambda d: d.update(cargo_lock_sha256="0" * 64), "index input binding mismatch")

    def test_missing_and_duplicate_bindings_are_rejected(self):
        binding = next(line for line in self.notice.splitlines() if b"Bound inputs:" in line)
        for raw in (self.notice.replace(binding, b""), self.notice + b"\n" + binding):
            self.cli(notice=raw, reason="exactly one Cargo.lock")

    def test_packaged_license_mutation_is_rejected(self):
        self.altered_index(lambda d: d["packages"][0].update(license="MIT"),
                           "packaged license declaration mismatch")
        self.cli(notice=self.notice.replace(b"`MIT OR Apache-2.0`", b"`MIT`", 1),
                 reason="feature scope/license table mismatch")

    def test_archive_and_registry_provenance_mutations_are_rejected(self):
        for field, value, reason in (("archive_sha256", "0" * 64, "archive checksum mismatch"),
                                     ("checksum", "0" * 64, "lock checksum mismatch"),
                                     ("source", "registry+https://example.invalid", "registry source mismatch"),
                                     ("manifest_sha256", "0" * 64, "packaged manifest mismatch")):
            with self.subTest(field=field):
                self.altered_index(lambda d: d["packages"][0].update({field: value}), reason)

    def test_source_text_mutation_even_with_self_consistent_hash_is_rejected(self):
        def change(doc):
            digest = next(iter(doc["bodies"]))
            body = doc["bodies"].pop(digest)
            body["text"] += "\nUnauthorized altered legal terms.\n"
            raw = body["text"].encode()
            body["bytes"] = len(raw)
            new_digest = hashlib.sha256(raw).hexdigest()
            doc["bodies"][new_digest] = body
            for package in doc["packages"]:
                for legal in package["license_files"]:
                    if legal["sha256"] == digest:
                        legal.update(sha256=new_digest, bytes=len(raw))
        self.altered_index(change, "legal-file occurrence attribution mismatch")
        self.altered_index(lambda d: next(iter(d["bodies"].values())).update(text="altered terms"),
                           "exact source text/byte metadata mismatch")
        start = self.notice.index(b"## Supplied legal files")
        end = self.notice.index(b"## Occurrence attribution index")
        legal = self.notice[start:end]
        self.assertIn(b"Copyright", legal)
        self.cli(notice=self.notice[:start] + legal.replace(b"Copyright", b"Altered attribution", 1) + self.notice[end:],
                 reason="source legal text rendering mismatch")

    def test_occurrence_attribution_mutations_are_rejected(self):
        self.altered_index(lambda d: d["packages"][0]["license_files"][0].update(path="WRONG-LICENSE"),
                           "legal-file occurrence attribution mismatch")
        marker = b"## Occurrence attribution index"
        front, rest = self.notice.split(marker, 1)
        self.cli(notice=front + marker + rest.replace(b"`ahash 0.8.12`", b"`wrong 0.8.12`", 1),
                 reason="occurrence attribution mismatch")

    def test_feature_and_target_membership_mutations_are_rejected(self):
        self.altered_index(lambda d: d["packages"][0]["membership"].update(default=[]),
                           "feature/target membership mismatch")
        self.altered_index(lambda d: d["target_counts"]["typesafe"].update({"x86_64-unknown-linux-gnu": 1}),
                           "feature/target scope mismatch")
        self.altered_index(lambda d: d["packages"].pop(), "package inventory mismatch")
        self.cli(notice=self.notice.replace(b"default 191; typesafe 242", b"default 242; typesafe 242", 1),
                 reason="feature scope/license table mismatch")

    def test_historical_attribution_mutations_are_rejected(self):
        self.altered_index(lambda d: d["historical"].update(sha256="0" * 64),
                           "historical attribution binding mismatch")
        self.cli(notice=self.notice.replace(b"`src/barrier.rs` (archive_legal_header_block)",
                                           b"`src/wrong.rs` (archive_legal_header_block)", 1),
                 reason="historical attribution mismatch")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / VERIFY.BUILD.HISTORICAL
            path.parent.mkdir(parents=True)
            path.write_bytes((ROOT / VERIFY.BUILD.HISTORICAL).read_bytes() + b"changed")
            with self.assertRaisesRegex(ValueError, "historical notice original-byte hash mismatch"):
                VERIFY.BUILD.historical_supplement(root)

    def test_noncanonical_index_or_notice_bytes_are_rejected(self):
        self.cli(index=json.dumps(self.index).encode(), reason="index deterministic serialization mismatch")
        self.altered_index(lambda d: d.update(unrecognized="metadata"), "index schema/metadata mismatch")
        self.cli(notice=self.notice.replace(b"\n", b"\r\n"), reason="front matter/input binding mismatch")

    def test_missing_or_corrupt_actual_cached_archive_is_rejected(self):
        package = self.index["packages"][0]
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            self.cli(cache=cache, reason="expected one regular archive")
            registry = cache / "registry"
            registry.mkdir()
            (registry / f"{package['name']}-{package['version']}.crate").write_bytes(b"corrupt archive")
            self.cli(cache=cache, reason="archive checksum mismatch")

    def test_symlinked_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notice"
            path.symlink_to(ROOT / "THIRD-PARTY-NOTICES.md")
            with self.assertRaisesRegex(ValueError, "symlinked"):
                VERIFY.verify(path, ROOT / "Cargo.lock")

    def test_assembler_source_gate_accepts_current_and_rejects_tampered_notice_before_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = ["Cargo.toml", "Cargo.lock", "LICENSE", "THIRD-PARTY-NOTICES.md",
                     "release/assemble-standalone-assets.sh", "release/verify-third-party-notices.py",
                     "release/build-current-third-party-notice.py", "release/audit-third-party-notice-inputs.py",
                     "release/current-third-party-notice.json", VERIFY.BUILD.HISTORICAL]
            for relative in files:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            # Cargo tree resolves the real manifest/lock. It does not compile sources.
            (root / "src").mkdir()
            (root / "src/main.rs").write_text("fn main() {}\n")
            (root / "src/lib.rs").write_text("")
            output = root / "dist"
            output.mkdir()
            for platform in ("darwin-arm64", "darwin-x86_64", "linux-x86_64"):
                (output / f"azdaja-v{self.index['version']}-{platform}").write_bytes(b"raw binary fixture")
            command = ["sh", str(root / "release/assemble-standalone-assets.sh"), str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((output / "THIRD-PARTY-NOTICES.md").read_bytes(), self.notice)
            baseline = {p.name: p.read_bytes() for p in output.iterdir()}
            (root / "THIRD-PARTY-NOTICES.md").write_bytes(self.notice.replace(b"`MIT OR Apache-2.0`", b"`MIT`", 1))
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("notice feature scope/license table mismatch", result.stderr)
            self.assertIn("current source-backed notice verification failed", result.stderr)
            self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, baseline)
            print("REJECTED [assembler tampered notice before any output mutation]", flush=True)

    def test_all_402_occurrences_round_trip_exact_cached_source_bytes(self):
        count = 0
        for package in self.index["packages"]:
            name, version = package["name"], package["version"]
            archive_path = next((Path.home() / ".cargo/registry/cache").glob(f"*/{name}-{version}.crate"))
            self.assertEqual(VERIFY.sha256(archive_path), package["archive_sha256"])
            with tarfile.open(archive_path, "r:gz") as archive:
                for legal in package["license_files"]:
                    raw = archive.extractfile(f"{name}-{version}/{legal['path']}").read()
                    body = self.index["bodies"][legal["sha256"]]
                    self.assertEqual(body["text"].encode("utf-8"), raw)
                    self.assertEqual(len(raw), legal["bytes"])
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), legal["sha256"])
                    count += 1
        self.assertEqual(count, 402)
        self.assertLess(len(self.index["bodies"]), count)
        self.assertTrue(any(b["line_endings"]["crlf"] for b in self.index["bodies"].values()))


if __name__ == "__main__":
    unittest.main()
