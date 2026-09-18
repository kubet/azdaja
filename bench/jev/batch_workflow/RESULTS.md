# Completed long-source batch workflow

**This is working product behavior, not a recovered planner result.** The native `jev batch` command read the declared work list, made real Jev requests, durably saved every observation, and produced the complete source-linked review file. No generated finalization program, extra generative call, or offline answer repair was used.

## Observed run, 2026-09-18

| Measure | Observed |
| --- | ---: |
| Full source files | 102 CUAD test contracts |
| Exact source bytes represented | 4,779,822 |
| Source windows / typed questions | 138 / 138 |
| Completed requests | 138 / 138 |
| Failed / unresolved requests | 0 / 0 |
| End-to-end native job wall time | 145.049 seconds |
| Reported input / output tokens | 1,113,588 / 2,760 |
| Unknown input / output usage | 0 / 0 |
| Generative calls | 0 |
| Completed resume with empty key | 138 reused, **0 new requests** |
| Ambiguous-intent resume | stopped, **0 new requests** |

Requested model: `jev-latest`. Observations report `jev-1.13.0`. A provider model name is not an immutable weights identity. Usage is not an invoice. No matched speedup or accuracy claim follows from this single workflow acceptance.

Executable source: `3dc893f5ace9da8ea905d40b68290fa032243644`.
Optimized executable SHA-256: `b2f28d842703852b9a898d4ac18fb5788384ad55268cf4dc7dca1c5cee9cd60c`.
Plan SHA-256: `6a0a2c53a01fd0053ed00f6179ab30eaeea0aee92e2f0a9061b2324697c7cc24`.
Complete review SHA-256: `3298a9791b4bf8f36f4ae988452ce0a48c3d151fb15bbb85b473b135d813ff41`.

The admission followed [PLAN.md](PLAN.md). A local inventory script initially referred to a nonexistent optional `build.rs`. It stopped before creating an admission marker or job and before any provider call. That zero-call failure is retained. The corrected setup admitted exactly one live job with unchanged source, binary, question and limits.

## Concrete output to use

The fixed question asks for operative assignment/transfer consent restrictions, excluding mere mentions of successors, permitted assigns and intellectual-property assignment. [The complete index](results-20260918/review-index.json) retains all 138 windows, probabilities, source hashes and offsets, including low scores. Reconstruct their **full verbatim text** and the actual JSONL review with:

```sh
python3 -B bench/jev/batch_workflow/replay.py --output ./cuad-review
```

This makes `cuad-review/review.jsonl`, `cuad-review/sources/*.txt` and the exact original plan, without a key or provider call. Existing output is refused. Original scratch paths and the original executable are unnecessary. The portable check validates retained bytes and bindings, not independent provider authenticity or historical executable bytes.

Exact clauses in the three highest-scoring windows were checked against the full source by the coordinator and a separate reviewer. These are useful review candidates, not a panel-wide accuracy estimate:

| Window | Source byte range of inspected clause | Raw p | Exact excerpt |
| --- | --- | ---: | --- |
| `000009-000000` | `009.txt:21480..21645` | 0.99 | “neither this Agreement nor any of the rights, interests or obligations hereunder shall be assigned by any Party without the prior written consent of the other Party.” |
| `000012-000000` | `012.txt:12707..12811` | 0.99 | “This Agreement may not be assigned by either Party without the prior written consent of the other Party.” |
| `000020-000001` | `020.txt:64547..64743` | 0.99 | “Neither party may assign this Agreement or subcontract its obligations under this Agreement to another party without the other party's prior, written consent executed by a duly authorized officer.” |

These excerpts are byte-bound in [inspected-examples.json](results-20260918/inspected-examples.json). The full windows preserve nearby exceptions and qualifications. A window split can still separate relevant context. No probability is converted into a legal approval or a claim that every restriction has been found. No gold labels or old predictions were used in the requests or this review.

## Requirement-to-observation map

| Required behavior | Concrete observed check |
| --- | --- |
| Long source without silent truncation | Export reconstructs every one of the 102 original files byte-for-byte and hash-for-hash from all 138 windows. |
| Real optional typed execution | Actual optimized CLI returned completed; 138 durable intents/results, 138 native attempts, all response request hashes match. |
| Durable results and honest usage | Independent sum over all saved stats equals the native summary. Each result saved before next progress event. Injected crash/failure/unknown-usage and cumulative-budget tests pass. |
| No rebilling completed work | Actual completed resume with `TYPESAFE_API_KEY` empty succeeds in a fresh process with zero requests and unchanged job-file hashes. |
| No automatic ambiguous retry | Actual copied-job witness removes the final result but preserves its intent. Resume stops with `ambiguous_inflight_request`, 137 completed and zero new requests. Original job is unchanged. |
| Stable source/config/limit binding | Actual changed-input and changed-token-limit resume attempts exit 2. Native tests also reject changed configuration and response bindings. |
| Useful export and safe outputs | Real public exporter produces all 138 exact-source rows. Occupied output is refused; link/corruption/partial tests pass. Three highest-ranked windows contain explicit relevant clauses. |
| Optionality and packaging | Default and TypeSafe-feature native CLI tests pass; default preflight performs no credential reads. Notice/package allowlist updated, strict lint passes. |
| Portable delivery | Actual replay outside the repository rebuilds the identical review. Network/process-forbidden replay passes; changed artifact and occupied/dangling-output tests reject. |

Scoped validation: 28 native judgment/batch unit tests, eight actual batch CLI tests, seven existing native judgment tests, 15 notice/package tests, 12 prepare/export tests and four retained-review tests. Default-feature CLI suites also pass. This is not a claim that the entire project suite was rerun locally for this commit. Hosted checks are tracked separately.

## Boundaries and attribution

The command is a local explicit work-list executor, not an automatic RLM planner, global memory system or multi-tenant job service. Stored provider observations are validated native JSON, not raw HTTP response bytes. Same-user artifact control is not cryptographic provider attestation.

The prior model-authored CUAD live failures remain failed and unmodified. This different workflow proves completion, durability, review export and no-key resume. It does not establish superior semantic quality or a matched long-task speed advantage.

Source texts: **CUAD: Contract Understanding Atticus Dataset**, The Atticus Project and contributors, pinned upstream commit `67faa0e6023b04fcaae6cc09497ab00e5d63a2a2`. Dataset license: **CC BY 4.0**, as recorded in the existing [source manifest](../long_task/fixtures/source-manifest.json) and linked dataset card. Excerpts and windows retain source identity and offsets. Full texts are reconstructed from that existing attributed corpus rather than duplicated here.

For your own authorized files, use the [source-build and execution instructions](../../../docs/jev-batch.md).
