# Azdaja Speed Campaign Progress

## Current state

- Frozen measurements, candidates, schedules, failures, and consumed scoring sentinels remain byte-unchanged. Benchmark harness sources remain unmodified; gold has only been opened by terminal one-shot scorers; all fixed denominators and leak evidence are retained.
- The holistic choice line remains closed at native 21/30 versus v4r 14/30 and v5 14/30. v5 is active-but-null: its structured contrastive path ran on 30/30 rows but did not change aggregate accuracy. No candidate may ship from offline gates without at least a 10-identical-row inference differential.
- The generic query-term maintenance patch (256 -> 512 under the unchanged 8,192-character envelope) passed regressions and a 10-row inference differential, but remains unpromoted. Candidate commit `bf75ad2`, binary `3d067bcf530667e9b05bbf2fdcf7111710cbb1b16f3663ef4637f58321c47047`.
- Native's frozen RULER smoke is 20/20 execution but **19/20** official/exact at 11.446s median. No retry changed that baseline.
- The candidate's fixed low/medium/high RULER sweep is terminal: low 20/20 execution at 11.304s median, medium 20/20 at 21.124s, and high 17/20 at 33.277s with two timeouts and one transport failure. No-gold validation passed 60/60 and leaks were 0/60. Its one-shot scorer consumed and opened gold, then failed on null usage for a retained high-effort failure; no score report exists, no rerun is permitted, and no reasoning effort is adopted.
- Stable keyed caching is hard-dead on the shipped OAuth route. A real same-session warm probe also failed strict task isolation: unrewound TASK B reproduced TASK A's marker. Rewind removed contamination, but Jcode source proves it resets provider continuation and resends full context. Therefore `azdaja-warm` is a NO-GO on Jcode v0.75.3; cold mode remains authoritative.
- Multi-turn peek-first snippets are ineligible because the required safe warm+cached+tuned operating point does not exist. No trajectory or provider-default change was adopted.

## Strict next step

There is no permissible promotion or downstream benchmark step for this frozen candidate: scored RULER parity is unavailable, so OOLONG and the 199-item RAH protocol remain blocked. Preserve all evidence. Reopen only for a genuinely new generic product mechanism and distinct candidate/fresh cohort with a no-gold-prevalidated scorer, or for a shipped provider API that can branch from a static prefix while proving zero cross-task content. Any reopened line must again pass regressions, at least a 10-row inference differential, zero-leak validation, terminal one-shot scoring, and same-commit ledgers before promotion.

## Blocking

- Do not rerun or rescore the reasoning sweep; its consumed sentinel and missing score are terminal evidence.
- Do not implement an unsafe warm daemon, refer to keyed prompt caching, run the conditional snippet scout, or tune defaults from unscored execution data.
- Do not launch OOLONG or RAH without a new candidate that first establishes scored RULER eligibility under the unchanged evidence rules.
