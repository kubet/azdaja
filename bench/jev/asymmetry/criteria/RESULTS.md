# Separated criteria and inverse-question result

One preregistered development-panel intervention completed. No row651 provider calls were made by this experiment. Neither the explicit criteria nor the inverse question improved item error count over the fresh control. Agreement rejected a few cases but retained six shared false positives.

## Exact measured outcome

All 227 row645 May occurrences, including duplicates, were judged under all three framings in separate requests. Official target: 132 ham. Each arm had four requests with identical per-block source state. Order rotated across blocks. All decisions below use the frozen .5 rule, not the independently trained .74 transfer threshold.

| Policy | FP | FN | Unresolved | Judged | Ham decisions | Sum ham probability |
|---|---:|---:|---:|---:|---:|---:|
| Fresh original control | 7 | 0 | 0 | 227 | 139 | 138.35 |
| Explicit ham true/false criteria | 8 | 0 | 0 | 227 | 140 | 136.46 |
| Inverse spam with swapped criteria | 7 | 0 | 0 | 227 | 139 | 137.34 |
| Control + inverse agreement | 6 | 0 | 2 | 225 | 138 known | Not an estimator |
| Criteria + inverse agreement | 6 | 0 | 3 | 224 | 138 known | Not an estimator |

Explicit criteria corrected one control error but introduced two others. The inverse corrected one and introduced one. Agreement is not an approval rule: six shared wrong agreements remain. The ranges 138–140 and 138–141 describe possible decision counts from unresolved entries only, not bounds on the true ham count. The true count 132 falls outside both ranges because known decisions can be wrong.

The explicit criteria's probability sum moved closer to 132, but its thresholded labels became worse. This is one development result, not validated calibration or an estimator to apply to row651. No wording or threshold was revised after observing these outputs.

## Actual time and usage

| Arm | Requests | Input tokens | Reported output tokens | Median call seconds | Input-price estimate USD |
|---|---:|---:|---:|---:|---:|
| Control | 4 | 35,673 | 5,010 | 1.074 | 0.001498266 |
| Explicit criteria | 4 | 54,060 | 5,010 | 1.366 | 0.002270520 |
| Inverse | 4 | 46,115 | 5,010 | 1.326 | 0.001936830 |

Total: 12 typed requests, 681 questions, 135,848 input tokens, 15,030 reported output tokens, 18.234 seconds including public lifecycle and cleanup. The total input-price estimate is $0.005705616 at the documented $0.042/M rate. Billing was not observed. Questions and added criteria consumed measured input tokens and were not free. These are native direct-HTTPS statistics, not generative model trace events. No generative call or model-trace file existed.

## Requirement-to-observation map

| Requirement | Check and observed result |
|---|---|
| Exact source and unchanged control | All 227 physical May IDs and raw lines matched the frozen source SHA. Control wording matched the historical literal. No gold was in model requests. |
| Separate framings | Twelve retained requests each contained one arm only. Per-block state hashes matched across arms. The frozen cyclic arm order was observed. |
| Optional engine via real Azdaja | Actual start/load/exec/final/reentry/reduction/kill completed. Offline preflight crossed all 681 IDs with zero calls before live admission. |
| Typed contract and provenance | All 12 bodies, request hashes, answer IDs and native `judge_stats` validated. Attempts/provider requests were 1 per cell, cache hits 0, known usage complete. All bodies matched real evaluator reentry. |
| Stop/cap discipline | Frozen 12/681/250k-input/100k-output/180s envelope respected, no retries. Mutation tests rejected completed deadline crossings, altered source, missing calls, empty rehashed inventory, and forged final reduction. A correctly failed crossing retained usage but was excluded from quality. |
| Complete reduction | Real final evaluator output observed=expected=681, complete=true, attempts=0. All 227 triplets were eligible. |
| No authority from agreement | Disagreements remained unresolved. Shared wrong agreements stayed errors. No automatic approval was enabled. |
| Privacy and cleanup | Native cleanup exit 0. Temporary attached key removed through public `jev detach`. Original persistent attachment hash and mode unchanged. Private runtime moved outside the repository. |
| Independent verification | Reviewer independently checked all 12 raw requests/stats/reentry/custody and totals, then reran the public grader to a new scratch output. Existing receipt/report hashes remained unchanged. All 24 inspected offline tests passed. |

## Reproduction and claim limits

Source/method commit `b1b9892`, pre-admission seal commit `3825af8`. Native binary SHA `13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32`. Returned model identifier `jev-1.13.0` is a provider-reported string, not a proof of immutable weights.

Canonical outputs:
- `results/native-20260917/receipt.json` and individual request/observation/reentry/custody artifacts.
- `results/grade-20260917.json` with all raw probabilities and matched errors.
- `results/timing-cost-20260917.json` with per-arm usage and timing.
- `results/native-20260917/privacy-cleanup.json`.

Run the public grader with a **new** output path:

```sh
python3 -B -m bench.jev.asymmetry.criteria.grade \
  --receipt-dir bench/jev/asymmetry/criteria/results/native-20260917 \
  --output /path/to/new-report.json
```

Frozen files, the retained binary, and source data must remain available at their recorded locations. This verifies local evidence consistency, not independent provider authenticity. Repeated message templates and post-error-inspection prompt design prevent an independent generalization claim. The experiment is closed. Do not rerun it to seek a favorable score.
