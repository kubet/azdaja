# Optional semantic engine: mechanism protocol

_Date: 2026-09-16. Frozen before implementation of `bench/jev/engine_lab/`._

## Question and limits

The requested product is an **optional typed semantic engine callable by Azdaja's LLM/RLM**, beside its existing generative `llm` functions. Retrieval/reranking is one application, not the entire product and not excluded. This protocol tests the execution substrate, not whether Jev is accurate or whether an RLM can automatically discover the programs.

The previous Jev pilot remains stopped: two inference attempts, zero validated judgments, unknown billing. This is a separate **provider-free mechanism experiment**. No credentials, remote inference, production hook changes, memory mutation, model downloads, or new packages are allowed. Original pilot fixtures, receipts, protocol, implementation and independent reviews remain untouched.

## Minimal prototype, not a new database

Implement a staged host-side `judge_many` kernel under `bench/jev/engine_lab/`:

1. A handwritten Python program runs in the real Azdaja/Monty evaluator over loaded source. It emits a bounded manifest of typed requests.
2. An explicitly enabled host engine uses an injected, named synthetic backend. It validates requests and typed responses, counts logical questions and backend invocations separately, and materializes complete results with request identity.
3. The host loads those results back into the **same persistent evaluator session**. Code performs joins, ranking, exact reductions or residual selection. Intermediates remain in evaluator state.
4. Exact repeated requests may reuse the same recorded judgment within this engine instance. Distinct occurrences stay distinct in the output ledger. Changed state, question, option order, or backend contract must miss the cache. Changing only an application threshold must not require another model judgment.

This staged manifest exchange is deliberately **not** a claim that `judge()` is now a native Monty external function. A future capability-gated Rust host function would remove the manual handoff. The prototype must not overload `llm`, impersonate generated text, infer unknown answers as false, or enable itself by discovering a key.

## Predeclared controls and acceptance bars

| ID | Mechanism and positive case | Falsifier / negative control | Exact bar |
|---|---|---|---|
| M1 | A bounded all-pairs query whose stated predicate is explicitly the conjunction of two unary semantic labels and exact structured conditions. Classify each source once, then enumerate pairs in Monty. | Same task implemented by competent ordinary Python using the identical oracle and decomposition. Naive pairwise logical evaluation is a complexity illustration, **not the competitive baseline**. | Full ordered output equality with both exhaustive oracle and matched Python. Distinct semantic questions = unique exact requests, not number of output pairs. No wall-clock or billing superiority claim. |
| M2 | Test the limits of unary factorization. Supply two relation tasks with the same chosen unary feature vectors but different pairwise gold relations. | Applying the M1 reduction to these tasks must be demonstrably wrong. Use a direct pairwise oracle to recover the distinction. | At least one differing pair with identical feature inputs. Record unsafe reduction as **falsified**, not a failed test to be tuned away. This disproves sufficiency of the chosen features, not existence of every possible representation. |
| M3 | Materialize complete typed judgments, select low-margin residual IDs in Monty, and request only those IDs from a second synthetic backend profile. | One residual remains unknown; a budget preventing a second stage must not manufacture an answer. High-confidence wrong answers are not detectable from confidence alone. | Exact residual set and stable occurrence coverage. Known partial results retained, remaining unknown explicitly represented. No claim of calibrated thresholds, automated reasoning, or real `llm` escalation. |
| M4 | Reuse requests across repeated views and recompute exact reductions without semantic calls. | Change state, question wording, option order, backend contract, or nested caller-owned objects. Include duplicate source occurrences. | Zero additional backend invocations on exact reuse. One additional invocation per changed unique request. Duplicate occurrence multiplicity preserved. Mutating a returned object must not alter cached evidence. |
| M5 | Choice, Noul and Score remain typed data with probabilities. | Missing/extra answers, malformed probabilities, invalid question types, disabled engine and exhausted budgets. | Reject before reduction, no inferred default value. Disabled and preflight budget cases enter no backend. Partial stage failure returns no pretend-complete stage; existing successful records remain inspectable. |
| M6 | Source and intermediate objects remain resident across staged execution. Symbolic output may exceed a small root-inspection summary. | Result rebound to a different request/source or missing occurrence; program must reject before using it. | Actual Monty checks request/source association and exact coverage. Every real-evaluator test runs without generative provider or network. Report only sizes/hashes as root-view illustration, not measured context savings for an automatic planner. |

### Stop rules

- Stop any test that attempts network or an unexpected child process. Inspect before resuming.
- If the staged exchange cannot preserve typed data and source/occurrence identity in the real evaluator, stop the engine promotion recommendation. Do not substitute a Python-only mock and call the interface validated.
- If matched Python equals the RLM-program output and semantic work, report equality. Do not weaken that baseline to manufacture an RLM advantage.
- If feature factorization fails on a relation-sensitive task, preserve that counterexample and restrict the optimization. Do not modify the task until the reduction looks correct.
- Do not expand into production integration or another live campaign on the strength of these controls.

## Accounting and interpretation

Count source occurrences, unique exact semantic requests, questions, backend invocations, cache reuses, unresolved rows, input/output serialization bytes, and full ordered result hashes separately. Batching many questions in one HTTP request is not the same as reducing semantic work or billed input. The synthetic backend has **no measured token cost or latency**. Any logical-call reduction is not a price or speed claim.

Thresholds in these mechanics are arbitrary declared test policies, not learned calibration. A typed value, a precise join, a checksum, a complete ledger, or a recorded model name cannot certify semantic truth, evidence completeness, backend weight immutability, or safe release decisions.

## Independent preimplementation constraints

The independent reviewer required these additions before any engine code was written:

- Factorization is allowed only under a supplied contract `R(x,y) = g(phi(x), phi(y), exact_fields)`. A successful finite panel cannot discover or prove that contract. The direct pair reference uses independently supplied pair truth over the same `i < j` occurrence universe, with no diagonal and no feature-extractor reuse.
- The collision case must **route to direct pair requests or return unresolved**, not merely demonstrate a known-wrong reduction separately. A deliberately wrong high-confidence feature must also expose downstream error amplification. Only unknown features test safe residual recovery.
- Manifest session/generation/source hash, ordered job IDs, exact serialized requests and backend contract digests are frozen before evaluation. Re-entry checks exact ID coverage and associations. Shuffled response rows are harmless. Missing, extra, duplicate, stale-generation or wrong-source results are rejected.
- Cache only raw complete typed judgments, not thresholded booleans or transient failures. Recompute derived decisions under changed thresholds. Cache hits are reuse of one observation, not independent corroboration. No cross-process resumption or immutable backend weights are implied.
- Keep semantic unknown/abstention, unjudged and transport/budget failure distinct. A failed second stage leaves the first stage available but cannot become a complete final result. The kernel preflights declared byte/call/question limits and never silently clips a pair universe.

## Next empirical gate, not executed here

After successful mechanisms, a separately registered study must compare:

- the same generating model with a plain Python/API wrapper and an equally capable cache/loop baseline;
- a static hand-written plan, relevant LOTUS/DocETL-style plan, and the adaptive Azdaja plan;
- Jev leaves versus a strong generative leaf, holding the plan fixed;
- automatic plans on **unseen task families and source formats**, with discovery/repair tokens included.

Require matched task quality, lower total end-to-end cost or materially better quality at the same budget, and no hidden increase in unknowns or hard-stratum misses. For reranking, measure candidate recall before ranking as well as ranking quality. For relation tasks, measure pair precision/recall and error amplification. For adaptive orchestration, measure whether selected follow-ups actually change correct decisions, rather than just reducing calls. Mechanism tests cannot satisfy this gate.
