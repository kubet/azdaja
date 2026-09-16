# Jev × Azdaja: decision and evidence

Date: 2026-09-16. **Decision: no production promotion. Keep the integration optional and experimental. Semantic value is still unmeasured because the live screen stopped at the API/model-identity boundary.**

## Our angle of attack

**Azdaja constructs and executes an evidence-preserving plan. A replaceable typed operator handles bounded semantic judgments. Ordinary code owns joins, occurrence identity, exact counts, budgets, and abstention.**

Jev is not an RLM and cannot replace Azdaja's program-generating root. Its plausible role is reducing repeated leaf-generation work on large-source tasks with many local judgments, not adding an always-on second opinion to every call. The smallest useful unit is a complete evidence pack for a specific entity, scope, and time, not an arbitrary line or token chunk.

The potentially defensible asset is the **planner and its measured evidence discipline**, not an API wrapper: dependency-aware pack construction, reversible selection, exact-context reuse, per-operator calibration, and auditable coverage. None of that is a demonstrated moat yet. Plain Python plus the same Jev inputs is a mandatory counterfactual. If it matches planning effort, custody, quality, and operational cost, Azdaja has shown no additional advantage on that task.

See the [full angle analysis](jev-angle-of-attack-20260916.md), [primary research](jev-primary-evidence-20260916.md), and [runtime boundary proposal](jev-runtime-boundaries-20260916.md).

## What the research actually supports

- **RLM:** externalizing input and decomposing work is a plausible architectural mechanism. The RLM paper does not evaluate Jev or establish that typed leaf substitution improves correctness.
- **Lost in the Middle:** evidence position matters. It motivates position/boundary tests, not a claim that local classification fixes long-context failures.
- **Calibration and selective prediction:** acceptance must be evaluated as selective risk versus coverage on the deployed schema and distribution. A .99 probability is not an individual safety certificate. Jev Choice confidence is derived from the same probability vector, not an independent witness.
- **FrugalGPT and RouteLLM:** compare complete cascades and routes, not advertised model prices. For a substitution cascade, ignoring overhead, 3x cost reduction requires acceptance fraction `a >= 2/3 + C_J/C_L`. A pilot with only 50% useful coverage cannot establish 3x savings even if Jev itself were free.
- **Ensemble diversity:** another API is not necessarily another independent source of truth. Shared evidence and premises can produce correlated failure.
- **Vendor evidence:** the launch's structured-output and internal-workflow claims are not independently adjudicated proof of semantic accuracy. Vendor price/speed and no-training claims do not establish account billing, throughput here, zero retention, or production privacy suitability.

The papers motivate a falsifiable experiment. They do not fill in missing live evidence.

## Preflight was a real falsification process

The first drafts had serious defects. Independent review demonstrated an S4 path that accepted three wrong high-confidence variant judgments while reporting success, timeout tests that could pass for the wrong exception, a worker cancellation leak, directly inverted gold, and a bridge with fabricated zero counts that did not execute correctly in Monty. Those drafts were rejected, not reported as evidence.

The frozen pilot revision `71f2c22` included corrected fixtures and **49 independently verified offline tests**. Every one of the 66 gold cases was reread. Real sleeping child processes were killed and reaped. The actual Azdaja binary verified source/payload hashes, duplicate consistency, coverage, source order, and exact mixed-label/accepted counts. Negative custody tests checked evaluator-specific failure messages, not merely any exception. The final existing core library run discovered 192 tests: 191 passed, none failed, and one pre-existing test was ignored. No ignored test is counted as a pass.

The [independent review](jev-independent-review-20260916.md) preserves specific witnesses, historical hashes, limitations, and separate post-pilot review scope. Green offline tests validate these paths, not model intelligence.

## Live evidence, including failed attempts

| Observation | Exact result | Consequence |
|---|---|---|
| Initial request, `jev-1.12` | HTTP 400, one attempt, no validated body | Setup blocked. The assumed available pin was not checked beforehand. |
| One metadata `GET /v1/models` | HTTP 200, only `jev-latest` and `jev-preview` advertised | Concrete request pin unavailable in the advertised account list. This is not itself proof of the 400's cause. |
| Explicitly preregistered alias run | One HTTP 200 response, 218 bytes, rejected as `response_model_mismatch` | Strict identity contract blocked the run before answer/usage validation. |
| Subsequent live work | None | No retries, threshold tuning, model fishing, holdout, or baseline. |

**Two credentialed inference attempts, zero validated semantic judgments.** Their observed usage is unknown, not zero. The second body was retained only as a hash and byte count. We cannot reconstruct its returned identity, label, probabilities, or token usage. Alias resolution is a plausible diagnosis, not a proven description of that discarded body.

The alias experiment was explicitly registered and committed before its request, with unchanged fixtures, prompts, thresholds, and stage order. It was not a silent substitution. Its amendment specified stopping again on any setup/schema failure, which we did.

