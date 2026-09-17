# Asymmetry follow-through: full matched result

## Finding

The full source-matched row651 generative comparison is complete. **Jev with the frozen row645-trained threshold made 382 item errors, versus 386 for the generative baseline, at an 18.3× lower median native-call latency.** This is similar total error on this panel, not statistical equivalence or interchangeable risk: Jev missed **135 ham records versus 5**. Default Jev made 675 errors. No production threshold or approval rule was changed.

The supported product direction is an **optional, task-calibrated second reader beside `llm`**. Azdaja retains source occurrences and raw judgments, performs exact reductions, and can expose disagreement for further reasoning. Agreement and concentrated probabilities do not establish truth. No universal replacement, automatic planner, exclusive RLM advantage, or 1000× dollar saving is established.

## Same 17,469 occurrences, same supplied source and questions

Official ham count: **8,638**. Every matrix uses all 17,469 occurrence IDs, including repeated messages. The generative arm used `gpt-5.6-sol`; the typed arm reported `jev-1.13.0`. The requests were historical and sequential, not randomized concurrent trials.

| Policy | False positives | False negatives | Total errors | Item accuracy | Ham count | Count bias |
|---|---:|---:|---:|---:|---:|---:|
| Jev, original `p >= .5` | 641 | 34 | 675 | 96.136% | 9,245 | +607 |
| Jev, frozen row645-only `p >= .74` | 247 | 135 | 382 | 97.813% | 8,750 | +112 |
| Matched generative baseline | 381 | 5 | 386 | 97.790% | 9,014 | +376 |

The `.74` threshold reduced Jev's errors by 293, but exchanged 394 fewer false positives for 101 additional false negatives relative to its `.5` policy. Against the generative arm, it produced 134 fewer false positives and 130 more false negatives. A four-error difference does not establish superiority, especially on dependent repeated-message data.

### Probability-summing did not fix the count

`sum(noul) = 9,287.38`, or **+649.38** above 8,638. This is worse than the original threshold count's +607. The previously retained Brier score is 0.028812, ECE with five bins is 0.062441, and ECE with ten bins is 0.067815. These calibration summaries do not guarantee an unbiased aggregate count. No expectation-based replacement is justified by this run.

### Threshold transfer is not a blind independent holdout

The selection used only the 227 labeled row645 May occurrences. A fixed .01 grid minimized FP+FN, with declared tie-breaking, and selected `.74` with three training errors. The freeze was committed before the transfer code read row651 probabilities. The coordinator already knew the original row651 aggregate failure.

There are zero identical full-record overlaps but **1,612 exact/normalized message overlaps** between training and the headline panel. All overlaps remain in headline scoring. On the 15,857 normalized-unseen occurrences, the retained transfer receipt shows default Jev 541 FP/34 FN, versus `.74` at 216 FP/134 FN. This is an overlap-aware descriptive transfer result, not independent generalization or a new production default.

## Time, usage, and cost

| Measurement | Jev, one retained pass | Matched generative pass |
|---|---:|---:|
| Requests / entered turns | 112 typed requests | 112 logical / 112 entered turns |
| Median native-call latency | 1.247 s | 22.8125 s |
| Median known controller-call duration | 1.478 s | 23.421 s |
| Input tokens | 2,749,030 | 2,452,510 |
| Reported output tokens | 357,302 | 189,608 |
| Whole workflow wall time | 210.013 s | 3,533.122 s, including interruption/recovery |
| Price evidence | $0.11545926 input-price estimate | Subscription marginal billing unknown |

The ratio of native medians is **18.294×**. The ratio of known controller medians is **15.846×**, with one recovered controller duration unknown. The generative native-event times sum to 2,541.001 seconds. The interrupted whole-wall comparison is disclosed, not used to pretend an uninterrupted speed benchmark.

