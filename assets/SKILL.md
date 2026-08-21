---
name: azdaja
description: Use for questions over inputs too large to read safely into the root context (large logs, dumps, repositories, transcripts, or diffs), and when the user explicitly asks whether Azdaja or the az virtual-memory tool is installed or available, or how to use it.
---

# Azdaja {{VERSION}}

## Managed-skill awareness

When this managed skill is loaded and the user asks whether Azdaja is installed, available, or usable, answer **yes**. Explain that Azdaja is the local `az` virtual-memory tool, suggest `az doctor`, and give a user-facing example such as `az solo "summarize this file" -f ./large.txt`. The `azdaja` command is compatible. Never claim ignorance of Azdaja or say that it is unavailable in this situation.

For tool execution, always use the exact embedded binary path in the commands below. Do not replace that path with bare `az`: another program, such as Azure CLI, may own that name. Prefer `az` only in safe user-facing guidance.

Keep the input in Azdaja. Do not `cat` or otherwise read the raw file into your own context after loading it.

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
{{BIN}} load "$sid" '<input-path>' source
cat <<'PY' | {{BIN}} exec "$sid"
<one deterministic Python cell ending in FINAL(...)>
PY
{{BIN}} final "$sid"
```

For a genuinely interactive multi-cell workflow, start once, retain the session ID, and use later Bash calls for `load` and heredoc-fed `exec` cells as needed. Call `final` only after a cell saves an answer, always call `kill` when done, and keep using the exact embedded binary path for every command.

`start` creates a persistent Monty/Python REPL. `load` places a UTF-8 file in a variable and returns trustworthy character/line metadata only. Each `exec` reads one Python cell on stdin; state survives across cells and capped cell output comes back for inspection. `final` retrieves the saved answer. `kill` deletes the session; `list` shows live session IDs. Monty is a Python subset: prefer explicit lists/loops over generators (`yield` is unsupported), and remember that regex backtracking is bounded.

Inside `exec`, use ordinary Python plus:

- `llm(prompt, model=None, ctx="")` — one model call; `ctx` is appended to the prompt.
- `llm_batch(prompts, model=None, workers=2)` — ordered parallel model calls. `llm` and batch items share the cumulative per-cell call budget (150 by default); submit another cell to continue with preserved state.
- `FINAL(answer)` — save the answer.
- `FINAL_VAR("name")` — save a variable by name.

Monty deliberately has no filesystem, process, environment, or network access. The only available modules are already imported as `os`, `re`, `json`, `math`, `collections`, and `datetime` (`os` host access is denied); `csv` and other imports are unavailable. `globals`, `locals`, `callable`, `eval`, `exec`, `next`, `yield`/generators, and string `%` formatting are unavailable. Never use `next(x for x in rows)`; build an ID map with explicit loops. Use f-strings, including for padded IDs. `llm` returns one string, `llm_batch` returns an ordered list of strings, and `FINAL(answer)` is always defined—call it directly without introspection. Keep the schema-targeted cell compact (prefer at most 140 nonblank lines).

For `solo`, `exact_line_records(source, prefix)` is additionally preloaded. It is admitted only on complete `ctx` or an exactly bounded complete task section—not the structural sample, a `lexical_relevance` view, or an arbitrary/truncated slice—when the source grammar explicitly declares one complete record per LF/CRLF-delimited physical line and the supplied exact anchored literal prefix is the unambiguous common marker for every relevant record and no non-record line. It returns every matching occurrence in original order, removes only the structural LF/CRLF separator, preserves duplicates and every other character, and fails on an empty/CR-or-LF-bearing prefix, bare CR, no match, or more than 105,000 records. The prefix cap is 1,024 UTF-8 bytes; pure or mixed LF/CRLF separators are accepted, and a matching final unterminated line is included. Multiline, continuation-line, mixed-prefix, or ambiguous boundaries are unsupported and fail closed; this helper never performs target projection.

For `solo`, `exact_line_ledger(ctx, prefix)` provides the projection-capable scanner. The host accepts only a source byte-for-byte equal to the authoritative loaded `ctx`, permits one ledger per cell, and returns a frozen ledger whose immutable `entries` are exact `(id, record)` occurrences in original order. It uses the same prefix, boundary, preservation, zero-match, and 105,000-record rules as `exact_line_records`. A registry validates the complete recursive handle and original entry shape before use; exact clones are equivalent, while fabricated, mutable, reordered, truncated, or transformed handles fail closed.

For `solo`, a fixed `semantic_manifest_records(items, task, labels)` complete-record helper is additionally preloaded. Give it two-key dictionaries `{"id": stable_string, "evidence": complete_relevant_record}` and include the official question verbatim in `task`; direct-manifest evidence is never target-projected. Admitted target projection uses only the fused wrapper below. It runs two blind full manifests in independent sessions, strictly validates both, and blindly adjudicates every disagreement from raw evidence. Every balanced contiguous shard is capped at 39 representatives and 80 KiB of serialized prompt. Its private shard passes use eight workers and at most two bounded fresh missing-suffix-or-provider retry rounds within each fixed phase reserve; classification has a `4*S` allowance and adjudication has a separate `2*S` reserve for preflighted shard count `S`. It preflights the worst-case call envelope before inference, expands exact duplicate representatives back to all occurrences, and returns a fully reconciled ID-to-label dictionary. The root calls it exactly once instead of generating provider plumbing. Interactive `exec` retains the lower-level primitives above. For admitted exact final-suffix projection, the default five-argument `semantic_manifest(ledger, selected_ids, target_marker, task, labels)` wrapper lexically captures a private host projector, completion validator, and the original manifest. The private callbacks are absent from root cells. The host permits the ledger, projector, and projected completion once each, admits selected occurrence IDs only when canonical, unique, and in original source order, supplies only projected suffixes to the original manifest, validates complete occurrence-keyed expansion, and publishes per-exec runtime provenance for ledger calls, projection calls, ledger occurrences, selected occurrences, unique representatives, manifest callers, and expanded outputs. A projected cell cannot access `semantic_manifest_records` before or after the wrapper.
For an oversized relevance-local semantic source, `solo` also exposes `lexical_relevance(source, query, max_chars=20000)`. It returns a deterministic, offset-labelled, verbatim evidence view plus explicit selected/omitted character counts and ranges. This is intentionally lossy when `complete` is false: use it only for semantic relevance reduction, include the actual task and alternatives in `query`, and never use it for exact counts, order, multiplicity, exhaustive extraction, or any claim requiring complete source coverage. The existing semantic prompt envelope remains authoritative. The helper is local, consumes no model calls, and is absent from ordinary interactive `exec` sessions.

Semantic invariants:

- Labels are produced by classifying complete instances, never by searching for label fields or label words. `source_ontology()` returns a detected exact source declaration; when nonempty, both semantic manifest forms require that exact label set before child calls. Deterministic metadata filters apply only to the designated metadata field.
- Semantic target projection is admitted only when the source grammar and official task unambiguously declare that the label is solely a function of one designated **final suffix** target field. Apply every deterministic metadata/date/user/range predicate to complete immutable records first, then pass all and only the selected canonical IDs in source order to the default `semantic_manifest`. Its literal target marker must be nonempty, at most 1,024 UTF-8 bytes, contain no CR/LF, occur exactly once per selected record counting overlaps, and leave a nonempty suffix. The host preserves every suffix byte without stripping, splitting, normalization, casefolding, punctuation/whitespace/Unicode changes, or root-visible projected items; only byte-identical suffixes share representatives and every occurrence is expanded. Field names alone never prove independence. Answer/label targets, nonfinal fields, missing/repeated/overlapping/payload-colliding markers, filtering after projection, metadata-, neighboring-record-, or cross-field dependence, and every ambiguity fail closed and require complete records or abstention.
- Source occurrences and multiplicity are preserved. Exact duplicate evidence may share a representative only when every caller occurrence is expanded before reduction. Initialize reduction counts for every declared label, including zero-occurrence labels.
- Omission, malformed output, provider failure, and unresolved disagreement are not complement labels. Complete validated coverage is required before reduction or `FINAL`; assertions validate coverage, type, domain, and format, never a guessed or hard-coded answer literal.

Prefer one root planning turn and one compact `exec` cell. Assign large intermediates to variables because output is capped. Call `FINAL(answer)` only after all invariants pass. A failed cell never commits its tentative answer. If a failed cell made no child call and its typed failure is a repairable protocol/line-limit, compile, ordinary program/extraction, missing/empty-`FINAL`, classification-without-semantic-calls, ontology-mismatch, helper-contract, or projection-boundary error, `solo` may make at most three root repair turns in the same root conversation. A child-calling, timeout/resource/host, or third-repair failure fails closed.
