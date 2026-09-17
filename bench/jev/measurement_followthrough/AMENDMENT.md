# Measurement v2: untouched-panel continuation

This is an explicit amendment, not an automatic retry or a replacement result.
Original source/fixtures at 645b925 and seal at 5551b94 remain immutable. The
original campaign remains stopped. Its second typed request, flat-02, returned
`judge: probabilities must sum to one`. The accepted native binary discarded the
invalid body. Its actual probability sum, affected IDs and rounding precision
are therefore unknown. No assertion of a rounding bug or provider defect follows.
The validator is NOT relaxed and the request is NOT repeated.

Retain all original calls: two typed requests (50 attempted questions, 25 valid
judgments), 17,705 known input tokens, 1,229 known output tokens plus one request
with unknown output usage, and two generative calls (50 judgments). Failed input
usage counts toward both the budget and estimated cost. Missing judgments remain
missing, never silently dropped or treated as abstentions.

## Remaining execution, fixed before any new provider call

Run the eight previously untouched verifier packs FIRST, then flat-03 and flat-04.
This order isolates the requested flag-only experiment from the already observed
Choice-contract failure. Within each pack, preserve the original ordinal's
typed-first/generative-first order. No previously attempted (pack, arm) can run
again, whether its result succeeded or failed. An additional failure stops this
continuation without retry. No judgment, question, gold, model, threshold, corpus,
native binary or validation contract is changed.

Cumulative caps across both receipts remain 12 typed requests, 12 logical
generative calls, 24 entered generative turns, 1,500,000 typed input tokens.
The original 1,800-second wall limit is superseded explicitly by 1,800 seconds
of summed campaign elapsed time, excluding this stopped investigation interval.
Both intervals and the amendment time are retained. Each request still has the
original bounded native timeouts. The remaining 10+10 calls fit the original
request budget. The continuation is independently sealed and one-shot.

Even if every remaining call succeeds, the original flat panel has at most 75
valid typed judgments out of 100. It cannot pass its 100-case completion or
quality bar. Report contract coverage and partial accuracy, NOT a >=100-case
semantic verdict. The untouched verifier can reach 200/200 on both arms under
the unchanged original bar. No automatic approvals are enabled. No RAH submission,
population calibration, RLM moat, README claim or general advantage is authorized.

## Evidence and acceptance

Replay both receipts from raw retained requests/observations/generative outputs
and traces. Carry failed input usage and explicitly unknown output usage. Reject
repeat attempts, input/prompt swaps, missing IDs, forged completion, hidden failed
usage and altered frozen inputs. Preserve the original report's demonstrated
partial-usage limitation rather than changing its frozen implementation.
New source, predecessor artifacts, tests and amendment are frozen before live.
Public offline load/exec/final preflight must pass before the continuation.
Temporary experiment credentials and its isolated bridge are removed afterwards;
the user's default persistent attachment and installation remain unchanged.
