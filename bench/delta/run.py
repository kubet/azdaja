#!/usr/bin/env python3
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import math
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
BINARY = REPO / "target/release/azdaja"
BENCH = REPO / "bench/delta"
CONTEXT = REPO / "bench/oolong/context-131072.txt"
PLAN = BENCH / "plan.json"
GOLD = 132
TIMEOUT_SECONDS = 300
TOKEN_KEYS = {
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_copy(source: Path, target: Path, mode: int = 0o600) -> None:
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    shutil.copyfile(source, target)
    target.chmod(mode)


def jsonl(raw: bytes) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(raw.decode("utf-8", "strict").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row {number} is not an object")
        rows.append(value)
    if not rows:
        raise ValueError("empty JSONL stream")
    return rows


def finite_int(value: Any) -> bool:
    return type(value) is int and value >= 0


def exact_answer(texts: list[str]) -> int:
    matches: list[int] = []
    for text in texts:
        for line in text.splitlines():
            line = line.strip()
            match = re.fullmatch(r"Answer: ([0-9]+)", line)
            if match:
                matches.append(int(match.group(1)))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one Answer line, found {len(matches)}")
    return matches[0]


def parse_codex(raw: bytes) -> tuple[int, dict[str, Any]]:
    rows = jsonl(raw)
    terminal: list[dict[str, Any]] = []
    messages: list[str] = []
    for row in rows:
        event_type = row.get("type")
        if event_type == "turn.failed" or row.get("error") is not None:
            raise ValueError("Codex stream contains failure evidence")
        if event_type == "turn.completed":
            terminal.append(row)
        elif event_type == "item.completed" and isinstance(row.get("item"), dict):
            item = row["item"]
            if item.get("type") == "agent_message" and item.get("status") in {None, "completed"}:
                text = item.get("text")
                if not isinstance(text, str):
                    raise ValueError("Codex completed message has no text")
                messages.append(text)
    if len(terminal) != 1 or len(messages) != 1:
        raise ValueError("Codex stream must contain one terminal event and one final message")
    usage = terminal[0].get("usage")
    if not isinstance(usage, dict) or set(usage) != TOKEN_KEYS:
        raise ValueError("Codex usage schema mismatch")
    if not all(finite_int(usage[key]) for key in TOKEN_KEYS):
        raise ValueError("Codex usage must be nonnegative integers")
    if usage["cached_input_tokens"] > usage["input_tokens"]:
        raise ValueError("Codex cached input exceeds input")
    normalized = {
        "input": usage["input_tokens"],
        "output": usage["output_tokens"],
        "reasoning": usage["reasoning_output_tokens"],
        "cache": {
            "read": usage["cached_input_tokens"],
            "write": usage["cache_write_input_tokens"],
        },
    }
    return exact_answer(messages), normalized


def canonical_usage(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) not in (
        {"input", "output", "reasoning", "cache"},
        {"total", "input", "output", "reasoning", "cache"},
    ):
        raise ValueError("OpenCode usage schema mismatch")
    cache = value["cache"]
    if not isinstance(cache, dict) or set(cache) != {"read", "write"}:
        raise ValueError("OpenCode cache usage schema mismatch")
    if not all(finite_int(value[key]) for key in ("input", "output", "reasoning")):
        raise ValueError("OpenCode usage fields must be nonnegative integers")
    if not all(finite_int(cache[key]) for key in ("read", "write")):
        raise ValueError("OpenCode cache fields must be nonnegative integers")
    if "total" in value and not finite_int(value["total"]):
        raise ValueError("OpenCode total usage must be a nonnegative integer")
    return {
        "input": value["input"],
        "output": value["output"],
        "reasoning": value["reasoning"],
        "cache": {"read": cache["read"], "write": cache["write"]},
    }


def parse_opencode(raw: bytes) -> tuple[int, dict[str, Any]]:
    rows = jsonl(raw)
    texts: list[str] = []
    finishes: list[dict[str, Any]] = []
    for row in rows:
        marker = row.get("type")
        if marker not in {"step_start", "text", "tool_use", "step_finish"}:
            raise ValueError(f"unknown OpenCode event {marker!r}")
        part = row.get("part")
        if not isinstance(part, dict):
            raise ValueError("OpenCode part missing")
        if marker == "text":
            if part.get("type") != "text" or not isinstance(part.get("text"), str):
                raise ValueError("OpenCode text schema mismatch")
            texts.append(part["text"])
        elif marker == "tool_use":
            state = part.get("state")
            if not isinstance(state, dict) or state.get("status") in {"error", "failed"}:
                raise ValueError("OpenCode tool failure")
        elif marker == "step_finish":
            reason = part.get("reason")
            if not isinstance(reason, str) or reason.casefold() in {"error", "failed", "failure", "retry"}:
                raise ValueError("OpenCode step failure")
            if not isinstance(part.get("cost"), (int, float)) or isinstance(part["cost"], bool) or not math.isfinite(part["cost"]):
                raise ValueError("OpenCode cost invalid")
            part = dict(part)
            part["tokens"] = canonical_usage(part.get("tokens"))
            finishes.append(part)
    if not finishes or sum(part.get("reason") == "stop" for part in finishes) != 1 or finishes[-1].get("reason") != "stop":
        raise ValueError("OpenCode stream must end with exactly one stop")
    usage = {"input": 0, "output": 0, "reasoning": 0, "cache": {"read": 0, "write": 0}}
    for part in finishes:
        step = part["tokens"]
        for key in ("input", "output", "reasoning"):
            usage[key] += step[key]
        for key in ("read", "write"):
            usage["cache"][key] += step["cache"][key]
    return exact_answer(texts), usage


def usage_total(usage: dict[str, Any]) -> int:
    return usage["input"] + usage["output"] + usage["reasoning"] + usage["cache"]["read"] + usage["cache"]["write"]


def trace_summary(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {
            "attempts": 0,
            "failures": 0,
            "successes": 0,
            "usage": {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0},
            "measured_tokens": 0,
            "usage_complete": True,
            "usage_complete_successes": 0,
            "missing_usage_fields": [],
            "models": [],
            "providers": [],
            "categories": [],
            "error_categories": [],
        }
    rows = jsonl(path.read_bytes())
    attempts = [row for row in rows if row.get("event") == "model_attempt"]
    failures = sum(row.get("outcome") == "failed" for row in attempts)
    successes = [row for row in attempts if row.get("outcome") == "succeeded"]
    usage = {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0}
    complete_successes = 0
    missing_usage_fields: list[list[str]] = []
    for row in successes:
        fields = (
            ("input_tokens", "input"),
            ("output_tokens", "output"),
            ("reasoning_tokens", "reasoning"),
            ("cache_read_tokens", "cache_read"),
            ("cache_write_tokens", "cache_write"),
        )
        missing = [source for source, _ in fields if not finite_int(row.get(source))]
        if missing:
            missing_usage_fields.append(missing)
            continue
        complete_successes += 1
        for source, target in fields:
            value = row.get(source)
            usage[target] += value
    usage_complete = complete_successes == len(successes)
    return {
        "attempts": len(attempts),
        "failures": failures,
        "successes": len(successes),
        "usage": usage,
        "measured_tokens": sum(usage.values()) if usage_complete else None,
        "usage_complete": usage_complete,
        "usage_complete_successes": complete_successes,
        "missing_usage_fields": missing_usage_fields,
        "models": sorted({row["model"] for row in successes if isinstance(row.get("model"), str)}),
        "providers": sorted({row["provider"] for row in successes if isinstance(row.get("provider"), str)}),
        "categories": [row.get("category") for row in attempts],
        "error_categories": [row.get("error_category") for row in attempts],
    }


def base_env(root: Path, harness: str) -> dict[str, str]:
    home = root / "home"
    xdg_config = root / "xdg-config"
    xdg_data = root / "xdg-data"
    xdg_cache = root / "xdg-cache"
    codex_home = root / "codex-home"
    tmp = root / "tmp"
    state = root / "state"
    for directory in (home, xdg_config, xdg_data, xdg_cache, codex_home, tmp, state):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory.chmod(0o700)
    clean_copy(Path.home() / ".codex/auth.json", codex_home / "auth.json")
    clean_copy(Path.home() / ".local/share/opencode/auth.json", xdg_data / "opencode/auth.json")
    path_parts = [
        str(Path(shutil.which("codex") or "codex").parent),
        str(Path(shutil.which("opencode") or "opencode").parent),
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/usr/sbin",
        "/sbin",
    ]
    return {
        "HOME": str(home),
        "USER": os.environ.get("USER", "vukasinkubet"),
        "LOGNAME": os.environ.get("LOGNAME", os.environ.get("USER", "vukasinkubet")),
        "PATH": ":".join(dict.fromkeys(path_parts)),
        "LANG": "C",
        "LC_ALL": "C",
        "TERM": "dumb",
        "NO_COLOR": "1",
        "TMPDIR": str(tmp),
        "CODEX_HOME": str(codex_home),
        "XDG_CONFIG_HOME": str(xdg_config),
        "XDG_DATA_HOME": str(xdg_data),
        "XDG_CACHE_HOME": str(xdg_cache),
        "AZDAJA_HOME": str(state),
        "AZDAJA_MODEL_TRACE": str(root / "work/model-trace.jsonl"),
        "OPENCODE_DISABLE_EXTERNAL_SKILLS": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "HARNESS": harness,
    }


def prepare_arm(campaign: Path, harness: str, arm: str) -> tuple[Path, dict[str, str], Path]:
    root = campaign / f"{harness}-{arm}"
    work = root / "work"
    work.mkdir(parents=True, mode=0o700)
    shutil.copyfile(CONTEXT, work / "context.txt")
    (work / "context.txt").chmod(0o400)
    env = base_env(root, harness)
    trace = Path(env["AZDAJA_MODEL_TRACE"])
    trace.touch(mode=0o600, exist_ok=False)
    trace.chmod(0o600)
    if arm == "candidate":
        installed = subprocess.run(
            [str(BINARY), "install", harness],
            env=env,
            cwd=work,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        if installed.returncode != 0:
            raise RuntimeError(f"{harness} install failed: {installed.stderr.decode('utf-8', 'replace')[-500:]}")
        config = (
            Path(env["HOME"]) / ".agents/skills/azdaja/config.toml"
            if harness == "codex"
            else Path(env["XDG_CONFIG_HOME"]) / "opencode/skills/azdaja/config.toml"
        )
        text = config.read_text(encoding="utf-8")
        if text.count("max_calls_per_cell = 64") != 1:
            raise RuntimeError(f"{harness} candidate call-limit source drift")
        config.write_text(text.replace("max_calls_per_cell = 64", "max_calls_per_cell = 1"), encoding="utf-8")
        config.chmod(0o600)
        if "max_calls_per_cell = 1" not in config.read_text(encoding="utf-8"):
            raise RuntimeError(f"{harness} candidate call-limit patch failed")
    return work, env, trace


def run_bounded(command: list[str], *, stdin: bytes | None, env: dict[str, str], cwd: Path) -> tuple[int, bytes, bytes, bool]:
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=cwd,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(input=stdin, timeout=TIMEOUT_SECONDS)
        return process.returncode, stdout, stderr, False
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate(timeout=5)
        return 124, stdout, stderr, True


def invoke(campaign: Path, harness: str, arm: str) -> dict[str, Any]:
    work, env, trace = prepare_arm(campaign, harness, arm)
    shared = (BENCH / "prompt.txt").read_text(encoding="utf-8")
    prefix = (BENCH / "candidate-prefix.txt").read_text(encoding="utf-8") if arm == "candidate" else ""
    prompt = prefix + ("\n" if prefix else "") + shared
    if harness == "codex":
        command = [
            shutil.which("codex") or "codex",
            "exec",
            "--ephemeral",
            "--skip-git-repo-check",
            "--ignore-user-config",
            "--ignore-rules",
            "--sandbox",
            "workspace-write",
            "-c",
            "model_reasoning_effort=low",
            "-c",
            "features.multi_agent=false",
            "-c",
            "features.multi_agent_v2=false",
            "-c",
            "agents.enabled=false",
            "-c",
            "web_search=disabled",
            "--json",
            "--model",
            "gpt-5.6-luna",
            "-C",
            str(work),
            "-",
        ]
        stdin = prompt.encode("utf-8")
    else:
        command = [
            shutil.which("opencode") or "opencode",
            "--pure",
            "run",
            "--model",
            "openai/gpt-5.6-luna",
            "--variant",
            "low",
            "--format",
            "json",
            "--dir",
            str(work),
            prompt,
        ]
        stdin = None
    started = time.monotonic()
    returncode, stdout, stderr, timed_out = run_bounded(command, stdin=stdin, env=env, cwd=work)
    wall = time.monotonic() - started
    parse_error: str | None = None
    answer: int | None = None
    usage = {"input": 0, "output": 0, "reasoning": 0, "cache": {"read": 0, "write": 0}}
    if not timed_out and returncode == 0:
        try:
            answer, usage = parse_codex(stdout) if harness == "codex" else parse_opencode(stdout)
        except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
            parse_error = str(exc)
    try:
        inner = trace_summary(trace)
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        inner = {"error": str(exc), "attempts": -1, "failures": -1, "successes": -1, "usage": {}, "measured_tokens": None, "usage_complete": False, "usage_complete_successes": 0, "missing_usage_fields": [], "models": [], "providers": [], "categories": [], "error_categories": []}
    outer_total = usage_total(usage)
    inner_measured = inner.get("measured_tokens")
    measured_total = outer_total + inner_measured if finite_int(inner_measured) else None
    return {
        "harness": harness,
        "arm": arm,
        "model": "gpt-5.6-luna" if harness == "codex" else "openai/gpt-5.6-luna",
        "answer": answer,
        "correct": answer == GOLD,
        "returncode": returncode,
        "timed_out": timed_out,
        "parse_error": parse_error,
        "wall_seconds": round(wall, 3),
        "outer_usage": usage,
        "outer_tokens": outer_total,
        "inner": inner,
        "measured_total_tokens": measured_total,
        "stdout_bytes": len(stdout),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_bytes": len(stderr),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "stderr_tail": stderr.decode("utf-8", "replace")[-500:],
    }


def main() -> int:
    validation = subprocess.run(
        [sys.executable, str(BENCH / "validate.py"), str(PLAN)],
        cwd=REPO,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    if validation.returncode != 0:
        raise RuntimeError(validation.stderr.decode("utf-8", "replace"))
    validated = json.loads(validation.stdout)
    if sha256(CONTEXT) != "05e4419a7280c91b3bbf1ea97629bfc235ee0eb23e67e1f0eeb21fc38b485bf2":
        raise RuntimeError("context hash drift")
    if not BINARY.is_file() or not os.access(BINARY, os.X_OK):
        raise RuntimeError("release binary missing")
    scratch = Path(os.environ["JCODE_SCRATCH_DIR"])
    campaign = Path(tempfile.mkdtemp(prefix="azdaja-luna-delta-gate-", dir=scratch))
    results: list[dict[str, Any]] = []
    try:
        for arms in (("native",), ("candidate",)):
            arm = arms[0]
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(invoke, campaign, harness, arm) for harness in ("codex", "opencode")]
                results.extend(future.result() for future in futures)
        results.sort(key=lambda row: (row["harness"], 0 if row["arm"] == "native" else 1))
        deltas: dict[str, Any] = {}
        overall = True
        for harness in ("codex", "opencode"):
            native = next(row for row in results if row["harness"] == harness and row["arm"] == "native")
            candidate = next(row for row in results if row["harness"] == harness and row["arm"] == "candidate")
            paired = native["correct"] and candidate["correct"]
            calls_ok = candidate["inner"].get("attempts") == 1 and candidate["inner"].get("failures") == 0 and candidate["inner"].get("successes") == 1 and candidate["inner"].get("usage_complete") is True
            outer_lower = paired and candidate["outer_tokens"] < native["outer_tokens"]
            total_lower = paired and finite_int(candidate["measured_total_tokens"]) and finite_int(native["measured_total_tokens"]) and candidate["measured_total_tokens"] < native["measured_total_tokens"]
            wall_lower = paired and candidate["wall_seconds"] < native["wall_seconds"]
            won = paired and calls_ok and outer_lower and total_lower and wall_lower
            overall = overall and won
            deltas[harness] = {
                "paired_both_correct": paired,
                "candidate_exactly_one_successful_inner_attempt": calls_ok,
                "candidate_outer_minus_native_tokens": candidate["outer_tokens"] - native["outer_tokens"],
                "candidate_measured_total_minus_native_tokens": candidate["measured_total_tokens"] - native["measured_total_tokens"],
                "candidate_minus_native_wall_seconds": round(candidate["wall_seconds"] - native["wall_seconds"], 3),
                "outer_tokens_lower": outer_lower,
                "measured_total_tokens_lower": total_lower,
                "wall_lower": wall_lower,
                "diagnostic_win": won,
            }
        summary = {
            "schema": "azdaja-luna-delta-cheap-gate/v1",
            "plan_sha256": validated["plan_sha256"],
            "fixture": "OOLONG row 645 May subset",
            "gold": GOLD,
            "parallel_groups": [["codex/native", "opencode/native"], ["codex/candidate", "opencode/candidate"]],
            "calls": results,
            "deltas": deltas,
            "overall_diagnostic_win": overall,
            "limitations": [
                "one paired observation per harness",
                "all-in token totals require complete input/output/reasoning/cache-read/cache-write usage for every successful inner attempt",
                "diagnostic result, not a robustness or general-superiority claim",
            ],
            "temporary_execution_data_deleted": True,
        }
        print(json.dumps(summary, sort_keys=True))
        return 0 if overall else 2
    finally:
        shutil.rmtree(campaign, ignore_errors=False)


if __name__ == "__main__":
    raise SystemExit(main())
