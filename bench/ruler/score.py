#!/usr/bin/env python3
"""Fail-closed deferred scoring for ``ruler-exact-mini-v1``.

Gold is deliberately not opened until the public manifest, frozen schedule,
all inference rows, and every claim/completion receipt have been validated.
The module uses only the Python standard library so scoring cannot silently
change with a scientific-Python dependency update.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import hmac
import itertools
import json
import math
import os
import random
import re
import stat
import string
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence

SCHEMA_VERSION = 1
SUITE_ID = "ruler-exact-mini-v1"
TASKS = ("niah_multikey_3", "vt", "fwe")
TARGET_LENGTHS = (8192, 32768, 131072)
EXPECTED_PER_CELL = 10
EXPECTED_FIXTURES = len(TASKS) * len(TARGET_LENGTHS) * EXPECTED_PER_CELL
ARMS = ("jcode-native", "jcode-azdaja", "prime-agent")
MODEL = "gpt-5.6-luna"
REASONING = "medium"
FULL_WORKFLOW = "full-v1"
PARALLEL_WIDTH = 4
PARALLEL_WIDTH_SCOPE = "global"
RUNNER_PARALLELISM_AUTHORITY = (
    "controller time.perf_counter_ns half-open arm intervals from one pre-launch "
    "batch origin; active-at-start counted under the controller lock"
)
RUNNER_PARALLELISM_KEYS = {
    "schema_version", "configured_global_width", "scope",
    "observed_active_at_start", "observed_peak_concurrency",
    "batch_started_at_unix_s", "monotonic_arm_start_offset_ms",
    "monotonic_arm_end_offset_ms", "controller_arm_wall_ms",
    "overall_makespan_ms", "authority",
}
WRAPPER_TEMPLATE_SHA256 = "8999a98d32e56e6e019b1908844fe081ee243cb967aa9e7462351a71b544260d"
STAGED_NAME_RE = re.compile(r"[0-9a-f]{32}\.txt\Z")
RUN_ID_DOMAIN = b"ruler-run-v1\0"
ISOLATED_GENERATION_BOOTSTRAP = (
    "import runpy,sys;"
    "site,script=sys.argv[1:3];"
    "sys.path[:]=[site,script.rsplit('/',1)[0]]+sys.path;"
    "sys.argv=sys.argv[2:];"
    "runpy.run_path(script,run_name='__main__')"
)
DEFAULT_BOOTSTRAP_SEED = 20260813
DEFAULT_BOOTSTRAP_RESAMPLES = 100000
RULER_URL = "https://github.com/NVIDIA/RULER.git"
RULER_COMMIT = "c3f5e3b4f87f97e048793bb510a3a6b19a46bf3a"
TASK_RESERVES = {"niah_multikey_3": 128, "vt": 30, "fwe": 50}
REQUIREMENTS_LOCK_SHA256 = "82d442a1cffdf8bf5b2d9e27f9e6432f3b3328f6813bf4086499d68bbb1ba1c9"
TOKENIZER_BLOB_SHA256 = "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"
TOKENIZER_CACHE_NAME = "9b5ad71b2ce5302211f9c61530b329a4922fc6a4"
THIRD_PARTY_NOTICES_SHA256 = "c5356d79adccad2264910a9df17792ed10fb1d452444ec2a8a96c1691f8152b2"
EXPECTED_NLTK_RESOURCE_HASHES = {
    "tokenizers/punkt.zip": "51c3078994aeaf650bfc8e028be4fb42b4a0d177d41c012b6a983979653660ec",
    "tokenizers/punkt_tab.zip": "e57f64187974277726a3417ca6f181ec5403676c717672eef6a748a7b20e0106",
}
EXPECTED_PACKAGE_VERSIONS = {
    "certifi": "2026.7.22", "charset-normalizer": "3.5.0", "click": "8.4.2",
    "idna": "3.18", "joblib": "1.5.3", "nltk": "3.9.2", "numpy": "2.3.5",
    "PyYAML": "6.0.3", "regex": "2026.7.19", "requests": "2.34.2",
    "scipy": "1.16.3", "tenacity": "9.1.2", "tiktoken": "0.12.0",
    "tqdm": "4.67.1", "urllib3": "2.7.0", "wonderwords": "3.0.1",
}
EXPECTED_RULER_SOURCE_HASHES = {
    "LICENSE": "43070e2d4e532684de521b885f385d0841030efa2b1a20bafb76133a5e1379c1",
    "scripts/synthetic.yaml": "34bc71dcacdc41a829a170f04b528fbf48d62c616338005ab4991680fbf8cb0b",
    "scripts/data/prepare.py": "f2d210860fbf5c640cb41ed104c7a923c9f4043f6e6c354277daacc73afc643d",
    "scripts/data/template.py": "2e82d85152212136fffcd5624b158a2c75fd5036ec1c537f4b21eeb78fd18069",
    "scripts/data/manifest_utils.py": "ecac79322f28ce9a12388b12e35d560ecb7cdad6b9888467a5a13b0eff2db91e",
    "scripts/data/tokenizer.py": "c2e4bfab607eef87a86334558303c1811bc8e93f22a5c4b129f302726d2357a4",
    "scripts/data/synthetic/constants.py": "6296e901d495ec6200dc3f68993ea13d8282e3c0dbe1a8c47967f111105d1fde",
    "scripts/data/synthetic/niah.py": "e9cada0a7660d274fe73a1338a90a7087e17b630169f1aaf14a8d3221c6805b5",
    "scripts/data/synthetic/variable_tracking.py": "9aac483420e158d116ab63fc43b9606bdb284ac0c053288c30776d5c365530e5",
    "scripts/data/synthetic/freq_words_extraction.py": "29b7af97ffdd2122fde348df20cd02add390a21cd6d64b6fd66c8663dc487f67",
    "scripts/eval/synthetic/constants.py": "6740467c17b8dc06b6b30f4f97e54ce8de81db0dd879f1538d0b6b5727f4bd5f",
}
EXPECTED_REDISTRIBUTION_FILES = {
    "LICENSE.NVIDIA-RULER": EXPECTED_RULER_SOURCE_HASHES["LICENSE"],
    "THIRD_PARTY_NOTICES.md": THIRD_PARTY_NOTICES_SHA256,
}
ARTIFACT_FILENAMES = {
    "stdout": "stdout.ndjson",
    "stderr": "stderr.log",
    "azdaja_model_trace": "azdaja-model-usage.jsonl",
    "azdaja_solo_trace": "azdaja-solo-trace.log",
}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
SAFE_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,191}\Z")
ROOT_LEAK_MIN_CHARS = 100
_ROLLING_HASH_BASE = 1_000_003
_ROLLING_HASH_MASK = (1 << 64) - 1
OPERATIONAL_FAILURE_PRECEDENCE = (
    "root_context_leak",
    "adapter_parser",
    "transport",
    "timeout",
    "depth",
    "monty_subset_tax",
    "other_execution",
)


class ScoreError(RuntimeError):
    """An artifact is incomplete, mutable, ambiguous, or identity-mismatched."""


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
    except (UnicodeEncodeError, ValueError, TypeError) as exc:
        raise ScoreError(f"value cannot be encoded as canonical JSON: {exc}") from exc


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


def _rolling_windows(text: str, width: int) -> Iterable[tuple[int, int]]:
    if width <= 0 or len(text) < width:
        return
    power = pow(_ROLLING_HASH_BASE, width - 1, 1 << 64)
    value = 0
    for char in text[:width]:
        value = (value * _ROLLING_HASH_BASE + ord(char) + 1) & _ROLLING_HASH_MASK
    yield 0, value
    for offset in range(1, len(text) - width + 1):
        value = (
            (value - (ord(text[offset - 1]) + 1) * power) * _ROLLING_HASH_BASE
            + ord(text[offset + width - 1]) + 1
        ) & _ROLLING_HASH_MASK
        yield offset, value


def exact_unicode_substring_present(
    public_payload: str, root_transcript: str, *, minimum_chars: int = ROOT_LEAK_MIN_CHARS
) -> bool:
    """Rolling-hash candidate search with collision-proof exact verification."""
    if type(minimum_chars) is not int or minimum_chars <= 0:
        raise ScoreError("root-context leak threshold must be a positive integer")
    if len(public_payload) < minimum_chars or len(root_transcript) < minimum_chars:
        return False
    if len(public_payload) <= len(root_transcript):
        indexed, scanned = public_payload, root_transcript
    else:
        indexed, scanned = root_transcript, public_payload
    candidates: dict[int, list[int]] = {}
    for offset, value in _rolling_windows(indexed, minimum_chars):
        candidates.setdefault(value, []).append(offset)
    for scanned_offset, value in _rolling_windows(scanned, minimum_chars):
        for indexed_offset in candidates.get(value, ()):
            if all(
                scanned[scanned_offset + delta] == indexed[indexed_offset + delta]
                for delta in range(minimum_chars)
            ):
                return True
    return False


def root_context_leak_audit(payload_data: bytes, trace_data: bytes) -> dict[str, Any]:
    """Scan exact decoded code points; never normalize, exempt, or retain a match."""
    try:
        payload = payload_data.decode("utf-8")
        trace = trace_data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ScoreError(f"root-context leak inputs must be exact UTF-8: {exc}") from exc
    return {
        "applicable": True,
        "scanned": True,
        "detected": exact_unicode_substring_present(payload, trace),
        "minimum_match_chars": ROOT_LEAK_MIN_CHARS,
        "payload_chars": len(payload),
        "trace_chars": len(trace),
        "payload_sha256": sha256_bytes(payload_data),
        "trace_sha256": sha256_bytes(trace_data),
        "algorithm": "uint64 polynomial rolling hash plus exact Unicode-code-point verification",
        "normalization": "none",
        "exemptions": "none",
        "matched_text_retained": False,
    }


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value}")


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _decode_json(text: str, label: str) -> Any:
    try:
        value = json.loads(
            text,
            object_pairs_hook=_object_no_duplicates,
            parse_constant=_reject_constant,
        )
        stack = [value]
        while stack:
            item = stack.pop()
            if isinstance(item, str):
                item.encode("utf-8")
            elif isinstance(item, dict):
                stack.extend(item.keys())
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
        return value
    except (json.JSONDecodeError, UnicodeEncodeError, ValueError) as exc:
        raise ScoreError(f"cannot parse {label}: {exc}") from exc


def require_private_regular(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise ScoreError(f"{label} is missing or unreadable: {path}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ScoreError(f"{label} must be a regular non-symlink file: {path}")
    if os.name == "posix":
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ScoreError(f"{label} must be owner-only: {path}")
        if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
            raise ScoreError(f"{label} must be owned by the scoring user: {path}")
        if metadata.st_nlink != 1:
            raise ScoreError(f"{label} must have exactly one hard link: {path}")


def require_private_directory(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise ScoreError(f"{label} is missing or unreadable: {path}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ScoreError(f"{label} must be a non-symlink directory: {path}")
    if os.name == "posix":
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ScoreError(f"{label} must be owner-only: {path}")
        if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
            raise ScoreError(f"{label} must be owned by the scoring user: {path}")


def read_regular_bytes(path: Path, label: str) -> bytes:
    lexical = lexical_absolute(path)
    _reject_symlink_components(lexical)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(lexical, flags)
    except OSError as exc:
        raise ScoreError(f"cannot open {label} {lexical}: {exc}") from exc
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ScoreError(f"{label} must be a single-link regular file")
        if os.name == "posix" and (
            stat.S_IMODE(metadata.st_mode) & 0o077
            or (hasattr(os, "getuid") and metadata.st_uid != os.getuid())
        ):
            raise ScoreError(f"{label} must be owner-only and owned by the scoring user")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def read_private_bytes(path: Path, label: str) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise ScoreError(f"{label} is missing or unreadable: {path}: {exc}") from exc
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise ScoreError(f"{label} must be a regular file: {path}")
        if os.name == "posix":
            if stat.S_IMODE(metadata.st_mode) & 0o077:
                raise ScoreError(f"{label} must be owner-only: {path}")
            if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
                raise ScoreError(f"{label} must be owned by the scoring user: {path}")
            if metadata.st_nlink != 1:
                raise ScoreError(f"{label} must have exactly one hard link: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def read_private_bytes_identity(
    path: Path, label: str, *, exact_mode: int
) -> tuple[bytes, os.stat_result]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise ScoreError(f"this platform cannot securely open {label} with O_NOFOLLOW")
    try:
        fd = os.open(path, os.O_RDONLY | nofollow)
    except OSError as exc:
        raise ScoreError(f"{label} is missing or unreadable: {path}: {exc}") from exc
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ScoreError(f"{label} must be a single-link regular file: {path}")
        if os.name == "posix" and (
            stat.S_IMODE(metadata.st_mode) != exact_mode
            or (hasattr(os, "getuid") and metadata.st_uid != os.getuid())
        ):
            raise ScoreError(f"{label} must be owned with exact mode {exact_mode:04o}: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        data = b"".join(chunks)
        if len(data) != metadata.st_size:
            raise ScoreError(f"{label} changed during its bound read: {path}")
        return data, metadata
    finally:
        os.close(fd)


def load_json_object(
    path: Path,
    label: str,
    *,
    canonical: bool = True,
    private: bool = True,
) -> dict[str, Any]:
    try:
        data = read_private_bytes(path, label) if private else path.read_bytes()
        text = data.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise ScoreError(f"cannot read {label} {path}: {exc}") from exc
    value = _decode_json(text, label)
    if not isinstance(value, dict):
        raise ScoreError(f"{label} must contain a JSON object")
    if canonical and data != canonical_json_file_bytes(value):
        raise ScoreError(f"{label} is not canonical compact JSON with one final newline")
    return value


def _strict_json_equal(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            _strict_json_equal(actual[key], value) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _strict_json_equal(left, right) for left, right in zip(actual, expected)
        )
    if isinstance(expected, tuple):
        return len(actual) == len(expected) and all(
            _strict_json_equal(left, right) for left, right in zip(actual, expected)
        )
    return actual == expected


def _require_equal(actual: Any, expected: Any, label: str) -> None:
    if not _strict_json_equal(actual, expected):
        raise ScoreError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def _nonnegative_number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(float(value)) and value >= 0


def _validate_runner_parallel_observation(
    value: Any, index: int, *, expected_width: int
) -> None:
    if (
        not isinstance(value, dict)
        or set(value) != RUNNER_PARALLELISM_KEYS
        or value.get("schema_version") != 1
        or value.get("configured_global_width") != expected_width
        or value.get("scope") != PARALLEL_WIDTH_SCOPE
        or value.get("authority") != RUNNER_PARALLELISM_AUTHORITY
        or type(value.get("observed_active_at_start")) is not int
        or not 1 <= value["observed_active_at_start"] <= expected_width
        or type(value.get("observed_peak_concurrency")) is not int
        or not value["observed_active_at_start"] <= value["observed_peak_concurrency"] <= expected_width
        or not _nonnegative_number(value.get("batch_started_at_unix_s"))
        or not _nonnegative_number(value.get("monotonic_arm_start_offset_ms"))
        or not _nonnegative_number(value.get("monotonic_arm_end_offset_ms"))
        or not _nonnegative_number(value.get("controller_arm_wall_ms"))
        or not _nonnegative_number(value.get("overall_makespan_ms"))
        or value["monotonic_arm_end_offset_ms"]
        < value["monotonic_arm_start_offset_ms"]
        or value["overall_makespan_ms"] < value["monotonic_arm_end_offset_ms"]
        or not math.isclose(
            value["controller_arm_wall_ms"],
            value["monotonic_arm_end_offset_ms"]
            - value["monotonic_arm_start_offset_ms"],
            rel_tol=0.0,
            abs_tol=1e-9,
        )
    ):
        raise ScoreError(f"inference row {index} runner parallelism is invalid")


def _validate_runner_parallel_batch(
    rows: Sequence[dict[str, Any]], *, expected_width: int
) -> dict[str, Any]:
    observations: list[dict[str, Any]] = []
    for index, row in enumerate(rows, 1):
        evidence = row.get("arm_evidence")
        value = evidence.get("runner_parallelism") if isinstance(evidence, dict) else None
        _validate_runner_parallel_observation(value, index, expected_width=expected_width)
        observations.append(value)
    origins = {item["batch_started_at_unix_s"] for item in observations}
    starts = [item["monotonic_arm_start_offset_ms"] for item in observations]
    peaks = {item["observed_peak_concurrency"] for item in observations}
    makespans = {item["overall_makespan_ms"] for item in observations}
    if (
        len(origins) != 1 or len(set(starts)) != len(starts)
        or len(peaks) != 1 or len(makespans) != 1
    ):
        raise ScoreError("runner parallel batch totals or interval identities are ambiguous")
    ordered = sorted(observations, key=lambda item: item["monotonic_arm_start_offset_ms"])
    prior: list[dict[str, Any]] = []
    observed_peak = 0
    for item in ordered:
        active = 1 + sum(
            previous["monotonic_arm_end_offset_ms"]
            > item["monotonic_arm_start_offset_ms"]
            for previous in prior
        )
        if active != item["observed_active_at_start"] or active > expected_width:
            raise ScoreError(
                "runner observed concurrency disagrees with half-open arm intervals"
            )
        observed_peak = max(observed_peak, active)
        prior.append(item)
    overall_makespan_ms = max(
        item["monotonic_arm_end_offset_ms"] for item in observations
    )
    if peaks != {observed_peak} or makespans != {overall_makespan_ms}:
        raise ScoreError("runner peak concurrency or makespan does not recompute exactly")
    return {
        "configured_global_width": expected_width,
        "scope": PARALLEL_WIDTH_SCOPE,
        "observed_peak_concurrency": observed_peak,
        "overall_makespan_ms": overall_makespan_ms,
        "authority": RUNNER_PARALLELISM_AUTHORITY,
    }


def manifest_identity_sha256(manifest: dict[str, Any]) -> str:
    """Hash the canonical public identity without its later gold commitment.

    The final manifest commits the exact gold file.  To avoid an impossible
    cyclic pair of exact-file hashes, gold commits this canonical pre-gold view.
    Generator JSON artifacts include exactly one final newline, so it is part of
    this identity too.
    """
    identity = copy.deepcopy(manifest)
    if "gold_sha256" not in identity:
        raise ScoreError("public manifest has no gold_sha256 commitment")
    del identity["gold_sha256"]
    return sha256_bytes(canonical_json_file_bytes(identity))


def _resolve_payload(parent: Path, raw: Any, fixture_id: str) -> Path:
    expected = f"payloads/{fixture_id}.txt"
    if raw != expected:
        raise ScoreError(
            f"fixture {fixture_id} payload path must be exactly {expected!r}"
        )
    require_private_directory(parent, "sealed suite root")
    payload_dir = parent / "payloads"
    require_private_directory(payload_dir, "sealed payload directory")
    if os.name == "posix" and stat.S_IMODE(payload_dir.stat().st_mode) != 0o700:
        raise ScoreError("sealed payload directory must have exact mode 0700")
    unresolved = payload_dir / f"{fixture_id}.txt"
    if unresolved.is_symlink():
        raise ScoreError(f"fixture {fixture_id} payload must not be a symlink")
    try:
        resolved = unresolved.resolve(strict=True)
        root = parent.resolve(strict=True)
    except OSError as exc:
        raise ScoreError(f"fixture {fixture_id} payload is missing: {exc}") from exc
    if resolved.parent != (root / "payloads"):
        raise ScoreError(f"fixture {fixture_id} payload escapes the sealed payload directory")
    require_private_regular(resolved, f"fixture {fixture_id} payload")
    if os.name == "posix" and stat.S_IMODE(resolved.stat().st_mode) != 0o600:
        raise ScoreError(f"fixture {fixture_id} payload must have exact mode 0600")
    return resolved


def load_public_manifest(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    path = lexical_absolute(path)
    _reject_symlink_components(path)
    if path.name != "manifest.json" or path.is_symlink():
        raise ScoreError("public suite manifest must be the non-symlink manifest.json entry")
    require_private_directory(path.parent, "sealed suite root")
    try:
        root_mode = stat.S_IMODE(path.parent.stat().st_mode)
        manifest_mode = stat.S_IMODE(path.stat().st_mode)
    except OSError as exc:
        raise ScoreError(f"cannot stat public suite manifest: {exc}") from exc
    if os.name == "posix" and (root_mode != 0o700 or manifest_mode != 0o600):
        raise ScoreError("sealed suite root/manifest modes must be exactly 0700/0600")
    document = load_json_object(path, "public suite manifest")
    if set(document) != {
        "schema_version", "record_type", "suite_id", "upstream_commit", "source",
        "configuration", "provenance_commitments", "redistribution_files",
        "fixtures", "gold_sha256",
    }:
        raise ScoreError("public manifest has an unexpected object shape")
    _require_equal(document.get("schema_version"), SCHEMA_VERSION, "manifest schema_version")
    _require_equal(
        document.get("record_type"),
        "ruler_exact_mini_public_manifest",
        "manifest record_type",
    )
    _require_equal(document.get("suite_id"), SUITE_ID, "manifest suite_id")
    _require_equal(document.get("upstream_commit"), RULER_COMMIT, "manifest upstream commit")
    _require_equal(
        document.get("source"),
        {"name": "NVIDIA/RULER", "url": RULER_URL, "commit": RULER_COMMIT},
        "manifest source identity",
    )
    _require_equal(
        document.get("redistribution_files"), EXPECTED_REDISTRIBUTION_FILES,
        "manifest redistribution-file commitments",
    )
    parent = path.parent
    expected_root_entries = {
        "manifest.json", "payloads", *EXPECTED_REDISTRIBUTION_FILES
    }
    try:
        actual_root_entries = {entry.name for entry in os.scandir(path.parent)}
    except OSError as exc:
        raise ScoreError(f"cannot inventory sealed suite root: {exc}") from exc
    if actual_root_entries != expected_root_entries:
        raise ScoreError("sealed suite root does not have the exact public inventory")
    for filename, expected_sha256 in EXPECTED_REDISTRIBUTION_FILES.items():
        redistribution_path = path.parent / filename
        _reject_symlink_components(redistribution_path)
        data = read_private_bytes(redistribution_path, f"redistribution file {filename}")
        if os.name == "posix" and stat.S_IMODE(redistribution_path.stat().st_mode) != 0o600:
            raise ScoreError(f"redistribution file must have exact mode 0600: {filename}")
        _require_equal(
            sha256_bytes(data), expected_sha256,
            f"redistribution file {filename} SHA-256",
        )
    configuration = document.get("configuration")
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
    _require_equal(configuration, expected_configuration, "manifest configuration")
    commitments = document.get("provenance_commitments")
    if not isinstance(commitments, dict) or set(commitments) != {
        "generation_plan_sha256", "requirements_lock_sha256",
        "tokenizer_blob_sha256", "ruler_source_files",
    }:
        raise ScoreError("manifest provenance commitments have an unexpected shape")
    if not _is_sha256(commitments.get("generation_plan_sha256")):
        raise ScoreError("manifest generation-plan commitment is invalid")
    _require_equal(
        commitments.get("requirements_lock_sha256"), REQUIREMENTS_LOCK_SHA256,
        "manifest pinned requirements lock hash",
    )
    _require_equal(
        commitments.get("tokenizer_blob_sha256"), TOKENIZER_BLOB_SHA256,
        "manifest pinned tokenizer blob hash",
    )
    _require_equal(
        commitments.get("ruler_source_files"), EXPECTED_RULER_SOURCE_HASHES,
        "manifest pinned RULER source-file hashes",
    )
    if not _is_sha256(document.get("gold_sha256")):
        raise ScoreError("manifest gold_sha256 must be lowercase SHA-256")
    entries = document.get("fixtures")
    if not isinstance(entries, list) or len(entries) != EXPECTED_FIXTURES:
        count = len(entries) if isinstance(entries, list) else "invalid"
        raise ScoreError(
            f"manifest must contain exactly {EXPECTED_FIXTURES} fixtures, got {count}"
        )

    by_id: dict[str, dict[str, Any]] = {}
    seen_paths: set[Path] = set()
    seen_payload_hashes: set[str] = set()
    cells: Counter[tuple[str, int]] = Counter()
    for index, raw_entry in enumerate(entries, 1):
        if not isinstance(raw_entry, dict):
            raise ScoreError(f"manifest fixture {index} is not an object")
        if set(raw_entry) != {
            "id", "task", "target_length", "payload", "payload_sha256",
            "payload_bytes", "construction_tokens", "row_length",
        }:
            raise ScoreError(f"manifest fixture {index} has an unexpected object shape")
        fixture_id = raw_entry.get("id")
        if not isinstance(fixture_id, str) or SAFE_ID_RE.fullmatch(fixture_id) is None:
            raise ScoreError(f"manifest fixture {index} id is invalid or unsafe")
        if fixture_id in by_id:
            raise ScoreError(f"duplicate manifest fixture id: {fixture_id}")
        task = raw_entry.get("task")
        target_length = raw_entry.get("target_length")
        if task not in TASKS or target_length not in TARGET_LENGTHS:
            raise ScoreError(f"fixture {fixture_id} has an invalid task/target_length cell")
        payload_sha = raw_entry.get("payload_sha256")
        if not _is_sha256(payload_sha):
            raise ScoreError(f"fixture {fixture_id} payload_sha256 is invalid")
        if not _positive_int(raw_entry.get("payload_bytes")):
            raise ScoreError(f"fixture {fixture_id} payload_bytes must be positive")
        construction_tokens = raw_entry.get("construction_tokens")
        if not _positive_int(construction_tokens) or construction_tokens > target_length:
            raise ScoreError(f"fixture {fixture_id} construction_tokens is invalid")
        row_length = raw_entry.get("row_length")
        if (
            not _positive_int(row_length)
            or row_length > target_length
            or construction_tokens + TASK_RESERVES[task] != row_length
        ):
            raise ScoreError(f"fixture {fixture_id} official row_length identity is invalid")
        payload = _resolve_payload(parent, raw_entry.get("payload"), fixture_id)
        payload_data = read_private_bytes(payload, f"fixture {fixture_id} payload")
        actual_bytes = len(payload_data)
        actual_hash = sha256_bytes(payload_data)
        _require_equal(actual_bytes, raw_entry["payload_bytes"], f"fixture {fixture_id} payload bytes")
        _require_equal(actual_hash, payload_sha, f"fixture {fixture_id} payload SHA-256")
        try:
            payload_data.decode("utf-8")
        except UnicodeError as exc:
            raise ScoreError(f"fixture {fixture_id} payload is not readable UTF-8: {exc}") from exc
        if payload in seen_paths:
            raise ScoreError(f"duplicate manifest payload path: {payload}")
        if payload_sha in seen_payload_hashes:
            raise ScoreError(f"duplicate manifest payload identity: {payload_sha}")
        seen_paths.add(payload)
        seen_payload_hashes.add(payload_sha)
        cells[(task, target_length)] += 1
        normalized = dict(raw_entry)
        normalized["_payload_path"] = payload
        normalized["_payload_bytes"] = payload_data
        by_id[fixture_id] = normalized

    expected_payload_names = {
        f"{fixture_id}.txt" for fixture_id in by_id
    }
    try:
        payload_entries = list((parent / "payloads").iterdir())
    except OSError as exc:
        raise ScoreError(f"cannot enumerate sealed payload directory: {exc}") from exc
    actual_payload_names = {entry.name for entry in payload_entries}
    if (
        len(payload_entries) != len(actual_payload_names)
        or actual_payload_names != expected_payload_names
    ):
        raise ScoreError("sealed payload directory inventory is not exact")
    expected_cells = {(task, length) for task in TASKS for length in TARGET_LENGTHS}
    if set(cells) != expected_cells or any(cells[cell] != EXPECTED_PER_CELL for cell in expected_cells):
        raise ScoreError(
            "manifest is not the exact 9-cell x 10-fixture ruler-exact-mini-v1 grid"
        )
    return document, by_id




def _read_identity_snapshot(path: Path, label: str, *, exact_mode: int) -> bytes:
    if not path.is_absolute():
        raise ScoreError(f"{label} path must be absolute")
    path = lexical_absolute(path)
    data = read_regular_bytes(path, label)
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise ScoreError(f"cannot stat {label}: {exc}") from exc
    if os.name == "posix" and stat.S_IMODE(metadata.st_mode) != exact_mode:
        raise ScoreError(f"{label} must have exact mode {exact_mode:04o}")
    return data


def _normalized_version(value: str) -> str | None:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    return lines[-1] if lines else None


def _validate_prime_bundle(bundle: Any, executable_path: Path) -> Path:
    if not isinstance(bundle, dict) or set(bundle) != {
        "root", "entrypoint", "aggregate_sha256", "files"
    }:
        raise ScoreError("Prime executable bundle identity has an unexpected shape")
    if not isinstance(bundle["root"], str) or not Path(bundle["root"]).is_absolute():
        raise ScoreError("Prime executable bundle root is invalid")
    root = lexical_absolute(Path(bundle["root"]))
    require_private_directory(root, "Prime executable bundle root")
    if root.name != "prime-agent-package":
        raise ScoreError("Prime executable bundle root name is invalid")
    if os.name == "posix" and stat.S_IMODE(root.stat().st_mode) != 0o700:
        raise ScoreError("Prime executable bundle root must have exact mode 0700")
    entrypoint = bundle["entrypoint"]
    if entrypoint != "dist/bundle/cli.js" or executable_path != root / entrypoint:
        raise ScoreError("Prime executable bundle entrypoint is invalid")
    entries = bundle["files"]
    if not isinstance(entries, list) or not entries:
        raise ScoreError("Prime executable bundle inventory is empty or invalid")
    observed_names: list[str] = []
    entrypoint_item: dict[str, Any] | None = None
    for index, item in enumerate(entries, 1):
        if not isinstance(item, dict) or set(item) != {
            "relative_path", "kind", "sha256", "bytes", "mode"
        }:
            raise ScoreError(f"Prime executable bundle entry {index} has an unexpected shape")
        name = item["relative_path"]
        pure = PurePosixPath(name) if isinstance(name, str) else PurePosixPath(".")
        kind = item["kind"]
        if (
            not isinstance(name, str)
            or not name
            or pure.is_absolute()
            or ".." in pure.parts
            or pure.as_posix() != name
            or name in observed_names
            or kind not in {"directory", "file", "materialized_internal_symlink"}
        ):
            raise ScoreError(f"Prime executable bundle entry {index} identity is invalid")
        path = root.joinpath(*pure.parts)
        try:
            metadata = path.lstat()
        except OSError as exc:
            raise ScoreError(f"cannot stat Prime bundle entry {name}: {exc}") from exc
        if kind == "directory":
            if (
                not stat.S_ISDIR(metadata.st_mode)
                or item["sha256"] is not None
                or item["bytes"] != 0
                or item["mode"] != "0700"
                or (os.name == "posix" and (
                    stat.S_IMODE(metadata.st_mode) != 0o700
                    or (hasattr(os, "getuid") and metadata.st_uid != os.getuid())
                ))
            ):
                raise ScoreError(f"Prime bundle directory identity is invalid: {name}")
        else:
            expected_mode = "0500" if name == entrypoint else "0400"
            if (
                not stat.S_ISREG(metadata.st_mode)
                or metadata.st_nlink != 1
                or not _is_sha256(item["sha256"])
                or not _nonnegative_int(item["bytes"])
                or item["mode"] != expected_mode
            ):
                raise ScoreError(f"Prime bundle retained file identity is invalid: {name}")
            data = _read_identity_snapshot(
                path, f"Prime executable bundle file {name}",
                exact_mode=int(expected_mode, 8),
            )
            _require_equal(len(data), item["bytes"], f"Prime executable bundle file {name} bytes")
            _require_equal(
                sha256_bytes(data), item["sha256"],
                f"Prime executable bundle file {name} SHA-256",
            )
            if name == entrypoint:
                entrypoint_item = item
        observed_names.append(name)
    if observed_names != sorted(observed_names):
        raise ScoreError("Prime executable bundle inventory is not lexicographically ordered")

    actual_names: list[str] = []
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            children = list(os.scandir(directory))
        except OSError as exc:
            raise ScoreError(f"cannot enumerate Prime executable bundle: {exc}") from exc
        for child in children:
            relative = Path(child.path).relative_to(root).as_posix()
            try:
                metadata = child.stat(follow_symlinks=False)
            except OSError as exc:
                raise ScoreError(f"cannot stat Prime bundle entry {relative}: {exc}") from exc
            if child.is_symlink() or not (
                stat.S_ISDIR(metadata.st_mode) or stat.S_ISREG(metadata.st_mode)
            ):
                raise ScoreError(f"Prime bundle contains a symlink or special entry: {relative}")
            actual_names.append(relative)
            if stat.S_ISDIR(metadata.st_mode):
                pending.append(Path(child.path))
    if sorted(actual_names) != observed_names:
        raise ScoreError("Prime executable bundle recursive inventory is not exact")
    if entrypoint_item is None:
        raise ScoreError("Prime executable bundle inventory omits its entrypoint")
    _require_equal(
        bundle["aggregate_sha256"], sha256_bytes(canonical_json_bytes(entries)),
        "Prime executable bundle aggregate SHA-256",
    )
    return root


def _schedule_fixture_id(item: dict[str, Any], label: str) -> str:
    value = item.get("fixture_id")
    if not isinstance(value, str):
        raise ScoreError(f"{label} fixture_id is invalid")
    return value


def validate_schedule(
    schedule: dict[str, Any],
    manifest_path: Path,
    manifest: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], tuple[str, ...]]:
    _require_equal(schedule.get("schema_version"), SCHEMA_VERSION, "schedule schema_version")
    _require_equal(schedule.get("record_type"), "ruler_frozen_schedule", "schedule record_type")
    schedule_id = schedule.get("schedule_id")
    if not _is_sha256(schedule_id):
        raise ScoreError("schedule_id must be lowercase SHA-256")

    identity = copy.deepcopy(schedule)
    identity.pop("schedule_id", None)
    identity_jobs = identity.get("jobs")
    if not isinstance(identity_jobs, list):
        raise ScoreError("schedule jobs must be a list")
    for job in identity_jobs:
        if not isinstance(job, dict):
            raise ScoreError("schedule job must be an object")
        job.pop("run_id", None)
    computed = sha256_bytes(canonical_json_bytes(identity))
    _require_equal(schedule_id, computed, "frozen schedule SHA-256 identity")

    if set(schedule) != {
        "schema_version", "record_type", "suite", "configuration", "jobs", "schedule_id"
    }:
        raise ScoreError("schedule has an unexpected object shape")
    suite = schedule.get("suite")
    configuration = schedule.get("configuration")
    if not isinstance(suite, dict) or not isinstance(configuration, dict):
        raise ScoreError("schedule must contain suite and configuration objects")
    if set(suite) != {"suite_id", "manifest_sha256", "fixtures"}:
        raise ScoreError("schedule suite binding has an unexpected object shape")
    if set(configuration) != {
        "model", "reasoning", "arms", "repetitions", "seed", "timeout_seconds",
        "workflow", "workflow_fixture_ids", "workflow_fixture_ids_sha256",
        "parallel_width", "configured_global_width", "parallel_width_scope",
        "wrapper_template_sha256", "candidate", "candidate_source_path",
        "controller", "controller_source_paths", "executables", "containment",
    }:
        raise ScoreError("schedule configuration has an unexpected object shape")
    _require_equal(suite.get("suite_id"), SUITE_ID, "schedule suite_id")
    _require_equal(
        suite.get("manifest_sha256"), sha256_bytes(canonical_json_file_bytes(manifest)),
        "schedule public manifest SHA-256",
    )
    scheduled_fixtures = suite.get("fixtures")
    if not isinstance(scheduled_fixtures, list) or len(scheduled_fixtures) != EXPECTED_FIXTURES:
        raise ScoreError("schedule suite fixture identity list is incomplete")
    scheduled_by_id: dict[str, dict[str, Any]] = {}
    staged_names: set[str] = set()
    for index, item in enumerate(scheduled_fixtures, 1):
        if not isinstance(item, dict):
            raise ScoreError(f"schedule fixture {index} is not an object")
        if set(item) != {
            "fixture_id", "payload_sha256", "task", "target_length", "staged_filename"
        }:
            raise ScoreError(f"schedule fixture {index} has an unexpected object shape")
        fixture_id = _schedule_fixture_id(item, f"schedule fixture {index}")
        staged_name = item["staged_filename"]
        if (
            not isinstance(staged_name, str)
            or STAGED_NAME_RE.fullmatch(staged_name) is None
            or staged_name in staged_names
        ):
            raise ScoreError(f"schedule fixture {index} staged filename is invalid or duplicate")
        staged_names.add(staged_name)
        if fixture_id in scheduled_by_id or fixture_id not in fixtures:
            raise ScoreError(f"schedule fixture identity is duplicate or unknown: {fixture_id}")
        public = fixtures[fixture_id]
        for key in ("payload_sha256", "task", "target_length"):
            _require_equal(item.get(key), public.get(key), f"schedule fixture {fixture_id} {key}")
        scheduled_by_id[fixture_id] = item
    if set(scheduled_by_id) != set(fixtures):
        raise ScoreError("schedule fixture ids differ from the public manifest")

    arms_raw = configuration.get("arms")
    if not isinstance(arms_raw, list) or any(not isinstance(x, str) for x in arms_raw):
        raise ScoreError("schedule arms are invalid")
    arms = tuple(arms_raw)
    _require_equal(arms, ARMS, "schedule frozen arm order")
    _require_equal(configuration.get("repetitions"), 1, "schedule repetitions")
    _require_equal(configuration.get("model"), MODEL, "schedule model")
    _require_equal(configuration.get("reasoning"), REASONING, "schedule reasoning")
    _require_equal(configuration.get("workflow"), FULL_WORKFLOW, "schedule scored workflow")
    _require_equal(configuration.get("parallel_width"), PARALLEL_WIDTH, "schedule parallel width")
    _require_equal(
        configuration.get("configured_global_width"), PARALLEL_WIDTH,
        "schedule configured global width",
    )
    _require_equal(
        configuration.get("parallel_width_scope"), PARALLEL_WIDTH_SCOPE,
        "schedule parallel width scope",
    )
    if type(configuration.get("seed")) is not int:
        raise ScoreError("schedule seed must be an integer")
    _require_equal(configuration.get("timeout_seconds"), 1800, "schedule timeout_seconds")
    _require_equal(
        configuration.get("wrapper_template_sha256"), WRAPPER_TEMPLATE_SHA256,
        "schedule wrapper template hash",
    )
    _require_equal(
        configuration.get("containment"),
        {
            "os_level_asserted": False,
            "disclaimer": "owner-only isolation and event auditing are advisory, not OS-level containment",
            "claim_ledger": "local append-only creation protocol is not authenticated against malicious same-owner deletion/retry; external signing or transparency is future work",
        },
        "schedule containment disclosure",
    )
    if not isinstance(configuration.get("executables"), dict):
        raise ScoreError("schedule executable identities must be an object")
    controller = configuration.get("controller")
    if not isinstance(controller, dict) or not _is_sha256(controller.get("sha256")):
        raise ScoreError("schedule controller identity is invalid")
    candidate_source_path = configuration.get("candidate_source_path")
    if (
        not isinstance(candidate_source_path, str)
        or not candidate_source_path
        or not Path(candidate_source_path).is_absolute()
    ):
        raise ScoreError("schedule candidate source path metadata is invalid")
    candidate = configuration.get("candidate")
    if not isinstance(candidate, dict) or set(candidate) != {
        "sha256", "snapshot_root", "components"
    }:
        raise ScoreError("schedule candidate identity has an unexpected shape")
    candidate_components = candidate["components"]
    if (
        not isinstance(candidate_components, dict)
        or set(candidate_components) != {"azdaja", "config.toml", "SKILL.md"}
        or not isinstance(candidate["snapshot_root"], str)
        or not Path(candidate["snapshot_root"]).is_absolute()
    ):
        raise ScoreError("schedule candidate snapshot identity is invalid")
    candidate_snapshot_root = lexical_absolute(Path(candidate["snapshot_root"]))
    require_private_directory(candidate_snapshot_root, "candidate snapshot directory")
    if os.name == "posix" and stat.S_IMODE(candidate_snapshot_root.stat().st_mode) != 0o700:
        raise ScoreError("candidate snapshot directory must have exact mode 0700")
    candidate_bound: dict[str, dict[str, Any]] = {}
    for name, component in candidate_components.items():
        expected_mode = "0500" if name == "azdaja" else "0400"
        if (
            not isinstance(component, dict)
            or set(component) != {"path", "sha256", "bytes", "mode"}
            or not isinstance(component["path"], str)
            or not Path(component["path"]).is_absolute()
            or not _is_sha256(component["sha256"])
            or not _positive_int(component["bytes"])
            or component["mode"] != expected_mode
        ):
            raise ScoreError(f"schedule candidate component {name} is invalid")
        component_path = lexical_absolute(Path(component["path"]))
        if component_path != candidate_snapshot_root / name:
            raise ScoreError(f"schedule candidate component {name} path is not exact")
        data = _read_identity_snapshot(
            component_path, f"schedule candidate component {name}",
            exact_mode=int(expected_mode, 8),
        )
        _require_equal(
            len(data), component["bytes"], f"schedule candidate component {name} bytes"
        )
        _require_equal(
            sha256_bytes(data), component["sha256"],
            f"schedule candidate component {name} SHA-256",
        )
        candidate_bound[name] = {
            "sha256": component["sha256"], "bytes": component["bytes"],
            "mode": component["mode"],
        }
    try:
        candidate_entries = {entry.name for entry in candidate_snapshot_root.iterdir()}
    except OSError as exc:
        raise ScoreError(f"cannot enumerate candidate snapshot directory: {exc}") from exc
    if candidate_entries != set(candidate_components):
        raise ScoreError("candidate snapshot directory inventory is not exact")
    _require_equal(
        candidate["sha256"],
        sha256_bytes(canonical_json_bytes(dict(sorted(candidate_bound.items())))),
        "schedule candidate aggregate identity",
    )
    source_paths = configuration["controller_source_paths"]
    if (
        not isinstance(source_paths, dict)
        or set(source_paths) != {"ruler_runner", "oolong_execution_module"}
        or any(not isinstance(path, str) or not Path(path).is_absolute() for path in source_paths.values())
    ):
        raise ScoreError("schedule controller source path metadata is invalid")
    controller = configuration["controller"]
    if not isinstance(controller, dict) or set(controller) != {"sha256", "components"}:
        raise ScoreError("schedule controller identity has an unexpected shape")
    controller_components = controller["components"]
    if not isinstance(controller_components, dict) or set(controller_components) != {
        "ruler_runner", "oolong_execution_module"
    }:
        raise ScoreError("schedule controller component identity set is invalid")
    controller_bound: dict[str, dict[str, Any]] = {}
    controller_snapshot_parents: set[Path] = set()
    for name, component in controller_components.items():
        if (
            not isinstance(component, dict)
            or set(component) != {"path", "sha256", "bytes"}
            or not isinstance(component["path"], str)
            or not component["path"]
            or not _is_sha256(component["sha256"])
            or not _positive_int(component["bytes"])
        ):
            raise ScoreError(f"schedule controller component {name} is invalid")
        component_path = lexical_absolute(Path(component["path"]))
        controller_snapshot_parents.add(component_path.parent)
        component_data = _read_identity_snapshot(
            component_path, f"schedule controller component {name}", exact_mode=0o500
        )
        _require_equal(
            len(component_data), component["bytes"],
            f"schedule controller component {name} byte count",
        )
        _require_equal(
            sha256_bytes(component_data), component["sha256"],
            f"schedule controller component {name} file hash",
        )
        controller_bound[name] = {
            "sha256": component["sha256"], "bytes": component["bytes"]
        }
    _require_equal(
        controller["sha256"],
        sha256_bytes(canonical_json_bytes(dict(sorted(controller_bound.items())))),
        "schedule controller aggregate identity",
    )
    if len(controller_snapshot_parents) != 1:
        raise ScoreError("schedule controller snapshots are not confined to one directory")
    controller_snapshot_root = next(iter(controller_snapshot_parents))
    require_private_directory(controller_snapshot_root, "controller snapshot directory")
    if os.name == "posix" and stat.S_IMODE(controller_snapshot_root.stat().st_mode) != 0o700:
        raise ScoreError("controller snapshot directory must have exact mode 0700")
    try:
        controller_entries = {entry.name for entry in controller_snapshot_root.iterdir()}
    except OSError as exc:
        raise ScoreError(f"cannot enumerate controller snapshot directory: {exc}") from exc
    if controller_entries != {path.name for path in map(lexical_absolute, map(Path, (
        controller_components["ruler_runner"]["path"],
        controller_components["oolong_execution_module"]["path"],
    )))}:
        raise ScoreError("controller snapshot directory inventory is not exact")
    executables = configuration["executables"]
    if set(executables) != {"jcode", "azdaja", "prime-agent"}:
        raise ScoreError("schedule executable identity set is incomplete")
    executable_snapshot_root: Path | None = None
    expected_executable_entries: set[str] = set()
    for name, identity_entry in executables.items():
        if (
            not isinstance(identity_entry, dict)
            or set(identity_entry) != {
                "path", "sha256", "bytes", "version", "version_command", "bundle", "smoke"
            }
            or not _is_sha256(identity_entry.get("sha256"))
            or not _positive_int(identity_entry.get("bytes"))
            or not isinstance(identity_entry.get("path"), str)
            or not identity_entry["path"]
            or not isinstance(identity_entry.get("version"), str)
            or not identity_entry["version"]
            or not isinstance(identity_entry.get("version_command"), list)
            or not identity_entry["version_command"]
            or any(not isinstance(part, str) for part in identity_entry["version_command"])
        ):
            raise ScoreError(f"schedule executable identity for {name} is invalid")
        executable_path = lexical_absolute(Path(identity_entry["path"]))
        executable_data = _read_identity_snapshot(
            executable_path, f"schedule executable {name}", exact_mode=0o500
        )
        _require_equal(
            len(executable_data), identity_entry["bytes"],
            f"schedule executable {name} byte count",
        )
        _require_equal(
            sha256_bytes(executable_data), identity_entry["sha256"],
            f"schedule executable {name} file hash",
        )
        smoke = identity_entry["smoke"]
        if name == "prime-agent":
            if not isinstance(smoke, dict) or set(smoke) != {
                "command", "returncode", "stdout", "stderr", "matched_source_version"
            }:
                raise ScoreError("Prime executable smoke receipt has an unexpected shape")
            if (
                smoke["command"] != identity_entry["version_command"]
                or smoke["command"] != [identity_entry["path"], "--version"]
                or smoke["returncode"] != 0
                or not isinstance(smoke["stdout"], str)
                or not isinstance(smoke["stderr"], str)
                or smoke["matched_source_version"] is not True
            ):
                raise ScoreError("Prime executable smoke receipt is invalid")
            source_version = _normalized_version(identity_entry["version"])
            frozen_version = _normalized_version(smoke["stdout"] + "\n" + smoke["stderr"])
            if source_version is None or frozen_version != source_version:
                raise ScoreError("Prime executable smoke version does not match source")
            bundle_root = _validate_prime_bundle(identity_entry["bundle"], executable_path)
            candidate_root = bundle_root.parent
            expected_executable_entries.add(bundle_root.name)
            bundle_files = identity_entry["bundle"]["files"]
            entrypoint_item = next(
                item for item in bundle_files
                if item["relative_path"] == identity_entry["bundle"]["entrypoint"]
            )
            _require_equal(
                {"sha256": identity_entry["sha256"], "bytes": identity_entry["bytes"]},
                {"sha256": entrypoint_item["sha256"], "bytes": entrypoint_item["bytes"]},
                "Prime top-level entrypoint identity",
            )
        else:
            if identity_entry["bundle"] is not None or smoke is not None:
                raise ScoreError(f"schedule executable {name} must not declare a bundle/smoke")
            candidate_root = executable_path.parent
            expected_executable_entries.add(executable_path.name)
        if executable_snapshot_root is None:
            executable_snapshot_root = candidate_root
        elif candidate_root != executable_snapshot_root:
            raise ScoreError("schedule executable snapshots are not confined to one directory")

    assert executable_snapshot_root is not None
    if (
        executable_snapshot_root == controller_snapshot_root
        or executable_snapshot_root.parent != controller_snapshot_root.parent
    ):
        raise ScoreError("schedule identity snapshot hierarchy is invalid")
    require_private_directory(executable_snapshot_root, "executable snapshot directory")
    if os.name == "posix" and stat.S_IMODE(executable_snapshot_root.stat().st_mode) != 0o700:
        raise ScoreError("executable snapshot directory must have exact mode 0700")
    try:
        executable_entries = {entry.name for entry in executable_snapshot_root.iterdir()}
    except OSError as exc:
        raise ScoreError(f"cannot enumerate executable snapshot directory: {exc}") from exc
    if executable_entries != expected_executable_entries:
        raise ScoreError("executable snapshot directory inventory is not exact")
    candidate_binary = candidate_components["azdaja"]
    executed_binary = executables["azdaja"]
    for key in ("sha256", "bytes"):
        _require_equal(
            candidate_binary[key], executed_binary[key],
            f"candidate azdaja component equals executed Azdaja {key}",
        )
    identity_root = executable_snapshot_root.parent
    require_private_directory(identity_root, "immutable identity root")
    if (
        candidate_snapshot_root.parent != identity_root
        or controller_snapshot_root.parent != identity_root
        or candidate_snapshot_root == controller_snapshot_root
    ):
        raise ScoreError("candidate/controller/executable snapshot hierarchy is invalid")
    try:
        identity_entries = {entry.name for entry in identity_root.iterdir()}
    except OSError as exc:
        raise ScoreError(f"cannot enumerate immutable identity root: {exc}") from exc
    if identity_entries != {
        candidate_snapshot_root.name, controller_snapshot_root.name,
        executable_snapshot_root.name,
    }:
        raise ScoreError("immutable identity root inventory is not exact")

    jobs = schedule.get("jobs")
    assert isinstance(jobs, list)
    expected_count = EXPECTED_FIXTURES * len(ARMS)
    if len(jobs) != expected_count:
        raise ScoreError(f"schedule must have exactly {expected_count} jobs")
    expected_grid = {(fixture_id, arm, 1) for fixture_id in fixtures for arm in arms}
    observed_grid: set[tuple[str, str, int]] = set()
    seen_run_ids: set[str] = set()
    for index, job in enumerate(jobs, 1):
        if not isinstance(job, dict):
            raise ScoreError(f"schedule job {index} is not an object")
        if set(job) != {
            "ordinal", "fixture_id", "payload_sha256", "task", "target_length",
            "staged_filename", "repetition", "arm", "run_id",
        }:
            raise ScoreError(f"schedule job {index} has an unexpected object shape")
        _require_equal(job.get("ordinal"), index, f"schedule job {index} ordinal")
        if type(job.get("repetition")) is not int:
            raise ScoreError(f"schedule job {index} repetition must be an integer")
        fixture_id = job.get("fixture_id")
        arm = job.get("arm")
        repetition = job.get("repetition")
        cell = (fixture_id, arm, repetition)
        if cell not in expected_grid or cell in observed_grid:
            raise ScoreError(f"schedule job {index} is duplicate or outside the frozen grid")
        public = fixtures[fixture_id]
        for key in ("payload_sha256", "task", "target_length"):
            _require_equal(job.get(key), public.get(key), f"schedule job {index} {key}")
        _require_equal(
            job.get("staged_filename"), scheduled_by_id[fixture_id]["staged_filename"],
            f"schedule job {index} staged filename",
        )
        run_id = job.get("run_id")
        if not _is_sha256(run_id) or run_id in seen_run_ids:
            raise ScoreError(f"schedule job {index} run_id is invalid or duplicate")
        base_job = dict(job)
        del base_job["run_id"]
        expected_run_id = sha256_bytes(
            RUN_ID_DOMAIN + schedule_id.encode("ascii") + canonical_json_bytes(base_job)
        )
        _require_equal(run_id, expected_run_id, f"schedule job {index} run_id")
        observed_grid.add(cell)
        seen_run_ids.add(run_id)
    if observed_grid != expected_grid:
        raise ScoreError("schedule is not a complete frozen fixture/arm grid")

    rng = random.Random(configuration["seed"])
    expected_fixture_order = list(fixtures)
    rng.shuffle(expected_fixture_order)
    expected_arm_orders = list(itertools.permutations(ARMS)) * 15
    rng.shuffle(expected_arm_orders)
    workflow_ids = configuration.get("workflow_fixture_ids")
    expected_workflow_ids = list(expected_fixture_order)
    if workflow_ids != expected_workflow_ids:
        raise ScoreError("schedule workflow fixture IDs are not the exact seeded full order")
    _require_equal(
        configuration.get("workflow_fixture_ids_sha256"),
        sha256_bytes(canonical_json_bytes(expected_workflow_ids)),
        "schedule workflow fixture ID list hash",
    )
    reconstructed = [
        (fixture_id, arm)
        for fixture_id, order in zip(expected_fixture_order, expected_arm_orders)
        for arm in order
    ]
    observed_order = [(job["fixture_id"], job["arm"]) for job in jobs]
    _require_equal(
        observed_order, reconstructed,
        "schedule exact seeded fixture/permutation order",
    )

    # The runner promises three consecutive arms for each fixture.  Require the
    # six orderings exactly 15 times each rather than accepting order bias.
    permutations: Counter[tuple[str, ...]] = Counter()
    for start in range(0, len(jobs), len(arms)):
        group = jobs[start : start + len(arms)]
        fixture_ids = {item["fixture_id"] for item in group}
        if len(fixture_ids) != 1:
            raise ScoreError("schedule does not keep each fixture's three arms consecutive")
        order = tuple(item["arm"] for item in group)
        if set(order) != set(arms):
            raise ScoreError("schedule fixture group does not contain every arm once")
        permutations[order] += 1
    expected_permutation_n = EXPECTED_FIXTURES // math.factorial(len(arms))
    if set(permutations) != set(itertools.permutations(arms)) or any(
        count != expected_permutation_n for count in permutations.values()
    ):
        raise ScoreError("schedule does not balance all six arm permutations 15 times")
    return jobs, arms


def load_run_rows(path: Path) -> list[dict[str, Any]]:
    try:
        lines = read_private_bytes(path, "frozen inference JSONL").splitlines(keepends=True)
    except OSError as exc:
        raise ScoreError(f"cannot read frozen inference JSONL: {exc}") from exc
    if not lines:
        raise ScoreError("frozen inference JSONL is empty")
    rows: list[dict[str, Any]] = []
    for line_number, data in enumerate(lines, 1):
        if not data.endswith(b"\n") or not data[:-1].strip():
            raise ScoreError(f"inference row {line_number} is blank or lacks final newline")
        try:
            text = data.decode("utf-8")
        except UnicodeError as exc:
            raise ScoreError(f"inference row {line_number} is not UTF-8: {exc}") from exc
        value = _decode_json(text, f"inference row {line_number}")
        if not isinstance(value, dict):
            raise ScoreError(f"inference row {line_number} is not an object")
        if data != canonical_json_file_bytes(value):
            raise ScoreError(f"inference row {line_number} is not canonical JSON")
        rows.append(value)
    return rows


def _nonnegative_int(value: Any) -> bool:
    return type(value) is int and value >= 0


def _json_lines(data: bytes, label: str) -> list[dict[str, Any]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ScoreError(f"{label} is not UTF-8") from exc
    objects: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        value = _decode_json(line, f"{label} line {line_number}")
        if not isinstance(value, dict):
            raise ScoreError(f"{label} line {line_number} is not an object")
        objects.append(value)
    return objects


def _json_objects_authoritative(data: bytes, label: str) -> list[dict[str, Any]]:
    """Parse every nonempty authority-stream line; never skip malformed evidence."""
    return _json_lines(data, label)


def _independent_route(arm: str, evidence: dict[str, bytes]) -> bool:
    if arm == "jcode-azdaja":
        rows = _json_lines(evidence["azdaja_model_trace"], "Azdaja model trace")
        successful = [row for row in rows if "error" not in row]
        return (
            bool(successful)
            and any(row.get("depth") == 0 for row in successful)
            and all(
                type(row.get("depth")) is int
                and row["depth"] >= 0
                and isinstance(row.get("provider"), str)
                and row["provider"].lower().startswith("openai")
                and row.get("model") == MODEL
                for row in successful
            )
            and all("error" not in row for row in rows)
        )
    rows = _json_objects_authoritative(evidence["stdout"], f"{arm} stdout")
    if arm == "jcode-native":
        done = [row for row in rows if (row.get("type") or row.get("ev")) == "done"]
        return bool(done) and done[-1].get("provider") == "OpenAI" and done[-1].get("model") == MODEL
    assistant_events = [
        row["message"] for row in rows
        if row.get("type") == "message_end"
        and isinstance(row.get("message"), dict)
        and row["message"].get("role") == "assistant"
    ]
    return bool(assistant_events) and all(
        message.get("provider") == "openai-codex"
        and message.get("model") == MODEL
        and message.get("api") == "openai-codex-responses"
        for message in assistant_events
    )


def _independent_usage(arm: str, evidence: dict[str, bytes]) -> dict[str, int] | None:
    if arm == "jcode-azdaja":
        rows = _json_lines(evidence["azdaja_model_trace"], "Azdaja model trace")
        totals = {key: 0 for key in (
            "input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"
        )}
        for row in rows:
            if "error" in row:
                if row.get("error") == "provider_call_failed" and row.get("stage") == "session_setup":
                    continue
                return None
            required = {
                "depth", "input_tokens", "output_tokens", "timestamp_ms", "latency_ms"
            }
            if (
                not required.issubset(row)
                or any(type(row[key]) is not int or row[key] < 0 for key in required)
                or not isinstance(row.get("provider"), str) or not row["provider"]
                or not isinstance(row.get("model"), str) or not row["model"]
            ):
                return None
            for key in totals:
                value = row.get(key, 0)
                if value is None and key in {"cache_read_tokens", "cache_write_tokens"}:
                    value = 0
                if type(value) is not int or value < 0:
                    return None
                totals[key] += value
        if not rows:
            return None
    else:
        rows = _json_objects_authoritative(evidence["stdout"], f"{arm} stdout")
        totals = {key: 0 for key in (
            "input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"
        )}
        if arm == "jcode-native":
            selected = [row for row in rows if row.get("type") == "tokens"]
            field_map = {
                "input_tokens": "input", "output_tokens": "output",
                "cache_read_tokens": "cache_read_input",
                "cache_write_tokens": "cache_creation_input",
            }
        else:
            selected = [
                row["message"].get("usage") for row in rows
                if row.get("type") == "message_end"
                and isinstance(row.get("message"), dict)
                and row["message"].get("role") == "assistant"
            ]
            field_map = {
                "input_tokens": "input", "output_tokens": "output",
                "cache_read_tokens": "cacheRead", "cache_write_tokens": "cacheWrite",
            }
        if not selected:
            return None
        for item in selected:
            if not isinstance(item, dict):
                return None
            for destination, source in field_map.items():
                default = 0 if destination.startswith("cache_") and arm == "jcode-native" else None
                value = item.get(source, default)
                if value is None and default == 0:
                    value = 0
                if type(value) is not int or value < 0:
                    return None
                totals[destination] += value
            if arm == "prime-agent":
                component = sum(item[source] for source in field_map.values())
                provider_total = item.get("totalTokens", item.get("total_tokens", item.get("total")))
                if provider_total is not None and provider_total != component:
                    return None
    totals["total_tokens"] = (
        totals["input_tokens"] + totals["output_tokens"]
        + (totals["cache_read_tokens"] + totals["cache_write_tokens"] if arm == "prime-agent" else 0)
    )
    return totals


def _try_json_lines(data: bytes) -> tuple[list[dict[str, Any]] | None, str | None]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, "authority stream is not UTF-8"
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = _decode_json(line, f"root-token authority line {line_number}")
        except ScoreError as exc:
            return None, str(exc)
        if not isinstance(value, dict):
            return None, f"root-token authority line {line_number} is not an object"
        rows.append(value)
    return rows, None


def _prime_tool_result_chars(result: Any) -> int | None:
    if isinstance(result, str):
        return len(result)
    if not isinstance(result, dict):
        return None
    content = result.get("content")
    if isinstance(content, str):
        return len(content)
    if not isinstance(content, list):
        return None
    total = 0
    for item in content:
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            return None
        total += len(item["text"])
    return total


def _control_root_token_economy(arm: str, stdout_data: bytes) -> dict[str, Any]:
    rows, error = _try_json_lines(stdout_data)
    if rows is None:
        return {
            "root_tokens": None,
            "authority": "retained control stdout tool-result events",
            "missing": True,
            "fallback_used": True,
            "source_chars": None,
            "missing_reason": error,
        }
    total_chars = 0
    if arm == "jcode-native":
        events = [row for row in rows if row.get("type") == "tool_done"]
        for event in events:
            output = event.get("output")
            if not isinstance(output, str):
                return {
                    "root_tokens": None,
                    "authority": "jcode tool_done.output Unicode characters / 4",
                    "missing": True,
                    "fallback_used": True,
                    "source_chars": None,
                    "missing_reason": "a jcode tool_done event lacks exact text output",
                }
            total_chars += len(output)
        authority = "jcode tool_done.output Unicode characters entering root context / 4"
    elif arm == "prime-agent":
        events = [row for row in rows if row.get("type") == "tool_execution_end"]
        for event in events:
            chars = _prime_tool_result_chars(event.get("result"))
            if chars is None:
                return {
                    "root_tokens": None,
                    "authority": "Prime tool_execution_end result text Unicode characters / 4",
                    "missing": True,
                    "fallback_used": True,
                    "source_chars": None,
                    "missing_reason": "a Prime tool result lacks an exact text representation",
                }
            total_chars += chars
        authority = "Prime tool_execution_end result text Unicode characters entering root context / 4"
    else:
        raise ScoreError(f"unsupported control arm for root-token economy: {arm}")
    return {
        "root_tokens": total_chars / 4.0,
        "authority": authority,
        "missing": False,
        "fallback_used": True,
        "source_chars": total_chars,
        "missing_reason": None,
    }


def _exact_root_request_chars(trace_data: bytes) -> tuple[int | None, str | None]:
    try:
        trace = trace_data.decode("utf-8")
    except UnicodeDecodeError:
        return None, "AZDAJA_SOLO_TRACE is not UTF-8"
    header = re.compile(
        r"(?:^|\n)=== root request begin [^\n]* request_chars=([0-9]+) ===\n"
    )
    matches = list(header.finditer(trace))
    if len(matches) != 1:
        return None, "AZDAJA_SOLO_TRACE does not contain exactly one root request header"
    declared = int(matches[0].group(1))
    start = matches[0].end()
    end = start + declared
    if end > len(trace) or not trace.startswith("\n=== root request end ", end):
        return None, "AZDAJA_SOLO_TRACE root request character count/boundary is inconsistent"
    return declared, None


def _treatment_root_token_economy(evidence: dict[str, bytes]) -> dict[str, Any]:
    model_data = evidence.get("azdaja_model_trace")
    if model_data is not None:
        rows, _ = _try_json_lines(model_data)
        if rows is not None:
            depth_zero = [
                row for row in rows
                if row.get("depth") == 0
                and "error" not in row
                and _nonnegative_int(row.get("input_tokens"))
            ]
            if depth_zero:
                return {
                    "root_tokens": sum(int(row["input_tokens"]) for row in depth_zero),
                    "authority": "AZDAJA_MODEL_TRACE successful depth-0 input_tokens",
                    "missing": False,
                    "fallback_used": False,
                    "source_chars": None,
                    "missing_reason": None,
                }
    solo_data = evidence.get("azdaja_solo_trace")
    if solo_data is not None:
        request_chars, reason = _exact_root_request_chars(solo_data)
        if request_chars is not None:
            return {
                "root_tokens": request_chars / 4.0,
                "authority": "exact AZDAJA_SOLO_TRACE root request Unicode characters / 4",
                "missing": False,
                "fallback_used": True,
                "source_chars": request_chars,
                "missing_reason": None,
            }
    else:
        reason = "AZDAJA_SOLO_TRACE is missing"
    return {
        "root_tokens": None,
        "authority": "depth-0 model usage, else exact solo root-request characters / 4",
        "missing": True,
        "fallback_used": True,
        "source_chars": None,
        "missing_reason": reason,
    }


def root_token_economy(arm: str, evidence: dict[str, bytes]) -> dict[str, Any]:
    if arm == "jcode-azdaja":
        return _treatment_root_token_economy(evidence)
    return _control_root_token_economy(arm, evidence["stdout"])


SCORE_SOLO_RUNTIME_KEYS = {
    "schema_version", "event", "request_id", "outcome",
    "exec_invocation_count", "exec_wall_ns", "snapshot_save_count",
    "snapshot_save_wall_ns", "snapshot_load_count", "snapshot_load_wall_ns",
    "sub_call_count", "sub_call_wall_ns",
}
SCORE_MODEL_TRACE_KEYS = {
    "schema_version", "event", "timestamp_ms", "depth", "request_id",
    "attempt", "entered_turn", "session_id", "category", "outcome",
    "error", "error_category", "stage", "setup_substage", "provider", "model",
    "input_tokens", "output_tokens", "cache_read_tokens", "latency_ms",
    "degraded_transport", "failed_attempts_before_success", "response",
}
SCORE_MODEL_TRACE_REQUIRED = {
    "schema_version", "event", "timestamp_ms", "depth", "request_id",
    "attempt", "session_id", "category", "outcome",
}
PERFORMANCE_AUTHORITY = (
    "AZDAJA_MODEL_TRACE v2 provider attempts plus the unique absolute-EOF "
    "AZDAJA_SOLO_TRACE solo_runtime v1 record"
)


def _independent_performance_ledger(
    model_data: bytes,
    solo_data: bytes,
    index: int,
    *,
    parallel_width: int,
    parallel_active_at_start: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    label = f"inference row {index} performance ledger"
    try:
        model_text = model_data.decode("utf-8")
        solo_text = solo_data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ScoreError(f"{label} trace is not UTF-8") from exc
    solo_lines = solo_text.splitlines()
    if len(solo_lines) < 3:
        raise ScoreError(f"{label} has no absolute-EOF runtime footer")
    try:
        runtime = json.loads(solo_lines[-2])
    except json.JSONDecodeError as exc:
        raise ScoreError(f"{label} runtime footer is malformed") from exc
    request_id = runtime.get("request_id") if isinstance(runtime, dict) else None
    if (
        not isinstance(runtime, dict)
        or set(runtime) != SCORE_SOLO_RUNTIME_KEYS
        or runtime.get("schema_version") != 1
        or runtime.get("event") != "solo_runtime"
        or runtime.get("outcome") != "succeeded"
        or not isinstance(request_id, str)
        or re.fullmatch(r"[0-9]+-[0-9]+-[0-9]+", request_id) is None
    ):
        raise ScoreError(f"{label} runtime footer shape is invalid")
    if (
        solo_lines[-3] != f'=== solo runtime trace begin request_id="{request_id}" ==='
        or solo_lines[-1] != f'=== solo runtime trace end request_id="{request_id}" ==='
    ):
        raise ScoreError(f"{label} runtime footer envelope is not exact")
    runtime_rows = []
    for line in solo_lines:
        if not line.startswith("{"):
            continue
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and candidate.get("event") == "solo_runtime":
            runtime_rows.append(candidate)
    if runtime_rows != [runtime]:
        raise ScoreError(f"{label} runtime footer is spoof-ambiguous")
    counter_keys = SCORE_SOLO_RUNTIME_KEYS - {
        "schema_version", "event", "request_id", "outcome"
    }
    if any(not _nonnegative_int(runtime.get(key)) for key in counter_keys):
        raise ScoreError(f"{label} runtime counters are invalid")
    if runtime["sub_call_wall_ns"] > runtime["exec_wall_ns"]:
        raise ScoreError(f"{label} child wall exceeds exec wall")

    raw_lines = [line for line in model_text.splitlines() if line.strip()]
    if not raw_lines:
        raise ScoreError(f"{label} model trace is empty")
    model_rows: list[dict[str, Any]] = []
    for line in raw_lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ScoreError(f"{label} failed to parse model trace") from exc
        if (
            not isinstance(row, dict)
            or not SCORE_MODEL_TRACE_REQUIRED.issubset(row)
            or not set(row).issubset(SCORE_MODEL_TRACE_KEYS)
            or row.get("schema_version") != 2
            or row.get("event") != "model_attempt"
            or not _nonnegative_int(row.get("timestamp_ms"))
            or not _nonnegative_int(row.get("depth"))
            or type(row.get("attempt")) is not int
            or row["attempt"] < 1
            or not isinstance(row.get("request_id"), str)
            or not row["request_id"]
            or row.get("category") not in {"session_setup", "turn", "repair"}
            or row.get("outcome") not in {"failed", "succeeded"}
        ):
            raise ScoreError(f"{label} model trace row is invalid")
        if row["category"] in {"turn", "repair"} and (
            type(row.get("entered_turn")) is not int
            or row["entered_turn"] < 1
            or not _nonnegative_int(row.get("latency_ms"))
        ):
            raise ScoreError(f"{label} entered turn lacks ordinal or latency")
        model_rows.append(row)

    root_rows = [
        row for row in model_rows
        if row["depth"] == 0 and row["category"] in {"turn", "repair"}
    ]
    initial_rows = [row for row in root_rows if row["category"] == "turn"]
    if not initial_rows or any(row["request_id"] != request_id for row in initial_rows):
        raise ScoreError(f"{label} root correlation is invalid")
    ordinals = [row["entered_turn"] for row in root_rows]
    if sorted(ordinals) != list(range(1, len(root_rows) + 1)):
        raise ScoreError(f"{label} root ordinals are not unique and contiguous")
    repair_rows = [row for row in root_rows if row["category"] == "repair"]
    repair_suffixes = [
        row["request_id"].removeprefix(request_id + "-repair-")
        for row in repair_rows
    ]
    if repair_suffixes != [str(value) for value in range(1, len(repair_rows) + 1)]:
        raise ScoreError(f"{label} repair sequence is invalid")
    sub_request_ids = {row["request_id"] for row in model_rows if row["depth"] > 0}
    sub_turn_rows = [
        row for row in model_rows
        if row["depth"] > 0 and row["category"] in {"turn", "repair"}
    ]
    if len(sub_request_ids) != runtime["sub_call_count"]:
        raise ScoreError(f"{label} logical child count disagrees with trace")
    if (
        runtime["snapshot_save_count"] != 1
        or runtime["snapshot_load_count"] != len(repair_rows)
        or not 1 <= runtime["exec_invocation_count"] <= 1 + len(repair_rows)
    ):
        raise ScoreError(f"{label} successful count identities are invalid")
    repair_usage_complete = all(
        row["outcome"] == "succeeded"
        and all(_nonnegative_int(row.get(key)) for key in (
            "input_tokens", "output_tokens", "cache_read_tokens"
        ))
        for row in repair_rows
    )
    repair_cost = {
        "inference_ms": sum(row["latency_ms"] for row in repair_rows),
        "input_tokens": sum(row["input_tokens"] for row in repair_rows)
        if repair_usage_complete else None,
        "output_tokens": sum(row["output_tokens"] for row in repair_rows)
        if repair_usage_complete else None,
        "cache_read_tokens": sum(row["cache_read_tokens"] for row in repair_rows)
        if repair_usage_complete else None,
        "token_accounting_complete": repair_usage_complete,
    }
    ledger = {
        "schema_version": 1,
        "complete": True,
        "root_turn_count": len(root_rows),
        "root_inference_ms": sum(row["latency_ms"] for row in root_rows),
        "exec_invocation_count": runtime["exec_invocation_count"],
        "exec_wall_ms": runtime["exec_wall_ns"] / 1_000_000.0,
        "snapshot_save_count": runtime["snapshot_save_count"],
        "snapshot_save_ms": runtime["snapshot_save_wall_ns"] / 1_000_000.0,
        "snapshot_load_count": runtime["snapshot_load_count"],
        "snapshot_load_ms": runtime["snapshot_load_wall_ns"] / 1_000_000.0,
        "sub_call_count": runtime["sub_call_count"],
        "sub_call_turn_count": len(sub_turn_rows),
        "sub_call_wall_ms": runtime["sub_call_wall_ns"] / 1_000_000.0,
        "repair_count": len(repair_rows),
        "repair_cost": repair_cost,
        "configured_global_width": parallel_width,
        "parallel_width_scope": PARALLEL_WIDTH_SCOPE,
        "observed_active_at_start": parallel_active_at_start,
    }
    assertion = {
        "applicable": True,
        "asserted": True,
        "authority": PERFORMANCE_AUTHORITY,
        "raw_runtime": runtime,
        "reasons": [],
    }
    return ledger, assertion


def _validate_recorded_performance_shape(
    ledger: Any, assertion: Any, index: int
) -> None:
    assertion_keys = {"applicable", "asserted", "authority", "raw_runtime", "reasons"}
    if (
        not isinstance(assertion, dict)
        or set(assertion) != assertion_keys
        or type(assertion.get("applicable")) is not bool
        or type(assertion.get("asserted")) is not bool
        or not isinstance(assertion.get("authority"), str)
        or not isinstance(assertion.get("reasons"), list)
        or any(not isinstance(reason, str) for reason in assertion["reasons"])
    ):
        raise ScoreError(f"inference row {index} performance assertion shape is invalid")
    if ledger is None:
        if assertion["asserted"]:
            raise ScoreError(f"inference row {index} asserted performance ledger is missing")
        return
    keys = {
        "schema_version", "complete", "root_turn_count", "root_inference_ms",
        "exec_invocation_count", "exec_wall_ms", "snapshot_save_count",
        "snapshot_save_ms", "snapshot_load_count", "snapshot_load_ms",
        "sub_call_count", "sub_call_turn_count", "sub_call_wall_ms",
        "repair_count", "repair_cost", "configured_global_width",
        "parallel_width_scope", "observed_active_at_start",
    }
    integer_keys = {
        "root_turn_count", "root_inference_ms", "exec_invocation_count",
        "snapshot_save_count", "snapshot_load_count", "sub_call_count",
        "sub_call_turn_count", "repair_count",
    }
    if (
        not isinstance(ledger, dict)
        or set(ledger) != keys
        or ledger.get("schema_version") != 1
        or type(ledger.get("complete")) is not bool
        or ledger.get("configured_global_width") != PARALLEL_WIDTH
        or ledger.get("parallel_width_scope") != PARALLEL_WIDTH_SCOPE
        or type(ledger.get("observed_active_at_start")) is not int
        or not 1 <= ledger["observed_active_at_start"] <= PARALLEL_WIDTH
        or any(not _nonnegative_int(ledger.get(key)) for key in integer_keys)
        or any(not _nonnegative_number(ledger.get(key)) for key in (
            "exec_wall_ms", "snapshot_save_ms", "snapshot_load_ms", "sub_call_wall_ms"
        ))
    ):
        raise ScoreError(f"inference row {index} performance ledger shape is invalid")
    cost = ledger["repair_cost"]
    cost_keys = {
        "inference_ms", "input_tokens", "output_tokens", "cache_read_tokens",
        "token_accounting_complete",
    }
    if (
        not isinstance(cost, dict)
        or set(cost) != cost_keys
        or not _nonnegative_int(cost.get("inference_ms"))
        or type(cost.get("token_accounting_complete")) is not bool
    ):
        raise ScoreError(f"inference row {index} performance repair cost is invalid")
    tokens = [cost.get(key) for key in (
        "input_tokens", "output_tokens", "cache_read_tokens"
    )]
    if cost["token_accounting_complete"]:
        if any(not _nonnegative_int(value) for value in tokens):
            raise ScoreError(f"inference row {index} repair token cost is invalid")
    elif any(value is not None for value in tokens):
        raise ScoreError(f"inference row {index} incomplete repair tokens are not null")
    if ledger["complete"] != assertion["asserted"]:
        raise ScoreError(f"inference row {index} ledger completeness disagrees with assertion")


def _audit_performance_evidence(
    row: dict[str, Any], retained: dict[str, bytes], index: int
) -> dict[str, Any] | None:
    evidence = row["arm_evidence"]
    if (
        "performance_ledger" not in evidence
        or "performance_ledger_assertion" not in evidence
    ):
        raise ScoreError(f"inference row {index} performance ledger evidence is missing")
    ledger = evidence["performance_ledger"]
    assertion = evidence["performance_ledger_assertion"]
    if row["arm"] != "jcode-azdaja":
        expected = {
            "applicable": False,
            "asserted": True,
            "authority": "not applicable to control arm",
            "raw_runtime": None,
            "reasons": [],
        }
        if ledger is not None or assertion != expected:
            raise ScoreError(f"inference row {index} control performance evidence is invalid")
        return None
    _validate_recorded_performance_shape(ledger, assertion, index)
    if assertion["applicable"] is not True:
        raise ScoreError(f"inference row {index} Azdaja performance assertion is invalid")
    if row["execution_success"] and not assertion["asserted"]:
        raise ScoreError(f"inference row {index} successful Azdaja ledger is incomplete")
    parallel = evidence.get("runner_parallelism")
    if not isinstance(parallel, dict):
        raise ScoreError(
            f"inference row {index} runner parallelism evidence is missing"
        )
    if ledger is not None and (
        ledger["configured_global_width"] != parallel.get("configured_global_width")
        or ledger["observed_active_at_start"]
        != parallel.get("observed_active_at_start")
    ):
        raise ScoreError(
            f"inference row {index} product ledger disagrees with controller concurrency"
        )
    if not assertion["asserted"]:
        return None
    try:
        expected_ledger, expected_assertion = _independent_performance_ledger(
            retained["azdaja_model_trace"],
            retained["azdaja_solo_trace"],
            index,
            parallel_width=parallel["configured_global_width"],
            parallel_active_at_start=parallel["observed_active_at_start"],
        )
    except KeyError as exc:
        raise ScoreError(
            f"inference row {index} asserted Azdaja performance traces are missing"
        ) from exc
    _require_equal(ledger, expected_ledger, f"inference row {index} performance ledger")
    _require_equal(
        assertion, expected_assertion,
        f"inference row {index} performance ledger assertion",
    )
    return expected_ledger


def _validate_artifact_record(
    record: Any, label: str
) -> tuple[Path, bytes, tuple[int, int]]:
    expected_keys = {
        "path", "sha256", "bytes", "mode", "contains_private_raw_trajectory",
        "credential_redacted", "sensitivity",
    }
    if not isinstance(record, dict) or set(record) != expected_keys:
        raise ScoreError(f"{label} artifact record has an unexpected shape")
    raw_path = record["path"]
    if (
        not isinstance(raw_path, str)
        or not raw_path
        or not Path(raw_path).is_absolute()
    ):
        raise ScoreError(f"{label} artifact path must be absolute")
    path = lexical_absolute(Path(raw_path))
    _reject_symlink_components(path)
    if path.is_symlink():
        raise ScoreError(f"{label} artifact path must not be a symlink")
    data, metadata = read_private_bytes_identity(path, label, exact_mode=0o600)
    _require_equal(len(data), record["bytes"], f"{label} artifact byte count")
    _require_equal(sha256_bytes(data), record["sha256"], f"{label} artifact SHA-256")
    _require_equal(record["mode"], "0600", f"{label} artifact recorded mode")
    if type(record["contains_private_raw_trajectory"]) is not bool:
        raise ScoreError(f"{label} artifact trajectory flag is invalid")
    if record["credential_redacted"] is not True:
        raise ScoreError(f"{label} artifact is not credential-redacted")
    if not isinstance(record["sensitivity"], str) or not record["sensitivity"]:
        raise ScoreError(f"{label} artifact sensitivity label is invalid")
    return path, data, (metadata.st_dev, metadata.st_ino)


def _validate_arm_artifacts(
    row: dict[str, Any], index: int, payload_data: bytes
) -> tuple[Path, dict[str, Any]]:
    evidence = row["arm_evidence"]
    trajectories = evidence.get("trajectory_artifacts")
    base_keys = {"stdout", "stderr"}
    trace_keys = {"azdaja_model_trace", "azdaja_solo_trace"}
    if not isinstance(trajectories, dict):
        raise ScoreError(f"inference row {index} trajectory artifacts must be an object")
    actual_keys = set(trajectories)
    if row["arm"] == "jcode-azdaja":
        if row["execution_success"] and actual_keys != base_keys | trace_keys:
            raise ScoreError(
                f"inference row {index} successful Azdaja artifacts are not the exact four-key set"
            )
        if not row["execution_success"] and (
            not base_keys.issubset(actual_keys)
            or not actual_keys.issubset(base_keys | trace_keys)
        ):
            raise ScoreError(
                f"inference row {index} failed Azdaja artifacts have unexpected keys"
            )
    elif actual_keys != base_keys:
        raise ScoreError(
            f"inference row {index} {row['arm']} artifacts are not exactly stdout/stderr"
        )

    paths: list[Path] = []
    inodes: list[tuple[int, int]] = []
    retained: dict[str, bytes] = {}
    for name, record in trajectories.items():
        path, data, inode = _validate_artifact_record(
            record, f"inference row {index} {name}"
        )
        expected_name = ARTIFACT_FILENAMES[name]
        if path.name != expected_name:
            raise ScoreError(
                f"inference row {index} {name} artifact must be named {expected_name!r}"
            )
        paths.append(path)
        inodes.append(inode)
        retained[name] = data
    if len(set(paths)) != len(paths) or len(set(inodes)) != len(inodes):
        raise ScoreError(f"inference row {index} artifact paths/inodes are not unique")

    # Every retained artifact for one attempt must share its exact private run dir.
    parents = {path.parent for path in paths}
    if len(parents) != 1:
        raise ScoreError(f"inference row {index} artifacts do not share one run directory")
    run_directory = next(iter(parents))
    expected_run_directory_name = (
        f"{row['execution_ordinal']:03d}-{row['run_id'][:16]}-{row['arm']}"
    )
    if run_directory.name != expected_run_directory_name:
        raise ScoreError(f"inference row {index} artifact directory is not bound to its run")
    require_private_directory(run_directory, f"inference row {index} run artifact directory")
    require_private_directory(run_directory.parent, "frozen artifact work root")
    expected_names = {ARTIFACT_FILENAMES[name] for name in actual_keys}
    try:
        run_entries = list(run_directory.iterdir())
    except OSError as exc:
        raise ScoreError(f"cannot enumerate inference row {index} run directory: {exc}") from exc
    actual_names = {entry.name for entry in run_entries}
    if len(run_entries) != len(actual_names) or actual_names != expected_names:
        raise ScoreError(
            f"inference row {index} run directory inventory differs from declared artifacts"
        )
    cleanup = evidence.get("credential_cleanup")
    if cleanup is not None:
        if not isinstance(cleanup, dict):
            raise ScoreError(f"inference row {index} credential cleanup is invalid")
        for field in ("retained_entries", "retention_allowlist"):
            if cleanup.get(field) != sorted(expected_names):
                raise ScoreError(
                    f"inference row {index} credential cleanup {field} differs from artifacts"
                )

    if row["arm"] == "jcode-azdaja":
        solo_trace = retained.get("azdaja_solo_trace")
        if solo_trace is None:
            leak_audit = {
                "applicable": True,
                "scanned": False,
                "detected": False,
                "minimum_match_chars": ROOT_LEAK_MIN_CHARS,
                "matched_text_retained": False,
                "missing_reason": "AZDAJA_SOLO_TRACE was not retained",
            }
        else:
            leak_audit = root_context_leak_audit(payload_data, solo_trace)
        if leak_audit["detected"]:
            if row["execution_success"]:
                raise ScoreError(
                    f"inference row {index} falsely claims success despite hard root_context_leak"
                )
            failure = row.get("failure")
            if not isinstance(failure, dict) or failure.get("kind") != "root_context_leak":
                raise ScoreError(
                    f"inference row {index} did not record independently detected root_context_leak"
                )
    else:
        leak_audit = {
            "applicable": False,
            "scanned": False,
            "detected": False,
            "minimum_match_chars": ROOT_LEAK_MIN_CHARS,
            "matched_text_retained": False,
            "missing_reason": "not applicable to control arm",
        }
    economy = root_token_economy(row["arm"], retained)
    performance_ledger = _audit_performance_evidence(row, retained, index)

    if row["execution_success"]:
        # Hash-check above binds these exact bytes; route and usage are then replayed
        # independently from every nonempty authority-stream line.
        if not _independent_route(row["arm"], retained):
            raise ScoreError(f"inference row {index} retained route evidence is invalid")
        recomputed = _independent_usage(row["arm"], retained)
        if recomputed is None:
            raise ScoreError(f"inference row {index} retained usage evidence is incomplete")
        usage = row.get("usage")
        if not isinstance(usage, dict):
            raise ScoreError(f"inference row {index} lacks normalized usage")
        for key, value in recomputed.items():
            _require_equal(
                value, usage.get(key),
                f"inference row {index} independently recomputed {key}",
            )
    return run_directory, {
        "root_context_leak": leak_audit,
        "root_token_economy": economy,
        "performance_ledger": performance_ledger,
    }


def _validate_telemetry(row: dict[str, Any], index: int) -> None:
    arm = row["arm"]
    route = row.get("route_assertion")
    if not isinstance(route, dict) or set(route) != {
        "asserted", "subscription", "provider", "model"
    }:
        raise ScoreError(f"inference row {index} route_assertion shape is invalid")
    if type(route["asserted"]) is not bool or type(route["subscription"]) is not bool:
        raise ScoreError(f"inference row {index} route assertion booleans are invalid")
    expected_provider = "OpenAI OAuth" if arm.startswith("jcode") else "openai-codex"
    _require_equal(route["provider"], expected_provider, f"inference row {index} provider route")
    _require_equal(route["model"], MODEL, f"inference row {index} routed model")

    lifecycle = row.get("lifecycle_assertion")
    if not isinstance(lifecycle, dict) or set(lifecycle) != {
        "asserted", "isolated_home", "fresh_session", "cleanup_complete"
    }:
        raise ScoreError(f"inference row {index} lifecycle_assertion shape is invalid")
    if any(type(lifecycle[key]) is not bool for key in lifecycle):
        raise ScoreError(f"inference row {index} lifecycle assertion booleans are invalid")

    usage = row.get("usage")
    if usage is not None:
        if not isinstance(usage, dict) or set(usage) != {
            "input_tokens", "output_tokens", "cache_read_tokens",
            "cache_write_tokens", "total_tokens", "accounting_complete",
        }:
            raise ScoreError(f"inference row {index} normalized usage shape is invalid")
        for key in (
            "input_tokens", "output_tokens", "cache_read_tokens",
            "cache_write_tokens", "total_tokens",
        ):
            if not _nonnegative_int(usage[key]):
                raise ScoreError(f"inference row {index} usage {key} is invalid")
        if type(usage["accounting_complete"]) is not bool:
            raise ScoreError(f"inference row {index} usage accounting flag is invalid")
        expected_total = usage["input_tokens"] + usage["output_tokens"]
        if arm == "prime-agent":
            expected_total += usage["cache_read_tokens"] + usage["cache_write_tokens"]
        _require_equal(
            usage["total_tokens"], expected_total,
            f"inference row {index} normalized usage total",
        )
    if row["execution_success"]:
        if not route["asserted"] or not route["subscription"]:
            raise ScoreError(f"inference row {index} successful route is not asserted")
        if not all(lifecycle.values()):
            raise ScoreError(f"inference row {index} successful lifecycle is not asserted")
        if usage is None or not usage["accounting_complete"]:
            raise ScoreError(f"inference row {index} successful usage accounting is incomplete")


def validate_run_rows(
    rows: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
    schedule: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    if len(rows) != len(jobs):
        raise ScoreError(
            f"frozen inference is not terminal-complete (scheduled={len(jobs)}, rows={len(rows)})"
        )
    configuration = schedule["configuration"]
    candidate = configuration.get("candidate")
    candidate_sha = candidate.get("sha256") if isinstance(candidate, dict) else None
    controller_sha = configuration["controller"]["sha256"]
    seen: set[str] = set()
    artifact_work_root: Path | None = None
    run_directories: set[Path] = set()
    independent_audits: dict[str, dict[str, Any]] = {}
    expected_row_keys = {
        "schema_version", "record_type", "schedule_id", "run_id", "fixture_id",
        "payload_sha256", "execution_ordinal", "arm", "repetition", "model",
        "reasoning", "schedule_seed", "timeout_seconds", "workflow",
        "workflow_fixture_ids_sha256", "parallel_width", "configured_global_width",
        "parallel_width_scope", "timed_out", "exit_code",
        "candidate_sha256", "controller_sha256", "success", "score",
        "scoring_status", "execution_success",
        "latency_seconds", "response", "route_assertion", "usage",
        "lifecycle_assertion", "failure", "arm_evidence", "containment",
    }
    for index, (row, job) in enumerate(zip(rows, jobs), 1):
        if set(row) != expected_row_keys:
            raise ScoreError(f"inference row {index} has an unexpected object shape")
        expected = {
            "schema_version": SCHEMA_VERSION,
            "record_type": "inference",
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "fixture_id": job["fixture_id"],
            "payload_sha256": job["payload_sha256"],
            "execution_ordinal": job["ordinal"],
            "arm": job["arm"],
            "repetition": job["repetition"],
            "model": configuration["model"],
            "reasoning": configuration["reasoning"],
            "schedule_seed": configuration["seed"],
            "timeout_seconds": configuration["timeout_seconds"],
            "workflow": configuration["workflow"],
            "workflow_fixture_ids_sha256": configuration[
                "workflow_fixture_ids_sha256"
            ],
            "parallel_width": configuration["parallel_width"],
            "configured_global_width": configuration["configured_global_width"],
            "parallel_width_scope": configuration["parallel_width_scope"],
            "candidate_sha256": candidate_sha,
            "controller_sha256": controller_sha,
            "success": None,
            "score": None,
            "scoring_status": "deferred",
        }
        for key, expected_value in expected.items():
            _require_equal(row.get(key), expected_value, f"inference row {index} {key}")
        fixture = row.get("fixture")
        if fixture is not None:
            if not isinstance(fixture, dict):
                raise ScoreError(f"inference row {index} nested fixture is invalid")
            _require_equal(
                fixture.get("payload_sha256"), job["payload_sha256"],
                f"inference row {index} nested payload_sha256",
            )
        if type(row.get("execution_success")) is not bool:
            raise ScoreError(f"inference row {index} lacks a terminal execution_success bool")
        if not isinstance(row.get("response"), str):
            raise ScoreError(f"inference row {index} response must be a string")
        if row["execution_success"] and not row["response"]:
            raise ScoreError(f"inference row {index} successful response must be nonempty")
        if not _nonnegative_number(row.get("latency_seconds")):
            raise ScoreError(f"inference row {index} latency_seconds is invalid")
        if type(row.get("timed_out")) is not bool:
            raise ScoreError(f"inference row {index} timed_out must be a bool")
        if row.get("exit_code") is not None and type(row["exit_code"]) is not int:
            raise ScoreError(f"inference row {index} exit_code must be integer or null")
        if row["execution_success"] and (row["timed_out"] or row["exit_code"] != 0):
            raise ScoreError(f"inference row {index} successful process status is invalid")
        if row["timed_out"] and row["exit_code"] == 0:
            raise ScoreError(f"inference row {index} timed-out process cannot have exit code zero")
        failure = row.get("failure")
        if row["execution_success"]:
            if failure is not None:
                raise ScoreError(f"inference row {index} succeeded but has a failure object")
        elif not isinstance(failure, dict) or not isinstance(failure.get("kind"), str) or not failure["kind"]:
            raise ScoreError(f"inference row {index} failed without a typed failure object")
        arm_evidence = row["arm_evidence"]
        if not isinstance(arm_evidence, dict):
            raise ScoreError(f"inference row {index} arm_evidence must be an object")
        _validate_runner_parallel_observation(
            arm_evidence.get("runner_parallelism"),
            index,
            expected_width=configuration["configured_global_width"],
        )
        if "staged_filename" in arm_evidence:
            _require_equal(
                arm_evidence["staged_filename"], job["staged_filename"],
                f"inference row {index} staged filename evidence",
            )
        run_directory, audit = _validate_arm_artifacts(
            row, index, fixtures[job["fixture_id"]]["_payload_bytes"]
        )
        independent_audits[row["run_id"]] = audit
        row_artifact_root = run_directory.parent
        if artifact_work_root is None:
            artifact_work_root = row_artifact_root
        elif row_artifact_root != artifact_work_root:
            raise ScoreError("inference artifacts are not confined to one frozen work root")
        if run_directory in run_directories:
            raise ScoreError("multiple inference rows share one run artifact directory")
        run_directories.add(run_directory)
        containment = row["containment"]
        if (
            not isinstance(containment, dict)
            or set(containment) != {"os_level_asserted", "disclaimer", "claim_ledger"}
            or containment["os_level_asserted"] is not False
            or not isinstance(containment["disclaimer"], str)
            or not containment["disclaimer"]
            or containment["claim_ledger"] != "local append-only creation protocol is not authenticated against malicious same-owner deletion/retry; external signing or transparency is future work"
        ):
            raise ScoreError(f"inference row {index} containment disclosure is invalid")
        _validate_telemetry(row, index)
        if row["run_id"] in seen:
            raise ScoreError(f"duplicate inference run_id at row {index}")
        if row["fixture_id"] not in fixtures:
            raise ScoreError(f"inference row {index} has unknown fixture id")
        seen.add(row["run_id"])

    runner_batch = _validate_runner_parallel_batch(
        rows, expected_width=configuration["configured_global_width"]
    )
    for audit in independent_audits.values():
        audit["runner_batch"] = runner_batch
    if artifact_work_root is None:
        raise ScoreError("terminal inference has no artifact work root")
    try:
        work_entries = list(artifact_work_root.iterdir())
    except OSError as exc:
        raise ScoreError(f"cannot enumerate frozen artifact work root: {exc}") from exc
    actual_names = {entry.name for entry in work_entries}
    expected_names = {directory.name for directory in run_directories}
    if len(work_entries) != len(actual_names) or actual_names != expected_names:
        raise ScoreError("frozen artifact work root is not the exact scheduled run-directory set")
    return independent_audits


def validate_pre_gold_root_context_leak_gate(
    jobs: list[dict[str, Any]], independent_audits: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Require exact solo-trace scan evidence for every terminal treatment row."""
    treatment_rows = [
        (index, job) for index, job in enumerate(jobs, 1)
        if job["arm"] == "jcode-azdaja"
    ]
    for index, job in treatment_rows:
        audit = independent_audits.get(job["run_id"])
        leak = audit.get("root_context_leak") if isinstance(audit, dict) else None
        valid_exact_scan = (
            isinstance(leak, dict)
            and leak.get("applicable") is True
            and leak.get("scanned") is True
            and type(leak.get("detected")) is bool
            and leak.get("minimum_match_chars") == ROOT_LEAK_MIN_CHARS
            and leak.get("payload_sha256") == job["payload_sha256"]
            and _is_sha256(leak.get("trace_sha256"))
            and _nonnegative_int(leak.get("trace_chars"))
            and "missing_reason" not in leak
        )
        if not valid_exact_scan:
            raise ScoreError(
                "pre-gold root-context leak gate requires a valid exact retained "
                "AZDAJA_SOLO_TRACE with scanned=true for every jcode-azdaja terminal "
                f"row, including failed rows (inference row {index})"
            )
    count = len(treatment_rows)
    return {
        "scope": "every jcode-azdaja terminal row, including failed rows",
        "treatment_terminal_rows": count,
        "valid_exact_retained_solo_trace_rows": count,
        "scanned_rows": count,
        "complete": True,
    }


