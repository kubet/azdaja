---
name: azdaja
description: Use for questions over inputs too large to read safely into the root context (large logs, dumps, repositories, transcripts, or diffs), and when the user explicitly asks whether Azdaja or the az virtual-memory tool is installed or available, or how to use it.
---

# Azdaja {{VERSION}}

## Managed-skill awareness

When this managed skill is loaded and the user asks whether Azdaja is installed, available, or usable, answer **yes**. Explain that Azdaja is the local `az` virtual-memory tool, suggest `az doctor`, and give a user-facing example such as `az solo "summarize this file" -f ./large.txt`. The `azdaja` command is compatible. Never claim ignorance of Azdaja or say that it is unavailable in this situation.

For tool execution, always use the exact embedded binary path in the commands below. Do not replace that path with bare `az`: another program, such as Azure CLI, may own that name. Prefer `az` only in safe user-facing guidance.

Keep the input in Azdaja. Do not `cat` or otherwise read the raw file into your own context after loading it.

Choose exactly one execution lane for a task. In **Claude Code and OpenCode**, always use the explicit lifecycle transaction: do not invoke `solo`. Those hosts already provide the planning model, so `solo` would add a slow nested root-program generation and repair loop. If a task describes a solo-only helper, preserve its semantic contract with a complete-record scan plus the explicit `llm_batch` workflow below; do not call the unavailable helper from `exec`. In other hosts, use one `solo` invocation only when the task truly requires its exact-line or fused semantic-projection helpers. Never retry `solo`, never invoke it more than once for the same task, and never combine `solo` with `start`/`load`/`exec` fallback. If that one `solo` call fails or times out, stop and report the failure instead of starting another Azdaja or native full-source attempt.

For a deterministic analysis that fits one `exec` cell, send this entire transaction as exactly one Bash tool call. Replace `<input-path>` and the cell, but keep the `EXIT` trap so `kill` runs after success or failure:

```bash
set -euo pipefail
sid=
cleanup() {
  if [[ -n "$sid" ]]; then
    {{BIN}} kill "$sid" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT
sid="$({{BIN}} start)"
{{BIN}} load "$sid" '<input-path>' source >/dev/null
cat <<'PY' | {{BIN}} exec "$sid" >/dev/null
<one deterministic Python cell ending in FINAL(...)>
PY
{{BIN}} final "$sid"
```

The transaction suppresses successful `load`/`exec` output, so its stdout is exactly the `final` JSON value. In Claude Code or OpenCode, return that exact value as the sole assistant response. Do not omit it, summarize it, wrap it in markdown, or replace it with a completion notice.

### Claude Code and OpenCode semantic fast path

For semantic classification or extraction in Claude Code or OpenCode, author the deterministic Monty/Python cell yourself and run it through the one-Bash lifecycle transaction above. Go directly to one compact transaction without a planning preamble, temporary scripts, exploratory tools, comments, or repeated validation code; target at most 85 nonblank cell lines. This removes every nested root-generation and repair turn. Ordinary `exec` does **not** expose `exact_line_ledger`, `semantic_manifest`, `semantic_manifest_records`, `source_ontology`, or `lexical_relevance`; do not call those solo-only names or claim their host-attested projection provenance.

In the cell:

1. Scan the complete loaded source by declared record boundaries. Reject ambiguous boundaries. Assign stable occurrence IDs in source order, preserve duplicates, and apply every deterministic selector to complete immutable records before semantic calls.
2. Keep complete selected records as evidence unless the official grammar explicitly guarantees that one exact final field alone determines the label. Only then may the cell require one nonempty final marker and project its nonempty suffix byte-for-byte. Deduplicate only byte-identical evidence while retaining the complete ordered occurrence expansion.
3. Build balanced contiguous shards of at most 80 unique items and 80 KiB per serialized prompt. Put the official task, exact labels, strict positional output contract, and stable IDs in every prompt. Prefer the fewest balanced shards that satisfy both bounds so `2 * shard_count <= 8` uses one eight-worker wave when the source permits it.
4. Create blind A and B prompts for every shard, reversing item and label presentation in B, and submit the ordered primary prompts in one `llm_batch(..., workers=8)`. This call is mandatory: every semantic label must come from a parsed `llm_batch` result. Never replace it with keyword, regex, substring, label-name, or hand-written classification rules. Strictly validate every response, exact ID coverage, and label domain.
5. Blind-adjudicate every A/B disagreement from its original evidence in one bounded `llm_batch`. Treat `azdaja_error`, malformed output, omission, extra output, or unresolved disagreement as failure—never as a complement label. Preflight `3 * shard_count <= 150` before inference.
6. Expand labels back to every occurrence. Validate coverage, multiplicity, all requested reductions, and output schema. Use `sha256(text)` for native UTF-8 SHA-256 when needed, then call `FINAL(answer_dict)` exactly once with the actual dictionary/object—never `json.dumps(...)` or another JSON string—so `final` emits an extractable JSON object.

