<p align="center"><img src="azdaja-logo.png" alt="azdaja" width="240"></p>

# azdaja

**A fast recursive-language-model layer for long contexts.**

Azdaja keeps the full input inside a persistent, sandboxed Monty/Python evaluator. A root model writes compact analysis code; semantic work is delegated through `llm` and `llm_batch`; deterministic reduction happens locally.

> Private and unreleased. The CLI is functional and end-to-end tested. Benchmark results below are diagnostics, not a superiority claim.

## Why

Long-context agents repeatedly reread, copy, and reason over the same input. Azdaja separates the work:

1. `load` places the complete UTF-8 input in a persistent evaluator.
2. Python performs exact parsing, filtering, grouping, and reduction.
3. Model calls handle only semantic predicates.
4. Strict manifests enforce complete ID coverage before `FINAL` is accepted.

The model-facing surface is deliberately small:

```python
llm(prompt, model=None, ctx="")
llm_batch(prompts, model=None, workers=2)
FINAL(answer)
FINAL_VAR("variable_name")
```

`solo` additionally preloads `semantic_manifest(items, task, labels)`: two blind independent full manifests, strict validation, and one blind complete adjudication of every disagreement within a preflighted call envelope.

## Install

Requires Rust 1.95 and a supported harness login.

```bash
cargo build --release
./target/release/azdaja install --harness jcode
azdaja doctor
```

Other install targets: `claude`, `codex`, `gemini`, `opencode`, and `all`.

The jcode adapter uses its stable Harness API over an owner-only Unix socket and pins `openai-oauth:<model>`. It does not fall back to a metered API key.

## Use

### Direct product loop

```bash
azdaja solo "question about this input" -f ./large.txt   --model gpt-5.6-luna --sub-model gpt-5.6-luna
```

### Persistent evaluator

```bash
sid=$(azdaja start)
azdaja load "$sid" ./large.txt ctx

cat <<'PY' | azdaja exec "$sid"
rows = ctx.splitlines()
selected = [row for row in rows if "failure" in row.lower()]
judgments = llm_batch(["Classify:\n" + row for row in selected])
FINAL({"count": len(selected), "judgments": judgments})
PY

azdaja final "$sid"
azdaja kill "$sid"
```

Core commands:

```text
start  load  exec  final  list  kill  solo  doctor  install  uninstall
```

## Current benchmark

One immutable current Azdaja candidate is evaluated against the controls. Historical development versions are intentionally omitted from this headline. This is a private derived-RULER diagnostic, not an official leaderboard result or a superiority claim.

| Arm | Execution | Completed exact | End-to-end exact | Mean root tokens | Mean time / item | Total time |
|---|---:|---:|---:|---:|---:|---:|
| **Azdaja** | 52/90 (57.78%) | 38/52 (73.08%) | 38/90 (42.22%) | **2,747** | 31.0s | 46.5m |
| Native jcode | 90/90 (100%) | 84/90 (93.33%) | 84/90 (93.33%) | 16,318 | **10.5s** | **15.7m** |
| Prime Agent | 90/90 (100%) | 85/90 (94.44%) | 85/90 (94.44%) | 7,064 | 12.8s | 19.3m |

Azdaja used 83.2% less root context than native jcode and 61.1% less than Prime Agent. That efficiency did **not** translate into a better overall result: 38 Monty/runtime process exits reduced fixed-denominator accuracy to 42.22%, while both controls exceeded 93%. Among completed Azdaja executions, accuracy was 73.08%. The clear current engineering target is execution reliability, not further context reduction.

Root-token evidence covers 90/90 attempts for every arm and measures context entering each arm’s root, not total provider compute. Full provider-token totals are available for both controls (native 5.18M; Prime 4.59M), but Azdaja provider usage covers only its 52 successful executions, so no misleading all-attempt Azdaja provider-total comparison is shown. All 90 Azdaja root transcripts, including failures, passed the exact pre-gold leak gate: no loaded-context substring of 100 or more Unicode characters appeared at the root.

The candidate was built from private commit `48b8a16`; binary SHA-256 is `f53d43ecde4fd800789d0b7469fa6ad81bb2dd46e41a0c643f90dc8e77a2228d`. A LongBench-v2 run with the same bytes was stopped after 12/189 rows before scoring; no benchmark inference is currently active while reliability is being repaired. “Completed exact” excludes execution failures; “end-to-end exact” keeps the fixed 90-item denominator and counts failures as incorrect.

## Guarantees

- Failed cells cannot publish tentative `FINAL` or `FINAL_VAR` values.
- Semantic manifests reject missing, duplicate, unknown, malformed, or invalid-label records.
- Source occurrences and integer multiplicity are preserved.
- Provider/model routing fails closed.
- Session files, prompts, sockets, and retained benchmark artifacts are owner-only.
- OAuth inference uses explicit subscription routing.
- Batch successes survive sibling failures; retries never repeat valid items.
- Root and child session cleanup is bounded.

## Boundaries

Monty code has no ambient filesystem, environment, subprocess, or network access. The CLI itself can read paths explicitly supplied to `load`, and model calls can receive data selected by evaluator code. This is not information-flow control.

Native harnesses still run with the user’s host permissions. Benchmark staging and tool-event scans detect obvious violations but are not an OS sandbox. Strong containment requires a separate trusted inference broker.

Monty 0.0.21 is experimental and snapshot-format-bound. Snapshots are unencrypted owner-only files; there is no evaluator memory ceiling.

## Configuration

```toml
sub_llm_cmd = "jcode-api"
default_model = "gpt-5.6-luna"
jcode_provider = "openai"
jcode_reasoning = "medium"
output_cap = 8192
max_depth = 1
sub_timeout = 300
max_sessions = 4
cell_timeout = 30
idle_timeout = 1800
max_calls_per_cell = 64
clean_patterns = []
```

## Validate

```bash
cargo test --all -- --test-threads=1
cargo clippy --all-targets --all-features -- -D warnings
cargo build --release
python3 -m unittest discover -s bench/oolong -p 'test_*.py' -v
```

The suite covers lifecycle persistence, snapshot ownership, Unicode caps, transactional finalization, call budgets, batch ordering and partial recovery, Harness API framing, OAuth model pinning, streamed usage, bounded cleanup, manifest coverage, installer rollback, Monty compatibility, and blind benchmark controls.

GitHub Actions is currently disabled because the account cannot start hosted jobs; local validation is authoritative until billing is enabled.

## License

MIT.
