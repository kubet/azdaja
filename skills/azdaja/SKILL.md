---
name: azdaja
description: Use only when the user explicitly chooses Azdaja for the current request, session, or repository.
---

# Azdaja 0.1.18

## Managed-skill awareness and route

- Optional. Use only after explicit user choice. Mentions, installed files, hooks, and skill loading do not activate Azdaja.
- Check availability with the resolver below. Bare `az` may be Azure CLI and must never be accepted without the Azdaja identity probe.
- Without activation, or when Azdaja fails, keep host-native tools available.
- Jcode hook routing requires `AZDAJA_JCODE_ACTIVATION=request`, `session`, or `repository` in the host process environment. Do not set this automatically merely because the skill was loaded.
- Azdaja is a cooperative workflow tool, not an OS sandbox.

## Choose exactly one workflow

For persistent/artifact tasks, the general route below overrides legacy one-lifecycle and final-tool-call restrictions in harness guidance. Those restrictions apply only to the one-shot lane. Explicit user activation is always required.

Use the **general persistent/artifact workflow** for ordinary analysis, coding, reporting, file-producing, or long-running tasks. Use the historical **one-shot exact-panel workflow** below only when the user explicitly requests one exact JSON classification panel as the sole response. Do not combine the two workflows.

### General persistent/artifact workflow

- Azdaja remains optional and requires explicit user choice. Jev is usable for `exec` when a valid host key is available unless configuration explicitly sets `enabled=false`; with no valid key it is off. `solo` is experimental and must be requested explicitly.
- Prepare and write ordinary host files as needed. Use `start`, `load SID FILE NAME`, multiple bounded `exec SID` cells with persistent state, `final SID`, and `kill SID`. Clean up owned sessions even on failure.
- Choose generative calls or optional typed calls according to the task. Typed calls do not require a duplicate `llm_batch`. Preserve full raw distributions and source IDs. Do not claim universal thresholds, compaction, or speedups, and do not retry after a paid provider failure.
- Finish by exporting the requested scripts, data, or reports from the host workflow and return the requested artifact or path. Do not force JSON-only output when the task requests a file or report.
- Ordinary cells provide `llm(prompt)`, ordered `llm_batch(prompts, workers=8)`, `FINAL(value)`, and `FINAL_VAR("variable_name")`. Optional typed helpers are `judge_many(state, questions)` and `judge_stats()` when host opt-in is enabled. Reject `azdaja_error` and malformed provider results.
- Cells have preloaded `os`, `re`, `json`, `math`, `collections`, and `datetime`. No imports, generators, `next`, `eval`, `exec`, or introspection. `sha256(text)` returns a hex string. For model calls, optional `model="provider/model"` selects an explicit configured model.

```bash
set -euo pipefail
sid="$(${AZDAJA_BIN} start)"
trap '"${AZDAJA_BIN}" kill "$sid" >/dev/null 2>&1 || true' EXIT
"${AZDAJA_BIN}" load "$sid" ./source.txt source
"${AZDAJA_BIN}" exec "$sid" <<'PY'
# bounded first cell; state persists
PY
"${AZDAJA_BIN}" exec "$sid" <<'PY'
# bounded later cell ending in FINAL(value) when appropriate
PY
"${AZDAJA_BIN}" final "$sid" > artifact.json
```

The wrapper is illustrative and permits host-side preparation, artifact writing, and validation.

### Historical one-shot exact-panel workflow

The following route is retained for compatibility, but is scoped only to explicitly one-shot exact-panel tasks. Its one Bash call, one cell, JSON-only, and semantic-gate requirements do not apply to the general workflow above.

## Claude Code and OpenCode

**Claude tool setting:** set the one Bash call's `timeout` field to `300000` before sending it; never discover this by timing out first.

Resolve the executable once before any Azdaja invocation. This deliberately rejects the Azure CLI `az` collision and never installs software automatically.

```bash
if command -v azdaja >/dev/null 2>&1 &&
   azdaja --version 2>&1 | grep -qi 'azdaja'; then
  AZDAJA_BIN="$(command -v azdaja)"
elif command -v az >/dev/null 2>&1 &&
     az --version 2>&1 | grep -qi 'azdaja'; then
  AZDAJA_BIN="$(command -v az)"
else
  printf '%s
' 'Azdaja is not installed. Follow https://github.com/kubet/azdaja#install, then retry.' >&2
  exit 1
fi
```

