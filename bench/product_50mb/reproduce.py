#!/usr/bin/env python3
"""Reproduce the provider-free, current-source 50 MiB acceptance capsule."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "azdaja.product_50mb.acceptance.v2"
ARTIFACT = "product_50mb_current_source_acceptance"
SCENARIOS = {"build", "repo", "transcript"}
EXPECTED_ANSWERS = {
    "build": "Answer: 13",
    "repo": "src/module_07777.rs|AZD-7777",
    "transcript": "ship-v0.1-after-doctor",
}
FIXED_INVARIANTS = {
    "input_bytes": 50 * 1024 * 1024,
    "root_calls": 1,
    "exec_invocation_count": 1,
    "sub_call_count": 0,
    "exact_answer": True,
    "no_raw_source_span_bytes": 100,
}
NOT_DEMONSTRATED = [
    "live-model program synthesis",
    "semantic quality on natural data",
    "arbitrary-input support",
    "comparison superiority",
    "official benchmark status",
    "operating-system sandbox guarantees",
]
DEMONSTRATED = [
    "three deterministic 50 MiB inputs traverse the release solo CLI path",
    "each scripted answer is exact after one Monty execution and zero recursive subcalls",
    "each model-facing root prompt is below 64 KiB and below one-fiftieth of its input",
    "no exact 100-byte source span or host input path reaches the scripted transport prompt",
    "runtime traces report success and cleanup leaves no persistent session",
]
BUILD_CMD = ["cargo", "build", "--release", "--locked"]
TEST_CMD = [
    "cargo",
    "test",
    "--release",
    "--locked",
    "--test",
    "product_50mb",
    "offline_scripted_harness_answers_three_real_world_50_mib_files_without_a_death",
    "--",
    "--ignored",
    "--exact",
    "--test-threads=1",
    "--nocapture",
]
TEST_ENV = {"AZDAJA_PRODUCT_BINARY": "target/release/azdaja"}
BUILD_LOG_HEADER = b"===== cargo build --release --locked =====\n"
TEST_LOG_HEADER = b"\n===== product_50mb exact ignored test =====\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def parse_structured(text: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("{"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and record.get("kind") in {"scenario", "summary"}:
            records.append(record)
    return records


def validate_records(
    records: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    scenarios = [record for record in records if record.get("kind") == "scenario"]
    summaries = [record for record in records if record.get("kind") == "summary"]
    if len(scenarios) != 3 or {record.get("scenario") for record in scenarios} != SCENARIOS:
        raise ValueError("expected exactly one record for each of build, repo, and transcript")

    expected_scenario_keys = {
        "kind",
        "scenario",
        "answer",
        "root_prompt_bytes",
        "reaped_children_high_water_bytes",
        *FIXED_INVARIANTS.keys(),
    }
    for record in scenarios:
        scenario = record.get("scenario")
        if set(record) != expected_scenario_keys:
            raise ValueError(f"{scenario}: unexpected scenario fields")
        for key, expected in FIXED_INVARIANTS.items():
            if record.get(key) != expected:
                raise ValueError(f"{scenario}: invariant {key} mismatch")
        if record.get("answer") != EXPECTED_ANSWERS[scenario]:
            raise ValueError(f"{scenario}: answer mismatch")
        root_prompt_bytes = record.get("root_prompt_bytes")
        if not isinstance(root_prompt_bytes, int) or isinstance(root_prompt_bytes, bool):
            raise ValueError(f"{scenario}: root_prompt_bytes is not an integer")
        if root_prompt_bytes <= 0 or root_prompt_bytes >= 64 * 1024:
            raise ValueError(f"{scenario}: root prompt is outside the accepted bound")
        if root_prompt_bytes * 50 >= FIXED_INVARIANTS["input_bytes"]:
            raise ValueError(f"{scenario}: root prompt is not below one-fiftieth of the input")
        rss = record.get("reaped_children_high_water_bytes")
        if rss is not None and (not isinstance(rss, int) or isinstance(rss, bool) or rss <= 0):
            raise ValueError(f"{scenario}: invalid reaped-child RSS value")

    if len(summaries) != 1:
        raise ValueError("expected exactly one summary record")
    summary = summaries[0]
    expected_summary_keys = {
        "kind",
        "scenarios",
        "cleanup",
        "surviving_sessions",
        "rss_available",
        "peak_reaped_children_high_water_bytes",
    }
    if set(summary) != expected_summary_keys:
        raise ValueError("unexpected summary fields")
    if (
        summary.get("scenarios") != 3
        or summary.get("cleanup") != "passed"
        or summary.get("surviving_sessions") != 0
        or not isinstance(summary.get("rss_available"), bool)
    ):
        raise ValueError("summary invariants failed")
    peak = summary.get("peak_reaped_children_high_water_bytes")
    rss_values = [
        record["reaped_children_high_water_bytes"]
        for record in scenarios
        if record["reaped_children_high_water_bytes"] is not None
    ]
    if summary["rss_available"] != bool(rss_values):
        raise ValueError("summary RSS availability disagrees with scenario records")
    if peak != (max(rss_values) if rss_values else None):
        raise ValueError("summary peak RSS disagrees with scenario records")
    return sorted(scenarios, key=lambda record: str(record["scenario"])), summary


def expected_source_paths(root: Path = ROOT) -> list[str]:
    paths = {
        "Cargo.toml",
        "Cargo.lock",
        "tests/product_50mb.rs",
        "bench/product_50mb/reproduce.py",
        "bench/product_50mb/verify.py",
    }
    paths.update(path.relative_to(root).as_posix() for path in (root / "src").rglob("*.rs"))
    for optional in ("build.rs", ".cargo/config", ".cargo/config.toml"):
        if (root / optional).is_file():
            paths.add(optional)
    missing = [path for path in paths if not (root / path).is_file()]
    if missing:
        raise ValueError(f"missing runtime-defining source files: {missing}")
    return sorted(paths)


def source_manifest(root: Path = ROOT) -> list[dict[str, object]]:
    return [
        {"path": name, "bytes": (root / name).stat().st_size, "sha256": sha256(root / name)}
        for name in expected_source_paths(root)
    ]


def ensure_new_outputs(paths: list[Path], force: bool) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing and not force:
        raise FileExistsError("refusing to overwrite existing output: " + ", ".join(existing))


def tracked_diff_clean(root: Path = ROOT) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout == ""


def sanitize_command_output(data: bytes, root: Path = ROOT) -> bytes:
    root_bytes = os.fsencode(root.resolve())
    if not root_bytes:
        raise ValueError("repository root cannot be empty")
    return data.replace(root_bytes, b"<repo>")


def run_command(
    argv: list[str], env_delta: dict[str, str] | None = None
) -> tuple[dict[str, object], bytes]:
    environment = os.environ.copy()
    if env_delta:
        environment.update(env_delta)
    started = time.monotonic()
    result = subprocess.run(
        argv,
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    elapsed = time.monotonic() - started
    output = sanitize_command_output(result.stdout)
    record = {
        "argv": argv,
        "env": env_delta or {},
        "exit_code": result.returncode,
        "elapsed_seconds": round(elapsed, 6),
        "output_sha256": sha256_bytes(output),
    }
    return record, output


def tool_version(argv: list[str]) -> str:
    return subprocess.check_output(argv, cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_bytes(data)
    temporary.replace(path)


def render_summary(receipt: dict[str, object], receipt_path: Path, log_path: Path) -> str:
    lines = [
        "# Azdaja 50 MiB current-source acceptance capsule",
        "",
        f"Source commit: `{receipt['source']['commit']}`",
        "",
        "This provider-free acceptance run exercised the release `azdaja solo` path over three deterministic, exactly 50 MiB inputs. The scripted transport returned programs rather than answer constants, and Azdaja executed those programs against the full local input.",
        "",
        "| Scenario | Exact answer | Input | Root prompt | Input / prompt | Reaped-child RSS high-water |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for scenario in receipt["scenarios"]:
        input_bytes = scenario["input_bytes"]
        prompt_bytes = scenario["root_prompt_bytes"]
        ratio = input_bytes / prompt_bytes
        rss = scenario["reaped_children_high_water_bytes"]
        rss_text = "unavailable" if rss is None else f"{rss / (1024 * 1024):.1f} MiB"
        answer = str(scenario["answer"]).replace("|", "\\|")
        lines.append(
            f"| {scenario['scenario']} | `{answer}` | 50 MiB | {prompt_bytes:,} B | {ratio:,.0f}x | {rss_text} |"
        )
    lines.extend(
        [
            "",
            "All three runs reported one root transport call, one Monty execution, zero recursive subcalls, no exact 100-byte source span in the model-facing prompt, and no surviving session after cleanup.",
            "",
            "## What this does not prove",
            "",
            *[f"- {item}" for item in receipt["claim_boundary"]["does_not_demonstrate"]],
            "",
            f"Machine-readable receipt: `{display_path(receipt_path)}`",
            f"Captured command log: `{display_path(log_path)}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    outputs = [args.receipt, args.summary, args.log]
    try:
        ensure_new_outputs(outputs, args.force)
    except FileExistsError as error:
        print(error, file=sys.stderr)
        return 2
    if not tracked_diff_clean():
        print("refusing to produce evidence from a tracked-dirty worktree", file=sys.stderr)
        return 2

    build_record, build_output = run_command(BUILD_CMD)
    if build_record["exit_code"] != 0:
        sys.stdout.buffer.write(build_output)
        return int(build_record["exit_code"])
    test_record, test_output = run_command(TEST_CMD, TEST_ENV)
    if test_record["exit_code"] != 0:
        sys.stdout.buffer.write(test_output)
        return int(test_record["exit_code"])

    try:
        scenarios, summary = validate_records(
            parse_structured(test_output.decode("utf-8", errors="replace"))
        )
    except ValueError as error:
        print(f"structured output validation failed: {error}", file=sys.stderr)
        return 1

    log_data = BUILD_LOG_HEADER + build_output + TEST_LOG_HEADER + test_output
    atomic_write(args.log, log_data)

    binary = ROOT / "target/release/azdaja"
    commit = tool_version(["git", "rev-parse", "HEAD"])
    receipt: dict[str, object] = {
        "schema": SCHEMA,
        "artifact": ARTIFACT,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "source": {
            "commit": commit,
            "tracked_diff_clean": True,
            "files": source_manifest(),
        },
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
            "rustc": tool_version(["rustc", "--version"]),
            "cargo": tool_version(["cargo", "--version"]),
        },
        "commands": [build_record, test_record],
        "binary": {
            "path": binary.relative_to(ROOT).as_posix(),
            "bytes": binary.stat().st_size,
            "sha256": sha256(binary),
        },
        "log": {
            "path": display_path(args.log),
            "bytes": len(log_data),
            "sha256": sha256_bytes(log_data),
        },
        "scenarios": scenarios,
        "summary": summary,
        "claim_boundary": {
            "demonstrates": DEMONSTRATED,
            "does_not_demonstrate": NOT_DEMONSTRATED,
        },
    }
    receipt_data = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    atomic_write(args.receipt, receipt_data)
    atomic_write(args.summary, render_summary(receipt, args.receipt, args.log).encode())
    print(f"wrote {args.receipt}, {args.summary}, and {args.log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
