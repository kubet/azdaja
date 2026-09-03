# Azdaja receipts leaderboard

Versioned, hash-bound evidence for claims made by this repository. This page separates product acceptance, single-arm diagnostics, and efficiency follow-ups so a reader can see exactly what was measured and what was not.

> **Live three-scenario product suite:** Claude Fable synthesized three generic programs from bounded root prompts. Azdaja executed them locally against three complete deterministic inputs and returned **3/3 exact results**: a duplicate-sensitive build-log count, a repository blocker with its path, and the color attached to the final matching catalog record. The run used **three provider calls, three Monty executions, and zero recursive or semantic subcalls**. This is a synthetic live product-path suite with no baseline or repetitions, not a benchmark or superiority claim.

## Live Claude Fable product suite

At source commit `2514d26a245a5d1c9f6bb1f351391b69a616c3b1`, the opt-in harness invoked the authenticated local Claude CLI once per scenario as:

```text
claude -p <model-facing prompt> --model claude-fable-5 --output-format text --max-turns 1 --tools ""
```

| Scenario | Exact result | Complete input | Root prompt | Input / prompt | Provider time |
|---|---|---:|---:|---:|---:|
| Build-log aggregation | `Answer: 13` | 52,428,800 B | 12,739 B | 4,116x | 17.570 s |
| Repository blocker | `src/module_07777.rs\|AZD-7777` | 52,428,800 B | 12,460 B | 4,208x | 22.054 s |
| Final matching catalog record | `Color: cerulean` | 52,428,800 B | 12,770 B | 4,106x | 23.872 s |

Across the suite, the complete local inputs totaled `157,286,400` bytes while the three root prompts totaled `37,969` bytes. Every model-authored program is published in the receipt and contains neither its expected answer nor its answer-specific constant. Exact scanners found zero 100-byte source spans in all provider prompts, and no prompt contained a repository, input, or scratch host path. Runtime traces recorded one execution per scenario, zero recursive calls, zero semantic calls, one snapshot save, and success.

