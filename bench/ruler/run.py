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
import concurrent.futures
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
import threading
import time
import tomllib
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
FULL_WORKFLOW = "full-v1"
CANDIDATE_FULL_WORKFLOW = "candidate-full-90-v1"
SMOKE_WORKFLOW = "candidate-smoke-20-v1"
WORKFLOWS = (FULL_WORKFLOW, CANDIDATE_FULL_WORKFLOW, SMOKE_WORKFLOW)
PARALLEL_WIDTH = 4
PARALLEL_WIDTH_SCOPE = "global"
SMOKE_EXPECTED_FIXTURES = 20
# Two fixtures from every task/length cell plus two fixed diagonal extras.
SMOKE_CELL_QUOTAS = {
    ("niah_multikey_3", 8192): 3,
    ("vt", 8192): 2,
    ("fwe", 8192): 2,
    ("niah_multikey_3", 32768): 2,
    ("vt", 32768): 3,
    ("fwe", 32768): 2,
    ("niah_multikey_3", 131072): 2,
    ("vt", 131072): 2,
    ("fwe", 131072): 2,
}
# Immutable identities selected once by ascending fixture ID within each cell
# from the released ruler-exact-mini-v1 public manifest.  Payload commitments
# prevent a different manifest from reusing an ID with different bytes.
SMOKE_FIXTURE_COMMITMENTS = (
    ("rxm-0842be47abaf03e7f7608f4e080b7b49", "37d6a1d80bc8dd11756b1d7047f6899bfef75f5f70bb49470ebe2376dc289c24", "niah_multikey_3", 8192),
    ("rxm-6670e3c89f0a5890a7e589245915d2c9", "ef82da6a46a76668934c04bf26439a4d1ef5fd7c677557a24c22425fa0ad0ad0", "niah_multikey_3", 8192),
    ("rxm-6a55c9a3cbd7eeb6afa3c9a66cb03ac7", "ce98538c39226cd9098f7239254a8c5a280f8e00883df6cd59505dbb26880705", "niah_multikey_3", 8192),
    ("rxm-05b3f054f9022a57c4982c211373027b", "7ccf3ca92a1fdb2a1fb71c74bf3fc177d0d4343c9ebaa53e78fac1e3fd3c59a5", "vt", 8192),
    ("rxm-324ca4d778d06fbfa4bb504d8147116a", "932bbaa10a3795b05813d657523956e99a4cbc2bfa28734b96d149bee03d1429", "vt", 8192),
    ("rxm-20717f3b83d7a80648f95e49e6452346", "a20028b2e3489cdebd66dc3af3c2db4f0da3b86e37f15ea697c1d7f8a9b644b5", "fwe", 8192),
    ("rxm-2a38707acfc3c0c0e7899f893226ce48", "48cdffd4e526dfd26c94627309505d0d98e940f3477e3c9e6260178c620ede3e", "fwe", 8192),
    ("rxm-0d5ef27c4cec939ae76718dcfec439f2", "f385690533d93f9c5d84ae01e537dce46a2658202f00774f5ea4a51efe973ee4", "niah_multikey_3", 32768),
    ("rxm-2285810b89e4909ccf15581027b173cc", "6bd8884baa5b5329fad1651bf041654abacaec140f3288687762a670af107fd2", "niah_multikey_3", 32768),
    ("rxm-1d930dbb1e9ea475815822e3ac16a999", "abfdd08a7484cd41e6b7480f1f34662146b2ebcc0f841f6902ea3e332a9d3226", "vt", 32768),
    ("rxm-4373136e673616983d16863a929238be", "d54054d22b7e89de8561d7b71083c89cc72123a8d66915359314c1c368a27bdf", "vt", 32768),
    ("rxm-513316fa756fbec5bc68b46dabcca508", "1e76d4bed439a31120a9cddd56ec4dba60608514f01d80a4a78555c854ec1aa2", "vt", 32768),
    ("rxm-11dc65da42de7eb3f228e18a2a8eff65", "2984d9aabb37f157b1b6606eba174ad9d591cf80932a40fc12fec86f7d69f193", "fwe", 32768),
    ("rxm-9361854e5de1e01d72c8c549b4006f9e", "a0e7da19b7a6fbd14941e686d363f93ebd3a6e17d77681fb7dc6966571cce2e9", "fwe", 32768),
    ("rxm-2ac3ee8a8d478d822a685de2dc0b16a3", "861ecb9f2fddfa1babeaf315781c1a42378c2b7f6d665c3a6c11b077f82cf797", "niah_multikey_3", 131072),
    ("rxm-4423687db17d9a31b3a9857c8cd69f30", "f0a1a7678ced8a95578776962773942a09a8441f6e3e13d4951cfa956a211d44", "niah_multikey_3", 131072),
    ("rxm-00cc544fcda467237ed86a3e160f886a", "1710948857ee97ee2188879557bec020a402c7d3df9850ff509a6bbf7ddd7828", "vt", 131072),
    ("rxm-0638d6b89286a8334b8af333258cf275", "eea48495d80bc60012dc9fa2d329aa843ac45990283da3f5826cc17d7f3e30fa", "vt", 131072),
    ("rxm-1ed71e2bbcc6731fc8c7b90b288180f7", "26ac9857508a8666d9f9f4c2fd16c148d721c70758817fa69db1df7d83ae4e0d", "fwe", 131072),
    ("rxm-44cd3a588f0db7c23e48b584dbfcba22", "a86d35874a265d96c3191490f1305540a00ba322a6ba7eab5cc7c8137f0543fa", "fwe", 131072),
)
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
ROOT_LEAK_MIN_CHARS = 100
_ROLLING_HASH_BASE = 1_000_003
_ROLLING_HASH_MASK = (1 << 64) - 1


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


