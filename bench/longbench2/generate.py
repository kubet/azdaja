#!/usr/bin/env python3
"""Validate and seal the private ``lb2-hard-long-63-v1`` derived suite.

This program performs no inference.  It accepts an already downloaded, pinned
LongBench-v2 ``data.json``, validates all 503 rows before filtering the exact 63
``difficulty == hard`` and ``length == long`` rows, and atomically writes an
inference-safe public tree plus a separately rooted owner-only gold receipt.
"""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import hmac
import json
import os
import re
import secrets
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SUITE_ID = "lb2-hard-long-63-v1"
SCHEMA_VERSION = 1
EXPECTED_SOURCE_COUNT = 503
EXPECTED_COUNT = 63
SOURCE_NAME = "zai-org/LongBench-v2"
SOURCE_URL = "https://huggingface.co/datasets/zai-org/LongBench-v2"
SOURCE_REVISION = "2b48e494f2c7a2f0af81aae178e05c7e1dde0fe9"
SOURCE_FILES = {
    ".gitattributes": {
        "sha256": "b3ca89743b410b60a97ba9486e44b205c70f6fb35024ef02198cf766dfdffb18",
        "bytes": 2507,
        "git_oid": "adec96cd34a8bdb402a98453004ec7b60123d9d2",
    },
    "README.md": {
        "sha256": "9fdd1a3ebe86507253c124a18e9f78c898ce6341c12990af17ab868b8f600c35",
        "bytes": 4626,
        "git_oid": "87decc4d91ca85fcf7e593cacfb5b954e36cd0d9",
    },
    "data.json": {
        "sha256": "15d61c22d92c96900b3c4948b6aeea218d3214b676a65df48e7b8555604c7fe2",
        "bytes": 465490535,
        "git_oid": "6cdc8c85cf593dcdc2311cdc0fd59ac34817fd7e",
        "lfs_oid_sha256": "15d61c22d92c96900b3c4948b6aeea218d3214b676a65df48e7b8555604c7fe2",
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
ROW_KEYS = (
    "_id", "domain", "sub_domain", "difficulty", "length", "question",
    "choice_A", "choice_B", "choice_C", "choice_D", "answer", "context",
)
CHOICE_LABELS = ("A", "B", "C", "D")
DIFFICULTIES = frozenset(("easy", "hard"))
LENGTHS = frozenset(("short", "medium", "long"))
DOMAINS = frozenset((
    "Code Repository Understanding", "Long In-context Learning",
    "Long Structured Data Understanding", "Long-dialogue History Understanding",
    "Multi-Document QA", "Single-Document QA",
))
SUB_DOMAINS = frozenset((
    "Academic", "Agent history QA", "Code repo QA", "Detective",
    "Dialogue history QA", "Event ordering", "Financial", "Governmental",
    "Knowledge graph reasoning", "Legal", "Literary", "Many-shot learning",
    "Multi-news", "New language translation", "Table QA", "User guide QA",
))
CELL_COUNTS = {
    ("easy", "long"): 45, ("easy", "medium"): 88, ("easy", "short"): 59,
    ("hard", "long"): 63, ("hard", "medium"): 127, ("hard", "short"): 121,
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


class SealError(RuntimeError):
    """A fail-closed generation error."""


@dataclass(frozen=True)
class SourceRow:
    ordinal: int
    row: dict[str, str]
    raw_row_sha256: str
    canonical_row_sha256: str
    payload: dict[str, Any]
    payload_bytes: bytes
    payload_sha256: str


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def _pairs_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(data: bytes, label: str) -> Any:
    try:
        text = data.decode("utf-8")
        return json.loads(text, object_pairs_hook=_pairs_object,
                          parse_constant=_reject_constant)
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SealError(f"invalid {label}: {exc}") from exc


def _mode(st: os.stat_result) -> int:
    return stat.S_IMODE(st.st_mode)


def require_private_dir(path: Path, label: str) -> Path:
    if path.is_symlink():
        raise SealError(f"{label} must not be a symlink: {path}")
    try:
        st = path.stat()
    except OSError as exc:
        raise SealError(f"cannot stat {label} {path}: {exc}") from exc
    if not stat.S_ISDIR(st.st_mode):
        raise SealError(f"{label} must be a directory: {path}")
    if os.name == "posix":
        if st.st_uid != os.geteuid():
            raise SealError(f"{label} must be owned by the current user: {path}")
        if _mode(st) != 0o700:
            raise SealError(f"{label} mode must be 0700, got {_mode(st):04o}: {path}")
    return path.resolve(strict=True)


def read_private_file(path: Path, label: str) -> bytes:
    if path.is_symlink():
        raise SealError(f"{label} must not be a symlink: {path}")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise SealError(f"cannot open {label} {path}: {exc}") from exc
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise SealError(f"{label} must be a regular file: {path}")
        if os.name == "posix":
            if st.st_uid != os.geteuid():
                raise SealError(f"{label} must be owned by current user: {path}")
            if _mode(st) != 0o600:
                raise SealError(f"{label} mode must be 0600, got {_mode(st):04o}: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        os.close(fd)


def read_regular_file(path: Path, label: str) -> bytes:
    if path.is_symlink():
        raise SealError(f"{label} must not be a symlink: {path}")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise SealError(f"cannot open {label} {path}: {exc}") from exc
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise SealError(f"{label} must be a regular file: {path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        os.close(fd)


@dataclass(frozen=True)
class ParentHandle:
    path: Path
    fd: int
    device: int
    inode: int


def open_private_parent(path: Path, label: str) -> ParentHandle:
    """Open a pre-existing owner-only parent and pin its directory identity."""
    parent = path.expanduser().parent
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(parent, flags)
    except OSError as exc:
        raise SealError(f"cannot open pre-existing {label}: {parent}: {exc}") from exc
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISDIR(metadata.st_mode):
            raise SealError(f"{label} must be a directory: {parent}")
        if os.name == "posix":
            if metadata.st_uid != os.geteuid():
                raise SealError(f"{label} must be owned by current user: {parent}")
            if _mode(metadata) != 0o700:
                raise SealError(
                    f"{label} mode must be 0700, got {_mode(metadata):04o}: {parent}"
                )
        # Resolve only for separation/diagnostics. All mutations below remain
        # relative to this held fd, never to this pathname.
        resolved = parent.resolve(strict=True)
        current = os.stat(resolved, follow_symlinks=False)
        if (current.st_dev, current.st_ino) != (metadata.st_dev, metadata.st_ino):
            raise SealError(f"{label} pathname changed while it was opened: {parent}")
        return ParentHandle(resolved, fd, metadata.st_dev, metadata.st_ino)
    except Exception:
        os.close(fd)
        raise


def _verify_parent_handle(parent: ParentHandle, label: str) -> None:
    metadata = os.fstat(parent.fd)
    if (metadata.st_dev, metadata.st_ino) != (parent.device, parent.inode):
        raise SealError(f"held {label} identity changed")
    try:
        current = os.stat(parent.path, follow_symlinks=False)
    except OSError as exc:
        raise SealError(f"{label} pathname was removed or swapped: {parent.path}: {exc}") from exc
    if (current.st_dev, current.st_ino) != (parent.device, parent.inode):
        raise SealError(f"{label} pathname was swapped after validation: {parent.path}")


def _close_parent_handles(*parents: ParentHandle) -> None:
    closed: set[int] = set()
    for parent in parents:
        if parent.fd not in closed:
            os.close(parent.fd)
            closed.add(parent.fd)


def write_exclusive_private(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise SealError(f"cannot exclusively create {path}: {exc}") from exc
    try:
        if os.name == "posix":
            os.fchmod(fd, 0o600)
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise SealError(f"short write to {path}")
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)


def validate_pinned_companion(path: Path, relative: str) -> dict[str, Any]:
    expected = SOURCE_FILES[relative]
    data = read_private_file(path, f"pinned {relative}")
    actual = {"sha256": sha256_bytes(data), "bytes": len(data)}
    if actual != {"sha256": expected["sha256"], "bytes": expected["bytes"]}:
        raise SealError(f"pinned {relative} drift: expected {expected}, got {actual}")
    return dict(expected)


def validate_requirements_lock(path: Path) -> str:
    data = read_regular_file(path, "requirements lock")
    digest = sha256_bytes(data)
    if digest != REQUIREMENTS_LOCK_SHA256:
        raise SealError(f"requirements lock drift: expected {REQUIREMENTS_LOCK_SHA256}, got {digest}")
    return digest


def load_public_notice_files() -> list[tuple[str, bytes]]:
    """Load the exact, pinned attribution files bundled next to this program."""
    result: list[tuple[str, bytes]] = []
    for name, expected in PUBLIC_NOTICE_FILES.items():
        data = read_regular_file(Path(__file__).with_name(name), f"bundled {name}")
        actual = {"sha256": sha256_bytes(data), "bytes": len(data)}
        if actual != expected:
            raise SealError(f"bundled notice drift for {name}: expected {expected}, got {actual}")
        result.append((name, data))
    return result


JSON_WHITESPACE = frozenset(" \t\r\n")


def _skip_json_whitespace(text: str, position: int) -> int:
    while position < len(text) and text[position] in JSON_WHITESPACE:
        position += 1
    return position


def split_top_level_array(data: bytes) -> list[tuple[dict[str, Any], bytes]]:
    """Parse JSON once strictly, then recover each exact top-level element byte slice."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SealError(f"source data.json is not UTF-8: {exc}") from exc
    decoder = json.JSONDecoder(object_pairs_hook=_pairs_object, parse_constant=_reject_constant)
    length = len(text)
    pos = 0
    pos = _skip_json_whitespace(text, pos)
    if pos >= length or text[pos] != "[":
        raise SealError("source data.json must contain one top-level JSON array")
    pos += 1
    result: list[tuple[dict[str, Any], bytes]] = []
    while True:
        pos = _skip_json_whitespace(text, pos)
        if pos < length and text[pos] == "]":
            pos += 1
            break
        start = pos
        try:
            value, end = decoder.raw_decode(text, pos)
        except (json.JSONDecodeError, ValueError) as exc:
            raise SealError(f"invalid source row {len(result)}: {exc}") from exc
        if not isinstance(value, dict):
            raise SealError(f"source row {len(result)} must be a JSON object")
        try:
            raw_row = text[start:end].encode("utf-8")
        except UnicodeEncodeError as exc:
            raise SealError(f"source row {len(result)} is not valid UTF-8: {exc}") from exc
        result.append((value, raw_row))
        pos = end
        pos = _skip_json_whitespace(text, pos)
        if pos < length and text[pos] == ",":
            pos += 1
            lookahead = pos
            lookahead = _skip_json_whitespace(text, lookahead)
            if lookahead < length and text[lookahead] == "]":
                raise SealError("source data.json must not contain a trailing array comma")
            continue
        if pos < length and text[pos] == "]":
            pos += 1
            break
        raise SealError(f"source data.json has invalid array separator after row {len(result)-1}")
    pos = _skip_json_whitespace(text, pos)
    if pos != length:
        raise SealError("source data.json has trailing content after its array")
    return result


def validate_source_row(row: dict[str, Any], raw_row: bytes, ordinal: int) -> SourceRow:
    if tuple(row.keys()) != ROW_KEYS:
        raise SealError(f"source row {ordinal} schema/order drift: expected {ROW_KEYS}, got {tuple(row)}")
    for key in ROW_KEYS:
        if not isinstance(row[key], str) or not row[key]:
            raise SealError(f"source row {ordinal} field {key} must be nonempty text")
    if re.fullmatch(r"[0-9a-f]{24}", row["_id"]) is None:
        raise SealError(f"source row {ordinal} has invalid upstream _id")
    if row["difficulty"] not in DIFFICULTIES:
        raise SealError(f"source row {ordinal} has unknown difficulty")
    if row["length"] not in LENGTHS:
        raise SealError(f"source row {ordinal} has unknown length")
    if row["domain"] not in DOMAINS or row["sub_domain"] not in SUB_DOMAINS:
        raise SealError(f"source row {ordinal} has category taxonomy drift")
    if row["answer"] not in CHOICE_LABELS:
        raise SealError(f"source row {ordinal} answer must be one of A/B/C/D")
    payload = {
        "question": row["question"],
        "context": row["context"],
        "choices": {label: row[f"choice_{label}"] for label in CHOICE_LABELS},
    }
    payload_bytes = canonical_json_bytes(payload)
    return SourceRow(
        ordinal=ordinal,
        row=dict(row),
        raw_row_sha256=sha256_bytes(raw_row),
        canonical_row_sha256=sha256_bytes(canonical_json_bytes(row)),
        payload=payload,
        payload_bytes=payload_bytes,
        payload_sha256=sha256_bytes(payload_bytes),
    )


def load_and_validate_source(path: Path) -> tuple[list[SourceRow], dict[str, Any]]:
    data = read_private_file(path, "pinned source data.json")
    expected = SOURCE_FILES["data.json"]
    digest = sha256_bytes(data)
    if len(data) != expected["bytes"] or digest != expected["sha256"]:
        raise SealError(
            f"source data.json drift: expected {expected['bytes']} bytes/{expected['sha256']}, "
            f"got {len(data)} bytes/{digest}"
        )
    pairs = split_top_level_array(data)
    if len(pairs) != EXPECTED_SOURCE_COUNT:
        raise SealError(f"expected exactly {EXPECTED_SOURCE_COUNT} source rows, got {len(pairs)}")
    rows = [validate_source_row(row, raw, ordinal) for ordinal, (row, raw) in enumerate(pairs)]
    ids = [item.row["_id"] for item in rows]
    canonical_hashes = [item.canonical_row_sha256 for item in rows]
    payload_hashes = [item.payload_sha256 for item in rows]
    if len(set(ids)) != len(ids):
        raise SealError("duplicate upstream _id across source rows")
    if len(set(canonical_hashes)) != len(canonical_hashes):
        raise SealError("duplicate canonical source row across source rows")
    if len(set(payload_hashes)) != len(payload_hashes):
        raise SealError("duplicate question/context/choices payload across source rows")
    from collections import Counter
    cells = Counter((item.row["difficulty"], item.row["length"]) for item in rows)
    if dict(cells) != CELL_COUNTS:
        raise SealError(f"difficulty/length cell drift: expected {CELL_COUNTS}, got {dict(cells)}")
    selected = [item for item in rows if item.row["difficulty"] == "hard" and item.row["length"] == "long"]
    if len(selected) != EXPECTED_COUNT:
        raise SealError(f"filter must select exactly {EXPECTED_COUNT} rows, got {len(selected)}")
    domains = Counter(item.row["domain"] for item in selected)
    subs = Counter(item.row["sub_domain"] for item in selected)
    if dict(domains) != SELECTED_DOMAIN_COUNTS:
        raise SealError(f"selected domain cell drift: {dict(domains)}")
    if dict(subs) != SELECTED_SUB_DOMAIN_COUNTS:
        raise SealError(f"selected sub-domain cell drift: {dict(subs)}")
    receipt = {"sha256": digest, "bytes": len(data), "rows": len(rows)}
    return selected, receipt


def load_key(path: Path | None) -> tuple[bytes, str]:
    if path is None:
        key = secrets.token_bytes(32)
    else:
        data = read_private_file(path, "randomization key")
        if len(data) != 32:
            raise SealError("randomization key must contain exactly 32 raw bytes")
        key = data
    return key, sha256_bytes(key)


def fixture_id(key: bytes, row: SourceRow) -> str:
    message = b"\0".join((
        SUITE_ID.encode(), str(row.ordinal).encode(), row.row["_id"].encode(),
        row.canonical_row_sha256.encode(),
    ))
    return "lb2-" + hmac.new(key, message, hashlib.sha256).hexdigest()[:32]


def _mkdir_temp_at(parent: ParentHandle, *, prefix: str) -> tuple[str, int]:
    """Create and open an unpredictable temp directory relative to a held parent."""
    for _ in range(1024):
        name = prefix + secrets.token_hex(12)
        try:
            os.mkdir(name, mode=0o700, dir_fd=parent.fd)
        except FileExistsError:
            continue
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(name, flags, dir_fd=parent.fd)
        except Exception:
            try:
                os.rmdir(name, dir_fd=parent.fd)
            finally:
                raise
        metadata = os.fstat(fd)
        if os.name == "posix":
            os.fchmod(fd, 0o700)
        if not stat.S_ISDIR(metadata.st_mode):
            os.close(fd)
            raise SealError("created temporary entry is not a directory")
        return name, fd
    raise SealError("could not allocate a unique temporary directory")


def _rename_noreplace_at(parent: ParentHandle, source_name: str, target_name: str) -> None:
    """Atomically rename within a held directory fd without replacing target."""
    source_b = os.fsencode(source_name)
    target_b = os.fsencode(target_name)
    libc = ctypes.CDLL(None, use_errno=True)
    if __import__("sys").platform == "darwin":
        renameatx_np = getattr(libc, "renameatx_np", None)
        if renameatx_np is None:
            raise SealError("kernel has no dir-fd atomic no-replace rename primitive")
        renameatx_np.argtypes = (
            ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p,
            ctypes.c_uint,
        )
        renameatx_np.restype = ctypes.c_int
        result = renameatx_np(parent.fd, source_b, parent.fd, target_b, 0x00000004)
    elif __import__("sys").platform.startswith("linux"):
        renameat2 = getattr(libc, "renameat2", None)
        if renameat2 is None:
            raise SealError("kernel has no dir-fd atomic no-replace rename primitive")
        renameat2.argtypes = (
            ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p,
            ctypes.c_uint,
        )
        renameat2.restype = ctypes.c_int
        result = renameat2(parent.fd, source_b, parent.fd, target_b, 1)
    else:
        raise SealError("platform has no supported dir-fd atomic no-replace rename primitive")
    if result != 0:
        error = ctypes.get_errno()
        if error in (errno.EEXIST, errno.ENOTEMPTY):
            raise SealError(
                f"publication target already exists; refusing replacement: {target_name}"
            )
        raise SealError(
            f"atomic no-replace publication failed for {target_name}: {os.strerror(error)}"
        )


def _write_file_at(directory_fd: int, name: str, data: bytes) -> None:
    if not name or "/" in name or name in (".", ".."):
        raise SealError(f"unsafe file name: {name!r}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(name, flags, 0o600, dir_fd=directory_fd)
    try:
        if os.name == "posix":
            os.fchmod(fd, 0o600)
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise SealError(f"short write to {name}")
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)


def _open_directory_at(directory_fd: int, name: str) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    return os.open(name, flags, dir_fd=directory_fd)


def _list_names_fd(directory_fd: int) -> list[str]:
    """Enumerate the directory referenced by an already held fd."""
    return os.listdir(directory_fd)


def _require_exact_names_fd(directory_fd: int, expected: set[str], label: str) -> None:
    entries = _list_names_fd(directory_fd)
    actual = set(entries)
    if len(entries) != len(actual) or actual != expected:
        raise SealError(
            f"{label} inventory drift: expected {sorted(expected)}, got {sorted(actual)}"
        )


def _remove_tree_contents_fd(directory_fd: int) -> None:
    """Recursively unlink entries relative to held, no-follow directory fds."""
    for name in _list_names_fd(directory_fd):
        metadata = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if stat.S_ISDIR(metadata.st_mode):
            child_fd = _open_directory_at(directory_fd, name)
            try:
                _remove_tree_contents_fd(child_fd)
            finally:
                os.close(child_fd)
            os.rmdir(name, dir_fd=directory_fd)
        else:
            os.unlink(name, dir_fd=directory_fd)


def _cleanup_quarantine_hook(parent: ParentHandle, name: str, temp_fd: int) -> None:
    """No-op injection point for deterministic post-rename race tests."""
    del parent, name, temp_fd


def _cleanup_temp_at(parent: ParentHandle, name: str, temp_fd: int) -> None:
    """Quarantine, but never delete, a failed temporary publication tree.

    POSIX has no portable conditional-rmdir-by-inode operation. Even an
    fd-relative ``stat`` immediately followed by ``rmdir(name)`` can delete an
    empty racer directory swapped into that name. Therefore failure cleanup
    never unlinks or removes a temp tree. It atomically moves the expected temp
    to an unpredictable owner-only quarantine name and preserves it for explicit
    operator inspection/removal. If a racer is moved instead, restore it with a
    no-replace rename when possible and preserve it under one of the names in
    every case.
    """
    expected = os.fstat(temp_fd)
    try:
        current = os.stat(name, dir_fd=parent.fd, follow_symlinks=False)
    except FileNotFoundError:
        os.fsync(parent.fd)
        return
    if (
        not stat.S_ISDIR(current.st_mode)
        or (current.st_dev, current.st_ino) != (expected.st_dev, expected.st_ino)
    ):
        os.fsync(parent.fd)
        return

    quarantine = f"{name}.abandoned-{secrets.token_hex(16)}"
    _rename_noreplace_at(parent, name, quarantine)
    os.fsync(parent.fd)
    try:
        moved = os.stat(quarantine, dir_fd=parent.fd, follow_symlinks=False)
    except FileNotFoundError:
        # A same-owner racer moved it again. No deletion is attempted.
        os.fsync(parent.fd)
        return
    _cleanup_quarantine_hook(parent, quarantine, temp_fd)
    if (moved.st_dev, moved.st_ino) != (expected.st_dev, expected.st_ino):
        # We atomically caught a racer between the name check and rename. Put it
        # back only if the original name is still free; no-replace failure also
        # preserves it safely under the quarantine name.
        try:
            _rename_noreplace_at(parent, quarantine, name)
        except SealError:
            pass
    # Deliberately no rmdir/unlink: there is no portable atomic inode-conditional
    # delete. Keeping an owner-only abandoned tree is the fail-closed behavior.
    os.fsync(parent.fd)



def build_sealed_objects(rows: list[SourceRow], key: bytes, key_sha256: str,
                         source_receipt: dict[str, Any], companions: dict[str, Any],
                         lock_sha256: str) -> tuple[dict[str, Any], dict[str, Any], list[tuple[str, bytes]]]:
    public_fixtures: list[dict[str, Any]] = []
    gold_fixtures: list[dict[str, Any]] = []
    payloads: list[tuple[str, bytes]] = []
    seen_ids: set[str] = set()
    for row in rows:
        identity = fixture_id(key, row)
        if identity in seen_ids:
            raise SealError(f"duplicate randomized fixture ID: {identity}")
        seen_ids.add(identity)
        relative = f"payloads/{identity}.json"
        public_fixtures.append({
            "id": identity,
            "domain": row.row["domain"],
            "sub_domain": row.row["sub_domain"],
            "payload": relative,
            "payload_sha256": row.payload_sha256,
            "payload_bytes": len(row.payload_bytes),
        })
        gold_fixtures.append({
            "id": identity,
            "answer": row.row["answer"],
            "source_ordinal": row.ordinal,
            "source_id": row.row["_id"],
            "raw_row_sha256": row.raw_row_sha256,
            "canonical_row_sha256": row.canonical_row_sha256,
            "payload_sha256": row.payload_sha256,
        })
        payloads.append((relative, row.payload_bytes))
    if len(public_fixtures) != EXPECTED_COUNT or len(gold_fixtures) != EXPECTED_COUNT:
        raise SealError(f"sealed suite must contain exactly {EXPECTED_COUNT} fixtures")
    public_identity = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_hard_long_public_manifest",
        "suite_id": SUITE_ID,
        "source": {"name": SOURCE_NAME, "url": SOURCE_URL, "revision": SOURCE_REVISION},
        "configuration": {
            "difficulty": "hard", "length": "long",
            "source_row_count": EXPECTED_SOURCE_COUNT, "fixture_count": EXPECTED_COUNT,
            "payload_schema": ["question", "context", "choices"],
            "choice_labels": list(CHOICE_LABELS),
            "domain_counts": dict(SELECTED_DOMAIN_COUNTS),
            "sub_domain_counts": dict(SELECTED_SUB_DOMAIN_COUNTS),
        },
        "provenance_commitments": {
            "data_json_sha256": SOURCE_FILES["data.json"]["sha256"],
            "readme_sha256": SOURCE_FILES["README.md"]["sha256"],
            "gitattributes_sha256": SOURCE_FILES[".gitattributes"]["sha256"],
            "requirements_lock_sha256": lock_sha256,
            "public_notice_files": {
                name: metadata["sha256"] for name, metadata in PUBLIC_NOTICE_FILES.items()
            },
        },
        "fixtures": public_fixtures,
    }
    identity_sha = sha256_bytes(canonical_json_bytes(public_identity))
    gold = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "lb2_hard_long_gold",
        "suite_id": SUITE_ID,
        "manifest_identity_sha256": identity_sha,
        "fixtures": gold_fixtures,
        "provenance": {
            "source": {
                "name": SOURCE_NAME, "url": SOURCE_URL, "revision": SOURCE_REVISION,
                "files": {"data.json": dict(SOURCE_FILES["data.json"]), **companions},
            },
            "source_file_sha256": source_receipt["sha256"],
            "source_file_bytes": source_receipt["bytes"],
            "source_row_count": source_receipt["rows"],
            "filter": {"difficulty": "hard", "length": "long", "selected_count": EXPECTED_COUNT},
            "randomization_key_sha256": key_sha256,
            "requirements_lock_sha256": lock_sha256,
        },
    }
    return public_identity, gold, payloads


def seal_suite(*, data_path: Path, readme_path: Path, gitattributes_path: Path,
               requirements_lock: Path, out_public: Path, out_gold: Path,
               key_path: Path | None = None) -> tuple[Path, Path]:
    rows, source_receipt = load_and_validate_source(data_path)
    companions = {
        "README.md": validate_pinned_companion(readme_path, "README.md"),
        ".gitattributes": validate_pinned_companion(gitattributes_path, ".gitattributes"),
    }
    lock_sha = validate_requirements_lock(requirements_lock)
    notice_files = load_public_notice_files()
    key, key_sha = load_key(key_path)
    public_identity, gold, payloads = build_sealed_objects(
        rows, key, key_sha, source_receipt, companions, lock_sha
    )
    public_requested = out_public.expanduser()
    gold_requested = out_gold.expanduser()
    if public_requested.name in ("", ".", "..") or gold_requested.name in ("", ".", ".."):
        raise SealError("output roots must have safe final path components")

    public_parent = open_private_parent(public_requested, "public output parent")
    gold_parent: ParentHandle | None = None
    public_temp_name: str | None = None
    gold_temp_name: str | None = None
    public_temp_fd: int | None = None
    gold_temp_fd: int | None = None
    payload_fd: int | None = None
    gold_published = False
    public_published = False
    try:
        gold_parent = open_private_parent(gold_requested, "gold output parent")
        public_target = public_parent.path / public_requested.name
        gold_target = gold_parent.path / gold_requested.name
        if (
            public_target == gold_target
            or public_target in gold_target.parents
            or gold_target in public_target.parents
        ):
            raise SealError("public and gold outputs must be separately rooted, non-nested paths")
        _verify_parent_handle(public_parent, "public output parent")
        _verify_parent_handle(gold_parent, "gold output parent")

        public_temp_name, public_temp_fd = _mkdir_temp_at(
            public_parent, prefix=f".{public_requested.name}.tmp-"
        )
        gold_temp_name, gold_temp_fd = _mkdir_temp_at(
            gold_parent, prefix=f".{gold_requested.name}.tmp-"
        )
        os.mkdir("payloads", mode=0o700, dir_fd=public_temp_fd)
        payload_fd = _open_directory_at(public_temp_fd, "payloads")
        if os.name == "posix":
            os.fchmod(payload_fd, 0o700)
        for relative, content in payloads:
            relative_path = Path(relative)
            if relative_path.parent != Path("payloads"):
                raise SealError(f"unsafe derived payload path: {relative}")
            _write_file_at(payload_fd, relative_path.name, content)
        for name, content in notice_files:
            _write_file_at(public_temp_fd, name, content)

        gold_bytes = canonical_json_bytes(gold)
        manifest = dict(public_identity)
        manifest["gold_sha256"] = sha256_bytes(gold_bytes)
        manifest_bytes = canonical_json_bytes(manifest)
        identity = dict(manifest)
        del identity["gold_sha256"]
        if sha256_bytes(canonical_json_bytes(identity)) != gold["manifest_identity_sha256"]:
            raise SealError("internal manifest identity commitment mismatch")
        if sha256_bytes(gold_bytes) != manifest["gold_sha256"]:
            raise SealError("internal gold byte commitment mismatch")
        _write_file_at(public_temp_fd, "manifest.json", manifest_bytes)
        _write_file_at(gold_temp_fd, "gold.json", gold_bytes)

        expected_payloads = {Path(relative).name for relative, _ in payloads}
        _require_exact_names_fd(payload_fd, expected_payloads, "public payload directory")
        _require_exact_names_fd(
            public_temp_fd,
            {"manifest.json", "payloads", *PUBLIC_NOTICE_FILES},
            "public sealed root",
        )
        _require_exact_names_fd(gold_temp_fd, {"gold.json"}, "gold sealed root")
        os.fsync(payload_fd)
        os.fsync(public_temp_fd)
        os.fsync(gold_temp_fd)

        # Verify the user-visible parent names still bind to our held directory
        # fds, then publish by fd-relative, kernel no-replace rename. A swap
        # either fails verification or is irrelevant to the held directory.
        _verify_parent_handle(gold_parent, "gold output parent")
        _rename_noreplace_at(gold_parent, gold_temp_name, gold_requested.name)
        gold_published = True
        gold_temp_name = None
        os.fsync(gold_parent.fd)

        _verify_parent_handle(public_parent, "public output parent")
        _rename_noreplace_at(public_parent, public_temp_name, public_requested.name)
        public_published = True
        public_temp_name = None
        os.fsync(public_parent.fd)
    finally:
        if payload_fd is not None:
            os.close(payload_fd)
        cleanup_error: Exception | None = None
        for parent, name, temp_fd in (
            (public_parent, public_temp_name, public_temp_fd),
            (gold_parent, gold_temp_name, gold_temp_fd),
        ):
            if parent is not None and name is not None and temp_fd is not None:
                try:
                    _cleanup_temp_at(parent, name, temp_fd)
                except Exception as exc:
                    cleanup_error = cleanup_error or exc
            if temp_fd is not None:
                os.close(temp_fd)
        if gold_parent is not None:
            _close_parent_handles(public_parent, gold_parent)
        else:
            _close_parent_handles(public_parent)
        if cleanup_error is not None:
            raise cleanup_error
    if not (gold_published and public_published):
        raise SealError("internal publication state did not reach its public commit point")
    return public_target / "manifest.json", gold_target / "gold.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, help="owner-only pinned data.json")
    parser.add_argument("--readme", required=True, help="pinned upstream README.md")
    parser.add_argument("--gitattributes", required=True, help="pinned upstream .gitattributes")
    parser.add_argument("--requirements-lock", default=str(Path(__file__).with_name("requirements.lock")))
    parser.add_argument("--out-public", required=True, help="fresh inference-safe output root")
    parser.add_argument("--out-gold", required=True, help="fresh separately rooted owner-only gold root")
    parser.add_argument("--randomization-key", help="optional owner-only file of exactly 32 raw random bytes")
    parser.add_argument("--difficulty", default="hard")
    parser.add_argument("--length", default="long")
    parser.add_argument("--expected-count", default=EXPECTED_COUNT, type=int)
    parser.add_argument("--yes-seal", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if not args.yes_seal:
            raise SealError("refusing to seal without --yes-seal")
        if (args.difficulty, args.length, args.expected_count) != ("hard", "long", EXPECTED_COUNT):
            raise SealError("suite design is frozen to difficulty=hard, length=long, count=63")
        manifest, gold = seal_suite(
            data_path=Path(args.data), readme_path=Path(args.readme),
            gitattributes_path=Path(args.gitattributes),
            requirements_lock=Path(args.requirements_lock),
            out_public=Path(args.out_public), out_gold=Path(args.out_gold),
            key_path=Path(args.randomization_key) if args.randomization_key else None,
        )
        print(json.dumps({"manifest": str(manifest), "gold": str(gold)}, sort_keys=True))
        return 0
    except (SealError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
