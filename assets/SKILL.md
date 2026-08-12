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

End by calling `FINAL(...)` or `FINAL_VAR(...)`. Output is capped, so assign large intermediate results to variables and inspect small slices.
