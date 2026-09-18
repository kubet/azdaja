# v0.1.18 optional Jev activation and release contract

User-authorized patch release. Jev remains optional. No live inference campaign or mutation of the user's installed binary is part of this work.

## Activation policy

`judge.enabled` is tri-state. Omitted means auto. A locally valid credential for the exact configured `key_env` activates the optional engine at a later execution boundary in a TypeSafe-capable build. No usable key or no compiled transport leaves auto off. Explicit false always wins, including old development configurations. Explicit true preserves the existing explicit-mode path. Published v0.1.17 stock configuration has no judge section and therefore naturally enters auto mode on upgrade. No config migration may erase a user's false setting.

Environment presence is authoritative, including invalid, empty and non-Unicode values. It must never silently fall back to an attached key. Attachment is still private plaintext, not a vault. Local syntax validity does not authenticate a provider. No setup, inspection, help or discovery call may make inference. Batch execution still requires `--execute` and explicit limits. No new fallback, retry, threshold or automatic approval is added.

## Requirement-to-observation map

| Requirement / public output | Concrete acceptance path | Required observation |
| --- | --- | --- |
| Raw configuration is credential-free | Config serde tests and invalid config/discovery CLI tests | Omitted/true/false roundtrip distinctly, no state creation |
| Automatic environment activation | Actual start/exec/final/kill with synthetic named keys | Host `judge_stats().enabled` follows build and local key validity with zero attempts |
| Persistent attachment and detach | Actual attach/status, fresh CLI invocation, exec, detach | Auto follows retained key then turns off, config bytes unchanged |
| Explicit false and custom names | Actual CLI with attached and environment keys | False wins, only configured name considered, invalid override does not fall back |
| Exclude unproven automatic solo use | Actual solo with stdin-draining local root fixture, plus direct SoloSession API | Auto with a key preserves old contract, only explicit true advertises typed API when compiled, feature-off says unavailable, synthetic key not forwarded |
| No automatic spending | Help/caps/offline batch and missing-approval/limits cases | No provider attempt or batch intent created |
| Old completed/ambiguous jobs | Current installed.py with retained native jobs | Completed resume makes zero new requests, ambiguous intent is never retried |
| Batch/primitive composition | Native engine, batch, credential, solo preflight/transport suites plus installed exporter/queue | Existing source bindings, budgets, failure/unknown accounting and secret boundaries hold |
| Official binaries have optional transport | Both feature-flavor builds and exact release candidate `doctor --caps` | Feature-off false, official candidate true, neither probes readiness |
| Existing no-Jev product workflow | Real full Cargo suite, 50 MiB product test, installed lifecycle | Ordinary paths still work with no key or explicit off |
| Packaging and notices | Exact Cargo package list, source-backed notice verification, proof reproduction | All current inputs bound, historical evidence unchanged |
| Publication | Exact-source candidate dispatch, receipt promotion, main/tag CI, release workflow, channel verifier | Asset-only promotion, exact bytes/architectures, non-overwriting publication and download equality |

## Stop and release rules

Synthetic/local tests are not new provider success or quality evidence. Keep old empirical results and failures frozen. Reject a release on failing acceptance, mismatched binary flavor, unsafe publication inventory or missing required CI. A tagged release uses only reviewed workflow-dispatch artifacts, never a locally substituted binary. Promote from a clean disposable checkout because unrelated untracked user files must remain untouched. Stage candidate source on a separate remote branch so the public installer does not advertise unpromoted assets. Finish with exact main/tag gates, publication attestations and downloaded-asset verification. Runtime changes, release source and proof bindings must be committed before candidate dispatch.
