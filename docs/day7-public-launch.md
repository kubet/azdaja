# Day-7 public launch runbook

Status: **private staging only**. Nothing in this assembly authorizes a visibility
flip, tag, release, asset upload, email, provider call, or ARC run.

The former calendar gate is superseded and is not an active launch gate. The
only launch gate is explicit owner approval: set `AZDAJA_OWNER_APPROVAL=GO` only
after the owner has reviewed the complete saga, complete README, and complete
private author email, and has confirmed the 16/16 install matrix is green. The
launch block refuses every other value, including an unset variable.

This branch owns the reviewed public-flip runbook, sanitized receipts, launch
saga, ARC results presentation, transport post-mortem, and final README evidence
pass. It does not perform launch actions. Do not open a PR and do not run any
publication step while assembling or reviewing this branch.

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

## Private assembly review

The intentional README, saga, and sanitized install-matrix changes are part of
the assembly. Never reset or replay older README/saga commits over them. Review
and push the private branch with:

```bash
set -euo pipefail
REPO=kubet/azdaja
ASSEMBLY=launch/day7-public-assembly

git fetch origin --prune --tags
git switch "$ASSEMBLY"
git diff origin/main...HEAD -- README.md docs/launch-saga.md \
  docs/day7-public-launch.md release/day7-public-launch.json \
  bench/results/install-matrix-v0.1.2-public.json tools/check_docs.py
python3 tools/check_docs.py
cargo fmt --all --check
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features --locked -- -D warnings
git diff --check
test -z "$(git status --porcelain)"
git push --set-upstream origin "$ASSEMBLY"
test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE
```

Do not set the approval variable merely because those mechanical checks pass.
The owner must separately complete the full saga, README, and private email
review and confirm the green matrix.

## Approval-gated private merge, build, tag, and release

Run the following only after the owner has deliberately supplied the gate. It
merges the assembly into `main` while private, validates the complete receipt
set and locked source, builds fresh v0.1.2 assets from final `main` with Rust
1.95, creates the exact checksums file, creates a new annotated tag and GitHub
release while private, verifies release-object metadata without downloading an
asset, removes non-`main` heads, and only then flips visibility.

The v0.1.1 tag and release are immutable and untouched. v0.1.2 must be new; any
pre-existing local tag, remote tag, or GitHub release is a hard stop.

