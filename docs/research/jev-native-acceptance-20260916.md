# Native Jev: usefulness and final-source acceptance

> Historical receipt for executable source `ed0403b`. Its counts, failed notice
> gate and live-study identities below remain the observations from that run.
> The notice/custody repair and later clean-source acceptance are recorded
> separately in [the 2026-09-17 follow-through](jev-final-followthrough-20260917.md).
> The later [source-selection study](../../bench/jev/span_selection/RESULTS.md)
> also failed its quality-preserving benefit bar. Neither follow-up relabels
> this older binary or turns its results into a current-build measurement.

## Decision first

**The useful angle is optional evidence operations inside the RLM, not a mandatory judge.** Keep complete source and occurrence IDs, use exact code for bookkeeping, ask selected typed semantic questions, retain every returned alternative, and let the RLM inspect evidence or use `llm` where that helps. Neither a confidence cutoff nor entropy alone should decide what evidence survives.

The native operation works. **Better final answers have not been demonstrated.** In the closed seven-task live study, Jev-informed review tied ordinary self-review and missed the same material privacy omission. One retrieval diagnostic improved required-source coverage from 2/4 to 4/4, but no answer was generated from either shortlist. See [the actual outputs and decision](../../bench/jev/usefulness/RESULTS.md).

The strongest next hypothesis is claim/obligation-by-source evidence work, including counterexamples and consequential assumptions. It is not validated by the generic critic's failure. Extraction repair, entity joins, memory associations and adaptive orchestration remain additional hypotheses in the [application portfolio](../typed-judgments.md#angles-worth-testing). A matched Python implementation might do equally well. Native availability is not an RLM moat.

## Build identities must not be conflated

- **Live useful-work study:** frozen native source `d9922a7`, two real typed requests and three real generative calls. Its outputs were not edited or rerun to seek a better score.
- **Final source acceptance:** `ed0403baea72d0f2656e405a2e7454dd4393f24e`, reconciled on released v0.1.17. Subsequent integer-usage hardening and integration repairs were tested offline and through real local CLI/install boundaries, not by repeating the live study.
- **Historical prototype:** its retained pre-native binary and stopped live receipts were replayed separately. That acceptance explicitly reports no native `judge_many`; it is not evidence about the current native interface.

The [machine-readable acceptance receipt](../../bench/jev/usefulness/results/acceptance-20260916.json) binds these identities, commands, outcomes and log digests. Full local logs remain under the agent scratch directory `jev-final-source-acceptance-20260916-2225`. These records do not attest provider weights or billing.

## Requirements mapped to observed behavior