def validate_claims(
    claims_root: Path,
    rows: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
    schedule: dict[str, Any],
) -> Path:
    require_private_directory(claims_root, "frozen claims root")
    try:
        root_entries = list(claims_root.iterdir())
    except OSError as exc:
        raise ScoreError(f"cannot enumerate frozen claims root: {exc}") from exc
    if [entry.name for entry in root_entries] != [schedule["schedule_id"]]:
        raise ScoreError("frozen claims root must contain only the active schedule directory")
    claims = claims_root / schedule["schedule_id"]
    require_private_directory(claims, "frozen schedule claims directory")
    expected_names = {
        name
        for job in jobs
        for name in (job["run_id"] + ".json", job["run_id"] + ".done.json")
    }
    try:
        entries = list(claims.iterdir())
    except OSError as exc:
        raise ScoreError(f"cannot enumerate frozen claims: {exc}") from exc
    actual_names = {entry.name for entry in entries}
    if len(entries) != len(actual_names) or actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        raise ScoreError(
            "claims are not the exact terminal 2N set "
            f"(missing={missing[:3]}, extra={extra[:3]})"
        )
    for index, (row, job) in enumerate(zip(rows, jobs), 1):
        claim = load_json_object(claims / (job["run_id"] + ".json"), f"run claim {index}")
        if set(claim) != {"schedule_id", "run_id", "ordinal", "pid"}:
            raise ScoreError(f"run claim {index} has unexpected fields")
        expected_claim = {
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "ordinal": job["ordinal"],
        }
        for key, value in expected_claim.items():
            _require_equal(claim.get(key), value, f"run claim {index} {key}")
        if not _positive_int(claim.get("pid")):
            raise ScoreError(f"run claim {index} pid is invalid")
        done = load_json_object(
            claims / (job["run_id"] + ".done.json"), f"run completion {index}"
        )
        expected_done = {
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "row_sha256": sha256_bytes(canonical_json_bytes(row)),
        }
        if done != expected_done:
            raise ScoreError(f"run completion {index} receipt mismatch")
    return claims


