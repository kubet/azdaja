import copy
import hashlib
import importlib.util
import itertools
import json
import os
import stat
import subprocess
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST_LICENSE_DATA = b"test-only pinned RULER license bytes"
TEST_NOTICE_DATA = b"test-only third-party notice bytes"
TEST_GOLD_DATA = b"test-only sealed gold (never read by runner)"
TEST_NOTICE_SHA256 = hashlib.sha256(TEST_NOTICE_DATA).hexdigest()
SPEC = importlib.util.spec_from_file_location("azdaja_ruler_run", HERE / "run.py")
RUN = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUN
assert SPEC.loader is not None
SPEC.loader.exec_module(RUN)
TEST_IDENTITY_ROOT = Path(tempfile.mkdtemp(prefix="ruler-run-test-identity-")).resolve()
os.chmod(TEST_IDENTITY_ROOT, 0o700)
(TEST_IDENTITY_ROOT / "controller").mkdir(mode=0o700)
TEST_CONTROLLER, TEST_CONTROLLER_SOURCES = RUN.snapshot_controller(
    TEST_IDENTITY_ROOT / "controller"
)
TEST_CANDIDATE_SOURCE = TEST_IDENTITY_ROOT / "candidate-source"
TEST_CANDIDATE_SOURCE.mkdir(mode=0o700)
for _name, _data, _mode in (
    ("azdaja", b"#!/bin/sh\nexit 0\n", 0o755),
    ("config.toml", b"x=1\n", 0o644),
    ("SKILL.md", b"---\nname: azdaja\n---\n# azdaja\n", 0o644),
):
    _path = TEST_CANDIDATE_SOURCE / _name
    _path.write_bytes(_data)
    os.chmod(_path, _mode)
(TEST_IDENTITY_ROOT / "candidate").mkdir(mode=0o700)
TEST_CANDIDATE = RUN.snapshot_candidate(
    TEST_CANDIDATE_SOURCE, TEST_IDENTITY_ROOT / "candidate"
)
TEST_EXECUTABLE = TEST_IDENTITY_ROOT / "test-executable"
TEST_EXECUTABLE.write_bytes(b"test executable identity")
os.chmod(TEST_EXECUTABLE, 0o500)


def write_private(path: Path, data: bytes) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.write_bytes(data)
    if os.name == "posix":
        os.chmod(path.parent, 0o700)
        os.chmod(path, 0o600)


def fake_suite(root: Path) -> RUN.PublicSuite:
    manifest = root / "manifest.json"
    manifest.write_bytes(b"{}\n")
    fixtures = []
    for target_length in RUN.TARGET_LENGTHS:
        for task in RUN.TASKS:
            for index in range(10):
                payload = root / f"{task}-{target_length}-{index}.txt"
                data = f"official {task} {target_length} {index}".encode()
                payload.write_bytes(data)
                fixtures.append(RUN.PublicFixture(
                    fixture_id=f"f-{task}-{target_length}-{index}",
                    task=task,
                    target_length=target_length,
                    payload_path=payload,
                    payload_data=data,
                    payload_sha256=hashlib.sha256(data).hexdigest(),
                    payload_bytes=len(data),
                    construction_tokens=target_length - RUN.TASK_RESERVES[task],
                    row_length=target_length,
                ))
    if os.name == "posix":
        os.chmod(root, 0o700)
        for path in root.iterdir():
            if path.is_file():
                os.chmod(path, 0o600)
    return RUN.PublicSuite(
        path=manifest,
        sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        manifest={},
        fixtures=tuple(fixtures),
    )


