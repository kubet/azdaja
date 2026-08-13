#!/usr/bin/env python3
"""Security/contract tests for the no-gold LongBench-v2 runner."""

from __future__ import annotations

import argparse
import copy
import errno
import hashlib
import importlib.util
import inspect
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


def synthetic_root_transcript(request: str) -> bytes:
    request_id = json.dumps("synthetic-request")
    model = json.dumps(SCORE.MODEL)
    return (
        f"\n=== root request begin request_id={request_id} model={model} "
        f"request_chars={len(request)} ===\n{request}"
        f"\n=== root request end request_id={request_id} ===\n"
        f"=== turn 0 request_id={request_id} attempt=1 session_id=\"session\" "
        f"category=turn outcome=succeeded degraded_transport=false "
        f"failed_attempts_before_success=0 provider=\"openai\" model={model} "
        f"input=1 output=1 cache_read=0 latency_ms=1 ===\nreply\n"
    ).encode("utf-8")


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
                "sha256": ("2" * 64 if name == "azdaja" else digit * 64),
                "bytes": (2 if name == "azdaja" else 11),
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
        digest = hashlib.sha256(data).hexdigest()
        return {
            "path": str(path),
            "sha256": digest,
            "bytes": len(data),
            "mode": "0600",
            "contains_private_raw_trajectory": False,
            "credential_redacted": True,
            "sensitivity": "redacted retained trace",
            **(
                {"source_sha256_before_redaction": digest, "exact_text_preserved": True}
                if path.name in {"azdaja-model-usage.jsonl", "azdaja-solo-trace.log"}
                else {}
            ),
        }

    def load_binding_adapter(self, original_arm_for, *, original_cleanup_run=None):
        source_adapter = RUN._load_python(
            "lb2_binding_source_" + os.urandom(4).hex(), RUN.OOLONG_SOURCE
        )
        # These unit tests replace the loaded frozen module with a deterministic
        # adapter double.  Pin its contract to LongBench rather than inheriting
        # unrelated in-progress OOLONG campaign arm ordering from the worktree.
        source_adapter.ARMS = RUN.ARMS
        source = RUN.OOLONG_SOURCE.read_bytes()
        frozen_root = self.root / ("binding-frozen-" + os.urandom(4).hex())
        frozen_root.mkdir(mode=0o700)
        frozen_adapter = frozen_root / "oolong-run.py"
        frozen_adapter.write_bytes(source)
        frozen_adapter.chmod(0o700)
        paths = mock.Mock(
            adapter=frozen_adapter,
            node=self.root / "bin" / "node",
            jcode=self.root / "bin" / "jcode",
        )
        source_adapter.arm_for = original_arm_for
        if original_cleanup_run is not None:
            source_adapter.cleanup_run = original_cleanup_run
        source_adapter.arm_for.__signature__ = inspect.signature(
            RUN._load_python(
                "lb2_binding_signature_" + os.urandom(4).hex(),
                RUN.OOLONG_SOURCE,
            ).arm_for
        )
        # Patch the loader result so the production wrapper is exercised around
        # a deterministic arm implementation without subprocesses.
        prior = RUN._ADAPTER
        try:
            with mock.patch.object(RUN, "_load_python", return_value=source_adapter):
                adapter = RUN._load_frozen_adapter(
                    paths, kernel_environment=self.root / "kernel"
                )
        finally:
            RUN._ADAPTER = prior
        return adapter

    @staticmethod
    def binding_arm_kwargs(run_dir: Path):
        return {
            "prompt": "prompt", "args": argparse.Namespace(),
            "root": run_dir / "task", "fixture": object(),
            "run_dir": run_dir, "auth_jcode": {}, "auth_prime": {},
            "source_home": run_dir / "source", "skill": run_dir / "skill",
        }

    def test_frozen_prime_tool_policy_scans_argument_leaves_without_json_escape_tokens(self):
        def unused_arm_for(name, **kwargs):
            del name, kwargs
            raise AssertionError("arm creation is not used")

        adapter = self.load_binding_adapter(unused_arm_for)
        task_dir = self.root / "tool-policy-task"
        task_dir.mkdir(mode=0o700)
        context_path = task_dir / "payload.json"
        private_bytes(context_path, b"{}\n")

        safe_code = "%%bash\npwd\nls -l\ncat file"
        safe_stdout = json.dumps(
            {
                "type": "tool_execution_start",
                "toolName": "bash",
                "args": {"code": safe_code},
            },
            separators=(",", ":"),
        ) + "\n"
        self.assertEqual(
            adapter._tool_invocations("prime-agent", safe_stdout),
            [("bash", safe_code)],
        )
        # Serializing structured args would turn the final ``\ncat`` escape into
        # the apparent command token ``ncat``. The loaded adapter must scan the
        # actual string value instead, including when it is nested more deeply.
        self.assertIsNotNone(
            adapter.NETWORK_ACCESS.search(json.dumps({"code": safe_code}))
        )
        self.assertIsNone(adapter.NETWORK_ACCESS.search(safe_code))
        safe_receipt = adapter.scan_tool_policy(
            "prime-agent", safe_stdout,
            task_dir=task_dir, context_path=context_path,
        )
        self.assertTrue(safe_receipt["asserted"])
        self.assertEqual(safe_receipt["events_scanned"], 1)
        self.assertEqual(safe_receipt["violations"], [])

        nested_args = {
            "metadata": {"attempt": 1, "enabled": True},
            "payload": [{"ignored": None}, {"code": safe_code}],
        }
        nested_stdout = json.dumps(
            {
                "type": "tool_execution_start",
                "toolName": "bash",
                "args": nested_args,
            },
            separators=(",", ":"),
        ) + "\n"
        self.assertEqual(
            adapter._tool_invocations("prime-agent", nested_stdout),
            [("bash", safe_code)],
        )
        nested_receipt = adapter.scan_tool_policy(
            "prime-agent", nested_stdout,
            task_dir=task_dir, context_path=context_path,
        )
        self.assertTrue(nested_receipt["asserted"])
        self.assertEqual(nested_receipt["events_scanned"], 1)
        self.assertEqual(nested_receipt["violations"], [])

        # Jcode streams a JSON-encoded argument object through delta events. Decode
        # the completed stream before scanning so JSON ``\ncat`` cannot become
        # the synthetic token ``ncat``.
        jcode_arguments = json.dumps(
            {"command": safe_code, "intent": "inspect local fixture"},
            separators=(",", ":"),
        )
        split = len(jcode_arguments) // 2
        jcode_stdout = "\n".join(
            json.dumps(event, separators=(",", ":"))
            for event in (
                {"type": "tool_start", "name": "bash"},
                {"type": "tool_input", "delta": jcode_arguments[:split]},
                {"type": "tool_input", "delta": jcode_arguments[split:]},
                {"type": "tool_exec", "name": "bash"},
            )
        ) + "\n"
        jcode_invocations = adapter._tool_invocations("jcode-native", jcode_stdout)
        self.assertEqual(len(jcode_invocations), 1)
        self.assertIn(safe_code, jcode_invocations[0][1].split("\0"))
        jcode_receipt = adapter.scan_tool_policy(
            "jcode-native", jcode_stdout,
            task_dir=task_dir, context_path=context_path,
        )
        self.assertTrue(jcode_receipt["asserted"])

        malformed_stdout = "\n".join(
            json.dumps(event, separators=(",", ":"))
            for event in (
                {"type": "tool_start", "name": "bash"},
                {
                    "type": "tool_input",
                    "delta": r'{"command":"\u0063url https://example.test"',
                },
                {"type": "tool_exec", "name": "bash"},
            )
        ) + "\n"
        malformed_receipt = adapter.scan_tool_policy(
            "jcode-native", malformed_stdout,
            task_dir=task_dir, context_path=context_path,
        )
        self.assertFalse(malformed_receipt["asserted"])
        self.assertIn(
            "malformed tool arguments",
            {item["category"] for item in malformed_receipt["violations"]},
        )

        # All aliases are inspected and a nonmatching boundary prevents distinct
        # leaves from manufacturing ``git\s+clone``.
        aliases_stdout = json.dumps(
            {
                "type": "tool_execution_start",
                "toolName": "bash",
                "args": {"left": "git", "right": "clone"},
                "arguments": {"command": "curl https://example.test"},
            },
            separators=(",", ":"),
        ) + "\n"
        aliases = adapter._tool_invocations("prime-agent", aliases_stdout)
        self.assertNotRegex(aliases[0][1], r"git\s+clone")
        alias_receipt = adapter.scan_tool_policy(
            "prime-agent", aliases_stdout,
            task_dir=task_dir, context_path=context_path,
        )
        self.assertFalse(alias_receipt["asserted"])
        self.assertIn(
            "network access",
            {item["category"] for item in alias_receipt["violations"]},
        )

        network_code = (
            "%%bash\nncat host",
            "%%bash\ncurl https://example.test/data",
            "import urllib.request\nurllib.request.urlopen('https://example.test')",
        )
        for code in network_code:
            with self.subTest(code=code):
                stdout = json.dumps(
                    {
                        "type": "tool_execution_start",
                        "toolName": "bash",
                        "args": {"code": code},
                    },
                    separators=(",", ":"),
                ) + "\n"
                receipt = adapter.scan_tool_policy(
                    "prime-agent", stdout,
                    task_dir=task_dir, context_path=context_path,
                )
                self.assertFalse(receipt["asserted"])
                self.assertEqual(receipt["events_scanned"], 1)
                self.assertIn(
                    "network access",
                    {item["category"] for item in receipt["violations"]},
                )

    def test_transport_error_then_success_is_route_failure_accepted_by_live_scorer(self):
        manifest, public, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        job = next(item for item in schedule["jobs"] if item["arm"] == "jcode-azdaja")
        state: dict[str, Path] = {}

        def treatment_arm_for(name, **kwargs):
            self.assertEqual(name, "jcode-azdaja")
            run_dir = Path(kwargs["run_dir"])
            (run_dir / "home").mkdir(mode=0o700)
            state["model_trace"] = run_dir / "azdaja-model-usage.jsonl"
            state["solo_trace"] = run_dir / "azdaja-solo-trace.log"
            arm = mock.Mock()
            arm.command = ["azdaja", "--solo", "prompt"]
            arm.auth_assertion = {"asserted": True}
            arm.activation_mode = "direct_solo_product"
            arm.skill_instructions_sha256 = None
            arm.staged_skill = None
            return arm, {}, {
                "azdaja_model_trace": state["model_trace"],
                "azdaja_solo_trace": state["solo_trace"],
            }

        def no_cleanup(arm_name, args, env, run_dir):
            del arm_name, args, env, run_dir
            return []

        adapter = self.load_binding_adapter(
            treatment_arm_for, original_cleanup_run=no_cleanup
        )
        fixture = RUN._make_adapter_fixture(
            adapter,
            next(item for item in suite.fixtures if item.fixture_id == job["fixture_id"]),
            public,
        )
        answer = "The correct answer is (A)"
        stdout = json.dumps(
            {"type": "result", "response": answer}, separators=(",", ":")
        ) + "\n"
        trace_rows = [
            {
                "timestamp_ms": 1,
                "depth": 0,
                "error": "provider_call_failed",
                "stage": "turn",
                "detail": "TimeoutError: deterministic injected timeout",
            },
            {
                "timestamp_ms": 2,
                "depth": 0,
                "provider": "openai",
                "model": RUN.MODEL,
                "input_tokens": 11,
                "output_tokens": 3,
                "cache_read_tokens": 2,
                "cache_write_tokens": 0,
                "latency_ms": 7,
            },
        ]

        def successful_retry_execute(*_args):
            private_bytes(
                state["model_trace"],
                b"".join(
                    (json.dumps(row, separators=(",", ":")) + "\n").encode()
                    for row in trace_rows
                ),
            )
            private_bytes(state["solo_trace"], synthetic_root_transcript("safe root request"))
            return 0, stdout, "", False, 0.25

        work_root = self.root / "transport-incident-runs"
        args = argparse.Namespace(
            timeout=60,
            seed=RUN.DEFAULT_SEED,
            jcode="jcode",
            executable_identities=schedule["configuration"]["executables"],
        )
        with mock.patch.object(
            adapter, "execute", side_effect=successful_retry_execute
        ):
            adapter_row = adapter.run_one(
                arm_name="jcode-azdaja",
                repetition=1,
                ordinal=job["ordinal"],
                fixture=fixture,
                prompt=None,
                args=args,
                root=self.root,
                source_home=self.root / "source-home",
                skill=self.root / "candidate",
                auth_jcode={},
                auth_prime={},
                work_root=work_root,
                defer_scoring=True,
            )

        route = adapter_row["runtime_route_assertion"]
        self.assertFalse(route["asserted"])
        self.assertEqual(route["transport_error_rows"], 1)
        self.assertEqual(
            route["routes"], [{"provider": "openai", "model": RUN.MODEL}]
        )
        self.assertFalse(adapter_row["execution_success"])
        self.assertEqual(adapter_row["failure"]["kind"], "route_assertion")
        self.assertIsNone(adapter_row["azdaja_model_usage"])
        self.assertFalse(adapter_row["efficiency_evidence"]["valid"])
        self.assertIsNone(adapter_row["usage"]["total_tokens"])

        run_dir = work_root / f"r001-{job['ordinal']:03d}-jcode-azdaja"
        retained_trace = (run_dir / "azdaja-model-usage.jsonl").read_text()
        self.assertIn("provider_call_failed", retained_trace)
        self.assertIn("deterministic injected timeout", retained_trace)
        raw_response = RUN.extract_final_raw(
            adapter, "jcode-azdaja", (run_dir / "stdout.ndjson").read_text()
        )
        row = RUN.transform_adapter_row(
            adapter_row,
            job,
            schedule,
            raw_response=raw_response,
            trajectory_artifacts=adapter_row["trajectory_artifacts"],
            stdout_bytes=(run_dir / "stdout.ndjson").read_bytes(),
            root_trace_bytes=(run_dir / "azdaja-solo-trace.log").read_bytes(),
            public_context="Context 0.",
        )
        # This exercises the scorer's full terminal-row contract: a detailed false
        # route is an accepted execution failure, never a degraded success.
        RUN._verify_row_live(row, job, schedule, suite)
        self.assertFalse(row["execution_success"])
        self.assertEqual(row["failure"]["kind"], "route_assertion")

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

    def test_bound_purge_rejects_arm_time_rename_escape_and_closes_fd(self):
        run_dir = self.root / "bound-rename-run"
        run_dir.mkdir(mode=0o700)
        escaped = self.root / "escaped-bound-home"

        def original_arm_for(name, **kwargs):
            self.assertEqual(name, "jcode-native")
            home = Path(kwargs["run_dir"]) / "home"
            home.mkdir(mode=0o700)
            private_bytes(home / "oauth-secret", b"escaped credential bytes")
            return mock.Mock(command=["jcode"]), {}, {}

        adapter = self.load_binding_adapter(original_arm_for)
        adapter.arm_for(
            "jcode-native", **self.binding_arm_kwargs(run_dir)
        )
        binding = next(iter(adapter._lb2_credential_home_bindings.values()))
        held_fd = binding.fd
        self.assertFalse(os.get_inheritable(held_fd))
        os.rename(run_dir / "home", escaped)
        errors: list[str] = []
        receipt = adapter.purge_transient_run_state(run_dir, set(), errors)
        self.assertEqual(
            (escaped / "oauth-secret").read_bytes(), b"escaped credential bytes"
        )
        self.assertFalse(binding.deletion_verified)
        self.assertTrue(any("missing or moved" in error for error in errors))
        self.assertFalse(receipt["credential_homes_deleted"])
        self.assertFalse(receipt["asserted"])
        self.assertEqual(adapter._lb2_credential_home_bindings, {})
        with self.assertRaises(OSError):
            os.fstat(held_fd)

    def test_bound_purge_normal_cleanup_is_true_and_sequential_binding_is_exact(self):
        def original_arm_for(name, **kwargs):
            home_name = "prime-home" if name == "prime-agent" else "home"
            home = Path(kwargs["run_dir"]) / home_name
            home.mkdir(mode=0o755)
            private_bytes(home / "oauth-secret", name.encode())
            return mock.Mock(command=[name]), {}, {}

        adapter = self.load_binding_adapter(original_arm_for)
        self.assertIs(adapter.run_one.__globals__["arm_for"], adapter.arm_for)
        self.assertIs(
            adapter.run_one.__globals__["purge_transient_run_state"],
            adapter.purge_transient_run_state,
        )
        prior_fd: int | None = None
        for index, arm_name in enumerate(("jcode-native", "prime-agent")):
            run_dir = self.root / f"bound-normal-{index}"
            run_dir.mkdir(mode=0o700)
            adapter.arm_for(arm_name, **self.binding_arm_kwargs(run_dir))
            self.assertEqual(
                list(adapter._lb2_credential_home_bindings), [os.fspath(run_dir)]
            )
            binding = adapter._lb2_credential_home_bindings[os.fspath(run_dir)]
            self.assertEqual(
                binding.name, "prime-home" if arm_name == "prime-agent" else "home"
            )
            prior_fd = binding.fd
            errors: list[str] = []
            receipt = adapter.purge_transient_run_state(run_dir, set(), errors)
            self.assertEqual(errors, [])
            self.assertTrue(receipt["credential_homes_deleted"])
            self.assertTrue(receipt["asserted"])
            self.assertEqual(adapter._lb2_credential_home_bindings, {})
            with self.assertRaises(OSError):
                os.fstat(prior_fd)

    def test_cleanup_run_exception_cannot_skip_bound_purge_or_report_success(self):
        state: dict[str, object] = {"executed": False}
        adapter_ref: dict[str, object] = {}

        def original_arm_for(name, **kwargs):
            self.assertEqual(name, "jcode-native")
            home = Path(kwargs["run_dir"]) / "home"
            home.mkdir(mode=0o700)
            private_bytes(home / "oauth-secret", b"credential bytes")
            arm = mock.Mock()
            arm.command = ["jcode", "--ndjson", "prompt"]
            arm.auth_assertion = {"asserted": True}
            arm.activation_mode = "test"
            arm.skill_instructions_sha256 = None
            arm.staged_skill = None
            return arm, {}, {}

        def original_cleanup_run(arm_name, args, env, run_dir):
            del arm_name, args, env
            self.assertTrue(state["executed"])
            adapter = adapter_ref["adapter"]
            binding = next(iter(adapter._lb2_credential_home_bindings.values()))
            state["held_fd"] = binding.fd
            self.assertTrue((run_dir / "home").is_dir())
            raise RuntimeError("injected cleanup failure")

        adapter = self.load_binding_adapter(
            original_arm_for, original_cleanup_run=original_cleanup_run
        )
        adapter_ref["adapter"] = adapter
        self.assertIs(
            adapter.run_one.__globals__["cleanup_run"], adapter.cleanup_run
        )

        context_path = self.root / "cleanup-exception-context.json"
        private_bytes(context_path, b'{"question":"Question?"}\n')
        context_sha = hashlib.sha256(context_path.read_bytes()).hexdigest()
        fixture = adapter.Fixture(
            row_path=context_path,
            context_path=context_path,
            metadata={"question": "Question?"},
            expected_kind="Answer",
            expected_value="A",
            expected_canonical="Answer: A",
            row_sha256=context_sha,
            context_sha256=context_sha,
            context_bytes=context_path.stat().st_size,
            context_chars=len(context_path.read_text()),
            context_lines=1,
        )
        stdout = "\n".join(
            (
                json.dumps({"type": "tokens", "input": 1, "output": 1}),
                json.dumps(
                    {
                        "type": "done",
                        "provider": "OpenAI",
                        "model": RUN.MODEL,
                        "response": "The correct answer is (A)",
                    }
                ),
            )
        ) + "\n"

        def successful_execute(*_args):
            state["executed"] = True
            return 0, stdout, "", False, 0.01

        work_root = self.root / "cleanup-exception-work"
        args = argparse.Namespace(
            timeout=10, seed=RUN.DEFAULT_SEED, jcode="jcode",
            executable_identities={
                "jcode": {"path": "/frozen/jcode", "sha256": "c" * 64,
                          "bytes": 1, "version": "test",
                          "version_command": ["/frozen/jcode", "--version"]},
            },
        )
        with mock.patch.object(adapter, "execute", side_effect=successful_execute):
            row = adapter.run_one(
                arm_name="jcode-native",
                repetition=0,
                ordinal=0,
                fixture=fixture,
                prompt=None,
                args=args,
                root=self.root,
                source_home=self.root / "source-home",
                skill=self.root / "skill",
                auth_jcode={},
                auth_prime={},
                work_root=work_root,
                defer_scoring=True,
            )

        diagnostic = "adapter cleanup_run failed: RuntimeError: injected cleanup failure"
        run_dir = work_root / "r000-000-jcode-native"
        self.assertEqual(row["cleanup_errors"], [diagnostic])
        self.assertFalse(row["execution_success"])
        self.assertIsNone(row["success"])
        self.assertEqual(row["failure"]["kind"], "cleanup")
        self.assertEqual(row["failure"]["message"], diagnostic)
        self.assertTrue(row["credential_cleanup_assertion"]["asserted"])
        self.assertTrue(
            row["credential_cleanup_assertion"]["credential_homes_deleted"]
        )
        self.assertFalse((run_dir / "home").exists())
        self.assertEqual(adapter._lb2_credential_home_bindings, {})
        with self.assertRaises(OSError) as closed:
            os.fstat(state["held_fd"])
        self.assertEqual(closed.exception.errno, errno.EBADF)

    def test_bound_purge_missing_binding_is_false_without_fd_leak(self):
        def original_arm_for(name, **kwargs):
            del name, kwargs
            raise AssertionError("arm creation is not used")

        adapter = self.load_binding_adapter(original_arm_for)
        run_dir = self.root / "missing-binding-run"
        run_dir.mkdir(mode=0o700)
        home = run_dir / "home"
        home.mkdir(mode=0o700)
        private_bytes(home / "oauth-secret", b"credential bytes")
        errors: list[str] = []
        receipt = adapter.purge_transient_run_state(run_dir, set(), errors)
        self.assertTrue(any("missing exact arm-time" in error for error in errors))
        self.assertFalse(receipt["credential_homes_deleted"])
        self.assertFalse(receipt["asserted"])
        self.assertFalse(home.exists())
        self.assertEqual(adapter._lb2_credential_home_bindings, {})

    def test_safe_purge_removes_readonly_nested_skill_without_following_symlink(self):
        run_dir = self.root / "readonly-cleanup-run"
        run_dir.mkdir(mode=0o700)
        home = run_dir / "home"
        skill = home / ".jcode" / "skills" / "azdaja" / "nested"
        skill.mkdir(mode=0o700, parents=True)
        readonly = skill / "component.bin"
        readonly.write_bytes(b"frozen candidate bytes")
        readonly.chmod(0o400)
        for directory in (
            skill, skill.parent, skill.parent.parent,
            skill.parent.parent.parent, home,
        ):
            directory.chmod(0o500)
        external = self.root / "external-cleanup-target"
        external.mkdir(mode=0o700)
        private_bytes(external / "must-survive", b"external")
        (run_dir / "external-link").symlink_to(external, target_is_directory=True)
        private_bytes(run_dir / "stdout.ndjson", b"")
        private_bytes(run_dir / "stderr.log", b"")
        errors: list[str] = []
        receipt = RUN.safe_purge_transient_run_state(
            run_dir, {"stdout.ndjson", "stderr.log"}, errors
        )
        self.assertEqual(errors, [])
        self.assertEqual(
            set(os.listdir(run_dir)), {"stdout.ndjson", "stderr.log"}
        )
        self.assertFalse(home.exists())
        self.assertFalse((run_dir / "external-link").exists())
        self.assertEqual((external / "must-survive").read_bytes(), b"external")
        self.assertTrue(receipt["asserted"])
        self.assertTrue(receipt["credential_homes_deleted"])

    def test_safe_purge_quarantine_escape_cannot_claim_credentials_deleted(self):
        run_dir = self.root / "cleanup-escape-run"
        run_dir.mkdir(mode=0o700)
        home = run_dir / "home"
        home.mkdir(mode=0o700)
        private_bytes(home / "secret", b"owner oauth secret")
        private_bytes(run_dir / "stdout.ndjson", b"")
        private_bytes(run_dir / "stderr.log", b"")
        escaped = self.root / "escaped-home"
        invoked = False

        def escape(parent_fd, quarantine, expected):
            nonlocal invoked
            del expected
            if invoked:
                return
            invoked = True
            os.rename(quarantine, escaped, src_dir_fd=parent_fd)

        errors: list[str] = []
        with mock.patch.object(
            RUN, "_cleanup_after_quarantine_hook", side_effect=escape
        ):
            receipt = RUN.safe_purge_transient_run_state(
                run_dir, {"stdout.ndjson", "stderr.log"}, errors
            )
        self.assertTrue(invoked)
        self.assertEqual((escaped / "secret").read_bytes(), b"owner oauth secret")
        self.assertFalse((run_dir / "home").exists())
        self.assertTrue(errors)
        self.assertFalse(receipt["credential_homes_deleted"])
        self.assertFalse(receipt["asserted"])

        # The scorer's successful-row evidence contract refuses the false
        # credential cleanup receipt, so such a job cannot publish success.
        score_test = importlib.util.spec_from_file_location(
            "lb2_score_fixture_for_cleanup_escape", HERE / "test_score.py"
        )
        module = importlib.util.module_from_spec(score_test)
        sys.modules[score_test.name] = module
        assert score_test.loader is not None
        score_test.loader.exec_module(module)
        with tempfile.TemporaryDirectory(dir=TMP_PARENT) as directory:
            fixture_case = module.ScoreTests()
            generated = fixture_case.make_artifacts(Path(directory))
            successful = next(
                row for row in generated["rows"] if row["arm"] == "prime-agent"
            )
            successful["credential_cleanup_assertion"] = receipt
            successful["cleanup_errors"] = list(errors)
            matching_job = next(
                item for item in generated["schedule"]["jobs"]
                if item["run_id"] == successful["run_id"]
            )
            with self.assertRaises(SCORE.ScoreError):
                SCORE.validate_run_rows(
                    [successful], [matching_job], generated["schedule"],
                    {item["id"]: item for item in generated["fixtures"]},
                )

    def test_safe_purge_regular_final_unlink_race_detects_escape(self):
        run_dir = self.root / "cleanup-final-file-run"
        run_dir.mkdir(mode=0o700)
        secret = run_dir / "secret-file"
        private_bytes(secret, b"regular secret")
        secret.chmod(0o400)
        private_bytes(run_dir / "stdout.ndjson", b"")
        private_bytes(run_dir / "stderr.log", b"")
        escaped = self.root / "escaped-regular"
        real_unlink = os.unlink
        invoked = False

        def raced_unlink(path, *, dir_fd=None):
            nonlocal invoked
            if not invoked and str(path).startswith(".lb2-cleanup-"):
                invoked = True
                os.rename(path, escaped, src_dir_fd=dir_fd)
                replacement_fd = os.open(
                    path, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600, dir_fd=dir_fd,
                )
                os.close(replacement_fd)
            return real_unlink(path, dir_fd=dir_fd)

        errors: list[str] = []
        with mock.patch.object(RUN.os, "unlink", side_effect=raced_unlink):
            receipt = RUN.safe_purge_transient_run_state(
                run_dir, {"stdout.ndjson", "stderr.log"}, errors
            )
        self.assertTrue(invoked)
        self.assertEqual(escaped.read_bytes(), b"regular secret")
        self.assertTrue(any("escaped" in error for error in errors))
        self.assertFalse(receipt["credential_homes_deleted"])
        self.assertFalse(receipt["asserted"])

    def test_safe_purge_directory_final_rmdir_race_detects_escape(self):
        run_dir = self.root / "cleanup-final-directory-run"
        run_dir.mkdir(mode=0o700)
        (run_dir / "home").mkdir(mode=0o500)
        private_bytes(run_dir / "stdout.ndjson", b"")
        private_bytes(run_dir / "stderr.log", b"")
        escaped = self.root / "escaped-directory"
        real_rmdir = os.rmdir
        invoked = False

        def raced_rmdir(path, *, dir_fd=None):
            nonlocal invoked
            if not invoked and str(path).startswith(".lb2-cleanup-"):
                invoked = True
                os.rename(path, escaped, src_dir_fd=dir_fd)
                os.mkdir(path, mode=0o700, dir_fd=dir_fd)
            return real_rmdir(path, dir_fd=dir_fd)

        errors: list[str] = []
        with mock.patch.object(RUN.os, "rmdir", side_effect=raced_rmdir):
            receipt = RUN.safe_purge_transient_run_state(
                run_dir, {"stdout.ndjson", "stderr.log"}, errors
            )
        self.assertTrue(invoked)
        self.assertTrue(escaped.is_dir())
        self.assertTrue(any("escaped" in error for error in errors))
        self.assertFalse(receipt["credential_homes_deleted"])
        self.assertFalse(receipt["asserted"])

    @unittest.skipUnless(
        sys.platform == "darwin" and hasattr(os, "O_SYMLINK"),
        "requires Darwin held-symlink descriptor semantics",
    )
    def test_safe_purge_symlink_final_unlink_race_detects_escape(self):
        run_dir = self.root / "cleanup-final-symlink-run"
        run_dir.mkdir(mode=0o700)
        target = self.root / "symlink-target"
        private_bytes(target, b"target")
        (run_dir / "transient-link").symlink_to(target)
        private_bytes(run_dir / "stdout.ndjson", b"")
        private_bytes(run_dir / "stderr.log", b"")
        escaped = self.root / "escaped-symlink"
        real_unlink = os.unlink
        invoked = False

        def raced_unlink(path, *, dir_fd=None):
            nonlocal invoked
            if not invoked and str(path).startswith(".lb2-cleanup-"):
                invoked = True
                os.rename(path, escaped, src_dir_fd=dir_fd)
                os.symlink(target, path, dir_fd=dir_fd)
            return real_unlink(path, dir_fd=dir_fd)

        errors: list[str] = []
        with mock.patch.object(RUN.os, "unlink", side_effect=raced_unlink):
            receipt = RUN.safe_purge_transient_run_state(
                run_dir, {"stdout.ndjson", "stderr.log"}, errors
            )
        self.assertTrue(invoked)
        self.assertTrue(escaped.is_symlink())
        self.assertEqual(escaped.resolve(), target)
        self.assertTrue(any("escaped" in error for error in errors))
        self.assertFalse(receipt["credential_homes_deleted"])
        self.assertFalse(receipt["asserted"])

    def test_safe_purge_final_unlink_detects_hardlink_injection_without_chmod(self):
        run_dir = self.root / "cleanup-final-hardlink-run"
        run_dir.mkdir(mode=0o700)
        secret = run_dir / "readonly-secret"
        private_bytes(secret, b"hard-linked secret")
        secret.chmod(0o400)
        private_bytes(run_dir / "stdout.ndjson", b"")
        private_bytes(run_dir / "stderr.log", b"")
        escaped = self.root / "injected-hardlink"
        real_unlink = os.unlink
        invoked = False

        def raced_unlink(path, *, dir_fd=None):
            nonlocal invoked
            if not invoked and str(path).startswith(".lb2-cleanup-"):
                invoked = True
                os.link(
                    path, escaped, src_dir_fd=dir_fd,
                    follow_symlinks=False,
                )
            return real_unlink(path, dir_fd=dir_fd)

        errors: list[str] = []
        with mock.patch.object(RUN.os, "unlink", side_effect=raced_unlink):
            receipt = RUN.safe_purge_transient_run_state(
                run_dir, {"stdout.ndjson", "stderr.log"}, errors
            )
        self.assertTrue(invoked)
        self.assertEqual(escaped.read_bytes(), b"hard-linked secret")
        self.assertEqual(stat.S_IMODE(escaped.stat().st_mode), 0o400)
        self.assertTrue(any("hard link" in error for error in errors))
        self.assertFalse(receipt["credential_homes_deleted"])
        self.assertFalse(receipt["asserted"])

    def test_safe_purge_detects_quarantine_inode_swap_and_preserves_racer(self):
        run_dir = self.root / "cleanup-racer-run"
        run_dir.mkdir(mode=0o700)
        home = run_dir / "home"
        home.mkdir(mode=0o500)
        private_bytes(run_dir / "stdout.ndjson", b"")
        private_bytes(run_dir / "stderr.log", b"")
        invoked = False

        def swap(parent_fd, quarantine, expected):
            nonlocal invoked
            del expected
            if invoked:
                return
            invoked = True
            os.rename(
                quarantine, "preserved-original",
                src_dir_fd=parent_fd, dst_dir_fd=parent_fd,
            )
            fd = os.open(
                quarantine, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600, dir_fd=parent_fd,
            )
            try:
                os.write(fd, b"racer must survive")
                os.fsync(fd)
            finally:
                os.close(fd)

        errors: list[str] = []
        with mock.patch.object(
            RUN, "_cleanup_after_quarantine_hook", side_effect=swap
        ):
            receipt = RUN.safe_purge_transient_run_state(
                run_dir, {"stdout.ndjson", "stderr.log"}, errors
            )
        self.assertTrue(invoked)
        self.assertTrue(any("swapped" in error for error in errors))
        quarantine = next(
            child for child in run_dir.iterdir()
            if child.name.startswith(".lb2-cleanup-")
        )
        self.assertEqual(quarantine.read_bytes(), b"racer must survive")
        self.assertTrue((run_dir / "preserved-original").is_dir())
        self.assertFalse(receipt["asserted"])

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
        self.assertIn("not OS containment", RUN.CONTAINMENT_DISCLOSURE)
        self.assertIn("copy credential bytes first", RUN.CONTAINMENT_DISCLOSURE)

    def test_actual_full_prime_snapshot_runs_frozen_version_when_available(self):
        required = {name: shutil.which(name) for name in ("prime-agent", "jcode", "node")}
        kernel = Path.home() / ".prime" / "agent" / "kernel-venv"
        if any(value is None for value in required.values()) or not (kernel / "bin" / "python").exists():
            self.skipTest("Prime/Jcode/Node/kernel runtime closure is unavailable")
        source_adapter = RUN._load_python(
            "lb2_actual_contract_" + os.urandom(4).hex(), RUN.OOLONG_SOURCE
        )
        adapter_arms = tuple(getattr(source_adapter, "ARMS", ()))
        if len(adapter_arms) != len(RUN.ARMS) or set(adapter_arms) != set(RUN.ARMS):
            self.skipTest("working OOLONG adapter arm contract is incompatible")
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



    def test_build_schedule_independently_rejects_candidate_binary_hash_mismatch(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        valid = self.fake_schedule(suite)["configuration"]
        candidate = copy.deepcopy(valid["candidate"])
        candidate["components"]["azdaja"]["sha256"] = "9" * 64
        candidate["sha256"] = SCORE.sha256_bytes(
            SCORE.canonical_json_bytes(candidate["components"])
        )
        with self.assertRaisesRegex(RUN.BenchError, "component/executable"):
            RUN.build_schedule(
                suite, seed=RUN.DEFAULT_SEED, timeout=60,
                candidate=candidate, controller=valid["controller"],
                executables=valid["executables"],
                runtime_closure=valid["runtime_closure"],
            )

    def test_transform_legacy_missing_root_transcript_is_terminal_trace_failure(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        job = next(item for item in schedule["jobs"] if item["arm"] == "jcode-azdaja")
        run_dir = self.root / "legacy-transform"
        run_dir.mkdir(mode=0o700)
        private_bytes(run_dir / "stdout.ndjson", b"")
        private_bytes(run_dir / "stderr.log", b"")
        artifacts = {
            "stdout": self.artifact_receipt(run_dir / "stdout.ndjson"),
            "stderr": self.artifact_receipt(run_dir / "stderr.log"),
        }
        context = "safe public context"
        base = RUN.controller_failure_row(
            job, schedule, "synthetic", artifacts, public_context=context
        )
        row = RUN.transform_adapter_row(
            base, job, schedule, raw_response="", trajectory_artifacts=artifacts,
            stdout_bytes=b"", root_trace_bytes=None, public_context=context,
        )
        self.assertFalse(row["execution_success"])
        self.assertEqual(row["failure"]["kind"], "trace_capture")
        self.assertFalse(row["root_context_leak_assertion"]["trace_valid"])
        RUN._verify_row_live(row, job, schedule, suite)

    def test_transform_exact_root_context_leak_has_terminal_precedence(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        job = next(item for item in schedule["jobs"] if item["arm"] == "jcode-azdaja")
        run_dir = self.root / "leak-transform"
        run_dir.mkdir(mode=0o700)
        private_bytes(run_dir / "stdout.ndjson", b"")
        private_bytes(run_dir / "stderr.log", b"")
        artifacts = {
            "stdout": self.artifact_receipt(run_dir / "stdout.ndjson"),
            "stderr": self.artifact_receipt(run_dir / "stderr.log"),
        }
        context = "Ω" * 120
        base = RUN.controller_failure_row(
            job, schedule, "synthetic", artifacts, public_context=context
        )
        trace = synthetic_root_transcript("prefix" + context + "suffix")
        row = RUN.transform_adapter_row(
            base, job, schedule, raw_response="", trajectory_artifacts=artifacts,
            stdout_bytes=b"", root_trace_bytes=trace, public_context=context,
        )
        self.assertFalse(row["execution_success"])
        self.assertEqual(row["failure"]["kind"], "root_context_leak")
        self.assertTrue(row["root_context_leak_assertion"]["leak_detected"])
        RUN._verify_row_live(row, job, schedule, suite)

    def test_transform_control_missing_usage_uses_tool_output_char_fallback(self):
        manifest, _, _ = self.make_public()
        suite = RUN.capture_public_suite(manifest)
        schedule = self.fake_schedule(suite)
        job = next(item for item in schedule["jobs"] if item["arm"] == "jcode-native")
        run_dir = self.root / "control-economy-transform"
        run_dir.mkdir(mode=0o700)
        stdout = (json.dumps({
            "type": "tool_done", "id": "call-1", "output": "abcdefgh"
        }, separators=(",", ":")) + "\n").encode()
        private_bytes(run_dir / "stdout.ndjson", stdout)
        private_bytes(run_dir / "stderr.log", b"")
        artifacts = {
            "stdout": self.artifact_receipt(run_dir / "stdout.ndjson"),
            "stderr": self.artifact_receipt(run_dir / "stderr.log"),
        }
        base = RUN.controller_failure_row(job, schedule, "synthetic", artifacts)
        row = RUN.transform_adapter_row(
            base, job, schedule, raw_response="", trajectory_artifacts=artifacts,
            stdout_bytes=stdout,
        )
        economy = row["root_token_economy"]
        self.assertTrue(economy["available"])
        self.assertEqual(economy["tokens"], 2.0)
        self.assertEqual(
            economy["authority"],
            "exact_control_tool_output_unicode_characters_div_4",
        )
        RUN._verify_row_live(row, job, schedule, suite)


if __name__ == "__main__":
    unittest.main()
