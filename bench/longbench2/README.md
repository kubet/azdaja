# `lb2-hard-long-63-v1`

`lb2-hard-long-63-v1` is a **private, harness-derived diagnostic** containing
exactly all 63 LongBench v2 rows whose upstream fields are
`difficulty == "hard"` and `length == "long"`. It is not an official LongBench
suite or leaderboard result, and results from this file/agent harness must never
be compared as though they were official direct-prompt LongBench numbers.

`generate.py` performs validation and sealing only and performs **no inference**.
`run.py` is the separate subscription-inference ceremony; it never accepts a
gold path. `score.py` is the owner-only deferred scorer.

## Mandatory offline pre-freeze rehearsal

Every fresh production run now requires a completed `rehearsal.py` receipt for
its exact manifest, candidate, controller, rehearsal, validator, OOLONG adapter,
versioned executables, Node/Prime package/kernel/runtime recursive closures,
candidate config, seed, and timeout. This is a fixed, deterministic
20-fixture x 3-arm synthetic pipeline exercise. It performs no OAuth and no
inference, and its distinct `lb2_pre_freeze_rehearsal_*` records are never a
benchmark or candidate-performance claim.

```bash
umask 077
REHEARSAL_PARENT=$(mktemp -d /private/tmp/azdaja-lb2-rehearsal.XXXXXX)
python3 bench/longbench2/rehearsal.py run \
  --bundle "$REHEARSAL_PARENT/bundle" \
  --target-manifest "$PUBLIC/manifest.json" \
  --target-candidate /absolute/path/to/candidate \
  --target-jcode /absolute/path/to/jcode \
  --target-prime-agent /absolute/path/to/prime-agent \
  --target-seed 20260813 --target-timeout 1800

python3 bench/longbench2/rehearsal.py verify \
  --receipt "$REHEARSAL_PARENT/bundle/final-receipt.json"
```

The offline run boundary has no gold argument. The fixed wrapper uses the production
schedule constructor and claim-before-job / canonical-append / done-after-row
helpers to write exactly 60 production-shaped deferred rows, 60 claims, 60 done
receipts, and 60 production-shaped artifact directories. The no-gold terminal
stage calls the shared `validate_run_rows`, `validate_claims`, and
`validate_artifact_rows` authorities. Committed actual v43 success and retry raw
bytes are parsed by both the real OOLONG adapter parsers and scorer parser. Only
then is synthetic gold opened; shared score-row, aggregate, paired-comparison,
and report-core code runs and must match the exact committed synthetic oracle. The
final receipt is published last and binds the complete bundle inventories and
production target.

Pass that exact receipt only on a **fresh** production invocation:

```bash
python3 bench/longbench2/run.py ... \
  --pre-freeze-rehearsal-receipt "$REHEARSAL_PARENT/bundle/final-receipt.json" \
  --yes-run-inference
```

Absence, tamper, target drift, or incomplete bundle replay is refused before
OAuth preflight or production artifact creation. `--resume` refuses the CLI
option and instead reopens the full receipt bound into the frozen schedule; no
verification skip exists. The production contract remains exactly 63 fixtures,
189 jobs, three fixed arms, and the preregistered 16-correct candidate gate.
The receipt's path and all target source paths must therefore remain available
and byte-identical through resume.

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
operator must verify those controls **before** accepting a blind-run claim.
The implemented `run.py` passes no gold path and stages only one captured public
payload for each job, but it deliberately asserts neither an OS sandbox nor
network/DNS/cache containment. Native tools retain ambient host access, and the
retained post-hoc tool-event scan is not enforcement. Consequently this runner's
artifacts explicitly describe the cohort as publicly answer-joinable and
nonblind. Never infer blindness merely from randomized filenames.

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

## Frozen three-arm inference ceremony

`run.py` executes exactly 189 serial subscription-OAuth jobs: every one of the
63 fixtures once under each of `jcode-native`, `jcode-azdaja`, and
`prime-agent`. The model is fixed to `gpt-5.6-luna`, reasoning is fixed to
`medium`, and repetitions are fixed to one; the CLI cannot select a subset.
The default schedule seed is `20260813` and the default per-job timeout is 1,800
seconds. `random.Random(seed)` shuffles the 63 fixtures once and then shuffles
the three arms within each fixture. Independently of that deterministic order,
each arm receives the captured public payload as the sole 0444 file in a fresh
task directory under a CSPRNG-generated 128-bit filename. That random staging
name is not a gold-hiding mechanism.

