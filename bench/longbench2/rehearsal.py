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
RUN = _load_python("azdaja_lb2_run_for_pre_freeze_rehearsal", PRODUCTION_CONTROLLER)
ADAPTER = _load_python("azdaja_oolong_for_pre_freeze_rehearsal", PRODUCTION_ADAPTER)
ADAPTER.MODEL = SCORE.MODEL
ADAPTER.REASONING = SCORE.REASONING

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
EXPECTED_LABELS = tuple("ABCD"[index % 4] for index in range(FIXTURE_COUNT))
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
    """Capture the complete source/runtime closure a fresh production freeze consumes."""
    manifest_identity = _file_identity(Path(manifest), "target production manifest")
    candidate_identity = _candidate_identity(Path(candidate))
    jcode_path = _resolve_executable(jcode, "jcode")
    prime_path = _resolve_executable(prime_agent, "prime-agent")
    node_path = _resolve_executable("node", "Node")
    azdaja_path = Path(candidate_identity["path"]) / "azdaja"
    home = os.environ.get("HOME")
    if not home:
        raise RehearsalError("HOME is required to bind the Prime kernel closure")
    kernel_root = _absolute(Path(home) / ".prime" / "agent" / "kernel-venv")
    kernel_python_path = kernel_root / "bin" / "python"
    if not kernel_python_path.exists():
        raise RehearsalError("Prime kernel environment is unavailable for target binding")
    runtime_python_root = kernel_python_path.resolve(strict=True).parents[1]
    try:
        package_root, cli_relative = RUN.find_prime_package_root(prime_path)
        prime_inventory = RUN.recursive_inventory(package_root, hash_files=True)
        kernel_inventory = RUN.ambient_recursive_inventory(kernel_root)
        runtime_inventory = RUN.ambient_recursive_inventory(runtime_python_root)
        executables = {
            "jcode": RUN._version_identity(jcode_path, "target jcode"),
            "azdaja": RUN._version_identity(azdaja_path, "target azdaja"),
            "prime-agent": RUN._version_identity(
                prime_path, "target prime-agent", path_prefix=node_path.parent
            ),
        }
        node = RUN._version_identity(node_path, "target Node")
        kernel_python = RUN._version_identity(
            kernel_python_path.resolve(strict=True), "target Prime kernel Python"
        )
    except RUN.BenchError as exc:
        raise RehearsalError(f"cannot bind complete production runtime target: {exc}") from exc
    runtime_closure = {
        "adapter": _file_identity(PRODUCTION_ADAPTER, "target production adapter"),
        "validator": _file_identity(PRODUCTION_VALIDATOR, "target production validator"),
        "prime_package": {
            "snapshot_root": str(package_root),
            "inventory_sha256": sha256_bytes(canonical_json_bytes(prime_inventory)),
            "entry_count": len(prime_inventory),
            "cli_relative": cli_relative.as_posix(),
        },
        "node": node,
        "kernel_python": kernel_python,
        "kernel_launcher": {
            "path": str(kernel_python_path),
            "target": (
                os.readlink(kernel_python_path)
                if kernel_python_path.is_symlink() and not os.path.isabs(os.readlink(kernel_python_path))
                else "bin/python"
            ),
            "resolved_path": str(kernel_python_path.resolve(strict=True)),
        },
        "kernel_environment": {
            "root": str(kernel_root),
            "inventory_sha256": sha256_bytes(canonical_json_bytes(kernel_inventory)),
            "entry_count": len(kernel_inventory),
        },
        "runtime_python": {
            "snapshot_root": str(runtime_python_root),
            "inventory_sha256": sha256_bytes(canonical_json_bytes(runtime_inventory)),
            "entry_count": len(runtime_inventory),
        },
        "ambient_closure_disclosure": SCORE.AMBIENT_CLOSURE_DISCLOSURE,
    }
    target = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_target",
        "manifest": manifest_identity,
        "candidate": candidate_identity,
        "controller": _file_identity(PRODUCTION_CONTROLLER, "target production controller"),
        "rehearsal": _file_identity(Path(__file__), "target rehearsal controller"),
        "validator": runtime_closure["validator"],
        "adapter": runtime_closure["adapter"],
        "executables": executables,
        "runtime_closure": runtime_closure,
        "config": _file_identity(
            Path(candidate_identity["path"]) / "config.toml", "target candidate config"
        ),
        "configuration": production_configuration(seed=seed, timeout=timeout),
    }
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
    return EXPECTED_LABELS[index]


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
            "domain": "Synthetic",
            "sub_domain": "Offline pipeline",
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
            "id", "ordinal", "payload", "payload_sha256", "payload_bytes",
            "domain", "sub_domain"
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
            "domain": "Synthetic",
            "sub_domain": "Offline pipeline",
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
        by_id[fixture_id] = {
            **item, "payload_object": payload, "_payload_bytes_captured": data,
            "fixture_id": fixture_id,
        }
    if {item.name for item in os.scandir(payloads)} != expected_names:
        raise RehearsalError("rehearsal payload inventory is not exact")
    if manifest_bytes != canonical_json_file_bytes(manifest):
        raise RehearsalError("rehearsal manifest bytes changed")
    return manifest, by_id


