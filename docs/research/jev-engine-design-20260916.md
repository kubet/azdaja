# Jev × Azdaja: a programmable semantic engine, not just a reranker

_Date: 2026-09-16. Research and experimental design, not a production release._

## Recommendation

**Expose an optional, provider-neutral typed judgment capability beside Azdaja's generative `llm` calls. Let the RLM write and revise programs that combine those judgments with exact code over resident source data.** Reranking is one application. The wider product is computation over a repository or document corpus, rather than merely returning relevant snippets.

The useful division of labor is:

- **Generative root / RLM:** understand the task, construct questions and evidence, choose a decomposition, inspect results, generate code, revise a plan, explain the result.
- **Jev or another typed backend:** answer bounded Choice/Noul/Score questions. It does not write the program, invent an explanation, or replace the root model.
- **Azdaja runtime:** keep source and intermediate data resident, execute exact joins/counts/constraints, retain source associations, enforce capability and resource limits, and expose small summaries or symbolic output handles.

This is an engineering hypothesis, **not an established moat**. A competent Python orchestrator with the same data, models, cache and plan can perform the same computation. The possible advantage is making task-specific program construction, adaptation, and reuse reliable and cheap for arbitrary agents. Those benefits need automatic-planning and end-to-end measurements.

## 1. What the primary literature actually supports

The following are primary papers or first-party API examples, read at method level. They are evidence of existing mechanisms, not evidence that our integration wins.

