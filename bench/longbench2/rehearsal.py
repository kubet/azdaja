#!/usr/bin/env python3
"""Offline fail-closed pre-freeze dress rehearsal for LongBench-v2 production.

This is a synthetic pipeline-integrity rehearsal, never a benchmark run.  It
creates a fixed 20-fixture x 3-arm bundle without OAuth or inference, validates
all terminal rows/claims/completions/artifacts before opening synthetic gold,
then publishes a private score report and, last, a target-bound final receipt.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import random
import re
import shutil
import stat
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
PRODUCTION_CONTROLLER = HERE / "run.py"
PRODUCTION_VALIDATOR = HERE / "score.py"
PRODUCTION_ADAPTER = HERE.parent / "oolong" / "run.py"
SUCCESS_TRACE = HERE / "fixtures" / "v43-rust-serde-success.jsonl"
RETRY_TRACE = HERE / "fixtures" / "v43-rust-serde-transient-retry.jsonl"


def _load_python(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Python component: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCORE = _load_python("azdaja_lb2_score_for_pre_freeze_rehearsal", PRODUCTION_VALIDATOR)

SCHEMA_VERSION = 1
SUITE_ID = "lb2-pre-freeze-rehearsal-20x3-v1"
FIXTURE_COUNT = 20
ARMS = tuple(SCORE.ARMS)
JOB_COUNT = FIXTURE_COUNT * len(ARMS)
REHEARSAL_SEED = 43002026
REHEARSAL_TIMEOUT_SECONDS = 7
PRODUCTION_FIXTURE_COUNT = 63
PRODUCTION_JOB_COUNT = 189
PRODUCTION_MINIMUM_CORRECT_N = 16
RUN_ID_DOMAIN = b"lb2-pre-freeze-rehearsal-run-v1\0"
CANDIDATE_FILES = ("SKILL.md", "azdaja", "config.toml")
SUCCESS_TRACE_SHA256 = "41e4456b4a6601424ae03b3b3d0821a4866666a8e117cd5f6d6e5d51a17f754f"
RETRY_TRACE_SHA256 = "9294429a6354f9e42690adbf1b6ac453fd3d0657d035b357adbf9a9dcc3b8f5c"
ROOT_NAMES_WITHOUT_RECEIPT = {
    "public", "private", "schedule.json", "runs.jsonl", "claims", "artifacts",
    "terminal-validation.json", "report.json",
}
FINAL_RECEIPT_NAME = "final-receipt.json"
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class RehearsalError(RuntimeError):
    """A rehearsal or production-target invariant failed."""


def canonical_json_bytes(value: Any) -> bytes:
    return SCORE.canonical_json_bytes(value)


def canonical_json_file_bytes(value: Any) -> bytes:
    return SCORE.canonical_json_file_bytes(value)


def sha256_bytes(value: bytes) -> str:
    return SCORE.sha256_bytes(value)


def _absolute(path: Path | str) -> Path:
    return Path(os.path.abspath(Path(path).expanduser()))


def _mode(metadata: os.stat_result) -> int:
    return stat.S_IMODE(metadata.st_mode)


def _require_owner_directory(path: Path, label: str) -> Path:
    path = _absolute(path)
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise RehearsalError(f"cannot stat {label} {path}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise RehearsalError(f"{label} must be a non-symlink directory: {path}")
    if os.name == "posix":
        if _mode(metadata) != 0o700:
            raise RehearsalError(f"{label} must be exactly mode 0700: {path}")
        if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
            raise RehearsalError(f"{label} must be owned by the current user: {path}")
    return path


def _read_regular(path: Path, label: str, *, owner_only: bool = False) -> bytes:
    path = _absolute(path)
    if path.is_symlink():
        raise RehearsalError(f"{label} must not be a symlink: {path}")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise RehearsalError(f"cannot open {label} {path}: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise RehearsalError(f"{label} must be a singly-linked regular file: {path}")
        if os.name == "posix":
            if before.st_mode & 0o022:
                raise RehearsalError(f"{label} must not be group/other writable: {path}")
            if owner_only and _mode(before) != 0o600:
                raise RehearsalError(f"{label} must be exactly mode 0600: {path}")
            if hasattr(os, "getuid") and before.st_uid != os.getuid():
                raise RehearsalError(f"{label} must be owned by the current user: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(fd)
        data = b"".join(chunks)
        fingerprint = lambda item: (
            item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns,
            item.st_ctime_ns, item.st_nlink,
        )
        if fingerprint(before) != fingerprint(after) or len(data) != before.st_size:
            raise RehearsalError(f"{label} changed during capture: {path}")
        rebound = path.lstat()
        if stat.S_ISLNK(rebound.st_mode) or fingerprint(rebound) != fingerprint(after):
            raise RehearsalError(f"{label} pathname identity changed during capture: {path}")
        return data
    finally:
        os.close(fd)


def _decode_object(data: bytes, label: str, *, canonical: bool = True) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=SCORE._object_no_duplicates,
            parse_constant=SCORE._reject_constant,
        )
    except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise RehearsalError(f"invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise RehearsalError(f"{label} must be a JSON object")
    if canonical and data != canonical_json_file_bytes(value):
        raise RehearsalError(f"{label} must be canonical compact JSON with one final LF")
    return value


def _read_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    data = _read_regular(path, label, owner_only=True)
    return _decode_object(data, label), data


def _write_exclusive(path: Path, data: bytes, *, mode: int = 0o600) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, mode)
    except OSError as exc:
        raise RehearsalError(f"cannot exclusively create {path}: {exc}") from exc
    try:
        if os.name == "posix":
            os.fchmod(fd, mode)
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise RehearsalError(f"short write to {path}")
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_json(path: Path, value: Any) -> None:
    # Reuse the production scorer's canonical, durable, no-replace publisher.
    try:
        SCORE.atomic_create_private_json(path, value)
    except (SCORE.ScoreError, OSError) as exc:
        raise RehearsalError(f"cannot publish {path.name}: {exc}") from exc


def _mkdir(path: Path) -> None:
    try:
        path.mkdir(mode=0o700, exist_ok=False)
    except OSError as exc:
        raise RehearsalError(f"cannot create private directory {path}: {exc}") from exc
    if os.name == "posix":
        os.chmod(path, 0o700)


def _file_identity(path: Path, label: str, *, executable: bool = False) -> dict[str, Any]:
    resolved = _absolute(path).resolve(strict=True)
    data = _read_regular(resolved, label)
    metadata = resolved.stat()
    if executable and not metadata.st_mode & stat.S_IXUSR:
        raise RehearsalError(f"{label} must have owner execute permission: {resolved}")
    return {"path": str(resolved), "sha256": sha256_bytes(data), "bytes": len(data)}


def _resolve_executable(value: str | Path, label: str) -> Path:
    raw = str(value)
    found = shutil.which(raw) if os.sep not in raw else raw
    if not found:
        raise RehearsalError(f"cannot resolve target {label} executable: {value}")
    path = _absolute(found).resolve(strict=True)
    _file_identity(path, f"target {label}", executable=True)
    return path


def _candidate_identity(path: Path) -> dict[str, Any]:
    candidate = _absolute(path)
    if candidate.is_symlink():
        raise RehearsalError("target candidate must not be a symlink")
    candidate = candidate.resolve(strict=True)
    if not candidate.is_dir():
        raise RehearsalError("target candidate must be a directory")
    names = {entry.name for entry in os.scandir(candidate)}
    if names != set(CANDIDATE_FILES):
        raise RehearsalError(
            f"target candidate inventory must be exactly {list(CANDIDATE_FILES)}, got {sorted(names)}"
        )
    components: dict[str, Any] = {}
    for name in CANDIDATE_FILES:
        identity = _file_identity(
            candidate / name, f"target candidate {name}", executable=name == "azdaja"
        )
        identity.pop("path")
        components[name] = identity
    return {
        "path": str(candidate),
        "sha256": sha256_bytes(canonical_json_bytes(components)),
        "components": components,
    }


def production_configuration(*, seed: int, timeout: int) -> dict[str, Any]:
    if type(seed) is not int or type(timeout) is not int or timeout <= 0:
        raise RehearsalError("target production seed/timeout must be an integer/positive integer")
    return {
        "suite_id": SCORE.SUITE_ID,
        "fixture_count": PRODUCTION_FIXTURE_COUNT,
        "scheduled_jobs": PRODUCTION_JOB_COUNT,
        "minimum_correct_n": PRODUCTION_MINIMUM_CORRECT_N,
        "model": SCORE.MODEL,
        "reasoning": SCORE.REASONING,
        "arms": list(SCORE.ARMS),
        "repetitions": 1,
        "seed": seed,
        "timeout_seconds": timeout,
    }


def build_target_identity(
    *, manifest: Path | str, candidate: Path | str, jcode: Path | str,
    prime_agent: Path | str, seed: int, timeout: int,
) -> dict[str, Any]:
    """Capture the exact source inputs a fresh production freeze will consume."""
    manifest_identity = _file_identity(Path(manifest), "target production manifest")
    candidate_identity = _candidate_identity(Path(candidate))
    jcode_path = _resolve_executable(jcode, "jcode")
    prime_path = _resolve_executable(prime_agent, "prime-agent")
    azdaja_path = Path(candidate_identity["path"]) / "azdaja"
    target = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_target",
        "manifest": manifest_identity,
        "candidate": candidate_identity,
        "controller": _file_identity(PRODUCTION_CONTROLLER, "target production controller"),
        "validator": _file_identity(PRODUCTION_VALIDATOR, "target production validator"),
        "adapter": _file_identity(PRODUCTION_ADAPTER, "target production adapter"),
        "executables": {
            "jcode": _file_identity(jcode_path, "target jcode", executable=True),
            "azdaja": _file_identity(azdaja_path, "target azdaja", executable=True),
            "prime-agent": _file_identity(prime_path, "target prime-agent", executable=True),
        },
        "config": _file_identity(
            Path(candidate_identity["path"]) / "config.toml", "target candidate config"
        ),
        "configuration": production_configuration(seed=seed, timeout=timeout),
    }
    # The separately named config and executable identities must be exact aliases
    # of the candidate components, closing accidental target substitution.
    config_component = candidate_identity["components"]["config.toml"]
    binary_component = candidate_identity["components"]["azdaja"]
    if any(target["config"][key] != config_component[key] for key in ("sha256", "bytes")):
        raise RehearsalError("target candidate/config identity diverged")
    if any(target["executables"]["azdaja"][key] != binary_component[key] for key in ("sha256", "bytes")):
        raise RehearsalError("target candidate/azdaja executable identity diverged")
    target["target_sha256"] = sha256_bytes(canonical_json_bytes(target))
    return target


def _reopen_target(target: Any) -> dict[str, Any]:
    """Rebuild an embedded target from paths; no identity check may be skipped."""
    if not isinstance(target, dict) or target.get("record_type") != "lb2_pre_freeze_rehearsal_target":
        raise RehearsalError("final receipt target is malformed")
    try:
        rebuilt = build_target_identity(
            manifest=target["manifest"]["path"],
            candidate=target["candidate"]["path"],
            jcode=target["executables"]["jcode"]["path"],
            prime_agent=target["executables"]["prime-agent"]["path"],
            seed=target["configuration"]["seed"],
            timeout=target["configuration"]["timeout_seconds"],
        )
    except (KeyError, TypeError) as exc:
        raise RehearsalError("final receipt target paths/configuration are malformed") from exc
    if rebuilt != target:
        raise RehearsalError("target production identities changed since rehearsal")
    return rebuilt


def _fixture_id(index: int) -> str:
    digest = sha256_bytes(f"{SUITE_ID}\0{index}".encode())[:24]
    return f"lb2r-{digest}"


def _synthetic_answer(index: int) -> str:
    return SCORE.CHOICE_LABELS[index % len(SCORE.CHOICE_LABELS)]


def _manifest_identity(manifest: dict[str, Any]) -> str:
    value = copy.deepcopy(manifest)
    value.pop("gold_sha256", None)
    return sha256_bytes(canonical_json_file_bytes(value))


def generate_synthetic_phase(bundle: Path) -> tuple[Path, Path, dict[str, Any]]:
    """Generate deterministic synthetic public+gold; perform no run or scoring."""
    public = bundle / "public"
    private = bundle / "private"
    payloads = public / "payloads"
    _mkdir(public)
    _mkdir(private)
    _mkdir(payloads)
    fixtures: list[dict[str, Any]] = []
    gold_fixtures: list[dict[str, Any]] = []
    for index in range(FIXTURE_COUNT):
        fixture_id = _fixture_id(index)
        payload = {
            "choices": {
                label: f"Synthetic choice {label} for fixture {index:02d}"
                for label in SCORE.CHOICE_LABELS
            },
            "context": (
                f"Deterministic offline rehearsal context {index:02d}. "
                "It is synthetic and carries no LongBench observation."
            ),
            "fixture_ordinal": index + 1,
            "question": f"Synthetic pipeline question {index:02d}?",
        }
        payload_bytes = canonical_json_file_bytes(payload)
        payload_name = f"{fixture_id}.json"
        _write_exclusive(payloads / payload_name, payload_bytes)
        fixtures.append({
            "id": fixture_id,
            "ordinal": index + 1,
            "payload": f"payloads/{payload_name}",
            "payload_sha256": sha256_bytes(payload_bytes),
            "payload_bytes": len(payload_bytes),
        })
        gold_fixtures.append({
            "id": fixture_id,
            "answer": _synthetic_answer(index),
            "payload_sha256": sha256_bytes(payload_bytes),
        })
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_public_manifest",
        "suite_id": SUITE_ID,
        "synthetic": True,
        "benchmark_result": False,
        "configuration": {
            "fixture_count": FIXTURE_COUNT,
            "arms": list(ARMS),
            "jobs": JOB_COUNT,
            "seed": REHEARSAL_SEED,
            "timeout_seconds": REHEARSAL_TIMEOUT_SECONDS,
        },
        "fixtures": fixtures,
    }
    gold = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_synthetic_gold",
        "suite_id": SUITE_ID,
        "synthetic": True,
        "benchmark_result": False,
        "manifest_identity_sha256": _manifest_identity(manifest),
        "fixtures": gold_fixtures,
    }
    gold_bytes = canonical_json_file_bytes(gold)
    manifest["gold_sha256"] = sha256_bytes(gold_bytes)
    _write_exclusive(private / "gold.json", gold_bytes)
    _write_json(public / "manifest.json", manifest)
    return public / "manifest.json", private / "gold.json", manifest


def _load_public(manifest_path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    public = _require_owner_directory(manifest_path.parent, "rehearsal public root")
    names = {item.name for item in os.scandir(public)}
    if names != {"manifest.json", "payloads"}:
        raise RehearsalError("rehearsal public root inventory is not exact")
    manifest, manifest_bytes = _read_object(manifest_path, "rehearsal public manifest")
    expected_shape = {
        "schema_version", "record_type", "suite_id", "synthetic", "benchmark_result",
        "configuration", "fixtures", "gold_sha256",
    }
    if set(manifest) != expected_shape:
        raise RehearsalError("rehearsal public manifest shape is invalid")
    literals = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_public_manifest",
        "suite_id": SUITE_ID,
        "synthetic": True,
        "benchmark_result": False,
    }
    if any(manifest.get(key) != value for key, value in literals.items()):
        raise RehearsalError("rehearsal public manifest literals drifted")
    if manifest["configuration"] != {
        "fixture_count": FIXTURE_COUNT,
        "arms": list(ARMS),
        "jobs": JOB_COUNT,
        "seed": REHEARSAL_SEED,
        "timeout_seconds": REHEARSAL_TIMEOUT_SECONDS,
    } or not isinstance(manifest.get("gold_sha256"), str) or not SHA256_RE.fullmatch(manifest["gold_sha256"]):
        raise RehearsalError("rehearsal public configuration/commitment drifted")
    entries = manifest["fixtures"]
    if not isinstance(entries, list) or len(entries) != FIXTURE_COUNT:
        raise RehearsalError("rehearsal public fixture count drifted")
    payloads = _require_owner_directory(public / "payloads", "rehearsal payload root")
    expected_names: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(entries):
        if not isinstance(item, dict) or set(item) != {
            "id", "ordinal", "payload", "payload_sha256", "payload_bytes"
        }:
            raise RehearsalError(f"rehearsal fixture {index + 1} shape is invalid")
        fixture_id = _fixture_id(index)
        payload_name = f"{fixture_id}.json"
        if item != {
            "id": fixture_id,
            "ordinal": index + 1,
            "payload": f"payloads/{payload_name}",
            "payload_sha256": item["payload_sha256"],
            "payload_bytes": item["payload_bytes"],
        } or fixture_id in by_id:
            raise RehearsalError(f"rehearsal fixture {index + 1} identity/order drifted")
        data = _read_regular(payloads / payload_name, f"rehearsal payload {fixture_id}", owner_only=True)
        payload = _decode_object(data, f"rehearsal payload {fixture_id}")
        if set(payload) != {"choices", "context", "fixture_ordinal", "question"}:
            raise RehearsalError(f"rehearsal payload {fixture_id} shape drifted")
        if payload["fixture_ordinal"] != index + 1:
            raise RehearsalError(f"rehearsal payload {fixture_id} ordinal drifted")
        if item["payload_sha256"] != sha256_bytes(data) or item["payload_bytes"] != len(data):
            raise RehearsalError(f"rehearsal payload {fixture_id} commitment drifted")
        expected_names.add(payload_name)
        by_id[fixture_id] = {**item, "payload_object": payload}
    if {item.name for item in os.scandir(payloads)} != expected_names:
        raise RehearsalError("rehearsal payload inventory is not exact")
    if manifest_bytes != canonical_json_file_bytes(manifest):
        raise RehearsalError("rehearsal manifest bytes changed")
    return manifest, by_id


def build_schedule(manifest: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    target_sha = target.get("target_sha256")
    if not isinstance(target_sha, str) or not SHA256_RE.fullmatch(target_sha):
        raise RehearsalError("target identity is missing its aggregate hash")
    rng = random.Random(REHEARSAL_SEED)
    fixture_order = list(manifest["fixtures"])
    rng.shuffle(fixture_order)
    jobs: list[dict[str, Any]] = []
    for fixture in fixture_order:
        arm_order = list(ARMS)
        rng.shuffle(arm_order)
        for arm in arm_order:
            jobs.append({
                "ordinal": len(jobs) + 1,
                "fixture_id": fixture["id"],
                "payload_sha256": fixture["payload_sha256"],
                "arm": arm,
                "repetition": 1,
            })
    schedule: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_schedule",
        "suite": {
            "suite_id": SUITE_ID,
            "manifest_sha256": sha256_bytes(canonical_json_file_bytes(manifest)),
            "fixture_count": FIXTURE_COUNT,
        },
        "configuration": {
            "arms": list(ARMS),
            "repetitions": 1,
            "seed": REHEARSAL_SEED,
            "timeout_seconds": REHEARSAL_TIMEOUT_SECONDS,
            "offline": True,
            "oauth": False,
            "inference": False,
            "gold_path_parameter": False,
            "target_sha256": target_sha,
        },
        "target": copy.deepcopy(target),
        "jobs": jobs,
    }
    schedule_id = sha256_bytes(canonical_json_bytes(schedule))
    for job in jobs:
        job["run_id"] = sha256_bytes(
            RUN_ID_DOMAIN + schedule_id.encode("ascii") + canonical_json_bytes(job)
        )
    schedule["schedule_id"] = schedule_id
    return schedule


def _validate_schedule(
    schedule: dict[str, Any], manifest: dict[str, Any], fixtures: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    if set(schedule) != {
        "schema_version", "record_type", "suite", "configuration", "target", "jobs", "schedule_id"
    }:
        raise RehearsalError("rehearsal schedule shape is invalid")
    schedule_id = schedule.get("schedule_id")
    if not isinstance(schedule_id, str) or not SHA256_RE.fullmatch(schedule_id):
        raise RehearsalError("rehearsal schedule_id is invalid")
    identity = copy.deepcopy(schedule)
    identity.pop("schedule_id")
    for job in identity.get("jobs", []):
        if isinstance(job, dict):
            job.pop("run_id", None)
    if schedule_id != sha256_bytes(canonical_json_bytes(identity)):
        raise RehearsalError("rehearsal schedule identity drifted")
    if schedule["schema_version"] != SCHEMA_VERSION or schedule["record_type"] != "lb2_pre_freeze_rehearsal_schedule":
        raise RehearsalError("rehearsal schedule literals drifted")
    if schedule["suite"] != {
        "suite_id": SUITE_ID,
        "manifest_sha256": sha256_bytes(canonical_json_file_bytes(manifest)),
        "fixture_count": FIXTURE_COUNT,
    }:
        raise RehearsalError("rehearsal schedule/public binding drifted")
    target = schedule["target"]
    if not isinstance(target, dict) or target.get("target_sha256") != schedule["configuration"].get("target_sha256"):
        raise RehearsalError("rehearsal schedule target binding drifted")
    if schedule["configuration"] != {
        "arms": list(ARMS), "repetitions": 1, "seed": REHEARSAL_SEED,
        "timeout_seconds": REHEARSAL_TIMEOUT_SECONDS, "offline": True,
        "oauth": False, "inference": False, "gold_path_parameter": False,
        "target_sha256": target["target_sha256"],
    }:
        raise RehearsalError("rehearsal schedule configuration drifted")
    jobs = schedule["jobs"]
    if not isinstance(jobs, list) or len(jobs) != JOB_COUNT:
        raise RehearsalError("rehearsal schedule must contain exactly 60 jobs")
    rng = random.Random(REHEARSAL_SEED)
    fixture_order = list(manifest["fixtures"])
    rng.shuffle(fixture_order)
    expected: list[tuple[str, str]] = []
    for fixture in fixture_order:
        arm_order = list(ARMS)
        rng.shuffle(arm_order)
        expected.extend((fixture["id"], arm) for arm in arm_order)
    grid: set[tuple[str, str]] = set()
    for index, (job, cell) in enumerate(zip(jobs, expected), 1):
        if not isinstance(job, dict) or set(job) != {
            "ordinal", "fixture_id", "payload_sha256", "arm", "repetition", "run_id"
        }:
            raise RehearsalError(f"rehearsal schedule job {index} shape is invalid")
        if (job["fixture_id"], job["arm"]) != cell or job["ordinal"] != index or job["repetition"] != 1:
            raise RehearsalError(f"rehearsal schedule job {index} sequence drifted")
        fixture = fixtures.get(job["fixture_id"])
        if fixture is None or job["payload_sha256"] != fixture["payload_sha256"]:
            raise RehearsalError(f"rehearsal schedule job {index} payload drifted")
        base = dict(job)
        run_id = base.pop("run_id")
        expected_run = sha256_bytes(
            RUN_ID_DOMAIN + schedule_id.encode("ascii") + canonical_json_bytes(base)
        )
        if run_id != expected_run or (job["fixture_id"], job["arm"]) in grid:
            raise RehearsalError(f"rehearsal schedule job {index} run/grid identity drifted")
        grid.add((job["fixture_id"], job["arm"]))
    if grid != {(fixture_id, arm) for fixture_id in fixtures for arm in ARMS}:
        raise RehearsalError("rehearsal schedule is not the exact 20 x 3 grid")
    return jobs


def _response_for(job: dict[str, Any], fixture: dict[str, Any]) -> str:
    index = fixture["ordinal"] - 1
    answer = _synthetic_answer(index)
    # Exercise all production extraction envelopes without consulting gold.
    if job["arm"] == "jcode-native":
        return f"The correct answer is ({answer})"
    if job["arm"] == "jcode-azdaja":
        return f"{answer}\n"
    return f"The correct answer is {answer}"


def _validate_committed_trace_authority() -> tuple[bytes, bytes]:
    success = _read_regular(SUCCESS_TRACE, "committed v43 success trace")
    retry = _read_regular(RETRY_TRACE, "committed v43 transient retry trace")
    if sha256_bytes(success) != SUCCESS_TRACE_SHA256 or sha256_bytes(retry) != RETRY_TRACE_SHA256:
        raise RehearsalError("committed retained v43 model-trace sample identity drifted")
    try:
        routes = SCORE._category_routes_from_retained_trace(success, 1, SCORE.MODEL)
        retried_routes = SCORE._category_routes_from_retained_trace(retry, 1, SCORE.MODEL)
    except SCORE.ScoreError as exc:
        raise RehearsalError(f"production trace validator rejected committed v43 trace: {exc}") from exc
    if len(routes) != 1 or routes[0].get("depth") != 0 or routes[0].get("model") != SCORE.MODEL:
        raise RehearsalError("committed v43 success trace route drifted")
    if retried_routes != []:
        raise RehearsalError("committed v43 transient timeout/retry trace must suppress route assertion")
    # Prove the live validator accepts every duplicate-free compact permutation
    # of known fields rather than depending on serde or sorted key order.
    parsed = _decode_object(success, "committed v43 success trace", canonical=False)
    permutations = [
        dict(reversed(list(parsed.items()))),
        {"event": parsed["event"], **{key: value for key, value in parsed.items() if key != "event"}},
    ]
    for permutation in permutations:
        compact = json.dumps(
            permutation, ensure_ascii=False, sort_keys=False, separators=(",", ":")
        ).encode("utf-8") + b"\n"
        try:
            if SCORE._category_routes_from_retained_trace(compact, 1, SCORE.MODEL) != routes:
                raise RehearsalError("trace validator changed route under a known-field key permutation")
        except SCORE.ScoreError as exc:
            raise RehearsalError("trace validator rejected a duplicate-free compact known-field key order") from exc
    return success, retry


def run_offline_phase(
    *, manifest_path: Path, schedule_path: Path, runs_path: Path,
    claims_root: Path, artifacts_root: Path,
) -> None:
    """Write 60 rows + 60 claims + 60 done + 60 artifacts; accepts no gold path."""
    manifest, fixtures = _load_public(manifest_path)
    schedule, _ = _read_object(schedule_path, "rehearsal schedule")
    jobs = _validate_schedule(schedule, manifest, fixtures)
    success_trace, retry_trace = _validate_committed_trace_authority()
    _mkdir(claims_root)
    _mkdir(artifacts_root)
    row_bytes: list[bytes] = []
    for job in jobs:
        run_id = job["run_id"]
        _write_json(claims_root / f"{run_id}.claim.json", {
            "schema_version": SCHEMA_VERSION,
            "record_type": "lb2_pre_freeze_rehearsal_claim",
            "schedule_id": schedule["schedule_id"],
            "run_id": run_id,
            "ordinal": job["ordinal"],
        })
        run_dir = artifacts_root / run_id
        _mkdir(run_dir)
        fixture = fixtures[job["fixture_id"]]
        response = _response_for(job, fixture)
        response_bytes = response.encode("utf-8")
        _write_exclusive(run_dir / "response.txt", response_bytes)
        trace_kind = None
        trace_sha = None
        if job["arm"] == "jcode-azdaja":
            trace_kind = "v43_success" if fixture["ordinal"] % 2 else "v43_transient_timeout_retry"
            trace_bytes = success_trace if trace_kind == "v43_success" else retry_trace
            _write_exclusive(run_dir / "model-trace.jsonl", trace_bytes)
            trace_sha = sha256_bytes(trace_bytes)
        row = {
            "schema_version": SCHEMA_VERSION,
            "record_type": "lb2_pre_freeze_rehearsal_run",
            "suite_id": SUITE_ID,
            "benchmark_result": False,
            "schedule_id": schedule["schedule_id"],
            "run_id": run_id,
            "execution_ordinal": job["ordinal"],
            "fixture_id": job["fixture_id"],
            "payload_sha256": job["payload_sha256"],
            "arm": job["arm"],
            "repetition": 1,
            "offline": True,
            "oauth_used": False,
            "inference_used": False,
            "execution_success": True,
            "scoring_status": "rehearsal_deferred",
            "response": response,
            "artifact": {
                "directory": run_id,
                "response_sha256": sha256_bytes(response_bytes),
                "response_bytes": len(response_bytes),
                "model_trace_kind": trace_kind,
                "model_trace_sha256": trace_sha,
            },
        }
        encoded = canonical_json_file_bytes(row)
        row_bytes.append(encoded)
        _write_json(claims_root / f"{run_id}.done.json", {
            "schema_version": SCHEMA_VERSION,
            "record_type": "lb2_pre_freeze_rehearsal_done",
            "schedule_id": schedule["schedule_id"],
            "run_id": run_id,
            "row_sha256": sha256_bytes(canonical_json_bytes(row)),
        })
    _write_exclusive(runs_path, b"".join(row_bytes))


def _load_rows(path: Path) -> tuple[list[dict[str, Any]], bytes]:
    data = _read_regular(path, "rehearsal runs JSONL", owner_only=True)
    lines = data.splitlines(keepends=True)
    if len(lines) != JOB_COUNT:
        raise RehearsalError("rehearsal runs JSONL must contain exactly 60 rows")
    rows: list[dict[str, Any]] = []
    for index, line in enumerate(lines, 1):
        if not line.endswith(b"\n") or not line[:-1]:
            raise RehearsalError(f"rehearsal row {index} lacks exact final LF")
        row = _decode_object(line, f"rehearsal row {index}")
        rows.append(row)
    return rows, data


def _inventory(root: Path, *, exclude_receipt: bool = False) -> list[dict[str, Any]]:
    root = _require_owner_directory(root, "rehearsal bundle root")
    entries: list[dict[str, Any]] = []
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        directories.sort()
        files.sort()
        current_path = Path(current)
        for name in list(directories):
            path = current_path / name
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                raise RehearsalError(f"bundle contains an unsafe directory entry: {path}")
            if os.name == "posix" and _mode(metadata) != 0o700:
                raise RehearsalError(f"bundle directory mode is not 0700: {path}")
            entries.append({
                "path": path.relative_to(root).as_posix(),
                "type": "directory",
                "mode": _mode(metadata),
            })
        for name in files:
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            if exclude_receipt and relative == FINAL_RECEIPT_NAME:
                continue
            data = _read_regular(path, f"bundle inventory {relative}", owner_only=True)
            entries.append({
                "path": relative,
                "type": "file",
                "mode": _mode(path.stat()),
                "sha256": sha256_bytes(data),
                "bytes": len(data),
            })
    entries.sort(key=lambda item: item["path"])
    return entries


def _inventory_slice(inventory: list[dict[str, Any]], prefix: str) -> dict[str, Any]:
    selected = [item for item in inventory if item["path"] == prefix or item["path"].startswith(prefix + "/")]
    return {
        "prefix": prefix,
        "entry_count": len(selected),
        "inventory_sha256": sha256_bytes(canonical_json_bytes(selected)),
    }


def terminal_validate(
    *, manifest_path: Path, schedule_path: Path, runs_path: Path,
    claims_root: Path, artifacts_root: Path,
) -> dict[str, Any]:
    """No-gold terminal validator over the complete fixed schedule and artifacts."""
    manifest, fixtures = _load_public(manifest_path)
    schedule, schedule_bytes = _read_object(schedule_path, "rehearsal schedule")
    jobs = _validate_schedule(schedule, manifest, fixtures)
    rows, runs_bytes = _load_rows(runs_path)
    claims = _require_owner_directory(claims_root, "rehearsal claims root")
    artifacts = _require_owner_directory(artifacts_root, "rehearsal artifacts root")
    expected_claim_names = {
        name for job in jobs for name in (
            f"{job['run_id']}.claim.json", f"{job['run_id']}.done.json"
        )
    }
    if {item.name for item in os.scandir(claims)} != expected_claim_names:
        raise RehearsalError("rehearsal claims inventory is not the exact 60 claim/60 done set")
    if {item.name for item in os.scandir(artifacts)} != {job["run_id"] for job in jobs}:
        raise RehearsalError("rehearsal artifact inventory is not exactly 60 run directories")
    trace_counts: Counter[str] = Counter()
    seen_runs: set[str] = set()
    row_shape = {
        "schema_version", "record_type", "suite_id", "benchmark_result", "schedule_id",
        "run_id", "execution_ordinal", "fixture_id", "payload_sha256", "arm", "repetition",
        "offline", "oauth_used", "inference_used", "execution_success", "scoring_status",
        "response", "artifact",
    }
    for index, (row, job) in enumerate(zip(rows, jobs), 1):
        if set(row) != row_shape:
            raise RehearsalError(f"rehearsal row {index} shape is invalid")
        expected_literals = {
            "schema_version": SCHEMA_VERSION,
            "record_type": "lb2_pre_freeze_rehearsal_run",
            "suite_id": SUITE_ID,
            "benchmark_result": False,
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "execution_ordinal": index,
            "fixture_id": job["fixture_id"],
            "payload_sha256": job["payload_sha256"],
            "arm": job["arm"],
            "repetition": 1,
            "offline": True,
            "oauth_used": False,
            "inference_used": False,
            "execution_success": True,
            "scoring_status": "rehearsal_deferred",
        }
        if any(row.get(key) != value for key, value in expected_literals.items()):
            raise RehearsalError(f"rehearsal row {index} job/literal binding drifted")
        if row["run_id"] in seen_runs:
            raise RehearsalError(f"rehearsal row {index} duplicates a run_id")
        seen_runs.add(row["run_id"])
        fixture = fixtures[job["fixture_id"]]
        if row["response"] != _response_for(job, fixture):
            raise RehearsalError(f"rehearsal row {index} deterministic response drifted")
        claim, _ = _read_object(claims / f"{job['run_id']}.claim.json", f"rehearsal claim {index}")
        done, _ = _read_object(claims / f"{job['run_id']}.done.json", f"rehearsal done {index}")
        if claim != {
            "schema_version": SCHEMA_VERSION,
            "record_type": "lb2_pre_freeze_rehearsal_claim",
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "ordinal": index,
        }:
            raise RehearsalError(f"rehearsal claim {index} binding drifted")
        if done != {
            "schema_version": SCHEMA_VERSION,
            "record_type": "lb2_pre_freeze_rehearsal_done",
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "row_sha256": sha256_bytes(canonical_json_bytes(row)),
        }:
            raise RehearsalError(f"rehearsal done {index} row binding drifted")
        run_dir = _require_owner_directory(artifacts / job["run_id"], f"rehearsal artifact {index}")
        expected_artifact_names = {"response.txt"}
        if job["arm"] == "jcode-azdaja":
            expected_artifact_names.add("model-trace.jsonl")
        if {item.name for item in os.scandir(run_dir)} != expected_artifact_names:
            raise RehearsalError(f"rehearsal artifact {index} file inventory drifted")
        response_bytes = _read_regular(run_dir / "response.txt", f"rehearsal response artifact {index}", owner_only=True)
        artifact = row["artifact"]
        if not isinstance(artifact, dict) or set(artifact) != {
            "directory", "response_sha256", "response_bytes", "model_trace_kind", "model_trace_sha256"
        } or artifact["directory"] != job["run_id"] or artifact["response_sha256"] != sha256_bytes(response_bytes) or artifact["response_bytes"] != len(response_bytes) or response_bytes != row["response"].encode("utf-8"):
            raise RehearsalError(f"rehearsal response artifact {index} binding drifted")
        if job["arm"] != "jcode-azdaja":
            if artifact["model_trace_kind"] is not None or artifact["model_trace_sha256"] is not None:
                raise RehearsalError(f"rehearsal control artifact {index} has model trace metadata")
            continue
        trace = _read_regular(run_dir / "model-trace.jsonl", f"rehearsal model trace {index}", owner_only=True)
        trace_sha = sha256_bytes(trace)
        expected_kind = "v43_success" if fixture["ordinal"] % 2 else "v43_transient_timeout_retry"
        expected_sha = SUCCESS_TRACE_SHA256 if expected_kind == "v43_success" else RETRY_TRACE_SHA256
        if artifact["model_trace_kind"] != expected_kind or artifact["model_trace_sha256"] != trace_sha or trace_sha != expected_sha:
            raise RehearsalError(f"rehearsal model trace {index} exact sample binding drifted")
        try:
            routes = SCORE._category_routes_from_retained_trace(trace, index, SCORE.MODEL)
        except SCORE.ScoreError as exc:
            raise RehearsalError(f"production trace validator rejected rehearsal artifact {index}: {exc}") from exc
        if expected_kind == "v43_success" and len(routes) != 1:
            raise RehearsalError(f"rehearsal success trace {index} lost its route")
        if expected_kind != "v43_success" and routes != []:
            raise RehearsalError(f"rehearsal transient retry trace {index} asserted a route")
        trace_counts[expected_kind] += 1
    if trace_counts != Counter({"v43_success": 10, "v43_transient_timeout_retry": 10}):
        raise RehearsalError(f"rehearsal trace coverage drifted: {dict(trace_counts)}")
    _validate_committed_trace_authority()
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_terminal_validation",
        "suite_id": SUITE_ID,
        "benchmark_result": False,
        "gold_path_parameter": False,
        "gold_opened": False,
        "terminal_validated": True,
        "schedule_id": schedule["schedule_id"],
        "manifest_sha256": sha256_bytes(canonical_json_file_bytes(manifest)),
        "schedule_sha256": sha256_bytes(schedule_bytes),
        "runs_sha256": sha256_bytes(runs_bytes),
        "fixture_count": FIXTURE_COUNT,
        "job_count": JOB_COUNT,
        "row_count": len(rows),
        "claim_count": JOB_COUNT,
        "done_count": JOB_COUNT,
        "artifact_run_count": JOB_COUNT,
        "trace_sample_counts": dict(sorted(trace_counts.items())),
        "trace_validator": {
            "authority": "score.py:_category_routes_from_retained_trace",
            "known_fields": list(SCORE.MODEL_TRACE_FIELDS),
            "duplicate_free_compact_any_known_field_order": True,
            "v43_success_sha256": SUCCESS_TRACE_SHA256,
            "v43_transient_timeout_retry_sha256": RETRY_TRACE_SHA256,
        },
    }


def _load_gold_after_terminal(
    gold_path: Path, manifest: dict[str, Any], fixtures: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, str]]:
    private = _require_owner_directory(gold_path.parent, "rehearsal private gold root")
    if {item.name for item in os.scandir(private)} != {"gold.json"}:
        raise RehearsalError("rehearsal private gold inventory is not exact")
    gold, gold_bytes = _read_object(gold_path, "rehearsal synthetic gold")
    if sha256_bytes(gold_bytes) != manifest["gold_sha256"]:
        raise RehearsalError("rehearsal public/gold exact-file commitment drifted")
    if set(gold) != {
        "schema_version", "record_type", "suite_id", "synthetic", "benchmark_result",
        "manifest_identity_sha256", "fixtures",
    } or gold.get("record_type") != "lb2_pre_freeze_rehearsal_synthetic_gold" or gold.get("suite_id") != SUITE_ID or gold.get("synthetic") is not True or gold.get("benchmark_result") is not False or gold.get("schema_version") != SCHEMA_VERSION:
        raise RehearsalError("rehearsal synthetic gold shape/literals drifted")
    if gold["manifest_identity_sha256"] != _manifest_identity(manifest):
        raise RehearsalError("rehearsal synthetic gold/public identity edge drifted")
    entries = gold["fixtures"]
    if not isinstance(entries, list) or len(entries) != FIXTURE_COUNT:
        raise RehearsalError("rehearsal synthetic gold fixture count drifted")
    answers: dict[str, str] = {}
    for index, item in enumerate(entries):
        fixture_id = _fixture_id(index)
        if item != {
            "id": fixture_id,
            "answer": _synthetic_answer(index),
            "payload_sha256": fixtures[fixture_id]["payload_sha256"],
        } or fixture_id in answers:
            raise RehearsalError(f"rehearsal synthetic gold fixture {index + 1} drifted")
        answers[fixture_id] = item["answer"]
    return gold, answers


def build_report_after_terminal(
    *, terminal_path: Path, manifest_path: Path, schedule_path: Path,
    runs_path: Path, claims_root: Path, artifacts_root: Path, gold_path: Path,
) -> dict[str, Any]:
    # Revalidate the full no-gold terminal bundle first. Only after exact equality
    # with the committed terminal record is the synthetic gold pathname opened.
    terminal, terminal_bytes = _read_object(terminal_path, "rehearsal terminal validation")
    rebuilt_terminal = terminal_validate(
        manifest_path=manifest_path, schedule_path=schedule_path, runs_path=runs_path,
        claims_root=claims_root, artifacts_root=artifacts_root,
    )
    if terminal != rebuilt_terminal:
        raise RehearsalError("rehearsal terminal validation receipt drifted")
    manifest, fixtures = _load_public(manifest_path)
    schedule, _ = _read_object(schedule_path, "rehearsal schedule")
    jobs = _validate_schedule(schedule, manifest, fixtures)
    rows, runs_bytes = _load_rows(runs_path)
    gold, answers = _load_gold_after_terminal(gold_path, manifest, fixtures)
    score_rows: list[dict[str, Any]] = []
    per_arm: dict[str, dict[str, int]] = {
        arm: {"official_correct_n": 0, "strict_correct_n": 0, "derived_correct_n": 0}
        for arm in ARMS
    }
    derived_sources: Counter[str] = Counter()
    for row, job in zip(rows, jobs):
        answer = answers[job["fixture_id"]]
        response = row["response"]
        official_prediction = SCORE.official_extract_answer(response)
        strict_prediction = SCORE.strict_extract_answer(response)
        derived_prediction, derived_source = SCORE.derived_envelope_extract_answer(response)
        diagnostics = SCORE.official_answer_diagnostics(response)
        cell = {
            "fixture_id": job["fixture_id"],
            "arm": job["arm"],
            "answer": answer,
            "response": response,
            "official_prediction": official_prediction,
            "strict_prediction": strict_prediction,
            "derived_prediction": derived_prediction,
            "derived_source": derived_source,
            "official_correct": official_prediction == answer,
            "strict_correct": strict_prediction == answer,
            "derived_correct": derived_prediction == answer,
            "official_diagnostics": diagnostics,
        }
        score_rows.append(cell)
        aggregate = per_arm[job["arm"]]
        aggregate["official_correct_n"] += int(cell["official_correct"])
        aggregate["strict_correct_n"] += int(cell["strict_correct"])
        aggregate["derived_correct_n"] += int(cell["derived_correct"])
        derived_sources[str(derived_source)] += 1
    arm_report = {
        arm: {
            **counts,
            "fixed_denominator_n": FIXTURE_COUNT,
            "official_accuracy": counts["official_correct_n"] / FIXTURE_COUNT,
            "strict_accuracy": counts["strict_correct_n"] / FIXTURE_COUNT,
            "derived_accuracy": counts["derived_correct_n"] / FIXTURE_COUNT,
        }
        for arm, counts in per_arm.items()
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_private_report",
        "suite_id": SUITE_ID,
        "synthetic": True,
        "benchmark_result": False,
        "disclosure": (
            "Deterministic offline pipeline dress rehearsal only; no OAuth, model inference, "
            "LongBench observation, candidate result, benchmark claim, or leaderboard claim."
        ),
        "integrity": {
            "terminal_validated_before_gold_open": True,
            "terminal_validation_sha256": sha256_bytes(terminal_bytes),
            "gold_sha256": sha256_bytes(canonical_json_file_bytes(gold)),
            "runs_sha256": sha256_bytes(runs_bytes),
            "schedule_id": schedule["schedule_id"],
            "fixture_count": FIXTURE_COUNT,
            "row_count": JOB_COUNT,
            "claim_count": JOB_COUNT,
            "done_count": JOB_COUNT,
            "artifact_run_count": JOB_COUNT,
            "actual_score_extractors": [
                "official_extract_answer", "strict_extract_answer",
                "derived_envelope_extract_answer", "official_answer_diagnostics",
            ],
        },
        "arms": arm_report,
        "derived_source_counts": dict(sorted(derived_sources.items())),
        "scores": score_rows,
    }


def _contract_identity() -> dict[str, Any]:
    return {
        "implementation": _file_identity(Path(__file__), "rehearsal implementation"),
        "score_validator": _file_identity(PRODUCTION_VALIDATOR, "rehearsal score authority"),
        "retained_trace_samples": {
            "v43_success": _file_identity(SUCCESS_TRACE, "committed v43 success trace"),
            "v43_transient_timeout_retry": _file_identity(RETRY_TRACE, "committed v43 retry trace"),
        },
    }


def _counts_from_inventory(inventory: list[dict[str, Any]]) -> dict[str, int]:
    paths = {item["path"] for item in inventory}
    return {
        "rows": JOB_COUNT,
        "claims": sum(path.startswith("claims/") and path.endswith(".claim.json") for path in paths),
        "done": sum(path.startswith("claims/") and path.endswith(".done.json") for path in paths),
        "artifact_runs": sum(
            item["type"] == "directory" and item["path"].count("/") == 1
            and item["path"].startswith("artifacts/")
            for item in inventory
        ),
    }


def build_final_receipt(bundle: Path, target: dict[str, Any]) -> dict[str, Any]:
    inventory = _inventory(bundle, exclude_receipt=True)
    if {item.name for item in os.scandir(bundle)} != ROOT_NAMES_WITHOUT_RECEIPT:
        raise RehearsalError("receipt must be published only after the exact complete pre-receipt root")
    counts = _counts_from_inventory(inventory)
    if counts != {"rows": JOB_COUNT, "claims": JOB_COUNT, "done": JOB_COUNT, "artifact_runs": JOB_COUNT}:
        raise RehearsalError(f"pre-receipt bundle counts drifted: {counts}")
    inventories = {
        prefix: _inventory_slice(inventory, prefix)
        for prefix in (
            "public", "private", "schedule.json", "runs.jsonl", "claims", "artifacts",
            "terminal-validation.json", "report.json",
        )
    }
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_final_receipt",
        "suite_id": SUITE_ID,
        "benchmark_result": False,
        "published_last": True,
        "contract": {
            "fixture_count": FIXTURE_COUNT,
            "arms": list(ARMS),
            "job_count": JOB_COUNT,
            "seed": REHEARSAL_SEED,
            "timeout_seconds": REHEARSAL_TIMEOUT_SECONDS,
            "offline": True,
            "oauth": False,
            "inference": False,
            "run_gold_path_parameter": False,
            "production_fixture_count": PRODUCTION_FIXTURE_COUNT,
            "production_job_count": PRODUCTION_JOB_COUNT,
            "production_minimum_correct_n": PRODUCTION_MINIMUM_CORRECT_N,
        },
        "contract_identity": _contract_identity(),
        "bundle_root": str(_absolute(bundle)),
        "bundle_inventory": inventory,
        "bundle_inventory_sha256": sha256_bytes(canonical_json_bytes(inventory)),
        "inventories": inventories,
        "counts": counts,
        "target": copy.deepcopy(target),
        "target_sha256": target["target_sha256"],
    }
    receipt["receipt_id"] = sha256_bytes(canonical_json_bytes(receipt))
    return receipt


def receipt_binding(receipt_path: Path, receipt: dict[str, Any], receipt_bytes: bytes) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_binding",
        "path": str(_absolute(receipt_path)),
        "receipt_sha256": sha256_bytes(receipt_bytes),
        "receipt_id": receipt["receipt_id"],
        "bundle_inventory_sha256": receipt["bundle_inventory_sha256"],
        "target_sha256": receipt["target_sha256"],
        "suite_id": SUITE_ID,
    }


def verify_rehearsal_receipt(
    receipt_path: Path | str, *, expected_target: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Reopen and revalidate the complete bundle and every target identity."""
    receipt_path = _absolute(receipt_path)
    if receipt_path.name != FINAL_RECEIPT_NAME:
        raise RehearsalError(f"rehearsal receipt filename must be exactly {FINAL_RECEIPT_NAME}")
    bundle = _require_owner_directory(receipt_path.parent, "rehearsal bundle root")
    names = {item.name for item in os.scandir(bundle)}
    if names != ROOT_NAMES_WITHOUT_RECEIPT | {FINAL_RECEIPT_NAME}:
        raise RehearsalError("completed rehearsal bundle root inventory is not exact")
    receipt, receipt_bytes = _read_object(receipt_path, "pre-freeze rehearsal final receipt")
    expected_shape = {
        "schema_version", "record_type", "suite_id", "benchmark_result", "published_last",
        "contract", "contract_identity", "bundle_root", "bundle_inventory",
        "bundle_inventory_sha256", "inventories", "counts", "target", "target_sha256",
        "receipt_id",
    }
    if set(receipt) != expected_shape:
        raise RehearsalError("pre-freeze rehearsal final receipt shape is invalid")
    identity = copy.deepcopy(receipt)
    receipt_id = identity.pop("receipt_id")
    if not isinstance(receipt_id, str) or receipt_id != sha256_bytes(canonical_json_bytes(identity)):
        raise RehearsalError("pre-freeze rehearsal final receipt identity drifted")
    if receipt.get("schema_version") != SCHEMA_VERSION or receipt.get("record_type") != "lb2_pre_freeze_rehearsal_final_receipt" or receipt.get("suite_id") != SUITE_ID or receipt.get("benchmark_result") is not False or receipt.get("published_last") is not True or receipt.get("bundle_root") != str(bundle):
        raise RehearsalError("pre-freeze rehearsal final receipt literals/root drifted")
    expected_contract = {
        "fixture_count": FIXTURE_COUNT, "arms": list(ARMS), "job_count": JOB_COUNT,
        "seed": REHEARSAL_SEED, "timeout_seconds": REHEARSAL_TIMEOUT_SECONDS,
        "offline": True, "oauth": False, "inference": False,
        "run_gold_path_parameter": False,
        "production_fixture_count": PRODUCTION_FIXTURE_COUNT,
        "production_job_count": PRODUCTION_JOB_COUNT,
        "production_minimum_correct_n": PRODUCTION_MINIMUM_CORRECT_N,
    }
    if receipt["contract"] != expected_contract:
        raise RehearsalError("pre-freeze rehearsal v1 contract drifted")
    if receipt["contract_identity"] != _contract_identity():
        raise RehearsalError("pre-freeze rehearsal implementation/authority identities drifted")
    target = _reopen_target(receipt["target"])
    if receipt["target_sha256"] != target["target_sha256"]:
        raise RehearsalError("pre-freeze rehearsal target aggregate binding drifted")
    if expected_target is not None and target != expected_target:
        raise RehearsalError("rehearsal receipt does not bind the requested production target")
    inventory = _inventory(bundle, exclude_receipt=True)
    if receipt["bundle_inventory"] != inventory or receipt["bundle_inventory_sha256"] != sha256_bytes(canonical_json_bytes(inventory)):
        raise RehearsalError("pre-freeze rehearsal complete bundle inventory drifted")
    expected_inventories = {
        prefix: _inventory_slice(inventory, prefix)
        for prefix in (
            "public", "private", "schedule.json", "runs.jsonl", "claims", "artifacts",
            "terminal-validation.json", "report.json",
        )
    }
    if receipt["inventories"] != expected_inventories or receipt["counts"] != _counts_from_inventory(inventory):
        raise RehearsalError("pre-freeze rehearsal sub-inventories/counts drifted")
    if receipt["counts"] != {"rows": JOB_COUNT, "claims": JOB_COUNT, "done": JOB_COUNT, "artifact_runs": JOB_COUNT}:
        raise RehearsalError("pre-freeze rehearsal exact cardinalities drifted")
    manifest_path = bundle / "public" / "manifest.json"
    schedule_path = bundle / "schedule.json"
    runs_path = bundle / "runs.jsonl"
    claims_root = bundle / "claims"
    artifacts_root = bundle / "artifacts"
    terminal_path = bundle / "terminal-validation.json"
    gold_path = bundle / "private" / "gold.json"
    report_path = bundle / "report.json"
    terminal, _ = _read_object(terminal_path, "rehearsal terminal validation")
    if terminal != terminal_validate(
        manifest_path=manifest_path, schedule_path=schedule_path, runs_path=runs_path,
        claims_root=claims_root, artifacts_root=artifacts_root,
    ):
        raise RehearsalError("pre-freeze rehearsal terminal receipt failed replay")
    report, _ = _read_object(report_path, "rehearsal private report")
    rebuilt_report = build_report_after_terminal(
        terminal_path=terminal_path, manifest_path=manifest_path,
        schedule_path=schedule_path, runs_path=runs_path, claims_root=claims_root,
        artifacts_root=artifacts_root, gold_path=gold_path,
    )
    if report != rebuilt_report:
        raise RehearsalError("pre-freeze rehearsal private report failed replay")
    return receipt_binding(receipt_path, receipt, receipt_bytes)


