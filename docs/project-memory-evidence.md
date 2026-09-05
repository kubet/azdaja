# Repo-local memory acceptance evidence

This records local development evidence, not publication status or a claim that
agent memory improves coding correctness. Tests invoke the actual CLI in isolated
Git worktrees and separate personal-state roots. No model is needed for these tests.

## Reproduce

```sh
cargo +1.95.0 test --locked --test project_memory -- --nocapture
cargo +1.95.0 clippy --locked --all-targets --all-features -- -D warnings
```

The observed September 5, 2026 run passed 15 tests. One explicitly ignored test
prepares separate Luna pilot inputs and is not an inference-quality assertion.

## Requirement mapping

| Requirement | Public-CLI acceptance check | Observed result |
| --- | --- | --- |
| Default project storage and cross-agent handoff | `repo_local_handoff_crosses_homes_and_subdirectories_without_global_leakage` | Different HOME roots and repository subdirectories retrieve the same note and nonmatching linked disagreement. Personal-global and unrelated-directory reads do not retrieve it. |
| Explicit disable is effective | `explicit_project_memory_off_does_not_create_a_project_store` | Nonglobal write is refused without creating project or fallback personal storage. |
| Empty-store reads do not initialize state | `empty_project_recall_is_read_only_and_reports_project_scope` | List, show and recall do not create an absent project store. Empty recall reports project scope. |
| Partially present empty stores are preserved | `preexisting_empty_project_directories_are_not_initialized_by_read_commands` | List, kind-filtered list, show and recall preserve existing private directories and unrelated sentinel bytes. |
| All public read routes select the same store | `kind_filtered_list_and_show_use_the_project_store_across_homes` | `memory list --kind hypothesis` and show use project notes across HOME roots and subdirectories rather than personal fallback. |
| File associations survive relocation | `project_notes_keep_file_tags_after_repository_relocation_and_stay_git_ignored` | Ordinary file tags and recall output survive moving the checkout. Normal Git status does not expose the local store. Tags are not validated source anchors or automatic rename tracking. |
| Concurrent first use retains successful writes | `concurrent_first_use_keeps_every_acknowledged_project_note` | Twelve synchronized writers succeed; fresh per-note queries verify all distinct persisted notes. The ignore rule is complete and owned initialization files are cleaned up. This is one bounded schedule, not universal concurrency proof. |
| Existing unsafe directories are not repaired | `unsafe_project_directory_is_refused_without_permission_repair` | Unix public directory is refused and its mode and contents remain unchanged. |
| Project-root symlinks are refused | `symlinked_project_store_is_refused_without_touching_the_target` | Refusal preserves the external fixture target. |
| Legacy notes are not silently merged | `legacy_memory_is_explicitly_accessible_not_silently_merged_or_migrated` | Default project reads omit legacy notes and emit an actionable compatibility notice; explicit legacy mode retrieves them without automatic migration. |
| Global storage remains separate | `explicit_global_memory_remains_separate_when_project_memory_is_off` | Explicit global operations remain available with project mode off and do not create project storage. |
| Environment precedence is uniform | `authoritative_home_and_explicit_modes_have_consistent_precedence` | Auto honors explicit AZDAJA_HOME; explicit on selects project storage; off rejects nonglobal operations; explicit global remains independent. Invalid project-mode values are rejected for nonglobal operations. |
| Invalid authoritative configuration does not fall back | `invalid_authoritative_home_and_forced_project_outside_git_fail_without_fallback` | Invalid personal-state overrides and forced project mode outside Git fail without creating substitute state. |
| Existing unsafe ledger entries cannot appear as an empty store | `existing_invalid_project_ledger_entries_are_refused_without_exposure_or_repair` | On Unix, symlink, directory and public-file entries are refused by list, filtered list, show and recall. Each exits normally with code 2 and empty stdout, preserves target/type/mode/bytes, and recovers after fixture restoration. |
| Corrupt project data fails closed | `corrupt_project_ledger_is_refused_without_rewriting_or_personal_fallback` | List and recall refuse corrupt data without rewriting the store or using personal state; restoring the original fixture permits recovery. |

## Portability and limits of the evidence

Strict Clippy compile checks also passed for the `project_memory` target on
`x86_64-pc-windows-gnu`, `x86_64-unknown-linux-gnu`, and `x86_64-apple-darwin`.
These are compilation checks, not runtime tests on those platforms. Native CLI
runtime tests were executed on macOS ARM64. Unix ownership and mode checks do not
establish equivalent Windows ACL confidentiality.

Cold list/show immutability is tested. Existing populated list/show retain the
underlying reader's custody behavior; these checks do not promise that every
existing-store metadata path is read-only. Recall has separate bounded-output,
corruption, provenance, deterministic-ordering and missing-lock regression suites.

This feature stores explicitly authored notes. It does not harvest transcripts,
automatically create summaries, synchronize machines, count votes as truth, or
prove that repeated agent statements are independent evidence. The separate Luna
pilot must report actual subject traces, budget violations and concurrent-revision
limitations. Passing this CLI suite is not a substitute for measured agent benefit.