def validate_frozen_runs(
    manifest_path: Path,
    manifest: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    runs_path: Path,
    schedule_path: Path | None = None,
    claims_root: Path | None = None,
) -> tuple[
    dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], tuple[str, ...],
    dict[str, dict[str, Any]], dict[str, Any],
]:
    """Validate terminal completion and all pre-gold audits without reading gold."""
    schedule_path = lexical_absolute(
        schedule_path or Path(str(runs_path) + ".schedule.json")
    )
    claims_root = lexical_absolute(claims_root or Path(str(runs_path) + ".claims"))
    _reject_symlink_components(schedule_path)
    _reject_symlink_components(claims_root / "placeholder")
    if schedule_path.is_symlink() or claims_root.is_symlink():
        raise ScoreError("frozen schedule/claims paths must not be symlinks")
    schedule = load_json_object(schedule_path, "frozen schedule")
    jobs, arms = validate_schedule(schedule, manifest_path, manifest, fixtures)
    rows = load_run_rows(runs_path)
    independent_audits = validate_run_rows(rows, jobs, schedule, fixtures)
    leak_gate = validate_pre_gold_root_context_leak_gate(jobs, independent_audits)
    validate_claims(claims_root, rows, jobs, schedule)
    return schedule, jobs, rows, arms, independent_audits, leak_gate


