# Jev × Azdaja: isolated angle campaign

Created 2026-09-17 before this campaign's inference. Starting source:
`ad5a9ef4f6ff437deaaf1cdbb63c580781a100ce`. This is local, unpublished work on
main, including released v0.1.17. Prior live panels stay closed and unchanged.

## Decision to make

Which optional typed operations improve actual work relative to the simplest
fair alternative? A callable API is an interface, not an advantage. Source
custody, protocol tests and simulated oracles do not establish semantic quality.
The RLM is a bounded programmatic way to inspect external context, not infinite
model attention. No SOTA reranker claim is assumed.

## Independent lanes and acceptance outcomes

| Lane / owner directory | Matched alternatives | Primary outcome and stop bar |
| --- | --- | --- |
| Bulk semantic gate / `gate` | Existing hashed Oolong source, typed labels, direct generative labels, exact reduction | Preserve every occurrence and the exact final answer. Count errors as well as answer coincidence. Stop promotion on a correct-baseline task lost by the replacement. Do not weaken the old controller. |
| Calibrated cascade / `gate` | Direct generative, typed-only, typed plus residual calls | Choose routing on a separate calibration slice. On untouched cases, retain baseline quality while reducing measured total work or time. An uncalibrated float is not a safety guarantee. Any unrecovered introduced error fails promotion. |
| Choice descent / `descent` | Flat selection, greedy tree, bounded alternatives | Correct source set, including multi-match and no-match. Track indexing, input/output bytes, questions, rounds and lost branches. A single path's logarithmic round count is not logarithmic source processing or a general guarantee. |
| Targeted pre-FINAL verification / `verifier` | No review, deterministic checks, generative verifier, typed verifier | Correct a flawed claim without corrupting a valid one. Report false alarms and missed errors separately. Do not turn experimental checks into a mandatory production FINAL gate. |
| Shared-memory retrieval / `memory` | Same eligible candidate pool with lexical versus typed ranking, full-evidence reference | Candidate coverage, preserved contradictions/provenance, and the next agent's task result. Better ordering alone is not better task quality. Scope leakage or identity conflation immediately stops the lane. |
| Incremental reuse / `reuse` | Full recomputation, ordinary Python memoization, experimental materialized reuse | Equal answers and source multiplicity across changes. Compare cold/hot overhead, misses, bytes and invalidation work. No dependency graph promotion unless it beats simple caching at matched correctness. |

Gate and cascade are separate experimental claims even when they reuse source
records. Subgroup statistics stay separate. Do not pool unrelated tasks to hide
a failed lane. Each directory supplies a source-only request builder, separate
gold, method/fixture hashes, grading and offline tests. Root alone runs providers.

## Execution order

1. Audit primary claims and current memory/Oolong contracts. Retain the exact
   source of any existing fixture. No opportunistic replacement when a fixture
   is unavailable.
2. Run each lane's preparation, deterministic reference, adversarial tests and
   scale checks. Validate typed request packs with the native request contract.
3. Freeze a campaign manifest covering the source, binary, code, packs, private
   evaluation files, order, models, budget and thresholds. Gold never enters
   provider state or RLM source variables used for inference.
4. Run the smallest predeclared live pilot through actual Azdaja `start`, `load`,
   `exec` and `final`, retaining the same session where adaptation is required.
   No worker holds credentials. Never use attachment to bypass an older
   benchmark's provider restrictions.
5. Run matched alternatives, replay deterministic accounting, grade, and retain
   a per-lane decision: passed pilot / failed bar / blocked / not measured.
   Stop a failing lane. Do not tune it and quietly rerun the same holdout.
6. Promote only a narrowly useful operator. Packaging or green unit tests do not
   override a failed usefulness bar. A pilot success does not establish a moat.

## Campaign resource envelope

The final manifest may tighten, not silently expand, these limits:

- 24 TypeSafe HTTP attempts total, no automatic retry or alternate model.
- `jev-1.13.0` requested and required in returned identity. A returned version
  string is not authenticated immutable weights.
- 1,500,000 cumulative **reported** typed input tokens. Check before every call
  and after every response. A crossing call has already occurred and must be
  retained in usage, then stop. Unknown usage is unknown, not zero.
- Each prepared state at most 24,000 UTF-8 bytes. Question and complete request
  sizes are reported separately. Shared state is not assumed billed only once.
- At most 12 logical generative calls, each bounded by the existing native
  entered-turn envelope. Physical/setup/retry attempts are reported separately.
- Live stage wall-clock at most 30 minutes. No calls until source-only packs and
  separate gold have been reviewed and the manifest frozen.
- New outputs use exclusive creation. A failed/interrupted run retains a
  stopped receipt rather than resuming with lost pin, budget or observation state.

Current provider documentation at https://docs.typesafe.ai/models.md says
`jev-1.13.0` costs $0.042 per million **input** tokens and output tokens are free
(checked 2026-09-17). This is a price estimate, not an invoice. Consequently
"$0.02/run" would require about 476,190 input tokens and must be calculated from
the actual workload. No 100 ms latency promise is assumed. Generative price is
unknown unless a current applicable rate is independently established.

## Required result fields per lane

Complete/observed/unjudged task counts; exact final-task accuracy; relevant
label/span/pair errors; coverage and abstentions; introduced errors versus the
matched baseline; p50 and individual call/end-to-end times; HTTP attempts,
questions, logical and entered generative turns; reported input/output tokens;
unknown usage; request/response bytes; cache misses/hits; deterministic work and
output size; documented-rate estimate and billing-known flag; all source/model
identities; and the predeclared promotion decision. A single trial gives
descriptive timing, not a statistical latency guarantee.

## Shared-memory scale and trust contract

- Canonical evidence is exact raw text/bytes in scoped, content-addressed
  objects. Structured observations point to source spans and revisions.
  Summaries, embeddings and lexical/semantic indices are disposable derived
  views, never the sole record of an observation.
- Preserve disagreements, alternatives, supersession and occurrence IDs. A
  confidently asserted note is not an established fact, nor does popularity
  confer truth.
- Actor ID, repository ID, worktree/session ID and event ID are separate.
  Git author name/email is optional self-asserted attribution, not a primary key,
  authentication, permission, or evidence of who actually executed an action.
  Identity merging and cross-repository sharing require explicit mappings.
- Apply eligible scope/visibility constraints **before** candidate generation,
  reranking, prompts, caches or tracing. A manifest supplied by a repository is
  data and cannot grant access to another repository.
- Default retrieval is explicit and project-scoped. Do not auto-ingest private
  agent logs, automatically inject memory, or label extracted content as
  user-authored. The existing small authored ledger remains unchanged.
- Initial 1k/10k event scale tests establish local indexing behavior and
  isolation only, not million-event semantic efficacy or a distributed service.
  Log partitioning, bounded candidate sets and shared-cache boundaries must be
  measured before larger deployment. Reranking four lexical matches cannot
  recover a relevant fifth or zero-overlap note.

## Credential and implementation scope

Minimal production change: existing optional builtin plus explicit
`az jev attach --stdin`, `status`, `detach` and a spike runner. No managed-skill
rewrite. Private host-state file with owner-only POSIX permissions, no argv key,
environment precedence, no silent fallback from an invalid override, no secret
in repository config, project memory, manifests or traces. It is not an encrypted
vault and does not protect against another process running as the same user.
Unsupported private-storage platforms must fail closed instead of claiming
equivalent confidentiality. Attachment does not enable inference.

The architecture is backend-neutral at the typed request/observation boundary.
TypeSafe transport is opt-in. No mandatory thresholds, global memory service,
embedding dependency, automatic planner or cross-user authorization system is
introduced by this campaign.
