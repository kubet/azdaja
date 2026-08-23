#!/usr/bin/env python3
from __future__ import annotations

import concurrent.futures
import hashlib
import importlib.util
import json
import math
import os
import re
import signal
import shutil
import shlex
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
BENCH = REPO / "bench/delta"
PLAN = BENCH / "plan.json"
PLAN_DATA = json.loads(PLAN.read_text(encoding="utf-8"))
RUNTIME = PLAN_DATA["runtime"]
BASELINE = BENCH / PLAN_DATA["baseline"]["path"]
BINARY = Path(RUNTIME["azdaja_release_path"])
CODEX = Path(RUNTIME["codex_path"])
OPENCODE = Path(RUNTIME["opencode_path"])
TIMEOUT_SECONDS = 300
TOKEN_KEYS = {
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
}

FIXTURE_SPEC = importlib.util.spec_from_file_location("delta_fixture", BENCH / "fixture.py")
if FIXTURE_SPEC is None or FIXTURE_SPEC.loader is None:
    raise RuntimeError("unable to load frozen delta fixture")
FIXTURE = importlib.util.module_from_spec(FIXTURE_SPEC)
FIXTURE_SPEC.loader.exec_module(FIXTURE)
CONTEXT_BYTES = FIXTURE.generate().encode("ascii")
GOLD = FIXTURE.expected_answer()


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


def ensure_owner_directory(path: Path) -> None:
    path.mkdir(parents=False, exist_ok=False, mode=0o700)
    path.chmod(0o700)
    metadata = path.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or path.is_symlink():
        raise RuntimeError(f"unsafe benchmark directory: {path}")
    if metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) != 0o700:
        raise RuntimeError(f"benchmark directory custody mismatch: {path}")


def managed_binary(env: dict[str, str], harness: str) -> Path:
    if harness == "codex":
        return Path(env["HOME"]) / ".agents/skills/azdaja/azdaja"
    return Path(env["XDG_CONFIG_HOME"]) / "opencode/skills/azdaja/azdaja"


def candidate_cell(model: str) -> str:
    return f'''lines = source.splitlines()
items = []
positions = {{}}
for raw in lines:
    pieces = raw.split(" || ")
    if len(pieces) != 3 or not pieces[0].startswith("Date: ") or not pieces[2].startswith("Instance: "):
        raise ValueError("record grammar mismatch")
    if "-May-" not in pieces[0]:
        continue
    value = pieces[2][10:]
    if value == "":
        raise ValueError("empty decision evidence")
    if value not in positions:
        positions[value] = len(items)
        items.append(value)
if len(items) != {FIXTURE.SELECTED_RECORDS}:
    raise ValueError("selected evidence count mismatch")
payload = []
for index in range(len(items)):
    payload.append(str(index) + "\\t" + json.dumps(items[index]))
prompt = "Classify every SMS below. Count H, where H means a legitimate requested personal, work, school, travel, appointment, delivery, repair, or community message. Treat unsolicited prize, phishing, fee, gambling, miracle-product, guaranteed-income, guaranteed-return, premium-rate, or credential-stealing promotions as not H. Return exactly one line: Answer: <H count>.\\n" + "\\n".join(payload)
if len(prompt) > 65536:
    raise ValueError("compact prompt exceeds character ceiling")
semantic_rows = llm_batch([prompt], workers=6, model={json.dumps(model)})
if len(semantic_rows) != 1:
    raise ValueError("semantic result count mismatch")
answer_lines = []
for line in semantic_rows[0].splitlines():
    line = line.strip()
    if line.startswith("Answer: "):
        answer_lines.append(line[8:])
if len(answer_lines) != 1 or not answer_lines[0].isdigit():
    raise ValueError("semantic answer contract mismatch")
ham = int(answer_lines[0])
if ham < 0 or ham > len(items):
    raise ValueError("semantic answer range mismatch")
FINAL("Answer: " + str(ham))
'''


def write_candidate_driver(work: Path, env: dict[str, str], harness: str) -> None:
    binary = managed_binary(env, harness)
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise RuntimeError(f"{harness} managed binary missing")
    model = "gpt-5.6-luna" if harness == "codex" else "openai/gpt-5.6-luna"
    driver = work / "azdaja-evaluate"
    script = f'''#!/bin/sh
set -eu
umask 077
AZDAJA={shlex.quote(str(binary))}
sid=
cleanup() {{
  if [ -n "$sid" ]; then
    "$AZDAJA" kill "$sid" >/dev/null 2>&1 || true
  fi
}}
trap cleanup EXIT HUP INT TERM
sid="$("$AZDAJA" start)"
"$AZDAJA" load "$sid" context.txt source >/dev/null
if ! cat <<'PY' | "$AZDAJA" exec "$sid" >exec.stdout 2>exec.stderr
{candidate_cell(model)}PY
then
  cat exec.stdout >&2
  cat exec.stderr >&2
  exit 1
fi
"$AZDAJA" final "$sid"
'''
    driver.write_text(script, encoding="utf-8")
    driver.chmod(0o500)


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


