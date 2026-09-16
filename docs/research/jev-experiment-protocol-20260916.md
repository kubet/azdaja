# Jev inside Azdaja: preregistered investigation

Date: 2026-09-16. Status: frozen before any live inference. This is an experiment, not a product or superiority announcement.

## Question and angle of attack

Can optional typed semantic leaves reduce the cost of evidence judgments inside Azdaja without weakening its complete-source custody, occurrence accounting, or fail-closed result contract?

Jev is **not an RLM**. TypeSafe documents a discriminative `state + questions -> answers` API (Choice/Noul/Score). Azdaja supplies persistent context, programmatic evidence construction, recursion and exact reduction. The possible advantage belongs to the composition, not exclusive access to a vendor model. A durable advantage would be an evidence-preserving semantic work planner, calibrated abstention, replayable receipts, and provider-independent leaf contracts. A cheap endpoint alone is not a moat.

Start with claim-versus-evidence judgments: `supported`, `contradicted`, `insufficient`. This is relevant to repository findings, memory recall, citation support, and record classification. Do not replace the root model, silently reinterpret `llm`, or discard evidence on Jev's opinion. Keep hypotheses separate:

1. H1: Jev can make difficult local evidence judgments accurately enough to justify further research.
2. H2: a conservative abstention policy can find useful coverage without accepted errors on independently authored cases.
3. H3: shared-state batching and deterministic duplicate expansion reduce work without changing judgments or occurrence identity.
4. H4: the complete workflow beats a real generative-leaf baseline at matched accuracy, including escalation cost and latency. H4 cannot be claimed from API token prices, scripted transports, or an oracle fallback.

## Research before implementation

Read the installed TypeSafe skill, live API, confidence, System One, Choice, and cascade guidance. Independently review RLM and selective prediction/cascade research. Track vendor claims separately from measurements. The homepage's “zero hallucinations” marketing is **not** a correctness guarantee. TypeSafe's technical documentation explicitly says calibration does not guarantee an individual answer is correct.

## Frozen interface and policy

- Experiment uses documented `POST https://api.typesafe.ai/v1/systemone` and an explicit model identifier. Prefer a concrete available version, not a drifting alias. If only `jev-latest` is used, record returned model and mark alias drift unresolved.
- HTTP adapter remains outside the production Rust runtime until evidence and security gates warrant deeper integration.
- Explicit live opt-in is required. No import-time or default-path network. An API key by itself is not activation.
- Credentials are environment/private-file host inputs, never source-state fields, command-line values, receipts, fixtures, or commits. Only synthetic authored evidence is transmitted in this campaign.
- No automatic fallback, retries, hidden parallel requests, model substitution, root replacement, or mutation of existing `llm` behavior.
- Every request includes the claim and all evidence needed for that local judgment. Labels, rationales, split names, and case family metadata never enter model state or question IDs.
- Exact coverage/type/domain checks precede reduction. Reject malformed JSON, duplicate JSON object keys, missing/extra answer IDs, invalid/nonfinite probabilities, invalid sums, mismatched selected option, wrong model, oversized input/output, redirects, and unbounded error bodies.
- Preserve full raw judgments. A Choice confidence is a distribution-concentration statistic, not independent evidence of correctness.
- Frozen automatic-accept policy for this pilot: selected-option probability >= 0.98 AND reported confidence >= 0.90. All other judgments abstain. No threshold tuning after viewing holdout results.

## Progressive stages and stop rules

### S0: offline transport and custody

100% of contract tests must pass. Cover disabled/no-key paths without network, request/response caps, malformed and duplicate keys, every primitive shape, credential redaction, budget exhaustion, HTTP errors, redirects, timeout, exact provenance, and duplicates. Any security or custody failure blocks live experiments until fixed. Fixes to infrastructure are allowed, semantic prompt/label changes require a new named experiment.

### S1: six-case smoke

Independent fixtures: two cases per class. All six raw labels and response schemas must be correct. Sequential requests, stop at first wrong label or transport failure. This is a connectivity/task sanity check, not evidence of general capability.

### S2: thirty-case challenge

