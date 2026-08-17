#!/bin/sh
set -eu

[ "$#" -eq 1 ] || { printf '%s\n' 'usage: run-platform-gate.sh /path/to/asset' >&2; exit 2; }
ASSET=$(CDPATH= cd -- "$(dirname -- "$1")" && pwd)/$(basename -- "$1")
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
case "$(uname -s)-$(uname -m)" in
  Darwin-arm64)
    NAME=azdaja-v0.1.1-darwin-arm64
    EXPECTED=b58975de462e823adcf901e331acfd4e70c9e72b5db014de265c04e371d31883
    ;;
  Linux-x86_64)
    NAME=azdaja-v0.1.1-linux-x86_64
    EXPECTED=b18775f0d3572b20804ff3c3af880ffc5fa3131017c566dc941c1dd743c00247
    ;;
  *) printf '%s\n' 'platform gate: unsupported host' >&2; exit 2 ;;
esac
[ "$(basename -- "$ASSET")" = "$NAME" ] || { printf '%s\n' 'platform gate: wrong asset name' >&2; exit 2; }
if command -v shasum >/dev/null 2>&1; then
  ACTUAL=$(shasum -a 256 "$ASSET" | awk '{print $1}')
else
  ACTUAL=$(sha256sum "$ASSET" | awk '{print $1}')
fi
[ "$ACTUAL" = "$EXPECTED" ] || { printf '%s\n' 'platform gate: asset digest mismatch' >&2; exit 1; }

SCRATCH=$(mktemp -d)
HOME_GATE=$SCRATCH/home
TOOLS=$SCRATCH/provider-guard
MARKER=$SCRATCH/provider-called
mkdir -p "$HOME_GATE" "$TOOLS"
cleanup() {
  pidfile=$HOME_GATE/.local/state/azdaja/jcode-api/bridge.pid
  if [ -f "$pidfile" ]; then
    pid=$(cat "$pidfile" 2>/dev/null || true)
    case "$pid" in *[!0-9]*|'') ;; *) kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true ;; esac
  fi
  rm -rf "$SCRATCH"
}
trap cleanup EXIT HUP INT TERM
for tool in jcode claude codex gemini opencode; do
  cat > "$TOOLS/$tool" <<EOF
#!/bin/sh
printf called > "$MARKER"
exit 93
EOF
  chmod 755 "$TOOLS/$tool"
done

HOME="$HOME_GATE" PATH="$TOOLS:$PATH" \
  AZDAJA_INSTALL_TEST_MODE=local \
  AZDAJA_INSTALL_URL="file://$ASSET" \
  AZDAJA_INSTALL_SHA256="$EXPECTED" \
  sh "$ROOT/site/install"
INSTALLED=$HOME_GATE/.jcode/skills/azdaja/azdaja
cmp "$ASSET" "$INSTALLED"
[ ! -e "$MARKER" ]
[ "$("$INSTALLED" --version)" = 'azdaja 0.1.1 (monty 0.0.21)' ]
"$INSTALLED" doctor --caps | grep -F '"azdaja":"0.1.1"' >/dev/null

if [ "${AZDAJA_LIVE_DOCTOR:-0}" = 1 ]; then
  [ -f "${AZDAJA_OAUTH_SOURCE:-}" ] || {
    printf '%s\n' 'platform gate: AZDAJA_OAUTH_SOURCE must name an owner-only OAuth credential' >&2
    exit 2
  }
  (umask 077 && cp "$AZDAJA_OAUTH_SOURCE" "$HOME_GATE/.jcode/openai-auth.json")
  chmod 600 "$HOME_GATE/.jcode/openai-auth.json"
  HOME="$HOME_GATE" "$INSTALLED" doctor
fi

(
  cd "$ROOT"
  CARGO_TARGET_DIR="$SCRATCH/cargo-target" AZDAJA_PRODUCT_BINARY="$INSTALLED" \
    cargo test --test product_50mb --locked -- --test-threads=1
)
printf '\n# v0.1.1-gate-custom\n' >> "$HOME_GATE/.jcode/skills/azdaja/config.toml"
HOME="$HOME_GATE" PATH="$TOOLS:$PATH" \
  AZDAJA_INSTALL_TEST_MODE=local \
  AZDAJA_INSTALL_URL="file://$ASSET" \
  AZDAJA_INSTALL_SHA256="$EXPECTED" \
  sh "$ROOT/site/install"
grep -Fx '# v0.1.1-gate-custom' "$HOME_GATE/.jcode/skills/azdaja/config.toml" >/dev/null
HOME="$HOME_GATE" "$INSTALLED" uninstall --harness jcode
[ ! -e "$HOME_GATE/.jcode/skills/azdaja" ]
[ ! -e "$MARKER" ]
printf '%s\n' "platform gate PASS: $NAME $EXPECTED"
