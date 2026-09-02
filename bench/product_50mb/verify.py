#!/usr/bin/env python3
"""Fail-closed verification for a product_50mb acceptance receipt."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import reproduce

ROOT = Path(__file__).resolve().parents[2]
RECEIPT_KEYS = {
    "schema",
    "artifact",
    "generated_at_utc",
    "source",
    "environment",
    "commands",
    "binary",
    "log",
    "scenarios",
    "summary",
    "claim_boundary",
}


def require_exact_keys(value: object, keys: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label}: schema keys mismatch")
    return value


def validate_source_manifest(
    manifest: object, root: Path, expected_paths: list[str] | None = None
) -> None:
    if not isinstance(manifest, list):
        raise ValueError("source files must be a list")
    expected = expected_paths if expected_paths is not None else reproduce.expected_source_paths(root)
    if len(manifest) != len(expected):
        raise ValueError("source manifest length mismatch")
    names: list[str] = []
    for row in manifest:
        entry = require_exact_keys(row, {"path", "bytes", "sha256"}, "source file")
        name = entry["path"]
        if not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts:
            raise ValueError("unsafe source path")
        names.append(name)
        path = root / name
        if not path.is_file():
            raise ValueError(f"missing source file: {name}")
        if entry["bytes"] != path.stat().st_size:
            raise ValueError(f"source size mismatch: {name}")
        if not reproduce.is_sha256(entry["sha256"]) or reproduce.sha256(path) != entry["sha256"]:
            raise ValueError(f"source hash mismatch: {name}")
    if names != expected:
        raise ValueError("source manifest paths or ordering mismatch")


def validate_command_records(commands: object) -> None:
    if not isinstance(commands, list) or len(commands) != 2:
        raise ValueError("expected exactly two command records")
    expected = [
        (reproduce.BUILD_CMD, {}),
        (reproduce.TEST_CMD, reproduce.TEST_ENV),
    ]
    for index, (record, (argv, env)) in enumerate(zip(commands, expected)):
        command = require_exact_keys(
            record,
            {"argv", "env", "exit_code", "elapsed_seconds", "output_sha256"},
            f"command {index}",
        )
        if command["argv"] != argv or command["env"] != env:
            raise ValueError(f"command {index}: invocation mismatch")
        if command["exit_code"] != 0:
            raise ValueError(f"command {index}: nonzero exit code")
        elapsed = command["elapsed_seconds"]
        if not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool) or elapsed < 0:
            raise ValueError(f"command {index}: invalid elapsed time")
        if not reproduce.is_sha256(command["output_sha256"]):
            raise ValueError(f"command {index}: invalid output hash")


def validate_file_artifact(value: object, label: str) -> dict[str, object]:
    artifact = require_exact_keys(value, {"path", "bytes", "sha256"}, label)
    if not isinstance(artifact["path"], str) or not artifact["path"]:
        raise ValueError(f"{label}: invalid path")
    if not isinstance(artifact["bytes"], int) or isinstance(artifact["bytes"], bool) or artifact["bytes"] <= 0:
        raise ValueError(f"{label}: invalid byte count")
    if not reproduce.is_sha256(artifact["sha256"]):
        raise ValueError(f"{label}: invalid hash")
    return artifact


def validate_log_contents(
    path: Path, artifact: dict[str, object], commands: list[dict[str, object]]
) -> None:
    data = path.read_bytes()
    for marker in (b"/Users/", b"/home/", b"\\Users\\"):
        if marker in data:
            raise ValueError("captured log contains a host user path")
    if len(data) != artifact["bytes"]:
        raise ValueError("log size mismatch")
    if reproduce.sha256_bytes(data) != artifact["sha256"]:
        raise ValueError("log hash mismatch")
    if not data.startswith(reproduce.BUILD_LOG_HEADER):
        raise ValueError("log build header mismatch")
    remainder = data[len(reproduce.BUILD_LOG_HEADER) :]
    build_output, separator, test_output = remainder.partition(reproduce.TEST_LOG_HEADER)
    if separator != reproduce.TEST_LOG_HEADER:
        raise ValueError("log test header mismatch")
    if reproduce.sha256_bytes(build_output) != commands[0]["output_sha256"]:
        raise ValueError("build output hash disagrees with log")
    if reproduce.sha256_bytes(test_output) != commands[1]["output_sha256"]:
        raise ValueError("test output hash disagrees with log")


def validate_receipt(
    receipt: object,
    root: Path = ROOT,
    binary_path: Path | None = None,
    log_path: Path | None = None,
    require_binary: bool = False,
    require_log: bool = False,
) -> dict[str, bool]:
    data = require_exact_keys(receipt, RECEIPT_KEYS, "receipt")
    if data["schema"] != reproduce.SCHEMA or data["artifact"] != reproduce.ARTIFACT:
        raise ValueError("wrong receipt schema or artifact")
    if not isinstance(data["generated_at_utc"], str):
        raise ValueError("missing generation timestamp")
    try:
        parsed_time = dt.datetime.fromisoformat(data["generated_at_utc"].replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("invalid generation timestamp") from error
    if parsed_time.tzinfo is None:
        raise ValueError("generation timestamp lacks a timezone")

    source = require_exact_keys(data["source"], {"commit", "tracked_diff_clean", "files"}, "source")
    commit = source["commit"]
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("invalid source commit")
    if source["tracked_diff_clean"] is not True:
        raise ValueError("receipt was not generated from a tracked-clean tree")
    validate_source_manifest(source["files"], root)
    commit_check = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if commit_check.returncode != 0:
        raise ValueError("source commit is unavailable")
    bound_paths = [entry["path"] for entry in source["files"]]
    diff_check = subprocess.run(
        ["git", "diff", "--quiet", commit, "--", *bound_paths],
        cwd=root,
        check=False,
    )
    if diff_check.returncode != 0:
        raise ValueError("bound source differs from the recorded source commit")

    environment = require_exact_keys(
        data["environment"], {"platform", "machine", "python", "rustc", "cargo"}, "environment"
    )
    if any(not isinstance(environment[key], str) or not environment[key] for key in environment):
        raise ValueError("invalid environment record")
    validate_command_records(data["commands"])
    if not isinstance(data["scenarios"], list) or not isinstance(data["summary"], dict):
        raise ValueError("scenario records have the wrong type")
    reproduce.validate_records([*data["scenarios"], data["summary"]])

    boundary = require_exact_keys(
        data["claim_boundary"], {"demonstrates", "does_not_demonstrate"}, "claim boundary"
    )
    if boundary["demonstrates"] != reproduce.DEMONSTRATED:
        raise ValueError("demonstrated-claim boundary mismatch")
    if boundary["does_not_demonstrate"] != reproduce.NOT_DEMONSTRATED:
        raise ValueError("not-demonstrated claim boundary mismatch")

    binary = validate_file_artifact(data["binary"], "binary")
    log = validate_file_artifact(data["log"], "log")
    checks = {"source": True, "binary": False, "log": False}
    if binary_path is not None:
        if not binary_path.is_file() or binary_path.stat().st_size != binary["bytes"]:
            raise ValueError("binary size mismatch")
        if reproduce.sha256(binary_path) != binary["sha256"]:
            raise ValueError("binary hash mismatch")
        checks["binary"] = True
    elif require_binary:
        raise ValueError("binary verification was required but no binary path was supplied")
    if log_path is not None:
        if not log_path.is_file():
            raise ValueError("log is missing")
        validate_log_contents(log_path, log, data["commands"])
        checks["log"] = True
    elif require_log:
        raise ValueError("log verification was required but no log path was supplied")
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--require-binary", action="store_true")
    parser.add_argument("--require-log", action="store_true")
    args = parser.parse_args()
    try:
        receipt = json.loads(args.receipt.read_text())
        checks = validate_receipt(
            receipt,
            binary_path=args.binary,
            log_path=args.log,
            require_binary=args.require_binary,
            require_log=args.require_log,
        )
    except (OSError, ValueError, TypeError, KeyError, AttributeError, json.JSONDecodeError) as error:
        print(f"verification failed: {error}", file=sys.stderr)
        return 1
    checked = ", ".join(name for name, passed in checks.items() if passed)
    unchecked = ", ".join(name for name, passed in checks.items() if not passed)
    print(f"verified: {checked}")
    if unchecked:
        print(f"not checked because no path was supplied: {unchecked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
