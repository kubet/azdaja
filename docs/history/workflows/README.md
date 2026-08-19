# Archived workflow definitions

These are exact, non-active copies of the last tracked v0.1.0-bound workflows. They are retained to preserve the historical receipt bindings after their removal from `.github/workflows/`; they are not current release instructions and cannot be dispatched from this directory.

| Archived definition | SHA-256 | Historical evidence |
|---|---|---|
| [`public-release-integrity-v0.1.0.yml`](public-release-integrity-v0.1.0.yml) | `89a0f91e7167f414aeaf1057402db7692501d50dbc5ddd247ce4d2b8e98567c1` | [v0.1.0 metadata-only integrity receipt](../../../release/v0.1.0/public-release-integrity-receipt.json) |
| [`source-install-v0.1.0.yml`](source-install-v0.1.0.yml) | `3642ed50f13a6cd1ba81df69718da69213abcbf50585dfe1541758e3b12771b1` | [v0.1.0 source-installed 50 MiB receipt](../../../release/v0.1.0/public-source-installed-50mb-receipt.json) |

The current active source/install workflow validates checked-out source and a loopback HTTP fixture. It does not fetch release assets or mutate a release.
