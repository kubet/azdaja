# Jev public-contract traceability and integration observations

**This is a complete mapping, not a claim that every desired outcome succeeded.** Eleven explicit requirements and 62 named native API/configuration/output entries are bound to checks in the [machine-readable map](../../bench/jev/usefulness/results/public-contract-map-20260916.json). The research command outputs are mapped separately below. The map records test names, actual results, executed REPL programs and binary/source identities. It deliberately sets `all_requirements_satisfied: false` and `publication_cleared: false`.

## Additional actual public-interface observations

A single provider-free chain executed successfully:

```text
fresh retrieve.py output
  → evaluate.py checks exact query/candidate identity and coverage
  → actual installed Azdaja start/load/exec/final
  → seven top-8 selections materialized by stable source IDs
  → another exec/final reuses retained source and observations
  → kill
```

All seven selections matched the fresh ranker output. All 16 source records remained available. Q1's eight selected records matched the original source records exactly and covered its four authored evidence groups. Another session retained all **seven Choice distributions and sixteen Noul answers** from the prior live study, with every observation field unchanged after re-entry. The current engine reported **zero new provider requests**. These are real public CLI/data-boundary checks, not fresh inference, autonomous planning or answer-quality validation.

The installed executable is the private all-feature source build `ed0403b`, SHA-256 `0aefe8e6…`, not a newly published release. Runtime source is unchanged at the checked worktree `c36d88d`. The public native CLI tests were rerun in both feature modes, 5/5 each. The engine contract tests were rerun with injected transport, 15/15 without the feature and 14/14 with it. No real credential was read in this follow-up.

## Evidence levels and check identifiers

- **N1–N5:** the five named tests in [`tests/judge_native.rs`](../../tests/judge_native.rs). N4 is a direct TOML/config roundtrip. The others execute the actual public binary, including the real local custom-generative subprocess boundary.
- **U1–U15:** named engine tests in [`src/judge.rs`](../../src/judge.rs), listed in the JSON map. These use private injected transport/credential seams and do not test live service accuracy.
- **P1:** full disabled `judge_stats` schema and explicit refusal through the installed CLI.
- **P2/P3:** exact evidence materialization and persistent re-entry through that CLI.
- **P4:** actual host key-variable selection. A missing named variable produced `credential unavailable` despite an invalid synthetic default token. An invalid synthetic token in the named variable produced `invalid credential syntax`. Both had zero attempts and no silent default-key fallback.
- **P5:** ordinary execution after those failures returned 42, with zero provider requests.
- **D1:** independently recomputed request digests and all metadata fields in retained live observations, plus the actual full-distribution re-entry above.
- **C1:** the complete fresh-retrieval-to-installed-REPL chain above.
- **L1:** the unchanged live study at source `d9922a7`. Two typed requests, 23 questions and three generative calls. This is the only live native quality study, not a rerun on current source.
- **S1:** inspection and compilation of the production HTTP policy, not a hostile live HTTP-server test.

## Every explicit requirement

