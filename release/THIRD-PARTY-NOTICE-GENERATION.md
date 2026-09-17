# Current third-party notice generation and verification

This is an offline, source-backed engineering check, **not legal-sufficiency approval** and not permission to publish. The current artifact is the repository-root `THIRD-PARTY-NOTICES.md`, paired with `release/current-third-party-notice.json`. There is no separate CURRENT candidate notice. The public release entry point remains **`release/verify-third-party-notices.py`** (plural, as invoked by the release workflow). `verify-current-third-party-notice.py` is a compatibility alias for that same gate.

## Inputs and prerequisites

Run in a complete source checkout with Python 3.9 or newer, the repository's supported Rust/Cargo toolchain already available, its exact `Cargo.toml` and `Cargo.lock`, and the checksum-matching `.crate` archives and Cargo registry metadata already cached. No Python dependencies or installs are needed. No target toolchain compilation is needed for Cargo tree. A missing archive, ambiguous duplicate cached archive, checksum mismatch, unresolved offline closure, or non-registry dependency fails closed. The scripts do not fetch dependencies or call providers.

The generator imports `audit-third-party-notice-inputs.py` for its already-tested Cargo/lock/packaged-manifest parsing, path checks, named-legal-file inventory, and archive checksum checks. It resolves the root-excluded closures for **default** and **default plus typesafe**, each on:

- `aarch64-apple-darwin`
- `x86_64-apple-darwin`
- `x86_64-unknown-linux-gnu`

`cargo tree --locked --offline` uses Cargo's default edge selection (normal, build, and dev dependencies). This is a conservative dependency closure, not a linked-symbol inventory. `--features typesafe` retains default features. The manifest, lock, package declarations, archive hashes, and every package's separate feature/target membership are bound in the index. At v0.1.17 the default union is 191 packages, typesafe is 242, and the combined union has 402 named legal-file occurrences. Target counts are 189/190/190 and 240/241/241 respectively. These are observed values, not a verifier substitute for re-resolving the inputs.

## Reproduce without publishing

```sh
python3 release/build-current-third-party-notice.py
python3 release/verify-third-party-notices.py
python3 -m unittest discover -s release -p 'test_*notice*.py' -v
CARGO_NET_OFFLINE=true cargo test --locked --offline --test notice_distribution -- --test-threads=1
cargo fmt --all --check
```

Generation writes only the root notice and its machine index. Review both diffs together. Verification is read-only and independently regenerates source evidence and the expected rendering from actual cached archives on every invocation, then requires **exact bytes** for both artifacts. It does not trust a newly substituted notice hash, self-consistent index hashes, or assertions in a candidate rendering.

To generate scratch outputs or use an alternate archive-cache directory:

```sh
python3 release/build-current-third-party-notice.py \
  --cache "$HOME/.cargo/registry/cache" \
  --output /your/scratch/current-index.json --notice /your/scratch/current-notice.md
python3 release/verify-third-party-notices.py \
  --cache "$HOME/.cargo/registry/cache" \
  --index /your/scratch/current-index.json --notice /your/scratch/current-notice.md \
  --lockfile Cargo.lock
```

`--notice` and `--lockfile` remain supported. An alternate lockfile must be byte-identical to the checkout's actual lock, because Cargo resolves against that actual manifest/lock pair. `--cache` is the directory containing registry subdirectories, not an extracted source directory. Cargo itself uses its configured Cargo home for offline metadata. Generation/verification work from another working directory because the project root is derived from the script path.

## Exact bytes and rendering

The index stores 170 distinct current text bodies once, keyed by their **source-byte SHA-256**. Each of the 402 occurrences records package, version, archive-relative path, source byte count, and body hash. Declarations and manifest hashes come from the archived normalized Cargo.toml, not a guessed SPDX interpretation or an extracted working copy.

To recover a named file exactly:

```python
import hashlib, json
from pathlib import Path
index = json.loads(Path('release/current-third-party-notice.json').read_bytes())
package = next(p for p in index['packages'] if p['name'] == 'ahash')
occurrence = package['license_files'][0]
raw = index['bodies'][occurrence['sha256']]['text'].encode('utf-8')
assert len(raw) == occurrence['bytes']
assert hashlib.sha256(raw).hexdigest() == occurrence['sha256']
# Path('/your/scratch/recovered-license').write_bytes(raw)
```

No newline conversion is applied to indexed UTF-8 strings. CRLF, lone CR, trailing LF, and any UTF-8 BOM round-trip. Body metadata separately counts CRLF/LF/lone CR and records whether source bytes end in LF. Invalid UTF-8 fails rather than being replaced. Markdown converts CRLF and lone CR to LF, retains trailing source newlines, and adds one framing LF only when a body has no final LF. A fence longer than every source backtick run prevents embedded text from closing the fence. Framing is never source content.

Named-file enumeration does not supersede source-header, embedded, README, font, or other obligations. Packages with no supplied named legal file are called out explicitly. No claim is made that scanning these names constitutes a complete legal audit.