The runner freezes the captured public tree, controller, live scorer, OOLONG
execution adapter, explicit candidate, Jcode executable, and executable version
receipts before publishing the schedule. For Prime it freezes the **complete npm
package**, a selected Node executable, the complete Prime kernel venv, and the
base Python runtime prefix to which the frozen venv launcher is retargeted. The
schedule binds recursive inventories for those trees. The live controller and
scorer must continue to equal their frozen bytes, and resume revalidates the
snapshots rather than resolving new tools.

This is a bounded runtime closure, not a hermetic machine image. Node and Python
dynamic libraries, the OS/kernel runtime, OAuth homes, and the model network
service remain ambient and are not snapshotted. Per-job OAuth homes are isolated
and removed after retained credential-redacted trajectories are captured, but
those controls do not remove ambient host filesystem or network reachability.

### Install and stage the exact candidate

Rust 1.95, Jcode, Prime Agent, Node, the Prime kernel venv, and valid paid
OpenAI subscription OAuth logins for both Jcode and Prime must already be
available. From this checkout, build and install the Jcode adapter, then copy
only the three treatment inputs into a fresh owner-only candidate directory:

```bash
cd /Users/vukasinkubet/dev/azdaja
umask 077
cargo build --release
./target/release/azdaja install --harness jcode

RUN_ROOT=$(mktemp -d /private/tmp/azdaja-lb2-run.XXXXXX)
chmod 700 "$RUN_ROOT"
CANDIDATE="$RUN_ROOT/candidate"
mkdir -m 700 "$CANDIDATE"
install -m 600 "$HOME/.jcode/skills/azdaja/SKILL.md" "$CANDIDATE/SKILL.md"
install -m 700 "$HOME/.jcode/skills/azdaja/azdaja" "$CANDIDATE/azdaja"
install -m 600 "$HOME/.jcode/skills/azdaja/config.toml" "$CANDIDATE/config.toml"
python3 - "$CANDIDATE" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
assert {x.name for x in p.iterdir()} == {"SKILL.md", "azdaja", "config.toml"}
PY
```

`azdaja install` performs its own one-call adapter canary; it is not one of the
189 benchmark jobs. The managed installed directory also contains
`.azdaja-managed`, so it is **not** itself an accepted `--azdaja-skill`.
The explicit candidate must be a non-symlink directory with exactly
`SKILL.md`, executable `azdaja`, and `config.toml`, with no fourth entry. Its
files must be singly linked, owned by the runner, and not group/other writable.
The config must pin `sub_llm_cmd="jcode-api"`,
`default_model="gpt-5.6-luna"`, `jcode_provider="openai"`, and
`jcode_reasoning="medium"`.

### No-benchmark-inference preflight

There is no `--preflight` or dry-run flag. The following command calls the exact
current validation/auth helpers, version probes, and Jcode offline auth-status
probe without running a model turn or opening gold. The fresh runner repeats the
candidate, executable, OAuth, and kernel preflight **before** creating the work
root, output, schedule, or claims; only then does it perform the recursive
snapshots. This separate command is an operator-visible advance check, not a
substitute for the runner's fail-closed preflight.

```bash
cd /Users/vukasinkubet/dev/azdaja
export CANDIDATE
export JCODE=$(command -v jcode)
export PRIME_AGENT=$(command -v prime-agent)
test -x "$JCODE" && test -x "$PRIME_AGENT" && test -x "$(command -v node)"
test -x "$HOME/.prime/agent/kernel-venv/bin/python"

python3 - <<'PY'
import importlib.util, os, sys
from pathlib import Path
path = Path("bench/longbench2/run.py").resolve()
spec = importlib.util.spec_from_file_location("lb2_documented_preflight", path)
assert spec is not None and spec.loader is not None
run = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = run
spec.loader.exec_module(run)

candidate = Path(os.environ["CANDIDATE"])
if candidate.is_symlink():
    raise SystemExit("candidate must not be a symlink")
run.candidate_identity(candidate)
adapter = run._load_python("lb2_documented_source_adapter", run.OOLONG_SOURCE)
run._validate_adapter_contract(adapter)
adapter.MODEL, adapter.REASONING = run.MODEL, run.REASONING
adapter.validate_skill(str(candidate))
jcode = run._resolve_executable(os.environ["JCODE"], "jcode")
prime = run._resolve_executable(os.environ["PRIME_AGENT"], "prime-agent")
node = run._resolve_executable("node", "Node")
run.find_prime_package_root(prime)
run._version_identity(jcode, "jcode")
run._version_identity(candidate / "azdaja", "azdaja")
run._version_identity(node, "Node")
run._version_identity(prime, "prime-agent", path_prefix=node.parent)
home = Path(os.environ["HOME"]).expanduser().resolve(strict=True)
adapter.preflight_jcode(home, str(jcode))
adapter.preflight_prime(home)
print("LB2 source candidate, tools, and OAuth preflight: ok")
PY

python3 bench/longbench2/run.py --help
python3 bench/longbench2/score.py --help
```

