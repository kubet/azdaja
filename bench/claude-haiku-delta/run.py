#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
BENCH = REPO / "bench/delta"
SCRATCH = Path(os.environ.get("JCODE_SCRATCH_DIR") or (Path.home() / ".jcode" / "scratch"))
CLAUDE = Path(os.environ.get("CLAUDE_BIN") or shutil.which("claude") or "/nonexistent/claude")
AZDAJA = Path(os.environ.get("AZDAJA_CLAUDE_BINARY") or str(Path.home() / ".claude/skills/azdaja/azdaja"))
MODEL = "haiku"
REPETITIONS = int(os.environ.get("AZDAJA_DELTA_REPETITIONS", "5"))
ARM_FILTER = os.environ.get("AZDAJA_DELTA_ARMS", "native,candidate").split(",")
TIMEOUT = int(os.environ.get("AZDAJA_DELTA_TIMEOUT", "300"))
GOLD = 42

spec = importlib.util.spec_from_file_location("delta_fixture", BENCH / "fixture.py")
if spec is None or spec.loader is None:
    raise RuntimeError("fixture import failed")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
CONTEXT = fixture.generate().encode("ascii")
PROMPT = (BENCH / "prompt.txt").read_bytes()
CANDIDATE_PROMPT = (BENCH / "candidate-prefix.txt").read_bytes()
if hashlib.sha256(CONTEXT).hexdigest() != "cb2b72c4a945c07186044aad2ddfcb94fa9e1bbadd4bae03f59843568d655d79":
    raise RuntimeError("fixture hash drift")
if fixture.expected_answer() != GOLD:
    raise RuntimeError("gold drift")


def private_dir(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=False)
    path.chmod(0o700)


def exact_answer(text: str) -> int | None:
    matches = re.findall(r"(?m)^Answer: ([0-9]+)\s*$", text)
    if len(matches) != 1:
        return None
    return int(matches[0])


def json_envelope(raw: bytes) -> dict[str, Any]:
    value = json.loads(raw.decode("utf-8", "strict"))
    if not isinstance(value, dict):
        raise ValueError("Claude envelope is not an object")
    return value


def result_text(envelope: dict[str, Any]) -> str:
    result = envelope.get("result")
    if isinstance(result, str):
        return result
    structured = envelope.get("structured_output")
    if isinstance(structured, str):
        return structured
    return ""


def usage_from_envelope(envelope: dict[str, Any]) -> dict[str, int | None]:
    usage = envelope.get("usage")
    if not isinstance(usage, dict):
        return {
            "input": None,
            "output": None,
            "cache_read": None,
            "cache_write": None,
            "uncached": None,
            "gross": None,
        }
    def number(*names: str) -> int | None:
        for name in names:
            value = usage.get(name)
            if type(value) is int and value >= 0:
                return value
        return None
    input_tokens = number("input_tokens", "input")
    output_tokens = number("output_tokens", "output")
    cache_read = number("cache_read_input_tokens", "cache_read_tokens", "cache_read")
    cache_write = number("cache_creation_input_tokens", "cache_write_input_tokens", "cache_write_tokens", "cache_write")
    if cache_read is None:
        cache_read = 0
    if cache_write is None:
        cache_write = 0
    uncached = None
    gross = None
    if input_tokens is not None and output_tokens is not None:
        # Anthropic reports fresh input separately from cache reads. Cache creation is billed input.
        uncached = input_tokens + cache_write + output_tokens
        gross = input_tokens + cache_read + cache_write + output_tokens
    return {
        "input": input_tokens,
        "output": output_tokens,
        "cache_read": cache_read,
        "cache_write": cache_write,
        "uncached": uncached,
        "gross": gross,
    }


def inner_trace(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"attempts": 0, "successes": 0, "failures": 0, "usage_complete": False, "uncached": None, "gross": None, "models": [], "providers": []}
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if isinstance(value, dict) and value.get("event") == "model_attempt":
                rows.append(value)
    success = [row for row in rows if row.get("outcome") == "succeeded"]
    failure = [row for row in rows if row.get("outcome") == "failed"]
    fields = ("input_tokens", "output_tokens", "reasoning_tokens", "cache_read_tokens", "cache_write_tokens")
    complete = all(all(type(row.get(field)) is int and row[field] >= 0 for field in fields) for row in success)
    uncached = gross = None
    if success and complete:
        total = {field: sum(row[field] for row in success) for field in fields}
        uncached = total["input_tokens"] - total["cache_read_tokens"] + total["cache_write_tokens"] + total["output_tokens"] + total["reasoning_tokens"]
        gross = total["input_tokens"] + total["cache_write_tokens"] + total["output_tokens"] + total["reasoning_tokens"]
    return {
        "attempts": len(rows),
        "successes": len(success),
        "failures": len(failure),
        "usage_complete": bool(success) and complete,
        "uncached": uncached,
        "gross": gross,
        "models": sorted({row.get("model") for row in success if isinstance(row.get("model"), str)}),
        "providers": sorted({row.get("provider") for row in success if isinstance(row.get("provider"), str)}),
    }