The typed dollar figure is known input tokens multiplied by the documented $0.042 per million rate, not an observed invoice. Output usage is retained. The generative trace reports input/output/cache/reasoning fields for all 112 turns, with no unknown usage fields, zero setup attempts, and zero failed turns. Subscription dollar allocation remains unknown, so **no dollar ratio is calculable**. Questions consumed tokens. This is not a token-count reduction.

## What the 641 false positives actually look like

All 641 FP and 34 FN are retained with source hashes, byte spans and official labels in `fp_analysis/errors.jsonl`. Of the false positives, 191 had `p` in [.5,.6), 154 in [.6,.7), 130 in [.7,.8), 120 in [.8,.9), and 46 in [.9,1]. They are **not uniformly high-confidence errors**. Uncertainty-only routing can still miss the 46 high-probability false positives, and low confidence is not the only failure mode.

Exploratory source-text categories include paid-service language (274 FP among 2,446 gold-negative occurrences), delivery/transaction language (53/317), and sports language (18/69). The categories are descriptive post hoc probes, not causal explanations or tuned correction rules. All errors occur in repeated-message groups and cover 139 distinct error message texts. Gold labels were not relabeled to improve the result. See `fp_analysis/RESULTS.md` for exact tokenization and denominators.

## Criteria and inverse questions: separately executed development test

All 227 row645 May occurrences received a fresh control, explicit ham true/false criteria, and inverse-spam criteria in **separate requests**. Identical source states were used across each block's arms, and order rotated. This avoids presenting sibling framings in one request. It does not make repeated messages or model outputs independent.

| Rule | FP | FN | Unresolved | Result |
|---|---:|---:|---:|---|
| Fresh original control | 7 | 0 | 0 | Reference |
| Explicit ham criteria | 8 | 0 | 0 | Corrected one, introduced two |
| Inverse spam | 7 | 0 | 0 | Corrected one, introduced one |
| Control + inverse agreement | 6 | 0 | 2 | Six shared wrong agreements remain |
| Criteria + inverse agreement | 6 | 0 | 3 | Six shared wrong agreements remain |

All 12 requests and 681 answers passed source-bound native replay. Usage: 135,848 input / 15,030 reported output tokens, 18.234 seconds, $0.005705616 input-price estimate. Explicit criteria were not an error-count improvement. These development findings were not rerun or applied to row651 after observing them. Details and the independent check are in `criteria/RESULTS.md`.

## Does combining the two readers make approval safe?

No. This is now directly measurable on the full matched panel:

| Jev policy paired with generative baseline | Disagreements | Agreements | Shared errors among agreements |
|---|---:|---:|---:|
| Original `.5` | 551 (3.15%) | 16,918 | 255 (1.51%) |
| Transferred `.74` | 464 (2.66%) | 17,005 | 152 (0.89%) |

The disagreement set is small enough to be a plausible escalation target, but even a perfect disagreement adjudicator would leave the shared errors. No new full-row adjudicator was run. The earlier four-record row645 adjudication remains a separate narrow result. **Agreement is a routing observation, not permission to approve.**

## Actual execution and interruption custody

Both arms used the same retained native Azdaja binary, SHA256 `13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32`, through public `start → load → exec → final → persistent reentry → reduction → kill`. The generative arm's state/questions matched the original typed requests by ID and exact content. No occurrence was dropped, deduplicated, or repaired by a second model call.

The original generative controller was externally killed by a 600-second tool limit. Twenty-four ordinary results and an already-admitted 25th native result were preserved. The 25th was read through `final` with zero new model requests. An explicit amendment restored those 25 observations and admitted only untouched packs 026–112 under the original cumulative budgets and absolute deadline. The completed trace contains exactly 112 successful physical attempts, zero setup attempts, and no controller retries. This was an **interrupted, amended one-pass run**, not an uninterrupted original campaign.

