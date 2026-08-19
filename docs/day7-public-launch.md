# Day-7 public launch runbook

Status: **private staging only**. Do not run the launch block before
`2026-08-26T00:20:29.359377+00:00`. Preparing, reviewing, and pushing the
private assembly branch is allowed before then; changing repository visibility
or publishing the saga is not.

This branch owns the reviewed public-flip runbook, sanitized receipts, launch
saga, ARC results presentation, transport post-mortem, and final README evidence
pass. It does not own a visibility change, publication, benchmark run, ARC run,
or provider call.

After the private merge, the mechanical public order is: **public flip, anonymous
saga verification, then the queued RAH author email**. The email follows the
flip and verified saga; it is not sent during staging and does not depend on an
invented canonical repository.

## Bound launch statement

The staged saga contains this authorized result exactly once:

> **Launch result:** **68.64164968987583%** on a fixed 199-row, validation-derived RAH slice, with 185 execution successes (valid predictions) and 14 retained failures counted as zero.

Both preregistered levers are terminal FAIL. Neither authorized a successor
fixed-199 run, so this is the permanent launch result. The score block is frozen;
no substitution, rerun, resume, or rescore is authorized.

## Bound paired ARC statement

The five-game result is terminal and public-safe:

> same harness, same model, ± Azdaja: -1.24% fewer wasted actions (1.24% more)

All five Ember-minus-baseline paired RHAE deltas are 0.0. Baseline/Ember wasted
actions are ls20 92/103, ft09 186/208, vc33 0/0, ar25 137/110, and wa30
231/233, totaling 646/654. Both arms used fresh sessions on the same Claude
Sonnet lane via the direct Claude CLI. The obsolete bridge/helper was bypassed,
so no helper anomaly was observed. Version 9 retained neither arm's absolute
RHAE nor the revisited-state/repeated-control split; only paired deltas and the
predefined unchanged-official-feedback aggregate are evidenced.

The owner-directed retrieval-only interrogation made no new game or provider
request. All ten closed scorecard detail requests returned HTTP 404 despite the
pinned open-or-closed retrieval contract, and the HTML result exposed no detail.
With close responses discarded, absolute per-arm RHAE, levels completed, and
total actions are unrecoverable. Zero-level and equal nonzero arm results cannot
be distinguished, so the memory-efficiency hypothesis remains open. The vc33
stdout proves two create/reset/close lifecycles, not zero actions or levels;
degeneracy is unresolved.

## Pre-Day-7 private assembly

The initial documentation-only README input was source commit
`0ed643e31a93cc060cf7a4917108224f13553ee5`; it changed only `README.md` and
`tools/check_docs.py` and is already in this assembly's ancestry. The reviewed
second-act pass now lives on this assembly branch; do not replay the source
commit over it or merge the README branch's benchmark ancestry. To validate and
push the private assembly, use:

```bash
set -euo pipefail
REPO=kubet/azdaja
ASSEMBLY=launch/day7-public-assembly
README_COMMIT=0ed643e31a93cc060cf7a4917108224f13553ee5

git fetch origin --prune --tags
git switch "$ASSEMBLY"
git show --stat --oneline "$README_COMMIT"
# Ancestry check only: never replay README_COMMIT over this reviewed final pass.
git merge-base --is-ancestor "$README_COMMIT" HEAD
python3 tools/check_docs.py
git diff --check
test -z "$(git status --porcelain --untracked-files=no)"
git push --set-upstream origin "$ASSEMBLY"
test "$(gh repo view "$REPO" --json visibility --jq .visibility)" = PRIVATE
```

