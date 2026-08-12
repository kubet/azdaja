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

`solo` additionally preloads `semantic_manifest(items, task, labels)`: one full-coverage semantic wave, internal boundary review, strict validation, and bounded transient recovery.

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
azdaja solo "question about this input" -f ./large.txt   --model gpt-5.4 --sub-model gpt-5.4
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

Private diagnostic on official OOLONG row 645, identical hidden context/question, GPT-5.4, reasoning `medium`, fresh serial sessions, subscription OAuth, and strict exact scoring:

| Arm | Output | Correct | Wall time |
|---|---:|:---:|---:|
| Prime Agent | `Answer: 132` | yes | 109.9s |
| Native jcode | `Answer: 133` | no | 64.6s |
| Azdaja one-wave v19 | `Answer: 131` | no | **43.1s** |

The new architecture is 2.55× faster than Prime on this diagnostic, but it is not yet an accuracy win. Azdaja remains private until repeated blind tasks show exactness plus stable latency and token advantages.

The relevant improvement is architectural: the earlier 277.5s multi-pass path was replaced by one compact root plan and one full-coverage semantic wave. A clean v19 trajectory spent 12.4s in root planning and 30.3s in semantic classification, with no provider error row.

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
default_model = "gpt-5.4"
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
