#!/usr/bin/env python3
"""Zero-network checks for README/draft links, evidence language, and plot freshness."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "README.md",
    ROOT / "drafts" / "README.md",
    ROOT / "drafts" / "v0.1.1-launch.md",
    ROOT / "docs" / "launch-saga.md",
    ROOT / "docs" / "transport-flip-postmortem.md",
    ROOT / "docs" / "day7-public-launch.md",
]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_SRC_RE = re.compile(r'''src=["\']([^"\']+)["\']''')


def check_relative_links() -> list[str]:
    errors: list[str] = []
    for doc in DOCS:
        text = doc.read_text(encoding="utf-8")
        targets = LINK_RE.findall(text) + HTML_SRC_RE.findall(text)
        for raw_target in targets:
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            path_text = unquote(target.split("#", 1)[0])
            if path_text and not (doc.parent / path_text).resolve().exists():
                errors.append(f"{doc.relative_to(ROOT)}: missing link or asset target {target}")
    return errors


def check_claim_contract() -> list[str]:
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    draft = (ROOT / "drafts" / "v0.1.1-launch.md").read_text(encoding="utf-8")
    saga = (ROOT / "docs" / "launch-saga.md").read_text(encoding="utf-8")
    postmortem = (ROOT / "docs" / "transport-flip-postmortem.md").read_text(encoding="utf-8")
    runbook = (ROOT / "docs" / "day7-public-launch.md").read_text(encoding="utf-8")
    required_readme = [
        "All 199 rows reached terminal accounting",
        "not an official leaderboard result",
        "185/199 (92.96%)",
        "5,403.36 provider-authoritative mean across 198 measured rows; one row is not imputed",
        "4.26164968987583 percentage points",
        "**+4.3 points**",
        "highest bare-RLM number shown in this non-exhaustive ladder",
        "64.38%",
        "71.75%",
        "81.36%",
        "52,428,800",
        "65,536",
        "not a token or cost-savings claim",
        "docs/token-context-crossover.svg",
        "curl -fsSL https://raw.githubusercontent.com/kubet/azdaja/main/site/install | sh",
        "cargo install --git https://github.com/kubet/azdaja.git --tag v0.1.2 --locked",
        "A passing `doctor` proves only",
        "**-1.24% fewer wasted actions (1.24% more)**",
        "bench/results/arc3-ember-five-public-v9-result.json",
        "bench/results/arc3-scorecard-interrogation-public-v1.json",
        "not absolute arm scores",
        "revisited-state/repeated-control split",
        "memory-efficiency hypothesis remains open",
        "both baseline and Ember scored 0.0 shadow RHAE",
        "took 35 actions",
        "emitted 36 journal records",
        "terminated at `ACTION_BUDGET`",
        "full five-game rerun remains on hold",
        "bench/results/arc3-vc33-smoke-v2-public.json",
    ]
    required_draft = [
        "NONPUBLISHED DRAFT",
        "This draft makes no adoption claim",
        "not currently an anonymous install path",
        "Darwin-arm64",
        "Linux-x86_64",
        "provider-free",
        "52,428,800",
        "61.452662890467536%",
        "not a leaderboard result",
        "No cost or token",
    ]
    readme_lines = len(readme.splitlines())
    if not 100 <= readme_lines <= 155:
        errors.append(f"README.md: expected 100-155 lines, found {readme_lines}")
    stale_readme = [
        "## First-use feedback",
        "### Derived RULER",
        "### Derived LongBench",
        "### Derived OOLONG",
        "release candidate",
        "GitHub Actions push run",
        "prepublication plan",
        "The repository is private",
        "authenticated owner",
        "ssh://git@",
        "Do not publish or claim anonymous reachability",
    ]
    for needle in stale_readme:
        if needle in readme:
            errors.append(f"README.md: stale or nonpublic claim remains: {needle}")
    for needle in required_readme:
        if needle not in readme:
            errors.append(f"README.md: missing required evidence or install phrase: {needle}")
    for needle in required_draft:
        if needle not in draft:
            errors.append(f"drafts/v0.1.1-launch.md: missing required boundary phrase: {needle}")

    required_saga = [
        "**+4.3 percentage points**",
        "not proof of a global best-published result",
        "5,403.36 mean total root tokens",
        "Codex at 71.75",
        "same harness, same model, ± Azdaja: -1.24% fewer wasted actions (1.24% more)",
        "same Claude Sonnet lane through the direct Claude CLI",
        "obsolete bridge/helper was bypassed",
        "All five paired deltas are 0.0",
        "| ls20 | 0.0 | 92 | 103 |",
        "| ft09 | 0.0 | 186 | 208 |",
        "| vc33 | 0.0 | 0 | 0 |",
        "| ar25 | 0.0 | 137 | 110 |",
        "| wa30 | 0.0 | 231 | 233 |",
        "`-1.238390092879257%` fewer wasted actions",
        "revisited-state/repeated-control split was not retained",
        "only the predefined unchanged-official-feedback aggregate is evidenced",
        "all ten closed scorecard detail requests returned HTTP 404",
        "zero-level play and equal nonzero arm results cannot be distinguished",
        "memory-efficiency hypothesis remains open",
        "total actions and degeneracy remain unresolved",
        "arc3-scorecard-interrogation-public-v1.json",
        "post-launch v0.2 roadmap material only",
    ]
    required_postmortem = [
        "pre-inference setup failure, non-diagnostic for discoverability or selection—not genuine disuse",
        "successful provider turns were **0**",
        "agent-class calls were **0**",
        "0.00 vs 0.00",
        "no live root turn was reached",
        "v0.2 roadmap",
        "does **not** authorize an extra",
    ]
    required_runbook = [
        "private staging only",
        "transport-flip-postmortem.md",
        "gpt-rah199-mortality-v3-terminal-public.json",
        "arc3-ember-five-public-v9-result.json",
        "arc3-scorecard-interrogation-public-v1.json",
        "public flip, anonymous saga verification, then the queued RAH author email",
        "The owner resolved the missing-canonical-repository question",
        "public runbook intentionally omits local staging locations and recipient addresses",
        "Do not open a PR",
        "release asset `GET`/`HEAD`",
    ]
    for name, text, required in (
        ("docs/launch-saga.md", saga, required_saga),
        ("docs/transport-flip-postmortem.md", postmortem, required_postmortem),
        ("docs/day7-public-launch.md", runbook, required_runbook),
    ):
        flat_text = " ".join(text.split())
        for phrase in required:
            if phrase not in flat_text:
                errors.append(f"{name}: missing second-act boundary phrase: {phrase}")

    if saga.count("68.64164968987583%") != 1:
        errors.append("docs/launch-saga.md: expected exact launch percentage once")
    if "best published bare-configuration RLM" in readme or "best published bare-configuration RLM" in saga:
        errors.append("launch docs: unsupported absolute best-published claim")

    marker = "ENDGAME-FIXED199-SUBSTITUTION-POINT"
    if marker in readme:
        errors.append(f"README.md: frozen launch still contains {marker}")
    expected_result_rows = [
        "| RAH-protocol Oolong, fixed 199 rows | **68.64%** |",
        "| Execution / valid predictions | 185/199 (92.96%) |",
        "| Mean root tokens per item | ~5.4K |",
        "| Captured root-prompt source-span leaks in the scripted 50 MiB gate | 0 |",
    ]
    for row_start in expected_result_rows:
        if readme.count(row_start) != 1:
            errors.append(f"README.md: expected one current result row beginning {row_start}")
    unsupported_readme_claims = [
        "Cheapest configuration in its table",
        "convergence is the claim",
        "~90%",
        "global best",
        "all runs, all time",
        "O(1) root",
        "cost of asking does not grow",
        "Model-agnostic, proven",
    ]
    for claim in unsupported_readme_claims:
        if claim.casefold() in readme.casefold():
            errors.append(f"README.md: unsupported owner-draft claim remains: {claim}")
    install_section = readme.split("## Install", 1)[1].split("## Use", 1)[0]
    if install_section.count("```bash") != 3:
        errors.append("README.md: Install section must contain exactly three bash blocks")
    if "v0.1.1" in install_section:
        errors.append("README.md: Install section still references immutable v0.1.1 assets")

    for doc in DOCS:
        doc_text = doc.read_text(encoding="utf-8")
        name = str(doc.relative_to(ROOT))
        if re.search(r"(?:~|≈)\s*72(?:\.0+)?%?", doc_text):
            errors.append(f"{name}: forbidden approximate-72 result claim")
        for private_prefix in ("/Users/", "/private/tmp/", "C:\\Users\\"):
            if private_prefix in doc_text:
                errors.append(f"{name}: private host path leaked: {private_prefix}")
    return errors



def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def check_launch_receipts() -> list[str]:
    errors: list[str] = []
    release_path = ROOT / "release" / "day7-public-launch.json"
    public_path = ROOT / "bench" / "results" / "gpt-rah199-mortality-v3-terminal-public.json"
    transport_path = ROOT / "bench" / "results" / "endgame-agent-transport-v2-disease10-terminal.json"
    arc_path = ROOT / "bench" / "results" / "arc3-ember-five-public-v9-result.json"
    interrogation_path = ROOT / "bench" / "results" / "arc3-scorecard-interrogation-public-v1.json"
    vc33_smoke_path = ROOT / "bench" / "results" / "arc3-vc33-smoke-v2-public.json"
    postmortem_path = ROOT / "docs" / "transport-flip-postmortem.md"
    saga_path = ROOT / "docs" / "launch-saga.md"
    try:
        release = json.loads(release_path.read_text(encoding="utf-8"))
        public = json.loads(public_path.read_text(encoding="utf-8"))
        transport = json.loads(transport_path.read_text(encoding="utf-8"))
        arc = json.loads(arc_path.read_text(encoding="utf-8"))
        interrogation = json.loads(interrogation_path.read_text(encoding="utf-8"))
        vc33_smoke = json.loads(vc33_smoke_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"launch receipt read failed: {exc}"]

    score = release.get("authorized_launch_score", {})
    public_score = public.get("score", {})
    root_usage = public.get("root_usage", {})
    evidence = release.get("evidence", {})
    if score.get("percent") != 68.64164968987583 or public_score.get("fixed_199_score_percent") != 68.64164968987583:
        errors.append("launch receipts: frozen exact score mismatch")
    if public_score.get("execution_successes") != 185 or public_score.get("retained_failure_zeros") != 14:
        errors.append("sanitized terminal receipt: fixed-199 accounting mismatch")
    if abs(public_score.get("completed_row_mean_percent", 0) * 185 / 199 - 68.64164968987583) > 1e-12:
        errors.append("sanitized terminal receipt: completed-row mean does not decompose")
    if round(68.64164968987583 - 64.38, 1) != 4.3:
        errors.append("launch receipts: rounded class-reference delta changed")

    expected_root = {
        "scheduled_rows": 199,
        "measured_rows": 198,
        "missing_rows": 1,
        "measured_input_tokens": 891498,
        "measured_output_tokens": 178367,
        "measured_total_tokens": 1069865,
        "median_total_tokens_across_measured_rows": 4723,
        "successful_rows": 185,
        "successful_rows_total_tokens": 916133,
    }
    for key, value in expected_root.items():
        if root_usage.get(key) != value:
            errors.append(f"sanitized terminal receipt: root usage {key} changed")
    if root_usage.get("complete_fixed_199_aggregate") is not False or root_usage.get("estimated") is not False:
        errors.append("sanitized terminal receipt: missing-root boundary changed")
    if abs(root_usage.get("mean_total_tokens_across_measured_rows", 0) - 1069865 / 198) > 1e-12:
        errors.append("sanitized terminal receipt: measured root-token mean mismatch")
    if abs(root_usage.get("mean_total_tokens_across_successful_rows", 0) - 916133 / 185) > 1e-12:
        errors.append("sanitized terminal receipt: successful-row root-token mean mismatch")

    execution = transport.get("execution", {})
    transport_score = transport.get("score", {})
    if transport.get("terminal_status") != "FAIL" or execution.get("successful_provider_turns") != 0:
        errors.append("transport receipt: terminal pre-inference failure boundary changed")
    for key, value in (("agent_class_calls", 0), ("control_failures", 10), ("treatment_failures", 10), ("terminal_rows", 20)):
        if execution.get(key) != value:
            errors.append(f"transport receipt: {key} changed")
    if transport_score.get("control_official_points") != 0.0 or transport_score.get("treatment_official_points") != 0.0 or transport_score.get("delta_points") != 0.0:
        errors.append("transport receipt: fail-closed +0.00 accounting changed")
    if transport.get("forced_live_proof", {}).get("passed") is not False:
        errors.append("transport receipt: forced live proof boundary changed")

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
    expected_arc_sha256 = "f6a518df0183f9d4791e99f58bdc0e91c198056ffa67b9013b8f97ff8fc27c21"
    if arc != expected_arc:
        errors.append("ARC receipt: exact public-safe schema or values changed")
    if _sha256(arc_path) != expected_arc_sha256:
        errors.append("ARC receipt: canonical v9 byte hash changed")
    else:
        baseline_wasted = sum(game["baseline_wasted_actions"] for game in arc["games"])
        ember_wasted = sum(game["ember_wasted_actions"] for game in arc["games"])
        if baseline_wasted != 646 or ember_wasted != 654:
            errors.append("ARC receipt: wasted-action totals changed")
        fewer_percent = (baseline_wasted - ember_wasted) / baseline_wasted * 100
        if abs(fewer_percent - (-1.238390092879257)) > 1e-15:
            errors.append("ARC receipt: wasted-action percentage changed")
        if any(game["ember_minus_baseline_rhae_delta"] != 0.0 for game in arc["games"]):
            errors.append("ARC receipt: paired RHAE delta changed")

    expected_interrogation = {
        "schema_version": 1,
        "record_type": "arc3_closed_scorecard_interrogation_sanitized_receipt",
        "scope": {
            "arms": ["baseline", "ember"],
            "closed_scorecards_queried": 10,
            "game_pairs": 5,
            "credential_continuity": "one unchanged owner credential",
            "new_experiment": False,
            "game_requests_performed": False,
            "provider_requests_performed": False,
        },
        "official_scorecard_retrieval": {
            "pinned_contract": "open or closed scorecard retrieval",
            "observed_http_status": 404,
            "observed_count": 10,
            "absolute_arm_rhae_recovered": False,
            "levels_completed_recovered": False,
            "total_actions_recovered": False,
        },
        "html_results_route": {
            "observation": "redirected to the generic ARC-AGI-3 page",
            "scorecard_detail_recovered": False,
        },
        "retention_boundary": {
            "driver_retained_close_responses": False,
            "public_v9_receipt_retains_paired_deltas": True,
            "public_v9_receipt_retains_aggregate_wasted_actions": True,
            "zero_level_vs_equal_nonzero_distinguishable": False,
            "memory_efficiency_hypothesis_status": "open",
        },
        "vc33": {
            "scorecard_lifecycles_created_reset_closed": 2,
            "lifecycle_source": "retained stdout metadata",
            "total_actions_established": False,
            "levels_completed_established": False,
            "degeneracy_status": "unresolved",
            "zero_wasted_actions_implies_zero_total_actions": False,
        },
        "redaction": {
            "scorecard_identifiers_included": False,
            "credentials_included": False,
            "host_paths_included": False,
            "raw_logs_included": False,
        },
    }
    if interrogation != expected_interrogation:
        errors.append("ARC interrogation receipt: exact sanitized schema or findings changed")
    if _sha256(interrogation_path) != "17de6893eee9cafafdd164965a91fe08b72aecc69d1f2e41044c0b7d4cbc210c":
        errors.append("ARC interrogation receipt: canonical byte hash changed")

    expected_vc33_smoke = {'schema_version': 1,
 'package': {'commit': '1d500edd8eaf651364cfdd8e29638ee540db6062',
             'manifest_sha256': 'ef56236950ba4e44f901dff79342145f944c79bb3c7236d64da06f6265e86ab1'},
 'game': 'vc33',
 'arms': {'baseline': {'shadow_rhae': 0.0,
                       'levels_completed': 0,
                       'total_actions': 35,
                       'per_level_action_counts': [35, 0, 0, 0, 0, 0, 0],
                       'wasted_actions': {'official_feedback_wasted_actions': 0,
                                          'revisited_states': 0,
                                          'repeated_known_controls': 0},
                       'termination': 'ACTION_BUDGET',
                       'journal': {'record_count': 36,
                                   'sha256': '18ddb74e409521a6666845ceab6283d8f227b5571c292d1a4d005828c0718e28'},
                       'terminal_receipt_sha256': '4ff55203bdbc6d61874a817b9059df850fe64e82f17b684b43d899d2ad11cac2'},
          'ember': {'shadow_rhae': 0.0,
                    'levels_completed': 0,
                    'total_actions': 35,
                    'per_level_action_counts': [35, 0, 0, 0, 0, 0, 0],
                    'wasted_actions': {'official_feedback_wasted_actions': 0,
                                       'revisited_states': 0,
                                       'repeated_known_controls': 0},
                    'termination': 'ACTION_BUDGET',
                    'journal': {'record_count': 36,
                                'sha256': '28ab0ade89e4d5d0996733b7d6fb26ee727e754fb6eac77315874da1f46eb55f'},
                    'terminal_receipt_sha256': 'bbc17cb9af387defc9ad3338353a44259ed63fba558c57e7cf6549bc88361a35'}},
 'paired': {'ember_minus_baseline_shadow_rhae_delta': 0.0,
            'receipt_sha256': 'a2f732483d707df9ce0de871243efef5e4e491fd7d34140e3af05765b51daed6'},
 'full_five_game_rerun': {'status': 'HOLD',
                          'release_condition': 'post-public flip and explicit owner authorization'}}
    if vc33_smoke != expected_vc33_smoke:
        errors.append("ARC-v2 vc33 smoke receipt: exact sanitized schema or values changed")
    if _sha256(vc33_smoke_path) != "002deda1f7d6740b0aeffc277ea9f7bab87939960fd6644b6852f6e747f97551":
        errors.append("ARC-v2 vc33 smoke receipt: canonical byte hash changed")

    expected_second_act_arc = {
        "absolute_arm_rhae_retained": False,
        "all_paired_rhae_deltas": 0.0,
        "arms": ["baseline", "ember"],
        "games": 5,
        "identity": "Ember",
        "method": {
            "fresh_sessions": True,
            "helper_anomaly_observed": False,
            "model_lane": "Claude Sonnet",
            "obsolete_bridge_helper_bypassed": True,
            "transport": "direct Claude CLI",
        },
        "result_framing": "same harness, same model, ± Azdaja: -1.24% fewer wasted actions (1.24% more)",
        "revisited_state_repeated_control_split_retained": False,
        "wasted_actions": {
            "baseline": 646,
            "ember": 654,
            "baseline_minus_ember_percent_of_baseline": -1.238390092879257,
        },
        "levels_completed_retained": False,
        "total_actions_retained": False,
        "scorecard_interrogation": {
            "absolute_arm_rhae_recovered": False,
            "closed_scorecards_queried": 10,
            "game_or_provider_requests_performed": False,
            "html_result": "redirected_to_generic_arc_agi_3_page",
            "observed_http_status": 404,
            "pinned_contract": "open_or_closed_scorecard_retrieval",
        },
        "paired_null_interpretation": "zero_level_vs_equal_nonzero_not_distinguishable",
        "memory_efficiency_hypothesis": "open",
        "vc33": {
            "scorecard_lifecycles_created_reset_closed": 2,
            "total_actions_established": False,
            "levels_completed_established": False,
            "degeneracy": "unresolved",
        },
    }

    if release.get("second_act", {}).get("arc") != expected_second_act_arc:
        errors.append("day7 receipt: ARC method or evidence boundary changed")

    expected_hashes = {
        "sanitized_terminal_receipt_sha256": _sha256(public_path),
        "transport_terminal_receipt_sha256": _sha256(transport_path),
        "transport_postmortem_sha256": _sha256(postmortem_path),
        "arc_terminal_receipt_sha256": _sha256(arc_path),
        "arc_interrogation_receipt_sha256": _sha256(interrogation_path),
    }
    for key, value in expected_hashes.items():
        if evidence.get(key) != value:
            errors.append(f"day7 receipt: stale {key}")
    if evidence.get("arc_terminal_receipt_path") != "bench/results/arc3-ember-five-public-v9-result.json":
        errors.append("day7 receipt: stale ARC public receipt path")
    if evidence.get("arc_interrogation_receipt_path") != "bench/results/arc3-scorecard-interrogation-public-v1.json":
        errors.append("day7 receipt: stale ARC interrogation receipt path")
    if score.get("terminal_receipt_path") is not None or score.get("terminal_receipt_retained_private") is not True:
        errors.append("day7 receipt: missing private-terminal path boundary")
    if score.get("terminal_receipt_sha256") != "27bbb4da02bf75ff5c3c6b73697bf8518e33566a55f3b9fc8d7012ee5b648e74":
        errors.append("day7 receipt: retained private terminal identity changed")
    saga = release.get("saga", {})
    if saga.get("sha256") != _sha256(saga_path) or saga.get("git_blob") != _git_blob(saga_path):
        errors.append("day7 receipt: stale launch saga identity")
    if saga.get("authorized_score_occurrences") != 1 or release.get("release_asset_requests_performed") is not False:
        errors.append("day7 receipt: publication or score-occurrence boundary changed")

    for path in (
        release_path,
        public_path,
        transport_path,
        arc_path,
        interrogation_path,
        vc33_smoke_path,
        postmortem_path,
    ):
        text = path.read_text(encoding="utf-8")
        for private_prefix in ("/Users/", "/private/tmp/", "C:\\Users\\"):
            if private_prefix in text:
                errors.append(f"{path.relative_to(ROOT)}: private host path leaked: {private_prefix}")
    return errors

def main() -> int:
    errors = check_relative_links() + check_claim_contract() + check_launch_receipts()
    plot_check = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "render_token_crossover.py"), "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if plot_check.returncode:
        errors.append(plot_check.stdout.strip())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    readme_lines = len((ROOT / "README.md").read_text(encoding="utf-8").splitlines())
    print(f"ok: README.md is concise at {readme_lines} lines; {len(DOCS)} Markdown files have valid local links and evidence boundaries")
    print(plot_check.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
