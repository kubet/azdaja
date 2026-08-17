<p align="center"><img src="azdaja-logo.png" alt="azdaja" width="240"></p>

# azdaja

**Virtual memory for language models. Ask about inputs far past any context window; the model's context stays small, constant, and verified leak-free.**

## What it is

Azdaja is a recursive language model (RLM) layer in the bare configuration: one persistent, sandboxed Monty/Python evaluator at the root, plain model calls below it. It spawns no agent environment per sub-call and hands no filesystem or tools to children. In the taxonomy of long-context systems it is a context virtualization sidecar for existing harnesses, not a harness itself: the document lives in the evaluator as a variable, the root model sees only the question plus bounded observations, and the cost of asking does not grow with the size of what is asked about.

1. Load the complete UTF-8 input once into the evaluator.
2. Use deterministic code for exact parsing, filtering, grouping, and reduction.
3. Delegate only selected semantic work through `llm` / `llm_batch`, then require strict coverage before `FINAL`.

Azdaja does not paste the file into the root request. Model-authored code can still select source material for a model call, so this is bounded context, not information-flow control.

## Fast and small

Measured, in this repository:

- Three exact 50 MiB inputs (build log, repository dump, transcript) each answered correctly in **one root turn, zero child calls, root prompt under 64 KiB**, inside a 90-second watchdog (`tests/product_50mb.rs`).
- The root envelope is constant by construction: input grows by megabytes, the root request does not.

Observed, in internal paired diagnostics (single runs, private fixtures, not public benchmarks):

- Roughly **6K root tokens per item** where a full-context harness spent 63K on the same fixtures.
- Faster median wall time than both compared systems on long fixtures. On short inputs a single heavy root call makes azdaja slower, which is why the managed skill wakes only above a size threshold.

The [crossover figure](docs/token-context-crossover.svg) is deliberately illustrative: it assumes four bytes/token and a constant 64 KiB root envelope, so the crossover is algebraic, not measured. Reproduce with `python3 tools/render_token_crossover.py --check`.

## Current evidence

| Measure | Immutable result | Boundary |
|---|---:|---|
| RAH scheduled rows | 199 | Fixed denominator |
| Valid completions | 161/199 | Completed-row mean **75.96%** |
| Retained deaths | 38 | Each contributes zero |
| Fixed-199 score | **61.45%** | Validation-derived RAH slice |

For class context: the RAH paper (arXiv 2606.13643, same 199-row, 13-bucket protocol, GPT-5 backbone) reports **64.38%** for this same bare RLM configuration, 71.75% for a coding agent, and 81.36% for recursive harnesses. Shown for orientation only; our number is a single-arm, validation-derived slice with no paired control and no superiority claim. The run is frozen and never rerun or rescored. See [`SCOREBOARD.md`](SCOREBOARD.md), the [score provenance](bench/results/rah199-99f-provenance.json), and the [terminal receipt](bench/results/rah199-99f-terminal-receipt.json).

## Install

The repository is private. An authenticated owner with Rust 1.95 can install the reviewed tag from source:

```bash
cargo install --git ssh://git@github.com/kubet/azdaja.git \
  --tag v0.1.1 --locked
azdaja install --harness jcode
```

`azdaja install` validates evaluator capabilities and installs the managed skill without calling a model. Other targets: `claude`, `codex`, `gemini`, `opencode`, `all`. The immutable tag installer in [`site/install`](site/install) is bound to the exact v0.1.1 `Darwin-arm64` and `Linux-x86_64` assets and is for authenticated internal handling only while the repository is private.

Authentication is a separate, explicit check:

```bash
azdaja doctor
```

A passing `doctor` proves only that the configured harness route answered its fixed canary.

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
- Use synthetic or sanitized issue reproductions only. Never post raw inputs, traces, configuration, host paths, OAuth material, tokens, or secrets.
- Benchmark diagnostics do not determine release readiness or demonstrate adoption.

## Validate

```bash
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features -- -D warnings
python3 tools/check_docs.py
```

## License

MIT.