def _valid_gold_value(task: str, value: str) -> bool:
    if task == "niah_multikey_3":
        return re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
            r"[89ab][0-9a-f]{3}-[0-9a-f]{12}", value
        ) is not None
    if task == "vt":
        return re.fullmatch(r"[A-Z]{5}", value) is not None
    if task == "fwe":
        return re.fullmatch(r"[a-z]{6}", value) is not None
    return False


def _derive(key: bytes, *parts: object) -> bytes:
    message = b"\0".join(str(part).encode("utf-8") for part in parts)
    return hmac.new(key, message, hashlib.sha256).digest()


def _validate_generation_plan(plan: Any) -> tuple[bytes, dict[tuple[str, int], int]]:
    if not isinstance(plan, dict) or set(plan) != {
        "schema_version", "record_type", "suite_id", "master_key_hex", "cells"
    }:
        raise ScoreError("gold generation plan has an unexpected object shape")
    _require_equal(plan["schema_version"], SCHEMA_VERSION, "gold generation-plan schema")
    _require_equal(
        plan["record_type"],
        "ruler_exact_mini_generation_plan",
        "gold generation-plan record_type",
    )
    _require_equal(plan["suite_id"], SUITE_ID, "gold generation-plan suite_id")
    raw_key = plan["master_key_hex"]
    if not isinstance(raw_key, str) or re.fullmatch(r"[0-9a-f]{64}", raw_key) is None:
        raise ScoreError("gold generation plan master key is invalid")
    master_key = bytes.fromhex(raw_key)
    cells = plan["cells"]
    if not isinstance(cells, list) or len(cells) != 9:
        raise ScoreError("gold generation plan must contain exactly nine cells")
    expected_order = [
        (task, length) for length in TARGET_LENGTHS for task in TASKS
    ]
    seeds: dict[tuple[str, int], int] = {}
    for index, (cell, expected_cell) in enumerate(zip(cells, expected_order), 1):
        if not isinstance(cell, dict) or set(cell) != {
            "task", "target_length", "generator_seed"
        }:
            raise ScoreError(f"gold generation-plan cell {index} shape is invalid")
        actual_cell = (cell["task"], cell["target_length"])
        _require_equal(actual_cell, expected_cell, f"gold generation-plan cell {index}")
        expected_seed = int.from_bytes(
            _derive(master_key, SUITE_ID, "generator", *actual_cell)[:4], "big"
        )
        _require_equal(
            cell["generator_seed"], expected_seed,
            f"gold generation-plan cell {index} derived seed",
        )
        if expected_seed in (0, 42):
            raise ScoreError("gold generation plan uses a forbidden generator seed")
        seeds[actual_cell] = expected_seed
    return master_key, seeds


