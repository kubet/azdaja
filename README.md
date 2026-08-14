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
`solo` treats a blank string passed to `FINAL` as an incomplete terminal answer and spends only its remaining bounded same-session correction budget; tasks whose intended answer is blank are therefore unsupported by `solo`.

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

One immutable current Azdaja candidate is shown against both controls. Historical
candidate versions are intentionally omitted from these headline tables. The
candidate is private commit `6588c06`, binary SHA-256
`6be5b9ff567eca6d1a5c2315dfb0c12fb5bd847b58daef0b3b8191151e45b509`.
These are single-run private diagnostics, not official leaderboard results or a
superiority claim.

### Derived RULER, 90 fixtures

| Arm | Execution | Completed strict exact | Fixed-90 strict exact | Mean root tokens | Median time / item |
|---|---:|---:|---:|---:|---:|
| **Azdaja** | **90/90 (100%)** | 85/90 (94.44%) | 85/90 (94.44%) | **2,835** | 22.5s |
| Native jcode | **90/90 (100%)** | **86/90 (95.56%)** | **86/90 (95.56%)** | 16,373 | **8.1s** |
| Prime Agent | 87/90 (96.67%) | 81/87 (93.10%) | 81/90 (90.00%) | 6,925 | 10.9s |

Azdaja cleared its 90/90 reliability gate and the separate candidate-only
90-item run completed at global width 4 in 562.3 seconds. The official
three-arm run completed 270 rows in 1,101.5 seconds. Azdaja's strict point
estimate was one item below native; the paired native-minus-Azdaja difference
was +1.11 percentage points with a 95% bootstrap interval of [-5.56, +7.78].
This supports neither superiority nor equivalence. Azdaja remained slower:
its median attempt was 2.77x native, so the <=1.5x speed gate did not pass.

### Derived LongBench-v2 hard/long subset, 63 fixtures

The pinned official LongBench-v2 answer extractor is the primary metric here.
Every scheduled failure remains a fixed-denominator zero.

| Arm | Execution | Completed official accuracy | Fixed-63 official accuracy | Mean root tokens | Median time / item |
|---|---:|---:|---:|---:|---:|
| **Azdaja** | 48/63 (76.19%) | 7/48 (14.58%) | 7/63 (11.11%) | **6,156** | 51.4s |
| Native jcode | **63/63 (100%)** | **35/63 (55.56%)** | **35/63 (55.56%)** | 63,223 | **19.8s** |
| Prime Agent | 56/63 (88.89%) | 12/56 (21.43%) | 12/63 (19.05%) | 9,827 | 39.4s |

Azdaja failed the preregistered 16/63 fixed-denominator gate, so the same-candidate
OOLONG run and the 199-item RAH protocol are blocked. Its 15 execution failures
were 14 deterministic Monty/program, assertion, or semantic-envelope failures and
one inner 30-second cell timeout; the frozen report conservatively normalizes all
15 raw `process_exit` rows as `other_execution`. Prime's seven `tool_policy` rows
are also fixed zeros. Among completed Azdaja rows, 20 outputs were not recognized
by the official extractor, 21 were wrong, and seven were correct; the stricter
full-string diagnostic was 0/63 because even the seven accepted canonical answers
retained a trailing newline.

Root-token authorities are explicit per arm and are not identical provider-signed
receipts. The lower Azdaja root input did not offset its much lower LongBench
accuracy or 2.59x native median latency. Across both suites, all mandatory Azdaja
root transcripts were retained and independently scanned with zero exact loaded-
context overlaps of 100 or more Unicode characters. The diagnostics use
owner-only local evidence and post-hoc policy checks, not authenticated history or
OS-level containment. LongBench is a derived public-answer-joinable subset, and
historical development-family gold exposure prevents a blind-validation claim.

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
