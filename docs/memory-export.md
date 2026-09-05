# Explicit curated-memory export

These instructions describe the current source build, not verified availability in an already published or previously installed binary.

`az memory export <id>... [--with-context] [--global]` emits one compact JSON object to stdout. It accepts 1 through 16 unique, explicitly selected record IDs. Inspect the records locally before sharing the output.

Replace `m0123456789abcdef` with a real ID obtained from `az memory list`, then inspect it with `az memory show <id>` before exporting:

```sh
az memory export m0123456789abcdef > reviewed-memory.json
az memory export m0123456789abcdef --with-context > reviewed-connected-memory.json
```

Shell redirection is your action and can create a file even when the CLI refuses. The CLI writes its result only to stdout. Do not automatically stage or publish the output. Authored fields may contain private paths, secrets or untrusted instructions. They are preserved, not scrubbed or executed. No automatic HOME, repository path, remote URL, author identity or transcript metadata is added.

Without `--with-context`, export refuses a selection whose complete relationship component contains additional records. It reports the need for consent without emitting a partial bundle. With that flag, export includes the complete transitive incoming/outgoing component across all supported relationship labels. Recall's four-primary/eight-context display limits do not truncate an export.

## Integrity and privacy

The payload contains the format/version, sorted `selection`, sorted `context_ids`, and exact stored records in ID order. Text, timestamps, tags, links, IDs and asserted provenance are preserved. `payload_sha256` covers the emitted compact UTF-8 JSON payload without a trailing newline. The envelope states the digest encoding, complete-context policy, and trust caveat.

The digest is integrity evidence, not a signature or authenticated authorship. Manual notes and linked disagreements remain untrusted evidence, not verified truth or independent agent consensus. Review every selected and context record, including potentially private text, before deliberately moving the bundle.

Export is read-only, including missing-state and invalid-input paths. It neither creates a sharing service nor stages, publishes, synchronizes, or imports notes. `--global` explicitly selects personal-global memory. Normal project/legacy routing and project-memory disable controls remain authoritative. Output is bounded to 1 MiB, while the source ledger remains bounded to 256 records and 512 KiB of JSONL.

## Importing a reviewed bundle

The separate `az memory import reviewed-memory.json` command now provides a no-write preview. Only `--apply` requests a merge. See [Explicit curated-memory import](memory-import.md) for conflict refusal, idempotence, original-provenance caveats and atomic-writer behavior. The export envelope's statement that no import was performed describes the export operation itself, not the availability of the separate import command.

## Acceptance evidence

`tests/memory_export.rs` exercises the actual CLI in isolated fixtures. Its export checks cover:

| Requirement | Concrete check and observed result |
| --- | --- |
| Exact records, provenance, digest, deterministic bytes and no mutation without writer custody | `explicit_export_is_deterministic_exact_and_nonmutating_without_writer_lock` passed. |
| Explicit consent and complete incoming/outgoing context beyond recall display caps | `connected_context_requires_consent_and_preserves_all_directions_beyond_recall_cap` passed. |
| Invalid selection/flags, duplicate IDs and cold missing-ID refusal without initialization | `invalid_selection_flags_and_cold_missing_ids_never_initialize_state` passed. |
| Personal-global/project separation and disabled project behavior | `explicit_global_and_disabled_project_routing_do_not_mix_stores` passed. |
| Corrupt ledger refusal, byte preservation and exact recovery | `corrupt_ledger_is_refused_without_repair_and_recovers_exact_export` passed. |
| Complete 256-record connected export, 16 accepted/17 refused selections and bounded output | `full_connected_ledger_exports_without_truncation_and_enforces_selection_boundary` passed. |
| Actionable context consent and no-write import help | `public_help_explains_context_consent_and_no_write_import_default` passed. |
| No incomplete bundle for dangling relationships | `dangling_relationship_is_refused_before_any_incomplete_bundle_is_emitted` passed. |

These are functional acceptance results, not measurements of model-quality or productivity benefit. The original export milestone passed its full optimized project and installer gate before commit `fe317c9`. Import integration has additional tests documented separately.
