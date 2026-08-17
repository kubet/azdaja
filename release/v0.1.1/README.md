# Azdaja v0.1.1 release candidate

Status: **prepublication; not tagged or published**.

The one-tag release plan has exactly three release assets:

| asset | platform | bytes | SHA-256 |
|---|---|---:|---|
| `azdaja-v0.1.1-darwin-arm64` | Apple Silicon macOS (`Darwin-arm64`) | 6,414,864 | `b58975de462e823adcf901e331acfd4e70c9e72b5db014de265c04e371d31883` |
| `azdaja-v0.1.1-linux-x86_64` | Ubuntu 24.04/glibc x86_64 (`Linux-x86_64`) | 7,935,072 | `b18775f0d3572b20804ff3c3af880ffc5fa3131017c566dc941c1dd743c00247` |
| `SHA256SUMS` | checksum manifest | 186 | recorded by the final prepublication receipt |

Both binaries report `azdaja 0.1.1 (monty 0.0.21)` and are built with
Rust 1.95.0 from one final source commit. The Darwin build normalizes its single
linker-generated `LC_UUID` to a value derived from the exact asset name, then
uses bound Apple `codesign`/`codesign_allocate` bytes to create a timestamp-free
ad-hoc signature with fixed identifier `dev.kubet.azdaja`; this makes independent
build directories byte-identical without shipping an invalid missing-UUID Mach-O.
The versioned installer accepts only
the two exact `uname -s`/`uname -m` pairs above. It binds each immutable GitHub
release URL and digest; ordinary URL or digest environment variables are
rejected. The explicit `AZDAJA_INSTALL_TEST_MODE=local` path exists only for
hash-bound prepublication regression testing.

Publication remains blocked until internal review gives GO. After GO, create
annotated tag `v0.1.1` at the reviewed commit, create one GitHub prerelease, and
upload only the three names in this table. Do not alter tag/release/assets,
checksums, or versioned installer after publication. `v0.1.0` and all of its
existing public objects remain immutable forever.
