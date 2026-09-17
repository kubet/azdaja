# Historical notice artifacts, not current release approval

`THIRD-PARTY-NOTICES-pre-v0.1.17.md` preserves the complete former root notice byte-for-byte from baseline `4c3ba3e`. Its embedded candidate, scope, binding, and PASS wording are historical, not current approval.

Original SHA-256: `393cfd092b543059d376b96134e7dadf2da5e2f5e76df84d9edbca42d22f62d2`.

`Cargo.lock.notice-inputs` is the exact old lock bound by the retained `release/third-party-notice-inputs.json`, recovered from commit `c8da7fa83d07929cb19e72df5467148373d83078`. SHA-256: `f2ff24a523f718f12c7a3a40fbf412cc91346bf7acbb517ae23b98a3d7c1bfb3`. It is not the current project lock and does not validate the old notice's own still-older binding.

`published-notice-hashes.json` records unchanged public release assets, font files, LICENSE, and site configuration at the remediation baseline. These are preservation assertions, not permission to republish or update those assets.

See [current notice generation and verification](../THIRD-PARTY-NOTICE-GENERATION.md) for the authoritative current root notice, archive-backed index, exact-byte recovery, and public verifier.
