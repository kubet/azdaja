# Requested measurements: observed results, 2026-09-17

## Decision

The measured advantage is **latency and low documented input cost, not better judgments**.
Keep the typed engine optional. These results do not justify an authoritative gate,
automatic approval, a quality-superiority claim or a README benchmark headline.
Memory/RAG work remains stopped. Cache work remains closed. No new angle was added.

| Requested measurement | Observed quality | Measured time | Interpretation |
| --- | --- | --- | --- |
| Row645 exact-label audit, 227 May occurrences | Both models 220/227. Each has seven false positives and zero false negatives, but only five errors are shared. Official count132, both threshold counts139. | No new inference. | Exact official labels resolve the discrepancy. No framing, month-filter, multiplicity or reduction defect was found on the audited path. |
| Row645 probability audit | `sum(noul)=138.02`, +6.02 above132. Brier0.0259868 against aligned per-item labels. | No new inference. | Aggregate calibration is not established. A matching or near-matching sum alone would not establish calibration either. |
| Flat raw-window localization, 100 attempted cases | One25-case native Choice response rejected. On75 matched valid cases, Jev67/75 and generative67/75. Generative89/100 overall. | Matched native operations: Jev3.668s, generative32.653s. | Incomplete for Jev. No100-case semantic verdict or benefit-bar pass. All25 missing judgments stay in the ledger. |
| Flag-only verifier, 200 cases | Jev179/200, generative180/200. Among100 unsupported claims:15 vs14 false supports. Among100 supported controls:6 false flags each. | Jev9.242s, generative101.675s across eight matched packs, about11.0x faster in this serial run. | Complete panel. Speed bar passes, strict quality and combined benefit bars fail. A result never approves an action. |

Times include actual Azdaja load/exec/final and retained-result handling per operation.
The receipts also separate native call time. They are serial matched-pack measurements,
not a production-throughput, concurrent-load or universal latency guarantee.

## The seven records are identified, not inferred from a count

The local fixture omitted the official dataset's `context_window_text_with_labels`.
We retrieved that field for row645 from the official dataset server and verified:

- Row ID117010248, context window10004, question and aggregate answer match.
- Unlabeled source SHA256 is exactly `05e4419a7280c91b3bbf1ea97629bfc235ee0eb23e67e1f0eeb21fc38b485bf2`.
- All2177 occurrences, including non-May occurrences and duplicate multiplicity,
  align byte-for-byte after removing only the official label suffix.
- The227 May labels contain exactly132 ham messages.

Jev false positives: `r0044 r0503 r0576 r1383 r1394 r1747 r1856`.
Generative false positives: `r0044 r0503 r0514 r1383 r1394 r1581 r1747`.
The four differing decisions explain why equal139 counts were not equal error sets.
These are errors against official benchmark annotations, not a new adjudication
of every ambiguous SMS message. The models were not rerun and labels were never
added to their inputs. [Exact executable audit and source](../../row645_labels/PROVENANCE.md).

## Failed Choice contract and bounded continuation

The original sealed run stopped on flat-02 with `judge: probabilities must sum to one`.
The native validator discarded the rejected body. Its actual sum, affected question IDs,
precision and underlying cause cannot be reconstructed. Do not assert that rounding
caused this failure, or that Jev or Azdaja alone was responsible.

The [explicit amendment](../AMENDMENT.md) preserved the failure and ran only untouched
packs, verifier first, with unchanged sources/questions/models/validators. No attempted
pair was repeated. The original12typed/12generative call budget was shared across both
receipts. The amended wall policy was explicitly summed campaign elapsed, excluding
the investigation interval, not a claim that the original study ran uninterrupted.
All remaining packs completed. The original receipt remains `stopped` permanently.

## Usage and cost, including the failed call

| Arm | Requests / entered turns | Known input tokens | Known output tokens | Cost evidence |
| --- | --- | --- | --- | --- |
| Jev | 12requests, 300questions attempted, 275valid judgments | 81,574 | 7,551 plus one request with unknown output usage | $0.003426108 at documented $0.042/M input tokens. This is an estimate, not an invoice. |
| Generative | 12logical calls, 12entered turns, 300valid judgments | 79,143 | 6,769 | No applicable dollar price established. No dollar comparison inferred. |

