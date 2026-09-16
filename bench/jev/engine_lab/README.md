# Optional typed semantic engine laboratory

This is an **experimental staged engine**, not a native `judge()` function or a production Jev integration. Real Azdaja/Monty programs emit typed request manifests, a host kernel evaluates them through injected synthetic backends, and validated results return to the same persistent evaluator session. Existing `llm` behavior and production Rust code are unchanged.

The goal is a general optional capability. Retrieval/reranking is one application. Dense semantic queries, selective follow-ups, extraction repair and revision-bound views are other candidates. See the [research and architecture](../../../docs/research/jev-engine-design-20260916.md) and [preregistered mechanism protocol](../../../docs/research/jev-engine-mechanism-protocol-20260916.md).

## Run without a key or network

From the repository root, with Python 3.9+ and a built Azdaja binary:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m bench.jev.engine_lab.run
```

The default binary is `target/debug/azdaja`. Build it with `cargo build` if needed, or set `AZDAJA_BINARY` to an explicit existing binary. The report records the exact binary hash. This is not runtime validation of another OS or another build.

To retain a **new** result without overwriting evidence:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m bench.jev.engine_lab.run \
  --receipt "$JCODE_SCRATCH_DIR/my-engine-mechanisms.json"
```

Set that scratch variable to an existing private scratch directory if your agent does not supply it. Tests use an isolated Azdaja home/config, `/usr/bin/false` as generative provider, cleared credential environment, network guards and a child-process allowlist. No model download or live request is needed. Do not pass an API key.

## What is actually implemented

- `kernel.py`: explicit activation, registered typed backend profiles, complete request/response validation using the existing adapter's validators, preflight call/question/byte budgets, instance-local exact raw-observation cache, separate occurrence rows, partial-failure evidence, and engine-owned immutable stage bindings.
- `monty.py`: staged `start/load/exec/final/kill` harness over the real binary. The evaluator verifies session, generation, source, manifest, request, profile and response-observation associations on re-entry. Caller reordering is harmless; changing or swapping bodies is rejected. Failed handoffs poison the host session rather than exposing an old successful stage.
- `scenarios.py`: explicitly **handwritten** programs and injected oracles. No automatic plan generation or real semantic inference occurs.
- `fixtures.json`: authored source records, independent literal pair truth, chosen-feature collision cases and a predeclared residual policy. Gold fields are not loaded into the evaluator as source evidence.
- `tests.py`: positive controls, matched ordinary-Python comparison, cache ablation, deliberate confident wrong labels, unknown/budget stops, and actual-evaluator handoff attacks.
- `run.py`: guarded test runner and version-bound JSON receipt. It has no `--live` mode.

The host-side composition is:

```python
# Abbreviated laboratory flow, not a new sandbox API.
with Session(binary, scratch, source_rows, engine.contracts()) as workspace:
    manifest_text = workspace.plan(handwritten_request_program)
    result_view = engine.judge_many(manifest_text)
    workspace.bind(engine, result_view)
    answer = workspace.value(handwritten_reduction_program)
```

`Engine` is disabled by default. A trusted host explicitly supplies its backend callbacks. The manifest cannot invent a command, endpoint, credential, model profile or larger budget. A future production adapter must additionally enforce deadlines, cancellation, authenticated transport, model policy and usage limits. This laboratory is not a security sandbox against malicious host Python code.

## Evidence and interpretation

The [retained result](results/mechanisms-20260916.json) records 20 passing tests, zero skips, implementation/dependency/protocol/binary hashes, and these observations:

| Control | Observed result |
|---|---|
| Factorable query | 72 occurrences, 16 unique records, 2,556 pairs fully accounted for, 336 positives. |
| Reuse ablation | 72 semantic questions without reuse, 16 with reuse. A second view adds no questions. |
| Strong Python baseline | Identical complete pair ledger with the same 16 unique semantic questions. No exclusive RLM execution advantage. |
| Symbolic result | 34,739-byte full ledger remains resident; a count summary is 29 bytes. Not a measured automatic-planner token saving. |
| Wrong high-confidence feature | One unique wrong feature creates 96 wrong pair decisions despite a structurally complete result. |
| Chosen-feature collision | Same chosen unary features cannot distinguish two different pair relations. Explicit direct-pair fallback succeeds. Not automatic collision discovery. |
| Residual stage | Three occurrence IDs, two unique follow-up questions, unknown pairs fall from nine to three. The result correctly stays incomplete. |

The initial 15-test suite did **not** catch mutable response-body substitution or stale-state reuse after process/load exceptions. Independent review executed those counterexamples. The implementation now retains response bindings in the trusted engine, verifies them inside Monty, and tests those exact failure modes. Test count alone was not treated as proof.

These results establish narrow execution mechanics with synthetic oracle data. They do **not** establish Jev quality, speed, billing, a native host capability, automatic RLM planning, retrieval quality, cross-process resumption, immutable model weights, completeness of task-wide evidence, or a product moat. A cache hit is one reused observation, not independent corroboration. The earlier live pilot remains stopped with zero validated judgments.