The README launch freeze is complete: the substitution marker and provisional
sentence are absent, and the checker binds the permanent score arithmetic. The
Day-7 block below refuses to publish either stale phrase.

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
EXPECTED_ARC_LINE='> same harness, same model, ± Azdaja: -1.24% fewer wasted actions (1.24% more)'

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
test -f docs/transport-flip-postmortem.md
test -f bench/results/gpt-rah199-mortality-v3-terminal-public.json
test -f bench/results/endgame-agent-transport-v2-disease10-terminal.json
test -f bench/results/arc3-ember-five-public-v9-result.json
test -f bench/results/arc3-scorecard-interrogation-public-v1.json
test "$(grep -Fxc "$EXPECTED_LINE" docs/launch-saga.md)" -eq 1
test "$(grep -Fxc "$EXPECTED_ARC_LINE" docs/launch-saga.md)" -eq 1
test "$(grep -Fc "$EXPECTED_SCORE" docs/launch-saga.md)" -eq 1
! grep -Fq 'SCORE_SUBSTITUTION_POINT' docs/launch-saga.md
! grep -Fq 'ENDGAME-FIXED199-SUBSTITUTION-POINT' README.md
! grep -Fq 'provisional only because' README.md
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

receipt = json.loads(Path("release/day7-public-launch.json").read_text())
score = receipt["authorized_launch_score"]
assert receipt["hard_public_launch_not_before"] == "2026-08-26T00:20:29.359377+00:00"
assert score["percent"] == 68.64164968987583
assert score["fixed_denominator"] == 199
assert score["execution_successes"] == 185
assert score["retained_failure_zeros"] == 14
assert score["status"] == "permanent_final_no_successor_authorized"
assert receipt["release_asset_requests_performed"] is False

public_path = Path("bench/results/gpt-rah199-mortality-v3-terminal-public.json")
public = json.loads(public_path.read_text())
assert public["score"]["fixed_199_score_percent"] == score["percent"]
assert public["score"]["execution_successes"] == score["execution_successes"]
assert public["root_usage"]["measured_rows"] == 198
assert public["root_usage"]["missing_rows"] == 1
assert public["root_usage"]["measured_total_tokens"] == 1069865
assert public["root_usage"]["complete_fixed_199_aggregate"] is False
assert receipt["evidence"]["sanitized_terminal_receipt_sha256"] == hashlib.sha256(public_path.read_bytes()).hexdigest()

transport_path = Path("bench/results/endgame-agent-transport-v2-disease10-terminal.json")
transport = json.loads(transport_path.read_text())
assert transport["terminal_status"] == "FAIL"
assert transport["execution"]["successful_provider_turns"] == 0
assert transport["execution"]["agent_class_calls"] == 0
assert transport["execution"]["control_failures"] == 10
assert transport["execution"]["treatment_failures"] == 10
assert receipt["evidence"]["transport_terminal_receipt_sha256"] == hashlib.sha256(transport_path.read_bytes()).hexdigest()

arc_path = Path("bench/results/arc3-ember-five-public-v9-result.json")
arc = json.loads(arc_path.read_text())
expected_arc = {
    "arms": ["baseline", "ember"],
    "games": [
        {"baseline_wasted_actions": 92, "ember_minus_baseline_rhae_delta": 0.0, "ember_wasted_actions": 103, "game_id": "ls20"},
        {"baseline_wasted_actions": 186, "ember_minus_baseline_rhae_delta": 0.0, "ember_wasted_actions": 208, "game_id": "ft09"},
        {"baseline_wasted_actions": 0, "ember_minus_baseline_rhae_delta": 0.0, "ember_wasted_actions": 0, "game_id": "vc33"},
        {"baseline_wasted_actions": 137, "ember_minus_baseline_rhae_delta": 0.0, "ember_wasted_actions": 110, "game_id": "ar25"},
        {"baseline_wasted_actions": 231, "ember_minus_baseline_rhae_delta": 0.0, "ember_wasted_actions": 233, "game_id": "wa30"},
    ],
    "identity": "Ember",
}
assert arc == expected_arc
assert hashlib.sha256(arc_path.read_bytes()).hexdigest() == "f6a518df0183f9d4791e99f58bdc0e91c198056ffa67b9013b8f97ff8fc27c21"
assert sum(game["baseline_wasted_actions"] for game in arc["games"]) == 646
assert sum(game["ember_wasted_actions"] for game in arc["games"]) == 654
assert all(game["ember_minus_baseline_rhae_delta"] == 0.0 for game in arc["games"])
assert receipt["evidence"]["arc_terminal_receipt_path"] == str(arc_path)
assert receipt["evidence"]["arc_terminal_receipt_sha256"] == hashlib.sha256(arc_path.read_bytes()).hexdigest()

