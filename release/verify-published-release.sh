#!/bin/sh
# Usage: release/verify-published-release.sh [version]
# Read-only post-publication audit of the installer, manifests, and payloads.
set -eu

VERSION=${1:-0.1.12}
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SITE_BASE=${AZDAJA_SITE_BASE:-https://azdaja.dev}
GITHUB_RELEASE_BASE=${AZDAJA_GITHUB_RELEASE_BASE:-https://github.com/kubet/azdaja/releases/download/v$VERSION}
EXPECTED_DIR=${AZDAJA_EXPECTED_DIR:-$ROOT/site/releases/v$VERSION}
TEST_MODE=${AZDAJA_VERIFY_TEST_MODE:-}

SITE_BASE=${SITE_BASE%/}
GITHUB_RELEASE_BASE=${GITHUB_RELEASE_BASE%/}
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
fetch "$SITE_BASE/releases/v$VERSION/SHA256SUMS" "$SITE_MANIFEST"
fetch "$GITHUB_RELEASE_BASE/SHA256SUMS" "$GITHUB_MANIFEST"
[ "$(file_size "$SITE_MANIFEST")" -le 1048576 ] || \
  fail 'site SHA256SUMS exceeds the 1 MiB verification cap'
[ "$(file_size "$GITHUB_MANIFEST")" -le 1048576 ] || \
  fail 'GitHub release SHA256SUMS exceeds the 1 MiB verification cap'
validate_manifest "$SITE_MANIFEST" site
validate_manifest "$GITHUB_MANIFEST" 'GitHub release'
cmp -s "$LOCAL_MANIFEST" "$SITE_MANIFEST" || \
  fail 'site SHA256SUMS differs from the reviewed local release manifest'
cmp -s "$LOCAL_MANIFEST" "$GITHUB_MANIFEST" || \
  fail 'GitHub release SHA256SUMS differs from the reviewed local release manifest'

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

printf 'verified published v%s across %s and %s\n' \
  "$VERSION" "$SITE_BASE" "$GITHUB_RELEASE_BASE"