def _captured_suite(
    manifest_path: Path, manifest: dict[str, Any], fixtures: dict[str, dict[str, Any]]
) -> Any:
    captured = tuple(
        RUN.CapturedFixture(
            fixture_id=item["id"], entry=fixtures[item["id"]],
            payload=fixtures[item["id"]]["payload_object"],
            payload_bytes=fixtures[item["id"]]["_payload_bytes_captured"],
        )
        for item in manifest["fixtures"]
    )
    return RUN.CapturedSuite(
        manifest_path=manifest_path, public_root=manifest_path.parent,
        manifest=manifest, manifest_bytes=canonical_json_file_bytes(manifest),
        manifest_sha256=sha256_bytes(canonical_json_file_bytes(manifest)),
        fixtures=captured, notice_bytes={},
    )


def build_schedule(
    manifest_path: Path, manifest: dict[str, Any], fixtures: dict[str, dict[str, Any]],
    target: dict[str, Any],
) -> dict[str, Any]:
    """Fixed wrapper over the production schedule constructor."""
    suite = _captured_suite(manifest_path, manifest, fixtures)
    try:
        candidate = copy.deepcopy(target["candidate"])
        candidate.pop("path", None)
        return RUN.build_schedule(
            suite, seed=REHEARSAL_SEED, timeout=REHEARSAL_TIMEOUT_SECONDS,
            candidate=candidate,
            controller=copy.deepcopy(target["controller"]),
            executables=copy.deepcopy(target["executables"]),
            runtime_closure=copy.deepcopy(target["runtime_closure"]),
            profile=SCORE.REHEARSAL_PROFILE,
        )
    except (RUN.BenchError, SCORE.ScoreError, KeyError) as exc:
        raise RehearsalError(f"production schedule helper refused rehearsal: {exc}") from exc


