# Third-party notice semantic audit

**Audit date:** 2026-09-04
**Scope:** repository notice, package metadata, release assembly, and provenance claims

## Exact stale semantic metadata blocker

The root `THIRD-PARTY-NOTICES.md` has the corrected v0.1.14 identity and all three supported targets, but its bound lockfile metadata is stale. Notice line 15 records `Cargo.lock` SHA-256 `4e2419eaf2f1cf4818dca37950af56a7aedf6a079567357f4b7b72f8dd72066d`; the current tracked `Cargo.lock` hashes to `f2ff24a523f718f12c7a3a40fbf412cc91346bf7acbb517ae23b98a3d7c1bfb3`. Therefore the notice's 156-package supported-target closure cannot be asserted as the closure of the current lockfile. This is the exact remaining semantic metadata blocker.

The historical blocker that led to the current front-matter repair was the then-current notice being headed `Candidate: Azdaja v0.1.2 public content snapshot`, listing only `aarch64-apple-darwin` and `x86_64-unknown-linux-gnu`, and describing an older two-target snapshot while v0.1.14 added `x86_64-apple-darwin`. That version/target problem is corrected now. The remaining problem is the lockfile binding, not byte integrity.

## Evidence audit

- `Cargo.toml` is version `0.1.14`, declares `crossterm = "0.29"` and Ratatui `0.30` with the `crossterm` feature, and its package `include` allowlist contains `Cargo.toml`, `Cargo.lock`, `LICENSE`, `THIRD-PARTY-NOTICES.md`, README, source, and packaged assets.
- The current notice front matter names `Azdaja v0.1.14` and `aarch64-apple-darwin`, `x86_64-apple-darwin`, and `x86_64-unknown-linux-gnu`. Its notice byte SHA-256 is `393cfd092b543059d376b96134e7dadf2da5e2f5e76df84d9edbca42d22f62d`, matching the release assembler's pinned notice identity.
- `release/assemble-standalone-assets.sh` is version-pinned to `0.1.14`, requires three raw non-symlink binaries, byte-compares the copied `LICENSE` and notice, and emits `SHA256SUMS` for the three binaries plus `LICENSE` and the notice.
- `cargo test --test notice_distribution --locked` passed all 12 tests. The suite covers notice front matter and target membership, reviewed license/font preservation, Cargo package allowlist parity, assembly and five-payload checksums, release provenance, public installer-target claims, and the Intel Darwin dependency delta. These tests verify the current notice identity and packaging gates, but they do not make the stale lockfile hash semantically correct.

## Decision

Do not rewrite the notice corpus or infer a new dependency/license closure from package names. The current lockfile hash mismatch means a fully supported notice correction requires regenerating the dependency closure from the current locked supported-target graph and authoritative upstream package/license metadata, then updating the notice's bound hash and any affected records together. A one-line hash substitution would be unsafe because it could falsely bind unchanged notice records to a changed closure.

No package, lockfile, notice corpus, release asset, or notice test source was changed by this audit.

## Safe claim boundary

Allowed: the current tracked notice is byte-authentic to the assembler's reviewed notice identity; it has v0.1.14 three-target front matter; the package include list and assembler preserve the reviewed notice and license bytes; and the focused notice-distribution regression suite passes.

Not allowed: claiming that the current notice is a complete or current dependency/license inventory for the current `Cargo.lock`, claiming that its 156-package closure is bound to the current lockfile, or claiming that a checksum/provenance match resolves the lockfile semantic mismatch. A checksum proves bytes, not semantic completeness.

## Fail-closed follow-up

Regenerate from the current `Cargo.lock` and supported-target closure using authoritative upstream package/license metadata. Add or retain tests that fail on a notice lock-hash mismatch, stale candidate/version text, missing release targets, missing closure records, notice identity drift, or a notice/provenance source-commit mismatch. Until that regeneration passes, keep the semantic completeness claim withheld.

The repository now includes `release/verify-third-party-notices.py`. It compares the notice's single declared `Cargo.lock` SHA-256 binding with the current regular, non-symlink lockfile and fails closed on a missing, duplicate, malformed, or stale binding. The main CI job runs its isolated unit tests, and the manual publication workflow runs the strict verifier before any GitHub API or release action. On the current checkout, the strict command is expected to fail with the exact stale-hash mismatch documented above. This gate does not regenerate or validate the dependency/license closure by itself.
