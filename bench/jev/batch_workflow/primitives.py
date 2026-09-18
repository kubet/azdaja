#!/usr/bin/env python3
"""Offline verification of the one retained three-primitive request. Never executes new work."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
DATA = HERE / "primitives-20260918"
FILES = {"plan.jsonl", "config.toml", "preflight.json", "admission.started.json",
         "live.stdout", "live.stderr", "terminal.json", "resume.json", "acceptance.json",
         "job/manifest.json", "job/000000.intent.json", "job/000000.result.json", "controller.txt"}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate key")
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode()


def distribution(value, keys):
    require(set(value) == set(keys), "distribution domain")
    require(all(type(p) in (int, float) and math.isfinite(p) and 0 <= p <= 1
                for p in value.values()), "distribution values")
    require(abs(sum(value.values()) - 1) <= 1e-6, "distribution normalization")


def verify(data=DATA):
    data = Path(data)
    seal = load(data / "RETENTION.json")
    require(set(seal["files"]) == FILES, "retention inventory")
    require(sha((HERE / "PRIMITIVES.md").read_bytes()) == seal["protocol_sha256"], "protocol")
    for name, expected in seal["files"].items():
        path = data / name
        require(not path.is_symlink() and path.is_file(), "unsafe retained path")
        require(sha(path.read_bytes()) == expected, "changed retained artifact")
    plan = load(data / "plan.jsonl")
    manifest = load(data / "job/manifest.json")
    intent = load(data / "job/000000.intent.json")
    result = load(data / "job/000000.result.json")
    admission = load(data / "admission.started.json")
    terminal = load(data / "terminal.json")
    receipt = load(data / "acceptance.json")
    summary = load(data / "live.stdout")
    resume = load(data / "resume.json")
    preflight = load(data / "preflight.json")
    binding = manifest["binding"]
    plan_sha = sha((data / "plan.jsonl").read_bytes())
    request_sha = sha(canonical({"model": binding["config"]["model"],
                                 "state": plan["state"], "questions": plan["questions"]}))
    require(binding["input_sha256"] == plan_sha == receipt["plan_sha256"] == admission["plan_sha256"], "plan identity")
    require(admission["controller_sha256"] == sha((data / "controller.txt").read_bytes())
            and admission["protocol_sha256"] == seal["protocol_sha256"], "admitted method")
    require(admission["binary_sha256"] == receipt["binary_sha256"]
            and admission["retry_authorized"] is False, "admission identity")
    require(binding["limits"] == {"max_requests": 1, "max_input_tokens": 3000, "max_seconds": 30}, "limits")
    require(binding["requests"] == [{"id": plan["id"], "request_sha256": request_sha}], "request identity")
    require(intent == {"schema": "azdaja.judge_batch.intent.v1", "index": 0,
                       "id": plan["id"], "request_sha256": request_sha}, "intent identity")
    require(result["intent"] == intent and result["status"] == "completed", "result identity")
    require(manifest["started_unix_ms"] <= result["finished_unix_ms"] <= manifest["deadline_unix_ms"], "completed deadline")
    obs, stats = result["observation"], result["stats"]
    require(obs["_azdaja"]["request_sha256"] == request_sha
            and obs["_azdaja"]["cache_hit"] is False
            and obs["_azdaja"]["provider_requests_this_call"] == 1, "native binding")
    answers, questions = obs["answers"], plan["questions"]
    require(set(answers) == set(questions) == {"has_workaround", "route", "severity"}, "question coverage")
    require({key: answer["type"] for key, answer in answers.items()}
            == {key: question["type"] for key, question in questions.items()}, "primitive types")
    noul, choice, score = answers["has_workaround"], answers["route"], answers["severity"]
    require(type(noul["noul"]) in (int, float) and 0 <= noul["noul"] <= 1, "noul range")
    distribution(choice["probabilities"], questions["route"]["criteria"])
    require(choice["choice"] in choice["probabilities"]
            and choice["probabilities"][choice["choice"]] == max(choice["probabilities"].values()), "choice winner")
    legend = {str(i): text for i, text in enumerate(questions["severity"]["criteria"])}
    require(score["legend"] == legend, "score legend")
    distribution(score["probabilities"], legend)
    require(abs(score["score"] - sum(int(k) * p for k, p in score["probabilities"].items())) <= 1e-6, "score expectation")
    require(terminal["summary"] == summary and terminal["exit"] == 0
            and terminal["further_calls_authorized"] is False, "terminal status")
    require(summary["status"] == "completed" and summary["calls"] == summary["new_requests"] == 1
            and summary["records"] == {"total": 1, "completed": 1, "pending": 0}, "complete coverage")
    require(summary["usage"] == receipt["usage"]
            and all(stats[key] == value for key, value in summary["usage"].items()), "usage identity")
    require(stats["attempts"] == stats["provider_requests"] == stats["successful_requests"] == 1
            and stats["failed_attempts"] == stats["unknown_input_usage_requests"] == stats["unknown_output_usage_requests"] == 0
            and stats["questions"] == 3, "native accounting")
    require(obs["usage"] == {"input_tokens": stats["known_input_tokens"], "output_tokens": stats["known_output_tokens"]}
            == obs["_azdaja"]["new_request_usage"] == obs["_azdaja"]["original_usage"], "response usage")
    require(resume == dict(summary, new_requests=0), "no-key retained resume")
    require(preflight["provider_requests"] == 0 and preflight["credentials_checked"] is False
            and preflight["execution_enabled"] is False and preflight["input_sha256"] == plan_sha, "offline preflight")
    require(receipt["descriptive_answers"] == answers and receipt["job_unchanged"] is True, "retained observations")
    require(receipt["retained"] == {Path(name).name: seal["files"][name] for name in FILES if name.startswith("job/")}, "job retention")
    return {"status": "retained_compatibility_verified", "new_provider_calls": 0,
            "original_requests": 1, "questions": 3, "requested_model": binding["config"]["model"],
            "returned_model": obs["model"], "usage": summary["usage"], "answers": answers,
            "semantic_generalization_established": False, "billing_known": False,
            "provider_authenticity_independently_verified": False,
            "historical_binary_bytes_verified": False,
            "semantic_caution": "Noul returned0.47 despite the explicit browser workaround. Choice selected workaround and Score selected level1. No rerun or accuracy claim."}


def native_replay(binary, data=DATA):
    report = verify(data)
    binary = Path(binary).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="jev-primitives-replay-", dir=os.environ.get("JCODE_SCRATCH_DIR")) as tmp:
        root = Path(tmp)
        (root / "job").mkdir(mode=0o700)
        for name in ["plan.jsonl", "config.toml", "job/manifest.json", "job/000000.intent.json", "job/000000.result.json"]:
            path = root / name
            with path.open("xb") as handle:
                handle.write((data / name).read_bytes())
            path.chmod(0o600)
        before = {p.name: sha(p.read_bytes()) for p in (root / "job").iterdir()}
        env = {"HOME": str(root / "no-home"), "AZDAJA_HOME": str(root / "no-state"),
               "AZDAJA_CONFIG": str(root / "config.toml"), "PATH": "/usr/bin:/bin"}
        proc = subprocess.run([str(binary), "jev", "batch", "--input", str(root / "plan.jsonl"),
                               "--execute", "--resume", "--output", str(root / "job"),
                               "--max-requests", "1", "--max-input-tokens", "3000", "--max-seconds", "30"],
                              env=env, cwd=root, capture_output=True, text=True, timeout=10)
        require(proc.returncode == 0, "native resume failed")
        actual = json.loads(proc.stdout)
        require(actual == load(data / "resume.json"), "native replay differs")
        require(all(sha((root / "job" / name).read_bytes()) == expected for name, expected in before.items()), "job mutated")
        require(not (root / "no-state").exists(), "unexpected application state")
    report["current_native_replay"] = {"binary_sha256": sha(binary.read_bytes()), "new_requests": 0,
                                       "completed": 1, "questions": 3, "job_unchanged": True}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, help="Optionally exercise completed no-key replay using this actual binary")
    args = parser.parse_args()
    try:
        report = native_replay(args.binary) if args.binary else verify()
    except (OSError, ValueError, KeyError, TypeError, IndexError, subprocess.SubprocessError):
        print("error: retained evidence or native replay refused; no new work admitted", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