def integer_delta(left: Any, right: Any) -> int | None:
    return left - right if finite_int(left) and finite_int(right) else None


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
    # OpenCode exposes fresh input and cache reads as disjoint counters. The
    # benchmark normalizes both harnesses to the broker terminal contract,
    # where input is total prompt input and cache.read is its cached subset.
    normalized_input = value["input"] + cache["read"]
    return {
        "input": normalized_input,
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


def usage_uncached_total(usage: dict[str, Any]) -> int:
    uncached_input = usage["input"] - usage["cache"]["read"]
    if uncached_input < 0:
        raise ValueError("cached input exceeds input")
    return uncached_input + usage["cache"]["write"] + usage["output"] + usage["reasoning"]


def usage_gross_total(usage: dict[str, Any]) -> int:
    return usage["input"] + usage["cache"]["write"] + usage["output"] + usage["reasoning"]


def trace_summary(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {
            "attempts": 0,
            "failures": 0,
            "successes": 0,
            "usage": {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0},
            "measured_uncached_tokens": 0,
            "measured_gross_tokens": 0,
            "usage_complete": True,
            "usage_complete_successes": 0,
            "missing_usage_fields": [],
            "models": [],
            "providers": [],
            "categories": [],
            "error_categories": [],
            "error_sha256": [],
            "error_summaries": [],
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
    uncached = usage["input"] - usage["cache_read"]
    if uncached < 0:
        raise ValueError("inner cached input exceeds input")
    failure_errors = [row.get("error") for row in attempts if row.get("outcome") == "failed"]
    if not all(isinstance(error, str) for error in failure_errors):
        raise ValueError("failed inner attempts require string errors")
    scratch = os.environ.get("JCODE_SCRATCH_DIR", "")
    summaries = []
    for error in failure_errors:
        summary = error.replace(str(Path.home()), "$HOME")
        if scratch:
            summary = summary.replace(scratch, "$JCODE_SCRATCH_DIR")
        summaries.append(summary[-500:])
    return {
        "attempts": len(attempts),
        "failures": failures,
        "successes": len(successes),
        "usage": usage,
        "measured_uncached_tokens": (uncached + usage["cache_write"] + usage["output"] + usage["reasoning"]) if usage_complete else None,
        "measured_gross_tokens": (usage["input"] + usage["cache_write"] + usage["output"] + usage["reasoning"]) if usage_complete else None,
        "usage_complete": usage_complete,
        "usage_complete_successes": complete_successes,
        "missing_usage_fields": missing_usage_fields,
        "models": sorted({row["model"] for row in successes if isinstance(row.get("model"), str)}),
        "providers": sorted({row["provider"] for row in successes if isinstance(row.get("provider"), str)}),
        "categories": [row.get("category") for row in attempts],
        "error_categories": [row.get("error_category") for row in attempts],
        "error_sha256": [hashlib.sha256(error.encode()).hexdigest() for error in failure_errors],
        "error_summaries": summaries,
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
    ensure_owner_directory(root)
    ensure_owner_directory(work)
    (work / "context.txt").write_bytes(CONTEXT_BYTES)
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
        if text.count("max_calls_per_cell = 64") != 1 or text.count("cell_timeout = 60") != 1:
            raise RuntimeError(f"{harness} candidate call-limit source drift")
        config.write_text(
            text.replace("max_calls_per_cell = 64", "max_calls_per_cell = 1").replace(
                "cell_timeout = 60", "cell_timeout = 180"
            ),
            encoding="utf-8",
        )
        config.chmod(0o600)
        patched = config.read_text(encoding="utf-8")
        if "max_calls_per_cell = 1" not in patched or "cell_timeout = 180" not in patched:
            raise RuntimeError(f"{harness} candidate call-limit patch failed")
        write_candidate_driver(work, env, harness)
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


def invoke_candidate_direct(campaign: Path, harness: str) -> dict[str, Any]:
    work, env, trace = prepare_arm(campaign, harness, "candidate")
    command = [str(work / "azdaja-evaluate")]
    started = time.monotonic()
    returncode, stdout, stderr, timed_out = run_bounded(command, stdin=None, env=env, cwd=work)
    wall = time.monotonic() - started
    parse_error: str | None = None
    answer: int | None = None
    if not timed_out and returncode == 0:
        try:
            answer = exact_answer([stdout.decode("utf-8", "strict")])
        except (UnicodeError, ValueError) as exc:
            parse_error = str(exc)
    try:
        inner = trace_summary(trace)
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        inner = {"error": str(exc), "attempts": -1, "failures": -1, "successes": -1, "usage": {}, "measured_uncached_tokens": None, "measured_gross_tokens": None, "usage_complete": False, "usage_complete_successes": 0, "missing_usage_fields": [], "models": [], "providers": [], "categories": [], "error_categories": [], "error_sha256": [], "error_summaries": []}
    inner_uncached = inner.get("measured_uncached_tokens")
    inner_gross = inner.get("measured_gross_tokens")
    return {
        "harness": harness,
        "arm": "candidate",
        "execution": "direct-azdaja-driver",
        "model": "gpt-5.6-luna" if harness == "codex" else "openai/gpt-5.6-luna",
        "answer": answer,
        "correct": answer == GOLD,
        "returncode": returncode,
        "timed_out": timed_out,
        "parse_error": parse_error,
        "wall_seconds": round(wall, 3),
        "outer_usage": {"input": 0, "output": 0, "reasoning": 0, "cache": {"read": 0, "write": 0}},
        "outer_uncached_tokens": 0,
        "outer_gross_tokens": 0,
        "inner": inner,
        "measured_total_uncached_tokens": inner_uncached if finite_int(inner_uncached) else None,
        "measured_total_gross_tokens": inner_gross if finite_int(inner_gross) else None,
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
    fixture_validation = FIXTURE.validate()
    if hashlib.sha256(CONTEXT_BYTES).hexdigest() != fixture_validation["context_sha256"]:
        raise RuntimeError("generated context hash drift")
    if not BINARY.is_file() or not os.access(BINARY, os.X_OK):
        raise RuntimeError("release binary missing")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    native_results = [row for row in baseline["calls"] if row.get("arm") == "native"]
    if {row.get("harness") for row in native_results} != {"codex", "opencode"}:
        raise RuntimeError("frozen native baseline mismatch")
    scratch = Path(os.environ["JCODE_SCRATCH_DIR"])
    campaign = Path(tempfile.mkdtemp(prefix="azdaja-luna-delta-followup-", dir=scratch))
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(invoke_candidate_direct, campaign, harness) for harness in ("codex", "opencode")]
            candidate_results = [future.result() for future in futures]
        results = native_results + candidate_results
        results.sort(key=lambda row: (row["harness"], 0 if row["arm"] == "native" else 1))
        deltas: dict[str, Any] = {}
        overall = True
        for harness in ("codex", "opencode"):
            native = next(row for row in results if row["harness"] == harness and row["arm"] == "native")
            candidate = next(row for row in results if row["harness"] == harness and row["arm"] == "candidate")
            paired = native["correct"] and candidate["correct"]
            expected_model = "gpt-5.6-luna" if harness == "codex" else "openai/gpt-5.6-luna"
            native_no_inner = native["inner"].get("attempts") == 0
            calls_ok = candidate["inner"].get("attempts") == 1 and candidate["inner"].get("failures") == 0 and candidate["inner"].get("successes") == 1 and candidate["inner"].get("usage_complete") is True and candidate["inner"].get("models") == [expected_model] and candidate["inner"].get("providers") == [harness]
            outer_lower = paired and candidate["outer_uncached_tokens"] < native["outer_uncached_tokens"]
            total_lower = paired and finite_int(candidate["measured_total_uncached_tokens"]) and finite_int(native["measured_total_uncached_tokens"]) and candidate["measured_total_uncached_tokens"] < native["measured_total_uncached_tokens"]
            wall_lower = paired and candidate["wall_seconds"] < native["wall_seconds"]
            won = paired and native_no_inner and calls_ok and outer_lower and total_lower and wall_lower
            overall = overall and won
            deltas[harness] = {
                "paired_both_correct": paired,
                "native_has_zero_inner_attempts": native_no_inner,
                "candidate_exactly_one_successful_inner_attempt": calls_ok,
                "candidate_outer_minus_native_uncached_tokens": candidate["outer_uncached_tokens"] - native["outer_uncached_tokens"],
                "candidate_measured_total_minus_native_uncached_tokens": integer_delta(candidate["measured_total_uncached_tokens"], native["measured_total_uncached_tokens"]),
                "candidate_minus_native_wall_seconds": round(candidate["wall_seconds"] - native["wall_seconds"], 3),
                "outer_uncached_tokens_lower": outer_lower,
                "measured_total_uncached_tokens_lower": total_lower,
                "wall_lower": wall_lower,
                "diagnostic_win": won,
            }
        summary = {
            "schema": "azdaja-luna-delta-followup/v1",
            "plan_sha256": validated["plan_sha256"],
            "baseline_result_sha256": validated["baseline"]["sha256"],
            "baseline_plan_sha256": validated["baseline"]["plan_sha256"],
            "fixture": "synthetic clear SMS May subset with irrelevant metadata",
            "gold": GOLD,
            "new_provider_invocations": 2,
            "parallel_groups": [["codex/candidate-direct", "opencode/candidate-direct"]],
            "calls": results,
            "deltas": deltas,
            "overall_diagnostic_win": overall,
            "limitations": [
                "candidate-only follow-up against the exact frozen r8 native baseline",
                "native and candidate observations were not concurrent",
                "uncached token totals are input minus cache-read plus cache-write plus output plus reasoning",
                "all-in totals require complete five-field usage for every successful inner attempt",
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
