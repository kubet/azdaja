# Optional solo native-hash preflight, 2026-09-18

This is a narrow reliability repair to an **optional** workflow. It is not a new model-quality experiment, an automatic approval mechanism, or evidence that autonomous long-task planning is production-ready. Jev remains default-off. Credential attachment does not enable it.

## Concrete before and after

The actual `azdaja solo ... -f SOURCE` command previously executed one local child read, then failed on `sha256(ctx.encode('utf-8')).hexdigest()`. The retained before log records exit 2, one root call and one child call. Native `sha256` accepts text and already returns hexadecimal text.

With the repair, the same invalid generated program is rejected before its cell executes. The existing bounded root-repair path receives the error. The corrected program succeeds with **two root invocations, one child invocation and one executed cell**. Its answer matches an independently computed SHA-256 and the complete 1,605,632 UTF-8 source bytes / 1,507,328 characters, including Unicode and CRLF. There is no silent code rewrite and no replay of a cell after a child has run.

These are real compiled CLI integration tests using an explicit local, stdin-draining model fixture. The fixture deliberately supplies the correction. This proves the execution boundary, not that a remote model will always repair itself. No new remote inference was performed, and the historical failed CUAD campaigns remain failed and unchanged.

## Requirement-to-observation map

| Requirement or changed output | Concrete check | Observed result |
|---|---|---|
| Prevent the known post-read hash failure | `optional_hash_contract_is_repaired_before_any_child_read`, actual public CLI | Failed before the production edit. Passes after, with exact full-source hash and length, two roots, one child, one executed cell. |
| All Jev behavior stays optional | `disabled_and_feature_off_preserve_legacy_execution`, both build modes | Default-disabled and enabled-but-feature-off modes retain the old execution and failure behavior. No new diagnostic or extra root turn. |
| Valid work and source-like text remain valid | `valid_hash_and_source_like_literals_work_in_both_modes` | Correct native hashing succeeds in both modes. Comments and string literals containing the bad expression are not treated as code. |
| Do not repeat already-performed work | `unrelated_failure_after_a_child_is_not_automatically_replayed` | A cell that fails after its child stops with one root and one child. The supplied repair is not invoked. |
| Keep the existing bounded repair policy | `persistent_bad_program_stops_at_existing_root_limit_without_children` | Four root attempts, zero children, zero cell executions, terminal failure. |
| Reject before any typed callback | `known_hash_failure_never_enters_prior_typed_callback` | An invalid program with `judge_many` before the hash is rejected before execution. Only the corrected cell executes. Trusted typed attempts and evaluation wall time remain zero. |
| Syntax-aware, conservative lint | Six `solo_preflight::tests` functions | Known direct mistakes rejected. Valid literals/comments, actual versus escaped f-string expressions, unknown types, 40 shadowing/dynamic cases, dead-code policy, parser errors and traversal bound tested. |
| Preserve current semantic gates and command behavior | Full `--bin azdaja` tests in both feature modes | 90 optional and 84 default tests pass, including existing solo gate, prompt and repair tests. |
| Compose with native judgments, credentials and durable batch | `judge_native`, `judge_batch_cli`, `jev_credentials`, plus judge core tests | Public boundaries pass in both builds. Optional judge/core tests: 33 passed. No live transport calls. |
| Installed features still work together | `bench/jev/batch_workflow/installed.py`, current binaries in both modes | 23 checks per build pass, using a disposable actual installation, synthetic credentials, ordinary session lifecycle, exact retained 138-result resume and ambiguous-result refusal. Zero new requests. |
| Package and dependency integrity | Exact Cargo package listing, locked dependency and notice comparison | 33 package files. Ruff 0.0.3 was already locked through Monty. Only two direct optional dependency links were added. Package versions/checksums, feature-union membership and legal bytes are unchanged. |
| Formatting, warnings and source-backed notices | `cargo fmt`, all-target/all-feature strict Clippy, notice verifier and three notice test modules | All pass. Notice manifest/lock hashes are rebound, not historical notice content. |

The same public integration targets are registered in hosted CI for Linux, Apple Silicon and Intel macOS. A registered workflow is not evidence that it has run. Exact-revision hosted results are checked separately after publication.

## Deliberate limits

- The lint is enabled only with the `typesafe` build feature **and** `[judge].enabled = true`.
- It is not a Python typechecker, security sandbox, or general cost guard. Monty still compiles and executes the program.
- It checks direct native result `.digest`/`.hexdigest` access, byte literals, and direct encoding of literal text or the unshadowed original `ctx`.
- It scans unreachable code. Any syntactic `sha256` binding, including nested scopes, conservatively disables the hash lint for that program. Aliases and unknown argument types are not inferred. Dynamic namespace references also cause abstention.
- Parsing and the 256-level lint traversal bound fail closed before cell execution. Existing code-size and root-repair limits remain in force.
- The independent review was source inspection, not an independent test run. Its retained wording incorrectly says repository files were not accessed. The reviewer did read the listed sources and wrote only its report. No source edits or provider calls were made by that review.

## Reproduce without a provider

```sh
cargo test --locked --offline --features typesafe --bin azdaja solo_preflight
cargo test --locked --offline --features typesafe --test judge_solo_preflight
cargo test --locked --offline --test judge_solo_preflight
cargo test --locked --offline --features typesafe --test judge_native --test judge_batch_cli --test jev_credentials
```

After building the desired feature mode, run the existing installed-workflow command against that binary with a **new** private output directory:

```sh
python3 -B bench/jev/batch_workflow/installed.py \
  --binary /absolute/path/to/azdaja --output /absolute/new-private-output
```

The installed check does not replace the user's installation. It reuses previously retained, attributed observations without a credential or new model request. Receipts and exact log/source hashes are under `results-20260918/`.
