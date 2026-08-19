<p align="center"><img src="azdaja-logo.png" alt="azdaja" width="240"></p>

# azdaja

**Virtual memory for language models: keep large UTF-8 inputs in a local evaluator and give models a bounded analysis surface.**

## What it is

Azdaja is a recursive language model (RLM) layer in the bare configuration: one persistent, sandboxed Monty/Python evaluator at the root, plain model calls below it. It spawns no agent environment per sub-call and hands no filesystem or tools to children. In the taxonomy of long-context systems it is a context virtualization sidecar for existing harnesses, not a harness itself: the document lives in the evaluator as a variable, and the full input is not automatically pasted into the root request.

1. Load the complete UTF-8 input once into the evaluator.
2. Use deterministic code for exact parsing, filtering, grouping, and reduction.
3. Delegate only selected semantic work through `llm` / `llm_batch`, then require strict coverage before `FINAL`.

Azdaja does not paste the file into the root request. Model-authored code can still select source material for a model call, so this is bounded context, not information-flow control.

## Fast and small

Measured, in this repository: three UTF-8 inputs of exactly **52,428,800 bytes** each (build log, repository dump, transcript) answered correctly in **one root turn, zero child calls, root prompt under 65,536 bytes**, inside a 90-second watchdog (`tests/product_50mb.rs`). This is an offline scripted gate for those three cases, not a claim about arbitrary-file accuracy, latency, memory use, total provider usage, or savings.

The [crossover figure](docs/token-context-crossover.svg) is deliberately illustrative: it assumes four bytes/token and a constant 64 KiB root envelope, so the crossover is algebraic, not measured. It is not a token or cost-savings claim. Reproduce with `python3 tools/render_token_crossover.py --check`.

## Current evidence

One current Azdaja candidate is shown as a sanitized public aggregate. Historical
candidates, failed campaigns, and incident detail are intentionally excluded. This is
single-arm diagnostic evidence—not an official leaderboard result, a paired
comparison, or a superiority claim.

### Fixed-199 validation slice

The Azdaja row is the current exact endgame value. It is provisional only because
the frozen plan permits one possible successor run; if that run becomes terminal,
replace this row, and otherwise treat the current row as final.

<!-- ENDGAME-FIXED199-SUBSTITUTION-POINT: If and only if the sole authorized successor fixed-199 run becomes terminal, replace the single Azdaja row immediately below. Otherwise remove this comment at launch freeze. -->
| Candidate | Execution / valid predictions | Completed-row Oolong mean | Fixed-199 Oolong Score | Root tokens | Latency |
|---|---:|---:|---:|---:|---:|
| **Azdaja — current terminal candidate** | 185/199 (92.96%) | 73.83615290965021% | **68.64164968987583%** | Not reported | Not reported |

All 199 scheduled rows reached terminal accounting; retained execution failures
contribute zero to the fixed denominator. Complete, comparable token and latency
aggregates are not available, so neither is estimated and no efficiency claim is
made. The frozen run is never rerun, resumed, or rescored.

### Published class ladder

For orientation, the RAH paper ([arXiv:2606.13643](https://arxiv.org/abs/2606.13643))
reports these Oolong-Synthetic results for its 199-sample, 13-bucket protocol with
a GPT-5 backbone:

| Paper label | System class | Paper-reported Oolong Score |
|---|---|---:|
| RLM | Model recursion without agent tools | **64.38%** |
| Codex, No Retriever | Coding agent | **71.75%** |
| RAH, GPT-5 | Recursive Agent Harness | **81.36%** |

These literature values are reference points, not controls rerun by us. Protocol
alignment does not make this a controlled head-to-head comparison or establish
superiority, equivalence, or general capability.

## Install

Requires Rust 1.95. On macOS Apple Silicon or Linux x86-64, install the immutable
v0.1.1 release with the versioned installer:

```bash
curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/v0.1.1/site/install | sh
azdaja install --harness jcode
```

For other systems, build the same reviewed tag from the public HTTPS source:

```bash
cargo install --git https://github.com/kubet/azdaja.git --tag v0.1.1 --locked
azdaja install --harness jcode
```

`azdaja install` validates evaluator capabilities and installs the managed skill
without calling a model. Other targets: `claude`, `codex`, `gemini`, `opencode`,
`all`.

Authentication is a separate, explicit check:

```bash
azdaja doctor
```

A passing `doctor` proves only that the configured harness route answered its fixed
canary.

## Use

```bash
azdaja solo "question about this input" -f ./large.txt \
  --model gpt-5.6-luna --sub-model gpt-5.6-luna
```

Explicit evaluator session:

```bash
sid=$(azdaja start)
azdaja load "$sid" ./large.txt ctx
printf '%s\n' 'FINAL(len(ctx))' | azdaja exec "$sid"
azdaja final "$sid"
azdaja kill "$sid"
```

Core commands: `start`, `load`, `exec`, `final`, `list`, `kill`, `solo`, `doctor`, `install`, `uninstall`.

## Boundaries

- The CLI reads only paths the user supplies; selected context can be sent to the configured provider.
- Native harnesses retain the user's host permissions. Strong containment requires a separate trusted inference broker.
- Monty 0.0.21 is experimental and snapshot-format-bound. Snapshots are unencrypted owner-only files; there is no evaluator memory ceiling.
- Use synthetic or sanitized issue reproductions only. Never post raw inputs, traces, configuration, host paths, or credentials.
- Benchmark diagnostics do not determine release readiness or demonstrate adoption.

## Validate

```bash
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features -- -D warnings
python3 tools/check_docs.py
```

## License

MIT.
