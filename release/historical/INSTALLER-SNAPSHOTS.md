# Frozen v0.1.17 rolling-installer snapshots

These files preserve the installer bytes captured from source commit
`48a10a06760d796bfcf794a7ea16f18df5bd62b5` before the v0.1.18 rolling
installer selectors and notice pin were changed.

| Snapshot | Source path at that commit | SHA-256 |
| --- | --- | --- |
| `install-v0.1.17.sh` | `install.sh` (identical to `site/install`) | `ff8f13a96db348a322baa25a90ea18f006f80d3d2b68e5950cd1b998c9f410da` |
| `install-v0.1.17.ps1` | `site/install.ps1` | `144cf9bcff40118fe25795264c01e636444398f86eae2ddf39ce155edfdbf807` |

Both hashes match the existing, unchanged installer entries in
`published-notice-hashes.json`. The inventory regression test checks these
snapshots for those two rolling installer entries. All other inventory entries
continue to check their original paths and hashes.

**The shell snapshot is not byte-identical to the `v0.1.17` Git tag's
`site/install`.** Its filename records the rolling installer's `VERSION=0.1.17`
selector, not a claim that it was taken from that tag. The PowerShell snapshot
is byte-identical to both the source commit above and the `v0.1.17` tag.

The frozen shell script is used only by the historical rejection regression:
it must refuse the new current notice even when a fixture manifest honestly
hashes that notice. Current installer tests and CI use `site/install` with the
current source-backed notice. Neither frozen installer is a current release
entry point or permission to install old bytes.
