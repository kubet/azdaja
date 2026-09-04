#!/usr/bin/env python3
"""Compare current notice inputs with the retained reviewed notice corpus.

This checker proves a narrow mechanical comparison only. It intentionally does
not update or authorize the notice's Cargo.lock binding, recompute retained
legal-text bodies, or make a legal conclusion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TARGETS = [
    "aarch64-apple-darwin",
    "x86_64-apple-darwin",
    "x86_64-unknown-linux-gnu",
]
HISTORICAL_START = "## Exact supported-target third-party union (root excluded)"
HISTORICAL_END = "## Lock records outside both supported closures"
ADDITIVE_START = "### Current-closure records absent from the historical inventory"
ADDITIVE_END = "### Additive legal file/header occurrence index"
MANIFEST_ONLY_START = "## Thirteen MIT-declared archives with no detected legal file"
MANIFEST_ONLY_END = "The machine manifest records the archive hash"
ROW_RE = re.compile(r"^\| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \|")
MANIFEST_ONLY_ROW_RE = re.compile(r"^\| `([^`]+)` \|")
LOCK_BINDING_RE = re.compile(
    r"Bound inputs: `Cargo\.lock` SHA-256 `([0-9a-f]{64})`"
)
SCHEMA = "azdaja.third_party_notice_reconciliation.v1"
STATUS = "inputs_compared_notice_binding_blocked"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def regular_file(path: Path, label: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{label} is missing, not regular, or symlinked: {path}")


def exact_section(text: str, start: str, end: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"notice section markers are missing or ambiguous: {start}")
    return text.split(start, 1)[1].split(end, 1)[0]


def normalized_license(cell: str) -> str:
    match = re.fullmatch(r'license = "([^"]+)"', cell)
    return match.group(1) if match else cell


def inventory_rows(text: str) -> Dict[Tuple[str, str], str]:
    rows: Dict[Tuple[str, str], str] = {}
    for section in (
        exact_section(text, HISTORICAL_START, HISTORICAL_END),
        exact_section(text, ADDITIVE_START, ADDITIVE_END),
    ):
        for line in section.splitlines():
            match = ROW_RE.match(line)
            if not match:
                continue
            name, version, license_cell = match.groups()
            key = (name, version)
            if key in rows:
                raise ValueError(f"duplicate notice inventory row: {name}@{version}")
            rows[key] = normalized_license(license_cell)
    if not rows:
        raise ValueError("notice inventory is empty")
    return rows


def manifest_only_rows(text: str) -> Set[Tuple[str, str]]:
    rows: Set[Tuple[str, str]] = set()
    section = exact_section(text, MANIFEST_ONLY_START, MANIFEST_ONLY_END)
    for line in section.splitlines():
        match = MANIFEST_ONLY_ROW_RE.match(line)
        if not match:
            continue
        cell = match.group(1)
        if " " not in cell:
            raise ValueError(f"manifest-only notice identity is malformed: {cell}")
        name, version = cell.rsplit(" ", 1)
        identity = (name, version)
        if identity in rows:
            raise ValueError(f"duplicate manifest-only notice row: {name}@{version}")
        rows.add(identity)
    if not rows:
        raise ValueError("manifest-only notice table is empty")
    return rows


def validate_manifest(document: object) -> List[dict]:
    if not isinstance(document, dict):
        raise ValueError("input manifest must be an object")
    required = {
        "cargo_lock_sha256",
        "claim",
        "manifest_only_records",
        "named_legal_files",
        "packages",
        "registry_lock_records",
        "schema",
        "supported_union_records",
        "target_counts",
        "targets",
    }
    if set(document) != required:
        raise ValueError("input manifest keys differ from the reviewed schema")
    if document["schema"] != "azdaja.third_party_notice_input_evidence.v1":
        raise ValueError("input manifest schema mismatch")
    if document["claim"] != (
        "source-input evidence only; does not establish notice semantic completeness"
    ):
        raise ValueError("input manifest claim boundary mismatch")
    if document["registry_lock_records"] != 247:
        raise ValueError("registry lock record count mismatch")
    if not isinstance(document["cargo_lock_sha256"], str) or not re.fullmatch(
        r"[0-9a-f]{64}", document["cargo_lock_sha256"]
    ):
        raise ValueError("input manifest lock digest is malformed")
    if document["targets"] != EXPECTED_TARGETS:
        raise ValueError("supported target list mismatch")
    if document["target_counts"] != {
        "aarch64-apple-darwin": 189,
        "x86_64-apple-darwin": 190,
        "x86_64-unknown-linux-gnu": 190,
    }:
        raise ValueError("supported target counts mismatch")
    packages = document["packages"]
    if not isinstance(packages, list):
        raise ValueError("input packages must be an array")
    if document["supported_union_records"] != len(packages) or len(packages) != 191:
        raise ValueError("supported union count mismatch")

    identities: Set[Tuple[str, str]] = set()
    legal_count = 0
    manifest_only = 0
    computed_target_counts = {target: 0 for target in EXPECTED_TARGETS}
    for package in packages:
        if not isinstance(package, dict):
            raise ValueError("package record must be an object")
        required_package = {
            "archive_sha256",
            "checksum",
            "license",
            "license_files",
            "manifest_sha256",
            "name",
            "source",
            "targets",
            "version",
        }
        if set(package) != required_package:
            raise ValueError("package record keys differ from the reviewed schema")
        name, version = package["name"], package["version"]
        if not isinstance(name, str) or not isinstance(version, str):
            raise ValueError("package identity is malformed")
        identity = (name, version)
        if identity in identities:
            raise ValueError(f"duplicate input package: {name}@{version}")
        identities.add(identity)
        if package["archive_sha256"] != package["checksum"]:
            raise ValueError(f"archive checksum drift: {name}@{version}")
        for digest_field in ("archive_sha256", "checksum", "manifest_sha256"):
            if not isinstance(package[digest_field], str) or not re.fullmatch(
                r"[0-9a-f]{64}", package[digest_field]
            ):
                raise ValueError(f"package digest is malformed: {name}@{version}")
        if package["source"] != (
            "registry+https://github.com/rust-lang/crates.io-index"
        ):
            raise ValueError(f"unexpected package source: {name}@{version}")
        if not isinstance(package["license"], str) or not package["license"]:
            raise ValueError(f"package license is malformed: {name}@{version}")
        targets = package["targets"]
        if not isinstance(targets, list) or not targets or any(
            target not in EXPECTED_TARGETS for target in targets
        ):
            raise ValueError(f"package target membership is malformed: {name}@{version}")
        if targets != [target for target in EXPECTED_TARGETS if target in targets]:
            raise ValueError(f"package target membership is not canonical: {name}@{version}")
        for target in targets:
            computed_target_counts[target] += 1
        legal_files = package["license_files"]
        if not isinstance(legal_files, list):
            raise ValueError(f"license_files is malformed: {name}@{version}")
        if not legal_files:
            manifest_only += 1
            if package["license"] != "MIT":
                raise ValueError(f"unexpected manifest-only license: {name}@{version}")
        for legal_file in legal_files:
            if not isinstance(legal_file, dict) or set(legal_file) != {
                "bytes",
                "path",
                "sha256",
            }:
                raise ValueError(f"legal file record is malformed: {name}@{version}")
            if not isinstance(legal_file["sha256"], str) or not re.fullmatch(
                r"[0-9a-f]{64}", legal_file["sha256"]
            ):
                raise ValueError(f"legal file digest is malformed: {name}@{version}")
            path = legal_file["path"]
            if (
                not isinstance(path, str)
                or not path
                or path.startswith("/")
                or "\\" in path
                or ".." in Path(path).parts
                or type(legal_file["bytes"]) is not int
                or legal_file["bytes"] < 0
            ):
                raise ValueError(f"legal file metadata is malformed: {name}@{version}")
            legal_count += 1
    if document["named_legal_files"] != legal_count or legal_count != 314:
        raise ValueError("named legal file count mismatch")
    if document["manifest_only_records"] != manifest_only or manifest_only != 13:
        raise ValueError("manifest-only exception count mismatch")
    if computed_target_counts != document["target_counts"]:
        raise ValueError("per-package target memberships do not match target counts")
    return packages


def canonical_commitment(packages: List[dict]) -> str:
    records = []
    for package in packages:
        for legal_file in package["license_files"]:
            records.append(
                {
                    "bytes": legal_file["bytes"],
                    "name": package["name"],
                    "path": legal_file["path"],
                    "sha256": legal_file["sha256"],
                    "version": package["version"],
                }
            )
    records.sort(
        key=lambda record: (
            record["name"],
            record["version"],
            record["path"],
            record["sha256"],
            record["bytes"],
        )
    )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(payload)


def reconcile(notice: Path, manifest: Path, lockfile: Path) -> dict:
    regular_file(notice, "notice")
    regular_file(manifest, "input manifest")
    regular_file(lockfile, "lockfile")
    notice_text = notice.read_text(encoding="utf-8")
    manifest_bytes = manifest.read_bytes()
    document = json.loads(manifest_bytes)
    packages = validate_manifest(document)

    actual_lock = sha256_bytes(lockfile.read_bytes())
    if document["cargo_lock_sha256"] != actual_lock:
        raise ValueError("input manifest is not bound to the current Cargo.lock")
    bindings = LOCK_BINDING_RE.findall(notice_text)
    if len(bindings) != 1:
        raise ValueError("notice must contain exactly one Cargo.lock binding")

    expected = {
        (package["name"], package["version"]): package["license"]
        for package in packages
    }
    observed = inventory_rows(notice_text)
    if set(observed) != set(expected):
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        raise ValueError(f"notice inventory identity mismatch: missing={missing}, extra={extra}")
    mismatched = sorted(
        identity
        for identity, license_expression in expected.items()
        if observed[identity] != license_expression
    )
    if mismatched:
        raise ValueError(f"notice inventory license mismatch: {mismatched}")

    legal_hashes = [
        legal_file["sha256"]
        for package in packages
        for legal_file in package["license_files"]
    ]
    missing_hashes = sorted(
        {
            digest
            for digest in legal_hashes
            if not re.search(
                rf"^###(?:#)? (?:Additive text|Text) `{digest}`$",
                notice_text,
                re.MULTILINE,
            )
        }
    )
    if missing_hashes:
        raise ValueError(f"notice is missing reviewed legal text hashes: {missing_hashes}")
    expected_manifest_only = {
        (package["name"], package["version"])
        for package in packages
        if not package["license_files"]
    }
    observed_manifest_only = manifest_only_rows(notice_text)
    if observed_manifest_only != expected_manifest_only:
        missing = sorted(expected_manifest_only - observed_manifest_only)
        extra = sorted(observed_manifest_only - expected_manifest_only)
        raise ValueError(
            f"manifest-only notice identity mismatch: missing={missing}, extra={extra}"
        )

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "authorization": "does not authorize a notice binding or publication change",
        "cargo_lock_sha256": actual_lock,
        "notice_bound_cargo_lock_sha256": bindings[0],
        "notice_binding_current": bindings[0] == actual_lock,
        "input_manifest_sha256": sha256_bytes(manifest_bytes),
        "packages_inventory_matched": len(packages),
        "legal_file_records_checked": len(legal_hashes),
        "unique_legal_hash_headings_found": len(set(legal_hashes)),
        "manifest_only_records_matched": len(observed_manifest_only),
        "legal_record_commitment_sha256": canonical_commitment(packages),
        "targets": EXPECTED_TARGETS,
    }


def render(document: dict) -> str:
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def write_atomic(path: Path, content: str) -> None:
    if path.exists() and (not path.is_file() or path.is_symlink()):
        raise ValueError(f"output is not a regular non-symlink file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notice", type=Path, default=ROOT / "THIRD-PARTY-NOTICES.md")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "release/third-party-notice-inputs.json",
    )
    parser.add_argument("--lockfile", type=Path, default=ROOT / "Cargo.lock")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "release/third-party-notice-reconciliation.json",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = reconcile(args.notice, args.manifest, args.lockfile)
        rendered = render(result)
        if args.check:
            regular_file(args.output, "reconciliation output")
            if args.output.read_text(encoding="utf-8") != rendered:
                raise ValueError("reconciliation output differs from current inputs")
        else:
            write_atomic(args.output, rendered)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"third-party notice reconciliation failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