def _select_pool_rows(
    rows: list[dict[str, Any]], task: str, target_length: int, master_key: bytes
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    if len(rows) != 100:
        raise ScoreError(f"selection pool {(task, target_length)} must have 100 rows")
    cell_key = _derive(master_key, SUITE_ID, "selection", task, target_length)
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    if task == "niah_multikey_3":
        ordered = sorted(
            rows,
            key=lambda item: (item["token_position_answer"], item["ordinal"]),
        )
        for decile in range(10):
            bucket = ordered[decile * 10 : (decile + 1) * 10]
            ranked = sorted(
                bucket,
                key=lambda item: _derive(cell_key, "decile", decile, item["ordinal"]),
            )
            picked = ranked[0]
            selected.append(
                (
                    picked,
                    {
                        "method": "answer_position_decile_hmac_rank",
                        "decile": decile,
                        "hmac_rank_sha256": _derive(
                            cell_key, "decile", decile, picked["ordinal"]
                        ).hex(),
                    },
                )
            )
    else:
        ranked = sorted(
            rows,
            key=lambda item: _derive(cell_key, "ordinal", item["ordinal"]),
        )[:10]
        for picked in ranked:
            selected.append(
                (
                    picked,
                    {
                        "method": "ordinal_hmac_rank",
                        "hmac_rank_sha256": _derive(
                            cell_key, "ordinal", picked["ordinal"]
                        ).hex(),
                    },
                )
            )
    if len({item["ordinal"] for item, _ in selected}) != 10:
        raise ScoreError(f"selection for {(task, target_length)} duplicated a row")
    return selected


def _fixture_id(
    master_key: bytes, task: str, target_length: int, pool_row: dict[str, Any]
) -> str:
    digest = _derive(
        master_key, SUITE_ID, "fixture-id", task, target_length,
        pool_row["ordinal"], pool_row["raw_row_sha256"],
    )
    return "rxm-" + digest[:16].hex()


def _validate_raw_task_semantics(
    task: str,
    target_length: int,
    ordinal: int,
    raw_row: dict[str, Any],
    pool_row: dict[str, Any],
) -> None:
    prompt = raw_row["input"]
    prefix = raw_row["answer_prefix"]
    outputs = raw_row["outputs"]
    patterns = {
        "niah_multikey_3": re.compile(
            r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z"
        ),
        "vt": re.compile(r"[A-Z]{5}\Z"),
        "fwe": re.compile(r"[a-z]{6}\Z"),
    }
    cardinality = {"niah_multikey_3": 1, "vt": 5, "fwe": 3}[task]
    if (
        not isinstance(outputs, list)
        or len(outputs) != cardinality
        or any(not isinstance(value, str) or patterns[task].fullmatch(value) is None for value in outputs)
        or len(set(outputs)) != len(outputs)
    ):
        raise ScoreError(f"{task}/{target_length} row {ordinal} has invalid task-domain outputs")
    if task != "niah_multikey_3" and raw_row["index"] != ordinal:
        raise ScoreError(f"{task}/{target_length} row {ordinal} index is not its pool ordinal")
    if task == "niah_multikey_3":
        match = re.fullmatch(
            r" The special magic uuid for "
            r"([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}) "
            r"mentioned in the provided text is",
            prefix,
        )
        if match is None:
            raise ScoreError(f"niah_multikey_3/{target_length} row {ordinal} prefix is invalid")
        query = match.group(1)
        start = (
            "A special magic uuid is hidden within the following text. "
            "Make sure to memorize it. I will quiz you about the uuid afterwards.\n"
        )
        end = f"\nWhat is the special magic uuid for {query} mentioned in the provided text?"
        position = raw_row.get("token_position_answer")
        answer_index = prompt.find(outputs[0])
        if (
            not prompt.startswith(start) or not prompt.endswith(end)
            or prompt.count(query) < 2
            or type(position) is not int
            or not 0 <= position < raw_row["length"]
            or position != pool_row["token_position_answer"]
            or raw_row["index"] != answer_index
            or answer_index < 0
            or prompt.count(outputs[0]) != 1
        ):
            raise ScoreError(f"niah_multikey_3/{target_length} row {ordinal} semantics are invalid")
    elif task == "vt":
        match = re.fullmatch(
            r" Answer: According to the chain\(s\) of variable assignment in the text above, "
            r"5 variables are assigned the value ([0-9]{5}), they are: ",
            prefix,
        )
        if match is None:
            raise ScoreError(f"vt/{target_length} row {ordinal} prefix is invalid")
        query = match.group(1)
        start = "Memorize and track the chain(s) of variable assignment hidden in the following text.\n\n"
        end = f"\nQuestion: Find all variables that are assigned the value {query} in the text above."
        if (
            not prompt.startswith(start) or not prompt.endswith(end)
            or any(re.search(rf"\b{re.escape(value)}\b", prompt) is None for value in outputs)
        ):
            raise ScoreError(f"vt/{target_length} row {ordinal} semantics are invalid")
    else:
        start = (
            "Read the following coded text and track the frequency of each coded word. "
            "Find the three most frequently appeared coded words. "
        )
        end = (
            "\nQuestion: Do not provide any explanation. Please ignore the dots '....'. "
            "What are the three most frequently appeared words in the above coded text?"
        )
        expected_prefix = (
            " Answer: According to the coded text above, the three most frequently appeared words are:"
        )
        if prefix != expected_prefix or not prompt.startswith(start) or not prompt.endswith(end):
            raise ScoreError(f"fwe/{target_length} row {ordinal} template is invalid")
        words = prompt[len(start):-len(end)].split()
        if not words or any(word != "..." and re.fullmatch(r"[a-z]{6}", word) is None for word in words):
            raise ScoreError(f"fwe/{target_length} row {ordinal} context is invalid")
        counts: dict[str, int] = {}
        for word in words:
            if word != "...":
                counts[word] = counts.get(word, 0) + 1
        output_counts = [counts.get(value, 0) for value in outputs]
        remaining = [count for word, count in counts.items() if word not in outputs]
        if (
            not output_counts[0] > output_counts[1] > output_counts[2]
            or (remaining and output_counts[-1] <= max(remaining))
        ):
            raise ScoreError(f"fwe/{target_length} row {ordinal} outputs are not exact top frequencies")


def load_gold(
    path: Path,
    manifest: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, tuple[str, ...]]]:
    """Open and validate private gold. Call only after ``validate_frozen_runs``."""
    data = read_private_bytes(path, "owner-only gold")
    _require_equal(sha256_bytes(data), manifest["gold_sha256"], "exact gold file SHA-256")
    try:
        document = _decode_json(data.decode("utf-8"), "owner-only gold")
    except UnicodeError as exc:
        raise ScoreError(f"owner-only gold is not UTF-8: {exc}") from exc
    if not isinstance(document, dict):
        raise ScoreError("owner-only gold must contain a JSON object")
    if data != canonical_json_file_bytes(document):
        raise ScoreError("owner-only gold is not canonical compact JSON with one final newline")
    if set(document) != {
        "schema_version", "record_type", "suite_id", "manifest_identity_sha256",
        "fixtures", "provenance",
    }:
        raise ScoreError("owner-only gold has an unexpected object shape")
    _require_equal(document.get("schema_version"), SCHEMA_VERSION, "gold schema_version")
    _require_equal(
        document.get("record_type"), "ruler_exact_mini_gold", "gold record_type"
    )
    _require_equal(document.get("suite_id"), SUITE_ID, "gold suite_id")
    _require_equal(
        document.get("manifest_identity_sha256"),
        manifest_identity_sha256(manifest),
        "gold public-manifest identity commitment",
    )
    entries = document.get("fixtures")
    if not isinstance(entries, list) or len(entries) != EXPECTED_FIXTURES:
        raise ScoreError("gold fixture list is incomplete")
    expected_cardinality = {"niah_multikey_3": 1, "vt": 5, "fwe": 3}
    outputs_by_id: dict[str, tuple[str, ...]] = {}
    seen_raw_rows: set[str] = set()
    ordinals_by_cell: defaultdict[tuple[str, int], set[int]] = defaultdict(set)
    seeds_by_cell: defaultdict[tuple[str, int], set[int]] = defaultdict(set)
    for index, item in enumerate(entries, 1):
        if not isinstance(item, dict):
            raise ScoreError(f"gold fixture {index} is not an object")
        if set(item) != {
            "id", "task", "target_length", "outputs", "raw_row_sha256",
            "canonical_row_sha256", "raw_row_utf8", "ordinal", "generator_seed",
            "payload_sha256", "selection",
        }:
            raise ScoreError(f"gold fixture {index} has an unexpected object shape")
        fixture_id = item.get("id")
        if fixture_id not in fixtures or fixture_id in outputs_by_id:
            raise ScoreError(f"gold fixture id is duplicate or unknown: {fixture_id!r}")
        public = fixtures[fixture_id]
        task = public["task"]
        _require_equal(item.get("task"), task, f"gold fixture {fixture_id} task")
        _require_equal(
            item.get("target_length"), public["target_length"],
            f"gold fixture {fixture_id} target_length",
        )
        if not isinstance(item.get("selection"), dict):
            raise ScoreError(f"gold fixture {fixture_id} selection receipt is invalid")
        outputs = item.get("outputs")
        if (
            not isinstance(outputs, list)
            or len(outputs) != expected_cardinality[task]
            or any(not isinstance(value, str) or not value for value in outputs)
        ):
            raise ScoreError(f"gold fixture {fixture_id} output cardinality/type is invalid")
        folded = [value.lower() for value in outputs]
        if len(set(folded)) != len(folded):
            raise ScoreError(f"gold fixture {fixture_id} outputs are case-insensitively duplicate")
        if any(not _valid_gold_value(task, value) for value in outputs):
            raise ScoreError(f"gold fixture {fixture_id} has an invalid {task} output value")
        raw_row_sha = item.get("raw_row_sha256")
        if not _is_sha256(raw_row_sha) or raw_row_sha in seen_raw_rows:
            raise ScoreError(f"gold fixture {fixture_id} raw row hash is invalid or duplicate")
        ordinal = item.get("ordinal")
        if type(ordinal) is not int or not 0 <= ordinal < 100:
            raise ScoreError(f"gold fixture {fixture_id} ordinal must be in [0, 99]")
        seed = item.get("generator_seed")
        if type(seed) is not int or not 0 <= seed < 2**32:
            raise ScoreError(f"gold fixture {fixture_id} generator_seed is invalid")
        cell = (task, public["target_length"])
        if ordinal in ordinals_by_cell[cell]:
            raise ScoreError(f"gold cell {cell} repeats raw line ordinal {ordinal}")
        ordinals_by_cell[cell].add(ordinal)
        seeds_by_cell[cell].add(seed)
        seen_raw_rows.add(raw_row_sha)
        outputs_by_id[fixture_id] = tuple(outputs)
    if set(outputs_by_id) != set(fixtures):
        raise ScoreError("gold fixture ids differ from the public manifest")
    if any(len(seeds) != 1 for seeds in seeds_by_cell.values()):
        raise ScoreError("gold generator seed provenance is inconsistent within a cell")

    provenance = document.get("provenance")
    if not isinstance(provenance, dict) or set(provenance) != {
        "generation_plan", "generation_plan_sha256", "upstream",
        "dependencies", "pool_receipts",
    }:
        raise ScoreError("gold provenance has an unexpected object shape")
    commitments = manifest["provenance_commitments"]
    plan = provenance["generation_plan"]
    master_key, plan_seeds = _validate_generation_plan(plan)
    plan_sha = sha256_bytes(canonical_json_file_bytes(plan))
    _require_equal(
        plan_sha, commitments["generation_plan_sha256"],
        "gold generation-plan public commitment",
    )
    _require_equal(
        provenance["generation_plan_sha256"], plan_sha,
        "gold generation-plan provenance",
    )
    upstream = provenance["upstream"]
    if not isinstance(upstream, dict) or set(upstream) != {"url", "commit", "files"}:
        raise ScoreError("gold upstream provenance has an unexpected shape")
    _require_equal(upstream["url"], RULER_URL, "gold upstream URL")
    _require_equal(upstream["commit"], RULER_COMMIT, "gold upstream commit")
    _require_equal(
        upstream["files"], EXPECTED_RULER_SOURCE_HASHES,
        "gold upstream file hashes",
    )
    dependencies = provenance["dependencies"]
    if not isinstance(dependencies, dict) or set(dependencies) != {
        "requirements_lock_sha256", "python", "platform", "packages", "wheels",
        "site_packages_sha256", "tokenizer", "nltk_resources",
    }:
        raise ScoreError("gold dependency provenance has an unexpected object shape")
    _require_equal(
        dependencies["requirements_lock_sha256"], REQUIREMENTS_LOCK_SHA256,
        "gold requirements lock hash",
    )
    python_identity = dependencies["python"]
    if not isinstance(python_identity, dict) or set(python_identity) != {
        "implementation", "version", "executable", "build"
    }:
        raise ScoreError("gold Python identity has an unexpected shape")
    _require_equal(python_identity["implementation"], "CPython", "gold Python implementation")
    if (
        not isinstance(python_identity["version"], str)
        or re.fullmatch(r"3\.11(?:\.[0-9]+)?", python_identity["version"]) is None
        or not isinstance(python_identity["executable"], str)
        or not python_identity["executable"]
        or not isinstance(python_identity["build"], list)
        or len(python_identity["build"]) != 2
        or any(not isinstance(value, str) for value in python_identity["build"])
    ):
        raise ScoreError("gold CPython runtime identity is incomplete")
    platform_identity = dependencies["platform"]
    if (
        not isinstance(platform_identity, dict)
        or set(platform_identity) != {"description", "os", "release", "machine"}
        or any(not isinstance(value, str) or not value for value in platform_identity.values())
    ):
        raise ScoreError("gold platform identity is invalid")
    _require_equal(
        dependencies["packages"], EXPECTED_PACKAGE_VERSIONS,
        "gold package-version identities",
    )
    wheels = dependencies["wheels"]
    if (
        not isinstance(wheels, dict)
        or set(wheels) != set(EXPECTED_PACKAGE_VERSIONS)
        or any(
            not isinstance(receipt, dict)
            or set(receipt) != {"filename", "sha256"}
            or not isinstance(receipt["filename"], str)
            or not receipt["filename"].endswith(".whl")
            or not _is_sha256(receipt["sha256"])
            for receipt in wheels.values()
        )
        or not _is_sha256(dependencies["site_packages_sha256"])
    ):
        raise ScoreError("gold wheel/runtime snapshot identities are invalid")
    tokenizer = dependencies["tokenizer"]
    _require_equal(
        tokenizer,
        {
            "name": "cl100k_base", "blob_sha256": TOKENIZER_BLOB_SHA256,
            "cache_filename": TOKENIZER_CACHE_NAME,
        },
        "gold tokenizer identity",
    )
    _require_equal(
        dependencies["nltk_resources"], EXPECTED_NLTK_RESOURCE_HASHES,
        "gold NLTK resource hashes",
    )
    pool_receipts = provenance["pool_receipts"]
    if not isinstance(pool_receipts, list) or len(pool_receipts) != 9:
        raise ScoreError("gold pool provenance must contain exactly nine receipts")
    receipt_by_cell: dict[tuple[str, int], dict[str, Any]] = {}
    expected_pool_row_shape = {
        "ordinal", "raw_row_sha256", "canonical_row_sha256", "payload_sha256",
        "construction_tokens", "row_length",
    }
    seen_pool_payload_hashes: set[str] = set()
    seen_pool_raw_hashes: set[str] = set()
    for receipt in pool_receipts:
        if not isinstance(receipt, dict) or set(receipt) != {
            "task", "target_length", "generator_seed", "generation_cwd",
            "generation_argv", "rows"
        }:
            raise ScoreError("gold pool receipt has an unexpected object shape")
        cell = (receipt["task"], receipt["target_length"])
        if cell in receipt_by_cell or cell not in plan_seeds:
            raise ScoreError("gold pool receipt cell is duplicate or invalid")
        _require_equal(
            receipt["generator_seed"], plan_seeds[cell],
            f"gold pool receipt derived seed for {cell}",
        )
        _require_equal(
            seeds_by_cell[cell], {plan_seeds[cell]},
            f"gold selected fixture seeds for {cell}",
        )
        if not isinstance(receipt["generation_cwd"], str) or not receipt["generation_cwd"]:
            raise ScoreError(f"gold pool receipt generation cwd for {cell} is invalid")
        argv = receipt["generation_argv"]
        if not isinstance(argv, list) or any(not isinstance(value, str) for value in argv):
            raise ScoreError(f"gold pool receipt generation argv for {cell} is invalid")
        cwd = Path(receipt["generation_cwd"])
        if cwd != Path("/RULER/scripts/data"):
            raise ScoreError(f"gold pool receipt generation cwd for {cell} is not /RULER/scripts/data")
        if (
            len(argv) != 28
            or argv[:6] != [
                python_identity["executable"], "-I", "-S", "-B", "-c",
                ISOLATED_GENERATION_BOOTSTRAP,
            ]
        ):
            raise ScoreError(f"gold pool receipt argv shape for {cell} is invalid")
        site_packages = Path(argv[6])
        prepare_path = Path(argv[7])
        save_dir = Path(argv[9])
        if (
            site_packages != Path("/RUNTIME/site-packages")
            or prepare_path != Path("/RULER/scripts/data/prepare.py")
            or save_dir != Path(f"/POOL/{cell[1]}")
        ):
            raise ScoreError(f"gold pool receipt isolated paths for {cell} are invalid")
        expected_argv = [
            python_identity["executable"], "-I", "-S", "-B", "-c",
            ISOLATED_GENERATION_BOOTSTRAP, argv[6], argv[7],
            "--save_dir", argv[9], "--benchmark", "synthetic", "--task", cell[0],
            "--subset", "test", "--tokenizer_path", "cl100k_base",
            "--tokenizer_type", "openai", "--max_seq_length", str(cell[1]),
            "--model_template_type", "base", "--num_samples", "100",
            "--random_seed", str(plan_seeds[cell]),
        ]
        _require_equal(argv, expected_argv, f"gold pool receipt exact argv for {cell}")
        pool_rows = receipt["rows"]
        if not isinstance(pool_rows, list) or len(pool_rows) != 100:
            raise ScoreError(f"gold pool receipt for {cell} is not an exact 100-row pool")
        row_by_ordinal: dict[int, dict[str, Any]] = {}
        for pool_row in pool_rows:
            if not isinstance(pool_row, dict):
                raise ScoreError(f"gold pool receipt for {cell} has an invalid row")
            expected_shape = set(expected_pool_row_shape)
            if cell[0] == "niah_multikey_3":
                expected_shape.add("token_position_answer")
            if set(pool_row) != expected_shape:
                raise ScoreError(f"gold pool row for {cell} has an unexpected shape")
            pool_ordinal = pool_row["ordinal"]
            if type(pool_ordinal) is not int or not 0 <= pool_ordinal < 100:
                raise ScoreError(f"gold pool receipt for {cell} has invalid ordinal")
            if pool_ordinal in row_by_ordinal:
                raise ScoreError(f"gold pool receipt for {cell} repeats an ordinal")
            for key in ("raw_row_sha256", "canonical_row_sha256", "payload_sha256"):
                if not _is_sha256(pool_row[key]):
                    raise ScoreError(f"gold pool receipt for {cell} has invalid {key}")
            if pool_row["payload_sha256"] in seen_pool_payload_hashes:
                raise ScoreError("gold 900-row pool repeats a payload hash")
            if pool_row["raw_row_sha256"] in seen_pool_raw_hashes:
                raise ScoreError("gold 900-row pool repeats a raw-row hash")
            seen_pool_payload_hashes.add(pool_row["payload_sha256"])
            seen_pool_raw_hashes.add(pool_row["raw_row_sha256"])
            construction_tokens = pool_row["construction_tokens"]
            row_length = pool_row["row_length"]
            if (
                not _positive_int(construction_tokens)
                or type(row_length) is not int
                or construction_tokens + TASK_RESERVES[cell[0]] != row_length
                or row_length > cell[1]
            ):
                raise ScoreError(f"gold pool receipt for {cell} has invalid lengths")
            if cell[0] == "niah_multikey_3" and (
                type(pool_row["token_position_answer"]) is not int
                or not 0 <= pool_row["token_position_answer"] < row_length
            ):
                raise ScoreError(f"gold pool receipt for {cell} has invalid answer position")
            row_by_ordinal[pool_ordinal] = pool_row
        if set(row_by_ordinal) != set(range(100)):
            raise ScoreError(f"gold pool receipt for {cell} lacks exact ordinals 0..99")
        # Keep ordinal-indexed order independent of receipt list ordering.
        receipt_by_cell[cell] = {**receipt, "rows": [row_by_ordinal[i] for i in range(100)]}
    if set(receipt_by_cell) != set(plan_seeds):
        raise ScoreError("gold pool receipt cells are incomplete")

    selected_by_id: dict[str, tuple[dict[str, Any], dict[str, Any], tuple[str, int]]] = {}
    for cell, receipt in receipt_by_cell.items():
        for pool_row, selection in _select_pool_rows(
            receipt["rows"], cell[0], cell[1], master_key
        ):
            fixture_id = _fixture_id(master_key, cell[0], cell[1], pool_row)
            if fixture_id in selected_by_id:
                raise ScoreError("derived gold fixture id collision")
            selected_by_id[fixture_id] = (pool_row, selection, cell)
    if set(selected_by_id) != set(fixtures):
        raise ScoreError("public fixture ids differ from precommitted HMAC selection")
    for item in entries:
        fixture_id = item["id"]
        public = fixtures[fixture_id]
        pool_row, expected_selection, cell = selected_by_id[fixture_id]
        raw_row_utf8 = item["raw_row_utf8"]
        if not isinstance(raw_row_utf8, str):
            raise ScoreError(f"gold fixture {fixture_id} raw_row_utf8 must be text")
        try:
            raw_row_bytes = raw_row_utf8.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ScoreError(f"gold fixture {fixture_id} raw row has invalid Unicode: {exc}") from exc
        _require_equal(
            sha256_bytes(raw_row_bytes), item["raw_row_sha256"],
            f"gold fixture {fixture_id} exact raw row hash",
        )
        raw_row = _decode_json(raw_row_utf8, f"gold fixture {fixture_id} raw row")
        if not isinstance(raw_row, dict):
            raise ScoreError(f"gold fixture {fixture_id} raw row is not an object")
        expected_raw_keys = {
            "index", "input", "outputs", "length", "length_w_model_temp", "answer_prefix"
        }
        if cell[0] == "niah_multikey_3":
            expected_raw_keys.add("token_position_answer")
        if set(raw_row) != expected_raw_keys:
            raise ScoreError(f"gold fixture {fixture_id} raw row shape is invalid")
        if (
            type(raw_row["index"]) is not int
            or not isinstance(raw_row["input"], str)
            or not raw_row["input"]
            or not isinstance(raw_row["answer_prefix"], str)
            or not raw_row["answer_prefix"]
        ):
            raise ScoreError(f"gold fixture {fixture_id} raw row identity types are invalid")
        _require_equal(raw_row["outputs"], item["outputs"], f"gold fixture {fixture_id} raw outputs")
        _validate_raw_task_semantics(
            cell[0], cell[1], pool_row["ordinal"], raw_row, pool_row
        )
        _require_equal(raw_row["length"], public["row_length"], f"gold fixture {fixture_id} raw length")
        _require_equal(
            raw_row["length_w_model_temp"], public["row_length"],
            f"gold fixture {fixture_id} templated row length",
        )
        expected_payload = (raw_row["input"] + raw_row["answer_prefix"]).encode("utf-8")
        _require_equal(expected_payload, public["_payload_bytes"], f"gold fixture {fixture_id} exact payload")
        canonical_row_sha = sha256_bytes(canonical_json_file_bytes(raw_row))
        _require_equal(
            canonical_row_sha, item["canonical_row_sha256"],
            f"gold fixture {fixture_id} canonical row hash",
        )
        if cell[0] == "niah_multikey_3":
            _require_equal(
                raw_row["token_position_answer"], pool_row["token_position_answer"],
                f"gold fixture {fixture_id} NIAH answer position",
            )
        _require_equal(
            (public["task"], public["target_length"]), cell,
            f"gold fixture {fixture_id} derived cell",
        )
        _require_equal(
            item["selection"], expected_selection,
            f"gold fixture {fixture_id} HMAC selection receipt",
        )
        _require_equal(
            item["ordinal"], pool_row["ordinal"],
            f"gold fixture {fixture_id} selected ordinal",
        )
        for key in (
            "raw_row_sha256", "canonical_row_sha256", "payload_sha256"
        ):
            _require_equal(
                item[key], pool_row[key],
                f"gold fixture {fixture_id} {key} pool binding",
            )
        _require_equal(
            item["payload_sha256"], public["payload_sha256"],
            f"gold fixture {fixture_id} public payload hash",
        )
        _require_equal(
            pool_row["construction_tokens"], public["construction_tokens"],
            f"gold fixture {fixture_id} public construction token count",
        )
        _require_equal(
            pool_row["row_length"], public["row_length"],
            f"gold fixture {fixture_id} public row length",
        )
    return document, outputs_by_id


