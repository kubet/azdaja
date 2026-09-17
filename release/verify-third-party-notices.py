#!/usr/bin/env python3
"""Verify the public current notice against offline Cargo closures and actual archives."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("current_notice", ROOT / "release/build-current-third-party-notice.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)
LOCK_BINDING = re.compile(r"Bound inputs: `Cargo\.lock` SHA-256 `([0-9a-f]{64})`")


def sha256(path):
    return BUILD.audit.sha256_bytes(path.read_bytes())


def regular_file(path, label):
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{label} is missing, not regular, or symlinked: {path}")


def compare_index(actual, expected):
    """Classify mismatches before the final byte-for-byte canonical comparison."""
    if not isinstance(actual, dict):
        raise ValueError("index must be an object")
    for key in ("cargo_lock_sha256", "cargo_manifest_sha256"):
        if actual.get(key) != expected[key]:
            raise ValueError(f"index input binding mismatch: {key}")
    for key in ("features", "targets", "feature_union_records", "target_counts", "supported_union_records"):
        if actual.get(key) != expected[key]:
            raise ValueError(f"index feature/target scope mismatch: {key}")
    packages = actual.get("packages")
    if not isinstance(packages, list) or len(packages) != len(expected["packages"]):
        raise ValueError("index package inventory mismatch")
    for package, source in zip(packages, expected["packages"]):
        if not isinstance(package, dict) or any(package.get(k) != source[k] for k in ("name", "version")):
            raise ValueError("index package identity/order mismatch")
        identity = f"{source['name']}@{source['version']}"
        for key, reason in (("license", "packaged license declaration"),
                            ("membership", "feature/target membership"),
                            ("archive_sha256", "archive checksum"),
                            ("checksum", "lock checksum"),
                            ("source", "registry source"),
                            ("manifest_sha256", "packaged manifest"),
                            ("license_files", "legal-file occurrence attribution")):
            if package.get(key) != source[key]:
                raise ValueError(f"index {reason} mismatch: {identity}")
    if actual.get("bodies") != expected["bodies"]:
        raise ValueError("index exact source text/byte metadata mismatch")
    if actual.get("historical") != expected["historical"]:
        raise ValueError("index historical attribution binding mismatch")
    if actual != expected:
        raise ValueError("index schema/metadata mismatch")


def compare_notice(actual, expected):
    if actual == expected:
        return
    # Rendering is compared in sections solely to provide specific diagnostics.
    # The whole-file comparison above and final rejection accept no alternate bytes.
    markers = ["## Current feature-qualified package union", "## Packages with no supplied named legal file",
               "## Supplied legal files (deduplicated bodies)", "## Occurrence attribution index",
               BUILD.HISTORY_HEADING]
    for marker in markers:
        if actual.count(marker) != 1:
            raise ValueError(f"notice section framing mismatch: {marker}")
    def sections(text):
        result = []
        for marker in markers:
            front, text = text.split(marker, 1)
            result.append(front)
        return result + [text]
    reasons = ["front matter/input binding", "feature scope/license table", "manifest-only attribution",
               "source legal text rendering", "occurrence attribution", "historical attribution"]
    for got, wanted, reason in zip(sections(actual), sections(expected), reasons):
        if got != wanted:
            raise ValueError(f"notice {reason} mismatch")
    raise ValueError("notice deterministic rendering mismatch")


def verify(notice, lockfile, index=None, cache=None):
    index = index or ROOT / "release/current-third-party-notice.json"
    for path, label in ((notice, "notice"), (lockfile, "lockfile"), (index, "index")):
        regular_file(path, label)
    # --lockfile is retained, but an alternate lock cannot substitute for the
    # manifest's actual lock used by Cargo tree. An identical copied lock is OK.
    if lockfile.read_bytes() != (ROOT / "Cargo.lock").read_bytes():
        raise ValueError("Cargo.lock hash mismatch: supplied lock differs from project lock")
    raw = notice.read_bytes()
    text = raw.decode("utf-8")
    bindings = LOCK_BINDING.findall(text)
    if len(bindings) != 1:
        raise ValueError(f"notice must contain exactly one Cargo.lock SHA-256 binding; found {len(bindings)}")
    if bindings[0] != sha256(lockfile):
        raise ValueError("Cargo.lock hash mismatch: notice binding")
    expected = BUILD.build(ROOT, cache)
    index_bytes = index.read_bytes()
    compare_index(json.loads(index_bytes), expected)
    if index_bytes != BUILD.audit.render(expected).encode("utf-8"):
        raise ValueError("index deterministic serialization mismatch")
    compare_notice(text, BUILD.render(expected, ROOT))
    return {"schema": "azdaja.third_party_notice_provenance.v2", "status": "current",
            "cargo_lock_sha256": sha256(lockfile), "feature_union_records": expected["feature_union_records"],
            "records": expected["supported_union_records"], "named_legal_files": expected["named_legal_files"],
            "historical_sha256": expected["historical"]["sha256"], "claim": expected["claim"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notice", type=Path, default=ROOT / "THIRD-PARTY-NOTICES.md")
    parser.add_argument("--lockfile", type=Path, default=ROOT / "Cargo.lock")
    parser.add_argument("--index", type=Path, default=ROOT / "release/current-third-party-notice.json")
    parser.add_argument("--cache", type=Path, default=Path.home() / ".cargo/registry/cache")
    args = parser.parse_args()
    try:
        result = verify(args.notice, args.lockfile, args.index, args.cache)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, subprocess.CalledProcessError, tarfile.TarError) as error:
        print(f"third-party notice verification failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
