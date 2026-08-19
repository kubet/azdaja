# Day-7 public launch runbook

Status: **private staging only**. Do not run the launch block before
`2026-08-26T00:20:29.359377+00:00`. Preparing, reviewing, and pushing the
private assembly branch is allowed before then; changing repository visibility
or publishing the saga is not.

This branch owns only the public-flip runbook, its sanitized receipt, and the
launch-saga assembly. README work is intentionally owned by the separate
`docs/endgame-readme-evidence-v1` branch and must be cherry-picked as a
single documentation-only commit before the launch block is used.

## Bound launch statement

The staged saga contains this authorized result exactly once:

> **Launch result:** **68.64164968987583%** on a fixed 199-row, validation-derived RAH slice, with 185 execution successes (valid predictions) and 14 retained failures counted as zero.

This is the permanent launch result if neither preregistered lever clears its
fixed gate. The only permitted replacement is the single fresh fixed-199 result
allowed by `ENDGAME.md`: it must be terminal, valid, owner-authorized, and
committed with a sanitized terminal receipt. If that exceptional replacement
exists, update the blockquote and `release/day7-public-launch.json` together on
the private assembly branch, rerun the checks below, and review the diff before
Day 7. No other score substitution is authorized.

## Pre-Day-7 private assembly

The documentation-only README input is source commit
`0ed643e31a93cc060cf7a4917108224f13553ee5`; it changes only `README.md` and
`tools/check_docs.py`. It has already been cherry-picked into this assembly.
Do not merge the README branch's benchmark ancestry and do not edit its evidence
presentation independently. To reconstruct and push the private assembly, use:

```bash
set -euo pipefail
REPO=kubet/azdaja
ASSEMBLY=launch/day7-public-assembly
README_COMMIT=0ed643e31a93cc060cf7a4917108224f13553ee5

git fetch origin --prune --tags
git switch "$ASSEMBLY"
git show --stat --oneline "$README_COMMIT"
# Reconstruction only: cherry-pick README_COMMIT once if its two-file diff is absent.
python3 tools/check_docs.py
git diff --check
test -z "$(git status --porcelain --untracked-files=no)"
git push --set-upstream origin "$ASSEMBLY"
test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE
```

At the launch freeze, the README owner must either apply the one authorized
successor row or remove its substitution marker and provisional sentence. The
Day-7 block below refuses to publish either marker.

## Day-7 launch block — exact commands

Run from a fresh directory. This block gates the exact hard timestamp, merges
and pushes the reviewed private assembly while the repository is still private,
removes every non-`main` remote head so private experiment branches do not
become public, flips visibility, and verifies anonymous source reachability.
It does not request release assets.

```bash
set -euo pipefail
REPO=kubet/azdaja
ASSEMBLY=launch/day7-public-assembly
DEADLINE=2026-08-26T00:20:29.359377+00:00
EXPECTED_SCORE='68.64164968987583%'
EXPECTED_LINE='> **Launch result:** **68.64164968987583%** on a fixed 199-row, validation-derived RAH slice, with 185 execution successes (valid predictions) and 14 retained failures counted as zero.'

python3 - "$DEADLINE" <<'PY'
from datetime import datetime, timezone
import sys

deadline = datetime.fromisoformat(sys.argv[1])
now = datetime.now(timezone.utc)
if now < deadline:
    raise SystemExit(f"refusing public launch before {deadline.isoformat()}; now={now.isoformat()}")
PY

test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE
test "$(gh api "repos/$REPO" --jq .private)" = true

git clone "git@github.com:${REPO}.git" azdaja-day7-ship
cd azdaja-day7-ship
git fetch origin --prune --tags
git switch -c day7-ship origin/main
git merge --no-ff --no-edit "origin/$ASSEMBLY"

test -f docs/launch-saga.md
test "$(grep -Fxc "$EXPECTED_LINE" docs/launch-saga.md)" -eq 1
test "$(grep -Fc "$EXPECTED_SCORE" docs/launch-saga.md)" -eq 1
! grep -Fq 'SCORE_SUBSTITUTION_POINT' docs/launch-saga.md
! grep -Fq 'ENDGAME-FIXED199-SUBSTITUTION-POINT' README.md
! grep -Fq 'provisional only because' README.md
python3 - <<'PY'
import json
from pathlib import Path

receipt = json.loads(Path("release/day7-public-launch.json").read_text())
score = receipt["authorized_launch_score"]
assert receipt["hard_public_launch_not_before"] == "2026-08-26T00:20:29.359377+00:00"
assert score["percent"] == 68.64164968987583
assert score["fixed_denominator"] == 199
assert score["execution_successes"] == 185
assert score["retained_failure_zeros"] == 14
assert score["status"] == "final_unless_single_preregistered_replacement_is_authorized"
assert receipt["release_asset_requests_performed"] is False
PY

python3 tools/check_docs.py
git diff --check
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features -- -D warnings
test -z "$(git status --porcelain)"

# Merge/push assembly and ship docs/launch-saga.md while still private.
git push origin HEAD:main
MAIN_HEAD="$(git rev-parse HEAD)"
test "$(git ls-remote origin refs/heads/main | awk '{print $1}')" = "$MAIN_HEAD"
test "$(git show HEAD:docs/launch-saga.md | grep -Fxc "$EXPECTED_LINE")" -eq 1

# A public repository exposes every remaining branch. Delete all non-main heads.
branches_file="$(mktemp)"
trap 'rm -f "$branches_file"; if [ -n "${anon_home:-}" ]; then rm -rf "$anon_home"; fi' EXIT
git ls-remote --heads origin | awk '{sub("refs/heads/", "", $2); print $2}' > "$branches_file"
while IFS= read -r branch; do
    if [ "$branch" != main; then
        git push origin --delete "$branch"
    fi
done < "$branches_file"
test "$(git ls-remote --heads origin | awk '{sub("refs/heads/", "", $2); print $2}')" = main

# Mandatory public visibility flip. Never run this command before DEADLINE.
gh repo edit kubet/azdaja --visibility public --accept-visibility-change-consequences

# Mandatory authenticated and anonymous verification; source only, no release assets.
test "$(gh repo view kubet/azdaja --json visibility --jq .visibility)" = PUBLIC
test "$(gh api repos/kubet/azdaja --jq .private)" = false
anon_home="$(mktemp -d)"
PUBLIC_HEAD="$(HOME="$anon_home" GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 \
  git -c credential.helper= ls-remote https://github.com/kubet/azdaja.git refs/heads/main | awk '{print $1}')"
test "$PUBLIC_HEAD" = "$MAIN_HEAD"
HOME="$anon_home" GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 \
  git -c credential.helper= clone --depth 1 https://github.com/kubet/azdaja.git public-check
cd public-check
test "$(grep -Fxc "$EXPECTED_LINE" docs/launch-saga.md)" -eq 1
test "$(git rev-parse HEAD)" = "$MAIN_HEAD"
```

Stop immediately on any mismatch. Do not force-push, rewrite tags, create a new
release, upload/download release assets, or use release asset `GET`/`HEAD`
requests as part of this launch. The existing v0.1.0 and v0.1.1 tags/releases
remain immutable.
