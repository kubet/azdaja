#!/usr/bin/env python3
"""Build fail-closed source-input evidence for the supported Cargo closure.

The resulting manifest inventories checksum-verified registry archives and their
packaged license metadata. It is evidence for a later reviewed notice
regeneration. It does not establish notice semantic completeness.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Optional

TARGETS = (
    "aarch64-apple-darwin",
    "x86_64-apple-darwin",
    "x86_64-unknown-linux-gnu",
)
REGISTRY = "registry+https://github.com/rust-lang/crates.io-index"
TREE_RE = re.compile(r"^(?P<name>[A-Za-z0-9_.+-]+) v(?P<version>\S+)")
LEGAL_RE = re.compile(
    r"^(?:licen[cs]e|copying|copyright|notice|authors|unlicense)(?:[._-].*)?$",
    re.IGNORECASE,
)
CLAIM = "source-input evidence only; does not establish notice semantic completeness"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def toml_string(text: str, key: str) -> Optional[str]:
    pattern = re.compile(
        rf'^\s*{re.escape(key)}\s*=\s*"((?:[^"\\]|\\.)*)"\s*$', re.MULTILINE
    )
    matches = pattern.findall(text)
    if len(matches) > 1:
        raise ValueError(f"duplicate TOML field: {key}")
    if not matches:
        return None
    value = json.loads(f'"{matches[0]}"')
    if not isinstance(value, str):
        raise ValueError(f"malformed TOML string: {key}")
    return value


def package_section(text: str) -> str:
    match = re.search(
        r"^\s*\[package\]\s*$\n(?P<body>.*?)(?=^\s*\[|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise ValueError("missing [package] section")
    return match.group("body")


def lock_records(lockfile: Path) -> dict[tuple[str, str], dict[str, str]]:
    records: dict[tuple[str, str], dict[str, str]] = {}
    identities: dict[tuple[str, str], Optional[str]] = {}
    text = lockfile.read_text(encoding="utf-8")
    for block in text.split("[[package]]")[1:]:
        source = toml_string(block, "source")
        name = toml_string(block, "name")
        version = toml_string(block, "version")
        if name is None or version is None:
            raise ValueError("malformed Cargo.lock package identity")
        key = (name, version)
        if key in identities:
            raise ValueError(
                f"ambiguous name/version package identity across lock records: {name}@{version}"
            )
        identities[key] = source
        if source != REGISTRY:
            continue
        checksum = toml_string(block, "checksum")
        if checksum is None or not re.fullmatch(r"[0-9a-f]{64}", checksum):
            raise ValueError(f"malformed registry checksum for {name}@{version}")
        records[key] = {"checksum": checksum, "source": source}
    if not records:
        raise ValueError("no crates.io registry records in Cargo.lock")
    return records


def parse_tree(text: str, root_name: str) -> set[tuple[str, str]]:
    records: set[tuple[str, str]] = set()
    for line in text.splitlines():
        match = TREE_RE.match(line)
        if match and match.group("name") != root_name:
            records.add((match.group("name"), match.group("version")))
    if not records:
        raise ValueError("empty Cargo target closure")
    return records


def tree_closures(root: Path, root_name: str) -> dict[str, set[tuple[str, str]]]:
    closures: dict[str, set[tuple[str, str]]] = {}
    for target in TARGETS:
        command = [
            "cargo",
            "tree",
            "--locked",
            "--offline",
            "--target",
            target,
            "--prefix",
            "none",
            "--format",
            "{p}",
        ]
        process = subprocess.run(
            command,
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        )
        closures[target] = parse_tree(process.stdout, root_name)
    return closures


def find_archive(cache: Path, name: str, version: str, checksum: str) -> bytes:
    candidates = sorted(
        path
        for path in cache.glob(f"*/{name}-{version}.crate")
        if path.is_file() and not path.is_symlink()
    )
    if len(candidates) != 1:
        raise ValueError(
            f"expected one regular archive for {name}@{version}, found {len(candidates)}"
        )
    data = candidates[0].read_bytes()
    actual = sha256_bytes(data)
    if actual != checksum:
        raise ValueError(
            f"archive checksum mismatch for {name}@{version}: {actual} != {checksum}"
        )
    return data


def safe_member_path(raw: str, prefix: str) -> str:
    if "\\" in raw:
        raise ValueError(f"archive member uses a backslash: {raw}")
    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts or not raw.startswith(prefix):
        raise ValueError(f"archive member escapes package root: {raw}")
    relative = raw[len(prefix) :]
    if not relative:
        raise ValueError(f"empty archive member path: {raw}")
    return relative


def archive_evidence(data: bytes, name: str, version: str) -> dict[str, object]:
    prefix = f"{name}-{version}/"
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members: dict[str, tarfile.TarInfo] = {}
        relative_paths: dict[str, str] = {}
        for member in archive.getmembers():
            relative = safe_member_path(member.name, prefix)
            if member.name in members:
                raise ValueError(f"duplicate archive member: {member.name}")
            members[member.name] = member
            relative_paths[member.name] = relative

        manifest_name = prefix + "Cargo.toml"
        manifest_member = members.get(manifest_name)
        if manifest_member is None or not manifest_member.isfile():
            raise ValueError(f"missing regular packaged Cargo.toml for {name}@{version}")
        manifest_handle = archive.extractfile(manifest_member)
        if manifest_handle is None:
            raise ValueError(f"unreadable packaged Cargo.toml for {name}@{version}")
        manifest_bytes = manifest_handle.read()
        package = package_section(manifest_bytes.decode("utf-8"))
        packaged_name = toml_string(package, "name")
        packaged_version = toml_string(package, "version")
        if packaged_name != name or packaged_version != version:
            raise ValueError(f"packaged Cargo.toml identity mismatch for {name}@{version}")

        license_expression = toml_string(package, "license")
        license_path = toml_string(package, "license-file")
        legacy_license_path = toml_string(package, "license_file")
        if license_path and legacy_license_path and license_path != legacy_license_path:
            raise ValueError(f"conflicting license-file fields for {name}@{version}")
        license_path = license_path or legacy_license_path
        if license_path:
            pure = PurePosixPath(license_path)
            if pure.is_absolute() or ".." in pure.parts or "\\" in license_path:
                raise ValueError(f"malformed license-file path for {name}@{version}")

        legal_names = {
            member_name
            for member_name, member in members.items()
            if member.isfile() and LEGAL_RE.fullmatch(PurePosixPath(member_name).name)
        }
        if license_path:
            legal_names.add(prefix + license_path)
        legal_files = []
        for member_name in sorted(legal_names):
            member = members.get(member_name)
            if member is None or not member.isfile():
                raise ValueError(
                    f"declared legal file is missing or not regular for {name}@{version}: "
                    f"{member_name[len(prefix):]}"
                )
            handle = archive.extractfile(member)
            if handle is None:
                raise ValueError(f"unreadable legal file: {member_name}")
            content = handle.read()
            legal_files.append(
                {
                    "bytes": len(content),
                    "path": relative_paths[member_name],
                    "sha256": sha256_bytes(content),
                }
            )
        if not legal_files and not license_expression:
            raise ValueError(f"missing license evidence for {name}@{version}")
        return {
            "license": license_expression,
            "license_files": legal_files,
            "manifest_sha256": sha256_bytes(manifest_bytes),
            "name": name,
            "version": version,
        }


def root_package_name(root: Path) -> str:
    package = package_section((root / "Cargo.toml").read_text(encoding="utf-8"))
    name = toml_string(package, "name")
    if name is None:
        raise ValueError("root Cargo.toml has no package name")
    return name


def build(root: Path, cache: Path) -> dict[str, object]:
    lockfile = root / "Cargo.lock"
    records = lock_records(lockfile)
    closures = tree_closures(root, root_package_name(root))
    union = set().union(*closures.values())
    missing = sorted(union - set(records))
    if missing:
        raise ValueError(f"Cargo target closure drifts from registry lock records: {missing}")

    packages = []
    named_legal_files = 0
    manifest_only_records = 0
    for name, version in sorted(union):
        record = records[(name, version)]
        data = find_archive(cache, name, version, record["checksum"])
        package = {
            "archive_sha256": sha256_bytes(data),
            "checksum": record["checksum"],
            "source": record["source"],
            "targets": [target for target in TARGETS if (name, version) in closures[target]],
            **archive_evidence(data, name, version),
        }
        count = len(package["license_files"])
        named_legal_files += count
        manifest_only_records += int(count == 0)
        packages.append(package)

    return {
        "cargo_lock_sha256": sha256_bytes(lockfile.read_bytes()),
        "claim": CLAIM,
        "manifest_only_records": manifest_only_records,
        "named_legal_files": named_legal_files,
        "packages": packages,
        "registry_lock_records": len(records),
        "schema": "azdaja.third_party_notice_input_evidence.v1",
        "supported_union_records": len(union),
        "target_counts": {target: len(closures[target]) for target in TARGETS},
        "targets": list(TARGETS),
    }


def render(document: dict[str, object]) -> str:
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def write_atomic(path: Path, content: str) -> None:
    if path.exists() and (not path.is_file() or path.is_symlink()):
        raise ValueError(f"manifest is not a regular non-symlink file: {path}")
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
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--cache", type=Path, default=Path.home() / ".cargo/registry/cache")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).with_name("third-party-notice-inputs.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        rendered = render(build(args.root, args.cache))
        if args.check:
            if (
                not args.manifest.is_file()
                or args.manifest.is_symlink()
                or args.manifest.read_text(encoding="utf-8") != rendered
            ):
                raise ValueError("manifest is missing, symlinked, or differs from current inputs")
        else:
            write_atomic(args.manifest, rendered)
    except (
        OSError,
        UnicodeError,
        ValueError,
        subprocess.CalledProcessError,
        tarfile.TarError,
    ) as error:
        print(f"third-party INPUT audit failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
