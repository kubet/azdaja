# Native typed capability discovery, 2026-09-17

## Concrete usability gap and repair

The actual `azdaja doctor --caps` command did not advertise the native typed API, even in a `typesafe` build. The managed skill already named `judge_many` and `judge_stats`, but a caller inspecting machine-readable capabilities could not discover them or distinguish an API-bearing default build from one with the optional HTTP transport compiled.

A new public CLI regression **failed before the fix** on the missing `native-typed-judgments` capability. Source commit `6b1139e86af8d18365232b7f57f9b9aa1352f6cb` adds static metadata, its regression and guidance. It changes no transport, inference policy, model, threshold, cache implementation, managed skill, or activation hook.

```json
{
  "typed_judgments": {
    "functions": ["judge_many", "judge_stats"],
    "typesafe_compiled": true,
    "enabled_by_default": false,
    "host_opt_in_required": true,
    "runtime_configuration_checked": false,
    "credentials_checked": false,
    "cache_and_budget_scope": "cell"
  }
}
```

This is **capability discovery, not provider readiness**. The default build reports `typesafe_compiled: false`; the API names still exist, including zero-request accounting. A feature-enabled build reports `true`, but it does not assert that the host enabled inference, supplied a key or has provider access. An older build with no such metadata is unknown, not automatically ready.

Use **`doctor --caps`**, not bare `doctor`, for this provider-free operation. Bare `doctor` is a different diagnostic path that can make a model canary call. The capability branch does not load user configuration, inspect credentials, create state, start a session or call a provider.

## Actual acceptance and requirement map

The clean source above completed 19 acceptance stages. Its actual privately installed all-feature debug binary was SHA-256 `455846f6e613463e96a7e37e4b5ed0541a9cfc90502f60b20c98c13d367d9546`.

| Requirement / output | Concrete observation |
|---|---|
| Machine-readable API discovery | Actual default and feature-enabled CLI outputs contain `native-typed-judgments`, both function names and the per-cell scope. The retained before-fix regression fails at the missing capability. |
| Distinguish compiled transport from enablement | Default output reports compiled `false`; an actual private feature-enabled install reports `true`. Both retain default-disabled, host-opt-in-required and unchecked runtime/credential fields. |
| No configuration side effects | The public test invokes the command with malformed and nonexistent config paths. Both succeed with identical stdout and no new HOME, state directory or config file. |
| No secret disclosure or provider probing | The test uses only a distinctive synthetic environment value, which never appears in stdout/stderr. The production branch constructs static JSON before configuration loading. No real credential or provider was used. |
| Existing native use and recovery | All six `judge_native` tests pass in each feature mode, including default-off rejection, missing feature/key, argument errors, regular execution recovery, config round-trip and generative-child credential isolation. |
| Installed public interface | Real install into a new HOME containing spaces, binary byte equality, `doctor claude`, `doctor --caps`, persistent offline workflow, 30 native/result checks, two separately enabled installed-memory tests and actual uninstall all pass. Private install removed. |
| Whole source and distribution boundaries | Clean `cargo +1.95.0 test --locked --offline --all-targets --all-features --no-fail-fast`: **659 passed, 0 failed, 5 ignored**. Strict Clippy, rustfmt, verified Cargo package compilation, source-backed notice and retained-history proof commands all pass. |
| Preserve previous evidence and user work | The preceding accepted `7fbbc3bc…` binary was copied and hash-checked before rebuilding. All original 25 files retain bytes/modes, the prior 123 asset/license files remain unchanged, and all frozen study binaries keep their identities. No push or live user-install update. |

Two of the five ignored tests were subsequently executed against the real private install and passed. The remaining exclusions are release-only 16M-character stress, release-only 50 MiB acceptance, and frozen Luna pilot input preparation. This is local macOS ARM64 debug acceptance, not hosted CI, cross-platform runtime, legal-sufficiency approval or release authorization.

## What this does not prove

This closes a concrete API-consumption gap. It does not demonstrate that an autonomous RLM uses the primitive well, or improve the measured semantic scores. The closed live source-selection study remains **17/18 versus 18/18**, with a failed quality-preserving benefit bar. The earlier seven-task answer study remains a no-gain result. There were **zero new inference calls** in this follow-through, no new cutoff and no favorable rerun.

The [prior whole-result report](jev-final-followthrough-20260917.md) and [application-angle report](jev-angle-of-attack-20260917.md) retain their original source-specific conclusions. The [new machine-readable receipt](jev-native-discovery-20260917.json) binds this different source and binary to [its own retained logs](../../bench/jev/results/native-discovery-20260917/). Only local absolute path prefixes are redacted in retained copies; original and retained hashes are both recorded.
