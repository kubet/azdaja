# Optional Jev foundation hardening, 2026-09-18

This slice hardens the shipped work-list runner. It does not promote autonomous planning, calibrated approval, memory/RAG, or the earlier research panels to production features. Jev remains optional and default-off. Attaching a credential does not enable it.

## Observed change

Two native regressions first failed because failed requests lost their cause. They now pass: categorical diagnostics survive a fresh no-key resume, arbitrary error text is not retained, and a failed request is never automatically retried. Historical completed records keep their original serialization. Historical failures lacking a diagnostic report `not_recorded`.

| Requirement | Concrete check | Observed result |
|---|---|---|
| Safe actionable diagnostics | `failed_job_keeps_safe_diagnostic_across_no_key_resume`, `failed_job_never_persists_arbitrary_error_text`, vocabulary/legacy/malformed tests | Red before, green after. HTTP status is numeric only. No provider text or credentials copied. |
| Existing safety and resource bounds | Native `judge` tests, default and `typesafe` builds | 34 and 33 passed respectively. Accounting, unknown usage, deadlines, source binding, crash intent, locks and private paths exercised. |
| Public option/config/credential boundaries | `judge_batch_cli`, `judge_native`, `jev_credentials`, both builds | 23 tests passed in each build. Fresh config-free preflight succeeds. An explicitly missing config override still fails closed. |
| Features work together after installation | `installed.py`, actual private `install claude` and fresh processes | 20 commands passed in each feature mode, including disabled-but-attached refusal, ordinary session use, detach and uninstall. Installed bytes equal supplied binary. |
| Existing paid work is reusable | Installed native resume of retained 138-request job, without a key | All 138 reused, zero requests, durable job bytes unchanged. Feature-off binary can also validate completed observations. |
| Ambiguous work cannot be rebilled automatically | Actual installed resume with last result removed in a disposable copy | 137 completed, one unresolved, zero requests. No credential resolution needed. |
| Failure replay is backward compatible | Public synthetic HTTP429 envelope, legacy missing diagnostic and invalid-field mutation | Stopped with safe category, legacy `not_recorded`, malformed metadata rejected. These mutations are not claimed as live transport failures. |
| Export preserves evidence | Complete and partial review export after native replay | Full output remains SHA256 `3298a9791b4bf8f36f4ae988452ce0a48c3d151fb15bbb85b473b135d813ff41`. Partial output includes all 138 windows, with the missing result unknown. |
| Command discoverability | Exact `e2e` help/usage test through `az` and `azdaja` | Updated stale credentials-only fixture to check batch help and explicit opt-in. Previous hosted failure is retained, not called a product transport failure. |
| Python/output portability | Python 3.9, preparation/export/replay/installed boundary tests | 20 passed. Existing and dangling outputs refused. Private copies use 0700/0600. |
| Build/package integrity | Strict all-target/all-feature Clippy, rustfmt, exact Cargo package list | Checked separately before publication. No dependencies added. |

No new inference was needed. The earlier successful live 138-request receipt remains the transport/usefulness evidence. This pass verifies lifecycle and integration behavior, not a new accuracy measurement. Native failure creation uses the existing injected transport seam. Current public replay uses real retained observations and explicitly labeled synthetic failure envelopes.

## Reproduce against a current binary

```sh
cargo test --locked --features typesafe --lib judge
cargo test --locked --features typesafe --test judge_batch_cli --test judge_native --test jev_credentials
python3 -B bench/jev/batch_workflow/installed.py \
  --binary target/debug/azdaja --output /absolute/new-private-output
```

Repeat with a default-feature build. The command installs only into an exclusively created private HOME, uses synthetic credentials, reconstructs the attributed public corpus, exercises actual public commands, and uninstalls its copy. It does not replace the user's installation or read real provider credentials.

The CI workflow runs this path in both feature modes on Linux, Apple Silicon and Intel macOS. A workflow definition is not a passing hosted result. Publication remains source-only, with no release or tag implied.