def _rolling_windows(text: str, width: int) -> Iterable[tuple[int, int]]:
    """Yield (offset, uint64 hash) for exact Unicode-code-point windows."""
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
    """Detect an exact common code-point substring without retaining matched text."""
    if type(minimum_chars) is not int or minimum_chars <= 0:
        raise BenchError("root-context leak threshold must be a positive integer")
    if len(public_payload) < minimum_chars or len(root_transcript) < minimum_chars:
        return False
    # Index the shorter stream's hashes. Hash equality is only a candidate: every
    # code point is then compared exactly, so uint64 collisions cannot create a hit.
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
    """Audit the exact UTF-8 payload and exact retained solo transcript."""
    try:
        payload = payload_data.decode("utf-8")
        trace = trace_data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BenchError(f"root-context leak inputs must be exact UTF-8: {exc}") from exc
    detected = exact_unicode_substring_present(payload, trace)
    return {
        "applicable": True,
        "scanned": True,
        "detected": detected,
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


def candidate_repair_model(skill: Path) -> str:
    config_path = skill / "config.toml"
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise BenchError(f"cannot parse frozen candidate config: {exc}") from exc
    root_model = config.get("default_model")
    if root_model != MODEL:
        raise BenchError("frozen candidate root model does not match RULER model")
    if "jcode_repair_model" not in config:
        raise BenchError("fresh candidate config lacks explicit jcode_repair_model")
    repair_model = config["jcode_repair_model"]
    if (
        not isinstance(repair_model, str)
        or not repair_model
        or repair_model.strip() != repair_model
    ):
        raise BenchError("frozen candidate repair model is invalid")
    return repair_model


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


def validate_candidate_executable_binding(
    candidate: dict[str, Any], executables: dict[str, Any]
) -> None:
    """Require the snapshotted candidate binary to be the executed Azdaja bytes."""
    try:
        component = candidate["components"]["azdaja"]
        executable = executables["azdaja"]
    except (KeyError, TypeError) as exc:
        raise BenchError("candidate/Azdaja executable binding is missing") from exc
    if not isinstance(component, dict) or not isinstance(executable, dict):
        raise BenchError("candidate/Azdaja executable binding is invalid")
    if any(component.get(key) != executable.get(key) for key in ("sha256", "bytes")):
        raise BenchError(
            "candidate azdaja component hash/bytes differ from the executed Azdaja binary"
        )


def frozen_smoke_slice(
    fixtures: Sequence[PublicFixture],
) -> tuple[PublicFixture, ...]:
    """Bind the released manifest's exact 20 public, no-gold smoke fixtures."""
    by_id = {fixture.fixture_id: fixture for fixture in fixtures}
    if len(by_id) != len(fixtures):
        raise BenchError("public fixture IDs are not unique")
    if len(SMOKE_FIXTURE_COMMITMENTS) != SMOKE_EXPECTED_FIXTURES or len({
        item[0] for item in SMOKE_FIXTURE_COMMITMENTS
    }) != SMOKE_EXPECTED_FIXTURES:
        raise BenchError("code-frozen smoke fixture commitments are invalid")
    selected: list[PublicFixture] = []
    counts: Counter[tuple[str, int]] = Counter()
    for fixture_id, payload_sha256, task, target_length in SMOKE_FIXTURE_COMMITMENTS:
        fixture = by_id.get(fixture_id)
        if fixture is None:
            raise BenchError(f"public manifest lacks frozen smoke fixture {fixture_id}")
        if (
            fixture.payload_sha256 != payload_sha256
            or fixture.task != task
            or fixture.target_length != target_length
        ):
            raise BenchError(f"frozen smoke fixture identity drifted: {fixture_id}")
        selected.append(fixture)
        counts[(task, target_length)] += 1
    if counts != Counter(SMOKE_CELL_QUOTAS):
        raise BenchError("code-frozen smoke fixtures violate declared stratification")
    return tuple(selected)

def workflow_fixture_ids(
    suite: PublicSuite, *, seed: int, workflow: str
) -> tuple[str, ...]:
    if workflow == SMOKE_WORKFLOW:
        return tuple(fixture.fixture_id for fixture in frozen_smoke_slice(suite.fixtures))
    if workflow not in {FULL_WORKFLOW, CANDIDATE_FULL_WORKFLOW}:
        raise BenchError(f"unknown frozen RULER workflow: {workflow!r}")
    ordered = list(suite.fixtures)
    random.Random(seed).shuffle(ordered)
    return tuple(fixture.fixture_id for fixture in ordered)


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
    repair_model: str = MODEL,
    workflow: str = FULL_WORKFLOW,
    parallel_width: int = PARALLEL_WIDTH,
    random_names: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Build a full balanced schedule or the frozen candidate smoke slice."""
    if workflow not in WORKFLOWS:
        raise BenchError(f"unknown frozen RULER workflow: {workflow!r}")
    if parallel_width != PARALLEL_WIDTH:
        raise BenchError(f"parallel width is frozen at exactly {PARALLEL_WIDTH} globally")
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
    if workflow == FULL_WORKFLOW:
        planned = (
            (fixture, arm)
            for fixture, order in zip(fixture_order, permutations)
            for arm in order
        )
    elif workflow == CANDIDATE_FULL_WORKFLOW:
        planned = ((fixture, "jcode-azdaja") for fixture in fixture_order)
    else:
        planned = (
            (fixture, "jcode-azdaja")
            for fixture in frozen_smoke_slice(suite.fixtures)
        )
    for ordinal, (fixture, arm) in enumerate(planned, 1):
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
    frozen_workflow_fixture_ids = list(
        workflow_fixture_ids(suite, seed=seed, workflow=workflow)
    )
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
            "repair_model": repair_model,
            "arms": list(ARMS),
            "repetitions": REPETITIONS,
            "seed": seed,
            "timeout_seconds": timeout,
            "workflow": workflow,
            "workflow_fixture_ids": frozen_workflow_fixture_ids,
            "workflow_fixture_ids_sha256": sha256_bytes(
                canonical_json_bytes(frozen_workflow_fixture_ids)
            ),
            "parallel_width": parallel_width,
            "configured_global_width": parallel_width,
            "parallel_width_scope": PARALLEL_WIDTH_SCOPE,
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
    repair_model: str = MODEL,
    workflow: str = FULL_WORKFLOW,
    parallel_width: int = PARALLEL_WIDTH,
) -> None:
    """Validate a frozen schedule and every execution identity exactly."""
    if workflow not in WORKFLOWS:
        raise BenchError(f"unknown frozen RULER workflow: {workflow!r}")
    if parallel_width != PARALLEL_WIDTH:
        raise BenchError(f"parallel width is frozen at exactly {PARALLEL_WIDTH} globally")
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

    workflow_ids = list(
        workflow_fixture_ids(suite, seed=seed, workflow=workflow)
    )
    expected_configuration = {
        "model": MODEL,
        "reasoning": REASONING,
        "repair_model": repair_model,
        "arms": list(ARMS),
        "repetitions": 1,
        "seed": seed,
        "timeout_seconds": timeout,
        "workflow": workflow,
        "workflow_fixture_ids": workflow_ids,
        "workflow_fixture_ids_sha256": sha256_bytes(
            canonical_json_bytes(workflow_ids)
        ),
        "parallel_width": parallel_width,
        "configured_global_width": parallel_width,
        "parallel_width_scope": PARALLEL_WIDTH_SCOPE,
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
    seeded_fixture_order = list(suite.fixtures)
    random.Random(seed).shuffle(seeded_fixture_order)
    if workflow == FULL_WORKFLOW:
        expected_grid = {
            (fixture_id, arm, 1) for fixture_id in public_by_id for arm in ARMS
        }
        expected_job_count = EXPECTED_FIXTURES * len(ARMS)
    elif workflow == CANDIDATE_FULL_WORKFLOW:
        expected_grid = {
            (fixture_id, "jcode-azdaja", 1) for fixture_id in public_by_id
        }
        expected_job_count = EXPECTED_FIXTURES
    else:
        smoke_fixtures = frozen_smoke_slice(suite.fixtures)
        expected_grid = {
            (fixture.fixture_id, "jcode-azdaja", 1) for fixture in smoke_fixtures
        }
        expected_job_count = SMOKE_EXPECTED_FIXTURES
    if not isinstance(jobs, list) or len(jobs) != expected_job_count:
        raise BenchError(
            f"frozen {workflow} schedule must contain exactly {expected_job_count} jobs"
        )
    observed: set[tuple[str, str, int]] = set()
    run_ids: set[str] = set()
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
        raise BenchError("frozen schedule is not the exact workflow grid")
    if workflow == FULL_WORKFLOW:
        permutation_counts: Counter[tuple[str, ...]] = Counter()
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
            raise BenchError(
                "frozen schedule must balance all six arm permutations exactly 15 times"
            )

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
        repair_model=repair_model,
        workflow=workflow,
        parallel_width=parallel_width,
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
        "workflow": schedule["configuration"]["workflow"],
        "workflow_fixture_ids_sha256": schedule["configuration"][
            "workflow_fixture_ids_sha256"
        ],
        "parallel_width": schedule["configuration"]["parallel_width"],
        "configured_global_width": schedule["configuration"][
            "configured_global_width"
        ],
        "parallel_width_scope": schedule["configuration"]["parallel_width_scope"],
        "candidate_sha256": candidate["sha256"],
        "controller_sha256": schedule["configuration"]["controller"]["sha256"],
        "success": None,
        "score": None,
        "scoring_status": "deferred",
    }


def _valid_nonnegative_number(value: Any) -> bool:
    return (
        type(value) in (int, float)
        and math.isfinite(float(value))
        and value >= 0
    )


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


class ParallelBatchClock:
    """Thread-safe controller authority for one fixed-width inference batch."""

    def __init__(self, configured_width: int) -> None:
        if configured_width != PARALLEL_WIDTH:
            raise BenchError(
                f"parallel width is frozen at exactly {PARALLEL_WIDTH} globally"
            )
        self.configured_width = configured_width
        self.started_perf_ns = time.perf_counter_ns()
        self.started_unix = time.time()
        self.active = 0
        self.lock = threading.Lock()

    def begin(self) -> tuple[int, int]:
        with self.lock:
            self.active += 1
            if self.active > self.configured_width:
                self.active -= 1
                raise BenchError("global parallel width exceeded its frozen limit")
            return self.active, time.perf_counter_ns() - self.started_perf_ns

    def finish(self, active_at_start: int, started_offset_ns: int) -> dict[str, Any]:
        with self.lock:
            finished_offset_ns = time.perf_counter_ns() - self.started_perf_ns
            self.active -= 1
            if self.active < 0:
                raise BenchError("parallel activity counter underflowed")
        start_ms = started_offset_ns / 1_000_000.0
        end_ms = finished_offset_ns / 1_000_000.0
        return {
            "schema_version": 1,
            "configured_global_width": self.configured_width,
            "scope": PARALLEL_WIDTH_SCOPE,
            "observed_active_at_start": active_at_start,
            "observed_peak_concurrency": None,
            "batch_started_at_unix_s": self.started_unix,
            "monotonic_arm_start_offset_ms": start_ms,
            "monotonic_arm_end_offset_ms": end_ms,
            "controller_arm_wall_ms": end_ms - start_ms,
            "overall_makespan_ms": None,
            "authority": RUNNER_PARALLELISM_AUTHORITY,
        }


def validate_parallel_observation(value: Any, *, expected_width: int) -> None:
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
        or not _valid_nonnegative_number(value.get("batch_started_at_unix_s"))
        or not _valid_nonnegative_number(value.get("monotonic_arm_start_offset_ms"))
        or not _valid_nonnegative_number(value.get("monotonic_arm_end_offset_ms"))
        or not _valid_nonnegative_number(value.get("controller_arm_wall_ms"))
        or not _valid_nonnegative_number(value.get("overall_makespan_ms"))
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
        raise BenchError("runner parallelism observation is invalid")


def finalize_parallel_batch_rows(
    rows: Sequence[dict[str, Any]], *, expected_width: int
) -> dict[str, Any]:
    """Set immutable batch totals before the first append, then self-validate."""
    if not rows:
        raise BenchError("parallel batch has no returned rows")
    observations: list[dict[str, Any]] = []
    for row in rows:
        evidence = row.get("arm_evidence")
        observation = evidence.get("runner_parallelism") if isinstance(evidence, dict) else None
        if not isinstance(observation, dict) or set(observation) != RUNNER_PARALLELISM_KEYS:
            raise BenchError("parallel worker omitted its controller interval")
        observations.append(observation)
    starts = [item["monotonic_arm_start_offset_ms"] for item in observations]
    origins = {item["batch_started_at_unix_s"] for item in observations}
    if len(origins) != 1 or len(set(starts)) != len(starts):
        raise BenchError("parallel batch origin or arm start offsets are ambiguous")
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
            raise BenchError(
                "observed item concurrency disagrees with half-open controller intervals"
            )
        observed_peak = max(observed_peak, active)
        prior.append(item)
    overall_makespan_ms = max(
        item["monotonic_arm_end_offset_ms"] for item in observations
    )
    for item in observations:
        item["observed_peak_concurrency"] = observed_peak
        item["overall_makespan_ms"] = overall_makespan_ms
    return validate_terminal_parallel_batch(rows, expected_width=expected_width)


def validate_terminal_parallel_batch(
    rows: Sequence[dict[str, Any]], *, expected_width: int
) -> dict[str, Any]:
    """Independently recompute peak concurrency and global batch makespan."""
    observations: list[dict[str, Any]] = []
    for row in rows:
        evidence = row.get("arm_evidence")
        observation = evidence.get("runner_parallelism") if isinstance(evidence, dict) else None
        validate_parallel_observation(observation, expected_width=expected_width)
        observations.append(observation)
    if not observations:
        raise BenchError("terminal parallel batch has no observations")
    origins = {item["batch_started_at_unix_s"] for item in observations}
    starts = [item["monotonic_arm_start_offset_ms"] for item in observations]
    peaks = {item["observed_peak_concurrency"] for item in observations}
    makespans = {item["overall_makespan_ms"] for item in observations}
    if (
        len(origins) != 1 or len(set(starts)) != len(starts)
        or len(peaks) != 1 or len(makespans) != 1
    ):
        raise BenchError("parallel batch totals or interval identities are ambiguous")
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
            raise BenchError(
                "observed item concurrency disagrees with half-open controller intervals"
            )
        observed_peak = max(observed_peak, active)
        prior.append(item)
    overall_makespan_ms = max(
        item["monotonic_arm_end_offset_ms"] for item in observations
    )
    if peaks != {observed_peak} or makespans != {overall_makespan_ms}:
        raise BenchError("recorded peak concurrency or makespan does not recompute exactly")
    return {
        "configured_global_width": expected_width,
        "scope": PARALLEL_WIDTH_SCOPE,
        "observed_peak_concurrency": observed_peak,
        "overall_makespan_ms": overall_makespan_ms,
        "authority": RUNNER_PARALLELISM_AUTHORITY,
    }


def validate_performance_ledger(
    ledger: Any,
    evidence: Any,
    *,
    candidate: bool,
    successful: bool,
    expected_parallel_width: int = PARALLEL_WIDTH,
    expected_active_at_start: int | None = None,
) -> None:
    evidence_keys = {"applicable", "asserted", "authority", "raw_runtime", "reasons"}
    if (
        not isinstance(evidence, dict)
        or set(evidence) != evidence_keys
        or type(evidence.get("applicable")) is not bool
        or type(evidence.get("asserted")) is not bool
        or not isinstance(evidence.get("authority"), str)
        or not isinstance(evidence.get("reasons"), list)
        or any(not isinstance(reason, str) for reason in evidence["reasons"])
    ):
        raise BenchError("performance ledger assertion shape is invalid")
    if not candidate:
        expected = {
            "applicable": False,
            "asserted": True,
            "authority": "not applicable to control arm",
            "raw_runtime": None,
            "reasons": [],
        }
        if ledger is not None or evidence != expected:
            raise BenchError("control arm claimed invalid Azdaja performance evidence")
        return
    if evidence["applicable"] is not True:
        raise BenchError("Azdaja performance ledger is not marked applicable")
    if ledger is None:
        if evidence["asserted"] or successful:
            raise BenchError("successful Azdaja row lacks a performance ledger")
        return
    keys = {
        "schema_version", "complete", "root_turn_count", "root_inference_ms",
        "exec_invocation_count", "exec_wall_ms", "snapshot_save_count",
        "snapshot_save_ms", "snapshot_load_count", "snapshot_load_ms",
        "sub_call_count", "sub_call_turn_count", "sub_call_wall_ms",
        "repair_count", "repair_cost", "configured_global_width",
        "parallel_width_scope", "observed_active_at_start",
    }
    count_keys = {
        "root_turn_count", "root_inference_ms", "exec_invocation_count",
        "snapshot_save_count", "snapshot_load_count", "sub_call_count",
        "sub_call_turn_count", "repair_count",
    }
    if (
        not isinstance(ledger, dict)
        or set(ledger) != keys
        or ledger.get("schema_version") != 1
        or type(ledger.get("complete")) is not bool
        or ledger.get("configured_global_width") != expected_parallel_width
        or ledger.get("parallel_width_scope") != PARALLEL_WIDTH_SCOPE
        or type(ledger.get("observed_active_at_start")) is not int
        or not 1 <= ledger["observed_active_at_start"] <= expected_parallel_width
        or (
            expected_active_at_start is not None
            and ledger["observed_active_at_start"] != expected_active_at_start
        )
        or any(_uint(ledger.get(key)) is None for key in count_keys)
        or any(not _valid_nonnegative_number(ledger.get(key)) for key in (
            "exec_wall_ms", "snapshot_save_ms", "snapshot_load_ms",
            "sub_call_wall_ms",
        ))
    ):
        raise BenchError("performance ledger shape or timing value is invalid")
    cost = ledger["repair_cost"]
    cost_keys = {
        "inference_ms", "input_tokens", "output_tokens", "cache_read_tokens",
        "token_accounting_complete",
    }
    if (
        not isinstance(cost, dict)
        or set(cost) != cost_keys
        or _uint(cost.get("inference_ms")) is None
        or type(cost.get("token_accounting_complete")) is not bool
    ):
        raise BenchError("performance repair cost is invalid")
    token_values = [cost.get(key) for key in (
        "input_tokens", "output_tokens", "cache_read_tokens"
    )]
    if cost["token_accounting_complete"]:
        if any(_uint(value) is None for value in token_values):
            raise BenchError("complete repair token cost is invalid")
    elif any(value is not None for value in token_values):
        raise BenchError("incomplete repair token cost must fail closed to null")
    if ledger["complete"] != evidence["asserted"] or (successful and not ledger["complete"]):
        raise BenchError("performance ledger completeness disagrees with execution")


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
        arm_evidence = row.get("arm_evidence")
        if not isinstance(arm_evidence, dict):
            raise BenchError(f"inference row {line_number} arm evidence is invalid")
        try:
            parallel_observation = arm_evidence.get("runner_parallelism")
            validate_parallel_observation(
                parallel_observation,
                expected_width=schedule["configuration"]["parallel_width"],
            )
            validate_performance_ledger(
                arm_evidence.get("performance_ledger"),
                arm_evidence.get("performance_ledger_assertion"),
                candidate=row["arm"] == "jcode-azdaja",
                successful=row["execution_success"],
                expected_parallel_width=schedule["configuration"]["parallel_width"],
                expected_active_at_start=parallel_observation["observed_active_at_start"],
            )
        except BenchError as exc:
            raise BenchError(
                f"inference row {line_number} has invalid performance evidence: {exc}"
            ) from exc
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
    if len(rows) == len(schedule["jobs"]):
        validate_terminal_parallel_batch(
            rows, expected_width=schedule["configuration"]["parallel_width"]
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


SOLO_RUNTIME_KEYS = {
    "schema_version", "event", "request_id", "outcome",
    "exec_invocation_count", "exec_wall_ns",
    "snapshot_save_count", "snapshot_save_wall_ns",
    "snapshot_load_count", "snapshot_load_wall_ns",
    "sub_call_count", "sub_call_wall_ns",
}
MODEL_TRACE_KEYS = {
    "schema_version", "event", "timestamp_ms", "depth", "request_id",
    "attempt", "entered_turn", "session_id", "category", "outcome",
    "error", "error_category", "stage", "setup_substage", "provider", "model",
    "input_tokens", "output_tokens", "cache_read_tokens", "latency_ms",
    "degraded_transport", "failed_attempts_before_success", "response",
}
MODEL_TRACE_REQUIRED = {
    "schema_version", "event", "timestamp_ms", "depth", "request_id",
    "attempt", "session_id", "category", "outcome",
}


def _uint(value: Any, *, positive: bool = False) -> int | None:
    if type(value) is not int or value < (1 if positive else 0):
        return None
    return value


def parse_performance_ledger(
    model_trace_path: Path | None,
    solo_trace_path: Path | None,
    *,
    parallel_width: int = PARALLEL_WIDTH,
    parallel_active_at_start: int = 1,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Build one strict per-item ledger from the two existing product traces.

    Provider-attempt rows remain authority for model time and tokens. The exact
    final solo-runtime record contributes only monotonic internal spans which the
    provider trace cannot observe. Any ambiguity returns no normalized ledger.
    """
    if parallel_width != PARALLEL_WIDTH or not (
        type(parallel_active_at_start) is int
        and 1 <= parallel_active_at_start <= parallel_width
    ):
        raise BenchError("performance ledger parallel observation is invalid")
    evidence: dict[str, Any] = {
        "asserted": False,
        "authority": (
            "AZDAJA_MODEL_TRACE v2 provider attempts plus the unique absolute-EOF "
            "AZDAJA_SOLO_TRACE solo_runtime v1 record"
        ),
        "raw_runtime": None,
        "reasons": [],
    }
    if model_trace_path is None or solo_trace_path is None:
        evidence["reasons"].append("required model or solo trace path is unavailable")
        return None, evidence
    try:
        model_text = read_owner_file_once(
            model_trace_path, "performance model trace", exact_mode=0o600
        ).decode("utf-8")
        solo_text = read_owner_file_once(
            solo_trace_path, "performance solo trace", exact_mode=0o600
        ).decode("utf-8")
    except (BenchError, UnicodeError, OSError) as exc:
        evidence["reasons"].append(f"secure trace read failed: {type(exc).__name__}: {exc}")
        return None, evidence

    solo_lines = solo_text.splitlines()
    if len(solo_lines) < 3:
        evidence["reasons"].append("solo runtime footer is missing")
        return None, evidence
    try:
        runtime = json.loads(solo_lines[-2])
    except json.JSONDecodeError:
        runtime = None
    if not isinstance(runtime, dict):
        evidence["reasons"].append("absolute-EOF solo runtime row is not JSON object")
        return None, evidence
    evidence["raw_runtime"] = runtime
    request_id = runtime.get("request_id")
    if (
        set(runtime) != SOLO_RUNTIME_KEYS
        or runtime.get("schema_version") != 1
        or runtime.get("event") != "solo_runtime"
        or runtime.get("outcome") not in {"succeeded", "failed"}
        or not isinstance(request_id, str)
        or re.fullmatch(r"[0-9]+-[0-9]+-[0-9]+", request_id) is None
    ):
        evidence["reasons"].append("solo runtime row shape or correlation key is invalid")
        return None, evidence
    expected_begin = f'=== solo runtime trace begin request_id="{request_id}" ==='
    expected_end = f'=== solo runtime trace end request_id="{request_id}" ==='
    if solo_lines[-3] != expected_begin or solo_lines[-1] != expected_end:
        evidence["reasons"].append("solo runtime row is not in its exact absolute-EOF envelope")
        return None, evidence
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
        evidence["reasons"].append("solo runtime row is missing, duplicated, or spoof-ambiguous")
        return None, evidence
    counter_keys = {
        "exec_invocation_count", "exec_wall_ns", "snapshot_save_count",
        "snapshot_save_wall_ns", "snapshot_load_count", "snapshot_load_wall_ns",
        "sub_call_count", "sub_call_wall_ns",
    }
    if any(_uint(runtime.get(key)) is None for key in counter_keys):
        evidence["reasons"].append("solo runtime counters are not nonnegative integers")
        return None, evidence
    if runtime["sub_call_wall_ns"] > runtime["exec_wall_ns"]:
        evidence["reasons"].append("child-call wall exceeds its containing exec wall")
        return None, evidence

    raw_model_lines = [line for line in model_text.splitlines() if line.strip()]
    if not raw_model_lines:
        evidence["reasons"].append("model trace has no rows")
        return None, evidence
    model_rows: list[dict[str, Any]] = []
    for line in raw_model_lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            evidence["reasons"].append("model trace contains malformed JSON")
            return None, evidence
        if (
            not isinstance(row, dict)
            or not MODEL_TRACE_REQUIRED.issubset(row)
            or not set(row).issubset(MODEL_TRACE_KEYS)
            or row.get("schema_version") != 2
            or row.get("event") != "model_attempt"
            or _uint(row.get("timestamp_ms")) is None
            or _uint(row.get("depth")) is None
            or _uint(row.get("attempt"), positive=True) is None
            or not isinstance(row.get("request_id"), str)
            or not row["request_id"]
            or row.get("category") not in {"session_setup", "turn", "repair"}
            or row.get("outcome") not in {"failed", "succeeded"}
        ):
            evidence["reasons"].append("model trace contains a structurally invalid row")
            return None, evidence
        if row["category"] in {"turn", "repair"} and (
            _uint(row.get("entered_turn"), positive=True) is None
            or _uint(row.get("latency_ms")) is None
        ):
            evidence["reasons"].append("entered model turn lacks ordinal or latency")
            return None, evidence
        model_rows.append(row)

    root_rows = [
        row for row in model_rows
        if row["depth"] == 0 and row["category"] in {"turn", "repair"}
    ]
    initial_root_rows = [row for row in root_rows if row["category"] == "turn"]
    if not initial_root_rows or any(row["request_id"] != request_id for row in initial_root_rows):
        evidence["reasons"].append("runtime request_id is not bound to every initial root turn")
        return None, evidence
    entered_ordinals = [row["entered_turn"] for row in root_rows]
    if sorted(entered_ordinals) != list(range(1, len(root_rows) + 1)):
        evidence["reasons"].append("root entered-turn ordinals are duplicated or noncontiguous")
        return None, evidence

    repair_rows = [row for row in root_rows if row["category"] == "repair"]
    repair_suffixes = [
        row["request_id"].removeprefix(request_id + "-repair-")
        for row in repair_rows
    ]
    if repair_suffixes != [str(index) for index in range(1, len(repair_rows) + 1)]:
        evidence["reasons"].append("repair rows are not a unique contiguous root sequence")
        return None, evidence
    sub_request_ids = {row["request_id"] for row in model_rows if row["depth"] > 0}
    sub_turn_rows = [
        row for row in model_rows
        if row["depth"] > 0 and row["category"] in {"turn", "repair"}
    ]
    if len(sub_request_ids) != runtime["sub_call_count"]:
        evidence["reasons"].append("logical child-call count disagrees with model trace")
        return None, evidence

    repair_usage_complete = all(
        row["outcome"] == "succeeded"
        and all(_uint(row.get(key)) is not None for key in (
            "input_tokens", "output_tokens", "cache_read_tokens"
        ))
        for row in repair_rows
    )
    repair_cost = {
        "inference_ms": sum(row["latency_ms"] for row in repair_rows),
        "input_tokens": (
            sum(row["input_tokens"] for row in repair_rows)
            if repair_usage_complete else None
        ),
        "output_tokens": (
            sum(row["output_tokens"] for row in repair_rows)
            if repair_usage_complete else None
        ),
        "cache_read_tokens": (
            sum(row["cache_read_tokens"] for row in repair_rows)
            if repair_usage_complete else None
        ),
        "token_accounting_complete": repair_usage_complete,
    }
    complete = runtime["outcome"] == "succeeded"
    if complete and (
        runtime["snapshot_save_count"] != 1
        or runtime["snapshot_load_count"] != len(repair_rows)
        or not 1 <= runtime["exec_invocation_count"] <= 1 + len(repair_rows)
    ):
        evidence["reasons"].append("successful runtime count identities are inconsistent")
        return None, evidence
    ledger = {
        "schema_version": 1,
        "complete": complete,
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
    evidence["asserted"] = complete
    return ledger, evidence


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


def capture_trace_artifact_secure(
    path: Path, label: str, *, preserve_exact: bool = False
) -> dict[str, Any]:
    """Seal one stopped-writer trace through a single O_NOFOLLOW fd.

    The solo transcript is an exact audit authority. It is never normalized or
    rewritten; capture fails if the credential scanner would have changed it.
    """
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
        if preserve_exact and redacted != raw:
            raise BenchError(
                f"{label} contains credential-shaped text and cannot be retained as exact audit evidence"
            )
        sealed = raw if preserve_exact else redacted
        if sealed != raw:
            os.lseek(fd, 0, os.SEEK_SET)
            os.ftruncate(fd, 0)
            view = memoryview(sealed)
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
            or final.st_size != len(sealed)
        ):
            raise BenchError(f"{label} path identity changed during capture")
    finally:
        os.close(fd)
    return {
        "path": str(path),
        "sha256": sha256_bytes(sealed),
        "bytes": len(sealed),
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
    parallel_width: int = PARALLEL_WIDTH,
    parallel_active_at_start: int = 1,
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
                    trace_path, trace_name,
                    preserve_exact=(trace_name == "azdaja_solo_trace"),
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
    if job["arm"] == "jcode-azdaja":
        performance_ledger, performance_evidence = parse_performance_ledger(
            model_trace_path if "azdaja_model_trace" in trace_captured else None,
            trace_paths.get("azdaja_solo_trace")
            if "azdaja_solo_trace" in trace_captured else None,
            parallel_width=parallel_width,
            parallel_active_at_start=parallel_active_at_start,
        )
        performance_evidence["applicable"] = True
    else:
        performance_ledger = None
        performance_evidence = {
            "applicable": False,
            "asserted": True,
            "authority": "not applicable to control arm",
            "raw_runtime": None,
            "reasons": [],
        }
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
    root_leak_audit: dict[str, Any] = {
        "applicable": job["arm"] == "jcode-azdaja",
        "scanned": False,
        "detected": False,
        "minimum_match_chars": ROOT_LEAK_MIN_CHARS,
        "matched_text_retained": False,
        "missing_reason": (
            "AZDAJA_SOLO_TRACE was not captured"
            if job["arm"] == "jcode-azdaja" else "not applicable to control arm"
        ),
    }
    if job["arm"] == "jcode-azdaja" and "azdaja_solo_trace" in trace_captured:
        solo_path = trace_paths["azdaja_solo_trace"]
        try:
            solo_data = read_owner_file_once(
                solo_path, "exact AZDAJA_SOLO_TRACE", exact_mode=0o600
            )
            root_leak_audit = root_context_leak_audit(fixture.payload_data, solo_data)
        except Exception as exc:
            root_leak_audit["missing_reason"] = f"exact solo trace scan failed: {type(exc).__name__}: {exc}"
            cleanup_errors.append(root_leak_audit["missing_reason"])
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
        and performance_evidence.get("asserted") is True
        and (job["arm"] != "jcode-azdaja" or (
            root_leak_audit.get("scanned") is True
            and root_leak_audit.get("detected") is False
        ))
        and payload_asserted
        and skill_asserted
        and tool_policy.get("asserted") is True
    )
    failure: dict[str, Any] | None = None
    if not execution_success:
        if root_leak_audit.get("detected") is True:
            kind, message = (
                "root_context_leak",
                f"exact public payload and root transcript share at least {ROOT_LEAK_MIN_CHARS} Unicode characters",
            )
        elif execution_error is not None:
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
        elif performance_evidence.get("asserted") is not True:
            kind, message = "performance_trace", "per-item timing ledger was missing, partial, or inconsistent"
        elif job["arm"] == "jcode-azdaja" and root_leak_audit.get("scanned") is not True:
            kind, message = "trace_capture", "exact root-context leak scan was unavailable"
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
            "performance_ledger": performance_ledger,
            "performance_ledger_assertion": performance_evidence,
            "root_context_leak": root_leak_audit,
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


def _controller_failure_execution(
    job: dict[str, Any], work_root: Path, message: str
) -> dict[str, Any]:
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
    return {
        "execution_success": False,
        "timed_out": False,
        "exit_code": None,
        "latency_seconds": 0.0,
        "response": "",
        "route_assertion": {
            "asserted": False,
            "subscription": False,
            "provider": (
                "OpenAI OAuth" if job["arm"].startswith("jcode") else "openai-codex"
            ),
            "model": MODEL,
        },
        "usage": None,
        "lifecycle_assertion": {
            "asserted": False,
            "isolated_home": False,
            "fresh_session": False,
            "cleanup_complete": False,
        },
        "failure": {"kind": "controller", "message": message},
        "arm_evidence": {
            "controller_exception": message,
            "trajectory_artifacts": emergency_artifacts,
            "performance_ledger": None,
            "performance_ledger_assertion": {
                "applicable": job["arm"] == "jcode-azdaja",
                "asserted": job["arm"] != "jcode-azdaja",
                "authority": (
                    "controller exception occurred before ledger collection"
                    if job["arm"] == "jcode-azdaja"
                    else "not applicable to control arm"
                ),
                "raw_runtime": None,
                "reasons": (
                    ["controller exception occurred before ledger collection"]
                    if job["arm"] == "jcode-azdaja" else []
                ),
            },
            "telemetry_authority": {
                "route_and_usage": (
                    "mandatory empty stdout artifact after controller failure"
                ),
                "process": "controller assertion",
                "controller_fields_are_assertions": True,
            },
            "staged_filename": job["staged_filename"],
        },
        "containment": {
            "os_level_asserted": False,
            "disclaimer": "controller failure; no OS-level containment is asserted",
            "claim_ledger": (
                "local append-only creation protocol is not authenticated against malicious "
                "same-owner deletion/retry; external signing or transparency is future work"
            ),
        },
    }


def execute_claimed_job(
    *,
    job: dict[str, Any],
    fixture: PublicFixture,
    schedule: dict[str, Any],
    args: argparse.Namespace,
    source_home: Path,
    skill: Path,
    auth_jcode: dict[str, Any],
    auth_prime: dict[str, Any],
    work_root: Path,
    claims: Path,
    candidate: dict[str, Any],
    controller: dict[str, Any],
    executables: dict[str, Any],
    batch_clock: ParallelBatchClock,
) -> dict[str, Any]:
    """Claim and execute exactly one turn; never append, retry, or resubmit it."""
    active_at_start, started_offset = batch_clock.begin()
    try:
        # Shared inputs are read-only snapshots; each worker independently checks
        # them before its exclusive claim and owns every mutable run path it uses.
        if controller_identity().get("sha256") != controller.get("sha256"):
            raise BenchError("controller identity drifted after schedule freeze")
        validate_candidate_snapshot(candidate)
        for label, frozen in executables.items():
            path = Path(frozen["path"])
            frozen_data = read_owner_file_once(
                path, f"immutable {label} executable snapshot", exact_mode=0o500
            )
            if (
                len(frozen_data) != frozen["bytes"]
                or sha256_bytes(frozen_data) != frozen["sha256"]
            ):
                raise BenchError(
                    f"{label} immutable executable snapshot drifted after schedule freeze"
                )
            if label == "prime-agent":
                validate_prime_bundle_identity(frozen.get("bundle"), path)
        if (
            sha256_bytes(fixture.payload_data) != fixture.payload_sha256
            or len(fixture.payload_data) != fixture.payload_bytes
        ):
            raise BenchError("captured scheduled payload identity drifted")
        claim_path = claims / f"{job['run_id']}.json"
        done_path = claims / f"{job['run_id']}.done.json"
        if (
            claim_path.exists() or claim_path.is_symlink()
            or done_path.exists() or done_path.is_symlink()
        ):
            raise BenchError(
                "orphan claim/completion makes execution indeterminate; refusing "
                f"duplicate inference: {job['run_id']}"
            )
        atomic_create_private_json(claim_path, {
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "ordinal": job["ordinal"],
            "pid": os.getpid(),
        })
        try:
            execution = execute_product_arm(
                job=job,
                fixture=fixture,
                args=args,
                source_home=source_home,
                skill=skill,
                auth_jcode=auth_jcode,
                auth_prime=auth_prime,
                work_root=work_root,
                parallel_width=schedule["configuration"]["parallel_width"],
                parallel_active_at_start=active_at_start,
            )
        except Exception as exc:
            execution = _controller_failure_execution(
                job, work_root, f"{type(exc).__name__}: {exc}"
            )
        row = {**_expected_envelope(schedule, job), **execution}
    finally:
        observation = batch_clock.finish(active_at_start, started_offset)
    # If setup/claim failed, the exception propagates after the activity counter
    # is closed and no row is fabricated.  If a claimed turn returned, attach the
    # controller interval before handing the row to the sole append coordinator.
    row["arm_evidence"]["runner_parallelism"] = observation
    return row


def execute_fixed_width_ordered(
    jobs: Sequence[dict[str, Any]],
    *,
    worker: Any,
    finalize: Any,
    commit: Any,
    width: int,
) -> None:
    """Run one predeclared global queue and commit only after batch totals freeze."""
    if width != PARALLEL_WIDTH:
        raise BenchError(f"parallel width is frozen at exactly {PARALLEL_WIDTH} globally")
    if [job.get("ordinal") for job in jobs] != list(range(1, len(jobs) + 1)):
        raise BenchError("parallel queue is not the exact ordinal schedule")
    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=width, thread_name_prefix="ruler-item"
    )
    futures: list[concurrent.futures.Future[Any]] = []
    failed = False
    try:
        futures = [executor.submit(worker, job) for job in jobs]
        rows = [future.result() for future in futures]
        finalize(rows)
        for job, row in zip(jobs, rows):
            commit(job, row)
    except BaseException:
        failed = True
        for future in futures:
            future.cancel()
        raise
    finally:
        executor.shutdown(wait=True, cancel_futures=failed)


