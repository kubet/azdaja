#!/usr/bin/env python3
"""Bind a fresh post-flip GitHub PUBLIC receipt to the owner GO approval.

This program performs no network, ARC, game, model, provider, or scorecard call.
The owner first captures ``gh api repos/kubet/azdaja`` to a 0600 file, then
passes that exact response here with the explicit post-public GO marker.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
RUNNER_SPEC = importlib.util.spec_from_file_location("arc_v2_post_public_binder_runner", HERE / "arc_v2_post_public.py")
assert RUNNER_SPEC and RUNNER_SPEC.loader
RUNNER = importlib.util.module_from_spec(RUNNER_SPEC)
sys.modules[RUNNER_SPEC.name] = RUNNER
RUNNER_SPEC.loader.exec_module(RUNNER)

GateError = RUNNER.GateError


def github_public_receipt(metadata_data: bytes, *, captured_at: dt.datetime) -> dict[str, Any]:
    try:
        metadata = json.loads(metadata_data)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GateError("captured GitHub metadata is not JSON") from exc
    if not isinstance(metadata, dict):
        raise GateError("captured GitHub metadata is not an object")
    if (
        metadata.get("full_name") != "kubet/azdaja"
        or metadata.get("visibility") != "public"
        or metadata.get("private") is not False
        or metadata.get("html_url") != "https://github.com/kubet/azdaja"
    ):
        raise GateError("captured GitHub metadata does not prove kubet/azdaja PUBLIC")
    required_types = (
        type(metadata.get("id")) is int,
        isinstance(metadata.get("node_id"), str),
        isinstance(metadata.get("default_branch"), str),
        type(metadata.get("archived")) is bool,
        type(metadata.get("disabled")) is bool,
        isinstance(metadata.get("updated_at"), str),
    )
    if not all(required_types):
        raise GateError("captured GitHub repository identity fields are incomplete")
    return {
        "receipt_type": RUNNER.VISIBILITY_RECEIPT_TYPE,
        "captured_at_utc": RUNNER.iso_utc(captured_at),
        "source_request": "GET https://api.github.com/repos/kubet/azdaja",
        "repository_full_name": "kubet/azdaja",
        "repository_visibility": RUNNER.PUBLIC,
        "private": False,
        "proof_assertion": "GITHUB_REPOSITORY_METADATA_PUBLIC",
        "github_metadata_sha256": RUNNER.sha256_bytes(metadata_data),
        "github_metadata_fields": {
            "id": metadata["id"],
            "node_id": metadata["node_id"],
            "html_url": metadata["html_url"],
            "default_branch": metadata["default_branch"],
            "archived": metadata["archived"],
            "disabled": metadata["disabled"],
            "updated_at": metadata["updated_at"],
        },
    }


def artifact_paths(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    freshness = manifest["execution_freshness"]
    prefix = freshness["artifact_prefix"]
    journals = {
        game_id: {
            arm: str(root / f"{prefix}.{game_id}.{arm}.actions.jsonl")
            for arm in RUNNER.ARMS
        }
        for game_id in RUNNER.GAMES
    }
    terminal = {
        game_id: {
            arm: str(root / f"{prefix}.{game_id}.{arm}.arm-terminal-receipt.json")
            for arm in RUNNER.ARMS
        }
        for game_id in RUNNER.GAMES
    }
    paired = {
        game_id: str(root / f"{prefix}.{game_id}.paired-terminal-receipt.json")
        for game_id in RUNNER.GAMES
    }
    return {
        "action_journal_paths": journals,
        "terminal_receipt_paths": terminal,
        "paired_receipt_paths": paired,
        "output_path": str(root / freshness["output_filename"]),
        "direct_claude_failure_artifact_path": str(
            root / freshness["direct_claude_failure_artifact_filename"]
        ),
        "execution_sentinel_path": str(root / freshness["execution_sentinel_filename"]),
        "suite_terminal_receipt_path": str(root / freshness["suite_terminal_receipt_filename"]),
    }


def bind(
    *,
    manifest_path: Path,
    github_metadata_path: Path,
    visibility_receipt_path: Path,
    authorization_path: Path,
    artifact_root: Path,
    owner_go: str,
    now: dt.datetime | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest, manifest_sha256 = RUNNER.verify_manifest(manifest_path)
    if owner_go != RUNNER.OWNER_GO:
        raise GateError("explicit owner GO/post-flip marker is absent")
    if not artifact_root.is_absolute() or not artifact_root.is_dir():
        raise GateError("artifact root must be an existing absolute directory")
    if (
        not visibility_receipt_path.is_absolute()
        or visibility_receipt_path.name != manifest["execution_freshness"]["visibility_receipt_filename"]
        or not visibility_receipt_path.parent.is_dir()
        or visibility_receipt_path.exists()
    ):
        raise GateError("visibility receipt path must have its fresh absolute identity")
    if (
        not authorization_path.is_absolute()
        or authorization_path.name != manifest["execution_freshness"]["authorization_filename"]
        or not authorization_path.parent.is_dir()
        or authorization_path.exists()
    ):
        raise GateError("authorization path must have its fresh absolute identity")
    if visibility_receipt_path == authorization_path:
        raise GateError("visibility receipt and authorization paths must differ")
    metadata_data = RUNNER.read_owner_bytes(github_metadata_path, label="captured GitHub metadata")
    captured_at = (now or RUNNER.utc_now()).astimezone(dt.timezone.utc)
    receipt = github_public_receipt(metadata_data, captured_at=captured_at)
    paths = artifact_paths(manifest, artifact_root)
    prospective: list[Path] = [
        Path(paths["output_path"]), Path(paths["direct_claude_failure_artifact_path"]),
        Path(paths["execution_sentinel_path"]), Path(paths["suite_terminal_receipt_path"]),
    ]
    for game_id in RUNNER.GAMES:
        prospective.append(Path(paths["paired_receipt_paths"][game_id]))
        for arm in RUNNER.ARMS:
            prospective.append(Path(paths["action_journal_paths"][game_id][arm]))
            prospective.append(Path(paths["terminal_receipt_paths"][game_id][arm]))
    if len(set(prospective)) != len(prospective) or any(path.exists() for path in prospective):
        raise GateError("one or more post-public execution paths are not fresh and distinct")
    receipt_sha256, _ = RUNNER.CORE.write_owner_json(
        visibility_receipt_path, receipt, label="GitHub PUBLIC visibility receipt"
    )
    approval = {
        "approval_type": RUNNER.APPROVAL_TYPE,
        "authorization_id": "ARC-V2-FIVE-POSTLAUNCH-OWNER-GO-V1",
        "authorized_at_utc": RUNNER.iso_utc(captured_at),
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": manifest_sha256,
        "output_identity": manifest["execution_freshness"]["output_identity"],
        "repository_full_name": "kubet/azdaja",
        "required_repository_visibility": RUNNER.PUBLIC,
        "github_visibility_receipt_path": str(visibility_receipt_path),
        "github_visibility_receipt_sha256": receipt_sha256,
        "owner_go_post_public_flip_marker": owner_go,
        "full_five_game_rerun_authorized": True,
        "arc_live_owner_authorized": True,
        "separate_arc_claude_lane_owner_authorized": True,
        "game_count": 5,
        "game_order": list(RUNNER.GAMES),
        "pair_count": 5,
        "pair_order": list(RUNNER.ARMS),
        **paths,
    }
    RUNNER.CORE.write_owner_json(
        authorization_path, approval, label="post-public owner approval"
    )
    return receipt, approval


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bind GitHub PUBLIC proof to ARC-v2 owner GO")
    parser.add_argument("--manifest", type=Path, default=HERE / "arc-v2-five-postlaunch-manifest.json")
    parser.add_argument("--github-metadata", required=True, type=Path)
    parser.add_argument("--visibility-receipt", required=True, type=Path)
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--owner-go", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        _, approval = bind(
            manifest_path=args.manifest,
            github_metadata_path=args.github_metadata,
            visibility_receipt_path=args.visibility_receipt,
            authorization_path=args.authorization,
            artifact_root=args.artifact_root,
            owner_go=args.owner_go,
        )
        print(json.dumps({
            "status": "BOUND_NOT_EXECUTED",
            "authorization": str(args.authorization),
            "visibility_receipt": str(args.visibility_receipt),
            "output": approval["output_path"],
            "execution_sentinel": approval["execution_sentinel_path"],
        }, sort_keys=True))
        return 0
    except (GateError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
