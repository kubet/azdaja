<p align="center"><img src="azdaja-logo.png" alt="Azdaja logo" width="120"></p>

# Azdaja

Azdaja keeps complete source material in a local evaluator and gives language models a bounded working surface for code and semantic calls. It is a **recursive language model layer**, not a model or agent harness.

[Install](#install) · [Use](#use) · [Results](#results) · [Jev](#optional-jev) · [Live proof](https://azdaja.dev/proof.html) · [Releases](https://github.com/kubet/azdaja/releases)

- **Load once:** keep full inputs in a persistent Monty/Python evaluator, not every model prompt.
- **Compute locally:** use code for parsing, filtering, joins and exact reduction.
- **Recurse selectively:** send semantic work through `llm` / `llm_batch`, then return `FINAL`. Subcalls are model calls, not new agent environments.

## Install

macOS 11+ on Apple Silicon and Intel, or x86-64 Linux with glibc 2.35+:

```bash
curl -fsSL https://azdaja.dev/install | sh
```

Choose Jcode, Claude, Codex, Gemini or OpenCode when prompted. Installation verifies downloads and makes no model calls. The installer adds `az` as an alias when available.

From source with Rust 1.95:

```bash
cargo install --git https://github.com/kubet/azdaja.git --tag v0.1.18 --locked --features typesafe
```

Remove Azdaja-managed installations:

```bash
azdaja uninstall all
```

[Install options](docs/install.md) · [LICENSE](LICENSE) · [supported-target third-party notices](THIRD-PARTY-NOTICES.md)

## Use

```bash
azdaja solo "Summarize the unresolved issues" -f ./large.txt
azdaja solo "Find release blockers" --repo ./project
```

For explicit, persistent work:

```bash
sid=$(azdaja start)
azdaja load "$sid" ./large.txt ctx
printf '%s\n' 'FINAL(len(ctx))' | azdaja exec "$sid"
azdaja final "$sid"
azdaja kill "$sid"
```

Run `azdaja` for a provider-free local overview, or `azdaja map` for its interactive view. [Leave evidence for the next session](docs/agent-memory-handoff-walkthrough.md).

## Results

### RLM comparison

Historical 199-row Oolong diagnostic under the [RAH protocol](https://arxiv.org/abs/2606.13643). All 14 failed rows remain in the denominator as zeros.

| Source | System | Class | Score |
|---|---|---|---:|
| RAH paper | RLM | Model recursion without agent tools | **64.38%** |
| This repo | Azdaja | Bare RLM layer | **68.64%** |
| RAH paper | Codex, No Retriever | Coding agent | **71.75%** |
| RAH paper | RAH, GPT-5 | Recursive agent harness | **81.36%** |

Single-arm historical diagnostic, not a matched rerun of the paper's controls. [Receipt](bench/results/gpt-rah199-mortality-v3-terminal-public.json) · [Launch saga](docs/launch-saga.md) · [All measurements and limitations](BENCHMARKS.md).

### Context and cost

<p align="center"><img src="docs/token-context-crossover.svg" alt="Illustrative crossover between a whole-input prompt and a constant 64 KiB root envelope" width="720"></p>

Illustration, not a benchmark. Recorded RAH runs averaged **5,403 root tokens** across 198 measured rows ([accounting](bench/results/cost-evidence-public.json)).

On one frozen 1.3 MiB task, the same-model projection diagnostic kept the exact answer with **66.7% fewer uncached tokens / 54.8% less time on Codex**, and **88.0% / 63.7% on OpenCode**. These were candidate-only follow-ups, not concurrent or repeated benchmarks. [Method and receipt](bench/delta/README.md).

The [live Fable suite](bench/results/live-fable-suite.md) returned **3/3 exact results**, one provider call per synthetic scenario. Separate [provider-free acceptance](bench/product_50mb/README.md) tests exercise the real CLI with scripted model responses, not live-model quality.

## Optional Jev

[Jev / TypeSafe](https://typesafe.ai) adds optional typed semantic work alongside generative calls:

| Feature | What it does |
|---|---|
| `judge_many` | Returns Noul, Choice and Score judgments with raw distributions. Your harness chooses how to use uncertainty and alternatives. |
| `judge_stats` | Reports attempts, tokens and timing separately from generative calls. Missing usage stays unknown. |
| `jev batch` | Runs an explicit, budgeted work list with durable checkpoints. Resume reuses completed requests and refuses ambiguous automatic retries. |
| Source review | Exports JSONL or a read-only HTML queue with full source windows, hashes and byte offsets. No automatic approval. |

Set `TYPESAFE_API_KEY` through your host's secret manager. To save that key locally for later sessions:

```bash
printf '%s' "$TYPESAFE_API_KEY" | azdaja jev attach --stdin
azdaja jev status
```

A usable key enables `exec` and explicitly executed batches. No key or `[judge] enabled = false` means off. Automatic `solo` use stays off. No automatic compaction or tool suppression is claimed. [Typed API](docs/typed-judgments.md) · [Batch and review commands](docs/jev-batch.md).

## Boundaries and verification

Use Azdaja only after explicit activation in your harness. Selected source can reach the configured provider. Monty is experimental, and Azdaja is not an OS security boundary. [Security](SECURITY.md) · [CLI](docs/cli.md).

Verify recorded evidence offline with `./proof/reproduction/run.sh`. [Manifest](proof/reproduction/manifest.json) · [Offline verifier](proof/reproduction/verify.py). This makes no model calls and does not reproduce the original live runs.
