#!/usr/bin/env python3
"""Fail-closed verifier for live Claude Fable repository smoke receipts."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("live_fable_repo_verify_run", HERE / "run.py")
harness = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(harness)

ROOT = Path(__file__).resolve().parents[2]
RECEIPT_KEYS = {
    "schema",
    "artifact",
    "generated_at_utc",
    "source",
    "environment",
    "model",
    "route",
    "commands",
    "fixture",
    "binary",
    "transport",
    "prompt",
    "model_response",
    "result",
    "runtime",
    "checks",
    "timings",
    "limits",
}


def exact_dict(value: object, keys: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label}: schema keys mismatch")
    return value


def positive_number(value: object, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{label}: expected a positive number")


def validate_source_manifest(manifest: object, root: Path = ROOT) -> None:
    if not isinstance(manifest, list):
        raise ValueError("source manifest must be a list")
    expected = harness.source_paths(root)
    if len(manifest) != len(expected):
        raise ValueError("source manifest length mismatch")
    names: list[str] = []
    for value in manifest:
        entry = exact_dict(value, {"path", "bytes", "sha256"}, "source file")
        name = entry["path"]
        if not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts:
            raise ValueError("unsafe source path")
        names.append(name)
        path = root / name
        if not path.is_file():
            raise ValueError(f"missing source file: {name}")
        if entry["bytes"] != path.stat().st_size:
            raise ValueError(f"source size mismatch: {name}")
        if not harness.is_sha256(entry["sha256"]) or entry["sha256"] != harness.sha256(path):
            raise ValueError(f"source hash mismatch: {name}")
    if names != expected:
        raise ValueError("source paths or ordering mismatch")


def validate_command(value: object, label: str) -> dict[str, object]:
    command = exact_dict(
        value,
        {"argv", "env", "elapsed_seconds", "exit_code", "output_sha256"},
        label,
    )
    if not isinstance(command["argv"], list) or not all(
        isinstance(part, str) for part in command["argv"]
    ):
        raise ValueError(f"{label}: invalid argv")
    if not isinstance(command["env"], dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in command["env"].items()
    ):
        raise ValueError(f"{label}: invalid environment")
    if command["exit_code"] != 0:
        raise ValueError(f"{label}: nonzero exit code")
    positive_number(command["elapsed_seconds"], f"{label} elapsed time")
    if not harness.is_sha256(command["output_sha256"]):
        raise ValueError(f"{label}: invalid output hash")
    return command


def validate_receipt(
    receipt: object, root: Path = ROOT, binary_path: Path | None = None
) -> dict[str, bool]:
    data = exact_dict(receipt, RECEIPT_KEYS, "receipt")
    if data["schema"] != harness.SCHEMA or data["artifact"] != harness.ARTIFACT:
        raise ValueError("wrong receipt schema or artifact")
    if not isinstance(data["generated_at_utc"], str):
        raise ValueError("missing generation timestamp")
    parsed = dt.datetime.fromisoformat(data["generated_at_utc"].replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("generation timestamp lacks timezone")

    source = exact_dict(data["source"], {"commit", "tracked_clean", "files"}, "source")
    commit = source["commit"]
    if not isinstance(commit, str) or len(commit) != 40 or any(
        character not in "0123456789abcdef" for character in commit
    ):
        raise ValueError("invalid source commit")
    if source["tracked_clean"] is not True:
        raise ValueError("receipt was not produced from a tracked-clean tree")
    validate_source_manifest(source["files"], root)
    if subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    ).returncode:
        raise ValueError("source commit is unavailable")
    bound_paths = [entry["path"] for entry in source["files"]]
    if subprocess.run(
        ["git", "diff", "--quiet", commit, "--", *bound_paths], cwd=root, check=False
    ).returncode:
        raise ValueError("bound source differs from recorded commit")

    environment = exact_dict(
        data["environment"],
        {"platform", "machine", "python", "rustc", "cargo", "claude"},
        "environment",
    )
    if any(not isinstance(value, str) or not value for value in environment.values()):
        raise ValueError("invalid environment value")
    if data["model"] != harness.MODEL or data["route"] != "local claude CLI authenticated subscription":
        raise ValueError("model or route mismatch")

    commands = exact_dict(
        data["commands"], {"build", "solo", "overlap_compile", "overlap_check"}, "commands"
    )
    build = validate_command(commands["build"], "build command")
    solo = validate_command(commands["solo"], "solo command")
    overlap_compile = validate_command(commands["overlap_compile"], "overlap compile command")
    overlap_check = validate_command(commands["overlap_check"], "overlap check command")
    if build["argv"] != ["cargo", "build", "--release", "--locked"]:
        raise ValueError("build command mismatch")
    if solo["argv"] != [
        "target/release/azdaja",
        "solo",
        harness.QUESTION,
        "-f",
        "<fixture>",
    ]:
        raise ValueError("solo command mismatch")
    if overlap_compile["argv"] != [
        "rustc",
        "-O",
        "<scratch>/overlap.rs",
        "-o",
        "<scratch>/overlap",
    ]:
        raise ValueError("overlap compile command mismatch")
    if overlap_check["argv"] != [
        "<scratch>/overlap",
        "<fixture>",
        "<model-facing-prompt>",
    ]:
        raise ValueError("overlap check command mismatch")

    fixture = exact_dict(
        data["fixture"],
        {"bytes", "record_bytes", "sha256", "unique_blocker_occurrences", "expected"},
        "fixture",
    )
    if fixture != {
        "bytes": harness.INPUT_BYTES,
        "record_bytes": harness.RECORD_BYTES,
        "sha256": fixture["sha256"],
        "unique_blocker_occurrences": 1,
        "expected": harness.EXPECTED,
    } or not harness.is_sha256(fixture["sha256"]):
        raise ValueError("fixture invariants failed")

    binary = exact_dict(data["binary"], {"path", "bytes", "sha256"}, "binary")
    if binary["path"] != "target/release/azdaja":
        raise ValueError("binary path mismatch")
    positive_number(binary["bytes"], "binary bytes")
    if not harness.is_sha256(binary["sha256"]):
        raise ValueError("invalid binary hash")

    transport = exact_dict(
        data["transport"],
        {
            "call",
            "command_template",
            "elapsed_seconds",
            "exit_code",
            "prompt_bytes",
            "prompt_sha256",
            "response_sha256",
            "stderr_sha256",
        },
        "transport",
    )
    if transport["call"] != 1 or transport["exit_code"] != 0:
        raise ValueError("transport was not one successful call")
    if transport["command_template"] != harness.CLAUDE_COMMAND_TEMPLATE:
        raise ValueError("Claude command template mismatch")
    positive_number(transport["elapsed_seconds"], "transport elapsed time")
    positive_number(transport["prompt_bytes"], "transport prompt bytes")
    for key in ("prompt_sha256", "response_sha256", "stderr_sha256"):
        if not harness.is_sha256(transport[key]):
            raise ValueError(f"invalid transport hash: {key}")

    prompt = exact_dict(data["prompt"], {"bytes", "sha256", "input_to_prompt_ratio"}, "prompt")
    if prompt["bytes"] != transport["prompt_bytes"] or prompt["bytes"] >= 64 * 1024:
        raise ValueError("prompt byte bound mismatch")
    if prompt["sha256"] != transport["prompt_sha256"]:
        raise ValueError("prompt hash mismatch")
    expected_ratio = harness.INPUT_BYTES / prompt["bytes"]
    if abs(prompt["input_to_prompt_ratio"] - expected_ratio) > 1e-9:
        raise ValueError("input-to-prompt ratio mismatch")

    model_response = exact_dict(
        data["model_response"], {"text", "sha256", "contains_answer_constant"}, "model response"
    )
    if not isinstance(model_response["text"], str):
        raise ValueError("model response text missing")
    harness.validate_model_response(model_response["text"])
    if model_response["contains_answer_constant"] is not False:
        raise ValueError("model response answer-constant flag mismatch")
    if harness.sha256_bytes(model_response["text"].encode()) != model_response["sha256"]:
        raise ValueError("model response hash mismatch")
    if model_response["sha256"] != transport["response_sha256"]:
        raise ValueError("transport and model response hashes disagree")

    if data["result"] != {
        "expected": harness.EXPECTED,
        "actual": harness.EXPECTED,
        "exact": True,
    }:
        raise ValueError("exact result mismatch")
    if data["runtime"] != {
        "outcome": "succeeded",
        "exec_invocation_count": 1,
        "sub_call_count": 0,
        "semantic_call_count": 0,
        "snapshot_save_count": 1,
        "snapshot_load_count": 0,
    }:
        raise ValueError("runtime mismatch")
    if data["checks"] != {
        "root_prompt_below_64_kib": True,
        "no_input_or_scratch_path_in_prompt": True,
        "no_exact_100_byte_source_span_in_prompt": True,
        "one_provider_call": True,
        "model_response_has_no_answer_constant": True,
    }:
        raise ValueError("acceptance checks mismatch")
    timings = exact_dict(data["timings"], {"solo_seconds", "total_seconds"}, "timings")
    positive_number(timings["solo_seconds"], "solo time")
    positive_number(timings["total_seconds"], "total time")
    if data["limits"] != harness.LIMITS:
        raise ValueError("claim limits mismatch")

    checks = {"source": True, "binary": False}
    if binary_path is not None:
        if not binary_path.is_file() or binary_path.stat().st_size != binary["bytes"]:
            raise ValueError("binary size mismatch")
        if harness.sha256(binary_path) != binary["sha256"]:
            raise ValueError("binary hash mismatch")
        checks["binary"] = True
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--binary", type=Path)
    args = parser.parse_args()
    try:
        checks = validate_receipt(json.loads(args.receipt.read_text()), binary_path=args.binary)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, json.JSONDecodeError) as error:
        print(f"verification failed: {error}", file=sys.stderr)
        return 1
    checked = ", ".join(name for name, passed in checks.items() if passed)
    print(f"verified: {checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
