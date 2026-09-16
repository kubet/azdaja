"""Reproduce the local Jev acceptance paths without enabling a provider.

This checks the delivered experiment and actual Azdaja CLI. It does not install
judge_many, run a planner, replay HTTP requests, or establish semantic efficacy.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "bench/jev/engine_lab/results/whole-result-acceptance-20260916.json"


class CheckFailed(Exception):
    pass


def require(condition, code):
    if not condition:
        raise CheckFailed(code)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_strict_rejection(result, output):
    # The legacy CLI deliberately hides the internal cause. Its fixed rejection
    # envelope is distinguishable from argparse/startup errors, not every IO fault.
    require(result.returncode == 2
            and result.stdout.strip() == "offline receipt audit failed; no successful result emitted"
            and not result.stderr.strip(), "strict_audit:unexpected_diagnostic")
    require(not os.path.lexists(output), "strict_audit:unexpected_result")


def run_checks(binary, scratch, report):
    reference = json.loads(REFERENCE.read_text())
    report["reference_receipt_sha256"] = digest(REFERENCE)
    report["binary_sha256"] = digest(binary)
    report["same_binary_as_reference"] = report["binary_sha256"] == reference["binary_sha256"]
    with tempfile.TemporaryDirectory(prefix="jev-public-acceptance-", dir=scratch) as directory:
        work = Path(directory)
        home = work / "home"
        home.mkdir(mode=0o700)
        config = work / "config.toml"
        config.write_text("sub_llm_cmd = '/usr/bin/false'\ndefault_model = 'offline-acceptance'\n"
                          "output_cap = 262144\ncell_timeout = 10\nmax_calls_per_cell = 1\n"
                          "max_depth = 1\nmax_sessions = 1\nclean_patterns = []\n")
        config.chmod(0o600)
        # Do not inherit API credentials, proxies, Python hooks or live providers.
        env = {"PATH": "/usr/bin:/bin", "HOME": str(home), "TMPDIR": str(work),
               "AZDAJA_HOME": str(home), "AZDAJA_CONFIG": str(config), "RLM_DEPTH": "0",
               "AZDAJA_BINARY": str(binary), "JCODE_SCRATCH_DIR": str(work),
               "PYTHONDONTWRITEBYTECODE": "1"}

        def command(stage, argv, text="", expected=0, timeout=90):
            report["stage"] = stage
            try:
                result = subprocess.run(argv, input=text, text=True, capture_output=True,
                                        cwd=ROOT, env=env, timeout=timeout)
            except (OSError, subprocess.SubprocessError):
                raise CheckFailed(stage + ":process_failed") from None
            require(len(result.stdout.encode()) <= 4194304 and len(result.stderr.encode()) <= 4194304,
                    stage + ":output_limit")
            require(result.returncode == expected, stage + ":unexpected_exit")
            return result

        python = [sys.executable, "-B"]
        planned = json.loads(command("default_offline", python + ["bench/jev/run.py"]).stdout)
        require(all(planned[k] == reference["checks"]["default_experiment_cli"][k]
                    for k in ("status", "network_calls", "cases")), "default_offline:mismatch")
        report["checks"]["default_offline"] = {k: planned[k] for k in ("status", "network_calls", "cases")}

        tested = command("original_suite", python + ["-m", "unittest", "discover", "-s", "bench/jev", "-p", "test_*.py", "-v"])
        count = re.search(r"Ran (\d+) tests in", tested.stderr)
        require(count is not None and re.search(r"\nOK\s*$", tested.stderr) is not None,
                "original_suite:missing_or_skipped_tests")
        require(int(count.group(1)) >= reference["checks"]["original_suite"]["passed"], "original_suite:missing_tests")
        report["checks"]["original_suite"] = {"passed": int(count.group(1)), "skipped": 0,
            "test_sha256": {p.name: digest(p) for p in sorted((ROOT / "bench/jev").glob("test_*.py"))}}

        engine = json.loads(command("engine_public_cli", python + ["-m", "bench.jev.engine_lab.run"]).stdout)
        expected_engine = reference["checks"]["engine_public_cli"]
        require(engine["passed"] is True and engine["tests"] == expected_engine["tests"], "engine_public_cli:tests")
        require(engine["observations"] == expected_engine["observations"], "engine_public_cli:observations")
        actual_sources = dict(engine["sha256"])
        require(actual_sources.pop(binary.name, None) == report["binary_sha256"], "engine_public_cli:binary_changed")
        expected_sources = {k: v for k, v in expected_engine["sha256"].items() if k != "azdaja"}
        require(actual_sources == expected_sources, "engine_public_cli:source_revision_changed")
        require(engine["live_provider_calls"] == 0 and engine["semantic_efficacy_established"] is False
                and engine["automatic_planning_established"] is False
                and engine["native_judge_function_implemented"] is False, "engine_public_cli:scope")
        report["checks"]["engine_public_cli"] = {"tests": engine["tests"], "observations": engine["observations"],
                                                   "source_hashes_match_reference": True}

        audits = {}
        for name, expected_audit in reference["checks"]["frozen_live_receipt_public_audits"].items():
            receipt = ROOT / "bench/jev/results" / (name + ".json")
            require(digest(receipt) == expected_audit["receipt_sha256"], "frozen_receipt:changed")
            output = work / (name + "-audit.json")
            base = python + ["bench/jev/audit.py", "--receipt", str(receipt), "--azdaja", str(binary)]
            audited = command("audit_" + name, base + ["--audit-only", "--output", str(output)])
            summary = json.loads(audited.stdout)
            full = json.loads(output.read_text())
            result = full["evaluation"]
            require(summary["receipt_replay_consistent"] is True and result["complete"] is False
                    and result["occurrences"] == 68 and result["unique_judged"] == 0
                    and len(result["unjudged_occurrences"]) == 68 and len(result["ledger"]) == 68
                    and all(row["label"] == "unjudged" and row["accepted"] is False for row in result["ledger"])
                    and full["semantic_efficacy_established"] is False, "audit:projection_mismatch")
            strict_output = work / (name + "-strict.json")
            strict = command("strict_" + name, base + ["--output", str(strict_output)], expected=2)
            validate_strict_rejection(strict, strict_output)
            audits[name] = {"audit_exit": 0, "strict_exit": 2, "occurrences": 68,
                            "unjudged": 68, "complete": False, "strict_result_created": False,
                            "strict_failure_envelope": "matched",
                            "strict_internal_cause": "not distinguished by legacy CLI"}
        report["checks"]["frozen_public_audits"] = audits

        sid = None
        try:
            sid = command("ordinary_start", [str(binary), "start"]).stdout.strip()
            require(re.fullmatch(r"[A-Za-z0-9_-]{1,128}", sid) is not None, "ordinary_start:session_id")
            source = ROOT / "Cargo.toml"
            command("ordinary_load", [str(binary), "load", sid, str(source), "repository_source"])
            command("ordinary_initialize", [str(binary), "exec", sid],
                    "saved_chars = len(repository_source)\nsaved_sha = sha256(repository_source)\n")
            final_code = 'FINAL({"chars": saved_chars, "source_sha256": saved_sha})\n'
            expected_source = {"chars": len(source.read_text()), "source_sha256": digest(source)}
            for phase in ("before", "after"):
                command("ordinary_exec_" + phase, [str(binary), "exec", sid], final_code)
                answer = json.loads(command("ordinary_final_" + phase, [str(binary), "final", sid]).stdout)
                require(answer == expected_source, "ordinary_final:source_mismatch")
                if phase == "before":
                    absent = command("native_availability", [str(binary), "exec", sid], "judge_many([])\n", expected=1)
                    require("unknown external function: judge_many" in absent.stdout + absent.stderr,
                            "native_availability:unexpected_failure")
            report["checks"]["ordinary_public_cli"] = {**expected_source, "persistent_execution": "passed",
                "native_judge_many": "not_implemented", "native_probe_exit": 1, "execution_after_probe": "passed"}
        finally:
            if sid and re.fullmatch(r"[A-Za-z0-9_-]{1,128}", sid):
                prior_stage = report["stage"]
                try:
                    command("ordinary_cleanup", [str(binary), "kill", sid], timeout=15)
                finally:
                    report["stage"] = prior_stage
    report["stage"] = "complete"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azdaja", type=Path, default=ROOT / "target/debug/azdaja")
    parser.add_argument("--scratch", type=Path, default=os.environ.get("JCODE_SCRATCH_DIR"),
                        help="existing scratch directory, or JCODE_SCRATCH_DIR")
    parser.add_argument("--receipt", type=Path, help="new output file only, optional")
    args = parser.parse_args(argv)
    report = {"schema_version": 1, "recorded_at": datetime.now(timezone.utc).isoformat(),
              "runner_sha256": digest(Path(__file__)), "live_provider_calls": 0,
              "status": "failed", "stage": "preflight", "checks": {},
              "semantic_efficacy_established": False, "automatic_planning_established": False,
              "native_judge_function_implemented": False,
              "scope": "Provider-free public acceptance of this research snapshot, not live Jev acceptance. "
                       "Uses a trusted local binary and repository. Does not rerun the Rust library suite or install toolchains."}
    try:
        # Reject existing outputs before executing any test or evaluator command.
        require(args.receipt is None or not os.path.lexists(args.receipt), "receipt_exists")
        require(args.receipt is None or args.receipt.parent.is_dir(), "receipt_parent_missing")
        require(args.scratch is not None and args.scratch.is_dir(), "scratch_directory_required")
        require(args.azdaja.is_file() and os.access(args.azdaja, os.X_OK), "evaluator_missing_or_not_executable")
        require(Path("/usr/bin/false").is_file(), "unix_offline_provider_required")
        run_checks(args.azdaja.resolve(), args.scratch.resolve(), report)
        report["status"] = "passed"
    except CheckFailed as error:
        report["error_code"] = str(error)
    except (OSError, ValueError, KeyError, TypeError):
        report["error_code"] = "invalid_local_artifact_or_io"
    # Interrupted runs do not emit a success report. No provider error text is logged.
    text = json.dumps(report, indent=2) + "\n"
    if args.receipt is not None and report["stage"] != "preflight":
        try:
            fd = os.open(args.receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(text)
        except OSError:
            report["status"] = "failed"
            report["error_code"] = "receipt_write_failed"
            text = json.dumps(report, indent=2) + "\n"
    print(text, end="")
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
