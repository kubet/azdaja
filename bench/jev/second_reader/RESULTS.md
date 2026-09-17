# Second-reader follow-through: observed results, 2026-09-17

## Decision

The strongest new result is **disagreement-only escalation on the fixed row645 development panel**: one blind four-record adjudication raised accuracy from **220/227 to 222/227**. The five shared errors remained. This supports testing a second-reader routing policy, not treating agreement or a Jev probability as approval.

The full row651 run completed all **17,469 occurrences** through the actual native Azdaja CLI, but returned **9,245 versus official 8,638**. It did not replicate exact-count success. The three-phrasing majority also did not improve the original panel. No README claim, provider defect report, production policy change, release, push, or user-install change was made.

## Every requested experiment

| Request | Concrete observed result | Interpretation and evidence |
|---|---|---|
| Diagnose the rejected probability batch | Historical evidence contains **one failed 25-question request**, with 3–4 options per question. Original raw body was not retained. Three fresh captures under a separate campaign seal all passed the unchanged native validator. | Not 25 proven invalid distributions, not a 255-option rounding case. New residuals were at most one f64 ULP, below the existing 1e-6 tolerance. Historical cause remains unresolved. No old missing rows were filled. `diagnostic/NEW-EVIDENCE.md`, `results/diagnostic-20260917/`. |
| Inspect five shared false positives | All five exact texts and source hashes reviewed. `r1747` reads as an anti-scam warning. Four others depend on missing relationship, notification or subscription context. | One plausible annotation-noise candidate, not five proven gold errors. Missing consent is not evidence of nonconsent. Official labels unchanged. Agent review, not independent human adjudication. `review/REVIEW.md`. |
| Full row651, once | **17,469/17,469 observed**, 112 requests, count **9,245**, sum(p) **9,287.38**, gold **8,638**. **210.013 seconds** end to end, median native request **1.247 seconds**. | Exact task failed by **+607**. Sum(p) overshot by **649.38**. No item-level full-row labels were collected, so no per-item accuracy or calibration claim. `results/row651-replay.json`. |
| Disagreement-only adjudication | Original models each scored **220/227**. Their four differing records were selected without gold. One fresh blind generative call classified all four correctly, giving **222/227** overall. | Actual narrow gain of two correct records. The **five shared errors** remain untouched. Same generative model, not an independent oracle. Call: **2.990 seconds**, **1,418 input / 33 output tokens**. `results/policy-replay.json`. |
| Three question phrasings | Fresh v0/v1/v2 scored **219/227, 220/227, 220/227**. Majority **219/227**. Unanimous on **225/227**, still **six errors**. | No majority gain. Only `r0044` and `r0282` changed votes across wordings. New v0 also differs from the original call in batch composition, so drift cannot be attributed solely to wording. All variants retained, none selected post hoc. `results/policy-replay.json`. |
| Calibration receipt | Original row645 **Brier 0.0259868**. Positive-probability ECE using predeclared 5 and 10 bins: **0.0676652**. Original sum(p) **138.02**, official ham **132**. | Descriptive known-panel calibration, not a safety certificate or a first-in-the-world claim. Top-label ECE is separately reported: 0.0366520 / 0.0502203. `review/metrics.json`. |

All six requested investigations have retained observations. Unrecoverable historical probability-body attribution is explicitly unresolved rather than silently marked diagnosed.

## Speed, bytes, tokens and money

| New phase | TypeSafe requests / questions | Reported input / output tokens | Time | Input-price estimate |
|---|---:|---:|---|---:|
| Probability diagnostics | 3 / 75 | 26,898 / 3,735 | Instrumented diagnostic, not a speed comparison | $0.001129716 |
| Full row651 | 112 / 17,469 | 2,749,030 / 357,302 | 210.013 s whole workflow | $0.115459260 |
| Three phrasings | 11 / 681 | 73,841 / 15,026 | 12.913 s summed typed-call time | $0.003101322 |
| **Total new typed work** | **126 / 18,225** | **2,849,769 / 376,063** | Separate phases, not one matched workload | **$0.119690298** |

The policy workflow including blind adjudication, typed calls and lifecycle took **20.261 seconds**. The one adjudication used **one logical call and one entered transport turn**, with **1,418 input / 33 output tokens**. Its dollar price was not established.

Dollar figures are **reported input tokens × documented $0.042/M**, not invoice totals. Output tokens are recorded, not silently discarded. No matched full-row generative baseline was run, so this does not establish a full-row speedup or a 1000× dollar ratio.