def sealed_public_manifest(root: Path) -> Path:
    root = root.resolve()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    payloads = root / "payloads"
    payloads.mkdir(mode=0o700)
    entries = []
    for target_length in RUN.TARGET_LENGTHS:
        for task in RUN.TASKS:
            for index in range(10):
                fixture_id = f"f-{task}-{target_length}-{index}"
                data = f"official prompt {task} {target_length} {index}".encode()
                payload = payloads / f"{fixture_id}.txt"
                payload.write_bytes(data)
                if os.name == "posix":
                    os.chmod(payload, 0o600)
                entries.append({
                    "id": fixture_id,
                    "task": task,
                    "target_length": target_length,
                    "payload": f"payloads/{fixture_id}.txt",
                    "payload_sha256": hashlib.sha256(data).hexdigest(),
                    "payload_bytes": len(data),
                    "construction_tokens": target_length - RUN.TASK_RESERVES[task],
                    "row_length": target_length,
                })
    for name, data in (
        ("LICENSE.NVIDIA-RULER", TEST_LICENSE_DATA),
        ("THIRD_PARTY_NOTICES.md", TEST_NOTICE_DATA),
    ):
        target = root / name
        target.write_bytes(data)
        if os.name == "posix":
            os.chmod(target, 0o600)
    source_hashes = dict(RUN.EXPECTED_RULER_SOURCE_HASHES)
    source_hashes["LICENSE"] = hashlib.sha256(TEST_LICENSE_DATA).hexdigest()
    document = {
        "schema_version": 1,
        "record_type": "ruler_exact_mini_public_manifest",
        "suite_id": RUN.SUITE_ID,
        "upstream_commit": RUN.RULER_COMMIT,
        "source": {"name": "NVIDIA/RULER", "url": RUN.RULER_URL, "commit": RUN.RULER_COMMIT},
        "configuration": {
            "tasks": list(RUN.TASKS),
            "target_lengths": list(RUN.TARGET_LENGTHS),
            "pool_size": 100,
            "per_cell": 10,
            "tokenizer": "cl100k_base",
            "task_generation_reserves": RUN.TASK_RESERVES,
            "payload_rule": 'row["input"] + row["answer_prefix"]',
            "selection": {
                "niah_multikey_3": "one secret-HMAC-ranked row per answer-position decile",
                "vt": "ten secret-HMAC-ranked line ordinals",
                "fwe": "ten secret-HMAC-ranked line ordinals",
            },
        },
        "provenance_commitments": {
            "generation_plan_sha256": "a" * 64,
            "requirements_lock_sha256": RUN.REQUIREMENTS_LOCK_SHA256,
            "tokenizer_blob_sha256": RUN.TOKENIZER_BLOB_SHA256,
            "ruler_source_files": source_hashes,
        },
        "redistribution_files": {
            "LICENSE.NVIDIA-RULER": hashlib.sha256(TEST_LICENSE_DATA).hexdigest(),
            "THIRD_PARTY_NOTICES.md": TEST_NOTICE_SHA256,
        },
        "fixtures": entries,
        "gold_sha256": hashlib.sha256(TEST_GOLD_DATA).hexdigest(),
    }
    manifest = root / "manifest.json"
    manifest.write_bytes(RUN.canonical_json_file_bytes(document))
    if os.name == "posix":
        os.chmod(root, 0o700)
        os.chmod(payloads, 0o700)
        os.chmod(manifest, 0o600)
    return manifest


def test_sealed_constants():
    source_hashes = dict(RUN.EXPECTED_RULER_SOURCE_HASHES)
    source_hashes["LICENSE"] = hashlib.sha256(TEST_LICENSE_DATA).hexdigest()
    return mock.patch.multiple(
        RUN,
        EXPECTED_RULER_SOURCE_HASHES=source_hashes,
        THIRD_PARTY_NOTICES_SHA256=TEST_NOTICE_SHA256,
    )