| Requirement | Exercised path | Observed result and limit |
|---|---|---|
| Use TypeSafe skill and actual documented primitives | Installed project-local `.agents/skills/typesafe-ai`; native typed request/response validation; retained live bodies | Noul and Choice executed live. Score validation exercised offline. No claim all primitives were tested live. |
| Optional, no forced vendor dependency | Default-feature and feature-enabled `tests/judge_native.rs` through actual `start`, `exec`, `final`, `kill` | Disabled calls reject before transport, ordinary execution recovers and variables persist. Missing feature/key fail explicitly. Existing `llm` remains available. The typed transport currently implements TypeSafe only, not a multi-vendor plugin system. |
| Preserve distributions and disagreement rather than enforce semantic verdicts | Live returned dictionaries, cross-`exec` equality, typed validation tests | Alternatives and probabilities retained, exact repeated requests cached, no semantic confidence filter. This is not evidence of calibration or correctness. |
| Host-owned credentials and bounded execution | Native CLI synthetic environment-isolation check, runtime malformed-schema/deadline/budget/overflow tests | Custom generative subprocess receives neither configured nor default judge key. Invalid responses and budget crossings do not yield accepted answers. Boundary tests use injected transport, not hostile live services. |
| Produce genuinely useful final work | Actual native lifecycle over seven source-backed developer tasks, common draft and two review arms | All arms met 32/32 mechanical facts. Both blinded model reviewers tied every arm, despite different absolute rubric interpretations. No final-answer quality gain. These were not human reviews. |
| Test retrieval as one application, not the whole product | Real Jev scores versus fixed BM25, same 16 candidates and top-4 size | Required evidence groups 2/4 to 4/4 on one query. Weak baseline and no shortlist-conditioned answer comparison. No general search claim. |
| Test the claimed RLM advantage | Provider-free same-plan Python/Monty comparison, independent pair oracle, residual and accepted-error witnesses | Matched Python also used 16 semantic questions. One wrong unary feature caused 96 wrong pairs. Exact joining does not repair semantic error. Automatic planning or RLM superiority was not established. |
| Keep progressive stop bars and old failures visible | Frozen failed pilots, historical public audit/strict commands, closed live quality comparison | Failed receipts stay incomplete with 68 unjudged occurrences. Later successful calls do not rewrite them. No additional paid calls in final-source follow-through. Blanket answer judging was not promoted. |
| Reconcile released main without losing work | Actual Git ancestry check and 25-file byte/mode comparison | Released `origin/main` is an ancestor, 69 ahead / 0 behind at executable source commit. All original files preserved, old main archived. No push or user-install mutation. |
| Preserve real installed Claude workflow | `tests/claude_profile_hooks.rs` installs in isolated profiles and executes registered shell hook commands | Literal skill wrapper and captured Skill PreToolUse sequence work without nonexistent PostToolUse Skill. Success/failure release the prompt. Same-clock profile collision regression fixed. This is event replay, not a fresh live Claude Code host session. |
| Preserve managed handoff, packaging and bounded instructions | Whole final-source E2E/main/package tests | Released handoff test restored intact, actual workflow passed. Rendered skill size bounds pass without raising them. Package allowlist includes `src/judge.rs`. |
| Exercise an actual installed candidate | Real final-source debug build installed into isolated HOME containing spaces, then explicit installed-memory tests | Installed bytes equal source binary. Cross-home relocation/handoff and corrupt/disabled storage behavior passed. Existing user HOME untouched. This is not a published artifact. |
| Check the whole result, including nonhappy paths | Final all-target/all-feature Cargo command, separate default-feature native paths, strict Clippy and rustfmt | **Full suite is not green:** 659 passed, 1 failed, 5 ignored. Default-feature scoped suite 294 passed, 1 ignored. Lint/format passed. The one failure is the publication gate below. |

## What the full run caught and repaired

The broad run exposed failures that earlier library-only and focused checks missed: oversized installed skill instructions, stale rendered-profile digests, a commented-out stale handoff test body, and a package allowlist missing the new module. The repairs retained the original instruction size limits, restored the complete released handoff assertion sequence, and added only the actually shipped module to the allowlist. The full command was then rerun over the repaired source:

```sh
cargo test --locked --offline --all-targets --all-features --no-fail-fast
```

The 659/1/5 result includes the user's unchanged untracked `tests/memory_recall_precision.rs`. It is a working-tree count, not necessarily the exact count in a fresh checkout. Two of the five ignored installed-artifact tests were then explicitly executed against the actual private install and both passed. The remaining exclusions were the release-only 16M-character stress test, release-only 50 MiB acceptance and frozen Luna input preparation. Final-source release-mode acceptance is not claimed. All runtime evidence here is macOS ARM64, not Windows runtime acceptance.

## Unwaived publication blocker

`current_notice_front_matter_tracks_canonical_version_targets_and_table_membership` failed. Running the actual `python3 release/verify-third-party-notices.py` also exited 1: the historical notice binds lockfile `4e2419ea…`, while the current lockfile is `2667713c…`. The optional HTTP dependency closure has not received a fresh notice audit.

**Publication is not cleared.** The old notice was not relabeled, its binding was not changed to manufacture a pass, and the failing gate was not weakened. Local integration and native usability are demonstrated within the limits above. Release readiness, representative quality improvement and the broader application advantage are not.

This closes the bounded experiment with an observed negative quality decision and an explicit release blocker, not with a claim that more green tests prove useful AI work. A later efficacy study needs held-out real tasks, strong matched baselines and final-work scoring. It must not reuse the discovered privacy omission as a gold-targeted demonstration.
