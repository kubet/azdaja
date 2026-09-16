# Angle of attack: evidence-addressed semantic operators

2026-09-16. Design analysis, not a measured capability claim. Companion: [frozen pilot protocol](jev-experiment-protocol-20260916.md), [primary evidence](jev-primary-evidence-20260916.md), [runtime boundaries](jev-runtime-boundaries-20260916.md).

Later scope clarification: the implemented experiment tests supplied claim/evidence packs, not memory retrieval or automatic repository evidence construction. See the [request-to-evidence map and concrete memory use-case boundary](jev-request-evidence-map-20260916.md). The product bet below remains a hypothesis, not delivered product behavior.

## The actual product bet

**Azdaja plans and executes evidence-complete work over large local sources. Jev is one replaceable implementation of a typed semantic operator. Exact code owns identity, multiplicity, aggregation, budgets, and escalation.**

This targets tasks with many independent or locally dependent semantic judgments, where a generative root currently spends most of its budget on leaf calls. Examples: identify which incident records meet a natural-language condition, distinguish support from contradiction in repository evidence packs, or map complete message threads to a small domain taxonomy before exact counting. It does not target arbitrary proof, code generation, strategic planning, or globally entangled reasoning.

The moat hypothesis is NOT "we have an API key" or "we use an RLM". TypeSafe is available to competitors. A defensible systems advantage would have to come from the combination of:

1. correct **evidence construction**: recover complete relevant records, provenance, scopes, and relation joins before semantic evaluation;
2. reusable **semantic operator plans**: explicit question schemas, dependencies, abstention, and provider-independent outputs;
3. **scheduling and reuse**: safe deterministic filtering, shared-state independent questions, bounded batching, exact-context deduplication, and invalidation;
4. **auditability**: source-bound judgments, stable occurrence indices, coverage ledgers, failure receipts, and reproducible tests;
5. **measured deployment knowledge**: which operator, data family, model version, and confidence policy actually lies on the quality/cost frontier.

These are hypotheses about useful engineering and accumulated evidence. They are not defensibility established by this repository or by a 66-case pilot.

## Why this shape, and why not the obvious alternatives

| Candidate | Potential gain | Fatal trap | Initial decision |
|---|---|---|---|
| Replace the root model with Jev | Lower apparent model price | Jev does not generate programs, explanations, or recursive plans | Reject |
| Treat Jev as `sub_llm_cmd` | Quick integration | Violates the text-producing leaf contract and hides a changed capability behind an existing API | Reject |
| Add a verifier after every LLM call | Detect some errors | Adds overhead to every case and may agree on the same wrong evidence | Not the first bet |
| Use Jev to discard source blocks | Smaller contexts | False negatives silently remove the only supporting or contradictory evidence | No irreversible pruning |
| Advisory evidence ordering | More useful first views | Local retention is not evidence coverage; stopping after top-k can still lose recall | Plausible later, separately evaluate recall |
| Typed semantic map over complete evidence packs | Avoid free-form generation/parsing, batch independent decisions, enable explicit abstention | Local errors compound into wrong exact aggregates | Chosen falsifiable entry point |
| Purely deterministic parsing or joins | Exact and cheap | Asking a model what code can prove wastes money and introduces errors | Always use code instead |

## Independence is a property of evidence, not an API parameter

A record is not independent merely because it is in a different JSON array position. A claim about a current owner needs the owner record, explicit supersession rule, and applicable corrections. A claim about a deployment may need a joined artifact digest, environment, and execution receipt. Splitting such evidence into separate questions and multiplying probabilities destroys the relationship.

The minimum unit is therefore a **complete evidence pack for one judgment**, not a line, sentence, or arbitrary token chunk. The planner must declare dependencies before batching. Ask independent questions over a shared state together, but make each question's evidence scope explicit. Preserve unused source locally and separately measure what was actually evaluated.

Deterministic exact-match deduplication is legal only for identical evidence packs under an identical semantic contract. The cache key would include full evidence bytes, question instructions and criteria, preprocessing/schema version, concrete provider/model version, and task scope. Same sentence in different time, entity, or policy contexts is not a cache hit. A moving `latest` alias is not a stable cache identity. Cached answers are not new independent observations. No persistent cache is implemented in this pilot.

## Economic break-even, including the work optimism usually omits

Let one ordinary generative leaf cost `C_L`. Let the typed judgment cost `C_J`, and let the acceptance fraction be `a`. If all rejected cases need the ordinary leaf and the typed call is additional work:

`E[C_cascade] = C_J + (1-a) C_L + C_build + C_validate + C_audit`.

