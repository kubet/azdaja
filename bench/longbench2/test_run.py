#!/usr/bin/env python3
"""Security/contract tests for the no-gold LongBench-v2 runner."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import random
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent

# Import the current scorer independently. Tests use its public validator as the
# contract authority rather than duplicating schedule/run acceptance logic.
SCORE_SPEC = importlib.util.spec_from_file_location(
    "azdaja_lb2_live_score_in_run_tests", HERE / "score.py"
)
SCORE = importlib.util.module_from_spec(SCORE_SPEC)
sys.modules[SCORE_SPEC.name] = SCORE
assert SCORE_SPEC.loader is not None
SCORE_SPEC.loader.exec_module(SCORE)

RUN_SPEC = importlib.util.spec_from_file_location(
    "azdaja_lb2_runner_under_test", HERE / "run.py"
)
RUN = importlib.util.module_from_spec(RUN_SPEC)
sys.modules[RUN_SPEC.name] = RUN
assert RUN_SPEC.loader is not None
RUN_SPEC.loader.exec_module(RUN)

TMP_PARENT = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp")


def private_json(path: Path, value: object) -> None:
    path.write_bytes(SCORE.canonical_json_file_bytes(value))
    path.chmod(0o600)


def private_bytes(path: Path, value: bytes) -> None:
    path.write_bytes(value)
    path.chmod(0o600)


def make_writable(root: Path) -> None:
    if not root.exists():
        return
    for directory, dirnames, filenames in os.walk(root, topdown=False, followlinks=False):
        for name in filenames:
            path = Path(directory) / name
            if not path.is_symlink():
                try:
                    path.chmod(0o600)
                except OSError:
                    pass
        for name in dirnames:
            path = Path(directory) / name
            if not path.is_symlink():
                try:
                    path.chmod(0o700)
                except OSError:
                    pass
        try:
            Path(directory).chmod(0o700)
        except OSError:
            pass


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=TMP_PARENT)
        self.root = Path(self.temp.name)
        self.root.chmod(0o700)

    def tearDown(self) -> None:
        make_writable(self.root)
        self.temp.cleanup()

    def make_public(self, *, payload_extra: dict[str, object] | None = None):
        public = self.root / f"public-{len(list(self.root.glob('public-*')))}"
        public.mkdir(mode=0o700)
        payloads = public / "payloads"
        payloads.mkdir(mode=0o700)
        for name in SCORE.PUBLIC_NOTICE_FILES:
            private_bytes(public / name, (HERE / name).read_bytes())
        domains = [
            value
            for value, count in SCORE.SELECTED_DOMAIN_COUNTS.items()
            for _ in range(count)
        ]
        sub_domains = [
            value
            for value, count in SCORE.SELECTED_SUB_DOMAIN_COUNTS.items()
            for _ in range(count)
        ]
        fixtures = []
        for index in range(SCORE.EXPECTED_FIXTURES):
            fixture_id = f"lb2-{index:032x}"
            payload: dict[str, object] = {
                "question": f"Question {index}?",
                "context": f"Context {index}.",
                "choices": {
                    label: f"Choice {label} {index}" for label in SCORE.CHOICE_LABELS
                },
            }
            if index == 0 and payload_extra:
                payload.update(payload_extra)
            path = payloads / f"{fixture_id}.json"
            private_json(path, payload)
            data = path.read_bytes()
            fixtures.append(
                {
                    "id": fixture_id,
                    "domain": domains[index],
                    "sub_domain": sub_domains[index],
                    "payload": f"payloads/{fixture_id}.json",
                    "payload_sha256": hashlib.sha256(data).hexdigest(),
                    "payload_bytes": len(data),
                }
            )
        manifest = {
            "schema_version": SCORE.SCHEMA_VERSION,
            "record_type": "lb2_hard_long_public_manifest",
            "suite_id": SCORE.SUITE_ID,
            "source": {
                "name": SCORE.SOURCE_NAME,
                "url": SCORE.SOURCE_URL,
                "revision": SCORE.SOURCE_REVISION,
            },
            "configuration": {
                "difficulty": "hard",
                "length": "long",
                "source_row_count": SCORE.EXPECTED_SOURCE_COUNT,
                "fixture_count": SCORE.EXPECTED_FIXTURES,
                "payload_schema": ["question", "context", "choices"],
                "choice_labels": list(SCORE.CHOICE_LABELS),
                "domain_counts": SCORE.SELECTED_DOMAIN_COUNTS,
                "sub_domain_counts": SCORE.SELECTED_SUB_DOMAIN_COUNTS,
            },
            "provenance_commitments": {
                "data_json_sha256": SCORE.SOURCE_FILES["data.json"]["sha256"],
                "readme_sha256": SCORE.SOURCE_FILES["README.md"]["sha256"],
                "gitattributes_sha256": SCORE.SOURCE_FILES[".gitattributes"]["sha256"],
                "requirements_lock_sha256": SCORE.REQUIREMENTS_LOCK_SHA256,
                "public_notice_files": {
                    name: metadata["sha256"]
                    for name, metadata in SCORE.PUBLIC_NOTICE_FILES.items()
                },
            },
            "fixtures": fixtures,
            # It is a one-way public commitment, not an opened/provided gold path.
            "gold_sha256": "f" * 64,
        }
        manifest_path = public / "manifest.json"
        private_json(manifest_path, manifest)
        return manifest_path, public, fixtures

    def fake_schedule(self, suite):
        candidate_components = {
            name: {"sha256": str(index) * 64, "bytes": index}
            for index, name in enumerate(RUN.CANDIDATE_ALLOWLIST, 1)
        }
        candidate = {
            "components": candidate_components,
            "sha256": SCORE.sha256_bytes(
                SCORE.canonical_json_bytes(candidate_components)
            ),
        }
        controller = {
            "path": "/frozen/run.py", "sha256": "b" * 64, "bytes": 10
        }
        executables = {}
        for name, digit in zip(("jcode", "azdaja", "prime-agent"), "cde"):
            path = f"/frozen/{name}"
            executables[name] = {
                "path": path,
                "sha256": digit * 64,
                "bytes": 11,
                "version": f"{name} test",
                "version_command": [path, "--version"],
            }
        runtime_closure = {
            "adapter": {"path": "/frozen/adapter.py", "sha256": "6" * 64, "bytes": 16},
            "validator": {"path": "/frozen/score.py", "sha256": "7" * 64, "bytes": 17},
            "prime_package": {
                "snapshot_root": "/frozen/prime-package", "inventory_sha256": "8" * 64,
                "entry_count": 100, "cli_relative": "dist/bundle/cli.js",
            },
            "node": {
                "path": "/frozen/node", "sha256": "9" * 64, "bytes": 18,
                "version": "node test", "version_command": ["/frozen/node", "--version"],
            },
            "kernel_python": {
                "path": "/frozen/python", "sha256": "a" * 64, "bytes": 19,
                "version": "python test", "version_command": ["/frozen/python", "--version"],
            },
            "kernel_launcher": {
                "path": "/frozen/kernel/bin/python",
                "target": "../../runtime-python/bin/python3.11",
                "resolved_path": "/frozen/runtime-python/bin/python3.11",
            },
            "kernel_environment": {
                "root": "/frozen/kernel", "inventory_sha256": "f" * 64, "entry_count": 200,
            },
            "runtime_python": {
                "snapshot_root": "/frozen/runtime-python",
                "inventory_sha256": "0" * 64, "entry_count": 300,
            },
            "ambient_closure_disclosure": SCORE.AMBIENT_CLOSURE_DISCLOSURE,
        }
        return RUN.build_schedule(
            suite,
            seed=RUN.DEFAULT_SEED,
            timeout=60,
            candidate=candidate,
            controller=controller,
            executables=executables,
            runtime_closure=runtime_closure,
        )

    def resign(self, schedule):
        value = copy.deepcopy(schedule)
        value.pop("schedule_id", None)
        for job in value["jobs"]:
            job.pop("run_id", None)
        schedule_id = SCORE.sha256_bytes(SCORE.canonical_json_bytes(value))
        for job in value["jobs"]:
            job["run_id"] = SCORE.sha256_bytes(
                SCORE.RUN_ID_DOMAIN
                + schedule_id.encode("ascii")
                + SCORE.canonical_json_bytes(job)
            )
        value["schedule_id"] = schedule_id
        return value

    def test_failed_fresh_auth_preflight_leaves_no_artifact_roots(self):
        manifest, _, _ = self.make_public()
        runs_parent = self.root / "fresh-auth-runs"
        work_parent = self.root / "fresh-auth-work-parent"
        runs_parent.mkdir(mode=0o700)
        work_parent.mkdir(mode=0o700)
        output = runs_parent / "runs.jsonl"
        work = work_parent / "work"
        args = RUN.parser().parse_args(
            [
                "--manifest", str(manifest), "--output", str(output),
                "--work-dir", str(work), "--azdaja-skill", str(self.root / "candidate"),
                "--yes-run-inference",
            ]
        )
        with mock.patch.object(
            RUN, "fresh_source_preflight",
            side_effect=RUN.BenchError("injected invalid OAuth"),
        ):
            with self.assertRaisesRegex(RUN.BenchError, "invalid OAuth"):
                RUN.run_suite(args)
        self.assertFalse(work.exists())
        self.assertFalse(output.exists())
        self.assertFalse(Path(str(output) + ".schedule.json").exists())
        self.assertFalse(Path(str(output) + ".claims").exists())

    def test_azdaja_skill_is_fresh_only_and_optional_on_resume(self):
        parsed = RUN.parser().parse_args(
            [
                "--manifest", "/public/manifest.json", "--output", "/runs/runs.jsonl",
                "--work-dir", "/work", "--resume", "--yes-run-inference",
            ]
        )
        self.assertIsNone(parsed.azdaja_skill)
        parsed.resume = False
        with self.assertRaisesRegex(RUN.BenchError, "azdaja-skill"):
            RUN.fresh_source_preflight(parsed, self.root)

    def test_public_capture_uses_live_validator_and_has_no_gold_cli(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        self.assertEqual(len(suite.fixtures), 63)
        self.assertEqual(
            suite.manifest_sha256, hashlib.sha256(manifest.read_bytes()).hexdigest()
        )
        options = RUN.parser()._option_string_actions
        self.assertNotIn("--gold", options)
        self.assertNotIn("--gold-path", options)
        # The runner module never calls the scorer's gold-opening API.
        source = (HERE / "run.py").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"SCORE\s*\.\s*load_gold\s*\(")

    def test_payload_with_gold_or_answer_field_is_rejected_even_when_rehashed(self):
        for extra in ({"answer": "A"}, {"gold": "A"}):
            with self.subTest(extra=extra):
                manifest, _, _ = self.make_public(payload_extra=extra)
                with self.assertRaises(RUN.BenchError):
                    RUN.capture_public_suite(manifest)

    def test_public_gold_file_symlink_and_hardlink_are_rejected(self):
        # A collocated gold-shaped file violates the exact public inventory.
        manifest, public, _ = self.make_public()
        private_json(public / "gold.json", {"answer": "A"})
        with self.assertRaises(RUN.BenchError):
            RUN.capture_public_suite(manifest)

        # Payload symlinks are never followed.
        manifest, public, fixtures = self.make_public()
        payload = public / fixtures[0]["payload"]
        outside = self.root / "outside-payload.json"
        payload.rename(outside)
        payload.symlink_to(outside)
        with self.assertRaises(RUN.BenchError):
            RUN.capture_public_suite(manifest)

        # A hash-matching hard link is still rejected by the live fd validator.
        manifest, public, fixtures = self.make_public()
        payload = public / fixtures[0]["payload"]
        os.link(payload, self.root / "second-hard-link.json")
        with self.assertRaises(RUN.BenchError):
            RUN.capture_public_suite(manifest)

    def test_schedule_is_exact_live_scorer_contract_and_recomputed_tamper_fails(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        jobs, arms = SCORE.validate_schedule(
            copy.deepcopy(schedule),
            manifest,
            suite.fixtures_by_id,
            manifest_sha256=suite.manifest_sha256,
        )
        self.assertEqual(len(jobs), 189)
        self.assertEqual(arms, SCORE.ARMS)
        self.assertEqual({job["repetition"] for job in jobs}, {1})

        tampered = copy.deepcopy(schedule)
        tampered["jobs"][0], tampered["jobs"][3] = (
            tampered["jobs"][3], tampered["jobs"][0]
        )
        for index, job in enumerate(tampered["jobs"], 1):
            job["ordinal"] = index
        tampered = self.resign(tampered)
        with self.assertRaises(SCORE.ScoreError):
            SCORE.validate_schedule(
                tampered,
                manifest,
                suite.fixtures_by_id,
                manifest_sha256=suite.manifest_sha256,
            )

    def test_resume_accepts_only_canonical_immutable_prefix_and_exact_2n_claims(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        runs = self.root / "runs"
        runs.mkdir(mode=0o700)
        output = runs / "runs.jsonl"
        claims_root = Path(str(output) + ".claims")
        claims_root.mkdir(mode=0o700)
        claims = claims_root / schedule["schedule_id"]
        claims.mkdir(mode=0o700)
        rows = []
        for job in schedule["jobs"][:3]:
            artifacts = {
                name: {
                    "path": f"/private/artifacts/{job['run_id']}/{basename}",
                    "sha256": hashlib.sha256(f"{job['run_id']} {name}".encode()).hexdigest(),
                    "bytes": 0, "mode": "0600",
                    "contains_private_raw_trajectory": False,
                    "credential_redacted": True,
                    "sensitivity": "synthetic redacted trajectory",
                }
                for name, basename in {
                    "stdout": "stdout.ndjson", "stderr": "stderr.log"
                }.items()
            }
            row = RUN.controller_failure_row(
                job, schedule, "synthetic terminal failure", artifacts
            )
            rows.append(row)
            RUN.atomic_create_private_json(
                claims / (job["run_id"] + ".json"),
                {
                    "schedule_id": schedule["schedule_id"],
                    "run_id": job["run_id"],
                    "ordinal": job["ordinal"],
                    "pid": os.getpid(),
                },
            )
            RUN.atomic_create_private_json(
                claims / (job["run_id"] + ".done.json"),
                {
                    "schedule_id": schedule["schedule_id"],
                    "run_id": job["run_id"],
                    "row_sha256": SCORE.sha256_bytes(
                        SCORE.canonical_json_bytes(row)
                    ),
                },
            )
        output.write_bytes(b"".join(SCORE.canonical_json_file_bytes(row) for row in rows))
        output.chmod(0o600)
        captured_rows, output_state = RUN.validate_result_prefix(
            output, schedule, suite, claims
        )
        self.assertEqual(captured_rows, rows)
        self.assertEqual(output_state, (
            output.stat().st_dev, output.stat().st_ino, output.stat().st_size,
            hashlib.sha256(output.read_bytes()).hexdigest(),
        ))

        # A crash-orphaned next claim makes whether inference occurred ambiguous.
        following = schedule["jobs"][3]
        RUN.atomic_create_private_json(
            claims / (following["run_id"] + ".json"),
            {
                "schedule_id": schedule["schedule_id"],
                "run_id": following["run_id"],
                "ordinal": following["ordinal"],
                "pid": os.getpid(),
            },
        )
        with self.assertRaises(RUN.BenchError):
            RUN.validate_result_prefix(output, schedule, suite, claims)

    def test_prefix_rejects_hardlink_symlink_and_byte_tamper(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        runs = self.root / "runs"
        runs.mkdir(mode=0o700)
        output = runs / "runs.jsonl"
        claims_root = Path(str(output) + ".claims")
        claims_root.mkdir(mode=0o700)
        claims = claims_root / schedule["schedule_id"]
        claims.mkdir(mode=0o700)
        # Empty prefixes are valid and have exactly zero receipts.
        self.assertEqual(
            RUN.validate_result_prefix(output, schedule, suite, claims), ([], None)
        )
        output.write_bytes(b"{}\n")
        output.chmod(0o600)
        with self.assertRaises(RUN.BenchError):
            RUN.validate_result_prefix(output, schedule, suite, claims)
        output.unlink()
        target = self.root / "outside.jsonl"
        private_bytes(target, b"{}\n")
        output.symlink_to(target)
        with self.assertRaises(RUN.BenchError):
            RUN.validate_result_prefix(output, schedule, suite, claims)
        output.unlink()
        private_bytes(output, b"{}\n")
        os.link(output, self.root / "output-hardlink")
        with self.assertRaises(RUN.BenchError):
            RUN.validate_result_prefix(output, schedule, suite, claims)

    def test_output_state_refuses_post_validation_insertion_and_mutation(self):
        output_parent = self.root / "output-state"
        output_parent.mkdir(mode=0o700)
        row = {"record_type": "synthetic-output-state"}

        # Positive first append: validated absence is authority only for an
        # atomic O_CREAT|O_EXCL creation, and returns the new exact token.
        first = output_parent / "first.jsonl"
        data, state = RUN._capture_private_file(
            first, "test output", allow_missing=True
        )
        self.assertIsNone(data)
        self.assertIsNone(state)
        state = RUN._append_private_jsonl(first, row, expected_state=state)
        self.assertEqual(first.read_bytes(), SCORE.canonical_json_file_bytes(row))
        self.assertEqual(
            state, (
                first.stat().st_dev, first.stat().st_ino, first.stat().st_size,
                hashlib.sha256(first.read_bytes()).hexdigest(),
            )
        )

        # A clean owner-only regular file inserted after absence validation must
        # not be silently adopted by O_APPEND|O_CREAT.
        inserted = output_parent / "inserted.jsonl"
        _, absent = RUN._capture_private_file(
            inserted, "test output", allow_missing=True
        )
        private_bytes(inserted, b"")
        with self.assertRaises(RUN.BenchError):
            RUN._append_private_jsonl(inserted, row, expected_state=absent)

        # A same-size regular replacement has different dev/inode authority.
        replaced = output_parent / "replaced.jsonl"
        private_bytes(replaced, b"old")
        _, replaced_state = RUN._capture_private_file(
            replaced, "test output", allow_missing=False
        )
        replacement = output_parent / "replacement.tmp"
        private_bytes(replacement, b"new")
        os.replace(replacement, replaced)
        self.assertEqual(replaced.stat().st_size, replaced_state[2])
        with self.assertRaises(RUN.BenchError):
            RUN._append_private_jsonl(replaced, row, expected_state=replaced_state)

        # Same inode with a mutated size is also outside the captured prefix.
        resized = output_parent / "resized.jsonl"
        private_bytes(resized, b"old")
        _, resized_state = RUN._capture_private_file(
            resized, "test output", allow_missing=False
        )
        with resized.open("ab") as handle:
            handle.write(b"!")
        with self.assertRaises(RUN.BenchError):
            RUN._append_private_jsonl(resized, row, expected_state=resized_state)

        # Same inode and same size but different prefix bytes is detected by the
        # cryptographic byte state, not only metadata.
        overwritten = output_parent / "overwritten.jsonl"
        private_bytes(overwritten, b"old")
        _, overwritten_state = RUN._capture_private_file(
            overwritten, "test output", allow_missing=False
        )
        with overwritten.open("r+b") as handle:
            handle.write(b"new")
            handle.flush()
            os.fsync(handle.fileno())
        self.assertEqual(
            (overwritten.stat().st_dev, overwritten.stat().st_ino, overwritten.stat().st_size),
            overwritten_state[:3],
        )
        with self.assertRaises(RUN.BenchError):
            RUN._append_private_jsonl(overwritten, row, expected_state=overwritten_state)

        # Path replacement with a symlink is refused by O_NOFOLLOW.
        symlinked = output_parent / "symlinked.jsonl"
        private_bytes(symlinked, b"old")
        _, symlink_state = RUN._capture_private_file(
            symlinked, "test output", allow_missing=False
        )
        target = output_parent / "symlink-target.jsonl"
        private_bytes(target, b"old")
        symlinked.unlink()
        symlinked.symlink_to(target)
        with self.assertRaises(RUN.BenchError):
            RUN._append_private_jsonl(symlinked, row, expected_state=symlink_state)

        # Adding a second hard link after capture invalidates single-link state.
        linked = output_parent / "linked.jsonl"
        private_bytes(linked, b"old")
        _, linked_state = RUN._capture_private_file(
            linked, "test output", allow_missing=False
        )
        os.link(linked, output_parent / "linked-alias.jsonl")
        with self.assertRaises(RUN.BenchError):
            RUN._append_private_jsonl(linked, row, expected_state=linked_state)

    def test_atomic_json_partial_write_never_publishes_final(self):
        parent = self.root / "atomic-json"
        parent.mkdir(mode=0o700)
        target = parent / "done.json"
        real_write = os.write
        calls = 0

        def fail_after_half(fd, data):
            nonlocal calls
            calls += 1
            if calls == 1:
                chunk = bytes(data)
                return real_write(fd, chunk[: max(1, len(chunk) // 2)])
            raise OSError("injected write failure")

        with mock.patch.object(RUN.os, "write", side_effect=fail_after_half):
            with self.assertRaises(OSError):
                RUN.atomic_create_private_json(target, {"terminal": True})
        self.assertFalse(target.exists())
        self.assertEqual(os.listdir(parent), [])
        RUN.atomic_create_private_json(target, {"terminal": True})
        self.assertEqual(
            target.read_bytes(), SCORE.canonical_json_file_bytes({"terminal": True})
        )

    def test_held_ceremony_detects_claims_and_runs_root_swaps(self):
        runs_parent = self.root / "runs-parent"
        claims_root = self.root / "claims-root"
        work_runs = self.root / "work" / "runs"
        for directory in (runs_parent, claims_root, work_runs.parent):
            directory.mkdir(mode=0o700)
        work_runs.mkdir(mode=0o700)
        active = claims_root / ("a" * 64)
        active.mkdir(mode=0o700)
        output = runs_parent / "runs.jsonl"
        handles = RUN.open_ceremony_handles(
            output=output, claims_root=claims_root, claims=active,
            work_runs=work_runs, allow_existing_output=False,
        )
        try:
            RUN.atomic_create_private_json_at(
                handles.claims_fd, "claim.json", {"claimed": True}
            )
            moved = claims_root / "moved-active"
            active.rename(moved)
            active.mkdir(mode=0o700)
            with self.assertRaises(RUN.BenchError):
                RUN.recheck_ceremony_handles(handles)
            self.assertTrue((moved / "claim.json").is_file())
            self.assertEqual(os.listdir(active), [])
            active.rmdir()
            moved.rename(active)
            RUN.recheck_ceremony_handles(handles)

            # Swapping the entire runs parent cannot redirect the reserved FD.
            runs_parent_held = self.root / "runs-parent-held"
            runs_parent.rename(runs_parent_held)
            runs_parent.mkdir(mode=0o700)
            with self.assertRaises(RUN.BenchError):
                RUN.recheck_ceremony_handles(handles)
            self.assertTrue((runs_parent_held / "runs.jsonl").is_file())
            self.assertFalse((runs_parent / "runs.jsonl").exists())
        finally:
            handles.close()

    def test_runtime_closure_tamper_breaks_attestation_binding(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        attestation = {
            "controller": copy.deepcopy(schedule["configuration"]["controller"]),
            "candidate": copy.deepcopy(schedule["configuration"]["candidate"]),
            "executables": copy.deepcopy(schedule["configuration"]["executables"]),
            "runtime_closure": copy.deepcopy(schedule["configuration"]["runtime_closure"]),
        }
        paths = RUN.FrozenPaths(
            root=Path("/frozen"), controller=Path("/frozen/run.py"),
            validator=Path("/frozen/score.py"), adapter=Path("/frozen/adapter.py"),
            candidate=Path("/frozen/candidate"), jcode=Path("/frozen/jcode"),
            node=Path("/frozen/node"), kernel_environment=Path("/frozen/kernel"),
            runtime_python=Path("/frozen/runtime-python"),
            prime_package=Path("/frozen/prime-package"),
            prime_agent=Path("/frozen/prime-agent"), public=Path("/frozen/public"),
            attestation=Path("/frozen/attestation.json"),
        )
        tampered = copy.deepcopy(schedule)
        tampered["configuration"]["runtime_closure"]["adapter"]["sha256"] = "0" * 64
        with self.assertRaises(RUN.BenchError):
            RUN._assert_schedule_matches_attestation(tampered, attestation, paths)
        tampered = copy.deepcopy(schedule)
        tampered["configuration"]["runtime_closure"]["prime_package"]["entry_count"] += 1
        with self.assertRaises(RUN.BenchError):
            RUN._assert_schedule_matches_attestation(tampered, attestation, paths)

    def artifact_receipt(self, path: Path):
        data = path.read_bytes()
        return {
            "path": str(path),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "mode": "0600",
            "contains_private_raw_trajectory": False,
            "credential_redacted": True,
            "sensitivity": "redacted retained trace",
        }

    def test_mandatory_artifacts_and_exact_run_directory_inventory(self):
        run_dir = self.root / "run-artifacts"
        run_dir.mkdir(mode=0o700)
        names = {
            "stdout.ndjson": "stdout",
            "stderr.log": "stderr",
            "azdaja-model-usage.jsonl": "azdaja_model_trace",
            "azdaja-solo-trace.log": "azdaja_solo_trace",
        }
        for name in names:
            private_bytes(run_dir / name, f"retained {name}\n".encode())
        row = {
            "trajectory_artifacts": {
                key: self.artifact_receipt(run_dir / name)
                for name, key in names.items()
            },
            "credential_cleanup_assertion": {
                "asserted": True,
                "credential_homes_deleted": True,
                "retained_entries": sorted(names),
                "retention_allowlist": sorted(names),
            },
        }
        RUN.audit_run_artifacts(row, run_dir, "jcode-azdaja")
        private_bytes(run_dir / "unexpected", b"x")
        with self.assertRaises(RUN.BenchError):
            RUN.audit_run_artifacts(row, run_dir, "jcode-azdaja")
        (run_dir / "unexpected").unlink()
        trace = run_dir / "azdaja-solo-trace.log"
        trace.unlink()
        trace.symlink_to(run_dir / "stderr.log")
        with self.assertRaises(RUN.BenchError):
            RUN.audit_run_artifacts(row, run_dir, "jcode-azdaja")

    def test_post_turn_audit_failure_preserves_billed_evidence_and_raises(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        job = schedule["jobs"][0]
        work = self.root / "post-turn-work"
        (work / "runs").mkdir(mode=0o700, parents=True)
        run_dir = RUN._run_directory(work, job)

        class Adapter:
            def run_one(self, **kwargs):
                run_dir.mkdir(mode=0o700)
                private_bytes(run_dir / "stdout.ndjson", b"billed evidence\n")
                private_bytes(run_dir / "stderr.log", b"post-turn stderr\n")
                return {"execution_success": True}

        args = argparse.Namespace(work_dir=str(work))
        paths = mock.Mock(public=self.root / "unused", candidate=self.root / "candidate")
        with (
            mock.patch.object(RUN, "_make_adapter_fixture", return_value=object()),
            mock.patch.object(RUN, "verify_snapshots", return_value=None),
            mock.patch.object(
                RUN, "audit_run_artifacts",
                side_effect=RUN.BenchError("injected post-turn audit failure"),
            ),
        ):
            with self.assertRaises(RUN.BenchError):
                RUN._execute_job(
                    Adapter(), job, schedule, suite, paths, {}, args,
                    self.root, {}, {},
                )
        self.assertEqual(
            set(os.listdir(run_dir)), {"stdout.ndjson", "stderr.log"}
        )
        self.assertEqual(
            (run_dir / "stdout.ndjson").read_bytes(), b"billed evidence\n"
        )

    def test_controller_failure_artifacts_exist_before_scorer_valid_row(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        job = schedule["jobs"][0]
        work = self.root / "controller-failure-work"
        (work / "runs").mkdir(mode=0o700, parents=True)
        adapter = RUN._load_python(
            "lb2_test_controller_failure_adapter", RUN.OOLONG_SOURCE
        )
        run_dir = RUN._run_directory(work, job)
        artifacts = RUN.materialize_controller_failure_artifacts(
            adapter, run_dir, "injected controller failure"
        )
        row = RUN.controller_failure_row(
            job, schedule, "injected controller failure", artifacts
        )
        RUN._verify_row_live(row, job, schedule, suite)
        RUN.validate_retained_prefix_artifacts(work, schedule, [row])
        self.assertEqual(set(os.listdir(run_dir)), {"stdout.ndjson", "stderr.log"})

    def test_resume_rehashes_trajectory_artifacts_against_row(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        job = schedule["jobs"][0]
        work = self.root / "artifact-resume-work"
        runs = work / "runs"
        runs.mkdir(mode=0o700, parents=True)
        run_dir = RUN._run_directory(work, job)
        run_dir.mkdir(mode=0o700)
        for name, data in (("stdout.ndjson", b""), ("stderr.log", b"old!")):
            private_bytes(run_dir / name, data)
        artifacts = {
            key: self.artifact_receipt(run_dir / name)
            for name, key in {
                "stdout.ndjson": "stdout", "stderr.log": "stderr"
            }.items()
        }
        row = RUN.controller_failure_row(job, schedule, "synthetic", artifacts)
        RUN.validate_retained_prefix_artifacts(work, schedule, [row])
        private_bytes(run_dir / "stderr.log", b"evil")  # same byte length
        with self.assertRaises(RUN.BenchError):
            RUN.validate_retained_prefix_artifacts(work, schedule, [row])

    def test_candidate_snapshot_inventory_is_an_exact_allowlist(self):
        candidate = self.root / "candidate"
        candidate.mkdir(mode=0o700)
        for name in RUN.CANDIDATE_ALLOWLIST:
            private_bytes(candidate / name, name.encode())
        (candidate / "azdaja").chmod(0o700)
        identity = RUN.candidate_identity(candidate)
        SCORE._validate_candidate_identity(identity)
        private_bytes(candidate / "unbound-helper", b"malicious")
        with self.assertRaises(RUN.BenchError):
            RUN.candidate_identity(candidate)

    def test_public_runs_work_roots_must_be_owner_only_separate_and_nonnested(self):
        manifest, public, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        runs = self.root / "runs"
        runs.mkdir(mode=0o700)
        nested_work = runs / "work"
        with self.assertRaises(RUN.BenchError):
            RUN._prepare_roots(
                suite, runs / "runs.jsonl", nested_work, resume=False
            )
        insecure = self.root / "insecure"
        insecure.mkdir(mode=0o755)
        os.chmod(insecure, 0o755)  # independent of the invoking process umask
        with self.assertRaises(RUN.BenchError):
            RUN._prepare_roots(
                suite, insecure / "runs.jsonl", self.root / "fresh-work", resume=False
            )
        self.assertIn("not asserted", RUN.CONTAINMENT_DISCLOSURE)
        self.assertIn("joinable", RUN.CONTAINMENT_DISCLOSURE)

    def test_actual_full_prime_snapshot_runs_frozen_version_when_available(self):
        required = {name: shutil.which(name) for name in ("prime-agent", "jcode", "node")}
        kernel = Path.home() / ".prime" / "agent" / "kernel-venv"
        if any(value is None for value in required.values()) or not (kernel / "bin" / "python").exists():
            self.skipTest("Prime/Jcode/Node/kernel runtime closure is unavailable")
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        candidate = self.root / "candidate-source"
        candidate.mkdir(mode=0o700)
        installed = Path.home() / ".jcode" / "skills" / "azdaja"
        if not all((installed / name).is_file() for name in RUN.CANDIDATE_ALLOWLIST):
            self.skipTest("installed candidate components are unavailable")
        for name in RUN.CANDIDATE_ALLOWLIST:
            shutil.copy2(installed / name, candidate / name)
        work = self.root / "actual-snapshot-work"
        work.mkdir(mode=0o700)
        paths, attestation = RUN.create_snapshots(
            work,
            suite,
            candidate_source=candidate,
            jcode_source=RUN._resolve_executable(required["jcode"], "jcode"),
            node_source=RUN._resolve_executable(required["node"], "Node"),
            prime_source=RUN._resolve_executable(required["prime-agent"], "Prime"),
            kernel_environment=kernel,
        )
        self.assertGreater(attestation["prime_package"]["entry_count"], 1)
        self.assertIn(
            "package.json",
            {item["path"] for item in attestation["prime_package"]["entries"]},
        )
        RUN.smoke_frozen_versions(paths, attestation)
        RUN.verify_snapshots(paths, attestation, suite, full_prime=True)

        # Exercise the default schedule's first Prime attempt through real
        # staging, retention, raw-response transform, and the live score
        # validator. Only the network/process execute boundary is mocked.
        schedule = RUN.build_schedule(
            suite, seed=RUN.DEFAULT_SEED, timeout=60,
            candidate=attestation["candidate"], controller=attestation["controller"],
            executables=attestation["executables"],
            runtime_closure=attestation["runtime_closure"],
        )
        job = next(item for item in schedule["jobs"] if item["arm"] == "prime-agent")
        source_home = self.root / "source-home"
        auth_path = source_home / ".prime" / "agent" / "auth.json"
        auth_path.parent.mkdir(mode=0o700, parents=True)
        private_json(
            auth_path,
            {"openai-codex": {"type": "oauth", "access": "not-read", "expires": 9_999_999_999_999}},
        )
        (work / "runs").mkdir(mode=0o700)
        adapter = RUN._load_frozen_adapter(
            paths, kernel_environment=paths.kernel_environment
        )
        text = "The correct answer is (A)\n"
        event = {
            "type": "message_end",
            "message": {
                "role": "assistant", "provider": "openai-codex",
                "model": SCORE.MODEL, "api": "openai-codex-responses",
                "content": [{"type": "text", "text": text}],
                "usage": {
                    "input": 100, "output": 10, "cacheRead": 3,
                    "cacheWrite": 2, "totalTokens": 115,
                },
            },
        }
        stdout = json.dumps(event, separators=(",", ":")) + "\n"
        args = argparse.Namespace(
            timeout=60, seed=RUN.DEFAULT_SEED, jcode=str(paths.jcode),
            prime_agent=str(paths.prime_agent), work_dir=str(work),
            executable_identities=schedule["configuration"]["executables"],
        )
        auth_prime = {
            "asserted": True, "method": "subscription-oauth",
            "issuer": "https://auth.openai.com", "audience": "https://api.openai.com/v1",
            "plan_present_and_paid": True, "account_id_present": True,
            "expires_at_ms": 9_999_999_999_999,
            "credential_source": "~/.prime/agent/auth.json:openai-codex",
            "provider_cli": "openai-codex", "model_cli": SCORE.MODEL,
            "credential_type_asserted": "oauth",
        }
        with mock.patch.object(
            adapter, "execute", return_value=(0, stdout, "", False, 0.1)
        ):
            row = RUN._execute_job(
                adapter, job, schedule, suite, paths, attestation, args,
                source_home, {}, auth_prime,
            )
        self.assertTrue(row["execution_success"])
        self.assertEqual(row["response"], text)
        self.assertNotEqual(row["response"], row["response"].strip())
        RUN._verify_row_live(row, job, schedule, suite)
        artifact_schedule = copy.deepcopy(schedule)
        artifact_schedule["jobs"] = [job]
        RUN.validate_retained_prefix_artifacts(work, artifact_schedule, [row])



if __name__ == "__main__":
    unittest.main()
