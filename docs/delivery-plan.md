# Executable delivery plan

## Outcome and priority

Deliver inspectable memory that helps a fresh agent or developer finish real work, then ship it through verified release gates. A larger memory store, more tests, or more stars alone is not proof of usefulness.

Work order: **finish the current worktree acceptance, implement deliberate cross-developer transfer, measure usefulness, and release through the existing integrity gates**. Release-access work can proceed in parallel. A blocked lane must not cause another unchanged green suite to be run as substitute progress.

## 1. Curated local memory foundation

**Status:** implemented. Project memory is available by default in a Git worktree when neither project-mode nor authoritative legacy-home overrides are set. Recording remains explicit.

- Preserve manual provenance, exact note text, file tags and relationships.
- Keep personal global, legacy scoped and project stores separate.
- Bound lexical recall and expose omissions and contrary context.
- Keep filesystem custody, corruption refusal and concurrent-write acceptance.

Existing acceptance targets: `project_memory`, `memory_recall_contract`, `memory_recall_paths`, `memory_recall_reliability`, `memory_recall_review`.

## 2. Real Git worktree and clone acceptance

**Status:** both optimized tests passed. The integrated formatting, strict all-target Clippy and full optimized Cargo suite passed, followed by strict compilation/lint checks for Linux x86_64 and Intel macOS. Those cross-target checks are not foreign-platform runtime results.

Owned file: `tests/project_memory_worktrees.rs`.

```bash
cargo +1.95.0 test --locked --release --test project_memory_worktrees -- --nocapture
cargo +1.95.0 clippy --locked --test project_memory_worktrees -- -D warnings
```

Exit checks:

1. A real linked worktree uses a `.git` file, not a fabricated repository marker.
2. Its nested-directory recall works across fresh processes and separate personal HOMEs.
3. Notes do not silently cross from the main worktree into the linked worktree or back.
4. Exact text, file tags, manual provenance and nonmatching linked disagreement survive handoff.
5. Recall preserves project-store directory entries, file types, modes and bytes.
6. Ordinary Git staging and cloning exclude the private `.azdaja` contents.
7. Cold clone recall creates no project store. An explicit new note enables a subsequent cross-HOME handoff.
8. Provider tripwires remain untouched. These tests are Unix runtime coverage, not Windows runtime proof.

## 3. Deliberate cross-developer transfer

**Status:** not implemented. Local worktree handoff is not cross-clone synchronization. This is the next missing part of the shared-wisdom goal.

Implementation order:

1. Define a versioned, size-bounded transfer envelope and exact validation rules before exposing a CLI.
2. Make export an explicit selection of notes with an inspectable relationship/context manifest. No automatic upload, Git staging, personal-global inclusion or transcript extraction.
3. Define how dependent links are preserved without silently dropping contrary evidence or exporting unrelated records. Refuse an incomplete transfer unless incompleteness is explicit in the contract.
4. Validate import without writing first. Make applying a reviewed import explicit and atomic.
5. Preserve original evidence and mark imported provenance as asserted/untrusted, not independently verified or locally authored. Do not invent a new provenance value without a compatible schema plan.
6. Treat identical repeat imports as idempotent. Reject conflicting contents under the same identity, unsupported schemas, dangling required links, unsafe files and capacity overflow without rewriting prior history.
7. Integrate through existing custody and validation primitives after exact source review. Do not implement a second independent ledger or parser merely to avoid that review.

Required E2E: export in repository A, import in an ordinary clone B with a different HOME, then recall exact evidence and disagreements in a fresh process. Include dry-run no-mutation, duplicate import, conflicting identity, corrupt/oversized bundles, interrupted write recovery and explicit global-scope isolation. Proposed transfer commands must not be documented as existing until implemented and exercised.

## 4. Measured usefulness and performance

**Status:** the earlier exploratory Luna pilot found no demonstrated gain. The latency diagnostic remains unexecuted. Neither is positive product evidence.

Before another model trial, freeze the source revision, task corpus, actual CLI-derived memory inputs, provider/model route, budgets, ordering, scoring and stopping rules. Use executable task correctness as the primary outcome. Include stale notes, conflicting notes, irrelevant notes and tasks where abstaining is correct. Count memory retrieval and verification overhead in the assisted arm's budget.

Report every arm, timeout, tool failure and protocol deviation. Separate outer tool calls from nested requested actions. Do not claim a causal improvement from unmatched revisions or a tiny convenience sample. No additional subjects should run until the existing protocol and execution path can be followed honestly.

Run the existing latency diagnostic only through an allowed path. Record binary identity, corpus sizes, fresh-process median/p95, response sizes and subprocess overhead. Timing a copied reimplementation is not CLI performance evidence.

## 5. Installed artifact and release

**Status:** HTTP-installed current-build memory acceptance passed at `ae1b23a`. Candidate notes are prepared in `release/v0.1.15.md`. A new release is not published.

1. Resolve the normal integration-upgrade/access blocker without disabling guards or reusing consumed challenges.
2. Review the intended unpublished history and all publication paths for private or unrelated content.
3. Update candidate version metadata consistently. Never rewrite historical version assets or the existing v0.1.14 tag.
4. Pass exact-source CI, Cargo source installation and the explicit installed-artifact workflows.
5. Build platform candidates through the existing workflow, then promote reviewed artifacts using its source-SHA/run-bound provenance procedure.
6. Pass the immutable final tag's CI and source-install gates.
7. Verify attestations, uploaded byte equality and public install channels before declaring the release complete.

Full local gate after a relevant code or acceptance change:

```bash
cargo +1.95.0 fmt --all --check
cargo +1.95.0 clippy --all-targets --all-features --locked -- -D warnings
cargo +1.95.0 test --locked --release --all-targets
```

The two explicitly ignored `installed_project_memory` workflows require a genuine separately installed executable. Test enumeration or a Cargo test-built binary is not a substitute. Local HTTP installer acceptance also does not substitute for remote release provenance.

## 6. Earn adoption

After release, publish a runnable two-agent handoff example and a clear statement of limits. Demonstrate a completed task rather than advertise memory capacity. Invite opt-in feedback on successful installation and completed handoffs before optimizing for stars. No implicit telemetry, fabricated benchmark claims, automatic HN posting or publication of private evaluation artifacts.

Candidate differentiation is reliable evidence reuse, explicit conflict handling and lower repeated-work cost. It is not an established competitive advantage until real outcomes support it.

## 7. Ownership loop

Maintain one renewing 30-minute heartbeat. Each wake checks active work and prior receipts first, advances one unmet acceptance requirement, and records exact commands, outcomes, file scope and blockers. Keep blocked lanes visible while advancing genuinely independent work. Do not present scheduled work as currently running work.