def load_bound_target(
    receipt_path: Path | str, binding: dict[str, Any]
) -> dict[str, Any]:
    """Reopen a just-verified receipt and retain its exact byte binding."""
    receipt, receipt_bytes = _read_object(
        _absolute(receipt_path), "schedule-bound rehearsal receipt"
    )
    if (
        sha256_bytes(receipt_bytes) != binding.get("receipt_sha256")
        or receipt.get("receipt_id") != binding.get("receipt_id")
        or receipt.get("target_sha256") != binding.get("target_sha256")
    ):
        raise RehearsalError("schedule-bound rehearsal receipt changed after verification")
    target = receipt.get("target")
    if not isinstance(target, dict):
        raise RehearsalError("schedule-bound rehearsal target is malformed")
    return target


def assert_schedule_target_binding(
    schedule: dict[str, Any], target: dict[str, Any], binding: dict[str, Any],
) -> None:
    """Bind a verified source rehearsal target to the frozen production schedule."""
    configuration = schedule.get("configuration")
    suite = schedule.get("suite")
    if not isinstance(configuration, dict) or not isinstance(suite, dict):
        raise RehearsalError("production schedule is malformed for rehearsal binding")
    if configuration.get("pre_freeze_rehearsal") != binding:
        raise RehearsalError("production schedule does not contain the verified rehearsal binding")
    expected_config = target["configuration"]
    if (
        suite.get("suite_id") != expected_config["suite_id"]
        or suite.get("manifest_sha256") != target["manifest"]["sha256"]
        or len(suite.get("fixtures", [])) != expected_config["fixture_count"]
        or len(schedule.get("jobs", [])) != expected_config["scheduled_jobs"]
        or configuration.get("model") != expected_config["model"]
        or configuration.get("reasoning") != expected_config["reasoning"]
        or configuration.get("arms") != expected_config["arms"]
        or configuration.get("repetitions") != expected_config["repetitions"]
        or configuration.get("seed") != expected_config["seed"]
        or configuration.get("timeout_seconds") != expected_config["timeout_seconds"]
        or configuration.get("derived_gate", {}).get("minimum_correct_n")
        != expected_config["minimum_correct_n"]
    ):
        raise RehearsalError("production schedule configuration/manifest differs from rehearsal target")
    pairs = (
        (configuration.get("candidate"), target["candidate"]),
        (configuration.get("controller"), target["controller"]),
    )
    for scheduled, source in pairs:
        if not isinstance(scheduled, dict) or any(
            scheduled.get(key) != source.get(key) for key in ("sha256", "bytes")
        ):
            raise RehearsalError("production frozen candidate/controller differs from rehearsal target")
    runtime = configuration.get("runtime_closure", {})
    for name in ("validator", "adapter"):
        scheduled = runtime.get(name, {})
        source = target[name]
        if any(scheduled.get(key) != source.get(key) for key in ("sha256", "bytes")):
            raise RehearsalError(f"production frozen {name} differs from rehearsal target")
    for name in ("jcode", "azdaja", "prime-agent"):
        scheduled = configuration.get("executables", {}).get(name, {})
        source = target["executables"][name]
        if any(scheduled.get(key) != source.get(key) for key in ("sha256", "bytes")):
            raise RehearsalError(f"production frozen {name} executable differs from rehearsal target")