# This is the upstream NVIDIA/RULER string_match_all definition, kept at its
# original 0..100 scale and two-decimal rounding for coverage compatibility.
def string_match_all(preds: Sequence[str], refs: Sequence[Sequence[str]]) -> float:
    score = sum(
        [
            sum([1.0 if r.lower() in pred.lower() else 0.0 for r in ref]) / len(ref)
            for pred, ref in zip(preds, refs)
        ]
    ) / len(preds) * 100
    return round(score, 2)


def official_ruler_coverage(prediction: str, references: Sequence[str]) -> float:
    if not references:
        raise ScoreError("official RULER coverage requires at least one reference")
    return sum(1.0 if ref.lower() in prediction.lower() else 0.0 for ref in references) / len(references)


def _ascii_lower(text: str) -> str:
    return "".join(chr(ord(char) + 32) if "A" <= char <= "Z" else char for char in text)


def _formatting_only_with_answers(text: str) -> bool:
    """Parse punctuation-only answer lists with optional line-leading ordinals."""
    sentinel = "\x00"
    for line in text.splitlines():
        # Every nonempty logical line with an ordinal must label an answer on
        # that same line; ordinals left after an answer or on empty lines fail.
        ordinal = re.match(r"^[ \t]*[1-9][0-9]*[.)][ \t]*(?=\x00)", line)
        if ordinal:
            line = line[ordinal.end():]
        elif re.search(r"[0-9]", line):
            return False
        for char in line:
            if char == sentinel or char.isspace() or char in string.punctuation:
                continue
            if unicodedata.category(char).startswith("P"):
                continue
            return False
    return True


