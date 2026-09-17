# Jev × Azdaja: six isolated angles, measured

## Bottom line

**Keep the optional typed primitive and explicit credential attachment. Do not promote it into a mandatory semantic gate, automatic memory writer, or general quality claim.** The strongest signal here is scoped evidence retrieval: an actual next-agent handoff improved from 0/4 to 3/4 required decisions. It still omitted the migration decision. Fast bulk judgments are useful building blocks, but speed did not rescue failed quality bars.

The working hypothesis is **retain exact evidence, compute cheap typed judgments over it, then let the agent inspect missing or conflicting evidence and use generative reasoning where needed**. Reranking is one application. Classification, verification, adaptive routing, hierarchical lookup and reuse are separate applications with separate outcomes below. Calling a function from an RLM is the interface, not a moat. This study does not establish superiority over a competent Python program using the same models.

## Delivered versus proposed

- Implemented locally: optional `judge_many`/`judge_stats`, full distributions, actual model and usage metadata, persistent evaluator observations, and `az jev attach --stdin`, `status`, `detach`, plus provider-free `az doctor jev`.
- The supplied key was attached through stdin to the normal private host state. Attachment does not enable inference. No key was committed, placed in a prompt, or written to repository memory/configuration.
- Environment override takes precedence. An invalid override fails rather than falling back. Owner-only plaintext storage is not an encrypted vault, same-user sandbox, or a Windows confidentiality guarantee.
- Still proposed: production multiwriter agent-event storage, cross-user authorization, authenticated replication, a persistent global semantic cache, automatic planning and million-event semantic retrieval.
- Released v0.1.17 main fixes are ancestors of this local branch. This work is local and unpublished. It did not replace the user's installed binary, push a branch, or authorize a release.

## Actual experiment and failure history

Methods/source: `9ef4f6fad150505c87db612fe6aefcccf4cfcbaf`, original seal `7950c24`.
Binary SHA-256: `16b3d35002fcec31bb0243c0e33fbcf4b751eab78be77c04fd856b5607540bbb`.
Typed model requested and returned: `jev-1.13.0`. Generative model/provider: `gpt-5.6-sol` / OpenAI.

The original attempt completed the 20-question calibration, then failed during local generative setup with **zero entered model turns**. Inspection found a regular OAuth file in the existing private bridge where Azdaja requires a managed symlink, and unavailable bridge sockets. The shared bridge was not modified. The original stopped receipt remains retained. Its failed exec output was not retained verbatim, so the exact error text cannot be reconstructed from the receipt alone.

An explicit [setup-only amendment](../../bench/jev/angle_followthrough/AMENDMENT.md) moved only experimental state to a new private bridge. It retained the same binary, source, questions, gold, thresholds and order. The completed calibration was reloaded into real Monty, not requested again. Prior calls/tokens and the original wall deadline were carried forward, including repair time. Six offline continuation tests exercised real reentry, cumulative caps and predecessor rejection before admission.

All live work used actual Azdaja `start → load → exec → final`, with retained observations verified on evaluator reentry and a final `kill`. A temporary experimental attachment was removed afterward. Only the experiment-owned bridge process group was stopped. The default durable attachment remains.

## Quality and timing, without pooling unlike tasks

Times below sum measured `exec`/`final` call wall times, excluding input load, later reentry and deterministic preparation. They are descriptive single-run measurements, not provider-only latency, a statistical speed guarantee or complete deployment latency.

| Angle | Observed quality | Measured call time | Decision |
|---|---|---|---|
| Bulk gate, all 227 May occurrences from frozen Oolong row645 | Jev **139**, generative **139**, official **132**. Both wrong by 7. Four individual labels differ despite equal totals. | Jev **5.324 s**, generative **63.292 s**, five calls each. About **11.9×** faster for this labeling phase. | Failed exact-answer bar. No replacement promotion. Aggregate agreement is not per-record accuracy. |
| Calibrated cascade | Threshold 0.7 selected on separate 20-case non-May prefix. Ten May cases escalated, 217 accepted directly. Final **138**, still wrong by 6. | **15.001 s**, including calibration, typed labeling and residual generation. | Failed quality bar. The routing float did not establish correctness of accepted cases. |
| Pre-FINAL claim screening | Jev **10/12**, generative **12/12**. No-review 5/12, abstain-all 4/12. Jev falsely supported q03 and confused insufficient with contradicted on q02. No valid-claim false alarms. | Jev **0.854 s**, generative **6.488 s**. | Useful signal versus no review, but failed matched quality bar. No mandatory gate or measured prose-repair claim. |
| Choice descent | Flat exact-source selection **4/4**. Greedy and two-path variant **1/4**, only the no-match query. Root selected no-match for every query, so no children were called. | Flat **1.009 s**, root **0.831 s**. | Failed source-set bar. This falsifies this headings/paths-only routing representation, not all hierarchical search or Jev reranking. |
| Shared-memory handoff | Same 12 eligible events and 1,800-byte maximum. Lexical **0/4** required decisions, Jev-ranked **3/4**. The remaining migration field was `unknown`. | Lexical handoff **2.773 s**, ranking plus typed-view handoff **3.503 s**. | Partial retrieval-enabled gain, not complete task success. No general advantage over strong retrieval established. |
| Reuse | Exact cache and full recomputation match all occurrence arrays under mutations. At 10k occurrences, five stages give 50k uncached oracle evaluations versus 12 exact-cache misses. | Local injected-oracle timings retained, not provider timings. | Ordinary memoization earns reuse. No distinct dependency-graph or incremental-engine advantage was tested. |