interrogation_path = Path("bench/results/arc3-scorecard-interrogation-public-v1.json")
interrogation = json.loads(interrogation_path.read_text())
assert hashlib.sha256(interrogation_path.read_bytes()).hexdigest() == "17de6893eee9cafafdd164965a91fe08b72aecc69d1f2e41044c0b7d4cbc210c"
assert interrogation["scope"]["closed_scorecards_queried"] == 10
assert interrogation["scope"]["new_experiment"] is False
assert interrogation["scope"]["game_requests_performed"] is False
assert interrogation["scope"]["provider_requests_performed"] is False
assert interrogation["official_scorecard_retrieval"]["observed_http_status"] == 404
assert interrogation["official_scorecard_retrieval"]["observed_count"] == 10
assert interrogation["retention_boundary"]["zero_level_vs_equal_nonzero_distinguishable"] is False
assert interrogation["retention_boundary"]["memory_efficiency_hypothesis_status"] == "open"
assert interrogation["vc33"]["scorecard_lifecycles_created_reset_closed"] == 2
assert interrogation["vc33"]["total_actions_established"] is False
assert interrogation["vc33"]["degeneracy_status"] == "unresolved"
assert receipt["evidence"]["arc_interrogation_receipt_path"] == str(interrogation_path)
assert receipt["evidence"]["arc_interrogation_receipt_sha256"] == hashlib.sha256(interrogation_path.read_bytes()).hexdigest()

private_prefixes = ("/" + "private/tmp/", "/" + "Users/")
for path in (public_path, transport_path, arc_path, interrogation_path, Path("docs/transport-flip-postmortem.md")):
    text = path.read_text()
    assert not any(prefix in text for prefix in private_prefixes)
PY

python3 tools/check_docs.py
git diff --check
cargo test --all --locked -- --test-threads=1
cargo clippy --all-targets --all-features -- -D warnings
test -z "$(git status --porcelain)"

# Prestage the assembly on main while still private; the saga becomes public only at the flip.
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

# Public step 1: mandatory visibility flip. Never run this command before DEADLINE.
gh repo edit kubet/azdaja --visibility public --accept-visibility-change-consequences

# Public step 2: ship the saga by authenticated and anonymous verification; source only, no release assets.
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
test "$(grep -Fxc "$EXPECTED_ARC_LINE" docs/launch-saga.md)" -eq 1
test "$(git rev-parse HEAD)" = "$MAIN_HEAD"
```

## RAH author email — mechanical third step

The owner resolved the missing-canonical-repository question by converting the
prepared PR into a short author email. Send it only after both the public flip
and anonymous saga verification above succeed. The owner-only staging package
contains the queued message, its exact Day-7 Mail command, and a syntax-tested
send script; this public runbook intentionally omits local staging locations and
recipient addresses.

Before invoking that private command, verify that its two recipients still
match the paper-published addresses, its public README/receipt/saga links resolve,
and it has no Cc or Bcc. The script refuses pre-deadline execution and requires an
explicit send confirmation. Do not open a PR and do not send the email during
pre-Day-7 staging.

Stop immediately on any launch mismatch. Do not force-push, rewrite tags,
create a new release, upload/download release assets, or use release asset `GET`/`HEAD`
requests as part of this launch. The existing v0.1.0 and v0.1.1 tags/releases
remain immutable.
