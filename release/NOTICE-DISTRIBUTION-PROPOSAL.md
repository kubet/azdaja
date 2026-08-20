# Supported-target notice co-distribution proposal

Status: **local implementation proposal; no tag, release, push, or publication performed**.

For the next standalone release assembled from this source, retain the two raw
platform binaries and co-locate the exact root `LICENSE` and
`THIRD-PARTY-NOTICES.md`. `SHA256SUMS` is a fifth release asset and must contain
exactly one entry for each of those four payloads. Run
`release/assemble-standalone-assets.sh DIST_DIR` only after both raw binaries
are present; it verifies the reviewed root document identities, copies their
bytes, and writes the four-entry manifest.

A raw binary is compliant only while the exact license and notice remain
co-located release assets and the versioned installer fetches and verifies both
before any install mutation. This proposal does not amend any historical
receipt, tag, release, asset, or checksum manifest. It contains no host path,
credential, provider transcript, or private input.
