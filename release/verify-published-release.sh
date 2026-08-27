#!/bin/sh
# Usage: release/verify-published-release.sh VERSION
# Read-only post-publication audit of the installer, manifests, and payloads.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
usage() {
  printf '%s\n' 'Usage: release/verify-published-release.sh VERSION'
}
case "${1-}" in
  -h|--help)
    usage
    exit 0
    ;;
esac
[ "$#" -eq 1 ] || {
  usage >&2
  exit 2
}
VERSION=$1
SITE_BASE=${AZDAJA_SITE_BASE:-https://azdaja.dev}
GITHUB_RELEASE_BASE=${AZDAJA_GITHUB_RELEASE_BASE:-https://github.com/kubet/azdaja/releases/download/v$VERSION}
GITHUB_TAG_BASE=${AZDAJA_GITHUB_TAG_BASE:-https://raw.githubusercontent.com/kubet/azdaja/v$VERSION/site/releases/v$VERSION}
EXPECTED_DIR=${AZDAJA_EXPECTED_DIR:-$ROOT/site/releases/v$VERSION}
TEST_MODE=${AZDAJA_VERIFY_TEST_MODE:-}

SITE_BASE=${SITE_BASE%/}
GITHUB_RELEASE_BASE=${GITHUB_RELEASE_BASE%/}
GITHUB_TAG_BASE=${GITHUB_TAG_BASE%/}
DARWIN=azdaja-v$VERSION-darwin-arm64
DARWIN_X86_64=azdaja-v$VERSION-darwin-x86_64
LINUX=azdaja-v$VERSION-linux-x86_64
PAYLOADS="$DARWIN $DARWIN_X86_64 $LINUX LICENSE THIRD-PARTY-NOTICES.md"

fail() {
  printf 'verify-published-release: %s\n' "$1" >&2
  exit "${2:-1}"
}

printf '%s\n' "$VERSION" | awk '
  /^[0-9]+[.][0-9]+[.][0-9]+$/ { valid = 1 }
  END { exit valid ? 0 : 1 }
' || fail "invalid version '$VERSION'" 2

validate_base() {
  label=$1
  base=$2
  case "$base" in
    https://*) ;;
    http://127.0.0.1:*|http://localhost:*|file://*)
      [ "$TEST_MODE" = local ] || fail "$label must use https outside local validation mode" 2
      ;;
    *) fail "$label must use https, or loopback/file in local validation mode" 2 ;;
  esac
}
validate_base AZDAJA_SITE_BASE "$SITE_BASE"
validate_base AZDAJA_GITHUB_RELEASE_BASE "$GITHUB_RELEASE_BASE"
validate_base AZDAJA_GITHUB_TAG_BASE "$GITHUB_TAG_BASE"

[ -d "$EXPECTED_DIR" ] && [ ! -L "$EXPECTED_DIR" ] || \
  fail "expected release directory is missing or unsafe: $EXPECTED_DIR" 2

TMP_ROOT=${TMPDIR:-/tmp}
TMP=$TMP_ROOT/azdaja-published-release.$$
(umask 077 && mkdir "$TMP") || fail "cannot create private staging directory: $TMP" 2
cleanup() {
  status=$?
  trap - 0
  rm -rf "$TMP"
  exit "$status"
}
trap cleanup 0
trap 'exit 1' HUP INT TERM

fetch() {
  url=$1
  destination=$2
  case "$url" in
    https://*)
      curl --fail --silent --show-error --location --proto '=https' --tlsv1.2 \
        --proto-redir '=https' \
        --connect-timeout 15 --max-time 300 --max-filesize 67108864 \
        "$url" -o "$destination" || fail "download failed: $url"
      ;;
    http://127.0.0.1:*|http://localhost:*|file://*)
      [ "$TEST_MODE" = local ] || fail "refusing non-https download: $url" 2
      curl --fail --silent --show-error --location \
        --connect-timeout 15 --max-time 300 --max-filesize 67108864 \
        "$url" -o "$destination" || fail "download failed: $url"
      ;;
    *) fail "refusing unsupported download URL: $url" 2 ;;
  esac
}

sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    fail 'shasum or sha256sum is required' 2
  fi
}

file_size() {
  wc -c < "$1" | tr -d ' '
}

