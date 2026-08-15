# Azdaja Speed Campaign Progress

## Current state

- **RAH-199 is 28.2899% official partial credit** on the fixed validation-derived 199-row cohort (95% deterministic item-bootstrap CI **22.2927-34.4903%**). The equal-weight 13-length macro is 28.4893% (95% stratified CI 22.9423-34.1485%). This is not the official full OOLONG test score.
- The owner explicitly voided no-rescore only for scorer failures. The old failed scorer and sentinel remain immutable. The repaired scorer implemented released OOLONG parser semantics including `datetime.date` gold, passed an end-to-end exact-format synthetic rehearsal over 199 rows and all 13 buckets with exit 0 and exact expected score, then scored retained transcripts once without altering any inference row. Report: `bench/results/rah199-repaired-score.json` (`c1f4b1f1900f0e7745b2d629d21ceb3a1c1e7ce9fbc55ce21ab316b676877adb`).
- RAH inference remains frozen at 199/199 rows, 159 execution successes, 40 retained failures, 21.589s median, and zero root-context leaks across 199 applicable scans. No row was retried or replaced.
- Per-bucket official scores: 1K 58.33%, 2K 50.42%, 4K 45.86%, 8K 59.52%, 16K 25.83%, 32K 27.84%, 64K 12.50%, 128K 20.00%, 256K 14.00%, 512K 12.50%, 1M 23.44%, 2M 6.79%, 4M 13.33%. Bucket score declines strongly with length (Spearman rho -0.835, p=0.000380).
- The complete 40-failure cause x length taxonomy is committed. Counts: 29 generated assertions, 3 type errors, 2 unsupported attributes, 2 semantic-manifest parses, 2 child-call-budget overruns, 1 cell timeout, and 1 route assertion. The monotonic execution-death-vs-length hypothesis is killed at alpha 0.05 (Cochran-Armitage p=0.217; Spearman rate p=0.169); 4M is nevertheless the worst observed bucket at 5/15 deaths. No RAM/OOM cause exists.
- OOLONG remains 57.6923% official on its separate 26-row diagnostic. The retained RULER effort sweep remains low 19/20 official at 11.304s, so its conditional speed close did not trigger.
- No candidate is promoted. Cache-prefix/WARM daemon remains a hard NO.

## Strict next step

Build exactly one reliability candidate #2 from the current product tree, attacking only measured top causes: document the unsupported `dict.__getitem__`/boolean-arithmetic subset hazards in the fixed root contract; raise the child-call cap from 64 to the measured headroom cap 72 (observed demand 65/66); and raise the root repair cap from two to three repairs with a fail-closed fourth total turn. Do not change evaluator memory limits because no RAM/OOM cause exists. Require focused regressions, full tests/clippy/release, and immutable candidate identity. Then run one fresh no-gold scout over the 15 frozen-public 4M fixtures with zero leaks and no retries. The candidate must beat the frozen predecessor's 5/15 death rate (at most 4/15 deaths) to continue.

Only after that scout passes may the distinct candidate run a fresh RAH-199 schedule. Its scorer must first pass the same exact-format rehearsal. No separate OOLONG run is needed because RAH subsumes it. Any inference, failures, score, and final disposition must update `WORKS.md`, `FAILS.md`, and `PROGRESS.md` in the same commit.

## Blocking

- Reliability candidate #2 may not expand beyond the three measured changes above.
- No memory-ceiling change: memory is absent from the failure causes.
- No fresh RAH-199 launch before the worst-bucket death-rate scout beats 5/15 and the exact-format scorer rehearsal passes.
- Frozen predecessor measurements, old scorer failures, sentinels, rows, and reports remain immutable.
