#!/usr/bin/env python3
"""Fail-closed deferred scoring for the private derived LongBench-v2 cohort.

``lb2-hard-long-63-v1`` is a private, derived 63-question slice.  It is not an
official LongBench-v2 leaderboard submission.  Gold is not resolved, stated,
hashed, or opened until the exact frozen three-arm schedule, all terminal result
rows, and the complete claim/completion set have passed validation.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
import errno
import hashlib
import itertools
import json
import math
import os
import random
import re
import secrets
import stat
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA_VERSION = 1
SUITE_ID = "lb2-hard-long-63-v1"
EXPECTED_SOURCE_COUNT = 503
EXPECTED_FIXTURES = 63
ARMS = ("jcode-native", "jcode-azdaja", "prime-agent")
MODEL = "gpt-5.6-luna"
REASONING = "medium"
AMBIENT_CLOSURE_DISCLOSURE = (
    "The Prime npm package, Node executable, and complete Prime kernel venv are frozen "
    "owner-only snapshots with schedule-bound recursive inventories. Node/Python dynamic "
    "libraries, the OS runtime, OAuth homes, and network service remain ambient and are "
    "not snapshotted."
)
RUN_ID_DOMAIN = b"lb2-hard-long-63-run-v1\0"
DEFAULT_BOOTSTRAP_SEED = 20260813
DEFAULT_BOOTSTRAP_RESAMPLES = 100000
USAGE_FIELDS = (
    "input_tokens", "output_tokens", "cache_read_tokens",
    "cache_write_tokens", "total_tokens",
)
CHOICE_LABELS = ("A", "B", "C", "D")
SOURCE_NAME = "zai-org/LongBench-v2"
SOURCE_URL = "https://huggingface.co/datasets/zai-org/LongBench-v2"
SOURCE_REVISION = "2b48e494f2c7a2f0af81aae178e05c7e1dde0fe9"
OFFICIAL_EVAL_REPO_URL = "https://github.com/THUDM/LongBench"
OFFICIAL_EVAL_COMMIT = "2e00731f8d0bff23dc4325161044d0ed8af94c1e"
OFFICIAL_PRED_PY_SHA256 = "ab63f77866a1c0dc770582bc3fe6b014c3b4be4667399b0ee267075780c6a138"
SOURCE_FILES = {
    "data.json": {
        "sha256": "15d61c22d92c96900b3c4948b6aeea218d3214b676a65df48e7b8555604c7fe2",
        "bytes": 465490535,
        "git_oid": "6cdc8c85cf593dcdc2311cdc0fd59ac34817fd7e",
        "lfs_oid_sha256": "15d61c22d92c96900b3c4948b6aeea218d3214b676a65df48e7b8555604c7fe2",
    },
    "README.md": {
        "sha256": "9fdd1a3ebe86507253c124a18e9f78c898ce6341c12990af17ab868b8f600c35",
        "bytes": 4626,
        "git_oid": "87decc4d91ca85fcf7e593cacfb5b954e36cd0d9",
    },
    ".gitattributes": {
        "sha256": "b3ca89743b410b60a97ba9486e44b205c70f6fb35024ef02198cf766dfdffb18",
        "bytes": 2507,
        "git_oid": "adec96cd34a8bdb402a98453004ec7b60123d9d2",
    },
}
REQUIREMENTS_LOCK_SHA256 = "18b34586a2a60af19f86a8ce844ed3639823610b6291a9f352425d89f277a2eb"
PUBLIC_NOTICE_FILES = {
    "LICENSE.LONGBENCH2": {
        "sha256": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
        "bytes": 11358,
    },
    "THIRD_PARTY_NOTICES.md": {
        "sha256": "9b1e4375b6b2d85d52cf6c7d24a545ada0a92d7cdcee24655e2701aff8279835",
        "bytes": 799,
    },
}
SELECTED_DOMAIN_COUNTS = {
    "Code Repository Understanding": 19,
    "Long In-context Learning": 12,
    "Long Structured Data Understanding": 3,
    "Multi-Document QA": 17,
    "Single-Document QA": 12,
}
SELECTED_SUB_DOMAIN_COUNTS = {
    "Academic": 7, "Code repo QA": 19, "Detective": 3, "Event ordering": 1,
    "Financial": 5, "Governmental": 10, "Literary": 3,
    "New language translation": 8, "Table QA": 3, "User guide QA": 4,
}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
FIXTURE_ID_RE = re.compile(r"lb2-[0-9a-f]{32}\Z")
EXECUTION_FAILURE_KINDS = frozenset({
    "execution", "timeout", "process_exit", "route_assertion", "product_lifecycle",
    "trace_capture", "context_integrity", "skill_integrity", "tool_policy",
    "usage_evidence", "cleanup", "root_context_leak",
})
ROOT_CONTEXT_MATCH_CHARACTERS = 100
ROOT_CONTEXT_ROLLING_HASH = "rabin-karp-u64-unicode-codepoints-plus-exact-verification"
FAILURE_TAXONOMY = (
    "adapter_parser", "transport", "timeout", "depth", "monty_subset_tax",
    "other_execution", "root_context_leak",
)
# A failure can expose more than one textual signal.  Apply this order rather
# than relying on whichever adapter diagnostic happened to be rendered first.
FAILURE_TAXONOMY_PRECEDENCE = (
    "root_context_leak", "timeout", "transport", "adapter_parser", "depth",
    "monty_subset_tax", "other_execution",
)
ROOT_TOKEN_ECONOMY_AUTHORITIES = frozenset({
    "provider_usage_api_root_input_tokens",
    "validated_AZDAJA_MODEL_TRACE_depth_0_input_tokens",
    "exact_control_tool_output_unicode_characters_div_4",
    "validated_AZDAJA_SOLO_TRACE_root_request_unicode_characters_div_4",
    "unavailable",
})
INFERENCE_ROW_KEYS = frozenset({
    "schema_version", "benchmark", "record_type", "schedule_id", "run_id",
    "fixture_id", "payload_sha256", "execution_ordinal", "arm", "repetition",
    "model", "reasoning", "candidate_sha256", "controller_sha256",
    "schedule_seed", "timeout_seconds", "executables", "success", "score",
    "scoring_status", "execution_success", "response", "latency_seconds",
    "started_at_unix_s", "fresh_session", "serial",
    "hidden_context_and_official_question_identical_across_arms", "timed_out",
    "exit_code", "auth_assertion", "runtime_route_assertion",
    "product_lifecycle_assertion", "product_execution_asserted",
    "trace_capture_assertion", "task_context_integrity",
    "tool_access_policy_assertion", "credential_cleanup_assertion",
    "cleanup_errors", "root_usage", "azdaja_model_usage",
    "efficiency_evidence", "usage", "root_token_economy",
    "root_context_leak_assertion", "trajectory_artifacts", "failure",
})


class ScoreError(RuntimeError):
    """An artifact is incomplete, mutable, ambiguous, or identity-mismatched."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def canonical_json_file_bytes(value: Any) -> bytes:
    return canonical_json_bytes(value) + b"\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _rolling_window_hashes(text: str, width: int) -> Iterable[tuple[int, int]]:
    """Yield deterministic unsigned-64-bit hashes of exact Unicode windows."""
    if width <= 0 or len(text) < width:
        return
    mask = (1 << 64) - 1
    base = 1_000_003
    high = pow(base, width - 1, 1 << 64)
    value = 0
    for character in text[:width]:
        value = ((value * base) + ord(character) + 1) & mask
    yield 0, value
    for start in range(1, len(text) - width + 1):
        value = (value - ((ord(text[start - 1]) + 1) * high)) & mask
        value = ((value * base) + ord(text[start + width - 1]) + 1) & mask
        yield start, value


def _exact_unicode_substring_match(
    left: str, right: str, width: int = ROOT_CONTEXT_MATCH_CHARACTERS
) -> str | None:
    """Return only a match hash, using rolling candidates plus exact verification."""
    if len(left) < width or len(right) < width:
        return None
    # Index the smaller transcript side.  Real LongBench contexts can be much
    # larger, so this keeps the per-row auxiliary memory bounded by its trace.
    indexed: dict[int, list[int]] = {}
    for start, value in _rolling_window_hashes(right, width):
        indexed.setdefault(value, []).append(start)
    for left_start, value in _rolling_window_hashes(left, width):
        for right_start in indexed.get(value, ()):
            candidate = left[left_start : left_start + width]
            if candidate == right[right_start : right_start + width]:
                return sha256_bytes(candidate.encode("utf-8"))
    return None


def _parse_exact_root_request(transcript: str) -> tuple[str, int] | None:
    """Parse the exact v32 AZDAJA_SOLO_TRACE root-request frame by char count."""
    quoted = r'"(?:[^"\\]|\\.)*"'
    match = re.match(
        rf'\A\n=== root request begin request_id=(?P<request>{quoted}) '
        rf'model=(?P<model>{quoted}) request_chars=(?P<characters>0|[1-9][0-9]*) ===\n',
        transcript,
    )
    if match is None:
        return None
    try:
        request_id = json.loads(match.group("request"))
        model = json.loads(match.group("model"))
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(request_id, str) or not request_id or model != MODEL:
        return None
    character_count = int(match.group("characters"))
    request_start = match.end()
    request_end = request_start + character_count
    if request_end > len(transcript):
        return None
    request = transcript[request_start:request_end]
    end_frame = f'\n=== root request end request_id={match.group("request")} ===\n'
    if not transcript.startswith(end_frame, request_end):
        return None
    # A counted prefix is not enough: successful product traces must contain
    # subsequent root-turn evidence rather than only a preflight header.
    remainder = transcript[request_end + len(end_frame) :]
    if not re.search(
        rf'(?m)^=== turn 0 request_id={re.escape(match.group("request"))} '
        rf'.* outcome=succeeded .* model={re.escape(match.group("model"))} '
        rf'input=[0-9]+ output=[0-9]+ cache_read=[0-9]+ latency_ms=[0-9]+ ===$',
        remainder,
    ):
        return None
    return request, character_count


def root_context_leak_assertion(
    transcript_bytes: bytes | None, context: str
) -> dict[str, Any]:
    """Hash-only receipt for exact root-trace validation and PUBLIC-context leakage."""
    if not isinstance(context, str):
        raise ScoreError("PUBLIC payload context must be a string for root leak validation")
    context_sha256 = sha256_bytes(context.encode("utf-8"))
    transcript_sha256 = None if transcript_bytes is None else sha256_bytes(transcript_bytes)
    transcript: str | None = None
    if transcript_bytes is not None:
        try:
            transcript = transcript_bytes.decode("utf-8")
        except UnicodeError:
            transcript = None
    parsed = None if transcript is None else _parse_exact_root_request(transcript)
    match_sha256 = (
        None if transcript is None
        else _exact_unicode_substring_match(context, transcript)
    )
    leak_detected = None if transcript is None else match_sha256 is not None
    trace_valid = parsed is not None
    request = None if parsed is None else parsed[0]
    request_characters = None if parsed is None else parsed[1]
    return {
        "asserted": trace_valid and leak_detected is False,
        "trace_present": transcript_bytes is not None,
        "trace_valid": trace_valid,
        "leak_detected": leak_detected,
        "minimum_match_characters": ROOT_CONTEXT_MATCH_CHARACTERS,
        "rolling_hash_algorithm": ROOT_CONTEXT_ROLLING_HASH,
        "context_sha256": context_sha256,
        "context_characters": len(context),
        "transcript_sha256": transcript_sha256,
        "transcript_characters": None if transcript is None else len(transcript),
        "root_request_sha256": (
            None if request is None else sha256_bytes(request.encode("utf-8"))
        ),
        "root_request_characters": request_characters,
        "matched_substring_sha256": match_sha256,
    }


def _usage_root_input(row: dict[str, Any], arm: str) -> tuple[int, str] | None:
    evidence = row.get("efficiency_evidence")
    root = row.get("root_usage")
    if not isinstance(evidence, dict) or evidence.get("valid") is not True:
        return None
    if not isinstance(root, dict) or set(root) != set(USAGE_FIELDS):
        return None
    if any(type(root[field]) is not int or root[field] < 0 for field in USAGE_FIELDS):
        return None
    if root["input_tokens"] <= 0 or root["output_tokens"] <= 0:
        return None
    if arm == "jcode-azdaja":
        trace = row.get("azdaja_model_usage")
        if (
            not isinstance(trace, dict)
            or trace.get("all_rows_valid") is not True
            or not isinstance(trace.get("depth_usage"), dict)
            or trace["depth_usage"].get("0") != root
        ):
            return None
        authority = "validated_AZDAJA_MODEL_TRACE_depth_0_input_tokens"
    else:
        authority = "provider_usage_api_root_input_tokens"
    return root["input_tokens"], authority


def _text_content_characters(value: Any) -> int | None:
    if isinstance(value, str):
        return len(value)
    if not isinstance(value, list):
        return None
    total = 0
    for item in value:
        if not isinstance(item, dict) or item.get("type") != "text" or not isinstance(item.get("text"), str):
            return None
        total += len(item["text"])
    return total


def _control_tool_output_characters(arm: str, stdout: bytes) -> int | None:
    """Count each adapter's canonical final tool-result representation exactly once."""
    try:
        text = stdout.decode("utf-8")
    except UnicodeError:
        return None
    objects: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line:
            continue
        try:
            item = json.loads(
                line, object_pairs_hook=_object_no_duplicates, parse_constant=_reject_constant
            )
        except (json.JSONDecodeError, ValueError):
            return None
        if not isinstance(item, dict):
            return None
        objects.append(item)
    if not objects:
        return None

    if arm == "jcode-native":
        # Jcode also emits tool_start/tool_input/tool_exec updates.  Only the
        # final tool_done.output is the text placed back into root context.
        events = [item for item in objects if item.get("type") == "tool_done"]
        id_field = "id"
    elif arm == "prime-agent":
        # Prime repeats tool results inside message/turn snapshots.  The
        # canonical final representation is tool_execution_end.result.content.
        events = [
            item for item in objects if item.get("type") == "tool_execution_end"
        ]
        id_field = "toolCallId"
    else:
        return None
    # With no canonical terminal event, an arbitrary NDJSON stream cannot
    # prove a zero-character tool result.  Treat it as missing, not zero.
    if not events:
        return None

    invocation_ids: list[str | None] = []
    total = 0
    for event in events:
        invocation_id = event.get(id_field)
        if invocation_id is not None and (
            not isinstance(invocation_id, str) or not invocation_id
        ):
            return None
        invocation_ids.append(invocation_id)
        if arm == "jcode-native":
            # Do not guess from content/result aliases: those are not Jcode's
            # canonical terminal schema.
            if (
                "output" not in event
                or not isinstance(event["output"], str)
                or any(key in event for key in ("content", "result"))
            ):
                return None
            count = len(event["output"])
        else:
            result = event.get("result")
            if not isinstance(result, dict) or "content" not in result:
                return None
            count = _text_content_characters(result["content"])
        if count is None:
            return None
        total += count

    # Real multi-call streams provide stable invocation IDs.  Missing IDs are
    # unambiguous only for a single terminal event; repeated terminal IDs are
    # duplicate representations and must never be summed.
    if len(events) > 1 and any(value is None for value in invocation_ids):
        return None
    present_ids = [value for value in invocation_ids if value is not None]
    if len(present_ids) != len(set(present_ids)):
        return None
    return total


def root_token_economy_receipt(
    row: dict[str, Any], arm: str, stdout: bytes,
    root_trace: bytes | None,
    root_assertion: dict[str, Any] | None,
) -> dict[str, Any]:
    usage = _usage_root_input(row, arm)
    if usage is not None:
        tokens, authority = usage
        return {
            "available": True, "tokens": tokens, "authority": authority,
            "estimated": False, "observed_characters": None,
            "usage_input_tokens": tokens,
        }
    observed: int | None
    authority: str
    if arm == "jcode-azdaja":
        if not isinstance(root_assertion, dict) or root_assertion.get("trace_valid") is not True:
            observed = None
        else:
            observed = root_assertion.get("root_request_characters")
            if type(observed) is not int or observed < 0:
                observed = None
        authority = "validated_AZDAJA_SOLO_TRACE_root_request_unicode_characters_div_4"
    else:
        observed = _control_tool_output_characters(arm, stdout)
        authority = "exact_control_tool_output_unicode_characters_div_4"
    if observed is None:
        return {
            "available": False, "tokens": None, "authority": "unavailable",
            "estimated": None, "observed_characters": None,
            "usage_input_tokens": None,
        }
    return {
        "available": True, "tokens": observed / 4.0, "authority": authority,
        "estimated": True, "observed_characters": observed,
        "usage_input_tokens": None,
    }


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(Path(path).expanduser()))