def exact_set(prediction: str, references: Sequence[str]) -> bool:
    """Require each expected ASCII literal once and reject foreign content."""
    if not isinstance(prediction, str) or not references:
        return False
    if any(
        unicodedata.category(char).startswith("C") and char not in "\n\r\t"
        for char in prediction
    ):
        return False
    if any(not isinstance(value, str) or not value or not value.isascii() for value in references):
        return False
    folded_prediction = _ascii_lower(prediction)
    folded_references = [_ascii_lower(value) for value in references]
    if len(set(folded_references)) != len(references):
        return False
    matches: list[tuple[int, int]] = []
    for expected in folded_references:
        positions: list[int] = []
        start = 0
        while True:
            position = folded_prediction.find(expected, start)
            if position < 0:
                break
            positions.append(position)
            start = position + 1
        if len(positions) != 1:
            return False
        end = positions[0] + len(expected)
        # Explicit ASCII folding must never allow a Unicode homoglyph slice.
        if not prediction[positions[0]:end].isascii():
            return False
        matches.append((positions[0], end))
    ordered = sorted(matches)
    if any(left[1] > right[0] for left, right in zip(ordered, ordered[1:])):
        return False
    marked = prediction
    for start, end in sorted(matches, reverse=True):
        marked = marked[:start] + "\x00" + marked[end:]
    return _formatting_only_with_answers(marked)


def _mean(values: Iterable[float]) -> float | None:
    collected = list(values)
    return sum(collected) / len(collected) if collected else None


def _percent(value: float | None) -> float | None:
    return None if value is None else round(value * 100.0, 2)


def normalize_operational_failure(
    row: dict[str, Any], independent_audit: dict[str, Any]
) -> dict[str, Any] | None:
    if row.get("execution_success") is True:
        return None
    raw = row.get("failure")
    raw_copy = copy.deepcopy(raw) if isinstance(raw, dict) else raw
    kind = str(raw.get("kind", "")) if isinstance(raw, dict) else ""
    message = str(raw.get("message", "")) if isinstance(raw, dict) else ""
    combined = f"{kind} {message}".lower()
    candidates: set[str] = {"other_execution"}
    leak = independent_audit.get("root_context_leak")
    if isinstance(leak, dict) and leak.get("detected") is True:
        candidates.add("root_context_leak")
    if kind in OPERATIONAL_FAILURE_PRECEDENCE:
        candidates.add(kind)
    if row.get("timed_out") is True or "timeout" in combined or "timed out" in combined:
        candidates.add("timeout")
    if any(token in combined for token in (
        "maximum rlm depth", "max depth", "depth limit", "recursion depth", "rlm_depth",
    )) or kind == "depth":
        candidates.add("depth")
    if any(token in combined for token in (
        "monty", "python subset", "unsupported syntax", "unsupported import",
        "solo solve cell", "patternerror", "semantic prompt envelope",
    )) or kind == "monty_subset_tax":
        candidates.add("monty_subset_tax")
    if any(token in combined for token in (
        "adapter", "parser", "parse", "malformed", "invalid json", "empty_response",
        "extract_final", "usage_evidence", "trace_capture",
    )) or kind == "adapter_parser":
        candidates.add("adapter_parser")
    if any(token in combined for token in (
        "transport", "provider", "connection", "network", "oauth", "route_assertion",
    )) or kind == "transport":
        candidates.add("transport")
    category = next(name for name in OPERATIONAL_FAILURE_PRECEDENCE if name in candidates)
    return {
        "category": category,
        "raw": raw_copy,
    }


def _failure_kind(score_row: dict[str, Any]) -> str:
    failure = score_row.get("operational_failure")
    return str(failure["category"]) if isinstance(failure, dict) else "other_execution"


