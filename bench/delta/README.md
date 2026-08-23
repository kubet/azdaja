# Codex/OpenCode Luna delta ladder

This benchmark starts with the cheapest task that can expose Azdaja's intended advantage. It does not begin with the 17,469-record row-651 task.

## Stage 1: cheap gate

OOLONG row 645 contains 2,177 records, but the question selects only May. Provider-free validation proves the selected workload is 227 records and 226 unique decision texts. Both native and candidate prompts receive the same filtering and deduplication contract. The candidate adds only the Azdaja treatment instruction.

The candidate must use:

- GPT-5.6 Luna at low reasoning for outer and inner calls
- the standard lane, not redundant A/B or adjudication
- one compact positional semantic batch
- at most 256 unique items and 64 KiB
- six workers
- exactly one transaction and at most one inner model attempt
- an isolated candidate runtime with `max_calls_per_cell = 1`
- no retries

Codex-native and OpenCode-native run in parallel. Then Codex-candidate and OpenCode-candidate run in parallel. Each run has a 300-second timeout.

## Gates

Quality is evaluated first. A candidate must return the exact public row-645 answer. Efficiency is compared only when native and candidate are both correct for a harness.

A positive diagnostic efficiency delta requires both:

1. candidate outer tokens are lower than native outer tokens
2. candidate outer-plus-inner total tokens are lower than native total tokens
3. candidate wall time is lower than native wall time

Candidate inner usage and total usage are always reported. Every successful inner attempt must expose exact input, output, reasoning, cache-read, and cache-write fields. Missing usage blocks the efficiency result rather than being treated as zero. A candidate also fails if it uses anything other than one successful inner attempt. One repetition is diagnostic only and cannot support a general superiority claim.

The hard row-651 task is blocked until both harnesses pass this gate. It must then use the same compact standard-lane algorithm and no-retry rule, with an independently frozen call ceiling before inference.

The initial r1 attempt was acceptance-invalid because its strict output parsers lagged the installed harness schemas and its isolated candidate config did not runtime-enforce the preregistered one-call ceiling. R2 was frozen before any benchmark rerun with explicit harness activation, schema-correct outer parsers, and `max_calls_per_cell = 1`. A two-call transport-only preflight then exposed that the managed command trace omitted reasoning and cache-write usage, so no benchmark outcome was evaluated. R3 was frozen before another provider call. A Codex-only transport preflight then failed before provider entry because its isolated `AZDAJA_HOME` was inside the launch directory, which the product correctly rejects for provider-sandbox custody. R4 was frozen before another provider call with state outside the launch directory. Separate minimal transport preflights then passed for both harnesses with one successful GPT-5.6 Luna inner attempt and complete five-field usage. R5 is the final provider-free custody amendment before paired inference. It requires owner-only `0700` per-arm work directories and pins Codex to `--sandbox workspace-write --cd <arm-workdir>`. It does not change the model, prompts, fixture, schedule, quality gates, efficiency gates, or one-call ceiling. The plan pins candidate commit `486c6dc1e84146bac8b6beebfda731e70515973b`, the versioned runner, and fail-closed five-field outer-plus-inner accounting.

## Provider-free validation

```bash
python3 bench/delta/validate.py
python3 -m unittest discover -s bench/delta -p 'test_*.py' -v
python3 bench/delta/run.py
```
