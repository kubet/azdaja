# Codex/OpenCode GPT-5.6 Luna delta gate

This is a one-shot diagnostic of Azdaja's intended metadata-projection advantage. It is not a general benchmark or a claim of broad superiority.

## Frozen r8 fixture

`fixture.py` deterministically generates a public 1,306,163-byte context with 306 records. Exactly 64 May records require semantic spam-versus-ham classification. Their long `User` fields are irrelevant synthetic metadata, while each `Instance` is complete decision evidence. The selected set has 64 unique instances, a 7,655-byte compact projection, and a frozen answer of 42 ham messages.

The messages use clear legitimate and unsolicited-scam categories. This reduces quality variance while retaining the workload property under test: the native harness must discover and perform the projection, while the Azdaja arm receives a pinned one-call execution shim that performs deterministic filtering and projection inside Azdaja before one semantic batch.

## Execution contract

Both harnesses use GPT-5.6 Luna at low reasoning.

- Codex-native and OpenCode-native run in parallel.
- Codex-candidate and OpenCode-candidate then run in parallel.
- Every arm has one 300-second timeout and no retry.
- Every arm runs in an owner-only `0700` work directory.
- The release Azdaja binary and resolved Codex/OpenCode executable paths, versions, and SHA-256 hashes are exact plan pins.
- Codex is pinned to `--sandbox workspace-write --cd <arm-workdir>`.
- Codex adds the isolated owner-private arm root as writable so nested provider state and temporary files remain usable without exposing any other campaign arm. Workspace network transport is enabled for the nested Luna call. Web search remains disabled.
- Candidate config is runtime-patched to `max_calls_per_cell = 1`.
- Candidate config is runtime-patched to a 180-second cell timeout inside the unchanged 300-second arm timeout.
- The candidate outer harness must run `./azdaja-evaluate` exactly once and must not read the context itself.
- The shim runs one literal `start`, `load`, `exec`, `final`, and `kill` lifecycle.
- The cell makes exactly one `llm_batch` call with one compact prompt, six workers, and the same harness-specific Luna model.

## Gates

Quality is evaluated first. Efficiency is compared only when native and candidate both return the exact frozen answer for a harness. A positive diagnostic delta requires all of the following on both Codex and OpenCode:

1. the native arm uses zero inner attempts
2. the candidate uses exactly one successful inner attempt and no failed inner attempt
3. candidate outer uncached tokens are lower than native outer uncached tokens
4. candidate outer-plus-inner uncached tokens are lower than native total uncached tokens
5. candidate wall time is lower than native wall time

The primary metric is:

```text
total_uncached_tokens = input - cache.read + cache.write + output + reasoning
```

The normalized `input` field is total prompt input including cache reads. Codex already reports that representation. OpenCode reports fresh input and cache reads separately, so r7 normalizes it as `tokens.input + tokens.cache.read`. Gross tokens are also reported. Every successful inner attempt must expose exact input, output, reasoning, cache-read, and cache-write fields. Missing usage blocks the result instead of being treated as zero.

## Audit history

- r1 was invalid because its output parsers lagged installed harness schemas and its candidate config did not enforce the one-call ceiling.
- r2 fixed those issues. A transport-only preflight then found missing reasoning and cache-write trace fields, so no benchmark outcome was evaluated.
- r3 added exact five-field accounting. Its Codex transport preflight failed before provider entry because `AZDAJA_HOME` was inside the sandbox work directory.
- r4 moved state outside the work directory. Separate minimal Codex and OpenCode preflights then passed with one successful Luna inner attempt and complete usage.
- r5 pinned owner-only work directories and explicit Codex sandbox/cwd arguments. Its single paired result is frozen at `results/r5-result.json`. The gate failed because passive skill activation produced zero candidate inner attempts, and OpenCode-native was not exact. No efficiency claim was made.
- r6 was a new diagnostic fixture and an outcome-independent activation repair. Its one live attempt stopped while resolving the parallel native group because OpenCode's fresh-input counter was incorrectly treated as total input. The empty result artifact and exception are recorded in `results/r6-failure.json`. The candidate group never started, and no efficiency claim was made.
- r7 kept the frozen r6 fixture and execution contract, but normalized OpenCode fresh input plus cache reads into the same terminal representation as Codex before applying the preregistered uncached-token formula. Its exact result is frozen at `results/r7-result.json`. Both native arms returned the exact answer. Both candidate arms entered exactly one inner attempt, but those attempts failed before producing usage or an answer. No efficiency claim was made.
- r8 reduces the semantic batch from 226 to 64 clear messages while retaining a context above 1 MiB, binds the full isolated arm root for nested Codex state, raises only the candidate cell timeout, and adds a provider-free end-to-end candidate lifecycle test for both structured harness transports. It was frozen and pushed before any r8 provider call.

## Provider-free validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 bench/delta/fixture.py
PYTHONDONTWRITEBYTECODE=1 python3 bench/delta/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s bench/delta -p 'test_*.py' -v
```

`run.py` is not provider-free. After the exact plan, runner, fixture, prompts, candidate source, and release binary are frozen and pushed, the one live campaign is:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 bench/delta/run.py
```
