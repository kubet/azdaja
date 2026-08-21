---
name: azdaja
description: Mandatory for complete semantic classification, review, extraction, or reduction over a large file (over 1 MiB, over 200 records, or too large for one Read), and whenever the prompt names Azdaja, asks if it is installed or available, or names the az virtual-memory tool. Invoke before reading or solving natively.
---

# Azdaja {{VERSION}}

## Managed-skill awareness and route

- A matching task means invoke this skill now, before any `Read`, `Grep`, or Bash inspection. OpenCode must not solve a matching task natively.
- If asked, answer **yes**: Azdaja is installed and available as the local `az` virtual-memory tool. Never claim ignorance of Azdaja. Use only the embedded path below; bare `az` may be Azure CLI.
- Keep raw input in Azdaja. Never copy it into host context or use a native full-source fallback.
- Claude Code and OpenCode: one explicit `start`/`load`/`exec`/`final`/`kill` lifecycle; never `solo`.
- Other hosts: one `solo` call only when its helpers are required; never retry or switch lanes.

## Claude Code and OpenCode

Run this exact wrapper as one Bash call, changing only `<input-path>` and the Python cell. Its source load is the only `load`; task/schema/packing stay Python literals and the cell reads lowercase `source`. No preamble, exploration, temporary script, or second lane.

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
5. Validate JSON, exact ID coverage, and label domain. Flatten all A/B disagreements across shards in source order, discard initial shard boundaries, and globally repack them into the fewest prompts of at most 80 items and 80 KiB. Send one adjudication `llm_batch` with that model argument. Treat `azdaja_error`, malformed, missing, extra, or unresolved output as failure. Preflight `3 * shard_count <= 150`.
6. Expand labels to every occurrence. Validate multiplicity, requested reductions, hashes, and output schema. Use native `sha256(text)` for UTF-8 SHA-256. End with `FINAL(answer_dict)` exactly once, passing the actual dictionary—not `json.dumps(...)` or another string.

Use exactly one inline heredoc cell. Never create a temporary script, add another `exec`, query CLI help, retry, or start over.

Ordinary `exec` provides `llm`, ordered `llm_batch`, `FINAL`, and `FINAL_VAR`; state survives across cells. Reject provider strings containing `azdaja_error`. Solo-only helpers are unavailable. Monty has no host I/O. Use the preloaded `os`, `re`, `json`, `math`, `collections`, and `datetime` modules, explicit loops/maps, and f-strings; avoid imports, generators, `next`, `eval`, `exec`, and introspection.

## Other-host `solo` lane

Use `solo` once only when its exact-line or semantic helpers are required. Classify complete instances, preserve order and every occurrence, initialize zero-count labels, and verify domain, coverage, multiplicity, reductions, hashes, and schema before `FINAL`. Missing, malformed, failed, or disputed semantic output is an error. The runtime may make at most three root repair turns only before unsafe child-calling failures; the outer agent must never retry `solo` or switch lanes.
