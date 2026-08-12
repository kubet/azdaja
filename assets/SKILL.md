---
name: azdaja
description: Use for questions over inputs too large to read safely into the root context: large logs, dumps, repositories, transcripts, or diffs.
---

# azdaja {{VERSION}}

Keep the input in azdaja. Do not `cat` or otherwise read the raw file into your own context after loading it. Run:

```bash
{{BIN}} start
{{BIN}} load <session-id> <path> <variable>
printf '%s' '<python code>' | {{BIN}} exec <session-id>
{{BIN}} final <session-id>
{{BIN}} kill <session-id>
```

`start` creates a persistent Monty/Python session. `load` places a UTF-8 file in a variable and returns metadata only. `exec` reads Python on stdin and returns capped output. `final` retrieves the answer saved by the code. `kill` deletes the session; `list` shows live session IDs.

Inside `exec`, use ordinary Python plus:

- `llm(prompt, model=None, ctx="")` — one model call; `ctx` is appended to the prompt.
- `llm_batch(prompts, model=None, workers=8)` — ordered parallel model calls.
- `FINAL(answer)` — save the answer.
- `FINAL_VAR("name")` — save a variable by name.

End by calling `FINAL(...)` or `FINAL_VAR(...)`. Output is capped, so assign large intermediate results to variables and inspect small slices.

Example (illustrates the interface, not a required strategy):

```bash
{{BIN}} start
{{BIN}} load SESSION app.log ctx
cat <<'PY' | {{BIN}} exec SESSION
hits = [line for line in ctx.splitlines() if "ERROR" in line]
checks = llm_batch(["Classify this log line:\n" + line for line in hits])
FINAL({"error_count": len(hits), "classes": checks})
PY
{{BIN}} final SESSION
```
