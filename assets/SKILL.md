---
name: azdaja
description: Use for questions over inputs too large to read safely into the root context: large logs, dumps, repositories, transcripts, or diffs.
---

# azdaja {{VERSION}}

Keep the input in azdaja. Do not `cat` or otherwise read the raw file into your own context after loading it. Run:

```bash
{{BIN}} start
{{BIN}} load <session-id> <path> <variable>
cat <<'PY' | {{BIN}} exec <session-id>
<python code>
PY
{{BIN}} final <session-id>
{{BIN}} kill <session-id>
```

`start` creates a persistent Monty/Python REPL. `load` places a UTF-8 file in a variable and returns trustworthy character/line metadata only. Each `exec` reads one Python cell on stdin; state survives across cells and capped cell output comes back for inspection. `final` retrieves the saved answer. `kill` deletes the session; `list` shows live session IDs. Monty is a Python subset: prefer explicit lists/loops over generators (`yield` is unsupported), and remember that regex backtracking is bounded.

Inside `exec`, use ordinary Python plus:

- `llm(prompt, model=None, ctx="")` — one model call; `ctx` is appended to the prompt.
- `llm_batch(prompts, model=None, workers=2)` — ordered parallel model calls. `llm` and batch items share the cumulative per-cell call budget (64 by default); submit another cell to continue with preserved state.
- `FINAL(answer)` — save the answer.
- `FINAL_VAR("name")` — save a variable by name.

Monty deliberately has no filesystem, process, environment, or network access. The only available modules are already imported as `os`, `re`, `json`, `math`, `collections`, and `datetime` (`os` host access is denied); `csv` and other imports are unavailable. `globals`, `locals`, `callable`, `eval`, `exec`, `next`, `yield`/generators, and string `%` formatting are unavailable. Never use `next(x for x in rows)`; build an ID map with explicit loops. Use f-strings, including for padded IDs. `llm` returns one string, `llm_batch` returns an ordered list of strings, and `FINAL(answer)` is always defined—call it directly without introspection. Keep the schema-targeted cell compact (prefer at most 140 nonblank lines).

For `solo`, a fixed `semantic_manifest(items, task, labels)` helper is additionally preloaded. Give it two-key dictionaries `{"id": stable_string, "evidence": complete_text}` and include the official question verbatim in `task`. It runs two blind full manifests in independent sessions, strictly validates both, and blindly adjudicates every disagreement from raw evidence. It preflights the worst-case call envelope before inference, expands exact duplicate representatives back to all occurrences, and returns a fully reconciled ID-to-label dictionary. The root calls it exactly once instead of generating provider plumbing. Interactive `exec` retains the lower-level primitives above.

For exact semantic counts and aggregates:

1. Inspect only a tiny structural sample, then parse the exact observed record boundaries and fields and check source accounting. Do not build a generic multi-format parser, invent alternate schemas, or add explicit-label fallbacks. (`solo` supplies a bounded, automatically captured, untrusted `repr` sample before its first root call, so its root must solve rather than inspect again.) Each source occurrence is an aggregation unit unless the question explicitly asks for unique/distinct items. Never discard equal-content records or strip occurrence IDs. You may classify one representative of exact duplicates only while retaining every source ID or an integer multiplicity for the weighted reduction.
2. Separate deterministic predicates from semantic predicates and apply deterministic filters first, but only to the parsed field they govern; do not search unrelated text. A requested category need not be an explicit field or literal label: if the predicate depends on meaning, it must use `llm`/`llm_batch`, not keyword or explicit-label rules; never infer zero merely because the label is absent.
3. Give surviving occurrences or weighted groups stable IDs. Preserve all relevant evidence; never silently slice a record. Pack prompts by their actual rendered character length and expected response size, not a fixed number of items. Assert a conservative ceiling (for example, about 32,000 characters including instructions), putting an oversized item in its own prompt.
4. Partition survivors exactly once across disjoint prompts. For every semantic representative, require two independent complete manifests containing every supplied ID once as `ID|actual_label`. Reverse presentation order for the second blind annotator. Strictly reject unknown, duplicate, missing, malformed, invalid-label, or structured `azdaja_error` results. Omission is unresolved, never a complement label.
5. Retry only malformed primary shards once and never repeat a valid shard. Blindly adjudicate every A/B disagreement from raw evidence without showing prior decisions; require complete adjudication coverage and do not contract-retry the judge. Preflight the conservative dual/retry/adjudication call envelope before the first child call. No confidence vote, lexical tie break, or silent complement label is allowed.
6. Before reduction, assert parsed = deterministically excluded + surviving occurrence weight, every survivor has exactly one reconciled label, and no failed/review item remains. Sum occurrence weights, not unique texts.

Prefer one root planning turn and one compact `exec` cell. Assign large intermediates to variables because output is capped. Call `FINAL(answer)` only after all invariants pass. A failed cell never commits its tentative answer; `solo` fails closed rather than asking the root to repair it.
