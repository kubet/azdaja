# Release and managed-file internals

This document records distribution invariants for packagers and downstream auditors. End users normally need only the [install lifecycle guide](install.md).

## Standalone payload

A standalone release contains two raw platform binaries, `LICENSE`, `THIRD-PARTY-NOTICES.md`, and `SHA256SUMS`. The checksum manifest covers the two binaries and both legal documents. The installer downloads and verifies all selected bytes before changing installation state, then publishes staged files atomically.

A bare platform binary is not the complete standalone distribution. Keep the matching license and supported-target notices co-located with it.

## Managed legal documents

The curl route stores `LICENSE`, `THIRD-PARTY-NOTICES.md`, and an exact v2 ownership marker under `${XDG_DATA_HOME:-$HOME/.local/share}/azdaja`. Reinstall accepts only the fixed current marker and matching documents.

One fixed legacy v1 document set can migrate to v2. Missing, changed, foreign, linked, hardlinked, or marker-declared alternative bytes are refused. Migration quarantines and revalidates the old set, replaces it atomically, and restores it byte-for-byte if a later selected step fails.

## Standalone ownership

Removal starts from the executing canonical `azdaja` binary and requires the exact adjacent ownership marker. Eligible paths are the owned binary, an exact relative `az -> azdaja` link, the two Azdaja configuration files, and the exact managed legal-document directory. No marker field is trusted as a caller-selected digest.

The install and removal paths share lifecycle exclusion, preflight every selected surface, and quarantine before deletion. These rules keep foreign commands, configuration, documents, and neighboring files outside the transaction.

## Terminal output

Noninteractive invocation through either command name emits the same five-line help text. An interactive color terminal may place the indexed 16-row truecolor sprite above those lines; `NO_COLOR`, `TERM=dumb`, and non-TTY output suppress the sprite.
