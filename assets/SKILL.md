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

Monty deliberately has no filesystem, process, environment, or network access. The only available modules are already imported as `os`, `re`, `json`, `math`, `collections`, and `datetime` (`os` host access is denied); `csv` and other imports are unavailable. Keep intermediate data in REPL variables. Use explicit list-building loops: no `yield` or generators. Do not use `%` string formatting; use concatenation or f-strings.

For exact semantic counts and aggregates:

1. Inspect only a tiny structural sample, then parse the exact observed record boundaries and fields and check source accounting. Do not build a generic multi-format parser, invent alternate schemas, or add explicit-label fallbacks. (`solo` supplies a bounded, automatically captured, untrusted `repr` sample before its first root call, so its root must solve rather than inspect again.) Each source occurrence is an aggregation unit unless the question explicitly asks for unique/distinct items. Never discard equal-content records or strip occurrence IDs. You may classify one representative of exact duplicates only while retaining every source ID or an integer multiplicity for the weighted reduction.
2. Separate deterministic predicates from semantic predicates and apply deterministic filters first, but only to the parsed field they govern; do not search unrelated text. A requested category need not be an explicit field or literal label: if the predicate depends on meaning, it must use `llm`/`llm_batch`, not keyword or explicit-label rules; never infer zero merely because the label is absent.
3. Give surviving occurrences or weighted groups stable IDs. Preserve all relevant evidence; never silently slice a record. Pack prompts by their actual rendered character length and expected response size, not a fixed number of items. Assert a conservative ceiling (for example, about 32,000 characters including instructions), putting an oversized item in its own prompt.
4. For an exact result, use two independently phrased classification passes that do not reveal one another's answers. Require strict JSON covering every supplied ID with an allowed label and a confidence value. Validate exact IDs, cardinality, schema, and values after each pass. Re-query only failures, low-confidence items, and label disagreements in small adjudication prompts; a syntactically valid first answer is not semantic verification.
5. Before calling, compute a hard logical child-call budget: primary chunks + independent verification chunks + a small adjudication reserve must fit the per-cell limit. Use `llm_batch` with its default two workers. Treat malformed output and `azdaja_error` batch items as unresolved, retry a targeted failed chunk at most once, and never repeat an already valid whole batch or spend one call per record.
6. Before reduction, assert that parsed = deterministically excluded + surviving occurrence weight, every survivor has a reconciled label, and no failed or ambiguous item remains. Sum occurrence weights, not the number of unique texts.

Prefer one root planning turn and one well-planned `exec` cell; use a later cell only for targeted repair. Assign large intermediates to variables because output is capped. End with `FINAL(...)` or `FINAL_VAR(...)` only after all invariants pass. A failed cell never commits its tentative final answer.
