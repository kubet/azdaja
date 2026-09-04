# Third-party notice semantic audit

**Audit date:** 2026-09-04
**Scope:** repository notice, package metadata, release assembly, provenance claims, and current-lock source inputs

## New current-lock INPUT evidence

`release/audit-third-party-notice-inputs.py` now runs `cargo tree --locked --offline` independently for exactly `aarch64-apple-darwin`, `x86_64-apple-darwin`, and `x86_64-unknown-linux-gnu`. It cross-checks the supported-target union against registry records and checksums in the current `Cargo.lock`, verifies each corresponding Cargo cache archive byte checksum, and records Cargo metadata plus hashed legal files in `release/third-party-notice-inputs.json`. The script is stdlib-only and fails closed on missing or ambiguous archives, checksum mismatch, closure drift, malformed legal paths, and missing license evidence.

The JSON is explicitly **source-input evidence only; it does not establish notice semantic completeness**. It does not alter the reviewed notice, its bound hash, or release publication claims.

Focused tests cover synthetic archives, legal-file hashing, malformed paths, and malformed lock records. The exact manifest check is `python3 release/audit-third-party-notice-inputs.py --check`.

## Remaining blocker

The root `THIRD-PARTY-NOTICES.md` still binds a stale Cargo.lock hash. Its semantic completeness remains withheld. This audit supplies reproducible inputs for a future reviewed regeneration, not a notice rewrite or a claim that the existing corpus is complete.

The existing evidence, safe claim boundary, and prior packaging findings remain unchanged below.

## Existing evidence

- `Cargo.toml` is version `0.1.14` and declares the three-target package and notice assets.
- The current notice has the reviewed v0.1.14 identity and three supported targets.
- Existing notice-distribution tests and `release/verify-third-party-notices.py` remain unchanged.

## Decision

Do not rewrite the notice corpus or infer a new dependency/license closure from package names. Keep semantic completeness withheld until reviewed regeneration binds the current lock and authoritative license evidence together.