Do not use plain `azdaja doctor` as a no-inference check: it runs a sub-model
canary (`azdaja doctor --caps` is local only). Do not change `PATH`, `HOME`, the
candidate, credentials, source files, or tools between preflight and the fresh
invocation.

### Fresh inference run

Set `PUBLIC` to the sealed public root; do not place or expose gold on the
inference host. Keep the variables from the installation block in the same
private shell. The runs directory must be fresh owner-only storage, while
`WORK` itself must not exist. Public, runs, and work paths may share a parent
but must be lexically distinct and pairwise non-nested.

```bash
cd /Users/vukasinkubet/dev/azdaja
umask 077
PUBLIC=/absolute/path/lb2-hard-long-63-v1-public
mkdir -m 700 "$RUN_ROOT/runs" "$RUN_ROOT/reports"
RUNS="$RUN_ROOT/runs/lb2-hard-long-63-v1.jsonl"
WORK="$RUN_ROOT/work"
for p in "$RUNS" "$RUNS.schedule.json" "$RUNS.claims" "$WORK"; do
  test ! -e "$p" && test ! -L "$p"
done

python3 bench/longbench2/run.py \
  --manifest "$PUBLIC/manifest.json" \
  --output "$RUNS" \
  --work-dir "$WORK" \
  --seed 20260813 --timeout 1800 \
  --model gpt-5.6-luna --reasoning medium \
  --jcode "$JCODE" \
  --prime-agent "$PRIME_AGENT" \
  --azdaja-skill "$CANDIDATE" \
  --pre-freeze-rehearsal-receipt "$REHEARSAL_PARENT/bundle/final-receipt.json" \
  --yes-run-inference
```

This command performs 189 potentially billed subscription turns. The mandatory
acknowledgement is intentionally explicit. Fresh execution creates the output
with `O_CREAT|O_EXCL`, creates the canonical schedule and claim/completion files
exclusively, and refuses any existing output/schedule/claims target. The work
root and every per-job directory must also be newly created. Artifacts are
owner-only; do not move, edit, truncate, replace, or add entries to them.
Exit 0 means terminal completion with no execution-failure rows; exit 1 means a
terminal 189-row artifact containing at least one explicit execution failure;
exit 2 is refusal/error and must not be interpreted as terminal completion.

### Exact-prefix resume

Resume with the same manifest, output, work path, seed, and timeout:

```bash
cd /Users/vukasinkubet/dev/azdaja
python3 bench/longbench2/run.py \
  --manifest "$PUBLIC/manifest.json" \
  --output "$RUNS" \
  --work-dir "$WORK" \
  --resume \
  --seed 20260813 --timeout 1800 \
  --model gpt-5.6-luna --reasoning medium \
  --jcode "$JCODE" \
  --prime-agent "$PRIME_AGENT" \
  --yes-run-inference
```

`--azdaja-skill` is a fresh-only explicit candidate and is optional on resume;
the resume command above deliberately omits it. Resume does not re-freeze or
consult a source candidate directory: it executes the candidate, Jcode, Prime
package, Node, venv, Python prefix, adapter, controller, scorer, and public tree
already frozen under `WORK`. A resume accepts only a canonical byte-exact
scheduled prefix whose retained trajectories rehash and whose claim directory
contains exactly one claim and one matching completion for every committed row.

A claim is created **before** a job can incur inference; the row is appended and
then its completion receipt is created. A crash after the claim but before both
later commits leaves an orphan (including the ambiguous case where the provider
turn completed or was billed). That extra/missing receipt deliberately makes the
prefix non-resumable so the controller cannot issue a duplicate billed turn.
Do not delete an orphan or fabricate a completion to force resume. Preserve the
artifacts for audit and, if a rerun is authorized, start a wholly fresh
output/claims/work ceremony.

### Owner-only terminal scoring

