<p align="center"><img src="azdaja-logo.png" alt="azdaja" width="240"></p>

# azdaja

**Virtual memory for language models: ask about inputs beyond a context window while keeping the full UTF-8 input in a local evaluator and the model-facing analysis surface bounded.**

## Results first

| Measure | Result | Provenance |
|---|---:|---|
| RAH-protocol Oolong, fixed 199 rows | **68.64%** | One-shot consumed scorer, frozen diagnostic run; [terminal receipt](bench/results/gpt-rah199-mortality-v3-terminal-public.json) |
| Execution / valid predictions | 185/199 (92.96%) | All 199 rows reached terminal accounting; 14 failures scored zero |
| Mean root tokens per item | ~5.4K | 5,403.36 provider-authoritative mean across 198 measured rows; one row is not imputed |
| Captured root-prompt source-span leaks in the scripted 50 MiB gate | 0 | Three synthetic cases in `tests/product_50mb.rs`; not an information-flow guarantee |

For class context, the RAH paper ([arXiv:2606.13643](https://arxiv.org/abs/2606.13643)) reports Oolong-Synthetic results for its 199-sample, 13-bucket protocol with a GPT-5 backbone:

| Paper label | System class | Paper-reported Oolong Score |
|---|---|---:|
| RLM | Model recursion without agent tools | **64.38%** |
| Codex, No Retriever | Coding agent | **71.75%** |
| RAH, GPT-5 | Recursive Agent Harness | **81.36%** |

Azdaja's fixed-199 diagnostic is 4.26164968987583 percentage points above the 64.38% RLM reference (**+4.3 points**, rounded), making it the highest bare-RLM number shown in this non-exhaustive ladder. It is a single Azdaja arm, not an official leaderboard result, a rerun of the paper controls, or evidence of superiority, equivalence, best-published status, or general capability. The visible next class step is Codex at 71.75%, not a result Azdaja has reached.

## What it is

Azdaja is a recursive language model (RLM) layer in the bare configuration: one persistent, sandboxed Monty/Python evaluator at the root, plain model calls below it. It spawns no agent environment per sub-call and hands no filesystem or tools to children. It is a context-virtualization sidecar for existing harnesses, not a harness itself: the document lives in the evaluator as a variable, and the full input is not automatically pasted into the root request.

1. Load the complete UTF-8 input once into the evaluator.
2. Use deterministic code for exact parsing, filtering, grouping, and reduction.
3. Delegate only selected semantic work through `llm` / `llm_batch`, then require strict coverage before `FINAL`.

Model-authored code can still select source material for a model call, so this is bounded context, not information-flow control.

## Why it is different

- **Bounded-root evidence.** The frozen run measured ~5.4K mean root tokens on 198 rows, and the scripted 50 MiB cases stayed below a 64 KiB root prompt. These are measured boundaries for named runs, not an O(1), total-token, or cost claim.
- **Bare architecture.** Children receive plain model calls rather than full agent environments. Systems above 68.64% in the displayed paper ladder use heavier system classes; that comparison does not isolate the cause of score differences.
- **Harness adapters.** The managed skill supports Jcode, Claude, Codex, Gemini, and OpenCode. Installation is provider-free; only an explicit passing `doctor` validates the selected local route.
- **Receipts include losses.** The fixed denominator retains every failed row as zero, and public-safe receipts preserve terminal accounting and evidence boundaries. See [FAILS.md](FAILS.md) and [SCOREBOARD.md](SCOREBOARD.md).

## Fast and small

Measured in this repository: three synthetic UTF-8 inputs of exactly **52,428,800 bytes** each (build log, repository dump, transcript) answered correctly in **one root turn, zero child calls, root prompt under 65,536 bytes**, inside a 90-second watchdog (`tests/product_50mb.rs`). This offline scripted gate covers those three cases, not arbitrary-file accuracy, latency, memory use, total provider usage, or savings.

The [crossover figure](docs/token-context-crossover.svg) is illustrative: it assumes four bytes/token and a constant 64 KiB root envelope, so the crossover is algebraic, not measured. It is not a token or cost-savings claim. Reproduce it with `python3 tools/render_token_crossover.py --check`.

## Install

One command on Apple Silicon macOS or Linux x86-64. It detects installed harnesses without reading their configuration contents, downloads the v0.1.2 binary and `SHA256SUMS`, verifies the selected asset, atomically writes the binary, and reports any PATH action needed:

```bash
curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/main/site/install | sh
```

Manual alternative with Rust 1.95:

```bash
cargo install --git https://github.com/kubet/azdaja.git --tag v0.1.2 --locked
azdaja install --harness all
azdaja doctor
```

Uninstall the managed harness copies; if the one-command installer wrote a standalone binary, also remove the exact binary and adjacent `config.toml` path it reported:

```bash
azdaja uninstall --harness all
```

Supported harness targets are `jcode`, `claude`, `codex`, `gemini`, `opencode`, and `all`. Installation makes no provider call. A passing `doctor` proves only that the configured harness route answered its fixed canary.

## Use

```bash
azdaja solo "question about this input" -f ./large.txt
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

## ARC-AGI-3 appendix

A five-game paired pilot on the same Claude Sonnet lane, with and without Azdaja, produced a 0.0 Ember-minus-baseline RHAE delta in every game. Under the predefined unchanged-official-feedback rule, wasted actions totaled 646 for baseline and 654 for Ember: **-1.24% fewer wasted actions (1.24% more)**. The receipt retains paired deltas and aggregate waste only, not absolute arm scores or the revisited-state/repeated-control split.

A retrieval-only follow-up found that all ten closed scorecards returned HTTP 404 from the official detail endpoint despite its pinned open-or-closed contract; the HTML results route exposed no detail. Absolute results for that five-game pilot therefore cannot be recovered, and its paired null cannot distinguish zero-level play from equal nonzero results, so the memory-efficiency hypothesis remains open.

A later bounded `vc33` smoke captured absolutes locally: both baseline and Ember scored 0.0 shadow RHAE, completed zero levels, took 35 actions with per-level counts `[35, 0, 0, 0, 0, 0, 0]`, recorded zero wasted actions under the predefined split, emitted 36 journal records, and terminated at `ACTION_BUDGET`; the paired delta was 0.0. This establishes a true played zero-level null for that smoke only. The full five-game rerun remains on hold.

See the [sanitized pilot receipt](bench/results/arc3-ember-five-public-v9-result.json), [retrieval receipt](bench/results/arc3-scorecard-interrogation-public-v1.json), [sanitized `vc33` smoke receipt](bench/results/arc3-vc33-smoke-v2-public.json), and [full evidence boundary](docs/launch-saga.md#the-five-game-second-act).

## Boundaries

- The CLI reads only paths the user supplies; selected context can be sent to the configured provider.
- Native harnesses retain the user's host permissions. Strong containment requires a separate trusted inference broker.
- Monty 0.0.21 is experimental and snapshot-format-bound. Snapshots are unencrypted owner-only files; there is no evaluator memory ceiling.
- Benchmark diagnostics are single-arm or paired as stated, not release gates, leaderboard entries, or evidence of adoption.
- Use synthetic or sanitized issue reproductions only. Never post raw inputs, traces, configuration, host paths, OAuth material, tokens, or secrets.

## Validate

```bash
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features --locked -- -D warnings
python3 tools/check_docs.py
```

## License

MIT.