def _validate_schedule(
    schedule: dict[str, Any], manifest_path: Path, manifest: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    try:
        jobs, arms = SCORE.validate_schedule(
            copy.deepcopy(schedule), manifest_path, fixtures,
            manifest_sha256=sha256_bytes(canonical_json_file_bytes(manifest)),
            profile=SCORE.REHEARSAL_PROFILE,
        )
    except SCORE.ScoreError as exc:
        raise RehearsalError(f"shared schedule validator refused rehearsal: {exc}") from exc
    if len(jobs) != JOB_COUNT or arms != ARMS:
        raise RehearsalError("rehearsal schedule is not the exact fixed 20 x 3 grid")
    return jobs


def _response_for(job: dict[str, Any], fixture: dict[str, Any]) -> str:
    # Independent fixed response vector. Gold is not passed to or opened by run phase.
    answer = EXPECTED_LABELS[fixture["ordinal"] - 1]
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
    # The actual adapter parsers and scorer parser must agree on these exact raw bytes.
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        success_path = Path(directory) / "success.jsonl"
        retry_path = Path(directory) / "retry.jsonl"
        success_path.write_bytes(success)
        retry_path.write_bytes(retry)
        adapter_success = ADAPTER.parse_azdaja_route_evidence(success_path)
        adapter_retry = ADAPTER.parse_azdaja_route_evidence(retry_path)
        usage_success = ADAPTER.parse_azdaja_usage(success_path)
        usage_retry = ADAPTER.parse_azdaja_usage(retry_path)
    scorer_success = SCORE._category_routes_from_retained_trace(success, 1, SCORE.MODEL)
    scorer_retry = SCORE._category_routes_from_retained_trace(retry, 1, SCORE.MODEL)
    if (
        not isinstance(adapter_success, dict)
        or adapter_success.get("route_rows") != [
            {key: row[key] for key in ("depth", "category", "provider", "model")}
            for row in scorer_success
        ]
        or usage_success is None
        or not isinstance(adapter_retry, dict)
        or adapter_retry.get("route_rows") != []
        or usage_retry is not None
        or scorer_retry != []
    ):
        raise RehearsalError("OOLONG adapter and production scorer disagree on actual v43 trace bytes")
    return success, retry


def _root_trace(job: dict[str, Any]) -> bytes:
    request_id = json.dumps("rehearsal-" + job["run_id"][:12])
    model = json.dumps(SCORE.MODEL)
    request = "synthetic offline root request without fixture context"
    return (
        f"\n=== root request begin request_id={request_id} model={model} request_chars={len(request)} ===\n"
        f"{request}\n=== root request end request_id={request_id} ===\n"
        f"=== turn 0 request_id={request_id} category=turn outcome=succeeded provider=\"OpenAI OAuth\" "
        f"model={model} input=1 output=1 cache_read=0 latency_ms=1 ===\n"
    ).encode()


def _artifact_receipt(path: Path, data: bytes, *, exact: bool = False) -> dict[str, Any]:
    receipt = {
        "path": str(path.resolve()), "sha256": sha256_bytes(data), "bytes": len(data),
        "mode": "0600", "contains_private_raw_trajectory": False,
        "credential_redacted": True, "sensitivity": "committed synthetic rehearsal trajectory",
    }
    if exact:
        receipt.update({
            "source_sha256_before_redaction": sha256_bytes(data),
            "exact_text_preserved": True,
        })
    return receipt


def _auth(arm: str) -> dict[str, Any]:
    del arm
    return {
        "asserted": False, "offline_rehearsal": True,
        "oauth_used": False, "inference_used": False,
    }


def _adapter_row(
    job: dict[str, Any], fixture: dict[str, Any], response: str,
    run_dir: Path, model_trace: bytes | None,
) -> tuple[dict[str, Any], bytes, bytes | None]:
    arm = job["arm"]
    if arm == "jcode-native":
        stdout_object = {"type": "tokens", "input": 11, "output": 2,
                         "cache_read_input": 0, "cache_creation_input": 0}
        done = {"type": "done", "provider": "OpenAI", "model": SCORE.MODEL,
                "response": response}
        stdout = (json.dumps(stdout_object, separators=(",", ":")) + "\n" +
                  json.dumps(done, separators=(",", ":")) + "\n").encode()
        root_usage = ADAPTER.parse_jcode_usage(stdout.decode(), "")
        usage = ADAPTER.combine_usage(root_usage, None)
        evidence = ADAPTER.usage_evidence_assertion(
            usage, root_usage=root_usage, subusage_required=False, azdaja_usage=None
        )
        route = ADAPTER.runtime_assertion(arm, stdout.decode())
        azdaja_usage = None
        lifecycle = {"asserted": True, "requirement": "not applicable: non-product control arm"}
        root_trace = None
    elif arm == "prime-agent":
        event = {"type": "message_end", "message": {
            "role": "assistant", "provider": "openai-codex", "model": SCORE.MODEL,
            "api": "openai-codex-responses", "usage": {
                "input": 11, "output": 2, "cacheRead": 0, "cacheWrite": 0,
                "totalTokens": 13,
            }, "content": [{"type": "text", "text": response}],
        }}
        stdout = (json.dumps(event, separators=(",", ":")) + "\n").encode()
        root_usage = ADAPTER.sum_usage_fields(ADAPTER.json_objects(stdout.decode()), prime=True)
        usage = ADAPTER.combine_usage(root_usage, None)
        evidence = ADAPTER.usage_evidence_assertion(
            usage, root_usage=root_usage, subusage_required=False, azdaja_usage=None
        )
        route = ADAPTER.runtime_assertion(arm, stdout.decode())
        azdaja_usage = None
        lifecycle = {"asserted": True, "requirement": "not applicable: non-product control arm"}
        root_trace = None
    else:
        assert model_trace is not None
        model_path = run_dir / "azdaja-model-usage.jsonl"
        model_path.write_bytes(model_trace)
        model_path.chmod(0o600)
        route_evidence = ADAPTER.parse_azdaja_route_evidence(model_path)
        azdaja_usage = ADAPTER.parse_azdaja_usage(model_path)
        route = ADAPTER.runtime_assertion(
            arm, "", route_evidence, repair_model=SCORE.MODEL
        )
        root_usage = ADAPTER.usage_fields_from_azdaja(
            None if azdaja_usage is None else azdaja_usage.get("depth_usage", {}).get("0")
        )
        usage = ADAPTER.usage_fields_from_azdaja(azdaja_usage)
        evidence = ADAPTER.direct_solo_usage_evidence(usage, azdaja_usage)
        lifecycle = ADAPTER.direct_solo_lifecycle_assertion(
            exit_code=0, timed_out=False, response=response, trace_usage=route_evidence
        )
        root_trace = _root_trace(job)
        root_path = run_dir / "azdaja-solo-trace.log"
        root_path.write_bytes(root_trace)
        root_path.chmod(0o600)
        stdout = (json.dumps({"type": "result", "response": response},
                             separators=(",", ":")) + "\n").encode()
    stdout_path = run_dir / "stdout.ndjson"
    stderr_path = run_dir / "stderr.log"
    stdout_path.write_bytes(stdout); stdout_path.chmod(0o600)
    stderr_path.write_bytes(b""); stderr_path.chmod(0o600)
    artifacts = {
        "stdout": _artifact_receipt(stdout_path, stdout),
        "stderr": _artifact_receipt(stderr_path, b""),
    }
    if arm == "jcode-azdaja":
        assert model_trace is not None and root_trace is not None
        artifacts.update({
            "azdaja_model_trace": _artifact_receipt(
                run_dir / "azdaja-model-usage.jsonl", model_trace, exact=True
            ),
            "azdaja_solo_trace": _artifact_receipt(
                run_dir / "azdaja-solo-trace.log", root_trace, exact=True
            ),
        })
    retained = sorted(path.name for path in run_dir.iterdir())
    success = bool(route["asserted"] and lifecycle["asserted"] and evidence["valid"])
    adapter_row = {
        "execution_success": success, "latency_seconds": 0.01,
        "started_at_unix_s": 1_700_000_000 + job["ordinal"],
        "fresh_session": True, "serial": True,
        "hidden_context_and_official_question_identical_across_arms": True,
        "timed_out": False, "exit_code": 0, "auth_assertion": _auth(arm),
        "runtime_route_assertion": route,
        "product_lifecycle_assertion": lifecycle,
        "product_execution_asserted": lifecycle["asserted"],
        "trace_capture_assertion": {
            "asserted": True,
            "required": ["azdaja_model_trace", "azdaja_solo_trace"] if arm == "jcode-azdaja" else [],
            "captured": ["azdaja_model_trace", "azdaja_solo_trace"] if arm == "jcode-azdaja" else [],
            "missing": [],
        },
        "task_context_integrity": {
            "asserted_before": True, "asserted_after": True,
            "expected_sha256": job["payload_sha256"],
            "source_sha256_before": job["payload_sha256"],
            "source_sha256_after_copy": job["payload_sha256"],
            "staged_sha256_before": job["payload_sha256"],
            "staged_sha256_after": job["payload_sha256"],
            "source_sha256_after": job["payload_sha256"],
            "staged_mode_before": "0444", "staged_mode_after": "0444",
            "task_directory_single_file_before": True,
            "task_directory_single_file_after": True,
            "random_context_filename": True, "errors": [],
        },
        "tool_access_policy_assertion": {
            "asserted": True, "events_scanned": 0, "violations": [],
            "policy": "no network or external dataset access in executed tool command/code events",
            "enforcement": "post-hoc event detection only; not OS-level containment",
            "containment_asserted": False,
        },
        "credential_cleanup_assertion": {
            "asserted": True, "credential_homes_deleted": True,
            "retained_entries": retained, "retention_allowlist": retained,
        },
        "cleanup_errors": [], "root_usage": root_usage,
        "azdaja_model_usage": azdaja_usage, "efficiency_evidence": evidence,
        "usage": usage, "failure": (
            None if success else {
                "kind": "route_assertion",
                "message": "actual retry trace conservatively suppresses route assertion",
                "stderr": "",
            }
        ),
        "trajectory_artifacts": artifacts,
    }
    return adapter_row, stdout, root_trace


def run_offline_phase(
    *, manifest_path: Path, schedule_path: Path, runs_path: Path,
    claims_root: Path, artifacts_root: Path,
) -> None:
    """Shared production claim -> job/artifact -> append -> done pipeline; no gold arg."""
    manifest, fixtures = _load_public(manifest_path)
    schedule, _ = _read_object(schedule_path, "rehearsal schedule")
    jobs = _validate_schedule(schedule, manifest_path, manifest, fixtures)
    success_trace, retry_trace = _validate_committed_trace_authority()
    _mkdir(claims_root); claims = claims_root / schedule["schedule_id"]; _mkdir(claims)
    _mkdir(artifacts_root)
    claims_fd = os.open(claims, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    state = None
    try:
        for job in jobs:
            RUN.publish_job_claim_at(claims_fd, job, schedule, pid=os.getpid())
            run_dir = artifacts_root / f"r001-{job['ordinal']:03d}-{job['arm']}"
            _mkdir(run_dir)
            fixture = fixtures[job["fixture_id"]]
            response = _response_for(job, fixture)
            trace = None
            if job["arm"] == "jcode-azdaja":
                trace = success_trace if fixture["ordinal"] % 2 else retry_trace
            adapter_row, stdout, root_trace = _adapter_row(
                job, fixture, response, run_dir, trace
            )
            row = RUN.transform_adapter_row(
                adapter_row, job, schedule, raw_response=response,
                trajectory_artifacts=adapter_row["trajectory_artifacts"],
                stdout_bytes=stdout, root_trace_bytes=root_trace,
                public_context=fixture["payload_object"]["context"],
                profile=SCORE.REHEARSAL_PROFILE,
            )
            try:
                SCORE.validate_run_rows(
                    [row], [job], schedule, fixtures,
                    profile=SCORE.REHEARSAL_PROFILE,
                )
            except SCORE.ScoreError as exc:
                raise RehearsalError(f"shared live row validation failed: {exc}") from exc
            state = RUN.append_job_row(runs_path, row, expected_state=state)
            RUN.publish_job_done_at(claims_fd, job, schedule, row)
    finally:
        os.close(claims_fd)


def _load_rows(path: Path) -> tuple[list[dict[str, Any]], bytes]:
    data = _read_regular(path, "rehearsal runs JSONL", owner_only=True)
    try:
        rows = SCORE._load_run_rows_captured(data)
    except SCORE.ScoreError as exc:
        raise RehearsalError(f"shared row loader refused rehearsal: {exc}") from exc
    if len(rows) != JOB_COUNT:
        raise RehearsalError("rehearsal runs JSONL must contain exactly 60 rows")
    return rows, data


def _inventory(root: Path, *, exclude_receipt: bool = False) -> list[dict[str, Any]]:
    # Every verify performs this exact full-tree snapshot twice; SCORE's validators
    # separately use held O_NOFOLLOW descriptors for claims/artifacts.
    root = _require_owner_directory(root, "rehearsal bundle root")
    entries: list[dict[str, Any]] = []
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        directories.sort(); files.sort(); current_path = Path(current)
        for name in list(directories):
            path = current_path / name; metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                raise RehearsalError(f"bundle contains an unsafe directory entry: {path}")
            if os.name == "posix" and _mode(metadata) != 0o700:
                raise RehearsalError(f"bundle directory mode is not 0700: {path}")
            entries.append({"path": path.relative_to(root).as_posix(), "type": "directory", "mode": _mode(metadata)})
        for name in files:
            path = current_path / name; relative = path.relative_to(root).as_posix()
            if exclude_receipt and relative == FINAL_RECEIPT_NAME: continue
            data = _read_regular(path, f"bundle inventory {relative}", owner_only=True)
            entries.append({"path": relative, "type": "file", "mode": _mode(path.stat()),
                            "sha256": sha256_bytes(data), "bytes": len(data)})
    entries.sort(key=lambda item: item["path"])
    return entries


def _inventory_slice(inventory: list[dict[str, Any]], prefix: str) -> dict[str, Any]:
    selected = [item for item in inventory if item["path"] == prefix or item["path"].startswith(prefix + "/")]
    return {"prefix": prefix, "entry_count": len(selected),
            "inventory_sha256": sha256_bytes(canonical_json_bytes(selected))}


def terminal_validate(
    *, manifest_path: Path, schedule_path: Path, runs_path: Path,
    claims_root: Path, artifacts_root: Path,
) -> dict[str, Any]:
    """Shared exact-60 validators. Signature intentionally cannot receive gold."""
    manifest, fixtures = _load_public(manifest_path)
    schedule, schedule_bytes = _read_object(schedule_path, "rehearsal schedule")
    jobs = _validate_schedule(schedule, manifest_path, manifest, fixtures)
    rows, runs_bytes = _load_rows(runs_path)
    try:
        SCORE.validate_run_rows(
            rows, jobs, schedule, fixtures, profile=SCORE.REHEARSAL_PROFILE
        )
        SCORE.validate_claims(claims_root, rows, jobs, schedule)
        SCORE.validate_artifact_rows(artifacts_root, rows, jobs, fixtures)
    except SCORE.ScoreError as exc:
        raise RehearsalError(f"shared terminal pipeline validation failed: {exc}") from exc
    treatment = [row for row in rows if row["arm"] == "jcode-azdaja"]
    trace_counts = Counter({
        "v43_success": sum(row["runtime_route_assertion"]["asserted"] for row in treatment),
        "v43_transient_timeout_retry": sum(not row["runtime_route_assertion"]["asserted"] for row in treatment),
    })
    if len(rows) != JOB_COUNT or trace_counts != Counter({"v43_success": 10, "v43_transient_timeout_retry": 10}):
        raise RehearsalError("exact 60-row/actual-trace coverage oracle drifted")
    _validate_committed_trace_authority()
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_terminal_validation",
        "suite_id": SUITE_ID, "benchmark_result": False,
        "gold_path_parameter": False, "gold_opened": False,
        "terminal_validated": True, "shared_validators": [
            "validate_run_rows", "validate_claims", "validate_artifact_rows"
        ],
        "schedule_id": schedule["schedule_id"],
        "manifest_sha256": sha256_bytes(canonical_json_file_bytes(manifest)),
        "schedule_sha256": sha256_bytes(schedule_bytes), "runs_sha256": sha256_bytes(runs_bytes),
        "fixture_count": FIXTURE_COUNT, "job_count": JOB_COUNT, "row_count": len(rows),
        "claim_count": JOB_COUNT, "done_count": JOB_COUNT, "artifact_run_count": JOB_COUNT,
        "trace_sample_counts": dict(sorted(trace_counts.items())),
        "trace_validator": {
            "authority": "OOLONG parse_azdaja_route_evidence/parse_azdaja_usage + score retained parser",
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
    entries = gold.get("fixtures")
    answers: dict[str, str] = {}
    if not isinstance(entries, list) or len(entries) != FIXTURE_COUNT:
        raise RehearsalError("rehearsal synthetic gold fixture count drifted")
    for index, item in enumerate(entries):
        fixture_id = _fixture_id(index)
        expected = {"id": fixture_id, "answer": EXPECTED_LABELS[index],
                    "payload_sha256": fixtures[fixture_id]["payload_sha256"]}
        if item != expected or fixture_id in answers:
            raise RehearsalError(f"rehearsal synthetic gold fixture {index + 1} drifted")
        answers[fixture_id] = item["answer"]
    return gold, answers


def build_report_after_terminal(
    *, terminal_path: Path, manifest_path: Path, schedule_path: Path,
    runs_path: Path, claims_root: Path, artifacts_root: Path, gold_path: Path,
) -> dict[str, Any]:
    terminal, terminal_bytes = _read_object(terminal_path, "rehearsal terminal validation")
    rebuilt = terminal_validate(
        manifest_path=manifest_path, schedule_path=schedule_path, runs_path=runs_path,
        claims_root=claims_root, artifacts_root=artifacts_root,
    )
    if terminal != rebuilt:
        raise RehearsalError("rehearsal terminal validation receipt drifted")
    manifest, fixtures = _load_public(manifest_path)
    schedule, _ = _read_object(schedule_path, "rehearsal schedule")
    jobs = _validate_schedule(schedule, manifest_path, manifest, fixtures)
    rows, runs_bytes = _load_rows(runs_path)
    gold, answers = _load_gold_after_terminal(gold_path, manifest, fixtures)
    try:
        core = SCORE.build_report_core(
            schedule=schedule, jobs=jobs, rows=rows, arms=ARMS,
            fixtures=fixtures, answers=answers, profile=SCORE.REHEARSAL_PROFILE,
            bootstrap_seed=REHEARSAL_SEED, bootstrap_resamples=256,
            envelope_threshold_n=10,
        )
    except SCORE.ScoreError as exc:
        raise RehearsalError(f"shared scoring/report core refused rehearsal: {exc}") from exc
    oracle = {
        "jcode-native": {"official": 20, "strict": 20, "end_to_end": 20},
        "jcode-azdaja": {"official": 0, "strict": 0, "end_to_end": 0,
                           "derived_end_to_end": 10},
        "prime-agent": {"official": 20, "strict": 0, "end_to_end": 20},
    }
    for arm, expected in oracle.items():
        overall = core["arms"][arm]["overall"]
        observed = {
            "official": overall["answer_scoring_all_terminal_outputs"]["official_longbench_v2_correct_n"],
            "strict": overall["answer_scoring_all_terminal_outputs"]["strict_mcq_correct_n"],
            "end_to_end": overall["end_to_end_fixed_denominator"]["official_longbench_v2_correct_n"],
        }
        for key in ("official", "strict", "end_to_end"):
            if observed[key] != expected[key]:
                raise RehearsalError(f"exact synthetic scoring oracle drifted for {arm}/{key}")
    gate = core["envelope_compatible_gate"]["arms"]
    if {arm: gate[arm]["correct_n"] for arm in ARMS} != {
        "jcode-native": 20, "jcode-azdaja": 10, "prime-agent": 20,
    }:
        raise RehearsalError(
            "exact synthetic derived scoring oracle drifted: "
            + repr({arm: gate[arm]["correct_n"] for arm in ARMS})
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_pre_freeze_rehearsal_private_report",
        "suite_id": SUITE_ID, "synthetic": True, "benchmark_result": False,
        "disclosure": "Offline shared-pipeline dress rehearsal; no OAuth or inference.",
        "integrity": {
            "terminal_validated_before_gold_open": True,
            "terminal_validation_sha256": sha256_bytes(terminal_bytes),
            "gold_sha256": sha256_bytes(canonical_json_file_bytes(gold)),
            "runs_sha256": sha256_bytes(runs_bytes), "schedule_id": schedule["schedule_id"],
            "fixture_count": FIXTURE_COUNT, "row_count": JOB_COUNT,
            "claim_count": JOB_COUNT, "done_count": JOB_COUNT,
            "artifact_run_count": JOB_COUNT,
            "shared_score_core": True, "exact_synthetic_oracle_asserted": True,
        },
        "arms": core["arms"], "domains": core["domains"],
        "comparisons": core["comparisons"],
        "envelope_compatible_gate": core["envelope_compatible_gate"],
        "scores": core["score_rows"], "oracle": oracle,
    }

def _contract_identity() -> dict[str, Any]:
    return {
        "implementation": _file_identity(Path(__file__), "rehearsal implementation"),
        "production_runner": _file_identity(PRODUCTION_CONTROLLER, "shared production runner"),
        "score_validator": _file_identity(PRODUCTION_VALIDATOR, "rehearsal score authority"),
        "production_adapter": _file_identity(PRODUCTION_ADAPTER, "shared OOLONG adapter"),
        "retained_trace_samples": {
            "v43_success": _file_identity(SUCCESS_TRACE, "committed v43 success trace"),
            "v43_transient_timeout_retry": _file_identity(RETRY_TRACE, "committed v43 retry trace"),
        },
    }


def _counts_from_inventory(inventory: list[dict[str, Any]]) -> dict[str, int]:
    paths = {item["path"] for item in inventory}
    return {
        "rows": JOB_COUNT,
        "claims": sum(path.startswith("claims/") and path.endswith(".json") and not path.endswith(".done.json") for path in paths),
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


def _verify_rehearsal_receipt_unheld(
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
    final_inventory = _inventory(bundle, exclude_receipt=True)
    final_receipt, final_receipt_bytes = _read_object(
        receipt_path, "rechecked pre-freeze rehearsal final receipt"
    )
    if final_inventory != inventory or final_receipt != receipt or final_receipt_bytes != receipt_bytes:
        raise RehearsalError("rehearsal bundle/receipt changed across full replay")
    return receipt_binding(receipt_path, receipt, receipt_bytes)


def verify_rehearsal_receipt(
    receipt_path: Path | str, *, expected_target: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Hold the no-symlink bundle root across the complete replay and rebind it."""
    receipt_path = _absolute(receipt_path)
    try:
        held_path, held_fd = SCORE._open_directory_fd(
            receipt_path.parent, "held rehearsal bundle root"
        )
    except SCORE.ScoreError as exc:
        raise RehearsalError(f"cannot hold rehearsal bundle root: {exc}") from exc
    fingerprint = SCORE._directory_fingerprint(os.fstat(held_fd))
    try:
        result = _verify_rehearsal_receipt_unheld(
            receipt_path, expected_target=expected_target
        )
        try:
            rebound_path, rebound_fd = SCORE._open_directory_fd(
                receipt_path.parent, "rebound rehearsal bundle root"
            )
        except SCORE.ScoreError as exc:
            raise RehearsalError(f"cannot rebind rehearsal bundle root: {exc}") from exc
        try:
            held_identity = os.fstat(held_fd)
            rebound_identity = os.fstat(rebound_fd)
            if (
                held_path != rebound_path
                or (held_identity.st_dev, held_identity.st_ino)
                != (rebound_identity.st_dev, rebound_identity.st_ino)
                or SCORE._directory_fingerprint(held_identity) != fingerprint
            ):
                raise RehearsalError("held rehearsal bundle root changed across replay")
        finally:
            os.close(rebound_fd)
        return result
    finally:
        os.close(held_fd)


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
    if binding.get("target_sha256") != target.get("target_sha256"):
        raise RehearsalError("production schedule receipt does not bind the full runtime target")
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
        if any(scheduled.get(key) != source.get(key) for key in ("sha256", "bytes", "version")):
            raise RehearsalError(f"production frozen {name} executable differs from rehearsal target")
    target_runtime = target.get("runtime_closure", {})
    for name in ("node", "kernel_python"):
        scheduled = runtime.get(name, {})
        source = target_runtime.get(name, {})
        if any(scheduled.get(key) != source.get(key) for key in ("sha256", "bytes", "version")):
            raise RehearsalError(f"production frozen runtime {name} differs from rehearsal target")
    for name in ("prime_package", "runtime_python"):
        scheduled = runtime.get(name, {})
        source = target_runtime.get(name, {})
        keys = ("inventory_sha256", "entry_count") + (("cli_relative",) if name == "prime_package" else ())
        if any(scheduled.get(key) != source.get(key) for key in keys):
            raise RehearsalError(f"production frozen runtime inventory {name} differs from rehearsal target")


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
    _, fixtures = _load_public(manifest_path)
    schedule = build_schedule(manifest_path, manifest, fixtures, target)
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