The dataset calls row651 a 1,048,576-context fixture. Its actual retained source is **2,693,859 UTF-8 bytes**. Repeated question text and JSON produced **9,989,933 request bytes** and **2,749,030 reported input tokens**. The observed result is 112 requests and about 210 seconds, not the speculative 40 requests / 30 seconds / $0.015 forecast. Bytes/3 and bytes/4 were only preflight estimates, not tokenizer bounds.

## What Azdaja actually contributed

The unchanged, feature-enabled native binary ran `start → load → exec judge_many → final → persistent reentry → deterministic reduction → kill`. Source occurrences were parsed and packed by authored code, with ID-bound typed leaves and exact downstream accounting. All 112 responses reentered the same persistent evaluator. No source occurrence was dropped or deduplicated. The final count was reduced inside Azdaja, not invented in a prose answer.

This demonstrates a working typed-worker execution path beside `llm`. It does **not** demonstrate automatic planning, autonomous decomposition, exclusive RLM efficiency, or superiority to a matched Python controller. The useful tested policy is: retain both readings, preserve agreement errors as possible errors, and spend reasoning on the disagreement set. That policy remains optional and unshipped.

The source-order ledger and contiguous pack membership are preserved. Canonical JSON object keys are lexicographic, so a boundary pack lists `r10000` before `r9913`. Binding is by ID, never position.

## Acceptance and boundary checks

| Requirement / changed output | Concrete check and observed behavior |
|---|---|
| Exact full-source coverage, no month filter or dedup | `row651/test_prepare.py` and `large_run.packs()` validate all 17,469 byte spans, source hash, unique occurrence IDs, contiguous pack membership and the 112 caps. Duplicate preservation also tested with a synthetic duplicate occurrence. |
| Actual public native path, not only mocks | `results/row651-offline-20260917/receipt.json`: all 112 loads and canonical hashes passed with **zero provider requests**. An explicitly synthetic 17,469-row reduction also ran inside real Monty. Live receipt separately records all 112 actual responses and native final reduction. |
| No fake live completion | `test_large_run.py` proves the live branch invokes typed execution. Budget-crossing usage is preserved, failure poisons the controller, invalid probabilities and request swaps cannot enter reentry. Real live receipt contains 112 confirmed requests, not a renamed offline result. |
| Original task and blind escalation | `test_policy_study.py` compares v0/adjudication instructions byte-for-byte with the original gate questions. Actual prompt contains only four raw records and questions, with no gold or earlier predictions. Strict disjoint agreement/fresh coverage is tested. |
| All phrasings, no winning-arm selection | Same source state, 681 exact IDs across 11 requests, all three variants graded. Unanimity retains its six residual errors. Missing variants and non-boolean gold are rejected. |
| Reproducible reported quality, speed and usage | `replay_large.py` and `replay_policy.py` check sealed source hashes, actual source/request equality, typed response identities, all IDs, native usage, trace identity and reductions. Eight real-receipt-copy mutation tests reject fake wins, missing packs, source replacement, impossible speed, boolean probabilities and adjudication gold injection. |
| No changed historical results or diagnostic repair | Earlier closed receipts remain untouched. Three new diagnostic captures are explicitly ungraded. Production `src/judge.rs` retains SHA256 `0707a24c0a86426f51277e72e1d61e37482864c8d67b1b0ed10c5d5071c7bf39`. |
| User credential and install custody | Actual public `jev detach` removed only the experimental attachment. Only the recorded experimental broker was stopped. Temporary OAuth copy, private runtime and work directories were removed. User key/OAuth bytes and modes unchanged, 825 study files exact-secret scanned. `results/private-cleanup.json`. |

**49 scoped tests passed** after the final live studies, including real-receipt mutation checks. These do not substitute for the separately observed live public workflows. Frozen binary SHA256: `13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32`.

Initial discarded worker scaffolding and preflight defects were repaired **before** the respective live seals. The large-run preflight caught the missing live branch and clarified canonical ordering. Policy preparation corrected an impossible full-panel grading contract and restored exact old wording. The original diagnostic setup failure was provably zero-call and is retained separately. No batch was retried within either new quality run. The separate diagnostic campaign reused the old request only to investigate transport validation, not to repair its grade.

## Offline replay

From this repository, with the retained source files and the exact local binary path recorded in each receipt available:

```sh
python3 -B -m bench.jev.second_reader.replay_large bench/jev/second_reader/results/row651-live-20260917
python3 -B -m bench.jev.second_reader.replay_policy bench/jev/second_reader/results/policy-live-20260917
python3 -B -m unittest bench.jev.second_reader.test_replays -v
```

These commands do not infer or read credentials. Replays establish local artifact consistency, not cryptographic provider authentication. Original absolute source/binary inventory paths are intentionally checked and must be available. Raw diagnostic sidecars remain local, owner-only evidence. No external failure report was sent because no new invalid provider body was captured.
