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

## Benchmark status

These are private, frozen diagnostics—not official leaderboard results or a superiority claim. “Completed accuracy” uses only execution-success rows; “fixed-denominator exact” counts every scheduled row and treats execution failures as incorrect.

### Latest finalized cohorts

| Suite / cohort | Arm | Execution success | Completed accuracy | Fixed-denominator exact | Mean root tokens |
|---|---|---:|---:|---:|---:|
| Derived RULER v32b, 90 fixtures | Azdaja | 52/90 (57.78%) | 38/52 (73.08%) | 38/90 (42.22%) | 2,746.98 |
| Derived RULER v32b, 90 fixtures | Native jcode | 90/90 (100%) | 84/90 (93.33%) | 84/90 (93.33%) | 16,318.49 |
| Derived RULER v32b, 90 fixtures | Prime Agent | 90/90 (100%) | 85/90 (94.44%) | 85/90 (94.44%) | 7,064.26 |
| OOLONG diagnostic v29, 26 fixtures | Azdaja | 25/26 (96.15%) | 24/25 (96.00%) | 24/26 (92.31%) | — |
| OOLONG diagnostic v29, 26 fixtures | Native jcode | 25/26 (96.15%) | 22/25 (88.00%) | 22/26 (84.62%) | — |
| OOLONG diagnostic v29, 26 fixtures | Prime Agent | 25/26 (96.15%) | 20/25 (80.00%) | 20/26 (76.92%) | — |

RULER v32b passed its frozen candidate regression floor: Azdaja improved from the historical v3 fixed-denominator result of 28/90 to 38/90, despite execution success falling from 60/90 to 52/90. All 90 Azdaja root transcripts—including failed attempts—passed the exact pre-gold scan with no common loaded-context substring of 100 or more Unicode characters. Its 38 execution failures were all normalized as `other_execution` from raw `process_exit`; controls had none. Root-token evidence covered 90/90 rows for every arm. Azdaja’s recorded mean root context was 83.2% lower than native jcode and 61.1% lower than Prime Agent, but its end-to-end accuracy was also much lower; this is an accuracy/economy trade-off, not a win over the controls.

Derived RULER is a project diagnostic, not an official RULER leaderboard. An earlier complete v32a cohort was preserved unscored after an OrbStack-driven disk-full incident caused one treatment row to lack mandatory transcript authority; v32b is a complete fresh cohort, not a selected retry. LongBench-v2 attempts v1–v5 were likewise preserved as failed, non-resumable, unscored cohorts.

### Active same-candidate campaign

Candidate v32 was built from private commit `48b8a16` with binary SHA-256 `f53d43ecde4fd800789d0b7469fa6ad81bb2dd46e41a0c643f90dc8e77a2228d`. RULER v32b passed; fresh LongBench-v2 (189 jobs) is next, followed only on a pass by OOLONG (78 jobs), using exactly the same candidate. Each suite is scored only after exact schedule closure and artifact validation.

Every finalized report includes execution success, completed accuracy, fixed-denominator end-to-end accuracy, normalized failure taxonomy, root-token economy, and missingness. For Azdaja, any exact substring of at least 100 Unicode characters shared by the loaded long context and retained root transcript is a hard failure. Missing root-transcript evidence also blocks scoring.

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
