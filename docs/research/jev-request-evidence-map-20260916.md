# Jev follow-up: request-to-evidence map and concrete use-case boundary

2026-09-16. This is an offline continuation, not a reopened live experiment. The two original credentialed attempts remain stopped with zero validated judgments. Original fixtures, protocol, provider adapter/runner, and live receipts are unchanged.

**Later scope clarification:** the memory direction below is one possible application, not the user's whole goal. The requested direction is a general optional typed Jev engine exposed beside Azdaja's `llm`/RLM, including reranking and other semantic computation/orchestration uses. The [engine research and mechanism study](jev-engine-design-20260916.md) supersedes any memory-only reading of this historical map. No live-efficacy status changed.

## Completion correction

The delivered artifact is a researched, optional **claim-versus-supplied-evidence operator prototype** with tested control flow and local accounting. It is not a working memory-retrieval product, repository auditor, demonstrated semantic advantage, or moat. Broad goal completion and acceptance traceability were downgraded accordingly. A blocked provider contract is neither a semantic success nor evidence that Jev cannot perform the task.

The earlier explanation mixed three different layers:

1. **Operator implemented in the experiment:** classify one supplied claim/evidence pack as supported, contradicted, or insufficient.
2. **Possible memory application:** order useful curated notes for a new task, preserving provenance and disagreements. This requires a different rubric and retrieval evaluation.
3. **Possible repository application:** assess a finding against a correctly assembled code/test evidence pack. The prototype does not discover dependencies or establish that the pack is complete.

The root/model/tools would assemble context. Jev does not generate repository joins or recursive programs. Calling the generic operator a demonstrated repository-audit advantage was premature.

## Original request mapped to evidence

| Requested outcome | Concrete check or artifact | Evidence state |
|---|---|---|
| Install and use TypeSafe skill | Project-local `.agents/skills/typesafe-ai`, `skills-lock.json`, one successful non-Claude installation method, skill loaded during both passes | Executed |
| Research papers and the distinct Azdaja angle | [Primary sources](jev-primary-evidence-20260916.md), [counterfactuals and economics](jev-angle-of-attack-20260916.md) | Research/design, not empirical superiority |
| Optional integration, no hard lock | Default offline CLI, explicit live activation, constructor preflight, no production Rust dispatch changes, ordinary `llm` paths unchanged | Executed offline, experimental adapter only |
| Difficult progressive cases and defined bars | 66 frozen cases, every gold case independently reread, smoke/challenge/holdout/invariance criteria in the [protocol](jev-experiment-protocol-20260916.md) | Authored and reviewed synthetic panel; not representative deployment data |
| Stop hopeless or unsafe active tests | Executed early-stop counterexamples and exact regressions; both real requests stopped without automatic retries; explicit amendment's second-failure stop honored | Executed |
| Demonstrate useful Jev judgments | First request HTTP 400, second response identity mismatch before full judgment validation | **Blocked, zero validated judgments** |
| Demonstrate actual Azdaja accounting | Real Monty checks source/payload hashes, stable occurrences, mixed counts, missing labels, duplicate expansion | Executed on synthetic controls and actual failed receipts |
| Demonstrate successful receipt plumbing | New complete exact-model and allowlisted-alias synthetic campaigns use the actual CLI and adapter validation, then replay and project through the real evaluator | Executed with an explicitly injected oracle transport, **not Jev** |
| Demonstrate a cost/speed/quality advantage | Matched labels-only LLM, typed LLM, plain Python + Jev, deterministic-only and full-context comparisons | **Not run** |
| Periodic angle reassessment | Recorded 18:33/19:03 checkpoints, heartbeat cancelled at first close and restarted only for the active offline continuation | Executed process control, not model evidence |
| Preserve credentials and unrelated work | Host-side private credential file removed; no secret in committed artifacts; original unrelated dirty Rust/tests left alone | Checked |

A complete evidence map does not mean every requirement has passed. The overarching empirical outcome remains acceptance-blocked, with only partial acceptance evidence.

## New falsification, not just a larger green count

The original 67-test verdict was limited to the then-reviewed snapshots and primarily stopped-receipt replay. The follow-up deliberately exercised the missing successful and partially accepted paths.

Concrete executable witnesses found and repaired:

- Empty or falsy transport metrics could remove request/worker binding while a complete synthetic campaign still replayed as passed. Completed and attempted-response events now require typed, mapped transport evidence. Genuine preflight failures and interruptions are not forced to invent metrics.
- A fully typed first response reporting over one million input tokens could be replayed as completed, including binding an alias identity, although the actual adapter would stop. Replay recomputes cumulative known usage and the default CLI byte/token envelope before eligibility and binding.
- A declared first-call latency beyond 20 minutes, or 79 sequential 20-second calls, could still pass replay. Replay now checks the sum of conservative per-call duration lower bounds. It subtracts the `.0005 ms` rounding allowance per call and tolerates floating-point error. It does not incorrectly cap final receipt time, which may include post-call checkpoint work.
- An invalid model name could pass with recomputed hashes. Requested model grammar is checked unconditionally. Legacy unpinned-alias compatibility preserves the historical no-judgment failures but cannot expose retained judgments, even if the new policy marker is removed.
- Contradictory threshold/custody metadata and impossible response-size claims were accepted. The relevant metadata is compared and a conservative JSON structural size lower bound rejects impossible declared body sizes. This is not raw-body reconstruction or provider authentication.

