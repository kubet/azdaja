#!/usr/bin/env python3
"""Provider-free *public solo* acceptance, not a real-model quality evaluation.

Uses only an explicit local Python stub through sub_llm_cmd, never a code-provider
backdoor. --output must be a new directory (normally under JCODE_SCRATCH_DIR).
All root prompts, subprocess output and host traces are retained for inspection.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "fixtures" / "corpus.json"
QUESTION = "Return the SHA-256 and character count of the complete original ctx."
CAPABILITIES = ("judge_many(state, questions)", "judge_stats()", "llm(prompt)", "llm_batch(prompts)")
ZERO_FIELDS = ("provider_requests", "attempts", "questions", "cache_hits", "cached_requests",
               "known_input_tokens", "unknown_input_usage_requests", "known_output_tokens",
               "unknown_output_usage_requests", "successful_requests", "failed_attempts", "total_wall_ns")
STUB = '''import pathlib, sys
# Drain stdin completely before responding, including when it exceeds pipe capacity.
prompt = sys.stdin.buffer.read()
with pathlib.Path(sys.argv[1]).open("xb") as out:
    out.write(prompt)
print("```python")
print(sys.argv[2])
print("```")
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def private_write(path, data):
    with path.open("xb") as stream:
        stream.write(data)
    path.chmod(0o600)


def isolated_environment(case):
    """Allowlist, never copy provider keys, sockets, runtime or parent config."""
    home = case / "home"
    home.mkdir(mode=0o700)
    return {"HOME": str(home), "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8",
            "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1",
            "AZDAJA_HOME": str(case / "state"), "AZDAJA_CONFIG": str(case / "config.toml"),
            "AZDAJA_SOLO_TRACE": str(case / "solo.trace"),
            "AZDAJA_MODEL_TRACE": str(case / "model.jsonl")}


def json_rows(text):
    rows = []
    for line in text.splitlines():
        if line.startswith("{"):
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if isinstance(value, dict):
                rows.append(value)
    return rows


def zero_stats(stats, transport):
    return (isinstance(stats, dict) and stats.get("enabled") is True
            and stats.get("transport_available") is transport
            and stats.get("poisoned") is False
            and all(type(stats.get(key)) is int and stats[key] == 0 for key in ZERO_FIELDS)
            and stats.get("input_usage_complete") is True
            and stats.get("output_usage_complete") is True)


def run_case(binary, output, name, enabled, expected, transport=True):
    case = output / name
    case.mkdir(mode=0o700)
    env = isolated_environment(case)
    stub = case / "stub.py"
    private_write(stub, STUB.encode())
    code = "FINAL({'source_sha256':sha256(ctx),'characters':len(ctx)"
    code += ",'stats':judge_stats()})" if enabled else "})"
    command = shlex.join([sys.executable, str(stub), str(case / "root-prompt.txt"), code])
    config = ("sub_llm_cmd = " + json.dumps(command) + "\ncell_timeout = 30\nsub_timeout = 30\n"
              "[judge]\nenabled = " + str(enabled).lower() + "\nkey_env = \"AZDAJA_ACCEPTANCE_SYNTHETIC_ABSENT\"\n")
    private_write(case / "config.toml", config.encode())
    argv = [str(binary), "solo", QUESTION, "-f", str(CORPUS)]
    result = subprocess.run(argv, env=env, cwd=case, capture_output=True, timeout=90)
    private_write(case / "stdout.txt", result.stdout)
    private_write(case / "stderr.txt", result.stderr)
    prompt_path = case / "root-prompt.txt"
    prompt = prompt_path.read_text() if prompt_path.exists() else ""
    solo_path = case / "solo.trace"
    solo = solo_path.read_text() if solo_path.exists() else ""
    model_path = case / "model.jsonl"
    model = json_rows(model_path.read_text()) if model_path.exists() else []
    runtime = [row for row in json_rows(solo) if row.get("event") == "solo_runtime"]
    try:
        actual = json.loads(result.stdout)
    except ValueError:
        actual = None
    cells = runtime[-1].get("judge_cells") if runtime else None
    checks = {
        "exit_success": result.returncode == 0,
        "complete_corpus_result": isinstance(actual, dict) and all(actual.get(k) == v for k, v in expected.items()),
        "root_prompt_retained": bool(prompt),
        "root_prompt_in_host_trace": bool(prompt) and prompt in solo,
        "model_trace_present": bool(model),
        "single_root_attempt": (len(model) == 1 and model[0].get("depth") == 0
                                and model[0].get("event") == "model_attempt"
                                and model[0].get("outcome") == "succeeded"),
        "host_runtime_success": len(runtime) == 1 and runtime[0].get("outcome") == "succeeded",
        "no_generative_children": (len(runtime) == 1 and runtime[0].get("sub_call_count") == 0
                                   and runtime[0].get("semantic_call_count") == 0),
    }
    if enabled:
        checks["zero_typed_result_stats"] = isinstance(actual, dict) and zero_stats(actual.get("stats"), transport)
        checks["host_zero_typed_cells"] = isinstance(cells, list) and len(cells) == 1 and zero_stats(cells[0], transport)
        checks["host_result_stats_agree"] = (isinstance(actual, dict) and isinstance(cells, list)
                                             and len(cells) == 1 and cells[0] == actual.get("stats"))
        if transport:
            checks["optional_capabilities_advertised"] = all(item in prompt for item in CAPABILITIES)
        else:
            checks["feature_off_unavailable_notice"] = "TypeSafe transport is unavailable in this build" in prompt
    return {"binary": str(binary), "binary_sha256": digest(binary.read_bytes()), "argv": argv,
            "returncode": result.returncode, "result": actual, "checks": checks,
            "passed": all(checks.values()), "missing_capabilities": [item for item in CAPABILITIES if item not in prompt],
            "prompt_sha256": digest(prompt.encode()), "prompt_characters": len(prompt),
            "host_runtime": runtime, "model_trace": model, "artifact_directory": str(case)}


def accept(binary, old_binary, output, feature_off_binary=None):
    output = output.resolve()
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    raw = CORPUS.read_bytes()
    corpus = json.loads(raw)
    if [record["id"] for record in corpus["contracts"]] != ["d%03d" % i for i in range(102)]:
        raise ValueError("expected all 102 source contracts")
    expected = {"source_sha256": digest(raw), "characters": len(raw.decode("utf-8"))}
    report = {"schema_version": 1, "evaluation": "public_solo_local_stub_acceptance",
              "real_model": False, "provider_mode": "local deterministic Python stub",
              "scope": "Interface and accounting only, not legal accuracy or model quality",
              "corpus": str(CORPUS), "contracts": 102, "expected": expected, "cases": {}}
    cases = report["cases"]
    if old_binary:
        cases["before_enabled"] = run_case(old_binary, output, "before-enabled", True, expected)
        cases["before_disabled"] = run_case(old_binary, output, "before-disabled", False, expected)
    cases["after_enabled"] = run_case(binary, output, "after-enabled", True, expected)
    cases["after_disabled"] = run_case(binary, output, "after-disabled", False, expected)
    checks = {"after_enabled": cases["after_enabled"]["passed"], "after_disabled": cases["after_disabled"]["passed"]}
    if old_binary:
        before = cases["before_enabled"]
        checks["before_missing_capability_witness"] = (
            bool(before["missing_capabilities"])
            and all(before["checks"][key] for key in (
                "exit_success", "complete_corpus_result", "root_prompt_retained",
                "root_prompt_in_host_trace", "single_root_attempt", "host_runtime_success")))
        checks["before_disabled_success"] = cases["before_disabled"]["passed"]
        checks["disabled_prompt_byte_identical"] = ((output / "before-disabled/root-prompt.txt").read_bytes()
                                                    == (output / "after-disabled/root-prompt.txt").read_bytes())
    if feature_off_binary:
        cases["feature_off_enabled"] = run_case(feature_off_binary, output, "feature-off-enabled", True, expected, False)
        checks["feature_off_enabled"] = cases["feature_off_enabled"]["passed"]
    report["checks"] = checks
    report["passed"] = all(checks.values())
    private_write(output / "report.json", (json.dumps(report, indent=2) + "\n").encode())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--old-binary", type=Path)
    parser.add_argument("--feature-off-binary", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="new exclusive artifact directory")
    args = parser.parse_args()
    report = accept(args.binary.resolve(), args.old_binary.resolve() if args.old_binary else None,
                    args.output, args.feature_off_binary.resolve() if args.feature_off_binary else None)
    print(json.dumps({"passed": report["passed"], "checks": report["checks"], "output": str(args.output.resolve())}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
