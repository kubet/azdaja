# Full-row labels and three-goal follow-through

## New finding, without another inference call

The missing per-item audit was possible: the official Oolong API exposes a complete labeled row651. One public data fetch returned 5,679,258 bytes with `partial=false` and no truncated cells. Its unlabeled source matches the frozen 2,693,859-byte input exactly. All **17,469 labeled occurrences** align byte for byte, after removing only the official label suffix.

| Metric on the unchanged row651 predictions | Result |
|---|---:|
| Correct / observed | **16,794 / 17,469 (96.136%)** |
| False ham predictions | **641** |
| Missed ham predictions | **34** |
| Net count error | **641 - 34 = +607** |
| Predicted / official ham count | **9,245 / 8,638** |
| Sum of ham probabilities | **9,287.38**, or **+649.38** above gold |
| Brier score | **0.0288117923** |
| Positive-probability ECE, 5 equal-width bins | **0.0624408953** |
| Positive-probability ECE, 10 equal-width bins | **0.0678149865** |

**The full-row counting miss is now localized to official-label classification errors, not missing occurrences or the deterministic reduction.** High item accuracy coexists with a biased aggregate. This does not establish parity with a full-row generative baseline, which was not run. Official annotations can be ambiguous, and these are occurrence-weighted statistics on a public, potentially dependent dataset, not a calibration or safety guarantee.

The original runtime remains **112 requests, 210.013 seconds, 2,749,030 input / 357,302 output tokens**, with **$0.11545926** documented input-price estimate. No invoice, price ratio, new model result, corrected prompt, adjusted threshold or production approval policy was created.

`result.json` contains every occurrence ID, exact byte span, record hash, official label and original probability. Its confusion counts and all errors are reproducible, not inferred from aggregate totals. Decimal arithmetic independently reproduced Brier and both ECE values. Threshold remains **0.5**. Both fixed bin counts and empty bins are retained.

## Requirement-to-check map

The following checks were run after the final new implementation. **35 tests passed, zero skipped**. The actual public CLIs for the angle report, measurement audit and new label audit also ran independently and exited 0. See `ACCEPTANCE.json` and its four retained logs. Passing acceptance means the measurements are faithfully delivered, not that the scientific quality bars passed.

### Isolated Jev angles

| Requirement / public output | Concrete check | Observed behavior |
|---|---|---|
| Six separately reported semantic outcomes | `python3 -B -m bench.jev.angle_analysis.report --output NEW.json`, retained as `angle-public.json` | Gate 139 vs 132, cascade 138 vs 132, verifier 10/12 vs 12/12, flat 4/4 vs lossy root 1/4, historical synthetic handoff 3/4 vs 0/4, ordinary cache mechanism. Small diagnostics do not establish general application effectiveness. |
| Exact source/request matching, not a favorable unrelated baseline | `test_rehashed_unmatched_baseline_state_is_rejected`; public replay | Changed generative source rejected. Original native and generative payloads replay consistently. |
| Honest quality, usage and attempted-work accounting | `test_rehashed_false_win_is_rejected`, `test_rehashed_receipt_cannot_erase_reported_usage`, `test_actual_retained_result_is_negative_and_usage_is_complete` | False win and erased usage rejected. Ten typed requests, nine entered successful generative turns and original known/unknown usage preserved. `general_quality_advantage_established=false`. |
| No invalid/missing judgment becomes evidence | `test_rehashed_invalid_probability_is_not_a_judgment`, `test_missing_source_artifact_is_rejected` | Boolean probability and missing request rejected. |
| Delivered public CLI protects retained evidence | `test_public_cli_refuses_existing_or_dangling_output` plus the fresh normal CLI invocation | Existing output preserved, dangling target not created, normal output regenerates. Memory/RAG implementation remains cancelled. |

### Arbitrage and row651 calibration

