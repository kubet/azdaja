#!/usr/bin/env python3
"""Integrity-checked JSON reporting for frozen OOLONG suite runs.

The reporter is intentionally independent of the benchmark controller and uses
only the Python standard library.  It will not summarize a partial or
unverifiable run: the inference JSONL and both controller sidecars must be
private regular files and their hashes and identities must agree exactly.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import itertools
import json
import math
import os
import random
import re
import stat
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

SCHEMA_VERSION = 1
BOOTSTRAP_SEED = 20260812
BOOTSTRAP_ITERATIONS = 2000
CAMPAIGN_MODEL = "gpt-5.6-luna"
CAMPAIGN_REASONING = "medium"
CAMPAIGN_ARMS = ("jcode-native", "prime-agent", "jcode-azdaja")
CAMPAIGN_FIXTURE_COUNT = 26
CAMPAIGN_REPETITIONS = 1
CAMPAIGN_SEED = 20260813
CAMPAIGN_TIMEOUT_SECONDS = 600
CAMPAIGN_ROW_COUNT = CAMPAIGN_FIXTURE_COUNT * len(CAMPAIGN_ARMS) * CAMPAIGN_REPETITIONS
SMALL_CLUSTER_COUNT = 10
USAGE_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
    "total_tokens",
)


class ReportError(RuntimeError):
    """The input artifacts cannot safely and unambiguously be reported."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        return json.loads(
            text,
            object_pairs_hook=_object_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ReportError(f"cannot parse {label}: {exc}") from exc


