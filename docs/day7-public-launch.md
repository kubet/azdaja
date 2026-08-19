# Day-7 public launch runbook

Status: **private staging only**. Nothing in this curated private-main
consolidation authorizes a visibility flip, tag, release, asset upload, email,
provider call, or ARC run.

The former calendar gate is superseded and is not an active launch gate. The
only launch gate is explicit owner approval: set `AZDAJA_OWNER_APPROVAL=GO` only
after the owner has reviewed the complete saga, complete README, and complete
private author email, and has confirmed the 16/16 install matrix is green. The
launch block refuses every other value, including an unset variable.

This consolidation owns the reviewed public-flip runbook, sanitized receipts,
launch saga, ARC results presentation, transport post-mortem, and final README
evidence pass. It does not perform launch actions. Do not open a PR and do not
run any publication step while consolidating or reviewing it.

## Bound launch statement

The staged saga contains this authorized result exactly once:

> **Launch result:** **68.64164968987583%** on a fixed 199-row, validation-derived RAH slice, with 185 execution successes (valid predictions) and 14 retained failures counted as zero.

Both preregistered levers are terminal FAIL. Neither authorized a successor
fixed-199 run, so this is the permanent launch result. The score block is frozen;
no substitution, rerun, resume, or rescore is authorized.

## Bound ARC and install evidence

The original five-game public-safe result remains:

> same harness, same model, ± Azdaja: -1.24% fewer wasted actions (1.24% more)

All five Ember-minus-baseline paired RHAE deltas are 0.0 and the retained
baseline/Ember wasted-action totals are 646/654. The retrieval-only follow-up
recovered no absolute results from the ten closed scorecards.

The later local-custody `vc33` smoke establishes, for both baseline and Ember,
0.0 shadow RHAE, zero levels, 35 total actions, per-level action counts
`[35, 0, 0, 0, 0, 0, 0]`, zero official-feedback waste, zero revisited states,
zero repeated known controls, 36 journal records, and `ACTION_BUDGET`
termination. The public ARC-v2 receipt binds those facts without publishing the
private streams.

The full five-game rerun is the **first post-launch update**. It must not run
before the public flip. Execution is handled by the owner-only package; this
public runbook deliberately does not invent or expose a command.

The sanitized v0.1.2 install receipt binds the implementation commit, 16/16
green cells, 14 genuine-provider positive cells, two expected graceful
no-harness refusals, two binary digests, the exact `SHA256SUMS` digest, and the
owner aggregate receipt digest. It retains no private paths, prompts, responses,
traces, credentials, or raw input.

## Private-main consolidation and remote-head cleanup

The intentional README, saga, CLI, ARC source, and sanitized evidence changes
are already curated together. Never reset or replay older README/saga commits
over them. Before any owner GO, the parent must fast-forward the reviewed local
head to private `main`, verify the exact remote commit, and delete every non-`main`
remote head while the repository remains private:

```bash
set -euo pipefail
REPO=kubet/azdaja
SOURCE_CONSOLIDATION=662b713f17a157cfd0241d87afcc3b9107232eed

# Run from the clean, reviewed launch/pre-main-consolidation worktree.
test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE
test "$(gh api "repos/$REPO" --jq .private)" = true
git fetch origin main --tags
CURATED_HEAD="$(git rev-parse HEAD)"
MAIN_BEFORE="$(git rev-parse origin/main)"
git merge-base --is-ancestor "$SOURCE_CONSOLIDATION" "$CURATED_HEAD"
git merge-base --is-ancestor "$MAIN_BEFORE" "$CURATED_HEAD"

git diff "$MAIN_BEFORE...$CURATED_HEAD" -- README.md docs/launch-saga.md \
  docs/day7-public-launch.md release/day7-public-launch.json \
  bench/results/install-matrix-v0.1.2-final-public.json \
  bench/results/install-real-adapters-v0.1.2-final-public.json tools/check_docs.py
python3 tools/check_docs.py
cargo fmt --all --check
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features --locked -- -D warnings
git diff --check
test -z "$(git status --porcelain)"

# A normal push must fast-forward private main; force is never permitted.
git push origin "$CURATED_HEAD:refs/heads/main"
test "$(git ls-remote origin refs/heads/main | awk '{print $1}')" = "$CURATED_HEAD"
git fetch origin main
test "$(git rev-parse origin/main)" = "$CURATED_HEAD"
test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE

# Remove every other remote head now, before approval GO or any publication.
branches_file="$(mktemp)"
trap 'rm -f "$branches_file"' EXIT
git ls-remote --heads origin > "$branches_file"
while read -r _ ref; do
  branch="${ref#refs/heads/}"
  if [ "$branch" != main ]; then
    git push origin --delete "$branch"
  fi
done < "$branches_file"
test "$(git ls-remote --heads origin | awk '{sub("refs/heads/", "", $2); print $2}')" = main
test "$(git ls-remote origin refs/heads/main | awk '{print $1}')" = "$CURATED_HEAD"
test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE
test "$(gh api "repos/$REPO" --jq .private)" = true
```

