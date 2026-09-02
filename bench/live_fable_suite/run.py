#!/usr/bin/env python3
"""Opt-in three-scenario live Claude Fable product-path suite."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO_HARNESS_PATH = ROOT / "bench/live_fable_repo/run.py"
SPEC = importlib.util.spec_from_file_location("live_fable_repo_run", REPO_HARNESS_PATH)
repo = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(repo)

SCHEMA = "azdaja.live_fable_suite.v1"
ARTIFACT = "live_fable_three_scenario_suite"
MODEL = repo.MODEL
LIMITS = [
    "three deterministic synthetic live smokes",
    "one model and one provider route",
    "one provider call per scenario",
    "no baseline arm",
    "no repeated trials",
    "subscription token usage unavailable in text mode",
    "not a benchmark or superiority result",
]
SCENARIOS = {
    "build": {
        "question": "PRODUCT_BUILD_LOG_LIVE: How many ERROR records target payments::retry? Reply as Answer: N.",
        "expected": "Answer: 13",
        "forbidden": ["Answer: 13"],
    },
    "repo": {
        "question": repo.QUESTION,
        "expected": repo.EXPECTED,
        "forbidden": [repo.EXPECTED, repo.TICKET],
    },
    "catalog": {
        "question": (
            "PRODUCT_CATALOG_LIVE: Find the final record whose item field is SKU-4821 "
            "and return its color field. Reply exactly as Color: VALUE."
        ),
        "expected": "Color: cerulean",
        "forbidden": ["Color: cerulean", "cerulean"],
    },
}


def source_paths(root: Path = ROOT) -> list[str]:
    paths = set(repo.source_paths(root))
    paths.update(
        {
            "bench/live_fable_suite/run.py",
            "bench/live_fable_suite/verify.py",
        }
    )
    return sorted(paths)


def source_manifest(root: Path = ROOT) -> list[dict[str, object]]:
    return [
        {"path": name, "bytes": (root / name).stat().st_size, "sha256": repo.sha256(root / name)}
        for name in source_paths(root)
    ]


def write_records(path: Path, record) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("wb") as handle:
        for index in range(repo.BLOCKS):
            text = record(index).encode()
            if len(text) >= repo.RECORD_BYTES:
                raise ValueError(f"record {index} exceeds fixture block")
            block = text + b" " * (repo.RECORD_BYTES - len(text) - 1) + b"\n"
            handle.write(block)
            digest.update(block)
    if path.stat().st_size != repo.INPUT_BYTES:
        raise ValueError("fixture size mismatch")
    return digest.hexdigest()


def write_build_fixture(path: Path) -> str:
    def record(index: int) -> str:
        if index % 1000 == 17:
            level, target = "ERROR", "payments::retry"
        elif index % 137 == 9:
            level, target = "ERROR", "search::index"
        else:
            level, target = "INFO", "azdaja::worker"
        return (
            f"[2026-08-17T08:{index % 60:02}:{(index * 17) % 60:02}Z] "
            f"job={index:05} level={level} target={target} "
            f"duration_ms={20 + index % 300} message=compile step completed\n"
        )

    return write_records(path, record)


def write_catalog_fixture(path: Path) -> str:
    def record(index: int) -> str:
        if index in {100, 5000, 12000}:
            color = "cerulean" if index == 12000 else "amber"
            return (
                f"catalog_record={index:05} item=SKU-4821 color={color} "
                f"aisle={index % 40:02} stock={20 + index % 300}\n"
            )
        return (
            f"catalog_record={index:05} item=SKU-{index:05} color=gray "
            f"aisle={index % 40:02} stock={20 + index % 300}\n"
        )

    return write_records(path, record)


def write_fixture(name: str, path: Path) -> str:
    if name == "build":
        return write_build_fixture(path)
    if name == "repo":
        return repo.write_fixture(path)
    if name == "catalog":
        return write_catalog_fixture(path)
    raise ValueError(f"unknown scenario: {name}")


def validate_response(name: str, response: str) -> None:
    if not response.strip() or "FINAL(" not in response:
        raise ValueError(f"{name}: model response is not a finalizing program")
    for forbidden in SCENARIOS[name]["forbidden"]:
        if forbidden in response:
            raise ValueError(f"{name}: model response contains answer constant {forbidden!r}")


def write_config(path: Path, wrapper: Path, scratch: Path) -> None:
    path.write_text(
        f"sub_llm_cmd = {json.dumps(shlex.join(['python3', str(wrapper), str(scratch)]))}\n"
        f'default_model = "{MODEL}"\n'
        "output_cap = 4096\n"
        "max_depth = 1\n"
        "sub_timeout = 240\n"
        "max_sessions = 1\n"
        "cell_timeout = 90\n"
        "idle_timeout = 1800\n"
        "clean_patterns = []\n"
        'jcode_provider = "claude"\n'
        'jcode_reasoning = "medium"\n'
        "max_calls_per_cell = 1\n"
    )


def run_scenario(name: str, suite_scratch: Path, scanner_binary: Path) -> dict[str, object]:
    definition = SCENARIOS[name]
    scratch = suite_scratch / name
    scratch.mkdir()
    fixture_path = scratch / f"{name}.input"
    prompt_path = scratch / "prompt.txt"
    response_path = scratch / "model-response.txt"
    trace_path = scratch / "trace.txt"
    transport_path = scratch / "transport.json"
    fixture_sha256 = write_fixture(name, fixture_path)
    wrapper = scratch / "transport.py"
    wrapper.write_text(repo.TRANSPORT)
    config = scratch / "config.toml"
    write_config(config, wrapper, scratch)

    solo_record, solo_output = repo.run_command(
        [
            str(ROOT / "target/release/azdaja"),
            "solo",
            definition["question"],
            "-f",
            str(fixture_path),
        ],
        {
            "AZDAJA_HOME": str(scratch / "state"),
            "AZDAJA_CONFIG": str(config),
            "AZDAJA_SOLO_TRACE": str(trace_path),
        },
        timeout=300,
        public_argv=[
            "target/release/azdaja",
            "solo",
            definition["question"],
            "-f",
            f"<{name}-fixture>",
        ],
        public_env={
            "AZDAJA_HOME": f"<scratch>/{name}/state",
            "AZDAJA_CONFIG": f"<scratch>/{name}/config.toml",
            "AZDAJA_SOLO_TRACE": f"<scratch>/{name}/trace.txt",
        },
    )
    if solo_record["exit_code"] != 0:
        sys.stdout.buffer.write(solo_output)
        for label, path in (
            ("transport metadata", transport_path),
            ("provider stderr", scratch / "model-stderr.txt"),
            ("provider stdout", response_path),
        ):
            if path.is_file():
                print(f"\n--- {name} {label} ---", file=sys.stderr)
                print(path.read_text(errors="replace"), file=sys.stderr)
        raise RuntimeError(f"{name}: azdaja solo failed")
    actual = solo_output.decode("utf-8", errors="replace").strip()
    if actual != definition["expected"]:
        raise ValueError(f"{name}: wrong exact output {actual!r}")
    if not all(path.is_file() for path in (prompt_path, response_path, trace_path, transport_path)):
        raise ValueError(f"{name}: missing private evidence file")

    prompt = prompt_path.read_text(errors="replace")
    response = response_path.read_text(errors="replace")
    transport = json.loads(transport_path.read_text())
    validate_response(name, response)
    if transport.get("call") != 1 or transport.get("exit_code") != 0:
        raise ValueError(f"{name}: transport was not one successful call")
    if transport.get("command_template") != repo.CLAUDE_COMMAND_TEMPLATE:
        raise ValueError(f"{name}: Claude command template mismatch")
    if transport.get("prompt_bytes") != len(prompt.encode()):
        raise ValueError(f"{name}: prompt byte count mismatch")
    if transport.get("prompt_sha256") != repo.sha256_bytes(prompt.encode()):
        raise ValueError(f"{name}: prompt hash mismatch")
    if transport.get("response_sha256") != repo.sha256_bytes(response.encode()):
        raise ValueError(f"{name}: response hash mismatch")
    if len(prompt.encode()) >= 64 * 1024:
        raise ValueError(f"{name}: root prompt exceeded 64 KiB")
    if any(value in prompt for value in (str(ROOT), str(scratch), str(fixture_path))):
        raise ValueError(f"{name}: model-facing prompt contains a host path")

    overlap_record, overlap_output = repo.run_command(
        [str(scanner_binary), str(fixture_path), str(prompt_path)],
        timeout=120,
        public_argv=["<scratch>/overlap", f"<{name}-fixture>", f"<{name}-prompt>"],
    )
    if overlap_record["exit_code"] != 0:
        sys.stdout.buffer.write(overlap_output)
        raise RuntimeError(f"{name}: exact overlap scanner failed")
    runtime = repo.parse_runtime(trace_path)
    scenario = {
        "name": name,
        "question": definition["question"],
        "fixture": {
            "bytes": repo.INPUT_BYTES,
            "record_bytes": repo.RECORD_BYTES,
            "sha256": fixture_sha256,
        },
        "transport": transport,
        "prompt": {
            "bytes": len(prompt.encode()),
            "sha256": repo.sha256_bytes(prompt.encode()),
            "input_to_prompt_ratio": repo.INPUT_BYTES / len(prompt.encode()),
        },
        "model_response": {
            "text": response,
            "sha256": repo.sha256_bytes(response.encode()),
            "contains_answer_constant": False,
        },
        "result": {
            "expected": definition["expected"],
            "actual": actual,
            "exact": True,
        },
        "runtime": runtime,
        "commands": {"solo": solo_record, "overlap_check": overlap_record},
        "checks": {
            "root_prompt_below_64_kib": True,
            "no_input_or_scratch_path_in_prompt": True,
            "no_exact_100_byte_source_span_in_prompt": True,
            "one_provider_call": True,
            "model_response_has_no_answer_constant": True,
        },
    }
    fixture_path.unlink()
    return scenario


def render_summary(receipt: dict[str, object]) -> str:
    lines = [
        "# Live Claude Fable three-scenario product suite",
        "",
        f"Source commit: `{receipt['source']['commit']}`",
        "",
        "Claude Fable synthesized three generic programs from three bounded root prompts. Azdaja executed each program locally against its complete deterministic input and returned all three exact answers.",
        "",
        "| Scenario | Exact result | Root prompt | Input / prompt | Provider time |",
        "|---|---|---:|---:|---:|",
    ]
    for scenario in receipt["scenarios"]:
        result = str(scenario["result"]["actual"]).replace("|", "\\|")
        lines.append(
            f"| {scenario['name']} | `{result}` | {scenario['prompt']['bytes']:,} B | "
            f"{scenario['prompt']['input_to_prompt_ratio']:,.0f}x | "
            f"{scenario['transport']['elapsed_seconds']:.3f} s |"
        )
    totals = receipt["totals"]
    lines.extend(
        [
            "",
            f"Totals: {totals['exact_results']}/3 exact, {totals['provider_calls']} provider calls, "
            f"{totals['monty_executions']} Monty executions, {totals['recursive_or_semantic_subcalls']} recursive or semantic subcalls.",
            "",
            "Every model response is published in the receipt and contains neither its expected answer nor its answer-specific constant. Exact scanners found zero 100-byte source spans in all provider prompts, and no prompt contained a repository, input, or scratch host path.",
            "",
            "## Limits",
            "",
            *[f"- {limit}" for limit in receipt["limits"]],
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes-run-inference", action="store_true")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        repo.validate_intent(args.yes_run_inference)
        repo.ensure_outputs_available([args.receipt, args.summary], args.force)
    except (PermissionError, FileExistsError) as error:
        print(error, file=sys.stderr)
        return 2
    if not repo.tracked_clean():
        print("refusing live evidence from a tracked-dirty worktree", file=sys.stderr)
        return 2
    if shutil.which("claude") is None:
        print("claude CLI is unavailable", file=sys.stderr)
        return 2

    started = time.monotonic()
    build_record, build_output = repo.run_command(
        ["cargo", "build", "--release", "--locked"], timeout=600
    )
    if build_record["exit_code"] != 0:
        sys.stdout.buffer.write(build_output)
        return int(build_record["exit_code"])
    scratch_parent = Path(os.environ.get("JCODE_SCRATCH_DIR", tempfile.gettempdir()))
    scratch_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="azdaja-live-fable-suite-", dir=scratch_parent) as directory:
        scratch = Path(directory)
        scanner_source = scratch / "overlap.rs"
        scanner_binary = scratch / "overlap"
        scanner_source.write_text(repo.OVERLAP_SCANNER)
        compile_record, compile_output = repo.run_command(
            ["rustc", "-O", str(scanner_source), "-o", str(scanner_binary)],
            timeout=120,
            public_argv=["rustc", "-O", "<scratch>/overlap.rs", "-o", "<scratch>/overlap"],
        )
        if compile_record["exit_code"] != 0:
            sys.stdout.buffer.write(compile_output)
            return int(compile_record["exit_code"])
        try:
            scenarios = []
            for index, name in enumerate(SCENARIOS):
                print(
                    "JCODE_PROGRESS "
                    + json.dumps(
                        {
                            "current": index + 1,
                            "total": len(SCENARIOS),
                            "unit": "scenarios",
                            "message": f"Running live Fable scenario: {name}",
                        }
                    ),
                    flush=True,
                )
                scenarios.append(run_scenario(name, scratch, scanner_binary))
                if index + 1 < len(SCENARIOS):
                    time.sleep(5)
        except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
            print(f"live suite failed: {error}", file=sys.stderr)
            return 1

    binary = ROOT / "target/release/azdaja"
    receipt: dict[str, object] = {
        "schema": SCHEMA,
        "artifact": ARTIFACT,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "source": {
            "commit": repo.tool_version(["git", "rev-parse", "HEAD"]),
            "tracked_clean": True,
            "files": source_manifest(),
        },
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
            "rustc": repo.tool_version(["rustc", "--version"]),
            "cargo": repo.tool_version(["cargo", "--version"]),
            "claude": repo.tool_version(["claude", "--version"]),
        },
        "model": MODEL,
        "route": "local claude CLI authenticated subscription",
        "commands": {"build": build_record, "overlap_compile": compile_record},
        "scenarios": scenarios,
        "binary": {
            "path": "target/release/azdaja",
            "bytes": binary.stat().st_size,
            "sha256": repo.sha256(binary),
        },
        "totals": {
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
            "provider_seconds": sum(item["transport"]["elapsed_seconds"] for item in scenarios),
            "total_seconds": round(time.monotonic() - started, 6),
        },
        "limits": LIMITS,
    }
    repo.atomic_write(args.receipt, (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode())
    repo.atomic_write(args.summary, render_summary(receipt).encode())
    print(f"wrote {args.receipt} and {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
