# `ruler-exact-mini-v1`

`ruler-exact-mini-v1` is Azdaja's 90-fixture **agent/file-harness**
complement to OOLONG. It is a disclosed three-task subset, not the complete
13-task RULER benchmark, and is not comparable to NVIDIA's direct-prompt RULER
leaderboard.

| Exact category | Pinned official task/config | Gold cardinality |
|---|---|---:|
| retrieval | `niah_multikey_3` | 1 UUID |
| multi-hop/tracing | `vt`, 1 chain / 4 hops | 5 variables |
| aggregation | `fwe`, Zipf alpha 2.0 | 3 coded words |

There are ten selected fixtures per task at each **target/maximum construction
length** 8,192, 32,768, and 131,072. A generated row may be shorter than its
target. Public `row_length` is the row's exact RULER construction length;
`construction_tokens + task_reserve == row_length <= target_length`, with
reserves 128/30/50. These are `cl100k_base` construction tokens, not bytes,
provider billing tokens, or a promise that every row exactly reaches its target.

`generate.py` never performs model inference.

## Frozen provenance and trust boundary

Production `build` requires:

* NVIDIA/RULER commit `c3f5e3b4f87f97e048793bb510a3a6b19a46bf3a`
  (Apache-2.0), plus SHA-256 for every transitive local file used;
* a worktree whose complete non-`.git` inventory exactly equals the pinned Git
  archive (no dirty, untracked, symlink, submodule, special-file, or executable
  mode drift);
* CPython 3.11 in a dedicated virtual environment launched with `-I -S -B`,
  plus exactly one compatible locked wheel per distribution; installed
  site-packages are ignored and never imported;
* the `cl100k_base` blob SHA-256
  `223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7`;
* NLTK `punkt.zip` SHA-256
  `51c3078994aeaf650bfc8e028be4fb42b4a0d177d41c012b6a983979653660ec`
  and `punkt_tab.zip` SHA-256
  `e57f64187974277726a3417ca6f181ec5403676c717672eef6a748a7b20e0106`.

Git commands neutralize fsmonitor/hooks and global/system configuration.
Generation never executes the supplied worktree: it executes a freshly
materialized, re-hashed `git archive` of the pinned commit. Locked wheels are
safely extracted without `.pth`, customization modules, symlinks, special files,
`.data` relocation, traversal, duplicates, or overlaps; their complete runtime
inventory hash is recorded. Both `prepare.py` and its nested bare-`python` task
run through `-I -S -B` bootstraps whose only third-party path is that snapshot,
so venv/user `sitecustomize`, `.pth`, and modified installed modules are never
imported. Tokenizer and NLTK inputs are copied into a private snapshot; verified
NLTK archives are safely extracted before execution. A sanitized environment
binds both RULER processes to exact `sys.executable`, supplies only pinned
resources, points proxies at a closed local endpoint, rejects downloader output,
and fails if any runtime/dependency snapshot changes. RULER's `prepare.py` can catch a child error
and exit zero, so `build` independently requires exactly one 100-row JSONL file
per cell and fully validates it.

This supports Darwin and Linux POSIX filesystems only: owner IDs, modes,
`O_NOFOLLOW`, directory fsync, and platform atomic no-replace directory
publication are required. It fails closed on Windows
rather than pretending POSIX modes create an owner-only DACL. Gold records the
exact CPython executable/build and OS/release/architecture. The executable
itself and operating system are trusted local inputs; this code does not verify
a CPython binary signature or provide a hermetic kernel/network sandbox.

See `THIRD_PARTY_NOTICES.md`. Every generated public tree contains that notice
and the exact pinned RULER license as `LICENSE.NVIDIA-RULER`.

## Private generation

Use a new owner-only directory. Do not commit or copy the plan, private build
scratch, gold, schedules, claims, or run artifacts into a public/inference tree.

