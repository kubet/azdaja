#!/bin/sh
set -eu

VERSION=0.1.3
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT=${1:-$ROOT/dist-v$VERSION}
DARWIN=azdaja-v$VERSION-darwin-arm64
LINUX=azdaja-v$VERSION-linux-x86_64

[ -f "$OUT/$DARWIN" ] && [ ! -L "$OUT/$DARWIN" ] || {
  printf 'assemble-standalone-assets: missing raw platform binary %s\n' "$OUT/$DARWIN" >&2
  exit 2
}
[ -f "$OUT/$LINUX" ] && [ ! -L "$OUT/$LINUX" ] || {
  printf 'assemble-standalone-assets: missing raw platform binary %s\n' "$OUT/$LINUX" >&2
  exit 2
}
sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    printf '%s\n' 'assemble-standalone-assets: shasum or sha256sum is required' >&2
    exit 2
  fi
}
[ "$(sha256_file "$ROOT/LICENSE")" = 45dd135e23e0e915b3dd61095d46eb45a8f59bbc53dadface6affbd1c76d7096 ] || {
  printf '%s\n' 'assemble-standalone-assets: root LICENSE identity mismatch' >&2
  exit 2
}
[ "$(sha256_file "$ROOT/THIRD-PARTY-NOTICES.md")" = ee908558c8d5f0d2080400558db351d8f24fb7ad3ca902c904822d97d7b5eac6 ] || {
  printf '%s\n' 'assemble-standalone-assets: reviewed notice identity mismatch' >&2
  exit 2
}
cp "$ROOT/LICENSE" "$OUT/LICENSE.tmp.$$"
cp "$ROOT/THIRD-PARTY-NOTICES.md" "$OUT/THIRD-PARTY-NOTICES.md.tmp.$$"
cmp -s "$ROOT/LICENSE" "$OUT/LICENSE.tmp.$$"
cmp -s "$ROOT/THIRD-PARTY-NOTICES.md" "$OUT/THIRD-PARTY-NOTICES.md.tmp.$$"
mv -f "$OUT/LICENSE.tmp.$$" "$OUT/LICENSE"
mv -f "$OUT/THIRD-PARTY-NOTICES.md.tmp.$$" "$OUT/THIRD-PARTY-NOTICES.md"
{
  for payload in "$DARWIN" "$LINUX" LICENSE THIRD-PARTY-NOTICES.md; do
    printf '%s  %s\n' "$(sha256_file "$OUT/$payload")" "$payload"
  done
} > "$OUT/SHA256SUMS.tmp.$$"
mv -f "$OUT/SHA256SUMS.tmp.$$" "$OUT/SHA256SUMS"
printf '%s\n' "assembled four checksummed payloads plus SHA256SUMS in $OUT"