| Requirement | Concrete check and observed result |
|---|---|
| Install one TypeSafe skill method and use it | Original non-Claude installer receipt reported one installed skill. Project-local `.agents/skills/typesafe-ai/SKILL.md` was loaded and reread. The current [HTTP API reference](https://docs.typesafe.ai/api.md) was reread on 2026-09-16. No second installation method was used. |
| Deep research and falsifiable design | [Primary evidence](jev-primary-evidence-20260916.md) and [engine design](jev-engine-design-20260916.md) distinguish vendor claims, prior semantic-operator systems and actual experiments. The matched Python mechanism also used 16 questions, so operator presence does not prove an RLM advantage. |
| Optional engine alongside `llm`, not mandatory reranking | N1–N5, P1/P4/P5 and L1. Default-off behavior, explicit build/config opt-in, named calls and ordinary execution/child-provider isolation passed. The typed transport currently supports TypeSafe only. Ordinary use does not require that vendor. |
| Supply the key safely from the host | U6/U11/U14, N5 and P4. Preflight precedes credential access, known-key leakage cases reject, errors are sanitized, the configured key is not forwarded to the custom generative child. This is not comprehensive private-data detection or malicious same-user containment. |
| Preserve alternatives and entropy | U1/U4, D1 and P2/P3. Complete distributions survived cache/re-entry unchanged and complete selected-corpus source remained available. No confidence cutoff, automatic truth promotion or hidden evidence deletion was added. Calibration is unproved. |
| Hard progressive tests and stop bars | Frozen failed pilots remain stopped. U3–U13 reject malformed answers, enforce the tested resource boundaries, retain known usage and stop the cell after provider failure. The bounded live study was not repeated to seek a better score. |
| Demonstrate useful final work | L1 and the retained blinded reviews: no final-answer improvement over ordinary self-review, with the same material privacy omission. Both reviewers were models, not humans. This desired positive outcome was **not reached**. |
| Investigate reranking and other angles | The [portfolio](../typed-judgments.md#angles-worth-testing), mechanism tests and [lexical counterfactual](../../bench/jev/usefulness/counterfactual/README.md) are retained. Q1's top-4 signal survived these specific controls, but wider normalized lexical retrieval covered all authored groups on all seven tasks. Other-angle efficacy and automatic orchestration remain hypotheses. |
| Thirty-minute active-work reassessment | Session-owned create/cancel records show 30-minute reminders for active follow-ups, canceled when the bounded work ends. They are not a permanent unattended campaign. |
| Reconcile v0.1.17 safely | Released main is an ancestor, the original 25 file contents/modes were preserved, and actual installed Claude command/event replay passed. No push or user-install mutation. A fresh live Claude host session was not run. |
| Validate public interfaces and boundaries | N1–N5, P1–P5, D1 and C1 provide actual binary/CLI observations. Full project acceptance still has the explicitly retained notice failure described below. |

## Public interface and configuration inventory

The JSON map lists every field separately. The compact table groups related fields without hiding untested efficacy.

| Public surface | Checks | Observed behavior |
|---|---|---|
| Cargo `typesafe` feature, TOML `[judge]`, `JudgeConfig::default/validate` | U14/U15, N1/N3/N4, P1/P4 | Both build modes exercised. Default disabled, typed transport unavailable without feature, zero-valued limits rejected, TOML roundtrip passed. |
| `JudgeEngine::new/evaluate/stats/set_deadline` | U1/U6/U12/U13/U14, N1/N3 | Constructor gating, typed evaluation and accounting exercised. Deadline can tighten, not extend. |
| `judge_many(state, questions)` positional/named arguments | N1/N2/N3, P4, L1 | Missing, duplicate, extra and non-JSON arguments rejected. Named valid shape reached explicit missing-key/feature preflight, not a fallback. Live positional calls succeeded in L1. |
| `judge_stats()` | N1/N2, P1/P4/P5 | Exact zero-activity schema checked through actual CLI. Arguments rejected. Ordinary execution recovers. |
| Request `state`, `questions`, question ID/type/instructions/criteria | U1/U2/U3/U4/U6, N2/N3, L1 | Supported string/object/array state and documented primitive shapes checked by validation and representative executions. Exact answer-ID coverage enforced. This is not a claim every possible prompt form was tried live. |
| Config `enabled` | U6/U15, N1/N4, P1/P4 | Explicit enable required, before transport. |
| Config `model`, `expected_model` | U2/U3, L1 | Alias/concrete strings retained. Explicit expectation mismatch poisons the cell. A returned string is not immutable backend weights or authenticated alias mapping. |
| Config `key_env` | N4/N5, P4, U11 | Named environment selection and no-default-key-fallback witnessed without a valid credential. |
| Config `timeout_secs` | U12/U13/U15 | Remaining cell deadline caps request timeout. Late responses are rejected while known usage remains. |
| Config `max_requests_per_cell`, `max_questions_per_cell` | U6/U10/U15 | New calls/questions bounded. Exact cache reuse does not spend another request/question allowance. |
| Config `max_request_bytes`, `max_response_bytes` | U6/U15, S1 | Oversized requests refuse before credentials; oversized injected responses fail and poison. Production body read is bounded in source. |
| Config `max_input_tokens_per_cell` | U5/U8/U9/U15 | Integer accounting, crossing and overflow cases checked. Crossing usage remains known, answer withheld. Unknown usage is not free or a guaranteed dollar cap. |

## Every returned field

| Returned surface | Checks | Observed behavior and limit |
|---|---|---|
| Envelope `model`, `answers`, `usage`, `_azdaja` | U1/U2/U3/U5/U7/U8/U9, D1 | Exact domains/shapes validated. Missing usage becomes explicitly unknown. Envelope/metadata preserved in real re-entry. |
| Noul `type`, `noul` | U1/U3/U4, L1/D1 | Numeric probability retained. Out-of-domain/type cases reject. Sixteen retained real answers survived current REPL re-entry. |
| Choice `type`, `choice`, `probabilities`, `confidence` | U1/U3/U4, L1/D1 | Full option map retained; numeric domain, sum and argmax checked. Seven real distributions survived current re-entry. Confidence is provider-supplied, not verified correctness. |
| Score `type`, `score`, `legend`, `probabilities`, `confidence` | U1/U3/U4 | Literal injected response preserves the full ordered legend/distribution and weighted score. Invalid legend/weight/domain cases reject. **Score was not live-tested.** |
| `_azdaja.request_sha256` | U1, D1 | Both live request digests independently recomputed from exact serialized request data and matched. Instruction mutation changes identity in U1. |
| `_azdaja.cache_hit`, `provider_requests_this_call` | U1, D1 | First observation false/1, exact reuse true/0. Cache hits are not new independent evidence. |
| `_azdaja.elapsed_ms` | D1 | Both original and cached retained values were nonnegative integers. This is local call elapsed time, not a latency distribution or model-only latency guarantee. |
| `_azdaja.original_usage`, `usage_semantics`, `new_request_usage` | U1/U7, D1 | Original usage retained; cache hit reports no new request usage. The original and cached semantic labels matched their actual roles. |
| `_azdaja.model_semantics`, `billing` | U7, D1 | Explicitly provider-reported identity and `not_inferred` billing. No pricing saving asserted. |
| Stats `enabled`, `poisoned`, `transport_available` | P1/P4, U3/U11/U13/U14 | Exact current CLI defaults observed. Post-attempt failures poison in unit seams; feature absence refuses. |
| Stats `provider_requests`, `attempts`, `questions` | P1/P4, U1/U5/U10 | Actual preflight zero counters and injected/retained live activity counters checked. No retry is hidden as a cache hit. |
| Stats `cache_hits`, `cached_requests` | P1, U1/U3/U10 | Zero initially; exact reuse increments hits without another observation. Invalid responses do not populate the cache. |
| Stats `known_input_tokens`, `unknown_input_usage_requests`, `input_usage_complete`, `billing` | P1/P4, U5/U7/U8/U9/U13 | Zero/known/unknown/crossing/overflow paths checked. `input_usage_complete` describes accounting availability, not completeness of evidence or answers. Billing remains uninferred. |

**Lifetime limit:** cache and budgets are per cell, not session-wide spending control. Saved variables persist. Failure accounting must be captured in the same cell if needed; a later `exec` starts a new engine. No automatic planner, global cache or resumable transaction scheduler is claimed.

**Transport evidence limit:** S1 inspected fixed HTTPS origin, no proxy, no redirects, no automatic retries, bounded reads and timeout configuration. U11/U15 inject failure/status cases. Native hostile HTTP-server behavior was not exercised live, and the earlier Python-adapter transport tests must not be relabeled as native Rust transport tests.

## Research commands, artifacts and documentation outputs

| Changed public output | Concrete check and observed result |
|---|---|
| `counterfactual/retrieve.py` CLI and `rankings.json` | The actual CLI ran to a fresh path, then a second run refused overwrite with exit 2. Twenty focused tests include input schemas, IDs, query tokenization, passage scores, MMR ties and output preflight. Independent public-command replay matched all method/task rankings and input/implementation/question digests, excluding variable timing. |
| Ranker `schema_version`, `source_only`, `inputs`, `implementation`, `methods`, `timing`, task IDs/questions/hashes/full rankings | Version 2/source-only true, exact file/code/plan hashes and all 16 candidates per method/task were observed. Timing is one local run, not service performance. All seven full rankings feed C1 by ID, not position. These are dataset-local research commands, not a production search-service claim. |
| `counterfactual/evaluate.py` CLI and `evaluation-results.json` | Actual evaluator ran on fresh ranker output. Per-task/method/k selected IDs, covered/total/missing groups, fractions, completeness and UTF-8 selected-text bytes matched retained results. Literal independent OR-group/macro/byte checks passed. Query/method/candidate mismatches reject, including a changed original-reference order. |
| Aggregate coverage and missing Jev/answer measurements | All lexical methods at top-4 had 13/18 groups and 3/7 complete tasks. Normalized/passage top-8 had 18/18 and 7/7. Only Q1 has retained Jev retrieval measurements. Other Jev task rows and shortlist-conditioned answer quality are explicitly unmeasured, not zero or assumed successes. |
| Counterfactual `verification.json` and README | Actual documented commands reproduced the observations and refused existing outputs. Source hashes, links and the corrected distinction between 27,296 corpus-file bytes and 19,635 item-text bytes were checked. The initial invalid draft remains labeled unscored. |
| Counterfactual-to-native integration | C1 executed fresh retrieval, evaluation, actual installed `load/exec/final`, state re-entry and cleanup in one chain. All seven selections, selected original source records, the 16-source pool and retained observation matched. Zero new provider requests, no fresh answer-quality claim. |
| Native guide and installed skill awareness | Real private installation retained native awareness. Source-rendered profile size/golden checks and the released literal wrapper/event paths passed in the prior whole-source run. The guide distinguishes per-cell accounting, provider-reported identity and development source from published assets. |
| Research, live-result, independent-review and acceptance documents/receipts | Each is scoped to its recorded source or binary, with original failures retained. Live model outputs are unchanged. Primary quality remains a tie, old strict pilots remain stopped, and the current public map explicitly distinguishes injected tests, live evidence, actual local workflows, source inspection and unproved hypotheses. |

## Whole-result acceptance remains honestly qualified

**2026-09-17 follow-up:** [The bounded notice audit](../release/jev-notice-followthrough-20260917.md) distinguishes the Rust test's stale candidate-version failure from the separate verifier's lock-hash failure. It confirms 191 unchanged default source records and 51 additional optional-feature closure records, and identifies four historical line-ending byte-fidelity discrepancies. Neither the notice nor its gate was relaxed. This is additional blocker diagnosis, not publication clearance or answer-quality evidence.

The full unchanged executable-source suite observed **659 passed, 1 failed, 5 ignored**. The one failure is `current_notice_front_matter_tracks_canonical_version_targets_and_table_membership`. The actual notice verifier also rejected the historical notice/current-lock mismatch. A fresh optional-feature dependency notice audit remains outstanding. Two ignored installed-artifact tests were explicitly run afterward against the private installed candidate and passed. Release-only stress/50 MiB and fresh live host claims remain outside the verified result.

The [earlier acceptance map](jev-native-acceptance-20260916.md) and [counterfactual verification](../../bench/jev/usefulness/counterfactual/verification.json) remain unchanged. The new observations close the current public data/configuration integration checks. They do not turn the negative final-answer result into a positive one, clear publication or establish the untested application angles.
