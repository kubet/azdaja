# Installed memory-transfer acceptance

## What this gate executes

`tests/site_installer.rs::installed_alias_matches_solo_through_a_provider_free_fixture`
uses the established loopback HTTP release fixture and installer. After checking
that the installed executable's SHA-256 equals the fixture candidate's SHA-256,
it calls `tests/support/http_installed_memory_transfer.rs` with that installed path.
The helper never builds, copies, installs, or substitutes an executable.

This is acceptance of the current candidate through the real local HTTP installer.
It is **not** verification of a published release asset, an upgrade of the user's
live installation, or a measurement of model productivity.

## Reproduce

```sh
cargo +1.95.0 test --locked --release --test site_installer \
  installed_alias_matches_solo_through_a_provider_free_fixture -- --exact --nocapture
```

## Requirement-to-observation map

| Requirement | Concrete check | Observed result |
| --- | --- | --- |
| Execute the installed candidate | Existing parent gate compares installed and candidate SHA-256, then passes the installed executable to every transfer command | Passed |
| Transfer actual project memory between independent homes and a clone | Create notes through installed CLI, commit a synthetic tracked file, clone using Git, import with a second HOME | Passed |
| Do not implicitly clone private memory | Assert `.azdaja` is absent from the clone before import | Passed |
| Require consent for connected notes | Export of the linked primary alone exits 2 with empty stdout; `--with-context` succeeds | Passed |
| Preserve complete note values and contrary context | Compare all returned record fields by ID, reject duplicate IDs, and require exactly two source records | Passed in hardened full-project gate |
| Deterministic export and exact round trip | Repeat source export and compare bytes; compare destination re-export to the original bundle | Passed |
| Preview performs no writes | Compare complete clone and personal-home directory/file/mode/byte snapshots before and after default import | Passed |
| Off switch prevents non-global import | Both preview and apply with project mode off refuse with exit 2 and no state change | Passed |
| Explicit apply is required and idempotent | Apply succeeds, repeated apply preserves the complete destination snapshot | Passed |
| Tampered input cannot alter history | Change one byte of note text while preserving valid JSON; preview and apply both refuse, destination remains identical | Passed |
| Corrupt destination fails closed and recovers | Verify the actual imported ledger contains the selected ID, corrupt that ledger, require import/export/recall refusal, restore exact bytes and verify exact re-export | Passed |
| Explicit global routing remains separate | With project mode off, global preview remains read-only and global apply succeeds without changing project state | Passed |
| Source state and bundle remain untouched | Compare source project state, source personal state, and input bundle bytes after the full workflow | Passed |

Initial runtime receipt: task `101149t4ku`, 2026-09-06 18:58 UTC, exit 0.
It reported `clone=passed export_consent=passed preview_no_write=passed
exact_records=2 idempotent=passed tamper_refusal=passed corrupt_recovery=passed
off_global_isolation=passed`.

## Harness boundaries

Child environments are cleared, then given the test runner's PATH and isolated
homes. Git hooks/signing and global/system Git configuration are disabled for the
synthetic fixture. Output is captured to fixture-owned regular files, with a
2 MiB per-stream observed cap and a 30-second direct-child deadline. Direct children
are killed and reaped on failure. This does not promise arbitrary descendant-tree
cleanup or deadlines for uninterruptible kernel I/O.

Snapshots check file/directory identity, Unix mode and bytes. They do not establish
Windows ACL privacy, filesystem crash durability, authenticated authorship, or
memory usefulness. The parent installer target is Unix-only.

The initial focused runtime passed. Environment-isolation, diagnostic-leakage and
duplicate-record hardening are now under a fresh full-project gate; that gate's
result and the literal-helper review must be collected before committing.
Intel macOS. Foreign compile/lint checks
are not foreign runtime tests. Independent review of the supplied literal capture,
snapshot and record-comparison helpers found no concrete defect for this Unix
fixture scope; it did not inspect other repository source or execute tests.

An additional negative control requires the record comparator to reject a repeated
ID spanning primary and context arrays. The final installer-target gate
(`324506gnjp`, 2026-09-06 19:02 UTC) passed all **50 tests**, including the actual
installed transfer workflow and that negative control. Formatting and strict native
Clippy also passed. The synthetic grader control is not counted as product evidence.
