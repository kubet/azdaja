# Azdaja Speed Campaign Progress

## Current state

- **OOLONG is 57.6923% official (15/26)** for the query-cap-512 binary at Luna/low. Execution was 23/26, canonical predictions 20/26, median latency 20.956s, and root-context leaks 0/26. The fixed report is `bench/results/oolong-current-best26-report.json` (`93c67a076ef7045c69723f89e4bd4d7e5ba6dfe5ee008faedd28969f4dc1af5b`).
- RAH-199 inference is terminal. The immutable validation-derived schedule completed all 199 rows across all 13 length buckets with 159 execution successes, 40 retained failures, median latency 21.589s, and zero root-context leaks on 199 applicable scans. The no-gold validator passed.
- RAH-199 terminal scoring was invoked exactly once. It created the consumed sentinel and opened scoring gold, then exited 2 on `score error: E: unsupported gold`. It created no report, so the official fixed-denominator score and equal-weight length macro are unavailable. The scorer, inference, cohort, failures, and sentinel are terminal and must never be rerun, replaced, altered, or rescored. Terminal record: `bench/results/rah199-terminal-failure.json` (`096456bc48b8d8deefdce5070a1a4aed1f87576e975f6e22c749fe13e8662382`).
- The retained RULER effort sweep's one authorized repaired score remains low 19/20 official full coverage and 18/20 exact at 11.304s; medium 19/20 and 18/20 at 21.124s; high 17/20 and 17/20 at 33.277s. No arm is 20/20, so no speed close or effort adoption occurred.
- Stable keyed caching and the WARM daemon lane remain hard NOs. The OAuth route omits stable cache keys; live continuation contaminates tasks; rewind/service reset clears provider-session identity and resends context. Cold fresh sessions remain authoritative. `JCODE_SESSION_FORK_API_REQUEST.md` records the upstream capability required to reopen this line.
- LongBench boundary remains: Azdaja is about 15% faster and about 9.2x cheaper in root context with zero leaks, but 23.3pp behind native on identical holistic-MCQ rows (14/30 vs 21/30).
- Read-only RAH failure forensics found 39 product exits plus one route assertion. Thirty-three product exits survived both repair turns; 29 ended on generated assertions. The task-family concentration and non-conclusive length trend do not establish a generic causal mechanism, so no third-repair/prompt/helper candidate was accepted. Report: `bench/results/rah199-failure-forensic.json` (`b2c9e1fe6aaae186c5b67984d831dad98459bfe376598457e245c9805efa6803`).
- No candidate was promoted. Frozen measurements, candidate binaries, schedules, retained failures, and consumed sentinels remain preserved.

## Strict next step

Stop this terminal sequence and preserve its evidence. Do not repair or rerun the RAH scorer, inference, failed rows, cohort, or sentinel. Reopen product work only for a genuinely new generic mechanism with independent causal evidence, a distinct frozen candidate, fresh regression and at-least-10-row inference gates, zero leaks, a scorer prevalidated against every retained value shape/failure row before gold access, and same-commit `WORKS.md`/`FAILS.md`/`PROGRESS.md` evidence before promotion; or for a shipped provider session-fork API that proves isolated static-prefix reuse.

## Blocking

- No RAH score exists; the consumed one-shot attempt failed terminally.
- RULER low effort is not 20/20 and cannot close speed.
- Cache-prefix, WARM daemon, peek-first, and silent service-restart reuse remain ineligible on Jcode v0.75.3.
- The RAH cohort is validation-derived rather than the official full OOLONG test split; its dataset-family exposure and exact two-window exclusion remain disclosed.
