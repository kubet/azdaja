#!/bin/sh
set -eu

VERSION=0.1.1
case "$(uname -s)-$(uname -m)" in
  Darwin-arm64)
    TARGET=aarch64-apple-darwin
    ASSET=azdaja-v0.1.1-darwin-arm64
    EXPECTED=b58975de462e823adcf901e331acfd4e70c9e72b5db014de265c04e371d31883
    ;;
  Linux-x86_64)
    TARGET=x86_64-unknown-linux-gnu
    ASSET=azdaja-v0.1.1-linux-x86_64
    EXPECTED=b18775f0d3572b20804ff3c3af880ffc5fa3131017c566dc941c1dd743c00247
    ;;
  *)
    printf '%s\n' 'build-asset: requires native Darwin-arm64 or Linux-x86_64' >&2
    exit 2
    ;;
esac

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$ROOT"
[ "$(rustc --version)" = 'rustc 1.95.0 (59807616e 2026-04-14)' ] || {
  printf '%s\n' 'build-asset: exact Rust 1.95.0 toolchain required' >&2
  exit 2
}
if [ "${AZDAJA_ALLOW_DIRTY_PREDICTION:-0}" != 1 ]; then
  test -z "$(git status --short)" || {
    printf '%s\n' 'build-asset: final rebuild requires a clean source commit' >&2
    exit 2
  }
fi
if [ "$TARGET" = aarch64-apple-darwin ]; then
  [ "$(shasum -a 256 /usr/bin/codesign | awk '{print $1}')" = 214d455584d19abc0d74d02b9cbc7d3da6bdcb0596c235e6156dd9ed2f4e1ba7 ] || {
    printf '%s\n' 'build-asset: unbound codesign executable' >&2
    exit 2
  }
  CODESIGN_ALLOCATE=$(/usr/bin/xcrun --find codesign_allocate)
  [ "$(shasum -a 256 "$CODESIGN_ALLOCATE" | awk '{print $1}')" = 3930ed7b7849c1a16ad0074c2efb5c906156cd9034510f6b08bebaf48e16f39f ] || {
    printf '%s\n' 'build-asset: unbound codesign_allocate executable' >&2
    exit 2
  }
  [ "$(shasum -a 256 "$ROOT/release/v0.1.1/normalize-darwin.py" | awk '{print $1}')" = 369f23c05288e24745a61296564e6b8d95836441ac41d1c96a4b08c521ada629 ] || {
    printf '%s\n' 'build-asset: Darwin normalizer identity mismatch' >&2
    exit 2
  }
fi
OUT=${AZDAJA_DIST_DIR:-$ROOT/dist-v0.1.1}
TARGET_DIR=${AZDAJA_TARGET_DIR:-${TMPDIR:-/tmp}/azdaja-v0.1.1-target}
rm -rf "$TARGET_DIR"
mkdir -p "$OUT"
CARGO_INCREMENTAL=0 SOURCE_DATE_EPOCH=0 CARGO_TARGET_DIR="$TARGET_DIR" \
  cargo build --release --locked --target "$TARGET"
cp "$TARGET_DIR/$TARGET/release/azdaja" "$OUT/$ASSET"
chmod 755 "$OUT/$ASSET"
if [ "$TARGET" = aarch64-apple-darwin ]; then
  "$ROOT/release/v0.1.1/normalize-darwin.py" "$OUT/$ASSET"
fi
"$OUT/$ASSET" --version | grep -Fx "azdaja $VERSION (monty 0.0.21)"
"$OUT/$ASSET" doctor --caps | grep -F '"azdaja":"0.1.1"' >/dev/null
if [ "$TARGET" = aarch64-apple-darwin ]; then
  otool -l "$OUT/$ASSET" | grep -F 'uuid 111117A3-F60D-47EE-A365-95B52A953121' >/dev/null || {
    printf '%s\n' 'build-asset: normalized Darwin LC_UUID missing' >&2
    exit 1
  }
  /usr/bin/codesign -dvvv "$OUT/$ASSET" 2>&1 | grep -Fx 'Identifier=dev.kubet.azdaja' >/dev/null || {
    printf '%s\n' 'build-asset: normalized Darwin identifier missing' >&2
    exit 1
  }
fi
if command -v shasum >/dev/null 2>&1; then
  ACTUAL=$(shasum -a 256 "$OUT/$ASSET" | awk '{print $1}')
else
  ACTUAL=$(sha256sum "$OUT/$ASSET" | awk '{print $1}')
fi
[ "$ACTUAL" = "$EXPECTED" ] || { printf '%s\n' 'build-asset: predicted digest mismatch' >&2; exit 1; }
printf '%s  %s\n' "$ACTUAL" "$OUT/$ASSET"
wc -c "$OUT/$ASSET"
