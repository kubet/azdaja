# Explicit curated-memory import

This guide describes the current source build. It does not claim that an already published or previously installed binary includes this unreleased command.

`az memory import <bundle-file>` previews a reviewed export without writing destination state. Add `--apply` to merge the records. Add `--global` only when the destination should be personal-global memory rather than the normal project or legacy store.

```sh
az memory import reviewed-memory.json
az memory import reviewed-memory.json --apply
```

The input is the complete compact JSON object emitted by `az memory export`, optionally followed by its single newline. Review both selected records and the explicitly consented connected context before applying it. Reformatting, duplicate JSON keys, unknown fields, unsupported versions, dangling links, invalid records, or a mismatched digest are refused. The input must be a bounded regular non-symlink file. Export and import do not publish or synchronize anything.

## Merge behavior

- The default preview validates the input and destination, reports counts, and creates no memory state.
- `--apply` preserves existing records. An exact existing record with the same ID is counted as already present. A differing record with the same ID is a conflict, not an update or a vote.
- New records are merged under the same writer lock as `memory add`. The destination and record/byte limits are checked again while holding that lock, then the ledger is replaced atomically.
- A valid apply may initialize custody metadata before a later write failure. This is not the no-write guarantee of preview. Existing history must not be overwritten on conflict or a rejected capacity check.
- An error does not by itself prove rollback: snapshot publication can succeed before a later validation fails. Preview the destination or retry the same unchanged bundle to determine whether its exact records are already present. Do not delete records or assume that every unsuccessful return left the old snapshot intact.
- Reapplying an unchanged bundle is idempotent. No extra copy or new ID is created for an already present exact record.
- Project controls and explicit `AZDAJA_HOME` precedence remain the same as other memory commands. `--global` never silently merges project and personal stores.

The receipt contains `action`, `scope`, `new_records`, `already_present`, `total_records`, `source_payload_sha256`, and a provenance caveat. It contains no record bodies or source filesystem path. Preview counts describe the snapshot it read, not a reservation against later writers.

## Trust and boundaries

The SHA-256 digest detects byte-level payload changes. It is not a signature and does not authenticate an author. Imported `provenance.origin` is preserved as an untrusted source assertion, not converted into verified truth, local authorship, or independent confirmation. Several copies of the same note do not constitute several independent agents agreeing.

Import has a 1 MiB input limit. The merged store retains its existing 256-record and 512 KiB serialized-JSONL limits. Relationships must reference records inside the reviewed bundle, and its declared context must exactly match the complete connected component of the selected records.

The workflow intentionally requires a person or explicitly instructed agent to move and review the bundle. An ordinary Git clone excludes `.azdaja` notes. Import does not harvest transcripts, call a provider, infer wisdom, or track renamed files automatically.

## Opened-file validation and platform limits

Import validates the opened file handle as well as checking the path. Unix opens use `O_NOFOLLOW`; Windows opens use `FILE_FLAG_OPEN_REPARSE_POINT` and reject reparse attributes on the resulting handle. This closes the final-entry replacement window between the path check and the open.

`changed_bundle_entry_is_refused_after_a_successful_regular_file_precheck` deterministically replaces a checked regular file with a symlink and then a directory, requires refusal without changing the target, and verifies regular-file recovery. It ran successfully on the native Unix host. Windows code and the Windows test branch compile under strict lint, but Windows runtime execution remains a separate CI gate. Windows reparse checks do not validate ACL exposure; Unix memory-store mode/ownership checks are not a Windows ACL guarantee.

## Acceptance evidence

`tests/memory_export.rs` contains the shared real-CLI export/import acceptance suite. No provider is needed.

| Requirement or public output | Concrete check and observed result |
| --- | --- |
| Actual clone handoff, no-write preview, exact records and metadata, contrary context, idempotence | `actual_clone_import_previews_without_writes_then_preserves_exact_handoff_idempotently` passed. The destination re-export is byte-identical and fresh-home recall finds the imported evidence. |
| Strict canonical input, duplicate/unknown fields, digest and schema validation, no invalid-input initialization | `malformed_tampered_duplicate_and_unknown_import_data_never_initializes_destination` passed with source bytes and destination snapshots unchanged. |
| Same-ID conflict refusal and exact-record idempotence without recreating missing custody | `conflicting_import_preserves_existing_records_and_does_not_recreate_missing_custody` passed. |
| Record capacity and idempotence at a full store | `import_at_record_capacity_refuses_without_losing_existing_history` passed with 256 existing records preserved. |
| Exact UTF-8 JSONL byte capacity, including metadata and newline framing | `import_byte_capacity_accounts_for_utf8_metadata_and_newlines_then_recovers` passed. The observed fixture retained 513,298 bytes, rejected a 16,558-byte incoming record and then accepted a 197-byte record without changing the existing prefix. |
| Concurrent import idempotence and compatibility with normal writers | `overlapping_imports_and_normal_writers_preserve_every_acknowledged_record` passed with 16 children alive during held writer custody: eight import calls produced one new imported record, all eight normal writes survived, and the final ten records included the unchanged original. This is a bounded schedule, not universal concurrency proof. |
| Project/global/legacy/off routing, receipt action/scope/counts, and read-only previews | `import_routing_matrix_keeps_project_global_and_legacy_stores_separate` passed across all six mode/global combinations, including exact receipt-key coverage, source digest, caveat, action, scope and every count field. |
| Invalid flags, missing/directory sources and Unix symlink-source refusal | `import_invalid_flags_and_nonregular_sources_refuse_without_initialization` passed without destination mutation or source changes. |
| Corrupt destination refusal and recovery after restoring valid history | `valid_import_refuses_corrupt_destination_without_repair_then_recovers` passed without exposing damaged note text or rewriting the damaged ledger. |
| Real write failure, preserved history and released writer custody | Unix-only `import_write_failure_preserves_history_and_releases_custody_for_recovery` passed after an 8 KiB file-size limit forced an ordinary exit-2 write failure. All 9,970 original ledger bytes survived, and a later unrestricted import and exact re-export succeeded. |
| Public help and the default no-write import contract | `public_help_explains_context_consent_and_no_write_import_default` passed. |

The final 18-case transfer suite and full optimized project suite, including 49 installer cases, passed. Native, Windows GNU, Linux and Intel macOS strict compile/lint checks also passed. The Unix fault case ran, rather than being counted as ignored. Foreign-target compilation is not foreign-platform runtime acceptance. Passing these functional tests is not evidence that memory improves model correctness or productivity.

Reproduce the public-CLI transfer checks with:

```sh
cargo +1.95.0 test --locked --release --test memory_export
```
