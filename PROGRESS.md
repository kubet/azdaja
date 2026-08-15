# Azdaja Speed Campaign Progress

## Current state

- Frozen measurements, candidate binaries, schedules, failures, and prior consumed sentinels remain byte-unchanged. The latest explicit owner instruction authorized one separate null-safe score of the retained 60-row reasoning sweep; no inference was rerun.
- **OOLONG is 57.6923% official (15/26)** for the current best query-cap-512 binary at Luna/low. Execution was 23/26, canonical predictions 20/26, median latency 20.956s, and root-context leaks 0/26. The fixed report is `bench/results/oolong-current-best26-report.json` (`93c67a076ef7045c69723f89e4bd4d7e5ba6dfe5ee008faedd28969f4dc1af5b`).
- The retained RULER effort sweep now has its one authorized repaired score. Low is 19/20 official full coverage and 18/20 exact at 11.304s; medium is 19/20 official and 18/20 exact at 21.124s; high is 17/20 official/exact at 33.277s. No arm is 20/20, so the conditional speed close does not trigger and no effort is adopted. Report: `bench/results/ruler20-reasoning-sweep-repaired-report.json` (`c23c95a3262dc2aa8380b2383fc399eb900265e22690e20885f24cb5d28f1b7c`).
- The terminal validation-derived RAH-199 run is active on the same binary. Its immutable schedule `d2448310be3ca7df33a71106acc89215b528d64a5eb22e3903ee9b04dd436d10` covers all 13 length buckets with 199 fixed rows, failures scored zero, official numeric `0.75 ** abs(y-y_hat)` scoring, and an equal-weight length macro. Selection and schedule are preserved in `bench/results/`; a five-minute internal heartbeat monitors it without retries.
- Stable keyed caching and the WARM daemon lane are conclusively closed. The OAuth route omits stable cache keys; unrewound continuation contaminates tasks; rewind/service reset clears provider-session identity and resends context. Cold fresh sessions remain authoritative. `JCODE_SESSION_FORK_API_REQUEST.md` specifies the isolated static-prefix fork needed to reopen the lane.
- LongBench boundary: Azdaja is about 15% faster and about 9.2x cheaper in root context with zero leaks, but is 23.3pp behind native on identical holistic-MCQ rows (14/30 vs 21/30).

## Strict next step

Monitor the frozen RAH-199 process to terminal completion. Never retry, resume, substitute, or alter a row. After exactly 199 terminal rows and a valid completion record, run the no-gold validator; only if it passes, invoke the frozen one-shot scorer once, preserve the report under `bench/results/`, update `WORKS.md`, `FAILS.md`, and this file in the same commit, and stop the heartbeat.

## Blocking

- The RULER speed close is a NO: low effort is not 20/20.
- No cache-prefix, WARM daemon, peek-first, or silent service-restart reuse work remains eligible on Jcode v0.75.3.
- The RAH result is a preregistered validation-derived subset, not the official full OOLONG test score. Dataset-family development exposure and the exact two-window exclusion must remain disclosed.