```bash
cd /Users/vukasinkubet/dev/azdaja
umask 077
unset PYTHONPATH PYTHONHOME
# Use a trusted absolute base whose resolved path contains only ASCII letters,
# digits, dot, underscore, hyphen, and slash; do not inherit an arbitrary TMPDIR.
G=$(mktemp -d "/tmp/azdaja-ruler.XXXXXX")
G=$(cd "$G" && pwd -P)  # eliminate `/tmp` symlink aliases (for example macOS)
case "$G" in (*[!A-Za-z0-9._/-]*) echo "unsafe generation path: $G" >&2; exit 1;; esac
chmod 700 "$G"
mkdir -m 700 "$G/private" "$G/scratch"
PUBLIC="$G/ruler-exact-mini-v1-public"
GOLD="$G/private/gold.json"

git clone https://github.com/NVIDIA/RULER.git "$G/RULER"
git -C "$G/RULER" checkout --detach c3f5e3b4f87f97e048793bb510a3a6b19a46bf3a
test "$(git -C "$G/RULER" rev-parse HEAD)" = \
  c3f5e3b4f87f97e048793bb510a3a6b19a46bf3a

uv venv --python 3.11 "$G/venv"
uv pip sync --python "$G/venv/bin/python" --require-hashes \
  bench/ruler/requirements.lock
mkdir -m 700 "$G/wheelhouse"
export PATH="$G/venv/bin:/usr/bin:/bin"
# Resolve the platform tag from this exact CPython (for example macosx_14_0_arm64)
# and download only matching cp311/py3 wheels. pip verifies every byte against
# requirements.lock; no sdist or extra file is allowed.
uvx --from 'pip==25.1.1' pip download --only-binary=:all: --require-hashes \
  --python-version 311 --implementation cp --abi cp311 \
  --platform <audited-platform-tag> \
  --dest "$G/wheelhouse" -r bench/ruler/requirements.lock
chmod 600 "$G"/wheelhouse/*.whl
export NLTK_DATA="$G/nltk_data"
export TIKTOKEN_CACHE_DIR="$G/tiktoken_cache"
python -m nltk.downloader -d "$NLTK_DATA" punkt punkt_tab
python -c 'import tiktoken; tiktoken.get_encoding("cl100k_base")'

python -I -S -B bench/ruler/generate.py plan --out "$G/generation-plan.json"
python -I -S -B bench/ruler/generate.py build \
  --plan "$G/generation-plan.json" \
  --ruler-source "$G/RULER" \
  --wheelhouse "$G/wheelhouse" \
  --scratch-parent "$G/scratch" \
  --tiktoken-cache-dir "$TIKTOKEN_CACHE_DIR" \
  --nltk-data "$NLTK_DATA" \
  --tasks niah_multikey_3 vt fwe \
  --lengths 8192 32768 131072 \
  --pool-size 100 --per-cell 10 \
  --out "$PUBLIC" --gold-out "$GOLD" --yes-build
```

The fixed task/length/count flags expose the declared design; any deviation is
rejected. `build` generates all nine pools internally in private temporary
storage, validates/selects immediately, and deletes the temporary pools. There
is no production command that trusts an externally supplied pool.

### Procedural selection commitment

`plan` exclusively and atomically publishes a canonical owner-only file holding
a fresh 256-bit master key and nine deterministically derived 32-bit generator
seeds. The owner must create it **before** `build`, retain its hash in review
records, and reject/restart the release procedure if it is replaced. Selection
and random fixture IDs are deterministic from this plan.

This is a procedural commitment, not a cryptographic timestamp or external TSA.
An owner able to make many plans and inspect many private generations can grind
the selection. Publication review should record the one plan hash created before
generation and every declared fixed-plan verification build; claims of an
externally provable precommitment require a separate trusted timestamp or
transparency system.

### Exact fixed-plan regeneration check

For release review, run `build` twice with the same plan, environment, and exact
`--out`/`--gold-out` path strings. After the first succeeds, move both artifacts
to private comparison names (do not edit them), repeat the same build command,
and compare the two manifests, gold files, notices/licenses, and all 90 payloads
byte-for-byte. Ephemeral scratch paths are randomized securely under `--scratch-parent`, but gold
receipts use fixed logical `/RULER`, `/POOL`, and `/RUNTIME` placeholders, so
physical paths do not change sealed bytes. Any mismatch fails release. A crashed
build may leave a private `azdaja-ruler-build-*` directory under the scratch
parent; inspect the failure and remove it explicitly before retrying.
This comparison proves deterministic reproduction for one recorded plan and
local platform; it does not remove the procedural plan-grinding trust boundary.

