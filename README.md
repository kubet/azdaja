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

The launch kit is **68.64%** fixed-199 (**+4.26 points** against the
published bare-RLM reference), **92.96%** execution, and **~5.4K** mean root
tokens over 198 measured rows, plus the paired ARC diagnostic below. Each number
keeps its own evidence boundary; this is not an official leaderboard result or
superiority claim.

### Fixed-199 validation slice

The frozen endgame is terminal. Neither preregistered lever authorized a
successor fixed-199 run, so the permanent fixed-denominator score is
**68.64164968987583%**.

| Candidate | Execution / valid predictions | Completed-row Oolong mean | Fixed-199 Oolong Score | Root tokens | Latency |
|---|---:|---:|---:|---:|---:|
| **Azdaja — final terminal candidate** | 185/199 (92.96%) | 73.83615290965021% | **68.64164968987583%** | ~5.4K mean (198/199 measured) | Not reported |

All 199 rows reached terminal accounting; 14 retained execution failures
contribute zero. Provider-authoritative root usage exists for 198 rows: mean
total root usage was 5,403.36 tokens and the median was 4,723. The missing row is
not imputed, so this is not an exact 6K or complete fixed-199 token claim and no
efficiency claim is made. The frozen run is never rerun, resumed, or rescored.
See the [sanitized terminal receipt](bench/results/gpt-rah199-mortality-v3-terminal-public.json).

### Published class ladder

For orientation, the RAH paper ([arXiv:2606.13643](https://arxiv.org/abs/2606.13643))
reports these Oolong-Synthetic results for its 199-sample, 13-bucket protocol with
a GPT-5 backbone:

| Paper label | System class | Paper-reported Oolong Score |
|---|---|---:|
| RLM | Model recursion without agent tools | **64.38%** |
| Codex, No Retriever | Coding agent | **71.75%** |
| RAH, GPT-5 | Recursive Agent Harness | **81.36%** |

The Azdaja diagnostic is 4.26164968987583 percentage points above the 64.38 RLM
reference (**+4.3 points**, rounded), making it the highest bare-RLM number shown
in this ladder. The ladder is not an exhaustive literature review or evidence of
best-published status. Its values are not controls rerun by us; protocol alignment
does not establish superiority, equivalence, or general capability. The visible
next class step is Codex at 71.75%, not a result Azdaja has reached.

### Paired ARC diagnostic

> same harness, same model, ± Azdaja: -1.24% fewer wasted actions (1.24% more)

Five fresh-session pairs on the same Claude Sonnet lane produced 0.0 Ember-minus-baseline RHAE delta in every game. Under the predefined
unchanged-official-feedback rule, wasted actions totaled 646 for baseline and 654 for Ember. The receipt retains paired deltas and aggregate
waste only—not absolute arm scores or the revisited-state/repeated-control split.

An owner-directed, retrieval-only follow-up found that all ten closed scorecards returned HTTP 404 from the official detail endpoint,
despite its pinned open-or-closed contract; the HTML results route exposed no detail. Because close responses were discarded, absolute RHAE,
levels completed, and total actions cannot be recovered. The paired null cannot distinguish zero-level play from equal nonzero results, so the memory-efficiency
hypothesis remains open. Retained lifecycle metadata proves that vc33 created, reset, and closed two scorecards; its total actions and degeneracy remain
unresolved, so 0/0 wasted actions is not a zero-action claim. See the [sanitized ARC receipt](bench/results/arc3-ember-five-public-v9-result.json), the
[sanitized interrogation receipt](bench/results/arc3-scorecard-interrogation-public-v1.json), and the [full evidence boundary](docs/launch-saga.md#the-five-game-second-act).

The transport flip remains v0.2 roadmap material: its +0.00 scout failed before
inference and observed no root choice, so it is not genuine disuse and is
non-diagnostic for discoverability. See the [sanitized post-mortem](docs/transport-flip-postmortem.md).

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