def run_rehearsal(args: argparse.Namespace) -> dict[str, Any]:
    bundle = _absolute(args.bundle)
    parent = _require_owner_directory(bundle.parent, "rehearsal bundle parent")
    if bundle.exists() or bundle.is_symlink():
        raise RehearsalError("--bundle must be a fresh path")
    target = build_target_identity(
        manifest=args.target_manifest, candidate=args.target_candidate,
        jcode=args.target_jcode, prime_agent=args.target_prime_agent,
        seed=args.target_seed, timeout=args.target_timeout,
    )
    del parent
    _mkdir(bundle)
    manifest_path, gold_path, manifest = generate_synthetic_phase(bundle)
    schedule = build_schedule(manifest, target)
    schedule_path = bundle / "schedule.json"
    _write_json(schedule_path, schedule)
    runs_path = bundle / "runs.jsonl"
    claims_root = bundle / "claims"
    artifacts_root = bundle / "artifacts"
    # Deliberately no gold argument at the offline execution boundary.
    run_offline_phase(
        manifest_path=manifest_path, schedule_path=schedule_path, runs_path=runs_path,
        claims_root=claims_root, artifacts_root=artifacts_root,
    )
    terminal = terminal_validate(
        manifest_path=manifest_path, schedule_path=schedule_path, runs_path=runs_path,
        claims_root=claims_root, artifacts_root=artifacts_root,
    )
    terminal_path = bundle / "terminal-validation.json"
    _write_json(terminal_path, terminal)
    report = build_report_after_terminal(
        terminal_path=terminal_path, manifest_path=manifest_path,
        schedule_path=schedule_path, runs_path=runs_path, claims_root=claims_root,
        artifacts_root=artifacts_root, gold_path=gold_path,
    )
    _write_json(bundle / "report.json", report)
    # The final receipt is constructed from every preceding inventory and is
    # the last path published into the exact bundle root.
    receipt = build_final_receipt(bundle, target)
    receipt_path = bundle / FINAL_RECEIPT_NAME
    _write_json(receipt_path, receipt)
    return verify_rehearsal_receipt(receipt_path, expected_target=target)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="create and verify a fresh offline v1 rehearsal bundle")
    run.add_argument("--bundle", required=True, type=Path)
    run.add_argument("--target-manifest", required=True, type=Path)
    run.add_argument("--target-candidate", required=True, type=Path)
    run.add_argument("--target-jcode", required=True)
    run.add_argument("--target-prime-agent", required=True)
    run.add_argument("--target-seed", type=int, default=20260813)
    run.add_argument("--target-timeout", type=int, default=1800)
    verify = sub.add_parser("verify", help="reopen and fully verify a completed bundle and target")
    verify.add_argument("--receipt", required=True, type=Path)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "run":
            binding = run_rehearsal(args)
        else:
            binding = verify_rehearsal_receipt(args.receipt)
    except (RehearsalError, SCORE.ScoreError, OSError, ValueError) as exc:
        print(f"pre-freeze rehearsal error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(binding, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