The terminal receipt passed public replay with all 112 packs and 17,469 answers eligible and the actual native count reduction intact. An independent reviewer then checked every public prompt/raw answer/reentry, all 112 native trace events, prefix/suffix usage, all three confusion matrices and paired errors. A fresh public replay matched the retained 23-key report exactly. Temporary subscription credentials and the owned broker were removed after termination. The user's original authentication bytes and mode were unchanged. Original receipts, source, production binary, and study outputs remain preserved.

## Requirement-to-observation map

| User requirement | Observed check and result |
|---|---|
| Sum probabilities versus 8,638 | All 17,469 retained probabilities sum to 9,287.38. Expected-count bias is worse, not better. |
| Characterize all 641 FP | Official-label/source join covers all 641 FP and 34 FN. Exact errors, bins and repeated-message grouping retained. No selective gold changes. |
| Test explicit and inverse criteria | Actual separate-arm native run: 12 requests, 681 questions, all 227 triplets. Criteria had 8 errors versus 7 control; agreement retained six errors. |
| Threshold on row645 only, apply once | Committed training freeze selects .74. Public transfer replay checks frozen inputs, all full-record/text overlaps and unchanged headline inclusion. Result 247 FP/135 FN. |
| One matched row651 generative baseline | All 112 calls/17,469 IDs completed. Exact old typed state/questions, known usage, final Monty reduction and cleanup verified. Result 381 FP/5 FN. |
| Handle failures without hidden retries or budget reset | Immutable interrupted prefix, recovered public-final envelope, exclusive suffix seal and original deadline validated. 27 offline replay tests include false-completion, deadline, source/prompt/answer, trace/usage, marker and output mutations. Independent reviewer reproduced rejection of a forged completed 7,201-second receipt. |
| Real acceptance path rather than a synthetic quality claim | Scores come from actual terminal public-Azdaja calls and all retained raw outputs. Synthetic tests only validate rejection/accounting logic. The public replay checks source, runtime, manifests, trace and reduction together. |
| Measure quality, speed, usage and cost | Three same-ID confusion matrices, native/controller/full-wall timing separated, complete known tokens and only a documented typed input-price estimate. Subscription billing and cost ratio remain unknown. |
| Preserve optionality and do not enforce arbitrary policy | No production source/config/threshold changed by this phase. Full probabilities remain reusable. No automatic approval enabled. |
| Send TypeSafe the Choice gap and reliability curve | A five-attachment draft is prepared and hash-checked, but **not sent** because no authorized sender is configured. One old 25-question batch is missing, not 25 proven malformed responses. Original body loss prevents attribution; later captures passed unchanged validation. |

## Retained outputs and reproduction

- `comparison-20260917.json`: source-hashed quality, timing, usage and claim limits.
- `baseline/results/paired-20260917.json`: public replay, all same-ID matrices and trace accounting.
- `baseline/results/continued-20260917/`: actual terminal outputs, supervisor result and privacy cleanup.
- `threshold/transfer-result.json`, `fp_analysis/`, and `criteria/results/`: separate immutable measurements.
- `provider_report/UNSENT.eml` and `delivery-status.json`: exact draft bytes and explicit unsent status.

With retained repository data and exact binary/source inventory paths available, replay without credentials or new inference:

```sh
python3 -B -m bench.jev.asymmetry.baseline.replay \
  --receipt-dir bench/jev/asymmetry/baseline/results/continued-20260917 \
  --output /path/to/new-paired-report.json
python3 -B -m bench.jev.asymmetry.criteria.grade \
  --receipt-dir bench/jev/asymmetry/criteria/results/native-20260917 \
  --output /path/to/new-criteria-report.json
python3 -B -m bench.jev.asymmetry.threshold.transfer \
  --output bench/jev/asymmetry/threshold/transfer-result.json --replay
```

These are local artifact-consistency checks, not provider-signed authenticity proofs. The measurements are closed. No README marketing, publication, push, user-install change, new RAG/memory feature, or further inference is authorized by these results.
