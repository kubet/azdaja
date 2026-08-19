#!/usr/bin/env python3
"""Exactly-once post-public ARC-v2 five-game local-custody runner.

Preparation and ``preflight`` are manifest-only. ``live`` refuses before any
ARC game or model call unless a fresh owner-only GitHub metadata receipt proves
``kubet/azdaja`` PUBLIC and the separately owner-custodied approval binds the
explicit post-flip GO marker. Platform scorecards are never requested.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterator

HERE = Path(__file__).resolve().parent
CORE_SPEC = importlib.util.spec_from_file_location("arc3_driver_post_public_core", HERE / "driver.py")
assert CORE_SPEC and CORE_SPEC.loader
CORE = importlib.util.module_from_spec(CORE_SPEC)
sys.modules[CORE_SPEC.name] = CORE
CORE_SPEC.loader.exec_module(CORE)

GAMES = ("ls20", "ft09", "vc33", "ar25", "wa30")
ARMS = ("baseline", "ember")
SCHEMA = 11
EXPERIMENT_ID = "ARC-V2-FIVE-POSTLAUNCH-LOCAL-CUSTODY-V1"
APPROVAL_TYPE = "ARC_V2_FIVE_POST_PUBLIC_OWNER_APPROVAL_V1"
VISIBILITY_RECEIPT_TYPE = "GITHUB_REPOSITORY_PUBLIC_VISIBILITY_RECEIPT_V1"
EXECUTION_SENTINEL_TYPE = "ARC_V2_FIVE_POST_PUBLIC_EXECUTION_CONSUMED_V1"
OWNER_GO = "OWNER_GO_ARC_V2_FIVE_POST_PUBLIC_FLIP_V1"
PUBLIC = "PUBLIC"

GateError = CORE.GateError


def canonical_bytes(value: Any) -> bytes:
    return CORE.canonical_bytes(value)


def sha256_bytes(data: bytes) -> str:
    return CORE.sha256_bytes(data)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso_utc(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_utc(value: Any, *, label: str) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise GateError(f"{label} is not a UTC timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise GateError(f"{label} is not a UTC timestamp") from exc
    if parsed.tzinfo is None:
        raise GateError(f"{label} is not timezone-aware")
    return parsed.astimezone(dt.timezone.utc)


def read_owner_bytes(path: Path, *, label: str) -> bytes:
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise GateError(f"cannot open owner-only {label}") from exc
    try:
        CORE.owner_file_assertion(fd)
        blocks: list[bytes] = []
        while True:
            block = os.read(fd, 65536)
            if not block:
                break
            blocks.append(block)
        return b"".join(blocks)
    finally:
        os.close(fd)


def read_owner_json(path: Path, *, label: str) -> tuple[dict[str, Any], bytes]:
    data = read_owner_bytes(path, label=label)
    try:
        value = json.loads(data)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GateError(f"owner-only {label} is not JSON") from exc
    if not isinstance(value, dict):
        raise GateError(f"owner-only {label} is not an object")
    return value, data


def verify_manifest(path: Path) -> tuple[dict[str, Any], str]:
    data = path.read_bytes()
    digest = sha256_bytes(data)
    fields = path.with_suffix(".sha256").read_text(encoding="ascii").strip().split()
    if fields != [digest, path.name]:
        raise GateError("post-public manifest sidecar mismatch")
    try:
        manifest = json.loads(data)
    except json.JSONDecodeError as exc:
        raise GateError("post-public manifest is not JSON") from exc
    if not isinstance(manifest, dict):
        raise GateError("post-public manifest is not an object")
    required_top = {
        "authorization_contract", "common_live_model_config", "custody_contract",
        "execution_freshness", "experiment_id", "games", "implementation",
        "launch_gate", "owner_only_evidence", "schema_version", "scope",
        "source_commit", "status", "suite", "treatment_only", "visibility_gate",
    }
    if set(manifest) != required_top:
        raise GateError("post-public manifest top-level shape drift")
    if manifest["schema_version"] != SCHEMA or manifest["experiment_id"] != EXPERIMENT_ID:
        raise GateError("post-public manifest identity drift")
    if manifest["source_commit"] != "1d500edd8eaf651364cfdd8e29638ee540db6062":
        raise GateError("post-public source commit drift")
    if manifest["status"] != "PREPARED_OWNER_AUTHORIZED_POST_PUBLIC_FLIP_GATE_NOT_YET_SATISFIED":
        raise GateError("post-public preparation status drift")

    scope = manifest["scope"]
    if scope != {
        "arm_count": 10, "game_count": 5, "game_order": list(GAMES),
        "pair_count": 5, "pair_order": list(ARMS), "scorecard_retrieval": False,
    }:
        raise GateError("post-public five-game scope drift")
    suite = manifest["suite"]
    expected_suite = {
        "fresh_game_instance_per_arm": True, "fresh_identity_per_arm": True,
        "fresh_process_per_action": True, "game_order": list(GAMES),
        "name": "ARC-V2-FIVE-POSTLAUNCH-LOCAL-CUSTODY",
        "pair_order": list(ARMS), "pairs": 5, "reuse_prior_game_or_session": False,
        "seed": 0,
    }
    if suite != expected_suite:
        raise GateError("post-public ordered suite drift")

    expected_baselines = {
        "ls20": [22, 123, 73, 84, 96, 192, 186],
        "ft09": [43, 12, 23, 28, 65, 37],
        "vc33": [7, 18, 44, 61, 131, 34, 152],
        "ar25": [32, 50, 75, 37, 89, 159, 233, 73],
        "wa30": [71, 119, 183, 98, 368, 68, 79, 442, 415],
    }
    games = manifest["games"]
    if not isinstance(games, list) or [item.get("game_id") for item in games] != list(GAMES):
        raise GateError("post-public game order/count drift")
    for game in games:
        game_id = game["game_id"]
        baseline = expected_baselines[game_id]
        caps = [5 * value for value in baseline]
        if (
            game.get("dry_run_stub") is not False
            or game.get("human_level_baseline_actions") != baseline
            or game.get("action_cap_multiplier") != 5
            or game.get("level_action_caps") != caps
            or game.get("max_actions") != sum(caps)
            or game.get("official_human_actions_total") != sum(baseline)
        ):
            raise GateError(f"post-public {game_id} action schedule drift")

    common = manifest["common_live_model_config"]
    exact_common = {
        "provider": "claude-code", "model": "sonnet", "claude_version": "2.1.234",
        "invocation": "direct-cli-fresh-process-v7", "reasoning_effort": "low",
        "strict_empty_mcp_config": {"mcpServers": {}}, "telemetry": False,
        "temperature": None,
    }
    if any(common.get(key) != value for key, value in exact_common.items()):
        raise GateError("post-public direct Claude Sonnet lane drift")
    for key in (
        "fresh_process_per_action", "no_project_discovery", "no_session_persistence",
        "no_tools", "print_mode", "safe_mode", "same_direct_lane_for_both_arms",
    ):
        if common.get(key) is not True:
            raise GateError(f"post-public Claude isolation drift: {key}")
    treatment = manifest["treatment_only"]
    if (
        treatment.get("trigger_completed_turns") != 2
        or treatment.get("max_skill_invocations_per_game") != 1
        or treatment.get("skill") != "ember"
        or treatment.get("root_model") != "claude-sonnet-5"
        or treatment.get("sub_model") != "claude-sonnet-5"
    ):
        raise GateError("post-public Ember treatment drift")
    if manifest["custody_contract"].get("platform_scorecard_retrieval") is not False:
        raise GateError("post-public scorecard gate drift")
    visibility = manifest["visibility_gate"]
    if (
        visibility.get("repository_full_name") != "kubet/azdaja"
        or visibility.get("required_visibility") != PUBLIC
        or visibility.get("required_private_flag") is not False
        or visibility.get("owner_go_post_flip_marker") != OWNER_GO
        or visibility.get("receipt_max_age_seconds_at_execution") != 600
    ):
        raise GateError("post-public visibility gate drift")
    launch = manifest["launch_gate"]
    if (
        launch.get("post_public_visibility_receipt_bound") is not False
        or launch.get("explicit_owner_go_post_flip_bound") is not False
        or launch.get("repository_must_be_public_at_execution") is not True
        or launch.get("single_vc33_smoke_is_completed_and_not_reused") is not True
    ):
        raise GateError("post-public launch hold drift")
    freshness = manifest["execution_freshness"]
    for key in (
        "action_journals_must_not_preexist", "terminal_receipts_must_not_preexist",
        "paired_receipts_must_not_preexist", "output_must_not_preexist",
        "private_failure_artifact_must_not_preexist",
        "execution_sentinel_created_once_before_first_game_or_model_call",
        "rerun_after_sentinel_refuses",
    ):
        if freshness.get(key) is not True:
            raise GateError(f"post-public freshness drift: {key}")
    if freshness.get("reuse_completed_vc33_smoke_artifacts") is not False:
        raise GateError("completed vc33 smoke reuse is forbidden")

    implementation = manifest["implementation"]
    expected_paths = {
        "core_driver_path": "bench/arc3/driver.py",
        "claude_lane_path": "bench/arc3/claude_lane.py",
        "runner_path": "bench/arc3/arc_v2_post_public.py",
        "binder_path": "bench/arc3/bind_arc_v2_post_public.py",
    }
    repository_root = HERE.parent.parent
    for key, relative in expected_paths.items():
        if implementation.get(key) != relative:
            raise GateError(f"post-public implementation path drift: {key}")
    digest_bindings = {
        "core_driver_sha256": expected_paths["core_driver_path"],
        "claude_lane_sha256": expected_paths["claude_lane_path"],
        "runner_sha256": expected_paths["runner_path"],
        "binder_sha256": expected_paths["binder_path"],
    }
    for key, relative in digest_bindings.items():
        actual = sha256_bytes((repository_root / relative).read_bytes())
        if implementation.get(key) != actual:
            raise GateError(f"post-public implementation digest mismatch: {key}")
    if common.get("driver_sha256") != implementation["core_driver_sha256"]:
        raise GateError("post-public core driver lane binding drift")
    if common.get("lane_wrapper_sha256") != implementation["claude_lane_sha256"]:
        raise GateError("post-public Claude wrapper lane binding drift")
    return manifest, digest


def verify_visibility_receipt(
    path: Path,
    expected_sha256: str,
    manifest: dict[str, Any],
    *,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    value, data = read_owner_json(path, label="GitHub visibility receipt")
    if sha256_bytes(data) != expected_sha256:
        raise GateError("GitHub visibility receipt digest differs from owner approval")
    required = {
        "captured_at_utc", "github_metadata_fields", "github_metadata_sha256",
        "private", "proof_assertion", "receipt_type", "repository_full_name",
        "repository_visibility", "source_request",
    }
    if set(value) != required:
        raise GateError("GitHub visibility receipt shape drift")
    gate = manifest["visibility_gate"]
    if (
        value["receipt_type"] != VISIBILITY_RECEIPT_TYPE
        or value["proof_assertion"] != "GITHUB_REPOSITORY_METADATA_PUBLIC"
        or value["repository_full_name"] != gate["repository_full_name"]
        or value["repository_visibility"] != gate["required_visibility"]
        or value["private"] is not gate["required_private_flag"]
        or value["source_request"] != "GET https://api.github.com/repos/kubet/azdaja"
    ):
        raise GateError("repository visibility proof is not PUBLIC for kubet/azdaja")
    metadata_fields = value["github_metadata_fields"]
    if not isinstance(metadata_fields, dict) or set(metadata_fields) != {
        "archived", "default_branch", "disabled", "html_url", "id", "node_id", "updated_at"
    }:
        raise GateError("GitHub visibility receipt metadata shape drift")
    if (
        type(metadata_fields["id"]) is not int
        or not isinstance(metadata_fields["node_id"], str)
        or metadata_fields["html_url"] != "https://github.com/kubet/azdaja"
        or not isinstance(metadata_fields["default_branch"], str)
        or type(metadata_fields["archived"]) is not bool
        or type(metadata_fields["disabled"]) is not bool
        or not isinstance(metadata_fields["updated_at"], str)
        or not isinstance(value["github_metadata_sha256"], str)
        or not CORE.SHA256.fullmatch(value["github_metadata_sha256"])
    ):
        raise GateError("GitHub visibility receipt metadata is invalid")
    current = (now or utc_now()).astimezone(dt.timezone.utc)
    captured = parse_utc(value["captured_at_utc"], label="visibility receipt captured_at_utc")
    age = (current - captured).total_seconds()
    if age > gate["receipt_max_age_seconds_at_execution"]:
        raise GateError("GitHub PUBLIC visibility receipt is stale at execution")
    if age < -gate["maximum_future_clock_skew_seconds"]:
        raise GateError("GitHub PUBLIC visibility receipt is from the future")
    return value


def expected_artifact_basenames(manifest: dict[str, Any]) -> dict[str, str]:
    freshness = manifest["execution_freshness"]
    prefix = freshness["artifact_prefix"]
    values = {
        "output": freshness["output_filename"],
        "private failure artifact": freshness["direct_claude_failure_artifact_filename"],
        "execution sentinel": freshness["execution_sentinel_filename"],
        "suite terminal receipt": freshness["suite_terminal_receipt_filename"],
    }
    for game_id in GAMES:
        for arm in ARMS:
            values[f"{game_id} {arm} action journal"] = f"{prefix}.{game_id}.{arm}.actions.jsonl"
            values[f"{game_id} {arm} terminal receipt"] = f"{prefix}.{game_id}.{arm}.arm-terminal-receipt.json"
        values[f"{game_id} paired receipt"] = f"{prefix}.{game_id}.paired-terminal-receipt.json"
    return values


def authorization_gate(
    authorization_path: Path,
    visibility_receipt_path: Path,
    manifest: dict[str, Any],
    manifest_sha256: str,
    *,
    output_path: Path,
    failure_artifact_path: Path,
    now: dt.datetime | None = None,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    value, authorization_data = read_owner_json(authorization_path, label="post-public owner approval")
    if set(value) != set(manifest["authorization_contract"]["required_fields"]):
        raise GateError("post-public owner approval shape drift")
    if (
        value["approval_type"] != APPROVAL_TYPE
        or value["authorization_id"] != "ARC-V2-FIVE-POSTLAUNCH-OWNER-GO-V1"
        or value["experiment_id"] != manifest["experiment_id"]
        or value["manifest_sha256"] != manifest_sha256
        or value["output_identity"] != manifest["execution_freshness"]["output_identity"]
        or value["game_count"] != 5
        or value["game_order"] != list(GAMES)
        or value["pair_count"] != 5
        or value["pair_order"] != list(ARMS)
        or value["repository_full_name"] != "kubet/azdaja"
        or value["required_repository_visibility"] != PUBLIC
        or value["owner_go_post_public_flip_marker"] != OWNER_GO
        or value["full_five_game_rerun_authorized"] is not True
        or value["arc_live_owner_authorized"] is not True
        or value["separate_arc_claude_lane_owner_authorized"] is not True
    ):
        raise GateError("explicit owner GO/post-public full-run authorization is absent")
    parse_utc(value["authorized_at_utc"], label="owner approval authorized_at_utc")
    if Path(value["github_visibility_receipt_path"]) != visibility_receipt_path:
        raise GateError("owner approval visibility receipt path differs from execution")
    if not visibility_receipt_path.is_absolute():
        raise GateError("GitHub visibility receipt path must be absolute")
    visibility = verify_visibility_receipt(
        visibility_receipt_path, value["github_visibility_receipt_sha256"], manifest, now=now
    )

    if set(value["action_journal_paths"]) != set(GAMES):
        raise GateError("action journal game binding drift")
    if set(value["terminal_receipt_paths"]) != set(GAMES):
        raise GateError("terminal receipt game binding drift")
    if set(value["paired_receipt_paths"]) != set(GAMES):
        raise GateError("paired receipt game binding drift")
    raw_paths: dict[str, Any] = {
        "output": value["output_path"],
        "private failure artifact": value["direct_claude_failure_artifact_path"],
        "execution sentinel": value["execution_sentinel_path"],
        "suite terminal receipt": value["suite_terminal_receipt_path"],
    }
    for game_id in GAMES:
        if set(value["action_journal_paths"][game_id]) != set(ARMS):
            raise GateError(f"{game_id} action journal arm binding drift")
        if set(value["terminal_receipt_paths"][game_id]) != set(ARMS):
            raise GateError(f"{game_id} terminal receipt arm binding drift")
        for arm in ARMS:
            raw_paths[f"{game_id} {arm} action journal"] = value["action_journal_paths"][game_id][arm]
            raw_paths[f"{game_id} {arm} terminal receipt"] = value["terminal_receipt_paths"][game_id][arm]
        raw_paths[f"{game_id} paired receipt"] = value["paired_receipt_paths"][game_id]
    expected_names = expected_artifact_basenames(manifest)
    bound: dict[str, Path] = {}
    for label, raw in raw_paths.items():
        if not isinstance(raw, str):
            raise GateError(f"{label} path is not a string")
        path = Path(raw)
        if not path.is_absolute() or path.exists():
            raise GateError(f"{label} path must be absolute and fresh")
        if path.name != expected_names[label]:
            raise GateError(f"{label} fresh identity drift")
        if not path.parent.is_dir():
            raise GateError(f"{label} parent directory is missing")
        bound[label] = path
    if len(set(bound.values())) != len(bound):
        raise GateError("post-public execution artifact paths must be distinct")
    if output_path != bound["output"] or failure_artifact_path != bound["private failure artifact"]:
        raise GateError("post-public CLI artifact paths differ from owner approval")
    if visibility_receipt_path in set(bound.values()) or authorization_path in set(bound.values()):
        raise GateError("proof/approval paths collide with execution artifacts")
    return value, visibility, sha256_bytes(authorization_data)


@contextlib.contextmanager
def custody_game_scope(game_id: str) -> Iterator[None]:
    """Reuse the sealed ARC-v2 journal/arm-receipt implementation for one game."""
    if game_id not in GAMES:
        raise GateError("post-public custody game is outside the frozen suite")
    original = CORE.ARC_V2_GAME
    CORE.ARC_V2_GAME = game_id
    try:
        yield
    finally:
        CORE.ARC_V2_GAME = original


def paired_terminal_receipt(
    rows: list[dict[str, Any]],
    *,
    game_id: str,
    manifest: dict[str, Any],
    manifest_sha256: str,
    terminal_paths: dict[str, Path],
) -> dict[str, Any]:
    if [row.get("arm") for row in rows] != list(ARMS) or any(row.get("game_id") != game_id for row in rows):
        raise GateError(f"{game_id} pair is not baseline then ember")
    baseline, ember = rows
    if (
        baseline["common_model_config_sha256"] != ember["common_model_config_sha256"]
        or baseline["action_cap"] != ember["action_cap"]
    ):
        raise GateError(f"{game_id} paired lane or action cap differs")
    delta = ember["shadow_rhae_fraction"] - baseline["shadow_rhae_fraction"]
    if not all(math.isfinite(value) for value in (
        baseline["shadow_rhae_fraction"], ember["shadow_rhae_fraction"], delta
    )):
        raise GateError(f"{game_id} pair contains non-finite shadow RHAE")
    return {
        "receipt_type": "ARC_V2_POST_PUBLIC_PAIRED_TERMINAL_RECEIPT_V1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": manifest_sha256,
        "game_id": game_id,
        "pair_order": list(ARMS),
        "arms": [
            {
                "arm": row["arm"],
                "absolute_shadow_rhae": row["shadow_rhae_fraction"],
                "terminal_receipt_path": str(terminal_paths[row["arm"]]),
                "terminal_receipt_sha256": row["terminal_receipt"]["sha256"],
            }
            for row in rows
        ],
        "ember_minus_baseline_absolute_shadow_rhae_delta": delta,
        "platform_scorecard_retrieved": False,
        "full_five_game_rerun": "PAIR_TERMINAL",
    }


def run_five(
    manifest: dict[str, Any],
    manifest_sha256: str,
    authorization: dict[str, Any],
    *,
    args: argparse.Namespace,
    api_key: str,
    visibility_receipt_sha256: str,
    execution_sentinel_sha256: str,
) -> dict[str, Any]:
    if manifest["suite"]["game_order"] != list(GAMES) or manifest["suite"]["pair_order"] != list(ARMS):
        raise GateError("post-public runtime order drift")
    failure_artifact = Path(authorization["direct_claude_failure_artifact_path"])
    rows: list[dict[str, Any]] = []
    pair_bindings: list[dict[str, Any]] = []
    cleanup_proofs: list[bool] = []
    isolation_values = {key: set() for key in ("HOME", "JCODE_HOME", "JCODE_RUNTIME_DIR", "AZDAJA_HOME")}
    for game_id in GAMES:
        game_config = CORE.manifest_game(manifest, game_id)
        pair_rows: list[dict[str, Any]] = []
        for arm in ARMS:
            work = Path(tempfile.mkdtemp(prefix=f"arc-v2-five-postlaunch-{game_id}-{arm}-"))
            try:
                run_root = work / "run"
                run_root.mkdir(mode=CORE.DIRECTORY_MODE)
                env = CORE.safe_env(
                    work / "home", reasoning=manifest["common_live_model_config"]["reasoning_effort"]
                )
                env["PATH"] = str(args.claude.parent) + os.pathsep + os.defpath
                Path(env["HOME"]).mkdir(mode=CORE.DIRECTORY_MODE)
                for key in isolation_values:
                    if env[key] in isolation_values[key]:
                        raise GateError(f"isolated {key} was reused")
                    isolation_values[key].add(env[key])
                claude_runtime = work / "claude-runtime"
                claude_runtime.mkdir(mode=CORE.DIRECTORY_MODE)
                model = CORE.LiveClaudeModel(
                    args.claude, manifest["common_live_model_config"], args.owner_home,
                    claude_runtime, env, failure_artifact,
                )
                skill = None
                if arm == "ember":
                    command = CORE.direct_claude_subcall_command(
                        args.claude, args.owner_home, claude_runtime, failure_artifact
                    )
                    staged = CORE.stage_ember_skill(
                        args.ember_bundle, env, manifest["treatment_only"], direct_lane_command=command
                    )
                    expected = manifest["treatment_only"]["binary_sha256_by_platform"][CORE.platform_key()]
                    skill = CORE.LiveAzdajaSkill(staged, manifest["treatment_only"], expected, env)
                game = CORE.LiveArcadeGame(game_id, api_key)
                journal_path = Path(authorization["action_journal_paths"][game_id][arm])
                terminal_path = Path(authorization["terminal_receipt_paths"][game_id][arm])
                with custody_game_scope(game_id):
                    row = CORE.run_arm(
                        arm=arm, game_id=game_id, game_config=game_config,
                        common_config=manifest["common_live_model_config"],
                        treatment_config=manifest["treatment_only"], game=game,
                        model=model, skill=skill, root=run_root,
                        action_journal_path=journal_path,
                        terminal_receipt_path=terminal_path,
                        terminal_receipt_context={
                            "experiment_id": manifest["experiment_id"],
                            "manifest_sha256": manifest_sha256,
                        },
                    )
                rows.append(row)
                pair_rows.append(row)
            finally:
                shutil.rmtree(work, ignore_errors=False)
                cleanup_proofs.append(not work.exists())
        if [row["arm"] for row in pair_rows] != list(ARMS):
            raise GateError(f"{game_id} did not complete baseline then ember")
        terminal_paths = {
            arm: Path(authorization["terminal_receipt_paths"][game_id][arm]) for arm in ARMS
        }
        pair_value = paired_terminal_receipt(
            pair_rows, game_id=game_id, manifest=manifest,
            manifest_sha256=manifest_sha256, terminal_paths=terminal_paths,
        )
        pair_path = Path(authorization["paired_receipt_paths"][game_id])
        pair_sha256, pair_bytes = CORE.write_owner_json(
            pair_path, pair_value, label=f"{game_id} paired terminal receipt"
        )
        pair_bindings.append({
            "game_id": game_id,
            "paired_terminal_receipt_path": str(pair_path),
            "paired_terminal_receipt_sha256": pair_sha256,
            "paired_terminal_receipt_bytes": pair_bytes,
            "baseline_absolute_shadow_rhae": pair_rows[0]["shadow_rhae_fraction"],
            "ember_absolute_shadow_rhae": pair_rows[1]["shadow_rhae_fraction"],
            "ember_minus_baseline_absolute_shadow_rhae_delta": (
                pair_rows[1]["shadow_rhae_fraction"] - pair_rows[0]["shadow_rhae_fraction"]
            ),
        })
    if (
        len(rows) != 10
        or [(row["game_id"], row["arm"]) for row in rows]
        != [(game_id, arm) for game_id in GAMES for arm in ARMS]
        or len(cleanup_proofs) != 10
        or not all(cleanup_proofs)
    ):
        raise GateError("post-public exact five-pair completion/cleanup gate failed")
    suite_receipt = {
        "receipt_type": "ARC_V2_FIVE_POST_PUBLIC_SUITE_TERMINAL_RECEIPT_V1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": manifest_sha256,
        "game_order": list(GAMES),
        "pair_order_per_game": list(ARMS),
        "game_count": 5,
        "pair_count": 5,
        "arm_count": 10,
        "pairs": pair_bindings,
        "execution_sentinel_path": authorization["execution_sentinel_path"],
        "execution_sentinel_sha256": execution_sentinel_sha256,
        "github_visibility_receipt_path": authorization["github_visibility_receipt_path"],
        "github_visibility_receipt_sha256": visibility_receipt_sha256,
        "repository_visibility_at_execution_gate": PUBLIC,
        "platform_scorecard_retrieved": False,
        "termination_reason": "ALL_FIVE_ORDERED_PAIRS_TERMINAL",
    }
    suite_path = Path(authorization["suite_terminal_receipt_path"])
    suite_sha256, suite_bytes = CORE.write_owner_json(
        suite_path, suite_receipt, label="five-game suite terminal receipt"
    )
    return {
        "identity": manifest["execution_freshness"]["output_identity"],
        "mode": "owner_only_local_custody_post_public",
        "game_order": list(GAMES),
        "pair_order_per_game": list(ARMS),
        "game_count": 5,
        "pair_count": 5,
        "arm_count": 10,
        "public_output_emitted": False,
        "platform_scorecard_retrieved": False,
        "repository_visibility_at_execution_gate": PUBLIC,
        "suite_terminal_receipt": {
            "path": str(suite_path), "sha256": suite_sha256, "bytes": suite_bytes,
        },
        "execution_sentinel": {
            "path": authorization["execution_sentinel_path"],
            "sha256": execution_sentinel_sha256,
        },
    }


def execute_live(args: argparse.Namespace, *, now: dt.datetime | None = None) -> dict[str, Any]:
    manifest, manifest_sha256 = verify_manifest(args.manifest)
    if args.authorization is None or args.visibility_receipt is None:
        raise GateError("live mode requires owner approval and GitHub visibility receipt")
    if args.output is None or args.direct_claude_failure_artifact is None:
        raise GateError("live mode requires output and private failure artifact paths")
    authorization, visibility, authorization_sha256 = authorization_gate(
        args.authorization, args.visibility_receipt, manifest, manifest_sha256,
        output_path=args.output, failure_artifact_path=args.direct_claude_failure_artifact,
        now=now,
    )
    api_key = os.environ.get("ARC_API_KEY")
    if not api_key:
        raise GateError("ARC_API_KEY is absent")
    if args.claude is None or args.ember_bundle is None:
        raise GateError("live mode requires --claude and --ember-bundle")
    preflight_manifest = dict(manifest)
    preflight_manifest["schema_version"] = CORE.ARC_V2_SCHEMA
    CORE.provider_free_live_artifact_preflight(
        args.claude, args.ember_bundle, preflight_manifest, owner_home=args.owner_home
    )
    # Recheck PUBLIC receipt freshness and every still-fresh artifact immediately
    # before consuming the exactly-once sentinel. No ARC game/model call precedes it.
    authorization, visibility, authorization_sha256 = authorization_gate(
        args.authorization, args.visibility_receipt, manifest, manifest_sha256,
        output_path=args.output, failure_artifact_path=args.direct_claude_failure_artifact,
        now=now,
    )
    sentinel_path = Path(authorization["execution_sentinel_path"])
    sentinel = {
        "receipt_type": EXECUTION_SENTINEL_TYPE,
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": manifest_sha256,
        "authorization_path": str(args.authorization),
        "authorization_sha256": authorization_sha256,
        "github_visibility_receipt_path": str(args.visibility_receipt),
        "github_visibility_receipt_sha256": authorization["github_visibility_receipt_sha256"],
        "repository_visibility_at_execution_gate": visibility["repository_visibility"],
        "owner_go_post_public_flip_marker": authorization["owner_go_post_public_flip_marker"],
        "consumed_at_utc": iso_utc((now or utc_now()).astimezone(dt.timezone.utc)),
        "game_order": list(GAMES),
        "pair_order_per_game": list(ARMS),
        "arc_game_or_model_calls_before_sentinel": 0,
        "rerun_permitted": False,
    }
    sentinel_sha256, _ = CORE.write_owner_json(
        sentinel_path, sentinel, label="exactly-once execution sentinel"
    )
    result = run_five(
        manifest, manifest_sha256, authorization, args=args, api_key=api_key,
        visibility_receipt_sha256=authorization["github_visibility_receipt_sha256"],
        execution_sentinel_sha256=sentinel_sha256,
    )
    CORE.write_output(args.output, result)
    return result


def preflight_value(manifest: dict[str, Any], manifest_sha256: str) -> dict[str, Any]:
    return {
        "status": "PREPARED_NOT_EXECUTED",
        "manifest_sha256": manifest_sha256,
        "game_order": list(GAMES),
        "pair_order_per_game": list(ARMS),
        "game_count": 5,
        "pair_count": 5,
        "arm_count": 10,
        "required_repository_visibility_at_execution": PUBLIC,
        "explicit_owner_go_marker_required": OWNER_GO,
        "provider_game_model_calls": 0,
        "platform_scorecard_retrieval": False,
        "completed_vc33_smoke_reused": False,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ARC-v2 five-game post-public exactly-once runner")
    parser.add_argument("mode", choices=("preflight", "live"))
    parser.add_argument("--manifest", type=Path, default=HERE / "arc-v2-five-postlaunch-manifest.json")
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--visibility-receipt", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--direct-claude-failure-artifact", type=Path)
    parser.add_argument("--claude", type=Path)
    parser.add_argument("--ember-bundle", type=Path)
    parser.add_argument("--owner-home", type=Path, default=Path.home())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.mode == "preflight":
            manifest, digest = verify_manifest(args.manifest)
            CORE.write_output(args.output, preflight_value(manifest, digest))
        else:
            execute_live(args)
        return 0
    except (GateError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
