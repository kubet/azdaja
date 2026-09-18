# Bounded long-artifact comparison, 2026-09-18

## Question
Does access to Azdaja's persistent runtime help a real agent finish the same large-source artifact task? This is not a single prompt versus a batch runner.

## Admission, fixed before any new provider request
- One fresh plain-agent arm and one fresh Azdaja-available arm. No repetitions, outcome-conditioned extensions, or replacement models.
- OpenCode 1.18.31, `openrouter/anthropic/claude-sonnet-5` for both roots and all Azdaja generative readers. Same original 102-contract task and source bytes, fresh isolated state. Baseline may use files, search, Python and chunking. It is not forced to fit the corpus into one prompt.
- Each arm gets 140 root steps, 1,800 seconds and an $8 observed generative-cost stop. Usage limits cannot undo an in-flight bill. Missing usage is unknown, never zero. All root event records and durable reader attempt records are retained.
- Optional Azdaja reader ceiling: 160 attempts and 2,000,000 reported input tokens, 90-second request timeout, 8,192 maximum output tokens, no adapter retries. Any failed or unknown-usage reader stops further reader admission. Root plus readers share the observed cost stop.
- Jev is **disabled in both fresh arms**. First isolate the missing Azdaja effect. Existing matched Jev/window evidence is reported separately, not substituted for this artifact task. A new Jev arm requires a separate prospective admission, not automatic retry-until-win.
- Use the published v0.1.18 executable, SHA-256 `70f620dc21bd053bbbc9c3e41beab0ce28b2ef3d50b58faf3731627233979052`. The treated arm receives the revised persistent/artifact skill route. This measures an experimental instruction repair, not an unchanged v0.1.18 stock-skill claim. Freeze the exact supplied skill before calls.
- Sequential fixed order plain, Azdaja. One observation per arm cannot establish a general speedup, order independence, or a multi-day extrapolation.

## Same deliverable acceptance
Both arms must produce executable `risk.py`, `risk.json` covering all 102 files, and `REPORT.md` containing counts and five exact source quotations with byte offsets. Use a common explicit JSON schema solely to make scoring deterministic. Re-run the generated program offline in a disposable copy after inspecting its imports and side effects. Verify exact file coverage, every positive's nonempty evidence, all original byte slices, count consistency, report quotations, and preservation of source bytes. Do not accept a path-only or JSON-only answer in place of these files.

Exact quotations and structural completion do not prove semantic label accuracy. CUAD expert labels are not identical to this task's definitions, so do not silently score them as equivalent gold. Report semantic correctness as unestablished unless separately adjudicated. Historical baseline and batch panels remain historical, including failed launches and unknown billing.

## Boundaries
No modification of the user's installed tools, existing credentials, release tag, previous experiment files, or frozen results. Private runtime and selected provider credentials stay outside the repository. No credentials in prompts, arguments, reports, or logs. Source contracts are data, not instructions. Public artifacts contain sanitized evidence only.
