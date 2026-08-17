<p align="center"><img src="azdaja-logo.png" alt="azdaja" width="240"></p>

# azdaja

**A fast recursive-language-model layer that keeps long UTF-8 inputs in a local evaluator and gives models a bounded analysis surface.**

## Why

1. Load the complete input once into a persistent, sandboxed Monty/Python evaluator.
2. Use deterministic code for exact parsing, filtering, grouping, and reduction.
3. Delegate only selected semantic work through `llm` / `llm_batch`, then require strict coverage before `FINAL`.

Azdaja does not automatically paste the whole file into the root request. Model-authored code can still select source material for a model call, so this is bounded context—not information-flow control.

## Install

The repository is private. The old raw-GitHub tag installer must **not** be presented as an anonymous public curl path. An authenticated owner with Rust 1.95 can install the reviewed tag from source:

```bash
cargo install --git ssh://git@github.com/kubet/azdaja.git \
  --tag v0.1.1 --locked
azdaja install --harness jcode
```

`azdaja install` validates local evaluator capabilities and installs the managed skill without calling a model. Other supported targets are `claude`, `codex`, `gemini`, `opencode`, and `all`.

The immutable tag installer in [`site/install`](site/install) remains bound to the exact `Darwin-arm64` and `Linux-x86_64` v0.1.1 assets, but it is for authenticated/internal release handling while the repository is private. Do not publish or claim anonymous reachability.

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

For an explicit evaluator session:

```bash
sid=$(azdaja start)
azdaja load "$sid" ./large.txt ctx
printf '%s\n' 'FINAL(len(ctx))' | azdaja exec "$sid"
azdaja final "$sid"
azdaja kill "$sid"
```

Core commands: `start`, `load`, `exec`, `final`, `list`, `kill`, `solo`, `doctor`, `install`, and `uninstall`.

## Exact 50 MiB acceptance

`tests/product_50mb.rs` runs the real `solo` CLI on three synthetic UTF-8 inputs of exactly **52,428,800 bytes** each: a build log, repository dump, and operational transcript. Every case must return its exact answer before a 90-second watchdog, use one root turn and zero child calls, keep the root prompt below **65,536 bytes**, retain no session, and expose neither the supplied host path nor any exact 100-byte source span in the captured provider prompt.

This is an offline scripted product-path gate. It does not establish arbitrary-file accuracy, live-model planning quality, a memory ceiling, or total provider usage.

The [crossover figure](docs/token-context-crossover.svg) is deliberately illustrative: it assumes four UTF-8 bytes/token and a constant 64 KiB root envelope, so 64 KiB is an algebraic—not measured—crossover. Exact evidence exists only for the three 50 MiB cases; child, repair, output, cache, tokenizer, and pricing effects are excluded. It is not a token or cost-savings claim. Reproduce it with `python3 tools/render_token_crossover.py --check`.

## Current evidence

| Measure | Immutable result | Boundary |
|---|---:|---|
| RAH scheduled rows | 199 | Fixed denominator |
| Valid completions | 161/199 | Completed-row mean **75.957%** (exact aggregate 75.95701810685118%) |
| Retained deaths | 38 | Each contributes zero |
| Fixed-199 score | **61.452662890467536%** | Validation-derived RAH slice |

This single-arm result is not official full OOLONG, not a leaderboard result, and has no paired-control, superiority, or product-gate claim. The run is frozen and never rerun or rescored. See [`SCOREBOARD.md`](SCOREBOARD.md), the [score provenance](bench/results/rah199-99f-provenance.json), and the [public-safe terminal receipt](bench/results/rah199-99f-terminal-receipt.json) for history and custody details.

## Boundaries

- The CLI can read paths explicitly supplied by the user; selected context can be sent to the configured model provider.
- Native harnesses retain the user's host permissions. Strong containment requires a separate trusted inference broker.
- Monty 0.0.21 is experimental and snapshot-format-bound. Snapshots are unencrypted owner-only files; there is no evaluator memory ceiling.
- Use synthetic or sanitized issue reproductions only—never post raw inputs, traces, configuration, host paths, OAuth material, tokens, or secrets.
- Benchmark diagnostics do not determine release readiness or demonstrate adoption.

## Validate

```bash
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features -- -D warnings
python3 tools/check_docs.py
```

## License

MIT.
