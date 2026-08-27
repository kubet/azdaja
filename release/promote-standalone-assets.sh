#!/bin/sh
# Promote three reviewed workflow_dispatch candidate artifacts into release assets.
# Usage: release/promote-standalone-assets.sh SOURCE_SHA RUN_ID RUN_ATTEMPT CANDIDATE_ROOT OUTPUT_DIR
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
usage() {
  printf '%s\n' 'Usage: release/promote-standalone-assets.sh SOURCE_SHA RUN_ID RUN_ATTEMPT CANDIDATE_ROOT OUTPUT_DIR'
}
case "${1-}" in
  -h|--help) usage; exit 0 ;;
esac
[ "$#" -eq 5 ] || { usage >&2; exit 2; }
SOURCE_SHA=$1
RUN_ID=$2
RUN_ATTEMPT=$3
CANDIDATE_ROOT=$4
OUTPUT_DIR=$5
VERSION=0.1.14

fail() {
  printf 'promote-standalone-assets: %s\n' "$1" >&2
  exit "${2:-1}"
}

case "$SOURCE_SHA" in *[!0-9a-f]*|'') fail 'SOURCE_SHA must be a full lowercase hexadecimal commit ID' 2 ;; esac
[ "${#SOURCE_SHA}" -eq 40 ] || fail 'SOURCE_SHA must be a full 40-character commit ID' 2
case "$RUN_ID" in *[!0-9]*|'') fail 'RUN_ID must be decimal digits' 2 ;; esac
case "$RUN_ATTEMPT" in *[!0-9]*|'') fail 'RUN_ATTEMPT must be decimal digits' 2 ;; esac
[ "$RUN_ID" -gt 0 ] || fail 'RUN_ID must be positive' 2
[ "$RUN_ATTEMPT" -gt 0 ] || fail 'RUN_ATTEMPT must be positive' 2

command -v git >/dev/null 2>&1 || fail 'git is required' 2
command -v python3 >/dev/null 2>&1 || fail 'python3 is required' 2
[ "$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null)" = "$ROOT" ] || fail 'script must run from its source repository' 2
HEAD_SHA=$(git -C "$ROOT" rev-parse HEAD)
[ "$HEAD_SHA" = "$SOURCE_SHA" ] || fail "source checkout HEAD $HEAD_SHA does not equal SOURCE_SHA $SOURCE_SHA"
[ -z "$(git -C "$ROOT" status --porcelain=v1 --untracked-files=all)" ] || fail 'source checkout is not clean'
[ -d "$CANDIDATE_ROOT" ] && [ ! -L "$CANDIDATE_ROOT" ] || fail 'candidate root is missing or is a symlink'
[ ! -e "$OUTPUT_DIR" ] && [ ! -L "$OUTPUT_DIR" ] || fail 'output directory already exists'
[ -f "$ROOT/LICENSE" ] && [ ! -L "$ROOT/LICENSE" ] || fail 'reviewed LICENSE is missing or unsafe'
[ -f "$ROOT/THIRD-PARTY-NOTICES.md" ] && [ ! -L "$ROOT/THIRD-PARTY-NOTICES.md" ] || fail 'reviewed THIRD-PARTY-NOTICES.md is missing or unsafe'

OUTPUT_PARENT=$(dirname -- "$OUTPUT_DIR")
OUTPUT_NAME=$(basename -- "$OUTPUT_DIR")
[ -d "$OUTPUT_PARENT" ] && [ ! -L "$OUTPUT_PARENT" ] || fail 'output parent is missing or unsafe'
STAGING=$(mktemp -d "$OUTPUT_PARENT/.${OUTPUT_NAME}.staging.XXXXXX") || fail 'cannot create staging directory'
cleanup() {
  status=$?
  trap - 0
  rm -rf "$STAGING"
  exit "$status"
}
trap cleanup 0
trap 'exit 1' HUP INT TERM

python3 - "$ROOT" "$SOURCE_SHA" "$RUN_ID" "$RUN_ATTEMPT" "$CANDIDATE_ROOT" "$STAGING" "$VERSION" <<'PY'
import hashlib
import json
import os
import pathlib
import shutil
import stat
import struct
import sys

root = pathlib.Path(sys.argv[1])
source_sha, run_id, run_attempt = sys.argv[2:5]
candidate_root = pathlib.Path(sys.argv[5])
staging = pathlib.Path(sys.argv[6])
version = sys.argv[7]

specs = [
    ("aarch64-apple-darwin", f"azdaja-v{version}-darwin-arm64", "mach-o", 0x0100000C),
    ("x86_64-apple-darwin", f"azdaja-v{version}-darwin-x86_64", "mach-o", 0x01000007),
    ("x86_64-unknown-linux-gnu", f"azdaja-v{version}-linux-x86_64", "elf", 0x3E),
]

