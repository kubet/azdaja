#!/bin/sh
set -eu

VERSION=0.1.2
RELEASE_BASE=https://github.com/kubet/azdaja/releases/download/v$VERSION
HARNESS=
BIN_DIR=${AZDAJA_INSTALL_DIR:-}

usage() {
  printf '%s\n' 'Usage: install.sh [--harness jcode|claude|codex|gemini|opencode|all] [--bin-dir DIR]'
}
fail() {
  printf 'azdaja install: %s\n' "$1" >&2
  exit "${2:-1}"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --harness)
      [ "$#" -ge 2 ] || fail '--harness requires a value' 2
      HARNESS=$2
      shift 2
      ;;
    --bin-dir)
      [ "$#" -ge 2 ] || fail '--bin-dir requires a value' 2
      BIN_DIR=$2
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1" 2
      ;;
  esac
done

case "$HARNESS" in
  ''|jcode|claude|codex|gemini|opencode|all) ;;
  *) fail "unknown harness '$HARNESS' (choose jcode, claude, codex, gemini, opencode, or all)" 2 ;;
esac

[ -n "${HOME:-}" ] || fail 'HOME is not set; use --bin-dir DIR and set HOME before installing a harness'

DETECTED=
add_detected() {
  case " $DETECTED " in
    *" $1 "*) ;;
    *) DETECTED="${DETECTED}${DETECTED:+ }$1" ;;
  esac
}
if [ -d "$HOME/.jcode" ] || command -v jcode >/dev/null 2>&1 || command -v jcode-api >/dev/null 2>&1; then
  add_detected jcode
fi
if [ -d "$HOME/.claude" ] || command -v claude >/dev/null 2>&1; then
  add_detected claude
fi
if [ -d "$HOME/.codex" ] || [ -d "$HOME/.agents/skills" ] || command -v codex >/dev/null 2>&1; then
  add_detected codex
fi
if [ -d "$HOME/.gemini" ] || command -v gemini >/dev/null 2>&1; then
  add_detected gemini
fi
CONFIG_ROOT=${XDG_CONFIG_HOME:-$HOME/.config}
if [ -d "$CONFIG_ROOT/opencode" ] || command -v opencode >/dev/null 2>&1; then
  add_detected opencode
fi

if [ -z "$HARNESS" ]; then
  [ -n "$DETECTED" ] || fail 'no supported harness found; install jcode, claude, codex, gemini, or opencode, or rerun with --harness NAME'
  INSTALL_NAMES=$DETECTED
  DISPLAY=$(printf '%s' "$DETECTED" | tr ' ' ',')
  DISPLAY=$(printf '%s' "$DISPLAY" | sed 's/,/, /g')
  DETECTION_REPORT="$DISPLAY (config/skill directories and PATH only)"
else
  if [ "$HARNESS" = all ]; then
    INSTALL_NAMES='jcode claude codex gemini opencode'
    DETECTION_REPORT='jcode, claude, codex, gemini, opencode (selected by --harness all)'
  else
    INSTALL_NAMES=$HARNESS
    DETECTION_REPORT="$HARNESS (selected by --harness)"
  fi
fi

case "${AZDAJA_INSTALL_TEST_MODE:-}" in
  '')
    [ -z "${AZDAJA_INSTALL_BASE_URL:-}${AZDAJA_INSTALL_OS:-}${AZDAJA_INSTALL_ARCH:-}" ] || \
      fail 'validation overrides require AZDAJA_INSTALL_TEST_MODE=local' 2
    OS=$(uname -s)
    ARCH=$(uname -m)
    BASE_URL=$RELEASE_BASE
    ;;
  local)
    OS=${AZDAJA_INSTALL_OS:-$(uname -s)}
    ARCH=${AZDAJA_INSTALL_ARCH:-$(uname -m)}
    BASE_URL=${AZDAJA_INSTALL_BASE_URL:-}
    [ -n "$BASE_URL" ] || fail 'AZDAJA_INSTALL_BASE_URL is required in local validation mode' 2
    case "$BASE_URL" in
      http://127.0.0.1:*|http://localhost:*|https://*) ;;
      *) fail 'local validation URL must use loopback http:// or https://' 2 ;;
    esac
    ;;
  *) fail 'invalid AZDAJA_INSTALL_TEST_MODE' 2 ;;
