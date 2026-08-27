# Azdaja receipts leaderboard

Versioned, hash-bound evidence for claims made by this repository. This page separates product acceptance, single-arm diagnostics, and efficiency follow-ups so a reader can see exactly what was measured and what was not.

> **Single-task efficiency headline:** at the same exact answer on one frozen synthetic 1.3 MiB classification task, Azdaja used **66.7% fewer uncached tokens on Codex** and **88.0% fewer on OpenCode**. This is a candidate-only diagnostic against hash-bound native rows, not a general benchmark or superiority claim.

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

## Same-answer efficiency diagnostic

Frozen r10 follow-up on a deterministic `1,306,163`-byte context with 306 records. Both native baselines and both Azdaja candidates returned the exact frozen answer, `42` ham messages.

| Harness | Native uncached tokens | Azdaja uncached tokens | Token reduction | Native wall time | Azdaja wall time | Time reduction |
|---|---:|---:|---:|---:|---:|---:|
| Codex | 32,862 | 10,938 | **66.7%** | 23.862 s | 10.784 s | **54.8%** |
| OpenCode | 70,397 | 8,453 | **88.0%** | 22.479 s | 8.151 s | **63.7%** |

Each candidate used exactly one successful GPT-5.6 Luna inner call with complete usage. Native rows were reused from the hash-bound frozen r8 result, so this was not a fresh concurrent paired run.

- [Method, failed predecessors, limits, and exact validation commands](bench/delta/README.md)
- [Frozen r10 result](bench/delta/results/r10-result.json)

## Product acceptance

| Contract | Observed result | Evidence |
|---|---|---|
| Three real-world-shaped 50 MiB inputs | `52,428,800` bytes each, one root turn each, zero child calls, root prompt below `65,536` bytes | [test](tests/product_50mb.rs), [receipt](bench/results/v0.1.2-product-acceptance-public.json), [demo](site/demo-50mb.gif) |
| Authoritative record coverage | JSONL and CSV preserve source order, duplicate occurrences, multiline CSV rows, raw hashes, and exact cardinality; omissions and tampering fail closed | public `solo` end-to-end tests |
| Typed final values | Supported JSON Schema subset validates before stdout; invalid shapes get one bounded repair only before semantic evidence spend | public `solo` end-to-end tests |
| Published v0.1.13 | tag `v0.1.13` at commit `50a4baaffbc8d4ee745d7324b8dbb052d247f9e0`; six release assets; all public channels verified | [GitHub Release](https://github.com/kubet/azdaja/releases/tag/v0.1.13) |

## Provider-free reproduction

These commands do not perform model inference:

```bash
cargo test --all --locked -- --test-threads=1
cargo build --release --locked
AZDAJA_PRODUCT_BINARY=target/release/azdaja \
  cargo test --release --locked --test product_50mb \
  offline_scripted_harness_answers_three_real_world_50_mib_files_without_a_death \
  -- --ignored --exact --test-threads=1
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
