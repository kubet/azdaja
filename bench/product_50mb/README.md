# Product 50 MiB current-source acceptance capsule

This capsule runs entirely offline. It builds the release binary and exercises the real `azdaja solo` CLI path over three deterministic inputs that are each exactly 50 MiB:

- a build log requiring duplicate-sensitive error counting
- a repository dump requiring a unique path and release-ticket extraction
- a transcript requiring the decision after the final matching escalation

The scripted transport returns a short Python program, not an answer constant. Azdaja must execute that program against the complete local input and finalize the exact expected answer.

The reproducer and verifier support Python 3.9 or newer.

## Reproduce

From a tracked-clean checkout at the repository root:

```sh
python3 bench/product_50mb/reproduce.py \
  --receipt bench/results/product-50mb-current-source.json \
  --summary bench/results/product-50mb-current-source.md \
  --log bench/results/product-50mb-current-source.txt
```

The script refuses to overwrite output files unless `--force` is supplied. It records exact command arrays, exit codes, output hashes, source commit and hashes, binary hash, environment, elapsed times, scenario results, and explicit claim boundaries.

## Verify

Verify the receipt against the current bound source files:

```sh
python3 bench/product_50mb/verify.py \
  bench/results/product-50mb-current-source.json
```

Also verify the locally built binary and captured command log:

```sh
python3 bench/product_50mb/verify.py \
  bench/results/product-50mb-current-source.json \
  --binary target/release/azdaja \
  --log bench/results/product-50mb-current-source.txt \
  --require-binary \
  --require-log
```

Verification fails on schema changes, command substitution, source drift, hash or size mismatch, scenario invariant changes, answer changes, weakened claim boundaries, path traversal, or missing required local artifacts.

## Claim boundary

This is a first-party product-path acceptance capsule. It demonstrates bounded model-facing prompts, exact scripted answers after one Monty execution, zero recursive subcalls, 100-byte source-span exclusion, successful traces, and cleanup on three deterministic 50 MiB inputs.

It does not demonstrate live-model program synthesis, semantic quality on natural data, arbitrary-input support, comparison superiority, official benchmark status, or operating-system sandbox guarantees.