Important limits:

- Oolong provides the aggregate official answer, not the per-row labels used here. Opposite errors can cancel. Neither equal totals nor a future correct total alone would prove all semantic leaves correct.
- The calibration set is a small author-labeled source prefix, not representative deployment calibration. No thresholds were changed after evaluation.
- The verifier screens claims, not completed prose, code or an issue fix. q03 remained a concrete unsupported-acceptance failure.
- Tree preprocessing read 5,947 source-excerpt bytes. Root state was only 324 bytes versus flat state 10,827 bytes. Cheaper routing discarded the information needed to find the sources. No million-source experiment occurred.
- The memory task is a controlled synthetic handoff. Its lexical baseline is deterministic term overlap, not tuned BM25/MMR or a full-context reasoning control. A live full-evidence control was **not run** under the amended two-handoff-call envelope. The unknown answers were appropriate given the views, not hallucinations by the next agent.
- Reuse contains six distinct scoped request states repeated across 1k/10k occurrences. It is a deliberately favorable reuse workload, not a heterogeneous repository benchmark. The single evidence mutation can hit another already-cached exact request. Independent mutation controls separately require misses for changed evidence/question/schema/model/contract/scope. No new Jev request was used to measure cache speed.

## Actual usage and estimated cost

Across the stopped attempt and completed continuation:

- **10 TypeSafe HTTP requests, 279 questions, 56,094 reported input and 6,701 output tokens.** No unknown typed usage.
- **10 logical generative admissions:** one failed local setup with zero entered turns, then **9 successful entered turns**. Reported generative usage: **44,254 input and 4,199 output tokens**. No additional native retry turns were observed.
- The [current model page](https://docs.typesafe.ai/models.md), rechecked 2026-09-17, lists **$0.042/M input tokens and free output** for `jev-1.13.0`. Thus the combined typed estimate is **$0.002355948**, not an invoice. The continuation-only receipt excludes the earlier calibration; the replay adds both correctly.
- Generative price and total billing are **unknown**. Input/output token counts are measured separately, not converted using an invented rate.

| Workload | Typed input / output | Generative input / output | Typed documented-rate estimate |
|---|---:|---:|---:|
| Gate | 35,937 / 4,560 | 34,659 / 3,306 | $0.001509354 |
| Cascade, including calibration and reused gate calls | 39,198 / 4,964 | 2,266 / 486 | $0.001646316 |
| Verifier | 4,763 / 537 | 4,108 / 319 | $0.000200046 |
| Flat source selection | 7,371 / 749 | 0 / 0 | $0.000309582 |
| Tree root | 1,216 / 231 | 0 / 0 | $0.000051072 |
| Memory ranking plus next-agent call | 3,546 / 220 | 1,562 / 51 | $0.000148932 |
| Lexical next-agent control | 0 / 0 | 1,659 / 37 | $0 typed; generative unknown |

Do not sum this table: cascade deliberately reuses the gate observations. The combined totals above count each actual request once. Median gate call times were **1.051 s** typed and **11.698 s** generative, not an assumed 100 ms.

## Validation of the proposed angles

| Claim from the proposed direction | Evidence-backed interpretation |
|---|---|
| Noul gives a routing float without a second judge | Correct when that Noul judgment was already needed. It still consumed measured input/output and requires a calibrated routing policy. Our held-out cascade failed despite zero calibration errors. The RLM can choose questions and inspect omissions, while code routes on returned signals. These are complementary roles. |
| Choice descent is a novel RLM primitive with O(log N) work | Hierarchical Choice/greedy/beam search is already [TypeSafe cookbook prior art](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md). Logarithmic depth assumes a balanced informative index and successful routing. It excludes index construction/update, branching, lost-source recovery and output work. This panel does not justify the million-source claim. |
| Cheap Jev means incremental machinery is unnecessary | Low token cost weakens the case for a complex dependency graph. Latency, repeated work, provenance and reproducibility still make simple exact caching useful. The plain cache passed the mechanism test, with no evidence a more complex engine is needed. |
| A claim store conflicts with the current memory contract | Automatic ingestion/injection or relabeling agent inferences as user-authored memory would conflict. This prototype is explicit and separate. The production authored ledger remains unchanged. Any event-store product needs a reviewed contract change, not a covert reinterpretation. |
| Frozen Oolong is the right spike | Yes. The actual complete subset was run against its existing hash and official answer. It was negative. Cost and speed were measured rather than guessed. |
| Reranking is the entire opportunity | No. The six measurements show different behavior, but only partial task gain from evidence ordering here. The engine can serve several workloads without pretending every workload passes. |
| The moat is measured behavior rather than a wrapper | Agreed. Current behavior supports optional primitives and further evidence-retrieval work, not an exclusive RLM advantage, SOTA label, automatic planner or broad quality claim. |

The [confidence documentation](https://docs.typesafe.ai/confidence.md) distinguishes Choice/Score confidence from their distributions and notes that Noul has no separate confidence field. It calls for domain-specific testing. Distribution concentration is not source completeness, authorization or proof of truth.

## Multi-person / multi-repository design and measured limits

Keep exact raw text/bytes as canonical evidence. Store summaries, embeddings, lexical postings and semantic judgments as rebuildable derived views. RLM is an execution model, not an embedding format. Preserve disagreement and supersession, with source spans, revisions and occurrence IDs.

Use separate stable actor/repository/session/event IDs. Git name/email is optional asserted attribution, **not a unique key or authorization**. The fixture deliberately includes shared email and changed email cases. Apply host-owned visibility/repository scope before candidate generation, prompts, cache and traces. Matching repository paths or self-declared IDs must not confer access.

The actual local scale check produced 1,000 and 10,000 unique event IDs across 31 repository partitions. Authorized query candidates were 31 and 300, respectively. Index-plus-scoped-query time was approximately 0.000327 s and 0.002894 s in this controlled run. This excludes event generation, provider reranking, disk persistence and distributed coordination. It demonstrates a bounded local path, not a team service or million-event quality.

The [design document](jev-wisdom-design-20260917.md) specifies per-actor append segments, source objects, explicit sharing and rebuildable indexes. Real concurrent writers, crash recovery, authenticated identity mapping, revocation and cross-machine replication still require implementation and acceptance tests before production multiuser claims.

## Executable next step, not another claim

Prioritize a **fresh** retrieval-and-follow-up panel, not rerunning this closed fixture:

1. Freeze new task/evidence cases with independent required decisions, permission boundaries, rare facts and conflicting observations. Include a competent lexical/diversity control and a budget-matched full-evidence reference where feasible.
2. Compare the current optional ranking with a workflow that exposes unresolved required fields and retrieves additional evidence only for those fields. Keep all original alternatives available. Test whether the next agent completes the real task, not whether the score rises.
3. Count extra retrieval, typed and generative calls, bytes, tokens and wall time. Require complete supported decisions without scope leakage or invented facts at a declared overhead. Otherwise do not promote it.
4. For bulk gates, acquire independent per-record gold before treating count agreement as reliable aggregation. For tree search, preregister richer routing representations and explicit recovery on a fresh corpus, counting their construction and updates.

These are next-study requirements, not measurements already made. No new provider calls are authorized by replaying the commands below.

## Reproduce and inspect, offline

```sh
python3 -B -m bench.jev.angle_analysis.report
python3 -B -m unittest bench.jev.angle_analysis.test_report -v
AZDAJA_ANGLE_BINARY=/path/to/current/azdaja python3 -B -m unittest \
  bench.jev.angle_lab.test_native bench.jev.angle_lab.test_lanes \
  bench.jev.angle_followthrough.test_run -v
```

The replay checks all 41 original frozen files, the separately frozen continuation inputs, exact matched request state/questions/instructions, complete answer coverage and typed probabilities, both usage ledgers, native trace identity, all 77 retained continuation files and every deterministic lane output. It rejects rehashed false wins, mismatched baseline state, malformed probabilities, erased usage, missing artifacts and output overwrite. Its seven tests passed. Replay validates the retained evidence offline; it does not independently authenticate the provider or repeat inference.

Data: [combined replay](../../bench/jev/angle_lab/results/REPLAY.json), [stopped receipt](../../bench/jev/angle_lab/results/run1-stopped/receipt.json), [continuation receipt](../../bench/jev/angle_lab/results/continuation-completed/receipt.json), [retention and cleanup](../../bench/jev/angle_lab/results/continuation-retention.json), [local memory scale](../../bench/jev/angle_lab/results/MEMORY-SCALE.json).

Prior seven-task answer and eighteen-case source-selection studies remain closed and negative at their original source/model identities. This result does not erase them.