Stop there. Do not set the approval variable merely because those mechanical
checks pass, and do not flip visibility, create a tag or release, or send email.
The owner must separately complete the full saga, README, and private email
review and confirm the green matrix.

## Approval-gated private-main validation, build, tag, and release

Run the following only after private `main` contains the curated consolidation,
every non-`main` remote head has already been deleted, and the owner has
deliberately supplied the gate. It fresh-clones only `main`, validates the
complete receipt set and locked source, independently builds v0.1.2 validation
binaries from final `main` with Rust 1.95, then verifies and uploads the exact
final-matrix-tested candidate bytes retained in owner-only custody. It creates a
new annotated tag and GitHub release while private, verifies release-object
metadata without downloading an asset, and only then flips visibility.

The v0.1.1 tag and release are immutable and untouched. v0.1.2 must be new; any
pre-existing local tag, remote tag, or GitHub release is a hard stop.

```bash
set -euo pipefail
if [ "${AZDAJA_OWNER_APPROVAL:-}" != GO ]; then
  printf '%s\n' 'refusing launch: AZDAJA_OWNER_APPROVAL must equal GO' >&2
  exit 1
fi
export AZDAJA_OWNER_APPROVAL
if [ -z "${AZDAJA_RELEASE_ASSET_DIR:-}" ]; then
  printf '%s\n' 'refusing launch: AZDAJA_RELEASE_ASSET_DIR is required' >&2
  exit 1
fi

REPO=kubet/azdaja
TAG=v0.1.2
IMPLEMENTATION_COMMIT=662b713f17a157cfd0241d87afcc3b9107232eed
EXPECTED_DARWIN=1a8b442599c25eda05ba4d5a979e018148484ec0396610b900e85e7d9cef1a24
EXPECTED_LINUX=ed71f631e137400754fb089dcf29f7194956c559f614c281c628838a08ae032e
EXPECTED_SUMS=33e8e6985ab500d874e4dd32cd4661c8475c4d91202f6cca7c8eba1c09d81ad1
EXPECTED_MATRIX=6d6950dc55611130b3811b5988278f88ea00bffacc6fc9f29dfbd13e3d4044a9
EXPECTED_OWNER_AGGREGATE=6d6950dc55611130b3811b5988278f88ea00bffacc6fc9f29dfbd13e3d4044a9
EXPECTED_REAL_ADAPTERS=b3c657da9be4cff611e9286d40be553232e7e51cfb8fe9f1eb734d8433ef48a8
EXPECTED_CUSTODY_RECEIPT=d65dcc21a791ec7d2ab2c3c02428ffc3c678d95b44c75b18e335d1172c91d33d
EXPECTED_SOURCE_TREE=4e803f48a8784bd5322db2d3f47fe8cc578029b3
EXPECTED_ARC_V2=002deda1f7d6740b0aeffc277ea9f7bab87939960fd6644b6852f6e747f97551
EXPECTED_SCORE='68.64164968987583%'
EXPECTED_LINE='> **Launch result:** **68.64164968987583%** on a fixed 199-row, validation-derived RAH slice, with 185 execution successes (valid predictions) and 14 retained failures counted as zero.'
EXPECTED_ARC_LINE='> same harness, same model, ± Azdaja: -1.24% fewer wasted actions (1.24% more)'

test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE
test "$(gh api "repos/$REPO" --jq .private)" = true

# This SSH URL is only for the authenticated owner's fresh private-main clone.
SHIP_ROOT="$(mktemp -d)"
git clone --branch main --single-branch "git@github.com:${REPO}.git" \
  "$SHIP_ROOT/azdaja-day7-ship"
cd "$SHIP_ROOT/azdaja-day7-ship"
MAIN_HEAD="$(git rev-parse HEAD)"
test "$(git ls-remote origin refs/heads/main | awk '{print $1}')" = "$MAIN_HEAD"
test "$(git ls-remote --heads origin | awk '{sub("refs/heads/", "", $2); print $2}')" = main

# Validate public text, every JSON receipt, exact receipt bindings, and source.
test -f docs/launch-saga.md
test -f docs/transport-flip-postmortem.md
test -f bench/results/gpt-rah199-mortality-v3-terminal-public.json
test -f bench/results/endgame-agent-transport-v2-disease10-terminal.json
test -f bench/results/arc3-ember-five-public-v9-result.json
test -f bench/results/arc3-scorecard-interrogation-public-v1.json
test -f bench/results/arc3-vc33-smoke-v2-public.json
test -f bench/results/install-matrix-v0.1.2-final-public.json
test -f bench/results/install-real-adapters-v0.1.2-final-public.json
test "$(grep -Fxc "$EXPECTED_LINE" docs/launch-saga.md)" -eq 1
test "$(grep -Fxc "$EXPECTED_ARC_LINE" docs/launch-saga.md)" -eq 1
test "$(grep -Fc "$EXPECTED_SCORE" docs/launch-saga.md)" -eq 1
! grep -Fq 'SCORE_SUBSTITUTION_POINT' docs/launch-saga.md
! grep -Fq 'ENDGAME-FIXED199-SUBSTITUTION-POINT' README.md
! grep -Fq 'provisional only because' README.md

python3 - "$IMPLEMENTATION_COMMIT" "$EXPECTED_MATRIX" \
  "$EXPECTED_OWNER_AGGREGATE" "$EXPECTED_REAL_ADAPTERS" \
  "$EXPECTED_SOURCE_TREE" "$EXPECTED_ARC_V2" <<'PY'
import hashlib
import json
from pathlib import Path
import sys

implementation, matrix_sha, owner_aggregate_sha, real_adapters_sha, source_tree, arc_v2_sha = sys.argv[1:]
for root in (Path("bench/results"), Path("release")):
    for path in sorted(root.glob("*.json")):
        json.loads(path.read_text())

receipt_path = Path("release/day7-public-launch.json")
receipt = json.loads(receipt_path.read_text())
assert receipt["schema_version"] == 3
assert receipt["record_type"] == "day7_public_launch_private_main_consolidation_receipt"
assert receipt["status"] == "PRIVATE_MAIN_CONSOLIDATION_READY_NO_PUBLICATION"
assembly = receipt["assembly"]
assert assembly["target_branch"] == "main"
assert assembly["active_remote_branch_dependency"] is False
assert assembly["source_consolidation_commit"] == implementation
assert assembly["v0_1_2_implementation_commit"] == implementation
assert receipt["superseded_calendar_gate"]["active"] is False
assert receipt["superseded_calendar_gate"]["status"] == "superseded_by_explicit_owner_approval_and_green_install_matrix"
gate = receipt["approval_gate"]
assert gate["environment_variable"] == "AZDAJA_OWNER_APPROVAL"
assert gate["required_value"] == "GO"
assert gate["satisfied_at_staging"] is False
assert all(gate["required_reviews"].values())
assert gate["install_matrix_requirement"]["result"] == "PASS"
assert gate["install_matrix_requirement"]["green_cells"] == 16
assert gate["install_matrix_requirement"]["total_cells"] == 16

score = receipt["authorized_launch_score"]
assert score["percent"] == 68.64164968987583
assert score["fixed_denominator"] == 199
assert score["execution_successes"] == 185
assert score["retained_failure_zeros"] == 14
assert score["status"] == "permanent_final_no_successor_authorized"
assert score["successor_fixed_199_authorized"] is False

plan = receipt["release_plan"]
assert plan["version"] == "0.1.2"
assert plan["tag"] == "v0.1.2"
assert plan["implementation_commit"] == implementation
assert plan["candidate_source_commit"] == implementation
assert plan["source_tree"] == source_tree
assert plan["asset_source"] == "exact_final_matrix_tested_candidate_from_owner_only_custody"
assert plan["independent_rebuilds_are_validation_only"] is True
assert plan["owner_asset_directory_disclosed"] is False
assert plan["candidate_custody_receipt"]["sha256"] == "d65dcc21a791ec7d2ab2c3c02428ffc3c678d95b44c75b18e335d1172c91d33d"
assert plan["candidate_custody_receipt"]["local_path_disclosed"] is False
assert plan["rust_version"] == "1.95.0"
assert plan["v0_1_1_immutable"] is True
assert plan["release_assets_published_at_staging"] is False

matrix_path = Path("bench/results/install-matrix-v0.1.2-final-public.json")
real_adapters_path = Path("bench/results/install-real-adapters-v0.1.2-final-public.json")
assert hashlib.sha256(matrix_path.read_bytes()).hexdigest() == matrix_sha == owner_aggregate_sha
assert hashlib.sha256(real_adapters_path.read_bytes()).hexdigest() == real_adapters_sha
matrix = json.loads(matrix_path.read_text())
assert matrix["schema"] == "azdaja-install-matrix-aggregate-v2"
assert matrix["version"] == "0.1.2"
assert matrix["implementation_commit"] == implementation
assert matrix["source_tree"] == source_tree
assert matrix["result"] == {
    "expected_no_harness_failures_green": 2,
    "green_cells": 16,
    "positive_cells_passed": 14,
    "positive_exact_five_line_dragon_passed": 14,
    "total_cells": 16,
}
assert matrix["published_or_tagged"] is False
assert {asset["name"]: asset["sha256"] for asset in matrix["candidate_custody"]["assets"]} == plan["expected_assets"]
assert matrix["candidate_custody"]["exact_matrix_tested_bytes_retained"] is True
assert matrix["candidate_custody"]["do_not_rebuild_or_replace"] is True
assert matrix["real_installed_adapters"]["receipt_sha256"] == real_adapters_sha

arc_v2_path = Path("bench/results/arc3-vc33-smoke-v2-public.json")
assert hashlib.sha256(arc_v2_path.read_bytes()).hexdigest() == arc_v2_sha
arc_v2 = json.loads(arc_v2_path.read_text())
for arm in ("baseline", "ember"):
    observed = arc_v2["arms"][arm]
    assert observed["shadow_rhae"] == 0.0
    assert observed["levels_completed"] == 0
    assert observed["total_actions"] == 35
    assert observed["per_level_action_counts"] == [35, 0, 0, 0, 0, 0, 0]
    assert observed["wasted_actions"] == {
        "official_feedback_wasted_actions": 0,
        "revisited_states": 0,
        "repeated_known_controls": 0,
    }
    assert observed["journal"]["record_count"] == 36
    assert observed["termination"] == "ACTION_BUDGET"
assert arc_v2["paired"]["ember_minus_baseline_shadow_rhae_delta"] == 0.0
assert arc_v2["full_five_game_rerun"]["status"] == "HOLD"

full_five = receipt["second_act"]["arc"]["full_five_game_rerun"]
assert full_five == {
    "execution": "owner_only_package",
    "launch_order": "first_post_launch_update",
    "public_command": None,
    "status": "HOLD_UNTIL_AFTER_PUBLIC_FLIP",
}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()

saga_path = Path("docs/launch-saga.md")
runbook_path = Path("docs/day7-public-launch.md")
assert receipt["saga"]["sha256"] == sha256(saga_path)
assert receipt["saga"]["git_blob"] == git_blob(saga_path)
assert receipt["runbook"]["sha256"] == sha256(runbook_path)
assert receipt["runbook"]["git_blob"] == git_blob(runbook_path)
assert receipt["evidence"]["install_matrix_public_receipt_sha256"] == matrix_sha
assert receipt["evidence"]["install_matrix_owner_aggregate_receipt_sha256"] == owner_aggregate_sha
assert receipt["evidence"]["install_real_adapters_public_receipt_sha256"] == real_adapters_sha
assert receipt["evidence"]["arc_v2_public_receipt_sha256"] == arc_v2_sha
assert receipt["release_asset_requests_performed"] is False
PY

python3 tools/check_docs.py
cargo fmt --all --check
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features --locked -- -D warnings
git diff --check
test -z "$(git status --porcelain)"

# Validate the exact private-main head cloned above before any build or upload.
test "$(git rev-parse HEAD)" = "$MAIN_HEAD"
test -z "$(git status --porcelain)"

# Matrix hashes remain mandatory because release-affecting source is unchanged.
if ! git diff --quiet "$IMPLEMENTATION_COMMIT" HEAD -- Cargo.toml Cargo.lock src; then
  printf '%s\n' 'refusing launch: release-affecting source changed after the green install matrix' >&2
  exit 1
fi

test "$(uname -s)" = Darwin
test "$(uname -m)" = arm64
test "$(rustup run 1.95.0 rustc --version | awk '{print $2}')" = 1.95.0
WORK="$(mktemp -d)"
trap 'rm -rf "$SHIP_ROOT" "$WORK"' EXIT

# Build both targets independently to validate final-main source. These builds
# are not release bytes: clean Mach-O links are not hash-reproducible.
CARGO_TARGET_DIR="$WORK/target-darwin" \
  rustup run 1.95.0 cargo build --release --locked
docker run --rm --platform linux/amd64 \
  -v "$PWD:/src:ro" -v "$WORK:/out" -w /src \
  rust:1.95.0-bookworm \
  cargo build --release --locked --target-dir /out/target-linux
test "$("$WORK/target-darwin/release/azdaja" --version | awk '{print $2}')" = 0.1.2
docker run --rm --platform linux/amd64 -v "$WORK/target-linux/release:/assets:ro" \
  debian:bookworm-slim /assets/azdaja --version | \
  grep -Fx 'azdaja 0.1.2 (monty 0.0.21)'

# Release only the exact final-matrix-tested candidate retained by the owner.
test ! -L "$AZDAJA_RELEASE_ASSET_DIR"
ASSET_DIR="$(cd "$AZDAJA_RELEASE_ASSET_DIR" && pwd -P)"
test "$(stat -f '%Lp' "$ASSET_DIR")" = 700
test "$(find "$ASSET_DIR" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')" = 4
DARWIN_ASSET="$ASSET_DIR/azdaja-v0.1.2-darwin-arm64"
LINUX_ASSET="$ASSET_DIR/azdaja-v0.1.2-linux-x86_64"
SUMS_ASSET="$ASSET_DIR/SHA256SUMS"
CUSTODY_ASSET="$ASSET_DIR/candidate-custody.json"
for asset in "$DARWIN_ASSET" "$LINUX_ASSET" "$SUMS_ASSET" "$CUSTODY_ASSET"; do
  test -f "$asset"
  test ! -L "$asset"
done
DARWIN_SHA="$(shasum -a 256 "$DARWIN_ASSET" | awk '{print $1}')"
LINUX_SHA="$(shasum -a 256 "$LINUX_ASSET" | awk '{print $1}')"
test "$DARWIN_SHA" = "$EXPECTED_DARWIN"
test "$LINUX_SHA" = "$EXPECTED_LINUX"
test "$(wc -c < "$DARWIN_ASSET" | tr -d ' ')" = 6434272
test "$(wc -c < "$LINUX_ASSET" | tr -d ' ')" = 7941464
test "$(wc -c < "$SUMS_ASSET" | tr -d ' ')" = 186
test "$(shasum -a 256 "$SUMS_ASSET" | awk '{print $1}')" = "$EXPECTED_SUMS"
test "$(shasum -a 256 "$CUSTODY_ASSET" | awk '{print $1}')" = "$EXPECTED_CUSTODY_RECEIPT"
python3 - "$CUSTODY_ASSET" "$IMPLEMENTATION_COMMIT" "$EXPECTED_SOURCE_TREE" \
  "$EXPECTED_DARWIN" "$EXPECTED_LINUX" "$EXPECTED_SUMS" <<'PY'
import json
from pathlib import Path
import sys

path, implementation, tree, darwin, linux, sums = sys.argv[1:]
receipt = json.loads(Path(path).read_text())
assert receipt["source"] == {"commit": implementation, "tree": tree}
assert receipt["custody"]["assets_are_exact_matrix_tested_bytes"] is True
assert receipt["custody"]["do_not_rebuild_or_replace"] is True
assert receipt["SHA256SUMS"]["sha256"] == sums
assert {asset["name"]: asset["sha256"] for asset in receipt["exact_tested_assets"]} == {
    "azdaja-v0.1.2-darwin-arm64": darwin,
    "azdaja-v0.1.2-linux-x86_64": linux,
}
PY
(
  cd "$ASSET_DIR"
  shasum -a 256 -c SHA256SUMS
)
test "$("$DARWIN_ASSET" --version | awk '{print $2}')" = 0.1.2
docker run --rm --platform linux/amd64 -v "$ASSET_DIR:/assets:ro" \
  debian:bookworm-slim /assets/azdaja-v0.1.2-linux-x86_64 --version | \
  grep -Fx 'azdaja 0.1.2 (monty 0.0.21)'

# v0.1.2 must be a brand-new immutable annotated tag and release.
test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE
test "$(gh api "repos/$REPO" --jq .private)" = true
! git rev-parse -q --verify "refs/tags/$TAG" >/dev/null
! git ls-remote --exit-code --tags origin "refs/tags/$TAG" >/dev/null 2>&1
! gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1
git tag -a "$TAG" -m 'azdaja v0.1.2' "$MAIN_HEAD"
git push origin "refs/tags/$TAG"
test "$(git ls-remote origin "refs/tags/$TAG^{}" | awk '{print $1}')" = "$MAIN_HEAD"

gh release create "$TAG" \
  "$DARWIN_ASSET" \
  "$LINUX_ASSET" \
  "$SUMS_ASSET" \
  --repo "$REPO" --verify-tag --title 'azdaja v0.1.2' \
  --notes 'First-run install UX for Darwin arm64 and glibc Linux x86-64.'

# Query the release object only. Never request an asset API/browser URL.
gh api "repos/$REPO/releases/tags/$TAG" > "$WORK/release-metadata.json"
python3 - "$WORK/release-metadata.json" "$TAG" "$EXPECTED_DARWIN" \
  "$EXPECTED_LINUX" "$EXPECTED_SUMS" <<'PY'
import json
from pathlib import Path
import sys

path, tag, darwin, linux, sums = sys.argv[1:]
release = json.loads(Path(path).read_text())
assert release["tag_name"] == tag
assert release["draft"] is False
assert release["prerelease"] is False
assert release["name"] == "azdaja v0.1.2"
assets = {asset["name"]: asset for asset in release["assets"]}
assert set(assets) == {
    "azdaja-v0.1.2-darwin-arm64",
    "azdaja-v0.1.2-linux-x86_64",
    "SHA256SUMS",
}
assert assets["azdaja-v0.1.2-darwin-arm64"]["digest"] == f"sha256:{darwin}"
assert assets["azdaja-v0.1.2-linux-x86_64"]["digest"] == f"sha256:{linux}"
assert assets["SHA256SUMS"]["digest"] == f"sha256:{sums}"
assert all(asset["state"] == "uploaded" for asset in assets.values())
PY

# Private prestaging already removed every non-main remote head; recheck it.
test "$(git ls-remote --heads origin | awk '{sub("refs/heads/", "", $2); print $2}')" = main

# Only now perform the visibility flip.
test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE
test "$(gh api "repos/$REPO" --jq .private)" = true
gh repo edit "$REPO" --visibility public --accept-visibility-change-consequences
```

