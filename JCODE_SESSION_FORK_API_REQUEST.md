# Upstream request: isolated session fork from a static prefix

## Problem

Jcode v0.75.3 (source commit `fd1ff012cd463c413d53a3de358ceb7a7b8459a2`) offers provider continuation inside one session, but not an operation that branches an immutable static prefix into isolated child sessions. Reusing one live session leaks prior task content between requests. Rewind restores isolation only by clearing the provider session identifiers and resending the truncated context. On the OpenAI OAuth/ChatGPT route, Jcode also omits the prompt-cache key and retention fields, so a stable keyed-cache workaround is unavailable.

## Requested API

Add a capability-detected operation resembling:

```text
fork_session(parent_session_id, at_message_id | at_history_index) -> child_session_id
```

Required semantics:

- The child inherits exactly the immutable prefix ending at the requested boundary.
- Each child has an independent mutable suffix. A turn in child A is never visible to child B or the parent.
- Forks may execute concurrently without suffix ordering or cancellation coupling.
- Rewind/clear applies only to the addressed child.
- The response reports whether the provider actually reused a server-side prefix and, when available, the reused/prefilled token count. Silent fallback to a full resend is not acceptable.
- Provider or daemon restart behavior is explicit: either forks remain valid, or use returns a typed `session_expired`/`fork_unsupported` error. Do not silently turn a fork into a cold full-context request.
- Lifecycle controls expose expiry, close, retention, and bounded resource use.
- Providers that cannot guarantee these semantics return `fork_unsupported`; Jcode must not emulate a fork by sharing an ordinary continuation session.

## Acceptance tests

1. Create a parent with a fixed contract and receive `READY`; fork children A and B at that boundary.
2. Plant a unique marker in A. Ask B for that marker; B must return the contract-defined absence result, with no A content in B's request, history, trace, or provider state.
3. Mutate and rewind B; parent and A remain unchanged.
4. Run A and B concurrently and prove stable, distinct provider session identities.
5. Restart the Jcode service. The next child call must either preserve the documented fork or return the typed expiry error—never silently resend while claiming reuse.
6. Emit auditable reuse telemetry and show that a positive reused-prefix count corresponds to provider evidence, not a local estimate.
7. Repeat the isolation test under error, cancellation, timeout, compaction, and child-close paths.

This capability would permit a warmed static contract without cross-task contamination. Until it exists and passes these tests, Azdaja will keep cold, fresh sessions and treat warm-daemon/prefix reuse as a hard NO.
