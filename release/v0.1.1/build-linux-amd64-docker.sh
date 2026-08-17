#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$ROOT"
if [ "${AZDAJA_ALLOW_DIRTY_PREDICTION:-0}" != 1 ]; then
  test -z "$(git status --short)" || {
    printf '%s\n' 'docker build-asset: final rebuild requires a clean source commit' >&2
    exit 2
  }
fi
OUT=${AZDAJA_DIST_DIR:-$ROOT/dist-v0.1.1}
mkdir -p "$OUT"
OUT=$(CDPATH= cd -- "$OUT" && pwd)
IMAGE=${AZDAJA_BUILDER_IMAGE:-sha256:e359cb7c0e6eabccc0acf545471ae83cedd2325814f6b5a72180e9cb1d17e815}
docker image inspect "$IMAGE" >/dev/null
exec docker run --rm --platform linux/amd64 \
  -v "$ROOT:/source:ro" -v "$OUT:/output" "$IMAGE" bash -lc '
    set -euo pipefail
    test "$(uname -s)-$(uname -m)" = Linux-x86_64
    test "$(rustc --version)" = "rustc 1.95.0 (59807616e 2026-04-14)"
    rm -rf /tmp/azdaja-v0.1.1-target
    cd /source
    CARGO_INCREMENTAL=0 SOURCE_DATE_EPOCH=0 CARGO_TARGET_DIR=/tmp/azdaja-v0.1.1-target \
      cargo build --release --locked --target x86_64-unknown-linux-gnu
    cp /tmp/azdaja-v0.1.1-target/x86_64-unknown-linux-gnu/release/azdaja \
      /output/azdaja-v0.1.1-linux-x86_64
    chmod 755 /output/azdaja-v0.1.1-linux-x86_64
    test "$(/output/azdaja-v0.1.1-linux-x86_64 --version)" = \
      "azdaja 0.1.1 (monty 0.0.21)"
    actual=$(sha256sum /output/azdaja-v0.1.1-linux-x86_64 | cut -d " " -f 1)
    test "$actual" = b18775f0d3572b20804ff3c3af880ffc5fa3131017c566dc941c1dd743c00247
    sha256sum /output/azdaja-v0.1.1-linux-x86_64
    wc -c /output/azdaja-v0.1.1-linux-x86_64
  '