esac

case "$OS-$ARCH" in
  Darwin-arm64) ASSET=azdaja-v$VERSION-darwin-arm64 ;;
  Linux-x86_64) ASSET=azdaja-v$VERSION-linux-x86_64 ;;
  *) fail "unsupported platform $OS-$ARCH; v$VERSION binaries support Darwin-arm64 and Linux-x86_64" ;;
esac

if [ -z "$BIN_DIR" ]; then
  # Prefer a user-owned directory already on PATH. Fall back to the conventional user bin.
  OLD_IFS=$IFS
  IFS=:
  for candidate in ${PATH:-}; do
    IFS=$OLD_IFS
    case "$candidate" in
      "$HOME"/*)
        if [ -d "$candidate" ] && [ -w "$candidate" ]; then
          BIN_DIR=$candidate
          break
        fi
        ;;
    esac
    IFS=:
  done
  IFS=$OLD_IFS
fi
BIN_DIR=${BIN_DIR:-$HOME/.local/bin}

# Stage and verify entirely outside HOME. Failure before verification must not
# create the binary directory, managed harness files, configuration, or alias.
TMP=${TMPDIR:-/tmp}/azdaja-install.$$
STAGED=
(umask 077 && mkdir "$TMP") || fail 'cannot create private staging directory'
cleanup() {
  rm -rf "$TMP"
  [ -z "$STAGED" ] || rm -f "$STAGED"
}
trap cleanup 0
trap 'exit 1' HUP INT TERM

command -v curl >/dev/null 2>&1 || fail 'curl is required'
download() {
  if [ "${AZDAJA_INSTALL_TEST_MODE:-}" = local ]; then
    curl --fail --silent --show-error --location \
      --connect-timeout 15 --max-time 300 --max-filesize 67108864 \
      "$1" -o "$2"
  else
    curl --fail --silent --show-error --location --proto '=https' --tlsv1.2 \
      --connect-timeout 15 --max-time 300 --max-filesize 67108864 \
      "$1" -o "$2"
  fi
}
download "$BASE_URL/SHA256SUMS" "$TMP/SHA256SUMS"
download "$BASE_URL/$ASSET" "$TMP/azdaja"

SUMS_SIZE=$(wc -c < "$TMP/SHA256SUMS" | tr -d ' ')
[ "$SUMS_SIZE" -le 1048576 ] || fail 'SHA256SUMS exceeds the 1 MiB download cap'
BIN_SIZE=$(wc -c < "$TMP/azdaja" | tr -d ' ')
[ "$BIN_SIZE" -le 67108864 ] || fail 'release binary exceeds the 64 MiB download cap'

MATCHES=$(awk -v asset="$ASSET" '$2 == asset || $2 == "*" asset { print $1 }' "$TMP/SHA256SUMS")
MATCH_COUNT=$(printf '%s\n' "$MATCHES" | awk 'NF { n += 1 } END { print n + 0 }')
[ "$MATCH_COUNT" -eq 1 ] || fail "SHA256SUMS must contain exactly one entry for $ASSET"
EXPECTED_SHA256=$(printf '%s\n' "$MATCHES" | awk 'NF { print; exit }')
case "$EXPECTED_SHA256" in
  *[!0-9a-f]*|'') fail "invalid SHA-256 entry for $ASSET" ;;
esac
[ "${#EXPECTED_SHA256}" -eq 64 ] || fail "invalid SHA-256 entry for $ASSET"

if command -v shasum >/dev/null 2>&1; then
  ACTUAL_SHA256=$(shasum -a 256 "$TMP/azdaja" | awk '{print $1}')
elif command -v sha256sum >/dev/null 2>&1; then
  ACTUAL_SHA256=$(sha256sum "$TMP/azdaja" | awk '{print $1}')
else
  fail 'shasum or sha256sum is required'
fi
[ "$ACTUAL_SHA256" = "$EXPECTED_SHA256" ] || fail 'SHA-256 mismatch; the existing installation was not changed'
chmod 755 "$TMP/azdaja"
VERSION_OUTPUT=$("$TMP/azdaja" --version) || fail 'downloaded binary did not run'
case "$VERSION_OUTPUT" in
  "azdaja $VERSION (monty "*) ;;
  *) fail "downloaded binary reported an unexpected version: $VERSION_OUTPUT" ;;
esac

DEST=$BIN_DIR/azdaja
ALIAS=$BIN_DIR/az
ALIAS_CREATE=true
if [ -L "$ALIAS" ]; then
  command -v readlink >/dev/null 2>&1 || fail 'readlink is required to validate the existing az alias'
  ALIAS_TARGET=$(readlink "$ALIAS") || fail "cannot inspect existing az alias: $ALIAS"
  [ "$ALIAS_TARGET" = azdaja ] || fail "refusing to overwrite foreign symlink: $ALIAS"
  ALIAS_CREATE=false
elif [ -e "$ALIAS" ]; then
  fail "refusing to overwrite foreign path: $ALIAS"
fi

(umask 077 && mkdir -p "$BIN_DIR") || fail "cannot create binary directory $BIN_DIR"
[ -d "$BIN_DIR" ] && [ -w "$BIN_DIR" ] || fail "binary directory is not writable: $BIN_DIR"
[ ! -d "$DEST" ] || fail "refusing to replace directory: $DEST"

STAGED=$BIN_DIR/.azdaja-install.$$
[ ! -e "$STAGED" ] || fail "temporary install path already exists: $STAGED"
(umask 077 && set -C && : > "$STAGED") 2>/dev/null || fail 'cannot create atomic install file'
cat "$TMP/azdaja" > "$STAGED"
chmod 755 "$STAGED"
mv -f "$STAGED" "$DEST"
STAGED=

harness_target() {
  case "$1" in
    jcode) printf '%s' "$HOME/.jcode/skills/azdaja" ;;
    claude) printf '%s' "$HOME/.claude/skills/azdaja" ;;
    codex) printf '%s' "$HOME/.agents/skills/azdaja" ;;
    gemini) printf '%s' "$HOME/.gemini/skills/azdaja" ;;
    opencode) printf '%s' "$CONFIG_ROOT/opencode/skills/azdaja" ;;
  esac
}
WRITTEN="azdaja -> $DEST ($ASSET); az -> $ALIAS (alias to azdaja)"
PRIMARY_TARGET=
for harness in $INSTALL_NAMES; do
  "$DEST" install --harness "$harness" >/dev/null
  TARGET=$(harness_target "$harness")
  WRITTEN="$WRITTEN; $harness -> $TARGET"
  [ -n "$PRIMARY_TARGET" ] || PRIMARY_TARGET=$TARGET
done

# Bind the PATH binary to the first selected harness without reading credentials.
CONFIG_STAGE=$BIN_DIR/.azdaja-config.$$
[ ! -e "$CONFIG_STAGE" ] || fail "temporary config path already exists: $CONFIG_STAGE"
STAGED=$CONFIG_STAGE
(umask 077 && set -C && : > "$STAGED") 2>/dev/null || fail 'cannot create atomic config file'
cat "$PRIMARY_TARGET/config.toml" > "$STAGED"
chmod 600 "$STAGED"
mv -f "$STAGED" "$BIN_DIR/config.toml"
STAGED=

# A direct symlink creation is atomic and refuses any path that appeared after
# the preflight. Managed aliases always use this exact relative target, so an
# update replaces only azdaja while an existing az link remains valid.
if [ "$ALIAS_CREATE" = true ]; then
  ln -s azdaja "$ALIAS" || fail "cannot create az alias without overwriting an existing path: $ALIAS"
fi

ON_PATH=false
OLD_IFS=$IFS
IFS=:
for candidate in ${PATH:-}; do
  if [ "$candidate" = "$BIN_DIR" ]; then
    ON_PATH=true
    break
  fi
done
IFS=$OLD_IFS
printf 'Detected: %s\n' "$DETECTION_REPORT"
printf 'Written: %s\n' "$WRITTEN"
if [ "$ON_PATH" = true ]; then
  printf 'Next: run az doctor (%s is on PATH)\n' "$BIN_DIR"
else
  printf 'Next: add %s to PATH, then run az doctor\n' "$BIN_DIR"
fi
