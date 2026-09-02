# Live Claude Fable repository smoke

This opt-in harness asks Claude Fable to synthesize a generic local-evaluator program for one deterministic repository task. Azdaja keeps the complete fixture local, sends one bounded root prompt through the direct `claude` CLI, executes the returned program in Monty, and requires the exact final answer.

## Run

Live subscription inference is disabled unless explicitly acknowledged:

```sh
python3 bench/live_fable_repo/run.py \
  --yes-run-inference \
  --receipt bench/results/live-fable-repo-smoke.json \
  --summary bench/results/live-fable-repo-smoke.md
```

The tracked worktree must be clean. Existing outputs are not replaced unless `--force` is supplied. The transport is hard-capped at one Claude call using:

```text
claude -p <model-facing prompt> --model claude-fable-5 --output-format text --max-turns 1 --tools ""
```

The runner validates all of the following before writing evidence:

- the synthetic repository dump is exactly 50 MiB with one blocker occurrence
- Azdaja returns `src/module_07777.rs|AZD-7777` exactly
- the model response is an executable program containing neither `AZD-7777` nor the final answer constant
- exactly one Claude transport call succeeds
- the model-facing prompt is below 64 KiB and contains no input, scratch, or repository host path
- an optimized exact scanner finds no 100-byte source span in the model-facing prompt
- runtime trace accounting reports one Monty execution, zero recursive or semantic subcalls, one snapshot save, and success
- source, binary, prompt, response, fixture, and command-output hashes are recorded

## Verify

```sh
python3 bench/live_fable_repo/verify.py \
  bench/results/live-fable-repo-smoke.json \
  --binary target/release/azdaja
```

The verifier is strict and source-bound. It rejects schema changes, weakened limits, command substitution, source drift, answer constants, result changes, and hash or invariant mismatches.

## Claim boundary

This is one synthetic live smoke on one model and one provider route. It has no baseline, no repeated trials, and no token-usage record in text mode. It is not a benchmark and does not establish general model quality, arbitrary-input support, or comparative superiority.