## Exact rows, payloads, and selection

Every upstream line must have the exact pinned task row schema. JSON duplicate
keys, non-finite numbers, lone Unicode surrogates, booleans in integer fields,
extra config metadata, and noncanonical plan data fail. The builder checks exact
task prompt/prefix shapes, VT/FWE line index identities, NIAH output literal /
character index / token-position identities, task output domains/cardinalities,
and FWE frequency ordering. The authoritative proof that the rows came from the
declared 1-chain/4-hop and alpha-2.0 configurations is internal execution of the
exact pinned generator and argv; arbitrary row content is never accepted by the
production CLI.

Payload bytes are exactly:

```python
payload = row["input"] + row["answer_prefix"]
```

There is no wrapping, rewording, normalization, or reconstruction. The builder
requires exact UTF-8, exact tokenizer identities, the length identity above, and
no duplicate payload SHA-256 among all 900 rows.

NIAH rows are sorted by official `token_position_answer`, divided into ten equal
answer-position deciles, and one secret-HMAC-ranked row is selected per decile.
VT/FWE use the ten secret-HMAC-ranked line ordinals. HMAC ranking depends on the
secret cell key and ordinal/decile, not mutable row content or global PRNG state.

## Public/private separation and commitments

`--out` and `--gold-out` must have distinct, pre-existing owner-only 0700 parent
directories. A successful build creates:

```text
$PUBLIC/manifest.json                  public/inference-safe metadata
$PUBLIC/payloads/<random>.txt          exact official prompt payloads
$PUBLIC/LICENSE.NVIDIA-RULER           pinned upstream license
$PUBLIC/THIRD_PARTY_NOTICES.md         redistribution notice
$GOLD                                  outputs, exact selected raw rows, plan,
                                       seeds, hashes, and provenance receipts
```

Files are 0600 and directories 0700. Gold is staged outside the public tree,
exclusively published and file/parent-fsynced first; the public root is then
published with an atomic no-replace directory rename and parent fsync. A crash
can leave orphan private gold with no public suite, but never intentionally
publishes a public manifest before its committed gold is durable. On a caught
pre-publication failure, newly published gold is safely rolled back. Existing or
raced targets are never merged, replaced, or followed.

Top-level `redistribution_files` commits the exact SHA-256 of both public notice
files; loaders require the exact public-root and payload-directory inventories
and rehash them. Each public fixture has only `id`, `task`, `target_length`,
relative `payload`, `payload_sha256`, `payload_bytes`, `construction_tokens`, and `row_length`.
`manifest.json.gold_sha256` hashes the exact canonical `gold.json` bytes. To
avoid a circular hash, `gold.json.manifest_identity_sha256` hashes canonical
compact public-manifest bytes (sorted keys, UTF-8, compact separators, final LF)
with only top-level `gold_sha256` omitted. Gold stores each selected exact
`raw_row_utf8`; scoring recomputes its raw and canonical hashes, outputs,
payload identity, lengths, and task semantics before using references.

The inference host must receive a **copy of `$PUBLIC` only**. Never copy `$G`,
`$G/private`, `$GOLD`, or the plan to that host. The runner accepts only the
public manifest/payload tree. Deferred scoring uses an explicit private path,
for example `score.py --manifest "$PUBLIC/manifest.json" --gold "$GOLD" ...`,
and opens gold only after terminal schedule/run validation. Owner-only modes
reduce accidental disclosure; they are not encryption or an information-flow
sandbox.

## Release review / tests

Before publication, reviewers should procedurally verify: the recorded plan hash
predates every declared fixed-plan build; source checkout inventory is exact; the build
printed the expected separate paths; only the public tree is staged for release;
no plan/gold/run files are tracked; and an independent validation recomputes both
manifest/gold commitments and every payload hash.

```bash
python3 -m unittest discover -s bench/ruler -p 'test_*.py' -v
```

### Telemetry authority

The scorer rehashes retained stdout and model-trace bytes and independently
recomputes their internal route and token arithmetic. The Azdaja model trace is
still emitted by the candidate, not signed by the provider, so this establishes
internal consistency rather than provider authenticity. Lifecycle fields are
controller assertions. Provider-signed or broker-captured receipts would be
required for adversarial-candidate telemetry claims.
