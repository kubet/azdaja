# `lb2-hard-long-63-v1`

`lb2-hard-long-63-v1` is a **private, harness-derived diagnostic** containing
exactly all 63 LongBench v2 rows whose upstream fields are
`difficulty == "hard"` and `length == "long"`. It is not an official LongBench
suite or leaderboard result, and results from this file/agent harness must never
be compared as though they were official direct-prompt LongBench numbers.

`generate.py` performs validation and sealing only. It performs **no inference**.

## Frozen source

The only accepted dataset revision is:

* repository: `zai-org/LongBench-v2` (the upstream documentation also uses the
  legacy `THUDM/LongBench-v2` name);
* revision: `2b48e494f2c7a2f0af81aae178e05c7e1dde0fe9`;
* `data.json`: 465,490,535 bytes, SHA-256
  `15d61c22d92c96900b3c4948b6aeea218d3214b676a65df48e7b8555604c7fe2`;
* `README.md`: 4,626 bytes, SHA-256
  `9fdd1a3ebe86507253c124a18e9f78c898ce6341c12990af17ab868b8f600c35`;
* `.gitattributes`: 2,507 bytes, SHA-256
  `b3ca89743b410b60a97ba9486e44b205c70f6fb35024ef02198cf766dfdffb18`.

The source has 503 rows and six frozen difficulty/length cells. The sealer first
validates every row's exact schema, taxonomy, count, cell count, unique upstream
ID, unique canonical row, and unique question/context/choices payload. Only then
does it filter. It additionally freezes selected domain and sub-domain cell counts, records
them in the public manifest, and checks them before gold is opened, so a 63-for-63
replacement does not pass. Answer syntax is checked, but answer aggregates are
deliberately not embedded in public code because they are gold.

This is **independent raw-source replay during generation**, not merely trust in
an embedded receipt: the sealer reads the exact 465,490,535-byte `data.json`,
checks its pinned SHA-256, strictly parses and validates all 503 rows, and only
then derives the cohort. The sealed gold provenance embeds the resulting pinned
receipts. A later scorer independently checks those receipts and all public/gold
commitments, but does not re-download or replay raw `data.json`.

Generation uses only the CPython standard library. The intentionally empty
third-party dependency lock is itself pinned by SHA-256. Remote retrieval is an
owner operation: the generator never follows an unpinned URL or trusts mutable
`main`. See `THIRD_PARTY_NOTICES.md` before distributing derived data.

## Download and seal privately

Use fresh paths, `umask 077`, and verify the revisioned downloads before invoking
the sealer. The following URLs are revision-pinned, but `generate.py` still
checks the exact bytes and refuses drift. `curl -fL` is illustrative; use your
controlled artifact downloader if required by policy.

```bash
cd /Users/vukasinkubet/dev/azdaja
umask 077
ROOT=$(mktemp -d /private/tmp/azdaja-lb2.XXXXXX)
PUBLIC="$ROOT/lb2-hard-long-63-v1-public"
GOLD="$ROOT/lb2-hard-long-63-v1-owner-gold"
BASE=https://huggingface.co/datasets/zai-org/LongBench-v2/resolve/2b48e494f2c7a2f0af81aae178e05c7e1dde0fe9

curl -fL "$BASE/data.json?download=true" -o "$ROOT/data.json"
curl -fL "$BASE/README.md?download=true" -o "$ROOT/README.md"
curl -fL "$BASE/.gitattributes?download=true" -o "$ROOT/.gitattributes"
chmod 600 "$ROOT/data.json" "$ROOT/README.md" "$ROOT/.gitattributes"

python3 bench/longbench2/generate.py \
  --data "$ROOT/data.json" \
  --readme "$ROOT/README.md" \
  --gitattributes "$ROOT/.gitattributes" \
  --difficulty hard --length long --expected-count 63 \
  --out-public "$PUBLIC" --out-gold "$GOLD" --yes-seal
```

By default the process obtains a fresh 256-bit secret from the OS CSPRNG. For a
reproducible private rerun, create a raw 32-byte owner-only file before sealing
and pass `--randomization-key /private/path/key.bin`. The key bytes are never
written to either output; only their SHA-256 appears in gold provenance. Never
commit or give this key to an inference runner.