## Historical preservation and publication boundaries

`release/historical/THIRD-PARTY-NOTICES-pre-v0.1.17.md` is the **complete old root notice, unchanged**, including its old claims and binding. Its original SHA-256 is:

`393cfd092b543059d376b96134e7dadf2da5e2f5e76df84d9edbca42d22f62d2`

The current root also retains all 182 historical non-named-file text records verbatim in a separate historical appendix: 136 header blocks, 40 header/marker records, four plain legal sections, one embedded legal file, and one font record. They preserve their original occurrence/package/path labels. They are neither newly audited nor claimed current or complete. The original whole-file hash is checked before every generation and verification.

The older `third-party-notice-inputs.json` and reconciliation JSON remain historical evidence. `reconcile-third-party-notice.py --check` reproduces them against the frozen historical root and `release/historical/Cargo.lock.notice-inputs`, recovered byte-for-byte from commit `c8da7fa83d07929cb19e72df5467148373d83078`. That lock's SHA-256 is `f2ff24a523f718f12c7a3a40fbf412cc91346bf7acbb517ae23b98a3d7c1bfb3`. It is not the current project lock or a replacement public release gate.

`release/historical/published-notice-hashes.json` freezes every existing published release payload/receipt/checksum, the font files, root LICENSE, and site configuration. These tests do not rebind or alter any published release. Site notice/license delivery and existing `site/releases/` bytes are untouched. Do not deploy the site or publish assets as part of notice regeneration.

The assembler now requires the same source-backed public verifier before copying the notice, while retaining its five-payload checksums and existing copying semantics. Therefore assembly also requires a complete source checkout and populated offline cache. Tests exercise the real public verifier with bad lock bindings, declarations, source bytes (including self-consistent forged hashes), archive bytes, occurrence attribution, historical attribution, feature/target membership, and noncanonical index/rendering bytes. They also prove a tampered notice is rejected by the assembler before any output file is changed. This validates the notice path, **not the entire release process**.

## Frozen installer and current binary custody

`site/install` and `site/install.ps1` are unchanged. The existing Unix installer still pins the old `393cfd...` notice hash and intentionally rejects the new unpublished current notice even if a download manifest correctly hashes it. Installer fixtures now use the retained old full notice, not a rewritten published artifact. Changing installer acceptance or publishing a candidate requires a separate release decision.

The current binary derives its current managed-document marker from its exact embedded LICENSE and root notice bytes. It separately recognizes the historical `393cfd...` marker only with that exact old notice SHA-256 and the exact LICENSE. Existing previous-v2 and legacy-v1 acceptance remains unchanged. Current/historical cross-pairs, modified bytes, and self-consistent attacker-chosen markers are rejected. Historical bytes are not newly embedded in the binary, so Cargo's package allowlist is unchanged.

Additional real boundary checks (all installation actions stay inside disposable test homes):

```sh
CARGO_NET_OFFLINE=true cargo test --locked --offline --test lifecycle_ux --test site_installer -- --test-threads=1
```

These include upgraded-binary uninstall of current and historical notice generations, every-step rollback with the historical generation added, and frozen-installer rejection of the current unpublished notice without home mutation. They do not demonstrate a current-notice public installation or a full release pass.

## CI prerequisites, distinct from proof reproduction

The `ci.yml` test job, `release.yml` publication preflight, and `verify-proof.yml` **separate notices job** install the already-pinned Rust 1.95.0 action and run `cargo fetch --locked --target ...` for all three supported targets before notice checks. Cargo fetch includes locked optional dependencies, unlike a default-host build alone. This is explicit CI cache preparation with network access, not part of the offline verifier and not an operation performed by notice generation. No verifier skip or hash-only fallback is permitted.

The first-party proof job remains Python/Git-only: its unit test and `proof/reproduction/run.sh` do not acquire a Rust dependency. The separate notice job uses Python 3.9, pinned Cargo, and actual cached archives. Relevant manifest, current index/generator, root notice, and historical paths trigger it. Workflow prerequisites are locally parsed/tested, not claimed remotely executed.

Current-source CI and the source-install workflow now label their local HTTP path as **current binary / frozen installer compatibility**. They copy and hash-check the historical `393cfd...` notice and compare those exact installed bytes. The source-install workflow separately verifies the current archive-backed notice and runs the explicit frozen-installer/current-notice rejection test. The main CI package allowlist matches the unchanged Cargo include scope, including judge.rs and the three memory submodules. Optional provider-free judge unit and native tests are separate commands, so a unit-test filter cannot silently select zero native tests.

**Frozen proof binding caveat:** the existing first-party proof manifest binds the former workflow bytes and source commit. The authorized workflow prerequisite changes therefore cause the unchanged proof verifier to fail closed with an artifact-size/hash mismatch until the coordinator explicitly reconciles that source/evidence binding. This repair does not reissue measured receipts, rewrite the proof manifest, or claim the full proof/release gate passed.