Only after all 189 rows, all 189 claim/completion pairs, and the complete retained
trajectory tree exist may the owner use the separate owner-only `gold.json`.
`--artifacts-root` is mandatory and must name the runner's exact `WORK/runs`
directory. The scorer treats it as an independent held directory authority: its
inventory must be exactly the 189 scheduled run directories; each directory and
file inventory, owner-only mode, absolute receipt path, byte count, and SHA-256
must match its row. It independently re-extracts the response from retained
`stdout.ndjson` and requires exact equality with the recorded raw response.

Do not relocate the trajectory tree: artifact receipts bind its absolute paths.
If artifacts are transferred to a separate owner machine, reproduce the same
absolute `WORK/runs` pathname and preserve every byte, mode, and inventory entry.
The scorer also requires schedule and claims to be the exact
`<runs>.schedule.json` and `<runs>.claims` siblings even when spelled explicitly.
The report root must be owner-only, fresh, and outside the public, gold, runs,
schedule, claims, and artifacts roots; the report path must not exist.

```bash
cd /Users/vukasinkubet/dev/azdaja
umask 077
PUBLIC=/absolute/path/lb2-hard-long-63-v1-public
GOLD_JSON=/absolute/private/path/lb2-hard-long-63-v1-owner-gold/gold.json
RUNS=/absolute/private/path/runs/lb2-hard-long-63-v1.jsonl
ARTIFACTS_ROOT=/absolute/private/path/work/runs
REPORT_ROOT=$(mktemp -d /private/tmp/azdaja-lb2-report.XXXXXX)
chmod 700 "$REPORT_ROOT"
REPORT="$REPORT_ROOT/lb2-hard-long-63-v1-scores.json"
test ! -e "$REPORT" && test ! -L "$REPORT"

python3 bench/longbench2/score.py \
  --manifest "$PUBLIC/manifest.json" \
  --gold "$GOLD_JSON" \
  --runs "$RUNS" \
  --schedule "$RUNS.schedule.json" \
  --claims "$RUNS.claims" \
  --artifacts-root "$ARTIFACTS_ROOT" \
  --output "$REPORT" \
  --bootstrap-seed 20260813 \
  --bootstrap-resamples 100000
```

The scorer establishes the owner-only gold-directory authority early, but does
not open, hash, parse, or state `gold.json` until the public manifest, exact
three-arm schedule, 189 canonical terminal rows, 378 exact claim/completion
files, and all 189 exact retained trajectory directories (including independently
re-extracted responses) have passed no-gold validation. Partial, orphaned, moved,
or trajectory-tampered runs therefore cannot open gold. The report is published
0600 with an exclusive temporary and an atomic no-replace rename; an existing
report is never replaced.

The runner records the raw final assistant text without trimming or whitespace
normalization. The strict diagnostic accepts only a full-string exact match to
`The correct answer is (X)` for uppercase A-D. The separately reported official
metric reproduces pinned LongBench-v2 `pred.py`: remove `*`, search the
case-sensitive parenthesized phrase first and then its bare-letter variant, and
compare the extracted label exactly. Diagnostics flag multiple, contradictory,
negated, quoted, hypothetical, or corrected matches but do not change that
official extraction behavior.

Every arm has a fixed denominator of 63. The report separates execution failure,
completed-answer failure, all-terminal-output extraction, completed-only
accuracy, and end-to-end fixed-denominator accuracy; the end-to-end metrics
count execution failures as incorrect. Paired comparisons and their deterministic
fixture bootstrap do not change the denominator.

## Claim and telemetry limitations

This is a private, derived, publicly answer-joinable diagnostic. It is nonblind,
is not the complete official LongBench-v2 evaluation, is not an official
leaderboard submission, and cannot substantiate a leaderboard, SOTA, release,
or product-superiority claim. Wrapper/product differences also mean its numbers
must not be presented as official direct-prompt LongBench results.

The schedule hashes, local claim/completion receipts, route checks, token
arithmetic, retained CLI trajectories, and candidate traces establish internal
consistency under this controller. They are not externally signed. In
particular, Azdaja traces are emitted by the candidate, lifecycle/timing fields
are local controller assertions, and the provider does not sign the retained
usage or answer record. Provider-signed receipts, a trusted inference broker,
external timestamp/signing, and an enforceable containment attestation would be
required for adversarial-candidate telemetry, billing, timing, or blindness
claims.

## Tests

```bash
python3 -m unittest discover -s bench/longbench2 -p 'test_*.py' -v
```

Tests use randomized synthetic upstream IDs and small local data, cover strict
shape/cell/preservation behavior, and tamper with hashes, duplicate keys/rows,
non-finite JSON, modes, symlinks, output roots, keys, and cross-file commitments.
They do not run inference or expose the pinned dataset's answer content.