All remote input artifact files must be owner-only regular files (0600), not
symlinks. Each output parent must already be an exactly 0700 owner-owned
directory. Both outputs must be fresh, separately rooted, non-nested paths and
must not be collocated or nested with run, claim, or report/output roots. The
sealer opens and holds both parent directory file descriptors, verifies their
pathname/inode bindings, and performs temp creation, writes, inventory checks,
fsync, cleanup, and kernel atomic no-replace renames relative to those descriptors.
Gold is made durable first; public is published last as the commit point. A
parent-path swap or raced target is never followed, replaced, or deleted. The
sealer writes directories as 0700 and files as 0600. If public publication loses
a race, the already durable owner-only gold root remains for explicit operator
cleanup; no public suite was committed. Failure handling is no-follow and fd-relative. Because POSIX has no portable
conditional-rmdir-by-inode primitive, the sealer does **not delete failed temp
trees**: it atomically moves the expected temp to a random `.abandoned-*`
quarantine name, verifies the inode, fsyncs the parent, and leaves it owner-only
for explicit operator inspection/removal. If a racer was caught instead, it is
restored with no-replace when possible and otherwise preserved in quarantine.
This intentionally prefers a harmless leftover over deleting a swapped racer.

## Exact preservation and public payload

For each selected upstream row, the inference payload is canonical UTF-8 JSON:

```json
{
  "question": "the exact upstream question",
  "context": "the exact upstream context",
  "choices": {
    "A": "the exact choice_A",
    "B": "the exact choice_B",
    "C": "the exact choice_C",
    "D": "the exact choice_D"
  }
}
```

The strings are copied exactly: there is no normalization, trimming, wrapping,
question rewriting, context truncation, or choice reordering. Canonicalization
only determines the JSON container bytes (`sort_keys=True`, compact separators,
UTF-8 without ASCII escaping, one final LF). Strict source parsing recognizes
only RFC JSON whitespace (space, tab, CR, LF), never Python's broader Unicode
whitespace set. The official answer is not included.
Fixture names are secret-keyed, randomized IDs, not upstream IDs or ordinals.

## Containment and gold-blindness threat model

Random fixture IDs provide **filename unlinking only**. They do not make gold
secret against a runner with network access, a Hugging Face/datasets cache, a
local copy of LongBench v2, or another content-addressed cache: each public
question/context/choice payload uniquely joins to the pinned upstream row and its
answer. Owner-only modes and separate roots prevent accidental collocation, not
content recognition.

A claim is blind only if the runner is launched inside an enforceable sandbox
that receives a public-root-only snapshot and denies all network access, DNS, the
Hugging Face/datasets caches, model/dataset caches, the source download, the
randomization key, the gold root, and run/report roots for other arms. The
operator must verify those controls **before** accepting a blind-run claim. This
repository currently supplies no LB2 runner or sandbox implementation; therefore
benchmark containment and gold blindness are advisory until such isolation is
provided and attested. Never infer blindness merely from randomized filenames.

The public root inventory is exact and contains only:

```text
manifest.json
LICENSE.LONGBENCH2
THIRD_PARTY_NOTICES.md
payloads/                         # exactly 63 entries
  lb2-<random 128-bit hex>.json
```

The separate gold root inventory is exactly one regular file: `gold.json`. Any
extra file, directory, symlink, socket, or missing entry fails validation. The
Apache-2.0 text and attribution notice are pinned byte-for-byte and their hashes
are committed by the manifest. The repository's top-level MIT license does not
license the LongBench-derived data.

The manifest contains inference-safe suite/source metadata, domains/sub-domains,
payload paths, byte counts, hashes, and an exact gold commitment. It contains no
answer, upstream ID, source ordinal, source-row hash, or randomization key hash.
The **runner must receive a public-only snapshot** of this root. It must not be
given the source download, key, or gold root.

The separate gold root contains only `gold.json`, which joins randomized IDs to
official answer labels and retains source ordinals/IDs and exact raw/canonical
row receipts for the owner/scorer. File modes reduce accidental disclosure; they
are not encryption or a substitute for OS isolation.

## Two-way byte commitments

Let `identity` be the canonical public manifest object with the top-level
`gold_sha256` field omitted. The sealer writes:

```text
gold.manifest_identity_sha256 = SHA256(canonical_bytes(identity))
manifest.gold_sha256 = SHA256(exact canonical gold.json bytes)
```

Omitting only `gold_sha256` from manifest identity avoids an impossible circular
hash while binding both artifacts in both directions. Consumers must verify exact
canonical encodings, all payload hashes, identical sets of 63 IDs, file types,
paths, ownership, and modes, and reject additions, omissions, duplicates, and
symlinks.

## Tests

```bash
python3 -m unittest discover -s bench/longbench2 -p 'test_*.py' -v
```

Tests use randomized synthetic upstream IDs and small local data, cover strict
shape/cell/preservation behavior, and tamper with hashes, duplicate keys/rows,
non-finite JSON, modes, symlinks, output roots, keys, and cross-file commitments.
They do not run inference or expose the pinned dataset's answer content.