def run_suite(args: argparse.Namespace, suite: PublicSuite) -> int:
    if not args.yes_run_inference:
        raise BenchError("refusing to run inference without --yes-run-inference")
    if args.timeout != 1800:
        raise BenchError("--timeout is frozen at exactly 1800 seconds")
    if args.workflow not in WORKFLOWS:
        raise BenchError(f"unknown frozen RULER workflow: {args.workflow!r}")
    if args.resume:
        raise BenchError(
            "fixed-width workflows are fresh-only; --resume is forbidden because "
            "an orphan parallel claim may already have performed inference"
        )
    args.parallel_width = PARALLEL_WIDTH
    output = Path(args.output).expanduser().resolve()
    schedule_path = Path(str(output) + ".schedule.json")
    claims_root = Path(str(output) + ".claims")
    work_base = (
        Path(args.work_dir).expanduser().resolve()
        if args.work_dir else Path(str(output) + ".artifacts")
    )
    if output in {suite.path, *(fixture.payload_path for fixture in suite.fixtures)}:
        raise BenchError("--output must not overwrite any sealed public artifact")
    for path, label in (
        (output, "inference output"),
        (schedule_path, "schedule"),
        (claims_root, "claims root"),
        (work_base, "artifact root"),
    ):
        if path.exists() or path.is_symlink():
            raise BenchError(f"fresh {label} path must not exist: {path}")

    home_raw = os.environ.get("HOME")
    if not home_raw:
        raise BenchError("HOME must identify the login home containing subscription OAuth")
    source_home = Path(home_raw).expanduser().resolve(strict=True)
    if not source_home.is_dir():
        raise BenchError("HOME must identify a directory")
    args.jcode = OOLONG.ensure_executable(args.jcode, "jcode")
    source_jcode = args.jcode
    skill = OOLONG.validate_skill(args.azdaja_skill)
    source_executables = {
        "jcode": OOLONG.executable_identity(args.jcode, "jcode"),
        "azdaja": OOLONG.executable_identity(str(skill / "azdaja"), "azdaja"),
    }
    if args.workflow == FULL_WORKFLOW:
        args.prime_agent = OOLONG.ensure_executable(args.prime_agent, "prime-agent")
        source_executables["prime-agent"] = OOLONG.executable_identity(
            args.prime_agent, "prime-agent"
        )
    args.executable_identities = source_executables
    candidate_source_path = str(skill)
    source_controller = controller_identity()

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
    repair_model = candidate_repair_model(frozen_skill)
    OOLONG.configure_azdaja_repair_model(repair_model)
    args.azdaja_repair_model = repair_model
    controller, controller_source_paths = snapshot_controller(controller_root)
    executables = snapshot_executables(source_executables, executable_root)
    validate_candidate_executable_binding(candidate, executables)
    if controller["sha256"] != source_controller["sha256"]:
        raise BenchError("immutable controller snapshot differs from active source")
    schedule = build_schedule(
        suite,
        seed=args.seed,
        timeout=args.timeout,
        candidate=candidate,
        candidate_source_path=candidate_source_path,
        controller=controller,
        controller_source_paths=controller_source_paths,
        executables=executables,
        repair_model=repair_model,
        workflow=args.workflow,
        parallel_width=args.parallel_width,
    )
    validate_schedule(
        schedule,
        suite,
        seed=args.seed,
        timeout=args.timeout,
        candidate=candidate,
        candidate_source_path=candidate_source_path,
        controller=controller,
        controller_source_paths=controller_source_paths,
        executables=executables,
        repair_model=repair_model,
        workflow=args.workflow,
        parallel_width=args.parallel_width,
    )
    atomic_create_private_json(schedule_path, schedule)

    if OOLONG.validate_skill(str(frozen_skill)) != frozen_skill:
        raise BenchError("frozen candidate validation returned an unexpected path")
    skill = frozen_skill
    args.frozen_executables = executables
    args.executable_identities = executables
    args.jcode = str(executables["jcode"]["path"])
    if "prime-agent" in executables:
        args.prime_agent = str(executables["prime-agent"]["path"])

    _create_private_directory(claims_root, "claims root", exist_ok=False)
    claims = claims_root / schedule["schedule_id"]
    _create_private_directory(claims, "schedule claims directory", exist_ok=False)
    completed, output_state = validate_result_prefix(output, schedule, claims)
    if completed or output_state is not None:
        raise BenchError("fresh fixed-width workflow unexpectedly has a result prefix")

    # Subscription checks are serialized and occur once before worker launch.
    # Workers copy the resulting source credentials into distinct isolated homes;
    # no refresh, relogin, or shared preflight subprocess races with inference.
    auth_jcode = OOLONG.preflight_jcode(source_home, source_jcode)
    scheduled_arms = {job["arm"] for job in schedule["jobs"]}
    if "prime-agent" in scheduled_arms:
        auth_prime = OOLONG.preflight_prime(source_home)
        kernel_python = (
            source_home / ".prime" / "agent" / "kernel-venv" / "bin" / "python"
        )
        if not kernel_python.is_file() or not os.access(kernel_python, os.X_OK):
            raise BenchError(f"Prime Agent kernel venv is not ready: {kernel_python}")
    else:
        auth_prime = {"asserted": False, "method": "not-scheduled"}

    schedule_root = work_base / f"schedule-{schedule['schedule_id']}"
    _create_private_directory(
        schedule_root, "schedule artifact directory", exist_ok=False
    )
    work_root = schedule_root / "runs"
    _create_private_directory(work_root, "run artifact directory", exist_ok=False)
    by_id = {fixture.fixture_id: fixture for fixture in suite.fixtures}
    batch_clock = ParallelBatchClock(args.parallel_width)

    def worker(job: dict[str, Any]) -> dict[str, Any]:
        return execute_claimed_job(
            job=job,
            fixture=by_id[job["fixture_id"]],
            schedule=schedule,
            args=args,
            source_home=source_home,
            skill=skill,
            auth_jcode=auth_jcode,
            auth_prime=auth_prime,
            work_root=work_root,
            claims=claims,
            candidate=candidate,
            controller=controller,
            executables=executables,
            batch_clock=batch_clock,
        )

    def commit(job: dict[str, Any], row: dict[str, Any]) -> None:
        nonlocal output_state
        if row.get("run_id") != job["run_id"] or row.get("execution_ordinal") != job["ordinal"]:
            raise BenchError("parallel worker returned a row for the wrong frozen job")
        output_state = append_private_jsonl(
            output, row, expected_token=output_state
        )
        done_path = claims / f"{job['run_id']}.done.json"
        atomic_create_private_json(done_path, {
            "schedule_id": schedule["schedule_id"],
            "run_id": job["run_id"],
            "row_sha256": sha256_bytes(canonical_json_bytes(row)),
        })
        print(json.dumps({
            "ordinal": job["ordinal"],
            "fixture_id": job["fixture_id"],
            "arm": job["arm"],
            "execution_success": row["execution_success"],
            "scoring_status": "deferred",
            "latency_seconds": row["latency_seconds"],
            "observed_active_at_start": row["arm_evidence"]["runner_parallelism"][
                "observed_active_at_start"
            ],
        }, sort_keys=True), flush=True)

    execute_fixed_width_ordered(
        schedule["jobs"],
        worker=worker,
        finalize=lambda returned_rows: finalize_parallel_batch_rows(
            returned_rows, expected_width=args.parallel_width
        ),
        commit=commit,
        width=args.parallel_width,
    )
    rows, final_output_state = validate_result_prefix(output, schedule, claims)
    if final_output_state != output_state:
        raise BenchError("inference output state changed after final append")
    batch_performance = validate_terminal_parallel_batch(
        rows, expected_width=args.parallel_width
    )
    print(json.dumps({
        "record_type": "ruler_batch_performance",
        "schedule_id": schedule["schedule_id"],
        "workflow": args.workflow,
        **batch_performance,
    }, sort_keys=True), flush=True)
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
    value.add_argument("--output", required=True, help="fresh append-only JSONL")
    value.add_argument(
        "--workflow", choices=WORKFLOWS, default=FULL_WORKFLOW,
        help=(
            "frozen pre-inference workflow: official 90x3 cohort, candidate-only "
            "90-item performance run, or immutable 20-item candidate smoke slice"
        ),
    )
    value.add_argument(
        "--resume", action="store_true",
        help="legacy spelling retained only to fail closed; fixed-width runs are fresh-only",
    )
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
        help="required explicit acknowledgement that the frozen workflow will run model turns",
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
