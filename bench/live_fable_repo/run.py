#!/usr/bin/env python3
"""Opt-in, one-provider-call live Claude Fable repository smoke harness."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
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
SCHEMA = "azdaja.live_fable_repo.v2"
ARTIFACT = "live_fable_repo_smoke"
MODEL = "claude-fable-5"
EXPECTED = "src/module_07777.rs|AZD-7777"
TICKET = "AZD-7777"
INPUT_BYTES = 50 * 1024 * 1024
RECORD_BYTES = 4096
BLOCKS = INPUT_BYTES // RECORD_BYTES
QUESTION = (
    "PRODUCT_REPO_DUMP_LIVE: Return path|ticket for the unique "
    "AZDAJA_RELEASE_BLOCKER in the complete repository dump."
)
CLAUDE_COMMAND_TEMPLATE = [
    "claude",
    "-p",
    "<model-facing prompt>",
    "--model",
    MODEL,
    "--output-format",
    "text",
    "--max-turns",
    "1",
    "--tools",
    "",
]
LIMITS = [
    "single synthetic live smoke",
    "one model and one provider route",
    "no baseline arm",
    "no repeated trials",
    "subscription token usage unavailable in text mode",
    "not a benchmark or superiority result",
]
OVERLAP_SCANNER = r'''
use std::{collections::HashMap, env, fs};
const WINDOW: usize = 100;
const BASE: u64 = 1_000_003;
fn hash(window: &[u8]) -> u64 {
    window.iter().fold(0u64, |value, byte| {
        value.wrapping_mul(BASE).wrapping_add(u64::from(*byte) + 1)
    })
}
fn main() {
    let args: Vec<String> = env::args().collect();
    let source = fs::read(&args[1]).unwrap();
    let prompt = fs::read(&args[2]).unwrap();
    assert!(source.len() >= WINDOW && prompt.len() >= WINDOW);
    let mut prompt_windows: HashMap<u64, Vec<usize>> = HashMap::new();
    for (offset, window) in prompt.windows(WINDOW).enumerate() {
        prompt_windows.entry(hash(window)).or_default().push(offset);
    }
    let mut power = 1u64;
    for _ in 1..WINDOW { power = power.wrapping_mul(BASE); }
    let mut rolling = hash(&source[..WINDOW]);
    for offset in 0..=source.len() - WINDOW {
        if let Some(prompt_offsets) = prompt_windows.get(&rolling) {
            for prompt_offset in prompt_offsets {
                if source[offset..offset + WINDOW]
                    == prompt[*prompt_offset..*prompt_offset + WINDOW]
                {
                    eprintln!("exact overlap at source={offset} prompt={prompt_offset}");
                    std::process::exit(1);
                }
            }
        }
        if offset + WINDOW < source.len() {
            rolling = rolling.wrapping_sub(
                (u64::from(source[offset]) + 1).wrapping_mul(power)
            );
            rolling = rolling
                .wrapping_mul(BASE)
                .wrapping_add(u64::from(source[offset + WINDOW]) + 1);
        }
    }
    println!("no exact 100-byte source span in model-facing prompt");
}
'''
TRANSPORT = r'''
import hashlib
import json
import pathlib
import subprocess
import sys
import time

root = pathlib.Path(sys.argv[1])
prompt = sys.stdin.read()
count_path = root / "call-count.txt"
count = int(count_path.read_text()) + 1 if count_path.exists() else 1
count_path.write_text(str(count))
if count > 1:
    print("live smoke is capped at one provider call", file=sys.stderr)
    raise SystemExit(70)
(root / "prompt.txt").write_text(prompt)
command = [
    "claude", "-p", prompt,
    "--model", "claude-fable-5",
    "--output-format", "text",
    "--max-turns", "1",
    "--tools", "",
]
started = time.monotonic()
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(root / "model-response.txt").write_bytes(result.stdout)
(root / "model-stderr.txt").write_bytes(result.stderr)
metadata = {
    "call": count,
    "command_template": [
        "claude", "-p", "<model-facing prompt>",
        "--model", "claude-fable-5",
        "--output-format", "text",
        "--max-turns", "1",
        "--tools", "",
    ],
    "elapsed_seconds": round(time.monotonic() - started, 6),
    "exit_code": result.returncode,
    "prompt_bytes": len(prompt.encode()),
    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
    "response_sha256": hashlib.sha256(result.stdout).hexdigest(),
    "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
}
(root / "transport.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
sys.stdout.buffer.write(result.stdout)
sys.stderr.buffer.write(result.stderr)
raise SystemExit(result.returncode)
'''


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


def tracked_clean(root: Path = ROOT) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout == ""


def ensure_outputs_available(paths: list[Path], force: bool) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing and not force:
        raise FileExistsError("refusing to overwrite existing output: " + ", ".join(existing))


def validate_intent(acknowledged: bool) -> None:
    if not acknowledged:
        raise PermissionError("refusing live inference without --yes-run-inference")


def validate_model_response(response: str) -> None:
    if not response.strip() or "FINAL(" not in response:
        raise ValueError("model response does not contain an executable finalization program")
    if EXPECTED in response or TICKET in response:
        raise ValueError("model response contains the answer constant")


def source_paths(root: Path = ROOT) -> list[str]:
    paths = {
        "Cargo.toml",
        "Cargo.lock",
        "bench/live_fable_repo/run.py",
        "bench/live_fable_repo/verify.py",
    }
    paths.update(path.relative_to(root).as_posix() for path in (root / "src").rglob("*.rs"))
    return sorted(paths)


def source_manifest(root: Path = ROOT) -> list[dict[str, object]]:
    return [
        {"path": name, "bytes": (root / name).stat().st_size, "sha256": sha256(root / name)}
        for name in source_paths(root)
    ]


def write_fixture(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("wb") as handle:
        for index in range(BLOCKS):
            blocker = f"AZDAJA_RELEASE_BLOCKER=AZD-{index}\n" if index == 7777 else ""
            text = (
                f"===== BEGIN FILE src/module_{index:05}.rs =====\n"
                "// repository export generated from tracked source\n"
                f"{blocker}"
                f"pub fn module_{index:05}() -> usize {{ {index} }}\n"
                "===== END FILE =====\n"
            ).encode()
            record = text + b" " * (RECORD_BYTES - len(text) - 1) + b"\n"
            handle.write(record)
            digest.update(record)
    if path.stat().st_size != INPUT_BYTES:
        raise ValueError("fixture size mismatch")
    return digest.hexdigest()


def run_command(
    argv: list[str],
    env_delta: dict[str, str] | None = None,
    timeout: int | None = None,
    public_argv: list[str] | None = None,
    public_env: dict[str, str] | None = None,
) -> tuple[dict[str, object], bytes]:
    environment = os.environ.copy()
    environment.update(env_delta or {})
    started = time.monotonic()
    try:
        result = subprocess.run(
            argv,
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        output = result.stdout
        exit_code = result.returncode
    except subprocess.TimeoutExpired as error:
        output = (error.stdout or b"") + (error.stderr or b"")
        exit_code = 124
    record = {
        "argv": public_argv or argv,
        "env": public_env if public_env is not None else (env_delta or {}),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "exit_code": exit_code,
        "output_sha256": sha256_bytes(output),
    }
    return record, output


def parse_runtime(trace: Path) -> dict[str, object]:
    runtime = None
    for line in trace.read_text(errors="replace").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("event") == "solo_runtime":
            runtime = value
    if runtime is None:
        raise ValueError("missing solo_runtime trace record")
    selected = {
        "outcome": runtime.get("outcome"),
        "exec_invocation_count": runtime.get("exec_invocation_count"),
        "sub_call_count": runtime.get("sub_call_count"),
        "semantic_call_count": runtime.get("semantic_call_count"),
        "snapshot_save_count": runtime.get("snapshot_save_count"),
        "snapshot_load_count": runtime.get("snapshot_load_count"),
    }
    expected = {
        "outcome": "succeeded",
        "exec_invocation_count": 1,
        "sub_call_count": 0,
        "semantic_call_count": 0,
        "snapshot_save_count": 1,
        "snapshot_load_count": 0,
    }
    if selected != expected:
        raise ValueError(f"runtime invariants failed: {selected}")
    return selected


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_bytes(data)
    temporary.replace(path)


def tool_version(argv: list[str]) -> str:
    return subprocess.check_output(argv, cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()


def render_summary(receipt: dict[str, object]) -> str:
    prompt = receipt["prompt"]
    transport = receipt["transport"]
    return "\n".join(
        [
            "# Live Claude Fable repository smoke",
            "",
            f"Source commit: `{receipt['source']['commit']}`",
            "",
            f"Claude Fable returned `{receipt['result']['actual']}` exactly from a {INPUT_BYTES:,}-byte synthetic repository dump. Azdaja sent a {prompt['bytes']:,}-byte root prompt, then executed the model-authored generic program locally against the complete input.",
            "",
            f"- Provider calls: {transport['call']}",
            f"- Provider wall time: {transport['elapsed_seconds']:.3f} seconds",
            f"- End-to-end wall time: {receipt['timings']['solo_seconds']:.3f} seconds",
            f"- Input-to-root-prompt ratio: {prompt['input_to_prompt_ratio']:,.0f}x by bytes",
            "- Local Monty executions: 1",
            "- Recursive or semantic subcalls: 0",
            "- Exact 100-byte source spans in the provider prompt: 0",
            "- Host input or scratch paths in the provider prompt: 0",
            "- The published model response contains neither the ticket nor the final answer constant.",
            "",
            "## Limits",
            "",
            *[f"- {limit}" for limit in receipt["limits"]],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes-run-inference", action="store_true")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    try:
        validate_intent(args.yes_run_inference)
        ensure_outputs_available([args.receipt, args.summary], args.force)
    except (PermissionError, FileExistsError) as error:
        print(error, file=sys.stderr)
        return 2
    if not tracked_clean():
        print("refusing live evidence from a tracked-dirty worktree", file=sys.stderr)
        return 2
    if shutil.which("claude") is None:
        print("claude CLI is unavailable", file=sys.stderr)
        return 2

    total_started = time.monotonic()
    build_record, build_output = run_command(["cargo", "build", "--release", "--locked"], timeout=600)
    if build_record["exit_code"] != 0:
        sys.stdout.buffer.write(build_output)
        return int(build_record["exit_code"])

    scratch_parent = Path(os.environ.get("JCODE_SCRATCH_DIR", tempfile.gettempdir()))
    scratch_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="azdaja-live-fable-", dir=scratch_parent) as directory:
        scratch = Path(directory)
        fixture_path = scratch / "repo.dump"
        prompt_path = scratch / "prompt.txt"
        response_path = scratch / "model-response.txt"
        trace_path = scratch / "trace.txt"
        transport_path = scratch / "transport.json"
        fixture_sha256 = write_fixture(fixture_path)

        wrapper = scratch / "transport.py"
        wrapper.write_text(TRANSPORT)
        config = scratch / "config.toml"
        config.write_text(
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
        solo_argv = [
            str(ROOT / "target/release/azdaja"),
            "solo",
            QUESTION,
            "-f",
            str(fixture_path),
        ]
        solo_record, solo_output = run_command(
            solo_argv,
            {
                "AZDAJA_HOME": str(scratch / "state"),
                "AZDAJA_CONFIG": str(config),
                "AZDAJA_SOLO_TRACE": str(trace_path),
            },
            timeout=300,
            public_argv=["target/release/azdaja", "solo", QUESTION, "-f", "<fixture>"],
            public_env={
                "AZDAJA_HOME": "<scratch>/state",
                "AZDAJA_CONFIG": "<scratch>/config.toml",
                "AZDAJA_SOLO_TRACE": "<scratch>/trace.txt",
            },
        )
        if solo_record["exit_code"] != 0:
            sys.stdout.buffer.write(solo_output)
            return int(solo_record["exit_code"])
        actual = solo_output.decode("utf-8", errors="replace").strip()
        if actual != EXPECTED:
            print(f"wrong exact output: {actual!r}", file=sys.stderr)
            return 1
        if not all(path.is_file() for path in (prompt_path, response_path, trace_path, transport_path)):
            print("live run did not produce all private evidence files", file=sys.stderr)
            return 1

        prompt = prompt_path.read_text(errors="replace")
        response = response_path.read_text(errors="replace")
        transport = json.loads(transport_path.read_text())
        validate_model_response(response)
        if transport.get("call") != 1 or transport.get("exit_code") != 0:
            raise ValueError("transport did not complete in exactly one successful call")
        if transport.get("command_template") != CLAUDE_COMMAND_TEMPLATE:
            raise ValueError("transport command template mismatch")
        if transport.get("prompt_bytes") != len(prompt.encode()):
            raise ValueError("transport prompt byte count mismatch")
        if transport.get("prompt_sha256") != sha256_bytes(prompt.encode()):
            raise ValueError("transport prompt hash mismatch")
        if transport.get("response_sha256") != sha256_bytes(response.encode()):
            raise ValueError("transport response hash mismatch")
        if len(prompt.encode()) >= 64 * 1024:
            raise ValueError("model-facing root prompt exceeded 64 KiB")
        contains_host_path = any(
            value in prompt for value in (str(ROOT), str(scratch), str(fixture_path))
        )
        if contains_host_path:
            raise ValueError("model-facing prompt contains a host path")

        scanner_source = scratch / "overlap.rs"
        scanner_binary = scratch / "overlap"
        scanner_source.write_text(OVERLAP_SCANNER)
        compile_record, compile_output = run_command(
            ["rustc", "-O", str(scanner_source), "-o", str(scanner_binary)],
            timeout=120,
            public_argv=["rustc", "-O", "<scratch>/overlap.rs", "-o", "<scratch>/overlap"],
        )
        if compile_record["exit_code"] != 0:
            sys.stdout.buffer.write(compile_output)
            return int(compile_record["exit_code"])
        overlap_record, overlap_output = run_command(
            [str(scanner_binary), str(fixture_path), str(prompt_path)],
            timeout=120,
            public_argv=["<scratch>/overlap", "<fixture>", "<model-facing-prompt>"],
        )
        if overlap_record["exit_code"] != 0:
            sys.stdout.buffer.write(overlap_output)
            return int(overlap_record["exit_code"])

        runtime = parse_runtime(trace_path)
        binary = ROOT / "target/release/azdaja"
        receipt: dict[str, object] = {
            "schema": SCHEMA,
            "artifact": ARTIFACT,
            "generated_at_utc": dt.datetime.now(dt.timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
            "source": {
                "commit": tool_version(["git", "rev-parse", "HEAD"]),
                "tracked_clean": True,
                "files": source_manifest(),
            },
            "environment": {
                "platform": platform.platform(),
                "machine": platform.machine(),
                "python": sys.version.split()[0],
                "rustc": tool_version(["rustc", "--version"]),
                "cargo": tool_version(["cargo", "--version"]),
                "claude": tool_version(["claude", "--version"]),
            },
            "model": MODEL,
            "route": "local claude CLI authenticated subscription",
            "commands": {
                "build": build_record,
                "solo": solo_record,
                "overlap_compile": compile_record,
                "overlap_check": overlap_record,
            },
            "fixture": {
                "bytes": INPUT_BYTES,
                "record_bytes": RECORD_BYTES,
                "sha256": fixture_sha256,
                "unique_blocker_occurrences": 1,
                "expected": EXPECTED,
            },
            "binary": {
                "path": "target/release/azdaja",
                "bytes": binary.stat().st_size,
                "sha256": sha256(binary),
            },
            "transport": transport,
            "prompt": {
                "bytes": len(prompt.encode()),
                "sha256": sha256_bytes(prompt.encode()),
                "input_to_prompt_ratio": INPUT_BYTES / len(prompt.encode()),
            },
            "model_response": {
                "text": response,
                "sha256": sha256_bytes(response.encode()),
                "contains_answer_constant": False,
            },
            "result": {"expected": EXPECTED, "actual": actual, "exact": True},
            "runtime": runtime,
            "checks": {
                "root_prompt_below_64_kib": True,
                "no_input_or_scratch_path_in_prompt": True,
                "no_exact_100_byte_source_span_in_prompt": True,
                "one_provider_call": True,
                "model_response_has_no_answer_constant": True,
            },
            "timings": {
                "solo_seconds": solo_record["elapsed_seconds"],
                "total_seconds": round(time.monotonic() - total_started, 6),
            },
            "limits": LIMITS,
        }

    atomic_write(args.receipt, (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode())
    atomic_write(args.summary, render_summary(receipt).encode())
    print(f"wrote {args.receipt} and {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