- [Human-readable three-scenario result](bench/results/live-fable-suite.md)
- [Source-bound receipt and all three model-authored programs](bench/results/live-fable-suite.json)
- [Opt-in reproduction and fail-closed verification](bench/live_fable_suite/README.md)
- [Public proof page](https://azdaja.dev/proof.html)

The live result covers one model, one route, three deterministic synthetic tasks, and one run per task. It does not establish general model quality, arbitrary-input support, comparative performance, or cost efficiency. The earlier [single-scenario receipt](bench/results/live-fable-repo-smoke.json) remains available as historical evidence.

## Current-source product acceptance

| Scenario | Exact answer | Input | Root prompt | Input / prompt |
|---|---|---:|---:|---:|
| Duplicate-sensitive build-log count | `Answer: 13` | 50 MiB | 12,737 B | 4,116x |
| Unique blocker in a repository dump | `src/module_07777.rs\|AZD-7777` | 50 MiB | 12,451 B | 4,211x |
| Decision after the final escalation | `ship-v0.1-after-doctor` | 50 MiB | 12,743 B | 4,114x |

All three cases exercised the release `azdaja solo` path. The scripted transport returned a program rather than an answer constant. The acceptance assertions require one root transport call, one Monty execution, zero recursive subcalls, no exact 100-byte source span or host input path in the model-facing prompt, a successful runtime trace, and no persistent session after cleanup.

- [Human-readable acceptance report](bench/results/product-50mb-current-source.md)
- [Source-bound machine-readable receipt](bench/results/product-50mb-current-source.json)
- [Captured build and test log](bench/results/product-50mb-current-source.txt)
- [Reproduction and fail-closed verification instructions](bench/product_50mb/README.md)
- [Acceptance test source](tests/product_50mb.rs)

The capsule does not demonstrate live-model program synthesis, semantic quality on natural data, arbitrary-input support, comparison superiority, official benchmark status, or operating-system sandbox guarantees.

## One-command first-party verification

The [source-bound manifest](proof/reproduction/manifest.json) joins the live receipt, provider-free receipt and raw log, fixture specifications, deterministic invariants, verifier sources, and public claim surfaces into one hash-checked inventory. Verify it without provider access or network calls:

```sh
./proof/reproduction/run.sh
```

The [stdlib verifier](proof/reproduction/verify.py) fails closed on source drift, missing or reordered artifacts, byte-count or SHA-256 changes, unsafe paths, schema changes, receipt-verifier failures, altered totals or answers, fixture mismatches, public timing drift, and weakened claim boundaries. Exact live fixture SHA-256 values are retained. The provider-free v2 receipt retains generator provenance and exact input sizes but not generated-input SHA-256 values.

This is narrow first-party reproducible evidence. It is not independent replication, a complete third-party verification capsule, or evidence of general quality, superiority, statistical significance, production readiness, sandboxing, or legal compliance. See the [bundle documentation](proof/reproduction/README.md) for optional provider-free and live replays.

## Accuracy ladder

| Source | System | Class | Score |
|---|---|---|---:|
| RAH paper | RLM | Model recursion without agent tools | **64.38%** |
| This repository | Azdaja | Bare RLM layer | **68.64%** |
| RAH paper | Codex, No Retriever | Coding agent | **71.75%** |
| RAH paper | RAH, GPT-5 | Recursive agent harness | **81.36%** |

Azdaja's figure is a **private, single-arm, validation-derived fixed-199 diagnostic** under the paper's protocol. It is not an official leaderboard result, a paired comparison, or a superiority claim. Of 199 scheduled rows, 185 produced valid predictions and 14 failures remained in the fixed denominator as zeros. The frozen score sum is `136.5968828828529`, or `68.64164968987583%`.

### Accuracy custody

- [Sanitized terminal receipt](bench/results/gpt-rah199-mortality-v3-terminal-public.json)
- [199-row public manifest with per-row and context SHA-256 hashes](bench/results/rah199-public-manifest.json)
- Dataset revision: `f0d59eaf0febf130664cfceb710436c8e3216b2b`
- Official output SHA-256: `5519d8091b76731d4e25bfec388da4af76965f897cce4f3853f999a9539f4cbd`
- Official receipt SHA-256: `8d280539dcaba65a3c4a251cbef93a588b6ac809c87f5ea3d131fa8b2da3f60d`
- Results SHA-256: `e2f2715dc5e8970ffa69be5f757d7860fa40bfc4a23e5bdcd7cc3dfa7768acc5`
- Schedule SHA-256: `fa06a53394b8bbc298f319bfe8b035065e6b2ec48002e4a1c9f2aa1fe6a150a1`

The historical score is frozen. It was not rerun, resumed, or rescored, and a successor fixed-199 campaign is not authorized.

## Historical same-answer efficiency diagnostic

Frozen r10 follow-up on a deterministic `1,306,163`-byte context with 306 records. Both native baselines and both Azdaja candidates returned the exact frozen answer, `42` ham messages.

| Harness | Native uncached tokens | Azdaja uncached tokens | Token reduction | Native wall time | Azdaja wall time | Time reduction |
|---|---:|---:|---:|---:|---:|---:|
| Codex | 32,862 | 10,938 | **66.7%** | 23.862 s | 10.784 s | **54.8%** |
| OpenCode | 70,397 | 8,453 | **88.0%** | 22.479 s | 8.151 s | **63.7%** |

Each candidate used exactly one successful GPT-5.6 Luna inner call with complete usage. Native rows were reused from the hash-bound frozen r8 result, so this was not a fresh concurrent paired run.

- [Method, failed predecessors, limits, and exact validation commands](bench/delta/README.md)
- [Frozen r10 result](bench/delta/results/r10-result.json)

## Provider-free reproduction

These commands do not perform model inference:

```bash
python3 bench/product_50mb/reproduce.py \
  --receipt bench/results/product-50mb-current-source.json \
  --summary bench/results/product-50mb-current-source.md \
  --log bench/results/product-50mb-current-source.txt
python3 bench/product_50mb/verify.py \
  bench/results/product-50mb-current-source.json \
  --binary target/release/azdaja \
  --log bench/results/product-50mb-current-source.txt \
  --require-binary --require-log

cargo test --all --locked -- --test-threads=1
cargo build --release --locked
AZDAJA_PRODUCT_BINARY=target/release/azdaja \
  cargo test --release --locked --test product_50mb \
  offline_scripted_harness_answers_three_real_world_50_mib_files_without_a_death \
  -- --ignored --exact --test-threads=1 --nocapture
```

The frozen delta verifier is intentionally source-bound to candidate commit `a642db83d54b5c80901aba1e1e183e7178481a0e`. Run these commands from that exact commit. The verifier must block when source, skill, config, fixture, prompt, runner, or runtime hashes differ.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 bench/delta/fixture.py
PYTHONDONTWRITEBYTECODE=1 python3 bench/delta/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s bench/delta -p 'test_*.py' -v
```

Current-main release verification remains:

```bash
release/verify-published-release.sh 0.1.14
```

The OOLONG runner performs subscription inference and therefore requires an explicit `--yes-run-inference` acknowledgement. See [the benchmark controller contract](bench/oolong/README.md). Do not infer authorization from this page.

## Holdout policy

The published 199-row manifest is validation-derived and permanently labeled as such. It will not be renamed into an unseen test set. Any successor campaign must declare and hash its public fixture manifest, candidate components, route, scoring procedure, and continuation gates before the first inference turn. A passing diagnostic does not itself authorize publication or a superiority claim.

## Update policy

Every major model rerun gets a new versioned receipt. Historical rows remain immutable. Corrections are additive and explicit, and headline text must link directly to the receipt that supports it.
