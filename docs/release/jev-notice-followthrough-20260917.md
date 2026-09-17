# Optional Jev dependency notice follow-through

**Disposition: still blocked.** This is an engineering source-input and byte-comparison audit, not legal-completeness approval. The notice, release gate, dependency versions and historical study receipts were not changed. The [observed input/result record](jev-notice-followthrough-20260917.json) is bound to source `461df9b`, unchanged runtime source `ed0403b`, current lock `2667713c…` and notice `393cfd09…`.

## Corrected failure attribution

These are distinct findings, not one interchangeable failed check:

1. The actual Rust acceptance test fails at `tests/notice_distribution.rs:95`: the root notice says candidate **v0.1.14**, while `Cargo.toml` says **v0.1.17**. The check was executed again and returned Cargo exit 101, with zero passed and one failed test. A diagnostic wrapper that expects this failure returning zero is **not** a passing release test.
2. The actual `release/verify-third-party-notices.py` exits 1 because the notice binds lock `4e2419ea…`, not current lock `2667713c…`.
3. The optional `typesafe` feature expands the audited three-target dependency union. Its additional attribution is not covered merely by changing the candidate or bound hash.

The first two problems are inherited notice state, not evidence that Jev changed existing dependency licenses. The new feature creates the third obligation. It would be wrong to call all three fixed by replacing a version string or hash.

## Measured dependency boundary

All six actual `cargo tree --locked --offline` commands ran, covering default features and `--features typesafe` for the three release targets. These are dependency-closure observations, not cross-platform execution tests.

| Mode | ARM macOS | Intel macOS | x86-64 Linux | Union |
|---|---:|---:|---:|---:|
| Default | 189 | 190 | 190 | 191 |
| With `typesafe` | 240 | 241 | 241 | 242 |

- All **191 default-closure records** equal the retained input manifest in package identity, archive checksum, source, packaged manifest hash, license declaration, named legal-file records and target membership.
- The feature adds **51 package records to that closure**, including 88 named legal-file occurrences. All 242 union archives were hashed against `Cargo.lock` and their packaged license inputs were read successfully.
- The lock contains 67 additional registry records relative to released `origin/main`, with no removals or changed retained source/checksum records. Lock membership is not the same as inclusion in a selected target/feature closure.
- The initial offline attempt correctly failed because `cpufeatures 0.3.1` was not cached. `cargo fetch --locked` fetched that one public archive without changing the lock. The subsequent audit was offline. No inference provider was called and no real API credential was read.

The result record retains the 51 additional package identities, exact declarations, archive/manifest hashes, target memberships and all 88 legal-file hashes and byte lengths. Notable declarations needing their actual supplied texts include `ring`'s `Apache-2.0 AND ISC` and `webpki-roots`'s `CDLA-Permissive-2.0`. This is not a conclusion that they are incompatible or legally sufficient for distribution.

## Why existing digest headings are insufficient

The follow-through read legal body bytes, rather than treating a Markdown hash heading as proof of its contents. Of the additional feature's 88 named occurrences, 63 do not have a byte-identical body among the valid retained notice texts. None of the 88 has an existing exact package/version/path/digest attribution occurrence. Some license bodies can legitimately be shared, but that does not invent the new package attribution.

Four older notice bodies also do not match their claimed exact source bytes:

| Package/path | Original bytes | Rendered bytes | Observed difference |
|---|---:|---:|---|
| `crossterm 0.29.0/LICENSE` | 1083 | 1062 | CRLF changed to LF |
| `allocator-api2 0.2.21/LICENSE-APACHE` | 9899 | 9723 | CRLF changed to LF |
| `allocator-api2 0.2.21/LICENSE-MIT` | 1046 | 1023 | CRLF changed to LF |
| `zerocopy 0.8.56/win-cargo.bat`, leading legal header | 391 | 385 | CRLF changed to LF |

Each original hash was independently recomputed from the checksum-verified archive. Normalizing its CRLF bytes to LF produced the retained rendered body exactly. This is a **byte-fidelity claim defect**, not a finding of removed license words or changed legal meaning. The fourth record is the leading 391-byte header, not the entire batch file.

## Remaining work and stop boundary

A proper release follow-up must review and reproduce the new legal/attribution material, reconcile the old historical and additive scopes with the current three-target feature matrix, and repair or explicitly describe the four normalized bodies. Only after that should it update candidate identity, feature/target scope, exact text, lock binding, pinned notice identity and distribution evidence together.

This follow-through does not silently turn a Jev usefulness investigation into a release authorization. It preserves the failing gate and supplies concrete inputs for that remaining work. In particular, it does not claim the optional dependency audit is complete merely because all archive checksums match.

The practical research decision is unchanged: native optional judgments work, but the seven-task study found **no final-answer quality improvement**. The one-query tight-shortlist signal does not justify a mandatory judge or new shipping default. No further model calls or quality-score tuning were performed.

## Re-execute the failing public checks

```sh
cargo test --locked --offline --test notice_distribution \
  current_notice_front_matter_tracks_canonical_version_targets_and_table_membership \
  -- --exact --nocapture
python3 release/verify-third-party-notices.py
```

Both are expected to fail on this recorded state. The JSON record gives the six exact Cargo closure commands and exact source digests. The existing `release/audit-third-party-notice-inputs.py` archive validator supplied the checksum, package-manifest and named-legal-file input checks, without modifying its historical manifest or reconciliation rules.
