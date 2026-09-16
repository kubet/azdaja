---
name: azdaja
description: Use only when the user explicitly chooses Azdaja for the current request, session, or repository.
---

# Azdaja 0.1.17

## Managed-skill awareness and route

- Optional. Use only after explicit user choice. Mentions, installed files, hooks, and skill loading do not activate Azdaja.
- Check availability with the resolver below. Bare `az` may be Azure CLI and must never be accepted without the Azdaja identity probe.
- Without activation, or when Azdaja fails, keep host-native tools available.
- Jcode hook routing requires `AZDAJA_JCODE_ACTIVATION=request`, `session`, or `repository` in the host process environment. Do not set this automatically merely because the skill was loaded.
- Azdaja is a cooperative workflow tool, not an OS sandbox.

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