def fail(message):
    raise SystemExit(f"promote-standalone-assets: {message}")

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def regular_nonsymlink(path):
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return False
    return stat.S_ISREG(mode) and not path.is_symlink()

def validate_architecture(path, kind, machine):
    data = path.read_bytes()[:32]
    if kind == "elf":
        return len(data) >= 20 and data[:7] == b"\x7fELF\x02\x01\x01" and struct.unpack("<H", data[18:20])[0] == machine
    return len(data) >= 8 and data[:4] == b"\xcf\xfa\xed\xfe" and struct.unpack("<I", data[4:8])[0] == machine

try:
    root_entries = sorted(candidate_root.iterdir(), key=lambda p: p.name)
except OSError as exc:
    fail(f"cannot inspect candidate root: {exc}")
expected_dirs = [f"azdaja-candidate-{target}" for target, _, _, _ in specs]
if [p.name for p in root_entries] != expected_dirs:
    fail(f"candidate root must contain exactly: {', '.join(expected_dirs)}")
if any(p.is_symlink() or not p.is_dir() for p in root_entries):
    fail("candidate artifact directories must be real directories, not symlinks")

artifact_records = []
for target, asset_name, kind, machine in specs:
    artifact_name = f"azdaja-candidate-{target}"
    artifact_dir = candidate_root / artifact_name
    entries = sorted(artifact_dir.iterdir(), key=lambda p: p.name)
    expected_entries = sorted(["candidate-receipt.json", asset_name])
    if [p.name for p in entries] != expected_entries:
        fail(f"{artifact_name} must contain exactly candidate-receipt.json and {asset_name}")
    receipt_path = artifact_dir / "candidate-receipt.json"
    binary_path = artifact_dir / asset_name
    if not regular_nonsymlink(receipt_path) or not regular_nonsymlink(binary_path):
        fail(f"{artifact_name} contains a missing, non-regular, or symlinked file")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"invalid receipt in {artifact_name}: {exc}")
    expected_keys = {
        "schema_version", "source_sha", "run_id", "run_attempt", "target",
        "asset_name", "bytes", "sha256", "version", "architecture_validation",
        "publication_authorized",
    }
    if set(receipt) != expected_keys:
        fail(f"receipt fields mismatch in {artifact_name}")
    expected = {
        "schema_version": 1,
        "source_sha": source_sha,
        "run_id": int(run_id),
        "run_attempt": int(run_attempt),
        "target": target,
        "asset_name": asset_name,
        "bytes": binary_path.stat().st_size,
        "sha256": sha256(binary_path),
        "version": version,
        "architecture_validation": True,
        "publication_authorized": False,
    }
    for key, value in expected.items():
        if receipt.get(key) != value or type(receipt.get(key)) is not type(value):
            fail(f"receipt mismatch for {key} in {artifact_name}")
    if not validate_architecture(binary_path, kind, machine):
        fail(f"wrong architecture or executable format for {asset_name}")
    destination = staging / asset_name
    shutil.copyfile(binary_path, destination)
    destination.chmod(0o755)
    artifact_records.append({
        "artifact_name": artifact_name,
        "asset_name": asset_name,
        "bytes": expected["bytes"],
        "sha256": expected["sha256"],
        "target": target,
    })

for name in ["LICENSE", "THIRD-PARTY-NOTICES.md"]:
    shutil.copyfile(root / name, staging / name)
    (staging / name).chmod(0o644)

payload_names = [asset_name for _, asset_name, _, _ in specs] + ["LICENSE", "THIRD-PARTY-NOTICES.md"]
(staging / "SHA256SUMS").write_text(
    "".join(f"{sha256(staging / name)}  {name}\n" for name in payload_names),
    encoding="utf-8",
)
(staging / "SHA256SUMS").chmod(0o644)

provenance = {
    "schema_version": 1,
    "release_version": version,
    "source_commit": source_sha,
    "workflow_run_id": int(run_id),
    "workflow_run_attempt": int(run_attempt),
    "source_artifacts": artifact_records,
    "status": "REVIEWED_FOR_PUBLICATION",
    "allowed_promotion_delta_paths": [
        f"site/releases/v{version}/LICENSE",
        f"site/releases/v{version}/PROVENANCE.json",
        f"site/releases/v{version}/SHA256SUMS",
        f"site/releases/v{version}/THIRD-PARTY-NOTICES.md",
        f"site/releases/v{version}/azdaja-v{version}-darwin-arm64",
        f"site/releases/v{version}/azdaja-v{version}-darwin-x86_64",
        f"site/releases/v{version}/azdaja-v{version}-linux-x86_64",
    ],
}
(staging / "PROVENANCE.json").write_text(
    json.dumps(provenance, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
(staging / "PROVENANCE.json").chmod(0o644)
PY

mv "$STAGING" "$OUTPUT_DIR" || fail 'cannot install completed output directory'
trap - 0
printf 'promoted reviewed standalone assets to %s\n' "$OUTPUT_DIR"