manifest_sha256() {
  manifest=$1
  asset=$2
  matches=$(awk -v asset="$asset" '$2 == asset || $2 == "*" asset { print $1 }' "$manifest")
  match_count=$(printf '%s\n' "$matches" | awk 'NF { n += 1 } END { print n + 0 }')
  [ "$match_count" -eq 1 ] || fail "$manifest must contain exactly one entry for $asset"
  digest=$(printf '%s\n' "$matches" | awk 'NF { print; exit }')
  case "$digest" in
    *[!0-9a-f]*|'') fail "$manifest contains an invalid SHA-256 for $asset" ;;
  esac
  [ "${#digest}" -eq 64 ] || fail "$manifest contains an invalid SHA-256 for $asset"
  printf '%s' "$digest"
}

validate_manifest() {
  manifest=$1
  label=$2
  entry_count=$(awk 'NF { n += 1 } END { print n + 0 }' "$manifest")
  [ "$entry_count" -eq 5 ] || fail "$label SHA256SUMS must contain exactly five payload entries"
  malformed=$(awk 'NF && NF != 2 { print; exit }' "$manifest")
  [ -z "$malformed" ] || fail "$label SHA256SUMS contains a malformed entry"
  unknown=$(awk -v darwin="$DARWIN" -v intel="$DARWIN_X86_64" -v linux="$LINUX" '
    NF && $2 != darwin && $2 != "*" darwin &&
      $2 != intel && $2 != "*" intel &&
      $2 != linux && $2 != "*" linux &&
      $2 != "LICENSE" && $2 != "*LICENSE" &&
      $2 != "THIRD-PARTY-NOTICES.md" && $2 != "*THIRD-PARTY-NOTICES.md" { print; exit }
  ' "$manifest")
  [ -z "$unknown" ] || fail "$label SHA256SUMS contains an unexpected payload"
  for payload in $PAYLOADS; do
    manifest_sha256 "$manifest" "$payload" >/dev/null
  done
}

LOCAL_MANIFEST=$EXPECTED_DIR/SHA256SUMS
[ -f "$LOCAL_MANIFEST" ] && [ ! -L "$LOCAL_MANIFEST" ] || \
  fail "local SHA256SUMS is missing or unsafe: $LOCAL_MANIFEST" 2
validate_manifest "$LOCAL_MANIFEST" local
for payload in $PAYLOADS; do
  [ -f "$EXPECTED_DIR/$payload" ] && [ ! -L "$EXPECTED_DIR/$payload" ] || \
    fail "local payload is missing or unsafe: $EXPECTED_DIR/$payload" 2
  expected=$(manifest_sha256 "$LOCAL_MANIFEST" "$payload")
  actual=$(sha256_file "$EXPECTED_DIR/$payload")
  [ "$actual" = "$expected" ] || fail "local SHA-256 mismatch for $payload"
done

validate_provenance() {
  provenance=$1
  label=$2
  python3 - "$provenance" "$VERSION" "$label" <<'PY'
import json
import pathlib
import re
import sys

path, version, label = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
try:
    value = json.loads(path.read_text(encoding="utf-8"))
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"verify-published-release: {label} PROVENANCE.json is invalid: {exc}")
required = {
    "schema_version", "release_version", "source_commit", "workflow_run_id",
    "workflow_run_attempt", "source_artifacts", "status",
    "allowed_promotion_delta_paths",
}
if set(value) != required:
    raise SystemExit(f"verify-published-release: {label} PROVENANCE.json fields mismatch")
if value["schema_version"] != 1 or type(value["schema_version"]) is not int:
    raise SystemExit(f"verify-published-release: {label} PROVENANCE.json schema_version must be 1")
if value["release_version"] != version:
    raise SystemExit(f"verify-published-release: {label} PROVENANCE.json release version mismatch")
if not isinstance(value["source_commit"], str) or not re.fullmatch(r"[0-9a-f]{40}", value["source_commit"]):
    raise SystemExit(f"verify-published-release: {label} PROVENANCE.json source_commit is invalid")
if value["status"] != "REVIEWED_FOR_PUBLICATION":
    raise SystemExit(f"verify-published-release: {label} PROVENANCE.json status is not reviewed")
for field in ("workflow_run_id", "workflow_run_attempt"):
    if type(value[field]) is not int or value[field] <= 0:
        raise SystemExit(f"verify-published-release: {label} PROVENANCE.json {field} is invalid")
artifacts = value["source_artifacts"]
targets = [
    ("aarch64-apple-darwin", f"azdaja-v{version}-darwin-arm64"),
    ("x86_64-apple-darwin", f"azdaja-v{version}-darwin-x86_64"),
    ("x86_64-unknown-linux-gnu", f"azdaja-v{version}-linux-x86_64"),
]
if not isinstance(artifacts, list) or len(artifacts) != 3:
    raise SystemExit(f"verify-published-release: {label} PROVENANCE.json must bind three source artifacts")
for artifact, (target, asset_name) in zip(artifacts, targets):
    if not isinstance(artifact, dict) or set(artifact) != {"artifact_name", "asset_name", "bytes", "sha256", "target"}:
        raise SystemExit(f"verify-published-release: {label} PROVENANCE.json source artifact fields mismatch")
    expected_name = f"azdaja-candidate-{target}"
    if artifact["artifact_name"] != expected_name or artifact["asset_name"] != asset_name or artifact["target"] != target:
        raise SystemExit(f"verify-published-release: {label} PROVENANCE.json source artifact identity mismatch")
    if type(artifact["bytes"]) is not int or artifact["bytes"] <= 0:
        raise SystemExit(f"verify-published-release: {label} PROVENANCE.json source artifact size is invalid")
    if not isinstance(artifact["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"]):
        raise SystemExit(f"verify-published-release: {label} PROVENANCE.json source artifact hash is invalid")
expected_delta = [
    f"site/releases/v{version}/LICENSE",
    f"site/releases/v{version}/PROVENANCE.json",
    f"site/releases/v{version}/SHA256SUMS",
    f"site/releases/v{version}/THIRD-PARTY-NOTICES.md",
    f"site/releases/v{version}/azdaja-v{version}-darwin-arm64",
    f"site/releases/v{version}/azdaja-v{version}-darwin-x86_64",
    f"site/releases/v{version}/azdaja-v{version}-linux-x86_64",
]
if value["allowed_promotion_delta_paths"] != expected_delta:
    raise SystemExit(f"verify-published-release: {label} PROVENANCE.json promotion delta mismatch")
PY
}