Jev verifier alone:45,904input/3,832output tokens, documented input estimate$0.001927968.
The failed Choice call's8,966input tokens remain counted. Unknown output usage is not zero.

## Probability diagnostics, not a tuned shipping threshold

Verifier Brier score:0.0736325. Sum of200 Noul probabilities:103.87 versus100 supported labels.
The five reliability bins and the predeclared confidence coverage curve are retained.
At the predeclared0.9 cutoff,138/200 observations have one error. At0.95,77/200 have zero
errors. Neither is an independently validated production policy or a safety certificate.
No threshold was selected after seeing results, and no approval route was enabled.

All verifier labels use official SQuAD2 annotations. Full paragraphs are supplied,
but annotation noise and training contamination are possible. Cases cluster within
articles. The100 flat cases and200 verifier cases use300 distinct paragraphs, not300
independent replications. This is short-paragraph localization, not million-token search.

## Requirement-to-observation map

| Requirement / changed output | Concrete check | Observed result |
| --- | --- | --- |
| Find row645 record discrepancy before blaming either model | Independent full-source grammar/calendar audit, exact request equality, then official labeled-context alignment |2177aligned records,227May,132gold. Both7FP/0FN, different error sets. No audited code defect found. |
| Report `sum(noul)` against gold | Replay all227 retained probabilities |138.02 vs132, with full labeled ledger and Brier score. |
| Raw flat Choice at n>=100 | Frozen100-case raw-window panel through native `judge_many` and matched `llm` |100attempted,75valid typed. Contract failure blocks complete semantic evaluation. No replacement/retry. |
| Asymmetric verifier at n>=100 bad claims | Native200-case panel:100unsupported and100supported controls, same evidence/questions in both arms |200/200observed both arms,15vs14false supports and6false flags each, zero authorized approvals. |
| Quality, speed, tokens and cost | Recompute outputs/trace/usage and whole-operation clocks from both receipts | Matching quality, time and usage tables above. Speed gain observed, quality bar failed. |
| Keep failures and sources, no selective repeats | Frozen manifests, ordered attempted-pair replay, failed-stat accounting |24distinct attempted pack/arm pairs,25unjudged typed IDs retained, failed usage included. |
| Default offline, no accidental provider calls | Actual public offline load/exec/final preflight and default CLI |Zero new requests in preflight or replay. |
| Falsifiable retained summaries | Mutation tests: hidden failed usage, forged completion, source/prompt swap, missing body/call, changed success bar, duplicate attempt |Rejected. Final audit recomputes grades rather than trusting the stored summary. |
| No memory/RAG, production changes, README claims or user-install changes | Scoped worktree/source check and worker stop |No production-source changes or provider work for cancelled ingestion. No push/release/installation changes. |
| Credential custody | Stop only owned bridge, actual public `jev detach` against experiment state, remove experiment OAuth copy/link, compare default credential bytes/modes |Cleanup passed. User's persistent attachment preserved. |

The requested flat100 **completed-judgment** target was not achieved. Measurement acceptance
means an accurate result, including this failure, not that every desired quality bar passed.

## Replay and retained evidence

```sh
python3 -B -m bench.jev.row645_labels.audit --output NEW-row645.json
python3 -B -m bench.jev.measurement_followthrough.report \
  --continuation bench/jev/measurement_followthrough/results/native-20260917 \
  --output NEW-measurement.json
python3 -B -m bench.jev.measurement_audit --output NEW-acceptance.json
```

These are provider-free, source-bound local replays. They need the unchanged repository
and recorded native binary at its manifest path. Hashes are local custody evidence,
not cryptographic attestations signed by either provider. Existing output paths and
dangling output symlinks are refused. The original frozen report is kept historical:
its partial-run usage denominator limitation is tested, not silently rewritten.
