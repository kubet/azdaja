# Real native workflow result, 2026-09-16

## Decision

**Keep the optional typed engine. Do not add blanket answer judging as a default policy.** On this small run, semantic ranking selected more of the required evidence, but feeding broad answer-quality distributions to the final reviewer did not improve the developer answers. Preserving distributions avoided information loss; it did not ensure that the questions exposed the right omission or that the reviewer acted on uncertainty.

The practical angle to pursue is **targeted evidence operations chosen inside the RLM**, with exact code and retained source around them. It is not an established RLM moat, automatic planner, or demonstrated improvement across all proposed applications.

## What actually ran

Frozen native source commit `d9922a7`, with the binary SHA-256 in [receipt.json](results/native-20260916/receipt.json). Corpus: 16 exact public tracked excerpts, 27,296 bytes, source revision `d851113`. Seven actual developer decision questions. The root used requested and observed `gpt-5.6-sol` through the OpenAI subscription route. TypeSafe returned **`jev-1.13.0`** for both requests to the requested `jev-latest` alias.

- Actual `start → load → exec → final → kill` CLI lifecycle.
- Three real generative calls: common draft, self-review, distribution-informed review.
- Two real native TypeSafe HTTP requests, 23 questions: seven `choice` answer reviews and sixteen `noul` retrieval scores.
- Every exact repeated request reused a cached typed observation. Both observation dictionaries survived a later `exec` and compared equal without new inference.
- All returned alternatives and probabilities were retained. No semantic confidence cutoff discarded tasks or evidence.
- Temporary credential file was removed after the bounded run. No real credential was written into repository artifacts or model inputs.

Historical stopped pilots remain unchanged: their zero validated judgments and unknown billing are not rewritten by this new study.

## Final work quality, not confidence

| Measure | Draft | Ordinary self-review | Jev-informed review |
|---|---:|---:|---:|
| Requested structured facts | 32/32 | 32/32 | 32/32 |
| Required source-group checks | pass | pass | pass |
| Strict frozen-checklist task success, blinded reviewer 1 | 1/7 | 1/7 | 1/7 |
| Task-sufficiency sensitivity, blinded reviewer 2 | 6/7 | 6/7 | 6/7 |

**Both independent model reviewers tied every arm.** These were model adjudications, not human assessment. Reviewer 1 applied every predeclared checklist point, including some broader than the exact task question. Reviewer 2 treated those extras as optional unless materially necessary. The strict predeclared result remains primary; the higher sensitivity score is not a replacement selected to make the result look better. Their disagreement makes the absolute success rate rubric-sensitive. Their no-improvement verdict is unchanged.

Both found the same material omission in Q2: all answers required review before destination `--apply`, but did not clearly warn that **all transitively exported context must be inspected for private authored content before sharing**. Reviewing selected IDs or reviewing the bundle after transfer is too late for that disclosure boundary. The frozen source E14 states that private paths, secrets and untrusted instructions are preserved, not scrubbed. Jev assigned the draft Q2 `adequate:0.84, incomplete:0.10, material_error:0.06`; retaining those probabilities did not make the final reviewer repair the omission.

Do not change these scored outputs retrospectively. The correct practical advice is to inspect every selected **and context** record locally and obtain sharing consent before moving the bundle, then preview/apply at the destination. This correction comes from post-run source review, not a successful Jev intervention.

Full original outputs, both blinded reviews, arm mapping and mechanical checks are retained in [the result directory](results/native-20260916/). [quality-summary.json](results/native-20260916/quality-summary.json) records both interpretations.

## Retrieval diagnostic

For the preselected Q1 query over the same 16 candidates, top-4 selection covered:

- BM25: **2/4** required evidence groups. IDs E09, E15, E14, E03.
- Native Jev Noul: **4/4**. IDs E13, E09, E14, E12.

BM25 used Unicode word tokens, `k1=1.2`, `b=0.75`, no tuned stoplist, and stable ID tie breaks. Jev received every candidate with the query and a substantive-evidence instruction. This is one query with a fixed top-4 diagnostic, not a strong search-system benchmark. No end-to-end answer was generated from only these shortlists; all answer arms had the complete corpus. Therefore this is **evidence selection improvement**, not demonstrated downstream answer improvement or a guarantee of full recall. More capable lexical/hybrid baselines remain untested.

## Observed work and latency

| Operation | Reported input tokens | Reported output tokens | Model/service latency |
|---|---:|---:|---:|
| Common draft, generative | 8,901 | 2,829 | 35.866 s |
| Ordinary self-review, generative | 10,875 | 2,524 | 32.078 s |
| Typed answer review | 13,848 | 304 | 1.199 s |
| Distribution-informed review, generative | 11,362 | 2,860 | 36.185 s |
| Typed retrieval diagnostic | 10,974 | 292 | 0.943 s |

The two TypeSafe calls reported **24,822 input tokens and 596 output tokens**, with no unknown input-usage requests. Usage is reported, not independently billed. Do not add different models' tokens and call the sum a dollar cost. No bill or pricing-adjusted saving was established. The typed-review arm added inference and about 5.3 seconds of measured service latency relative to ordinary self-review on this single sequential run, without observed quality gain. No repeat-run or p95 conclusion is possible.

## Defect found and repaired after the frozen run

Independent native review found `d9922a7` accepted fractional token metadata through an f64 validator. Actual retained responses here contain integer input/output fields, so the reported sums are exact and that hostile shape was not exercised. The final implementation uses unsigned integer validation and checked accumulation, rejects fractional/boolean/negative counts, handles null as explicitly unknown, and tests budget crossings/overflow. This is offline hardening after the live snapshot, not a claim that the frozen build already had that fix. A test-only parallel scratch-directory collision was also repaired with an atomic unique suffix.

## What this changes about the angle

1. **Validated narrow capability:** Jev is now an optional callable beside `llm`, with typed distributions, explicit evidence, cache/accounting, and persistent returned data. It is no longer merely an external harness.
2. **Promising measured application:** targeted evidence ranking, with the one-query limitations above.
3. **Rejected default for this workload:** a generic “is this answer adequate?” critic. It added work and missed a material disclosure obligation.
4. **Next hypothesis, not proved:** finer claim/obligation-by-source questions and consequence-aware inspection may expose omissions that a global adequacy label hides. They must be generated without access to gold and evaluated on held-out real tasks. Do not turn the discovered Q2 omission into a gold-targeted live rerun and call that general progress.
5. **Still unproved:** adaptive RLM superiority over a competent Python implementation with the same models, cache, prompts and budget. The tested control program was host-authored, and this corpus fits ordinary full context.

Other proposed angles, including extraction repair, entity joins, memory assistance and orchestration, remain hypotheses or provider-free mechanism demonstrations. See [the application portfolio](../../../docs/typed-judgments.md), not this result as a blanket endorsement.