def enrich_inner_from_claude_envelope(trace: dict[str, Any], path: Path) -> dict[str, Any]:
    if not path.exists():
        return trace
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(envelope, dict):
            return trace
        usage = usage_from_envelope(envelope)
        if type(usage.get("uncached")) is int and type(usage.get("gross")) is int:
            trace["uncached"] = usage["uncached"]
            trace["gross"] = usage["gross"]
            trace["usage_complete"] = True
        model_usage = envelope.get("modelUsage")
        if isinstance(model_usage, dict):
            trace["models"] = sorted(key for key in model_usage if isinstance(key, str))
        trace["providers"] = ["claude-code"]
    except (OSError, UnicodeError, json.JSONDecodeError):
        pass
    return trace


def wrapper_usage(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        return None
    usage = usage_from_envelope(value)
    required = ("input", "output", "cache_read", "cache_write", "uncached", "gross")
    if not all(type(usage.get(key)) is int and usage[key] >= 0 for key in required):
        return None
    return {**usage, "model": MODEL, "provider": "claude-code"}


def claude_command(tools: str) -> list[str]:
    command = [
        str(CLAUDE),
        "--print",
        "--safe-mode",
        "--no-session-persistence",
        "--disable-slash-commands",
        "--no-chrome",
        "--strict-mcp-config",
        "--mcp-config", '{"mcpServers":{}}',
        "--settings", "{}",
        "--setting-sources", "",
        "--tools", tools,
        "--permission-mode", "dontAsk",
        "--effort", "low",
        "--output-format", "json",
        "--model", MODEL,
    ]
    if tools == "Bash":
        command += ["--allowedTools", "Bash(./azdaja-evaluate)"]
    return command


def base_env(work: Path) -> dict[str, str]:
    env = dict(os.environ)
    env.update({
        "NO_COLOR": "1",
        "CI": "1",
        "CLAUDE_CODE_SAFE_MODE": "1",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        "TMPDIR": str(work / "tmp"),
        "XDG_CONFIG_HOME": str(work / "xdg-config"),
        "XDG_CACHE_HOME": str(work / "xdg-cache"),
        "XDG_DATA_HOME": str(work / "xdg-data"),
    })
    for name in ("tmp", "xdg-config", "xdg-cache", "xdg-data"):
        (work / name).mkdir(mode=0o700)
    return env


CELL = r'''lines = source.splitlines()
items = []
positions = {}
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
if len(items) != 64:
    raise ValueError("selected evidence count mismatch")
payload = []
for index in range(len(items)):
    payload.append(str(index) + "\t" + json.dumps(items[index]))
prompt = "Classify every SMS below. Count H, where H means a legitimate requested personal, work, school, travel, appointment, delivery, repair, or community message. Treat unsolicited prize, phishing, fee, gambling, miracle-product, guaranteed-income, guaranteed-return, premium-rate, or credential-stealing promotions as not H. Return exactly one line: Answer: number.\n" + "\n".join(payload)
if len(prompt) > 65536:
    raise ValueError("compact prompt exceeds character ceiling")
semantic_rows = llm_batch([prompt], workers=6, model="haiku")
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


def prepare_native(root: Path) -> tuple[Path, dict[str, str]]:
    work = root / "work"
    private_dir(root)
    private_dir(work)
    (work / "context.txt").write_bytes(CONTEXT)
    (work / "context.txt").chmod(0o400)
    return work, base_env(work)


def prepare_candidate(root: Path) -> tuple[Path, dict[str, str], Path, Path]:
    work, env = prepare_native(root)
    state = work / ".azdaja-state"
    state.mkdir(mode=0o700)
    trace = work / "model-trace.jsonl"
    trace.touch(mode=0o600)
    inner_envelope = work / "inner-envelope.json"
    inner = work / "inner-claude"
    inner.write_text(
        "#!/bin/sh\nset -eu\n"
        + "out=" + json.dumps(str(inner_envelope)) + "\n"
        + "tmp=\"$out.tmp\"\n"
        + "trap 'rm -f \"$tmp\"' EXIT HUP INT TERM\n"
        + str(CLAUDE) + " --print --safe-mode --no-session-persistence --disable-slash-commands --no-chrome --strict-mcp-config --mcp-config '{\"mcpServers\":{}}' --settings '{}' --setting-sources '' --tools '' --permission-mode dontAsk --effort low --output-format json --model \"$1\" > \"$tmp\"\n"
        + "mv \"$tmp\" \"$out\"\n"
        + "python3 - \"$out\" <<'PY'\n"
        + "import json, sys\nvalue=json.load(open(sys.argv[1], encoding='utf-8'))\nresult=value.get('result')\nif not isinstance(result, str) or not result.strip():\n    raise SystemExit(2)\nprint(result.strip())\n"
        + "PY\n",
        encoding="utf-8",
    )
    inner.chmod(0o500)
    config = work / "config.toml"
    config.write_text(
        'sub_llm_cmd = "' + str(inner) + ' {model}"\n'
        'default_model = "haiku"\n'
        'output_cap = 8192\n'
        'max_depth = 1\n'
        'sub_timeout = 300\n'
        'max_sessions = 1\n'
        'cell_timeout = 180\n'
        'idle_timeout = 1800\n'
        'clean_patterns = []\n'
        'jcode_provider = "openai"\n'
        'jcode_reasoning = "low"\n'
        'max_calls_per_cell = 1\n',
        encoding="utf-8",
    )
    config.chmod(0o400)
    driver = work / "azdaja-evaluate"
    driver.write_text(
        "#!/bin/sh\nset -eu\numask 077\n"
        + "AZDAJA=" + json.dumps(str(AZDAJA)) + "\n"
        + "export AZDAJA_HOME=" + json.dumps(str(state)) + "\n"
        + "export AZDAJA_CONFIG=" + json.dumps(str(config)) + "\n"
        + "export AZDAJA_MODEL_TRACE=" + json.dumps(str(trace)) + "\n"
        + "sid=\ncleanup(){ if [ -n \"$sid\" ]; then \"$AZDAJA\" kill \"$sid\" >/dev/null 2>&1 || true; fi; }\n"
        + "trap cleanup EXIT HUP INT TERM\n"
        + "sid=\"$(\"$AZDAJA\" start)\"\n"
        + "\"$AZDAJA\" load \"$sid\" context.txt source >/dev/null\n"
        + "cat <<'PY' | \"$AZDAJA\" exec \"$sid\" >/dev/null\n"
        + CELL
        + "PY\n"
        + "\"$AZDAJA\" final \"$sid\"\n",
        encoding="utf-8",
    )
    driver.chmod(0o500)
    env.update({
        "AZDAJA_HOME": str(state),
        "AZDAJA_CONFIG": str(config),
        "AZDAJA_MODEL_TRACE": str(trace),
    })
    return work, env, trace, inner_envelope


def run_arm(campaign: Path, repetition: int, arm: str) -> dict[str, Any]:
    root = campaign / f"r{repetition}-{arm}"
    if arm == "native":
        work, env = prepare_native(root)
        command = claude_command("Bash,Read,Grep")
        prompt = PROMPT
        trace = None
        inner_usage_path = None
    else:
        work, env, trace, inner_usage_path = prepare_candidate(root)
        command = claude_command("Bash")
        prompt = CANDIDATE_PROMPT
    start = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(command, cwd=work, env=env, input=prompt, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=TIMEOUT, check=False)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
        if isinstance(stdout, str):
            stdout = stdout.encode("utf-8", "replace")
        if isinstance(stderr, str):
            stderr = stderr.encode("utf-8", "replace")
        completed = subprocess.CompletedProcess(command, 124, stdout, stderr)
    wall = time.monotonic() - start
    envelope: dict[str, Any] = {}
    parse_error = "TimeoutExpired" if timed_out else None
    answer = None
    if not timed_out:
        try:
            envelope = json_envelope(completed.stdout)
            answer = exact_answer(result_text(envelope))
            if answer is None:
                parse_error = "AnswerContractError"
        except Exception as exc:
            parse_error = type(exc).__name__
    outer = usage_from_envelope(envelope)
    inner = inner_trace(trace) if trace is not None else {"attempts": 0, "successes": 0, "failures": 0, "usage_complete": True, "uncached": 0, "gross": 0, "models": [], "providers": []}
    measured_wrapper = wrapper_usage(inner_usage_path)
    if measured_wrapper is not None and inner.get("attempts") == 1 and inner.get("successes") == 1 and inner.get("failures") == 0:
        inner["usage_complete"] = True
        inner["uncached"] = measured_wrapper["uncached"]
        inner["gross"] = measured_wrapper["gross"]
        inner["models"] = [measured_wrapper["model"]]
        inner["providers"] = [measured_wrapper["provider"]]
    if trace is not None:
        inner = enrich_inner_from_claude_envelope(inner, work / "inner-envelope.json")
    total_uncached = None
    total_gross = None
    if type(outer.get("uncached")) is int and type(inner.get("uncached")) is int:
        total_uncached = int(outer["uncached"]) + int(inner["uncached"])
    if type(outer.get("gross")) is int and type(inner.get("gross")) is int:
        total_gross = int(outer["gross"]) + int(inner["gross"])
    row = {
        "pair": repetition,
        "arm": arm,
        "model_alias": MODEL,
        "answer": answer,
        "correct": answer == GOLD,
        "returncode": completed.returncode,
        "timed_out": timed_out,
        "wall_seconds": round(wall, 3),
        "parse_error": parse_error,
        "result_text": f"Answer: {answer}" if answer is not None else "",
        "outer_usage": outer,
        "inner": inner,
        "total_uncached": total_uncached,
        "total_gross": total_gross,
        "num_turns": envelope.get("num_turns") if type(envelope.get("num_turns")) is int else None,
        "duration_ms": envelope.get("duration_ms") if type(envelope.get("duration_ms")) is int else None,
        "duration_api_ms": envelope.get("duration_api_ms") if type(envelope.get("duration_api_ms")) is int else None,
        "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        "stdout_bytes": len(completed.stdout),
        "stderr_bytes": len(completed.stderr),
    }
    print("TRIAL " + json.dumps({key: row[key] for key in ("pair", "arm", "correct", "answer", "returncode", "timed_out", "wall_seconds", "total_uncached", "num_turns")}, sort_keys=True), flush=True)
    return row


def mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 3) if values else None


def median(values: list[float]) -> float | int | None:
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return round((ordered[middle - 1] + ordered[middle]) / 2, 3)


def build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    native = [row for row in rows if row["arm"] == "native"]
    candidate = [row for row in rows if row["arm"] == "candidate"]
    paired = []
    for repetition in range(1, REPETITIONS + 1):
        n = next(row for row in native if row["pair"] == repetition)
        c = next(row for row in candidate if row["pair"] == repetition)
        paired.append({
            "pair": repetition,
            "both_correct": n["correct"] and c["correct"],
            "candidate_minus_native_wall_seconds": round(c["wall_seconds"] - n["wall_seconds"], 3),
            "candidate_minus_native_uncached": (c["total_uncached"] - n["total_uncached"]) if type(c["total_uncached"]) is int and type(n["total_uncached"]) is int else None,
        })
    native_uncached = [row["total_uncached"] for row in native if type(row["total_uncached"]) is int]
    candidate_uncached = [row["total_uncached"] for row in candidate if type(row["total_uncached"]) is int]
    native_wall = [float(row["wall_seconds"]) for row in native]
    candidate_wall = [float(row["wall_seconds"]) for row in candidate]
    native_turns = [row["num_turns"] for row in native if type(row["num_turns"]) is int]
    candidate_turns = [row["num_turns"] for row in candidate if type(row["num_turns"]) is int]
    native_mean_uncached = mean(native_uncached)
    candidate_mean_uncached = mean(candidate_uncached)
    native_mean_wall = mean(native_wall)
    candidate_mean_wall = mean(candidate_wall)
    models = sorted({model for row in candidate for model in row["inner"].get("models", []) if isinstance(model, str)})
    summary = {
        "schema": "claude-code-haiku45-azdaja-delta/v2",
        "fixture_sha256": hashlib.sha256(CONTEXT).hexdigest(),
        "fixture_bytes": len(CONTEXT),
        "gold": GOLD,
        "model_alias": MODEL,
        "pairs": REPETITIONS,
        "native_correct": sum(row["correct"] for row in native),
        "candidate_correct": sum(row["correct"] for row in candidate),
        "native_mean_wall_seconds": native_mean_wall,
        "candidate_mean_wall_seconds": candidate_mean_wall,
        "native_median_wall_seconds": median(native_wall),
        "candidate_median_wall_seconds": median(candidate_wall),
        "native_mean_uncached": native_mean_uncached,
        "candidate_mean_uncached": candidate_mean_uncached,
        "native_median_uncached": median(native_uncached),
        "candidate_median_uncached": median(candidate_uncached),
        "native_mean_turns": round(mean(native_turns), 2) if native_turns else None,
        "candidate_mean_turns": round(mean(candidate_turns), 2) if candidate_turns else None,
        "candidate_exactly_one_successful_inner_each": all(row["inner"]["attempts"] == 1 and row["inner"]["successes"] == 1 and row["inner"]["failures"] == 0 and row["inner"]["usage_complete"] for row in candidate),
        "resolved_candidate_inner_model": models[0] if len(models) == 1 else None,
        "paired": paired,
        "rows": rows,
        "limitations": [
            f"{REPETITIONS} paired trials on one deterministic synthetic projection task",
            "Claude model alias haiku was used; resolved model identity is taken from Azdaja inner trace when available",
            "candidate includes a Claude outer routing turn plus one Claude inner semantic turn",
            "native may choose its own Read/Grep/Bash projection strategy",
            "diagnostic evidence, not a broad superiority claim",
        ],
    }
    if native_mean_uncached and candidate_mean_uncached is not None:
        summary["uncached_reduction_percent"] = round((native_mean_uncached - candidate_mean_uncached) / native_mean_uncached * 100, 1)
    else:
        summary["uncached_reduction_percent"] = None
    if native_mean_wall and candidate_mean_wall is not None:
        summary["wall_reduction_percent"] = round((native_mean_wall - candidate_mean_wall) / native_mean_wall * 100, 1)
    else:
        summary["wall_reduction_percent"] = None
    return summary


def main() -> int:
    if not CLAUDE.is_file() or not os.access(CLAUDE, os.X_OK):
        raise RuntimeError("Claude executable unavailable")
    if not AZDAJA.is_file() or not os.access(AZDAJA, os.X_OK):
        raise RuntimeError("managed Azdaja binary unavailable")
    campaign = Path(tempfile.mkdtemp(prefix="claude-haiku45-azdaja-delta-", dir=SCRATCH))
    campaign.chmod(0o700)
    rows: list[dict[str, Any]] = []
    orders = []
    for repetition in range(1, REPETITIONS + 1):
        order = ("native", "candidate") if repetition % 2 == 1 else ("candidate", "native")
        orders.append(tuple(arm for arm in order if arm in ARM_FILTER))
    try:
        for repetition, order in enumerate(orders, 1):
            for arm in order:
                rows.append(run_arm(campaign, repetition, arm))
        native = [row for row in rows if row["arm"] == "native"]
        candidate = [row for row in rows if row["arm"] == "candidate"]
        if not native or not candidate:
            summary = {"schema": "claude-code-haiku45-azdaja-delta/pilot", "rows": rows}
            result_path = Path(os.environ.get("AZDAJA_DELTA_RESULT") or str(SCRATCH / "claude-haiku45-azdaja-delta-result.json"))
            result_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            result_path.chmod(0o600)
            print("RESULT " + str(result_path), flush=True)
            return 0
        summary = build_summary(rows)
        result_path = Path(os.environ.get("AZDAJA_DELTA_RESULT") or str(SCRATCH / "claude-haiku45-azdaja-delta-result.json"))
        result_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        result_path.chmod(0o600)
        print("SUMMARY " + json.dumps({key: summary[key] for key in ("native_correct", "candidate_correct", "native_mean_wall_seconds", "candidate_mean_wall_seconds", "native_mean_uncached", "candidate_mean_uncached", "candidate_exactly_one_successful_inner_each")}, sort_keys=True), flush=True)
        print("RESULT " + str(result_path), flush=True)
        complete = all(row["returncode"] == 0 and not row["timed_out"] and type(row["answer"]) is int and type(row["total_uncached"]) is int and type(row["num_turns"]) is int for row in rows)
        return 0 if complete else 2
    finally:
        shutil.rmtree(campaign, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
