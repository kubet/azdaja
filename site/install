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

case "${HOME-}" in
  /*) ;;
  '') fail 'HOME is not set; use --bin-dir DIR and set HOME before installing a harness' ;;
  *) fail 'HOME must be set to an absolute path' ;;
esac
if [ "${JCODE_HOME+x}" = x ]; then
  case "$JCODE_HOME" in
    /*) JCODE_ROOT=$JCODE_HOME ;;
    *) fail 'JCODE_HOME must be set to a non-empty absolute path' ;;
  esac
else
  JCODE_ROOT=$HOME/.jcode
fi

DETECTED=
add_detected() {
  case " $DETECTED " in
    *" $1 "*) ;;
    *) DETECTED="${DETECTED}${DETECTED:+ }$1" ;;
  esac
}
if [ -d "$JCODE_ROOT" ] || command -v jcode >/dev/null 2>&1 || command -v jcode-api >/dev/null 2>&1; then
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
case "${XDG_CONFIG_HOME-}" in
  /*) CONFIG_ROOT=$XDG_CONFIG_HOME ;;
  *) CONFIG_ROOT=$HOME/.config ;;
esac
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

case "$INSTALL_NAMES" in
  jcode)
    RELOAD_INSTRUCTION='in Jcode run skill_manage reload_all or /skills -> Reload all (or restart Jcode)'
    ;;
  claude) RELOAD_INSTRUCTION='restart Claude to reload its skills' ;;
  codex) RELOAD_INSTRUCTION='restart Codex to reload its skills' ;;
  gemini) RELOAD_INSTRUCTION='restart Gemini to reload its skills' ;;
  opencode) RELOAD_INSTRUCTION='restart OpenCode to reload its skills' ;;
  'jcode claude codex gemini opencode') RELOAD_INSTRUCTION='reload/restart all five harnesses' ;;
  *)
    RELOAD_NAMES=$(printf '%s' "$INSTALL_NAMES" | tr ' ' ',')
    RELOAD_NAMES=$(printf '%s' "$RELOAD_NAMES" | sed 's/,/, /g')
    RELOAD_INSTRUCTION="reload/restart the selected harnesses ($RELOAD_NAMES)"
    ;;
esac

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

harness_target() {
  case "$1" in
    jcode) printf '%s' "$JCODE_ROOT/skills/azdaja" ;;
    claude) printf '%s' "$HOME/.claude/skills/azdaja" ;;
    codex) printf '%s' "$HOME/.agents/skills/azdaja" ;;
    gemini) printf '%s' "$HOME/.gemini/skills/azdaja" ;;
    opencode) printf '%s' "$CONFIG_ROOT/opencode/skills/azdaja" ;;
  esac
}

# Stage and verify entirely outside HOME. Failure before verification must not
# create the binary directory, managed harness files, configuration, or alias.
TMP=${TMPDIR:-/tmp}/azdaja-install.$$
STAGED=
STAGED_EXTRA=
TRANSACTION_ACTIVE=false
BIN_DIR_CREATED=false
DEST_MUTATED=false
DEST_HAD_OLD=false
DEST_BACKUP_CREATED=false
DEST_BACKUP=
CONFIG_CREATED=false
OWNER_CREATED=false
ALIAS_CREATED=false
ALIAS_REMOVED=false
DEST=
ALIAS=
CONFIG_PATH=
CONFIG_OWNER=
(umask 077 && mkdir "$TMP") || fail 'cannot create private staging directory'

rollback() {
  set +e
  if [ "$ALIAS_CREATED" = true ] && [ -L "$ALIAS" ] && [ "$(readlink "$ALIAS" 2>/dev/null)" = azdaja ]; then
    rm -f "$ALIAS"
  fi
  if [ "$ALIAS_REMOVED" = true ] && [ ! -e "$ALIAS" ] && [ ! -L "$ALIAS" ]; then
    ln -s azdaja "$ALIAS"
  fi
  [ "$OWNER_CREATED" = false ] || rm -f "$CONFIG_OWNER"
  [ "$CONFIG_CREATED" = false ] || rm -f "$CONFIG_PATH"
  if [ "$DEST_MUTATED" = true ]; then
    rm -f "$DEST"
    if [ "$DEST_HAD_OLD" = true ] && [ -n "$DEST_BACKUP" ]; then
      mv -f "$DEST_BACKUP" "$DEST"
      DEST_BACKUP_CREATED=false
    fi
  fi
  if [ "$DEST_BACKUP_CREATED" = true ] && [ -n "$DEST_BACKUP" ]; then
    rm -f "$DEST_BACKUP"
  fi
  if [ "$BIN_DIR_CREATED" = true ]; then
    rmdir "$BIN_DIR" 2>/dev/null || :
  fi
  set -e
}

cleanup() {
  status=$?
  trap - 0
  if [ "$TRANSACTION_ACTIVE" = true ]; then
    rollback
  fi
  [ -z "$STAGED" ] || rm -f "$STAGED"
  [ -z "$STAGED_EXTRA" ] || rm -f "$STAGED_EXTRA"
  rm -rf "$TMP"
  exit "$status"
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
CONFIG_PATH=$BIN_DIR/azdaja-config.toml
CONFIG_OWNER=$BIN_DIR/azdaja-config.toml.managed
OWNER_MAGIC=azdaja-installer-owned-config-v1
printf '%s\n' "$OWNER_MAGIC" > "$TMP/config-owner.expected"

if [ -L "$BIN_DIR" ] || { [ -e "$BIN_DIR" ] && [ ! -d "$BIN_DIR" ]; }; then
  fail "refusing unsafe binary directory: $BIN_DIR"
fi

# Refuse ambiguous adjacent configuration before the binary, harnesses, or
# alias can be changed. A matching owner manifest permits user customization:
# an owned config is deliberately preserved byte-for-byte on reinstall.
CONFIG_STATE=fresh
if [ -L "$CONFIG_PATH" ] || [ -L "$CONFIG_OWNER" ]; then
  fail "refusing ambiguous Azdaja config symlink or owner marker in $BIN_DIR"
fi
if [ -e "$CONFIG_PATH" ] || [ -e "$CONFIG_OWNER" ]; then
  if [ -f "$CONFIG_PATH" ] && [ -f "$CONFIG_OWNER" ] && \
     cmp -s "$CONFIG_OWNER" "$TMP/config-owner.expected"; then
    CONFIG_STATE=owned
  else
    fail "refusing unowned or incomplete Azdaja config state in $BIN_DIR"
  fi
fi

# The alias is managed only when it is this exact relative link. A foreign
# path in BIN_DIR is preserved and causes the optional alias to be skipped.
ALIAS_MANAGED=false
ALIAS_SKIP=false
FOREIGN_AZ=
if [ -L "$ALIAS" ]; then
  command -v readlink >/dev/null 2>&1 || fail 'readlink is required to validate the existing az alias'
  ALIAS_TARGET=$(readlink "$ALIAS") || fail "cannot inspect existing az alias: $ALIAS"
  if [ "$ALIAS_TARGET" = azdaja ]; then
    ALIAS_MANAGED=true
  else
    ALIAS_SKIP=true
    FOREIGN_AZ=$ALIAS
  fi
elif [ -e "$ALIAS" ]; then
  ALIAS_SKIP=true
  FOREIGN_AZ=$ALIAS
fi

# Scan every PATH component, including non-executable files, dangling links,
# later entries, and empty components (the current directory). command -v is
# intentionally insufficient because an installed alias must not shadow Azure
# CLI or any other foreign az path that happens to resolve later.
START_DIR=$(pwd -P)
path_dir_key() {
  path_dir=$1
  [ -n "$path_dir" ] || path_dir=$START_DIR
  if [ -d "$path_dir" ]; then
    (CDPATH= cd -P "$path_dir" 2>/dev/null && pwd -P)
  else
    case "$path_dir" in
      /*) printf '%s\n' "${path_dir%/}" ;;
      *) printf '%s\n' "$START_DIR/${path_dir%/}" ;;
    esac
  fi
}
shell_quote() {
  quoted=$(printf '%s' "$1" | sed "s/'/'\\\\''/g")
  printf "'%s'" "$quoted"
}
BIN_DIR_KEY=$(path_dir_key "$BIN_DIR")
PATH_REST=${PATH:-}
while :; do
  case "$PATH_REST" in
    *:*) PATH_ENTRY=${PATH_REST%%:*}; PATH_REST=${PATH_REST#*:}; PATH_LAST=false ;;
    *) PATH_ENTRY=$PATH_REST; PATH_REST=; PATH_LAST=true ;;
  esac
  [ -n "$PATH_ENTRY" ] || PATH_ENTRY=.
  PATH_AZ=$PATH_ENTRY/az
  if [ -e "$PATH_AZ" ] || [ -L "$PATH_AZ" ]; then
    PATH_ENTRY_KEY=$(path_dir_key "$PATH_ENTRY")
    if [ "$PATH_ENTRY_KEY" != "$BIN_DIR_KEY" ] || [ "$ALIAS_MANAGED" != true ]; then
      ALIAS_SKIP=true
      [ -n "$FOREIGN_AZ" ] || FOREIGN_AZ=$PATH_AZ
    fi
  fi
  [ "$PATH_LAST" = false ] || break
done

[ ! -d "$DEST" ] || fail "refusing to replace directory: $DEST"
DEST_BACKUP=$BIN_DIR/.azdaja-previous.$$
[ ! -e "$DEST_BACKUP" ] && [ ! -L "$DEST_BACKUP" ] || \
  fail "temporary binary backup path already exists: $DEST_BACKUP"

# Ask the downloaded, verified binary to preflight the complete selected set.
# This is read-only: an unowned, linked, symlinked, changed, or unknown target
# refuses before any harness, standalone binary, configuration, or alias entry
# is changed. The managed Rust installer repeats the same complete preflight.
if [ -z "$HARNESS" ]; then
  "$TMP/azdaja" install --preflight-only >/dev/null
  "$TMP/azdaja" install >/dev/null
else
  "$TMP/azdaja" install --harness "$HARNESS" --preflight-only >/dev/null
  "$TMP/azdaja" install --harness "$HARNESS" >/dev/null
fi

PRIMARY_TARGET=
HARNESS_WRITTEN=
for harness in $INSTALL_NAMES; do
  TARGET=$(harness_target "$harness")
  HARNESS_WRITTEN="$HARNESS_WRITTEN; $harness -> $TARGET"
  [ -n "$PRIMARY_TARGET" ] || PRIMARY_TARGET=$TARGET
done

# Commit the standalone surfaces only after the custody-safe Rust transaction.
# Rollback uses the original path entry itself (rename), never a recursive copy.
BIN_DIR_WAS_DIR=false
[ ! -d "$BIN_DIR" ] || BIN_DIR_WAS_DIR=true
TRANSACTION_ACTIVE=true
(umask 077 && mkdir -p "$BIN_DIR") || fail "cannot create binary directory $BIN_DIR"
if [ "$BIN_DIR_WAS_DIR" = false ]; then
  BIN_DIR_CREATED=true
fi
[ -d "$BIN_DIR" ] && [ -w "$BIN_DIR" ] || fail "binary directory is not writable: $BIN_DIR"

STAGED=$BIN_DIR/.azdaja-install.$$
[ ! -e "$STAGED" ] && [ ! -L "$STAGED" ] || fail "temporary install path already exists: $STAGED"
(umask 077 && set -C && : > "$STAGED") 2>/dev/null || fail 'cannot create atomic install file'
cat "$TMP/azdaja" > "$STAGED"
chmod 755 "$STAGED"
if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  mv "$DEST" "$DEST_BACKUP" || fail 'cannot retain the existing azdaja binary path entry'
  DEST_BACKUP_CREATED=true
  DEST_HAD_OLD=true
fi
DEST_MUTATED=true
mv -f "$STAGED" "$DEST"
STAGED=

WRITTEN="azdaja -> $DEST ($ASSET)$HARNESS_WRITTEN"

# Bind the standalone PATH binary to the first selected harness. The generic
# adjacent config.toml name is never written: Config::load support for this
# Azdaja-specific path is integrated separately.
if [ "$CONFIG_STATE" = fresh ]; then
  CONFIG_STAGE=$BIN_DIR/.azdaja-config.$$
  OWNER_STAGE=$BIN_DIR/.azdaja-config-owner.$$
  [ ! -e "$CONFIG_STAGE" ] && [ ! -L "$CONFIG_STAGE" ] || \
    fail "temporary config path already exists: $CONFIG_STAGE"
  [ ! -e "$OWNER_STAGE" ] && [ ! -L "$OWNER_STAGE" ] || \
    fail "temporary config owner path already exists: $OWNER_STAGE"
  STAGED=$CONFIG_STAGE
  STAGED_EXTRA=$OWNER_STAGE
  (umask 077 && set -C && : > "$CONFIG_STAGE") 2>/dev/null || \
    fail 'cannot create atomic config file'
  cat "$PRIMARY_TARGET/config.toml" > "$CONFIG_STAGE"
  chmod 600 "$CONFIG_STAGE"
  (umask 077 && set -C && : > "$OWNER_STAGE") 2>/dev/null || \
    fail 'cannot create atomic config owner file'
  printf '%s\n' "$OWNER_MAGIC" > "$OWNER_STAGE"
  chmod 600 "$OWNER_STAGE"
  if ! ln "$CONFIG_STAGE" "$CONFIG_PATH"; then
    fail "cannot create Azdaja config without overwriting an existing path: $CONFIG_PATH"
  fi
  CONFIG_CREATED=true
  if ! ln "$OWNER_STAGE" "$CONFIG_OWNER"; then
    rm -f "$CONFIG_PATH"
    CONFIG_CREATED=false
    fail "cannot create Azdaja config owner without overwriting an existing path: $CONFIG_OWNER"
  fi
  OWNER_CREATED=true
  rm -f "$CONFIG_STAGE" "$OWNER_STAGE"
  STAGED=
  STAGED_EXTRA=
  WRITTEN="$WRITTEN; config -> $CONFIG_PATH; config owner -> $CONFIG_OWNER"
else
  WRITTEN="$WRITTEN; config preserved -> $CONFIG_PATH; config owner -> $CONFIG_OWNER"
fi

# A direct relative symlink creation is atomic. If a foreign az exists anywhere
# on PATH, remove only an exact previously-managed local alias so it cannot
# shadow that command; all foreign paths themselves remain untouched.
if [ "$ALIAS_SKIP" = true ]; then
  if [ "$ALIAS_MANAGED" = true ]; then
    [ -L "$ALIAS" ] && [ "$(readlink "$ALIAS")" = azdaja ] || \
      fail "az alias changed during installation: $ALIAS"
    rm -f "$ALIAS" || fail "cannot remove managed az alias after foreign PATH collision: $ALIAS"
    ALIAS_REMOVED=true
  fi
  WRITTEN="$WRITTEN; short alias skipped (foreign az: $FOREIGN_AZ)"
else
  if [ "$ALIAS_MANAGED" = true ]; then
    [ -L "$ALIAS" ] && [ "$(readlink "$ALIAS")" = azdaja ] || \
      fail "az alias changed during installation: $ALIAS"
  else
    ln -s azdaja "$ALIAS" || \
      fail "cannot create az alias without overwriting an existing path: $ALIAS"
    ALIAS_CREATED=true
  fi
  WRITTEN="$WRITTEN; az -> $ALIAS (alias to azdaja)"
fi

# Only discard rollback material after every install surface is committed.
if [ "$DEST_BACKUP_CREATED" = true ]; then
  rm -f "$DEST_BACKUP"
  DEST_BACKUP_CREATED=false
fi
TRANSACTION_ACTIVE=false

ON_PATH=false
PATH_REST=${PATH:-}
while :; do
  case "$PATH_REST" in
    *:*) PATH_ENTRY=${PATH_REST%%:*}; PATH_REST=${PATH_REST#*:}; PATH_LAST=false ;;
    *) PATH_ENTRY=$PATH_REST; PATH_REST=; PATH_LAST=true ;;
  esac
  [ -n "$PATH_ENTRY" ] || PATH_ENTRY=.
  if [ "$(path_dir_key "$PATH_ENTRY")" = "$BIN_DIR_KEY" ]; then
    ON_PATH=true
  fi
  [ "$PATH_LAST" = false ] || break
done
printf 'Detected: %s\n' "$DETECTION_REPORT"
printf 'Written: %s\n' "$WRITTEN"
if [ "$ALIAS_SKIP" = true ]; then
  if [ "$ON_PATH" = true ]; then
    printf 'Next: run azdaja doctor, then %s (%s is on PATH; short alias skipped)\n' "$RELOAD_INSTRUCTION" "$BIN_DIR"
  else
    DOCTOR_COMMAND=$(shell_quote "$BIN_DIR_KEY/azdaja")
    printf 'Next: run %s doctor, then %s; add %s to PATH for bare azdaja commands (short alias skipped)\n' "$DOCTOR_COMMAND" "$RELOAD_INSTRUCTION" "$BIN_DIR"
  fi
elif [ "$ON_PATH" = true ]; then
  printf 'Next: run az doctor, then %s (%s is on PATH)\n' "$RELOAD_INSTRUCTION" "$BIN_DIR"
else
  DOCTOR_COMMAND=$(shell_quote "$BIN_DIR_KEY/azdaja")
  printf 'Next: run %s doctor, then %s; add %s to PATH for az/azdaja commands\n' "$DOCTOR_COMMAND" "$RELOAD_INSTRUCTION" "$BIN_DIR"
fi