```bash
set -euo pipefail
if [ "${AZDAJA_OWNER_APPROVAL:-}" != GO ]; then
  printf '%s\n' 'refusing launch: AZDAJA_OWNER_APPROVAL must equal GO' >&2
  exit 1
fi
export AZDAJA_OWNER_APPROVAL

REPO=kubet/azdaja
ASSEMBLY=launch/day7-public-assembly
TAG=v0.1.2
IMPLEMENTATION_COMMIT=a06a5acacf32c20dc19855bae54a013312b34597
EXPECTED_DARWIN=4fdb907c0af87be49d82ec82849848ca340eae99aeb02d7e18691f19fa39b6b7
EXPECTED_LINUX=8ab01cc6c14c6d02e3a0cc2cbfbf12c28c4a7ab662bb9d892bffaf1b567c4e4b
EXPECTED_SUMS=80fbdebeb6587552f6d04062427d3a699b67c1680b1857d35c30c86c588acb5b
EXPECTED_MATRIX=9170d7527c52d2d7ec7972639c8c3f1df776dfb5c2722b71f5102f79b74ffbf7
EXPECTED_OWNER_AGGREGATE=d7413c826f3efc9124c757705c1fffa7b3099102497193f2a436b9e7a230290b
EXPECTED_ARC_V2=002deda1f7d6740b0aeffc277ea9f7bab87939960fd6644b6852f6e747f97551
EXPECTED_SCORE='68.64164968987583%'
EXPECTED_LINE='> **Launch result:** **68.64164968987583%** on a fixed 199-row, validation-derived RAH slice, with 185 execution successes (valid predictions) and 14 retained failures counted as zero.'
EXPECTED_ARC_LINE='> same harness, same model, ± Azdaja: -1.24% fewer wasted actions (1.24% more)'

test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE
test "$(gh api "repos/$REPO" --jq .private)" = true

# This SSH URL is only for the authenticated owner's internal private clone.
git clone "git@github.com:${REPO}.git" azdaja-day7-ship
cd azdaja-day7-ship
git fetch origin --prune --tags
git switch -c day7-ship origin/main
git merge --no-ff --no-edit "origin/$ASSEMBLY"

# Validate public text, every JSON receipt, exact receipt bindings, and source.
test -f docs/launch-saga.md
test -f docs/transport-flip-postmortem.md
test -f bench/results/gpt-rah199-mortality-v3-terminal-public.json
test -f bench/results/endgame-agent-transport-v2-disease10-terminal.json
test -f bench/results/arc3-ember-five-public-v9-result.json
test -f bench/results/arc3-scorecard-interrogation-public-v1.json
test -f bench/results/arc3-vc33-smoke-v2-public.json
test -f bench/results/install-matrix-v0.1.2-public.json
test "$(grep -Fxc "$EXPECTED_LINE" docs/launch-saga.md)" -eq 1
test "$(grep -Fxc "$EXPECTED_ARC_LINE" docs/launch-saga.md)" -eq 1
test "$(grep -Fc "$EXPECTED_SCORE" docs/launch-saga.md)" -eq 1
! grep -Fq 'SCORE_SUBSTITUTION_POINT' docs/launch-saga.md
! grep -Fq 'ENDGAME-FIXED199-SUBSTITUTION-POINT' README.md
! grep -Fq 'provisional only because' README.md

python3 - "$IMPLEMENTATION_COMMIT" "$EXPECTED_MATRIX" \
  "$EXPECTED_OWNER_AGGREGATE" "$EXPECTED_ARC_V2" <<'PY'
import hashlib
import json
from pathlib import Path
import sys

implementation, matrix_sha, owner_aggregate_sha, arc_v2_sha = sys.argv[1:]
for root in (Path("bench/results"), Path("release")):
    for path in sorted(root.glob("*.json")):
        json.loads(path.read_text())

receipt_path = Path("release/day7-public-launch.json")
receipt = json.loads(receipt_path.read_text())
assert receipt["schema_version"] == 2
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
assert plan["rust_version"] == "1.95.0"
assert plan["v0_1_1_immutable"] is True
assert plan["release_assets_published_at_staging"] is False

matrix_path = Path("bench/results/install-matrix-v0.1.2-public.json")
assert hashlib.sha256(matrix_path.read_bytes()).hexdigest() == matrix_sha
matrix = json.loads(matrix_path.read_text())
assert matrix["schema"] == "azdaja-install-matrix-public-v1"
assert matrix["version"] == "0.1.2"
assert matrix["implementation_commit"] == implementation
assert matrix["result"] == "PASS"
assert matrix["cells"] == {"expected_no_harness_failures": 2, "green": 16, "positive": 14, "total": 16}
assert matrix["owner_aggregate_receipt_sha256"] == owner_aggregate_sha
assert matrix["assets"] == plan["expected_assets"]
assert matrix["release_assets_published"] is False

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
assert receipt["saga"]["sha256"] == sha256(saga_path)
assert receipt["saga"]["git_blob"] == git_blob(saga_path)
assert receipt["evidence"]["install_matrix_public_receipt_sha256"] == matrix_sha
assert receipt["evidence"]["install_matrix_owner_aggregate_receipt_sha256"] == owner_aggregate_sha
assert receipt["evidence"]["arc_v2_public_receipt_sha256"] == arc_v2_sha
assert receipt["release_asset_requests_performed"] is False
PY

python3 tools/check_docs.py
cargo fmt --all --check
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features --locked -- -D warnings
git diff --check
test -z "$(git status --porcelain)"

# Finalize private main before building. All assets are built from this exact main.
git push origin HEAD:main
MAIN_HEAD="$(git rev-parse HEAD)"
test "$(git ls-remote origin refs/heads/main | awk '{print $1}')" = "$MAIN_HEAD"
git fetch origin main
git switch --detach origin/main
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
DIST="$(mktemp -d)"
trap 'rm -rf "$DIST"' EXIT
mkdir "$DIST/assets"

CARGO_TARGET_DIR="$DIST/target-darwin" \
  rustup run 1.95.0 cargo build --release --locked
cp "$DIST/target-darwin/release/azdaja" \
  "$DIST/assets/azdaja-v0.1.2-darwin-arm64"

docker run --rm --platform linux/amd64 \
  -v "$PWD:/src:ro" -v "$DIST:/out" -w /src \
  rust:1.95.0-bookworm \
  cargo build --release --locked --target-dir /out/target-linux
cp "$DIST/target-linux/release/azdaja" \
  "$DIST/assets/azdaja-v0.1.2-linux-x86_64"

test "$("$DIST/assets/azdaja-v0.1.2-darwin-arm64" --version | awk '{print $2}')" = 0.1.2
docker run --rm --platform linux/amd64 -v "$DIST/assets:/assets:ro" \
  debian:bookworm-slim /assets/azdaja-v0.1.2-linux-x86_64 --version | \
  grep -Fx 'azdaja 0.1.2 (monty 0.0.21)'

DARWIN_SHA="$(shasum -a 256 "$DIST/assets/azdaja-v0.1.2-darwin-arm64" | awk '{print $1}')"
LINUX_SHA="$(shasum -a 256 "$DIST/assets/azdaja-v0.1.2-linux-x86_64" | awk '{print $1}')"
test "$DARWIN_SHA" = "$EXPECTED_DARWIN"
test "$LINUX_SHA" = "$EXPECTED_LINUX"
printf '%s  %s\n%s  %s\n' \
  "$EXPECTED_DARWIN" azdaja-v0.1.2-darwin-arm64 \
  "$EXPECTED_LINUX" azdaja-v0.1.2-linux-x86_64 \
  > "$DIST/assets/SHA256SUMS"
test "$(shasum -a 256 "$DIST/assets/SHA256SUMS" | awk '{print $1}')" = "$EXPECTED_SUMS"
(
  cd "$DIST/assets"
  shasum -a 256 -c SHA256SUMS
)

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
  "$DIST/assets/azdaja-v0.1.2-darwin-arm64" \
  "$DIST/assets/azdaja-v0.1.2-linux-x86_64" \
  "$DIST/assets/SHA256SUMS" \
  --repo "$REPO" --verify-tag --title 'azdaja v0.1.2' \
  --notes 'First-run install UX for Darwin arm64 and glibc Linux x86-64.'

# Query the release object only. Never request an asset API/browser URL.
gh api "repos/$REPO/releases/tags/$TAG" > "$DIST/release-metadata.json"
python3 - "$DIST/release-metadata.json" "$TAG" "$EXPECTED_DARWIN" \
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

# A public repository exposes every branch. Delete all non-main remote heads.
branches_file="$DIST/branches"
git ls-remote --heads origin | awk '{sub("refs/heads/", "", $2); print $2}' > "$branches_file"
while IFS= read -r branch; do
  if [ "$branch" != main ]; then
    git push origin --delete "$branch"
  fi
done < "$branches_file"
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
curl -fsS "$base/bench/results/install-matrix-v0.1.2-public.json" \
  -o "$anon_home/install-matrix.json"
cmp README.md "$anon_home/README.md"
cmp docs/launch-saga.md "$anon_home/launch-saga.md"
cmp site/install "$anon_home/install"
cmp bench/results/install-matrix-v0.1.2-public.json \
  "$anon_home/install-matrix.json"

python3 tools/check_docs.py
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

receipt = json.loads(Path("release/day7-public-launch.json").read_text())
checks = {
    "docs/launch-saga.md": receipt["saga"]["sha256"],
    "site/install": "36abdc64885cb9f9ff93daca6e1941ffbc7639fd7d3a3bd1034a6494b5bbf636",
    "bench/results/install-matrix-v0.1.2-public.json": "9170d7527c52d2d7ec7972639c8c3f1df776dfb5c2722b71f5102f79b74ffbf7",
    "bench/results/arc3-vc33-smoke-v2-public.json": "002deda1f7d6740b0aeffc277ea9f7bab87939960fd6644b6852f6e747f97551",
}
for name, expected in checks.items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected
readme = Path("README.md").read_text()
assert "curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/main/site/install | sh" in readme
assert "pre-release install matrix" in readme
assert "bench/results/install-matrix-v0.1.2-public.json" in readme
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

Mechanical launch order is therefore: **owner GO after full saga/README/email
review and green matrix; private merge and validation; fresh private v0.1.2
build/tag/release; metadata-only release verification; delete non-main heads;
public flip; anonymous source/text/receipt verification; private author email**.
The full-five ARC rerun remains the first post-launch update and cannot precede
the flip.