Receipts:

- [Initial stopped run](../../bench/jev/results/pilot-20260916.json)
- [Model metadata](../../bench/jev/results/model-discovery-20260916.json)
- [Explicit alias stopped run](../../bench/jev/results/pilot-alias-20260916.json)
- [Pre-response alias amendment](jev-model-availability-amendment-20260916.md)

## Acceptance scoreboard

| Gate | Required bar | Result |
|---|---|---|
| S0 transport/control/custody | All offline adversarial checks pass | Passed for frozen pilot scope. Later hardening is separately tested, not retroactive live validation. |
| S1 smoke | Six correct raw labels and valid contracts | **Blocked**, 0/6 validated observations in either run. |
| S2 challenge | >=27/30 correct, zero wrong automatic acceptances, >=15/30 accepted | Not run. |
| S3 prospective holdout | Same bars after S2, no tuning | Not run. |
| S4 live invariance | No label or acceptance changes, no wrong accepted variants | Not run. Structural custody tested separately. |
| S5 matched baseline | No quality loss and >=2x end-to-end speed or >=3x inference-cost reduction | Not run. |

There is no basis for an accuracy, calibration, selective-risk, throughput, cost-saving, or competitive-advantage claim. A setup rejection is also not evidence that Jev fails the semantic task.

## Actual Azdaja integration evidence

The prototype remains in [`bench/jev`](../../bench/jev/README.md), outside production Rust dispatch and ordinary `llm` behavior. The TypeSafe skill was installed using the non-Claude `npx skills add` method and loaded for this work. Credentials stayed host-side, outside prompts, model state, commits, and receipts.

The stopped alias receipt was replayed offline against fixture, policy, request and historical implementation identities, then projected through the **real** evaluator. With 66 supplied packs and two exact duplicate controls, the saved [custody artifact](../../bench/jev/results/custody-alias-20260916.json) reports:

- 68 preserved source occurrences and a full source-ordered ledger.
- Zero judged cases and **68 explicitly unjudged occurrences**.
- `complete: false`, with no fabricated labels or acceptance.
- Strict mode rejects the missing judgments. Explicit audit mode retains the incomplete result.

This establishes that the selected source ledger is not silently converted into a complete semantic answer after a failed provider call. It does **not** establish successful live semantic integration, provider-authenticated provenance, completeness of task-wide evidence, or attention to every input byte. Duplicate expansion can multiply one semantic error, and aggregate errors can cancel. Correct arithmetic is not semantic reliability.

## Post-pilot fixes, not a rerun

The current code adds future-study safeguards after preserving both original receipts and source revisions:

1. Live CLI requires an explicit model, rather than guessing availability.
2. Known aliases require a predeclared small allowlist of returned non-alias IDs. Exact concrete identity remains the default.
3. The first fully valid, budget-eligible response pins an allowed ID. Later ID change stops without re-pinning. The requested alias stays unchanged on the wire.
4. Safe returned-model metadata is retained even on strict mismatch. Model identity alone does not release unvalidated answers or usage.
5. JSON-escaped credential echoes are checked, and key syntax is narrowed to characters that do not require JSON escaping.
6. Receipt checkpoint failure prevents a next call. Offline replay detects altered identities, requests, summaries, extra post-stop calls, or invented usage completeness.

The final local suite passed **67 tests, zero failures, zero skipped**. Exact implementation hashes, commands, coverage categories and core-test accounting are preserved in the [validation receipt](../../bench/jev/results/validation-20260916.json). These changes have offline test evidence only. A provider-confirmed alias-to-returned-identity mapping has **not** been obtained. Consistent self-reported model IDs do not prove fixed backend weights. The future policy must not be presented as an already validated live repair.

## What to do next, and what not to do

The next highest-information step is resolving the account's request/response identity contract with TypeSafe, including a safe returned-ID diagnostic and a predeclared allowlist. Then register a new tightly bounded contract test before reopening the semantic screen. Do not guess IDs or keep submitting the frozen panel until it turns green.

If that gate passes, use the same progressive hard panel as a cheap rejection screen, then invest in a genuinely representative study: unseen repositories/threads, dependency joins, evidence-position variation, domain shift, and independently adjudicated top-level tasks. Measure a labels-only `llm_batch` baseline, a constrained-output LLM baseline, plain Python plus Jev, and deterministic-only subsets. Charge abstentions/escalations to the workflow. Cluster by independent task, not duplicate leaf or template.

If high-confidence semantic errors appear, the autonomous pruning angle should stop. A separately preregistered **advisory ordering** experiment may still be useful, but only with all evidence retained and independent recall/coverage checks. That is a different claim, not a rescue of a failed acceptance bar.

**Bottom line:** the optional systems angle is coherent and the falsification harness now exercises real Azdaja boundaries. Jev's semantic benefit and any moat remain unproven. No production hook, default dependency, or evidence-deletion path was added.
