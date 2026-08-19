#!/usr/bin/env python3
"""Fail-closed ARC-AGI-3 paired drivers and ARC-v2 local custody.

Historical ``dry-run`` uses only in-process stubs. ``live`` fails closed unless
its frozen manifest and separate owner-only authorization match exactly. The
ARC-v2 schema permits only one vc33 baseline-then-ember pair.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

LEGACY_ARMS = ("jcode-native", "jcode-azdaja")
PRIVATE_ARMS = ("baseline", "ember")
ACTIONS = frozenset({"RESET", *(f"ACTION{i}" for i in range(1, 8))})
SAFE_ID = re.compile(r"[a-z0-9][a-z0-9-]{1,31}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
GIT_COMMIT = re.compile(r"[0-9a-f]{40}\Z")
HISTORY_MODE = 0o600
DIRECTORY_MODE = 0o700
DRY_GAME = "ls20"
ARC_V2_SCHEMA = 10
ARC_V2_GAME = "vc33"
ARC_V2_ARMS = ("baseline", "ember")
ARC_V2_GENESIS_HASH = "0" * 64
DIRECT_CLAUDE_SCHEMAS = frozenset({4, 5, 6, 7, 8, 9, ARC_V2_SCHEMA})
DIRECT_CLAUDE_FAILURES = frozenset({
    "auth", "invalid_model", "cli_usage", "sandbox_permission",
    "rate_limit", "network", "other",
})
DIRECT_CLAUDE_FAILURE = re.compile(
    r"direct_claude_failure=(auth|invalid_model|cli_usage|sandbox_permission|rate_limit|network|other)"
)


class GateError(RuntimeError):
    """A deterministic preflight/runtime gate failed."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def direct_claude_failure_category(value: str | bytes) -> str:
    text = value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value
    matches = DIRECT_CLAUDE_FAILURE.findall(text)
    if len(matches) == 1 and matches[0] in DIRECT_CLAUDE_FAILURES:
        return matches[0]
    return "other"


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read JSON object {path.name}: {type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise GateError(f"{path.name} is not a JSON object")
    return value


def manifest_arms(manifest: dict[str, Any]) -> tuple[str, str]:
    return PRIVATE_ARMS if manifest.get("schema_version") in {3, 4, 5, 6, 7, 8, 9, ARC_V2_SCHEMA} else LEGACY_ARMS


def treatment_arm(manifest: dict[str, Any]) -> str:
    return manifest_arms(manifest)[1]




def verify_arc_v2_manifest(manifest: dict[str, Any]) -> None:
    """Verify the owner-authorized, exactly-one-pair ARC-v2 custody scope."""
    required_top_level = {
        "action_budget_semantics", "authorization_contract", "common_live_model_config",
        "custody_contract", "execution_freshness", "experiment_id", "games",
        "hold_gate", "launch_gate", "owner_only_evidence", "schema_version",
        "scope", "status", "suite", "treatment_only",
    }
    if set(manifest) != required_top_level:
        raise GateError("ARC-v2 manifest top-level shape drift")
    if manifest.get("schema_version") != ARC_V2_SCHEMA:
        raise GateError("ARC-v2 schema drift")
    if manifest.get("experiment_id") != "ARC-V2-VC33-PAIRED-LOCAL-CUSTODY-V1":
        raise GateError("ARC-v2 experiment identity drift")
    if manifest.get("status") != "FROZEN_AUTHORIZED_FOR_EXACTLY_ONE_LOCAL_CUSTODY_PAIR":
        raise GateError("ARC-v2 status drift")

    scope = manifest.get("scope")
    if scope != {
        "game_count": 1,
        "game_id": ARC_V2_GAME,
        "pair_count": 1,
        "pair_order": list(ARC_V2_ARMS),
        "selection_reason": "prior 0/0 aggregate was degenerate and unresolved; vc33 has the smallest first-level cap",
    }:
        raise GateError("ARC-v2 must freeze exactly one vc33 baseline-then-ember pair")
    suite = manifest.get("suite")
    if suite != {
        "fresh_game_instance_per_arm": True,
        "fresh_identity_per_arm": True,
        "game_order": [ARC_V2_GAME],
        "name": "ARC-V2-LOCAL-CUSTODY-SMOKE",
        "pair_order": list(ARC_V2_ARMS),
        "pairs": 1,
        "reuse_prior_game_or_session": False,
        "seed": 0,
    }:
        raise GateError("ARC-v2 suite scope or order drift")

    games = manifest.get("games")
    if not isinstance(games, list) or len(games) != 1 or not isinstance(games[0], dict):
        raise GateError("ARC-v2 manifest must contain exactly one game")
    game = games[0]
    if game.get("game_id") != ARC_V2_GAME or game.get("dry_run_stub") is not False:
        raise GateError("ARC-v2 permits only live vc33")
    baselines = game.get("human_level_baseline_actions")
    if baselines != [7, 18, 44, 61, 131, 34, 152]:
        raise GateError("ARC-v2 vc33 human baseline drift")
    caps = [5 * item for item in baselines]
    if (
        game.get("action_cap_multiplier") != 5
        or game.get("level_action_caps") != caps
        or game.get("max_actions") != sum(caps)
        or game.get("official_human_actions_total") != sum(baselines)
    ):
        raise GateError("ARC-v2 vc33 action budget drift")

    common = manifest.get("common_live_model_config")
    if not isinstance(common, dict):
        raise GateError("ARC-v2 common model config is missing")
    exact_common = {
        "provider": "claude-code",
        "model": "sonnet",
        "claude_version": "2.1.234",
        "invocation": "direct-cli-fresh-process-v7",
        "reasoning_effort": "low",
        "strict_empty_mcp_config": {"mcpServers": {}},
        "telemetry": False,
        "temperature": None,
    }
    if any(common.get(key) != value for key, value in exact_common.items()):
        raise GateError("ARC-v2 direct Claude Sonnet lane drift")
    for key in (
        "fresh_process_per_action", "no_project_discovery", "no_session_persistence",
        "no_tools", "print_mode", "safe_mode", "same_direct_lane_for_both_arms",
    ):
        if common.get(key) is not True:
            raise GateError(f"ARC-v2 Claude isolation drift: {key}")
    for key in ("claude_binary_sha256", "lane_wrapper_sha256", "driver_sha256"):
        if not isinstance(common.get(key), str) or not SHA256.fullmatch(common[key]):
            raise GateError(f"invalid ARC-v2 digest: {key}")
    if common["lane_wrapper_sha256"] != sha256_bytes(Path(__file__).with_name("claude_lane.py").read_bytes()):
        raise GateError("ARC-v2 direct Claude wrapper digest mismatch")
    if common["driver_sha256"] != sha256_bytes(Path(__file__).read_bytes()):
        raise GateError("ARC-v2 driver digest mismatch")

    treatment = manifest.get("treatment_only")
    if not isinstance(treatment, dict):
        raise GateError("ARC-v2 treatment config is missing")
    hashes = treatment.get("binary_sha256_by_platform")
    components = treatment.get("source_bundle_components_sha256")
    if not isinstance(hashes, dict) or set(hashes) != {"darwin-arm64"}:
        raise GateError("ARC-v2 Ember platform identity drift")
    if any(not isinstance(value, str) or not SHA256.fullmatch(value) for value in hashes.values()):
        raise GateError("ARC-v2 Ember binary digest is invalid")
    if not isinstance(components, dict) or set(components) != {"SKILL.md", "config.toml"}:
        raise GateError("ARC-v2 Ember source bundle identity drift")
    if any(not isinstance(value, str) or not SHA256.fullmatch(value) for value in components.values()):
        raise GateError("ARC-v2 Ember source bundle digest is invalid")
    if (
        treatment.get("bundle_version") != "0.1.0"
        or treatment.get("root_model") != "claude-sonnet-5"
        or treatment.get("sub_model") != "claude-sonnet-5"
        or treatment.get("subcall_transport") != "direct-claude-cli-fresh-process-v1"
        or treatment.get("trigger_completed_turns") != 2
        or treatment.get("max_skill_invocations_per_game") != 1
    ):
        raise GateError("ARC-v2 Ember treatment drift")

    freshness = manifest.get("execution_freshness")
    if freshness != {
        "action_journals_must_not_preexist": True,
        "authorization_generation": "arc-v2-local-custody-v1",
        "fresh_process_per_model_call": True,
        "fresh_runtime_per_arm": True,
        "manifest_generation": "arc-v2-local-custody-v1",
        "output_identity": "ARC-V2-VC33-PAIRED-LOCAL-CUSTODY-V1-OUTPUT",
        "output_must_not_preexist": True,
        "paired_receipt_must_not_preexist": True,
        "private_failure_artifact_filename": "arc-v2-vc33-paired-local-custody-v1.direct-claude-failure.private",
        "private_failure_artifact_must_not_preexist": True,
        "reuse_v9_game_session_output_or_runtime": False,
        "terminal_receipts_must_not_preexist": True,
    }:
        raise GateError("ARC-v2 execution freshness drift")

    custody = manifest.get("custody_contract")
    if custody != {
        "action_journal_creation": "O_EXCL mode 0600; canonical JSONL append and fsync for every record",
        "action_journal_hash_chain": "record_sha256=SHA256(canonical JSON of record without record_sha256); previous_record_sha256 links from 64 zeroes",
        "artifact_scope": "owner-only local custody; no public output required",
        "forbidden_journal_content": ["model prompts", "model responses", "OAuth material", "API keys"],
        "platform_scorecard_retrieval": False,
        "receipt_creation": "O_EXCL mode 0600",
    }:
        raise GateError("ARC-v2 local-custody contract drift")

    hold = manifest.get("hold_gate")
    if hold != {
        "full_five_game_rerun": "HOLD",
        "release_condition": "explicit post-public-flip owner authorization",
    }:
        raise GateError("ARC-v2 five-game rerun must remain on HOLD")
    launch = manifest.get("launch_gate")
    if launch != {
        "arc_live_owner_authorized": True,
        "arc_v2_exactly_one_pair_owner_authorized": True,
        "full_five_game_rerun_authorized": False,
        "separate_arc_claude_lane_owner_authorized": True,
        "track1_fixed_199_terminal_completed": True,
        "track1_fixed_denominator": 199,
    }:
        raise GateError("ARC-v2 launch gate drift")
    evidence = manifest.get("owner_only_evidence")
    if evidence != {
        "direct_claude_wrapper_helper_bypass_retained": True,
        "prior_vc33_aggregate": "0/0_DEGENERATE_UNRESOLVED",
        "source_commit": "3399cf700db21b48dbbc532372b6541b31cd62ad",
        "zero_live_calls_during_patch_preparation": True,
    }:
        raise GateError("ARC-v2 owner evidence drift")

    expected_authorization_fields = [
        "action_journal_paths", "arc_live_owner_authorized",
        "arc_v2_exactly_one_pair_owner_authorized", "direct_claude_failure_artifact_path",
        "experiment_id", "full_five_game_rerun_authorized", "manifest_sha256",
        "output_identity", "output_path", "pair_count", "pair_order",
        "paired_receipt_path", "selected_game_id",
        "separate_arc_claude_lane_owner_authorized", "terminal_receipt_paths",
        "track1_fixed_199_terminal_completed", "track1_fixed_denominator",
    ]
    authorization = manifest.get("authorization_contract")
    if authorization != {
        "all_artifact_paths_absolute_fresh_and_owner_only": True,
        "required_fields": expected_authorization_fields,
    }:
        raise GateError("ARC-v2 authorization contract drift")


def verify_manifest(path: Path) -> tuple[dict[str, Any], str]:
    data = path.read_bytes()
    digest = sha256_bytes(data)
    sidecar = path.with_suffix(".sha256")
    fields = sidecar.read_text(encoding="ascii").strip().split()
    if len(fields) != 2 or fields[0] != digest or fields[1] != path.name:
        raise GateError("manifest sidecar mismatch")
    manifest = read_json_object(path)
    schema_version = manifest.get("schema_version")
    if schema_version == ARC_V2_SCHEMA:
        verify_arc_v2_manifest(manifest)
        return manifest, digest
    if schema_version not in {1, 2, 3, 4, 5, 6, 7, 8, 9}:
        raise GateError("unsupported manifest schema")
    suite = manifest.get("suite")
    games = manifest.get("games")
    if not isinstance(suite, dict) or not isinstance(games, list) or len(games) != 5:
        raise GateError("manifest must freeze exactly five games")
    ids: list[str] = []
    dry_count = 0
    for game in games:
        if not isinstance(game, dict):
            raise GateError("game entry is not an object")
        game_id = game.get("game_id")
        baselines = game.get("human_level_baseline_actions")
        if not isinstance(game_id, str) or not SAFE_ID.fullmatch(game_id):
            raise GateError("invalid game id")
        if game_id in ids:
            raise GateError("duplicate game id")
        ids.append(game_id)
        if not isinstance(baselines, list) or not baselines or any(type(item) is not int or item <= 0 for item in baselines):
            raise GateError(f"{game_id}: invalid human baseline")
        human_total = sum(baselines)
        if game.get("official_human_actions_total") != human_total:
            raise GateError(f"{game_id}: human total drift")
        expected_level_caps = [5 * item for item in baselines]
        if (
            game.get("action_cap_multiplier") != 5
            or game.get("level_action_caps") != expected_level_caps
            or game.get("max_actions") != sum(expected_level_caps)
        ):
            raise GateError(f"{game_id}: per-level/total action cap is not exactly 5x human baseline")
        if game.get("dry_run_stub") is True:
            dry_count += 1
            if game_id != DRY_GAME:
                raise GateError("unexpected dry-run game")
    arms = manifest_arms(manifest)
    if ids != suite.get("game_order") or suite.get("pair_order") != list(arms):
        raise GateError("frozen game or pair order drift")
    if dry_count != 1:
        raise GateError("exactly one dry-run game must be selected")
    common = manifest.get("common_live_model_config")
    treatment = manifest.get("treatment_only")
    if not isinstance(common, dict) or not isinstance(treatment, dict):
        raise GateError("missing model/treatment config")
    if schema_version < 3:
        if not isinstance(common.get("jcode_binary_sha256"), str) or not SHA256.fullmatch(common["jcode_binary_sha256"]):
            raise GateError("invalid jcode_binary_sha256")
        if not isinstance(common.get("jcode_source_commit"), str) or not GIT_COMMIT.fullmatch(common["jcode_source_commit"]):
            raise GateError("invalid jcode_source_commit")
        hashes = treatment.get("azdaja_binary_sha256")
        if not isinstance(hashes, dict) or set(hashes) != {"darwin-arm64", "linux-x86_64"}:
            raise GateError("Azdaja platform identity drift")
    else:
        if ids != ["ls20", "ft09", "vc33", "ar25", "wa30"]:
            raise GateError("private public game order drift")
        hashes = treatment.get("binary_sha256_by_platform")
        if not isinstance(hashes, dict) or set(hashes) != {"darwin-arm64"}:
            raise GateError("owner treatment platform identity drift")
        components = treatment.get("source_bundle_components_sha256")
        if not isinstance(components, dict) or set(components) != {"SKILL.md", "config.toml"}:
            raise GateError("owner treatment bundle identity drift")
        if any(not isinstance(item, str) or not SHA256.fullmatch(item) for item in components.values()):
            raise GateError("invalid owner treatment component digest")
        if treatment.get("bundle_version") != "0.1.0":
            raise GateError("owner bundle version drift")
        if treatment.get("root_model") != "claude-sonnet-5" or treatment.get("sub_model") != "claude-sonnet-5":
            raise GateError("treatment source model aliases drift")
        privacy = manifest.get("privacy_contract")
        if not isinstance(privacy, dict) or privacy.get("platform_pseudonym") != "Ember":
            raise GateError("platform pseudonym drift")
        if privacy.get("public_arm_order") != list(PRIVATE_ARMS) or privacy.get("public_game_order") != ids:
            raise GateError("neutral public identities drift")
        evidence = manifest.get("owner_only_evidence")
        if not isinstance(evidence, dict):
            raise GateError("owner-only evidence is missing")
        for key in ("track1_terminal_receipt_sha256", "claude_v7_terminal_receipt_sha256"):
            if not isinstance(evidence.get(key), str) or not SHA256.fullmatch(evidence[key]):
                raise GateError(f"invalid evidence binding: {key}")
        if evidence.get("track1_status") != "TERMINAL_COMPLETED_SCORED_ONCE_CLOSED" or evidence.get("track1_fixed_denominator") != 199:
            raise GateError("terminal-completion evidence drift")
        if schema_version == 3:
            if common.get("provider") != "claude" or common.get("model") != "claude-sonnet-5":
                raise GateError("v3 must use common Claude Sonnet-5 for both paired arms")
            if common.get("jcode_api") != "claude-oauth" or common.get("jcode_version") != "0.77.1":
                raise GateError("v3 Claude subscription route drift")
            if not isinstance(common.get("jcode_binary_sha256"), str) or not SHA256.fullmatch(common["jcode_binary_sha256"]):
                raise GateError("invalid v3 Jcode digest")
            if not re.fullmatch(r"[0-9a-f]{9}", str(common.get("jcode_build_git_hash", ""))):
                raise GateError("invalid v3 Jcode build revision")
            if privacy.get("public_output_contract") != "only paired per-game RHAE delta (ember minus baseline)":
                raise GateError("v3 public output contract drift")
            if privacy.get("public_result_top_level_keys") != ["identity", "arms", "games"] or privacy.get("public_result_game_keys") != ["game_id", "ember_minus_baseline_rhae_delta"]:
                raise GateError("v3 public result shape drift")
            if evidence.get("claude_v7_status") != "TERMINAL_STRICT_MINI_GATE_FAILED" or evidence.get("claude_v7_used_only_to_bind_owner_mandated_lane") is not True:
                raise GateError("v3 Claude verdict evidence drift")
            if evidence.get("known_bridge_socket_fast_path_provider_revalidation") is not False or evidence.get("known_bridge_gap_fix_claimed") is not False:
                raise GateError("v3 known bridge gap annotation drift")
        else:
            if common.get("provider") != "claude-code" or common.get("model") != "sonnet":
                raise GateError("v4 must use the direct Claude Code Sonnet lane")
            expected_invocation = {
                4: "direct-cli-fresh-process-v1",
                5: "direct-cli-fresh-process-v2",
                6: "direct-cli-fresh-process-v3",
                7: "direct-cli-fresh-process-v4",
                8: "direct-cli-fresh-process-v5",
                9: "direct-cli-fresh-process-v6",
            }[schema_version]
            if common.get("invocation") != expected_invocation or common.get("claude_version") != "2.1.234":
                raise GateError(f"v{schema_version} direct Claude invocation drift")
            if not isinstance(common.get("claude_binary_sha256"), str) or not SHA256.fullmatch(common["claude_binary_sha256"]):
                raise GateError(f"invalid v{schema_version} Claude binary digest")
            if schema_version in {5, 6, 7, 8, 9} and (
                not isinstance(common.get("lane_wrapper_sha256"), str)
                or not SHA256.fullmatch(common["lane_wrapper_sha256"])
            ):
                raise GateError(f"invalid v{schema_version} direct Claude wrapper digest")
            for key in ("print_mode", "no_session_persistence", "safe_mode", "no_tools", "no_project_discovery"):
                if common.get(key) is not True:
                    raise GateError(f"v4 Claude isolation drift: {key}")
            expected_game_keys = ["game_id", "ember_minus_baseline_rhae_delta", "baseline_wasted_actions", "ember_wasted_actions"]
            if privacy.get("public_result_top_level_keys") != ["identity", "arms", "games"] or privacy.get("public_result_game_keys") != expected_game_keys:
                raise GateError("v4 public result shape drift")
            if privacy.get("wasted_action_definition") != "non-RESET action whose official post-action game feedback exactly equals the immediately preceding official game feedback":
                raise GateError("v4 wasted action definition drift")
            if evidence.get("claude_v7_verdict") != "STOP_NO_FULL" or evidence.get("separate_arc_claude_lane_owner_authorized") is not True:
                raise GateError("v4 separate ARC Claude authority drift")
            if evidence.get("expired_jcode_oauth_route_rejected") is not True or evidence.get("direct_claude_cli_selected") is not True:
                raise GateError("v4 local Claude diagnosis drift")
            if evidence.get("bridge_helper_bypassed") is not True or evidence.get("helper_bug_persists") is not False:
                raise GateError("v4 helper bypass evidence drift")
            mitigation = evidence.get("isolation")
            if not isinstance(mitigation, str) or any(name not in mitigation for name in ("HOME", "JCODE_HOME", "JCODE_RUNTIME_DIR", "AZDAJA_HOME")):
                raise GateError("v4 arm isolation evidence drift")
            freshness = manifest.get("execution_freshness")
            generation = f"v{schema_version}"
            expected_identity = f"ARC3-FIVE-PUBLIC-PAIRED-EMBER-V{schema_version}-RESULT"
            expected_filename = f"arc3-ember-five-public-v{schema_version}-result.json"
            if (
                not isinstance(freshness, dict)
                or freshness.get("manifest_generation") != generation
                or freshness.get("authorization_generation") != generation
                or freshness.get("output_identity") != expected_identity
                or freshness.get("output_filename") != expected_filename
                or freshness.get("reuse_v3_game_session_output_or_runtime") is not False
                or (schema_version in {5, 6, 7, 8, 9} and freshness.get("reuse_v4_game_session_output_or_runtime") is not False)
                or (schema_version in {6, 7, 8, 9} and freshness.get("reuse_v5_game_session_output_or_runtime") is not False)
                or (schema_version in {7, 8, 9} and freshness.get("reuse_v6_game_session_output_or_runtime") is not False)
                or (schema_version in {8, 9} and freshness.get("reuse_v7_game_session_output_or_runtime") is not False)
                or (schema_version == 9 and freshness.get("reuse_v8_game_session_output_or_runtime") is not False)
                or freshness.get("fresh_runtime_per_arm") is not True
                or freshness.get("fresh_process_per_model_call") is not True
                or freshness.get("output_must_not_preexist") is not True
                or (
                    schema_version in {8, 9}
                    and freshness.get("private_failure_artifact_filename")
                    != f"arc3-ember-five-public-v{schema_version}.direct-claude-failure.private"
                )
                or (
                    schema_version in {8, 9}
                    and freshness.get("private_failure_artifact_must_not_preexist") is not True
                )
            ):
                raise GateError(f"v{schema_version} execution freshness drift")
            if schema_version == 5 and (
                evidence.get("v4_attempt_status") != "TERMINATED_LOCAL_WRAPPER_ERROR_ZERO_ACTIONS_ZERO_PAIRS"
                or evidence.get("duplicate_stdin_input_fixed") is not True
            ):
                raise GateError("v5 predecessor failure binding drift")
            if schema_version == 6 and (
                evidence.get("v5_attempt_status") != "TERMINATED_LOCAL_DRIVER_ERROR_ZERO_ACTIONS_ZERO_PAIRS"
                or evidence.get("driver_duplicate_stdin_input_fixed") is not True
            ):
                raise GateError("v6 predecessor failure binding drift")
            if schema_version == 7 and (
                evidence.get("v6_attempt_status") != "TERMINATED_DIRECT_CLAUDE_NONZERO_ZERO_ACTIONS_ZERO_PAIRS"
                or evidence.get("direct_cli_failure_classifier_added") is not True
                or evidence.get("direct_cli_failure_categories") != [
                    "auth", "invalid_model", "cli_usage", "sandbox_permission",
                    "rate_limit", "network", "other",
                ]
            ):
                raise GateError("v7 predecessor failure binding drift")
            if schema_version == 8 and (
                evidence.get("v7_attempt_status") != "TERMINATED_CLASSIFIED_OTHER_ZERO_ACTIONS_ZERO_PAIRS"
                or evidence.get("private_direct_cli_failure_artifact_added") is not True
                or evidence.get("private_failure_artifact_format") != "ARC3_DIRECT_CLAUDE_FAILURE_V1"
            ):
                raise GateError("v8 predecessor/private-evidence binding drift")
            if schema_version == 9 and (
                evidence.get("v8_attempt_status") != "TERMINATED_INVALID_EMPTY_MCP_CONFIG_ZERO_ACTIONS_ZERO_PAIRS"
                or evidence.get("valid_strict_empty_mcp_config_added") is not True
                or common.get("strict_empty_mcp_config") != {"mcpServers": {}}
            ):
                raise GateError("v9 predecessor/MCP config binding drift")
            if schema_version == 9 and (
                not isinstance(common.get("driver_sha256"), str)
                or not SHA256.fullmatch(common["driver_sha256"])
            ):
                raise GateError("invalid v9 driver digest")
    if any(not isinstance(item, str) or not SHA256.fullmatch(item) for item in hashes.values()):
        raise GateError("invalid owner treatment binary digest")
    if treatment.get("trigger_completed_turns") != 2 or treatment.get("max_skill_invocations_per_game") != 1:
        raise GateError("treatment trigger drift")
    launch = manifest.get("launch_gate")
    if not isinstance(launch, dict):
        raise GateError("missing launch gate")
    if schema_version == 1:
        if any(type(launch.get(name)) is not bool for name in ("track1_full_199_confirmed", "arc_live_owner_authorized")):
            raise GateError("invalid legacy launch gate")
    elif schema_version == 2:
        if (launch.get("track1_full_199_confirmed") is not False or launch.get("track1_fixed_199_in_flight") is not True or launch.get("arc_live_owner_authorized") is not True or manifest.get("status") != "FROZEN_AUTHORIZED_FOR_LIVE_MINI"):
            raise GateError("invalid in-flight authorized launch gate")
    elif schema_version == 3:
        if (launch.get("track1_full_199_confirmed") is not True or launch.get("track1_fixed_199_terminal_completed") is not True or launch.get("track1_fixed_denominator") != 199 or launch.get("claude_lane_owner_mandated") is not True or launch.get("arc_live_owner_authorized") is not True or manifest.get("status") != "FROZEN_AUTHORIZED_FOR_LIVE_MINI"):
            raise GateError("invalid terminal-complete Claude authorized launch gate")
    elif (launch.get("track1_full_199_confirmed") is not True or launch.get("track1_fixed_199_terminal_completed") is not True or launch.get("track1_fixed_denominator") != 199 or launch.get("separate_arc_claude_lane_owner_authorized") is not True or launch.get("arc_live_owner_authorized") is not True or manifest.get("status") != "FROZEN_AUTHORIZED_FOR_LIVE_MINI"):
        raise GateError("invalid v4 separately authorized ARC Claude launch gate")
    return manifest, digest

def manifest_game(manifest: dict[str, Any], game_id: str) -> dict[str, Any]:
    matches = [item for item in manifest["games"] if item["game_id"] == game_id]
    if len(matches) != 1:
        raise GateError(f"manifest lacks unique game {game_id}")
    return matches[0]


def owner_file_assertion(fd: int, *, expected_identity: tuple[int, int] | None = None) -> tuple[int, int]:
    metadata = os.fstat(fd)
    if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != HISTORY_MODE:
        raise GateError("file is not an owner-only regular file")
    if hasattr(os, "geteuid") and metadata.st_uid != os.geteuid():
        raise GateError("owner-only file owner mismatch")
    if metadata.st_nlink != 1:
        raise GateError("owner-only file must have exactly one link")
    identity = (metadata.st_dev, metadata.st_ino)
    if expected_identity is not None and identity != expected_identity:
        raise GateError("owner-only file identity changed")
    return identity


class OwnerHistory:
    def __init__(self, directory: Path) -> None:
        self.path = directory / "turn-history.jsonl"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        self.fd = os.open(self.path, flags, HISTORY_MODE)
        os.chmod(self.path, HISTORY_MODE)
        self.identity = owner_file_assertion(self.fd)
        self.records = 0

    def _read_bound_path(self) -> bytes:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(self.path, flags)
        try:
            owner_file_assertion(fd, expected_identity=self.identity)
            blocks: list[bytes] = []
            while True:
                block = os.read(fd, 65536)
                if not block:
                    break
                blocks.append(block)
            return b"".join(blocks)
        finally:
            os.close(fd)

    def append(self, value: dict[str, Any]) -> None:
        owner_file_assertion(self.fd, expected_identity=self.identity)
        self._read_bound_path()
        data = canonical_bytes(value) + b"\n"
        offset = 0
        while offset < len(data):
            offset += os.write(self.fd, data[offset:])
        os.fsync(self.fd)
        self.records += 1

    def digest(self) -> tuple[str, int]:
        owner_file_assertion(self.fd, expected_identity=self.identity)
        data = self._read_bound_path()
        return sha256_bytes(data), len(data)

    def close(self) -> None:
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1


def fsync_parent_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path.parent, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class OwnerActionJournal:
    """Append-only, crash-durable local custody of official action feedback."""

    def __init__(self, path: Path, *, arm: str, game_id: str) -> None:
        if not path.is_absolute():
            raise GateError("action journal path must be absolute")
        if arm not in ARC_V2_ARMS or game_id != ARC_V2_GAME:
            raise GateError("action journal scope drift")
        self.path = path
        self.arm = arm
        self.game_id = game_id
        flags = (
            os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            self.fd = os.open(path, flags, HISTORY_MODE)
        except FileExistsError as exc:
            raise GateError("action journal already exists") from exc
        os.fchmod(self.fd, HISTORY_MODE)
        self.identity = owner_file_assertion(self.fd)
        self.records = 0
        self.last_record_sha256 = ARC_V2_GENESIS_HASH
        fsync_parent_directory(path)

    def _assert_bound_path(self) -> None:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(self.path, flags)
        try:
            owner_file_assertion(fd, expected_identity=self.identity)
        finally:
            os.close(fd)

    def _read_bound_path(self) -> bytes:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(self.path, flags)
        try:
            owner_file_assertion(fd, expected_identity=self.identity)
            blocks: list[bytes] = []
            while True:
                block = os.read(fd, 65536)
                if not block:
                    break
                blocks.append(block)
            return b"".join(blocks)
        finally:
            os.close(fd)

    def append(self, value: dict[str, Any]) -> dict[str, Any]:
        owner_file_assertion(self.fd, expected_identity=self.identity)
        self._assert_bound_path()
        if "record_sha256" in value or "previous_record_sha256" in value:
            raise GateError("action journal caller attempted to inject hash chain")
        body = {
            **value,
            "sequence": self.records,
            "previous_record_sha256": self.last_record_sha256,
        }
        record_sha256 = sha256_bytes(canonical_bytes(body))
        record = {**body, "record_sha256": record_sha256}
        data = canonical_bytes(record) + b"\n"
        offset = 0
        while offset < len(data):
            written = os.write(self.fd, data[offset:])
            if written <= 0:
                raise GateError("action journal append failed")
            offset += written
        os.fsync(self.fd)
        self.records += 1
        self.last_record_sha256 = record_sha256
        return record

    def append_start(self, observation: "Observation") -> dict[str, Any]:
        return self.append({
            "record_type": "start",
            "arm": self.arm,
            "game_id": self.game_id,
            "turn": 0,
            "state": observation.state,
            "levels_completed": observation.levels_completed,
            "start_observation": observation.history_value(),
        })

    def append_action(
        self,
        *,
        turn: int,
        before: "Observation",
        action: "Action",
        after: "Observation",
    ) -> dict[str, Any]:
        return self.append({
            "record_type": "action",
            "arm": self.arm,
            "game_id": self.game_id,
            "turn": turn,
            "state": {"before": before.state, "after": after.state},
            "action": {"name": action.name, "data": action.data},
            "levels_completed": {
                "before": before.levels_completed,
                "after": after.levels_completed,
                "change": after.levels_completed - before.levels_completed,
            },
            "before_feedback": before.history_value(),
            "after_feedback": after.history_value(),
        })

    def digest(self) -> tuple[str, int]:
        owner_file_assertion(self.fd, expected_identity=self.identity)
        data = self._read_bound_path()
        return sha256_bytes(data), len(data)

    def close(self) -> None:
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1


@dataclass(frozen=True)
class Observation:
    game_id: str
    state: str
    levels_completed: int
    win_levels: int
    available_actions: tuple[str, ...]
    public_state: dict[str, Any]

    def state_digest(self) -> str:
        return sha256_bytes(canonical_bytes({
            "game_id": self.game_id,
            "state": self.state,
            "levels_completed": self.levels_completed,
            "public_state": self.public_state,
        }))

    def history_value(self) -> dict[str, Any]:
        return {
            "game_id": self.game_id,
            "state": self.state,
            "levels_completed": self.levels_completed,
            "win_levels": self.win_levels,
            "available_actions": list(self.available_actions),
            "observation": self.public_state,
        }


@dataclass(frozen=True)
class Action:
    name: str
    data: dict[str, int]

    def __post_init__(self) -> None:
        if self.name not in ACTIONS:
            raise GateError(f"invalid action {self.name!r}")
        if self.name == "ACTION6":
            if set(self.data) != {"x", "y"} or any(type(self.data[key]) is not int or not 0 <= self.data[key] <= 63 for key in ("x", "y")):
                raise GateError("ACTION6 requires integer x/y in [0,63]")
        elif self.data:
            raise GateError(f"{self.name} must not carry action data")


class Game(Protocol):
    @property
    def observation(self) -> Observation: ...
    def step(self, action: Action) -> Observation: ...
    def close(self) -> None: ...


class Model(Protocol):
    calls: int
    def choose(self, observation: Observation, *, turn: int, history_path: Path, advisory: str | None) -> Action: ...
    def close(self) -> None: ...


class Skill(Protocol):
    invocations: int
    def analyze(self, history_path: Path, expected_identity: tuple[int, int]) -> str: ...


class StubArcadeGame:
    """Tiny deterministic simulation labelled with one public game id.

    It is not an ARC environment and never opens a socket. The toy state has a
    left boundary at 0 and a goal at 2, exposing only ACTION3/ACTION4.
    """

    def __init__(self, game_id: str) -> None:
        if game_id != DRY_GAME:
            raise GateError("stub permits exactly one public game id")
        self.position = 0
        self.closed = False
        self._observation = self._make_observation()

    def _make_observation(self) -> Observation:
        won = self.position == 2
        return Observation(
            game_id=DRY_GAME,
            state="WIN" if won else "NOT_FINISHED",
            levels_completed=1 if won else 0,
            win_levels=7,
            available_actions=() if won else ("ACTION3", "ACTION4"),
            public_state={"stub": True, "position": self.position, "goal": 2},
        )

    @property
    def observation(self) -> Observation:
        return self._observation

    def step(self, action: Action) -> Observation:
        if self.closed:
            raise GateError("step after close")
        if action.name not in self._observation.available_actions:
            raise GateError("stub received unavailable action")
        if action.name == "ACTION3":
            self.position = max(0, self.position - 1)
        else:
            self.position = min(2, self.position + 1)
        self._observation = self._make_observation()
        return self._observation

    def close(self) -> None:
        self.closed = True




class StubArcade:
    """In-process stand-in for the official Arcade.make surface."""

    def __init__(self) -> None:
        self.make_calls = 0
        self.game_ids: list[str] = []

    def make(self, game_id: str, *, seed: int = 0, **options: Any) -> StubArcadeGame:
        if seed != 0 or options:
            raise GateError("stub Arcade accepts only the frozen seed and no live options")
        self.make_calls += 1
        self.game_ids.append(game_id)
        return StubArcadeGame(game_id)


class StubJcodeModel:
    """One deterministic model implementation shared by both arms."""

    def __init__(self) -> None:
        self.calls = 0

    def choose(self, observation: Observation, *, turn: int, history_path: Path, advisory: str | None) -> Action:
        del observation, history_path
        self.calls += 1
        # Native explores a known-left boundary for 24 turns. Once the same
        # deterministic model receives the treatment advisory it moves right.
        if advisory == "prefer ACTION4" or turn > 24:
            return Action("ACTION4", {})
        return Action("ACTION3", {})

    def close(self) -> None:
        return


class StubAzdajaSkill:
    def __init__(self) -> None:
        self.invocations = 0
        self.last_input_sha256: str | None = None

    def analyze(self, history_path: Path, expected_identity: tuple[int, int]) -> str:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(history_path, flags)
        try:
            owner_file_assertion(fd, expected_identity=expected_identity)
            data = b""
            while True:
                block = os.read(fd, 65536)
                if not block:
                    break
                data += block
        finally:
            os.close(fd)
        rows = [json.loads(line) for line in data.decode("utf-8").splitlines()]
        turns = [row for row in rows if row.get("record_type") == "turn"]
        if len(turns) < 2:
            raise GateError("stub skill triggered before history accumulated")
        self.invocations += 1
        self.last_input_sha256 = sha256_bytes(data)
        return "prefer ACTION4"


class LiveAzdajaSkill:
    def __init__(self, binary: Path, config: dict[str, Any], expected_sha256: str, env: dict[str, str]) -> None:
        if sha256_bytes(binary.read_bytes()) != expected_sha256:
            raise GateError("Azdaja binary digest mismatch")
        self.binary = binary
        self.config = config
        self.env = env
        self.invocations = 0
        self.last_input_sha256: str | None = None

    def analyze(self, history_path: Path, expected_identity: tuple[int, int]) -> str:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(history_path, flags)
        try:
            owner_file_assertion(fd, expected_identity=expected_identity)
            data = b""
            while True:
                block = os.read(fd, 65536)
                if not block:
                    break
                data += block
        finally:
            os.close(fd)
        self.last_input_sha256 = sha256_bytes(data)
        question = self.config["skill_question"]
        completed = subprocess.run(
            [str(self.binary), "solo", question, "-f", str(history_path), "--model", self.config["root_model"], "--sub-model", self.config["sub_model"]],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.env,
            timeout=300,
            check=False,
        )
        if completed.returncode != 0:
            if "direct_claude_failure=" in completed.stderr:
                category = direct_claude_failure_category(completed.stderr)
                raise GateError(f"Azdaja skill direct Claude process failed: {category}")
            raise GateError("Azdaja skill process failed")
        verify_fd = os.open(history_path, flags)
        try:
            owner_file_assertion(verify_fd, expected_identity=expected_identity)
            after_blocks: list[bytes] = []
            while True:
                block = os.read(verify_fd, 65536)
                if not block:
                    break
                after_blocks.append(block)
        finally:
            os.close(verify_fd)
        if b"".join(after_blocks) != data:
            raise GateError("Azdaja skill modified its owner-only input")
        advisory = completed.stdout.strip()
        if not advisory or len(advisory) > 4096:
            raise GateError("Azdaja advisory is empty or oversized")
        self.invocations += 1
        return advisory


def ndjson_response(text: str) -> str:
    assembled = ""
    completed = ""
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue
        kind = value.get("type") or value.get("ev")
        if kind in {"text_delta", "assistant_text_delta"} and isinstance(value.get("text"), str):
            assembled += value["text"]
        for key in ("response", "output_text", "text", "content"):
            item = value.get(key)
            if kind in {"result", "message_end", "assistant", "final", "done"} and isinstance(item, str):
                completed = item
    return completed or assembled


class LiveJcodeModel:
    def __init__(self, binary: Path, config: dict[str, Any], expected_sha256: str, env: dict[str, str]) -> None:
        if sha256_bytes(binary.read_bytes()) != expected_sha256:
            raise GateError("Jcode binary digest mismatch")
        self.binary = binary
        self.config = config
        self.env = env
        self.calls = 0

    def choose(self, observation: Observation, *, turn: int, history_path: Path, advisory: str | None) -> Action:
        prompt = canonical_bytes({
            "contract": "Return exactly one JSON object: action is RESET or ACTION1..ACTION7; data is {} except ACTION6 requires integer x,y in 0..63.",
            "turn": turn,
            "owner_turn_history_file": str(history_path),
            "current_observation": observation.history_value(),
            "azdaja_advisory": advisory,
        }).decode("utf-8")
        command = [
            str(self.binary), "run", "--ndjson", "--no-update", "--no-selfdev",
            "--provider", self.config["provider"], "--model", self.config["model"],
            "--tool-profile", self.config["tool_profile"], "--tools", ",".join(self.config["tools"]),
            "--cwd", str(history_path.parent), prompt,
        ]
        completed = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.env, timeout=300, check=False)
        if completed.returncode != 0:
            raise GateError("Jcode action process failed")
        raw = ndjson_response(completed.stdout).strip()
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GateError("Jcode action is not exact JSON") from exc
        if not isinstance(value, dict) or set(value) != {"action", "data"} or not isinstance(value["action"], str) or not isinstance(value["data"], dict):
            raise GateError("Jcode action JSON has wrong shape")
        self.calls += 1
        return Action(value["action"], value["data"])

    def close(self) -> None:
        subprocess.run(
            [str(self.binary), "server", "stop", "--force", "--json", "--no-update", "--no-selfdev"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env=self.env, timeout=20, check=False,
        )


class LiveClaudeModel:
    """Fresh direct Claude Code process for every game action decision."""

    def __init__(
        self,
        binary: Path,
        config: dict[str, Any],
        owner_home: Path,
        runtime_root: Path,
        env: dict[str, str],
        failure_artifact: Path | None = None,
    ) -> None:
        if sha256_bytes(binary.read_bytes()) != config["claude_binary_sha256"]:
            raise GateError("Claude Code binary digest mismatch")
        self.binary = binary
        self.config = config
        self.owner_home = owner_home
        self.runtime_root = runtime_root
        self.env = env
        self.failure_artifact = failure_artifact
        self.calls = 0
        self.wrapper = Path(__file__).with_name("claude_lane.py")
        if not self.wrapper.is_file():
            raise GateError("direct Claude lane wrapper is missing")
        expected_wrapper = config.get("lane_wrapper_sha256")
        if expected_wrapper is not None and sha256_bytes(self.wrapper.read_bytes()) != expected_wrapper:
            raise GateError("direct Claude lane wrapper digest mismatch")

    def choose(self, observation: Observation, *, turn: int, history_path: Path, advisory: str | None) -> Action:
        del history_path
        prompt = canonical_bytes({
            "contract": "Return exactly one JSON object: action is RESET or ACTION1..ACTION7; data is {} except ACTION6 requires integer x,y in 0..63.",
            "turn": turn,
            "current_observation": observation.history_value(),
            "ember_advisory": advisory,
        })
        command = [
            sys.executable, str(self.wrapper), "action",
            "--claude", str(self.binary),
            "--owner-home", str(self.owner_home),
            "--runtime-root", str(self.runtime_root),
            "--model", self.config["model"],
        ]
        if self.failure_artifact is not None:
            command += ["--failure-artifact", str(self.failure_artifact)]
        completed = subprocess.run(
            command,
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
            timeout=320,
            check=False,
        )
        if completed.returncode != 0:
            category = direct_claude_failure_category(completed.stderr)
            raise GateError(f"direct Claude action process failed: {category}")
        try:
            value = json.loads(completed.stdout)
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise GateError("direct Claude action is not exact JSON") from exc
        if not isinstance(value, dict) or set(value) != {"action", "data"} or not isinstance(value["action"], str) or not isinstance(value["data"], dict):
            raise GateError("direct Claude action JSON has wrong shape")
        self.calls += 1
        return Action(value["action"], value["data"])

    def close(self) -> None:
        return


def public_frame_value(raw: Any) -> dict[str, Any]:
    frame = getattr(raw, "frame", [])
    normalized: list[Any] = []
    for item in frame or []:
        normalized.append(item.tolist() if hasattr(item, "tolist") else item)
    return {"frame": normalized, "full_reset": bool(getattr(raw, "full_reset", False))}


class LiveArcadeGame:
    def __init__(self, game_id: str, api_key: str) -> None:
        # This import and every Arcade operation are unreachable in the frozen
        # prep state because authorization is checked first.
        try:
            os.environ["MPLBACKEND"] = "Agg"
            import arc_agi  # type: ignore
            from arcengine import GameAction  # type: ignore
        except ImportError as exc:
            raise GateError("official arc-agi toolkit is not installed") from exc
        self.GameAction = GameAction
        self.arcade = arc_agi.Arcade(arc_api_key=api_key, operation_mode=arc_agi.OperationMode.ONLINE)
        self.env = None
        try:
            self.env = self.arcade.make(game_id, seed=0, save_recording=False, include_frame_data=True, render_mode=None)
            if self.env is None:
                raise GateError("Arcade.make returned no environment")
            self.game_id = game_id
            self._observation = self._convert(self.env.observation_space)
        except Exception:
            close_env = getattr(self.env, "close", None)
            if callable(close_env):
                close_env()
            close_card = getattr(self.arcade, "close_scorecard", None)
            if callable(close_card):
                close_card()
            raise

    def _convert(self, raw: Any) -> Observation:
        if raw is None:
            raise GateError("Arcade returned no frame")
        raw_actions = getattr(raw, "available_actions", []) or getattr(self.env, "action_space", [])
        action_names = []
        for item in raw_actions:
            action_names.append(item.name if hasattr(item, "name") else self.GameAction.from_id(item).name)
        actions = tuple(sorted(action_names))
        state = getattr(raw, "state", "UNKNOWN")
        state_name = state.name if hasattr(state, "name") else str(state)
        return Observation(
            game_id=self.game_id,
            state=state_name,
            levels_completed=int(getattr(raw, "levels_completed", 0)),
            win_levels=int(getattr(raw, "win_levels", 0)),
            available_actions=actions,
            public_state=public_frame_value(raw),
        )

    @property
    def observation(self) -> Observation:
        return self._observation

    def step(self, action: Action) -> Observation:
        enum_action = getattr(self.GameAction, action.name)
        self._observation = self._convert(self.env.step(enum_action, data=action.data))
        return self._observation

    def close(self) -> None:
        close = getattr(self.env, "close", None)
        if callable(close):
            close()
        close_card = getattr(self.arcade, "close_scorecard", None)
        if callable(close_card):
            close_card()


def shadow_rhae(human_baselines: list[int], agent_actions: list[int]) -> float:
    if len(agent_actions) > len(human_baselines) or any(type(item) is not int or item <= 0 for item in agent_actions):
        raise GateError("invalid per-level agent action counts")
    denominator = sum(range(1, len(human_baselines) + 1))
    numerator = 0.0
    for index, count in enumerate(agent_actions):
        numerator += (index + 1) * min((human_baselines[index] / count) ** 2, 1.15)
    value = numerator / denominator
    if not math.isfinite(value) or not 0 <= value <= 1.15:
        raise GateError("invalid shadow RHAE")
    return value


def write_owner_json(path: Path, value: dict[str, Any], *, label: str) -> tuple[str, int]:
    if not path.is_absolute():
        raise GateError(f"{label} path must be absolute")
    data = canonical_bytes(value) + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, HISTORY_MODE)
    except FileExistsError as exc:
        raise GateError(f"{label} already exists") from exc
    try:
        os.fchmod(fd, HISTORY_MODE)
        owner_file_assertion(fd)
        offset = 0
        while offset < len(data):
            written = os.write(fd, data[offset:])
            if written <= 0:
                raise GateError(f"{label} write failed")
            offset += written
        os.fsync(fd)
        owner_file_assertion(fd)
    finally:
        os.close(fd)
    fsync_parent_directory(path)
    return sha256_bytes(data), len(data)


def arm_terminal_receipt(
    row: dict[str, Any],
    *,
    experiment_id: str,
    manifest_sha256: str,
    journal_path: Path,
) -> dict[str, Any]:
    if row.get("game_id") != ARC_V2_GAME or row.get("arm") not in ARC_V2_ARMS:
        raise GateError("ARC-v2 arm receipt scope drift")
    return {
        "receipt_type": "ARC_V2_ARM_TERMINAL_RECEIPT_V1",
        "experiment_id": experiment_id,
        "manifest_sha256": manifest_sha256,
        "game_id": ARC_V2_GAME,
        "arm": row["arm"],
        "absolute_shadow_rhae": row["shadow_rhae_fraction"],
        "levels_completed": row["completed_levels"],
        "per_level_action_counts": row["per_level_action_counts"],
        "total_actions_issued": row["actions"],
        "wasted_actions": {
            "aggregate": row["official_feedback_wasted_actions"],
            "revisited_states": row["wasted_actions"]["revisited_states"],
            "repeated_known_controls": row["wasted_actions"]["repeated_known_controls"],
        },
        "termination_reason": row["termination_reason"],
        "action_journal": {
            "path": str(journal_path),
            "sha256": row["action_journal"]["sha256"],
            "record_count": row["action_journal"]["record_count"],
        },
        "platform_scorecard_retrieved": False,
    }


def paired_terminal_receipt(
    rows: list[dict[str, Any]],
    *,
    experiment_id: str,
    manifest_sha256: str,
    receipt_paths: dict[str, Path],
    receipt_sha256s: dict[str, str],
) -> dict[str, Any]:
    if len(rows) != 2 or [row.get("arm") for row in rows] != list(ARC_V2_ARMS):
        raise GateError("ARC-v2 paired receipt requires baseline then ember")
    if any(row.get("game_id") != ARC_V2_GAME for row in rows):
        raise GateError("ARC-v2 paired receipt permits only vc33")
    baseline, ember = rows
    if (
        baseline["common_model_config_sha256"] != ember["common_model_config_sha256"]
        or baseline["action_cap"] != ember["action_cap"]
    ):
        raise GateError("ARC-v2 paired model config or action cap differs")
    baseline_score = baseline["shadow_rhae_fraction"]
    ember_score = ember["shadow_rhae_fraction"]
    delta = ember_score - baseline_score
    if not all(math.isfinite(value) for value in (baseline_score, ember_score, delta)):
        raise GateError("ARC-v2 paired receipt contains a non-finite RHAE value")
    arms: list[dict[str, Any]] = []
    for row in rows:
        arm = row["arm"]
        arms.append({
            "arm": arm,
            "absolute_shadow_rhae": row["shadow_rhae_fraction"],
            "terminal_receipt_path": str(receipt_paths[arm]),
            "terminal_receipt_sha256": receipt_sha256s[arm],
        })
    return {
        "receipt_type": "ARC_V2_PAIRED_TERMINAL_RECEIPT_V1",
        "experiment_id": experiment_id,
        "manifest_sha256": manifest_sha256,
        "game_id": ARC_V2_GAME,
        "pair_order": list(ARC_V2_ARMS),
        "arms": arms,
        "ember_minus_baseline_absolute_shadow_rhae_delta": delta,
        "platform_scorecard_retrieved": False,
        "full_five_game_rerun": "HOLD_PENDING_EXPLICIT_POST_PUBLIC_FLIP_AUTHORIZATION",
    }


def run_arm(
    *,
    arm: str,
    game_id: str,
    game_config: dict[str, Any],
    common_config: dict[str, Any],
    treatment_config: dict[str, Any],
    game: Game,
    model: Model,
    skill: Skill | None,
    root: Path,
    action_journal_path: Path | None = None,
    terminal_receipt_path: Path | None = None,
    terminal_receipt_context: dict[str, str] | None = None,
) -> dict[str, Any]:
    valid_arms = set(LEGACY_ARMS + PRIVATE_ARMS)
    control_arms = {LEGACY_ARMS[0], PRIVATE_ARMS[0]}
    if arm not in valid_arms or (arm in control_arms) != (skill is None):
        raise GateError("arm/skill binding mismatch")
    custody_arguments = (action_journal_path, terminal_receipt_path, terminal_receipt_context)
    custody_enabled = all(item is not None for item in custody_arguments)
    if any(item is not None for item in custody_arguments) and not custody_enabled:
        raise GateError("partial local-custody binding")
    if custody_enabled and (arm not in ARC_V2_ARMS or game_id != ARC_V2_GAME):
        raise GateError("local custody is restricted to the ARC-v2 vc33 pair")

    os.chmod(root, DIRECTORY_MODE)
    history = OwnerHistory(root)
    action_journal: OwnerActionJournal | None = None
    cleanup_errors: list[str] = []
    action_counts: Counter[str] = Counter()
    seen_states = {game.observation.state_digest()}
    known_controls: set[tuple[str, str, bytes]] = set()
    revisited_states = 0
    repeated_known_controls = 0
    official_feedback_wasted_actions = 0
    completed_turns = 0
    level_start_action = 0
    level_action_counts: list[int] = []
    previous_levels = game.observation.levels_completed
    persisted_advisory: str | None = None
    skill_input_sha256: str | None = None
    trajectory_hasher = hashlib.sha256()
    try:
        if game.observation.game_id != game_id:
            raise GateError("game observation identity drift")
        if custody_enabled:
            assert action_journal_path is not None
            action_journal = OwnerActionJournal(
                action_journal_path, arm=arm, game_id=game_id
            )
            action_journal.append_start(game.observation)
        history.append({"record_type": "start", "observation": game.observation.history_value()})
        max_actions = game_config["max_actions"]
        level_action_caps = game_config["level_action_caps"]
        per_level_action_counts = [0 for _ in level_action_caps]
        termination_reason = "GAME_WIN"
        while game.observation.state != "WIN" and completed_turns < max_actions:
            current_level = game.observation.levels_completed
            if current_level >= len(level_action_caps):
                raise GateError("non-winning frame is beyond the frozen level cap table")
            if completed_turns - level_start_action >= level_action_caps[current_level]:
                termination_reason = "ACTION_BUDGET"
                break
            if (
                skill is not None
                and skill.invocations < treatment_config["max_skill_invocations_per_game"]
                and completed_turns == treatment_config["trigger_completed_turns"]
            ):
                persisted_advisory = skill.analyze(history.path, history.identity)
                skill_input_sha256 = getattr(skill, "last_input_sha256", None)
            before = game.observation
            forced_reset = before.state in {"GAME_OVER", "NOT_PLAYED"}
            if forced_reset:
                action = Action("RESET", {})
            else:
                history_before_model = history.digest()
                action = model.choose(
                    before,
                    turn=completed_turns + 1,
                    history_path=history.path,
                    advisory=persisted_advisory,
                )
                if history.digest() != history_before_model:
                    raise GateError("model modified the accumulated turn history")
            if not forced_reset and action.name not in before.available_actions:
                raise GateError("model selected unavailable action")
            control = (before.state_digest(), action.name, canonical_bytes(action.data))
            if control in known_controls:
                repeated_known_controls += 1
            else:
                known_controls.add(control)
            after = game.step(action)
            if after.game_id != game_id:
                raise GateError("post-action game observation identity drift")
            # Aggregate wasted actions are based only on exact official feedback
            # equality. RESET is excluded. The two diagnostic counters remain
            # separately preserved in the owner receipt.
            if action.name != "RESET" and after.history_value() == before.history_value():
                official_feedback_wasted_actions += 1
            completed_turns += 1
            action_counts[action.name] += 1
            per_level_action_counts[current_level] += 1
            after_digest = after.state_digest()
            if after_digest in seen_states:
                revisited_states += 1
            else:
                seen_states.add(after_digest)
            if action_journal is not None:
                # This retained O_APPEND/O_EXCL journal is fsynced immediately,
                # before any temporary history write or per-arm cleanup.
                action_journal.append_action(
                    turn=completed_turns,
                    before=before,
                    action=action,
                    after=after,
                )
            row = {
                "record_type": "turn",
                "turn": completed_turns,
                "before_state_sha256": before.state_digest(),
                "action": {"name": action.name, "data": action.data},
                "after": after.history_value(),
            }
            history.append(row)
            trajectory_hasher.update(canonical_bytes(row) + b"\n")
            if after.levels_completed > previous_levels:
                if after.levels_completed != previous_levels + 1:
                    raise GateError("levels completed skipped")
                level_action_counts.append(completed_turns - level_start_action)
                level_start_action = completed_turns
                previous_levels = after.levels_completed
        if game.observation.state != "WIN":
            termination_reason = "ACTION_BUDGET"
        expected_skill_calls = 0 if arm in control_arms else 1
        actual_skill_calls = 0 if skill is None else skill.invocations
        if actual_skill_calls != expected_skill_calls:
            raise GateError("skill invocation count drift")
        if game.observation.levels_completed != len(level_action_counts):
            raise GateError("completed-level accounting drift")
        history_sha256, history_bytes = history.digest()
        score = shadow_rhae(game_config["human_level_baseline_actions"], level_action_counts)
        status = "complete" if termination_reason == "GAME_WIN" else "action_budget"
        action_journal_value: dict[str, Any] | None = None
        if action_journal is not None:
            journal_sha256, journal_bytes = action_journal.digest()
            if action_journal.records != completed_turns + 1:
                raise GateError("action journal record count drift")
            action_journal_value = {
                "path": str(action_journal.path),
                "sha256": journal_sha256,
                "record_count": action_journal.records,
                "bytes": journal_bytes,
                "owner_only_mode_asserted": True,
                "append_fsync_each_record_asserted": True,
                "canonical_hash_chain_asserted": True,
            }
        result = {
            "arm": arm,
            "game_id": game_id,
            "status": status,
            "termination_reason": termination_reason,
            "common_model_config_sha256": sha256_bytes(canonical_bytes(common_config)),
            "level_action_caps": level_action_caps,
            "action_cap": max_actions,
            "actions": completed_turns,
            "actions_by_name": dict(sorted(action_counts.items())),
            "completed_levels": len(level_action_counts),
            "agent_actions_per_completed_level": level_action_counts,
            "per_level_action_counts": per_level_action_counts,
            "shadow_rhae_fraction": score,
            "official_feedback_wasted_actions": official_feedback_wasted_actions,
            "wasted_actions": {
                "revisited_states": revisited_states,
                "repeated_known_controls": repeated_known_controls,
            },
            "game_adapter": "arcade-api-game-stub-v1" if isinstance(game, StubArcadeGame) else "official-arcade-online-v1",
            "model_adapter": (
                "deterministic-stub-v1" if isinstance(model, StubJcodeModel)
                else "direct-claude-code-v1" if isinstance(model, LiveClaudeModel)
                else "jcode-live-v1"
            ),
            "model_calls": model.calls,
            "skill_adapter": None if skill is None else (
                "deterministic-stub-v1" if isinstance(skill, StubAzdajaSkill)
                else "azdaja-live-v1"
            ),
            "skill_invocations": actual_skill_calls,
            "skill_input_contract_asserted": skill is None or skill_input_sha256 is not None,
            "skill_input_history_sha256": skill_input_sha256,
            "history": {
                "records": history.records,
                "bytes": history_bytes,
                "sha256": history_sha256,
                "owner_only_mode_asserted": True,
                "single_link_asserted": True,
            },
            "action_journal": action_journal_value,
            "trajectory_sha256": trajectory_hasher.hexdigest(),
        }
        if custody_enabled:
            assert terminal_receipt_path is not None
            assert terminal_receipt_context is not None
            assert action_journal_path is not None
            if set(terminal_receipt_context) != {"experiment_id", "manifest_sha256"}:
                raise GateError("terminal receipt context drift")
            receipt = arm_terminal_receipt(
                result,
                experiment_id=terminal_receipt_context["experiment_id"],
                manifest_sha256=terminal_receipt_context["manifest_sha256"],
                journal_path=action_journal_path,
            )
            receipt_sha256, receipt_bytes = write_owner_json(
                terminal_receipt_path, receipt, label=f"{arm} terminal receipt"
            )
            result["terminal_receipt"] = {
                "path": str(terminal_receipt_path),
                "sha256": receipt_sha256,
                "bytes": receipt_bytes,
            }
        return result
    finally:
        if action_journal is not None:
            try:
                action_journal.close()
            except OSError as exc:
                cleanup_errors.append(type(exc).__name__)
        try:
            history.close()
        except OSError as exc:
            cleanup_errors.append(type(exc).__name__)
        try:
            model.close()
        except Exception as exc:  # cleanup result is fail-closed below
            cleanup_errors.append(type(exc).__name__)
        try:
            game.close()
        except Exception as exc:
            cleanup_errors.append(type(exc).__name__)
        if cleanup_errors:
            raise GateError("arm cleanup failed: " + ",".join(cleanup_errors))


def stage_active_jcode_oauth(owner_home: Path, destination_jcode_home: Path, *, provider: str) -> None:
    profiles = {
        "openai": ("openai-auth.json", "openai_accounts", "active_openai_account"),
        "claude": ("auth.json", "anthropic_accounts", "active_anthropic_account"),
    }
    profile = profiles.get(provider)
    if profile is None:
        raise GateError("unsupported Jcode OAuth provider")
    auth_file, accounts_key, active_key = profile
    source_path = owner_home / ".jcode" / auth_file
    source_fd = os.open(source_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        owner_file_assertion(source_fd)
        blocks: list[bytes] = []
        while True:
            block = os.read(source_fd, 65536)
            if not block:
                break
            blocks.append(block)
        value = json.loads(b"".join(blocks).decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GateError("owner Jcode OAuth record is invalid JSON") from exc
    finally:
        os.close(source_fd)
    if not isinstance(value, dict):
        raise GateError("owner Jcode OAuth record is not an object")
    accounts = value.get(accounts_key)
    active = value.get(active_key)
    if not isinstance(accounts, list) or not isinstance(active, str):
        raise GateError("owner Jcode OAuth metadata is invalid")
    selected = [item for item in accounts if isinstance(item, dict) and item.get("label") == active]
    if len(selected) != 1:
        raise GateError("owner Jcode active OAuth account is missing or ambiguous")
    destination_jcode_home.mkdir(mode=DIRECTORY_MODE, parents=True)
    auth_path = destination_jcode_home / auth_file
    fd = os.open(auth_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, HISTORY_MODE)
    try:
        data = canonical_bytes({accounts_key: selected, active_key: active})
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


def shell_quote(path: Path) -> str:
    return "'" + str(path).replace("'", "'\\''") + "'"


def validate_managed_skill(skill_root: Path, treatment: dict[str, Any]) -> None:
    expected_sources = treatment["managed_skill_components_sha256"]
    asset_root = Path(__file__).resolve().parents[2] / "assets"
    source_skill = asset_root / "SKILL.md"
    source_config = asset_root / "config.toml"
    for path in (source_skill, source_config):
        expected = expected_sources.get(path.name)
        if not isinstance(expected, str) or sha256_bytes(path.read_bytes()) != expected:
            raise GateError(f"managed skill source component mismatch: {path.name}")

    release = treatment.get("azdaja_release")
    if not isinstance(release, str) or not release.startswith("v") or len(release) == 1:
        raise GateError("invalid Azdaja release identity")
    staged_binary = skill_root / "azdaja"
    expected_binary = treatment["azdaja_binary_sha256"][platform_key()]
    if not staged_binary.is_file() or sha256_bytes(staged_binary.read_bytes()) != expected_binary:
        raise GateError("installed managed skill binary mismatch")

    installed_skill = skill_root / "SKILL.md"
    expected_skill = (
        source_skill.read_text(encoding="utf-8")
        .replace("{{VERSION}}", release[1:])
        .replace("{{BIN}}", shell_quote(staged_binary))
    )
    if not installed_skill.is_file() or installed_skill.read_text(encoding="utf-8") != expected_skill:
        raise GateError("installed managed skill component mismatch: SKILL.md")

    installed_config = skill_root / "config.toml"
    try:
        source_value = tomllib.loads(source_config.read_text(encoding="utf-8"))
        installed_value = tomllib.loads(installed_config.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise GateError("installed managed skill component mismatch: config.toml") from exc
    if installed_value != source_value:
        raise GateError("installed managed skill component mismatch: config.toml")

    expected_names = {".azdaja-managed", "SKILL.md", "config.toml", "azdaja"}
    if {path.name for path in skill_root.iterdir()} != expected_names:
        raise GateError("installed managed skill file set mismatch")


def install_managed_skill(binary: Path, env: dict[str, str], treatment: dict[str, Any]) -> None:
    expected_binary = treatment["azdaja_binary_sha256"][platform_key()]
    if not binary.is_file() or sha256_bytes(binary.read_bytes()) != expected_binary:
        raise GateError("Azdaja binary digest mismatch before install")
    expected_jcode_home = Path(env["HOME"]) / ".jcode"
    if Path(env["JCODE_HOME"]) != expected_jcode_home:
        raise GateError("Jcode managed-skill home is not aligned")
    completed = subprocess.run(
        [str(binary), "install", "--harness", "jcode"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        timeout=60,
        check=False,
    )
    if completed.returncode != 0:
        raise GateError("provider-free managed skill installation failed")
    skill_root = expected_jcode_home / "skills" / "azdaja"
    validate_managed_skill(skill_root, treatment)
    env["AZDAJA_CONFIG"] = str(skill_root / "config.toml")


def ember_bundle_paths(bundle: Path) -> dict[str, Path]:
    return {
        "binary": bundle / "ember",
        "SKILL.md": bundle / "SKILL.md",
        "config.toml": bundle / "config.toml",
    }


def validate_ember_source_bundle(bundle: Path, treatment: dict[str, Any]) -> dict[str, Path]:
    paths = ember_bundle_paths(bundle)
    if not bundle.is_dir() or {path.name for path in bundle.iterdir()} != {"ember", "SKILL.md", "config.toml"}:
        raise GateError("Ember owner bundle file set mismatch")
    expected_binary = treatment["binary_sha256_by_platform"][platform_key()]
    if not paths["binary"].is_file() or sha256_bytes(paths["binary"].read_bytes()) != expected_binary:
        raise GateError("Ember owner bundle binary mismatch")
    components = treatment["source_bundle_components_sha256"]
    for name in ("SKILL.md", "config.toml"):
        if not paths[name].is_file() or sha256_bytes(paths[name].read_bytes()) != components[name]:
            raise GateError(f"Ember owner bundle component mismatch: {name}")
    skill_template = paths["SKILL.md"].read_text(encoding="utf-8")
    if "{{VERSION}}" not in skill_template or "{{BIN}}" not in skill_template:
        raise GateError("Ember skill template placeholders are missing")
    try:
        config = tomllib.loads(paths["config.toml"].read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise GateError("Ember owner bundle config is invalid") from exc
    expected_route = {
        "sub_llm_cmd": "jcode-api",
        "default_model": "claude-sonnet-5",
        "jcode_provider": "claude",
        "jcode_reasoning": "low",
    }
    if any(config.get(key) != value for key, value in expected_route.items()):
        raise GateError("Ember owner bundle Claude route drift")
    return paths


def stage_ember_skill(
    bundle: Path,
    env: dict[str, str],
    treatment: dict[str, Any],
    *,
    direct_lane_command: str | None = None,
) -> Path:
    source = validate_ember_source_bundle(bundle, treatment)
    expected_jcode_home = Path(env["HOME"]) / ".jcode"
    if Path(env["JCODE_HOME"]) != expected_jcode_home:
        raise GateError("Jcode managed-skill home is not aligned")
    skill_root = expected_jcode_home / "skills" / "ember"
    skill_root.mkdir(mode=DIRECTORY_MODE, parents=True)
    staged_binary = skill_root / "ember"
    shutil.copyfile(source["binary"], staged_binary)
    os.chmod(staged_binary, 0o700)
    rendered = (
        source["SKILL.md"].read_text(encoding="utf-8")
        .replace("{{VERSION}}", treatment["bundle_version"])
        .replace("{{BIN}}", shell_quote(staged_binary))
    )
    (skill_root / "SKILL.md").write_text(rendered, encoding="utf-8")
    config_text = source["config.toml"].read_text(encoding="utf-8")
    if direct_lane_command is not None:
        config_text, replacements = re.subn(
            r'(?m)^sub_llm_cmd\s*=\s*"[^"]*"\s*$',
            "sub_llm_cmd = " + json.dumps(direct_lane_command),
            config_text,
        )
        if replacements != 1:
            raise GateError("staged Ember direct Claude command replacement failed")
    (skill_root / "config.toml").write_text(config_text, encoding="utf-8")
    os.chmod(skill_root / "SKILL.md", HISTORY_MODE)
    os.chmod(skill_root / "config.toml", HISTORY_MODE)
    if {path.name for path in skill_root.iterdir()} != {"ember", "SKILL.md", "config.toml"}:
        raise GateError("staged Ember skill file set mismatch")
    if "{{VERSION}}" in rendered or "{{BIN}}" in rendered:
        raise GateError("staged Ember skill was not fully rendered")
    staged_config = tomllib.loads((skill_root / "config.toml").read_text(encoding="utf-8"))
    source_config = tomllib.loads(source["config.toml"].read_text(encoding="utf-8"))
    if direct_lane_command is None:
        if staged_config != source_config:
            raise GateError("staged Ember config mismatch")
    else:
        expected_config = dict(source_config)
        expected_config["sub_llm_cmd"] = direct_lane_command
        if staged_config != expected_config or "jcode-api" in staged_config["sub_llm_cmd"]:
            raise GateError("staged Ember direct Claude config mismatch")
    if sha256_bytes(staged_binary.read_bytes()) != treatment["binary_sha256_by_platform"][platform_key()]:
        raise GateError("staged Ember binary mismatch")
    env["AZDAJA_CONFIG"] = str(skill_root / "config.toml")
    return staged_binary


def safe_env(base_home: Path, *, reasoning: str) -> dict[str, str]:
    env = {
        "HOME": str(base_home),
        "PATH": os.defpath,
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "USER": os.environ.get("USER", ""),
        "LOGNAME": os.environ.get("LOGNAME", ""),
        "SHELL": os.environ.get("SHELL", "/bin/sh"),
        "JCODE_HOME": str(base_home / ".jcode"),
        "JCODE_RUNTIME_DIR": str(base_home / "jcode-runtime"),
        "JCODE_NO_TELEMETRY": "1",
        "JCODE_RUN_MCP": "0",
        "JCODE_RUN_AUTO_POKE": "0",
        "JCODE_OPENAI_REASONING_EFFORT": reasoning,
        "AZDAJA_HOME": str(base_home / "azdaja-state"),
    }
    return env


def direct_claude_subcall_command(
    claude: Path,
    owner_home: Path,
    runtime_root: Path,
    failure_artifact: Path,
) -> str:
    wrapper = Path(__file__).with_name("claude_lane.py")
    parts = [
        sys.executable,
        str(wrapper),
        "subcall",
        "--claude", str(claude),
        "--owner-home", str(owner_home),
        "--runtime-root", str(runtime_root),
        "--failure-artifact", str(failure_artifact),
        "--model", "{model}",
    ]
    return shlex.join(parts)


def _process_snapshot(pid: int) -> tuple[int, int, str] | None:
    completed = subprocess.run(
        ["/bin/ps", "-o", "uid=", "-o", "pgid=", "-o", "command=", "-p", str(pid)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        env={"PATH": os.defpath, "LANG": "C", "LC_ALL": "C"},
        timeout=5,
        check=False,
    )
    line = completed.stdout.strip()
    if completed.returncode != 0 or not line:
        return None
    fields = line.split(maxsplit=2)
    if len(fields) != 3:
        raise GateError("private bridge process snapshot is malformed")
    try:
        return int(fields[0]), int(fields[1]), fields[2]
    except ValueError as exc:
        raise GateError("private bridge process snapshot is malformed") from exc


def stop_ember_bridge(env: dict[str, str]) -> bool:
    private = Path(env["AZDAJA_HOME"]) / "jcode-api"
    pidfile = private / "bridge.pid"
    if not pidfile.exists():
        return False
    fd = os.open(pidfile, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        owner_file_assertion(fd)
        raw = os.read(fd, 64)
        if os.read(fd, 1):
            raise GateError("private bridge pidfile is oversized")
    finally:
        os.close(fd)
    try:
        pid = int(raw.decode("ascii"))
    except (UnicodeError, ValueError) as exc:
        raise GateError("private bridge pidfile is invalid") from exc
    if pid <= 1 or pid == os.getpid():
        raise GateError("private bridge pid is unsafe")
    snapshot = _process_snapshot(pid)
    if snapshot is None:
        return True
    uid, pgid, command = snapshot
    if hasattr(os, "geteuid") and uid != os.geteuid():
        raise GateError("private bridge process owner mismatch")
    if pgid != pid or "api-bridge" not in command:
        raise GateError("private bridge process identity mismatch")
    marker = private / "runtime-dir"
    runtime = marker.read_text(encoding="utf-8")
    if not runtime or str(Path(runtime) / "api.sock") not in command:
        raise GateError("private bridge runtime identity mismatch")
    os.killpg(pgid, signal.SIGTERM)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if _process_snapshot(pid) is None:
            return True
        time.sleep(0.05)
    os.killpg(pgid, signal.SIGKILL)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if _process_snapshot(pid) is None:
            return True
        time.sleep(0.05)
    raise GateError("private bridge cleanup failed")


def provider_free_live_artifact_preflight(
    model_binary: Path,
    owner_bundle: Path,
    manifest: dict[str, Any],
    *,
    owner_home: Path | None = None,
) -> dict[str, str]:
    schema_version = manifest.get("schema_version")
    if schema_version in DIRECT_CLAUDE_SCHEMAS:
        expected_model = manifest["common_live_model_config"]["claude_binary_sha256"]
        model_label = "Claude Code"
    else:
        expected_model = manifest["common_live_model_config"]["jcode_binary_sha256"]
        model_label = "Jcode"
    if not model_binary.is_file() or sha256_bytes(model_binary.read_bytes()) != expected_model:
        raise GateError(f"{model_label} binary digest mismatch")
    try:
        import importlib.metadata
        import importlib.util
        runtime_versions = {
            "arc_agi": importlib.metadata.version("arc-agi"),
            "arcengine": importlib.metadata.version("arcengine"),
        }
        if importlib.util.find_spec("arc_agi") is None or importlib.util.find_spec("arcengine") is None:
            raise ImportError("official ARC modules are missing")
    except Exception as exc:
        raise GateError("pinned official ARC runtime is unavailable") from exc
    if runtime_versions != {"arc_agi": "0.9.9", "arcengine": "0.9.3"}:
        raise GateError("official ARC runtime version drift")
    work = Path(tempfile.mkdtemp(prefix=f"arc3-v{schema_version}-artifact-preflight-"))
    try:
        env = safe_env(work / "home", reasoning=manifest["common_live_model_config"]["reasoning_effort"])
        Path(env["HOME"]).mkdir(mode=DIRECTORY_MODE)
        if schema_version in DIRECT_CLAUDE_SCHEMAS:
            if owner_home is None:
                raise GateError(f"v{schema_version} Claude preflight requires owner HOME")
            runtime_root = work / "claude-runtime"
            runtime_root.mkdir(mode=DIRECTORY_MODE)
            version = subprocess.run(
                [str(model_binary), "--version"], stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                env={"HOME": str(owner_home), "PATH": str(model_binary.parent) + os.pathsep + os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"},
                timeout=20, check=False,
            )
            help_probe = subprocess.run(
                [str(model_binary), "--help"], stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                env={"HOME": str(owner_home), "PATH": str(model_binary.parent) + os.pathsep + os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"},
                timeout=20, check=False,
            )
            if version.returncode != 0 or not version.stdout.startswith(manifest["common_live_model_config"]["claude_version"] + " "):
                raise GateError("Claude Code version preflight failed")
            required_flags = ("--print", "--json-schema", "--no-session-persistence", "--safe-mode", "--tools")
            if help_probe.returncode != 0 or any(flag not in help_probe.stdout for flag in required_flags):
                raise GateError("Claude Code CLI contract preflight failed")
            wrapper = Path(__file__).with_name("claude_lane.py")
            expected_wrapper = manifest["common_live_model_config"].get("lane_wrapper_sha256")
            if expected_wrapper is not None and sha256_bytes(wrapper.read_bytes()) != expected_wrapper:
                raise GateError("direct Claude lane wrapper digest mismatch")
            auth_probe = subprocess.run(
                [sys.executable, str(wrapper), "auth-check", "--claude", str(model_binary), "--owner-home", str(owner_home), "--runtime-root", str(runtime_root)],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=env, timeout=40, check=False,
            )
            if auth_probe.returncode != 0:
                raise GateError("direct Claude subscription auth preflight failed")
            command = direct_claude_subcall_command(
                model_binary, owner_home, runtime_root, work / "private-failure-artifact"
            )
            stage_ember_skill(owner_bundle, env, manifest["treatment_only"], direct_lane_command=command)
            runtime_versions["claude_code"] = manifest["common_live_model_config"]["claude_version"]
        elif schema_version == 3:
            stage_ember_skill(owner_bundle, env, manifest["treatment_only"])
        else:
            install_managed_skill(owner_bundle, env, manifest["treatment_only"])
    finally:
        shutil.rmtree(work, ignore_errors=False)
    return runtime_versions

def authorization_gate(
    path: Path,
    manifest: dict[str, Any],
    manifest_sha256: str,
    *,
    private_failure_artifact: Path | None = None,
) -> dict[str, Any]:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        owner_file_assertion(fd)
    finally:
        os.close(fd)
    value = read_json_object(path)
    schema_version = manifest.get("schema_version")
    if schema_version == ARC_V2_SCHEMA:
        required = set(manifest["authorization_contract"]["required_fields"])
        if set(value) != required:
            raise GateError("ARC-v2 authorization receipt shape drift")
        launch = manifest["launch_gate"]
        if (
            value["experiment_id"] != manifest["experiment_id"]
            or value["manifest_sha256"] != manifest_sha256
            or value["output_identity"] != manifest["execution_freshness"]["output_identity"]
            or value["selected_game_id"] != ARC_V2_GAME
            or value["pair_count"] != 1
            or value["pair_order"] != list(ARC_V2_ARMS)
            or value["arc_live_owner_authorized"] is not True
            or value["arc_v2_exactly_one_pair_owner_authorized"] is not True
            or value["full_five_game_rerun_authorized"] is not False
            or value["separate_arc_claude_lane_owner_authorized"] is not True
            or value["track1_fixed_199_terminal_completed"] is not True
            or value["track1_fixed_denominator"] != 199
            or launch["arc_live_owner_authorized"] is not True
            or launch["arc_v2_exactly_one_pair_owner_authorized"] is not True
            or launch["full_five_game_rerun_authorized"] is not False
        ):
            raise GateError("ARC-v2 launch is not authorized for exactly one vc33 pair")
        if set(value["action_journal_paths"]) != set(ARC_V2_ARMS):
            raise GateError("ARC-v2 action journal arm binding drift")
        if set(value["terminal_receipt_paths"]) != set(ARC_V2_ARMS):
            raise GateError("ARC-v2 terminal receipt arm binding drift")
        raw_paths = {
            "output": value["output_path"],
            "private failure artifact": value["direct_claude_failure_artifact_path"],
            "paired receipt": value["paired_receipt_path"],
            **{
                f"{arm} action journal": value["action_journal_paths"][arm]
                for arm in ARC_V2_ARMS
            },
            **{
                f"{arm} terminal receipt": value["terminal_receipt_paths"][arm]
                for arm in ARC_V2_ARMS
            },
        }
        bound_paths: dict[str, Path] = {}
        for label, raw in raw_paths.items():
            if not isinstance(raw, str):
                raise GateError(f"ARC-v2 {label} path is not a string")
            artifact_path = Path(raw)
            if not artifact_path.is_absolute() or artifact_path.exists():
                raise GateError(f"ARC-v2 {label} path must be absolute and fresh")
            if not artifact_path.parent.is_dir():
                raise GateError(f"ARC-v2 {label} parent directory is missing")
            bound_paths[label] = artifact_path
        if len(set(bound_paths.values())) != len(bound_paths):
            raise GateError("ARC-v2 artifact paths must be distinct")
        expected_failure_name = manifest["execution_freshness"]["private_failure_artifact_filename"]
        if bound_paths["private failure artifact"].name != expected_failure_name:
            raise GateError("ARC-v2 private failure artifact identity drift")
        return value
    if schema_version in {4, 5, 6, 7, 8, 9}:
        required = {
            "experiment_id",
            "manifest_sha256",
            "output_identity",
            "track1_fixed_199_terminal_completed",
            "track1_fixed_denominator",
            "claude_v7_verdict",
            "separate_arc_claude_lane_owner_authorized",
            "arc_live_owner_authorized",
        }
        if schema_version in {8, 9}:
            required.add("private_failure_artifact_path")
    elif schema_version == 3:
        required = {
            "experiment_id",
            "manifest_sha256",
            "track1_fixed_199_terminal_completed",
            "track1_fixed_denominator",
            "claude_lane_owner_mandated",
            "arc_live_owner_authorized",
        }
    else:
        track_gate = "track1_fixed_199_in_flight" if schema_version == 2 else "track1_full_199_confirmed"
        required = {"experiment_id", "manifest_sha256", track_gate, "arc_live_owner_authorized"}
    if set(value) != required:
        raise GateError("authorization receipt shape drift")
    launch = manifest["launch_gate"]
    common_ok = (
        value["experiment_id"] == manifest["experiment_id"]
        and value["manifest_sha256"] == manifest_sha256
        and (schema_version not in {4, 5, 6, 7, 8, 9} or value["output_identity"] == manifest["execution_freshness"]["output_identity"])
        and (
            schema_version not in {8, 9}
            or (
                private_failure_artifact is not None
                and value["private_failure_artifact_path"] == str(private_failure_artifact)
            )
        )
        and value["arc_live_owner_authorized"] is True
        and launch.get("arc_live_owner_authorized") is True
        and manifest.get("status") == "FROZEN_AUTHORIZED_FOR_LIVE_MINI"
    )
    if schema_version in {4, 5, 6, 7, 8, 9}:
        track_ok = (
            value["track1_fixed_199_terminal_completed"] is True
            and value["track1_fixed_denominator"] == 199
            and value["claude_v7_verdict"] == "STOP_NO_FULL"
            and value["separate_arc_claude_lane_owner_authorized"] is True
            and launch.get("track1_fixed_199_terminal_completed") is True
            and launch.get("track1_fixed_denominator") == 199
            and launch.get("separate_arc_claude_lane_owner_authorized") is True
        )
    elif schema_version == 3:
        track_ok = (
            value["track1_fixed_199_terminal_completed"] is True
            and value["track1_fixed_denominator"] == 199
            and value["claude_lane_owner_mandated"] is True
            and launch.get("track1_fixed_199_terminal_completed") is True
            and launch.get("track1_fixed_denominator") == 199
            and launch.get("claude_lane_owner_mandated") is True
        )
    else:
        track_ok = value[track_gate] is True and launch.get(track_gate) is True
    if not common_ok or not track_ok:
        raise GateError("live ARC launch is not owner-authorized at its Track1 gate")
    return value


def platform_key() -> str:
    value = (platform.system(), platform.machine().lower())
    if value == ("Darwin", "arm64"):
        return "darwin-arm64"
    if value[0] == "Linux" and value[1] in {"x86_64", "amd64"}:
        return "linux-x86_64"
    raise GateError("unsupported Azdaja platform")


def public_ember_result(rows: list[dict[str, Any]], game_ids: list[str]) -> dict[str, Any]:
    if game_ids != ["ls20", "ft09", "vc33", "ar25", "wa30"]:
        raise GateError("public Ember result requires the exact five-game order")
    deltas: list[dict[str, Any]] = []
    for game_id in game_ids:
        selected = [row for row in rows if row["game_id"] == game_id]
        if [row["arm"] for row in selected] != list(PRIVATE_ARMS):
            raise GateError("paired arm order drift")
        baseline, ember = selected
        if baseline["common_model_config_sha256"] != ember["common_model_config_sha256"] or baseline["action_cap"] != ember["action_cap"]:
            raise GateError("paired model config or action cap differs")
        delta = ember["shadow_rhae_fraction"] - baseline["shadow_rhae_fraction"]
        if not math.isfinite(delta):
            raise GateError("paired RHAE delta is not finite")
        deltas.append({
            "game_id": game_id,
            "ember_minus_baseline_rhae_delta": delta,
        })
    return {
        "identity": "Ember",
        "arms": list(PRIVATE_ARMS),
        "games": deltas,
    }


def public_ember_result_v4(rows: list[dict[str, Any]], game_ids: list[str], *, helper_bug_persists: bool) -> dict[str, Any]:
    if game_ids != ["ls20", "ft09", "vc33", "ar25", "wa30"]:
        raise GateError("public Ember v4 result requires the exact five-game order")
    games: list[dict[str, Any]] = []
    for game_id in game_ids:
        selected = [row for row in rows if row["game_id"] == game_id]
        if [row["arm"] for row in selected] != list(PRIVATE_ARMS):
            raise GateError("paired arm order drift")
        baseline, ember = selected
        if baseline["common_model_config_sha256"] != ember["common_model_config_sha256"] or baseline["action_cap"] != ember["action_cap"]:
            raise GateError("paired model config or action cap differs")
        delta = ember["shadow_rhae_fraction"] - baseline["shadow_rhae_fraction"]
        if not math.isfinite(delta):
            raise GateError("paired RHAE delta is not finite")
        row = {
            "game_id": game_id,
            "ember_minus_baseline_rhae_delta": delta,
            "baseline_wasted_actions": baseline["official_feedback_wasted_actions"],
            "ember_wasted_actions": ember["official_feedback_wasted_actions"],
        }
        if helper_bug_persists:
            row["helper_bug_annotation"] = "A provider-helper limitation remained isolated; paired results use the same Claude lane."
        games.append(row)
    return {"identity": "Ember", "arms": list(PRIVATE_ARMS), "games": games}


def run_pair(manifest: dict[str, Any], manifest_sha256: str, *, live: bool, args: argparse.Namespace) -> dict[str, Any]:
    schema_version = manifest.get("schema_version")
    arms = manifest_arms(manifest)
    if live and schema_version in {4, 5, 6, 7, 8, 9}:
        raise GateError(f"v{schema_version} execution identity is consumed; use fresh ARC-v2")
    if schema_version == ARC_V2_SCHEMA and not live:
        raise GateError("ARC-v2 local-custody package has no dry-run execution mode")
    if schema_version == ARC_V2_SCHEMA and (
        manifest["suite"]["game_order"] != [ARC_V2_GAME]
        or manifest["suite"]["pair_order"] != list(ARC_V2_ARMS)
        or manifest["suite"]["pairs"] != 1
        or len(manifest["games"]) != 1
    ):
        raise GateError("ARC-v2 runtime scope must be exactly vc33 baseline then ember")

    owner_bundle = (
        args.ember_bundle
        if schema_version in {3, 4, 5, 6, 7, 8, 9, ARC_V2_SCHEMA}
        else args.azdaja
    )
    authorization_value: dict[str, Any] | None = None
    custody_journal_paths: dict[str, Path] = {}
    custody_receipt_paths: dict[str, Path] = {}
    custody_paired_receipt_path: Path | None = None
    if live:
        if args.authorization is None:
            raise GateError("live mode requires --authorization")
        if schema_version in {8, 9, ARC_V2_SCHEMA}:
            failure_artifact = args.direct_claude_failure_artifact
            if (
                failure_artifact is None
                or not failure_artifact.is_absolute()
                or failure_artifact.name != manifest["execution_freshness"]["private_failure_artifact_filename"]
                or failure_artifact.exists()
            ):
                raise GateError(
                    f"schema {schema_version} requires its fresh nonexisting private failure artifact identity"
                )
        else:
            failure_artifact = None
        authorization_value = authorization_gate(
            args.authorization,
            manifest,
            manifest_sha256,
            private_failure_artifact=failure_artifact,
        )
        if schema_version == ARC_V2_SCHEMA:
            assert authorization_value is not None
            if failure_artifact != Path(authorization_value["direct_claude_failure_artifact_path"]):
                raise GateError("ARC-v2 failure artifact differs from authorization")
            if args.output is None or args.output != Path(authorization_value["output_path"]):
                raise GateError("ARC-v2 output differs from authorization")
            if not args.output.is_absolute() or args.output.exists():
                raise GateError("ARC-v2 requires its fresh absolute owner output")
            custody_journal_paths = {
                arm: Path(authorization_value["action_journal_paths"][arm])
                for arm in ARC_V2_ARMS
            }
            custody_receipt_paths = {
                arm: Path(authorization_value["terminal_receipt_paths"][arm])
                for arm in ARC_V2_ARMS
            }
            custody_paired_receipt_path = Path(authorization_value["paired_receipt_path"])
        elif schema_version in {4, 5, 6, 7, 8, 9} and (
            args.output is None
            or args.output.name != manifest["execution_freshness"]["output_filename"]
            or args.output.exists()
        ):
            raise GateError(f"v{schema_version} requires its fresh nonexisting output identity")
        api_key = os.environ.get("ARC_API_KEY")
        if not api_key:
            raise GateError("ARC_API_KEY is absent")
        model_binary = args.claude if schema_version in DIRECT_CLAUDE_SCHEMAS else args.jcode
        if model_binary is None or owner_bundle is None:
            if schema_version in DIRECT_CLAUDE_SCHEMAS:
                required = "--claude and --ember-bundle"
            elif schema_version == 3:
                required = "--jcode and --ember-bundle"
            else:
                required = "--jcode and --azdaja"
            raise GateError(f"live mode requires {required}")
        provider_free_live_artifact_preflight(
            model_binary, owner_bundle, manifest, owner_home=args.owner_home
        )
        game_ids = manifest["suite"]["game_order"]
        if schema_version == ARC_V2_SCHEMA and game_ids != [ARC_V2_GAME]:
            raise GateError("ARC-v2 live selection drifted from vc33")
    else:
        if schema_version in {3, 4, 5, 6, 7, 8, 9, ARC_V2_SCHEMA}:
            raise GateError(f"v{schema_version} owner package does not emit a stub result")
        api_key = ""
        game_ids = [game["game_id"] for game in manifest["games"] if game["dry_run_stub"] is True]
        if game_ids != [DRY_GAME]:
            raise GateError("dry run must select exactly one public game id")

    rows: list[dict[str, Any]] = []
    cleanup_proofs: list[bool] = []
    isolation_values: dict[str, set[str]] = {
        key: set() for key in ("HOME", "JCODE_HOME", "JCODE_RUNTIME_DIR", "AZDAJA_HOME")
    }
    for game_id in game_ids:
        game_config = manifest_game(manifest, game_id)
        for arm in arms:
            work = Path(tempfile.mkdtemp(prefix=f"arc3-v{schema_version}-paired-"))
            arm_env: dict[str, str] | None = None
            try:
                run_root = work / "run"
                run_root.mkdir(mode=DIRECTORY_MODE)
                if live:
                    env = safe_env(
                        work / "home",
                        reasoning=manifest["common_live_model_config"]["reasoning_effort"],
                    )
                    arm_env = env
                    env["PATH"] = str(model_binary.parent) + os.pathsep + os.defpath
                    Path(env["HOME"]).mkdir(mode=DIRECTORY_MODE)
                    for key in isolation_values:
                        value = env[key]
                        if value in isolation_values[key]:
                            raise GateError(f"isolated {key} was reused")
                        isolation_values[key].add(value)
                    if schema_version in DIRECT_CLAUDE_SCHEMAS:
                        claude_runtime = work / "claude-runtime"
                        claude_runtime.mkdir(mode=DIRECTORY_MODE)
                        model: Model = LiveClaudeModel(
                            model_binary,
                            manifest["common_live_model_config"],
                            args.owner_home,
                            claude_runtime,
                            env,
                            failure_artifact,
                        )
                    else:
                        stage_active_jcode_oauth(
                            args.owner_home,
                            Path(env["JCODE_HOME"]),
                            provider=manifest["common_live_model_config"]["provider"],
                        )
                        model = LiveJcodeModel(
                            model_binary,
                            manifest["common_live_model_config"],
                            manifest["common_live_model_config"]["jcode_binary_sha256"],
                            env,
                        )
                    skill: Skill | None = None
                    if arm == arms[1]:
                        if schema_version in DIRECT_CLAUDE_SCHEMAS:
                            command = direct_claude_subcall_command(
                                model_binary, args.owner_home, claude_runtime, failure_artifact
                            )
                            staged_binary = stage_ember_skill(
                                owner_bundle,
                                env,
                                manifest["treatment_only"],
                                direct_lane_command=command,
                            )
                            expected = manifest["treatment_only"]["binary_sha256_by_platform"][platform_key()]
                        elif schema_version == 3:
                            staged_binary = stage_ember_skill(
                                owner_bundle, env, manifest["treatment_only"]
                            )
                            expected = manifest["treatment_only"]["binary_sha256_by_platform"][platform_key()]
                        else:
                            install_managed_skill(owner_bundle, env, manifest["treatment_only"])
                            staged_binary = owner_bundle
                            expected = manifest["treatment_only"]["azdaja_binary_sha256"][platform_key()]
                        skill = LiveAzdajaSkill(
                            staged_binary, manifest["treatment_only"], expected, env
                        )
                    game: Game = LiveArcadeGame(game_id, api_key)
                else:
                    arcade_stub = StubArcade()
                    model = StubJcodeModel()
                    game = arcade_stub.make(game_id, seed=0)
                    if arcade_stub.make_calls != 1 or arcade_stub.game_ids != [game_id]:
                        raise GateError("stub Arcade make proof failed")
                    skill = StubAzdajaSkill() if arm == arms[1] else None
                custody_kwargs: dict[str, Any] = {}
                if schema_version == ARC_V2_SCHEMA:
                    custody_kwargs = {
                        "action_journal_path": custody_journal_paths[arm],
                        "terminal_receipt_path": custody_receipt_paths[arm],
                        "terminal_receipt_context": {
                            "experiment_id": manifest["experiment_id"],
                            "manifest_sha256": manifest_sha256,
                        },
                    }
                row = run_arm(
                    arm=arm,
                    game_id=game_id,
                    game_config=game_config,
                    common_config=manifest["common_live_model_config"],
                    treatment_config=manifest["treatment_only"],
                    game=game,
                    model=model,
                    skill=skill,
                    root=run_root,
                    **custody_kwargs,
                )
                rows.append(row)
            finally:
                try:
                    if live and schema_version == 3 and arm == arms[1] and arm_env is not None:
                        stop_ember_bridge(arm_env)
                finally:
                    shutil.rmtree(work, ignore_errors=False)
                    cleanup_proofs.append(not work.exists())
    expected_rows = len(game_ids) * len(arms)
    if len(rows) != expected_rows or not all(cleanup_proofs):
        raise GateError("pair completion or cleanup gate failed")

    if schema_version == ARC_V2_SCHEMA:
        if len(rows) != 2 or game_ids != [ARC_V2_GAME] or arms != ARC_V2_ARMS:
            raise GateError("ARC-v2 completed scope is not exactly one ordered pair")
        assert custody_paired_receipt_path is not None
        receipt_sha256s = {
            row["arm"]: row["terminal_receipt"]["sha256"] for row in rows
        }
        paired = paired_terminal_receipt(
            rows,
            experiment_id=manifest["experiment_id"],
            manifest_sha256=manifest_sha256,
            receipt_paths=custody_receipt_paths,
            receipt_sha256s=receipt_sha256s,
        )
        paired_sha256, paired_bytes = write_owner_json(
            custody_paired_receipt_path, paired, label="paired terminal receipt"
        )
        return {
            "identity": manifest["execution_freshness"]["output_identity"],
            "mode": "owner_only_local_custody",
            "game_id": ARC_V2_GAME,
            "pair_order": list(ARC_V2_ARMS),
            "pair_count": 1,
            "public_output_emitted": False,
            "platform_scorecard_retrieved": False,
            "paired_receipt": {
                "path": str(custody_paired_receipt_path),
                "sha256": paired_sha256,
                "bytes": paired_bytes,
            },
            "full_five_game_rerun": "HOLD_PENDING_EXPLICIT_POST_PUBLIC_FLIP_AUTHORIZATION",
        }
    if schema_version in {4, 5, 6, 7, 8, 9}:
        return public_ember_result_v4(
            rows,
            game_ids,
            helper_bug_persists=manifest["owner_only_evidence"]["helper_bug_persists"],
        )
    if schema_version == 3:
        return public_ember_result(rows, game_ids)
    pairs: list[dict[str, Any]] = []
    for game_id in game_ids:
        selected = [row for row in rows if row["game_id"] == game_id]
        if [row["arm"] for row in selected] != list(arms):
            raise GateError("paired arm order drift")
        control, treatment = selected
        if control["common_model_config_sha256"] != treatment["common_model_config_sha256"] or control["action_cap"] != treatment["action_cap"]:
            raise GateError("paired model config or action cap differs")
        pairs.append({
            "game_id": game_id,
            "shadow_rhae_delta_treatment_minus_control": treatment["shadow_rhae_fraction"] - control["shadow_rhae_fraction"],
            "action_delta_treatment_minus_control": treatment["actions"] - control["actions"],
            "wasted_action_deltas_treatment_minus_control": {
                key: treatment["wasted_actions"][key] - control["wasted_actions"][key]
                for key in ("revisited_states", "repeated_known_controls")
            },
        })
    return {
        "schema_version": 1,
        "experiment_id": manifest["experiment_id"],
        "mode": "live" if live else "offline_stub_dry_run",
        "authority": "local shadow only; no absolute ARC score or leaderboard claim",
        "manifest_sha256": manifest_sha256,
        "driver_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "game_ids": game_ids,
        "rows": rows,
        "paired_deltas": pairs,
        "proof": {
            "arc_live_requests": None if live else 0,
            "provider_model_inferences": None if live else 0,
            "live_tokens_spent": None if live else 0,
            "stub_model_decisions": None if live else sum(row["model_calls"] for row in rows),
            "exactly_one_public_game_stubbed": not live and game_ids == [DRY_GAME],
            "action_history_tool_rhae_cleanup_complete": True,
            "history_workspaces_removed": all(cleanup_proofs),
        },
    }


def write_output(path: Path | None, value: dict[str, Any]) -> None:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if path is None:
        sys.stdout.write(data)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), HISTORY_MODE)
    except FileExistsError as exc:
        raise GateError("output already exists") from exc
    try:
        os.fchmod(fd, HISTORY_MODE)
        owner_file_assertion(fd)
        offset = 0
        encoded = data.encode("utf-8")
        while offset < len(encoded):
            written = os.write(fd, encoded[offset:])
            if written <= 0:
                raise GateError("output write failed")
            offset += written
        os.fsync(fd)
        owner_file_assertion(fd)
    finally:
        os.close(fd)
    fsync_parent_directory(path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fail-closed ARC-AGI-3 paired driver")
    parser.add_argument("mode", choices=("preflight", "dry-run", "live"))
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("mini-pilot-manifest.json"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--jcode", type=Path)
    parser.add_argument("--claude", type=Path)
    parser.add_argument("--azdaja", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--ember-bundle", type=Path)
    parser.add_argument("--owner-home", type=Path, default=Path.home())
    parser.add_argument("--direct-claude-failure-artifact", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest, digest = verify_manifest(args.manifest)
        if args.mode == "preflight":
            schema_version = manifest.get("schema_version")
            owner_bundle = args.ember_bundle if schema_version in {3, *DIRECT_CLAUDE_SCHEMAS} else args.azdaja
            model_binary = args.claude if schema_version in DIRECT_CLAUDE_SCHEMAS else args.jcode
            if (model_binary is None) != (owner_bundle is None):
                if schema_version in DIRECT_CLAUDE_SCHEMAS:
                    required = "--claude and --ember-bundle"
                elif schema_version == 3:
                    required = "--jcode and --ember-bundle"
                else:
                    required = "--jcode and --azdaja"
                raise GateError(f"artifact preflight requires both {required}")
            artifacts_validated = model_binary is not None and owner_bundle is not None
            runtime_versions: dict[str, str] | None = None
            if artifacts_validated:
                runtime_versions = provider_free_live_artifact_preflight(
                    model_binary, owner_bundle, manifest, owner_home=args.owner_home
                )
            owner_authorized = manifest["launch_gate"]["arc_live_owner_authorized"] is True
            value = {
                "status": "READY_FOR_OWNER_EXECUTION" if owner_authorized else "PREP_ONLY_LIVE_BLOCKED",
                "manifest_scope_validated": (
                    "exactly_one_vc33_baseline_then_ember_pair"
                    if schema_version == ARC_V2_SCHEMA else "exactly_five_games"
                ),
                "full_five_game_rerun": (
                    "HOLD_PENDING_EXPLICIT_POST_PUBLIC_FLIP_AUTHORIZATION"
                    if schema_version == ARC_V2_SCHEMA else None
                ),
                "local_live_artifacts_validated": artifacts_validated,
                "official_runtime_versions": runtime_versions,
                "parent_arc_api_key_present": bool(os.environ.get("ARC_API_KEY")),
                "network_or_model_call_made": False,
            }
        else:
            value = run_pair(manifest, digest, live=args.mode == "live", args=args)
        write_output(args.output, value)
        return 0
    except GateError as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 2
    except OSError:
        print("blocked: local file operation failed", file=sys.stderr)
        return 2
    except subprocess.SubprocessError:
        print("blocked: local subprocess failed", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