The controls also show behavior that must remain valid:

- Complete oracle control: 79 in-process transport evaluations, 66 unique judgments, 68 source occurrences, raw and accepted counts `supported=23`, `contradicted=22`, `insufficient=23`.
- Mixed acceptance: all 68 occurrences judged, only 34 accepted. `complete: true` means judgment coverage, **not universal acceptance, correctness, or deployment approval**.
- Semantic stop: the wrong observed label remains in the incomplete audit ledger. It is not replaced with fixture gold.
- Real adapter token crossing: two synthetic responses report 1.2 million tokens. Both responses and usage are retained, but only the first eligible judgment projects, yielding two judged occurrences including its duplicate and 66 unjudged occurrences.
- Exact one-million-token boundary remains eligible. Legitimate rounding and final-bookkeeping cases are not falsely rejected.

The [81-test checkpoint](../../bench/jev/results/validation-followup-20260916.json) is historical. The later [final validation receipt](../../bench/jev/results/validation-followup-final-20260916.json) and [separate independent follow-up review](jev-replay-followup-review-20260916.md) identify the final source hashes and scope. No oracle output is a validated live Jev judgment.

## Grounding a possible memory application in current code

Azdaja's actual local evaluator was used, with `/usr/bin/false` as provider and zero semantic calls, to inspect `src/memory/recall.rs`. Targeted source reads then confirmed:

- `src/memory.rs:28-134`: curated decision/observation/failure/hypothesis/disagreement records with stable IDs, links, tags and provenance. A note is not automatically verified truth.
- `src/memory/recall.rs:135-155`: the inspected recall path ranks by word intersection in note text and tags, with timestamp/ID tie-breaking. Zero-overlap notes are excluded at this stage.
- `src/memory/recall.rs:12-18,174-182`: at most four direct matches, eight context notes and a bounded output envelope.
- `src/memory/recall.rs:183-244`: one-hop links and backlinks supply context. Disagreements and incoming supersession receive priority. Omissions are counted rather than silently described as full coverage.
- `src/memory/recall.rs:306-328`: projection retains complete records and backlinks. The displayed ranking expression does not itself score code/file associations.

**The concrete memory hypothesis is optional semantic ordering of curated project wisdom for the current task.** It is not a generic code scan, truth certification, automatic memory writing, or replacement for the existing provider-free recall path. A query about avoiding reconnect storms might need a scoped note about randomized backoff even without shared query words. A term-heavy unrelated note might otherwise outrank it.

Crucially, reranking only the four current outputs cannot recover a relevant note already removed by lexical filtering. A new study must separately measure candidate coverage, ranking quality, and downstream usefulness. Candidate construction would have to precede the current positive-overlap/top-four cut, using a bounded whole ledger for a small study or an explicitly evaluated broader candidate union. It must not silently send all project memory to a third party.

If explored later, score whole note-plus-relevant-context bundles against the current task using an explicit relevance rubric. Keep relevance separate from truth, credibility, and consensus. Mandatory disagreement/supersession context must not disappear because a model ranks it low. If the bundle cannot fit, expose incompleteness rather than claim complete evidence. All storage remains untouched and the ordinary lexical route remains available.

## Separate future memory test, not a rescue of the stopped pilot

This study has **not** been run or activated. It needs a new preregistration and an acceptable provider identity/privacy contract. The existing claim-support panel cannot substitute for it.

| Hard case | Failure the new study must reveal |
|---|---|
| Useful zero-word-overlap paraphrase | Candidate generator omits the only relevant note, which no reranker can recover |
| Keyword-heavy irrelevant note | Surface overlap wins over genuinely useful project guidance |
| Superseded guidance with an incoming correction | Old advice is delivered without the correction or authority context |
| Disagreement with a popular conclusion | Model relevance silently erases the contrary evidence |
| Same text in a different project/version | Context-insensitive reuse leaks scope or imports stale guidance |
| Malicious instruction quoted in a memory note | Stored data becomes an instruction or causes a memory mutation |
| Context budget cannot hold a linked bundle | Local retention is mistaken for delivered evidence coverage |

Keep the context budget equal to the current recall baseline. Include current lexical retrieval, a strong model over the same candidate bundles, and plain Python plus the same Jev calls. Measure indispensable-note candidate recall, delivered disagreement/correction coverage, utility within the context budget, final agent task errors, latency and total cost including escalations. Cluster by independent task, not duplicated notes. Stop on scope leakage, silent mutation or hidden loss of required contrary context.

The defensible product hypothesis would be better delivery of useful, traceable cross-context lessons, **not more stored text or a cheaper scorer in isolation**. That usefulness is still unmeasured.

## Public model-contract clarification

A targeted reread of the [public HTTP API page](https://docs.typesafe.ai/api.md) at approximately 19:26 UTC still recommends request model `jev-latest`, describes the returned model as the model that performed evaluation, and gives examples echoing `jev-latest`. That page does not supply an account-specific immutable alias mapping. Our conservative non-alias pin policy is stricter than those examples. Do not call an alias echo an invalid provider response merely because it is ineligible under this research policy. No account endpoint or inference was called in this follow-up.
