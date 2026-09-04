#!/usr/bin/env python3
"""Fail closed when the reviewed notice is not bound to the current Cargo.lock."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_BINDING = re.compile(
    r"Bound inputs: `Cargo\.lock` SHA-256 `([0-9a-f]{64})`"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def regular_file(path: Path, label: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{label} is missing, not regular, or symlinked: {path}")


def verify(notice: Path, lockfile: Path) -> dict[str, object]:
    regular_file(notice, "notice")
    regular_file(lockfile, "lockfile")
    text = notice.read_text(encoding="utf-8")
    bindings = LOCK_BINDING.findall(text)
    if len(bindings) != 1:
        raise ValueError(
            f"notice must contain exactly one Cargo.lock SHA-256 binding; found {len(bindings)}"
        )
    bound = bindings[0]
    actual = sha256(lockfile)
    if bound != actual:
        raise ValueError(
            f"Cargo.lock hash mismatch: notice binds {bound}, current lock is {actual}"
        )
    return {
        "schema": "azdaja.third_party_notice_provenance.v1",
        "status": "current",
        "notice": str(notice),
        "lockfile": str(lockfile),
        "cargo_lock_sha256": actual,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notice", type=Path, default=ROOT / "THIRD-PARTY-NOTICES.md")
    parser.add_argument("--lockfile", type=Path, default=ROOT / "Cargo.lock")
    args = parser.parse_args()
    try:
        result = verify(args.notice, args.lockfile)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"third-party notice verification failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