LOCAL_PROVENANCE=$EXPECTED_DIR/PROVENANCE.json
[ -f "$LOCAL_PROVENANCE" ] && [ ! -L "$LOCAL_PROVENANCE" ] || \
  fail "local PROVENANCE.json is missing or unsafe: $LOCAL_PROVENANCE" 2
validate_provenance "$LOCAL_PROVENANCE" local

INSTALLER=$TMP/install
fetch "$SITE_BASE/install" "$INSTALLER"
[ "$(file_size "$INSTALLER")" -le 1048576 ] || \
  fail 'deployed installer exceeds the 1 MiB verification cap'
grep -Eq "^VERSION=$VERSION$" "$INSTALLER" || \
  fail "deployed installer does not declare VERSION=$VERSION"
grep -F 'Darwin-x86_64)' "$INSTALLER" >/dev/null || \
  fail 'deployed installer does not route Darwin-x86_64'
grep -F 'ASSET=azdaja-v$VERSION-darwin-x86_64' "$INSTALLER" >/dev/null || \
  fail 'deployed installer does not select the Intel macOS asset'

SITE_MANIFEST=$TMP/site-SHA256SUMS
GITHUB_MANIFEST=$TMP/github-SHA256SUMS
TAG_MANIFEST=$TMP/tag-SHA256SUMS
SITE_PROVENANCE=$TMP/site-PROVENANCE.json
GITHUB_PROVENANCE=$TMP/github-PROVENANCE.json
TAG_PROVENANCE=$TMP/tag-PROVENANCE.json
fetch "$SITE_BASE/releases/v$VERSION/SHA256SUMS" "$SITE_MANIFEST"
fetch "$GITHUB_RELEASE_BASE/SHA256SUMS" "$GITHUB_MANIFEST"
fetch "$GITHUB_TAG_BASE/SHA256SUMS" "$TAG_MANIFEST"
fetch "$SITE_BASE/releases/v$VERSION/PROVENANCE.json" "$SITE_PROVENANCE"
fetch "$GITHUB_RELEASE_BASE/PROVENANCE.json" "$GITHUB_PROVENANCE"
fetch "$GITHUB_TAG_BASE/PROVENANCE.json" "$TAG_PROVENANCE"
[ "$(file_size "$SITE_MANIFEST")" -le 1048576 ] || \
  fail 'site SHA256SUMS exceeds the 1 MiB verification cap'
