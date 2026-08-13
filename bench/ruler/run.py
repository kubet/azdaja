#!/usr/bin/env python3
"""No-gold, deferred RULER execution controller.

The controller accepts only the sealed public ``ruler-exact-mini-v1`` manifest.
It freezes a balanced three-arm schedule before inference, stages the exact same
randomly named read-only official prompt for every arm of a fixture, and writes
append-only claims, terminal completions, and unscored inference rows.

Owner-only homes and post-hoc tool-event checks reduce accidental disclosure;
they are advisory controls, not an OS information-flow or network sandbox.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import math
import os
import random
import re
import secrets
import shutil
import stat
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable, Sequence

MODEL = "gpt-5.6-luna"
REASONING = "medium"
ARMS = ("jcode-native", "jcode-azdaja", "prime-agent")
REPETITIONS = 1
SCHEMA_VERSION = 1
SUITE_ID = "ruler-exact-mini-v1"
TASKS = ("niah_multikey_3", "vt", "fwe")
TARGET_LENGTHS = (8192, 32768, 131072)
EXPECTED_PER_CELL = 10
EXPECTED_FIXTURES = 90
RUN_ID_DOMAIN = b"ruler-run-v1\0"
DEFAULT_SEED = 20260813
RULER_URL = "https://github.com/NVIDIA/RULER.git"
RULER_COMMIT = "c3f5e3b4f87f97e048793bb510a3a6b19a46bf3a"
TASK_RESERVES = {"niah_multikey_3": 128, "vt": 30, "fwe": 50}
REQUIREMENTS_LOCK_SHA256 = "82d442a1cffdf8bf5b2d9e27f9e6432f3b3328f6813bf4086499d68bbb1ba1c9"
TOKENIZER_BLOB_SHA256 = "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"
THIRD_PARTY_NOTICES_SHA256 = "c5356d79adccad2264910a9df17792ed10fb1d452444ec2a8a96c1691f8152b2"
EXPECTED_RULER_SOURCE_HASHES = {
    "LICENSE": "43070e2d4e532684de521b885f385d0841030efa2b1a20bafb76133a5e1379c1",
    "scripts/synthetic.yaml": "34bc71dcacdc41a829a170f04b528fbf48d62c616338005ab4991680fbf8cb0b",
    "scripts/data/prepare.py": "f2d210860fbf5c640cb41ed104c7a923c9f4043f6e6c354277daacc73afc643d",
    "scripts/data/tokenizer.py": "c2e4bfab607eef87a86334558303c1811bc8e93f22a5c4b129f302726d2357a4",
    "scripts/data/template.py": "2e82d85152212136fffcd5624b158a2c75fd5036ec1c537f4b21eeb78fd18069",
    "scripts/data/manifest_utils.py": "ecac79322f28ce9a12388b12e35d560ecb7cdad6b9888467a5a13b0eff2db91e",
    "scripts/data/synthetic/constants.py": "6296e901d495ec6200dc3f68993ea13d8282e3c0dbe1a8c47967f111105d1fde",
    "scripts/data/synthetic/niah.py": "e9cada0a7660d274fe73a1338a90a7087e17b630169f1aaf14a8d3221c6805b5",
    "scripts/data/synthetic/variable_tracking.py": "9aac483420e158d116ab63fc43b9606bdb284ac0c053288c30776d5c365530e5",
    "scripts/data/synthetic/freq_words_extraction.py": "29b7af97ffdd2122fde348df20cd02add390a21cd6d64b6fd66c8663dc487f67",
    "scripts/eval/synthetic/constants.py": "6740467c17b8dc06b6b30f4f97e54ce8de81db0dd879f1538d0b6b5727f4bd5f",
}
# One wrapper, including punctuation, is used for all three products.  Only the
# frozen random basename varies by fixture, and it is identical across its arms.
WRAPPER_TEMPLATE = (
    "Treat the attached file {filename} as the official RULER prompt. "
    "Read the complete file, follow its prompt, and return only its requested "
    "answer with no explanation or other text."
)
SAFE_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,191}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
STAGED_NAME_RE = re.compile(r"[0-9a-f]{32}\.txt\Z")


class BenchError(RuntimeError):
    """A fail-closed validation or execution-controller error."""


def _load_oolong_execution_module() -> Any:
    """Load the existing product adapters without importing any OOLONG data."""
    path = Path(__file__).resolve().parents[1] / "oolong" / "run.py"
    name = "_azdaja_bound_oolong_execution"
    existing = sys.modules.get(name)
    if existing is not None and Path(existing.__file__).resolve() == path:
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BenchError(f"cannot load product execution dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    if module.MODEL != MODEL or module.REASONING != REASONING:
        raise BenchError("product execution dependency has incompatible frozen routing")
    return module


OOLONG = _load_oolong_execution_module()
OOLONG_MODULE_PATH = Path(OOLONG.__file__).resolve(strict=True)


@dataclass(frozen=True)
class PublicFixture:
    fixture_id: str
    task: str
    target_length: int
    payload_path: Path
    payload_data: bytes
    payload_sha256: str
    payload_bytes: int
    construction_tokens: int
    row_length: int


@dataclass(frozen=True)
class PublicSuite:
    path: Path
    sha256: str
    manifest: dict[str, Any]
    fixtures: tuple[PublicFixture, ...]


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def canonical_json_file_bytes(value: Any) -> bytes:
    return canonical_json_bytes(value) + b"\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _decode_json(data: bytes, label: str) -> Any:
    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_object_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise BenchError(f"invalid {label}: {exc}") from exc


def require_private_regular(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise BenchError(f"{label} is missing or unreadable: {path}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise BenchError(f"{label} must be a regular non-symlink file: {path}")
    if os.name == "posix":
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise BenchError(f"{label} must be owner-only: {path}")
        if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
            raise BenchError(f"{label} must be owned by the current user: {path}")


def require_private_directory(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise BenchError(f"{label} is missing or unreadable: {path}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise BenchError(f"{label} must be a non-symlink directory: {path}")
    if os.name == "posix":
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise BenchError(f"{label} must be owner-only: {path}")
        if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
            raise BenchError(f"{label} must be owned by the current user: {path}")


def read_owner_file_once_with_token(
    path: Path, label: str, *, exact_mode: int, require_single_link: bool = True
) -> tuple[bytes, tuple[int, int, int]]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise BenchError(f"this platform cannot securely open {label} with O_NOFOLLOW")
    try:
        fd = os.open(path, os.O_RDONLY | nofollow)
    except OSError as exc:
        raise BenchError(f"cannot securely open {label} {path}: {exc}") from exc
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise BenchError(f"{label} must be a regular file: {path}")
        if require_single_link and metadata.st_nlink != 1:
            raise BenchError(f"{label} must have exactly one hard link: {path}")
        if os.name == "posix":
            if stat.S_IMODE(metadata.st_mode) != exact_mode:
                raise BenchError(f"{label} must have exact mode {exact_mode:04o}: {path}")
            if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
                raise BenchError(f"{label} must be owned by current user: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        data = b"".join(chunks)
        after = os.fstat(fd)
        if (
            len(data) != metadata.st_size
            or (after.st_dev, after.st_ino, after.st_size)
            != (metadata.st_dev, metadata.st_ino, metadata.st_size)
        ):
            raise BenchError(f"{label} changed during its single read: {path}")
        return data, (metadata.st_dev, metadata.st_ino, metadata.st_size)
    finally:
        os.close(fd)


def read_owner_file_once(
    path: Path, label: str, *, exact_mode: int, require_single_link: bool = True
) -> bytes:
    return read_owner_file_once_with_token(
        path, label, exact_mode=exact_mode, require_single_link=require_single_link
    )[0]


def load_private_json(path: Path, label: str) -> dict[str, Any]:
    data = read_owner_file_once(path, label, exact_mode=0o600)
    value = _decode_json(data, label)
    if not isinstance(value, dict):
        raise BenchError(f"{label} must contain a JSON object")
    try:
        canonical = canonical_json_file_bytes(value)
    except (UnicodeError, ValueError, TypeError) as exc:
        raise BenchError(f"{label} contains a value without canonical UTF-8 encoding: {exc}") from exc
    if data != canonical:
        raise BenchError(f"{label} must be canonical compact JSON with one final LF")
    return value


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def require_exact_private_directory(path: Path, label: str) -> Path:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise BenchError(f"{label} is missing or unreadable: {path}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise BenchError(f"{label} must be a non-symlink directory: {path}")
    if os.name == "posix":
        if stat.S_IMODE(metadata.st_mode) != 0o700:
            raise BenchError(f"{label} must have exact mode 0700: {path}")
        if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
            raise BenchError(f"{label} must be owned by the current user: {path}")
    return path


def read_sealed_payload_once(path: Path, label: str) -> bytes:
    """Open once without following links and bind exact inode safety+bytes."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise BenchError("this platform cannot enforce O_NOFOLLOW for sealed payloads")
    flags = os.O_RDONLY | nofollow
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise BenchError(f"cannot open {label} safely: {path}: {exc}") from exc
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise BenchError(f"{label} must be a regular file: {path}")
        if metadata.st_nlink != 1:
            raise BenchError(f"{label} must have exactly one hard link: {path}")
        if os.name == "posix":
            if stat.S_IMODE(metadata.st_mode) != 0o600:
                raise BenchError(f"{label} must have exact mode 0600: {path}")
            if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
                raise BenchError(f"{label} must be owned by the current user: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        data = b"".join(chunks)
        if len(data) != metadata.st_size:
            raise BenchError(f"{label} changed or was incompletely read: {path}")
        return data
    finally:
        os.close(fd)


def load_public_manifest(path_arg: str | Path) -> PublicSuite:
    """Validate the sealed inference-safe manifest without resolving gold."""
    unresolved = Path(path_arg).expanduser()
    if unresolved.is_symlink():
        raise BenchError("public manifest must not be a symlink")
    lexical = unresolved.absolute()
    require_exact_private_directory(lexical.parent, "sealed public root")
    path = lexical.resolve(strict=True)
    if path.parent != lexical.parent:
        raise BenchError("sealed public root must not resolve through a symlink")
    document = load_private_json(path, "public RULER manifest")
    if set(document) != {
        "schema_version", "record_type", "suite_id", "upstream_commit", "source",
        "configuration", "provenance_commitments", "redistribution_files",
        "fixtures", "gold_sha256",
    }:
        raise BenchError("public manifest has an unexpected object shape")
    expected_configuration = {
        "tasks": list(TASKS),
        "target_lengths": list(TARGET_LENGTHS),
        "pool_size": 100,
        "per_cell": EXPECTED_PER_CELL,
        "tokenizer": "cl100k_base",
        "task_generation_reserves": TASK_RESERVES,
        "payload_rule": 'row["input"] + row["answer_prefix"]',
        "selection": {
            "niah_multikey_3": "one secret-HMAC-ranked row per answer-position decile",
            "vt": "ten secret-HMAC-ranked line ordinals",
            "fwe": "ten secret-HMAC-ranked line ordinals",
        },
    }
    expected_source = {"name": "NVIDIA/RULER", "url": RULER_URL, "commit": RULER_COMMIT}
    for actual, expected, label in (
        (document.get("schema_version"), SCHEMA_VERSION, "schema_version"),
        (document.get("record_type"), "ruler_exact_mini_public_manifest", "record_type"),
        (document.get("suite_id"), SUITE_ID, "suite_id"),
        (document.get("upstream_commit"), RULER_COMMIT, "upstream_commit"),
        (document.get("source"), expected_source, "source"),
        (document.get("configuration"), expected_configuration, "configuration"),
    ):
        if actual != expected:
            raise BenchError(f"public manifest {label} does not match the sealed suite")
    commitments = document.get("provenance_commitments")
    if not isinstance(commitments, dict) or set(commitments) != {
        "generation_plan_sha256", "requirements_lock_sha256",
        "tokenizer_blob_sha256", "ruler_source_files",
    }:
        raise BenchError("public manifest provenance commitments have an unexpected shape")
    if not _is_sha256(commitments.get("generation_plan_sha256")):
        raise BenchError("public manifest generation plan commitment is invalid")
    if commitments.get("requirements_lock_sha256") != REQUIREMENTS_LOCK_SHA256:
        raise BenchError("public manifest requirements commitment drifted")
    if commitments.get("tokenizer_blob_sha256") != TOKENIZER_BLOB_SHA256:
        raise BenchError("public manifest tokenizer commitment drifted")
    if commitments.get("ruler_source_files") != EXPECTED_RULER_SOURCE_HASHES:
        raise BenchError("public manifest RULER source commitments drifted")
    expected_redistribution = {
        "LICENSE.NVIDIA-RULER": EXPECTED_RULER_SOURCE_HASHES["LICENSE"],
        "THIRD_PARTY_NOTICES.md": THIRD_PARTY_NOTICES_SHA256,
    }
    if document.get("redistribution_files") != expected_redistribution:
        raise BenchError("public manifest redistribution file commitments drifted")
    if not _is_sha256(document.get("gold_sha256")):
        raise BenchError("public manifest has an invalid opaque gold commitment")
    entries = document.get("fixtures")
    if not isinstance(entries, list) or len(entries) != EXPECTED_FIXTURES:
        raise BenchError(f"public manifest must contain exactly {EXPECTED_FIXTURES} fixtures")

    root = path.parent
    payloads_root = root / "payloads"
    require_exact_private_directory(payloads_root, "sealed payloads directory")
    expected_root_entries = {
        "manifest.json", "payloads",
        "LICENSE.NVIDIA-RULER", "THIRD_PARTY_NOTICES.md",
    }
    try:
        actual_root_entries = {entry.name for entry in root.iterdir()}
    except OSError as exc:
        raise BenchError(f"cannot enumerate sealed public root: {exc}") from exc
    if actual_root_entries != expected_root_entries:
        raise BenchError("sealed public root inventory is not exact")
    for name, expected_hash in expected_redistribution.items():
        data = read_sealed_payload_once(root / name, f"redistribution file {name}")
        if sha256_bytes(data) != expected_hash:
            raise BenchError(f"redistribution file hash mismatch: {name}")
    fixtures: list[PublicFixture] = []
    seen_ids: set[str] = set()
    seen_paths: set[Path] = set()
    seen_hashes: set[str] = set()
    cells: Counter[tuple[str, int]] = Counter()
    for index, entry in enumerate(entries, 1):
        if not isinstance(entry, dict) or set(entry) != {
            "id", "task", "target_length", "payload", "payload_sha256",
            "payload_bytes", "construction_tokens", "row_length",
        }:
            raise BenchError(f"public fixture {index} has an unexpected object shape")
        fixture_id = entry.get("id")
        task = entry.get("task")
        target_length = entry.get("target_length")
        payload_sha = entry.get("payload_sha256")
        if not isinstance(fixture_id, str) or SAFE_ID_RE.fullmatch(fixture_id) is None:
            raise BenchError(f"public fixture {index} has an unsafe id")
        if fixture_id in seen_ids:
            raise BenchError(f"duplicate public fixture id: {fixture_id}")
        if task not in TASKS or target_length not in TARGET_LENGTHS:
            raise BenchError(f"public fixture {fixture_id} has an invalid cell")
        if not _is_sha256(payload_sha):
            raise BenchError(f"public fixture {fixture_id} payload hash is invalid")
        if not _positive_int(entry.get("payload_bytes")):
            raise BenchError(f"public fixture {fixture_id} payload_bytes is invalid")
        construction_tokens = entry.get("construction_tokens")
        row_length = entry.get("row_length")
        if (
            not _positive_int(construction_tokens)
            or not _positive_int(row_length)
            or construction_tokens + TASK_RESERVES[task] != row_length
            or row_length > target_length
        ):
            raise BenchError(f"public fixture {fixture_id} construction length is invalid")
        relative = entry.get("payload")
        expected_relative = f"payloads/{fixture_id}.txt"
        if relative != expected_relative:
            raise BenchError(
                f"public fixture {fixture_id} payload must be exactly {expected_relative!r}"
            )
        payload = payloads_root / f"{fixture_id}.txt"
        if payload.parent != payloads_root or payload.is_symlink():
            raise BenchError(f"public fixture {fixture_id} payload path is unsafe")
        if payload in seen_paths or payload_sha in seen_hashes:
            raise BenchError(f"public fixture {fixture_id} duplicates a payload identity")
        payload_data = read_sealed_payload_once(
            payload, f"public fixture {fixture_id} payload"
        )
        if len(payload_data) != entry["payload_bytes"] or sha256_bytes(payload_data) != payload_sha:
            raise BenchError(f"public fixture {fixture_id} payload bytes/hash mismatch")
        try:
            payload_data.decode("utf-8")
        except UnicodeError as exc:
            raise BenchError(f"public fixture {fixture_id} payload is not UTF-8: {exc}") from exc
        fixtures.append(PublicFixture(
            fixture_id=fixture_id,
            task=task,
            target_length=target_length,
            payload_path=payload,
            payload_data=payload_data,
            payload_sha256=payload_sha,
            payload_bytes=entry["payload_bytes"],
            construction_tokens=construction_tokens,
            row_length=row_length,
        ))
        seen_ids.add(fixture_id)
        seen_paths.add(payload)
        seen_hashes.add(payload_sha)
        cells[(task, target_length)] += 1
    expected_payload_names = {f"{fixture_id}.txt" for fixture_id in seen_ids}
    try:
        actual_payload_names = {entry.name for entry in payloads_root.iterdir()}
    except OSError as exc:
        raise BenchError(f"cannot enumerate sealed payloads directory: {exc}") from exc
    if actual_payload_names != expected_payload_names:
        raise BenchError("sealed payloads directory inventory is not exact")
    expected_cells = {(task, length) for task in TASKS for length in TARGET_LENGTHS}
    if set(cells) != expected_cells or any(cells[cell] != EXPECTED_PER_CELL for cell in expected_cells):
        raise BenchError("public manifest is not the exact 9-cell x 10-fixture sealed grid")
    return PublicSuite(
        path, sha256_bytes(canonical_json_file_bytes(document)), document, tuple(fixtures)
    )


def wrapper_for(filename: str) -> str:
    if STAGED_NAME_RE.fullmatch(filename) is None:
        raise BenchError("staged payload filename is not a frozen random basename")
    return WRAPPER_TEMPLATE.format(filename=filename)


def _file_identity(path: Path) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    return {"path": str(resolved), "sha256": sha256_path(resolved), "bytes": resolved.stat().st_size}


def controller_identity() -> dict[str, Any]:
    """Bind both this controller and its imported product-execution module."""
    components = {
        "ruler_runner": _file_identity(Path(__file__)),
        "oolong_execution_module": _file_identity(OOLONG_MODULE_PATH),
    }
    bound = {
        name: {"sha256": value["sha256"], "bytes": value["bytes"]}
        for name, value in sorted(components.items())
    }
    return {"sha256": sha256_bytes(canonical_json_bytes(bound)), "components": components}


def candidate_identity(skill: Path) -> dict[str, Any]:
    return OOLONG.candidate_identity(skill)


def snapshot_identity_file(source: Path, destination: Path, label: str) -> dict[str, Any]:
    """Exclusively preserve exact identity bytes in the owner-only run artifact."""
    source_absolute = Path(os.path.abspath(source))
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise BenchError(f"this platform cannot securely snapshot {label}")
    try:
        source_fd = os.open(source_absolute, os.O_RDONLY | nofollow)
    except OSError as exc:
        raise BenchError(f"cannot securely open {label} source: {exc}") from exc
    try:
        source_metadata = os.fstat(source_fd)
        if not stat.S_ISREG(source_metadata.st_mode) or source_metadata.st_nlink != 1:
            raise BenchError(f"{label} source is not a single-link regular file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(source_fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        data = b"".join(chunks)
        if len(data) != source_metadata.st_size:
            raise BenchError(f"{label} source changed during snapshot read")
    finally:
        os.close(source_fd)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o500)
    try:
        if os.name == "posix":
            os.fchmod(fd, 0o500)
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError(f"short write while snapshotting {label}")
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    frozen_data = read_owner_file_once(
        destination, f"{label} immutable snapshot", exact_mode=0o500
    )
    if frozen_data != data:
        raise BenchError(f"{label} immutable snapshot bytes mismatch")
    return {
        "path": str(destination.resolve(strict=True)),
        "sha256": sha256_bytes(data),
        "bytes": len(data),
    }


def snapshot_controller(snapshot_root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    sources = {
        "ruler_runner": Path(__file__).resolve(strict=True),
        "oolong_execution_module": OOLONG_MODULE_PATH,
    }
    components = {
        name: snapshot_identity_file(source, snapshot_root / f"{name}.py", name)
        for name, source in sources.items()
    }
    bound = {
        name: {"sha256": value["sha256"], "bytes": value["bytes"]}
        for name, value in sorted(components.items())
    }
    return (
        {"sha256": sha256_bytes(canonical_json_bytes(bound)), "components": components},
        {name: str(source) for name, source in sources.items()},
    )


def _safe_bundle_relative(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def _copy_prime_file(source: Path, destination: Path, mode: int, label: str) -> tuple[bytes, int]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise BenchError("O_NOFOLLOW is required for Prime package snapshot")
    fd = os.open(source, os.O_RDONLY | nofollow)
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise BenchError(f"unsafe Prime package source file: {label}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        data = b"".join(chunks)
        if len(data) != metadata.st_size:
            raise BenchError(f"Prime package source changed during read: {label}")
    finally:
        os.close(fd)
    out = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        if os.name == "posix":
            os.fchmod(out, mode)
        view = memoryview(data)
        while view:
            written = os.write(out, view)
            if written <= 0:
                raise OSError(f"short Prime package snapshot write: {label}")
            view = view[written:]
    finally:
        os.close(out)
    return data, len(data)


def snapshot_prime_bundle(
    entrypoint_source: Path, snapshot_root: Path
) -> tuple[dict[str, Any], Path]:
    entrypoint_source = entrypoint_source.resolve(strict=True)
    package_root = entrypoint_source.parents[2].resolve(strict=True)
    entrypoint_relative = entrypoint_source.relative_to(package_root)
    inventory: list[dict[str, Any]] = []
    for current, dir_names, file_names in os.walk(package_root, topdown=True, followlinks=False):
        current_path = Path(current)
        relative_current = current_path.relative_to(package_root)
        destination_current = snapshot_root / relative_current
        destination_current.mkdir(mode=0o700, parents=True, exist_ok=True)
        if os.name == "posix":
            os.chmod(destination_current, 0o700)
        # Record every real directory other than the separately bound root.
        if relative_current != Path("."):
            inventory.append({
                "relative_path": str(relative_current), "kind": "directory",
                "sha256": None, "bytes": 0, "mode": "0700",
            })
        for name in list(dir_names):
            source_child = current_path / name
            metadata = source_child.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                # A directory symlink is materialized only when it resolves to a
                # regular file; symlinked directories would duplicate/escape trees.
                target = source_child.resolve(strict=True)
                try:
                    target.relative_to(package_root)
                except ValueError as exc:
                    raise BenchError(f"external Prime package symlink: {source_child}") from exc
                if not target.is_file():
                    raise BenchError(f"Prime directory symlink target is not regular: {source_child}")
                dir_names.remove(name)
                relative = relative_current / name
                mode = 0o500 if relative == entrypoint_relative else 0o400
                data, size = _copy_prime_file(
                    target, snapshot_root / relative, mode, str(relative)
                )
                inventory.append({
                    "relative_path": str(relative), "kind": "materialized_internal_symlink",
                    "sha256": sha256_bytes(data), "bytes": size, "mode": f"{mode:04o}",
                })
            elif not stat.S_ISDIR(metadata.st_mode):
                raise BenchError(f"unexpected Prime package entry type: {source_child}")
        for name in sorted(file_names):
            source_child = current_path / name
            metadata = source_child.lstat()
            kind = "file"
            read_source = source_child
            if stat.S_ISLNK(metadata.st_mode):
                target = source_child.resolve(strict=True)
                try:
                    target.relative_to(package_root)
                except ValueError as exc:
                    raise BenchError(f"external Prime package symlink: {source_child}") from exc
                if not target.is_file():
                    raise BenchError(f"Prime symlink target is not regular: {source_child}")
                kind = "materialized_internal_symlink"
                read_source = target
            elif not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise BenchError(f"unsafe Prime package file: {source_child}")
            relative = relative_current / name
            if not _safe_bundle_relative(str(relative)):
                raise BenchError(f"unsafe Prime package relative path: {relative}")
            mode = 0o500 if relative == entrypoint_relative else 0o400
            data, size = _copy_prime_file(
                read_source, snapshot_root / relative, mode, str(relative)
            )
            inventory.append({
                "relative_path": str(relative), "kind": kind,
                "sha256": sha256_bytes(data), "bytes": size, "mode": f"{mode:04o}",
            })
    inventory.sort(key=lambda item: item["relative_path"])
    entrypoint_frozen = snapshot_root / entrypoint_relative
    if not entrypoint_frozen.is_file():
        raise BenchError("Prime package snapshot omitted its CLI entrypoint")
    bundle = {
        "root": str(snapshot_root.resolve(strict=True)),
        "entrypoint": str(entrypoint_relative),
        "aggregate_sha256": sha256_bytes(canonical_json_bytes(inventory)),
        "files": inventory,
    }
    validate_prime_bundle_identity(bundle, entrypoint_frozen)
    return bundle, entrypoint_frozen


def validate_prime_bundle_identity(bundle: Any, entrypoint: Path) -> None:
    if not isinstance(bundle, dict) or set(bundle) != {
        "root", "entrypoint", "aggregate_sha256", "files"
    }:
        raise BenchError("Prime package identity has an unexpected shape")
    root = Path(str(bundle["root"]))
    require_exact_private_directory(root, "Prime immutable package root")
    entrypoint_relative = bundle["entrypoint"]
    if (
        not isinstance(entrypoint_relative, str)
        or not _safe_bundle_relative(entrypoint_relative)
        or entrypoint != root / entrypoint_relative
    ):
        raise BenchError("Prime package entrypoint identity is inconsistent")
    inventory = bundle.get("files")
    if not isinstance(inventory, list) or not inventory:
        raise BenchError("Prime package inventory is empty")
    names: set[str] = set()
    expected_files: set[str] = set()
    expected_dirs: set[str] = set()
    for item in inventory:
        if not isinstance(item, dict) or set(item) != {
            "relative_path", "kind", "sha256", "bytes", "mode"
        }:
            raise BenchError("Prime package item has an unexpected shape")
        name = item["relative_path"]
        if not isinstance(name, str) or not _safe_bundle_relative(name) or name in names:
            raise BenchError("Prime package relative path is unsafe or duplicate")
        names.add(name)
        kind = item["kind"]
        path = root / name
        if kind == "directory":
            if item != {
                "relative_path": name, "kind": "directory", "sha256": None,
                "bytes": 0, "mode": "0700",
            }:
                raise BenchError(f"Prime directory identity is invalid: {name}")
            require_exact_private_directory(path, f"Prime package directory {name}")
            expected_dirs.add(name)
        elif kind in {"file", "materialized_internal_symlink"}:
            expected_mode = "0500" if name == entrypoint_relative else "0400"
            if item["mode"] != expected_mode:
                raise BenchError(f"Prime package mode is invalid: {name}")
            data = read_owner_file_once(
                path, f"Prime package file {name}", exact_mode=int(expected_mode, 8)
            )
            if len(data) != item["bytes"] or sha256_bytes(data) != item["sha256"]:
                raise BenchError(f"Prime package file identity drifted: {name}")
            expected_files.add(name)
        else:
            raise BenchError(f"Prime package item kind is invalid: {name}")
    actual_files: set[str] = set()
    actual_dirs: set[str] = set()
    for current, dir_names, file_names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        require_exact_private_directory(current_path, "Prime package directory")
        if current_path != root:
            actual_dirs.add(str(current_path.relative_to(root)))
        for directory in dir_names:
            if (current_path / directory).is_symlink():
                raise BenchError("Prime snapshot contains a directory symlink")
        for filename in file_names:
            actual_files.add(str((current_path / filename).relative_to(root)))
    if actual_files != expected_files or actual_dirs != expected_dirs:
        raise BenchError("Prime immutable package inventory is not exact")
    if inventory != sorted(inventory, key=lambda item: item["relative_path"]):
        raise BenchError("Prime package inventory is not canonical order")
    if sha256_bytes(canonical_json_bytes(inventory)) != bundle["aggregate_sha256"]:
        raise BenchError("Prime package aggregate identity is invalid")


def _normalized_version(value: str) -> str:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if not lines:
        raise BenchError("version evidence is empty")
    return lines[-1]


def snapshot_executables(
    source_identities: dict[str, dict[str, Any]], snapshot_root: Path
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, source_identity in source_identities.items():
        source = Path(str(source_identity["path"]))
        bundle: dict[str, Any] | None = None
        smoke: dict[str, Any] | None = None
        if name == "prime-agent":
            prime_root = snapshot_root / "prime-agent-package"
            prime_root.mkdir(mode=0o700, exist_ok=False)
            bundle, frozen_path = snapshot_prime_bundle(source, prime_root)
            frozen_data = read_owner_file_once(
                frozen_path, "Prime frozen entrypoint", exact_mode=0o500
            )
            frozen = {
                "path": str(frozen_path),
                "sha256": sha256_bytes(frozen_data),
                "bytes": len(frozen_data),
            }
            command = [str(frozen_path), "--version"]
            env = OOLONG.sanitized_env()
            env["PI_PACKAGE_DIR"] = str(prime_root)
            try:
                probe = subprocess.run(
                    command, cwd=str(prime_root), env=env,
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True, encoding="utf-8",
                    errors="replace", timeout=30,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise BenchError(f"frozen Prime package smoke failed: {exc}") from exc
            combined = (probe.stdout + "\n" + probe.stderr).strip()
            source_version = _normalized_version(str(source_identity["version"]))
            frozen_version = _normalized_version(combined)
            if probe.returncode != 0 or frozen_version != source_version:
                raise BenchError(
                    "frozen Prime package --version differs from source "
                    f"(rc={probe.returncode}, source={source_version!r}, frozen={frozen_version!r})"
                )
            smoke = {
                "command": command,
                "returncode": probe.returncode,
                "stdout": OOLONG.bounded(probe.stdout, 4096),
                "stderr": OOLONG.bounded(probe.stderr, 4096),
                "matched_source_version": True,
            }
            version_command = command
        else:
            extension = source.suffix
            frozen = snapshot_identity_file(
                source, snapshot_root / f"{name}{extension}", f"{name} executable"
            )
            version_command = [str(frozen["path"]), "--version"]
        frozen.update({
            "version": source_identity["version"],
            "version_command": version_command,
            "bundle": bundle,
            "smoke": smoke,
        })
        result[name] = frozen
    return result


def snapshot_candidate(source_skill: Path, snapshot_root: Path) -> dict[str, Any]:
    required_modes = {"azdaja": 0o500, "config.toml": 0o400, "SKILL.md": 0o400}
    components: dict[str, dict[str, Any]] = {}
    for name, mode in required_modes.items():
        source = source_skill / name
        if source.is_symlink():
            raise BenchError(f"candidate component must not be a symlink: {name}")
        metadata = source.lstat()
        source_mode = 0o700 if name == "azdaja" else 0o600
        if (
            not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
            or (os.name == "posix" and (
                metadata.st_uid != os.geteuid()
                or stat.S_IMODE(metadata.st_mode) != source_mode
            ))
        ):
            raise BenchError(
                f"candidate component must be current-owner single-link regular file "
                f"with mode {source_mode:04o}: {name}"
            )
        frozen = snapshot_root / name
        identity = snapshot_identity_file(source, frozen, f"candidate {name}")
        if os.name == "posix":
            os.chmod(frozen, mode)
        components[name] = {
            "path": str(frozen.resolve(strict=True)),
            "sha256": identity["sha256"], "bytes": identity["bytes"],
            "mode": f"{mode:04o}",
        }
    if {entry.name for entry in snapshot_root.iterdir()} != set(required_modes):
        raise BenchError("candidate snapshot inventory is not exact")
    bound = {
        name: {key: component[key] for key in ("sha256", "bytes", "mode")}
        for name, component in sorted(components.items())
    }
    return {
        "sha256": sha256_bytes(canonical_json_bytes(bound)),
        "snapshot_root": str(snapshot_root.resolve(strict=True)),
        "components": components,
    }


def validate_candidate_snapshot(candidate: Any) -> Path:
    if not isinstance(candidate, dict) or set(candidate) != {
        "sha256", "snapshot_root", "components"
    }:
        raise BenchError("candidate snapshot identity has an unexpected shape")
    root = Path(str(candidate["snapshot_root"]))
    require_exact_private_directory(root, "candidate snapshot root")
    expected_modes = {"azdaja": "0500", "config.toml": "0400", "SKILL.md": "0400"}
    components = candidate.get("components")
    if not isinstance(components, dict) or set(components) != set(expected_modes):
        raise BenchError("candidate snapshot component inventory is invalid")
    bound: dict[str, Any] = {}
    for name, expected_mode in expected_modes.items():
        component = components[name]
        if not isinstance(component, dict) or set(component) != {
            "path", "sha256", "bytes", "mode"
        }:
            raise BenchError(f"candidate component identity is invalid: {name}")
        path = Path(str(component["path"]))
        if path != root / name or component["mode"] != expected_mode:
            raise BenchError(f"candidate component path/mode is invalid: {name}")
        data = read_owner_file_once(
            path, f"candidate snapshot {name}", exact_mode=int(expected_mode, 8)
        )
        if len(data) != component["bytes"] or sha256_bytes(data) != component["sha256"]:
            raise BenchError(f"candidate component drifted: {name}")
        bound[name] = {
            "sha256": component["sha256"], "bytes": component["bytes"],
            "mode": component["mode"],
        }
    if {entry.name for entry in root.iterdir()} != set(expected_modes):
        raise BenchError("candidate snapshot filesystem inventory is not exact")
    if candidate["sha256"] != sha256_bytes(canonical_json_bytes(dict(sorted(bound.items())))):
        raise BenchError("candidate snapshot aggregate identity is invalid")
    return root


def build_schedule(
    suite: PublicSuite,
    *,
    seed: int,
    timeout: int,
    candidate: dict[str, Any],
    candidate_source_path: str,
    controller: dict[str, Any],
    controller_source_paths: dict[str, str],
    executables: dict[str, Any],
    random_names: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Build one balanced randomized block schedule (six permutations x 15)."""
    rng = random.Random(seed)
    fixture_order = list(suite.fixtures)
    rng.shuffle(fixture_order)
    permutations = list(itertools.permutations(ARMS)) * 15
    rng.shuffle(permutations)
    names = iter(random_names) if random_names is not None else None
    fixture_names: dict[str, str] = {}
    for fixture in fixture_order:
        name = next(names) if names is not None else f"{secrets.token_hex(16)}.txt"
        if STAGED_NAME_RE.fullmatch(name) is None or name in fixture_names.values():
            raise BenchError("random staged payload names must be distinct 128-bit hex basenames")
        fixture_names[fixture.fixture_id] = name
    if names is not None:
        try:
            next(names)
        except StopIteration:
            pass
        else:
            raise BenchError("too many staged payload names were supplied")

    jobs: list[dict[str, Any]] = []
    ordinal = 0
    for fixture, order in zip(fixture_order, permutations):
        for arm in order:
            ordinal += 1
            jobs.append({
                "ordinal": ordinal,
                "fixture_id": fixture.fixture_id,
                "payload_sha256": fixture.payload_sha256,
                "task": fixture.task,
                "target_length": fixture.target_length,
                "staged_filename": fixture_names[fixture.fixture_id],
                "repetition": 1,
                "arm": arm,
            })
    identity: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "ruler_frozen_schedule",
        "suite": {
            "suite_id": SUITE_ID,
            "manifest_sha256": suite.sha256,
            "fixtures": [
                {
                    "fixture_id": fixture.fixture_id,
                    "payload_sha256": fixture.payload_sha256,
                    "task": fixture.task,
                    "target_length": fixture.target_length,
                    "staged_filename": fixture_names[fixture.fixture_id],
                }
                for fixture in suite.fixtures
            ],
        },
        "configuration": {
            "model": MODEL,
            "reasoning": REASONING,
            "arms": list(ARMS),
            "repetitions": REPETITIONS,
            "seed": seed,
            "timeout_seconds": timeout,
            "wrapper_template_sha256": sha256_bytes(WRAPPER_TEMPLATE.encode("utf-8")),
            "candidate": candidate,
            "candidate_source_path": candidate_source_path,
            "controller": controller,
            "controller_source_paths": controller_source_paths,
            "executables": executables,
            "containment": {
                "os_level_asserted": False,
                "disclaimer": "owner-only isolation and event auditing are advisory, not OS-level containment",
                "claim_ledger": "local append-only creation protocol is not authenticated against malicious same-owner deletion/retry; external signing or transparency is future work",
            },
        },
        "jobs": jobs,
    }
    schedule_id = sha256_bytes(canonical_json_bytes(identity))
    for job in jobs:
        job["run_id"] = sha256_bytes(
            RUN_ID_DOMAIN + schedule_id.encode("ascii") + canonical_json_bytes(job)
        )
    identity["schedule_id"] = schedule_id
    return identity


def validate_schedule(
    schedule: dict[str, Any],
    suite: PublicSuite,
    *,
    seed: int,
    timeout: int,
    candidate: dict[str, Any],
    candidate_source_path: str,
    controller: dict[str, Any],
    controller_source_paths: dict[str, str],
    executables: dict[str, Any],
) -> None:
    """Validate a frozen schedule and every resume-relevant identity exactly."""
    if schedule.get("schema_version") != 1 or schedule.get("record_type") != "ruler_frozen_schedule":
        raise BenchError("frozen schedule type/version is invalid")
    schedule_id = schedule.get("schedule_id")
    if not _is_sha256(schedule_id):
        raise BenchError("frozen schedule_id is invalid")
    identity = copy.deepcopy(schedule)
    identity.pop("schedule_id", None)
    jobs_identity = identity.get("jobs")
    if not isinstance(jobs_identity, list):
        raise BenchError("frozen schedule jobs are invalid")
    for job in jobs_identity:
        if not isinstance(job, dict):
            raise BenchError("frozen schedule job is not an object")
        job.pop("run_id", None)
    if sha256_bytes(canonical_json_bytes(identity)) != schedule_id:
        raise BenchError("frozen schedule identity does not recompute exactly")

    expected_configuration = {
        "model": MODEL,
        "reasoning": REASONING,
        "arms": list(ARMS),
        "repetitions": 1,
        "seed": seed,
        "timeout_seconds": timeout,
        "wrapper_template_sha256": sha256_bytes(WRAPPER_TEMPLATE.encode("utf-8")),
        "candidate": candidate,
        "candidate_source_path": candidate_source_path,
        "controller": controller,
        "controller_source_paths": controller_source_paths,
        "executables": executables,
        "containment": {
            "os_level_asserted": False,
            "disclaimer": "owner-only isolation and event auditing are advisory, not OS-level containment",
            "claim_ledger": "local append-only creation protocol is not authenticated against malicious same-owner deletion/retry; external signing or transparency is future work",
        },
    }
    if schedule.get("configuration") != expected_configuration:
        raise BenchError("resume configuration, candidate, controller, or executable identity drifted")
    controller_components = controller.get("components")
    if not isinstance(controller_components, dict):
        raise BenchError("controller component identities are missing")
    rebound: dict[str, dict[str, Any]] = {}
    for name, component in controller_components.items():
        if not isinstance(component, dict) or set(component) != {"path", "sha256", "bytes"}:
            raise BenchError(f"controller component identity is invalid: {name}")
        path = Path(str(component["path"]))
        snapshot_data = read_owner_file_once(
            path, f"immutable controller snapshot {name}", exact_mode=0o500
        )
        if len(snapshot_data) != component["bytes"] or sha256_bytes(snapshot_data) != component["sha256"]:
            raise BenchError(f"immutable controller snapshot drifted: {name}")
        rebound[name] = {"sha256": component["sha256"], "bytes": component["bytes"]}
    if controller.get("sha256") != sha256_bytes(canonical_json_bytes(dict(sorted(rebound.items())))):
        raise BenchError("immutable controller aggregate identity is invalid")
    for name, identity in executables.items():
        if not isinstance(identity, dict):
            raise BenchError(f"executable identity is invalid: {name}")
        path = Path(str(identity.get("path", "")))
        snapshot_data = read_owner_file_once(
            path, f"immutable executable snapshot {name}", exact_mode=0o500
        )
        if len(snapshot_data) != identity.get("bytes") or sha256_bytes(snapshot_data) != identity.get("sha256"):
            raise BenchError(f"immutable executable snapshot drifted: {name}")
        bundle = identity.get("bundle")
        if name == "prime-agent":
            validate_prime_bundle_identity(bundle, path)
        elif bundle is not None:
            raise BenchError(f"unexpected bundle identity for {name}")
    suite_record = schedule.get("suite")
    if not isinstance(suite_record, dict) or set(suite_record) != {
        "suite_id", "manifest_sha256", "fixtures"
    }:
        raise BenchError("frozen schedule suite identity has an unexpected shape")
    if suite_record["suite_id"] != SUITE_ID or suite_record["manifest_sha256"] != suite.sha256:
        raise BenchError("frozen schedule public manifest identity drifted")
    scheduled_fixtures = suite_record.get("fixtures")
    if not isinstance(scheduled_fixtures, list) or len(scheduled_fixtures) != EXPECTED_FIXTURES:
        raise BenchError("frozen schedule fixture identity list is incomplete")
    public_by_id = {fixture.fixture_id: fixture for fixture in suite.fixtures}
    names_by_id: dict[str, str] = {}
    for item in scheduled_fixtures:
        if not isinstance(item, dict) or set(item) != {
            "fixture_id", "payload_sha256", "task", "target_length", "staged_filename"
        }:
            raise BenchError("frozen schedule fixture identity has an unexpected shape")
        fixture = public_by_id.get(item.get("fixture_id"))
        if fixture is None or item.get("payload_sha256") != fixture.payload_sha256:
            raise BenchError("frozen schedule fixture is unknown or changed")
        if item.get("task") != fixture.task or item.get("target_length") != fixture.target_length:
            raise BenchError("frozen schedule fixture metadata drifted")
        name = item.get("staged_filename")
        if not isinstance(name, str) or STAGED_NAME_RE.fullmatch(name) is None:
            raise BenchError("frozen schedule staged filename is invalid")
        if name in names_by_id.values():
            raise BenchError("frozen schedule staged filenames are not unique")
        names_by_id[fixture.fixture_id] = name
    if set(names_by_id) != set(public_by_id):
        raise BenchError("frozen schedule fixture ids differ from the public manifest")

    jobs = schedule.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != EXPECTED_FIXTURES * len(ARMS):
        raise BenchError("frozen schedule must contain exactly 270 jobs")
    expected_grid = {(fixture_id, arm, 1) for fixture_id in public_by_id for arm in ARMS}
    observed: set[tuple[str, str, int]] = set()
    run_ids: set[str] = set()
    permutation_counts: Counter[tuple[str, ...]] = Counter()
    for index, job in enumerate(jobs, 1):
        if not isinstance(job, dict) or set(job) != {
            "ordinal", "fixture_id", "payload_sha256", "task", "target_length",
            "staged_filename", "repetition", "arm", "run_id",
        }:
            raise BenchError(f"frozen schedule job {index} has an unexpected shape")
        cell = (job.get("fixture_id"), job.get("arm"), job.get("repetition"))
        if job.get("ordinal") != index or cell not in expected_grid or cell in observed:
            raise BenchError(f"frozen schedule job {index} is duplicate or outside the exact grid")
        fixture = public_by_id[job["fixture_id"]]
        if (
            job["payload_sha256"] != fixture.payload_sha256
            or job["task"] != fixture.task
            or job["target_length"] != fixture.target_length
            or job["staged_filename"] != names_by_id[fixture.fixture_id]
        ):
            raise BenchError(f"frozen schedule job {index} fixture identity drifted")
        run_id = job.get("run_id")
        if not _is_sha256(run_id) or run_id in run_ids:
            raise BenchError(f"frozen schedule job {index} run_id is invalid or duplicate")
        base = dict(job)
        del base["run_id"]
        expected_run_id = sha256_bytes(
            RUN_ID_DOMAIN + schedule_id.encode("ascii") + canonical_json_bytes(base)
        )
        if run_id != expected_run_id:
            raise BenchError(f"frozen schedule job {index} run_id drifted")
        observed.add(cell)
        run_ids.add(run_id)
    if observed != expected_grid:
        raise BenchError("frozen schedule is not the complete fixture/arm grid")
    for start in range(0, len(jobs), 3):
        group = jobs[start:start + 3]
        if len({job["fixture_id"] for job in group}) != 1:
            raise BenchError("frozen schedule does not keep fixture arms consecutive")
        order = tuple(job["arm"] for job in group)
        if set(order) != set(ARMS):
            raise BenchError("frozen schedule fixture group is incomplete")
        permutation_counts[order] += 1
    if set(permutation_counts) != set(itertools.permutations(ARMS)) or any(
        count != 15 for count in permutation_counts.values()
    ):
        raise BenchError("frozen schedule must balance all six arm permutations exactly 15 times")

    # Identity validity is not enough: reconstruct fixture order and all six-way
    # arm blocks from the frozen seed. Random basenames are persisted identities,
    # so replay them in the exact seeded fixture order rather than regenerating.
    seeded_fixture_order = list(suite.fixtures)
    random.Random(seed).shuffle(seeded_fixture_order)
    replay_names = [names_by_id[item.fixture_id] for item in seeded_fixture_order]
    reconstructed = build_schedule(
        suite,
        seed=seed,
        timeout=timeout,
        candidate=candidate,
        candidate_source_path=candidate_source_path,
        controller=controller,
        controller_source_paths=controller_source_paths,
        executables=executables,
        random_names=replay_names,
    )
    if reconstructed != schedule:
        raise BenchError("frozen schedule is not the exact reconstruction from its seed")


def atomic_create_private_json(path: Path, value: Any) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise BenchError("O_NOFOLLOW is required for private JSON creation")
    data = canonical_json_file_bytes(value)
    try:
        fd = os.open(
            path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow, 0o600
        )
    except OSError as exc:
        raise BenchError(f"cannot exclusively create private JSON {path}: {exc}") from exc
    try:
        if os.name == "posix":
            os.fchmod(fd, 0o600)
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise BenchError("created private JSON is not a single-link regular file")
        if os.name == "posix" and (
            metadata.st_uid != os.geteuid() or stat.S_IMODE(metadata.st_mode) != 0o600
        ):
            raise BenchError("created private JSON ownership/mode is invalid")
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError(f"short write to {path}")
            view = view[written:]
        os.fsync(fd)
        after = os.fstat(fd)
        lexical = path.lstat()
        if (
            stat.S_ISLNK(lexical.st_mode)
            or not stat.S_ISREG(after.st_mode) or after.st_nlink != 1
            or (lexical.st_dev, lexical.st_ino) != (after.st_dev, after.st_ino)
            or (os.name == "posix" and (
                after.st_uid != os.geteuid()
                or stat.S_IMODE(after.st_mode) != 0o600
            ))
        ):
            raise BenchError("private JSON path identity changed during creation")
    finally:
        os.close(fd)


def secure_private_file_token(path: Path, label: str) -> tuple[int, int, int] | None:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise BenchError(f"O_NOFOLLOW is required for {label}")
    try:
        fd = os.open(path, os.O_RDONLY | nofollow)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise BenchError(f"cannot securely inspect {label}: {exc}") from exc
    try:
        metadata = os.fstat(fd)
        if (
            not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
            or (os.name == "posix" and (
                metadata.st_uid != os.geteuid()
                or stat.S_IMODE(metadata.st_mode) != 0o600
            ))
        ):
            raise BenchError(f"{label} must be current-owner mode-0600 single-link regular file")
        return (metadata.st_dev, metadata.st_ino, metadata.st_size)
    finally:
        os.close(fd)


def append_private_jsonl(
    path: Path, row: dict[str, Any], *,
    expected_token: tuple[int, int, int] | None | object = Ellipsis
) -> tuple[int, int, int]:
    data = canonical_json_file_bytes(row)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise BenchError("O_NOFOLLOW is required for append-only inference output")
    if path.is_symlink():
        raise BenchError(f"inference output must not be a symlink: {path}")
    if expected_token is Ellipsis:
        exists = path.exists()
    else:
        exists = expected_token is not None
    flags = os.O_WRONLY | os.O_APPEND | nofollow
    flags |= 0 if exists else os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise BenchError(f"cannot securely append inference output {path}: {exc}") from exc
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise BenchError("inference output must be a single-link regular file")
        if os.name == "posix" and (
            metadata.st_uid != os.geteuid() or stat.S_IMODE(metadata.st_mode) != 0o600
        ):
            raise BenchError("inference output must be owned by current user with mode 0600")
        if expected_token is not Ellipsis and expected_token is not None and (
            metadata.st_dev, metadata.st_ino, metadata.st_size
        ) != expected_token:
            raise BenchError("inference output identity/size changed after prefix validation")
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError(f"short append to {path}")
            view = view[written:]
        os.fsync(fd)
        after = os.fstat(fd)
        lexical = path.lstat()
        if (
            stat.S_ISLNK(lexical.st_mode)
            or not stat.S_ISREG(after.st_mode) or after.st_nlink != 1
            or (lexical.st_dev, lexical.st_ino) != (after.st_dev, after.st_ino)
            or (os.name == "posix" and (
                after.st_uid != os.geteuid()
                or stat.S_IMODE(after.st_mode) != 0o600
            ))
        ):
            raise BenchError("inference output path identity changed during append")
        new_token = (after.st_dev, after.st_ino, after.st_size)
    finally:
        os.close(fd)
    return new_token


def _expected_envelope(schedule: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
    candidate = schedule["configuration"]["candidate"]
    return {
        "schema_version": 1,
        "record_type": "inference",
        "schedule_id": schedule["schedule_id"],
        "run_id": job["run_id"],
        "fixture_id": job["fixture_id"],
        "payload_sha256": job["payload_sha256"],
        "execution_ordinal": job["ordinal"],
        "arm": job["arm"],
        "repetition": job["repetition"],
        "model": MODEL,
        "reasoning": REASONING,
        "schedule_seed": schedule["configuration"]["seed"],
        "timeout_seconds": schedule["configuration"]["timeout_seconds"],
        "candidate_sha256": candidate["sha256"],
        "controller_sha256": schedule["configuration"]["controller"]["sha256"],
        "success": None,
        "score": None,
        "scoring_status": "deferred",
    }


def validate_result_prefix(
    output: Path, schedule: dict[str, Any], claims: Path | None = None
) -> tuple[list[dict[str, Any]], tuple[int, int, int] | None]:
    try:
        data, output_state = read_owner_file_once_with_token(
            output, "inference JSONL", exact_mode=0o600, require_single_link=True
        )
    except BenchError as exc:
        try:
            output.lstat()
        except FileNotFoundError:
            return [], None
        except OSError:
            raise exc
        raise
    if not data or not data.endswith(b"\n") or b"\r" in data:
        raise BenchError("inference JSONL must be nonempty canonical LF-terminated rows")
    raw_lines = data[:-1].split(b"\n")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, raw in enumerate(raw_lines, 1):
        if not raw or len(rows) >= len(schedule["jobs"]):
            raise BenchError("inference JSONL is not an exact schedule prefix")
        row = _decode_json(raw, f"inference row {line_number}")
        if not isinstance(row, dict) or raw != canonical_json_bytes(row):
            raise BenchError(f"inference row {line_number} is not canonical JSON")
        job = schedule["jobs"][len(rows)]
        for key, expected in _expected_envelope(schedule, job).items():
            if row.get(key) != expected:
                raise BenchError(f"inference row {line_number} envelope mismatch for {key}")
        if type(row.get("execution_success")) is not bool:
            raise BenchError(f"inference row {line_number} has no terminal execution status")
        if type(row.get("timed_out")) is not bool:
            raise BenchError(f"inference row {line_number} timed_out is not boolean")
        if row.get("exit_code") is not None and type(row.get("exit_code")) is not int:
            raise BenchError(f"inference row {line_number} exit_code is invalid")
        if not isinstance(row.get("response"), str):
            raise BenchError(f"inference row {line_number} response is not text")
        latency = row.get("latency_seconds")
        if type(latency) not in (int, float) or not math.isfinite(float(latency)) or latency < 0:
            raise BenchError(f"inference row {line_number} latency is invalid")
        route = row.get("route_assertion")
        if not isinstance(route, dict) or set(route) != {"asserted", "subscription", "provider", "model"}:
            raise BenchError(f"inference row {line_number} route assertion shape is invalid")
        if type(route["asserted"]) is not bool or type(route["subscription"]) is not bool:
            raise BenchError(f"inference row {line_number} route assertion booleans are invalid")
        if not isinstance(route["provider"], str) or not isinstance(route["model"], str):
            raise BenchError(f"inference row {line_number} route strings are invalid")
        lifecycle = row.get("lifecycle_assertion")
        lifecycle_keys = {"asserted", "isolated_home", "fresh_session", "cleanup_complete"}
        if not isinstance(lifecycle, dict) or set(lifecycle) != lifecycle_keys or any(
            type(lifecycle[key]) is not bool for key in lifecycle_keys
        ):
            raise BenchError(f"inference row {line_number} lifecycle assertion is invalid")
        usage = row.get("usage")
        usage_keys = {
            "input_tokens", "output_tokens", "cache_read_tokens",
            "cache_write_tokens", "total_tokens", "accounting_complete",
        }
        failure = row.get("failure")
        if row["execution_success"]:
            expected_provider = "OpenAI OAuth" if row["arm"].startswith("jcode") else "openai-codex"
            if route != {
                "asserted": True, "subscription": True,
                "provider": expected_provider, "model": MODEL,
            }:
                raise BenchError(f"successful inference row {line_number} has an unverified route")
            if not all(lifecycle.values()):
                raise BenchError(f"successful inference row {line_number} has an incomplete lifecycle")
            if not isinstance(usage, dict) or set(usage) != usage_keys:
                raise BenchError(f"successful inference row {line_number} usage shape is invalid")
            for key in usage_keys - {"accounting_complete"}:
                if type(usage[key]) is not int or usage[key] < 0:
                    raise BenchError(f"successful inference row {line_number} usage is invalid")
            expected_total = usage["input_tokens"] + usage["output_tokens"]
            if row["arm"] == "prime-agent":
                expected_total += usage["cache_read_tokens"] + usage["cache_write_tokens"]
            if usage["accounting_complete"] is not True or usage["total_tokens"] != expected_total:
                raise BenchError(f"successful inference row {line_number} usage is incomplete")
            if failure is not None:
                raise BenchError(f"successful inference row {line_number} has a failure")
        else:
            if usage is not None:
                raise BenchError(f"failed inference row {line_number} must use null normalized usage")
            if not isinstance(failure, dict) or not isinstance(failure.get("kind"), str) or not failure["kind"]:
                raise BenchError(f"failed inference row {line_number} lacks a typed failure")
        if row["run_id"] in seen:
            raise BenchError(f"duplicate inference run_id at row {line_number}")
        if claims is not None:
            claim_path = claims / f"{job['run_id']}.json"
            done_path = claims / f"{job['run_id']}.done.json"
            claim = load_private_json(claim_path, f"run claim {line_number}")
            done = load_private_json(done_path, f"run completion {line_number}")
            if set(claim) != {"schedule_id", "run_id", "ordinal", "pid"} or claim.get("schedule_id") != schedule["schedule_id"] or claim.get("run_id") != job["run_id"] or claim.get("ordinal") != job["ordinal"] or not _positive_int(claim.get("pid")):
                raise BenchError(f"run claim {line_number} does not match the frozen job")
            if done != {
                "schedule_id": schedule["schedule_id"],
                "run_id": job["run_id"],
                "row_sha256": sha256_bytes(canonical_json_bytes(row)),
            }:
                raise BenchError(f"run completion {line_number} does not match its row")
        seen.add(row["run_id"])
        rows.append(row)
    if claims is not None:
        require_private_directory(claims, "schedule claims directory")
        expected_claim_names = {
            name
            for job in schedule["jobs"][:len(rows)]
            for name in (f"{job['run_id']}.json", f"{job['run_id']}.done.json")
        }
        try:
            entries = list(claims.iterdir())
        except OSError as exc:
            raise BenchError(f"cannot enumerate schedule claims: {exc}") from exc
        actual_claim_names = {entry.name for entry in entries}
        if len(entries) != len(actual_claim_names) or actual_claim_names != expected_claim_names:
            missing = sorted(expected_claim_names - actual_claim_names)
            extra = sorted(actual_claim_names - expected_claim_names)
            raise BenchError(
                "resume claims are not the exact completed-prefix 2N set "
                f"(missing={missing[:3]}, extra={extra[:3]})"
            )
    return rows, output_state


def stage_payload(
    fixture: PublicFixture, run_dir: Path, staged_filename: str
) -> tuple[Path, Path, dict[str, Any]]:
    if STAGED_NAME_RE.fullmatch(staged_filename) is None:
        raise BenchError("refusing an unsafe staged payload basename")
    source_before = sha256_bytes(fixture.payload_data)
    if source_before != fixture.payload_sha256 or len(fixture.payload_data) != fixture.payload_bytes:
        raise BenchError("captured sealed payload bytes failed their frozen identity")
    task_dir = run_dir / "task"
    task_dir.mkdir(mode=0o700, exist_ok=False)
    staged = task_dir / staged_filename
    fd = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        view = memoryview(fixture.payload_data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError("short write while staging captured payload bytes")
            view = view[written:]
        os.fsync(fd)
        if os.name == "posix":
            os.fchmod(fd, 0o444)
    finally:
        os.close(fd)
    initial = {
        "asserted_before": (
            sha256_path(staged) == fixture.payload_sha256
            and sha256_bytes(fixture.payload_data) == fixture.payload_sha256
            and stat.S_IMODE(staged.stat().st_mode) == 0o444
            and list(task_dir.iterdir()) == [staged]
        ),
        "asserted_after": False,
        "expected_sha256": fixture.payload_sha256,
        "staged_sha256_before": sha256_path(staged),
        "staged_sha256_after": None,
        "source_sha256_before": source_before,
        "source_sha256_after": None,
        "staged_mode_before": "0444",
        "staged_mode_after": None,
        "task_directory_single_file_before": True,
        "task_directory_single_file_after": False,
        "staged_filename": staged_filename,
        "same_frozen_filename_across_fixture_arms": True,
    }
    if not initial["asserted_before"]:
        raise BenchError("staged payload failed its initial integrity assertion")
    return task_dir, staged, initial


def finalize_payload(
    fixture: PublicFixture, task_dir: Path, staged: Path, evidence: dict[str, Any]
) -> dict[str, Any]:
    result = dict(evidence)
    errors: list[str] = []
    result["source_sha256_after"] = sha256_bytes(fixture.payload_data)
    try:
        metadata = staged.lstat()
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            raise BenchError("staged payload ceased to be a regular file")
        result["staged_sha256_after"] = sha256_path(staged)
        result["staged_mode_after"] = f"{stat.S_IMODE(metadata.st_mode):04o}"
    except (OSError, BenchError) as exc:
        errors.append(f"staged payload validation failed: {exc}")
    try:
        result["task_directory_single_file_after"] = list(task_dir.iterdir()) == [staged]
    except OSError as exc:
        errors.append(f"task directory validation failed: {exc}")
    result["asserted_after"] = (
        not errors
        and result.get("source_sha256_after") == fixture.payload_sha256
        and result.get("staged_sha256_after") == fixture.payload_sha256
        and result.get("staged_mode_after") == "0444"
        and result.get("task_directory_single_file_after") is True
    )
    result["errors"] = errors
    return result


def _normalized_usage(arm: str, stdout: str, stderr: str, trace: dict[str, Any] | None) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if arm == "jcode-native":
        raw = OOLONG.parse_jcode_usage(stdout, stderr)
        authority = "jcode type=tokens events"
        values = raw
    elif arm == "prime-agent":
        raw = OOLONG.sum_usage_fields(OOLONG.json_objects(stdout), prime=True)
        authority = "prime-agent assistant message_end provider usage"
        values = dict(raw)
    else:
        raw = trace
        authority = (
            "all valid candidate-emitted AZDAJA_MODEL_TRACE rows at every depth; "
            "replay proves retained internal consistency, not provider-signed authenticity"
        )
        values = {} if trace is None else {
            key: trace.get(key) for key in OOLONG.empty_usage()
        }
    complete = all(
        type(values.get(key)) is int and values[key] >= 0
        for key in OOLONG.empty_usage()
    )
    if complete:
        expected_total = values["input_tokens"] + values["output_tokens"]
        if arm == "prime-agent":
            expected_total += values["cache_read_tokens"] + values["cache_write_tokens"]
        complete = values["total_tokens"] == expected_total
    normalized = None if not complete else {
        "input_tokens": values["input_tokens"],
        "output_tokens": values["output_tokens"],
        "cache_read_tokens": values["cache_read_tokens"],
        "cache_write_tokens": values["cache_write_tokens"],
        "total_tokens": values["total_tokens"],
        "accounting_complete": True,
    }
    evidence = {
        "asserted": complete,
        "authority": authority,
        "raw": raw,
        "normalized": normalized,
        "missing_fields": [key for key in OOLONG.empty_usage() if values.get(key) is None],
    }
    return normalized, evidence


def _normalized_route(
    arm: str, stdout: str, auth: dict[str, Any], route_trace: dict[str, Any] | None
) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = OOLONG.runtime_assertion(arm, stdout, route_trace)
    provider = "OpenAI OAuth" if arm.startswith("jcode") else "openai-codex"
    no_transport_errors = not (
        arm == "jcode-azdaja"
        and (route_trace is None or route_trace.get("transport_error_rows") != 0)
    )
    subscription = auth.get("asserted") is True and auth.get("method") == "subscription-oauth"
    asserted = raw.get("asserted") is True and subscription and no_transport_errors
    return {
        "asserted": asserted,
        "subscription": subscription,
        "provider": provider,
        "model": MODEL,
    }, {
        "raw_runtime_route": raw,
        "raw_azdaja_route_trace": route_trace,
        "oauth_preflight": auth,
        "no_transport_error_rows": no_transport_errors,
    }


def capture_trace_artifact_secure(path: Path, label: str) -> dict[str, Any]:
    """Redact and seal one stopped-writer trace through a single O_NOFOLLOW fd."""
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise BenchError(f"this platform cannot securely capture {label}")
    try:
        fd = os.open(path, os.O_RDWR | nofollow)
    except OSError as exc:
        raise BenchError(f"cannot securely open {label} {path}: {exc}") from exc
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise BenchError(f"{label} must be a single-link regular file")
        if os.name == "posix" and (
            metadata.st_uid != os.geteuid() or stat.S_IMODE(metadata.st_mode) != 0o600
        ):
            raise BenchError(f"{label} must be owned by current user with exact mode 0600")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        raw = b"".join(chunks)
        if len(raw) != metadata.st_size:
            raise BenchError(f"{label} changed during its single read")
        try:
            redacted = OOLONG.redact_sensitive(raw.decode("utf-8")).encode("utf-8")
        except UnicodeError as exc:
            raise BenchError(f"{label} is not UTF-8: {exc}") from exc
        if redacted != raw:
            os.lseek(fd, 0, os.SEEK_SET)
            os.ftruncate(fd, 0)
            view = memoryview(redacted)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise OSError(f"short secure rewrite of {label}")
                view = view[written:]
        if os.name == "posix":
            os.fchmod(fd, 0o600)
        os.fsync(fd)
        final = os.fstat(fd)
        lexical = path.lstat()
        if (
            stat.S_ISLNK(lexical.st_mode)
            or not stat.S_ISREG(lexical.st_mode)
            or (lexical.st_dev, lexical.st_ino) != (final.st_dev, final.st_ino)
            or final.st_size != len(redacted)
        ):
            raise BenchError(f"{label} path identity changed during capture")
    finally:
        os.close(fd)
    return {
        "path": str(path),
        "sha256": sha256_bytes(redacted),
        "bytes": len(redacted),
        "mode": "0600",
        "contains_private_raw_trajectory": False,
        "credential_redacted": True,
        "sensitivity": "complete model/tool event stream with credential-shaped values redacted",
    }


def execute_product_arm(
    *,
    job: dict[str, Any],
    fixture: PublicFixture,
    args: argparse.Namespace,
    source_home: Path,
    skill: Path,
    auth_jcode: dict[str, Any],
    auth_prime: dict[str, Any],
    work_root: Path,
) -> dict[str, Any]:
    """Execute one product arm through the bound dataset-neutral OOLONG adapters."""
    run_dir = work_root / f"{job['ordinal']:03d}-{job['run_id'][:16]}-{job['arm']}"
    run_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
    task_dir: Path | None = None
    staged: Path | None = None
    payload_evidence: dict[str, Any] | None = None
    arm_obj: Any = None
    env: dict[str, str] = {}
    trace_paths: dict[str, Path] = {}
    trace_captured: set[str] = set()
    trajectory_artifacts: dict[str, Any] = {}
    retained: set[str] = set()
    cleanup_errors: list[str] = []
    stdout = ""
    stderr = ""
    exit_code: int | None = None
    timed_out = False
    latency = 0.0
    execution_error: str | None = None
    isolated_home = False
    staged_skill: dict[str, Any] | None = None
    wrapper = wrapper_for(job["staged_filename"])
    started_at = time.time()
    auth = auth_jcode if job["arm"].startswith("jcode") else auth_prime

    try:
        task_dir, staged, payload_evidence = stage_payload(
            fixture, run_dir, job["staged_filename"]
        )
        # pathlib's recursive parent creation need not apply 0700 to every new
        # ancestor. Create the HOME root explicitly before either shared adapter
        # copies its sole OAuth credential into the fresh session.
        isolated_home_path = run_dir / (
            "prime-home" if job["arm"] == "prime-agent" else "home"
        )
        isolated_home_path.mkdir(mode=0o700, exist_ok=False)
        if os.name == "posix":
            os.chmod(isolated_home_path, 0o700)
        adapter_fixture = SimpleNamespace(
            metadata={"question": wrapper},
            context_path=fixture.payload_path,
        )
        arm_obj, env, trace_paths = OOLONG.arm_for(
            job["arm"],
            prompt=wrapper,
            args=args,
            root=task_dir,
            fixture=adapter_fixture,
            run_dir=run_dir,
            auth_jcode=auth_jcode,
            auth_prime=auth_prime,
            source_home=source_home,
            skill=skill,
        )
        frozen_executables = getattr(args, "frozen_executables", None)
        if not isinstance(frozen_executables, dict):
            raise BenchError("frozen executable identities are unavailable")
        if job["arm"] == "jcode-azdaja":
            arm_obj.command[0] = str(frozen_executables["azdaja"]["path"])
        elif job["arm"] == "prime-agent":
            prime_bundle = frozen_executables["prime-agent"].get("bundle")
            if not isinstance(prime_bundle, dict):
                raise BenchError("frozen Prime package identity is unavailable")
            env["PI_PACKAGE_DIR"] = str(prime_bundle["root"])
        home = run_dir / ("prime-home" if job["arm"] == "prime-agent" else "home")
        isolated_home = home.is_dir() and (
            os.name != "posix" or stat.S_IMODE(home.stat().st_mode) & 0o077 == 0
        )
        for trace_name, trace_path in trace_paths.items():
            trace_fd = os.open(
                trace_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
            )
            try:
                if os.name == "posix":
                    os.fchmod(trace_fd, 0o600)
            finally:
                os.close(trace_fd)
        try:
            exit_code, stdout, stderr, timed_out, latency = OOLONG.execute(
                arm_obj.command, env, args.timeout, task_dir
            )
        except Exception as exc:
            execution_error = f"{type(exc).__name__}: {exc}"
            stderr = execution_error
        payload_evidence = finalize_payload(
            fixture, task_dir, staged, payload_evidence
        )
        if arm_obj.staged_skill is not None:
            staged_skill = OOLONG.finalize_staged_skill_hashes(arm_obj.staged_skill)
        trajectory_artifacts["stdout"] = OOLONG.write_private_artifact(
            run_dir / "stdout.ndjson", stdout
        )
        trajectory_artifacts["stderr"] = OOLONG.write_private_artifact(
            run_dir / "stderr.log", stderr
        )
        retained.update({"stdout.ndjson", "stderr.log"})
    except Exception as exc:
        execution_error = execution_error or f"{type(exc).__name__}: {exc}"
        stderr = stderr or execution_error
        # Even adapter/setup failures commit exact owner-only streams. Native and
        # Prime stdout are the later scorer's authoritative telemetry sources.
        try:
            if "stdout" not in trajectory_artifacts:
                trajectory_artifacts["stdout"] = OOLONG.write_private_artifact(
                    run_dir / "stdout.ndjson", stdout
                )
                retained.add("stdout.ndjson")
            if "stderr" not in trajectory_artifacts:
                trajectory_artifacts["stderr"] = OOLONG.write_private_artifact(
                    run_dir / "stderr.log", stderr
                )
                retained.add("stderr.log")
        except Exception as artifact_exc:
            cleanup_errors.append(
                f"mandatory stream capture failed: {type(artifact_exc).__name__}: {artifact_exc}"
            )
    finally:
        if arm_obj is not None:
            cleanup_errors.extend(OOLONG.cleanup_run(job["arm"], args, env, run_dir))
        for trace_name, trace_path in trace_paths.items():
            if not trace_path.exists():
                continue
            try:
                trajectory_artifacts[trace_name] = capture_trace_artifact_secure(
                    trace_path, trace_name
                )
                retained.add(trace_path.name)
                trace_captured.add(trace_name)
            except Exception as exc:
                cleanup_errors.append(f"unsafe {trace_name}: {type(exc).__name__}: {exc}")
        try:
            retention = OOLONG.purge_transient_run_state(run_dir, retained, cleanup_errors)
        except Exception as exc:
            cleanup_errors.append(f"retention audit failed: {type(exc).__name__}: {exc}")
            retention = {
                "asserted": False, "credential_homes_deleted": False,
                "retained_entries": [], "retention_allowlist": sorted(retained),
            }

    response = OOLONG.extract_final(job["arm"], stdout)
    model_trace_path = trace_paths.get("azdaja_model_trace")
    trace_usage = (
        OOLONG.parse_azdaja_usage(model_trace_path)
        if "azdaja_model_trace" in trace_captured else None
    )
    route_trace = (
        OOLONG.parse_azdaja_route_evidence(model_trace_path)
        if "azdaja_model_trace" in trace_captured else None
    )
    route, route_evidence = _normalized_route(job["arm"], stdout, auth, route_trace)
    normalized_usage, usage_evidence = _normalized_usage(
        job["arm"], stdout, stderr, trace_usage
    )
    expected_traces = {"azdaja_model_trace", "azdaja_solo_trace"} if job["arm"] == "jcode-azdaja" else set()
    trace_assertion = {
        "asserted": expected_traces.issubset(trace_captured),
        "required": sorted(expected_traces),
        "captured": sorted(trace_captured),
        "missing": sorted(expected_traces - trace_captured),
    }
    if job["arm"] == "jcode-azdaja":
        product_lifecycle = OOLONG.direct_solo_lifecycle_assertion(
            exit_code=exit_code,
            timed_out=timed_out,
            response=response,
            trace_usage=route_trace,
        )
    else:
        product_lifecycle = {"asserted": True, "requirement": "fresh control session"}
    cleanup_complete = retention.get("asserted") is True and not cleanup_errors
    fresh_session = arm_obj is not None and isolated_home
    lifecycle = {
        "asserted": bool(
            isolated_home and fresh_session and cleanup_complete
            and product_lifecycle.get("asserted") is True
        ),
        "isolated_home": isolated_home,
        "fresh_session": fresh_session,
        "cleanup_complete": cleanup_complete,
    }
    if task_dir is not None and staged is not None:
        tool_policy = OOLONG.scan_tool_policy(
            job["arm"], stdout, task_dir=task_dir, context_path=staged,
            forbidden_paths=(fixture.payload_path,),
        )
    else:
        tool_policy = {
            "asserted": False, "events_scanned": 0, "violations": [],
            "policy": "no network or external dataset access in executed events",
            "enforcement": "post-hoc event detection only; not OS-level containment",
            "containment_asserted": False,
        }
    payload_asserted = bool(
        payload_evidence
        and payload_evidence.get("asserted_before") is True
        and payload_evidence.get("asserted_after") is True
    )
    skill_asserted = staged_skill is None or staged_skill.get("asserted_after") is True
    process_asserted = (
        execution_error is None and not timed_out and exit_code == 0 and bool(response.strip())
    )
    execution_success = bool(
        process_asserted
        and route["asserted"]
        and normalized_usage is not None
        and lifecycle["asserted"]
        and trace_assertion["asserted"]
        and payload_asserted
        and skill_asserted
        and tool_policy.get("asserted") is True
    )
    failure: dict[str, Any] | None = None
    if not execution_success:
        if execution_error is not None:
            kind, message = "execution", execution_error
        elif timed_out:
            kind, message = "timeout", "arm exceeded the frozen timeout"
        elif exit_code != 0:
            kind, message = "process_exit", f"process exited {exit_code}"
        elif not response.strip():
            kind, message = "empty_response", "arm returned no answer text"
        elif not route["asserted"]:
            kind, message = "route_assertion", "runtime provider/model/subscription route was not verified"
        elif normalized_usage is None:
            kind, message = "usage_evidence", "runtime token accounting was missing or inconsistent"
        elif not lifecycle["asserted"]:
            kind, message = "lifecycle_assertion", "fresh isolated lifecycle or cleanup was not verified"
        elif not trace_assertion["asserted"]:
            kind, message = "trace_capture", "required product traces were not captured"
        elif not payload_asserted:
            kind, message = "payload_integrity", "sealed/staged payload integrity changed"
        elif not skill_asserted:
            kind, message = "candidate_integrity", "staged candidate changed during execution"
        else:
            kind, message = "tool_policy", "executed event evidence violated the advisory data-access policy"
        failure = {"kind": kind, "message": message}

    command = [] if arm_obj is None else OOLONG.public_command(
        arm_obj.command, 2 if job["arm"] == "jcode-azdaja" else -1
    )
    return {
        "execution_success": execution_success,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "latency_seconds": latency,
        "response": OOLONG.bounded(response),
        "route_assertion": route,
        "usage": normalized_usage if execution_success else None,
        "lifecycle_assertion": lifecycle,
        "failure": failure,
        "arm_evidence": {
            "started_at_unix_s": started_at,
            "timeout_seconds": args.timeout,
            "timed_out": timed_out,
            "exit_code": exit_code,
            "execution_error": execution_error,
            "auth_assertion": auth,
            "route": route_evidence,
            "usage": usage_evidence,
            "product_lifecycle": product_lifecycle,
            "payload_integrity": payload_evidence,
            "candidate_staging": staged_skill,
            "trace_capture": trace_assertion,
            "tool_access_policy": tool_policy,
            "credential_cleanup": retention,
            "cleanup_errors": cleanup_errors,
            "trajectory_artifacts": trajectory_artifacts,
            "telemetry_authority": {
                "route_and_usage": (
                    "stdout artifact" if job["arm"] in {"jcode-native", "prime-agent"}
                    else "azdaja_model_trace artifact"
                ),
                "process": "controller wait status corroborated by stdout/stderr artifacts",
                "controller_fields_are_assertions": True,
            },
            "command": command,
            "wrapper_sha256": sha256_bytes(wrapper.encode("utf-8")),
            "wrapper_identical_across_arms": True,
            "staged_filename": job["staged_filename"],
        },
        "containment": {
            "os_level_asserted": False,
            "disclaimer": (
                "owner-only homes, read-only copies, and post-hoc event auditing are advisory; "
                "this runner is not an OS information-flow or network sandbox"
            ),
            "claim_ledger": "local append-only creation protocol is not authenticated against malicious same-owner deletion/retry; external signing or transparency is future work",
        },
    }


def _create_private_directory(path: Path, label: str, *, exist_ok: bool) -> None:
    try:
        path.mkdir(mode=0o700, parents=True, exist_ok=exist_ok)
    except OSError as exc:
        raise BenchError(f"cannot create {label}: {exc}") from exc
    if os.name == "posix":
        os.chmod(path, 0o700)
    require_private_directory(path, label)


def run_suite(args: argparse.Namespace, suite: PublicSuite) -> int:
    if not args.yes_run_inference:
        raise BenchError("refusing to run inference without --yes-run-inference")
    if args.timeout != 1800:
        raise BenchError("--timeout is frozen at exactly 1800 seconds")
    output = Path(args.output).expanduser().resolve()
    schedule_path = Path(str(output) + ".schedule.json")
    claims_root = Path(str(output) + ".claims")
    work_base = (
        Path(args.work_dir).expanduser().resolve()
        if args.work_dir else Path(str(output) + ".artifacts")
    )
    if output in {suite.path, *(fixture.payload_path for fixture in suite.fixtures)}:
        raise BenchError("--output must not overwrite any sealed public artifact")

    home_raw = os.environ.get("HOME")
    if not home_raw:
        raise BenchError("HOME must identify the login home containing subscription OAuth")
    source_home = Path(home_raw).expanduser().resolve(strict=True)
    if not source_home.is_dir():
        raise BenchError("HOME must identify a directory")
    args.jcode = OOLONG.ensure_executable(args.jcode, "jcode")
    args.prime_agent = OOLONG.ensure_executable(args.prime_agent, "prime-agent")
    source_jcode = args.jcode
    source_prime_agent = args.prime_agent
    skill = OOLONG.validate_skill(args.azdaja_skill)
    source_executables = {
        "jcode": OOLONG.executable_identity(args.jcode, "jcode"),
        "prime-agent": OOLONG.executable_identity(args.prime_agent, "prime-agent"),
        "azdaja": OOLONG.executable_identity(str(skill / "azdaja"), "azdaja"),
    }
    args.executable_identities = source_executables
    candidate_source_path = str(skill)
    source_controller = controller_identity()

    if args.resume:
        if not schedule_path.exists():
            raise BenchError("--resume requires the frozen schedule sidecar")
        schedule = load_private_json(schedule_path, "frozen RULER schedule")
        frozen_configuration = schedule.get("configuration")
        if not isinstance(frozen_configuration, dict):
            raise BenchError("frozen schedule configuration is invalid")
        candidate = frozen_configuration.get("candidate")
        frozen_candidate_source_path = frozen_configuration.get("candidate_source_path")
        controller = frozen_configuration.get("controller")
        controller_source_paths = frozen_configuration.get("controller_source_paths")
        executables = frozen_configuration.get("executables")
        if frozen_candidate_source_path != candidate_source_path:
            raise BenchError("active candidate source path differs from frozen metadata")
        frozen_skill = validate_candidate_snapshot(candidate)
        for name, component in candidate["components"].items():
            source_data = read_owner_file_once(
                skill / name, f"active candidate {name}",
                exact_mode=(0o700 if name == "azdaja" else 0o600),
                require_single_link=True,
            )
            if sha256_bytes(source_data) != component["sha256"] or len(source_data) != component["bytes"]:
                raise BenchError(f"active candidate source drifted: {name}")
        if not isinstance(controller, dict) or not isinstance(controller_source_paths, dict) or not isinstance(executables, dict):
            raise BenchError("frozen immutable identities are invalid")
        # Resuming further inference requires the active source/controller and
        # product executables to remain byte-identical to those initially frozen.
        if source_controller.get("sha256") != controller.get("sha256"):
            raise BenchError("active controller source drifted after schedule freeze")
        for name, identity in source_executables.items():
            if name not in executables or any(
                identity.get(key) != executables[name].get(key)
                for key in ("sha256", "bytes", "version")
            ):
                raise BenchError(f"active {name} executable drifted after schedule freeze")
        validate_schedule(
            schedule, suite, seed=args.seed, timeout=args.timeout,
            candidate=candidate, candidate_source_path=candidate_source_path,
            controller=controller, controller_source_paths=controller_source_paths,
            executables=executables,
        )
    else:
        for path, label in (
            (output, "inference output"), (schedule_path, "schedule"),
            (claims_root, "claims root"), (work_base, "artifact root"),
        ):
            if path.exists() or path.is_symlink():
                raise BenchError(f"fresh {label} path must not exist: {path}")
        _create_private_directory(work_base, "artifact root", exist_ok=False)
        identity_root = work_base / "identity"
        _create_private_directory(identity_root, "immutable identity root", exist_ok=False)
        controller_root = identity_root / "controller"
        executable_root = identity_root / "executables"
        candidate_root = identity_root / "candidate"
        _create_private_directory(controller_root, "controller snapshots", exist_ok=False)
        _create_private_directory(executable_root, "executable snapshots", exist_ok=False)
        _create_private_directory(candidate_root, "candidate snapshot", exist_ok=False)
        candidate = snapshot_candidate(skill, candidate_root)
        frozen_skill = validate_candidate_snapshot(candidate)
        controller, controller_source_paths = snapshot_controller(controller_root)
        executables = snapshot_executables(source_executables, executable_root)
        if controller["sha256"] != source_controller["sha256"]:
            raise BenchError("immutable controller snapshot differs from active source")
        schedule = build_schedule(
            suite, seed=args.seed, timeout=args.timeout, candidate=candidate,
            candidate_source_path=candidate_source_path,
            controller=controller, controller_source_paths=controller_source_paths,
            executables=executables,
        )
        atomic_create_private_json(schedule_path, schedule)

    if OOLONG.validate_skill(str(frozen_skill)) != frozen_skill:
        raise BenchError("frozen candidate validation returned an unexpected path")
    skill = frozen_skill
    args.frozen_executables = executables
    args.executable_identities = executables
    _create_private_directory(claims_root, "claims root", exist_ok=args.resume)
    claims = claims_root / schedule["schedule_id"]
    _create_private_directory(claims, "schedule claims directory", exist_ok=args.resume)
    completed, output_state = validate_result_prefix(output, schedule, claims)
    if len(completed) == len(schedule["jobs"]):
        return 0 if all(row["execution_success"] for row in completed) else 1

    auth_jcode = OOLONG.preflight_jcode(source_home, source_jcode)
    auth_prime = OOLONG.preflight_prime(source_home)
    # Product turns invoke only byte-frozen executable snapshots. OAuth preflight
    # deliberately used the active source CLI immediately before this handoff.
    args.jcode = str(executables["jcode"]["path"])
    args.prime_agent = str(executables["prime-agent"]["path"])
    kernel_python = source_home / ".prime" / "agent" / "kernel-venv" / "bin" / "python"
    if not kernel_python.is_file() or not os.access(kernel_python, os.X_OK):
        raise BenchError(f"Prime Agent kernel venv is not ready: {kernel_python}")
    _create_private_directory(work_base, "artifact root", exist_ok=True)
    schedule_root = work_base / f"schedule-{schedule['schedule_id']}"
    _create_private_directory(schedule_root, "schedule artifact directory", exist_ok=args.resume)
    work_root = schedule_root / "runs"
    _create_private_directory(work_root, "run artifact directory", exist_ok=args.resume)
    by_id = {fixture.fixture_id: fixture for fixture in suite.fixtures}

    for job in schedule["jobs"][len(completed):]:
        # Revalidate all file identities and the public payload immediately before
        # claiming a turn. OAuth is refreshed/preflighted for the relevant arm.
        if controller_identity().get("sha256") != controller.get("sha256"):
            raise BenchError("controller identity drifted after schedule freeze")
        validate_candidate_snapshot(candidate)
        for label, frozen in executables.items():
            path = Path(frozen["path"])
            frozen_data = read_owner_file_once(
                path, f"immutable {label} executable snapshot", exact_mode=0o500
            )
            if len(frozen_data) != frozen["bytes"] or sha256_bytes(frozen_data) != frozen["sha256"]:
                raise BenchError(f"{label} immutable executable snapshot drifted after schedule freeze")
            if label == "prime-agent":
                validate_prime_bundle_identity(frozen.get("bundle"), path)
        fixture = by_id[job["fixture_id"]]
        # The validated manifest identity and payload bytes were captured before
        # freeze; turns never reopen mutable sealed inputs.
        if (
            sha256_bytes(fixture.payload_data) != fixture.payload_sha256
            or len(fixture.payload_data) != fixture.payload_bytes
        ):
            raise BenchError("captured scheduled payload identity drifted")
        if job["arm"].startswith("jcode"):
            auth_jcode = OOLONG.preflight_jcode(source_home, source_jcode)
        else:
            auth_prime = OOLONG.preflight_prime(source_home)
        claim_path = claims / f"{job['run_id']}.json"
        done_path = claims / f"{job['run_id']}.done.json"
        if claim_path.exists() or done_path.exists():
            raise BenchError(
                f"orphan claim/completion makes resume indeterminate; refusing duplicate inference: {job['run_id']}"
            )
        atomic_create_private_json(claim_path, {
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "ordinal": job["ordinal"],
            "pid": os.getpid(),
        })
        try:
            execution = execute_product_arm(
                job=job, fixture=fixture, args=args, source_home=source_home,
                skill=skill, auth_jcode=auth_jcode, auth_prime=auth_prime,
                work_root=work_root,
            )
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            emergency = work_root / f"{job['ordinal']:03d}-{job['run_id'][:16]}-{job['arm']}"
            emergency.mkdir(mode=0o700, exist_ok=True)
            if os.name == "posix":
                os.chmod(emergency, 0o700)
            stdout_path = emergency / "stdout.ndjson"
            stderr_path = emergency / "stderr.log"
            emergency_artifacts = {
                "stdout": (
                    capture_trace_artifact_secure(stdout_path, "stdout")
                    if stdout_path.exists()
                    else OOLONG.write_private_artifact(stdout_path, "")
                ),
                "stderr": (
                    capture_trace_artifact_secure(stderr_path, "stderr")
                    if stderr_path.exists()
                    else OOLONG.write_private_artifact(stderr_path, message)
                ),
            }
            execution = {
                "execution_success": False,
                "timed_out": False,
                "exit_code": None,
                "latency_seconds": 0.0,
                "response": "",
                "route_assertion": {
                    "asserted": False,
                    "subscription": False,
                    "provider": "OpenAI OAuth" if job["arm"].startswith("jcode") else "openai-codex",
                    "model": MODEL,
                },
                "usage": None,
                "lifecycle_assertion": {
                    "asserted": False, "isolated_home": False,
                    "fresh_session": False, "cleanup_complete": False,
                },
                "failure": {"kind": "controller", "message": message},
                "arm_evidence": {
                    "controller_exception": message,
                    "trajectory_artifacts": emergency_artifacts,
                    "telemetry_authority": {
                        "route_and_usage": "mandatory empty stdout artifact after controller failure",
                        "process": "controller assertion",
                        "controller_fields_are_assertions": True,
                    },
                    "staged_filename": job["staged_filename"],
                },
                "containment": {
                    "os_level_asserted": False,
                    "disclaimer": "controller failure; no OS-level containment is asserted",
                    "claim_ledger": "local append-only creation protocol is not authenticated against malicious same-owner deletion/retry; external signing or transparency is future work",
                },
            }
        row = {**_expected_envelope(schedule, job), **execution}
        output_state = append_private_jsonl(output, row, expected_token=output_state)
        atomic_create_private_json(done_path, {
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "row_sha256": sha256_bytes(canonical_json_bytes(row)),
        })
        print(json.dumps({
            "ordinal": job["ordinal"], "fixture_id": job["fixture_id"],
            "arm": job["arm"], "execution_success": row["execution_success"],
            "scoring_status": "deferred", "latency_seconds": row["latency_seconds"],
        }, sort_keys=True), flush=True)
    rows, final_output_state = validate_result_prefix(output, schedule, claims)
    if final_output_state != output_state:
        raise BenchError("inference output state changed after final append")
    return 0 if all(row["execution_success"] for row in rows) else 1


def parser() -> argparse.ArgumentParser:
    here = Path(__file__).resolve().parent
    value = argparse.ArgumentParser(
        description=(
            "Run the exact sealed 90-fixture RULER suite with three subscription-OAuth arms. "
            "This command performs inference but never opens gold or scores rows."
        )
    )
    value.add_argument("--manifest", required=True, help="sealed public manifest.json (never gold.json)")
    value.add_argument("--output", required=True, help="fresh or exactly resumable append-only JSONL")
    value.add_argument("--resume", action="store_true", help="resume the exact frozen prefix")
    value.add_argument("--seed", type=int, default=DEFAULT_SEED, help="balanced block randomization seed")
    value.add_argument("--timeout", type=int, choices=(1800,), default=1800, help="frozen per-arm timeout (1800 seconds)")
    value.add_argument("--jcode", default="jcode", help="jcode executable")
    value.add_argument("--prime-agent", default="prime-agent", help="prime-agent executable")
    value.add_argument(
        "--azdaja-skill",
        default=str(Path.home() / ".jcode" / "skills" / "azdaja"),
        help="candidate skill containing azdaja, config.toml, and SKILL.md",
    )
    value.add_argument("--work-dir", help="fresh owner-only artifact directory")
    value.add_argument(
        "--yes-run-inference", action="store_true",
        help="required explicit acknowledgement that 270 subscription model turns will run",
    )
    return value


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    suite = load_public_manifest(args.manifest)
    return run_suite(args, suite)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BenchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
