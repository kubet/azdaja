#!/bin/sh
set -eu
set -f

VERSION=0.1.3
GLIBC_MIN=2.35
RELEASE_BASE=https://azdaja.dev/releases/v$VERSION
HARNESS=
BIN_DIR=${AZDAJA_INSTALL_DIR:-}

usage() {
  printf '%s\n' 'Usage: install.sh [--all | TARGET[,TARGET...]] [--bin-dir DIR]'
}
fail() {
  printf 'azdaja install: %s\n' "$1" >&2
  exit "${2:-1}"
}

glibc_version_at_least() {
  awk -v actual="$1" -v required="$2" '
    BEGIN {
      if (actual !~ /^[0-9]+([.][0-9]+)*$/ || required !~ /^[0-9]+([.][0-9]+)*$/) {
        exit 2
      }
      actual_count = split(actual, actual_parts, ".")
      required_count = split(required, required_parts, ".")
      count = actual_count > required_count ? actual_count : required_count
      for (i = 1; i <= count; i++) {
        actual_part = i <= actual_count ? actual_parts[i] + 0 : 0
        required_part = i <= required_count ? required_parts[i] + 0 : 0
        if (actual_part > required_part) exit 0
        if (actual_part < required_part) exit 1
      }
      exit 0
    }
  '
}

linux_libc_unavailable() {
  fail "Linux x86-64 release binary requires glibc $GLIBC_MIN or newer; could not verify it with getconf GNU_LIBC_VERSION (musl is not supported). Use a glibc $GLIBC_MIN+ system or build from source with Rust 1.95."
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --all)
      [ -z "$HARNESS" ] || fail 'choose only one install target selection' 2
      HARNESS=all
      shift
      ;;
    jcode|claude|codex|gemini|opencode|all|*,*)
      [ -z "$HARNESS" ] || fail 'choose only one install target' 2
      HARNESS=$1
      shift
      ;;
    --harness)
      # Compatibility for older scripts. New help uses a positional target.
      [ "$#" -ge 2 ] || fail '--harness requires a value' 2
      [ -z "$HARNESS" ] || fail 'choose only one install target' 2
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

