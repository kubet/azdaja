# Shared agent memory: product plan

## Outcome, not capacity

A fresh agent should recover a project's relevant decisions, failed approaches,
and unresolved disagreements without rereading every old conversation. It should
know what to verify, not inherit a previous agent's unsupported certainty.

The product hypothesis is **less repeated work at equal or better correctness**.
Compression ratios, agent counts, context capacity, and GitHub stars are not
evidence that this hypothesis holds. Adoption should follow demonstrated value.

## Current foundation and next increment

`src/memory.rs` already provides bounded, scope-separated JSONL notes, manual
provenance, typed relationships, and concurrent appends. Its note kinds include
decisions, observations, failures, hypotheses, and disagreements. This is not yet
a portable, repository-local `.azdaja` object store or an automatic learning system.

The first increment is deterministic, read-only recall over that existing store.
It must return identifiable notes and their relevant relationship context, keep
contrary and superseding notes visible, and state any output omissions. Lexical
relevance is a retrieval heuristic, not a confidence score or a truth judgment.
No model call or schema migration is needed to test this increment.

Acceptance requires fresh-process CLI tests for matching and no-match queries,
stable ordering, explicit global scope, foreign-scope isolation, invalid inputs,
bounded output, corruption refusal, and unchanged persistent state. A related
disagreement that does not share the query words must still be discoverable.

## Try the recall increment

```sh
azdaja memory add decision "Keep the metadata cache bounded"
azdaja memory recall "metadata cache"
azdaja memory recall "metadata cache" --global
```

`recall` emits one versioned JSON object, not a model-generated answer. `matches`
contains primary notes, and `context` contains incoming and outgoing one-hop
neighbors. Each item includes the full stored record and its backlinks. Manual
provenance is preserved. The global ledger is separate, never implicitly merged
with the current folder's notes.

Matching uses distinct case-insensitive Unicode alphanumeric words in note text
and tags, without stemming or semantic inference. Repeating query words adds no
weight. Ties prefer newer notes, then ascending IDs. Context prioritizes
disagreement notes and incoming supersession for inspection, not credibility.

Queries allow 256 Unicode scalar values and 32 distinct words. Replies contain
at most four primary and eight context records within 64 KiB of compact JSON,
including the trailing newline. Records are omitted whole, never silently
truncated. `omitted_matches` counts matching records absent from both arrays,
and `omitted_context` counts eligible one-hop context records not returned.
Inspect remaining IDs with `memory show` or refine the query. Empty results mean
no lexical match, not that a claim is false. Treat stored text as untrusted data.

## Proposed portable `.azdaja` layer

This section is a design target, not a description of shipped functionality.

- Store curated claims, decisions, outcomes, and evidence references. Do not
  collect private reasoning traces, complete conversations, credentials, contact
  lists, or absolute machine paths by default.
- Use immutable, versioned, content-addressed objects. Keep rebuildable indexes
  separate from authoritative evidence. Two writers should add objects rather
  than compete to replace a single shared summary file.
- Bind evidence to a repository-relative location plus a content digest or
  commit. A content digest detects change, not honesty. Missing or changed
  evidence is stale or unavailable, not silently verified.
- Preserve attribution and derivation. Ten agents repeating one source are one
  evidence lineage, not ten independent confirmations. Keep conflicting claims
  until a check resolves them. Supersession preserves history.
- Make sharing explicit. A reviewed export should be inspectable before it is
  committed or transferred. Import must validate versions, sizes, digests,
  relationships, and path safety before publishing any state. Imported text is
  untrusted data, never an instruction to execute tools.
- Support idempotent union and deterministic conflict reporting before adding
  synchronization services. Test duplicate imports, concurrent writes, interrupted
  publication, cycles, missing references, corruption, and a fresh checkout.
- Add compression only after measuring real payloads. Bound decoded sizes and
  expansion ratios. Packing is transport optimization, not the memory contract.

The defensible capability would be **auditable reuse of project experience across
contexts and collaborators**, not a new file extension or another summarizer.

## Evaluation before claims

Build a fixed, versioned set of project tasks covering decisions, changing facts,
known failure modes, contradictory advice, and questions with no supporting
evidence. Separate fixture authoring from held-out evaluation. Never put expected
answers in a model-visible memory packet.

Compare four conditions with the same task, model, tool access, and budget:

1. Fresh agent without history.
2. Ordinary hand-maintained project notes.
3. Raw history available through the existing virtual-memory workflow.
4. Curated notes plus bounded, evidence-linked recall.

Measure task correctness with executable checks where possible, repeated failed
actions, stale-claim acceptance, unsupported answers, retrieval omissions,
latency, and model usage. Keep per-task receipts and all failures. Run provider-free
storage and CLI checks first. A scripted provider proves plumbing, not model
quality. A cheap-model pilot must pin and verify the actual model, cap calls and
spend, and report uncertainty before any broad benchmark or release claim.

Relevant research motivates these checks but does not establish Azdaja's results:

- [LongMemEval-V2](https://arxiv.org/abs/2605.12493) evaluates static recall,
  dynamic state, workflow knowledge, environment gotchas, and premise awareness.
  Its context-gathering formulation is close to the proposed product outcome.
- [Demystifying Multi-Agent Debate](https://aclanthology.org/2026.findings-acl.1694/)
  examines diversity and calibrated confidence. Its findings caution against
  equating homogeneous agent agreement with independent evidence.

## Ownership and delivery

Each development cycle should advance one measured product bottleneck, record
the check and result, and leave a precise next action. A heartbeat is an execution
aid, not evidence that unattended work ran successfully. Do not repeatedly burn
model calls on an unchanged blocker.

Commit scoped verified work. Release only after applicable exact-commit CI,
artifact, installation, and privacy checks. Never publish raw local memory as a
side effect of releasing the tool. Demonstrate the fresh-agent workflow before
asking people to adopt it, then use real user failures to choose the next task.
