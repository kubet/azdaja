# Live Claude Fable three-scenario product suite

This opt-in suite expands the one-task live smoke to three deterministic product-path cases:

- duplicate-sensitive build-log counting
- unique blocker extraction from a repository dump
- final-match color extraction from a synthetic catalog

Each input is exactly 50 MiB. Each scenario gets its own direct Claude Fable call, capped at one call, and must return the exact answer after one local Monty execution with zero recursive or semantic subcalls.

The runner and verifier support Python 3.9 or newer.

## Run

```sh
python3 bench/live_fable_suite/run.py \
  --yes-run-inference \
  --receipt bench/results/live-fable-suite.json \
  --summary bench/results/live-fable-suite.md
```

The runner requires a tracked-clean tree and refuses existing outputs unless `--force` is supplied. It builds the locked release binary once, compiles one exact 100-byte overlap scanner, then runs the three cases serially. No normal test invokes Claude.

## Verify

```sh
python3 bench/live_fable_suite/verify.py \
  bench/results/live-fable-suite.json \
  --binary target/release/azdaja
```

The source-bound verifier rejects source drift, schema changes, command substitution, weakened limits, non-exact answers, model responses containing answer constants, path or overlap check changes, runtime changes, total mismatches, and binary tampering.

## Claim boundary

This is three synthetic live smokes on one model and one provider route. It has no baseline, no repeated trials, and no subscription token-usage record in text mode. It is not a benchmark and does not establish general model quality, arbitrary-input support, comparative performance, or cost efficiency.
