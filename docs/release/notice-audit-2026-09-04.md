# Third-party notice semantic audit

**Audit date:** 2026-09-04
**Scope:** repository notice, package metadata, release assembly, and provenance claims

## Exact stale blocker recorded previously

The historical v0.1.14 release-evidence audit recorded a semantic metadata blocker in the then-current root `THIRD-PARTY-NOTICES.md`: it was headed `Candidate: Azdaja v0.1.2 public content snapshot`, listed only `aarch64-apple-darwin` and `x86_64-unknown-linux-gnu`, and described an older two-target snapshot even though the v0.1.14 release added `x86_64-apple-darwin`. The notice was byte-authentic, but its version, target set, dependency-closure scope, and release-source binding were stale. This was a semantic currency problem, not a checksum failure.

## Current repository disposition

That exact blocker is now corrected in the tracked tree, so no further notice rewrite is justified by this audit. The current notice front matter identifies `Azdaja v0.1.14`, names all three supported release targets, and records the locked dependency and local SPDX metadata bindings. `Cargo.toml` is also version `0.1.14` and its package `include` allowlist explicitly includes `Cargo.toml`, `Cargo.lock`, `LICENSE`, `THIRD-PARTY-NOTICES.md`, README, source, and the packaged asset paths.

The release assembler is version-pinned to `0.1.14`, requires three raw non-symlink binaries, pins the reviewed root `LICENSE` and notice SHA-256 values, copies both files with byte comparisons, and emits `SHA256SUMS` for the three binaries plus `LICENSE` and `THIRD-PARTY-NOTICES.md`. The notice is therefore bound fail-closed at the repository assembly boundary.

## Validation observed

`cargo test --test notice_distribution --locked` passed all 12 tests. The passing suite covers current notice front matter and target membership, preservation of reviewed license/font bytes, Cargo package allowlist parity, standalone assembly and five-payload checksums, release provenance, public installer-target claims, and the Intel Darwin dependency delta.

The tracked change in this commit is only this audit note. No package, lockfile, notice corpus, release asset, or test source was changed.

## Safe claim boundary

Allowed: the current tracked notice is a v0.1.14 three-target artifact with explicit lock/SPDX bindings; the package include list and release assembler preserve the reviewed notice and license bytes; the focused notice-distribution regression suite passes; and the assembly checksum set covers the three binaries, `LICENSE`, and the notice.

Not allowed without a fresh public release receipt: claiming that a particular public download still matches the current tracked tree, or extending the notice's completeness claim to a different release source commit, target set, lockfile, or dependency closure. A checksum proves bytes, not semantic completeness; every future dependency or target change must regenerate the notice and update its fail-closed bindings together.

## Follow-up rule

Any future correction must be generated from the locked supported-target dependency closure and authoritative upstream package/license metadata. Tests must fail on stale candidate/version text, missing release targets, missing closure records, notice identity drift, or a notice/provenance source-commit mismatch.