class RulerRunnerTests(unittest.TestCase):
    def identities(self):
        candidate = TEST_CANDIDATE
        controller_components = TEST_CONTROLLER["components"]
        controller_bound = {
            name: {"sha256": value["sha256"], "bytes": value["bytes"]}
            for name, value in sorted(controller_components.items())
        }
        controller = {
            "sha256": RUN.sha256_bytes(RUN.canonical_json_bytes(controller_bound)),
            "components": controller_components,
        }
        identity_path = TEST_EXECUTABLE
        return candidate, controller, {
            "jcode": {
                "path": str(identity_path), "sha256": RUN.sha256_path(identity_path),
                "bytes": identity_path.stat().st_size,
            }
        }

    def test_atomic_private_json_rejects_existing_symlink_and_hardlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            victim = root / "victim"
            victim.write_text("survive", encoding="utf-8")
            os.chmod(victim, 0o600)
            destination = root / "claim.json"
            destination.symlink_to(victim)
            with self.assertRaises(RUN.BenchError):
                RUN.atomic_create_private_json(destination, {"claim": 1})
            self.assertEqual(victim.read_text(), "survive")
            destination.unlink()
            os.link(victim, destination)
            with self.assertRaises(RUN.BenchError):
                RUN.atomic_create_private_json(destination, {"claim": 1})
            self.assertEqual(victim.read_text(), "survive")

    def test_append_jsonl_binds_pre_inference_absence_or_size(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            output = root / "runs.jsonl"
            expected = RUN.secure_private_file_token(output, "test output")
            self.assertIsNone(expected)
            output.write_text("intrusion\n", encoding="utf-8")
            os.chmod(output, 0o600)
            with self.assertRaises(RUN.BenchError):
                RUN.append_private_jsonl(output, {"x": 1}, expected_token=expected)
            self.assertEqual(output.read_text(), "intrusion\n")
            expected = RUN.secure_private_file_token(output, "test output")
            with output.open("a", encoding="utf-8") as stream:
                stream.write("raced\n")
            with self.assertRaisesRegex(RUN.BenchError, "identity/size changed"):
                RUN.append_private_jsonl(output, {"x": 1}, expected_token=expected)

    def test_append_jsonl_rejects_symlink_and_hardlink_victims(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            victim = root / "victim"
            victim.write_text("must survive", encoding="utf-8")
            os.chmod(victim, 0o600)
            link = root / "runs.jsonl"
            link.symlink_to(victim)
            with self.assertRaises(RUN.BenchError):
                RUN.append_private_jsonl(link, {"x": 1})
            self.assertEqual(victim.read_text(), "must survive")
            link.unlink()
            os.link(victim, link)
            with self.assertRaisesRegex(RUN.BenchError, "single-link"):
                RUN.append_private_jsonl(link, {"x": 1})
            self.assertEqual(victim.read_text(), "must survive")

    def test_trace_capture_rejects_symlink_and_hardlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            trace = root / "trace.jsonl"
            trace.write_text('{"type":"tokens"}\n', encoding="utf-8")
            if os.name == "posix":
                os.chmod(trace, 0o600)
            alias = root / "alias"
            os.link(trace, alias)
            with self.assertRaisesRegex(RUN.BenchError, "single-link"):
                RUN.capture_trace_artifact_secure(trace, "trace")
            alias.unlink()
            link = root / "link"
            link.symlink_to(trace)
            with self.assertRaises(RUN.BenchError):
                RUN.capture_trace_artifact_secure(link, "trace link")

    def test_private_json_rejects_lone_surrogate_as_bench_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve() / "bad.json"
            path.write_bytes(b'{"x":"\\ud800"}\n')
            if os.name == "posix":
                os.chmod(path, 0o600)
            with self.assertRaisesRegex(RUN.BenchError, "canonical UTF-8"):
                RUN.load_private_json(path, "surrogate JSON")

    def test_manifest_rejects_gold_path_substitution(self):
        with test_sealed_constants(), tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "sealed"
            manifest = sealed_public_manifest(root)
            document = json.loads(manifest.read_text())
            fixture = document["fixtures"][0]
            fixture["payload"] = "gold.json"
            manifest.write_bytes(RUN.canonical_json_file_bytes(document))
            if os.name == "posix":
                os.chmod(manifest, 0o600)
            with self.assertRaisesRegex(RUN.BenchError, "payload must be exactly"):
                RUN.load_public_manifest(manifest)

    def test_manifest_rejects_payload_hardlink_to_gold(self):
        if not hasattr(os, "link"):
            self.skipTest("hard links unavailable")
        with test_sealed_constants(), tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "sealed"
            manifest = sealed_public_manifest(root)
            document = json.loads(manifest.read_text())
            fixture = document["fixtures"][0]
            other = document["fixtures"][1]
            payload = root / fixture["payload"]
            other_payload = root / other["payload"]
            other_payload.unlink()
            os.link(payload, other_payload)
            with self.assertRaisesRegex(RUN.BenchError, "exactly one hard link"):
                RUN.load_public_manifest(manifest)

    def test_staging_uses_captured_bytes_without_reopening_source(self):
        with test_sealed_constants(), tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "sealed"
            suite = RUN.load_public_manifest(sealed_public_manifest(root))
            fixture = suite.fixtures[0]
            fixture.payload_path.unlink()
            run_dir = Path(directory).resolve() / "arm"
            run_dir.mkdir(mode=0o700)
            task, staged, evidence = RUN.stage_payload(
                fixture, run_dir, "abcdefabcdefabcdefabcdefabcdefab.txt"
            )
            self.assertEqual(staged.read_bytes(), fixture.payload_data)
            self.assertTrue(RUN.finalize_payload(fixture, task, staged, evidence)["asserted_after"])

    def test_wrapper_is_one_fixed_dataset_neutral_file_wrapper(self):
        name = "0123456789abcdef0123456789abcdef.txt"
        prompt = RUN.wrapper_for(name)
        self.assertEqual(
            prompt,
            "Treat the attached file 0123456789abcdef0123456789abcdef.txt as the "
            "official RULER prompt. Read the complete file, follow its prompt, and "
            "return only its requested answer with no explanation or other text.",
        )
        self.assertNotIn("gold", prompt.lower())
        with self.assertRaises(RUN.BenchError):
            RUN.wrapper_for("../gold.json")

    def test_controller_identity_hash_binds_imported_oolong_module(self):
        identity = RUN.controller_identity()
        self.assertEqual(
            identity["components"]["oolong_execution_module"]["sha256"],
            RUN.sha256_path(RUN.OOLONG_MODULE_PATH),
        )
        bound = {
            name: {"sha256": value["sha256"], "bytes": value["bytes"]}
            for name, value in sorted(identity["components"].items())
        }
        self.assertEqual(identity["sha256"], RUN.sha256_bytes(RUN.canonical_json_bytes(bound)))

    def test_candidate_snapshot_rejects_symlink_and_hardlink_components(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "source"
            source.mkdir(mode=0o700)
            for name, data, mode in (
                ("azdaja", b"#!/bin/sh\n", 0o755),
                ("config.toml", b"x=1\n", 0o644),
                ("SKILL.md", b"# azdaja\n", 0o644),
            ):
                path = source / name
                path.write_bytes(data)
                os.chmod(path, mode)
            target = root / "target"
            target.write_bytes(b"x=1\n")
            os.chmod(target, 0o644)
            (source / "config.toml").unlink()
            (source / "config.toml").symlink_to(target)
            symlink_snapshot = root / "symlink-snapshot"
            symlink_snapshot.mkdir(mode=0o700)
            with self.assertRaisesRegex(RUN.BenchError, "symlink"):
                RUN.snapshot_candidate(source, symlink_snapshot)
            (source / "config.toml").unlink()
            os.link(target, source / "config.toml")
            hardlink_snapshot = root / "hardlink-snapshot"
            hardlink_snapshot.mkdir(mode=0o700)
            with self.assertRaisesRegex(RUN.BenchError, "single-link"):
                RUN.snapshot_candidate(source, hardlink_snapshot)

    def test_candidate_snapshot_excludes_undeclared_extra_files_and_subdirs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "source"
            source.mkdir(mode=0o700)
            for name, data, mode in (
                ("azdaja", b"#!/bin/sh\n", 0o755),
                ("config.toml", b"x=1\n", 0o644),
                ("SKILL.md", b"# azdaja\n", 0o644),
            ):
                path = source / name
                path.write_bytes(data)
                os.chmod(path, mode)
            (source / ".azdaja-managed").write_text("behavior", encoding="utf-8")
            extra = source / "hooks"
            extra.mkdir()
            (extra / "run.py").write_text("raise SystemExit", encoding="utf-8")
            frozen_root = root / "candidate"
            frozen_root.mkdir(mode=0o700)
            candidate = RUN.snapshot_candidate(source, frozen_root)
            RUN.validate_candidate_snapshot(candidate)
            self.assertEqual(
                {entry.name for entry in frozen_root.iterdir()},
                {"azdaja", "config.toml", "SKILL.md"},
            )
            self.assertNotIn(".azdaja-managed", json.dumps(candidate))
            self.assertNotIn("hooks", json.dumps(candidate))

    @unittest.skipUnless(shutil.which("prime-agent"), "Prime Agent CLI not installed")
    def test_real_prime_bundle_snapshot_version_matches_source(self):
        source_command = shutil.which("prime-agent")
        assert source_command is not None
        source = Path(source_command).resolve()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "executables"
            root.mkdir(mode=0o700)
            source_identity = RUN.OOLONG.executable_identity(str(source), "prime-agent")
            frozen = RUN.snapshot_executables(
                {"prime-agent": source_identity}, root
            )["prime-agent"]
            RUN.validate_prime_bundle_identity(frozen["bundle"], Path(frozen["path"]))
            self.assertEqual(frozen["smoke"]["returncode"], 0)
            self.assertTrue(frozen["smoke"]["matched_source_version"])
            self.assertEqual(frozen["version_command"], [frozen["path"], "--version"])
            source_version = subprocess.run(
                [str(source), "--version"], check=True, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            frozen_version = subprocess.run(
                [frozen["path"], "--version"], check=True, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            self.assertEqual(frozen_version.returncode, source_version.returncode)
            self.assertEqual(
                (frozen_version.stdout + frozen_version.stderr).splitlines()[-1],
                (source_version.stdout + source_version.stderr).splitlines()[-1],
            )
            self.assertEqual(
                len(frozen["bundle"]["files"]),
                len({item["relative_path"] for item in frozen["bundle"]["files"]}),
            )

    def test_identity_snapshots_are_owner_only_exact_and_source_paths_are_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            controller_root = root / "controller"
            executable_root = root / "executables"
            controller_root.mkdir(mode=0o700)
            executable_root.mkdir(mode=0o700)
            controller, source_paths = RUN.snapshot_controller(controller_root)
            self.assertEqual(set(source_paths), {"ruler_runner", "oolong_execution_module"})
            self.assertEqual(controller["sha256"], RUN.controller_identity()["sha256"])
            for component in controller["components"].values():
                snapshot = Path(component["path"])
                self.assertTrue(snapshot.is_file())
                self.assertEqual(RUN.sha256_path(snapshot), component["sha256"])
                if os.name == "posix":
                    self.assertEqual(stat.S_IMODE(snapshot.stat().st_mode), 0o500)
            source = root / "source-executable"
            source.write_bytes(b"frozen executable bytes")
            source.chmod(0o700)
            source_identities = {
                "jcode": {
                    "path": str(source), "sha256": RUN.sha256_path(source),
                    "bytes": source.stat().st_size, "version": "jcode 1",
                    "version_command": [str(source), "--version"],
                }
            }
            frozen = RUN.snapshot_executables(source_identities, executable_root)["jcode"]
            self.assertNotEqual(frozen["path"], str(source))
            self.assertEqual(frozen["sha256"], RUN.sha256_path(source))
            self.assertEqual(Path(frozen["path"]).read_bytes(), source.read_bytes())

    def test_balanced_schedule_has_complete_grid_and_identical_fixture_names(self):
        with tempfile.TemporaryDirectory() as directory:
            suite = fake_suite(Path(directory))
            candidate, controller, executables = self.identities()
            names = [f"{index:032x}.txt" for index in range(90)]
            schedule = RUN.build_schedule(
                suite, seed=7, timeout=1800, candidate=candidate,
                candidate_source_path="/test/candidate-source",
                controller=controller, controller_source_paths={
                    "ruler_runner": controller["components"]["ruler_runner"]["path"],
                    "oolong_execution_module": controller["components"]["oolong_execution_module"]["path"],
                }, executables=executables, random_names=names,
            )
            RUN.validate_schedule(
                schedule, suite, seed=7, timeout=1800, candidate=candidate,
                candidate_source_path="/test/candidate-source",
                controller=controller, controller_source_paths={
                    "ruler_runner": controller["components"]["ruler_runner"]["path"],
                    "oolong_execution_module": controller["components"]["oolong_execution_module"]["path"],
                }, executables=executables,
            )
            self.assertEqual(len(schedule["jobs"]), 270)
            self.assertEqual(schedule["configuration"]["model"], "gpt-5.6-luna")
            self.assertEqual(schedule["configuration"]["reasoning"], "medium")
            self.assertEqual(schedule["configuration"]["arms"], list(RUN.ARMS))
            self.assertEqual(schedule["configuration"]["repetitions"], 1)
            groups = [schedule["jobs"][index:index + 3] for index in range(0, 270, 3)]
            counts = {permutation: 0 for permutation in itertools.permutations(RUN.ARMS)}
            for group in groups:
                self.assertEqual(len({job["fixture_id"] for job in group}), 1)
                self.assertEqual(len({job["staged_filename"] for job in group}), 1)
                counts[tuple(job["arm"] for job in group)] += 1
            self.assertEqual(set(counts.values()), {15})
            self.assertEqual(len({job["run_id"] for job in schedule["jobs"]}), 270)
            self.assertFalse(schedule["configuration"]["containment"]["os_level_asserted"])
            self.assertIn("not authenticated", schedule["configuration"]["containment"]["claim_ledger"])

    def test_schedule_tampering_and_resume_identity_drift_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            suite = fake_suite(Path(directory))
            candidate, controller, executables = self.identities()
            schedule = RUN.build_schedule(
                suite, seed=3, timeout=1800, candidate=candidate,
                candidate_source_path="/test/candidate-source",
                controller=controller, controller_source_paths={
                    "ruler_runner": controller["components"]["ruler_runner"]["path"],
                    "oolong_execution_module": controller["components"]["oolong_execution_module"]["path"],
                }, executables=executables,
                random_names=[f"{index:032x}.txt" for index in range(90)],
            )
            tampered = copy.deepcopy(schedule)
            tampered["jobs"][0]["arm"] = "prime-agent"
            with self.assertRaises(RUN.BenchError):
                RUN.validate_schedule(
                    tampered, suite, seed=3, timeout=1800, candidate=candidate,
                    candidate_source_path="/test/candidate-source",
                    controller=controller, controller_source_paths={
                    "ruler_runner": controller["components"]["ruler_runner"]["path"],
                    "oolong_execution_module": controller["components"]["oolong_execution_module"]["path"],
                }, executables=executables,
                )
            with self.assertRaises(RUN.BenchError):
                RUN.validate_schedule(
                    schedule, suite, seed=4, timeout=1800, candidate=candidate,
                    candidate_source_path="/test/candidate-source",
                    controller=controller, controller_source_paths={
                    "ruler_runner": controller["components"]["ruler_runner"]["path"],
                    "oolong_execution_module": controller["components"]["oolong_execution_module"]["path"],
                }, executables=executables,
                )

    def test_identical_read_only_staging_and_post_run_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            suite = fake_suite(root)
            fixture = suite.fixtures[0]
            names = "feedfacefeedfacefeedfacefeedface.txt"
            staged_hashes = []
            for arm in RUN.ARMS:
                run_dir = root / arm
                run_dir.mkdir(mode=0o700)
                task, staged, evidence = RUN.stage_payload(fixture, run_dir, names)
                self.assertEqual(staged.name, names)
                self.assertEqual(stat.S_IMODE(staged.stat().st_mode), 0o444)
                self.assertEqual(list(task.iterdir()), [staged])
                staged_hashes.append(RUN.sha256_path(staged))
                finished = RUN.finalize_payload(fixture, task, staged, evidence)
                self.assertTrue(finished["asserted_after"])
            self.assertEqual(set(staged_hashes), {fixture.payload_sha256})

    def test_normalized_usage_is_arm_specific_and_fail_closed(self):
        jcode = json.dumps({
            "type": "tokens", "input": 10, "output": 2,
            "cache_read_input": 3, "cache_creation_input": 4,
        })
        normalized, evidence = RUN._normalized_usage("jcode-native", jcode, "", None)
        self.assertTrue(evidence["asserted"])
        self.assertEqual(normalized, {
            "input_tokens": 10, "output_tokens": 2, "cache_read_tokens": 3,
            "cache_write_tokens": 4, "total_tokens": 12, "accounting_complete": True,
        })
        prime = json.dumps({
            "type": "message_end", "message": {"role": "assistant", "usage": {
                "input": 10, "output": 2, "cacheRead": 3, "cacheWrite": 4,
                "totalTokens": 19,
            }}
        })
        prime_normalized, prime_evidence = RUN._normalized_usage(
            "prime-agent", prime, "", None
        )
        self.assertTrue(prime_evidence["asserted"])
        self.assertEqual(prime_normalized["total_tokens"], 19)
        missing, missing_evidence = RUN._normalized_usage("jcode-native", "", "", None)
        self.assertIsNone(missing)
        self.assertFalse(missing_evidence["asserted"])

    def test_route_normalization_requires_runtime_and_subscription_evidence(self):
        auth = {"asserted": True, "method": "subscription-oauth"}
        done = json.dumps({"type": "done", "provider": "OpenAI", "model": RUN.MODEL})
        route, evidence = RUN._normalized_route("jcode-native", done, auth, None)
        self.assertEqual(route, {
            "asserted": True, "subscription": True,
            "provider": "OpenAI OAuth", "model": RUN.MODEL,
        })
        self.assertTrue(evidence["raw_runtime_route"]["asserted"])
        denied, _ = RUN._normalized_route("jcode-native", "", auth, None)
        self.assertFalse(denied["asserted"])

    def test_schedule_must_be_exact_seed_reconstruction_not_just_balanced(self):
        with tempfile.TemporaryDirectory() as directory:
            suite = fake_suite(Path(directory))
            candidate, controller, executables = self.identities()
            schedule = RUN.build_schedule(
                suite, seed=19, timeout=1800, candidate=candidate,
                candidate_source_path="/test/candidate-source",
                controller=controller, controller_source_paths={
                    "ruler_runner": controller["components"]["ruler_runner"]["path"],
                    "oolong_execution_module": controller["components"]["oolong_execution_module"]["path"],
                }, executables=executables,
                random_names=[f"{index:032x}.txt" for index in range(90)],
            )
            changed = copy.deepcopy(schedule)
            # Swap two complete fixture blocks. The grid and exact six-way arm
            # balance remain valid, and all cryptographic IDs are recomputed.
            changed["jobs"][:3], changed["jobs"][3:6] = changed["jobs"][3:6], changed["jobs"][:3]
            for ordinal, job in enumerate(changed["jobs"], 1):
                job["ordinal"] = ordinal
                job.pop("run_id")
            identity = copy.deepcopy(changed)
            identity.pop("schedule_id")
            for job in identity["jobs"]:
                job.pop("run_id", None)
            changed["schedule_id"] = RUN.sha256_bytes(RUN.canonical_json_bytes(identity))
            for job in changed["jobs"]:
                job["run_id"] = RUN.sha256_bytes(
                    RUN.RUN_ID_DOMAIN + changed["schedule_id"].encode("ascii")
                    + RUN.canonical_json_bytes(job)
                )
            with self.assertRaisesRegex(RUN.BenchError, "exact reconstruction"):
                RUN.validate_schedule(
                    changed, suite, seed=19, timeout=1800, candidate=candidate,
                    candidate_source_path="/test/candidate-source",
                    controller=controller, controller_source_paths={
                    "ruler_runner": controller["components"]["ruler_runner"]["path"],
                    "oolong_execution_module": controller["components"]["oolong_execution_module"]["path"],
                }, executables=executables,
                )

    def test_result_prefix_rejects_symlink_and_hardlink_before_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            suite = fake_suite(root)
            candidate, controller, executables = self.identities()
            schedule = RUN.build_schedule(
                suite, seed=37, timeout=1800, candidate=candidate,
                candidate_source_path="/test/candidate-source",
                controller=controller, controller_source_paths={
                    "ruler_runner": controller["components"]["ruler_runner"]["path"],
                    "oolong_execution_module": controller["components"]["oolong_execution_module"]["path"],
                }, executables=executables,
                random_names=[f"{index:032x}.txt" for index in range(90)],
            )
            victim = root / "victim"
            victim.write_text("{}\n", encoding="utf-8")
            os.chmod(victim, 0o600)
            output = root / "runs.jsonl"
            output.symlink_to(victim)
            with self.assertRaises(RUN.BenchError):
                RUN.validate_result_prefix(output, schedule)
            output.unlink()
            os.link(victim, output)
            with self.assertRaisesRegex(RUN.BenchError, "exactly one hard link"):
                RUN.validate_result_prefix(output, schedule)
            output.unlink()
            rows, absent_state = RUN.validate_result_prefix(output, schedule)
            self.assertEqual(rows, [])
            self.assertIsNone(absent_state)
            output.write_text("intrusion\n", encoding="utf-8")
            os.chmod(output, 0o600)
            with self.assertRaises(RUN.BenchError):
                RUN.append_private_jsonl(output, {"x": 1}, expected_token=absent_state)

    def test_strict_prefix_claim_completion_and_no_gold_or_scores(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            suite = fake_suite(root)
            candidate, controller, executables = self.identities()
            schedule = RUN.build_schedule(
                suite, seed=5, timeout=1800, candidate=candidate,
                candidate_source_path="/test/candidate-source",
                controller=controller, controller_source_paths={
                    "ruler_runner": controller["components"]["ruler_runner"]["path"],
                    "oolong_execution_module": controller["components"]["oolong_execution_module"]["path"],
                }, executables=executables,
                random_names=[f"{index:032x}.txt" for index in range(90)],
            )
            output = root / "runs.jsonl"
            claims = root / "claims"
            claims.mkdir(mode=0o700)
            job = schedule["jobs"][0]
            row = {
                **RUN._expected_envelope(schedule, job),
                "execution_success": True,
                "timed_out": False,
                "exit_code": 0,
                "latency_seconds": 1.25,
                "response": "requested answer",
                "route_assertion": {
                    "asserted": True, "subscription": True,
                    "provider": "OpenAI OAuth", "model": RUN.MODEL,
                },
                "usage": {
                    "input_tokens": 10, "output_tokens": 2,
                    "cache_read_tokens": 3, "cache_write_tokens": 0,
                    "total_tokens": 12, "accounting_complete": True,
                },
                "lifecycle_assertion": {
                    "asserted": True, "isolated_home": True,
                    "fresh_session": True, "cleanup_complete": True,
                },
                "failure": None,
            }
            RUN.atomic_create_private_json(claims / f"{job['run_id']}.json", {
                "schedule_id": schedule["schedule_id"], "run_id": job["run_id"],
                "ordinal": job["ordinal"], "pid": 123,
            })
            RUN.append_private_jsonl(output, row)
            RUN.atomic_create_private_json(claims / f"{job['run_id']}.done.json", {
                "schedule_id": schedule["schedule_id"], "run_id": job["run_id"],
                "row_sha256": RUN.sha256_bytes(RUN.canonical_json_bytes(row)),
            })
            rows, output_state = RUN.validate_result_prefix(output, schedule, claims)
            self.assertIsNotNone(output_state)
            self.assertEqual(rows, [row])
            self.assertIsNone(row["success"])
            self.assertIsNone(row["score"])
            forbidden = {"gold", "outputs", "expected", "correct", "scores"}
            self.assertTrue(forbidden.isdisjoint(row))
            original = output.read_bytes()
            output.unlink()
            output.write_bytes(original)
            if os.name == "posix":
                os.chmod(output, 0o600)
            with self.assertRaisesRegex(RUN.BenchError, "identity/size changed"):
                RUN.append_private_jsonl(output, {"x": 1}, expected_token=output_state)
            corrupted = output.read_bytes()[:-1]
            output.write_bytes(corrupted)
            if os.name == "posix":
                os.chmod(output, 0o600)
            with self.assertRaises(RUN.BenchError):
                RUN.validate_result_prefix(output, schedule, claims)

    def test_runner_schedule_satisfies_live_scorer_contract(self):
        score_spec = importlib.util.spec_from_file_location(
            "azdaja_ruler_score_for_runner_test", HERE / "score.py"
        )
        scorer = importlib.util.module_from_spec(score_spec)
        sys.modules[score_spec.name] = scorer
        assert score_spec.loader is not None
        score_spec.loader.exec_module(scorer)
        with tempfile.TemporaryDirectory() as directory:
            suite = fake_suite(Path(directory))
            if shutil.which("prime-agent") is None:
                self.skipTest("Prime Agent CLI not installed")
            identity_root = Path(directory).resolve() / "identity"
            identity_root.mkdir(mode=0o700)
            candidate_root = identity_root / "candidate"
            candidate_root.mkdir(mode=0o700)
            candidate = RUN.snapshot_candidate(TEST_CANDIDATE_SOURCE, candidate_root)
            controller_root = identity_root / "controller"
            controller_root.mkdir(mode=0o700)
            controller, controller_source_paths = RUN.snapshot_controller(controller_root)
            executables = {}
            executable_root = identity_root / "executables"
            executable_root.mkdir(mode=0o700)
            for name in ("jcode", "azdaja"):
                executable_path = executable_root / f"identity-{name}"
                executable_path.write_bytes(f"{name} immutable bytes".encode())
                if os.name == "posix":
                    os.chmod(executable_path, 0o500)
                executables[name] = {
                    "path": str(executable_path),
                    "sha256": RUN.sha256_path(executable_path),
                    "bytes": executable_path.stat().st_size,
                    "version": f"{name} 1",
                    "version_command": [str(executable_path), "--version"],
                    "bundle": None,
                    "smoke": None,
                }
            prime_path = Path(shutil.which("prime-agent")).resolve()
            prime_identity = RUN.OOLONG.executable_identity(str(prime_path), "prime-agent")
            executables.update(RUN.snapshot_executables(
                {"prime-agent": prime_identity}, executable_root
            ))
            schedule = RUN.build_schedule(
                suite, seed=11, timeout=1800, candidate=candidate,
                candidate_source_path="/test/candidate-source",
                controller=controller,
                controller_source_paths=controller_source_paths,
                executables=executables,
                random_names=[f"{index:032x}.txt" for index in range(90)],
            )
            public = {
                fixture.fixture_id: {
                    "id": fixture.fixture_id, "task": fixture.task,
                    "target_length": fixture.target_length,
                    "payload_sha256": fixture.payload_sha256,
                }
                for fixture in suite.fixtures
            }
            # scorer binds the canonical supplied manifest, so make the fake
            # suite identity use those exact bytes for this cross-module check.
            manifest = {"fake": "manifest"}
            schedule["suite"]["manifest_sha256"] = scorer.sha256_bytes(
                scorer.canonical_json_file_bytes(manifest)
            )
            identity = copy.deepcopy(schedule)
            identity.pop("schedule_id")
            for job in identity["jobs"]:
                job.pop("run_id")
            schedule_id = scorer.sha256_bytes(scorer.canonical_json_bytes(identity))
            schedule["schedule_id"] = schedule_id
            for job in schedule["jobs"]:
                job.pop("run_id")
                job["run_id"] = scorer.sha256_bytes(
                    scorer.RUN_ID_DOMAIN + schedule_id.encode("ascii")
                    + scorer.canonical_json_bytes(job)
                )
            jobs, arms = scorer.validate_schedule(
                schedule, suite.path, manifest, public
            )
            self.assertEqual(len(jobs), 270)
            self.assertEqual(arms, RUN.ARMS)

    def test_parser_exposes_no_gold_scoring_or_arm_model_overrides(self):
        options = {action.dest for action in RUN.parser()._actions}
        self.assertIn("manifest", options)
        self.assertIn("resume", options)
        for forbidden in ("gold", "scores", "model", "reasoning", "arms", "repetitions"):
            self.assertNotIn(forbidden, options)


if __name__ == "__main__":
    unittest.main()
