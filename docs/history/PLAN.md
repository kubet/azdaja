# PLAN.md

## Thesis

azdaja is the faithful minimum RLM layer: a persistent evaluator, Python, and model calls from inside the evaluator. It adds no decomposition strategy to the model-visible interface and depends on no agent protocol.

## Design laws

1. `load` returns metadata, never input content. The skill tells the root not to read the raw path. This is advisory, not information-flow enforcement.
2. Evaluated vocabulary is Monty/Python plus `llm`, `llm_batch`, `FINAL`, and `FINAL_VAR`; no search, retrieval, or chunking primitives.
3. All displayed evaluator and final output is capped; the default is 8192 Unicode scalar values.
4. Depth defaults to one. Environment enforcement is reinforced in the sub-prompt because daemon-backed harnesses may not propagate process environment.
5. The skill documents primitives, not strategies.
6. The transport is an argv command template using stdin or a secure prompt file, never a shell.
7. Safety boundaries and benchmark losses are published literally.

## v0.1 status (2026-08-12)

- [x] Single 5.9 MB release binary embedding Monty 0.0.21; no CPython, Jupyter, daemon, or tmux.
- [x] Closed lifecycle surface: `start/load/exec/final/list/kill`.
- [x] `install/doctor/uninstall` and standalone `solo`.
- [x] Snapshot persistence between separate invocations, locks, atomic Unix replacement, idle reaping, session cap.
- [x] Bounded streaming print capture, cell/subprocess timeouts, depth guard, ordered host-side batch fan-out.
- [x] Verified jcode adapter with >ARG_MAX prompt-file transport.
- [x] Tests for lifecycle, callbacks, cap, sandbox boundary, paths, concurrency, installer, solo, idioms, and regex flavor.
- [x] Release snapshot benchmark at 1/10/100 MB, n=20.
- [x] One-run native jcode / azdaja / Prime Agent pilot with all losses published.

## Gate results

- Monty idiom and regex suite: **pass**, with documented subset gaps.
- 100 MB snapshot load median: **91.9 ms**; p95: **135.8 ms**. The p95 `<100 ms` gate failed.
- 100 MB restore/evaluate/save median: **105.5 ms**; p95: **193.9 ms**. Gate failed.
- Semantic pilot correctness: all arms 6/6.
- Semantic pilot wall time: native jcode 5.75 s; Prime Agent 19.70 s; azdaja solo 29.89 s. azdaja did not beat the baseline or Prime on this task.
- Prime parity / OOLONG / n>=20 answer-quality claims: **not established** and must not be marketed.

## Deferred deliberately

- Process-isolated Monty pool for hostile code.
- Statistically powered OOLONG and real coding suites.
- Cross-platform release matrix and nightly live adapter CI.
- Strong depth propagation through daemon-backed harnesses.
- Any strategy-specific tool, MCP transport, provider SDK, memory, or document pipeline.

A new feature enters v1 only by replacing an existing concept, not by widening the model-visible vocabulary.
