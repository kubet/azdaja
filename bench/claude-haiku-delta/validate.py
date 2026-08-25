#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BENCH = Path(__file__).resolve().parent
PLAN = BENCH / "plan.json"


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_number(value: Any) -> bool:
    return type(value) in {int, float} and not isinstance(value, bool)


def mean(rows: list[dict[str, Any]], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def median(rows: list[dict[str, Any]], key: str) -> float:
    return float(statistics.median(row[key] for row in rows))


def load_fixture(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("claude_delta_fixture", path)
    if spec is None or spec.loader is None:
        raise ValidationError("fixture import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(plan_path: Path = PLAN) -> dict[str, Any]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    require(plan.get("schema") == "claude-code-haiku45-azdaja-delta-plan/v1", "plan schema mismatch")
    require("not a broad superiority" in plan.get("claim_boundary", ""), "claim boundary missing")

    runner = (BENCH / plan["runner"]["path"]).resolve()
    result_path = (BENCH / plan["result"]["path"]).resolve()
    fixture_path = (BENCH / plan["fixture"]["generator"]).resolve()
    native_prompt = (BENCH / plan["prompts"]["native"]).resolve()
    candidate_prompt = (BENCH / plan["prompts"]["candidate"]).resolve()
    for path in (runner, result_path, fixture_path, native_prompt, candidate_prompt):
        require(path.is_file() and not path.is_symlink(), f"unsafe or missing benchmark file: {path.name}")

    require(sha256(runner) == plan["runner"]["sha256"], "runner hash mismatch")
    require(sha256(result_path) == plan["result"]["sha256"], "result hash mismatch")
    require(sha256(fixture_path) == plan["fixture"]["generator_sha256"], "fixture generator hash mismatch")
    require(sha256(native_prompt) == plan["prompts"]["native_sha256"], "native prompt hash mismatch")
    require(sha256(candidate_prompt) == plan["prompts"]["candidate_sha256"], "candidate prompt hash mismatch")

    runner_text = runner.read_text(encoding="utf-8")
    require("/Users/" not in runner_text, "runner contains a private absolute user path")
    require('max_calls_per_cell = 1' in runner_text, "runner does not enforce one inner call")
    require('Bash(./azdaja-evaluate)' in runner_text, "runner does not bind the exact candidate command")

    fixture = load_fixture(fixture_path)
    fixture_summary = fixture.validate()
    require(fixture_summary["context_sha256"] == plan["fixture"]["generated_context_sha256"], "generated context hash mismatch")
    require(fixture_summary["context_bytes"] == plan["fixture"]["context_bytes"], "context byte count mismatch")
    require(fixture_summary["total_records"] == plan["fixture"]["total_records"], "record count mismatch")
    require(fixture_summary["selected_records"] == plan["fixture"]["selected_records"], "selected count mismatch")
    require(fixture_summary["expected_answer"] == plan["fixture"]["expected_answer"], "fixture gold mismatch")

    raw = result_path.read_text(encoding="utf-8")
    for forbidden in ("/Users/", "AZDAJA_JCODE_CHALLENGE=", "auth.json", "api_key", "access_token", "refresh_token"):
        require(forbidden not in raw, f"result contains forbidden private material: {forbidden}")
    result = json.loads(raw)
    require(result.get("schema") == "claude-code-haiku45-azdaja-delta/v2", "result schema mismatch")
    require(result.get("pairs") == 5, "pair count mismatch")
    require(result.get("gold") == 42, "result gold mismatch")
    require(result.get("model_alias") == "haiku", "model alias mismatch")
    require(result.get("resolved_candidate_inner_model") == "claude-haiku-4-5-20251001", "resolved model mismatch")

    rows = result.get("rows")
    require(isinstance(rows, list) and len(rows) == 10, "result must contain ten rows")
    native = [row for row in rows if row.get("arm") == "native"]
    candidate = [row for row in rows if row.get("arm") == "candidate"]
    require(len(native) == len(candidate) == 5, "arm row count mismatch")
    require({row.get("pair") for row in rows} == set(range(1, 6)), "pair IDs mismatch")
    for pair in range(1, 6):
        require(sum(row.get("pair") == pair and row.get("arm") == "native" for row in rows) == 1, f"pair {pair} native multiplicity mismatch")
        require(sum(row.get("pair") == pair and row.get("arm") == "candidate" for row in rows) == 1, f"pair {pair} candidate multiplicity mismatch")

    for row in rows:
        require(row.get("returncode") == 0, "nonzero Claude return code")
        require(type(row.get("answer")) is int, "answer is not an integer")
        require(type(row.get("correct")) is bool, "correctness is not boolean")
        require(type(row.get("num_turns")) is int and row["num_turns"] > 0, "turn count invalid")
        require(type(row.get("total_uncached")) is int and row["total_uncached"] > 0, "uncached usage invalid")
        require(exact_number(row.get("wall_seconds")) and row["wall_seconds"] > 0, "wall time invalid")
        require(row.get("result_text") in {"Answer: 42", "Answer: 44"}, "unexpected retained result text")

    require(sum(row["correct"] for row in native) == 4, "native exact count mismatch")
    require(sum(row["correct"] for row in candidate) == 5, "candidate exact count mismatch")
    require(sorted(row["answer"] for row in native) == [42, 42, 42, 42, 44], "native answer multiset mismatch")
    for row in candidate:
        require(row["answer"] == 42 and row["correct"] is True, "candidate answer mismatch")
        inner = row.get("inner")
        require(isinstance(inner, dict), "candidate inner summary missing")
        require(inner.get("attempts") == 1 and inner.get("successes") == 1 and inner.get("failures") == 0, "candidate inner call count mismatch")
        require(inner.get("usage_complete") is True, "candidate inner usage incomplete")
        require(inner.get("models") == ["claude-haiku-4-5-20251001"], "candidate inner model mismatch")
        require(inner.get("providers") == ["claude-code"], "candidate inner provider mismatch")

    expected = {
        "native_correct": sum(row["correct"] for row in native),
        "candidate_correct": sum(row["correct"] for row in candidate),
        "native_mean_uncached": round(mean(native, "total_uncached"), 3),
        "candidate_mean_uncached": round(mean(candidate, "total_uncached"), 3),
        "native_median_uncached": median(native, "total_uncached"),
        "candidate_median_uncached": median(candidate, "total_uncached"),
        "native_mean_wall_seconds": round(mean(native, "wall_seconds"), 3),
        "candidate_mean_wall_seconds": round(mean(candidate, "wall_seconds"), 3),
        "native_median_wall_seconds": median(native, "wall_seconds"),
        "candidate_median_wall_seconds": median(candidate, "wall_seconds"),
        "native_mean_turns": round(mean(native, "num_turns"), 2),
        "candidate_mean_turns": round(mean(candidate, "num_turns"), 2),
    }
    expected["uncached_reduction_percent"] = round((expected["native_mean_uncached"] - expected["candidate_mean_uncached"]) / expected["native_mean_uncached"] * 100, 1)
    expected["wall_reduction_percent"] = round((expected["native_mean_wall_seconds"] - expected["candidate_mean_wall_seconds"]) / expected["native_mean_wall_seconds"] * 100, 1)
    for key, value in expected.items():
        require(result.get(key) == value, f"summary mismatch: {key}")

    require(result.get("candidate_exactly_one_successful_inner_each") is True, "candidate one-call summary mismatch")
    require(plan["result"]["pairs"] == result["pairs"], "plan/result pair mismatch")
    require(plan["result"]["native_correct"] == result["native_correct"], "plan/result native quality mismatch")
    require(plan["result"]["candidate_correct"] == result["candidate_correct"], "plan/result candidate quality mismatch")
    for key in ("native_median_uncached", "candidate_median_uncached", "native_median_wall_seconds", "candidate_median_wall_seconds"):
        require(plan["result"][key] == result[key], f"plan/result mismatch: {key}")

    return {
        "schema": "claude-code-haiku45-azdaja-delta-validation/v1",
        "pairs": result["pairs"],
        "native_correct": result["native_correct"],
        "candidate_correct": result["candidate_correct"],
        "native_median_uncached": result["native_median_uncached"],
        "candidate_median_uncached": result["candidate_median_uncached"],
        "native_median_wall_seconds": result["native_median_wall_seconds"],
        "candidate_median_wall_seconds": result["candidate_median_wall_seconds"],
        "privacy_scan": "passed",
        "hash_bindings": "passed",
    }


def main() -> int:
    try:
        print(json.dumps(validate(), sort_keys=True))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, ValidationError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