If preflight exceeds the cell budget, use multiple heredoc-fed `exec` cells in the same Bash transaction and preserve one session; do not start another session. Do not write the question or source to temporary files, inspect the raw source with host `Read`/`Grep`/`cat`, or make a native full-source fallback attempt. This lane has exact candidate and semantic-call attribution, but its ledger/projection assertions are program-validated rather than the solo lane's host-attested provenance.

For a genuinely interactive multi-cell workflow, start once, retain the session ID, and use later Bash calls for `load` and heredoc-fed `exec` cells as needed. Call `final` only after a cell saves an answer, always call `kill` when done, and keep using the exact embedded binary path for every command.

`start` creates a persistent Monty/Python REPL. `load` places a UTF-8 file in a variable and returns trustworthy character/line metadata only. Each `exec` reads one Python cell on stdin; state survives across cells and capped cell output comes back for inspection. `final` retrieves the saved answer. `kill` deletes the session; `list` shows live session IDs. Monty is a Python subset: prefer explicit lists/loops over generators (`yield` is unsupported), and remember that regex backtracking is bounded.

Inside `exec`, use ordinary Python plus:

- `llm(prompt, model=None, ctx="")` — one model call; `ctx` is appended to the prompt.
- `llm_batch(prompts, model=None, workers=2)` — ordered parallel model calls whose results match input order. Provider failures are JSON strings containing `azdaja_error`; reject them explicitly. `llm` and batch items share the cumulative per-cell call budget (150 by default); submit another cell to continue with preserved state.
- `FINAL(answer)` — save the answer.
- `FINAL_VAR("name")` — save a variable by name.

Monty deliberately has no filesystem, process, environment, or network access. The only available modules are already imported as `os`, `re`, `json`, `math`, `collections`, and `datetime` (`os` host access is denied); `csv` and other imports are unavailable. `globals`, `locals`, `callable`, `eval`, `exec`, `next`, `yield`/generators, and string `%` formatting are unavailable. Never use `next(x for x in rows)`; build an ID map with explicit loops. Use f-strings, including for padded IDs. `llm` returns one string, `llm_batch` returns an ordered list of strings, and `FINAL(answer)` is always defined—call it directly without introspection. Keep the schema-targeted cell compact (prefer at most 140 nonblank lines).

## Other-host `solo` lane

The following helpers exist only inside `solo`; ordinary `exec` does not expose them:

- `exact_line_records(source, prefix)` scans complete LF/CRLF physical records with one exact anchored prefix. It preserves order, duplicates, and all bytes except the structural line separator, and fails closed on ambiguous boundaries, no matches, or more than 105,000 records.
- `exact_line_ledger(ctx, prefix)` returns immutable `(occurrence_id, record)` entries for the complete authoritative source. Fabricated, reordered, truncated, or transformed ledgers fail closed.
- `semantic_manifest_records(items, task, labels)` performs two blind complete-record manifests plus bounded disagreement adjudication. Its host implementation uses at most 39 representatives and 80 KiB per shard and expands every duplicate occurrence.
- `semantic_manifest(ledger, selected_ids, target_marker, task, labels)` is the only admitted projected form. It requires canonical selected IDs in source order and one exact nonempty final-suffix marker per selected record, projects byte-for-byte, and publishes host-attested ledger/projection/expansion counts.
- `source_ontology()` returns a detected exact ontology declaration. `lexical_relevance(source, query, max_chars=20000)` is lossy and is never evidence for exact counts, order, multiplicity, or exhaustive coverage.

Labels are produced by classifying complete instances, never by searching for label fields or label words. Apply deterministic selectors to complete records before projection. Source occurrences and multiplicity are preserved; every caller occurrence is expanded before reduction, and every declared label is initialized, including zero-count labels. Missing, malformed, failed, or disputed output is an error, never a complement label. Complete validated coverage is required before `FINAL`, including exact domain, multiplicity, reduction, and schema checks.

In hosts that use `solo`, invoke it once and accept its result or failure. Its 39-item semantic shards are capped at 39 representatives and 80 KiB and use eight workers. The runtime may make at most three root repair turns only before unsafe child-calling failures; the outer agent must never retry `solo` or switch lanes. Prefer one root planning turn and one compact successful cell.
