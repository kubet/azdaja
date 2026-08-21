---
name: azdaja
description: Mandatory for complete semantic classification, review, extraction, or reduction over a large file (over 1 MiB, over 200 records, or too large for one Read), and whenever the prompt names Azdaja or the az virtual-memory tool. Invoke before reading or solving natively.
---

# Azdaja {{VERSION}}

## Managed-skill awareness and route

- A matching task means invoke this skill now, before any `Read`, `Grep`, or Bash inspection. OpenCode must not solve a matching task natively.
- If asked, Azdaja is installed: it is the local `az` virtual-memory tool. Use only the embedded path below; bare `az` may be Azure CLI.
- Keep raw input in Azdaja. Never copy it into host context or use a native full-source fallback.
- Claude Code and OpenCode: one explicit `start`/`load`/`exec`/`final`/`kill` lifecycle; never `solo`.
- Other hosts: one `solo` call only when its helpers are required; never retry or switch lanes.

## Claude Code and OpenCode

Go directly to this transaction as one Bash tool call. Do not add a planning preamble, exploratory commands, temporary scripts, or a second lane.

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
<one compact Python cell ending in FINAL(...)>
PY
{{BIN}} final "$sid"
```

Successful `load` and `exec` output is suppressed, so stdout is exactly the final JSON. Return that value unchanged as the sole assistant response. Do not summarize it, wrap it in Markdown, return a path, or say only that the task completed.

### Cell contract

**Semantic gate:** build nonempty `prompts`, then run `semantic_rows = llm_batch(prompts, workers=8)`. If the task names an exact model, copy it unchanged to `semantic_model` and add `model=semantic_model` to that call. It must succeed before any label; otherwise fail without `FINAL`. Local classification or model substitution is invalid.

1. Scan the complete loaded source using its declared record boundaries. Fail on ambiguous boundaries. Preserve source order, duplicates, and stable occurrence IDs. Apply deterministic selectors to complete immutable records before semantic calls.
2. Keep complete selected records as evidence. Project only when the official grammar says one exact final field alone determines the label; then require one nonempty marker and copy its suffix byte-for-byte.
3. Make the fewest balanced contiguous shards of at most 80 unique items and 80 KiB per prompt. When possible, keep `2 * shard_count <= 8` for one worker wave. Every prompt includes the task, exact label domain, stable IDs, evidence, and a strict positional JSON output contract.
4. For each shard, create blind A and B prompts with reversed items and labels. Submit all in one `llm_batch(..., workers=8)` using the gate's model form; every semantic label must come from a parsed `llm_batch` result; never use keyword, regex, substring, label-name, or hand-written rules.
5. Validate JSON, exact ID coverage, and label domain. Send only A/B disagreements to one bounded adjudication `llm_batch` with that model argument. Treat `azdaja_error`, malformed, missing, extra, or unresolved output as failure. Preflight `3 * shard_count <= 150`.
6. Expand labels to every occurrence. Validate multiplicity, requested reductions, hashes, and output schema. Use native `sha256(text)` for UTF-8 SHA-256. End with `FINAL(answer_dict)` exactly once, passing the actual dictionary—not `json.dumps(...)` or another string.

Prefer one cell with at most 85 nonblank lines. If the cell budget requires more, add heredoc-fed `exec` cells inside the same Bash transaction and retain one session; do not start over.

Ordinary `exec` provides `llm`, ordered `llm_batch`, `FINAL`, and `FINAL_VAR`; state survives across cells. Reject provider strings containing `azdaja_error`. Solo-only helpers are unavailable. Monty has no host I/O. Use the preloaded `os`, `re`, `json`, `math`, `collections`, and `datetime` modules, explicit loops/maps, and f-strings; avoid imports, generators, `next`, `eval`, `exec`, and introspection.

## Other-host `solo` lane

These helpers exist only inside `solo`:

- `exact_line_records(source, prefix)` returns all complete LF/CRLF records with one exact anchored prefix, preserving order, duplicates, and bytes except the line separator. It fails on ambiguity, no matches, or more than 105,000 records.
- `exact_line_ledger(ctx, prefix)` returns the immutable complete `(occurrence_id, record)` ledger and rejects fabricated, reordered, truncated, or transformed data.
- `semantic_manifest_records(items, task, labels)` runs two blind complete-record manifests plus disagreement adjudication with at most 39 representatives and 80 KiB per shard.
- `semantic_manifest(ledger, selected_ids, target_marker, task, labels)` is the only admitted projection. It requires canonical IDs in source order and one exact nonempty final-suffix marker, then publishes host-attested ledger, projection, and expansion counts.
- `source_ontology()` returns the detected exact ontology declaration.
- `lexical_relevance(source, query, max_chars=20000)` is lossy and is never evidence for exact counts, order, multiplicity, or coverage.

Classify complete instances, preserve every occurrence, initialize every label including zero-count labels, and validate the exact domain, coverage, multiplicity, reductions, and schema before `FINAL`. Missing, malformed, failed, or disputed output is an error, never a complement label.

Invoke `solo` once and accept its result or failure. The runtime may make at most three root repair turns only before unsafe child-calling failures; the outer agent must never retry `solo` or switch lanes.