def _directory_fingerprint(metadata: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        metadata.st_dev, metadata.st_ino, metadata.st_mtime_ns,
        metadata.st_ctime_ns, metadata.st_nlink,
    )


def _open_directory_fd(path: Path, label: str, *, owner_only: bool = True) -> tuple[Path, int]:
    """Traverse every lexical component with openat(O_DIRECTORY|O_NOFOLLOW)."""
    absolute = _absolute_lexical(path)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        current = os.open("/", flags)
    except OSError as exc:
        raise ScoreError(f"cannot open filesystem root for {label}: {exc}") from exc
    try:
        for component in absolute.parts[1:]:
            try:
                following = os.open(component, flags, dir_fd=current)
            except OSError as exc:
                raise ScoreError(
                    f"{label} has an unsafe, missing, or non-directory lexical component "
                    f"{component!r}: {exc}"
                ) from exc
            os.close(current)
            current = following
        metadata = os.fstat(current)
        if not stat.S_ISDIR(metadata.st_mode):
            raise ScoreError(f"{label} must be a directory: {absolute}")
        if os.name == "posix" and owner_only:
            if stat.S_IMODE(metadata.st_mode) & 0o077:
                raise ScoreError(f"{label} must be owner-only: {absolute}")
            if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
                raise ScoreError(f"{label} must be owned by the scoring user: {absolute}")
        return absolute, current
    except Exception:
        os.close(current)
        raise


def _captured_directory_names(fd: int, label: str) -> tuple[list[str], tuple[int, int, int, int, int]]:
    before = os.fstat(fd)
    try:
        names = os.listdir(fd)
    except OSError as exc:
        raise ScoreError(f"cannot enumerate {label}: {exc}") from exc
    after = os.fstat(fd)
    if _directory_fingerprint(before) != _directory_fingerprint(after):
        raise ScoreError(f"{label} changed while its inventory was captured")
    if len(names) != len(set(names)):
        raise ScoreError(f"{label} contains duplicate directory-entry names")
    return names, _directory_fingerprint(after)


def _open_child_directory_fd(parent_fd: int, name: str, label: str) -> int:
    if not name or "/" in name or name in {".", ".."}:
        raise ScoreError(f"{label} name is unsafe")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(name, flags, dir_fd=parent_fd)
    except OSError as exc:
        raise ScoreError(f"{label} is missing, unsafe, or not a directory: {exc}") from exc
    metadata = os.fstat(fd)
    if not stat.S_ISDIR(metadata.st_mode):
        os.close(fd)
        raise ScoreError(f"{label} is not a directory")
    if os.name == "posix":
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            os.close(fd)
            raise ScoreError(f"{label} must be owner-only")
        if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
            os.close(fd)
            raise ScoreError(f"{label} must be owned by the scoring user")
    return fd


def _open_private_regular_fd_at(
    directory_fd: int, relative: str, label: str, *, owner_only: bool = True
) -> int:
    if not relative or "/" in relative or relative in {".", ".."}:
        raise ScoreError(f"{label} requires a single safe relative filename")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(relative, flags, dir_fd=directory_fd)
    except OSError as exc:
        raise ScoreError(f"{label} is missing, unsafe, or unreadable: {relative}: {exc}") from exc
    metadata = os.fstat(fd)
    try:
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ScoreError(f"{label} must be a singly-linked regular file")
        if os.name == "posix" and owner_only:
            if stat.S_IMODE(metadata.st_mode) & 0o077:
                raise ScoreError(f"{label} must be owner-only")
            if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
                raise ScoreError(f"{label} must be owned by the scoring user")
        return fd
    except Exception:
        os.close(fd)
        raise


def _capture_regular_fd(fd: int, label: str) -> bytes:
    before = os.fstat(fd)
    try:
        os.lseek(fd, 0, os.SEEK_SET)
    except OSError as exc:
        raise ScoreError(f"cannot seek held {label}: {exc}") from exc
    chunks: list[bytes] = []
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            break
        chunks.append(chunk)
    after = os.fstat(fd)
    before_identity = (
        before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
        before.st_ctime_ns, before.st_nlink,
    )
    after_identity = (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
        after.st_ctime_ns, after.st_nlink,
    )
    data = b"".join(chunks)
    if before_identity != after_identity or len(data) != before.st_size:
        raise ScoreError(f"held {label} changed during capture")
    return data