def require_private_regular(path: Path, label: str) -> None:
    """Require a non-symlink file owned by, and accessible only to, this user."""
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise ReportError(f"{label} is missing or unreadable: {path}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ReportError(f"{label} must be a regular non-symlink file: {path}")
    if os.name == "posix":
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ReportError(f"{label} must be owner-only: {path}")
        if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
            raise ReportError(f"{label} must be owned by the reporting user: {path}")


def require_private_directory(path: Path, label: str) -> None:
    """Require a non-symlink directory owned by and private to this user."""
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise ReportError(f"{label} is missing or unreadable: {path}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ReportError(f"{label} must be a directory and not a symlink: {path}")
    if os.name == "posix":
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ReportError(f"{label} must be owner-only: {path}")
        if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
            raise ReportError(f"{label} must be owned by the reporting user: {path}")


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    require_private_regular(path, label)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ReportError(f"cannot read {label} {path}: {exc}") from exc
    value = _decode_json(text, label)
    if not isinstance(value, dict):
        raise ReportError(f"{label} must contain a JSON object: {path}")
    return value


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _is_nonnegative_number(value: Any) -> bool:
    return (
        type(value) in (int, float)
        and math.isfinite(float(value))
        and value >= 0
    )


def _is_positive_number(value: Any) -> bool:
    return _is_nonnegative_number(value) and value > 0


def _require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ReportError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


ROOT_CONTEXT_LEAK_MIN_CHARS = 100
_ROLLING_HASH_BASE = 1_000_003
_ROLLING_HASH_MASK = (1 << 64) - 1
_FROZEN_FAILURE_KINDS = {
    "adapter_parser",
    "transport",
    "timeout",
    "depth",
    "monty_subset_tax",
    "other_execution",
    "root_context_leak",
}
_KNOWN_ARMS = set(CAMPAIGN_ARMS)


def _rolling_hash_windows(text: str, width: int) -> Iterable[tuple[int, int]]:
    if width <= 0 or len(text) < width:
        return
    power = pow(_ROLLING_HASH_BASE, width - 1, 1 << 64)
    value = 0
    for char in text[:width]:
        value = ((value * _ROLLING_HASH_BASE) + ord(char) + 1) & _ROLLING_HASH_MASK
    yield 0, value
    for offset in range(1, len(text) - width + 1):
        outgoing = ord(text[offset - 1]) + 1
        incoming = ord(text[offset + width - 1]) + 1
        value = (value - ((outgoing * power) & _ROLLING_HASH_MASK)) & _ROLLING_HASH_MASK
        value = ((value * _ROLLING_HASH_BASE) + incoming) & _ROLLING_HASH_MASK
        yield offset, value


def exact_common_substring_scan(
    context: str, transcript: str, *, minimum_chars: int = ROOT_CONTEXT_LEAK_MIN_CHARS
) -> dict[str, Any]:
    """Independent exact-Unicode rolling-hash scan with collision verification."""
    if type(minimum_chars) is not int or minimum_chars <= 0:
        raise ReportError("root-context leak threshold must be positive")
    index_transcript = len(transcript) <= len(context)
    indexed = transcript if index_transcript else context
    scanned = context if index_transcript else transcript
    buckets: dict[int, list[int]] = {}
    indexed_windows = 0
    for offset, value in _rolling_hash_windows(indexed, minimum_chars):
        buckets.setdefault(value, []).append(offset)
        indexed_windows += 1
    scanned_windows = 0
    for scan_offset, value in _rolling_hash_windows(scanned, minimum_chars):
        scanned_windows += 1
        for indexed_offset in buckets.get(value, ()):
            indexed_slice = indexed[indexed_offset : indexed_offset + minimum_chars]
            scanned_slice = scanned[scan_offset : scan_offset + minimum_chars]
            if indexed_slice != scanned_slice:
                continue
            context_offset = scan_offset if index_transcript else indexed_offset
            transcript_offset = indexed_offset if index_transcript else scan_offset
            return {
                "leak_detected": True,
                "minimum_match_chars": minimum_chars,
                "verified_match_chars": minimum_chars,
                "context_offset_chars": context_offset,
                "transcript_offset_chars": transcript_offset,
                "matched_substring_sha256": hashlib.sha256(
                    indexed_slice.encode("utf-8")
                ).hexdigest(),
                "context_chars": len(context),
                "transcript_chars": len(transcript),
                "indexed_windows": indexed_windows,
                "scanned_windows_through_match": scanned_windows,
                "matched_text_retained": False,
            }
    return {
        "leak_detected": False,
        "minimum_match_chars": minimum_chars,
        "verified_match_chars": None,
        "context_offset_chars": None,
        "transcript_offset_chars": None,
        "matched_substring_sha256": None,
        "context_chars": len(context),
        "transcript_chars": len(transcript),
        "indexed_windows": indexed_windows,
        "scanned_windows_through_match": scanned_windows,
        "matched_text_retained": False,
    }


def scan_context_file_against_solo_trace(
    context_path: Path,
    transcript_path: Path,
    *,
    expected_context_sha256: str,
    exact_transcript_preserved: bool,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "applicable": True,
        "asserted": False,
        "scan_complete": False,
        "leak_detected": None,
        "minimum_match_chars": ROOT_CONTEXT_LEAK_MIN_CHARS,
        "algorithm": "uint64 polynomial rolling hash with exact Unicode slice verification",
        "normalization": "none",
        "exemptions": "none; the complete AZDAJA_SOLO_TRACE text is scanned",
        "matched_text_retained": False,
        "authority": "exact fixture UTF-8 and exact preserved AZDAJA_SOLO_TRACE UTF-8",
        "missing_reasons": [],
    }
    if not exact_transcript_preserved:
        base["missing_reasons"].append(
            "AZDAJA_SOLO_TRACE was transformed before exact scanning authority was retained"
        )
        return base
    try:
        context_sha = sha256_path(context_path)
        transcript_sha = sha256_path(transcript_path)
        context = context_path.read_bytes().decode("utf-8")
        transcript = transcript_path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        base["missing_reasons"].append(
            f"cannot read exact UTF-8 scan inputs: {type(exc).__name__}: {exc}"
        )
        return base
    base["context_sha256"] = context_sha
    base["transcript_sha256"] = transcript_sha
    if context_sha != expected_context_sha256:
        base["missing_reasons"].append("fixture context SHA-256 differs from the frozen identity")
        return base
    finding = exact_common_substring_scan(context, transcript)
    base.update(finding)
    base["scan_complete"] = True
    base["asserted"] = finding["leak_detected"] is False
    return base


def normalize_failure_kind(failure: dict[str, Any] | None) -> str | None:
    if failure is None:
        return None
    raw_kind = failure.get("kind")
    raw_failure = {key: value for key, value in failure.items() if key != "normalized_kind"}
    text = json.dumps(raw_failure, sort_keys=True, ensure_ascii=False).lower()
    if raw_kind == "root_context_leak" or "root_context_leak" in text:
        return "root_context_leak"
    if raw_kind == "timeout" or re.search(r"\b(?:timed? out|timeout)\b", text):
        return "timeout"
    if raw_kind in {"depth", "depth_limit"} or re.search(
        r"(?:maximum|max|exceeded|exhausted|limit|budget).{0,32}(?:depth|recursion)|"
        r"(?:depth|recursion).{0,32}(?:maximum|max|exceeded|exhausted|limit|budget)", text
    ):
        return "depth"
    if raw_kind == "monty_subset_tax" or re.search(
        r"monty|python[- ]subset|subset.{0,24}(?:syntax|runtime)|"
        r"unsupported.{0,24}(?:syntax|import|operation|python)|compile error|"
        r"solo root python compile error|solo solve (?:cell runtime error|invalid regular expression)", text
    ):
        return "monty_subset_tax"
    if raw_kind == "adapter_parser" or re.search(
        r"adapter.{0,32}pars|pars.{0,32}adapter|response parser|solo root protocol|"
        r"malformed.{0,24}(?:adapter|provider response|event stream)", text
    ):
        return "adapter_parser"
    if raw_kind in {"route_assertion", "trace_capture", "usage_evidence", "transport"} or re.search(
        r"provider_call_failed|session_setup|transport|oauth|authentication|"
        r"connection|socket|http [45][0-9][0-9]|rate.?limit|service unavailable|"
        r"provider/model/api route|root provider|provider (?:turn|call|request).{0,32}(?:fail|unavailable|did not run)",
        text,
    ):
        return "transport"
    return "other_execution"


def _validate_executable_identity(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {
        "path", "sha256", "bytes", "version", "version_command"
    }:
        raise ReportError(f"frozen {label} executable identity fields are invalid")
    path = value.get("path")
    if not isinstance(path, str) or not path or not Path(path).is_absolute():
        raise ReportError(f"frozen {label} executable path is invalid")
    if not _is_sha256(value.get("sha256")):
        raise ReportError(f"frozen {label} executable SHA-256 is invalid")
    if type(value.get("bytes")) is not int or value["bytes"] <= 0:
        raise ReportError(f"frozen {label} executable byte count is invalid")
    if not isinstance(value.get("version"), str) or not value["version"].strip():
        raise ReportError(f"frozen {label} executable version is invalid")
    if value.get("version_command") != [path, "--version"]:
        raise ReportError(f"frozen {label} executable version command is invalid")
    return value


def expected_row_executables(arm: str, executables: dict[str, Any]) -> dict[str, Any]:
    keys = (
        ("jcode", "azdaja")
        if arm == "jcode-azdaja"
        else (("jcode",) if arm == "jcode-native" else ("prime-agent",))
    )
    try:
        return {key: executables[key] for key in keys}
    except KeyError as exc:
        raise ReportError(f"frozen executable identity missing for arm {arm}: {exc}") from exc


def validate_frozen_identity_stamp(
    configuration: dict[str, Any], arms: list[str]
) -> None:
    controller = configuration.get("controller")
    if not isinstance(controller, dict) or set(controller) != {"path", "sha256", "bytes"}:
        raise ReportError("frozen controller identity fields are invalid")
    if (
        not isinstance(controller.get("path"), str)
        or not controller["path"]
        or not _is_sha256(controller.get("sha256"))
        or type(controller.get("bytes")) is not int
        or controller["bytes"] <= 0
    ):
        raise ReportError("frozen controller identity is invalid")
    executables = configuration.get("executables")
    if not isinstance(executables, dict):
        raise ReportError("frozen executable identities must be an object")
    if set(arms).issubset(_KNOWN_ARMS):
        required = set()
        if any(arm.startswith("jcode") for arm in arms):
            required.add("jcode")
        if "jcode-azdaja" in arms:
            required.add("azdaja")
        if "prime-agent" in arms:
            required.add("prime-agent")
        if set(executables) != required:
            raise ReportError(
                f"frozen executable identity set is not exact (expected={sorted(required)}, "
                f"got={sorted(executables)})"
            )
    for label, identity in executables.items():
        if label not in {"jcode", "azdaja", "prime-agent"}:
            raise ReportError(f"unknown frozen executable identity: {label}")
        _validate_executable_identity(identity, label)

    candidate = configuration.get("candidate")
    treatment = "jcode-azdaja" in arms
    if not treatment:
        if candidate is not None:
            raise ReportError("frozen candidate is present without the Azdaja arm")
        return
    if not isinstance(candidate, dict) or set(candidate) != {"sha256", "components"}:
        raise ReportError("frozen candidate identity fields are invalid")
    components = candidate.get("components")
    expected_components = {"azdaja", "config.toml", "SKILL.md"}
    if not isinstance(components, dict) or set(components) != expected_components:
        raise ReportError("frozen candidate component set is not exact")
    for name, component in components.items():
        if not isinstance(component, dict) or set(component) != {"sha256", "bytes"}:
            raise ReportError(f"frozen candidate component fields are invalid: {name}")
        if not _is_sha256(component.get("sha256")):
            raise ReportError(f"frozen candidate component SHA-256 is invalid: {name}")
        if type(component.get("bytes")) is not int or component["bytes"] <= 0:
            raise ReportError(f"frozen candidate component byte count is invalid: {name}")
    expected_candidate_sha = hashlib.sha256(canonical_json_bytes({
        name: {"sha256": components[name]["sha256"], "bytes": components[name]["bytes"]}
        for name in sorted(components)
    })).hexdigest()
    _require_equal(candidate.get("sha256"), expected_candidate_sha, "frozen candidate identity")
    azdaja_executable = executables.get("azdaja")
    if not isinstance(azdaja_executable, dict):
        raise ReportError("frozen Azdaja candidate has no executable identity")
    for field in ("sha256", "bytes"):
        _require_equal(
            components["azdaja"].get(field),
            azdaja_executable.get(field),
            f"candidate azdaja/executable azdaja {field}",
        )


def validate_schedule(schedule: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    if schedule.get("schema_version") != 1:
        raise ReportError("frozen schedule schema_version must be 1")
    if schedule.get("record_type") != "oolong_frozen_schedule":
        raise ReportError("invalid frozen schedule record_type")
    schedule_id = schedule.get("schedule_id")
    if not _is_sha256(schedule_id):
        raise ReportError("frozen schedule has no valid schedule_id")

    unhashed = copy.deepcopy(schedule)
    unhashed.pop("schedule_id", None)
    unhashed_jobs = unhashed.get("jobs")
    if not isinstance(unhashed_jobs, list) or not unhashed_jobs:
        raise ReportError("frozen schedule jobs must be a nonempty list")
    for job in unhashed_jobs:
        if not isinstance(job, dict):
            raise ReportError("every frozen schedule job must be an object")
        job.pop("run_id", None)
    computed_schedule_id = hashlib.sha256(canonical_json_bytes(unhashed)).hexdigest()
    _require_equal(schedule_id, computed_schedule_id, "frozen schedule SHA-256 identity")

    configuration = schedule.get("configuration")
    suite = schedule.get("suite")
    if not isinstance(configuration, dict) or not isinstance(suite, dict):
        raise ReportError("frozen schedule must contain configuration and suite objects")
    arms = configuration.get("arms")
    repetitions = configuration.get("repetitions")
    if (
        not isinstance(arms, list)
        or not arms
        or any(not isinstance(arm, str) or not arm for arm in arms)
        or len(set(arms)) != len(arms)
    ):
        raise ReportError("frozen schedule configuration arms are invalid")
    if type(repetitions) is not int or repetitions <= 0:
        raise ReportError("frozen schedule repetitions must be positive")
    campaign_profile = {
        "model": CAMPAIGN_MODEL,
        "reasoning": CAMPAIGN_REASONING,
        "arms": list(CAMPAIGN_ARMS),
        "repetitions": CAMPAIGN_REPETITIONS,
        "seed": CAMPAIGN_SEED,
        "timeout_seconds": CAMPAIGN_TIMEOUT_SECONDS,
    }
    for field, expected in campaign_profile.items():
        _require_equal(
            configuration.get(field), expected,
            f"frozen campaign profile {field}",
        )
    controller = configuration.get("controller")
    if not isinstance(controller, dict) or not _is_sha256(controller.get("sha256")):
        raise ReportError("frozen schedule controller identity is invalid")
    validate_frozen_identity_stamp(configuration, list(arms))

    fixtures = suite.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ReportError("frozen schedule suite fixtures must be a nonempty list")
    _require_equal(
        len(fixtures), CAMPAIGN_FIXTURE_COUNT,
        "frozen campaign fixture count",
    )
    fixture_identity: dict[str, tuple[str, str]] = {}
    seen_row_hashes: set[str] = set()
    for item in fixtures:
        if not isinstance(item, dict):
            raise ReportError("frozen schedule fixture identity must be an object")
        fixture_id = item.get("fixture_id")
        row_sha = item.get("row_sha256")
        context_sha = item.get("context_sha256")
        if not isinstance(fixture_id, str) or not fixture_id:
            raise ReportError("frozen schedule fixture_id is invalid")
        if fixture_id in fixture_identity:
            raise ReportError(f"duplicate frozen schedule fixture_id: {fixture_id}")
        if not _is_sha256(row_sha) or not _is_sha256(context_sha):
            raise ReportError(f"invalid frozen hashes for fixture {fixture_id}")
        if row_sha in seen_row_hashes:
            raise ReportError(f"duplicate frozen row identity: {row_sha}")
        seen_row_hashes.add(row_sha)
        fixture_identity[fixture_id] = (row_sha, context_sha)
    manifest_sha = suite.get("manifest_sha256")
    if not _is_sha256(manifest_sha):
        raise ReportError("frozen schedule manifest_sha256 is invalid")

    jobs = schedule.get("jobs")
    assert isinstance(jobs, list)  # established on the deep copy above
    _require_equal(len(jobs), CAMPAIGN_ROW_COUNT, "frozen campaign scheduled row count")
    seen_runs: set[str] = set()
    seen_cells: set[tuple[str, int, str]] = set()
    expected_cells = {
        (fixture_id, repetition, arm)
        for fixture_id in fixture_identity
        for repetition in range(1, repetitions + 1)
        for arm in arms
    }
    for index, job in enumerate(jobs, 1):
        if not isinstance(job, dict):
            raise ReportError(f"frozen schedule job {index} is not an object")
        _require_equal(job.get("ordinal"), index, f"job {index} ordinal")
        fixture_id = job.get("fixture_id")
        arm = job.get("arm")
        repetition = job.get("repetition")
        if fixture_id not in fixture_identity:
            raise ReportError(f"job {index} references an unknown fixture")
        if arm not in arms:
            raise ReportError(f"job {index} references an unknown arm")
        if type(repetition) is not int or not 1 <= repetition <= repetitions:
            raise ReportError(f"job {index} repetition is invalid")
        _require_equal(
            (job.get("row_sha256"), job.get("context_sha256")),
            fixture_identity[fixture_id],
            f"job {index} fixture hashes",
        )
        run_id = job.get("run_id")
        if not _is_sha256(run_id) or run_id in seen_runs:
            raise ReportError(f"job {index} has an invalid or duplicate run_id")
        base_job = dict(job)
        del base_job["run_id"]
        expected_run_id = hashlib.sha256(
            b"oolong-run-v1\0"
            + schedule_id.encode("ascii")
            + canonical_json_bytes(base_job)
        ).hexdigest()
        _require_equal(run_id, expected_run_id, f"job {index} run_id")
        cell = (fixture_id, repetition, arm)
        if cell in seen_cells:
            raise ReportError(f"duplicate scheduled fixture/repetition/arm cell: {cell}")
        seen_runs.add(run_id)
        seen_cells.add(cell)
    if seen_cells != expected_cells:
        missing = len(expected_cells - seen_cells)
        extra = len(seen_cells - expected_cells)
        raise ReportError(
            f"frozen schedule is not a complete fixture/repetition/arm grid "
            f"(missing={missing}, extra={extra})"
        )
    return jobs, list(arms)


def load_raw_rows(path: Path) -> list[dict[str, Any]]:
    require_private_regular(path, "raw suite output")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ReportError(f"cannot read raw suite output {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            raise ReportError(f"blank raw suite output row at line {line_number}")
        value = _decode_json(line, f"raw suite output line {line_number}")
        if not isinstance(value, dict):
            raise ReportError(f"raw suite output line {line_number} is not an object")
        rows.append(value)
    if not rows:
        raise ReportError("raw suite output is empty")
    return rows


def validate_rows(
    rows: list[dict[str, Any]], jobs: list[dict[str, Any]], schedule: dict[str, Any]
) -> None:
    if len(rows) != len(jobs):
        raise ReportError(
            f"raw suite output is incomplete (scheduled={len(jobs)}, rows={len(rows)})"
        )
    configuration = schedule["configuration"]
    candidate = configuration.get("candidate")
    candidate_sha = None if candidate is None else candidate.get("sha256")
    if candidate_sha is not None and not _is_sha256(candidate_sha):
        raise ReportError("frozen candidate SHA-256 identity is invalid")
    model = configuration.get("model")
    reasoning = configuration.get("reasoning")
    if not isinstance(model, str) or not isinstance(reasoning, str):
        raise ReportError("frozen model/reasoning configuration is invalid")
    seen: set[str] = set()
    for line_number, (row, job) in enumerate(zip(rows, jobs), 1):
        expected = {
            "record_type": "inference",
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "fixture_id": job["fixture_id"],
            "row_sha256": job["row_sha256"],
            "context_sha256": job["context_sha256"],
            "execution_ordinal": job["ordinal"],
            "arm": job["arm"],
            "repetition": job["repetition"],
            "model": model,
            "reasoning": reasoning,
            "candidate_sha256": candidate_sha,
            "controller_sha256": configuration["controller"]["sha256"],
            "success": None,
            "score": None,
            "scoring_status": "deferred",
        }
        for key, expected_value in expected.items():
            _require_equal(
                row.get(key), expected_value, f"raw row {line_number} field {key}"
            )
        if type(row.get("execution_success")) is not bool:
            raise ReportError(f"raw row {line_number} lacks terminal execution status")
        if job["arm"] in _KNOWN_ARMS:
            expected_executables = expected_row_executables(
                job["arm"], configuration["executables"]
            )
            _require_equal(
                row.get("executables"), expected_executables,
                f"raw row {line_number} executable identities",
            )
            economy = row.get("root_token_economy")
            if not isinstance(economy, dict) or type(economy.get("missing")) is not bool:
                raise ReportError(f"raw row {line_number} root-token economy evidence is invalid")
            value = economy.get("root_input_tokens")
            if economy["missing"]:
                if value is not None or economy.get("authority_kind") != "missing":
                    raise ReportError(f"raw row {line_number} missing root-token evidence is inconsistent")
            elif not _is_nonnegative_number(value) or economy.get("authority_kind") not in {
                "provider_usage", "character_fallback"
            }:
                raise ReportError(f"raw row {line_number} root-token evidence is inconsistent")
            failure = row.get("failure")
            if failure is not None:
                if not isinstance(failure, dict):
                    raise ReportError(f"raw row {line_number} failure must be an object or null")
                normalized = normalize_failure_kind(failure)
                if normalized not in _FROZEN_FAILURE_KINDS:
                    raise ReportError(f"raw row {line_number} normalized failure is invalid")
                _require_equal(
                    failure.get("normalized_kind"), normalized,
                    f"raw row {line_number} normalized failure",
                )
        nested_fixture = row.get("fixture")
        if nested_fixture is not None:
            if not isinstance(nested_fixture, dict):
                raise ReportError(f"raw row {line_number} fixture identity is invalid")
            for key in ("row_sha256", "context_sha256"):
                _require_equal(
                    nested_fixture.get(key), job[key],
                    f"raw row {line_number} nested fixture {key}",
                )
        if row["run_id"] in seen:
            raise ReportError(f"duplicate raw run_id at line {line_number}")
        seen.add(row["run_id"])


def validate_claims(
    claims_root: Path,
    rows: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
    schedule: dict[str, Any],
) -> Path:
    """Validate the controller's one claim and one completion receipt per run."""
    require_private_directory(claims_root, "suite claims root")
    claims = claims_root / schedule["schedule_id"]
    require_private_directory(claims, "suite schedule claims directory")
    expected_names = {
        name
        for job in jobs
        for name in (job["run_id"] + ".json", job["run_id"] + ".done.json")
    }
    try:
        entries = list(claims.iterdir())
    except OSError as exc:
        raise ReportError(f"cannot enumerate suite completion artifacts: {exc}") from exc
    actual_names = {entry.name for entry in entries}
    if len(entries) != len(actual_names):
        # Directory entries cannot normally duplicate a name, but retain an
        # explicit fail-closed assertion rather than relying on that property.
        raise ReportError("suite completion artifact names are ambiguous")
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        raise ReportError(
            "suite completion artifacts are not the exact scheduled 2N set "
            f"(missing={missing}, extra={extra})"
        )
    for index, (row, job) in enumerate(zip(rows, jobs), 1):
        claim_path = claims / (job["run_id"] + ".json")
        done_path = claims / (job["run_id"] + ".done.json")
        claim = load_json_object(claim_path, f"suite run claim {index}")
        if set(claim) != {"schedule_id", "run_id", "ordinal", "pid"}:
            raise ReportError(f"suite run claim {index} has unexpected fields")
        for key, expected in (
            ("schedule_id", schedule["schedule_id"]),
            ("run_id", job["run_id"]),
            ("ordinal", job["ordinal"]),
        ):
            _require_equal(claim.get(key), expected, f"suite run claim {index} {key}")
        if type(claim.get("pid")) is not int or claim["pid"] <= 0:
            raise ReportError(f"suite run claim {index} pid is invalid")
        done = load_json_object(done_path, f"suite run completion {index}")
        expected_done = {
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "row_sha256": hashlib.sha256(canonical_json_bytes(row)).hexdigest(),
        }
        if done != expected_done:
            raise ReportError(f"suite run completion {index} receipt mismatch")
    return claims


def validate_scores(
    scores_document: dict[str, Any],
    scores_path: Path,
    raw_path: Path,
    rows: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
    schedule: dict[str, Any],
) -> list[dict[str, Any]]:
    if scores_document.get("schema_version") != 1:
        raise ReportError("scores schema_version must be 1")
    if scores_document.get("record_type") != "oolong_deferred_scores":
        raise ReportError("invalid scores record_type")
    _require_equal(
        scores_document.get("schedule_id"), schedule["schedule_id"], "scores schedule_id"
    )
    _require_equal(
        scores_document.get("manifest_sha256"),
        schedule["suite"]["manifest_sha256"],
        "scores manifest_sha256",
    )
    raw_sha = sha256_path(raw_path)
    _require_equal(
        scores_document.get("inference_jsonl_sha256"),
        raw_sha,
        "scores raw inference SHA-256",
    )
    scores = scores_document.get("scores")
    if not isinstance(scores, list) or len(scores) != len(jobs):
        count = len(scores) if isinstance(scores, list) else "invalid"
        raise ReportError(
            f"scores are incomplete (scheduled={len(jobs)}, scores={count})"
        )
    seen: set[str] = set()
    for index, (item, row, job) in enumerate(zip(scores, rows, jobs), 1):
        if not isinstance(item, dict):
            raise ReportError(f"score row {index} is not an object")
        expected = {
            "run_id": job["run_id"],
            "ordinal": job["ordinal"],
            "fixture_id": job["fixture_id"],
            "arm": job["arm"],
            "repetition": job["repetition"],
            "execution_success": row["execution_success"],
        }
        for key, expected_value in expected.items():
            _require_equal(item.get(key), expected_value, f"score row {index} field {key}")
        score = item.get("score")
        if not isinstance(score, dict) or type(score.get("correct")) is not bool:
            raise ReportError(f"score row {index} has no exact correctness boolean")
        if score.get("strict_exact") is not True:
            raise ReportError(f"score row {index} is not marked strict_exact")
        success = item.get("success")
        if type(success) is not bool:
            raise ReportError(f"score row {index} has no terminal success boolean")
        _require_equal(
            success,
            row["execution_success"] and score["correct"],
            f"score row {index} success",
        )
        if item["run_id"] in seen:
            raise ReportError(f"duplicate score run_id at row {index}")
        seen.add(item["run_id"])
    # Reading it was already protected, but naming the path in this validation
    # makes it explicit that no detached score object is accepted.
    require_private_regular(scores_path, "suite scores")
    return scores


def _metadata_value(item: dict[str, Any], key: str) -> Any:
    if key in item:
        return item[key]
    metadata = item.get("metadata")
    return metadata.get(key) if isinstance(metadata, dict) else None


def fixture_clusters(
    schedule: dict[str, Any], suite_document: dict[str, Any] | None
) -> tuple[dict[str, str], str, list[str]]:
    schedule_items = {
        item["fixture_id"]: item for item in schedule["suite"]["fixtures"]
    }
    suite_items: dict[str, dict[str, Any]] = {}
    if suite_document is not None:
        entries = suite_document.get("fixtures")
        if not isinstance(entries, list):
            raise ReportError("suite manifest fixtures must be a list")
        for item in entries:
            if not isinstance(item, dict) or not isinstance(item.get("fixture_id"), str):
                raise ReportError("suite manifest contains an invalid fixture entry")
            fixture_id = item["fixture_id"]
            if fixture_id in suite_items:
                raise ReportError(f"duplicate suite manifest fixture_id: {fixture_id}")
            suite_items[fixture_id] = item
        if set(suite_items) != set(schedule_items):
            raise ReportError("suite manifest fixture identities differ from the schedule")
        for fixture_id, scheduled in schedule_items.items():
            supplied = suite_items[fixture_id]
            for key in ("row_sha256", "context_sha256"):
                _require_equal(
                    supplied.get(key), scheduled.get(key),
                    f"suite manifest fixture {fixture_id} {key}",
                )
            for key in ("dataset", "context_window_id"):
                schedule_value = _metadata_value(scheduled, key)
                suite_value = _metadata_value(supplied, key)
                if schedule_value is not None and suite_value is not None:
                    _require_equal(
                        suite_value, schedule_value,
                        f"suite/schedule fixture {fixture_id} metadata {key}",
                    )

    metadata: dict[str, tuple[Any, Any]] = {}
    for fixture_id, scheduled in schedule_items.items():
        supplied = suite_items.get(fixture_id, {})
        dataset = _metadata_value(scheduled, "dataset")
        context_window = _metadata_value(scheduled, "context_window_id")
        if dataset is None:
            dataset = _metadata_value(supplied, "dataset")
        if context_window is None:
            context_window = _metadata_value(supplied, "context_window_id")
        if dataset is not None and context_window is not None:
            metadata[fixture_id] = (dataset, context_window)

    warnings: list[str] = []
    if len(metadata) == len(schedule_items):
        mapping = {
            fixture_id: "dataset+context_window_id:" + json.dumps(
                [values[0], values[1]],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            for fixture_id, values in metadata.items()
        }
        cluster_by = "dataset+context_window_id"
    else:
        mapping = {fixture_id: "fixture_id:" + fixture_id for fixture_id in schedule_items}
        cluster_by = "fixture_id"
        warnings.append(
            "dataset and context_window_id metadata were not available for every fixture; "
            "bootstrap clustering falls back to fixture_id"
        )
    return mapping, cluster_by, warnings


def validate_suite_manifest(
    path: Path, schedule: dict[str, Any]
) -> dict[str, Any]:
    """Hash-bind the manifest and its exact ordered fixture identity triples."""
    document = load_json_object(path, "suite manifest")
    _require_equal(
        sha256_path(path), schedule["suite"]["manifest_sha256"],
        "suite manifest SHA-256",
    )
    if document.get("schema_version") != 1:
        raise ReportError("suite manifest schema_version must be 1")
    for field in ("source", "split", "upstream_commit"):
        _require_equal(
            document.get(field), schedule["suite"].get(field),
            f"suite manifest {field}",
        )
    entries = document.get("fixtures")
    if not isinstance(entries, list):
        raise ReportError("suite manifest fixtures must be a list")
    identities: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for index, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            raise ReportError(f"suite manifest fixture {index} must be an object")
        fixture_id = entry.get("fixture_id")
        if not isinstance(fixture_id, str) or not fixture_id:
            raise ReportError(f"suite manifest fixture {index} fixture_id is invalid")
        if fixture_id in seen_ids:
            raise ReportError(f"duplicate suite manifest fixture_id: {fixture_id}")
        seen_ids.add(fixture_id)
        row_sha = entry.get("row_sha256")
        context_sha = entry.get("context_sha256")
        if not _is_sha256(row_sha) or not _is_sha256(context_sha):
            raise ReportError(f"suite manifest fixture {fixture_id} hashes are invalid")
        identities.append({
            "fixture_id": fixture_id,
            "row_sha256": row_sha,
            "context_sha256": context_sha,
        })
    _require_equal(
        identities, schedule["suite"]["fixtures"],
        "suite manifest fixture identity triples",
    )
    return document


def parse_gold(raw: Any, question: str) -> tuple[str, int | str, str]:
    """Independent copy of the controller's strict one-element gold parser."""
    if not isinstance(raw, str):
        raise ReportError("row 'answer' must be a string containing a one-element list")
    try:
        value = ast.literal_eval(raw)
    except (SyntaxError, ValueError) as exc:
        raise ReportError(f"row answer is not a one-element Python literal: {raw!r}") from exc
    if not isinstance(value, list) or len(value) != 1:
        raise ReportError(f"row answer must be a one-element list, got {raw!r}")
    item = value[0]
    requested = re.findall(r'''(?i)form\s+['"]([A-Za-z][A-Za-z0-9_-]*)\s*:''', question)
    kind = requested[-1].capitalize() if requested else (
        "Answer" if type(item) is int else "Label"
    )
    if type(item) is int and item >= 0:
        return kind, item, f"{kind}: {item}"
    if isinstance(item, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9 _-]*", item):
        return kind, item, f"{kind}: {item}"
    raise ReportError(f"unsupported OOLONG answer value: {item!r}")


def strict_score(text: str, row_metadata: dict[str, Any]) -> dict[str, Any]:
    """Independently reproduce the controller's exact score object."""
    question = row_metadata.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ReportError("suite row has no nonempty official question")
    expected_kind, expected_value, expected_canonical = parse_gold(
        row_metadata.get("answer"), question
    )
    answer_line = re.compile(
        rf"(?im)^\s*({re.escape(expected_kind)})\s*:\s*([^\r\n]+?)\s*$"
    )
    matches = answer_line.findall(text)
    normalized = text.strip()
    correct = normalized == expected_canonical
    parsed: int | str | None = None
    parse_error: str | None = None
    if len(matches) == 1:
        _, raw = matches[0]
        raw = raw.strip()
        if type(expected_value) is int and re.fullmatch(r"0|[1-9][0-9]*", raw):
            parsed = int(raw)
        elif isinstance(expected_value, str) and re.fullmatch(
            r"[A-Za-z][A-Za-z0-9 _-]*", raw
        ):
            parsed = raw
        else:
            parse_error = "answer value has invalid exact format"
    else:
        parse_error = f"expected exactly one {expected_kind} line, found {len(matches)}"
    if not correct and parse_error is None:
        parse_error = "output was not exactly the canonical gold answer"
    return {
        "correct": correct,
        "strict_exact": True,
        "expected": expected_canonical,
        "parsed_value": parsed,
        "parse_error": parse_error,
    }


def validate_independent_scores(
    manifest_path: Path,
    suite_document: dict[str, Any],
    rows: list[dict[str, Any]],
    scores: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
) -> None:
    entries = suite_document.get("fixtures")
    if not isinstance(entries, list):
        raise ReportError("suite manifest fixtures must be a list")
    parent = manifest_path.parent
    metadata_by_fixture: dict[str, dict[str, Any]] = {}
    for item in entries:
        if not isinstance(item, dict) or not isinstance(item.get("fixture_id"), str):
            raise ReportError("suite manifest contains an invalid fixture entry")
        fixture_id = item["fixture_id"]
        raw_row_path = item.get("row")
        if (
            not isinstance(raw_row_path, str)
            or not raw_row_path
            or Path(raw_row_path).is_absolute()
        ):
            raise ReportError(f"suite fixture {fixture_id} row path must be relative")
        unresolved = parent / raw_row_path
        if unresolved.is_symlink():
            raise ReportError(f"suite fixture {fixture_id} row must not be a symlink")
        try:
            row_path = unresolved.resolve(strict=True)
        except OSError as exc:
            raise ReportError(f"suite fixture {fixture_id} row is missing: {exc}") from exc
        if row_path.parent != parent.resolve():
            raise ReportError(f"suite fixture {fixture_id} row must stay in manifest directory")
        require_private_regular(row_path, f"suite fixture {fixture_id} row")
        expected_hash = item.get("row_sha256")
        if not _is_sha256(expected_hash):
            raise ReportError(f"suite fixture {fixture_id} row_sha256 is invalid")
        _require_equal(
            sha256_path(row_path), expected_hash,
            f"suite fixture {fixture_id} row SHA-256",
        )
        metadata = load_json_object(row_path, f"suite fixture {fixture_id} row")
        if metadata.get("source") != "oolongbench/oolong-synth":
            raise ReportError(f"suite fixture {fixture_id} is not OOLONG-synth")
        # Validate gold now, including fixtures that happened to fail execution.
        question = metadata.get("question")
        if not isinstance(question, str) or not question.strip():
            raise ReportError(f"suite fixture {fixture_id} has no official question")
        parse_gold(metadata.get("answer"), question)
        metadata_by_fixture[fixture_id] = metadata
    for index, (row, score, job) in enumerate(zip(rows, scores, jobs), 1):
        metadata = metadata_by_fixture.get(job["fixture_id"])
        if metadata is None:
            raise ReportError(f"score row {index} has no independently loaded fixture")
        independently_scored = strict_score(str(row.get("response", "")), metadata)
        if score.get("score") != independently_scored:
            raise ReportError(
                f"score row {index} differs from independent strict_score recomputation"
            )


def independently_validate_root_context_leaks(
    manifest_path: Path | None,
    suite_document: dict[str, Any] | None,
    rows: list[dict[str, Any]],
    scores: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
) -> dict[str, int]:
    """Independently re-open exact fixtures/traces and enforce the leak hard gate."""
    azdaja_indexes = [index for index, job in enumerate(jobs) if job["arm"] == "jcode-azdaja"]
    if not azdaja_indexes:
        return {"applicable_rows": 0, "scanned_rows": 0, "leak_rows": 0, "missing_rows": 0}
    if manifest_path is None or suite_document is None:
        raise ReportError(
            "--suite-manifest is required to independently scan Azdaja root transcripts"
        )
    entries = suite_document.get("fixtures")
    if not isinstance(entries, list):
        raise ReportError("suite manifest fixtures must be a list")
    parent = manifest_path.parent.resolve()
    contexts: dict[str, Path] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("fixture_id"), str):
            raise ReportError("suite manifest contains an invalid fixture entry")
        fixture_id = entry["fixture_id"]
        raw_context = entry.get("context")
        if not isinstance(raw_context, str) or not raw_context or Path(raw_context).is_absolute():
            raise ReportError(f"suite fixture {fixture_id} context path must be relative")
        unresolved = manifest_path.parent / raw_context
        if unresolved.is_symlink():
            raise ReportError(f"suite fixture {fixture_id} context must not be a symlink")
        try:
            context = unresolved.resolve(strict=True)
        except OSError as exc:
            raise ReportError(f"suite fixture {fixture_id} context is missing: {exc}") from exc
        if context.parent != parent:
            raise ReportError(f"suite fixture {fixture_id} context must stay in manifest directory")
        require_private_regular(context, f"suite fixture {fixture_id} context")
        expected_hash = entry.get("context_sha256")
        if not _is_sha256(expected_hash):
            raise ReportError(f"suite fixture {fixture_id} context_sha256 is invalid")
        _require_equal(
            sha256_path(context), expected_hash,
            f"suite fixture {fixture_id} context SHA-256",
        )
        contexts[fixture_id] = context

    scanned = 0
    leaked = 0
    missing = 0
    for index in azdaja_indexes:
        row = rows[index]
        score = scores[index]
        job = jobs[index]
        context = contexts.get(job["fixture_id"])
        if context is None:
            raise ReportError(f"Azdaja row {index + 1} has no exact fixture context")
        artifacts = row.get("trajectory_artifacts")
        metadata = artifacts.get("azdaja_solo_trace") if isinstance(artifacts, dict) else None
        if not isinstance(metadata, dict):
            raise ReportError(
                f"Azdaja row {index + 1} lacks mandatory exact root transcript authority"
            )
        raw_trace = metadata.get("path")
        if not isinstance(raw_trace, str) or not raw_trace:
            raise ReportError(f"Azdaja row {index + 1} solo trace path is invalid")
        trace = Path(os.path.abspath(Path(raw_trace).expanduser()))
        require_private_regular(trace, f"Azdaja row {index + 1} solo trace")
        if trace.name != "azdaja-solo-trace.log":
            raise ReportError(f"Azdaja row {index + 1} solo trace filename is invalid")
        run_directory = row.get("trajectory_run_directory")
        if not isinstance(run_directory, str) or not run_directory:
            raise ReportError(f"Azdaja row {index + 1} trajectory directory is invalid")
        run_path = Path(os.path.abspath(Path(run_directory).expanduser()))
        require_private_directory(run_path, f"Azdaja row {index + 1} trajectory directory")
        if trace.parent != run_path:
            raise ReportError(f"Azdaja row {index + 1} solo trace is outside its trajectory directory")
        if not _is_sha256(metadata.get("sha256")):
            raise ReportError(f"Azdaja row {index + 1} solo trace SHA-256 is invalid")
        _require_equal(
            sha256_path(trace), metadata["sha256"],
            f"Azdaja row {index + 1} solo trace SHA-256",
        )
        if type(metadata.get("bytes")) is not int or metadata["bytes"] < 0:
            raise ReportError(f"Azdaja row {index + 1} solo trace byte count is invalid")
        _require_equal(trace.stat().st_size, metadata["bytes"], f"Azdaja row {index + 1} solo trace bytes")
        exact_preserved = (
            metadata.get("exact_text_preserved") is True
            and metadata.get("source_sha256_before_redaction") == metadata.get("sha256")
        )
        assertion = scan_context_file_against_solo_trace(
            context,
            trace,
            expected_context_sha256=job["context_sha256"],
            exact_transcript_preserved=exact_preserved,
        )
        _require_equal(
            row.get("root_context_leak_assertion"), assertion,
            f"Azdaja row {index + 1} independent root-context assertion",
        )
        if assertion.get("scan_complete") is not True:
            raise ReportError(
                f"Azdaja row {index + 1} lacks mandatory complete exact leak scanning"
            )
        scanned += 1
        if assertion.get("leak_detected") is True:
            leaked += 1
            failure = row.get("failure")
            normalized = normalize_failure_kind(failure if isinstance(failure, dict) else None)
            if (
                row.get("execution_success") is not False
                or score.get("success") is not False
                or normalized != "root_context_leak"
            ):
                raise ReportError(
                    f"Azdaja row {index + 1} contains root_context_leak but was falsely successful"
                )
        elif row.get("execution_success") is True and assertion.get("asserted") is not True:
            raise ReportError(f"successful Azdaja row {index + 1} failed the leak hard gate")
    return {
        "applicable_rows": len(azdaja_indexes),
        "scanned_rows": scanned,
        "leak_rows": leaked,
        "missing_rows": missing,
    }


def percentile(values: Sequence[float], probability: float) -> float | None:
    """R-7/NumPy-style linear percentile for finite values."""
    if not values:
        return None
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


def _rate(values: Iterable[bool]) -> float | None:
    collected = list(values)
    if not collected:
        return None
    return sum(1 for value in collected if value) / len(collected)


def _geometric_ratio(
    records: Iterable[dict[str, Any]], numerator: str, denominator: str
) -> float | None:
    logs: list[float] = []
    for record in records:
        top = record.get(numerator)
        bottom = record.get(denominator)
        if _is_positive_number(top) and _is_positive_number(bottom):
            logs.append(math.log(float(top) / float(bottom)))
    return math.exp(sum(logs) / len(logs)) if logs else None


def _metric_seed(label: str) -> int:
    digest = hashlib.sha256(
        f"oolong-report-bootstrap-v1\0{BOOTSTRAP_SEED}\0{label}".encode("utf-8")
    ).digest()
    return int.from_bytes(digest[:8], "big")


def cluster_bootstrap_ci(
    records: Sequence[dict[str, Any]],
    estimator: Callable[[Sequence[dict[str, Any]]], float | None],
    *,
    label: str,
    iterations: int,
) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[str(record["_cluster"])].append(record)
    keys = sorted(groups)
    estimate = estimator(records)
    if estimate is None or not keys:
        return {
            "estimate": estimate,
            "lower": None,
            "upper": None,
            "valid_resamples": 0,
        }
    rng = random.Random(_metric_seed(label))
    draws: list[float] = []
    for _ in range(iterations):
        sample: list[dict[str, Any]] = []
        for _ in keys:
            sample.extend(groups[keys[rng.randrange(len(keys))]])
        value = estimator(sample)
        if value is not None and math.isfinite(float(value)):
            draws.append(float(value))
    return {
        "estimate": estimate,
        "lower": percentile(draws, 0.025),
        "upper": percentile(draws, 0.975),
        "valid_resamples": len(draws),
    }


def _usage(row: dict[str, Any]) -> tuple[bool, dict[str, int] | None]:
    evidence = row.get("efficiency_evidence")
    usage = row.get("usage")
    if not isinstance(evidence, dict) or evidence.get("valid") is not True:
        return False, None
    if not isinstance(usage, dict):
        return False, None
    result: dict[str, int] = {}
    for field in USAGE_FIELDS:
        value = usage.get(field)
        if type(value) is not int or value < 0:
            return False, None
        result[field] = value
    return True, result


def _root_economy(row: dict[str, Any]) -> tuple[bool, float | None, str]:
    evidence = row.get("root_token_economy")
    if not isinstance(evidence, dict) or evidence.get("missing") is not False:
        return False, None, "missing"
    value = evidence.get("root_input_tokens")
    authority = evidence.get("authority_kind")
    if not _is_nonnegative_number(value) or authority not in {
        "provider_usage", "character_fallback"
    }:
        return False, None, "missing"
    return True, float(value), str(authority)


def _cluster_warnings(
    records: Sequence[dict[str, Any]], repetitions: int, cluster_by: str
) -> list[str]:
    cluster_sizes = Counter(str(record["_cluster"]) for record in records)
    result: list[str] = []
    if repetitions == 1:
        result.append(
            "only one repetition is present; the interval cannot estimate "
            "within-fixture repetition variability"
        )
    if len(cluster_sizes) < SMALL_CLUSTER_COUNT:
        result.append(
            f"only {len(cluster_sizes)} {cluster_by} bootstrap clusters are present "
            f"(<{SMALL_CLUSTER_COUNT}); confidence intervals may be unstable"
        )
    if cluster_sizes and min(cluster_sizes.values()) < 2:
        result.append(
            "one or more bootstrap clusters contain a single scheduled observation"
        )
    return result


def arm_metrics(
    records: list[dict[str, Any]], arm: str, iterations: int
) -> dict[str, Any]:
    scheduled = len(records)
    execution_n = sum(record["execution_success"] for record in records)
    success_n = sum(record["success"] for record in records)
    normalized_execution_failures = Counter()
    raw_execution_failures = Counter()
    incorrect_completed = 0
    for record in records:
        if record["success"]:
            continue
        if record["execution_success"]:
            incorrect_completed += 1
        else:
            failure = record["row"].get("failure")
            raw_kind = failure.get("kind") if isinstance(failure, dict) else None
            raw_execution_failures[
                raw_kind if isinstance(raw_kind, str) and raw_kind else "unknown_execution_failure"
            ] += 1
            normalized = normalize_failure_kind(failure if isinstance(failure, dict) else None)
            normalized_execution_failures[normalized or "other_execution"] += 1
    normalized_outcomes = Counter(normalized_execution_failures)
    raw_outcomes = Counter(raw_execution_failures)
    if incorrect_completed:
        normalized_outcomes["strict_score"] = incorrect_completed
        raw_outcomes["strict_score"] = incorrect_completed
    failure_n = scheduled - success_n
    execution_failure_n = scheduled - execution_n
    if (
        sum(normalized_outcomes.values()) != failure_n
        or sum(raw_outcomes.values()) != failure_n
        or sum(normalized_execution_failures.values()) != execution_failure_n
        or sum(raw_execution_failures.values()) != execution_failure_n
    ):
        raise ReportError("internal failure taxonomy denominator mismatch")

    wall = [
        float(record["latency_seconds"])
        for record in records
        if _is_nonnegative_number(record.get("latency_seconds"))
    ]
    usage_valid = [record for record in records if record["usage_valid"]]
    recorded_totals = {
        field: sum(record["usage"][field] for record in usage_valid)
        for field in USAGE_FIELDS
    }
    missing_usage = scheduled - len(usage_valid)
    unconditional_totals = recorded_totals if missing_usage == 0 else None
    root_valid = [record for record in records if record["root_tokens_valid"]]
    root_values = [float(record["root_input_tokens"]) for record in root_valid]
    missing_root = scheduled - len(root_valid)
    root_authorities = Counter(record["root_token_authority"] for record in root_valid)

    estimators: dict[str, Callable[[Sequence[dict[str, Any]]], float | None]] = {
        "execution_completion_rate": lambda sample: _rate(
            record["execution_success"] for record in sample
        ),
        "exact_success_rate": lambda sample: _rate(record["success"] for record in sample),
        "failure_rate": lambda sample: _rate(not record["success"] for record in sample),
        "completed_accuracy": lambda sample: (
            sum(record["success"] for record in sample if record["execution_success"])
            / sum(record["execution_success"] for record in sample)
            if sum(record["execution_success"] for record in sample) else None
        ),
        "root_input_tokens_mean": lambda sample: (
            sum(float(record["root_input_tokens"]) for record in sample if record["root_tokens_valid"])
            / sum(record["root_tokens_valid"] for record in sample)
            if sum(record["root_tokens_valid"] for record in sample) else None
        ),
        "route_integrity_rate": lambda sample: _rate(
            record["route_asserted"] is True for record in sample
        ),
        "wall_seconds_p50": lambda sample: percentile(
            [float(record["latency_seconds"]) for record in sample
             if _is_nonnegative_number(record.get("latency_seconds"))],
            0.50,
        ),
        "wall_seconds_p95": lambda sample: percentile(
            [float(record["latency_seconds"]) for record in sample
             if _is_nonnegative_number(record.get("latency_seconds"))],
            0.95,
        ),
    }
    ci = {
        name: cluster_bootstrap_ci(
            records, estimator, label=f"arm:{arm}:{name}", iterations=iterations
        )
        for name, estimator in estimators.items()
    }
    route_asserted = sum(record["route_asserted"] is True for record in records)
    route_failed = sum(record["route_asserted"] is False for record in records)
    route_missing = scheduled - route_asserted - route_failed
    completed_accuracy = None if execution_n == 0 else success_n / execution_n
    return {
        "scheduled_n": scheduled,
        "scheduled": {"n": scheduled},
        "execution": {
            "completed_n": execution_n,
            "completion_rate": execution_n / scheduled,
        },
        "execution_rate": {
            "completed_n": execution_n,
            "scheduled_n": scheduled,
            "rate": execution_n / scheduled,
        },
        "completed_accuracy": {
            "correct_n": success_n,
            "completed_n": execution_n,
            "rate": completed_accuracy,
        },
        "fixed_denominator_e2e_accuracy": {
            "correct_n": success_n,
            "scheduled_n": scheduled,
            "rate": success_n / scheduled,
        },
        "exact_success": {"n": success_n, "rate": success_n / scheduled},
        "failure": {
            "n": scheduled - success_n,
            "rate": (scheduled - success_n) / scheduled,
            "incorrect_completed_n": incorrect_completed,
            "execution_failure_n": scheduled - execution_n,
            "taxonomy_scope": "all unsuccessful scheduled attempts",
            "taxonomy_denominator_n": scheduled - success_n,
            "taxonomy": dict(sorted(normalized_outcomes.items())),
            "normalized_taxonomy": dict(sorted(normalized_outcomes.items())),
            "raw_taxonomy": dict(sorted(raw_outcomes.items())),
            "execution_failure_taxonomy_scope": "execution failures only",
            "execution_failure_taxonomy_denominator_n": scheduled - execution_n,
            "execution_failure_taxonomy": dict(
                sorted(normalized_execution_failures.items())
            ),
            "raw_execution_failure_taxonomy": dict(
                sorted(raw_execution_failures.items())
            ),
        },
        "wall_seconds_all_attempts": {
            "observed_n": len(wall),
            "missing_n": scheduled - len(wall),
            "p50": percentile(wall, 0.50),
            "p95": percentile(wall, 0.95),
        },
        "tokens_all_attempts": {
            "valid_usage_n": len(usage_valid),
            "missing_usage_n": missing_usage,
            "recorded_totals": recorded_totals,
            "unconditional_totals": unconditional_totals,
            "recorded_total_tokens": recorded_totals["total_tokens"],
            "unconditional_total_tokens": (
                recorded_totals["total_tokens"] if missing_usage == 0 else None
            ),
        },
        "root_token_economy": {
            "metric": "root input tokens",
            "valid_n": len(root_valid),
            "missing_n": missing_root,
            "authority_counts": dict(sorted(root_authorities.items())),
            "recorded_total_root_input_tokens": sum(root_values),
            "unconditional_total_root_input_tokens": (
                sum(root_values) if missing_root == 0 else None
            ),
            "mean_root_input_tokens": (
                sum(root_values) / len(root_values) if root_values else None
            ),
            "p50_root_input_tokens": percentile(root_values, 0.50),
            "p95_root_input_tokens": percentile(root_values, 0.95),
        },
        "route_integrity": {
            "asserted_n": route_asserted,
            "failed_n": route_failed,
            "missing_n": route_missing,
            "rate": route_asserted / scheduled,
            "all_asserted": route_asserted == scheduled,
        },
        "bootstrap_ci95": ci,
    }


def pair_metrics(
    records: list[dict[str, Any]], arm_a: str, arm_b: str, iterations: int
) -> dict[str, Any]:
    both_correct_n = sum(record["both_correct"] for record in records)
    usage_eligible = [
        record for record in records
        if record["both_correct"] and record["both_valid_usage"]
    ]
    latency_eligible = [
        record for record in usage_eligible
        if _is_positive_number(record.get("latency_a"))
        and _is_positive_number(record.get("latency_b"))
    ]
    token_eligible = [
        record for record in usage_eligible
        if _is_positive_number(record.get("tokens_a"))
        and _is_positive_number(record.get("tokens_b"))
    ]
    root_token_eligible = [
        record for record in records
        if record["both_correct"]
        and record["both_valid_root_tokens"]
        and _is_positive_number(record.get("root_tokens_a"))
        and _is_positive_number(record.get("root_tokens_b"))
    ]
    accuracy_a = _rate(record["success_a"] for record in records)
    accuracy_b = _rate(record["success_b"] for record in records)
    delta = None if accuracy_a is None or accuracy_b is None else accuracy_b - accuracy_a
    latency_ratio = _geometric_ratio(latency_eligible, "latency_b", "latency_a")
    token_ratio = _geometric_ratio(token_eligible, "tokens_b", "tokens_a")
    root_token_ratio = _geometric_ratio(
        root_token_eligible, "root_tokens_b", "root_tokens_a"
    )

    estimators: dict[str, Callable[[Sequence[dict[str, Any]]], float | None]] = {
        "accuracy_delta": lambda sample: (
            (_rate(record["success_b"] for record in sample) or 0.0)
            - (_rate(record["success_a"] for record in sample) or 0.0)
        ) if sample else None,
        "latency_geometric_ratio": lambda sample: _geometric_ratio(
            (
                record for record in sample
                if record["both_correct"]
                and record["both_valid_usage"]
                and _is_positive_number(record.get("latency_a"))
                and _is_positive_number(record.get("latency_b"))
            ),
            "latency_b",
            "latency_a",
        ),
        "token_geometric_ratio": lambda sample: _geometric_ratio(
            (
                record for record in sample
                if record["both_correct"]
                and record["both_valid_usage"]
                and _is_positive_number(record.get("tokens_a"))
                and _is_positive_number(record.get("tokens_b"))
            ),
            "tokens_b",
            "tokens_a",
        ),
        "root_token_geometric_ratio": lambda sample: _geometric_ratio(
            (
                record for record in sample
                if record["both_correct"]
                and record["both_valid_root_tokens"]
                and _is_positive_number(record.get("root_tokens_a"))
                and _is_positive_number(record.get("root_tokens_b"))
            ),
            "root_tokens_b",
            "root_tokens_a",
        ),
    }
    ci = {
        name: cluster_bootstrap_ci(
            records,
            estimator,
            label=f"pair:{arm_a}:{arm_b}:{name}",
            iterations=iterations,
        )
        for name, estimator in estimators.items()
    }
    return {
        "arm_a": arm_a,
        "arm_b": arm_b,
        "ratio_direction": "arm_b / arm_a",
        "accuracy_delta_direction": "arm_b - arm_a",
        "paired_n": len(records),
        "both_correct_n": both_correct_n,
        "accuracy": {
            "arm_a": accuracy_a,
            "arm_b": accuracy_b,
            "delta": delta,
        },
        "both_correct_valid_usage_n": len(usage_eligible),
        "latency_geometric_ratio": {
            "eligible_n": len(latency_eligible),
            "value": latency_ratio,
            "gate": "both exact-correct, both valid usage, and both positive wall times",
        },
        "token_geometric_ratio": {
            "eligible_n": len(token_eligible),
            "value": token_ratio,
            "gate": "both exact-correct, both valid usage, and both positive total_tokens",
        },
        "root_token_geometric_ratio": {
            "eligible_n": len(root_token_eligible),
            "value": root_token_ratio,
            "gate": "both exact-correct, both authoritative/nonmissing root-token values, and both positive",
        },
        "bootstrap_ci95": ci,
    }


def build_report(
    raw_path: str | os.PathLike[str],
    *,
    suite_manifest: str | os.PathLike[str] | None = None,
    bootstrap_iterations: int = BOOTSTRAP_ITERATIONS,
) -> dict[str, Any]:
    """Validate a completed frozen run and return its JSON-serializable report."""
    if type(bootstrap_iterations) is not int or bootstrap_iterations <= 0:
        raise ReportError("bootstrap_iterations must be a positive integer")
    # ``Path.resolve`` would silently follow a symlink before the security
    # check.  ``abspath`` normalizes the spelling while preserving the final
    # directory entry for lstat-based non-symlink validation.
    raw = Path(os.path.abspath(Path(raw_path).expanduser()))
    schedule_path = Path(str(raw) + ".schedule.json")
    scores_path = Path(str(raw) + ".scores.json")
    schedule = load_json_object(schedule_path, "frozen schedule")
    jobs, arms = validate_schedule(schedule)
    if suite_manifest is None:
        raise ReportError(
            "--suite-manifest is required for a campaign-certified OOLONG suite report"
        )
    manifest_path = Path(os.path.abspath(Path(suite_manifest).expanduser()))
    # Bind the unique, exact fixture identity triples before any score or leak work.
    suite_document = validate_suite_manifest(manifest_path, schedule)

    rows = load_raw_rows(raw)
    validate_rows(rows, jobs, schedule)
    claims_root = Path(str(raw) + ".claims")
    claims = validate_claims(claims_root, rows, jobs, schedule)
    scores_document = load_json_object(scores_path, "suite scores")
    scores = validate_scores(
        scores_document, scores_path, raw, rows, jobs, schedule
    )
    validate_independent_scores(manifest_path, suite_document, rows, scores, jobs)
    root_context_gate = independently_validate_root_context_leaks(
        manifest_path, suite_document, rows, scores, jobs
    )
    cluster_for_fixture, cluster_by, warnings = fixture_clusters(
        schedule, suite_document
    )

    repetitions = schedule["configuration"]["repetitions"]
    records_by_arm: dict[str, list[dict[str, Any]]] = {arm: [] for arm in arms}
    keyed: dict[str, dict[tuple[str, int], dict[str, Any]]] = {
        arm: {} for arm in arms
    }
    for row, score, job in zip(rows, scores, jobs):
        evidence_valid, usage = _usage(row)
        root_tokens_valid, root_input_tokens, root_token_authority = _root_economy(row)
        route = row.get("runtime_route_assertion")
        route_asserted = (
            route.get("asserted") if isinstance(route, dict)
            and type(route.get("asserted")) is bool else None
        )
        latency = row.get("latency_seconds")
        record = {
            "row": row,
            "score": score,
            "fixture_id": job["fixture_id"],
            "repetition": job["repetition"],
            "execution_success": row["execution_success"],
            "success": score["success"],
            "latency_seconds": latency,
            "usage_valid": evidence_valid,
            "usage": usage,
            "root_tokens_valid": root_tokens_valid,
            "root_input_tokens": root_input_tokens,
            "root_token_authority": root_token_authority,
            "route_asserted": route_asserted,
            "_cluster": cluster_for_fixture[job["fixture_id"]],
        }
        arm = job["arm"]
        key = (job["fixture_id"], job["repetition"])
        if key in keyed[arm]:
            raise ReportError(f"duplicate paired identity for arm {arm}: {key}")
        records_by_arm[arm].append(record)
        keyed[arm][key] = record

    warnings.extend(
        _cluster_warnings(
            [record for arm in arms for record in records_by_arm[arm]],
            repetitions,
            cluster_by,
        )
    )
    arm_results = {
        arm: arm_metrics(records_by_arm[arm], arm, bootstrap_iterations)
        for arm in arms
    }

    comparisons: dict[str, Any] = {}
    if len(arms) > 1:
        reference_keys = set(keyed[arms[0]])
        for arm in arms[1:]:
            if set(keyed[arm]) != reference_keys:
                raise ReportError(f"paired fixture/repetition identities differ for arm {arm}")
        for arm_a, arm_b in itertools.combinations(arms, 2):
            paired: list[dict[str, Any]] = []
            for fixture_id, repetition in sorted(reference_keys):
                first = keyed[arm_a][(fixture_id, repetition)]
                second = keyed[arm_b][(fixture_id, repetition)]
                paired.append(
                    {
                        "fixture_id": fixture_id,
                        "repetition": repetition,
                        "success_a": first["success"],
                        "success_b": second["success"],
                        "both_correct": first["success"] and second["success"],
                        "both_valid_usage": (
                            first["usage_valid"] and second["usage_valid"]
                        ),
                        "latency_a": first["latency_seconds"],
                        "latency_b": second["latency_seconds"],
                        "tokens_a": (
                            first["usage"]["total_tokens"]
                            if first["usage_valid"] else None
                        ),
                        "tokens_b": (
                            second["usage"]["total_tokens"]
                            if second["usage_valid"] else None
                        ),
                        "both_valid_root_tokens": (
                            first["root_tokens_valid"] and second["root_tokens_valid"]
                        ),
                        "root_tokens_a": first["root_input_tokens"],
                        "root_tokens_b": second["root_input_tokens"],
                        "_cluster": cluster_for_fixture[fixture_id],
                    }
                )
            comparisons[f"{arm_a}__vs__{arm_b}"] = pair_metrics(
                paired, arm_a, arm_b, bootstrap_iterations
            )

    cluster_count = len(set(cluster_for_fixture.values()))
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "oolong_suite_report",
        "integrity": {
            "validated": True,
            "raw_suite_output": str(raw),
            "raw_suite_output_sha256": sha256_path(raw),
            "schedule": str(schedule_path),
            "schedule_file_sha256": sha256_path(schedule_path),
            "schedule_id": schedule["schedule_id"],
            "scores": str(scores_path),
            "scores_file_sha256": sha256_path(scores_path),
            "claims": str(claims),
            "completion_artifacts": len(jobs) * 2,
            "manifest_sha256": schedule["suite"]["manifest_sha256"],
            "scheduled_rows": len(jobs),
            "raw_rows": len(rows),
            "score_rows": len(scores),
            "campaign_profile": {
                "certified": True,
                "fixture_count": CAMPAIGN_FIXTURE_COUNT,
                "arms": list(CAMPAIGN_ARMS),
                "repetitions": CAMPAIGN_REPETITIONS,
                "scheduled_rows": CAMPAIGN_ROW_COUNT,
                "model": CAMPAIGN_MODEL,
                "reasoning": CAMPAIGN_REASONING,
                "seed": CAMPAIGN_SEED,
                "timeout_seconds": CAMPAIGN_TIMEOUT_SECONDS,
            },
            "root_context_leak_hard_gate": root_context_gate,
        },
        "bootstrap": {
            "method": "nonparametric cluster bootstrap with percentile 95% intervals",
            "seed": BOOTSTRAP_SEED,
            "iterations": bootstrap_iterations,
            "cluster_by": cluster_by,
            "cluster_count": cluster_count,
        },
        "frozen_identity_stamp": {
            "candidate": copy.deepcopy(schedule["configuration"].get("candidate")),
            "executables": copy.deepcopy(schedule["configuration"].get("executables", {})),
            "controller": copy.deepcopy(schedule["configuration"]["controller"]),
            "candidate_version_hash_stamp": (
                None
                if schedule["configuration"].get("candidate") is None
                else {
                    "candidate_sha256": schedule["configuration"]["candidate"]["sha256"],
                    "azdaja_sha256": schedule["configuration"]["executables"]["azdaja"]["sha256"],
                    "azdaja_bytes": schedule["configuration"]["executables"]["azdaja"]["bytes"],
                    "azdaja_version": schedule["configuration"]["executables"]["azdaja"]["version"],
                }
            ),
            "validation": (
                "candidate component aggregate recomputed; candidate azdaja hash/bytes "
                "equal executable azdaja; every row executable identity matched"
            ),
        },
        "warnings": list(dict.fromkeys(warnings)),
        "arms": arm_results,
        "comparisons": comparisons,
    }


def _write_private_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_json_bytes(value) + b"\n"
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ReportError(f"refusing to replace existing report output: {path}") from exc
    try:
        if os.name == "posix":
            os.fchmod(fd, 0o600)
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Validate and summarize a completed frozen OOLONG suite"
    )
    result.add_argument("raw_suite_output", help="completed inference JSONL")
    result.add_argument(
        "--suite-manifest",
        required=True,
        help="hash-bound owner-only 26-fixture campaign manifest",
    )
    result.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=BOOTSTRAP_ITERATIONS,
        help=f"cluster-bootstrap resamples (default: {BOOTSTRAP_ITERATIONS})",
    )
    result.add_argument(
        "--output",
        help="create an owner-only JSON report instead of writing JSON to stdout",
    )
    result.add_argument("--pretty", action="store_true", help="pretty-print stdout JSON")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    report = build_report(
        args.raw_suite_output,
        suite_manifest=args.suite_manifest,
        bootstrap_iterations=args.bootstrap_iterations,
    )
    if args.output:
        _write_private_json(Path(args.output).expanduser().resolve(), report)
    else:
        print(
            json.dumps(
                report,
                ensure_ascii=False,
                sort_keys=True,
                indent=2 if args.pretty else None,
                separators=None if args.pretty else (",", ":"),
            )
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReportError as exc:
        print(f"report error: {exc}", file=sys.stderr)
        raise SystemExit(2)