| Requirement / public output | Concrete check | Observed behavior |
|---|---|---|
| Full-source coverage and official reference | `test_every_source_occurrence_aligns_with_exact_bytes`, `align`, actual new audit CLI | All 17,469 exact spans/hashes/IDs match. Official ham sum 8,638 matches the task. No filtering, fuzzy matching or deduplication. |
| Correct label provenance, metadata and complete source | `test_truncation_wrong_row_or_metadata_refuses`, `test_reordered_labeled_lines_refuse`, `test_changed_source_record_or_nonrecord_refuses`, `test_unlabeled_source_and_label_sum_must_match`, `test_changed_snapshot_refuses_before_any_score` | Truncation, wrong task, altered bytes, reordered labeled rows, changed snapshot and inconsistent gold all rejected. |
| Every prediction bound to its occurrence | Existing native `replay_large.replay` followed by `test_join_is_by_id_preserves_multiplicity_and_rejects_missing_extra_duplicate` | Existing 112-request trace validates before labels are joined. ID reordering is harmless. Missing, extra and duplicate IDs reject. |
| Exact count and probability sum | `test_actual_full_row_negative_result_and_usage_replays`, `test_false_native_win_rejected_even_with_matching_summary`, `test_frozen_report_recomputes_exactly_and_remains_a_count_failure` | Count 9,245 and sum 9,287.38 reproduce. Forged 8,638 success rejected. Native reduction remains zero-inference. |
| Item confusion, accuracy, Brier, bins and ECE | `metrics`, `test_metrics_match_hand_computed_endpoint_and_threshold_example`, independent Decimal recomputation in `ACCEPTANCE.json` | 641 FP / 34 FN, 16,794 correct, full error IDs and both reliability tables retained. Endpoint 1 belongs to the last bin, threshold 0.5 is positive, empty bins stay visible. |
| Malformed values never enter metrics | `test_malformed_probability_gold_duplicate_or_empty_never_scores` | Boolean/NaN/infinite/out-of-range/string probabilities, numeric gold, duplicate IDs and empty input reject. |
| Speed, request bytes, tokens and cost limits | Existing public full-row replay plus `test_impossible_wall_speed_rejected` and exact replay/result equality | 210.013 s, 9,989,933 request bytes, 2,749,030 input / 357,302 output tokens. Impossible speed rejects. Cost is input-price estimate only, no matched generative full-row baseline. |
| Reusable public audit with no overwrite or model admission | `test_actual_public_audit_and_safe_output_refusals`, independently invoked new CLI | Public output equals retained result. Existing/symlink destinations refuse. **Zero new inference requests**. One separately recorded public dataset request. |

### Requested measurement rerun

| Requirement / public output | Concrete check | Observed behavior |
|---|---|---|
| Find the alleged seven extra records on row645 | Official row645 alignment tests plus fresh `bench.jev.measurement_audit` | All 2,177 source occurrences align. The 227-May panel has seven label FPs in each arm, zero FNs, five shared errors. Equal 139 totals did not imply an upstream counting bug or identical error sets. |
| Probability sum versus gold, without a tuned rerun | Existing row645 audit and retained summary equality | Sum 138.02 vs 132 and Brier 0.0259868 preserved. All earlier IDs/probabilities unchanged. |
| Raw-window flat selection at declared n=100 | `test_actual_full_replay_is_negative_but_consistent`, source/fixture freeze checks, `measurement-public.json` | 100 attempted, 75 valid typed, 25 still unjudged. Matched result67/75 for both arms. **The 100-valid-case target remains unmet.** No failed batch was retried to fill it. |
| Asymmetric verifier n=200 with false-support measurement | Fresh public measurement audit and combined report recomputation | Both arms 200 observed. Typed 179/200 versus generative 180/200. False support 15/100 versus 14/100 on unsupported claims. No approval policy shipped. |
| No hidden attempts, missing calls or rewritten bar | `test_missing_completed_call_is_rejected`, `test_changed_bar_cannot_become_a_rehashed_win`; public receipt replay | Missing call and forged win rejected. Original failed batch retained, repeated attempted pairs 0, 275 valid typed judgments from 300 questions, unknown failed-output usage preserved. |
| Hash-bound public receipts with safe destinations | `test_public_audit_fresh_output_and_refusal_paths` plus independent normal CLI run | New output passes, overwrite/symlink refuse. `all_quality_bars_passed=false`. These are native research receipts, not a claimed published RAH leaderboard row. |

## Replay and provenance

```sh
python3 -B -m bench.jev.row651_labels.audit --output NEW.json
python3 -B -m unittest bench.jev.row651_labels.test_audit -v
```

The audit uses the existing native replay, which requires the retained source/binary inventory paths recorded in the original receipt. It does not read credentials or invoke a provider. Local artifact consistency is not cryptographic provider authentication.

Official source: [oolongbench/oolong-synth validation row651](https://datasets-server.huggingface.co/rows?dataset=oolongbench%2Foolong-synth&config=default&split=validation&offset=651&length=1). Source paper: [Oolong: Evaluating Long Context Reasoning and Aggregation Capabilities](https://arxiv.org/abs/2511.02817), Bertsch, Pratapa, Mitamura, Neubig and Gormley. The unchanged API response is `official-row651.json`, SHA256 `469a5de6ca9b3e274837b5aba129e83e33e8ed1961a5a659521640fd33547f8c`. `fetch.json` records the sole public data request. Upstream data attribution and licensing are not replaced by the repository's software license.

This addendum supersedes only the earlier **absence of full-row per-item analysis**. The frozen native result, prior negative exact-count bar, original 25 missing Choice judgments, earlier reports and all model input/output bytes are untouched. Production source, package inputs and user credentials/install were not changed. No new memory/RAG work, README claim, external provider report, push or publication occurred.