## Anonymous public verification

After the flip, verify public source plus the exact saga, README, installer
source, and sanitized install receipt. Fetching raw source files is permitted.
Do **not** execute `site/install` in this verification because that would fetch
release assets.

Release asset `GET` and `HEAD` requests are forbidden in verification. Do not
use `gh release download`, an asset API URL, a browser-download URL, `curl -I`,
or any equivalent asset request. The release-object metadata and digests were
already checked while private.

```bash
set -euo pipefail
REPO=kubet/azdaja
MAIN_HEAD="$(git ls-remote https://github.com/kubet/azdaja.git refs/heads/main | awk '{print $1}')"
test -n "$MAIN_HEAD"
test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PUBLIC
test "$(gh api "repos/$REPO" --jq .private)" = false

anon_home="$(mktemp -d)"
trap 'rm -rf "$anon_home"' EXIT
HOME="$anon_home" GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 \
  git -c credential.helper= clone --depth 1 \
  https://github.com/kubet/azdaja.git public-check
cd public-check
test "$(git rev-parse HEAD)" = "$MAIN_HEAD"

base=https://raw.githubusercontent.com/kubet/azdaja/main
curl -fsS "$base/README.md" -o "$anon_home/README.md"
curl -fsS "$base/docs/launch-saga.md" -o "$anon_home/launch-saga.md"
curl -fsS "$base/site/install" -o "$anon_home/install"
curl -fsS "$base/bench/results/install-matrix-v0.1.2-final-public.json" \
  -o "$anon_home/install-matrix.json"
curl -fsS "$base/bench/results/install-real-adapters-v0.1.2-final-public.json" \
  -o "$anon_home/install-real-adapters.json"
cmp README.md "$anon_home/README.md"
cmp docs/launch-saga.md "$anon_home/launch-saga.md"
cmp site/install "$anon_home/install"
cmp bench/results/install-matrix-v0.1.2-final-public.json \
  "$anon_home/install-matrix.json"
cmp bench/results/install-real-adapters-v0.1.2-final-public.json \
  "$anon_home/install-real-adapters.json"

python3 tools/check_docs.py
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

receipt = json.loads(Path("release/day7-public-launch.json").read_text())
checks = {
    "docs/launch-saga.md": receipt["saga"]["sha256"],
    "site/install": "36abdc64885cb9f9ff93daca6e1941ffbc7639fd7d3a3bd1034a6494b5bbf636",
    "bench/results/install-matrix-v0.1.2-final-public.json": "6d6950dc55611130b3811b5988278f88ea00bffacc6fc9f29dfbd13e3d4044a9",
    "bench/results/install-real-adapters-v0.1.2-final-public.json": "b3c657da9be4cff611e9286d40be553232e7e51cfb8fe9f1eb734d8433ef48a8",
    "bench/results/arc3-vc33-smoke-v2-public.json": "002deda1f7d6740b0aeffc277ea9f7bab87939960fd6644b6852f6e747f97551",
}
for name, expected in checks.items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected
readme = Path("README.md").read_text()
assert "curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/main/site/install | sh" in readme
assert "pre-release install matrix" in readme
assert "bench/results/install-matrix-v0.1.2-final-public.json" in readme
assert "bench/results/install-real-adapters-v0.1.2-final-public.json" in readme
assert "```bash\nazdaja uninstall\n```" in readme
PY
```

Stop immediately on any mismatch. Do not force-push, move or rewrite a tag,
replace a release, or retry around a failed invariant.

## Private author email — final launch step

The owner resolved the missing-canonical-repository question by converting the
prepared PR into a short author email. Send it only after the public flip and
all anonymous verification above succeed. The owner-only staging package
contains the reviewed message and its syntax-tested send script; this public
runbook intentionally omits local staging locations and recipient addresses.

The email script uses the same approval environment: preserve
`AZDAJA_OWNER_APPROVAL=GO` when invoking the exact owner-only command. Do not
invent a command here. Before sending, recheck that the reviewed recipients
still match the paper-published addresses, that the public README, receipt, and
saga links resolve, and that the message has no Cc or Bcc.

Mechanical launch order is therefore: **curated private-main fast-forward and
non-main remote-head cleanup; owner GO after full saga/README/email review and
green matrix; fresh private-main source validation, exact tested-candidate
v0.1.2 upload/tag/release; metadata-only release verification; public flip;
anonymous source/text/receipt verification; private author email**.
The full-five ARC rerun remains the first post-launch update and cannot precede
the flip.
