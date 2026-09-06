# HTTP-installed memory transfer acceptance

## What this gate exercises

`tests/site_installer.rs::installed_alias_matches_solo_through_a_provider_free_fixture`
installs a locally built candidate using the established loopback HTTP installer fixture.
The existing helper verifies the installed executable's SHA-256 against that candidate
before invoking `tests/support/http_installed_memory_transfer.rs::verify`.
The transfer helper does not build, copy, install, or substitute an executable.
Every memory operation is a fresh process of that installed executable.

This is real installer/CLI integration using synthetic notes and isolated local Git
repositories. It is not verification of a published release asset, the user's existing
installation, model quality, or memory-induced productivity.

## Requirement-to-observation map

All checks below run in the named installer test, not in a mock transfer implementation.

| Requirement | Concrete check |
| --- | --- |
| Correct installed candidate | Existing `sha256(installed) == sha256(candidate)` assertion precedes the new helper. |
| Public transfer interface | Installed `memory --help` describes no-write import preview and `--with-context`. |
| Explicit sharing consent | Exporting an anchor with connected contrary evidence without `--with-context` exits 2 with empty stdout. Consented export succeeds. |
| Deterministic, read-only export | Two exports are byte-identical. Source project and personal directory/type/mode/byte snapshots remain equal. |
| Private notes do not enter an ordinary clone | A real Git clone of a committed source repository has no `.azdaja` directory before import. |
| Preview performs no writes | Import without `--apply` succeeds with JSON output while the entire clone and destination HOME snapshots remain unchanged. |
| Disabled project operations refuse | Both preview and apply with project memory `off` exit 2 without initializing destination state. |
| Exact linked handoff | Applied import preserves both complete record JSON values, including Unicode, multiline inert text, tags, original IDs, provenance, and nonmatching linked disagreement. Duplicate recalled IDs are rejected by the test helper. |
| Imported evidence stays explicitly untrusted | Destination recall retains its untrusted-evidence caveat. No authenticated authorship or agent consensus is inferred. |
| Round-trip and idempotence | Destination re-export equals the original bundle bytes. Reapplying the bundle leaves the complete destination snapshot unchanged. |
| Tampered bundles fail closed | One ASCII byte in a note is changed while preserving valid JSON. Preview and apply refuse, with empty stdout and no destination mutation. |
| Corrupt destination fails closed | The actual imported project ledger is confirmed present and populated, then damaged. Import, export, and recall refuse without repairing or rewriting the damaged snapshot. |
| Recovery is real | Restoring the original ledger bytes restores byte-identical export and exact recalled records through fresh installed processes. |
| Explicit global routing stays separate | Global preview with project mode `off` does not initialize personal state. Explicit global apply succeeds without changing project state and recalls the exact transferred records. |
| Source and input remain intact | Final source project, source HOME and supplied bundle bytes equal their saved originals. |
| Refusal does not expose note bodies | Refusal diagnostics must be nonempty but must not contain the fixture's note body markers. |

## Executed evidence

The first complete installed-transfer run passed on macOS arm64 on 2026-09-06:

```sh
cargo +1.95.0 test --locked --release --test site_installer \
  installed_alias_matches_solo_through_a_provider_free_fixture -- --exact --nocapture
```

It reported `clone=passed`, `export_consent=passed`, `preview_no_write=passed`,
`exact_records=2`, `idempotent=passed`, `tamper_refusal=passed`,
`corrupt_recovery=passed`, and `off_global_isolation=passed`.
The hardened revision also passed the full optimized all-target project suite, including
all 49 installer tests, with strict native Clippy. Strict all-target Clippy additionally
passed for Windows GNU, Linux x86-64, and Intel macOS cross-targets. The cross-target
results establish compilation/lint only, not execution on those platforms.
A Luna reviewer examined the supplied literal subprocess, snapshot, and record-comparison
helper bodies and reported no concrete defect under the stated fixture assumptions.
That was a helper-only static review, not independent execution or a full caller-body review.

## Boundaries

- This extends an existing Unix installer test. Cross-target compilation is not runtime
  proof on Linux, Intel macOS, or Windows.
- Child environments are cleared, then supplied only the necessary PATH and fixture
  routing values. Git configuration and hooks are isolated from the user's settings.
- Output is captured to fixture files rather than unbounded pipe-reader joins. Each
  command has a 30-second polling deadline and a 2 MiB checked output threshold.
  These are test safeguards, not a hard disk quota or an adversarial descendant-process
  containment guarantee.
- Snapshot equality covers path presence, directory/file type, Unix mode and bytes.
  It does not assert unchanged access times, inode identity, or absence of transient
  writes between snapshots.
- This gate does not test every transfer capacity/concurrency/fault case. Those remain
  covered by the separate real-CLI `memory_export` acceptance target.
- Passing this gate is not permission to publish private notes or evaluation artifacts.
