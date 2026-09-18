# Optional solo transport-failure acceptance

This closes a missing **engineering acceptance check**, not a newly discovered production defect. Jev and every Jev-dependent behavior remain optional and default-off. No product source, endpoint, credential handling, retry policy or dependency was changed.

## What actually ran

The new `tests/judge_solo_transport.rs` launches the real compiled `azdaja solo` command, uses its production HTTP client and checks its host-owned runtime footer. A local, stdin-draining Python fixture supplies the generated root program. macOS `sandbox-exec` denies network operations for the CLI and its children. Before admitting any typed program, TCP and UDP canaries must both fail with `EPERM`. Only a deliberately synthetic token is supplied, and the local generator asserts that it never receives that environment variable.

Consequently this is a real public-command **client transport-failure path**, not a successful TypeSafe response. Native `attempts=1` and `provider_requests=1` record entry into the production transport path while network access is denied. They do not distinguish initialization failure from `.send()`, prove upstream arrival, or establish a billable provider call. The host conservatively retains unknown usage rather than inventing known zero usage.

## Requirements and observed results

| Requirement or changed output | Concrete public check | Observed result |
|---|---|---|
| A present credential must not enable Jev | `disabled_solo_stats_stay_off_despite_a_present_synthetic_credential`, both builds | `enabled=false`, attempts zero, one local root and zero semantic children. |
| Model-controlled stats cannot authorize a result | `model_mutated_stats_cannot_forge_semantic_evidence`, both builds | Writing `successful_requests=99` and `attempts=99` into the returned dictionary does not affect trusted snapshots. FINAL is rejected for zero semantic evidence. Four bounded root invocations, all host attempt/success counters zero. |
| Preserve the legacy feature-off planner | Same test, explicit local planner markers | Feature-off runs exactly three local strategy probes before root execution. Optional mode runs none. The probes do not become semantic evidence. |
| Retain an uncaught entered-client failure | `actual_transport_failure_is_retained_and_never_automatically_repaired`, uncaught case | Terminal transport error, empty stdout, one executed cell, one root, no semantic child, one failed typed attempt and one unknown-input/unknown-output event. |
| Catching an error must not make FINAL eligible | Same test, caught case | FINAL fails the semantic gate. The attempted call and unknown usage survive in the trusted host footer. No root repair is attempted. |
| Do not automatically repeat already-attempted typed work | Both failure cases above | Exactly one root invocation and one typed attempt, with no repair after transport-path entry. |
| A generated retry cannot bypass poison | `catching_transport_failure_does_not_allow_a_second_attempt_in_the_cell` | Two caught calls still produce only one attempted transport-path entry. Engine remains poisoned; no successful request or cache entry. |
| Failure accounting and disclosure remain honest | `assert_failed_attempt` and `assert_no_secret` | Attempt, question, failure and unknown-usage counters equal one; known token totals, success and cache counters equal zero; input/output completeness false; elapsed positive. Synthetic value absent from stdout, stderr and traces. |
| Compose with the rest of the optional product | Five Cargo integration targets in both build modes | Default: 28 passed. TypeSafe: 33 passed. Targets cover credentials, native judgments, batch, hash preflight and these solo boundaries. |
| Installed features still work together | Existing public `bench/jev/batch_workflow/installed.py`, exact binaries in both modes | 23 checks per build pass, including disposable installation, restart-persistent attachment, default-off behavior, ordinary session lifecycle, no-key completed resume, ambiguous-inflight refusal, safe failures and source-exact exports/review queues. No new provider requests. |
| Test registration is platform-honest | `.github/workflows/ci.yml` | Feature-on transport tests explicitly run only on macOS, with a required OS-denial canary. The default full Cargo suite discovers the two controls on macOS. No Linux transport-denial claim. |
| No incidental production or package changes | Source diff, binary hashes, strict Clippy and formatting | Production and Cargo inputs unchanged. Both compiled binary hashes exactly match the previously accepted `2bce468` binaries. Strict all-target/all-feature Clippy and formatting pass. |

Raw composed logs, installed receipts, commands and source hashes are retained in `results-20260918/`. A read-only independent source review found no blocker, recommended the narrower transport-path wording above, and prompted explicit zero-planner assertions in the transport cases. The reviewer did not rerun Cargo. Hosted registration alone is not a passed run. Exact-revision hosted verification is pending at this local receipt and is checked after publication.

## Failures retained during test development

An initial capture command stopped before Cargo because the system Bash rejects an empty array under `set -u`. The portable Python capture runner replaced that shell wrapper. The first composed default-build run then exposed a **test-fixture omission**: legacy feature-off classification performs three strategy probes before the root, while the new fixture incorrectly forbade all non-root calls. Production behavior was not changed. The fixture now recognizes only the exact existing strategy contract and three role prefixes, records exclusive role markers, and asserts three probes in feature-off mode and zero in optional mode. Unexpected semantic children remain forbidden. The original semantic-gate and trusted-counter assertions were not weakened. The failing composed log is retained.

## Reproduce on macOS without a provider

```sh
cargo test --locked --offline --test judge_solo_transport
cargo test --locked --offline --features typesafe --test judge_solo_transport
cargo test --locked --offline --features typesafe \
  --test judge_solo_transport --test judge_solo_preflight \
  --test judge_native --test judge_batch_cli --test jev_credentials \
  -- --test-threads=1
```

The tests require `/usr/bin/sandbox-exec` and `/usr/bin/python3`. Missing or ineffective OS network denial is a test failure, never a reason to try an unrestricted connection. On other operating systems this test target has no tests.

## Readiness boundary

The optional supervised batch and review workflow remains the useful shipped path. These checks improve confidence in solo's refusal and accounting behavior. They do **not** establish successful remote typed-solo execution, calibrated judgments, useful autonomous planning, fault tolerance after process termination, Linux/macOS-equivalent sandboxing, or a long-task speedup. Historical failed live CUAD runs stay failed and unchanged. No additional live campaign, tag, release, user-install mutation or provider message is part of this slice.
