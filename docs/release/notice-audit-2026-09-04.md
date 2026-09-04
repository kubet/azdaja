# Third-party notice semantic audit

**Audit date:** 2026-09-04
**Scope:** repository notice, package metadata, release assembly, provenance claims, and current-lock source inputs

## Exact stale semantic metadata blocker

The root `THIRD-PARTY-NOTICES.md` has the corrected v0.1.14 identity and all three supported targets, but its bound lockfile metadata is stale. Notice line 15 records `Cargo.lock` SHA-256 `4e2419eaf2f1cf4818dca37950af56a7aedf6a079567357f4b7b72f8dd72066d`; the current tracked `Cargo.lock` hashes to `f2ff24a523f718f12c7a3a40fbf412cc91346bf7acbb517ae23b98a3d7c1bfb3`. Therefore the notice's historical and additive sections cannot yet be asserted as one current-lock, three-target notice corpus. This is the exact remaining semantic metadata blocker and publication blocker.

The historical blocker that led to the current front-matter repair was the then-current notice being headed `Candidate: Azdaja v0.1.2 public content snapshot`, listing only `aarch64-apple-darwin` and `x86_64-unknown-linux-gnu`, and describing an older two-target snapshot while v0.1.14 added `x86_64-apple-darwin`. That version/target problem is corrected in the front matter. The remaining problem is the semantic lock binding and unified current-closure claim, not byte integrity.

## New current-lock input evidence

`release/audit-third-party-notice-inputs.py` now reconstructs the dependency input inventory from the current checkout without changing the notice. It runs the default-edge `cargo tree --locked --offline` closure for exactly `aarch64-apple-darwin`, `x86_64-apple-darwin`, and `x86_64-unknown-linux-gnu`, cross-checks every supported record against the crates.io registry identity and checksum in `Cargo.lock`, verifies the corresponding cached `.crate` archive bytes, parses the packaged `Cargo.toml`, and hashes every named legal file plus any explicitly declared `license-file`.

The tracked `release/third-party-notice-inputs.json` records:

- current `Cargo.lock` SHA-256 `f2ff24a523f718f12c7a3a40fbf412cc91346bf7acbb517ae23b98a3d7c1bfb3`;
- 247 crates.io registry lock records;
- target closure counts 189, 190, and 190 respectively;
- a 191-record three-target union;
- 314 named or explicitly declared legal files with exact byte lengths and SHA-256 digests;
- 13 manifest-only MIT records with no named legal file in the packaged archive; and
- per-record target membership, archive checksum, packaged manifest hash, license declaration, and legal-file evidence.

The script is stdlib-only and fails closed on missing or ambiguous archives, checksum mismatch, closure drift, archive path traversal, duplicate archive members, malformed or missing declared legal files, malformed package identity, absent license evidence, or a stale checked-in manifest. Its output is explicitly classified as **source-input evidence only; it does not establish notice semantic completeness**.

Reproduce the input audit with:

```sh
python3 -m unittest release/test_audit_third_party_notice_inputs.py
python3 release/audit-third-party-notice-inputs.py --check
```

The current machine has all 191 required archives cached. Normal CI runs the cache-independent unit tests. It does not run the exact cross-target manifest check because the workflow does not yet explicitly fetch the complete three-target archive set before offline validation.

## Evidence audit

- `Cargo.toml` is version `0.1.14`, declares `crossterm = "0.29"` and Ratatui `0.30` with the `crossterm` feature, and its package `include` allowlist contains `Cargo.toml`, `Cargo.lock`, `LICENSE`, `THIRD-PARTY-NOTICES.md`, README, source, and packaged assets.
- The current notice front matter names `Azdaja v0.1.14` and `aarch64-apple-darwin`, `x86_64-apple-darwin`, and `x86_64-unknown-linux-gnu`. Its notice byte SHA-256 is `393cfd092b543059d376b96134e7dadf2da5e2f5e76df84d9edbca42d22f62d2`, matching the release assembler's pinned notice identity.
- `release/assemble-standalone-assets.sh` is version-pinned to `0.1.14`, requires three raw non-symlink binaries, byte-compares the copied `LICENSE` and notice, and emits `SHA256SUMS` for the three binaries plus `LICENSE` and the notice.
- `cargo test --test notice_distribution --locked` previously passed all 12 tests. The suite covers notice front matter and target membership, reviewed license/font preservation, Cargo package allowlist parity, assembly and five-payload checksums, release provenance, public installer-target claims, and the Intel Darwin dependency delta. These tests verify notice identity and packaging gates, but they do not make the stale lockfile hash semantically correct.
- The current lock and the lock bound by the 2026-08-24 additive audit contain the same 247 crates.io registry package name/version/source/checksum records: zero additions, zero removals, and zero checksum changes. This is strong continuity evidence, but it is not by itself permission to replace the stale top-level binding.
- All 314 current named legal-file hashes occur in the reviewed notice corpus, and every current supported package name/version record appears explicitly in its historical or additive inventory. This narrows the remaining work to reviewed reconciliation and verification. It does not turn the fragmented historical/additive document into a machine-proven current notice automatically.

## Decision

Do not replace the notice hash alone. Use the new current-lock input manifest to perform a reviewed reconciliation of the historical 156-record inventory, the 35-record additive inventory, Intel Darwin target membership, manifest-only exceptions, and exact legal-text occurrences. Only then update the notice's bound hash and affected claims together.

No package, lockfile, notice corpus, release asset, or publication state was changed by this audit.

## Safe claim boundary

Allowed: the current tracked notice is byte-authentic to the assembler's reviewed notice identity; it has v0.1.14 three-target front matter; the package include list and assembler preserve the reviewed notice and license bytes; the current 191-record source-input inventory is reproducible from checksum-verified locked archives; and the focused notice input tests and exact manifest check pass.

Not allowed: claiming that the current notice is a complete current-lock dependency/license inventory, claiming that its historical 156-record section alone is the current closure, claiming that the stale top-level lock binding is correct, or claiming that archive checksums alone resolve semantic completeness. A checksum proves bytes and identity, not legal sufficiency or a unified notice claim.

## Fail-closed follow-up

Reconcile or regenerate the notice from `release/third-party-notice-inputs.json` and reviewed exact legal text. Extend `release/verify-third-party-notices.py` to validate the reconciled 191-record closure, all three target memberships, manifest-only exceptions, exact legal occurrence commitments, and the current lock binding. Retain failures for stale candidate/version text, missing release targets, missing closure records, notice identity drift, or notice/provenance source-commit mismatch. Until that passes, keep semantic completeness and publication withheld.

The existing strict verifier compares the notice's single declared `Cargo.lock` SHA-256 binding with the current regular, non-symlink lockfile and fails closed on a missing, duplicate, malformed, or stale binding. The manual publication workflow runs it before any GitHub API or release action. On this checkout, failure with the documented stale-hash mismatch remains expected and desired.