[ "$(file_size "$GITHUB_MANIFEST")" -le 1048576 ] || \
  fail 'GitHub release SHA256SUMS exceeds the 1 MiB verification cap'
[ "$(file_size "$TAG_MANIFEST")" -le 1048576 ] || \
  fail 'GitHub tag SHA256SUMS exceeds the 1 MiB verification cap'
validate_manifest "$SITE_MANIFEST" site
validate_manifest "$GITHUB_MANIFEST" 'GitHub release'
validate_manifest "$TAG_MANIFEST" 'GitHub tag'
cmp -s "$LOCAL_MANIFEST" "$SITE_MANIFEST" || \
  fail 'site SHA256SUMS differs from the reviewed local release manifest'
cmp -s "$LOCAL_MANIFEST" "$GITHUB_MANIFEST" || \
  fail 'GitHub release SHA256SUMS differs from the reviewed local release manifest'
cmp -s "$LOCAL_MANIFEST" "$TAG_MANIFEST" || \
  fail 'GitHub tag SHA256SUMS differs from the reviewed local release manifest'
for provenance in "$SITE_PROVENANCE" "$GITHUB_PROVENANCE" "$TAG_PROVENANCE"; do
  [ "$(file_size "$provenance")" -le 1048576 ] || fail 'PROVENANCE.json exceeds the 1 MiB verification cap'
done
validate_provenance "$SITE_PROVENANCE" site
validate_provenance "$GITHUB_PROVENANCE" 'GitHub release'
validate_provenance "$TAG_PROVENANCE" 'GitHub tag'
cmp -s "$LOCAL_PROVENANCE" "$SITE_PROVENANCE" || \
  fail 'site PROVENANCE.json differs from the reviewed local provenance'
cmp -s "$LOCAL_PROVENANCE" "$GITHUB_PROVENANCE" || \
  fail 'GitHub release PROVENANCE.json differs from the reviewed local provenance'
cmp -s "$LOCAL_PROVENANCE" "$TAG_PROVENANCE" || \
  fail 'GitHub tag PROVENANCE.json differs from the reviewed local provenance'

SOURCE_COMMIT=$(python3 - "$TAG_PROVENANCE" <<'PY'
import json, pathlib, sys
print(json.loads(pathlib.Path(sys.argv[1]).read_text())["source_commit"])
PY
)
if git -C "$ROOT" cat-file -e "$SOURCE_COMMIT^{commit}" 2>/dev/null && \
   git -C "$ROOT" rev-parse --verify "refs/tags/v$VERSION^{commit}" >/dev/null 2>&1; then
  TAG_COMMIT=$(git -C "$ROOT" rev-parse "refs/tags/v$VERSION^{commit}")
  git -C "$ROOT" merge-base --is-ancestor "$SOURCE_COMMIT" "$TAG_COMMIT" || \
    fail "provenance source_commit is not an ancestor of tag v$VERSION"
else
  # In detached/local audits, the byte-identical immutable tag provenance is the
  # explicit binding to source_commit. It does not claim the binaries came from
  # the later asset commit.
  printf '  source binding: tag provenance explicitly binds %s\n' "$SOURCE_COMMIT"
fi

verify_channel() {
  label=$1
  base=$2
  manifest=$3
  channel_dir=$4
  mkdir "$channel_dir"
  for payload in $PAYLOADS; do
    fetch "$base/$payload" "$channel_dir/$payload"
    expected=$(manifest_sha256 "$manifest" "$payload")
    actual=$(sha256_file "$channel_dir/$payload")
    [ "$actual" = "$expected" ] || fail "$label SHA-256 mismatch for $payload"
  done
}
verify_channel site "$SITE_BASE/releases/v$VERSION" "$SITE_MANIFEST" "$TMP/site"
verify_channel 'GitHub release' "$GITHUB_RELEASE_BASE" "$GITHUB_MANIFEST" "$TMP/github"
verify_channel 'GitHub tag' "$GITHUB_TAG_BASE" "$TAG_MANIFEST" "$TMP/tag"

printf 'verified published v%s\n' "$VERSION"
printf '  site: %s\n' "$SITE_BASE"
printf '  GitHub release: %s\n' "$GITHUB_RELEASE_BASE"
printf '  GitHub tag: %s\n' "$GITHUB_TAG_BASE"
