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

For class context, the RAH paper ([arXiv:2606.13643](https://arxiv.org/abs/2606.13643)) reports Oolong-Synthetic results for its 199-sample, 13-bucket protocol with a GPT-5 backbone. This single ordered table places those paper numbers and this repository's diagnostic on one numeric ladder:

| Source | Label | System class | Oolong score |
|---|---|---|---:|
| Paper | RLM | Model recursion without agent tools | **64.38%** |
| This repository | Azdaja — single-arm diagnostic; not paper/leaderboard | Bare RLM layer | **68.64%** |
| Paper | Codex, No Retriever | Coding agent | **71.75%** |
| Paper | RAH, GPT-5 | Recursive Agent Harness | **81.36%** |

Azdaja's fixed-199 diagnostic is 4.26164968987583 percentage points above the 64.38% RLM reference (**+4.3 points**, rounded), making it the highest bare-RLM number shown in this non-exhaustive ladder. That arithmetic is not a rerun of the paper controls or evidence of superiority, equivalence, best-published status, or general capability. Azdaja remains a single-arm diagnostic, not an official leaderboard result; the visible next class step is Codex at 71.75%, not a result Azdaja has reached.

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

Measured in this repository: three synthetic UTF-8 inputs of exactly **52,428,800 bytes** each (build log, repository dump, transcript) answered correctly in **one root turn, zero child calls, root prompt under 65,536 bytes**, inside a 90-second watchdog (`tests/product_50mb.rs`). This performance acceptance is release-only and ignored by the ordinary debug suite; functional debug coverage remains active. The offline scripted gate covers those three cases, not arbitrary-file accuracy, latency, memory use, total provider usage, or savings.

The [crossover figure](docs/token-context-crossover.svg) is illustrative: it assumes four bytes/token and a constant 64 KiB root envelope, so the crossover is algebraic, not measured. It is not a token or cost-savings claim. Reproduce it with `python3 tools/render_token_crossover.py --check`.

## Install

One command on Apple Silicon macOS or Linux x86-64. It detects installed harnesses without reading their configuration contents, verifies the v0.1.2 asset against `SHA256SUMS`, and atomically writes the `azdaja` binary. Before adding the optional short `az` alias, it scans every PATH entry: if Azure CLI or any other foreign `az` file or symlink exists, the install succeeds without an alias and reports `short alias skipped`. Standalone route configuration uses owned `azdaja-config.toml` plus `azdaja-config.toml.managed`; an unrelated adjacent `config.toml` is never overwritten:

```bash
curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/main/site/install | sh
```

Detected harness setup runs automatically and installs the managed Azdaja skill for large-input tasks and explicit questions about Azdaja/`az` availability or use. Use `az install --harness all` (or a named harness) to update managed copies. Install output is exactly three lines: detection, writes, and an honest next step. Run the reported `az doctor`/`azdaja doctor` command, then reload the selected harness's skill registry or start a fresh session. `JCODE_HOME` is authoritative when set, including for detection and lifecycle operations. An already-open Jcode session caches its registry: run `skill_manage reload_all`, choose `/skills` -> `Reload all`, or start a fresh Jcode session before expecting the skill to appear. The installer does not kill or restart sessions and makes no provider call. If installed, `az` and `azdaja` run the same executable. A bare invocation prints an indexed 16-row truecolor half-block banner above the five-line help only on an interactive color terminal; non-TTY output, `NO_COLOR`, and `TERM=dumb` emit only the same exact five-line text through either name.

Manual alternative with Rust 1.95:

```bash
cargo install --git https://github.com/kubet/azdaja.git --tag v0.1.2 --locked
azdaja install --harness all
azdaja doctor
```

The Cargo path keeps `azdaja` available and does not create `az`; the one-line installer creates the short alias only when no foreign `az` exists anywhere on PATH. Inspect on-disk skill custody without contacting a provider, or run the existing route canary explicitly:

```bash
az doctor --harness jcode  # provider-free; use all for every target
az doctor                  # existing evaluator + configured-provider route canary
```

The custody check verifies the managed directory, marker and hashes, executable, valid configuration, rendered skill awareness/version, and its absolute embedded binary path. `PASS ... installed on disk` does not mean an already-open harness has reloaded its registry.

Uninstall one harness, all managed harness skills, only the installer-owned standalone PATH copy, or every managed surface:

```bash
az uninstall --harness claude
az uninstall --harness all
az uninstall --standalone
az uninstall --all
```

Every uninstall preflights all selected targets before deleting anything. Harness configuration remains user-editable, but changed binaries/skills, symlinks, and unknown files cause a refusal. Standalone removal requires the exact adjacent `azdaja-config.toml.managed` installer marker; it removes only the currently executing `azdaja`, an exact relative `az -> azdaja` alias, the Azdaja config, and marker. Foreign aliases/configuration/files are left untouched or cause a pre-mutation refusal. Unix self-unlink is supported; locked-file platforms fail closed. Successful uninstall output is exactly three lines, distinguishes skill-only from standalone removal, and reminds you to reload/restart affected sessions. See [Harness lifecycle and custody](docs/harness-lifecycle.md).

Supported harness targets are `jcode`, `claude`, `codex`, `gemini`, `opencode`, and `all`. Installation makes no provider call. A passing route `doctor` proves only that the configured harness answered its fixed canary; `doctor --harness` makes the narrower on-disk custody claim described above. The provider-free [current-source integration acceptance receipt](bench/results/integration-acceptance-v0.1.2-local.json) binds exact hashes for the installer, Rust custody preflight, refusal tests, release-only 50 MiB gate, workflows, and current documentation; its selector coverage is not a native cross-platform or provider validation. It supersedes the old [short-alias delta receipt](bench/results/install-alias-delta-v0.1.2-public.json) only for current-source claims without changing those immutable historical bytes. The historical receipt's then-pending label is no longer current: adjacent `azdaja-config.toml` loading is implemented and covered. The [readiness supersession receipt](bench/results/v0.1.2-candidate-readiness-superseded-public.json) still marks the retained v0.1.2 binaries and their earlier matrix stale; new native assets and a fresh release matrix are required before release readiness. The historical [matrix](bench/results/install-matrix-v0.1.2-final-public.json) and [real-adapter receipt](bench/results/install-real-adapters-v0.1.2-final-public.json) remain evidence for their old bytes only, not the current source.

## Use

```bash
az solo "question about this input" -f ./large.txt
```

Explicit evaluator session (use `azdaja` instead when installed through Cargo):

```bash
sid=$(az start)
az load "$sid" ./large.txt ctx
printf '%s\n' 'FINAL(len(ctx))' | az exec "$sid"
az final "$sid"
az kill "$sid"
```

Core commands: `start`, `load`, `exec`, `final`, `list`, `kill`, `solo`, `doctor`, `install`, `uninstall`. Every command accepts `--help`; top-level `--help` lists the full signatures. Invalid arity or options return that command's same canonical usage line on stderr with status 2.

For external command adapters, interrupting an in-flight `exec` or `solo` provider turn stops the provider process group and waits for it before returning status 130. A bound `{prompt_file}` temporary is removed without following a replaced path. Interrupted `exec` cells do not replace the prior session snapshot, so the session remains usable. `solo` rejects blank questions, blank model overrides, and a blank configured default model before loading the input or entering a provider. `doctor` configuration failures remain provider-free and report the sanitized configuration path, terminal cause, and repair action.

## ARC-AGI-3 diagnostic

A one-pair-per-game v9 diagnostic retained a 0.0 Ember-minus-baseline **local shadow RHAE** difference in each of five games. Its unchanged-feedback counts were 646 for baseline and 654 for Ember (**+8; +1.24% relative to the baseline raw count**), but v9 retained no absolute arm scores, levels, action totals, or separate waste diagnostics. The count difference is therefore not an efficiency or improvement claim.

A retrieval-only follow-up recovered no missing absolutes. A separate fresh `vc33` smoke recorded 0.0 local shadow RHAE, zero completed levels, 35 actions, three zero diagnostic counters, 36 journal records, and `ACTION_BUDGET` for each arm; it does not reconstruct v9. See the [ARC benchmark card](bench/arc3/README.md#benchmark-card) for method, per-game values, evidence links, and the not-run full-five boundary.

## Boundaries

- This private evidence lineage and its Git history are not a public-safe source tree. Any public launch requires a clean allowlisted export under a new repository identity while this lineage remains private; moving files does not sanitize history.
- The CLI reads only paths the user supplies; selected context can be sent to the configured provider.
- Native harnesses retain the user's host permissions. Strong containment requires a separate trusted inference broker.
- Monty 0.0.21 is experimental and snapshot-format-bound. Snapshots are unencrypted owner-only files; there is no evaluator memory ceiling.
- Benchmark diagnostics are single-arm or paired as stated, not release gates, leaderboard entries, or evidence of adoption.
- Use synthetic or sanitized issue reproductions only. Never post raw inputs, traces, configuration, host paths, OAuth material, tokens, or secrets.

## Validate

```bash
cargo test --all --locked -- --test-threads=1
cargo build --release --locked
AZDAJA_PRODUCT_BINARY=target/release/azdaja cargo test --release --locked --test product_50mb offline_scripted_harness_answers_three_real_world_50_mib_files_without_a_death -- --ignored --exact --test-threads=1
cargo clippy --all-targets --all-features --locked -- -D warnings
python3 tools/check_docs.py
```

## License

MIT.
