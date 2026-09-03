#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$ROOT"

exec python3 proof/reproduction/verify.py \
  --manifest proof/reproduction/manifest.json "$@"