case "${HOME-}" in
  /*) ;;
  '') fail 'HOME is not set; use --bin-dir DIR and set HOME before installing' ;;
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
if [ "${XDG_DATA_HOME+x}" = x ]; then
  case "$XDG_DATA_HOME" in
    /*) DATA_ROOT=$XDG_DATA_HOME ;;
    *) fail 'XDG_DATA_HOME must be set to a non-empty absolute path' ;;
  esac
else
  DATA_ROOT=$HOME/.local/share
fi
DOC_DIR=$DATA_ROOT/azdaja

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

display_names() {
  display=
  for display_name in $1; do
    display="${display}${display:+, }$display_name"
  done
  printf '%s' "$display"
}

explicit_targets() {
  requested=$1
  if [ "$requested" = all ]; then
    INSTALL_NAMES='jcode claude codex gemini opencode'
    HARNESS=all
    DETECTION_REPORT='jcode, claude, codex, gemini, opencode'
    return
  fi
  case "$requested" in
    ''|,*|*,|*,,*) fail 'install target list contains an empty name' 2 ;;
  esac
  names=
  csv=
  old_ifs=$IFS
  IFS=,
  for name in $requested; do
    IFS=$old_ifs
    case "$name" in
      jcode|claude|codex|gemini|opencode) ;;
      *) fail "unknown install target '$name'" 2 ;;
    esac
    case " $names " in
      *" $name "*) fail "install target list contains duplicate tool '$name'" 2 ;;
      *)
        names="${names}${names:+ }$name"
        csv="${csv}${csv:+,}$name"
        ;;
    esac
    IFS=,
  done
  IFS=$old_ifs
  INSTALL_NAMES=$names
  HARNESS=$csv
  DETECTION_REPORT=$(display_names "$INSTALL_NAMES")
}

prompt_targets() {
  [ -n "$DETECTED" ] || fail 'no supported tool found; install Jcode, Claude, Codex, Gemini, or OpenCode, or name one: install.sh jcode'

  if [ "${AZDAJA_INSTALL_TEST_MODE:-}" = local ] && [ "${AZDAJA_INSTALL_SELECTION+x}" = x ]; then
    answer=$AZDAJA_INSTALL_SELECTION
    [ -n "$answer" ] || fail 'select at least one integration' 2
    case "$answer" in
      a|all)
        INSTALL_NAMES=$DETECTED
        ;;
      *)
        INSTALL_NAMES=
        for choice in $(printf '%s' "$answer" | tr ',' ' '); do
          selected=
          index=1
          for name in $DETECTED; do
            if [ "$choice" = "$index" ] || [ "$choice" = "$name" ]; then
              selected=$name
              break
            fi
            index=$((index + 1))
          done
          [ -n "$selected" ] || fail "invalid integration selection '$choice'" 2
          case " $INSTALL_NAMES " in
            *" $selected "*) ;;
            *) INSTALL_NAMES="${INSTALL_NAMES}${INSTALL_NAMES:+ }$selected" ;;
          esac
        done
        ;;
    esac
  else
    ( : < /dev/tty ) 2>/dev/null && ( : > /dev/tty ) 2>/dev/null || \
      fail 'interactive selection needs a terminal; rerun with --all or name targets, for example: install.sh jcode,codex' 2
    command -v stty >/dev/null 2>&1 || fail 'interactive selection requires stty; rerun with --all or name targets' 2
    command -v dd >/dev/null 2>&1 || fail 'interactive selection requires dd; rerun with --all or name targets' 2
    command -v od >/dev/null 2>&1 || fail 'interactive selection requires od; rerun with --all or name targets' 2

    menu_count=0
    for name in jcode claude codex gemini opencode; do
      menu_count=$((menu_count + 1))
      eval "menu_name_$menu_count=\$name"
      eval "menu_selected_$menu_count=false"
      case " $DETECTED " in
        *" $name "*) eval "menu_installed_$menu_count=true" ;;
        *) eval "menu_installed_$menu_count=false" ;;
      esac
    done
    menu_cursor=1
    menu_rendered=false
    menu_lines=$((menu_count + 1))
    menu_color=true
    [ -z "${NO_COLOR:-}" ] && [ "${TERM:-}" != dumb ] || menu_color=false

    render_menu() {
      if [ "$menu_rendered" = true ]; then
        printf '\033[%sA' "$menu_lines" > /dev/tty
      fi
      printf '\r\033[KSelect integrations  ↑/↓ move  Space toggle  Enter install\n' > /dev/tty
      menu_index=1
      while [ "$menu_index" -le "$menu_count" ]; do
        eval "menu_name=\$menu_name_$menu_index"
        eval "menu_selected=\$menu_selected_$menu_index"
        eval "menu_installed=\$menu_installed_$menu_index"
        if [ "$menu_index" -eq "$menu_cursor" ]; then menu_pointer='›'; else menu_pointer=' '; fi
        if [ "$menu_selected" = true ]; then menu_mark='x'; else menu_mark=' '; fi
        if [ "$menu_installed" = true ]; then
          if [ "$menu_color" = true ]; then
            printf '\r\033[K%s [%s] \033[32m%s  ● installed\033[0m\n' "$menu_pointer" "$menu_mark" "$menu_name" > /dev/tty
          else
            printf '\r\033[K%s [%s] %s  installed\n' "$menu_pointer" "$menu_mark" "$menu_name" > /dev/tty
          fi
        else
          printf '\r\033[K%s [%s] %s\n' "$menu_pointer" "$menu_mark" "$menu_name" > /dev/tty
        fi
        menu_index=$((menu_index + 1))
      done
      menu_rendered=true
    }

    read_menu_byte() {
      dd bs=1 count=1 2>/dev/null < /dev/tty | od -An -tu1 | tr -d ' '
    }

    menu_stty=$(stty -g < /dev/tty) || fail 'could not read terminal settings' 2
    restore_menu_terminal() {
      stty "$menu_stty" < /dev/tty >/dev/null 2>&1 || true
    }
    trap 'restore_menu_terminal; printf "\n" > /dev/tty; exit 130' HUP INT TERM
    stty -echo -icanon min 1 time 0 < /dev/tty || {
      restore_menu_terminal
      trap - HUP INT TERM
      fail 'could not enable interactive selection; rerun with --all or name targets' 2
    }

    render_menu
    while :; do
      menu_key=$(read_menu_byte)
      case "$menu_key" in
        27)
          menu_escape_1=$(read_menu_byte)
          menu_escape_2=$(read_menu_byte)
          if [ "$menu_escape_1" = 91 ]; then
            case "$menu_escape_2" in
              65)
                if [ "$menu_cursor" -gt 1 ]; then menu_cursor=$((menu_cursor - 1)); else menu_cursor=$menu_count; fi
                render_menu
                ;;
              66)
                if [ "$menu_cursor" -lt "$menu_count" ]; then menu_cursor=$((menu_cursor + 1)); else menu_cursor=1; fi
                render_menu
                ;;
            esac
          fi
          ;;
        32)
          eval "menu_selected=\$menu_selected_$menu_cursor"
          if [ "$menu_selected" = true ]; then
            eval "menu_selected_$menu_cursor=false"
          else
            eval "menu_selected_$menu_cursor=true"
          fi
          render_menu
          ;;
        10|13)
          INSTALL_NAMES=
          menu_index=1
          while [ "$menu_index" -le "$menu_count" ]; do
            eval "menu_selected=\$menu_selected_$menu_index"
            if [ "$menu_selected" = true ]; then
              eval "menu_name=\$menu_name_$menu_index"
              INSTALL_NAMES="${INSTALL_NAMES}${INSTALL_NAMES:+ }$menu_name"
            fi
            menu_index=$((menu_index + 1))
          done
          if [ -n "$INSTALL_NAMES" ]; then break; fi
          printf '\a' > /dev/tty
          ;;
      esac
    done
    restore_menu_terminal
    trap - HUP INT TERM
  fi

  [ -n "$INSTALL_NAMES" ] || fail 'select at least one integration' 2
  HARNESS=
  for name in $INSTALL_NAMES; do
    HARNESS="${HARNESS}${HARNESS:+,}$name"
  done
  DETECTION_REPORT=$(display_names "$INSTALL_NAMES")
}

if [ -z "$HARNESS" ]; then
  prompt_targets
else
  explicit_targets "$HARNESS"
fi

case "${AZDAJA_INSTALL_TEST_MODE:-}" in
  '')
    [ -z "${AZDAJA_INSTALL_BASE_URL:-}${AZDAJA_INSTALL_OS:-}${AZDAJA_INSTALL_ARCH:-}${AZDAJA_INSTALL_GLIBC_VERSION:-}${AZDAJA_INSTALL_SELECTION:-}" ] || \
      fail 'validation overrides require AZDAJA_INSTALL_TEST_MODE=local' 2
    [ "${AZDAJA_INSTALL_DOC_DIR+x}" != x ] || \
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
    if [ "${AZDAJA_INSTALL_DOC_DIR+x}" = x ]; then
      case "$AZDAJA_INSTALL_DOC_DIR" in
        /*) DOC_DIR=$AZDAJA_INSTALL_DOC_DIR ;;
        *) fail 'AZDAJA_INSTALL_DOC_DIR must be set to a non-empty absolute path' 2 ;;
      esac
    fi
    case "$BASE_URL" in
      http://127.0.0.1:*|http://localhost:*|https://*) ;;
      *) fail 'local validation URL must use loopback http:// or https://' 2 ;;
    esac
    ;;
  *) fail 'invalid AZDAJA_INSTALL_TEST_MODE' 2 ;;
esac

case "$OS-$ARCH" in
  Darwin-arm64) ASSET=azdaja-v$VERSION-darwin-arm64 ;;
  Linux-x86_64)
    ASSET=azdaja-v$VERSION-linux-x86_64
    if [ "${AZDAJA_INSTALL_TEST_MODE:-}" = local ]; then
      [ "${AZDAJA_INSTALL_GLIBC_VERSION+x}" = x ] && [ -n "$AZDAJA_INSTALL_GLIBC_VERSION" ] || \
        fail 'AZDAJA_INSTALL_GLIBC_VERSION is required for a Linux local-validation selector' 2
      GLIBC_VERSION=$AZDAJA_INSTALL_GLIBC_VERSION
    else
      command -v getconf >/dev/null 2>&1 || linux_libc_unavailable
      GLIBC_REPORT=$(getconf GNU_LIBC_VERSION 2>/dev/null) || linux_libc_unavailable
      case "$GLIBC_REPORT" in
        glibc\ *) GLIBC_VERSION=${GLIBC_REPORT#glibc } ;;
        *) linux_libc_unavailable ;;
      esac
    fi
    GLIBC_COMPARE_STATUS=0
    glibc_version_at_least "$GLIBC_VERSION" "$GLIBC_MIN" || GLIBC_COMPARE_STATUS=$?
    case "$GLIBC_COMPARE_STATUS" in
      0) ;;
      1) fail "Linux x86-64 release binary requires glibc $GLIBC_MIN or newer; found glibc $GLIBC_VERSION. Upgrade glibc/use a newer distribution, or build from source with Rust 1.95." ;;
      *) fail "Linux x86-64 release binary requires glibc $GLIBC_MIN or newer; getconf returned an invalid version. Use a glibc $GLIBC_MIN+ system or build from source with Rust 1.95." ;;
    esac
    ;;
  *) fail "unsupported platform $OS-$ARCH; v$VERSION binaries support Apple Silicon macOS 11+ and Linux x86-64 with glibc $GLIBC_MIN+" ;;
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
DOC_LICENSE=$DOC_DIR/LICENSE
DOC_NOTICES=$DOC_DIR/THIRD-PARTY-NOTICES.md
DOC_OWNER=$DOC_DIR/.azdaja-managed
DOC_LICENSE_CREATED=false
DOC_NOTICES_CREATED=false
DOC_OWNER_CREATED=false
DOC_MIGRATED=false
DOC_PREVIOUS=
DOC_LOCK=
DOC_LOCK_ACQUIRED=false
CREATED_DOC_DIRS=
DOC_STAGE_LICENSE=
DOC_STAGE_NOTICES=
DOC_STAGE_OWNER=
(umask 077 && mkdir "$TMP") || fail 'cannot create private staging directory'

rollback() {
  set +e
  [ "$DOC_OWNER_CREATED" = false ] || rm -f "$DOC_OWNER"
  [ "$DOC_NOTICES_CREATED" = false ] || rm -f "$DOC_NOTICES"
  [ "$DOC_LICENSE_CREATED" = false ] || rm -f "$DOC_LICENSE"
  if [ -n "$CREATED_DOC_DIRS" ]; then
    printf '%s\n' "$CREATED_DOC_DIRS" | awk 'NF { line[++n] = $0 } END { for (i = n; i > 0; i--) print line[i] }' |
      while IFS= read -r directory; do rmdir "$directory" 2>/dev/null || :; done
  fi
  if [ "$DOC_MIGRATED" = true ] && [ -n "$DOC_PREVIOUS" ] && \
     [ ! -e "$DOC_DIR" ] && [ ! -L "$DOC_DIR" ]; then
    mv "$DOC_PREVIOUS" "$DOC_DIR" || :
  fi
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
  [ -z "$DOC_STAGE_LICENSE" ] || rm -f "$DOC_STAGE_LICENSE"
  [ -z "$DOC_STAGE_NOTICES" ] || rm -f "$DOC_STAGE_NOTICES"
  [ -z "$DOC_STAGE_OWNER" ] || rm -f "$DOC_STAGE_OWNER"
  if [ "$DOC_LOCK_ACQUIRED" = true ] && [ -n "$DOC_LOCK" ]; then
    rmdir "$DOC_LOCK" 2>/dev/null || :
  fi
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
download "$BASE_URL/LICENSE" "$TMP/LICENSE"
download "$BASE_URL/THIRD-PARTY-NOTICES.md" "$TMP/THIRD-PARTY-NOTICES.md"

SUMS_SIZE=$(wc -c < "$TMP/SHA256SUMS" | tr -d ' ')
[ "$SUMS_SIZE" -le 1048576 ] || fail 'SHA256SUMS exceeds the 1 MiB download cap'
BIN_SIZE=$(wc -c < "$TMP/azdaja" | tr -d ' ')
[ "$BIN_SIZE" -le 67108864 ] || fail 'release binary exceeds the 64 MiB download cap'
LICENSE_SIZE=$(wc -c < "$TMP/LICENSE" | tr -d ' ')
[ "$LICENSE_SIZE" -le 1048576 ] || fail 'LICENSE exceeds the 1 MiB download cap'
NOTICES_SIZE=$(wc -c < "$TMP/THIRD-PARTY-NOTICES.md" | tr -d ' ')
[ "$NOTICES_SIZE" -le 4194304 ] || fail 'THIRD-PARTY-NOTICES.md exceeds the 4 MiB download cap'

DARWIN_ASSET=azdaja-v$VERSION-darwin-arm64
LINUX_ASSET=azdaja-v$VERSION-linux-x86_64
ENTRY_COUNT=$(awk 'NF { n += 1 } END { print n + 0 }' "$TMP/SHA256SUMS")
[ "$ENTRY_COUNT" -eq 4 ] || fail 'SHA256SUMS must contain exactly the two platform binaries, LICENSE, and THIRD-PARTY-NOTICES.md'
MALFORMED_ENTRY=$(awk 'NF && NF != 2 { print; exit }' "$TMP/SHA256SUMS")
[ -z "$MALFORMED_ENTRY" ] || fail 'SHA256SUMS contains a malformed payload entry'
UNKNOWN_ENTRY=$(awk -v darwin="$DARWIN_ASSET" -v linux="$LINUX_ASSET" '
  NF && $2 != darwin && $2 != "*" darwin && $2 != linux && $2 != "*" linux &&
    $2 != "LICENSE" && $2 != "*LICENSE" &&
    $2 != "THIRD-PARTY-NOTICES.md" && $2 != "*THIRD-PARTY-NOTICES.md" { print; exit }
' "$TMP/SHA256SUMS")
[ -z "$UNKNOWN_ENTRY" ] || fail 'SHA256SUMS contains an unexpected payload name'
manifest_sha256() {
  manifest_name=$1
  matches=$(awk -v asset="$manifest_name" '$2 == asset || $2 == "*" asset { print $1 }' "$TMP/SHA256SUMS")
  match_count=$(printf '%s\n' "$matches" | awk 'NF { n += 1 } END { print n + 0 }')
  [ "$match_count" -eq 1 ] || fail "SHA256SUMS must contain exactly one entry for $manifest_name"
  expected=$(printf '%s\n' "$matches" | awk 'NF { print; exit }')
  case "$expected" in
    *[!0-9a-f]*|'') fail "invalid SHA-256 entry for $manifest_name" ;;
  esac
  [ "${#expected}" -eq 64 ] || fail "invalid SHA-256 entry for $manifest_name"
  printf '%s' "$expected"
}
EXPECTED_SHA256=$(manifest_sha256 "$ASSET")
# Require the full supported release set even though this invocation downloads
# only its selected platform binary.
manifest_sha256 "$DARWIN_ASSET" >/dev/null
manifest_sha256 "$LINUX_ASSET" >/dev/null
EXPECTED_LICENSE_SHA256=$(manifest_sha256 LICENSE)
EXPECTED_NOTICES_SHA256=$(manifest_sha256 THIRD-PARTY-NOTICES.md)
ROOT_LICENSE_SHA256=45dd135e23e0e915b3dd61095d46eb45a8f59bbc53dadface6affbd1c76d7096
ROOT_NOTICES_SHA256=ee908558c8d5f0d2080400558db351d8f24fb7ad3ca902c904822d97d7b5eac6
[ "$EXPECTED_LICENSE_SHA256" = "$ROOT_LICENSE_SHA256" ] || fail 'SHA256SUMS does not bind the exact Azdaja LICENSE'
[ "$EXPECTED_NOTICES_SHA256" = "$ROOT_NOTICES_SHA256" ] || fail 'SHA256SUMS does not bind the exact reviewed THIRD-PARTY-NOTICES.md'

sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    fail 'shasum or sha256sum is required'
  fi
}
ACTUAL_SHA256=$(sha256_file "$TMP/azdaja")
ACTUAL_LICENSE_SHA256=$(sha256_file "$TMP/LICENSE")
ACTUAL_NOTICES_SHA256=$(sha256_file "$TMP/THIRD-PARTY-NOTICES.md")
[ "$ACTUAL_SHA256" = "$EXPECTED_SHA256" ] || fail 'SHA-256 mismatch for release binary; the existing installation was not changed'
[ "$ACTUAL_LICENSE_SHA256" = "$EXPECTED_LICENSE_SHA256" ] || fail 'SHA-256 mismatch for LICENSE; the existing installation was not changed'
[ "$ACTUAL_NOTICES_SHA256" = "$EXPECTED_NOTICES_SHA256" ] || fail 'SHA-256 mismatch for THIRD-PARTY-NOTICES.md; the existing installation was not changed'
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
DOC_OWNER_V1_MAGIC=azdaja-installer-owned-docs-v1
LEGACY_NOTICES_SHA256=dde4b0d189ff4fbc79748212bc0fc90bbf75dd27a4f23aaddbb24624e6e8cabb
printf '%s\n' "$OWNER_MAGIC" > "$TMP/config-owner.expected"
printf '%s\n' "$DOC_OWNER_V1_MAGIC" > "$TMP/doc-owner-v1.expected"
cat > "$TMP/doc-owner-v2.expected" <<EOF
azdaja-installer-owned-docs-v2
schema=azdaja-managed-documents-v2
LICENSE.sha256=$ROOT_LICENSE_SHA256
THIRD-PARTY-NOTICES.md.sha256=$ROOT_NOTICES_SHA256
EOF

owned_single_link_regular() {
  owned_path=$1
  [ -f "$owned_path" ] && [ ! -L "$owned_path" ] || return 1
  [ "$(find "$owned_path" -prune -type f -links 1 -user "$(id -u)" -print)" = "$owned_path" ]
}

printf '%s' "$DOC_DIR" > "$TMP/document-lock-key"
DOC_LOCK_KEY=$(sha256_file "$TMP/document-lock-key")
DOC_LOCK=${TMPDIR:-/tmp}/azdaja-document-install-$(id -u)-$DOC_LOCK_KEY.lock
(umask 077 && mkdir "$DOC_LOCK") 2>/dev/null || \
  fail "another Azdaja document lifecycle is active; retry after it completes"
DOC_LOCK_ACQUIRED=true

DOC_STATE=fresh
if [ -e "$DOC_DIR" ] || [ -L "$DOC_DIR" ]; then
  [ -d "$DOC_DIR" ] && [ ! -L "$DOC_DIR" ] || fail "refusing unsafe Azdaja document directory: $DOC_DIR"
  [ "$(find "$DOC_DIR" -prune -type d -user "$(id -u)" -print)" = "$DOC_DIR" ] || \
    fail "refusing document directory not owned by the current user: $DOC_DIR"
  FOREIGN_DOC=$(find "$DOC_DIR" ! -path "$DOC_DIR" \
    ! -path "$DOC_LICENSE" ! -path "$DOC_NOTICES" ! -path "$DOC_OWNER" -print)
  [ -z "$FOREIGN_DOC" ] || fail "refusing foreign entry in Azdaja document directory: $DOC_DIR"
  owned_single_link_regular "$DOC_LICENSE" || fail "refusing unsafe or unowned Azdaja LICENSE: $DOC_LICENSE"
  owned_single_link_regular "$DOC_NOTICES" || fail "refusing unsafe or unowned Azdaja notices: $DOC_NOTICES"
  owned_single_link_regular "$DOC_OWNER" || fail "refusing unsafe or unowned Azdaja document marker: $DOC_OWNER"
  if cmp -s "$DOC_OWNER" "$TMP/doc-owner-v2.expected"; then
    cmp -s "$DOC_LICENSE" "$TMP/LICENSE" || fail "refusing changed Azdaja LICENSE: $DOC_LICENSE"
    cmp -s "$DOC_NOTICES" "$TMP/THIRD-PARTY-NOTICES.md" || fail "refusing changed Azdaja notices: $DOC_NOTICES"
    DOC_STATE=owned-v2
  elif cmp -s "$DOC_OWNER" "$TMP/doc-owner-v1.expected"; then
    [ "$(sha256_file "$DOC_LICENSE")" = "$ROOT_LICENSE_SHA256" ] || \
      fail "refusing changed legacy Azdaja LICENSE: $DOC_LICENSE"
    [ "$(sha256_file "$DOC_NOTICES")" = "$LEGACY_NOTICES_SHA256" ] || \
      fail "refusing unsupported legacy Azdaja notices: $DOC_NOTICES"
    DOC_STATE=legacy-v1
  else
    fail "refusing foreign Azdaja document owner marker: $DOC_OWNER"
  fi
else
  DOC_ANCESTOR=$DOC_DIR
  while [ ! -e "$DOC_ANCESTOR" ] && [ ! -L "$DOC_ANCESTOR" ]; do
    DOC_PARENT=${DOC_ANCESTOR%/*}
    [ -n "$DOC_PARENT" ] || DOC_PARENT=/
    DOC_ANCESTOR=$DOC_PARENT
  done
  [ -d "$DOC_ANCESTOR" ] && [ ! -L "$DOC_ANCESTOR" ] || \
    fail "refusing unsafe Azdaja document ancestry: $DOC_ANCESTOR"
fi

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
if [ -L "$ALIAS" ]; then
  command -v readlink >/dev/null 2>&1 || fail 'readlink is required to validate the existing az alias'
  ALIAS_TARGET=$(readlink "$ALIAS") || fail "cannot inspect existing az alias: $ALIAS"
  if [ "$ALIAS_TARGET" = azdaja ]; then
    ALIAS_MANAGED=true
  else
    ALIAS_SKIP=true
  fi
elif [ -e "$ALIAS" ]; then
  ALIAS_SKIP=true
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
    fi
  fi
  [ "$PATH_LAST" = false ] || break
done

[ ! -d "$DEST" ] || fail "refusing to replace directory: $DEST"
DEST_BACKUP=$BIN_DIR/.azdaja-previous.$$
[ ! -e "$DEST_BACKUP" ] && [ ! -L "$DEST_BACKUP" ] || \
  fail "temporary binary backup path already exists: $DEST_BACKUP"

# Delegate the complete harness lifecycle to the verified Rust transaction. It
# first performs a read-only selected-set preflight, then locks, re-preflights,
# stages every target, and commits or rolls back as one unit. The shell never
# copies or recursively removes a harness target.
"$TMP/azdaja" install "$HARNESS" --preflight-only >/dev/null

PRIMARY_TARGET=
for harness in $INSTALL_NAMES; do
  TARGET=$(harness_target "$harness")
  [ -n "$PRIMARY_TARGET" ] || PRIMARY_TARGET=$TARGET
done

# The complete harness and document preflights are read-only. Start one shell
# transaction; the Rust harness mutation remains independently transactional.
# Rollback uses the original binary path entry itself (rename), never a recursive copy.
BIN_DIR_WAS_DIR=false
[ ! -d "$BIN_DIR" ] || BIN_DIR_WAS_DIR=true
TRANSACTION_ACTIVE=true

if [ "$DOC_STATE" = legacy-v1 ]; then
  DOC_PREVIOUS=$DOC_DIR.azdaja-v1-previous.$$
  [ ! -e "$DOC_PREVIOUS" ] && [ ! -L "$DOC_PREVIOUS" ] || \
    fail "document migration quarantine already exists: $DOC_PREVIOUS"
  mv "$DOC_DIR" "$DOC_PREVIOUS" || fail "cannot quarantine legacy Azdaja documents for migration: $DOC_DIR"
  DOC_MIGRATED=true
  PREVIOUS_LICENSE=$DOC_PREVIOUS/LICENSE
  PREVIOUS_NOTICES=$DOC_PREVIOUS/THIRD-PARTY-NOTICES.md
  PREVIOUS_OWNER=$DOC_PREVIOUS/.azdaja-managed
  [ -d "$DOC_PREVIOUS" ] && [ ! -L "$DOC_PREVIOUS" ] || \
    fail "legacy Azdaja document directory changed during migration"
  [ "$(find "$DOC_PREVIOUS" -prune -type d -user "$(id -u)" -print)" = "$DOC_PREVIOUS" ] || \
    fail "legacy Azdaja document directory ownership changed during migration"
  PREVIOUS_FOREIGN=$(find "$DOC_PREVIOUS" ! -path "$DOC_PREVIOUS" \
    ! -path "$PREVIOUS_LICENSE" ! -path "$PREVIOUS_NOTICES" ! -path "$PREVIOUS_OWNER" -print)
  [ -z "$PREVIOUS_FOREIGN" ] || fail "legacy Azdaja document directory changed during migration"
  owned_single_link_regular "$PREVIOUS_LICENSE" || fail "legacy Azdaja LICENSE changed during migration"
  owned_single_link_regular "$PREVIOUS_NOTICES" || fail "legacy Azdaja notices changed during migration"
  owned_single_link_regular "$PREVIOUS_OWNER" || fail "legacy Azdaja marker changed during migration"
  cmp -s "$PREVIOUS_OWNER" "$TMP/doc-owner-v1.expected" || fail "legacy Azdaja marker changed during migration"
  [ "$(sha256_file "$PREVIOUS_LICENSE")" = "$ROOT_LICENSE_SHA256" ] || \
    fail "legacy Azdaja LICENSE changed during migration"
  [ "$(sha256_file "$PREVIOUS_NOTICES")" = "$LEGACY_NOTICES_SHA256" ] || \
    fail "legacy Azdaja notices changed during migration"
  DOC_STATE=fresh
fi

if [ "$DOC_STATE" = fresh ]; then
  TO_CREATE=
  CURRENT_DIR=$DOC_DIR
  while [ ! -e "$CURRENT_DIR" ] && [ ! -L "$CURRENT_DIR" ]; do
    TO_CREATE="${TO_CREATE}${TO_CREATE:+
}$CURRENT_DIR"
    PARENT_DIR=${CURRENT_DIR%/*}
    [ -n "$PARENT_DIR" ] || PARENT_DIR=/
    CURRENT_DIR=$PARENT_DIR
  done
  CREATE_ORDER=$(printf '%s\n' "$TO_CREATE" | awk 'NF { line[++n] = $0 } END { for (i = n; i > 0; i--) print line[i] }')
  OLD_IFS=$IFS
  IFS='
'
  for directory in $CREATE_ORDER; do
    IFS=$OLD_IFS
    (umask 077 && mkdir "$directory") || fail "cannot create Azdaja document directory: $directory"
    CREATED_DOC_DIRS="${CREATED_DOC_DIRS}${CREATED_DOC_DIRS:+
}$directory"
    IFS='
'
  done
  IFS=$OLD_IFS
  [ -d "$DOC_DIR" ] && [ ! -L "$DOC_DIR" ] && [ -w "$DOC_DIR" ] || \
    fail "Azdaja document directory is not safely writable: $DOC_DIR"

  DOC_STAGE_LICENSE=$DOC_DIR/.azdaja-license.$$
  DOC_STAGE_NOTICES=$DOC_DIR/.azdaja-notices.$$
  DOC_STAGE_OWNER=$DOC_DIR/.azdaja-doc-owner.$$
  for stage in "$DOC_STAGE_LICENSE" "$DOC_STAGE_NOTICES" "$DOC_STAGE_OWNER"; do
    [ ! -e "$stage" ] && [ ! -L "$stage" ] || fail "temporary document path already exists: $stage"
    (umask 077 && set -C && : > "$stage") 2>/dev/null || fail "cannot create atomic document file: $stage"
  done
  cat "$TMP/LICENSE" > "$DOC_STAGE_LICENSE"
  cat "$TMP/THIRD-PARTY-NOTICES.md" > "$DOC_STAGE_NOTICES"
  cat "$TMP/doc-owner-v2.expected" > "$DOC_STAGE_OWNER"
  chmod 600 "$DOC_STAGE_LICENSE" "$DOC_STAGE_NOTICES" "$DOC_STAGE_OWNER"
  ln "$DOC_STAGE_LICENSE" "$DOC_LICENSE" || fail "cannot install LICENSE without overwriting: $DOC_LICENSE"
  DOC_LICENSE_CREATED=true
  ln "$DOC_STAGE_NOTICES" "$DOC_NOTICES" || fail "cannot install notices without overwriting: $DOC_NOTICES"
  DOC_NOTICES_CREATED=true
  ln "$DOC_STAGE_OWNER" "$DOC_OWNER" || fail "cannot install document marker without overwriting: $DOC_OWNER"
  DOC_OWNER_CREATED=true
  rm -f "$DOC_STAGE_LICENSE" "$DOC_STAGE_NOTICES" "$DOC_STAGE_OWNER"
  DOC_STAGE_LICENSE=
  DOC_STAGE_NOTICES=
  DOC_STAGE_OWNER=
fi

# Commit the verified Rust harness transaction after document creation. If it
# refuses or rolls back, the shell trap removes the fresh document set.
"$TMP/azdaja" install "$HARNESS" >/dev/null

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
else
  if [ "$ALIAS_MANAGED" = true ]; then
    [ -L "$ALIAS" ] && [ "$(readlink "$ALIAS")" = azdaja ] || \
      fail "az alias changed during installation: $ALIAS"
  else
    ln -s azdaja "$ALIAS" || \
      fail "cannot create az alias without overwriting an existing path: $ALIAS"
    ALIAS_CREATED=true
  fi
fi

# Every preflighted standalone surface is committed. Subsequent cleanup is
# best-effort and cannot turn the completed install into a reported failure.
TRANSACTION_ACTIVE=false
if [ "$DEST_BACKUP_CREATED" = true ]; then
  rm -f "$DEST_BACKUP" || :
  DEST_BACKUP_CREATED=false
fi
if [ "$DOC_MIGRATED" = true ] && [ -n "$DOC_PREVIOUS" ]; then
  rm -f "$DOC_PREVIOUS/.azdaja-managed"     "$DOC_PREVIOUS/THIRD-PARTY-NOTICES.md" "$DOC_PREVIOUS/LICENSE" || :
  rmdir "$DOC_PREVIOUS" 2>/dev/null || :
  DOC_PREVIOUS=
fi

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
printf 'Installed: azdaja v%s\n' "$VERSION"
printf 'Integrations: %s\n' "$DETECTION_REPORT"
if [ "$ALIAS_SKIP" = true ]; then
  if [ "$ON_PATH" = true ]; then
    printf 'Next: azdaja doctor (az alias unavailable)\n'
  else
    DOCTOR_COMMAND=$(shell_quote "$BIN_DIR_KEY/azdaja")
    printf 'Next: %s doctor\n' "$DOCTOR_COMMAND"
  fi
elif [ "$ON_PATH" = true ]; then
  printf 'Next: az doctor\n'
else
  DOCTOR_COMMAND=$(shell_quote "$BIN_DIR_KEY/azdaja")
  printf 'Next: %s doctor\n' "$DOCTOR_COMMAND"
fi
