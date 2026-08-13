#!/usr/bin/env python3
"""Create and seal the private ``ruler-exact-mini-v1`` fixture suite.

This module never performs inference. ``plan`` creates the procedural secret seed
plan. ``build`` runs the official pinned RULER generator only from an archived
clean commit, validates every generated row, and publishes an inference-safe
public suite only after its separate owner-only gold receipt is durable.
"""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import hmac
import importlib.metadata
import io
import json
import os
import platform
import re
import secrets
import shlex
import shutil
import stat
import subprocess
import tarfile
import zipfile
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SUITE_ID = "ruler-exact-mini-v1"
SCHEMA_VERSION = 1
RULER_URL = "https://github.com/NVIDIA/RULER.git"
RULER_COMMIT = "c3f5e3b4f87f97e048793bb510a3a6b19a46bf3a"
TASKS = ("niah_multikey_3", "vt", "fwe")
LENGTHS = (8192, 32768, 131072)
POOL_SIZE = 100
PER_CELL = 10
TOKENIZER = "cl100k_base"
TOKENIZER_BLOB_SHA256 = "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"
TOKENIZER_CACHE_NAME = "9b5ad71b2ce5302211f9c61530b329a4922fc6a4"
NLTK_RESOURCE_HASHES = {
    "tokenizers/punkt.zip": "51c3078994aeaf650bfc8e028be4fb42b4a0d177d41c012b6a983979653660ec",
    "tokenizers/punkt_tab.zip": "e57f64187974277726a3417ca6f181ec5403676c717672eef6a748a7b20e0106",
}
REQUIREMENTS_LOCK_SHA256 = "82d442a1cffdf8bf5b2d9e27f9e6432f3b3328f6813bf4086499d68bbb1ba1c9"
THIRD_PARTY_NOTICES_SHA256 = "c5356d79adccad2264910a9df17792ed10fb1d452444ec2a8a96c1691f8152b2"
SOURCE_HASHES = {
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
LOCKED_VERSIONS = {
    "certifi": "2026.7.22",
    "charset-normalizer": "3.5.0",
    "click": "8.4.2",
    "idna": "3.18",
    "joblib": "1.5.3",
    "nltk": "3.9.2",
    "numpy": "2.3.5",
    "PyYAML": "6.0.3",
    "regex": "2026.7.19",
    "requests": "2.34.2",
    "scipy": "1.16.3",
    "tenacity": "9.1.2",
    "tiktoken": "0.12.0",
    "tqdm": "4.67.1",
    "urllib3": "2.7.0",
    "wonderwords": "3.0.1",
}


@dataclass(frozen=True)
class TaskSpec:
    reserve: int
    cardinality: int
    output_pattern: re.Pattern[str]


TASK_SPECS = {
    "niah_multikey_3": TaskSpec(
        128,
        1,
        re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"),
    ),
    "vt": TaskSpec(30, 5, re.compile(r"[A-Z]{5}")),
    "fwe": TaskSpec(50, 3, re.compile(r"[a-z]{6}")),
}


class SealError(RuntimeError):
    """A fail-closed suite-generation error."""


@dataclass(frozen=True)
class PoolRow:
    ordinal: int
    row: dict[str, Any]
    raw_row_sha256: str
    raw_row_utf8: str
    canonical_row_sha256: str
    payload: str
    payload_bytes: bytes
    payload_sha256: str
    construction_tokens: int
    row_length: int
    outputs: tuple[str, ...]
    token_position_answer: int | None


def canonical_json_bytes(value: Any) -> bytes:
    """Canonical encoding used by every receipt and cross-file commitment."""
    try:
        return (
            json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            + "\n"
        ).encode("utf-8")
    except (UnicodeEncodeError, TypeError, ValueError) as exc:
        raise SealError(f"value cannot be encoded as canonical UTF-8 JSON: {exc}") from exc


def strict_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(strict_equal(left[key], right[key]) for key in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(strict_equal(a, b) for a, b in zip(left, right))
    return bool(left == right)


def validate_unicode_scalars(value: Any, label: str) -> None:
    if isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise SealError(f"{label} contains a lone Unicode surrogate") from exc
    elif isinstance(value, dict):
        for key, child in value.items():
            validate_unicode_scalars(key, label)
            validate_unicode_scalars(child, label)
    elif isinstance(value, list):
        for child in value:
            validate_unicode_scalars(child, label)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
                raise SealError(f"{label} must be owned by the current user: {path}")
            if _mode(st) != 0o600:
                raise SealError(
                    f"{label} mode must be 0600, got {_mode(st):04o}: {path}"
                )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def read_regular_file(path: Path, label: str) -> bytes:
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
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise SealError(f"cannot open directory for fsync {path}: {exc}") from exc
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def rename_directory_noreplace(source: Path, target: Path) -> None:
    """Atomically publish a directory without replacing any raced target."""
    libc = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(source)
    target_bytes = os.fsencode(target)
    if sys.platform == "darwin":
        rename = getattr(libc, "renamex_np", None)
        if rename is None:
            raise SealError("renamex_np(RENAME_EXCL) is unavailable")
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        result = rename(source_bytes, target_bytes, 0x00000004)  # RENAME_EXCL
    elif sys.platform.startswith("linux"):
        rename = getattr(libc, "renameat2", None)
        if rename is None:
            raise SealError("renameat2(RENAME_NOREPLACE) is unavailable")
        rename.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        rename.restype = ctypes.c_int
        result = rename(-100, source_bytes, -100, target_bytes, 1)  # AT_FDCWD, RENAME_NOREPLACE
    else:
        raise SealError(f"no atomic no-replace directory rename for platform {sys.platform}")
    if result != 0:
        error = ctypes.get_errno()
        if error == errno.EEXIST:
            raise SealError(f"sealed public output raced into existence: {target}")
        raise SealError(f"cannot atomically publish public directory {target}: {os.strerror(error)}")


def require_posix_security() -> None:
    if os.name != "posix":
        raise SealError("suite generation is supported only on POSIX owner/mode filesystems")
    if sys.platform != "darwin" and not sys.platform.startswith("linux"):
        raise SealError("atomic no-replace publication is supported only on Darwin and Linux")
    for primitive in ("O_NOFOLLOW", "O_DIRECTORY"):
        if not hasattr(os, primitive):
            raise SealError(f"required POSIX security primitive os.{primitive} is unavailable")


def ensure_private_parent(path: Path) -> Path:
    require_posix_security()
    parent = path.expanduser().absolute().parent
    if not parent.exists():
        raise SealError(
            f"output parent must already exist as an owner-only 0700 directory: {parent}"
        )
    return require_private_dir(parent, "output parent")


def write_exclusive_private(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
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


def atomic_publish_private_file(path: Path, data: bytes) -> None:
    parent = ensure_private_parent(path)
    target = parent / path.name
    if os.path.lexists(target):
        raise SealError(f"output already exists; refusing overwrite: {target}")
    temporary = parent / f".{target.name}.tmp-{secrets.token_hex(16)}"
    try:
        write_exclusive_private(temporary, data)
        # Hard-link publication is atomic and fails if a racing target appeared.
        os.link(temporary, target, follow_symlinks=False)
        os.unlink(temporary)
        fsync_directory(parent)
    except Exception:
        try:
            if os.path.lexists(temporary):
                os.unlink(temporary)
        finally:
            pass
        raise


def _derive(key: bytes, *parts: object) -> bytes:
    message = b"\0".join(str(part).encode("utf-8") for part in parts)
    return hmac.new(key, message, hashlib.sha256).digest()


def _generator_seed(master_key: bytes, task: str, target_length: int) -> int:
    return int.from_bytes(
        _derive(master_key, SUITE_ID, "generator", task, target_length)[:4], "big"
    )


def build_plan(master_key: bytes) -> dict[str, Any]:
    if len(master_key) != 32:
        raise SealError("master key must be exactly 32 bytes")
    cells: list[dict[str, Any]] = []
    for target_length in LENGTHS:
        for task in TASKS:
            seed = _generator_seed(master_key, task, target_length)
            if seed in (0, 42):
                raise SealError("derived a forbidden generator seed; create a fresh plan")
            cells.append(
                {
                    "task": task,
                    "target_length": target_length,
                    "generator_seed": seed,
                }
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": "ruler_exact_mini_generation_plan",
        "suite_id": SUITE_ID,
        "master_key_hex": master_key.hex(),
        "cells": cells,
    }


def validate_plan(value: Any) -> tuple[dict[str, Any], bytes]:
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "record_type",
        "suite_id",
        "master_key_hex",
        "cells",
    }:
        raise SealError("generation plan has an unexpected object shape")
    if value["schema_version"] != SCHEMA_VERSION:
        raise SealError("generation plan schema_version must be 1")
    if value["record_type"] != "ruler_exact_mini_generation_plan":
        raise SealError("generation plan record_type is wrong")
    if value["suite_id"] != SUITE_ID:
        raise SealError("generation plan suite_id is wrong")
    raw_key = value["master_key_hex"]
    if not isinstance(raw_key, str) or not re.fullmatch(r"[0-9a-f]{64}", raw_key):
        raise SealError("generation plan master_key_hex must be 32-byte lowercase hex")
    master_key = bytes.fromhex(raw_key)
    expected = build_plan(master_key)
    if not strict_equal(value, expected):
        raise SealError("generation plan cells or derived seeds were changed")
    return value, master_key


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def _pairs_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json_object(data: bytes, label: str) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
        value = json.loads(
            text, object_pairs_hook=_pairs_object, parse_constant=_reject_constant
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SealError(f"invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise SealError(f"{label} must be a JSON object")
    validate_unicode_scalars(value, label)
    return value


def load_plan(path: Path) -> tuple[dict[str, Any], bytes, str]:
    data = read_private_file(path, "generation plan")
    value = parse_json_object(data, "generation plan JSON")
    plan, master_key = validate_plan(value)
    if data != canonical_json_bytes(plan):
        raise SealError("generation plan must use the canonical JSON encoding")
    return plan, master_key, sha256_bytes(data)


def validate_official_task_text(
    *,
    task: str,
    target_length: int,
    ordinal: int,
    prompt: str,
    answer_prefix: str,
    outputs: list[str],
) -> None:
    label = f"{task}/{target_length} row {ordinal}"
    if task == "niah_multikey_3":
        match = re.fullmatch(
            r" The special magic uuid for "
            r"([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}) "
            r"mentioned in the provided text is",
            answer_prefix,
        )
        if match is None:
            raise SealError(f"{label}: answer_prefix is not the frozen NIAH prefix")
        query = match.group(1)
        required_start = (
            "A special magic uuid is hidden within the following text. "
            "Make sure to memorize it. I will quiz you about the uuid afterwards.\n"
        )
        required_end = (
            f"\nWhat is the special magic uuid for {query} mentioned in the provided text?"
        )
        if not prompt.startswith(required_start) or not prompt.endswith(required_end):
            raise SealError(f"{label}: input is not the frozen NIAH prompt template")
        if prompt.count(query) < 2:
            raise SealError(f"{label}: NIAH query is not represented in context and question")
    elif task == "vt":
        match = re.fullmatch(
            r" Answer: According to the chain\(s\) of variable assignment in the text above, "
            r"5 variables are assigned the value ([0-9]{5}), they are: ",
            answer_prefix,
        )
        if match is None:
            raise SealError(f"{label}: answer_prefix is not the frozen VT 1-chain/4-hop prefix")
        query = match.group(1)
        required_start = (
            "Memorize and track the chain(s) of variable assignment hidden in the following text.\n\n"
        )
        required_end = (
            f"\nQuestion: Find all variables that are assigned the value {query} in the text above."
        )
        if not prompt.startswith(required_start) or not prompt.endswith(required_end):
            raise SealError(f"{label}: input is not the frozen VT prompt template")
        if any(re.search(rf"\b{re.escape(value)}\b", prompt) is None for value in outputs):
            raise SealError(f"{label}: VT gold variables are absent from the assignment text")
    else:
        required_start = (
            "Read the following coded text and track the frequency of each coded word. "
            "Find the three most frequently appeared coded words. "
        )
        required_end = (
            "\nQuestion: Do not provide any explanation. Please ignore the dots '....'. "
            "What are the three most frequently appeared words in the above coded text?"
        )
        expected_prefix = (
            " Answer: According to the coded text above, the three most frequently appeared words are:"
        )
        if (
            answer_prefix != expected_prefix
            or not prompt.startswith(required_start)
            or not prompt.endswith(required_end)
        ):
            raise SealError(f"{label}: input/prefix is not the frozen FWE alpha-2.0 task template")
        context = prompt[len(required_start) : -len(required_end)]
        words = context.split()
        if not words or any(
            word != "..." and re.fullmatch(r"[a-z]{6}", word) is None
            for word in words
        ):
            raise SealError(f"{label}: FWE coded context has an invalid token")
        counts: dict[str, int] = {}
        for word in words:
            if word != "...":
                counts[word] = counts.get(word, 0) + 1
        if any(counts.get(value, 0) == 0 for value in outputs):
            raise SealError(f"{label}: FWE gold words are absent from the coded text")
        output_counts = [counts[value] for value in outputs]
        remaining = [count for word, count in counts.items() if word not in outputs]
        if not (output_counts[0] > output_counts[1] > output_counts[2]):
            raise SealError(f"{label}: FWE outputs are not in strict frequency order")
        if remaining and output_counts[-1] <= max(remaining):
            raise SealError(f"{label}: FWE outputs are not exactly the top three words")


def validate_row(
    row: dict[str, Any],
    *,
    raw_bytes: bytes,
    ordinal: int,
    task: str,
    target_length: int,
    encoding: Any,
) -> PoolRow:
    spec = TASK_SPECS[task]
    expected_keys = {
        "index",
        "input",
        "outputs",
        "length",
        "length_w_model_temp",
        "answer_prefix",
    }
    if task == "niah_multikey_3":
        expected_keys.add("token_position_answer")
    if set(row) != expected_keys:
        raise SealError(
            f"{task}/{target_length} row {ordinal}: exact row keys changed; "
            f"expected {sorted(expected_keys)}, got {sorted(row)}"
        )
    upstream_index = row.get("index")
    if type(upstream_index) is not int:
        raise SealError(f"{task}/{target_length} row {ordinal}: index must be an integer")
    if task != "niah_multikey_3" and upstream_index != ordinal:
        raise SealError(
            f"{task}/{target_length} row {ordinal}: upstream index must equal line ordinal"
        )
    prompt = row.get("input")
    answer_prefix = row.get("answer_prefix")
    outputs = row.get("outputs")
    length = row.get("length")
    templated_length = row.get("length_w_model_temp")
    if not isinstance(prompt, str) or not prompt:
        raise SealError(f"{task}/{target_length} row {ordinal}: input must be nonempty text")
    if not isinstance(answer_prefix, str) or not answer_prefix:
        raise SealError(
            f"{task}/{target_length} row {ordinal}: answer_prefix must be nonempty text"
        )
    if not isinstance(outputs, list) or len(outputs) != spec.cardinality:
        raise SealError(
            f"{task}/{target_length} row {ordinal}: outputs must have cardinality {spec.cardinality}"
        )
    checked_outputs: list[str] = []
    for output in outputs:
        if not isinstance(output, str) or spec.output_pattern.fullmatch(output) is None:
            raise SealError(
                f"{task}/{target_length} row {ordinal}: invalid task-domain output {output!r}"
            )
        checked_outputs.append(output)
    if len(set(checked_outputs)) != len(checked_outputs):
        raise SealError(f"{task}/{target_length} row {ordinal}: duplicate outputs")
    validate_official_task_text(
        task=task,
        target_length=target_length,
        ordinal=ordinal,
        prompt=prompt,
        answer_prefix=answer_prefix,
        outputs=checked_outputs,
    )
    if type(length) is not int or length <= 0 or length > target_length:
        raise SealError(f"{task}/{target_length} row {ordinal}: invalid row length")
    if type(templated_length) is not int or templated_length != length:
        raise SealError(
            f"{task}/{target_length} row {ordinal}: length_w_model_temp must equal length"
        )
    payload = prompt + answer_prefix
    try:
        payload_bytes = payload.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise SealError(
            f"{task}/{target_length} row {ordinal}: payload is not valid UTF-8"
        ) from exc
    if not payload_bytes:
        raise SealError(f"{task}/{target_length} row {ordinal}: empty payload")
    try:
        construction_tokens = len(encoding.encode(payload))
    except Exception as exc:
        raise SealError(
            f"{task}/{target_length} row {ordinal}: tokenizer failed: {exc}"
        ) from exc
    if construction_tokens + spec.reserve != length:
        raise SealError(
            f"{task}/{target_length} row {ordinal}: exact payload token count "
            f"{construction_tokens} + reserve {spec.reserve} != row length {length}"
        )
    position: int | None = None
    if task == "niah_multikey_3":
        raw_position = row.get("token_position_answer")
        answer_index = prompt.find(checked_outputs[0])
        if (
            type(raw_position) is not int
            or not 0 <= raw_position < length
            or row["index"] != answer_index
            or answer_index < 0
            or prompt.count(checked_outputs[0]) != 1
        ):
            raise SealError(
                f"{task}/{target_length} row {ordinal}: invalid answer index/position identity"
            )
        try:
            computed_position = len(encoding.encode(prompt[:answer_index]))
        except Exception as exc:
            raise SealError(
                f"{task}/{target_length} row {ordinal}: answer-position tokenization failed: {exc}"
            ) from exc
        if raw_position != computed_position:
            raise SealError(
                f"{task}/{target_length} row {ordinal}: token_position_answer mismatch"
            )
        position = raw_position
    canonical_row = canonical_json_bytes(row)
    return PoolRow(
        ordinal=ordinal,
        row=row,
        raw_row_sha256=sha256_bytes(raw_bytes),
        raw_row_utf8=raw_bytes.decode("utf-8"),
        canonical_row_sha256=sha256_bytes(canonical_row),
        payload=payload,
        payload_bytes=payload_bytes,
        payload_sha256=sha256_bytes(payload_bytes),
        construction_tokens=construction_tokens,
        row_length=length,
        outputs=tuple(checked_outputs),
        token_position_answer=position,
    )


def parse_pool_cell_bytes(
    data: bytes, task: str, target_length: int, encoding: Any
) -> list[PoolRow]:
    if not data.endswith(b"\n") or b"\r" in data:
        raise SealError(f"{task}/{target_length}: pool JSONL must use final LF lines")
    raw_lines = data[:-1].split(b"\n")
    if len(raw_lines) != POOL_SIZE or any(not line for line in raw_lines):
        raise SealError(
            f"{task}/{target_length}: expected exactly {POOL_SIZE} nonempty rows, "
            f"found {len(raw_lines)}"
        )
    result: list[PoolRow] = []
    for ordinal, raw_line in enumerate(raw_lines):
        row = parse_json_object(raw_line, f"{task}/{target_length} row {ordinal}")
        result.append(
            validate_row(
                row,
                raw_bytes=raw_line,
                ordinal=ordinal,
                task=task,
                target_length=target_length,
                encoding=encoding,
            )
        )
    return result


def read_pool_cell_bytes(pool_root: Path, task: str, target_length: int) -> bytes:
    length_dir = pool_root / str(target_length)
    task_dir = length_dir / task
    require_private_dir(length_dir, f"pool length directory {target_length}")
    require_private_dir(task_dir, f"pool task directory {task}/{target_length}")
    return read_private_file(task_dir / "test.jsonl", f"pool JSONL {task}/{target_length}")


def load_pool_cell(
    pool_root: Path, task: str, target_length: int, encoding: Any
) -> list[PoolRow]:
    return parse_pool_cell_bytes(
        read_pool_cell_bytes(pool_root, task, target_length), task, target_length, encoding
    )


def select_rows(
    rows: list[PoolRow], task: str, target_length: int, master_key: bytes
) -> list[tuple[PoolRow, dict[str, Any]]]:
    if len(rows) != POOL_SIZE:
        raise SealError(f"selection requires exactly {POOL_SIZE} rows")
    cell_key = _derive(master_key, SUITE_ID, "selection", task, target_length)
    selected: list[tuple[PoolRow, dict[str, Any]]] = []
    if task == "niah_multikey_3":
        ordered = sorted(
            rows,
            key=lambda item: (
                item.token_position_answer
                if item.token_position_answer is not None
                else -1,
                item.ordinal,
            ),
        )
        for decile in range(PER_CELL):
            bucket = ordered[decile * 10 : (decile + 1) * 10]
            ranked = sorted(
                bucket,
                key=lambda item: _derive(cell_key, "decile", decile, item.ordinal),
            )
            picked = ranked[0]
            selected.append(
                (
                    picked,
                    {
                        "method": "answer_position_decile_hmac_rank",
                        "decile": decile,
                        "hmac_rank_sha256": _derive(
                            cell_key, "decile", decile, picked.ordinal
                        ).hex(),
                    },
                )
            )
    else:
        ranked = sorted(
            rows,
            key=lambda item: _derive(cell_key, "ordinal", item.ordinal),
        )[:PER_CELL]
        for picked in ranked:
            selected.append(
                (
                    picked,
                    {
                        "method": "ordinal_hmac_rank",
                        "hmac_rank_sha256": _derive(
                            cell_key, "ordinal", picked.ordinal
                        ).hex(),
                    },
                )
            )
    if len({item.ordinal for item, _ in selected}) != PER_CELL:
        raise SealError(f"{task}/{target_length}: deterministic selection duplicated a row")
    return selected


def fixture_id(
    master_key: bytes, task: str, target_length: int, row: PoolRow
) -> str:
    digest = _derive(
        master_key,
        SUITE_ID,
        "fixture-id",
        task,
        target_length,
        row.ordinal,
        row.raw_row_sha256,
    )
    return "rxm-" + digest[:16].hex()


def _run_git(source: Path, arguments: list[str], *, binary: bool = False) -> subprocess.CompletedProcess[Any]:
    env = {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C",
        "LANG": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "HOME": "/nonexistent-ruler-build-home",
        "XDG_CONFIG_HOME": "/nonexistent-ruler-build-home",
    }
    try:
        return subprocess.run(
            [
                "git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
                "-c", "core.untrackedCache=false", "-C", str(source), *arguments,
            ],
            check=True,
            capture_output=True,
            text=not binary,
            timeout=120,
            env=env,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise SealError(f"cannot verify pinned RULER Git source ({' '.join(arguments)}): {exc}") from exc


def validate_source(source: Path) -> dict[str, Any]:
    require_posix_security()
    if source.is_symlink():
        raise SealError(f"RULER source must not be a symlink: {source}")
    source = source.resolve(strict=True)
    if not stat.S_ISDIR(source.stat().st_mode):
        raise SealError(f"RULER source must be a directory: {source}")
    commit = _run_git(source, ["rev-parse", "--verify", "HEAD^{commit}"]).stdout.strip()
    if commit != RULER_COMMIT:
        raise SealError(f"RULER commit mismatch: expected {RULER_COMMIT}, got {commit}")
    tree_records = _run_git(
        source, ["ls-tree", "-r", "-z", "--full-tree", RULER_COMMIT], binary=True
    ).stdout.split(b"\0")
    if any(record.startswith(b"160000 commit ") for record in tree_records if record):
        raise SealError("RULER pinned commit must not contain Git submodule/gitlink entries")
    actual: dict[str, str] = {}
    for relative, expected in SOURCE_HASHES.items():
        data = read_regular_file(source / relative, f"RULER source {relative}")
        digest = sha256_bytes(data)
        if digest != expected:
            raise SealError(
                f"RULER source hash mismatch for {relative}: expected {expected}, got {digest}"
            )
        actual[relative] = digest
    # Compare the entire worktree to the pinned archive without invoking `git status`;
    # repository-local fsmonitor/config hooks therefore cannot execute.
    with tempfile.TemporaryDirectory(prefix="ruler-clean-check-") as clean_name:
        clean_root = Path(clean_name)
        clean_root.chmod(0o700)
        snapshot = extract_pinned_source_archive(source, clean_root / "snapshot")
        require_exact_worktree(source, snapshot)
    return {"url": RULER_URL, "commit": commit, "files": actual}


def extract_pinned_source_archive(source: Path, destination: Path) -> Path:
    """Materialize only the pinned commit; never execute the supplied worktree."""
    require_private_dir(destination.parent, "archive scratch parent")
    destination.mkdir(mode=0o700)
    archive = _run_git(source, ["archive", "--format=tar", RULER_COMMIT], binary=True).stdout
    seen: set[str] = set()
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
            for member in bundle.getmembers():
                name = member.name
                pure = Path(name)
                if (
                    not name
                    or pure.is_absolute()
                    or ".." in pure.parts
                    or name in seen
                    or not (member.isdir() or member.isfile())
                ):
                    raise SealError(f"unsafe or unsupported member in pinned Git archive: {name!r}")
                seen.add(name)
                target = destination / pure
                if member.isdir():
                    target.mkdir(mode=0o700, parents=True, exist_ok=True)
                    target.chmod(0o700)
                    continue
                target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                extracted = bundle.extractfile(member)
                if extracted is None:
                    raise SealError(f"cannot extract pinned Git archive member: {name}")
                write_exclusive_private(target, extracted.read())
                target.chmod(0o700 if member.mode & 0o111 else 0o600)
    except (tarfile.TarError, OSError) as exc:
        raise SealError(f"cannot materialize pinned RULER Git archive: {exc}") from exc
    for relative, expected in SOURCE_HASHES.items():
        actual = sha256_bytes(read_regular_file(destination / relative, f"archived RULER {relative}"))
        if actual != expected:
            raise SealError(f"archived RULER source hash mismatch for {relative}")
    if (destination / ".gitmodules").exists():
        raise SealError("RULER pinned archive unexpectedly declares submodules")
    return destination


def _tree_inventory(root: Path, *, exclude_git: bool) -> dict[str, tuple[str, str | None, bool | None]]:
    inventory: dict[str, tuple[str, str | None, bool | None]] = {}
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            entries = list(os.scandir(directory))
        except OSError as exc:
            raise SealError(f"cannot inventory RULER tree {directory}: {exc}") from exc
        for entry in entries:
            path = Path(entry.path)
            relative = path.relative_to(root).as_posix()
            if exclude_git and relative == ".git":
                continue
            try:
                st = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise SealError(f"cannot stat RULER tree entry {path}: {exc}") from exc
            if stat.S_ISDIR(st.st_mode):
                inventory[relative] = ("dir", None, None)
                pending.append(path)
            elif stat.S_ISREG(st.st_mode):
                inventory[relative] = (
                    "file",
                    sha256_bytes(read_regular_file(path, f"RULER tree entry {relative}")),
                    bool(st.st_mode & 0o111),
                )
            else:
                raise SealError(f"RULER tree contains unsupported symlink/special entry: {relative}")
    return inventory


def require_exact_worktree(source: Path, archived_snapshot: Path) -> None:
    worktree = _tree_inventory(source, exclude_git=True)
    archived = _tree_inventory(archived_snapshot, exclude_git=False)
    if worktree != archived:
        extra = sorted(set(worktree) - set(archived))[:3]
        missing = sorted(set(archived) - set(worktree))[:3]
        changed = sorted(
            name for name in set(worktree) & set(archived) if worktree[name] != archived[name]
        )[:3]
        raise SealError(
            "RULER worktree must exactly match the pinned archive (no dirty, untracked, "
            f"submodule, symlink, or mode changes); extra={extra}, missing={missing}, changed={changed}"
        )


def require_isolated_runtime() -> None:
    require_posix_security()
    if not sys.flags.isolated or not sys.flags.no_site or not sys.flags.dont_write_bytecode:
        raise SealError(
            "plan/build must be launched with the exact CPython flags -I -S -B"
        )
    if os.environ.get("PYTHONPATH") or os.environ.get("PYTHONHOME"):
        raise SealError("PYTHONPATH and PYTHONHOME must be unset for pinned generation")
    if any("site-packages" in entry or "dist-packages" in entry for entry in sys.path):
        raise SealError("unverified site-packages is present in the isolated builder path")


def _normalized_distribution(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _lock_hashes(lock_data: bytes) -> dict[str, tuple[str, set[str]]]:
    try:
        text = lock_data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SealError(f"requirements lock is not UTF-8: {exc}") from exc
    result: dict[str, tuple[str, set[str]]] = {}
    current: str | None = None
    current_version: str | None = None
    hashes: set[str] = set()

    def finish() -> None:
        nonlocal current, current_version, hashes
        if current is not None and current_version is not None:
            result[current] = (current_version, set(hashes))
        current = None
        current_version = None
        hashes = set()

    for line in text.splitlines():
        match = re.match(r"^([A-Za-z0-9_.-]+)==([^ ;\\]+)", line)
        if match:
            finish()
            current = _normalized_distribution(match.group(1))
            current_version = match.group(2)
        for digest in re.findall(r"--hash=sha256:([0-9a-f]{64})", line):
            hashes.add(digest)
    finish()
    return result


def _wheel_supported(filename: str) -> bool:
    if filename.endswith("-py3-none-any.whl"):
        return True
    if "-cp311-cp311-" not in filename:
        return False
    lowered = filename.lower()
    machine = platform.machine().lower()
    if platform.system() == "Darwin":
        return "macosx_" in lowered and (
            lowered.endswith(f"_{machine}.whl") or lowered.endswith("_universal2.whl")
        )
    if platform.system() == "Linux":
        aliases = {"x86_64": ("x86_64",), "aarch64": ("aarch64",), "arm64": ("aarch64",)}
        return ("manylinux" in lowered or "linux_" in lowered) and any(
            lowered.endswith(f"_{suffix}.whl") for suffix in aliases.get(machine, (machine,))
        )
    return False


def validate_dependencies(
    lock: Path, wheelhouse: Path, tokenizer_cache_dir: Path, nltk_data: Path
) -> dict[str, Any]:
    require_isolated_runtime()
    if sys.version_info[:2] != (3, 11) or platform.python_implementation() != "CPython":
        raise SealError(
            f"generation requires CPython 3.11, got "
            f"{platform.python_implementation()} {platform.python_version()}"
        )
    venv_root = Path(sys.executable).resolve().parent.parent
    # sys.executable itself may be a venv symlink; use its lexical parent first.
    lexical_venv_root = Path(sys.executable).absolute().parent.parent
    if not (lexical_venv_root / "pyvenv.cfg").is_file():
        raise SealError("isolated generation must use a dedicated virtual-environment executable")
    lock_data = read_regular_file(lock, "requirements lock")
    lock_digest = sha256_bytes(lock_data)
    if lock_digest != REQUIREMENTS_LOCK_SHA256:
        raise SealError(
            f"requirements lock mismatch: expected {REQUIREMENTS_LOCK_SHA256}, got {lock_digest}"
        )
    parsed_lock = _lock_hashes(lock_data)
    wheelhouse = require_private_dir(wheelhouse, "hash-locked wheelhouse")
    entries = list(os.scandir(wheelhouse))
    if any(entry.is_symlink() or not entry.is_file(follow_symlinks=False) for entry in entries):
        raise SealError("wheelhouse may contain only regular non-symlink wheel files")
    expected = {
        _normalized_distribution(name): (name, version)
        for name, version in LOCKED_VERSIONS.items()
    }
    wheels: dict[str, dict[str, str]] = {}
    matched: set[str] = set()
    for entry in entries:
        filename = entry.name
        if not filename.endswith(".whl"):
            raise SealError(f"wheelhouse contains a non-wheel artifact: {filename}")
        lowered = filename.lower()
        candidates = [
            normalized
            for normalized, (_, version) in expected.items()
            if lowered.startswith(normalized.replace("-", "_") + "-" + version.lower() + "-")
        ]
        if len(candidates) != 1:
            raise SealError(f"wheel filename does not identify one exact locked distribution: {filename}")
        normalized = candidates[0]
        if normalized in matched:
            raise SealError(f"wheelhouse repeats locked distribution: {normalized}")
        if not _wheel_supported(filename):
            raise SealError(f"wheel does not match pinned CPython 3.11 platform tags: {filename}")
        data = read_private_file(Path(entry.path), f"locked wheel {filename}")
        digest = sha256_bytes(data)
        lock_entry = parsed_lock.get(normalized)
        if lock_entry is None or lock_entry[0] != expected[normalized][1] or digest not in lock_entry[1]:
            raise SealError(f"wheel hash/version is absent from the exact requirements lock: {filename}")
        original_name = expected[normalized][0]
        wheels[original_name] = {"filename": filename, "sha256": digest}
        matched.add(normalized)
    if matched != set(expected):
        raise SealError(f"wheelhouse does not contain the exact locked set; missing={sorted(set(expected)-matched)}")
    cache_file = tokenizer_cache_dir / TOKENIZER_CACHE_NAME
    cache_digest = sha256_bytes(read_regular_file(cache_file, "cl100k_base tokenizer cache"))
    if cache_digest != TOKENIZER_BLOB_SHA256:
        raise SealError(
            f"cl100k_base cache hash mismatch: expected {TOKENIZER_BLOB_SHA256}, got {cache_digest}"
        )
    resource_hashes: dict[str, str] = {}
    for relative, expected_hash in NLTK_RESOURCE_HASHES.items():
        digest = sha256_bytes(read_regular_file(nltk_data / relative, f"NLTK {relative}"))
        if digest != expected_hash:
            raise SealError(
                f"NLTK resource hash mismatch for {relative}: expected {expected_hash}, got {digest}"
            )
        resource_hashes[relative] = digest
    return {
        "requirements_lock_sha256": lock_digest,
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "executable": sys.executable,
            "build": list(platform.python_build()),
        },
        "platform": {
            "description": platform.platform(),
            "os": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "packages": dict(LOCKED_VERSIONS),
        "wheels": wheels,
        "tokenizer": {
            "name": TOKENIZER,
            "blob_sha256": cache_digest,
            "cache_filename": TOKENIZER_CACHE_NAME,
        },
        "nltk_resources": resource_hashes,
    }


def materialize_wheel_snapshot(
    *, wheelhouse: Path, dependencies: dict[str, Any], destination: Path
) -> Path:
    require_private_dir(destination.parent, "wheel snapshot parent")
    destination.mkdir(mode=0o700)
    site_packages = destination / "site-packages"
    site_packages.mkdir(mode=0o700)
    seen: set[str] = set()
    for distribution in sorted(dependencies["wheels"]):
        receipt = dependencies["wheels"][distribution]
        filename = receipt["filename"]
        wheel_path = wheelhouse / filename
        data = read_private_file(wheel_path, f"locked wheel {filename}")
        if sha256_bytes(data) != receipt["sha256"]:
            raise SealError(f"locked wheel changed after validation: {filename}")
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as bundle:
                for member in bundle.infolist():
                    name = member.filename
                    pure = Path(name)
                    normalized = pure.as_posix()
                    unix_mode = member.external_attr >> 16
                    basename = pure.name.lower()
                    if (
                        not name
                        or "\\" in name
                        or pure.is_absolute()
                        or ".." in pure.parts
                        or normalized in seen
                        or ".data" in pure.parts
                        or basename.endswith(".pth")
                        or basename in {"sitecustomize.py", "usercustomize.py"}
                        or stat.S_ISLNK(unix_mode)
                        or (
                            stat.S_IFMT(unix_mode) not in (0, stat.S_IFREG, stat.S_IFDIR)
                        )
                    ):
                        raise SealError(f"unsafe or unsupported member in locked wheel {filename}: {name!r}")
                    seen.add(normalized)
                    target = site_packages / pure
                    if member.is_dir():
                        target.mkdir(mode=0o700, parents=True, exist_ok=True)
                        target.chmod(0o700)
                    else:
                        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                        if os.path.lexists(target):
                            raise SealError(f"locked wheels overlap at site-packages path: {normalized}")
                        write_exclusive_private(target, bundle.read(member))
        except (zipfile.BadZipFile, OSError) as exc:
            raise SealError(f"cannot safely extract locked wheel {filename}: {exc}") from exc
    found: dict[str, str] = {}
    for distribution in importlib.metadata.distributions(path=[str(site_packages)]):
        name = distribution.metadata.get("Name")
        if not isinstance(name, str) or not name:
            raise SealError("extracted wheel distribution has no Name metadata")
        normalized = _normalized_distribution(name)
        if normalized in found:
            raise SealError(f"extracted wheel snapshot repeats distribution: {name}")
        found[normalized] = distribution.version
    expected = {
        _normalized_distribution(name): version for name, version in LOCKED_VERSIONS.items()
    }
    if found != expected:
        raise SealError(f"extracted wheel metadata differs from exact lock: {found}")
    inventory = _tree_inventory(site_packages, exclude_git=False)
    inventory_bytes = canonical_json_bytes(
        [
            {"path": path, "kind": value[0], "sha256": value[1], "executable": value[2]}
            for path, value in sorted(inventory.items())
        ]
    )
    dependencies["site_packages_sha256"] = sha256_bytes(inventory_bytes)
    fsync_directory(site_packages)
    fsync_directory(destination)
    return site_packages


def load_pinned_encoding(site_packages: Path) -> Any:
    for name in tuple(sys.modules):
        if name == "tiktoken" or name.startswith("tiktoken."):
            raise SealError("tiktoken was imported before the verified wheel snapshot")
    sys.path.insert(0, str(site_packages))
    try:
        import tiktoken  # type: ignore

        return tiktoken.get_encoding(TOKENIZER)
    except Exception as exc:
        raise SealError(f"cannot initialize pinned {TOKENIZER} from wheel snapshot: {exc}") from exc


def _extract_nltk_zip(data: bytes, destination: Path, expected_root: str) -> None:
    seen: set[str] = set()
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as bundle:
            for member in bundle.infolist():
                name = member.filename
                pure = Path(name)
                unix_mode = member.external_attr >> 16
                if (
                    not name
                    or "\\" in name
                    or pure.is_absolute()
                    or ".." in pure.parts
                    or not pure.parts
                    or pure.parts[0] != expected_root
                    or pure.as_posix() in seen
                    or stat.S_ISLNK(unix_mode)
                ):
                    raise SealError(f"unsafe NLTK {expected_root} archive member: {name!r}")
                seen.add(pure.as_posix())
                target = destination / pure
                if member.is_dir():
                    target.mkdir(mode=0o700, parents=True, exist_ok=True)
                    target.chmod(0o700)
                else:
                    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                    write_exclusive_private(target, bundle.read(member))
    except (zipfile.BadZipFile, OSError) as exc:
        raise SealError(f"cannot extract pinned NLTK {expected_root} archive: {exc}") from exc
    root = destination / expected_root
    if not root.is_dir():
        raise SealError(f"pinned NLTK archive did not create tokenizers/{expected_root}")


def materialize_dependency_snapshot(
    *, tokenizer_cache_dir: Path, nltk_data: Path, destination: Path
) -> tuple[Path, Path]:
    require_private_dir(destination.parent, "dependency snapshot parent")
    destination.mkdir(mode=0o700)
    tokenizer_out = destination / "tiktoken"
    tokenizer_out.mkdir(mode=0o700)
    tokenizer_bytes = read_regular_file(
        tokenizer_cache_dir / TOKENIZER_CACHE_NAME, "cl100k_base tokenizer cache"
    )
    if sha256_bytes(tokenizer_bytes) != TOKENIZER_BLOB_SHA256:
        raise SealError("tokenizer changed after dependency validation")
    write_exclusive_private(tokenizer_out / TOKENIZER_CACHE_NAME, tokenizer_bytes)
    nltk_out = destination / "nltk_data"
    tokenizers_out = nltk_out / "tokenizers"
    tokenizers_out.mkdir(mode=0o700, parents=True)
    for relative, expected in NLTK_RESOURCE_HASHES.items():
        data = read_regular_file(nltk_data / relative, f"NLTK {relative}")
        if sha256_bytes(data) != expected:
            raise SealError(f"NLTK resource changed after dependency validation: {relative}")
        write_exclusive_private(nltk_out / relative, data)
        _extract_nltk_zip(data, tokenizers_out, Path(relative).stem)
    for resource in ("punkt", "punkt_tab"):
        extracted = tokenizers_out / resource
        if not extracted.is_dir() or not any(
            entry.is_file() for entry in extracted.rglob("*")
        ):
            raise SealError(f"extracted pinned NLTK tokenizer snapshot lacks {resource}")
    fsync_directory(tokenizer_out)
    fsync_directory(tokenizers_out)
    fsync_directory(nltk_out)
    fsync_directory(destination)
    return tokenizer_out, nltk_out


ISOLATED_BOOTSTRAP = (
    "import runpy,sys;"
    "site,script=sys.argv[1:3];"
    "sys.path[:]=[site,script.rsplit('/',1)[0]]+sys.path;"
    "sys.argv=sys.argv[2:];"
    "runpy.run_path(script,run_name='__main__')"
)


def create_isolated_python_wrapper(directory: Path, site_packages: Path) -> Path:
    require_private_dir(directory, "wrapper directory")
    executable = Path(sys.executable).absolute()
    if "\n" in str(executable) or "\r" in str(executable):
        raise SealError("CPython executable path contains a forbidden control character")
    site_packages = require_shell_safe_build_path(site_packages, "verified wheel snapshot")
    wrapper = directory / "python"
    bootstrap = (
        "import runpy,sys;site=sys.argv[1];script=sys.argv[2];"
        "sys.path[:]=[site,script.rsplit('/',1)[0]]+sys.path;"
        "sys.argv=sys.argv[2:];runpy.run_path(sys.argv[0],run_name='__main__')"
    )
    script = (
        "#!/bin/sh\n"
        "set -eu\n"
        f"exec {shlex.quote(str(executable))} -I -S -B -c "
        f"{shlex.quote(bootstrap)} {shlex.quote(str(site_packages))} \"$@\"\n"
    ).encode("utf-8")
    write_exclusive_private(wrapper, script)
    wrapper.chmod(0o700)
    fsync_directory(directory)
    return wrapper


def generation_argv(
    source: Path,
    pool: Path,
    task: str,
    target_length: int,
    seed: int,
    site_packages: Path | None = None,
) -> list[str]:
    if site_packages is None:
        site_packages = Path("/private/pinned/site-packages")
    return [
        sys.executable,
        "-I",
        "-S",
        "-B",
        "-c",
        ISOLATED_BOOTSTRAP,
        str(site_packages),
        str(source / "scripts" / "data" / "prepare.py"),
        "--save_dir",
        str(pool / str(target_length)),
        "--benchmark",
        "synthetic",
        "--task",
        task,
        "--subset",
        "test",
        "--tokenizer_path",
        TOKENIZER,
        "--tokenizer_type",
        "openai",
        "--max_seq_length",
        str(target_length),
        "--model_template_type",
        "base",
        "--num_samples",
        str(POOL_SIZE),
        "--random_seed",
        str(seed),
    ]


def canonical_generation_receipt(
    *, task: str, target_length: int, seed: int
) -> dict[str, Any]:
    logical_source = Path("/RULER")
    logical_pool = Path("/POOL")
    logical_site = Path("/RUNTIME/site-packages")
    return {
        "generation_cwd": "/RULER/scripts/data",
        "generation_argv": generation_argv(
            logical_source, logical_pool, task, target_length, seed, logical_site
        ),
    }


def generate_official_pool(
    *,
    source_snapshot: Path,
    reproduction_root: Path,
    plan: dict[str, Any],
    tokenizer_cache_dir: Path,
    nltk_data: Path,
    site_packages: Path,
) -> tuple[dict[tuple[str, int], bytes], dict[tuple[str, int], dict[str, Any]]]:
    """Generate every cell internally from the archived pinned source."""
    source_snapshot = require_shell_safe_build_path(
        require_private_dir(source_snapshot, "archived RULER source"), "archived source"
    )
    require_shell_safe_build_path(
        require_private_dir(reproduction_root.parent, "reproduction parent"),
        "reproduction parent",
    )
    reproduction_root.mkdir(mode=0o700)
    require_shell_safe_build_path(reproduction_root, "reproduction root")
    reproduction_root.chmod(0o700)
    site_packages = require_private_dir(site_packages, "verified wheel snapshot")
    wrapper_dir = reproduction_root / "isolated-bin"
    wrapper_dir.mkdir(mode=0o700)
    create_isolated_python_wrapper(wrapper_dir, site_packages)
    temp_dir = reproduction_root / "tmp"
    temp_dir.mkdir(mode=0o700)
    environment = {
        "PATH": str(wrapper_dir),
        "LC_ALL": "C",
        "LANG": "C",
        "PYTHONHASHSEED": "0",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
        "TIKTOKEN_CACHE_DIR": str(tokenizer_cache_dir.resolve(strict=True)),
        "NLTK_DATA": str(nltk_data.resolve(strict=True)),
        "TMPDIR": str(temp_dir),
        "HTTP_PROXY": "http://127.0.0.1:9",
        "HTTPS_PROXY": "http://127.0.0.1:9",
        "ALL_PROXY": "http://127.0.0.1:9",
        "NO_PROXY": "",
    }
    dependency_inventory = {
        "tokenizer": _tree_inventory(tokenizer_cache_dir, exclude_git=False),
        "nltk": _tree_inventory(nltk_data, exclude_git=False),
        "site_packages": _tree_inventory(site_packages, exclude_git=False),
    }
    compared: dict[tuple[str, int], bytes] = {}
    receipts: dict[tuple[str, int], dict[str, Any]] = {}
    cwd = source_snapshot / "scripts" / "data"
    for cell in plan["cells"]:
        task = cell["task"]
        target_length = cell["target_length"]
        seed = cell["generator_seed"]
        argv = generation_argv(
            source_snapshot, reproduction_root, task, target_length, seed, site_packages
        )
        try:
            proc = subprocess.run(
                argv,
                cwd=cwd,
                env=environment,
                check=False,
                capture_output=True,
                timeout=7200,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise SealError(f"official regeneration failed for {task}/{target_length}: {exc}") from exc
        if proc.returncode != 0:
            raise SealError(
                f"official regeneration failed for {task}/{target_length} with status "
                f"{proc.returncode}; stderr_sha256={sha256_bytes(proc.stderr)}"
            )
        combined_output = (proc.stdout + b"\n" + proc.stderr).lower()
        if b"[nltk_data]" in combined_output or b"downloading package" in combined_output:
            raise SealError(f"official generation attempted an NLTK download for {task}/{target_length}")
        if dependency_inventory != {
            "tokenizer": _tree_inventory(tokenizer_cache_dir, exclude_git=False),
            "nltk": _tree_inventory(nltk_data, exclude_git=False),
            "site_packages": _tree_inventory(site_packages, exclude_git=False),
        }:
            raise SealError(f"official generation mutated pinned dependency inputs for {task}/{target_length}")
        generated_task_dir = reproduction_root / str(target_length) / task
        try:
            entries = sorted(path.name for path in generated_task_dir.iterdir())
        except OSError as exc:
            raise SealError(
                f"official generator returned success without output for {task}/{target_length}: {exc}"
            ) from exc
        if entries != ["test.jsonl"]:
            raise SealError(
                f"official generator output shape changed for {task}/{target_length}: {entries}"
            )
        generated = read_regular_file(
            generated_task_dir / "test.jsonl", f"regenerated JSONL {task}/{target_length}"
        )
        key = (task, target_length)
        compared[key] = generated
        receipts[key] = canonical_generation_receipt(
            task=task, target_length=target_length, seed=seed
        )
    if set(compared) != {(task, length) for length in LENGTHS for task in TASKS}:
        raise SealError("internal generation did not cover the exact nine cells")
    return compared, receipts


def validate_provenance_receipts(
    upstream: dict[str, Any], dependencies: dict[str, Any]
) -> None:
    if not strict_equal(upstream, {
        "url": RULER_URL,
        "commit": RULER_COMMIT,
        "files": SOURCE_HASHES,
    }):
        raise SealError("upstream provenance receipt does not match the frozen source")
    if dependencies.get("requirements_lock_sha256") != REQUIREMENTS_LOCK_SHA256:
        raise SealError("dependency provenance has the wrong requirements lock")
    if not strict_equal(dependencies.get("packages"), LOCKED_VERSIONS):
        raise SealError("dependency provenance has the wrong package versions")
    wheels = dependencies.get("wheels")
    if (
        not isinstance(wheels, dict)
        or set(wheels) != set(LOCKED_VERSIONS)
        or any(
            not isinstance(receipt, dict)
            or set(receipt) != {"filename", "sha256"}
            or not isinstance(receipt["filename"], str)
            or re.fullmatch(r"[0-9a-f]{64}", receipt["sha256"]) is None
            for receipt in wheels.values()
        )
        or re.fullmatch(r"[0-9a-f]{64}", dependencies.get("site_packages_sha256", "")) is None
    ):
        raise SealError("dependency provenance has invalid exact wheel/runtime identities")
    if dependencies.get("tokenizer") != {
        "name": TOKENIZER,
        "blob_sha256": TOKENIZER_BLOB_SHA256,
        "cache_filename": TOKENIZER_CACHE_NAME,
    }:
        raise SealError("dependency provenance has the wrong tokenizer identity")
    if dependencies.get("nltk_resources") != NLTK_RESOURCE_HASHES:
        raise SealError("dependency provenance has the wrong NLTK resource identities")
    python = dependencies.get("python")
    if not isinstance(python, dict) or python.get("implementation") != "CPython":
        raise SealError("dependency provenance has no CPython identity")
    version = python.get("version")
    if not isinstance(version, str) or re.fullmatch(r"3\.11(?:\.[0-9]+)?", version) is None:
        raise SealError("dependency provenance is not CPython 3.11")
    executable = python.get("executable")
    build = python.get("build")
    if not isinstance(executable, str) or not executable or not isinstance(build, list) or len(build) != 2:
        raise SealError("dependency provenance has no exact CPython executable/build identity")
    platform_identity = dependencies.get("platform")
    if not isinstance(platform_identity, dict) or set(platform_identity) != {
        "description", "os", "release", "machine"
    } or any(not isinstance(value, str) or not value for value in platform_identity.values()):
        raise SealError("dependency provenance has no exact OS/architecture identity")


def build_sealed_objects(
    *,
    plan: dict[str, Any],
    master_key: bytes,
    plan_sha256: str,
    cells: dict[tuple[str, int], list[PoolRow]],
    upstream: dict[str, Any],
    dependencies: dict[str, Any],
    generation_receipts: dict[tuple[str, int], dict[str, Any]],
    redistribution_files: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any], list[tuple[str, bytes]]]:
    public_fixtures: list[dict[str, Any]] = []
    gold_fixtures: list[dict[str, Any]] = []
    payloads: list[tuple[str, bytes]] = []
    pool_receipts: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for cell in plan["cells"]:
        task = cell["task"]
        target_length = cell["target_length"]
        seed = cell["generator_seed"]
        rows = cells[(task, target_length)]
        selected = select_rows(rows, task, target_length, master_key)
        pool_receipts.append(
            {
                "task": task,
                "target_length": target_length,
                "generator_seed": seed,
                **generation_receipts[(task, target_length)],
                "rows": [
                    {
                        "ordinal": row.ordinal,
                        "raw_row_sha256": row.raw_row_sha256,
                        "canonical_row_sha256": row.canonical_row_sha256,
                        "payload_sha256": row.payload_sha256,
                        "construction_tokens": row.construction_tokens,
                        "row_length": row.row_length,
                        **(
                            {"token_position_answer": row.token_position_answer}
                            if row.token_position_answer is not None
                            else {}
                        ),
                    }
                    for row in rows
                ],
            }
        )
        for row, selection in selected:
            identity = fixture_id(master_key, task, target_length, row)
            if identity in seen_ids:
                raise SealError(f"duplicate derived fixture id: {identity}")
            seen_ids.add(identity)
            relative_payload = f"payloads/{identity}.txt"
            public_fixtures.append(
                {
                    "id": identity,
                    "task": task,
                    "target_length": target_length,
                    "payload": relative_payload,
                    "payload_sha256": row.payload_sha256,
                    "payload_bytes": len(row.payload_bytes),
                    "construction_tokens": row.construction_tokens,
                    "row_length": row.row_length,
                }
            )
            gold_fixtures.append(
                {
                    "id": identity,
                    "task": task,
                    "target_length": target_length,
                    "outputs": list(row.outputs),
                    "raw_row_sha256": row.raw_row_sha256,
                    "raw_row_utf8": row.raw_row_utf8,
                    "canonical_row_sha256": row.canonical_row_sha256,
                    "ordinal": row.ordinal,
                    "generator_seed": seed,
                    "payload_sha256": row.payload_sha256,
                    "selection": selection,
                }
            )
            payloads.append((relative_payload, row.payload_bytes))
    expected_count = len(TASKS) * len(LENGTHS) * PER_CELL
    if len(public_fixtures) != expected_count or len(gold_fixtures) != expected_count:
        raise SealError(f"sealed suite must contain exactly {expected_count} fixtures")
    public_identity = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "ruler_exact_mini_public_manifest",
        "suite_id": SUITE_ID,
        "upstream_commit": RULER_COMMIT,
        "source": {"name": "NVIDIA/RULER", "url": RULER_URL, "commit": RULER_COMMIT},
        "configuration": {
            "tasks": list(TASKS),
            "target_lengths": list(LENGTHS),
            "pool_size": POOL_SIZE,
            "per_cell": PER_CELL,
            "tokenizer": TOKENIZER,
            "task_generation_reserves": {
                task: TASK_SPECS[task].reserve for task in TASKS
            },
            "payload_rule": 'row["input"] + row["answer_prefix"]',
            "selection": {
                "niah_multikey_3": "one secret-HMAC-ranked row per answer-position decile",
                "vt": "ten secret-HMAC-ranked line ordinals",
                "fwe": "ten secret-HMAC-ranked line ordinals",
            },
        },
        "provenance_commitments": {
            "generation_plan_sha256": plan_sha256,
            "requirements_lock_sha256": dependencies["requirements_lock_sha256"],
            "tokenizer_blob_sha256": dependencies["tokenizer"]["blob_sha256"],
            "ruler_source_files": upstream["files"],
        },
        "redistribution_files": redistribution_files,
        "fixtures": public_fixtures,
    }
    identity_sha = sha256_bytes(canonical_json_bytes(public_identity))
    gold = {
        "schema_version": SCHEMA_VERSION,
        "record_type": "ruler_exact_mini_gold",
        "suite_id": SUITE_ID,
        "manifest_identity_sha256": identity_sha,
        "fixtures": gold_fixtures,
        "provenance": {
            "generation_plan": plan,
            "generation_plan_sha256": plan_sha256,
            "upstream": upstream,
            "dependencies": dependencies,
            "pool_receipts": pool_receipts,
        },
    }
    return public_identity, gold, payloads


SAFE_BUILD_PATH = re.compile(r"\A/[A-Za-z0-9._/-]+\Z")


def require_shell_safe_build_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if SAFE_BUILD_PATH.fullmatch(str(resolved)) is None:
        raise SealError(
            f"{label} path is unsafe for pinned RULER prepare.py shell interpolation: {resolved}"
        )
    return resolved


def validate_public_gold_targets(out: Path, gold_out: Path) -> tuple[Path, Path]:
    public_parent = ensure_private_parent(out)
    gold_parent = ensure_private_parent(gold_out)
    public_target = public_parent / out.name
    gold_target = gold_parent / gold_out.name
    if not out.name or out.name in {".", ".."} or not gold_out.name or gold_out.name in {".", ".."}:
        raise SealError("public and gold outputs must have ordinary final path components")
    if public_parent == gold_parent:
        raise SealError("--out and --gold-out must use separate owner-only parent directories")
    try:
        if os.path.commonpath([str(public_target), str(gold_target)]) == str(public_target):
            raise SealError("private gold must not be inside the public suite root")
    except ValueError as exc:
        raise SealError(f"cannot compare public and gold output paths: {exc}") from exc
    if os.path.lexists(public_target):
        raise SealError(f"sealed public output already exists; refusing overwrite: {public_target}")
    if os.path.lexists(gold_target):
        raise SealError(f"sealed gold output already exists; refusing overwrite: {gold_target}")
    return public_target, gold_target


def publish_verified_suite(
    *,
    verified_pool_bytes: dict[tuple[str, int], bytes],
    generation_receipts: dict[tuple[str, int], dict[str, Any]],
    out: Path,
    gold_out: Path,
    plan_path: Path,
    encoding: Any,
    upstream: dict[str, Any],
    dependencies: dict[str, Any],
    ruler_license_bytes: bytes,
    third_party_notice_bytes: bytes,
) -> tuple[Path, Path]:
    """Validate already byte-reproduced pools, then durably publish gold before public."""
    validate_provenance_receipts(upstream, dependencies)
    expected_cells = {(task, length) for length in LENGTHS for task in TASKS}
    if set(verified_pool_bytes) != expected_cells or set(generation_receipts) != expected_cells:
        raise SealError("verified pool and regeneration receipts must cover the exact nine cells")
    plan, master_key, plan_sha = load_plan(plan_path)
    cells: dict[tuple[str, int], list[PoolRow]] = {}
    seen_payloads: dict[str, tuple[str, int, int]] = {}
    for cell in plan["cells"]:
        task = cell["task"]
        target_length = cell["target_length"]
        rows = parse_pool_cell_bytes(
            verified_pool_bytes[(task, target_length)], task, target_length, encoding
        )
        for row in rows:
            previous = seen_payloads.get(row.payload_sha256)
            if previous is not None:
                raise SealError(
                    f"duplicate payload hash across pool: {row.payload_sha256} at "
                    f"{previous} and {(task, target_length, row.ordinal)}"
                )
            seen_payloads[row.payload_sha256] = (task, target_length, row.ordinal)
        cells[(task, target_length)] = rows
    if sha256_bytes(ruler_license_bytes) != SOURCE_HASHES["LICENSE"]:
        raise SealError("RULER LICENSE bytes do not match the pinned source")
    if sha256_bytes(third_party_notice_bytes) != THIRD_PARTY_NOTICES_SHA256:
        raise SealError("third-party notices bytes do not match the pinned suite notice")
    redistribution_files = {
        "LICENSE.NVIDIA-RULER": SOURCE_HASHES["LICENSE"],
        "THIRD_PARTY_NOTICES.md": THIRD_PARTY_NOTICES_SHA256,
    }
    public_identity, gold, payloads = build_sealed_objects(
        plan=plan,
        master_key=master_key,
        plan_sha256=plan_sha,
        cells=cells,
        upstream=upstream,
        dependencies=dependencies,
        generation_receipts=generation_receipts,
        redistribution_files=redistribution_files,
    )
    public_target, gold_target = validate_public_gold_targets(out, gold_out)
    public_parent = public_target.parent
    gold_parent = gold_target.parent
    public_temporary = Path(
        tempfile.mkdtemp(prefix=f".{public_target.name}.tmp-", dir=public_parent)
    )
    public_temporary.chmod(0o700)
    gold_temporary = gold_parent / f".{gold_target.name}.tmp-{secrets.token_hex(16)}"
    gold_published = False
    public_published = False
    try:
        payload_dir = public_temporary / "payloads"
        payload_dir.mkdir(mode=0o700)
        for relative, content in payloads:
            path = public_temporary / relative
            if path.parent != payload_dir:
                raise SealError(f"unsafe derived payload path: {relative}")
            write_exclusive_private(path, content)
        fsync_directory(payload_dir)
        gold_bytes = canonical_json_bytes(gold)
        gold_sha = sha256_bytes(gold_bytes)
        manifest = dict(public_identity)
        manifest["gold_sha256"] = gold_sha
        manifest_bytes = canonical_json_bytes(manifest)
        identity_view = dict(manifest)
        del identity_view["gold_sha256"]
        if sha256_bytes(canonical_json_bytes(identity_view)) != gold["manifest_identity_sha256"]:
            raise SealError("internal manifest identity commitment mismatch")
        if sha256_bytes(gold_bytes) != manifest["gold_sha256"]:
            raise SealError("internal gold commitment mismatch")
        if not third_party_notice_bytes:
            raise SealError("third-party notice bytes are empty")
        write_exclusive_private(public_temporary / "LICENSE.NVIDIA-RULER", ruler_license_bytes)
        write_exclusive_private(public_temporary / "THIRD_PARTY_NOTICES.md", third_party_notice_bytes)
        write_exclusive_private(public_temporary / "manifest.json", manifest_bytes)
        fsync_directory(public_temporary)
        write_exclusive_private(gold_temporary, gold_bytes)
        # Publish and durably sync gold first. A crash can leave only orphaned private gold,
        # never a public manifest whose committed gold was not already durable.
        os.link(gold_temporary, gold_target, follow_symlinks=False)
        os.unlink(gold_temporary)
        gold_published = True
        fsync_directory(gold_parent)
        rename_directory_noreplace(public_temporary, public_target)
        public_published = True
        fsync_directory(public_parent)
    except Exception:
        if not public_published:
            shutil.rmtree(public_temporary, ignore_errors=True)
        if os.path.lexists(gold_temporary):
            try:
                os.unlink(gold_temporary)
            except OSError:
                pass
        # Once the public rename succeeds, never remove its already-durable gold,
        # even if the following public-parent fsync reports an error.
        if gold_published and not public_published:
            try:
                if read_private_file(gold_target, "rollback gold") == gold_bytes:
                    os.unlink(gold_target)
                    fsync_directory(gold_parent)
            except Exception:
                pass
        raise
    return public_target / "manifest.json", gold_target


def command_plan(args: argparse.Namespace) -> int:
    require_isolated_runtime()
    out = Path(args.out).expanduser()
    parent = ensure_private_parent(out)
    target = parent / out.name
    if os.path.lexists(target):
        raise SealError(f"plan output already exists; refusing overwrite: {target}")
    for _ in range(1024):
        try:
            plan = build_plan(secrets.token_bytes(32))
            break
        except SealError:
            continue
    else:
        raise SealError("could not derive a valid fresh plan")
    atomic_publish_private_file(target, canonical_json_bytes(plan))
    print(target)
    return 0


def _require_exact_design_args(args: argparse.Namespace) -> None:
    if tuple(args.tasks) != TASKS:
        raise SealError(f"--tasks is frozen to: {' '.join(TASKS)}")
    if tuple(args.lengths) != LENGTHS:
        raise SealError(f"--lengths is frozen to: {' '.join(map(str, LENGTHS))}")
    if args.pool_size != POOL_SIZE or args.per_cell != PER_CELL:
        raise SealError(
            f"pool/per-cell sizes are frozen to {POOL_SIZE}/{PER_CELL}"
        )


def command_build(args: argparse.Namespace) -> int:
    require_isolated_runtime()
    if not args.yes_build:
        raise SealError("refusing to build without --yes-build")
    _require_exact_design_args(args)
    out = Path(args.out).expanduser()
    gold_out = Path(args.gold_out).expanduser()
    public_target, _ = validate_public_gold_targets(out, gold_out)
    source = Path(args.ruler_source).expanduser()
    upstream = validate_source(source)
    dependencies = validate_dependencies(
        Path(args.requirements_lock).expanduser(),
        Path(args.wheelhouse).expanduser(),
        Path(args.tiktoken_cache_dir).expanduser(),
        Path(args.nltk_data).expanduser(),
    )
    plan, _, _ = load_plan(Path(args.plan).expanduser())
    scratch_parent = require_shell_safe_build_path(
        require_private_dir(Path(args.scratch_parent).expanduser(), "scratch parent"),
        "scratch parent",
    )
    internal_base = Path(tempfile.mkdtemp(prefix="azdaja-ruler-build-", dir=scratch_parent))
    internal_base.chmod(0o700)
    scratch = require_shell_safe_build_path(
        require_private_dir(internal_base, "internal build scratch"),
        "internal build scratch",
    )
    try:
        stable_plan = scratch / "plan.json"
        write_exclusive_private(stable_plan, canonical_json_bytes(plan))
        source_snapshot = extract_pinned_source_archive(source.resolve(strict=True), scratch / "RULER")
        site_packages = materialize_wheel_snapshot(
            wheelhouse=Path(args.wheelhouse).expanduser(),
            dependencies=dependencies,
            destination=scratch / "runtime",
        )
        tokenizer_snapshot, nltk_snapshot = materialize_dependency_snapshot(
            tokenizer_cache_dir=Path(args.tiktoken_cache_dir).expanduser(),
            nltk_data=Path(args.nltk_data).expanduser(),
            destination=scratch / "dependencies",
        )
        generated_pool, generation_receipts = generate_official_pool(
            source_snapshot=source_snapshot,
            reproduction_root=scratch / "pool",
            plan=plan,
            tokenizer_cache_dir=tokenizer_snapshot,
            nltk_data=nltk_snapshot,
            site_packages=site_packages,
        )
        os.environ["TIKTOKEN_CACHE_DIR"] = str(tokenizer_snapshot)
        os.environ["NLTK_DATA"] = str(nltk_snapshot)
        encoding = load_pinned_encoding(site_packages)
        manifest, gold = publish_verified_suite(
            verified_pool_bytes=generated_pool,
            generation_receipts=generation_receipts,
            out=out,
            gold_out=gold_out,
            plan_path=stable_plan,
            encoding=encoding,
            upstream=upstream,
            dependencies=dependencies,
            ruler_license_bytes=read_regular_file(
                source_snapshot / "LICENSE", "archived RULER LICENSE"
            ),
            third_party_notice_bytes=read_regular_file(
                Path(__file__).with_name("THIRD_PARTY_NOTICES.md"),
                "suite third-party notices",
            ),
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(json.dumps({"manifest": str(manifest), "gold": str(gold)}, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="create a fresh owner-only seed plan")
    plan.add_argument("--out", required=True)
    plan.set_defaults(func=command_plan)

    build = subparsers.add_parser(
        "build", help="internally generate, validate, select, and publish the sealed suite"
    )
    build.add_argument("--out", required=True, help="new public suite directory")
    build.add_argument("--gold-out", required=True, help="new private gold JSON file in a separate root")
    build.add_argument("--plan", required=True)
    build.add_argument("--ruler-source", required=True)
    build.add_argument("--wheelhouse", required=True, help="owner-only directory with exact hash-locked wheels")
    build.add_argument("--scratch-parent", required=True, help="pre-existing owner-only 0700 shell-safe directory")
    build.add_argument("--tiktoken-cache-dir", required=True)
    build.add_argument("--nltk-data", required=True)
    build.add_argument(
        "--requirements-lock",
        default=str(Path(__file__).with_name("requirements.lock")),
    )
    build.add_argument("--tasks", nargs="+", default=list(TASKS))
    build.add_argument("--lengths", nargs="+", type=int, default=list(LENGTHS))
    build.add_argument("--pool-size", type=int, default=POOL_SIZE)
    build.add_argument("--per-cell", type=int, default=PER_CELL)
    build.add_argument("--yes-build", action="store_true")
    build.set_defaults(func=command_build)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (SealError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