def build_score_rows(
    rows: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
    fixtures: dict[str, dict[str, Any]],
    outputs_by_id: dict[str, tuple[str, ...]],
    *,
    independent_audits: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    independent_audits = independent_audits or {}
    for row, job in zip(rows, jobs):
        fixture_id = job["fixture_id"]
        audit = independent_audits.get(job["run_id"], {
            "root_context_leak": {
                "applicable": job["arm"] == "jcode-azdaja", "scanned": False,
                "detected": False, "minimum_match_chars": ROOT_LEAK_MIN_CHARS,
                "matched_text_retained": False, "missing_reason": "independent audit unavailable",
            },
            "root_token_economy": {
                "root_tokens": None, "authority": "unavailable", "missing": True,
                "fallback_used": False, "source_chars": None,
                "missing_reason": "independent audit unavailable",
            },
            "performance_ledger": None,
        })
        references = outputs_by_id[fixture_id]
        prediction = row["response"]
        coverage = official_ruler_coverage(prediction, references)
        strict = exact_set(prediction, references)
        execution_success = row["execution_success"]
        scored.append(
            {
                "run_id": job["run_id"],
                "ordinal": job["ordinal"],
                "fixture_id": fixture_id,
                "task": fixtures[fixture_id]["task"],
                "target_length": fixtures[fixture_id]["target_length"],
                "arm": job["arm"],
                "repetition": job["repetition"],
                "execution_success": execution_success,
                "operational_failure": normalize_operational_failure(row, audit),
                "root_context_leak": audit["root_context_leak"],
                "root_token_economy": audit["root_token_economy"],
                "performance_ledger": audit["performance_ledger"],
                "response_sha256": sha256_bytes(prediction.encode("utf-8")),
                "official_ruler_coverage": coverage,
                "official_ruler_coverage_percent": round(coverage * 100.0, 2),
                "exact_set": strict,
                "end_to_end_official_ruler_coverage": coverage if execution_success else 0.0,
                "end_to_end_exact_set": execution_success and strict,
            }
        )
    return scored


def _cell_summary(
    score_rows: Sequence[dict[str, Any]], raw_by_run: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    scheduled = len(score_rows)
    completed = [item for item in score_rows if item["execution_success"]]
    execution_failures = [item for item in score_rows if not item["execution_success"]]
    raw_rows = [raw_by_run[item["run_id"]] for item in score_rows]
    taxonomy = Counter(_failure_kind(item) for item in execution_failures)
    raw_taxonomy: Counter[str] = Counter()
    for item in execution_failures:
        raw_failure = raw_by_run[item["run_id"]].get("failure")
        raw_taxonomy[
            str(raw_failure.get("kind", "missing"))
            if isinstance(raw_failure, dict) else "missing"
        ] += 1
    official = _mean(float(item["official_ruler_coverage"]) for item in score_rows)
    exact = _mean(float(item["exact_set"]) for item in score_rows)
    end_official = _mean(float(item["end_to_end_official_ruler_coverage"]) for item in score_rows)
    end_exact = _mean(float(item["end_to_end_exact_set"]) for item in score_rows)
    completed_official = _mean(float(item["official_ruler_coverage"]) for item in completed)
    completed_exact = _mean(float(item["exact_set"]) for item in completed)
    latencies = [float(row["latency_seconds"]) for row in raw_rows]
    usages = [row.get("usage") for row in raw_rows]
    usage_n = sum(
        isinstance(usage, dict) and usage.get("accounting_complete") is True
        for usage in usages
    )
    usage_totals = None
    if usage_n == scheduled:
        usage_totals = {
            key: sum(int(usage[key]) for usage in usages)
            for key in (
                "input_tokens", "output_tokens", "cache_read_tokens",
                "cache_write_tokens", "total_tokens",
            )
        }
    route_valid_n = sum(
        row["route_assertion"]["asserted"]
        and row["route_assertion"]["subscription"]
        for row in raw_rows
    )
    lifecycle_valid_n = sum(
        all(row["lifecycle_assertion"].values()) for row in raw_rows
    )
    economy_rows = [item["root_token_economy"] for item in score_rows]
    economy_values = [
        float(item["root_tokens"]) for item in economy_rows
        if item.get("missing") is False
        and type(item.get("root_tokens")) in (int, float)
        and math.isfinite(float(item["root_tokens"]))
        and float(item["root_tokens"]) >= 0
    ]
    economy_authorities = Counter(str(item.get("authority")) for item in economy_rows)
    return {
        "scheduled_n": scheduled,
        "execution": {
            "completed_n": len(completed),
            "failed_n": len(execution_failures),
            "success_rate": len(completed) / scheduled,
            "failure_taxonomy": dict(sorted(taxonomy.items())),
            "raw_failure_taxonomy": dict(sorted(raw_taxonomy.items())),
        },
        "root_token_economy": {
            "available_n": len(economy_values),
            "missing_n": scheduled - len(economy_values),
            "coverage_rate": len(economy_values) / scheduled,
            "total_root_tokens": sum(economy_values) if economy_values else None,
            "mean_root_tokens": _mean(economy_values),
            "p50_root_tokens": percentile(economy_values, 0.50) if economy_values else None,
            "p95_root_tokens": percentile(economy_values, 0.95) if economy_values else None,
            "authority_counts": dict(sorted(economy_authorities.items())),
            "missing_is_explicit_per_score_row": True,
        },
        "telemetry_all_attempts": {
            "latency_seconds": {
                "n": scheduled,
                "total": sum(latencies),
                "p50": percentile(latencies, 0.50),
                "p95": percentile(latencies, 0.95),
            },
            "usage": {
                "valid_n": usage_n,
                "coverage_rate": usage_n / scheduled,
                "unconditional_totals": usage_totals,
            },
            "route_integrity": {
                "asserted_n": route_valid_n,
                "failed_n": scheduled - route_valid_n,
            },
            "lifecycle_integrity": {
                "asserted_n": lifecycle_valid_n,
                "failed_n": scheduled - lifecycle_valid_n,
            },
        },
        "output_scores_all_terminal_rows": {
            "official_ruler_coverage_percent": _percent(official),
            "exact_set_n": sum(bool(item["exact_set"]) for item in score_rows),
            "exact_set_rate": exact,
        },
        "correctness_completed_only": {
            "n": len(completed),
            "official_ruler_coverage_percent": _percent(completed_official),
            "exact_set_n": sum(bool(item["exact_set"]) for item in completed),
            "exact_set_rate": completed_exact,
        },
        "end_to_end_fixed_denominator": {
            "official_ruler_coverage_percent": _percent(end_official),
            "exact_set_n": sum(bool(item["end_to_end_exact_set"]) for item in score_rows),
            "exact_set_rate": end_exact,
        },
        "failure_separation": {
            "execution_failure_n": len(execution_failures),
            "completed_strict_failure_n": sum(not item["exact_set"] for item in completed),
            "completed_official_incomplete_n": sum(
                float(item["official_ruler_coverage"]) < 1.0 for item in completed
            ),
            "completed_official_full_but_strict_failed_n": sum(
                float(item["official_ruler_coverage"]) == 1.0 and not item["exact_set"]
                for item in completed
            ),
        },
    }


def aggregate_scores(
    score_rows: list[dict[str, Any]],
    raw_rows: list[dict[str, Any]],
    arms: Sequence[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw_by_run = {row["run_id"]: row for row in raw_rows}
    arm_documents: dict[str, Any] = {}
    cell_documents: list[dict[str, Any]] = []
    for arm in arms:
        arm_rows = [item for item in score_rows if item["arm"] == arm]
        if len(arm_rows) != EXPECTED_FIXTURES:
            raise ScoreError(
                f"arm {arm} must retain the exact {EXPECTED_FIXTURES}-scheduled denominator"
            )
        summaries: list[dict[str, Any]] = []
        for task in TASKS:
            for length in TARGET_LENGTHS:
                selected = [
                    item for item in arm_rows
                    if item["task"] == task and item["target_length"] == length
                ]
                if len(selected) != EXPECTED_PER_CELL:
                    raise ScoreError(f"arm {arm} cell {(task, length)} is incomplete")
                summary = _cell_summary(selected, raw_by_run)
                summary.update({"arm": arm, "task": task, "target_length": length})
                summaries.append(summary)
                cell_documents.append(summary)
        macro = {
            "cell_count": len(summaries),
            "official_ruler_coverage_percent": round(
                100.0 * sum(
                    sum(
                        float(item["official_ruler_coverage"])
                        for item in arm_rows
                        if item["task"] == cell["task"]
                        and item["target_length"] == cell["target_length"]
                    ) / EXPECTED_PER_CELL
                    for cell in summaries
                ) / len(summaries),
                2,
            ),
            "exact_set_rate": sum(
                cell["output_scores_all_terminal_rows"]["exact_set_rate"]
                for cell in summaries
            ) / len(summaries),
            "execution_success_rate": sum(
                cell["execution"]["success_rate"] for cell in summaries
            ) / len(summaries),
            "end_to_end_official_ruler_coverage_percent": round(
                100.0 * sum(
                    sum(
                        float(item["end_to_end_official_ruler_coverage"])
                        for item in arm_rows
                        if item["task"] == cell["task"]
                        and item["target_length"] == cell["target_length"]
                    ) / EXPECTED_PER_CELL
                    for cell in summaries
                ) / len(summaries),
                2,
            ),
            "end_to_end_exact_set_rate": sum(
                cell["end_to_end_fixed_denominator"]["exact_set_rate"]
                for cell in summaries
            ) / len(summaries),
        }
        all_summary = _cell_summary(arm_rows, raw_by_run)
        completed_n = all_summary["execution"]["completed_n"]
        completed_correct_n = all_summary["correctness_completed_only"]["exact_set_n"]
        end_to_end_correct_n = all_summary["end_to_end_fixed_denominator"]["exact_set_n"]
        headline = {
            "scheduled_n": EXPECTED_FIXTURES,
            "executed_n": completed_n,
            "execution_rate": completed_n / EXPECTED_FIXTURES,
            "completed_correct_n": completed_correct_n,
            "completed_accuracy_denominator_n": completed_n,
            "completed_accuracy": (
                completed_correct_n / completed_n if completed_n else None
            ),
            "end_to_end_correct_n": end_to_end_correct_n,
            "end_to_end_accuracy_denominator_n": EXPECTED_FIXTURES,
            "end_to_end_accuracy": end_to_end_correct_n / EXPECTED_FIXTURES,
        }
        arm_documents[arm] = {
            "scheduled_n": EXPECTED_FIXTURES,
            "execution_rate": headline["execution_rate"],
            "completed_accuracy": headline["completed_accuracy"],
            "end_to_end_accuracy": headline["end_to_end_accuracy"],
            "headline": headline,
            "primary_end_to_end_fixed_denominator": {
                "macro_9_cell_official_ruler_coverage_percent": macro[
                    "end_to_end_official_ruler_coverage_percent"
                ],
                "macro_9_cell_exact_set_rate": macro["end_to_end_exact_set_rate"],
                "execution_success_rate": macro["execution_success_rate"],
            },
            "macro_9_cell": macro,
            "overall_fixed_denominator": all_summary,
            "secondary_output_correctness": all_summary[
                "output_scores_all_terminal_rows"
            ],
        }
    return arm_documents, cell_documents


def percentile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ScoreError("cannot compute a percentile of no values")
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def paired_comparisons(
    score_rows: list[dict[str, Any]],
    fixtures: dict[str, dict[str, Any]],
    arms: Sequence[str],
    *,
    seed: int,
    resamples: int,
) -> dict[str, Any]:
    if type(seed) is not int or type(resamples) is not int or resamples <= 0:
        raise ScoreError("bootstrap seed/resamples must be integers and resamples positive")
    by_key = {(item["fixture_id"], item["arm"]): item for item in score_rows}
    cells = [
        [
            fixture_id for fixture_id, fixture in fixtures.items()
            if fixture["task"] == task and fixture["target_length"] == length
        ]
        for task in TASKS for length in TARGET_LENGTHS
    ]
    metrics = (
        "official_ruler_coverage",
        "exact_set",
        "end_to_end_official_ruler_coverage",
        "end_to_end_exact_set",
        "execution_success",
    )
    result: dict[str, Any] = {}
    for arm_a, arm_b in itertools.combinations(arms, 2):
        observed: dict[str, float] = {}
        differences: dict[str, list[list[float]]] = {}
        for metric in metrics:
            per_cells: list[list[float]] = []
            for cell in cells:
                values = []
                for fixture_id in cell:
                    left = by_key[(fixture_id, arm_a)]
                    right = by_key[(fixture_id, arm_b)]
                    values.append(float(left[metric]) - float(right[metric]))
                per_cells.append(values)
            differences[metric] = per_cells
            observed[metric] = sum(sum(cell) / len(cell) for cell in per_cells) / len(per_cells)
        rng_seed = int.from_bytes(
            hashlib.sha256(f"{seed}:{arm_a}:{arm_b}".encode("utf-8")).digest()[:8],
            "big",
        )
        rng = random.Random(rng_seed)
        draws: dict[str, list[float]] = {metric: [] for metric in metrics}
        for _ in range(resamples):
            totals = {metric: 0.0 for metric in metrics}
            for cell_index, fixture_ids in enumerate(cells):
                choices = [rng.randrange(len(fixture_ids)) for _ in fixture_ids]
                for metric in metrics:
                    values = differences[metric][cell_index]
                    totals[metric] += sum(values[index] for index in choices) / len(choices)
            for metric in metrics:
                draws[metric].append(totals[metric] / len(cells))
        metric_documents = {}
        for metric in metrics:
            scale = 100.0 if "coverage" in metric else 1.0
            metric_documents[metric] = {
                "delta": observed[metric] * scale,
                "ci95": [
                    percentile(draws[metric], 0.025) * scale,
                    percentile(draws[metric], 0.975) * scale,
                ],
            }
        result[f"{arm_a}__minus__{arm_b}"] = {
            "paired_fixture_n": EXPECTED_FIXTURES,
            "stratification": "task+target_length (10 fixtures in each of 9 cells)",
            "metrics": metric_documents,
        }
    return result


def candidate_version_stamp(schedule: dict[str, Any]) -> dict[str, Any]:
    configuration = schedule["configuration"]
    candidate = configuration["candidate"]
    components = {
        name: {
            "sha256": item["sha256"],
            "bytes": item["bytes"],
            "mode": item["mode"],
        }
        for name, item in sorted(candidate["components"].items())
    }
    candidate_binary = components["azdaja"]
    executable = configuration["executables"]["azdaja"]
    executed_binary = {
        "sha256": executable["sha256"],
        "bytes": executable["bytes"],
        "version": executable["version"],
    }
    if any(candidate_binary[key] != executed_binary[key] for key in ("sha256", "bytes")):
        raise ScoreError("candidate version stamp binary/executable binding changed")
    return {
        "candidate_aggregate_sha256": candidate["sha256"],
        "components": components,
        "candidate_binary": dict(candidate_binary),
        "executed_azdaja": executed_binary,
        "candidate_binary_equals_executed_azdaja": True,
    }


def build_report(
    manifest_path: Path,
    gold_path: Path,
    runs_path: Path,
    *,
    schedule_path: Path | None = None,
    claims_root: Path | None = None,
    bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED,
    bootstrap_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
) -> dict[str, Any]:
    unresolved_manifest = lexical_absolute(Path(manifest_path))
    unresolved_runs = lexical_absolute(Path(runs_path))
    _reject_symlink_components(unresolved_manifest)
    _reject_symlink_components(unresolved_runs)
    if unresolved_manifest.is_symlink():
        raise ScoreError("public suite manifest must not be a symlink")
    if unresolved_runs.is_symlink():
        raise ScoreError("frozen inference JSONL must not be a symlink")
    manifest_path = unresolved_manifest
    runs_path = unresolved_runs
    # GOLD ORDERING INVARIANT: do not resolve(strict=True), stat, hash, or open
    # gold until validate_frozen_runs has proved every frozen job terminal.
    unresolved_gold = lexical_absolute(Path(gold_path))
    manifest, fixtures = load_public_manifest(manifest_path)
    schedule, jobs, rows, arms, independent_audits, leak_gate = validate_frozen_runs(
        manifest_path, manifest, fixtures, runs_path, schedule_path, claims_root
    )
    _reject_symlink_components(unresolved_gold)
    if unresolved_gold.is_symlink():
        raise ScoreError("owner-only gold must not be a symlink")
    gold_path = unresolved_gold
    gold, outputs_by_id = load_gold(gold_path, manifest, fixtures)
    scores = build_score_rows(
        rows, jobs, fixtures, outputs_by_id, independent_audits=independent_audits
    )
    arm_documents, cells = aggregate_scores(scores, rows, arms)
    comparisons = paired_comparisons(
        scores, fixtures, arms, seed=bootstrap_seed, resamples=bootstrap_resamples
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "ruler_exact_mini_deferred_scores",
        "suite_id": SUITE_ID,
        "candidate_version_stamp": candidate_version_stamp(schedule),
        "integrity": {
            "validated": True,
            "terminal_complete_before_gold_read": True,
            "root_context_leak_scan_complete_before_gold_read": leak_gate["complete"],
            "root_context_leak_pre_gold_gate": leak_gate,
            "root_context_leak_policy": {
                "minimum_exact_unicode_characters": ROOT_LEAK_MIN_CHARS,
                "rolling_hash_exact_verification": True,
                "normalization": "none",
                "exemptions": "none",
                "matched_text_retained": False,
                "false_success_rejected": True,
            },
            "operational_failure_normalization": {
                "precedence": list(OPERATIONAL_FAILURE_PRECEDENCE),
                "raw_failure_retained_per_score_row": True,
            },
            "manifest_sha256": sha256_bytes(canonical_json_file_bytes(manifest)),
            "manifest_identity_sha256": manifest_identity_sha256(manifest),
            "gold_sha256": manifest["gold_sha256"],
            "inference_jsonl_sha256": sha256_bytes(
                b"".join(canonical_json_file_bytes(row) for row in rows)
            ),
            "schedule_id": schedule["schedule_id"],
            "scheduled_jobs": len(jobs),
            "scheduled_per_arm": {arm: EXPECTED_FIXTURES for arm in arms},
            "exact_90_per_arm_asserted": all(
                sum(job["arm"] == arm for job in jobs) == EXPECTED_FIXTURES
                for arm in arms
            ),
            "terminal_rows": len(rows),
            "claims_and_completions": 2 * len(jobs),
            "claim_ledger_authenticated": False,
            "claim_ledger_limitation": (
                "local hashes detect accidental/inconsistent tampering but are not authenticated "
                "history against malicious same-owner deletion/retry; external signing or "
                "transparency is future work"
            ),
            "route_and_usage_internally_recomputed_from_retained_artifacts": all(
                row.get("execution_success") is True for row in rows
            ),
            "route_and_usage_replay_scope": {
                "successful_rows_replayed_n": sum(
                    row.get("execution_success") is True for row in rows
                ),
                "failed_rows_hash_bound_but_not_route_or_usage_replayed_n": sum(
                    row.get("execution_success") is not True for row in rows
                ),
            },
            "telemetry_limitation": (
                "route and usage are independently recomputed from securely rehashed retained "
                "streams only for execution-success rows. Failed-row artifacts remain hash-bound "
                "but their route and usage are not independently replayed. The all-attempt "
                "telemetry aggregates recorded controller assertions and normalized usage across "
                "scheduled rows, so failed-row entries in that aggregate are not replay-validated. "
                "Azdaja model traces are emitted by the candidate rather than provider-signed "
                "receipts; replay proves internal consistency, not provider authenticity. "
                "Lifecycle values remain local controller assertions, not signed attestations."
            ),
        },
        "bootstrap": {
            "seed": bootstrap_seed,
            "resamples": bootstrap_resamples,
            "method": "fixture-stratified percentile bootstrap within each of 9 cells",
        },
        "arms": arm_documents,
        "cells": cells,
        "comparisons": comparisons,
        "scores": scores,
        "gold_provenance": {
            key: gold[key]
            for key in ("manifest_identity_sha256",)
            if key in gold
        },
    }


def lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.path.expanduser(str(path))))


def _reject_symlink_components(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:-1]:
        current /= part
        if current.is_symlink():
            raise ScoreError(f"output path contains a symlink directory: {current}")


def atomic_create_private_json(path: Path, value: Any) -> None:
    path = lexical_absolute(path)
    _reject_symlink_components(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _reject_symlink_components(path)
    if path.parent.is_symlink() or path.is_symlink() or os.path.lexists(path):
        raise ScoreError(f"output path must be a fresh non-symlink entry: {path}")
    data = canonical_json_file_bytes(value)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise ScoreError(f"cannot exclusively create output {path}: {exc}") from exc
    try:
        if os.name == "posix":
            os.fchmod(fd, 0o600)
        written = 0
        while written < len(data):
            count = os.write(fd, data[written:])
            if count <= 0:
                raise ScoreError(f"short write while creating output {path}")
            written += count
        os.fsync(fd)
    finally:
        os.close(fd)
    if hasattr(os, "O_DIRECTORY"):
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--runs", required=True, type=Path)
    parser.add_argument("--schedule", type=Path, help="default: <runs>.schedule.json")
    parser.add_argument("--claims", type=Path, help="default: <runs>.claims")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    parser.add_argument("--bootstrap-resamples", type=int, default=DEFAULT_BOOTSTRAP_RESAMPLES)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build_report(
            args.manifest,
            args.gold,
            args.runs,
            schedule_path=args.schedule,
            claims_root=args.claims,
            bootstrap_seed=args.bootstrap_seed,
            bootstrap_resamples=args.bootstrap_resamples,
        )
        output = lexical_absolute(args.output)
        atomic_create_private_json(output, result)
    except (ScoreError, OSError) as exc:
        print(f"score error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "output": str(output),
        "schedule_id": result["integrity"]["schedule_id"],
        "scheduled_jobs": result["integrity"]["scheduled_jobs"],
        "macro_9_cell": {
            arm: metrics["macro_9_cell"] for arm, metrics in result["arms"].items()
        },
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
