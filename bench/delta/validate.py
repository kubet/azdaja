#!/usr/bin/env python3
"""Provider-free validator for the cheap Codex/OpenCode Luna delta gate."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
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


def validate(plan_path: Path, repo_root: Path | None = None) -> dict[str, Any]:
    plan_path = plan_path.resolve(strict=True)
    root = plan_path.parent
    plan = exact_keys(
        json.loads(plan_path.read_text(encoding="utf-8")),
        {"schema", "stage", "model", "source", "runtime", "fixture", "prompts", "runner", "baseline", "execution", "accounting", "gates"},
        "plan",
    )
    require(plan["schema"] == "azdaja-delta-followup-v1", "schema")
    require(plan["stage"] == "synthetic-clear-sms-metadata-projection-r9-direct-followup", "stage")

    model = exact_keys(plan["model"], {"codex", "opencode", "outer_reasoning", "inner_reasoning"}, "model")
    require(model == {
        "codex": "gpt-5.6-luna",
        "opencode": "openai/gpt-5.6-luna",
        "outer_reasoning": "low",
        "inner_reasoning": "low",
    }, "Luna low-reasoning contract")

    repo = repo_root.resolve(strict=True) if repo_root is not None else root.parents[1]
    source = exact_keys(
        plan["source"],
        {"candidate_commit", "candidate_tree", "src_lib_sha256", "src_main_sha256", "skill_sha256", "config_sha256", "cargo_lock_sha256"},
        "source",
    )
    for key, value in source.items():
        length = 40 if key in {"candidate_commit", "candidate_tree"} else 64
        require(
            isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{length}}}", value),
            f"source {key}",
        )
    require(sha256(repo / "src/lib.rs") == source["src_lib_sha256"], "src/lib.rs hash")
    require(sha256(repo / "src/main.rs") == source["src_main_sha256"], "src/main.rs hash")
    require(sha256(repo / "assets/SKILL.md") == source["skill_sha256"], "skill hash")
    require(sha256(repo / "assets/config.toml") == source["config_sha256"], "config hash")
    require(sha256(repo / "Cargo.lock") == source["cargo_lock_sha256"], "Cargo.lock hash")
    tree = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{source['candidate_commit']}^{{tree}}"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()
    require(tree == source["candidate_tree"], "candidate source tree")
    ancestry = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", source["candidate_commit"], "HEAD"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    require(ancestry.returncode == 0, "candidate source commit is not current ancestry")

    runtime = exact_keys(
        plan["runtime"],
        {"azdaja_release_path", "azdaja_release_sha256", "codex_path", "codex_sha256", "codex_version", "opencode_path", "opencode_sha256", "opencode_version"},
        "runtime",
    )
    for key in ("azdaja_release_path", "codex_path", "opencode_path"):
        require(isinstance(runtime[key], str) and Path(runtime[key]).is_absolute(), f"runtime {key}")
    for key in ("azdaja_release_sha256", "codex_sha256", "opencode_sha256"):
        require(isinstance(runtime[key], str) and re.fullmatch(r"[0-9a-f]{64}", runtime[key]) is not None, f"runtime {key}")
    azdaja_binary = Path(runtime["azdaja_release_path"]).resolve(strict=True)
    codex_binary = Path(runtime["codex_path"]).resolve(strict=True)
    opencode_binary = Path(runtime["opencode_path"]).resolve(strict=True)
    require(azdaja_binary == (repo / "target/release/azdaja").resolve(strict=True), "Azdaja release path")
    require(codex_binary == Path(shutil.which("codex") or "").resolve(strict=True), "Codex executable path")
    require(opencode_binary == Path(shutil.which("opencode") or "").resolve(strict=True), "OpenCode executable path")
    require(sha256(azdaja_binary) == runtime["azdaja_release_sha256"], "Azdaja release hash")
    require(sha256(codex_binary) == runtime["codex_sha256"], "Codex executable hash")
    require(sha256(opencode_binary) == runtime["opencode_sha256"], "OpenCode executable hash")
    codex_version = subprocess.run([str(codex_binary), "--version"], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()
    opencode_version = subprocess.run([str(opencode_binary), "--version"], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()
    require(codex_version == runtime["codex_version"] == "codex-cli 0.149.0", "Codex version")
    require(opencode_version == runtime["opencode_version"] == "1.18.21", "OpenCode version")

    fixture = exact_keys(
        plan["fixture"],
        {"generator", "generator_sha256", "generated_context_sha256", "context_bytes", "total_records", "selected_records", "unique_decision_evidence", "expected_answer", "compact_evidence_bytes"},
        "fixture",
    )
    generator = contained_file(root, fixture["generator"], "fixture generator")
    require(sha256(generator) == fixture["generator_sha256"], "fixture generator hash")
    spec = importlib.util.spec_from_file_location("validated_delta_fixture", generator)
    require(spec is not None and spec.loader is not None, "fixture generator import")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    generated = module.validate()
    require(isinstance(generated, dict), "fixture validation result")
    require(generated == {
        "context_sha256": fixture["generated_context_sha256"],
        "context_bytes": fixture["context_bytes"],
        "total_records": fixture["total_records"],
        "selected_records": fixture["selected_records"],
        "unique_decision_evidence": fixture["unique_decision_evidence"],
        "expected_answer": fixture["expected_answer"],
        "compact_evidence_bytes": fixture["compact_evidence_bytes"],
    }, "generated fixture identity")
    require(fixture["context_bytes"] > 1_000_000, "large context threshold")
    require(fixture["total_records"] == 306, "total record count")
    require(fixture["selected_records"] == 64, "selected record count")
    require(fixture["unique_decision_evidence"] == 64, "unique evidence count")
    require(fixture["expected_answer"] == 42, "expected answer")
    require(fixture["compact_evidence_bytes"] < 65536, "compact evidence ceiling")

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
    require(
        all(gold not in shared_text for gold in ("42", "149", "132", "8638")),
        "prompt leaks gold",
    )
    require("Group byte-identical" in shared_text and "Return exactly `Answer: number`" in shared_text, "shared prompt contract")
    for term in (
        "./azdaja-evaluate",
        "exactly once",
        "Do not open, read, copy, sample, or classify `context.txt`",
        "Do not load a skill, retry, or use another analysis path",
        "stdout line unchanged",
    ):
        require(term in prefix_text, f"candidate prefix missing {term}")

    runner = exact_keys(plan["runner"], {"path", "sha256"}, "runner")
    runner_path = contained_file(root, runner["path"], "runner")
    require(sha256(runner_path) == runner["sha256"], "runner hash")
    runner_text = runner_path.read_text(encoding="utf-8")
    for field in ("reasoning_tokens", "cache_write_tokens", "usage_complete", "measured_total_uncached_tokens"):
        require(field in runner_text, f"runner missing {field}")
    for field in (
        "ensure_owner_directory(root)",
        "ensure_owner_directory(work)",
        "write_candidate_driver(work, env, harness)",
        "llm_batch([prompt], workers=6, model=",
        '"$AZDAJA" final "$sid"',
        "def invoke_candidate_direct",
        'command = [str(work / "azdaja-evaluate")]',
        "pool.submit(invoke_candidate_direct, campaign, harness)",
    ):
        require(field in runner_text, f"runner missing workdir custody contract: {field}")
    require("pool.submit(invoke," not in runner_text, "runner must not launch new native or outer candidate arms")

    baseline = exact_keys(plan["baseline"], {"path", "sha256", "plan_sha256", "native"}, "baseline")
    baseline_path = contained_file(root, baseline["path"], "baseline result")
    require(sha256(baseline_path) == baseline["sha256"], "baseline result hash")
    require(baseline["plan_sha256"] == "a4c3aa0ad272484f75b44504384af2438ff4916df513ea52a55c8849c36581ce", "baseline plan hash")
    baseline_result = json.loads(baseline_path.read_text(encoding="utf-8"))
    require(baseline_result.get("schema") == "azdaja-luna-delta-cheap-gate/v1", "baseline schema")
    require(baseline_result.get("plan_sha256") == baseline["plan_sha256"], "baseline embedded plan hash")
    native = exact_keys(baseline["native"], {"codex", "opencode"}, "baseline native")
    expected_native = {
        "codex": {"answer": 42, "model": "gpt-5.6-luna", "outer_uncached_tokens": 32862, "outer_gross_tokens": 150366, "wall_seconds": 23.862, "inner_attempts": 0},
        "opencode": {"answer": 42, "model": "openai/gpt-5.6-luna", "outer_uncached_tokens": 70397, "outer_gross_tokens": 238333, "wall_seconds": 22.479, "inner_attempts": 0},
    }
    require(native == expected_native, "baseline native pins")
    baseline_rows = {row.get("harness"): row for row in baseline_result.get("calls", []) if row.get("arm") == "native"}
    require(set(baseline_rows) == {"codex", "opencode"}, "baseline native rows")
    for harness, expected in expected_native.items():
        row = baseline_rows[harness]
        observed = {
            "answer": row.get("answer"),
            "model": row.get("model"),
            "outer_uncached_tokens": row.get("outer_uncached_tokens"),
            "outer_gross_tokens": row.get("outer_gross_tokens"),
            "wall_seconds": row.get("wall_seconds"),
            "inner_attempts": row.get("inner", {}).get("attempts"),
        }
        require(observed == expected and row.get("correct") is True, f"baseline {harness} identity")

    execution = exact_keys(
        plan["execution"],
        {"repetitions", "retry", "timeout_seconds", "candidate_only_followup", "new_outer_provider_invocations", "new_inner_provider_invocations", "candidate_inner_attempt_ceiling", "candidate_transaction_ceiling", "candidate_config_max_calls_per_cell", "candidate_config_cell_timeout_seconds", "max_unique_items_per_shard", "max_chars_per_shard", "workers", "parallel_groups"},
        "execution",
    )
    require(execution["repetitions"] == 1 and execution["retry"] is False, "one-shot no-retry contract")
    require(execution["timeout_seconds"] == 300, "timeout")
    require(execution["candidate_only_followup"] is True, "candidate-only follow-up")
    require(execution["new_outer_provider_invocations"] == 0, "no new outer provider calls")
    require(execution["new_inner_provider_invocations"] == 2, "two new inner provider calls")
    require(execution["candidate_inner_attempt_ceiling"] == 1, "inner call ceiling")
    require(execution["candidate_transaction_ceiling"] == 1, "transaction ceiling")
    require(execution["candidate_config_max_calls_per_cell"] == 1, "runtime call ceiling")
    require(execution["candidate_config_cell_timeout_seconds"] == 180, "candidate cell timeout")
    require(execution["max_unique_items_per_shard"] == 256, "item shard cap")
    require(execution["max_chars_per_shard"] == 65536, "character shard cap")
    require(execution["workers"] == 6, "worker cap")
    require(execution["parallel_groups"] == [
        ["codex/candidate-direct", "opencode/candidate-direct"],
    ], "schedule")

    accounting = exact_keys(
        plan["accounting"],
        {"outer_usage_fields", "inner_trace_fields", "normalized_input_semantics", "harness_input_normalization", "primary_metric", "primary_formula", "report_gross_tokens", "complete_usage_required_for_every_success", "missing_usage_blocks_efficiency"},
        "accounting",
    )
    require(accounting == {
        "outer_usage_fields": ["input", "output", "reasoning", "cache.read", "cache.write"],
        "inner_trace_fields": ["input_tokens", "output_tokens", "reasoning_tokens", "cache_read_tokens", "cache_write_tokens"],
        "normalized_input_semantics": "total prompt input including cache.read",
        "harness_input_normalization": {
            "codex": "usage.input_tokens",
            "opencode": "tokens.input + tokens.cache.read",
        },
        "primary_metric": "total_uncached_tokens",
        "primary_formula": "input - cache.read + cache.write + output + reasoning",
        "report_gross_tokens": True,
        "complete_usage_required_for_every_success": True,
        "missing_usage_blocks_efficiency": True,
    }, "five-field uncached accounting")

    gates = exact_keys(
        plan["gates"],
        {"quality_first", "candidate_exact_required", "efficiency_requires_both_correct", "native_inner_attempts_must_equal", "candidate_outer_uncached_tokens_must_be_lower", "candidate_total_uncached_tokens_must_be_lower", "candidate_wall_seconds_must_be_lower", "candidate_inner_attempts_must_equal", "candidate_inner_failures_must_equal", "frozen_native_baseline_required", "new_provider_invocations_must_equal", "single_run_is_diagnostic_only"},
        "gates",
    )
    require(all(value is True for key, value in gates.items() if key not in {"native_inner_attempts_must_equal", "candidate_inner_attempts_must_equal", "candidate_inner_failures_must_equal", "new_provider_invocations_must_equal"}), "boolean gates")
    require(gates["native_inner_attempts_must_equal"] == 0, "native inner attempt gate")
    require(gates["candidate_inner_attempts_must_equal"] == 1, "inner attempt gate")
    require(gates["candidate_inner_failures_must_equal"] == 0, "inner failure gate")
    require(gates["new_provider_invocations_must_equal"] == 2, "provider invocation gate")

    return {
        "valid": True,
        "plan_sha256": sha256(plan_path),
        "context_sha256": fixture["generated_context_sha256"],
        "selected_records": fixture["selected_records"],
        "unique_decision_evidence": fixture["unique_decision_evidence"],
        "maximum_candidate_inner_attempts_per_harness": 1,
        "model": model,
        "source": source,
        "runtime": runtime,
        "accounting": accounting,
        "baseline": baseline,
    }


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("plan.json")
    try:
        print(json.dumps(validate(path), sort_keys=True))
    except (OSError, UnicodeError, json.JSONDecodeError, subprocess.SubprocessError, PlanError) as exc:
        print(f"BLOCK: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
