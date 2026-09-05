# Explicit curated-memory export

`az memory export <id>... [--with-context] [--global]` emits one compact JSON object to stdout. It is a deliberate local export, not an upload, synchronization service, or import command. Use IDs obtained from `az memory list` and inspect their full text with `az memory show <id>`.

## Privacy and evidence completeness

- Select 1 through 16 unique IDs. There is no implicit export-all mode.
- Only the selected store is read. Existing project/legacy/off routing applies. `--global` explicitly selects the separate personal-global store.
- An isolated selected record can be exported directly. If any incoming or outgoing link connects it to additional records, export refuses with a count and emits no bundle.
- `--with-context` explicitly consents to including **every record in the complete transitive connected relationship component**, not merely the one-hop recall preview. This may include the whole store, up to 256 records. It includes contrary and superseding evidence without silently truncating it.
- Review all selected **and context** records locally before sending a bundle anywhere. Notes can contain private text, paths, secrets, or untrusted instructions supplied by their author. Context consent is not a guarantee that these contents are safe to publish.
- No automatic HOME, repository path, remote URL, author identity, or transcript metadata is added. Authored record fields are preserved, not scrubbed or executed.
- Export reads one validated snapshot and does not create the store, recreate an absent writer lock, repair permissions, or call a model.

For example, replace `m0123456789abcdef` with a real reviewed ID:

```sh
az memory show m0123456789abcdef
az memory export m0123456789abcdef
```

If complete linked context is required, inspect that context before explicitly adding `--with-context`. Shell redirection is your action and can create a file even if a command refuses. The CLI itself only writes its result to stdout. Do not automatically stage or publish the output.

## Version 1 envelope

The `payload` contains `format="azdaja-curated-memory"`, `version=1`, sorted `selection` IDs, sorted additional `context_ids`, and complete `records` sorted by ID. Records retain all schema, timestamp, kind, body, tag, link, and provenance fields. A note's existing `origin="manual"` describes the stored record, not an authenticated sender or independent agent confirmation.

`payload_sha256` is the lowercase SHA-256 digest of the compact UTF-8 JSON serialization of **only `payload`**, preserving the emitted object-key order and without a trailing newline. The envelope names this encoding explicitly. Pretty-printing, reordering keys, changing JSON escaping, or hashing the entire envelope is not the same byte encoding. This is not a general JSON canonicalization standard.

The digest detects payload changes when compared with a trusted expected digest. It is **not a signature**. Anyone can change a payload and recompute the digest. Envelope caveats, context-policy text, and other envelope fields are not authenticated or covered by the payload digest. Future import must validate the schema, IDs, links, provenance, and bounds independently rather than trusting any envelope claim.

The complete output, including the CLI newline, is limited to 1 MiB. Export refuses rather than emitting a partial bundle. Store validation still applies first, including corruption, unsafe file custody, dangling references, record-count, and ledger-byte limits.

## Acceptance map

Run `cargo +1.95.0 test --locked --release --test memory_export`. Observed on 2026-09-05: all eight tests below passed against the optimized CLI. Native all-target, all-feature strict Clippy also passed. The full-capacity test compares every field of all 256 exported records against the CLI-written ledger, rather than checking only aggregate counts.

| Requirement / output | Concrete fresh-process check |
| --- | --- |
| Exact inert text, tags, provenance, explicit selected IDs, no unrelated records or injected fixture path | `explicit_export_is_deterministic_exact_and_nonmutating_without_writer_lock` |
| Stable compact output, payload digest binding, changed-body digest mismatch | Same test, with reversed input ID order and mutated payload |
| Populated read-only behavior with actual `memory/global.lock` absent | Same test, byte/type/Unix-mode snapshots before and after |
| Separate consent, empty stdout on refusal, count-only diagnostic, incoming/outgoing transitive context beyond recall cap | `connected_context_requires_consent_and_preserves_all_directions_beyond_recall_cap` |
| Empty/invalid/missing/duplicate IDs, unknown/repeated flags, no cold initialization | `invalid_selection_flags_and_cold_missing_ids_never_initialize_state` |
| Dangling target refused with/without context consent, exact damaged-state preservation and recovery; all bundles have exact one-to-one declared ID / record coverage | `dangling_relationship_is_refused_before_any_incomplete_bundle_is_emitted` and the shared bundle assertions |
| Personal-global separation and project off behavior | `explicit_global_and_disabled_project_routing_do_not_mix_stores` |
| Corruption refusal, unchanged damaged bytes, exact successful recovery | `corrupt_ledger_is_refused_without_repair_and_recovers_exact_export` |
| 256 exact records, all four relationship labels, 16 selected / 240 context, UTF-8 output above 256 KiB and below 1 MiB, 17 unique selections refused | `full_connected_ledger_exports_without_truncation_and_enforces_selection_boundary` |
| Public help syntax and context/privacy warning, no import claim, no state initialization | `public_help_explains_explicit_context_consent_without_claiming_import` |

These are CLI/export correctness checks, not evidence of model productivity gains. The full optimized all-target project suite also passed on 2026-09-05, including the 49 installer tests. Rustfmt and strict all-target/all-feature Clippy passed natively and for Windows GNU, Linux x86_64, and Intel macOS compilation targets. Those foreign checks are not foreign-platform runtime acceptance. Cross-clone validated atomic import remains a separate delivery milestone. No new release publication is established by these tests.
