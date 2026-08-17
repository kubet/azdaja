# v0.1.1 publication checklist

## Hard stop before internal GO

- Work only from isolated branch `release/v0.1.1`, based on public main
  `26475d27fc57a9594d4a1bdd0e790cdbf6561d79`.
- Require a clean final candidate commit and rerun formatting, strict clippy,
  the complete locked suite, and release builds on both exact platforms.
- Rebuilt final-commit bytes must equal the predictions:
  - Darwin arm64: `b58975de462e823adcf901e331acfd4e70c9e72b5db014de265c04e371d31883` / 6,414,864 bytes.
  - Linux x86_64: `b18775f0d3572b20804ff3c3af880ffc5fa3131017c566dc941c1dd743c00247` / 7,935,072 bytes.
- Re-run each local platform gate with ephemeral OAuth staging. Confirm installer
  byte identity, provider-free installation, live `doctor`, exact installed-binary
  50 MiB 3/3, customized-config preservation, uninstall, and cleanup.
- Confirm `git status --short` is empty, no tag named `v0.1.1` exists locally or
  remotely, no v0.1.1 release exists, and v0.1.0 remote metadata/bytes are
  unchanged.
- Stop and present the commit, bytes, test logs, and receipt for internal review.
  **Do not push, tag, or publish without reviewed GO.**

## One manual publication after GO

1. Recheck that the reviewed commit and staged byte identities are unchanged.
2. Push that commit, then create one annotated tag `v0.1.1` at exactly that
   commit and push only that tag.
3. Create one GitHub prerelease for `v0.1.1` and upload exactly:
   - `azdaja-v0.1.1-darwin-arm64`
   - `azdaja-v0.1.1-linux-x86_64`
   - `SHA256SUMS`
4. Verify the peeled remote tag, release state, exact three-name asset set,
   asset sizes, GitHub digest metadata, downloaded bytes, and downloaded
   checksum manifest. Do not replace, add, rename, or edit published objects.

`SHA256SUMS` is 186 bytes with SHA-256
`339c08051f69d2492306890035d81afac603de0532b36e315db13e19d667e7c2`. The versioned
installer is 3961 bytes with prepublication
SHA-256 `d70e92bf8975840b6c13a18d3c65baca47ce59505e17d3ea6f46b676abf8c8b2`.

## Required postpublication receipts on both platforms

- Fetch the literal installer from raw tag `v0.1.1` into a new HOME and execute
  it without validation overrides.
- Compare installed bytes to the downloaded public release asset and the bound
  digest; prove the installation itself made no provider call.
- Run explicit live Jcode OpenAI subscription OAuth `doctor` using only an
  owner-only ephemeral credential copy.
- Run the three exact installed-binary 50 MiB cases: build log, repository dump,
  transcript; require 3/3.
- Reinstall over a customized managed config and prove preservation; uninstall
  and prove managed cleanup; remove isolated HOME/container and terminate all
  gate descendants.
- Record truthful platform-specific public receipts. A local gate is never a
  substitute for this public URL evidence.

The immutable v0.1.0 tag, release, asset, checksum, versioned installer, notes,
and receipts are out of scope and must never be mutated.
