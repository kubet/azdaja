#!/usr/bin/env python3
"""Fail-closed verifier for three-scenario live Fable suite receipts."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("live_fable_suite_verify_run", HERE / "run.py")
suite = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(suite)

ROOT = Path(__file__).resolve().parents[2]
TOP_KEYS = {
    "schema",
    "artifact",
    "generated_at_utc",
    "source",
    "environment",
    "model",
    "route",
    "commands",
    "scenarios",
    "binary",
    "totals",
    "limits",
}


def exact_dict(value: object, keys: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label}: schema keys mismatch")
    return value


def positive(value: object, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{label}: expected positive number")


def validate_source_manifest(manifest: object, root: Path = ROOT) -> None:
    if not isinstance(manifest, list):
        raise ValueError("source manifest must be a list")
    expected = suite.source_paths(root)
    if len(manifest) != len(expected):
        raise ValueError("source manifest length mismatch")
    names = []
    for value in manifest:
        entry = exact_dict(value, {"path", "bytes", "sha256"}, "source file")
        name = entry["path"]
        if not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts:
            raise ValueError("unsafe source path")
        names.append(name)
        path = root / name
        if not path.is_file() or path.stat().st_size != entry["bytes"]:
            raise ValueError(f"source size or presence mismatch: {name}")
        if not suite.repo.is_sha256(entry["sha256"]) or suite.repo.sha256(path) != entry["sha256"]:
            raise ValueError(f"source hash mismatch: {name}")
    if names != expected:
        raise ValueError("source path ordering mismatch")


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
    if not isinstance(command["env"], dict):
        raise ValueError(f"{label}: invalid environment")
    if command["exit_code"] != 0:
        raise ValueError(f"{label}: command failed")
    positive(command["elapsed_seconds"], f"{label} elapsed")
    if not suite.repo.is_sha256(command["output_sha256"]):
        raise ValueError(f"{label}: invalid output hash")
    return command


def validate_scenario(value: object, expected_name: str) -> dict[str, object]:
    scenario = exact_dict(
        value,
        {
            "name",
            "question",
            "fixture",
            "transport",
            "prompt",
            "model_response",
            "result",
            "runtime",
            "commands",
            "checks",
        },
        f"scenario {expected_name}",
    )
    definition = suite.SCENARIOS[expected_name]
    if scenario["name"] != expected_name or scenario["question"] != definition["question"]:
        raise ValueError(f"{expected_name}: identity mismatch")
    fixture = exact_dict(scenario["fixture"], {"bytes", "record_bytes", "sha256"}, "fixture")
    if fixture["bytes"] != suite.repo.INPUT_BYTES or fixture["record_bytes"] != suite.repo.RECORD_BYTES:
        raise ValueError(f"{expected_name}: fixture invariant mismatch")
    if not suite.repo.is_sha256(fixture["sha256"]):
        raise ValueError(f"{expected_name}: invalid fixture hash")

    transport = exact_dict(
        scenario["transport"],
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
        raise ValueError(f"{expected_name}: transport was not one successful call")
    if transport["command_template"] != suite.repo.CLAUDE_COMMAND_TEMPLATE:
        raise ValueError(f"{expected_name}: Claude command mismatch")
    positive(transport["elapsed_seconds"], f"{expected_name}: provider time")
    for key in ("prompt_sha256", "response_sha256", "stderr_sha256"):
        if not suite.repo.is_sha256(transport[key]):
            raise ValueError(f"{expected_name}: invalid {key}")

    prompt = exact_dict(scenario["prompt"], {"bytes", "sha256", "input_to_prompt_ratio"}, "prompt")
    positive(prompt["bytes"], f"{expected_name}: prompt bytes")
    if prompt["bytes"] >= 64 * 1024 or prompt["bytes"] != transport["prompt_bytes"]:
        raise ValueError(f"{expected_name}: prompt bound mismatch")
    if prompt["sha256"] != transport["prompt_sha256"]:
        raise ValueError(f"{expected_name}: prompt hash mismatch")
    if abs(prompt["input_to_prompt_ratio"] - suite.repo.INPUT_BYTES / prompt["bytes"]) > 1e-9:
        raise ValueError(f"{expected_name}: prompt ratio mismatch")

    response = exact_dict(
        scenario["model_response"], {"text", "sha256", "contains_answer_constant"}, "model response"
    )
    if not isinstance(response["text"], str):
        raise ValueError(f"{expected_name}: response text missing")
    suite.validate_response(expected_name, response["text"])
    if response["contains_answer_constant"] is not False:
        raise ValueError(f"{expected_name}: answer-constant flag mismatch")
    if suite.repo.sha256_bytes(response["text"].encode()) != response["sha256"]:
        raise ValueError(f"{expected_name}: response hash mismatch")
    if response["sha256"] != transport["response_sha256"]:
        raise ValueError(f"{expected_name}: transport response hash mismatch")

    if scenario["result"] != {
        "expected": definition["expected"],
        "actual": definition["expected"],
        "exact": True,
    }:
        raise ValueError(f"{expected_name}: exact result mismatch")
    if scenario["runtime"] != {
        "outcome": "succeeded",
        "exec_invocation_count": 1,
        "sub_call_count": 0,
        "semantic_call_count": 0,
        "snapshot_save_count": 1,
        "snapshot_load_count": 0,
    }:
        raise ValueError(f"{expected_name}: runtime mismatch")
    if scenario["checks"] != {
        "root_prompt_below_64_kib": True,
        "no_input_or_scratch_path_in_prompt": True,
        "no_exact_100_byte_source_span_in_prompt": True,
        "one_provider_call": True,
        "model_response_has_no_answer_constant": True,
    }:
        raise ValueError(f"{expected_name}: acceptance checks mismatch")

    commands = exact_dict(scenario["commands"], {"solo", "overlap_check"}, "scenario commands")
    solo = validate_command(commands["solo"], f"{expected_name} solo")
    overlap = validate_command(commands["overlap_check"], f"{expected_name} overlap")
    if solo["argv"] != [
        "target/release/azdaja",
        "solo",
        definition["question"],
        "-f",
        f"<{expected_name}-fixture>",
    ]:
        raise ValueError(f"{expected_name}: solo command mismatch")
    if overlap["argv"] != [
        "<scratch>/overlap",
        f"<{expected_name}-fixture>",
        f"<{expected_name}-prompt>",
    ]:
        raise ValueError(f"{expected_name}: overlap command mismatch")
    return scenario


def validate_receipt(
    receipt: object, root: Path = ROOT, binary_path: Path | None = None
) -> dict[str, bool]:
    data = exact_dict(receipt, TOP_KEYS, "receipt")
    if data["schema"] != suite.SCHEMA or data["artifact"] != suite.ARTIFACT:
        raise ValueError("wrong schema or artifact")
    if not isinstance(data["generated_at_utc"], str):
        raise ValueError("missing timestamp")
    timestamp = dt.datetime.fromisoformat(data["generated_at_utc"].replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("timestamp lacks timezone")

    source = exact_dict(data["source"], {"commit", "tracked_clean", "files"}, "source")
    commit = source["commit"]
    if not isinstance(commit, str) or len(commit) != 40 or any(
        character not in "0123456789abcdef" for character in commit
    ):
        raise ValueError("invalid source commit")
    if source["tracked_clean"] is not True:
        raise ValueError("source was not tracked-clean")
    validate_source_manifest(source["files"], root)
    if subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    ).returncode:
        raise ValueError("source commit unavailable")
    paths = [entry["path"] for entry in source["files"]]
    if subprocess.run(
        ["git", "diff", "--quiet", commit, "--", *paths], cwd=root, check=False
    ).returncode:
        raise ValueError("bound source differs from recorded commit")

    environment = exact_dict(
        data["environment"],
        {"platform", "machine", "python", "rustc", "cargo", "claude"},
        "environment",
    )
    if any(not isinstance(value, str) or not value for value in environment.values()):
        raise ValueError("invalid environment value")
    if data["model"] != suite.MODEL or data["route"] != "local claude CLI authenticated subscription":
        raise ValueError("model or route mismatch")
    commands = exact_dict(data["commands"], {"build", "overlap_compile"}, "commands")
    build = validate_command(commands["build"], "build")
    compile_command = validate_command(commands["overlap_compile"], "overlap compile")
    if build["argv"] != ["cargo", "build", "--release", "--locked"]:
        raise ValueError("build command mismatch")
    if compile_command["argv"] != [
        "rustc",
        "-O",
        "<scratch>/overlap.rs",
        "-o",
        "<scratch>/overlap",
    ]:
        raise ValueError("overlap compile command mismatch")

    if not isinstance(data["scenarios"], list) or len(data["scenarios"]) != 3:
        raise ValueError("expected three scenario receipts")
    scenarios = [
        validate_scenario(value, name)
        for value, name in zip(data["scenarios"], suite.SCENARIOS)
    ]
    binary = exact_dict(data["binary"], {"path", "bytes", "sha256"}, "binary")
    if binary["path"] != "target/release/azdaja":
        raise ValueError("binary path mismatch")
    positive(binary["bytes"], "binary bytes")
    if not suite.repo.is_sha256(binary["sha256"]):
        raise ValueError("invalid binary hash")

    totals = exact_dict(
        data["totals"],
        {
            "scenarios",
            "input_bytes",
            "root_prompt_bytes",
            "provider_calls",
            "monty_executions",
            "recursive_or_semantic_subcalls",
            "exact_results",
            "provider_seconds",
            "total_seconds",
        },
        "totals",
    )
    expected_totals = {
        "scenarios": 3,
        "input_bytes": sum(item["fixture"]["bytes"] for item in scenarios),
        "root_prompt_bytes": sum(item["prompt"]["bytes"] for item in scenarios),
        "provider_calls": sum(item["transport"]["call"] for item in scenarios),
        "monty_executions": sum(item["runtime"]["exec_invocation_count"] for item in scenarios),
        "recursive_or_semantic_subcalls": sum(
            item["runtime"]["sub_call_count"] + item["runtime"]["semantic_call_count"]
            for item in scenarios
        ),
        "exact_results": sum(1 for item in scenarios if item["result"]["exact"]),
    }
    for key, expected in expected_totals.items():
        if totals[key] != expected:
            raise ValueError(f"total mismatch: {key}")
    if totals["provider_calls"] != 3 or totals["monty_executions"] != 3:
        raise ValueError("suite call or execution total mismatch")
    if totals["recursive_or_semantic_subcalls"] != 0 or totals["exact_results"] != 3:
        raise ValueError("suite exactness or subcall total mismatch")
    positive(totals["provider_seconds"], "provider total")
    positive(totals["total_seconds"], "suite total")
    if data["limits"] != suite.LIMITS:
        raise ValueError("claim limits mismatch")

    checks = {"source": True, "binary": False}
    if binary_path is not None:
        if not binary_path.is_file() or binary_path.stat().st_size != binary["bytes"]:
            raise ValueError("binary size mismatch")
        if suite.repo.sha256(binary_path) != binary["sha256"]:
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
    print("verified: " + ", ".join(name for name, passed in checks.items() if passed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