Frozen independently authored cases include negation, conditionals, exceptions, stale evidence with explicit authority, identity mismatch, hypotheticals, missing evidence, prompt injection, and complete multi-fact evidence packs. Must have >= 27/30 raw correct (90%), zero incorrectly accepted decisions, and >= 15/30 automatically accepted (50% coverage).

After each response, stop immediately if an incorrect auto-accepted decision occurs, if errors exceed three, or if even perfect remaining responses cannot reach 50% coverage. Preserve the failure and denominator. Do not promote to holdout or scale just because the endpoint is cheap. A stop is an experimental result, not a reason to erase the run or keep rephrasing until it passes.

### S3: thirty-case prospective holdout

Run only if S2 passes. No fixture/prompt/threshold changes after S1. Same raw-accuracy, accepted-error, and coverage bars as S2. Holdout is independently authored but small and synthetic, not representative production data. Report family-level errors, confusion matrix, risk/coverage, Brier score, and one-sided exact binomial upper bound for accepted-error risk. Do not pool metamorphic variants or duplicate occurrences as independent samples.

### S4: invariance and actual Azdaja custody

If semantic promotion is blocked, offline structural custody checks can still run but cannot rescue semantic acceptance. Otherwise test option-order reversal, standalone versus shared-state questions (at most six questions), and irrelevant evidence padding on a frozen subset. Zero label or automatic-acceptance changes on unambiguous cases, and zero wrong auto-accepted decisions in variants. This acceptance check was tightened during pre-inference independent review. Report latency and billed tokens, not only HTTP count. The runner reports only `semantic_screen_passed` until a separate real CLI custody probe and comparative baseline have actually run.

Use Azdaja's real evaluator CLI to load complete synthetic source and a source-bound judgment receipt. Recompute source hashes, expand labels to every original occurrence in stable source order, preserve duplicate multiplicity, and reduce exact counts. A replayed oracle receipt validates custody only. A live receipt validates integration but does not prove the semantic labels correct. Any claim of end-to-end semantic correctness requires both checks.

### S5: comparative performance, not assumed

Only after semantic gates pass, run a bounded real generative-leaf baseline on the same frozen cases if an authorized available route exists. Include parse failures, abstentions, escalation work, retry budgets and timeouts. Promotion target: no observed accuracy regression and >= 2x measured end-to-end speedup OR >= 3x measured inference-cost reduction. If prices/usage/baseline are not comparable, mark this gate unmeasured, not passed. No production default or automated evidence deletion based on this pilot.

## Resource envelope

- Maximum 96 TypeSafe inference attempts for the entire initial campaign, sequential by default, no automatic retry.
- Maximum 64 KiB serialized request, 256 KiB response, 8 questions per request, 25-second wall-clock request deadline, 20-minute live campaign deadline.
- Maximum 1 MiB total serialized request bytes and 1,000,000 reported input tokens, stopping after the crossing response. These are local resource ceilings, not a guaranteed dollar cap because provider accounting must be verified. Freeze a conservative question-weighted input estimate before each call as an additional preflight.
- Public vendor input-price claim observed today: $42 per billion input tokens ($0.042/M). Do not assume an account's billing or output charges from marketing. Publish observed usage and labeled price-based estimates separately.
- Do not send repository secrets, real user notes, entire source trees or private documents. Tests use authored synthetic content.
- Authentication/rate-limit/overload/service failures stop the campaign. Do not hammer the service or silently consume another model.
- Every 30 minutes while active: reassess the falsifiable advantage, accumulated evidence, resource use, and next highest-information test. Cancel hopeless active tests. Stop reminders once this task is finished.

## Evidence and release bar

Commit fixtures, protocol, adapter/harness tests and scrubbed receipts, not credentials or unrelated dirty files. Record Git revision, fixture hash, question-policy hash, exact requested/returned model, source hash, attempt count, input/output bytes, latency, reported token usage, and every stop reason. Partial runs must remain partial. A cancelled stage is not a passing run.

Even 30 accepted decisions with zero failures have a roughly 9.5% one-sided 95% error upper bound under ideal iid assumptions. At least 299 independent zero-error acceptances are needed to push that bound below 1%, and distribution shift still invalidates naive guarantees. This campaign can reject an angle cheaply or justify a larger study. It cannot establish production-level safety or a moat.