Ignoring overhead only to expose the threshold, the cascade saves money iff `a > C_J/C_L`. For a threefold reduction, `a >= 2/3 + C_J/C_L`. A cheap model that accepts only half the work cannot deliver 3x savings in this serial design, even if its own cost were zero. The pilot's 50% coverage is a screen for research viability, not the 3x comparative promotion threshold.

There are two distinct workflows:

- **Substitution cascade**: Jev first, ordinary leaf on abstention. It may reduce generation work.
- **Verification cascade**: ordinary extraction first, Jev verification second, stronger leaf on failure. Its cost is `C_small + C_J + r C_strong`, and errors can be correlated between extractor and verifier. Do not report substitution economics for verification.

Latency is not the same equation as money. In a serial substitution cascade, accepted cases take roughly `T_J`; rejected cases take `T_J + T_L`. Average latency can improve while tail latency worsens. With batching/concurrency, queueing, service region, TLS setup, child-process startup, and the critical path matter. Report request count, total bytes, reported tokens, wall time, p50/p95 and timeout rate separately. The safety-first pilot is sequential for early stopping and is not itself a throughput benchmark.

Vendor price ($0.042/M input, free output at launch) is not a measured account invoice. Shared-state batching may save repeated state encoding, but extra questions still consume resources. Measure billed token usage, not a formula that assumes the provider shares all computation perfectly.

## Accuracy compounds, but not in one universally pessimistic direction

If an exact aggregate depends on all `n` labels being correct and their errors were independent with rate `e`, then `P(all correct)=(1-e)^n`. At `e=0.01,n=100`, this is about 36.6%. This is an illustration, not an estimate for Jev. A count can sometimes remain correct because label errors cancel, so correct counts alone can hide wrong occurrence-level classifications.

Without independence, a union bound gives `P(any error) <= sum_i P(error_i)`, but it is useful only when those marginal error estimates are defensible. Positive error correlation can create catastrophic all-at-once failures, while also changing the probability of at least one error relative to independence. It is mathematically wrong to say correlation always decreases the chance of an entirely correct batch. Measure the failure geometry instead of assuming it.

A reported probability of 0.99 is not automatically a bound on a new example's error. Choice confidence is derived from the same probability vector, so requiring both high probability and high confidence does not provide two independent checks. The pilot freezes both as a conservative heuristic and then tries to falsify it. No calibrated deployment guarantee follows.

For high-stakes source deletion or authoritative memory mutation, these observations favor explicit abstention and no automatic mutation. A negative judgment may control a view only when the full evidence stays available and the workflow still satisfies an independently measured recall/coverage contract.

## Counterfactuals that can kill the product story

1. **Ordinary Azdaja `llm_batch` with labels-only output.** Compare at the same task, source packing, call budget, and error target. Requiring the LLM to generate full probability tables gives Jev an artificial speed advantage if the application only needs labels.
2. **Ordinary Azdaja with a typed-output LLM.** Tests whether the gain is typed interfaces rather than Jev specifically. Run separately from labels-only baseline.
3. **Plain Python + Jev using the exact same evidence packs.** This should match leaf quality. If it also matches planning effort, custody, and operational safety, Azdaja has added no measured advantage on that task. Deterministic reduction by itself is not unique to Azdaja.
4. **Azdaja with no semantic model.** On parseable/symbolic subsets, exact code should win. If the experiment's tasks can all be solved by provided keys and rules, it did not test the semantic bet.
5. **A strong model alone with the full context where it fits.** Tests whether orchestration complexity pays for itself, rather than comparing only with a weak or deliberately awkward baseline.

The present small pilot can reject the leaf idea cheaply. It cannot establish all five comparisons. Unrun comparisons remain explicitly unmeasured.

## What would change the next decision

- **Wrong high-confidence judgments:** reject autonomous evidence filtering on the tested policy. Preserve the failed case. Consider a separately preregistered advisory-ranking study, not a hidden threshold relaxation on the same holdout.
- **Correct but mostly abstaining:** Jev may understand the cases but the confidence policy provides insufficient useful coverage. Explore calibration on a new development set, leaving future test data untouched. Recompute break-even first.
- **Batching changes labels:** narrow state packing, enforce dependency boundaries, and rerun a new versioned study. Do not assume parallel outputs are semantically independent.
- **Cheap leaf but slower complete workflow:** profile packing/transport/escalation. Stop claiming speed, even if the vendor's model latency is excellent.
- **Plain Python matches everything:** position this as an optional convenience adapter, not a moat. The next test must exercise model-authored planning over large unknown sources, not another fixed script.
- **All pilot gates pass:** run a broader independently adjudicated dataset, frozen calibration/test splits, a real baseline, and failure-mode slices. Only then consider a generic capability-gated `judge` host primitive. Existing Azdaja `llm` behavior remains unchanged.