def _read_private_regular_at(
    directory_fd: int,
    relative: str,
    label: str,
    *,
    owner_only: bool = True,
) -> tuple[bytes, os.stat_result]:
    if not relative or "/" in relative or relative in {".", ".."}:
        raise ScoreError(f"{label} requires a single safe relative filename")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(relative, flags, dir_fd=directory_fd)
    except OSError as exc:
        raise ScoreError(f"{label} is missing, unsafe, or unreadable: {relative}: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ScoreError(f"{label} must be a regular file: {relative}")
        if before.st_nlink != 1:
            raise ScoreError(f"{label} must have exactly one hard link: {relative}")
        if os.name == "posix" and owner_only:
            if stat.S_IMODE(before.st_mode) & 0o077:
                raise ScoreError(f"{label} must be owner-only: {relative}")
            if hasattr(os, "getuid") and before.st_uid != os.getuid():
                raise ScoreError(f"{label} must be owned by the scoring user: {relative}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(fd)
        fingerprint_before = (
            before.st_dev, before.st_ino, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns, before.st_nlink,
        )
        fingerprint_after = (
            after.st_dev, after.st_ino, after.st_size,
            after.st_mtime_ns, after.st_ctime_ns, after.st_nlink,
        )
        data = b"".join(chunks)
        if fingerprint_before != fingerprint_after or len(data) != before.st_size:
            raise ScoreError(f"{label} changed while its captured bytes were read")
        return data, before
    finally:
        os.close(fd)


def read_private_regular_once(
    path: Path, label: str, *, owner_only: bool = True
) -> tuple[Path, bytes, os.stat_result]:
    absolute = _absolute_lexical(path)
    parent, directory_fd = _open_directory_fd(
        absolute.parent, f"{label} parent", owner_only=owner_only
    )
    try:
        data, metadata = _read_private_regular_at(
            directory_fd, absolute.name, label, owner_only=owner_only
        )
        return parent / absolute.name, data, metadata
    finally:
        os.close(directory_fd)


def sha256_path(path: Path) -> str:
    # Security-sensitive callers use the returned bytes directly rather than
    # hashing and reopening.  This helper is retained for tests and lock pins.
    _, data, _ = read_private_regular_once(path, "hashed file", owner_only=False)
    return sha256_bytes(data)


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
        return json.loads(
            text,
            object_pairs_hook=_object_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ScoreError(f"cannot parse {label}: {exc}") from exc


def _require_equal(actual: Any, expected: Any, label: str) -> None:
    if type(actual) is not type(expected) or actual != expected:
        raise ScoreError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def _nonnegative_number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(float(value)) and value >= 0


def require_private_regular(path: Path, label: str) -> None:
    _, _, _ = read_private_regular_once(path, label)


def require_private_directory(path: Path, label: str) -> None:
    _, fd = _open_directory_fd(path, label)
    os.close(fd)


def load_json_object_captured(
    path: Path, label: str, *, canonical: bool = True
) -> tuple[dict[str, Any], bytes, Path]:
    absolute, data, _ = read_private_regular_once(path, label)
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise ScoreError(f"cannot decode {label} {absolute}: {exc}") from exc
    value = _decode_json(text, label)
    if not isinstance(value, dict):
        raise ScoreError(f"{label} must contain a JSON object")
    if canonical and data != canonical_json_file_bytes(value):
        raise ScoreError(f"{label} is not canonical compact JSON with one final newline")
    return value, data, absolute


def _json_object_from_captured_bytes(data: bytes, label: str, *, canonical: bool = True) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise ScoreError(f"cannot decode {label}: {exc}") from exc
    value = _decode_json(text, label)
    if not isinstance(value, dict):
        raise ScoreError(f"{label} must contain a JSON object")
    if canonical and data != canonical_json_file_bytes(value):
        raise ScoreError(f"{label} is not canonical compact JSON with one final newline")
    return value


def load_json_object(
    path: Path, label: str, *, canonical: bool = True, private: bool = True
) -> dict[str, Any]:
    del private  # every scoring artifact is private and fail-closed
    value, _, _ = load_json_object_captured(path, label, canonical=canonical)
    return value


def manifest_identity_sha256(manifest: dict[str, Any]) -> str:
    """Hash the exact canonical pre-gold manifest, including its final LF."""
    identity = copy.deepcopy(manifest)
    if "gold_sha256" not in identity:
        raise ScoreError("public manifest has no gold_sha256 commitment")
    del identity["gold_sha256"]
    return sha256_bytes(canonical_json_file_bytes(identity))


def _resolve_payload(parent: Path, raw: Any, fixture_id: str) -> Path:
    expected = f"payloads/{fixture_id}.json"
    if raw != expected or not isinstance(raw, str) or Path(raw).is_absolute():
        raise ScoreError(f"fixture {fixture_id} payload path must be exactly {expected!r}")
    unresolved = parent / raw
    if unresolved.is_symlink():
        raise ScoreError(f"fixture {fixture_id} payload must not be a symlink")
    try:
        resolved = unresolved.resolve(strict=True)
        root = parent.resolve(strict=True)
    except OSError as exc:
        raise ScoreError(f"fixture {fixture_id} payload is missing: {exc}") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ScoreError(f"fixture {fixture_id} payload escapes the sealed directory") from exc
    return resolved


def _validate_payload(path: Path, fixture_id: str) -> tuple[dict[str, Any], bytes]:
    payload, captured, _ = load_json_object_captured(path, f"fixture {fixture_id} payload")
    if set(payload) != {"question", "context", "choices"}:
        raise ScoreError(f"fixture {fixture_id} payload has an unexpected object shape")
    if not isinstance(payload["question"], str) or not payload["question"].strip():
        raise ScoreError(f"fixture {fixture_id} question is empty or invalid")
    if not isinstance(payload["context"], str) or not payload["context"]:
        raise ScoreError(f"fixture {fixture_id} context is empty or invalid")
    choices = payload["choices"]
    if not isinstance(choices, dict) or tuple(sorted(choices)) != CHOICE_LABELS:
        raise ScoreError(f"fixture {fixture_id} choices must be exactly A, B, C, D")
    if any(not isinstance(choices[label], str) or not choices[label].strip() for label in CHOICE_LABELS):
        raise ScoreError(f"fixture {fixture_id} has an empty or invalid choice")
    return payload, captured


def load_public_manifest(
    path: Path, *, held_root_fd: int | None = None
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    absolute_manifest = _absolute_lexical(path)
    if absolute_manifest.name != "manifest.json":
        raise ScoreError("public manifest filename must be exactly manifest.json")
    if held_root_fd is None:
        public_root, root_fd = _open_directory_fd(absolute_manifest.parent, "public suite root")
    else:
        public_root = absolute_manifest.parent
        root_fd = os.dup(held_root_fd)
    payload_fd: int | None = None
    try:
        root_names, root_fingerprint = _captured_directory_names(root_fd, "public suite root")
        expected_root_names = {"manifest.json", "payloads", *PUBLIC_NOTICE_FILES}
        if set(root_names) != expected_root_names:
            raise ScoreError(
                f"public suite root inventory drift: expected {sorted(expected_root_names)}, "
                f"got {sorted(root_names)}"
            )
        manifest_bytes, _ = _read_private_regular_at(
            root_fd, "manifest.json", "public suite manifest"
        )
        document = _json_object_from_captured_bytes(manifest_bytes, "public suite manifest")
        payload_fd = _open_child_directory_fd(root_fd, "payloads", "public payload directory")
        payload_names, payload_fingerprint = _captured_directory_names(
            payload_fd, "public payload directory"
        )
        if set(document) != {
            "schema_version", "record_type", "suite_id", "source", "configuration",
            "provenance_commitments", "fixtures", "gold_sha256",
        }:
            raise ScoreError("public manifest has an unexpected object shape")
        _require_equal(document["schema_version"], SCHEMA_VERSION, "manifest schema_version")
        _require_equal(document["record_type"], "lb2_hard_long_public_manifest", "manifest record_type")
        _require_equal(document["suite_id"], SUITE_ID, "manifest suite_id")
        _require_equal(
            document["source"],
            {"name": SOURCE_NAME, "url": SOURCE_URL, "revision": SOURCE_REVISION},
            "manifest embedded pinned source identity",
        )
        _require_equal(
            document["configuration"],
            {
                "difficulty": "hard", "length": "long",
                "source_row_count": EXPECTED_SOURCE_COUNT,
                "fixture_count": EXPECTED_FIXTURES,
                "payload_schema": ["question", "context", "choices"],
                "choice_labels": list(CHOICE_LABELS),
                "domain_counts": SELECTED_DOMAIN_COUNTS,
                "sub_domain_counts": SELECTED_SUB_DOMAIN_COUNTS,
            },
            "manifest derived-cohort configuration",
        )
        _require_equal(
            document["provenance_commitments"],
            {
                "data_json_sha256": SOURCE_FILES["data.json"]["sha256"],
                "readme_sha256": SOURCE_FILES["README.md"]["sha256"],
                "gitattributes_sha256": SOURCE_FILES[".gitattributes"]["sha256"],
                "requirements_lock_sha256": REQUIREMENTS_LOCK_SHA256,
                "public_notice_files": {
                    name: metadata["sha256"] for name, metadata in PUBLIC_NOTICE_FILES.items()
                },
            },
            "manifest embedded provenance commitments",
        )
        if not _is_sha256(document["gold_sha256"]):
            raise ScoreError("manifest gold_sha256 must be lowercase SHA-256")
        entries = document["fixtures"]
        if not isinstance(entries, list) or len(entries) != EXPECTED_FIXTURES:
            raise ScoreError(f"manifest must contain exactly {EXPECTED_FIXTURES} fixtures")

        by_id: dict[str, dict[str, Any]] = {}
        payload_hashes: set[str] = set()
        for index, item in enumerate(entries, 1):
            if not isinstance(item, dict) or set(item) != {
                "id", "domain", "sub_domain", "payload", "payload_sha256", "payload_bytes"
            }:
                raise ScoreError(f"manifest fixture {index} has an unexpected object shape")
            fixture_id = item.get("id")
            if not isinstance(fixture_id, str) or FIXTURE_ID_RE.fullmatch(fixture_id) is None:
                raise ScoreError(f"manifest fixture {index} id is invalid")
            if fixture_id in by_id:
                raise ScoreError(f"duplicate manifest fixture id: {fixture_id}")
            for field in ("domain", "sub_domain"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    raise ScoreError(f"fixture {fixture_id} {field} is empty or invalid")
            expected_relative = f"payloads/{fixture_id}.json"
            _require_equal(item.get("payload"), expected_relative, f"fixture {fixture_id} payload path")
            if not _is_sha256(item.get("payload_sha256")):
                raise ScoreError(f"fixture {fixture_id} payload_sha256 is invalid")
            if not _positive_int(item.get("payload_bytes")):
                raise ScoreError(f"fixture {fixture_id} payload_bytes must be positive")
            payload_bytes, _ = _read_private_regular_at(
                payload_fd, f"{fixture_id}.json", f"fixture {fixture_id} payload"
            )
            payload = _json_object_from_captured_bytes(
                payload_bytes, f"fixture {fixture_id} payload"
            )
            if set(payload) != {"question", "context", "choices"}:
                raise ScoreError(f"fixture {fixture_id} payload has an unexpected object shape")
            if not isinstance(payload["question"], str) or not payload["question"].strip():
                raise ScoreError(f"fixture {fixture_id} question is empty or invalid")
            if not isinstance(payload["context"], str) or not payload["context"]:
                raise ScoreError(f"fixture {fixture_id} context is empty or invalid")
            choices = payload["choices"]
            if not isinstance(choices, dict) or tuple(sorted(choices)) != CHOICE_LABELS:
                raise ScoreError(f"fixture {fixture_id} choices must be exactly A, B, C, D")
            if any(not isinstance(choices[label], str) or not choices[label].strip() for label in CHOICE_LABELS):
                raise ScoreError(f"fixture {fixture_id} has an empty or invalid choice")
            _require_equal(len(payload_bytes), item["payload_bytes"], f"fixture {fixture_id} payload bytes")
            _require_equal(sha256_bytes(payload_bytes), item["payload_sha256"], f"fixture {fixture_id} payload SHA-256")
            if item["payload_sha256"] in payload_hashes:
                raise ScoreError(f"fixture {fixture_id} duplicates a payload identity")
            payload_hashes.add(item["payload_sha256"])
            normalized = dict(item)
            normalized["_payload_path"] = public_root / expected_relative
            normalized["_payload_bytes_captured"] = payload_bytes
            by_id[fixture_id] = normalized
        _require_equal(
            dict(Counter(item["domain"] for item in entries)),
            SELECTED_DOMAIN_COUNTS,
            "public selected-domain counts",
        )
        _require_equal(
            dict(Counter(item["sub_domain"] for item in entries)),
            SELECTED_SUB_DOMAIN_COUNTS,
            "public selected-sub-domain counts",
        )
        expected_payload_names = {f"{fixture_id}.json" for fixture_id in by_id}
        if set(payload_names) != expected_payload_names:
            raise ScoreError(
                "public payload directory is not the exact 63-file set "
                f"(missing={sorted(expected_payload_names - set(payload_names))[:3]}, "
                f"extra={sorted(set(payload_names) - expected_payload_names)[:3]})"
            )
        for name, expected in PUBLIC_NOTICE_FILES.items():
            notice_bytes, _ = _read_private_regular_at(root_fd, name, f"public notice {name}")
            _require_equal(len(notice_bytes), expected["bytes"], f"public notice {name} bytes")
            _require_equal(sha256_bytes(notice_bytes), expected["sha256"], f"public notice {name} SHA-256")
        # Held directory descriptors make ancestor renames irrelevant.  Reject
        # any in-directory mutation across the complete capture window.
        if _directory_fingerprint(os.fstat(payload_fd)) != payload_fingerprint:
            raise ScoreError("public payload directory changed during capture")
        if _directory_fingerprint(os.fstat(root_fd)) != root_fingerprint:
            raise ScoreError("public suite root changed during capture")
        return document, by_id
    finally:
        if payload_fd is not None:
            os.close(payload_fd)
        os.close(root_fd)


def _fixture_schedule_identity(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": fixture["id"],
        "payload_sha256": fixture["payload_sha256"],
        "domain": fixture["domain"],
        "sub_domain": fixture["sub_domain"],
    }


def _validate_component_identity(
    value: Any, label: str, *, version: bool = False, path: bool = False
) -> None:
    expected = {"sha256", "bytes"}
    if version:
        expected |= {"version", "version_command"}
    if path:
        expected |= {"path"}
    if not isinstance(value, dict) or set(value) != expected:
        raise ScoreError(f"{label} has an unexpected component identity shape")
    if not _is_sha256(value.get("sha256")) or not _positive_int(value.get("bytes")):
        raise ScoreError(f"{label} hash/byte identity is invalid")
    if version and (not isinstance(value.get("version"), str) or not value["version"].strip()):
        raise ScoreError(f"{label} version identity is invalid")
    if path and (not isinstance(value.get("path"), str) or not Path(value["path"]).is_absolute()):
        raise ScoreError(f"{label} path identity is invalid")
    if version:
        _require_equal(
            value.get("version_command"), [value["path"], "--version"],
            f"{label} version command",
        )


def _validate_candidate_identity(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != {"sha256", "components"}:
        raise ScoreError("schedule treatment candidate identity has an unexpected shape")
    components = value["components"]
    if not isinstance(components, dict) or set(components) != {"SKILL.md", "azdaja", "config.toml"}:
        raise ScoreError("schedule treatment candidate must bind exactly SKILL.md, azdaja, config.toml")
    for name, component in components.items():
        _validate_component_identity(component, f"schedule candidate component {name}")
    _require_equal(
        value["sha256"], sha256_bytes(canonical_json_bytes(components)),
        "schedule candidate aggregate identity",
    )



def _validate_runtime_closure(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != {
        "adapter", "validator", "prime_package", "node", "kernel_python",
        "kernel_launcher", "kernel_environment", "runtime_python",
        "ambient_closure_disclosure",
    }:
        raise ScoreError("schedule runtime closure has an unexpected shape")
    for name in ("adapter", "validator"):
        _validate_component_identity(value[name], f"schedule runtime {name}", path=True)
    for name in ("node", "kernel_python"):
        _validate_component_identity(
            value[name], f"schedule runtime {name}", version=True, path=True
        )
    launcher = value["kernel_launcher"]
    if not isinstance(launcher, dict) or set(launcher) != {"path", "target", "resolved_path"} or not all(isinstance(launcher[key], str) for key in launcher) or not Path(launcher["path"]).is_absolute() or not Path(launcher["resolved_path"]).is_absolute() or os.path.isabs(launcher["target"]):
        raise ScoreError("schedule kernel launcher identity is invalid")
    prime = value["prime_package"]
    if not isinstance(prime, dict) or set(prime) != {
        "snapshot_root", "inventory_sha256", "entry_count", "cli_relative"
    }:
        raise ScoreError("schedule Prime package runtime identity shape is invalid")
    if (
        not isinstance(prime["snapshot_root"], str)
        or not Path(prime["snapshot_root"]).is_absolute()
        or not _is_sha256(prime["inventory_sha256"])
        or not _positive_int(prime["entry_count"])
        or not isinstance(prime["cli_relative"], str)
        or not prime["cli_relative"]
        or Path(prime["cli_relative"]).is_absolute()
        or ".." in Path(prime["cli_relative"]).parts
    ):
        raise ScoreError("schedule Prime package runtime identity is invalid")
    kernel = value["kernel_environment"]
    if not isinstance(kernel, dict) or set(kernel) != {
        "root", "inventory_sha256", "entry_count"
    }:
        raise ScoreError("schedule kernel environment runtime identity shape is invalid")
    if (
        not isinstance(kernel["root"], str)
        or not Path(kernel["root"]).is_absolute()
        or not _is_sha256(kernel["inventory_sha256"])
        or not _positive_int(kernel["entry_count"])
    ):
        raise ScoreError("schedule kernel environment runtime identity is invalid")
    runtime_python = value["runtime_python"]
    if not isinstance(runtime_python, dict) or set(runtime_python) != {
        "snapshot_root", "inventory_sha256", "entry_count"
    } or not isinstance(runtime_python["snapshot_root"], str) or not Path(runtime_python["snapshot_root"]).is_absolute() or not _is_sha256(runtime_python["inventory_sha256"]) or not _positive_int(runtime_python["entry_count"]):
        raise ScoreError("schedule runtime Python identity is invalid")
    _require_equal(
        value["ambient_closure_disclosure"],
        AMBIENT_CLOSURE_DISCLOSURE,
        "schedule ambient runtime closure disclosure",
    )


def validate_schedule(
    schedule: dict[str, Any],
    manifest_path: Path,
    fixtures: dict[str, dict[str, Any]],
    *,
    manifest_sha256: str | None = None,
) -> tuple[list[dict[str, Any]], tuple[str, ...]]:
    if set(schedule) != {
        "schema_version", "record_type", "suite", "configuration", "jobs", "schedule_id"
    }:
        raise ScoreError("frozen schedule has an unexpected object shape")
    _require_equal(schedule["schema_version"], SCHEMA_VERSION, "schedule schema_version")
    _require_equal(schedule["record_type"], "lb2_frozen_schedule", "schedule record_type")
    schedule_id = schedule["schedule_id"]
    if not _is_sha256(schedule_id):
        raise ScoreError("schedule_id must be lowercase SHA-256")

    identity = copy.deepcopy(schedule)
    identity.pop("schedule_id")
    identity_jobs = identity.get("jobs")
    if not isinstance(identity_jobs, list):
        raise ScoreError("schedule jobs must be a list")
    for job in identity_jobs:
        if not isinstance(job, dict):
            raise ScoreError("schedule job must be an object")
        job.pop("run_id", None)
    _require_equal(
        schedule_id,
        sha256_bytes(canonical_json_bytes(identity)),
        "frozen schedule SHA-256 identity",
    )

    suite = schedule["suite"]
    configuration = schedule["configuration"]
    if not isinstance(suite, dict) or not isinstance(configuration, dict):
        raise ScoreError("schedule suite/configuration must be objects")
    if set(suite) != {"suite_id", "manifest_sha256", "fixtures"}:
        raise ScoreError("schedule suite has an unexpected object shape")
    _require_equal(suite["suite_id"], SUITE_ID, "schedule suite_id")
    if manifest_sha256 is None:
        _, captured_manifest, _ = load_json_object_captured(
            manifest_path, "public suite manifest schedule binding"
        )
        manifest_sha256 = sha256_bytes(captured_manifest)
    _require_equal(suite["manifest_sha256"], manifest_sha256, "schedule manifest SHA-256")
    scheduled_fixtures = suite["fixtures"]
    if not isinstance(scheduled_fixtures, list) or len(scheduled_fixtures) != EXPECTED_FIXTURES:
        raise ScoreError("schedule suite fixture identity list is incomplete")
    manifest_order = list(fixtures)
    scheduled_order: list[str] = []
    seen_scheduled: set[str] = set()
    for index, item in enumerate(scheduled_fixtures, 1):
        if not isinstance(item, dict) or set(item) != {
            "fixture_id", "payload_sha256", "domain", "sub_domain"
        }:
            raise ScoreError(f"schedule fixture {index} has an unexpected shape")
        fixture_id = item.get("fixture_id")
        if fixture_id not in fixtures or fixture_id in seen_scheduled:
            raise ScoreError(f"schedule fixture is duplicate or unknown: {fixture_id!r}")
        _require_equal(item, _fixture_schedule_identity(fixtures[fixture_id]), f"schedule fixture {fixture_id}")
        seen_scheduled.add(fixture_id)
        scheduled_order.append(fixture_id)
    _require_equal(scheduled_order, manifest_order, "schedule fixture order")

    required_config = {
        "model", "reasoning", "arms", "repetitions", "seed", "timeout_seconds",
        "candidate", "controller", "executables", "runtime_closure",
    }
    if set(configuration) != required_config:
        raise ScoreError("schedule configuration has an unexpected object shape")
    _require_equal(configuration["model"], MODEL, "schedule exact model")
    _require_equal(configuration["reasoning"], REASONING, "schedule reasoning")
    arms_raw = configuration["arms"]
    _require_equal(arms_raw, list(ARMS), "schedule exact three-arm order")
    arms = tuple(arms_raw)
    _require_equal(configuration["repetitions"], 1, "schedule repetitions")
    if type(configuration["seed"]) is not int:
        raise ScoreError("schedule seed must be an integer")
    if not _nonnegative_number(configuration["timeout_seconds"]) or configuration["timeout_seconds"] <= 0:
        raise ScoreError("schedule timeout_seconds must be positive and finite")
    candidate = configuration["candidate"]
    _validate_candidate_identity(candidate)
    controller = configuration["controller"]
    _validate_component_identity(controller, "schedule controller", path=True)
    executables = configuration["executables"]
    if not isinstance(executables, dict) or set(executables) != {"jcode", "azdaja", "prime-agent"}:
        raise ScoreError("schedule must bind exactly jcode, azdaja, and prime-agent executables")
    for name, executable in executables.items():
        _validate_component_identity(
            executable, f"schedule executable {name}", version=True, path=True
        )
    candidate_binary = candidate["components"]["azdaja"]
    executable_binary = executables["azdaja"]
    _require_equal(
        candidate_binary["sha256"], executable_binary["sha256"],
        "candidate azdaja component/executable SHA-256 binding",
    )
    _require_equal(
        candidate_binary["bytes"], executable_binary["bytes"],
        "candidate azdaja component/executable byte-length binding",
    )
    _validate_runtime_closure(configuration["runtime_closure"])

    jobs = schedule["jobs"]
    expected_jobs = EXPECTED_FIXTURES * len(ARMS)
    if not isinstance(jobs, list) or len(jobs) != expected_jobs:
        raise ScoreError(f"schedule must contain exactly {expected_jobs} jobs")
    expected_grid = {(fixture_id, arm, 1) for fixture_id in fixtures for arm in ARMS}
    observed_grid: set[tuple[str, str, int]] = set()
    run_ids: set[str] = set()
    permutations: Counter[tuple[str, ...]] = Counter()
    rng = random.Random(configuration["seed"])
    expected_fixture_order = list(manifest_order)
    rng.shuffle(expected_fixture_order)
    expected_sequence: list[tuple[str, str]] = []
    for fixture_id in expected_fixture_order:
        arm_order = list(ARMS)
        rng.shuffle(arm_order)
        permutations[tuple(arm_order)] += 1
        expected_sequence.extend((fixture_id, arm) for arm in arm_order)
    actual_sequence = [(job.get("fixture_id"), job.get("arm")) for job in jobs]
    _require_equal(
        actual_sequence, expected_sequence,
        "schedule exact seeded fixture and per-fixture arm order",
    )

    expected_job_shape = {
        "ordinal", "fixture_id", "payload_sha256", "domain", "sub_domain",
        "repetition", "arm", "run_id",
    }
    for index, job in enumerate(jobs, 1):
        if not isinstance(job, dict) or set(job) != expected_job_shape:
            raise ScoreError(f"schedule job {index} has an unexpected object shape")
        _require_equal(job["ordinal"], index, f"schedule job {index} ordinal")
        fixture_id = job["fixture_id"]
        cell = (fixture_id, job["arm"], job["repetition"])
        if cell not in expected_grid or cell in observed_grid:
            raise ScoreError(f"schedule job {index} is duplicate or outside the exact grid")
        fixture = fixtures[fixture_id]
        for key in ("payload_sha256", "domain", "sub_domain"):
            _require_equal(job[key], fixture[key], f"schedule job {index} {key}")
        run_id = job["run_id"]
        if not _is_sha256(run_id) or run_id in run_ids:
            raise ScoreError(f"schedule job {index} run_id is invalid or duplicate")
        base_job = dict(job)
        del base_job["run_id"]
        expected_run_id = sha256_bytes(
            RUN_ID_DOMAIN + schedule_id.encode("ascii") + canonical_json_bytes(base_job)
        )
        _require_equal(run_id, expected_run_id, f"schedule job {index} run_id")
        observed_grid.add(cell)
        run_ids.add(run_id)
    if observed_grid != expected_grid:
        raise ScoreError("schedule is not the exact complete 63 x 3 grid")
    if sum(permutations.values()) != EXPECTED_FIXTURES:
        raise ScoreError("schedule arm-order receipts are incomplete")
    return jobs, arms


def _load_run_rows_captured(captured_runs: bytes) -> list[dict[str, Any]]:
    lines = captured_runs.splitlines(keepends=True)
    if not lines:
        raise ScoreError("frozen inference JSONL is empty")
    rows: list[dict[str, Any]] = []
    for line_number, data in enumerate(lines, 1):
        if not data.endswith(b"\n") or not data[:-1].strip():
            raise ScoreError(f"inference row {line_number} is blank or lacks its final newline")
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


def load_run_rows(path: Path) -> list[dict[str, Any]]:
    _, captured_runs, _ = read_private_regular_once(path, "frozen inference JSONL")
    return _load_run_rows_captured(captured_runs)


def _validate_route(route: Any, arm: str, index: int) -> bool:
    if not isinstance(route, dict) or type(route.get("asserted")) is not bool:
        raise ScoreError(f"inference row {index} runtime route assertion is malformed")
    if not route["asserted"]:
        return False
    if arm == "jcode-native":
        if set(route) != {"asserted", "provider", "model", "expected_provider", "expected_model"}:
            raise ScoreError(f"inference row {index} native route receipt shape is invalid")
        _require_equal(route["provider"], "OpenAI", f"inference row {index} route provider")
        _require_equal(route["model"], MODEL, f"inference row {index} route model")
        _require_equal(route["expected_provider"], "OpenAI", f"inference row {index} expected route provider")
    elif arm == "jcode-azdaja":
        if set(route) != {
            "asserted", "routes", "expected_provider", "expected_model",
            "transport_error_rows", "authority",
        }:
            raise ScoreError(f"inference row {index} treatment route receipt shape is invalid")
        routes = route["routes"]
        if not isinstance(routes, list) or not routes:
            raise ScoreError(f"inference row {index} treatment route has no evidence")
        for item in routes:
            if not isinstance(item, dict) or set(item) != {"provider", "model"}:
                raise ScoreError(f"inference row {index} treatment route item shape is invalid")
            if not isinstance(item["provider"], str) or not item["provider"].lower().startswith("openai"):
                raise ScoreError(f"inference row {index} treatment route provider is invalid")
            _require_equal(item["model"], MODEL, f"inference row {index} treatment route model")
        _require_equal(route["expected_provider"], "OpenAI subscription OAuth", f"inference row {index} expected route provider")
        _require_equal(route["transport_error_rows"], 0, f"inference row {index} route transport errors")
        if not isinstance(route["authority"], str) or "AZDAJA_MODEL_TRACE" not in route["authority"]:
            raise ScoreError(f"inference row {index} treatment route authority is invalid")
    else:
        if set(route) != {"asserted", "routes", "expected_provider", "expected_model", "expected_api"}:
            raise ScoreError(f"inference row {index} Prime route receipt shape is invalid")
        routes = route["routes"]
        if not isinstance(routes, list) or not routes:
            raise ScoreError(f"inference row {index} Prime route has no evidence")
        for item in routes:
            _require_equal(
                item,
                {"provider": "openai-codex", "model": MODEL, "api": "openai-codex-responses"},
                f"inference row {index} Prime route item",
            )
        _require_equal(route["expected_provider"], "openai-codex", f"inference row {index} expected route provider")
        _require_equal(route["expected_api"], "openai-codex-responses", f"inference row {index} expected route API")
    _require_equal(route["expected_model"], MODEL, f"inference row {index} expected route model")
    return True


def _validate_lifecycle(lifecycle: Any, row: dict[str, Any], arm: str, index: int) -> bool:
    if not isinstance(lifecycle, dict) or type(lifecycle.get("asserted")) is not bool:
        raise ScoreError(f"inference row {index} product lifecycle assertion is malformed")
    asserted = lifecycle["asserted"]
    if arm == "jcode-azdaja":
        if set(lifecycle) != {
            "asserted", "process_result_asserted", "exit_code", "timed_out",
            "nonempty_result", "valid_depth_zero_model_calls", "requirement",
        }:
            raise ScoreError(f"inference row {index} treatment lifecycle shape is invalid")
        if asserted:
            for key, expected in (
                ("process_result_asserted", True), ("timed_out", False),
                ("nonempty_result", True), ("exit_code", 0),
            ):
                _require_equal(lifecycle[key], expected, f"inference row {index} lifecycle {key}")
            if not _positive_int(lifecycle["valid_depth_zero_model_calls"]):
                raise ScoreError(f"inference row {index} asserted lifecycle has no valid depth-0 call")
            if not isinstance(lifecycle["requirement"], str) or "depth-0" not in lifecycle["requirement"]:
                raise ScoreError(f"inference row {index} lifecycle requirement is invalid")
    else:
        if set(lifecycle) != {"asserted", "requirement"}:
            raise ScoreError(f"inference row {index} control lifecycle shape is invalid")
        _require_equal(asserted, True, f"inference row {index} control lifecycle")
        if not isinstance(lifecycle["requirement"], str) or "not applicable" not in lifecycle["requirement"]:
            raise ScoreError(f"inference row {index} control lifecycle requirement is invalid")
    if type(row.get("product_execution_asserted")) is not bool:
        raise ScoreError(f"inference row {index} product_execution_asserted is malformed")
    _require_equal(row["product_execution_asserted"], asserted, f"inference row {index} lifecycle summary")
    return asserted


def _validate_root_context_receipt(
    value: Any, arm: str, index: int, *, execution_success: bool
) -> None:
    if arm != "jcode-azdaja":
        _require_equal(value, None, f"inference row {index} unexpected root-context receipt")
        return
    expected = {
        "asserted", "trace_present", "trace_valid", "leak_detected",
        "minimum_match_characters", "rolling_hash_algorithm", "context_sha256",
        "context_characters", "transcript_sha256", "transcript_characters",
        "root_request_sha256", "root_request_characters", "matched_substring_sha256",
    }
    if not isinstance(value, dict) or set(value) != expected:
        raise ScoreError(f"inference row {index} root-context receipt shape is invalid")
    for key in ("asserted", "trace_present", "trace_valid"):
        if type(value[key]) is not bool:
            raise ScoreError(f"inference row {index} root-context {key} is invalid")
    if value["leak_detected"] is not None and type(value["leak_detected"]) is not bool:
        raise ScoreError(f"inference row {index} root-context leak flag is invalid")
    _require_equal(
        value["minimum_match_characters"], ROOT_CONTEXT_MATCH_CHARACTERS,
        f"inference row {index} root-context match threshold",
    )
    _require_equal(
        value["rolling_hash_algorithm"], ROOT_CONTEXT_ROLLING_HASH,
        f"inference row {index} root-context rolling-hash authority",
    )
    if not _is_sha256(value["context_sha256"]) or type(value["context_characters"]) is not int or value["context_characters"] <= 0:
        raise ScoreError(f"inference row {index} root-context PUBLIC identity is invalid")
    for field in ("transcript_sha256", "root_request_sha256", "matched_substring_sha256"):
        if value[field] is not None and not _is_sha256(value[field]):
            raise ScoreError(f"inference row {index} root-context {field} is invalid")
    for field in ("transcript_characters", "root_request_characters"):
        if value[field] is not None and (type(value[field]) is not int or value[field] < 0):
            raise ScoreError(f"inference row {index} root-context {field} is invalid")
    expected_asserted = value["trace_valid"] and value["leak_detected"] is False
    _require_equal(value["asserted"], expected_asserted, f"inference row {index} root-context assertion summary")
    if value["trace_present"] != (value["transcript_sha256"] is not None):
        raise ScoreError(f"inference row {index} root-context trace presence/hash disagree")
    if value["trace_valid"] != (value["root_request_sha256"] is not None):
        raise ScoreError(f"inference row {index} root-context request validity/hash disagree")
    if (value["leak_detected"] is True) != (value["matched_substring_sha256"] is not None):
        raise ScoreError(f"inference row {index} root-context leak/hash disagree")
    if execution_success and value["asserted"] is not True:
        raise ScoreError(f"inference row {index} reports success without a valid leak-free exact root transcript")


def _validate_root_token_economy(value: Any, arm: str, index: int) -> None:
    expected = {
        "available", "tokens", "authority", "estimated", "observed_characters",
        "usage_input_tokens",
    }
    if not isinstance(value, dict) or set(value) != expected:
        raise ScoreError(f"inference row {index} root-token-economy receipt shape is invalid")
    if type(value["available"]) is not bool or value["authority"] not in ROOT_TOKEN_ECONOMY_AUTHORITIES:
        raise ScoreError(f"inference row {index} root-token-economy authority is invalid")
    if not value["available"]:
        _require_equal(
            value,
            {
                "available": False, "tokens": None, "authority": "unavailable",
                "estimated": None, "observed_characters": None,
                "usage_input_tokens": None,
            },
            f"inference row {index} unavailable root-token economy",
        )
        return
    tokens = value["tokens"]
    if not _nonnegative_number(tokens):
        raise ScoreError(f"inference row {index} root-token economy tokens are invalid")
    if type(value["estimated"]) is not bool:
        raise ScoreError(f"inference row {index} root-token economy estimate flag is invalid")
    if value["estimated"]:
        if (
            value["authority"] not in {
                "exact_control_tool_output_unicode_characters_div_4",
                "validated_AZDAJA_SOLO_TRACE_root_request_unicode_characters_div_4",
            }
            or type(value["observed_characters"]) is not int
            or value["observed_characters"] < 0
            or tokens != value["observed_characters"] / 4.0
            or value["usage_input_tokens"] is not None
        ):
            raise ScoreError(f"inference row {index} estimated root-token economy is inconsistent")
        expected_authority = (
            "validated_AZDAJA_SOLO_TRACE_root_request_unicode_characters_div_4"
            if arm == "jcode-azdaja"
            else "exact_control_tool_output_unicode_characters_div_4"
        )
        _require_equal(value["authority"], expected_authority, f"inference row {index} root-token fallback authority")
    else:
        expected_authority = (
            "validated_AZDAJA_MODEL_TRACE_depth_0_input_tokens"
            if arm == "jcode-azdaja" else "provider_usage_api_root_input_tokens"
        )
        _require_equal(value["authority"], expected_authority, f"inference row {index} root-token usage authority")
        if (
            value["observed_characters"] is not None
            or type(value["usage_input_tokens"]) is not int
            or value["usage_input_tokens"] <= 0
            or tokens != value["usage_input_tokens"]
        ):
            raise ScoreError(f"inference row {index} usage-authoritative root-token economy is inconsistent")


def _validate_usage(row: dict[str, Any], arm: str, index: int) -> tuple[bool, dict[str, int] | None]:
    evidence = row.get("efficiency_evidence")
    usage = row.get("usage")
    expected_evidence_keys = (
        {"valid", "missing_fields", "reasons", "required_authority", "calls_included", "depth_counts"}
        if arm == "jcode-azdaja"
        else {"valid", "missing_fields", "reasons", "required_authority"}
    )
    if (
        not isinstance(evidence, dict)
        or set(evidence) != expected_evidence_keys
        or type(evidence.get("valid")) is not bool
        or not isinstance(evidence.get("missing_fields"), list)
        or not isinstance(evidence.get("reasons"), list)
        or not isinstance(evidence.get("required_authority"), str)
    ):
        raise ScoreError(f"inference row {index} efficiency evidence is malformed")
    if not isinstance(usage, dict) or set(usage) != set(USAGE_FIELDS):
        raise ScoreError(f"inference row {index} usage has an unexpected object shape")
    valid = evidence["valid"]
    if not valid:
        if not evidence["reasons"]:
            raise ScoreError(f"inference row {index} invalid usage evidence has no reason")
        if any(value is not None and (type(value) is not int or value < 0) for value in usage.values()):
            raise ScoreError(f"inference row {index} invalid usage contains malformed counters")
        return False, None
    _require_equal(evidence["missing_fields"], [], f"inference row {index} usage missing fields")
    _require_equal(evidence["reasons"], [], f"inference row {index} usage evidence reasons")
    counters: dict[str, int] = {}
    for field in USAGE_FIELDS:
        value = usage[field]
        if type(value) is not int or value < 0:
            raise ScoreError(f"inference row {index} valid usage has invalid {field}")
        counters[field] = value
    expected_total = (
        sum(counters[field] for field in USAGE_FIELDS[:-1])
        if arm == "prime-agent"
        else counters["input_tokens"] + counters["output_tokens"]
    )
    _require_equal(counters["total_tokens"], expected_total, f"inference row {index} usage arithmetic")
    if counters["input_tokens"] <= 0 or counters["output_tokens"] <= 0 or counters["total_tokens"] <= 0:
        raise ScoreError(f"inference row {index} valid usage must contain a nonzero model call")

    root_usage = row.get("root_usage")
    if not isinstance(root_usage, dict) or set(root_usage) != set(USAGE_FIELDS):
        raise ScoreError(f"inference row {index} root usage receipt is malformed")
    if any(type(root_usage[field]) is not int or root_usage[field] < 0 for field in USAGE_FIELDS):
        raise ScoreError(f"inference row {index} root usage counters are invalid")
    trace_usage = row.get("azdaja_model_usage")
    if arm != "jcode-azdaja":
        _require_equal(trace_usage, None, f"inference row {index} unexpected treatment model trace usage")
        _require_equal(root_usage, counters, f"inference row {index} root/effective usage binding")
    else:
        if evidence["calls_included"] <= 0 or not isinstance(evidence["depth_counts"], dict):
            raise ScoreError(f"inference row {index} treatment usage evidence lacks model calls")
        if not isinstance(trace_usage, dict):
            raise ScoreError(f"inference row {index} treatment model-trace usage is missing")
        required_trace = {
            "calls", *USAGE_FIELDS, "routes", "depth_counts", "depth_usage", "all_rows_valid"
        }
        if set(trace_usage) != required_trace:
            raise ScoreError(f"inference row {index} treatment model-trace usage shape is invalid")
        _require_equal(trace_usage["all_rows_valid"], True, f"inference row {index} treatment trace validity")
        _require_equal(trace_usage["calls"], evidence["calls_included"], f"inference row {index} treatment trace call count")
        _require_equal(trace_usage["depth_counts"], evidence["depth_counts"], f"inference row {index} treatment trace depths")
        if not _positive_int(trace_usage["depth_counts"].get("0")):
            raise ScoreError(f"inference row {index} treatment trace lacks depth-0 model evidence")
        for field in USAGE_FIELDS:
            _require_equal(trace_usage[field], counters[field], f"inference row {index} treatment trace {field}")
        depth_counts = trace_usage["depth_counts"]
        if (
            any(not isinstance(key, str) or not key.isdigit() for key in depth_counts)
            or any(not _positive_int(value) for value in depth_counts.values())
            or sum(depth_counts.values()) != trace_usage["calls"]
        ):
            raise ScoreError(f"inference row {index} treatment depth/call counts do not reconcile")
        depth_usage = trace_usage["depth_usage"]
        if not isinstance(depth_usage, dict) or set(depth_usage) != set(depth_counts):
            raise ScoreError(f"inference row {index} treatment depth usage keys do not reconcile")
        aggregate = {field: 0 for field in USAGE_FIELDS}
        for depth, bucket in depth_usage.items():
            if not isinstance(bucket, dict) or set(bucket) != set(USAGE_FIELDS):
                raise ScoreError(f"inference row {index} treatment depth {depth} usage shape is invalid")
            if any(type(bucket[field]) is not int or bucket[field] < 0 for field in USAGE_FIELDS):
                raise ScoreError(f"inference row {index} treatment depth {depth} counters are invalid")
            if (
                bucket["input_tokens"] <= 0
                or bucket["output_tokens"] <= 0
                or bucket["total_tokens"] <= 0
            ):
                raise ScoreError(
                    f"inference row {index} treatment depth {depth} lacks positive token usage"
                )
            _require_equal(
                bucket["total_tokens"], bucket["input_tokens"] + bucket["output_tokens"],
                f"inference row {index} treatment depth {depth} arithmetic",
            )
            for field in USAGE_FIELDS:
                aggregate[field] += bucket[field]
        _require_equal(aggregate, counters, f"inference row {index} treatment depth aggregate")
        _require_equal(root_usage, depth_usage["0"], f"inference row {index} treatment root/depth-0 usage")
        runtime_route = row["runtime_route_assertion"]
        expected_routes = sorted(
            {f"{item['provider']}/{item['model']}" for item in runtime_route["routes"]}
        )
        _require_equal(trace_usage["routes"], expected_routes, f"inference row {index} treatment route/trace binding")
        _require_equal(
            row["product_lifecycle_assertion"]["valid_depth_zero_model_calls"],
            depth_counts["0"],
            f"inference row {index} treatment lifecycle/depth-0 call count",
        )
    return True, counters


def _validate_auth_assertion(auth: Any, arm: str, index: int) -> None:
    common = {
        "asserted", "method", "issuer", "audience", "plan_present_and_paid",
        "account_id_present", "expires_at_ms", "credential_source", "provider_cli",
        "model_cli",
    }
    arm_specific = (
        {"cli_auth_status_asserted_oauth", "cli_auth_status"}
        if arm.startswith("jcode") else {"credential_type_asserted"}
    )
    if not isinstance(auth, dict) or set(auth) != common | arm_specific:
        raise ScoreError(f"inference row {index} auth assertion has an unexpected shape")
    expected_provider = "openai" if arm.startswith("jcode") else "openai-codex"
    expected_source = (
        "~/.jcode/openai-auth.json"
        if arm.startswith("jcode") else "~/.prime/agent/auth.json:openai-codex"
    )
    for key, expected in (
        ("asserted", True), ("method", "subscription-oauth"),
        ("issuer", "https://auth.openai.com"),
        ("audience", "https://api.openai.com/v1"),
        ("plan_present_and_paid", True), ("account_id_present", True),
        ("credential_source", expected_source), ("provider_cli", expected_provider),
        ("model_cli", MODEL),
    ):
        _require_equal(auth.get(key), expected, f"inference row {index} auth {key}")
    if not _positive_int(auth.get("expires_at_ms")):
        raise ScoreError(f"inference row {index} auth expiration receipt is invalid")
    if arm.startswith("jcode"):
        _require_equal(auth["cli_auth_status_asserted_oauth"], True, f"inference row {index} CLI OAuth assertion")
        if not isinstance(auth["cli_auth_status"], str) or not auth["cli_auth_status"].strip():
            raise ScoreError(f"inference row {index} CLI auth status is empty")
    else:
        _require_equal(auth["credential_type_asserted"], "oauth", f"inference row {index} credential type")


def _validate_success_evidence(row: dict[str, Any], job: dict[str, Any], schedule: dict[str, Any], index: int) -> None:
    arm = job["arm"]
    _require_equal(row.get("timed_out"), False, f"inference row {index} timed_out")
    _require_equal(row.get("exit_code"), 0, f"inference row {index} exit_code")
    if not row["response"].strip():
        raise ScoreError(f"inference row {index} successful response is empty")
    started = row.get("started_at_unix_s")
    if not _nonnegative_number(started) or float(started) <= 0:
        raise ScoreError(f"inference row {index} start-time receipt is invalid")
    for key in ("fresh_session", "serial", "hidden_context_and_official_question_identical_across_arms"):
        _require_equal(row.get(key), True, f"inference row {index} {key}")
    timeout = float(schedule["configuration"]["timeout_seconds"])
    latency = float(row["latency_seconds"])
    if latency <= 0 or latency > timeout * 1.10 + 1.0:
        raise ScoreError(f"inference row {index} successful latency is zero or exceeds its timeout envelope")
    _validate_auth_assertion(row.get("auth_assertion"), arm, index)
    if row["auth_assertion"]["expires_at_ms"] <= int(float(started) * 1000) + 60_000:
        raise ScoreError(f"inference row {index} OAuth receipt expires too close to run start")

    trace = row.get("trace_capture_assertion")
    required = ["azdaja_model_trace", "azdaja_solo_trace"] if arm == "jcode-azdaja" else []
    if not isinstance(trace, dict) or set(trace) != {"asserted", "required", "captured", "missing"}:
        raise ScoreError(f"inference row {index} trace-capture assertion has an unexpected shape")
    _require_equal(trace["asserted"], True, f"inference row {index} trace capture")
    _require_equal(trace["required"], required, f"inference row {index} required traces")
    _require_equal(trace["captured"], required, f"inference row {index} captured traces")
    _require_equal(trace["missing"], [], f"inference row {index} missing traces")

    context = row.get("task_context_integrity")
    required_context = {
        "asserted_before", "asserted_after", "expected_sha256",
        "source_sha256_before", "source_sha256_after_copy", "staged_sha256_before",
        "staged_sha256_after", "source_sha256_after", "staged_mode_before",
        "staged_mode_after", "task_directory_single_file_before",
        "task_directory_single_file_after", "random_context_filename", "errors",
    }
    if not isinstance(context, dict) or set(context) != required_context:
        raise ScoreError(f"inference row {index} context-integrity receipt has an unexpected shape")
    for key in (
        "asserted_before", "asserted_after", "task_directory_single_file_before",
        "task_directory_single_file_after", "random_context_filename",
    ):
        _require_equal(context[key], True, f"inference row {index} context {key}")
    expected_context_hash = context["expected_sha256"]
    if not _is_sha256(expected_context_hash):
        raise ScoreError(f"inference row {index} expected staged-context hash is invalid")
    _require_equal(
        expected_context_hash, job["payload_sha256"],
        f"inference row {index} staged-context/public-payload binding",
    )
    for key in (
        "source_sha256_before", "source_sha256_after_copy", "staged_sha256_before",
        "staged_sha256_after", "source_sha256_after",
    ):
        _require_equal(context[key], expected_context_hash, f"inference row {index} context {key}")
    _require_equal(context["staged_mode_before"], "0444", f"inference row {index} staged mode before")
    _require_equal(context["staged_mode_after"], "0444", f"inference row {index} staged mode after")
    _require_equal(context["errors"], [], f"inference row {index} context errors")

    tool = row.get("tool_access_policy_assertion")
    if not isinstance(tool, dict) or set(tool) != {
        "asserted", "events_scanned", "violations", "policy", "enforcement",
        "containment_asserted",
    }:
        raise ScoreError(f"inference row {index} tool-policy receipt has an unexpected shape")
    _require_equal(tool["asserted"], True, f"inference row {index} tool policy")
    _require_equal(tool["violations"], [], f"inference row {index} tool-policy violations")
    _require_equal(tool["containment_asserted"], False, f"inference row {index} tool containment claim")
    if type(tool["events_scanned"]) is not int or tool["events_scanned"] < 0:
        raise ScoreError(f"inference row {index} tool event count is invalid")
    if not isinstance(tool["policy"], str) or "no network" not in tool["policy"]:
        raise ScoreError(f"inference row {index} tool policy text is invalid")
    if not isinstance(tool["enforcement"], str) or "post-hoc" not in tool["enforcement"]:
        raise ScoreError(f"inference row {index} tool enforcement disclosure is invalid")

    cleanup = row.get("credential_cleanup_assertion")
    if not isinstance(cleanup, dict) or set(cleanup) != {
        "asserted", "credential_homes_deleted", "retained_entries", "retention_allowlist"
    }:
        raise ScoreError(f"inference row {index} cleanup receipt has an unexpected shape")
    _require_equal(cleanup["asserted"], True, f"inference row {index} cleanup assertion")
    _require_equal(cleanup["credential_homes_deleted"], True, f"inference row {index} credential cleanup")
    if (
        not isinstance(cleanup["retained_entries"], list)
        or not isinstance(cleanup["retention_allowlist"], list)
        or sorted(cleanup["retained_entries"]) != cleanup["retained_entries"]
        or sorted(cleanup["retention_allowlist"]) != cleanup["retention_allowlist"]
        or not set(cleanup["retained_entries"]).issubset(cleanup["retention_allowlist"])
    ):
        raise ScoreError(f"inference row {index} cleanup allowlist receipt is invalid")
    _require_equal(row.get("cleanup_errors"), [], f"inference row {index} cleanup errors")



def _validate_trajectory_artifacts(
    value: Any, arm: str, index: int, *, execution_success: bool
) -> None:
    base = {"stdout", "stderr"}
    treatment = {"azdaja_model_trace", "azdaja_solo_trace"}
    allowed = base | (treatment if arm == "jcode-azdaja" else set())
    if not isinstance(value, dict) or not base.issubset(value) or not set(value).issubset(allowed):
        raise ScoreError(f"inference row {index} trajectory artifact set is invalid")
    if execution_success and set(value) != allowed:
        raise ScoreError(f"inference row {index} successful trajectory artifacts are incomplete")
    expected_basenames = {
        "stdout": "stdout.ndjson",
        "stderr": "stderr.log",
        "azdaja_model_trace": "azdaja-model-usage.jsonl",
        "azdaja_solo_trace": "azdaja-solo-trace.log",
    }
    paths: set[str] = set()
    for name, receipt in value.items():
        expected_receipt = {
            "path", "sha256", "bytes", "mode", "contains_private_raw_trajectory",
            "credential_redacted", "sensitivity",
        }
        if name in treatment:
            expected_receipt |= {"source_sha256_before_redaction", "exact_text_preserved"}
        if not isinstance(receipt, dict) or set(receipt) != expected_receipt:
            raise ScoreError(f"inference row {index} trajectory receipt {name} shape is invalid")
        raw_path = receipt["path"]
        if (
            not isinstance(raw_path, str)
            or not Path(raw_path).is_absolute()
            or Path(raw_path).name != expected_basenames[name]
            or raw_path in paths
            or not _is_sha256(receipt["sha256"])
            or type(receipt["bytes"]) is not int
            or receipt["bytes"] < 0
            or receipt["mode"] != "0600"
            or receipt["contains_private_raw_trajectory"] is not False
            or receipt["credential_redacted"] is not True
            or not isinstance(receipt["sensitivity"], str)
            or not receipt["sensitivity"].strip()
        ):
            raise ScoreError(f"inference row {index} trajectory receipt {name} is invalid")
        if name in treatment and (
            receipt["exact_text_preserved"] is not True
            or not _is_sha256(receipt["source_sha256_before_redaction"])
            or receipt["source_sha256_before_redaction"] != receipt["sha256"]
        ):
            raise ScoreError(f"inference row {index} trajectory receipt {name} did not preserve exact trace text")
        paths.add(raw_path)



def _trajectory_response(arm: str, stdout: bytes, index: int) -> str:
    try:
        text = stdout.decode("utf-8")
    except UnicodeError as exc:
        raise ScoreError(f"inference row {index} stdout trajectory is not UTF-8") from exc
    objects: list[dict[str, Any]] = []
    for line in text.splitlines():
        try:
            value = json.loads(line, object_pairs_hook=_object_no_duplicates, parse_constant=_reject_constant)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(value, dict):
            objects.append(value)
    if arm == "prime-agent":
        final: str | None = None
        for obj in objects:
            message = obj.get("message")
            if obj.get("type") != "message_end" or not isinstance(message, dict) or message.get("role") != "assistant":
                continue
            content = message.get("content")
            if isinstance(content, list):
                final = "".join(
                    part.get("text", "") for part in content
                    if isinstance(part, dict) and part.get("type") == "text"
                )
        return final if final is not None else ""
    assembled = ""
    completed: str | None = None
    for obj in objects:
        typ = obj.get("type") or obj.get("ev")
        if typ in {"text_delta", "assistant_text_delta"} and isinstance(obj.get("text"), str):
            assembled += obj["text"]
        for key in ("response", "output_text", "text", "content"):
            value = obj.get(key)
            if typ in {"result", "message_end", "assistant", "final", "done"} and isinstance(value, str):
                completed = value
    return completed if completed is not None else (assembled if assembled else text)


def validate_artifact_rows(
    artifacts_root: Path,
    rows: Sequence[dict[str, Any]],
    jobs: Sequence[dict[str, Any]],
    fixtures: dict[str, dict[str, Any]],
) -> None:
    absolute_root, root_fd = _open_directory_fd(artifacts_root, "trajectory artifacts root")
    try:
        names, fingerprint = _captured_directory_names(root_fd, "trajectory artifacts root")
        expected_dirs = {
            f"r001-{job['ordinal']:03d}-{job['arm']}" for job in jobs
        }
        if set(names) != expected_dirs:
            raise ScoreError("trajectory artifacts root is not the exact scheduled run-directory set")
        directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        basename = {
            "stdout": "stdout.ndjson", "stderr": "stderr.log",
            "azdaja_model_trace": "azdaja-model-usage.jsonl",
            "azdaja_solo_trace": "azdaja-solo-trace.log",
        }
        for index, (row, job) in enumerate(zip(rows, jobs), 1):
            run_name = f"r001-{job['ordinal']:03d}-{job['arm']}"
            fd = os.open(run_name, directory_flags, dir_fd=root_fd)
            try:
                metadata = os.fstat(fd)
                if stat.S_IMODE(metadata.st_mode) != 0o700 or (hasattr(os, "getuid") and metadata.st_uid != os.getuid()):
                    raise ScoreError(f"trajectory run directory {index} is not owner-only")
                run_names, _ = _captured_directory_names(fd, f"trajectory run directory {index}")
                receipts = row["trajectory_artifacts"]
                expected_names = {basename[key] for key in receipts}
                if set(run_names) != expected_names:
                    raise ScoreError(f"trajectory run directory {index} inventory differs from row")
                retained = row.get("credential_cleanup_assertion")
                if not isinstance(retained, dict) or retained.get("retained_entries") != sorted(expected_names) or retained.get("retention_allowlist") != sorted(expected_names):
                    raise ScoreError(f"inference row {index} cleanup/artifact inventories disagree")
                stdout: bytes | None = None
                root_trace: bytes | None = None
                for key, receipt in receipts.items():
                    data, _ = _read_private_regular_at(fd, basename[key], f"trajectory {index} {key}")
                    expected_path = absolute_root / run_name / basename[key]
                    if receipt["path"] != str(expected_path) or receipt["sha256"] != sha256_bytes(data) or receipt["bytes"] != len(data):
                        raise ScoreError(f"trajectory artifact {index} {key} bytes/path differ from receipt")
                    if key == "stdout":
                        stdout = data
                    elif key == "azdaja_solo_trace":
                        root_trace = data
                assert stdout is not None
                if _trajectory_response(job["arm"], stdout, index) != row["response"]:
                    raise ScoreError(f"inference row {index} response differs from retained stdout")
                root_assertion = None
                if job["arm"] == "jcode-azdaja":
                    fixture = fixtures[job["fixture_id"]]
                    payload = _json_object_from_captured_bytes(
                        fixture["_payload_bytes_captured"],
                        f"fixture {job['fixture_id']} payload root-context validation",
                    )
                    root_assertion = root_context_leak_assertion(
                        root_trace, payload["context"]
                    )
                _require_equal(
                    row["root_context_leak_assertion"], root_assertion,
                    f"inference row {index} exact root-context artifact receipt",
                )
                expected_economy = root_token_economy_receipt(
                    row, job["arm"], stdout, root_trace, root_assertion
                )
                _require_equal(
                    row["root_token_economy"], expected_economy,
                    f"inference row {index} root-token-economy artifact receipt",
                )
            finally:
                os.close(fd)
        if _directory_fingerprint(os.fstat(root_fd)) != fingerprint:
            raise ScoreError("trajectory artifacts root changed during validation")
    finally:
        os.close(root_fd)


def validate_run_rows(
    rows: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
    schedule: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
) -> None:
    if len(rows) != len(jobs):
        raise ScoreError(
            f"frozen inference is not terminal-complete (scheduled={len(jobs)}, rows={len(rows)})"
        )
    configuration = schedule["configuration"]
    candidate = configuration["candidate"]
    candidate_sha = None if candidate is None else candidate["sha256"]
    seen: set[str] = set()
    for index, (row, job) in enumerate(zip(rows, jobs), 1):
        if set(row) != INFERENCE_ROW_KEYS:
            missing = sorted(INFERENCE_ROW_KEYS - set(row))
            extra = sorted(set(row) - INFERENCE_ROW_KEYS)
            raise ScoreError(
                f"inference row {index} top-level schema mismatch "
                f"(missing={missing}, extra={extra})"
            )
        relevant_executable_names = (
            ("jcode", "azdaja") if job["arm"] == "jcode-azdaja"
            else (("jcode",) if job["arm"] == "jcode-native" else ("prime-agent",))
        )
        expected_executables = {
            name: configuration["executables"][name] for name in relevant_executable_names
        }
        expected = {
            "schema_version": SCHEMA_VERSION,
            "benchmark": SUITE_ID,
            "record_type": "inference",
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "fixture_id": job["fixture_id"],
            "payload_sha256": job["payload_sha256"],
            "execution_ordinal": job["ordinal"],
            "arm": job["arm"],
            "repetition": 1,
            "model": MODEL,
            "reasoning": REASONING,
            "candidate_sha256": candidate_sha,
            "controller_sha256": configuration["controller"]["sha256"],
            "schedule_seed": configuration["seed"],
            "timeout_seconds": configuration["timeout_seconds"],
            "executables": expected_executables,
            "success": None,
            "score": None,
            "scoring_status": "deferred",
        }
        for key, expected_value in expected.items():
            _require_equal(row.get(key), expected_value, f"inference row {index} {key}")
        if row["run_id"] in seen:
            raise ScoreError(f"duplicate inference run_id at row {index}")
        seen.add(row["run_id"])
        if row["fixture_id"] not in fixtures:
            raise ScoreError(f"inference row {index} has an unknown fixture id")
        if type(row.get("execution_success")) is not bool:
            raise ScoreError(f"inference row {index} lacks a terminal execution_success bool")
        if not isinstance(row.get("response"), str):
            raise ScoreError(f"inference row {index} response must be a string")
        if not _nonnegative_number(row.get("latency_seconds")):
            raise ScoreError(f"inference row {index} latency_seconds is invalid")
        if type(row.get("timed_out")) is not bool:
            raise ScoreError(f"inference row {index} timed_out is invalid")
        if row.get("exit_code") is not None and type(row.get("exit_code")) is not int:
            raise ScoreError(f"inference row {index} exit_code is invalid")
        _validate_trajectory_artifacts(
            row.get("trajectory_artifacts"), job["arm"], index,
            execution_success=row["execution_success"],
        )
        route_ok = _validate_route(row.get("runtime_route_assertion"), job["arm"], index)
        lifecycle_ok = _validate_lifecycle(row.get("product_lifecycle_assertion"), row, job["arm"], index)
        usage_ok, _ = _validate_usage(row, job["arm"], index)
        _validate_root_context_receipt(
            row.get("root_context_leak_assertion"), job["arm"], index,
            execution_success=row["execution_success"],
        )
        _validate_root_token_economy(row.get("root_token_economy"), job["arm"], index)
        if row["execution_success"] and not (route_ok and lifecycle_ok and usage_ok):
            raise ScoreError(f"inference row {index} reports execution success without valid route/lifecycle/usage")
        failure = row.get("failure")
        if row["execution_success"]:
            if failure is not None:
                raise ScoreError(f"inference row {index} succeeded but has a failure object")
            _validate_success_evidence(row, job, schedule, index)
        else:
            if not isinstance(failure, dict) or set(failure) != {"kind", "message", "stderr"}:
                raise ScoreError(f"inference row {index} execution failure has an unexpected shape")
            kind = failure.get("kind")
            if kind not in EXECUTION_FAILURE_KINDS:
                raise ScoreError(f"inference row {index} execution failure kind is not in the frozen taxonomy")
            if any(not isinstance(failure[field], str) for field in ("message", "stderr")):
                raise ScoreError(f"inference row {index} execution failure text fields are invalid")
            if kind == "timeout" and row["timed_out"] is not True:
                raise ScoreError(f"inference row {index} timeout failure lacks timed_out=true")
            if kind == "process_exit" and (type(row["exit_code"]) is not int or row["exit_code"] == 0):
                raise ScoreError(f"inference row {index} process_exit failure lacks nonzero exit code")
            if kind == "route_assertion" and route_ok:
                raise ScoreError(f"inference row {index} route failure contradicts asserted route evidence")
            if kind == "product_lifecycle" and lifecycle_ok:
                raise ScoreError(f"inference row {index} lifecycle failure contradicts asserted lifecycle evidence")
            if kind == "usage_evidence" and usage_ok:
                raise ScoreError(f"inference row {index} usage failure contradicts valid usage evidence")
            root_receipt = row["root_context_leak_assertion"]
            if job["arm"] == "jcode-azdaja" and root_receipt["leak_detected"] is True:
                _require_equal(
                    kind, "root_context_leak",
                    f"inference row {index} leaked root-context terminal failure kind",
                )
            if kind == "root_context_leak" and (
                job["arm"] != "jcode-azdaja" or root_receipt["leak_detected"] is not True
            ):
                raise ScoreError(f"inference row {index} root-context-leak kind lacks exact leak evidence")


def validate_claims(
    claims_root: Path,
    rows: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
    schedule: dict[str, Any],
    *,
    held_root_fd: int | None = None,
) -> Path:
    if held_root_fd is None:
        absolute_root, root_fd = _open_directory_fd(claims_root, "frozen claims root")
    else:
        absolute_root = _absolute_lexical(claims_root)
        root_fd = os.dup(held_root_fd)
    claims_fd: int | None = None
    try:
        root_names, root_fingerprint = _captured_directory_names(root_fd, "frozen claims root")
        if root_names != [schedule["schedule_id"]]:
            raise ScoreError("frozen claims root must contain only the active schedule directory")
        claims_fd = _open_child_directory_fd(
            root_fd, schedule["schedule_id"], "frozen schedule claims directory"
        )
        names, claims_fingerprint = _captured_directory_names(
            claims_fd, "frozen schedule claims directory"
        )
        expected_names = {
            name for job in jobs
            for name in (job["run_id"] + ".json", job["run_id"] + ".done.json")
        }
        if set(names) != expected_names:
            raise ScoreError(
                "claims are not the exact terminal 2N set "
                f"(missing={sorted(expected_names - set(names))[:3]}, "
                f"extra={sorted(set(names) - expected_names)[:3]})"
            )
        for index, (row, job) in enumerate(zip(rows, jobs), 1):
            claim_bytes, _ = _read_private_regular_at(
                claims_fd, job["run_id"] + ".json", f"run claim {index}"
            )
            claim = _json_object_from_captured_bytes(claim_bytes, f"run claim {index}")
            if set(claim) != {"schedule_id", "run_id", "ordinal", "pid"}:
                raise ScoreError(f"run claim {index} has unexpected fields")
            for key, value in {
                "schedule_id": schedule["schedule_id"],
                "run_id": job["run_id"],
                "ordinal": job["ordinal"],
            }.items():
                _require_equal(claim.get(key), value, f"run claim {index} {key}")
            if not _positive_int(claim.get("pid")):
                raise ScoreError(f"run claim {index} pid is invalid")
            done_bytes, _ = _read_private_regular_at(
                claims_fd, job["run_id"] + ".done.json", f"run completion {index}"
            )
            done = _json_object_from_captured_bytes(done_bytes, f"run completion {index}")
            _require_equal(
                done,
                {
                    "schedule_id": schedule["schedule_id"],
                    "run_id": job["run_id"],
                    "row_sha256": sha256_bytes(canonical_json_bytes(row)),
                },
                f"run completion {index} receipt",
            )
        if _directory_fingerprint(os.fstat(claims_fd)) != claims_fingerprint:
            raise ScoreError("frozen schedule claims directory changed during capture")
        if _directory_fingerprint(os.fstat(root_fd)) != root_fingerprint:
            raise ScoreError("frozen claims root changed during capture")
        return absolute_root / schedule["schedule_id"]
    finally:
        if claims_fd is not None:
            os.close(claims_fd)
        os.close(root_fd)


def validate_frozen_runs(
    manifest_path: Path,
    manifest: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    runs_path: Path,
    schedule_path: Path | None = None,
    claims_root: Path | None = None,
    artifacts_root: Path | None = None,
    *,
    captured_schedule: bytes | None = None,
    captured_runs: bytes | None = None,
    held_claims_root_fd: int | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], tuple[str, ...]]:
    """Validate terminal completion.  This function cannot receive or read gold."""
    schedule_path = schedule_path or Path(str(runs_path) + ".schedule.json")
    claims_root = claims_root or Path(str(runs_path) + ".claims")
    artifacts_root = artifacts_root or Path(str(runs_path) + ".artifacts")
    if captured_schedule is None:
        schedule, _, _ = load_json_object_captured(schedule_path, "frozen schedule")
    else:
        schedule = _json_object_from_captured_bytes(captured_schedule, "frozen schedule")
    jobs, arms = validate_schedule(
        schedule, manifest_path, fixtures,
        manifest_sha256=sha256_bytes(canonical_json_file_bytes(manifest)),
    )
    rows = (
        load_run_rows(runs_path)
        if captured_runs is None else _load_run_rows_captured(captured_runs)
    )
    validate_run_rows(rows, jobs, schedule, fixtures)
    validate_claims(
        claims_root, rows, jobs, schedule, held_root_fd=held_claims_root_fd
    )
    validate_artifact_rows(artifacts_root, rows, jobs, fixtures)
    return schedule, jobs, rows, arms


def load_gold(
    path: Path,
    manifest_path: Path,
    manifest: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    *,
    held_root_fd: int | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Open private gold.  Call only after :func:`validate_frozen_runs`."""
    absolute_gold = _absolute_lexical(path)
    if absolute_gold.name != "gold.json":
        raise ScoreError("owner-only gold filename must be exactly gold.json")
    if held_root_fd is None:
        _, gold_root_fd = _open_directory_fd(absolute_gold.parent, "owner-only gold root")
    else:
        gold_root_fd = os.dup(held_root_fd)
    try:
        gold_names, gold_root_fingerprint = _captured_directory_names(
            gold_root_fd, "owner-only gold root"
        )
        if gold_names != ["gold.json"]:
            raise ScoreError("owner-only gold root must contain exactly gold.json")
        gold_bytes, _ = _read_private_regular_at(
            gold_root_fd, "gold.json", "owner-only gold"
        )
        if _directory_fingerprint(os.fstat(gold_root_fd)) != gold_root_fingerprint:
            raise ScoreError("owner-only gold root changed during capture")
    finally:
        os.close(gold_root_fd)
    document = _json_object_from_captured_bytes(gold_bytes, "owner-only gold")
    _require_equal(
        sha256_bytes(gold_bytes), manifest["gold_sha256"], "exact captured gold file SHA-256"
    )
    if set(document) != {
        "schema_version", "record_type", "suite_id", "manifest_identity_sha256",
        "fixtures", "provenance",
    }:
        raise ScoreError("gold has an unexpected object shape")
    _require_equal(document["schema_version"], SCHEMA_VERSION, "gold schema_version")
    _require_equal(document["record_type"], "lb2_hard_long_gold", "gold record_type")
    _require_equal(document["suite_id"], SUITE_ID, "gold suite_id")
    identity_sha = manifest_identity_sha256(manifest)
    _require_equal(
        document["manifest_identity_sha256"], identity_sha,
        "gold pre-gold public-manifest identity commitment",
    )
    # Explicitly close both edges without constructing a self-referential hash:
    # gold -> canonical pre-gold manifest, final manifest -> exact gold file.
    full_manifest_sha = sha256_bytes(canonical_json_file_bytes(manifest))
    if document["manifest_identity_sha256"] == full_manifest_sha:
        raise ScoreError("gold uses the final manifest hash instead of the non-cyclic pre-gold identity")
    rebuilt_identity = copy.deepcopy(manifest)
    committed_gold_sha = rebuilt_identity.pop("gold_sha256")
    _require_equal(
        sha256_bytes(canonical_json_file_bytes(rebuilt_identity)),
        document["manifest_identity_sha256"],
        "manifest/gold non-cyclic identity edge",
    )
    _require_equal(committed_gold_sha, sha256_bytes(gold_bytes), "manifest/gold exact-file edge")

    entries = document["fixtures"]
    if not isinstance(entries, list) or len(entries) != EXPECTED_FIXTURES:
        raise ScoreError("gold fixture list is incomplete")
    answers: dict[str, str] = {}
    source_ordinals: set[int] = set()
    source_ids: set[str] = set()
    raw_hashes: set[str] = set()
    canonical_hashes: set[str] = set()
    expected_shape = {
        "id", "answer", "source_ordinal", "source_id", "raw_row_sha256",
        "canonical_row_sha256", "payload_sha256",
    }
    for index, item in enumerate(entries, 1):
        if not isinstance(item, dict) or set(item) != expected_shape:
            raise ScoreError(f"gold fixture {index} has an unexpected object shape")
        fixture_id = item.get("id")
        if fixture_id not in fixtures or fixture_id in answers:
            raise ScoreError(f"gold fixture id is duplicate or unknown: {fixture_id!r}")
        answer = item.get("answer")
        if answer not in CHOICE_LABELS:
            raise ScoreError(f"gold fixture {fixture_id} answer must be exactly A, B, C, or D")
        ordinal = item.get("source_ordinal")
        if type(ordinal) is not int or not 0 <= ordinal < EXPECTED_SOURCE_COUNT:
            raise ScoreError(f"gold fixture {fixture_id} source_ordinal is invalid")
        source_id = item.get("source_id")
        if not isinstance(source_id, str) or re.fullmatch(r"[0-9a-f]{24}", source_id) is None:
            raise ScoreError(f"gold fixture {fixture_id} source_id is invalid")
        raw_sha = item.get("raw_row_sha256")
        canonical_sha = item.get("canonical_row_sha256")
        if not _is_sha256(raw_sha) or not _is_sha256(canonical_sha):
            raise ScoreError(f"gold fixture {fixture_id} row hashes are invalid")
        if ordinal in source_ordinals or source_id in source_ids or raw_sha in raw_hashes or canonical_sha in canonical_hashes:
            raise ScoreError(f"gold fixture {fixture_id} duplicates a source identity")
        _require_equal(
            item.get("payload_sha256"), fixtures[fixture_id]["payload_sha256"],
            f"gold fixture {fixture_id} public payload binding",
        )
        source_ordinals.add(ordinal)
        source_ids.add(source_id)
        raw_hashes.add(raw_sha)
        canonical_hashes.add(canonical_sha)
        answers[fixture_id] = answer
    if set(answers) != set(fixtures):
        raise ScoreError("gold fixture ids differ from the public manifest")

    provenance = document["provenance"]
    if not isinstance(provenance, dict) or set(provenance) != {
        "source", "source_file_sha256", "source_file_bytes", "source_row_count",
        "filter", "randomization_key_sha256", "requirements_lock_sha256",
    }:
        raise ScoreError("gold provenance has an unexpected object shape")
    _require_equal(
        provenance["source"],
        {
            "name": SOURCE_NAME, "url": SOURCE_URL, "revision": SOURCE_REVISION,
            "files": SOURCE_FILES,
        },
        "gold independently pinned source receipt",
    )
    _require_equal(provenance["source_file_sha256"], SOURCE_FILES["data.json"]["sha256"], "gold source file hash")
    _require_equal(provenance["source_file_bytes"], SOURCE_FILES["data.json"]["bytes"], "gold source file bytes")
    _require_equal(provenance["source_row_count"], EXPECTED_SOURCE_COUNT, "gold source row count")
    _require_equal(
        provenance["filter"],
        {"difficulty": "hard", "length": "long", "selected_count": EXPECTED_FIXTURES},
        "gold derived filter receipt",
    )
    if not _is_sha256(provenance["randomization_key_sha256"]):
        raise ScoreError("gold randomization-key commitment is invalid")
    _require_equal(
        provenance["requirements_lock_sha256"], REQUIREMENTS_LOCK_SHA256,
        "gold requirements lock pin",
    )
    return document, answers


# Exact upstream LongBench-v2 ``pred.py`` extraction behavior at the pinned
# revision: remove '*' and search the prescribed case-sensitive phrases.
def official_extract_answer(response: str) -> str | None:
    if not isinstance(response, str):
        return None
    cleaned = response.replace("*", "")
    match = re.search(r"The correct answer is \(([A-D])\)", cleaned)
    if match:
        return match.group(1)
    match = re.search(r"The correct answer is ([A-D])", cleaned)
    return match.group(1) if match else None


def official_answer_diagnostics(response: str) -> dict[str, Any]:
    empty = {
        "matches": [], "multiple_matches": False, "contradictory": False,
        "possible_negated_false_positive": False,
        "possible_quoted_or_instruction_echo": False,
        "possible_hypothetical_or_attributed_false_positive": False,
        "possible_subsequent_correction": False,
        "case_insensitive_near_miss_n": 0,
        "other_choice_mentions": [],
    }
    if not isinstance(response, str):
        return empty
    cleaned = response.replace("*", "")
    found: list[tuple[int, int, str, str]] = []
    for pattern, form in (
        (r"The correct answer is \(([A-D])\)", "parenthesized"),
        (r"The correct answer is ([A-D])", "bare"),
    ):
        for match in re.finditer(pattern, cleaned):
            found.append((match.start(), match.end(), match.group(1), form))
    found.sort()
    labels = [label for _, _, label, _ in found]
    possible_negation = False
    quoted_or_echo = False
    hypothetical = False
    correction = False
    spans = [(start, end) for start, end, _, _ in found]
    for start, end, _, _ in found:
        before = cleaned[max(0, start - 120):start]
        after = cleaned[end:min(len(cleaned), end + 120)]
        possible_negation |= re.search(
            r"(?i)\b(?:not|isn't|is not|incorrect|reject|deny|false)\b", before
        ) is not None
        hypothetical |= re.search(
            r"(?i)\b(?:if|suppose|hypothetically|example|claimed|claims|initially|might|maybe|could)\b",
            before,
        ) is not None
        correction |= re.search(
            r"(?i)^\s*[,;:.!?-]*\s*(?:but|however|rather|instead|correction|actually)\b",
            after,
        ) is not None
        # Quoted prompt/template echoes are a known upstream regex false-positive.
        left_quote = before.rfind('"') > before.rfind("\n") or before.rfind("'") > before.rfind("\n")
        right_quote = re.match(r"\s*[\"']", after) is not None
        quoted_or_echo |= left_quote and right_quote
        quoted_or_echo |= re.search(r"(?i)\b(?:format|template|instruction|respond with|say)\b", before) is not None
    near_misses = list(re.finditer(
        r"the correct answer is\s*(?:\(([a-d])\)|([a-d]))", cleaned, flags=re.IGNORECASE
    ))
    exact_starts = {start for start, _, _, _ in found}
    near_miss_n = sum(match.start() not in exact_starts for match in near_misses)
    other_mentions: list[str] = []
    for mention in re.finditer(r"(?<![A-Za-z0-9])\(?([A-D])\)?(?![A-Za-z0-9])", cleaned):
        if not any(start <= mention.start() and mention.end() <= end for start, end in spans):
            other_mentions.append(mention.group(1))
    return {
        "matches": [
            {"answer": label, "form": form, "offset": start}
            for start, _, label, form in found
        ],
        "multiple_matches": len(found) > 1,
        "contradictory": len(set(labels)) > 1,
        "possible_negated_false_positive": possible_negation,
        "possible_quoted_or_instruction_echo": quoted_or_echo,
        "possible_hypothetical_or_attributed_false_positive": hypothetical,
        "possible_subsequent_correction": correction,
        "case_insensitive_near_miss_n": near_miss_n,
        "other_choice_mentions": other_mentions,
    }


def official_longbench_v2_correct(response: str, answer: str) -> bool:
    return official_extract_answer(response) == answer


def strict_extract_answer(response: str) -> str | None:
    """Accept only the complete, canonical answer sentence and no added prose."""
    if not isinstance(response, str):
        return None
    match = re.fullmatch(r"The correct answer is \(([A-D])\)", response)
    return match.group(1) if match else None


def strict_mcq_correct(response: str, answer: str) -> bool:
    return strict_extract_answer(response) == answer


def _failure_kind(row: dict[str, Any]) -> str:
    failure = row.get("failure")
    return str(failure.get("kind")) if isinstance(failure, dict) else "unknown_execution_failure"


def _normalized_failure_kind(row: dict[str, Any]) -> str:
    failure = row.get("failure")
    raw = _failure_kind(row)
    message = failure.get("message", "") if isinstance(failure, dict) else ""
    stderr = failure.get("stderr", "") if isinstance(failure, dict) else ""
    cleanup = row.get("cleanup_errors")
    cleanup_text = " ".join(cleanup) if isinstance(cleanup, list) else ""
    signal = " ".join((raw, str(message), str(stderr), cleanup_text)).lower()
    matches = {
        "root_context_leak": (
            raw == "root_context_leak"
            or isinstance(row.get("root_context_leak_assertion"), dict)
            and row["root_context_leak_assertion"].get("leak_detected") is True
        ),
        "timeout": raw == "timeout" or row.get("timed_out") is True or bool(
            re.search(r"\b(?:timed[ -]?out|timeout|deadline exceeded)\b", signal)
        ),
        "transport": raw == "route_assertion" or bool(re.search(
            r"\b(?:transport|provider_call_failed|session_setup|connection|oauth|route assertion|http 5[0-9][0-9])\b",
            signal,
        )),
        "adapter_parser": bool(re.search(
            r"\b(?:adapter parser|adapter parse|malformed (?:json|tool|argument)|response parser|extract(?:ion)? failed|protocol parse)\b",
            signal,
        )),
        "depth": raw == "product_lifecycle" or bool(re.search(
            r"\b(?:depth[ -]?0|depth zero|recursion depth|recursive depth|missing root call)\b",
            signal,
        )),
        "monty_subset_tax": bool(re.search(
            r"\b(?:monty|python subset|subset runtime|unsupported (?:syntax|operation|import)|compile error|generator expression|mapping\.get)\b",
            signal,
        )),
        "other_execution": True,
    }
    for category in FAILURE_TAXONOMY_PRECEDENCE:
        if matches[category]:
            return category
    raise AssertionError("failure taxonomy precedence is incomplete")


def build_score_rows(
    rows: list[dict[str, Any]],
    jobs: list[dict[str, Any]],
    fixtures: dict[str, dict[str, Any]],
    answers: dict[str, str],
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row, job in zip(rows, jobs):
        fixture_id = job["fixture_id"]
        response = row["response"]
        answer = answers[fixture_id]
        official_prediction = official_extract_answer(response)
        official_diagnostics = official_answer_diagnostics(response)
        strict_prediction = strict_extract_answer(response)
        official_correct = official_prediction == answer
        strict_correct = strict_prediction == answer
        execution_success = row["execution_success"]
        if not execution_success:
            failure_class = "execution_failure"
        elif strict_correct:
            failure_class = None
        elif official_correct:
            failure_class = "answer_format_failure"
        elif official_prediction is None:
            failure_class = "answer_parse_failure"
        else:
            failure_class = "answer_wrong"
        scored.append({
            "run_id": job["run_id"],
            "ordinal": job["ordinal"],
            "fixture_id": fixture_id,
            "domain": fixtures[fixture_id]["domain"],
            "sub_domain": fixtures[fixture_id]["sub_domain"],
            "arm": job["arm"],
            "repetition": 1,
            "execution_success": execution_success,
            "response_sha256": sha256_bytes(response.encode("utf-8")),
            "official_extracted_answer": official_prediction,
            "official_answer_diagnostics": official_diagnostics,
            "strict_extracted_answer": strict_prediction,
            "official_longbench_v2_correct": official_correct,
            "strict_mcq_correct": strict_correct,
            "end_to_end_official_correct": execution_success and official_correct,
            "end_to_end_strict_correct": execution_success and strict_correct,
            "failure_class": failure_class,
            "raw_execution_failure_kind": (
                None if execution_success else _failure_kind(row)
            ),
            "normalized_execution_failure_kind": (
                None if execution_success else _normalized_failure_kind(row)
            ),
        })
    return scored


def percentile(values: Sequence[float], probability: float) -> float | None:
    if not values:
        return None
    if not 0 <= probability <= 1:
        raise ScoreError("percentile probability must be in [0, 1]")
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


def _mean_bool(values: Iterable[bool]) -> float | None:
    items = list(values)
    return sum(items) / len(items) if items else None


def _usage_for_row(row: dict[str, Any]) -> dict[str, int] | None:
    evidence = row["efficiency_evidence"]
    if evidence["valid"] is not True:
        return None
    return {field: int(row["usage"][field]) for field in USAGE_FIELDS}


def _root_token_economy_summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    available = [row["root_token_economy"] for row in rows if row["root_token_economy"]["available"]]
    values = [float(item["tokens"]) for item in available]
    missing = len(rows) - len(available)
    recorded_total = sum(values)
    return {
        "available_n": len(available),
        "missing_n": missing,
        "authority_counts": dict(sorted(Counter(item["authority"] for item in available).items())),
        "recorded_tokens_total": recorded_total,
        "unconditional_tokens_total": recorded_total if missing == 0 else None,
        "recorded_tokens_p50": percentile(values, 0.50),
        "recorded_tokens_p95": percentile(values, 0.95),
        "unconditional_tokens_p50": percentile(values, 0.50) if missing == 0 else None,
        "unconditional_tokens_p95": percentile(values, 0.95) if missing == 0 else None,
        "missing_values_are_zero": False,
    }


def _fixed_denominator_summary(
    score_rows: Sequence[dict[str, Any]], raw_by_run: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    scheduled = len(score_rows)
    if scheduled <= 0:
        raise ScoreError("cannot summarize an empty score cell")
    completed = [item for item in score_rows if item["execution_success"]]
    execution_failures = [item for item in score_rows if not item["execution_success"]]
    raw_execution_taxonomy = Counter(
        _failure_kind(raw_by_run[item["run_id"]]) for item in execution_failures
    )
    execution_taxonomy = Counter(
        _normalized_failure_kind(raw_by_run[item["run_id"]])
        for item in execution_failures
    )
    answer_taxonomy = Counter(
        str(item["failure_class"]) for item in completed if item["failure_class"] is not None
    )
    raw_rows = [raw_by_run[item["run_id"]] for item in score_rows]
    route_asserted = sum(row["runtime_route_assertion"]["asserted"] for row in raw_rows)
    lifecycle_asserted = sum(row["product_lifecycle_assertion"]["asserted"] for row in raw_rows)
    latencies = [float(row["latency_seconds"]) for row in raw_rows]
    valid_usages = [usage for row in raw_rows if (usage := _usage_for_row(row)) is not None]
    recorded_totals = {
        field: sum(usage[field] for usage in valid_usages) for field in USAGE_FIELDS
    }
    missing_usage = scheduled - len(valid_usages)
    total_values = [float(usage["total_tokens"]) for usage in valid_usages]
    unconditional_totals = recorded_totals if missing_usage == 0 else None
    return {
        "scheduled_n_fixed_denominator": scheduled,
        "execution": {
            "completed_n": len(completed),
            "failed_n": len(execution_failures),
            "completion_rate": len(completed) / scheduled,
            "failure_taxonomy": dict(sorted(execution_taxonomy.items())),
            "raw_failure_kinds": dict(sorted(raw_execution_taxonomy.items())),
            "failure_taxonomy_precedence": list(FAILURE_TAXONOMY_PRECEDENCE),
        },
        "answer_scoring_all_terminal_outputs": {
            "official_longbench_v2_correct_n": sum(item["official_longbench_v2_correct"] for item in score_rows),
            "official_longbench_v2_accuracy": _mean_bool(item["official_longbench_v2_correct"] for item in score_rows),
            "strict_mcq_correct_n": sum(item["strict_mcq_correct"] for item in score_rows),
            "strict_mcq_accuracy": _mean_bool(item["strict_mcq_correct"] for item in score_rows),
        },
        "answer_scoring_completed_only": {
            "n": len(completed),
            "official_longbench_v2_correct_n": sum(item["official_longbench_v2_correct"] for item in completed),
            "official_longbench_v2_accuracy": _mean_bool(item["official_longbench_v2_correct"] for item in completed),
            "strict_mcq_correct_n": sum(item["strict_mcq_correct"] for item in completed),
            "strict_mcq_accuracy": _mean_bool(item["strict_mcq_correct"] for item in completed),
        },
        "end_to_end_fixed_denominator": {
            "denominator_n": scheduled,
            "official_longbench_v2_correct_n": sum(item["end_to_end_official_correct"] for item in score_rows),
            "official_longbench_v2_accuracy": _mean_bool(item["end_to_end_official_correct"] for item in score_rows),
            "strict_mcq_correct_n": sum(item["end_to_end_strict_correct"] for item in score_rows),
            "strict_mcq_accuracy": _mean_bool(item["end_to_end_strict_correct"] for item in score_rows),
        },
        "failure_separation": {
            "execution_failure_n": len(execution_failures),
            "completed_answer_failure_n": sum(not item["strict_mcq_correct"] for item in completed),
            "answer_failure_taxonomy": dict(sorted(answer_taxonomy.items())),
        },
        "route_integrity": {
            "asserted_n": route_asserted,
            "failed_n": scheduled - route_asserted,
            "rate": route_asserted / scheduled,
            "all_asserted": route_asserted == scheduled,
        },
        "product_lifecycle": {
            "asserted_n": lifecycle_asserted,
            "failed_n": scheduled - lifecycle_asserted,
            "rate": lifecycle_asserted / scheduled,
            "all_asserted": lifecycle_asserted == scheduled,
        },
        "wall_seconds_all_attempts": {
            "observed_n": len(latencies),
            "missing_n": scheduled - len(latencies),
            "p50": percentile(latencies, 0.50),
            "p95": percentile(latencies, 0.95),
        },
        "tokens_all_attempts_unconditional": {
            "valid_usage_n": len(valid_usages),
            "missing_usage_n": missing_usage,
            "recorded_totals": recorded_totals,
            "unconditional_totals": unconditional_totals,
            "recorded_total_tokens_p50": percentile(total_values, 0.50),
            "recorded_total_tokens_p95": percentile(total_values, 0.95),
            "unconditional_total_tokens_p50": percentile(total_values, 0.50) if missing_usage == 0 else None,
            "unconditional_total_tokens_p95": percentile(total_values, 0.95) if missing_usage == 0 else None,
        },
        "root_token_economy_all_attempts": _root_token_economy_summary(raw_rows),
    }


def aggregate_scores(
    score_rows: list[dict[str, Any]], raw_rows: list[dict[str, Any]], arms: Sequence[str]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw_by_run = {row["run_id"]: row for row in raw_rows}
    arm_documents: dict[str, Any] = {}
    domain_documents: list[dict[str, Any]] = []
    for arm in arms:
        selected = [item for item in score_rows if item["arm"] == arm]
        if len(selected) != EXPECTED_FIXTURES:
            raise ScoreError(f"arm {arm} does not have the fixed denominator {EXPECTED_FIXTURES}")
        overall = _fixed_denominator_summary(selected, raw_by_run)
        domains: list[dict[str, Any]] = []
        for domain, expected_n in SELECTED_DOMAIN_COUNTS.items():
            domain_rows = [item for item in selected if item["domain"] == domain]
            if len(domain_rows) != expected_n:
                raise ScoreError(f"arm {arm} domain {domain!r} denominator drift")
            summary = _fixed_denominator_summary(domain_rows, raw_by_run)
            summary.update({"arm": arm, "domain": domain})
            domains.append(summary)
            domain_documents.append(summary)
        completed = [item for item in selected if item["execution_success"]]
        arm_documents[arm] = {
            "scheduled": EXPECTED_FIXTURES,
            "scheduled_n": EXPECTED_FIXTURES,
            "execution_rate": len(completed) / EXPECTED_FIXTURES,
            "completed_accuracy": _mean_bool(
                item["official_longbench_v2_correct"] for item in completed
            ),
            "end_to_end_accuracy": _mean_bool(
                item["end_to_end_official_correct"] for item in selected
            ),
            "metric_authority": "pinned official LongBench-v2 answer extraction",
            "overall": overall,
            "domains": domains,
        }
    return arm_documents, domain_documents


def paired_comparisons(
    score_rows: list[dict[str, Any]],
    fixtures: dict[str, dict[str, Any]],
    arms: Sequence[str],
    *,
    seed: int = DEFAULT_BOOTSTRAP_SEED,
    resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
) -> dict[str, Any]:
    if type(seed) is not int or type(resamples) is not int or resamples <= 0:
        raise ScoreError("bootstrap seed/resamples must be integers and resamples positive")
    fixture_ids = list(fixtures)
    if len(fixture_ids) != EXPECTED_FIXTURES:
        raise ScoreError("paired bootstrap requires the exact 63-fixture cohort")
    by_key = {(item["fixture_id"], item["arm"]): item for item in score_rows}
    metrics = (
        "official_longbench_v2_correct", "strict_mcq_correct",
        "end_to_end_official_correct", "end_to_end_strict_correct",
        "execution_success",
    )
    result: dict[str, Any] = {}
    for arm_a, arm_b in itertools.combinations(arms, 2):
        differences = {
            metric: [
                float(by_key[(fixture_id, arm_a)][metric])
                - float(by_key[(fixture_id, arm_b)][metric])
                for fixture_id in fixture_ids
            ]
            for metric in metrics
        }
        observed = {
            metric: sum(values) / EXPECTED_FIXTURES
            for metric, values in differences.items()
        }
        draws: dict[str, list[float]] = {metric: [] for metric in metrics}
        rng_seed = int.from_bytes(
            hashlib.sha256(f"{seed}:{arm_a}:{arm_b}".encode("utf-8")).digest()[:8], "big"
        )
        rng = random.Random(rng_seed)
        for _ in range(resamples):
            indices = [rng.randrange(EXPECTED_FIXTURES) for _ in range(EXPECTED_FIXTURES)]
            for metric in metrics:
                values = differences[metric]
                draws[metric].append(sum(values[index] for index in indices) / EXPECTED_FIXTURES)
        result[f"{arm_a}__minus__{arm_b}"] = {
            "paired_fixture_n": EXPECTED_FIXTURES,
            "direction": "first arm minus second arm",
            "resamples": resamples,
            "metrics": {
                metric: {
                    "delta": observed[metric],
                    "ci95": [percentile(draws[metric], 0.025), percentile(draws[metric], 0.975)],
                }
                for metric in metrics
            },
        }
    return result


def _is_nested_or_equal(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _validate_separate_roots(public_root: Path, gold_root: Path, runs_root: Path) -> None:
    labeled = {
        "public": _absolute_lexical(public_root),
        "gold": _absolute_lexical(gold_root),
        "runs": _absolute_lexical(runs_root),
    }
    for (left_name, left), (right_name, right) in itertools.combinations(labeled.items(), 2):
        if _is_nested_or_equal(left, right):
            raise ScoreError(
                f"{left_name} and {right_name} roots must be lexically distinct and non-nested"
            )


def build_report(
    manifest_path: Path,
    gold_path: Path,
    runs_path: Path,
    *,
    schedule_path: Path | None = None,
    claims_root: Path | None = None,
    artifacts_root: Path | None = None,
    bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED,
    bootstrap_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
) -> dict[str, Any]:
    if type(bootstrap_seed) is not int or type(bootstrap_resamples) is not int or bootstrap_resamples <= 0:
        raise ScoreError("bootstrap configuration is invalid")
    manifest_path = _absolute_lexical(Path(manifest_path))
    runs_path = _absolute_lexical(Path(runs_path))
    unresolved_gold = _absolute_lexical(Path(gold_path))
    if manifest_path.name != "manifest.json" or unresolved_gold.name != "gold.json":
        raise ScoreError("sealed public/gold filenames must be manifest.json and gold.json")
    _validate_separate_roots(manifest_path.parent, unresolved_gold.parent, runs_path.parent)
    expected_schedule = Path(str(runs_path) + ".schedule.json")
    expected_claims = Path(str(runs_path) + ".claims")
    effective_schedule = _absolute_lexical(
        Path(schedule_path) if schedule_path is not None else expected_schedule
    )
    effective_claims = _absolute_lexical(
        Path(claims_root) if claims_root is not None else expected_claims
    )
    effective_artifacts = _absolute_lexical(
        Path(artifacts_root) if artifacts_root is not None
        else Path(str(runs_path) + ".artifacts")
    )
    if effective_schedule != expected_schedule:
        raise ScoreError(
            "schedule must be the exact runs sibling <runs>.schedule.json and must not alias gold"
        )
    if effective_claims != expected_claims:
        raise ScoreError("claims must be the exact runs sibling <runs>.claims")

    # Establish every root/file authority before reading any artifact bytes.
    # The gold directory is held now, but gold.json is deliberately not opened
    # until terminal schedule/result/claim validation below.
    public_root_fd = gold_root_fd = runs_parent_fd = runs_fd = schedule_fd = claims_root_fd = None
    try:
        _, public_root_fd = _open_directory_fd(manifest_path.parent, "public suite root")
        _, gold_root_fd = _open_directory_fd(unresolved_gold.parent, "owner-only gold root")
        _, runs_parent_fd = _open_directory_fd(runs_path.parent, "runs root")
        runs_fd = _open_private_regular_fd_at(
            runs_parent_fd, runs_path.name, "frozen inference JSONL"
        )
        schedule_fd = _open_private_regular_fd_at(
            runs_parent_fd, effective_schedule.name, "frozen schedule"
        )
        claims_root_fd = _open_child_directory_fd(
            runs_parent_fd, effective_claims.name, "frozen claims root"
        )

        manifest, fixtures = load_public_manifest(
            manifest_path, held_root_fd=public_root_fd
        )
        captured_schedule = _capture_regular_fd(schedule_fd, "frozen schedule")
        captured_runs = _capture_regular_fd(runs_fd, "frozen inference JSONL")
        schedule, jobs, rows, arms = validate_frozen_runs(
            manifest_path,
            manifest,
            fixtures,
            runs_path,
            effective_schedule,
            effective_claims,
            effective_artifacts,
            captured_schedule=captured_schedule,
            captured_runs=captured_runs,
            held_claims_root_fd=claims_root_fd,
        )
        gold_path = unresolved_gold
        gold, answers = load_gold(
            gold_path, manifest_path, manifest, fixtures, held_root_fd=gold_root_fd
        )
    finally:
        for descriptor in (
            claims_root_fd, schedule_fd, runs_fd, runs_parent_fd,
            gold_root_fd, public_root_fd,
        ):
            if descriptor is not None:
                os.close(descriptor)
    score_rows = build_score_rows(rows, jobs, fixtures, answers)
    arm_documents, domain_documents = aggregate_scores(score_rows, rows, arms)
    comparisons = paired_comparisons(
        score_rows, fixtures, arms, seed=bootstrap_seed, resamples=bootstrap_resamples
    )
    configuration = schedule["configuration"]
    candidate_binary = configuration["candidate"]["components"]["azdaja"]
    executable_binary = configuration["executables"]["azdaja"]
    candidate_binary_matches_executable = (
        candidate_binary["sha256"] == executable_binary["sha256"]
        and candidate_binary["bytes"] == executable_binary["bytes"]
    )
    if not candidate_binary_matches_executable:
        raise ScoreError("candidate azdaja component/executable identity diverged after validation")
    disclosure = (
        "Private execution of a derived, publicly answer-joinable lb2-hard-long-63-v1 "
        "cohort; it is not blind/secret gold, not the complete official LongBench-v2 "
        "evaluation, and not an official leaderboard result."
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_hard_long_deferred_scores",
        "suite_id": SUITE_ID,
        "disclosure": {
            "derived_subset": True,
            "private_execution_artifacts": True,
            "publicly_joinable_to_upstream_answers": True,
            "blind_or_secret_gold": False,
            "official_longbench_v2_leaderboard_result": False,
            "runner_network_dns_cache_containment_verified": False,
            "blindness_note": (
                "Randomized IDs only unlink filenames. All 63 public payloads are uniquely "
                "joinable to the pinned public upstream data/answers via network or cache. "
                "No enforceable runner network, DNS, dataset/model-cache, source/key/gold, "
                "other-arm, or prior-report sandbox receipt is available, so blindness is not claimed."
            ),
            "statement": disclosure,
        },
        "version_stamp": {
            "candidate": copy.deepcopy(configuration["candidate"]),
            "candidate_azdaja_component": copy.deepcopy(candidate_binary),
            "candidate_azdaja_executable": copy.deepcopy(executable_binary),
            "candidate_azdaja_component_equals_executable": candidate_binary_matches_executable,
            "controller": copy.deepcopy(configuration["controller"]),
            "executables": copy.deepcopy(configuration["executables"]),
        },
        "protocol": {
            "model": MODEL,
            "reasoning": REASONING,
            "arms": list(arms),
            "fixed_denominator_per_arm": EXPECTED_FIXTURES,
            "runner_artifact_contract": {
                "schedule_record_type": "lb2_frozen_schedule",
                "run_id_domain": RUN_ID_DOMAIN.decode("ascii"),
                "candidate_components": ["SKILL.md", "azdaja", "config.toml"],
                "controller_identity_fields": ["path", "sha256", "bytes"],
                "executable_identity_fields": [
                    "path", "sha256", "bytes", "version", "version_command"
                ],
                "executable_names": ["jcode", "azdaja", "prime-agent"],
                "version_command_rule": "[executable.path, '--version']",
                "ordering": "random.Random(seed): shuffle fixtures once, then shuffle three arms per fixture",
                "execution_failure_kinds": sorted(EXECUTION_FAILURE_KINDS),
                "normalized_failure_taxonomy": list(FAILURE_TAXONOMY),
                "failure_taxonomy_precedence": list(FAILURE_TAXONOMY_PRECEDENCE),
                "root_context_match_characters": ROOT_CONTEXT_MATCH_CHARACTERS,
                "root_context_rolling_hash": ROOT_CONTEXT_ROLLING_HASH,
                "root_token_economy_authorities": sorted(ROOT_TOKEN_ECONOMY_AUTHORITIES),
            },
            "official_metric": (
                "Pinned upstream LongBench-v2 pred.py extract_answer followed by exact answer equality"
            ),
            "official_metric_source": {
                "repository": OFFICIAL_EVAL_REPO_URL,
                "commit": OFFICIAL_EVAL_COMMIT,
                "pred_py_sha256": OFFICIAL_PRED_PY_SHA256,
            },
            "strict_metric": (
                "Recorded response string must be exactly 'The correct answer is (X)' "
                "for one uppercase A-D; the scorer applies no whitespace normalization"
            ),
        },
        "integrity": {
            "validated": True,
            "terminal_complete_before_gold_read": True,
            "receipts_match_embedded_pins": True,
            "raw_upstream_replayed_by_scorer": False,
            "manifest_gold_hash_cycle_checked": True,
            "manifest_sha256": sha256_bytes(canonical_json_file_bytes(manifest)),
            "manifest_identity_sha256": manifest_identity_sha256(manifest),
            "gold_sha256": sha256_bytes(canonical_json_file_bytes(gold)),
            "inference_jsonl_sha256": sha256_bytes(
                b"".join(canonical_json_file_bytes(row) for row in rows)
            ),
            "schedule_id": schedule["schedule_id"],
            "scheduled_jobs": len(jobs),
            "terminal_rows": len(rows),
            "claims_and_completions": 2 * len(jobs),
            "candidate_azdaja_component_equals_executable": candidate_binary_matches_executable,
            "treatment_exact_root_transcripts_valid_n": sum(
                row["root_context_leak_assertion"]["trace_valid"]
                for row in rows if row["arm"] == "jcode-azdaja"
            ),
            "treatment_root_context_leaks_n": sum(
                row["root_context_leak_assertion"]["leak_detected"] is True
                for row in rows if row["arm"] == "jcode-azdaja"
            ),
        },
        "bootstrap": {
            "seed": bootstrap_seed,
            "resamples": bootstrap_resamples,
            "method": "paired fixture percentile bootstrap over the frozen 63-fixture triplets",
        },
        "arms": arm_documents,
        "domains": domain_documents,
        "comparisons": comparisons,
        "scores": score_rows,
        "gold_provenance": {
            "manifest_identity_sha256": gold["manifest_identity_sha256"],
            "source": gold["provenance"]["source"],
            "filter": gold["provenance"]["filter"],
        },
    }


def _rename_noreplace_fd(directory_fd: int, source_name: str, target_name: str) -> None:
    source_b = os.fsencode(source_name)
    target_b = os.fsencode(target_name)
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        renameatx_np = getattr(libc, "renameatx_np", None)
        if renameatx_np is None:
            raise ScoreError("kernel has no dirfd atomic no-replace rename primitive")
        renameatx_np.argtypes = (
            ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p,
            ctypes.c_uint,
        )
        renameatx_np.restype = ctypes.c_int
        result = renameatx_np(
            directory_fd, source_b, directory_fd, target_b, 0x00000004
        )
    elif sys.platform.startswith("linux"):
        renameat2 = getattr(libc, "renameat2", None)
        if renameat2 is None:
            raise ScoreError("kernel has no dirfd atomic no-replace rename primitive")
        renameat2.argtypes = (
            ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p,
            ctypes.c_uint,
        )
        renameat2.restype = ctypes.c_int
        result = renameat2(directory_fd, source_b, directory_fd, target_b, 1)
    else:
        raise ScoreError("platform has no supported dirfd atomic no-replace rename primitive")
    if result != 0:
        error = ctypes.get_errno()
        if error in (errno.EEXIST, errno.ENOTEMPTY):
            raise ScoreError(f"private output already exists; refusing replacement: {target_name}")
        raise ScoreError(
            f"atomic no-replace publication failed for {target_name}: {os.strerror(error)}"
        )


def _path_directory_identity(path: Path, label: str) -> tuple[int, int]:
    _, fd = _open_directory_fd(path, label)
    try:
        metadata = os.fstat(fd)
        return metadata.st_dev, metadata.st_ino
    finally:
        os.close(fd)


def atomic_create_private_json(path: Path, value: Any) -> None:
    path = _absolute_lexical(Path(path))
    if not path.name or "/" in path.name or path.name in {".", ".."}:
        raise ScoreError("private report filename is unsafe")
    parent, parent_fd = _open_directory_fd(path.parent, "private report output root")
    parent_identity = (os.fstat(parent_fd).st_dev, os.fstat(parent_fd).st_ino)
    data = canonical_json_file_bytes(value)
    temporary = f".{path.name}.tmp-{secrets.token_hex(16)}"
    temp_created = False
    published = False
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            fd = os.open(temporary, flags, 0o600, dir_fd=parent_fd)
            temp_created = True
        except OSError as exc:
            raise ScoreError(f"cannot create private report temporary: {exc}") from exc
        try:
            if os.name == "posix":
                os.fchmod(fd, 0o600)
            opened = os.fstat(fd)
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise ScoreError("private report temporary is not a singly-linked regular file")
            view = memoryview(data)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise ScoreError("short write while creating private report temporary")
                view = view[written:]
            os.fsync(fd)
        finally:
            os.close(fd)
        if _path_directory_identity(parent, "private report output root recheck") != parent_identity:
            raise ScoreError("private report output root path changed before publication")
        _rename_noreplace_fd(parent_fd, temporary, path.name)
        temp_created = False
        published = True
        os.fsync(parent_fd)
        if _path_directory_identity(parent, "private report output root postcheck") != parent_identity:
            os.unlink(path.name, dir_fd=parent_fd)
            os.fsync(parent_fd)
            published = False
            raise ScoreError("private report output root path changed during publication")
        final = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            not stat.S_ISREG(final.st_mode) or final.st_nlink != 1
            or stat.S_IMODE(final.st_mode) != 0o600 or final.st_size != len(data)
        ):
            os.unlink(path.name, dir_fd=parent_fd)
            os.fsync(parent_fd)
            published = False
            raise ScoreError("published private report identity/mode/size is invalid")
    finally:
        if temp_created:
            try:
                os.unlink(temporary, dir_fd=parent_fd)
                os.fsync(parent_fd)
            except OSError:
                pass
        os.close(parent_fd)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--runs", required=True, type=Path)
    parser.add_argument("--schedule", type=Path, help="default: <runs>.schedule.json")
    parser.add_argument("--claims", type=Path, help="default: <runs>.claims")
    parser.add_argument(
        "--artifacts-root", required=True, type=Path,
        help="owner-only retained run-artifact directory",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    parser.add_argument("--bootstrap-resamples", type=int, default=DEFAULT_BOOTSTRAP_RESAMPLES)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        output = _absolute_lexical(args.output)
        input_roots = (
            _absolute_lexical(args.manifest).parent,
            _absolute_lexical(args.gold).parent,
            _absolute_lexical(args.runs).parent,
            _absolute_lexical(
                args.schedule if args.schedule is not None
                else Path(str(_absolute_lexical(args.runs)) + ".schedule.json")
            ).parent,
            _absolute_lexical(
                args.claims if args.claims is not None
                else Path(str(_absolute_lexical(args.runs)) + ".claims")
            ),
            _absolute_lexical(args.artifacts_root),
        )
        if any(_is_nested_or_equal(output.parent, root) for root in input_roots):
            raise ScoreError("private report output root must be outside every sealed/run root")
        result = build_report(
            args.manifest,
            args.gold,
            args.runs,
            schedule_path=args.schedule,
            claims_root=args.claims,
            artifacts_root=args.artifacts_root,
            bootstrap_seed=args.bootstrap_seed,
            bootstrap_resamples=args.bootstrap_resamples,
        )
        atomic_create_private_json(output, result)
    except (ScoreError, OSError) as exc:
        print(f"score error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "output": str(output),
        "schedule_id": result["integrity"]["schedule_id"],
        "scheduled_jobs": result["integrity"]["scheduled_jobs"],
        "disclosure": result["disclosure"]["statement"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
