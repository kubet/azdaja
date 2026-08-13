# v32 frozen three-suite campaign gate

This document records the decision rule for the private v32 diagnostic campaign. It was written after 71 of 270 RULER inference rows were terminal and their execution-success flags were visible, but before any v32 gold was opened or any v32 accuracy was computed. It is therefore a prospective gold/accuracy gate, not a fully preregistered execution-reliability threshold and not external authentication.

## Frozen candidate and suites

- Candidate source commit: `48b8a1688dc1056e4aee9086a643dbbf1aa100f3`
- `azdaja`: `f53d43ecde4fd800789d0b7469fa6ad81bb2dd46e41a0c643f90dc8e77a2228d`
- `config.toml`: `91a35c191f56856d05fb7c9599bd376e01bbd5d4589d128cc81b733b7056d396`
- `SKILL.md`: `923d8fc81bb19b5c7bb783b8aa9b6dbfbcc9906fe79fa7ed53272fea202fadc3`
- Model/reasoning: `gpt-5.6-luna`, medium, subscription OAuth
- Derived RULER: 90 fixtures × 3 arms = 270 terminal jobs
- LongBench-v2: 63 fixtures × 3 arms = 189 terminal jobs
- OOLONG diagnostic: 26 fixtures × 3 arms = 78 terminal jobs

The suites execute serially. Every scheduled row remains in its fixed denominator. A stopped or invalid cohort is preserved and not selectively retried, substituted, reordered, or repaired. Candidate bytes, model, reasoning, adapters, controller, fixtures, scoring, or policy drift blocks the campaign.

## Universal integrity gates

A suite may be scored exactly once only after its exact terminal schedule, claims, artifacts, identities, and hashes validate. Its gold remains unopened until that validation finishes. Every Azdaja row, including execution failures, must retain an exact authoritative root transcript. Any exact common substring of at least 100 Unicode characters between the loaded long context and Azdaja root transcript is a hard architectural failure. Missing/ambiguous usage and economy evidence remains missing, never zero. Degraded or typed failed transport remains a failed execution even if later output exists.

Every report must provide scheduled count, execution-success rate, completed-only accuracy, fixed-denominator end-to-end accuracy, normalized and raw failure taxonomy, root-token economy and missingness, version/executable stamps, and the leak gate. Controls disclose that the distinct Azdaja root/child containment boundary is inapplicable; post-hoc tool auditing is not OS containment.

## Sequential pass/block rule

“Pass” here means eligible to continue this private diagnostic campaign, not publication-grade proof or a superiority/SOTA claim.

1. **RULER:** all 270 rows terminal and all universal integrity gates pass. Azdaja fixed-denominator exact accuracy must be at least the historical v3 baseline, 28/90. Any root-context leak blocks. If it passes, LongBench-v2 may start.
2. **LongBench-v2:** all 189 rows terminal and all universal integrity gates pass. Because v1-v5 never produced a scored baseline, the preregistered diagnostic floor is Azdaja execution success at least 32/63 and fixed-denominator exact accuracy at least 16/63. Any root-context leak blocks. If it passes, OOLONG may start. These modest floors are campaign viability gates, not state-of-the-art thresholds.
3. **OOLONG:** all 78 rows terminal and all universal integrity gates pass. Azdaja execution success must be at least 25/26 and fixed-denominator exact accuracy at least the historical v29 baseline, 24/26. Any root-context leak blocks.

Accuracy equality at the floor passes; a smaller numerator blocks. Control results are reported but do not determine continuation, because this campaign is a candidate regression gate rather than a superiority test. No metric may be mixed across candidates.

## RAH boundary

Clearing these gates does not itself authorize a claimable RAH run. A 199-item OOLONG-Synth validation-derived RAH protocol additionally requires an externally signed and time-stamped preregistration made before a fixed future randomness-beacon round, independent gold custody and pre-gold terminal commitment, the released official scorer, immutable numeric statistical hypotheses, a locked runtime, enforceable OS/network containment through a broker, and honest validation-derived—not official/full OOLONG—wording. Without those prerequisites, RAH must not start.
