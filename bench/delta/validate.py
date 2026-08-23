#!/usr/bin/env python3
"""Provider-free validator for the cheap Codex/OpenCode Luna delta gate."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


class PlanError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_keys(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    require(set(value) == keys, f"{label} keys must be exact")
    return value


def contained_file(root: Path, relative: str, label: str) -> Path:
    require(isinstance(relative, str) and relative and not Path(relative).is_absolute(), f"{label} path")
    path = (root / relative).resolve(strict=True)
    require(path.is_file() and not path.is_symlink(), f"{label} must be a regular file")
    return path


def selected_evidence(context: Path) -> tuple[int, int]:
    values: list[str] = []
    for line in context.read_text(encoding="utf-8").splitlines():
        if " || Instance: " not in line:
            continue
        date, instance = line.split(" || Instance: ", 1)
        if re.search(r"\bMay\b", date):
            values.append(instance.strip())
    return len(values), len(set(values))


def validate(plan_path: Path) -> dict[str, Any]:
    plan_path = plan_path.resolve(strict=True)
    root = plan_path.parent
    plan = exact_keys(
        json.loads(plan_path.read_text(encoding="utf-8")),
        {"schema", "stage", "model", "fixture", "prompts", "execution", "gates"},
        "plan",
    )
    require(plan["schema"] == "azdaja-delta-ladder-v1", "schema")
    require(plan["stage"] == "oolong-row645-may-cheap-gate", "stage")

    model = exact_keys(plan["model"], {"codex", "opencode", "outer_reasoning", "inner_reasoning"}, "model")
    require(model == {
        "codex": "gpt-5.6-luna",
        "opencode": "openai/gpt-5.6-luna",
        "outer_reasoning": "low",
        "inner_reasoning": "low",
    }, "Luna low-reasoning contract")

    fixture = exact_keys(
        plan["fixture"],
        {"context", "context_sha256", "row", "row_sha256", "selected_records", "unique_decision_evidence", "expected_answer"},
        "fixture",
    )
    context = contained_file(root, fixture["context"], "context")
    row = contained_file(root, fixture["row"], "row")
    require(sha256(context) == fixture["context_sha256"], "context hash")
    require(sha256(row) == fixture["row_sha256"], "row hash")
    row_data = json.loads(row.read_text(encoding="utf-8"))
    require(row_data.get("answer") == "[132]", "row scorer")
    require(row_data.get("context_file") == context.name, "row context")
    selected, unique = selected_evidence(context)
    require(selected == fixture["selected_records"] == 227, "selected record count")
    require(unique == fixture["unique_decision_evidence"] == 226, "unique evidence count")
    require(fixture["expected_answer"] == 132, "expected answer")

    prompts = exact_keys(
        plan["prompts"],
        {"shared", "shared_sha256", "candidate_prefix", "candidate_prefix_sha256"},
        "prompts",
    )
    shared = contained_file(root, prompts["shared"], "shared prompt")
    prefix = contained_file(root, prompts["candidate_prefix"], "candidate prefix")
    require(sha256(shared) == prompts["shared_sha256"], "shared prompt hash")
    require(sha256(prefix) == prompts["candidate_prefix_sha256"], "candidate prefix hash")
    shared_text = shared.read_text(encoding="utf-8")
    prefix_text = prefix.read_text(encoding="utf-8")
    require("132" not in shared_text and "8638" not in shared_text, "prompt leaks gold")
    require("Group byte-identical" in shared_text and "Return exactly `Answer: number`" in shared_text, "shared prompt contract")
    for term in ("standard lane", "Do not use strict A/B", "one compact positional semantic batch", "workers=6"):
        require(term in prefix_text, f"candidate prefix missing {term}")

    execution = exact_keys(
        plan["execution"],
        {"repetitions", "retry", "timeout_seconds", "candidate_inner_attempt_ceiling", "candidate_transaction_ceiling", "max_unique_items_per_shard", "max_chars_per_shard", "workers", "parallel_groups"},
        "execution",
    )
    require(execution["repetitions"] == 1 and execution["retry"] is False, "one-shot no-retry contract")
    require(execution["timeout_seconds"] == 300, "timeout")
    require(execution["candidate_inner_attempt_ceiling"] == 1, "inner call ceiling")
    require(execution["candidate_transaction_ceiling"] == 1, "transaction ceiling")
    require(execution["max_unique_items_per_shard"] == 256, "item shard cap")
    require(execution["max_chars_per_shard"] == 65536, "character shard cap")
    require(execution["workers"] == 6, "worker cap")
    require(execution["parallel_groups"] == [
        ["codex/native", "opencode/native"],
        ["codex/candidate", "opencode/candidate"],
    ], "schedule")

    gates = exact_keys(
        plan["gates"],
        {"quality_first", "candidate_exact_required", "efficiency_requires_both_correct", "candidate_outer_tokens_must_be_lower", "candidate_total_tokens_must_be_lower", "candidate_wall_seconds_must_be_lower", "candidate_inner_attempts_must_equal", "candidate_inner_failures_must_equal", "single_run_is_diagnostic_only"},
        "gates",
    )
    require(all(value is True for key, value in gates.items() if key not in {"candidate_inner_attempts_must_equal", "candidate_inner_failures_must_equal"}), "boolean gates")
    require(gates["candidate_inner_attempts_must_equal"] == 1, "inner attempt gate")
    require(gates["candidate_inner_failures_must_equal"] == 0, "inner failure gate")

    return {
        "valid": True,
        "plan_sha256": sha256(plan_path),
        "context_sha256": sha256(context),
        "selected_records": selected,
        "unique_decision_evidence": unique,
        "maximum_candidate_inner_attempts_per_harness": 1,
        "model": model,
    }


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("plan.json")
    try:
        print(json.dumps(validate(path), sort_keys=True))
    except (OSError, UnicodeError, json.JSONDecodeError, PlanError) as exc:
        print(f"BLOCK: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