Run this exact wrapper as one Bash call, changing only `<input-path>` and the Python cell. Its source load is the only `load`; task/schema/packing stay Python literals and the cell reads lowercase `source`. No preamble, exploration, temporary script, or second lane.

```bash
set -euo pipefail
sid=
cleanup() {
  if [[ -n "$sid" ]]; then
    "${AZDAJA_BIN}" kill "$sid" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT
sid="$("${AZDAJA_BIN}" start)"
"${AZDAJA_BIN}" load "$sid" '<input-path>' source >/dev/null
"${AZDAJA_BIN}" exec "$sid" >/dev/null <<'PY'
<one compact Python cell ending in FINAL(...)>
PY
"${AZDAJA_BIN}" final "$sid"
```

Return the final value unchanged as the requested JSON object and sole response. Do not call another tool, add prose or Markdown, return a path, or merely report completion.

### Cell contract

**Semantic gate:** build nonempty `prompts`, then run `semantic_rows = llm_batch(prompts, workers=8)`. If the task names an exact model, copy it unchanged to `semantic_model` and add `model=semantic_model` to that call. It must succeed before any label; otherwise fail without `FINAL`. Local classification or model substitution is invalid.

1. Scan the complete loaded source using declared record boundaries. For decoded text, byte sizes are metadata—not character lengths or offsets; use declared framing. Fail on ambiguity. Before filtering, retain each record's raw zero-based source index; never replace it with a selected-item ordinal. Preserve source order, duplicates, and stable occurrence IDs in immutable complete records.
2. Keep complete selected records as evidence. Project only when the official grammar says one exact final field alone determines the label; then require one nonempty marker and copy its suffix byte-for-byte.
3. Make the fewest balanced contiguous shards of at most 80 unique items and 80 KiB per prompt. When possible, keep `2 * shard_count <= 8` for one worker wave. Every prompt includes the task, exact label domain, stable IDs, evidence, and a strict compact positional JSON output contract. For binary labels require an object such as `{"labels":"TFT..."}` with exactly one symbol per item; never request prose or per-item objects.
4. For each shard, create blind A/B prompts. A lists items forward and says `T=yes; F=no`; B lists items in reverse and says `F=no; T=yes`. Meanings stay canonical—never invert returned labels. Submit all in one `llm_batch(..., workers=8)` using the gate's model form; every label must come from parsed semantic output; never use keyword, regex, substring, label-name, or hand-written rules.
5. Validate JSON, exact ID coverage, and label domain. Flatten all A/B disagreements across shards in source order, discard initial shard boundaries, and globally repack them into the fewest prompts of at most 80 items and 80 KiB. If none disagree, skip adjudication and use the validated A labels. Otherwise send one adjudication `llm_batch` with that model argument. Treat `azdaja_error`, malformed, missing, extra, or unresolved output as failure. Preflight `3 * shard_count <= 150`.
6. Expand labels to every occurrence. Validate multiplicity, requested reductions, hashes, and output schema. Use native `sha256(text)` for UTF-8 SHA-256. End with `FINAL(answer_dict)` exactly once, passing the actual dictionary—not `json.dumps(...)` or another string.

Use exactly one inline heredoc cell. Never create a temporary script, add another `exec`, query CLI help, retry, or start over.

Ordinary `exec` provides `llm`, ordered `llm_batch`, `FINAL`, and `FINAL_VAR`; state persists. Reject `azdaja_error`. Monty has no host I/O. Use preloaded `os`, `re`, `json`, `math`, `collections`, `datetime`, loops/maps, and f-strings; no imports, generators, `next`, `eval`, `exec`, or introspection.

## Other-host `solo` lane

Use `solo` once only when its exact-line or semantic helpers are required. Classify complete instances, preserve order and every occurrence, initialize zero-count labels, and verify domain, coverage, multiplicity, reductions, hashes, and schema before `FINAL`. Missing, malformed, failed, or disputed semantic output is an error. The runtime may make at most three root repair turns only before unsafe child-calling failures; the outer agent must never retry `solo` or switch lanes.