| Source | Mechanism relevant to the engine | Consequence for this design |
|---|---|---|
| [Recursive Language Models, v3](https://arxiv.org/html/2512.24601v3), §2, §3, Appendix D.1 | Symbolic input handles, symbolic output variables, model calls inside generated programs, persistent REPL, execution feedback. | Azdaja already has the right place to compose semantic calls without bringing every source or intermediate into root context. Merely adding a callable is not a new reasoning architecture. |
| [LOTUS / Semantic Operators, v3](https://arxiv.org/html/2407.11418v3), §2–4 | Filters, joins, top-k, grouping, maps and aggregation. Optimized algorithms have statistical accuracy targets **relative to a specified gold model algorithm**. | Another semantic `filter` or `join` is not novelty. Agreement with a gold model is not semantic truth. Reuse the ideas rather than pretend these operators were missing. |
| [Palimpzest, v2](https://arxiv.org/html/2405.14696v2), system and optimization sections | Declarative typed transformations, logical/physical plans, model selection, code synthesis, sampling, cost/quality tradeoffs. | Schema plus a cheap model plus ordinary code is established. The quoted large speedups include particular baselines and quality tradeoffs, not a transferable guarantee. |
| [DocETL, v3](https://arxiv.org/html/2410.12189v3), §3–5 | Agentic logical rewrites, decomposition into split/gather/map/reduce, entity resolution, generated validation criteria, sample-based evaluation. | Calling our system adaptive while treating DocETL as a fixed map pipeline would be a straw man. The actual comparison must include adaptive rewrites. |
| [DisCIPL / Self-Steering Language Models, v2](https://arxiv.org/html/2504.07081v2), §3 and Algorithm 1 | A planner generates task-specific inference programs. Follower models, symbolic checks, probabilistic-program inference and retry feedback compose inside those programs. | LLM-written orchestration already exists. Algorithm 1 explicitly regenerates after program errors, so an unqualified claim that it cannot repair is false. Jev's label probabilities are **not** follower token likelihoods and cannot be substituted into SMC weights with the same guarantees. |
| [TypeSafe feature discovery cookbook](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery.md) | An LLM proposes questions, Jev supplies numeric features, a supervised model exposes errors, and another round revises the features. | Even LLM-directed semantic-feature discovery already exists in TypeSafe's own examples. Their reported wine-review results are not Azdaja results. |
| [TypeSafe function calling](https://docs.typesafe.ai/cookbooks/function_calling.md), [fan-out](https://docs.typesafe.ai/patterns/fan-out.md), [API](https://docs.typesafe.ai/api.md) | Closed-set routing/arguments, multiple independent questions over shared state, typed results. | Bounded routing is valid. It cannot synthesize arbitrary arguments or code. A single request with many questions is not necessarily less semantic work or lower billing. The provider's latency claims remain unmeasured here. |

### Two important corrections to the usual RLM sales pitch

**Quadratic output is not quadratic semantic work.** The RLM paper's OOLONG-Pairs tasks first categorize entries and then impose counts, dates, and user-pair conditions. Appendix D.1 explicitly makes output large by returning all pairs rather than only counting them. Much of this can be factored into per-entry semantic features plus exact aggregation and pair enumeration. Calling an LLM for every pair can therefore be the wrong algorithm. But a good ordinary Python program can exploit exactly the same factorization.

**RLM benchmark wins do not prove reliable dense analytics.** The paper reports roughly 58% F1 for one GPT-5 RLM OOLONG-Pairs condition, not exact correctness. Its CodeAct baselines place the full input in model context, so they do not exhaust the space of code agents with identical symbolic handles. The paper also reports cases where no-recursion performs better and where poor decompositions or syntax errors hurt. Recursion is an option, not an automatic improvement.

## 2. The engine boundary

Do not make Jev a `sub_llm_cmd` provider and do not change `llm`/`llm_batch` to sometimes return probabilities. Their generative-text contract stays intact. The [existing runtime-boundary investigation](jev-runtime-boundaries-20260916.md) identifies the Monty external dispatch and separate call-budget extension points.

### Proposed native capability, not implemented syntax

```python
# Proposed future API inside a capable Azdaja evaluator.
# These function names are NOT installed by the current experiment.
judgments = judge_many(requests, profile="fast_semantics")
residual_ids = choose_followups(judgments, dependency_counts, budget)
# The existing llm path remains available for genuine generation/reasoning.
# Source, judgments and exact derived outputs remain workspace variables.
```

Start with **one typed request/batch primitive**, not a second database API with seven new operators. Generated ordinary code can implement a filter, ranking, graph, join or reduction. Add specialized operators only after a repeated workload demonstrates that engine scheduling can improve them.

The host, not the generated program, controls:

1. **Activation and profiles.** Default absent/disabled, explicitly enabled for the session. No key discovery that silently turns it on. A request can select a registered backend profile, not an endpoint, command, credential or larger budget.
2. **Typed contract.** Full question meaning and options are supplied, not hidden in question IDs. Return probabilities and selected values, with exact answer coverage. Noul is a probability, not a Python Boolean. Preserve semantic unknown, policy abstention, unjudged, and transport failure separately.
3. **Materialization and identity.** Bind source version, request bytes, question/option order, backend contract and occurrence IDs. Hold raw judgments separately from acceptance thresholds and exact derived views.
4. **Budgets.** Preflight bytes, calls and questions. Count provider-reported usage when available. Deadlines, cancellation, model-resolution policy and transport evidence remain provider-adapter responsibilities. No retry or generative fallback that the user did not budget.
5. **Reuse.** Cache an exact raw observation, not an accepted Boolean. Changed evidence, question, criterion order or backend contract invalidates it. Changed thresholds recompute views. Cache hits do not count as independent supporting evidence.
6. **Failure and continuation.** Return a typed incomplete state or stop. Keep already validated observations inspectable. Never pass a missing response through as false. A partial reload cannot silently reuse an older successful stage.

Credentials remain host-only. A later Typesafe profile can invoke the existing bounded adapter with an explicitly supplied key source and declared model policy. The sandbox and root prompts never receive the key. Another backend must be usable without changing task programs. The current study does not authenticate any new request or resolve the earlier model-availability failure.

### Current prototype, deliberately narrower

[`bench/jev/engine_lab/`](../../bench/jev/engine_lab/) implements a staged manifest protocol:

```mermaid
flowchart LR
    A[Resident source in actual Monty] --> B[Handwritten program emits typed manifest]
    B --> C[Opt-in host kernel]
    C --> D[Injected synthetic backend]
    D --> E[Validated raw judgments and exact-request reuse]
    E --> F[Load into the same Monty session]
    F --> G[Exact join, residual selection, or derived view]
    G --> B
```

This is **not** a new native external function, an automatic RLM planner, a live Jev integration test, a concurrency scheduler, a resumable database, or a cross-process cache. It uses an explicit host handoff to prove that typed values can participate in persistent Azdaja computation without changing existing core behavior. Its backend is injected by trusted host code. The laboratory has no credential reader or HTTP path of its own.

## 3. Application portfolio and the best starting point

| Application | What the RLM contributes | What Jev and exact code contribute | Main failure and strong counterfactual |
|---|---|---|---|
| **Retrieval and reranking** | Choose candidate sources, question dimensions, context scope, and follow-up evidence. | Score candidates, compare bounded alternatives, preserve disagreement, assemble a source-backed context pack. | A reranker cannot recover an omitted candidate. Compare against strong lexical/vector retrieval plus a cross-encoder or generative reranker, and the same RLM with direct API loops. |
| **Dense corpus questions** | Turn an ad hoc question into semantic features plus a computational plan, revising when the decomposition is inadequate. | Classify bounded records, then exact counts, joins, graphs and large symbolic output. | Feature factorization may be invalid, and one mistaken feature can corrupt many pairs. Compare matched hand-written Python and LOTUS-style plans, not only naive pairwise calls. |
| **Semantic regression and witness finding** | Ask what changed across revisions, build evidence for an invariant, inspect contradictions, and choose the next local check. | Typed relation/policy judgments become an exact dependency graph or constraint problem. Source diffs can restrict recomputation. | Finding a verified violation can be useful. Failing to find one does not prove universal compliance. Compare static checks, graph/search baselines, and a direct generative auditor. Do not use this alone to authorize a release. |
| **Extraction and parser repair** | Propose a parser/schema, inspect malformed or semantically suspect partitions, change the local plan. | Code enumerates/copies candidate spans, Jev selects known candidates, typed unknowns route residuals to `llm`. | Silent format drift or missing candidate spans cannot be fixed by confidence. Compare DocETL and a generated-parser baseline with the same repair budget. |
| **Reusable semantic views of `.azdaja` memory** | Decide which task-specific features are worth materializing and when stale conclusions need re-examination. | Reuse revision-bound raw judgments, recompute rankings or constraints, retain provenance and incompatible observations. | This is not permission to rewrite memory. File association, task scope, question changes and model changes affect validity. A plain versioned feature cache is the required baseline. |
| **Bounded orchestration/routing** | Supply candidate tools or subplans and the state needed to choose among them. | Choice selects a known option; code enforces permissions and argument domains. Independent speculative questions can reduce sequential round trips. | Generic routing is already a TypeSafe pattern and not the moat. Min-confidence routing can miss confidently wrong actions. Never infer authorization from a model vote. |

**Recommended product sequence:** use the same minimal engine for (a) retrieval/context selection and (b) a dense corpus-query demonstration. Those two applications reveal whether the capability is general rather than a special-purpose reranker. Add adaptive witness/repair loops only when these have end-to-end evidence. Do not start by building a generic distributed query optimizer or automatically mutating project memory.

## 4. The less-obvious orchestration angle: verify by downstream impact

A persistent program can know which judgments affect which final decisions. That enables a follow-up policy more useful than “ask the big model about every low-confidence row.”

For a candidate judgment `j`, a research policy could prioritize:

`estimated decision impact × empirical chance of correction × expected value of resolving it / incremental cost`.

This is a **hypothesis**, not a calibrated equation we have implemented. Dependency count is an observable proxy, not the complete utility. Error probabilities, correlations, and expected resolution need held-out data. A high-fan-out feature can deserve verification even when Jev is confident, while an uncertain row that cannot affect the requested answer may not deserve another call.

This is where the RLM workspace is useful: it can keep a derived graph, run exact counterfactuals with a feature toggled, inspect which output changes, and choose a next question or larger-context `llm` call. The same technique is available to good ordinary code. The test is whether a generated, task-adaptive plan uses it effectively on new problems at an acceptable planning cost.

Required falsifiers for a future study:

- confident wrong high-impact feature, which uncertainty-only routing misses;
- low-impact uncertainty that consumes budget but cannot change the answer;
- correlated errors, so counting many agreeing leaves gives false comfort;
- wrong low-degree feature, so an impact-only policy also fails;
- relational ambiguity where unary features are insufficient;
- an unresolved item under a universal claim, which must prevent certification;
- evidence outside the initial candidate set, which tests retrieval/plan completeness rather than ranking.

## 5. Executed mechanism evidence

The [preregistered protocol](jev-engine-mechanism-protocol-20260916.md) was committed at `ba636ef` before the implementation. It defines M1–M6 and incorporated independent criticism before coding. All inputs and model outputs below are authored synthetic controls. Programs are handwritten. The tests run the real `target/debug/azdaja` binary with a `/usr/bin/false` generative provider and guarded host networking.

Final run: **20 tests passed, zero skipped**, independently reproduced. The [retained mechanism receipt](../../bench/jev/engine_lab/results/mechanisms-20260916.json) binds the implementation, dependency, protocol and actual binary hashes. The initial 15-test suite missed response-body substitution and stale-state reuse after failed handoffs. Independent executable witnesses exposed these defects. Engine-owned immutable observation bindings and all-exit session poisoning now have exact regressions. The [independent review](jev-engine-independent-review-20260916.md) records the failures, fixes and limits.

| Observation | Result | What it proves and does not prove |
|---|---|---|
| Explicitly factorable pair query | 72 occurrences, 16 unique source records, all 2,556 `i < j` pairs accounted for, 336 positives. | Exact program reduction on these typed inputs. The factorization is a supplied task contract, not something the model discovered. |
| Cache ablation | 72 questions without reuse, 16 with reuse. A second view adds no semantic questions. | Reusing exact observations saves logical calls in this synthetic control. No measured Jev price, latency or accuracy claim. |
| Strong matched Python | Identical full pair ledger and the same 16 unique semantic questions. | **No exclusive RLM execution advantage.** Naive 2,556 pair checks would be the wrong competitive baseline here. |
| Symbolic output | Full ledger serializes to 34,739 bytes; an exact count summary is 29 bytes. | Intermediate/output residency is real. This is not a measured token saving for an automatic planner, which was not run. |
| Non-factorable relation | Identical chosen unary features, different pair truths. Explicit direct-pair branch recovers both cases with six total questions. | Those features are insufficient. It does not rule out every representation, nor prove automatic collision discovery. |
| Confident wrong unary feature | One unique flipped feature creates **96 wrong pair decisions**, although the output is structurally complete. | Exact code and complete accounting do not repair semantic error. The resulting errors are dependent, not 96 independent observations. |
| Residual-only stage | Three occurrence IDs, two unique additional questions. Unknown pairs go from nine to three; final result remains incomplete. | Bounded adaptive dispatch and honest unresolved state, not a real generative escalation or calibrated uncertainty policy. |
| Identity/failure controls | Changes to source, generation, request, profile contract, coverage and option order are checked. Partial backend failure is not a complete stage. | Narrow source/typed-accounting mechanics, not authentication of provider truth or task-wide evidence completeness. |

## 6. End-to-end promotion bar

The mechanism gate is necessary, not sufficient. Before native production exposure, preregister a separate bounded study after resolving provider identity/availability without reopening the stopped campaign by stealth.

Use the same root model, source access, output requirements, leaf models and repair budget across:

1. Azdaja plus the typed engine.
2. An equally capable plain Python/API loop with caching and concurrency, not a deliberately weak wrapper.
3. A static task plan and the closest existing semantic-engine plan.
4. A fixed plan with Jev versus a strong generative leaf, to isolate the backend effect from planning.

Proposed screening bars to freeze with the future dataset, not results achieved here:

- **Quality floor:** no more than a 2 percentage-point decline on the primary task metric relative to the strongest matched baseline. No hard stratum more than 5 points worse. Explicit missing-counterevidence and unsafe-factorization controls must all be handled correctly or remain unknown.
- **Coverage floor:** include unknown/unjudged items as unsolved in the primary task metric, report conditional accepted-answer quality separately, and permit no more than a 2 percentage-point coverage loss against the matched baseline. Returning unknown on everything cannot satisfy the quality/cost gate.
- **Economic benefit:** at matched quality, at least 30% lower median total cost, including root planning, failed attempts, verification, repairs and outputs. Alternatively, a predeclared material quality gain at the same budget. Report p95 latency and prohibit hiding a greater than 2× tail-latency regression.
- **Planning generalization:** new task families and formats, not only new rows under the development template. Distinguish the benefit of a supplied plan from automatic plan discovery.
- **Reranking:** report candidate recall before ranking, nDCG/recall after ranking, and worst-stratum misses. A perfect ranking over an incomplete pool is a failure of the full workflow.
- **Dense relations:** compare full pair ledgers, unknown coverage and amplified error, not only unique-row accuracy. Count pair/output work separately from semantic questions and HTTP requests.
- **Stopping:** after each preregistered stage, stop if a critical counterexample occurs or if even perfect remaining results cannot reach the quality bar. Keep stopped/failed attempts in the cost denominator. Statistical intervals must respect task/project clustering and the declared sequential design.

These numbers are engineering screening targets, not safety guarantees. A small pilot cannot establish reliable rare-event risk or a commercial moat.

## Decision

**Build toward the optional typed engine, not a Jev hard dependency and not a reranking-only feature.** The present prototype establishes a workable staged execution boundary and preserves useful negative results. It does not yet justify native production integration. The strongest next research bet is task-adaptive semantic computation with selective, downstream-impact-aware verification, evaluated against matched code and existing semantic systems.

The earlier live status is unchanged: **two attempts, zero validated Jev judgments, unknown billing, no semantic efficacy or competitive advantage established.** See the [prior decision](jev-decision-20260916.md) for the frozen campaign and the [engine laboratory README](../../bench/jev/engine_lab/README.md) for reproducible mechanism commands.
