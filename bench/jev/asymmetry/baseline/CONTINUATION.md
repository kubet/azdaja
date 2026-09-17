# Interruption-only continuation amendment

The original frozen baseline was admitted once at 2026-09-17T17:40:45.946793Z.
The bash tool imposed a 600-second parent deadline despite a requested 7,320-second
execution envelope. It killed the controller after 24 ordinary completed packs.
The already-admitted 25th native turn finished. Its 157 answers were subsequently
retrieved through `azdaja final` without `exec` or another model call. The raw model
trace records all 25 successes and their known input/output usage.

The original receipt, requests, answers, trace and freeze remain unchanged. An
append-only `external-interruption.json` distinguishes the stopped parent from the
successful last native turn, its recovered final, and cleanup. No completed answer
is being retried or repaired. No partial quality scores motivated this amendment.

This amendment authorizes only the untouched ordered suffix, packs 026 through 112.
Keep exactly the original source/state/questions/instruction/model/reasoning,
112 total logical admissions including the 25 originals, 224 entered turns,
4,000,000 known input tokens, 1,000,000 known output tokens, and the original absolute
19:40:45.946793Z campaign deadline. Unknown input/output usage, malformed answers,
changed source, identity drift or any cap crossing still terminates without retry.

A new private native session reconstructs all 25 retained answers without inference,
including an exact-ID reentry of the recovered 25th final. All accounting includes
the predecessor, not reset budgets. The suffix is one exclusive sealed admission.
A controlled detached launcher avoids the tool's shorter parent-command deadline,
but does not extend the campaign deadline or native 120-second shared cell limit.
The watchdog retains a terminal failure if that deadline is reached. Progress is
written per pack. The user can stop the scoped process at any time.

This is an amended, interrupted one-pass comparison, not an uninterrupted run of
the original controller. Report full elapsed time including interruption/recovery,
model-call times separately, historical rather than randomized concurrent pairing,
known usage rather than subscription billing, and all predecessor artifacts.
There is no new quality threshold, discarded outcome, generative repair, or second
pass. If recovery fails, retain the incomplete receipt rather than inventing a
headline comparison. No README or external effectiveness claim is authorized.
