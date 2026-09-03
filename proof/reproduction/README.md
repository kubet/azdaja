# First-party proof bundle

This directory gives reviewers one offline command for checking Azdaja's current first-party evidence:

```sh
./proof/reproduction/run.sh
```

The command uses only Python 3.9+, Git, and files in this checkout. It performs no provider call, downloads nothing, and does not rewrite a receipt. A successful run prints one JSON object describing the verified artifact count, Git binding, live exact-result total, provider-call total, provider-free scenario total, and cleanup state.

## What it verifies

- every file named by `manifest.json` is a regular file with the recorded byte count and SHA-256 digest;
- the artifact set is unchanged from the manifest's source commit;
- the existing live Fable verifier accepts its source-bound receipt;
- the existing provider-free verifier accepts its receipt and captured raw log;
- the expected exact answers, input sizes, bounded prompt sizes, call counts, Monty execution counts, cleanup state, and live fixture SHA-256 values match the receipts;
- `README.md`, `BENCHMARKS.md`, and `site/proof.html` expose the receipt, manifest, runner, verifier, source commit, and recorded live timings;
- changed hashes, sizes, paths, schemas, totals, answers, fixture identities, or claim boundaries fail closed.

The verifier requires a Git checkout that contains the commits named by the two receipts and the bundle manifest. It does not require network access.

## Evidence map

- `manifest.json`: source-bound artifact inventory and hashes
- `fixtures/spec.json`: live fixture hashes plus the explicit provider-free v2 digest limitation
- `receipts/fable/index.json`: exact live receipt and summary hashes
- `receipts/provider-free/index.json`: exact provider-free receipt, summary, and log hashes
- `expected/invariants.json`: deterministic values checked across both proof paths
- `verify.py`: stdlib-only fail-closed verifier
- `test_verify.py`: artifact tamper, path escape, schema, and current-bundle tests

## Optional replays

Provider-free replay performs no model inference. A first Cargo build may need its declared Rust dependencies if they are not already cached:

```sh
python3 bench/product_50mb/reproduce.py \
  --receipt "$PWD/provider-free.json" \
  --summary "$PWD/provider-free.md" \
  --log "$PWD/provider-free.txt"
python3 bench/product_50mb/verify.py \
  "$PWD/provider-free.json" \
  --binary target/release/azdaja \
  --log "$PWD/provider-free.txt" \
  --require-binary --require-log
```

The live replay is opt-in, makes three Claude Fable calls, can vary in timing and provider behavior, and must never be treated as byte-identical reproduction:

```sh
python3 bench/live_fable_suite/run.py \
  --yes-run-inference \
  --receipt "$PWD/live-fable.json" \
  --summary "$PWD/live-fable.md"
```

## Claim boundary

This is **narrow first-party reproducible evidence**, not a complete verification capsule and not an independent replication. Deterministic hashes and invariants can be checked exactly. The live receipt is a timestamped observation, not a promise about future provider behavior. The provider-free v2 receipt records exact byte counts and generator provenance but does not retain generated-input SHA-256 values.

The bundle does not establish general model quality, arbitrary-input support, comparative superiority, statistical significance, production readiness, operating-system sandboxing, legal compliance, or completeness of third-party notice metadata.
