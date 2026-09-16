#!/usr/bin/env python3
"""Offline receipt replay and actual Azdaja custody projection. Never calls an API.

Verifies internal consistency, not provider authenticity or semantic correctness.
Historical implementation hashes are checked against retained Git objects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess

try:
    from . import bridge, run
    from .adapter import AdapterError, Limits, MODEL_ALIASES, MODEL_ID, canonical_bytes, strict_json_loads, validate_response
except ImportError:
    import bridge
    import run
    from adapter import AdapterError, Limits, MODEL_ALIASES, MODEL_ID, canonical_bytes, strict_json_loads, validate_response


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(receipt: dict, fixtures: dict, fixture_hash: str) -> dict:
    if not isinstance(receipt, dict) or type(receipt.get("schema_version")) is not int or receipt["schema_version"] != 1:
        raise ValueError("invalid receipt schema")
    if receipt.get("fixture_sha256") != fixture_hash:
        raise ValueError("receipt fixture identity mismatch")
    if receipt.get("policy_sha256") != run.digest(run.POLICY):
        raise ValueError("receipt policy identity mismatch")
    if receipt.get("acceptance_policy") != {key: run.POLICY[key] for key in ("selected_probability_min", "confidence_min")}:
        raise ValueError("receipt acceptance policy mismatch")
    if receipt.get("protocol_sha256") != sha(run.PROTOCOL.read_bytes()):
        raise ValueError("receipt protocol identity mismatch")
    allowed = receipt.get("resolved_model_allowlist")
    if allowed is not None and (not isinstance(allowed, list) or not 1 <= len(allowed) <= 8
            or receipt.get("requested_model") not in MODEL_ALIASES
            or any(not isinstance(m, str) or not MODEL_ID.fullmatch(m) or m in MODEL_ALIASES for m in allowed)
            or len(set(allowed)) != len(allowed)):
        raise ValueError("invalid receipt resolution policy")
    if "model_resolution_policy_sha256" in receipt or allowed is not None:
        expected = run.digest({"requested_model": receipt["requested_model"], "allowlist": allowed,
                               "policy": "exact-default-or-allowlisted-first-budget-eligible-pin-v1"})
        if expected != receipt.get("model_resolution_policy_sha256"):
            raise ValueError("receipt model policy identity mismatch")
    revision = receipt.get("source_revision", "")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("invalid receipt revision")
    for filename in ("adapter.py", "run.py"):
        raw = subprocess.check_output(["git", "show", f"{revision}:bench/jev/{filename}"],
                                      cwd=run.HERE, timeout=10, stderr=subprocess.DEVNULL,
                                      env={"PATH": os.defpath, "GIT_NO_LAZY_FETCH": "1",
                                           "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
                                           "GIT_CONFIG_GLOBAL": os.devnull})
        if sha(raw) != receipt.get("implementation_sha256", {}).get(filename):
            raise ValueError("historical implementation identity mismatch")
    calls = receipt.get("calls")
    if not isinstance(calls, list) or len(calls) > 96:
        raise ValueError("invalid receipt calls")

    class Replay:
        index = 0
        resolved_model = None
        reported_input = 0
        total_request = 0
        total_estimated = 0

        def evaluate(self, state, questions):
            if self.index >= len(calls):
                raise ValueError("receipt ends before declared stopping condition")
            event = calls[self.index]
            self.index += 1
            if event["state_sha256"] != run.digest(state) or event["questions_sha256"] != run.digest(questions):
                raise ValueError("receipt request identity mismatch")
            metrics = event.get("metrics")
            payload = canonical_bytes({"state": state, "model": receipt["requested_model"], "questions": questions})
            preflight_codes = {"adapter_poisoned", "adapter_disabled_or_missing_key", "invalid_questions",
                               "invalid_question", "invalid_criteria", "invalid_state", "invalid_json_value",
                               "credential_in_request_state", "resource_budget_exceeded"}
            no_transport_evidence_expected = (event["status"] == "interrupted" or
                (event["status"] == "failed" and event.get("error_code") in preflight_codes)) and "response" not in event
            if metrics is None and "metrics" not in event and no_transport_evidence_expected:
                metrics = {}
            else:
                required = {"attempt", "request_bytes", "response_bytes", "estimated_input_tokens",
                            "request_sha256", "worker_source_sha256", "latency_ms"}
                if not isinstance(metrics, dict) or not required <= set(metrics):
                    raise ValueError("receipt transport evidence missing")
                if (type(metrics["attempt"]) is not int or metrics["attempt"] != self.index
                        or type(metrics["request_bytes"]) is not int or metrics["request_bytes"] != len(payload)
                        or type(metrics["estimated_input_tokens"]) is not int
                        or metrics["estimated_input_tokens"] != len(payload) * len(questions)
                        or metrics["request_sha256"] != sha(payload)
                        or metrics["worker_source_sha256"] != receipt["implementation_sha256"]["adapter.py"]):
                    raise ValueError("receipt transport request mismatch")
                latency, size = metrics["latency_ms"], metrics["response_bytes"]
                if (isinstance(latency, bool) or not isinstance(latency, (int, float))
                        or not math.isfinite(latency) or latency < 0
                        or (size is not None and (type(size) is not int or not 0 <= size <= Limits().max_response_bytes))):
                    raise ValueError("invalid receipt transport metrics")
                if size is not None:
                    response_hash = metrics.get("response_sha256")
                    if not isinstance(response_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", response_hash):
                        raise ValueError("receipt response evidence missing")
                self.total_request += len(payload)
                self.total_estimated += len(payload) * len(questions)
            if "response" in event:
                expected_model = receipt["requested_model"]
                allowlist = receipt.get("resolved_model_allowlist")
                if allowlist is not None:
                    expected_model = event["response"].get("model")
                    if expected_model not in allowlist or self.resolved_model not in (None, expected_model):
                        raise ValueError("receipt resolved model mismatch")
                validate_response(event["response"], questions, expected_model)
                self.reported_input += event["response"]["usage"]["input_tokens"] or 0
                if (metrics.get("response_bytes") is None or metrics["response_bytes"] <= 0
                        or type(metrics.get("cumulative_reported_input_tokens")) is not int
                        or metrics["cumulative_reported_input_tokens"] != self.reported_input):
                    raise ValueError("receipt response accounting mismatch")
                if "returned_model" in metrics and metrics["returned_model"] != expected_model:
                    raise ValueError("receipt returned model mismatch")
                limits = Limits()  # The recorded CLI uses this default envelope, not custom Client limits.
                if event["status"] == "completed" and (
                        len(payload) > limits.max_request_bytes or len(questions) > limits.max_questions
                        or self.total_request > limits.max_total_request_bytes
                        or self.total_estimated > limits.max_total_estimated_tokens
                        or self.reported_input > limits.max_input_tokens):
                    raise ValueError("completed receipt exceeds resource envelope")
                if event["status"] == "completed" and allowlist is not None:
                    if metrics.get("resolved_model_pin") != expected_model:
                        raise ValueError("receipt resolved model pin missing")
                    self.resolved_model = expected_model
            if event["status"] == "failed":
                code = event.get("error_code", "")
                if not isinstance(code, str) or not re.fullmatch(r"[a-z0-9_]{1,80}", code):
                    raise ValueError("invalid failure code")
                raise AdapterError(code, response=event.get("response"), metrics=event.get("metrics"))
            if event["status"] == "interrupted":
                raise KeyboardInterrupt
            if event["status"] != "completed" or "response" not in event:
                raise ValueError("incomplete receipt event")
            return {"response": event["response"], "metrics": metrics}

    replay = Replay()
    rebuilt = run.run_campaign(replay, fixtures, {})
    if replay.index != len(calls):
        raise ValueError("receipt contains calls after stopping condition")
    for field in ("status", "stop_reason", "calls", "stages", "baseline", "custody", "error_code"):
        if rebuilt.get(field) != receipt.get(field):
            raise ValueError("receipt replay disagrees with recorded result")
    usages = [c["response"]["usage"] for c in calls if "response" in c]
    for name in ("input_tokens", "output_tokens"):
        if receipt.get("reported_" + name) != sum(u.get(name) or 0 for u in usages):
            raise ValueError("receipt usage total mismatch")
    complete = all(u.get("input_tokens") is not None and u.get("output_tokens") is not None for u in usages) and all(c["status"] == "completed" for c in calls)
    if receipt.get("usage_complete") is not complete or receipt.get("production_promotion") is not False:
        raise ValueError("receipt completeness or promotion mismatch")
    return rebuilt


def project(receipt_path: Path, fixture_path: Path, binary: Path, scratch: Path, audit_only=False):
    with receipt_path.open("rb") as handle:
        raw = handle.read(4_194_305)
    if len(raw) > 4_194_304:
        raise ValueError("receipt too large")
    receipt = strict_json_loads(raw)
    fixtures, fixture_hash = run.load_fixtures(fixture_path)
    rebuilt = verify(receipt, fixtures, fixture_hash)
    cases = fixtures["cases"]
    # Two exact duplicate controls are structural tests, not independent observations.
    source = [{"occurrence": i, "case_id": case["id"],
               "raw": canonical_bytes({"claim": case["claim"], "evidence": case["evidence"]}).decode()}
              for i, case in enumerate(cases + [cases[0], cases[-1]])]
    source_text = canonical_bytes(source).decode()
    payload_hashes = {r["case_id"]: sha(r["raw"].encode()) for r in source}
    entries = []
    for event in rebuilt["calls"]:
        if event["status"] == "completed" and event["variant"] == "ordinary":
            for row in event["judgments"]:
                entries.append({"case_id": row["id"], "payload_sha256": payload_hashes[row["id"]],
                                "label": row["answer"]["choice"], "accepted": row["accepted"]})
    manifest = {"schema_version": 1, "source_sha256": sha(source_text.encode()), "entries": entries}
    result = bridge.evaluate(binary, source_text, manifest, scratch, audit_only=audit_only)
    return {"schema_version": 1, "receipt_sha256": sha(raw), "fixture_sha256": fixture_hash,
            "receipt_status": receipt["status"], "receipt_stop_reason": receipt["stop_reason"],
            "receipt_replay_consistent": True, "source": source, "manifest": manifest,
            "azdaja_binary_sha256": sha(binary.read_bytes()), "bridge_cell_sha256": sha(bridge.CELL.encode()),
            "evaluation": result, "semantic_efficacy_established": False,
            "caveat": "Offline internal-consistency replay and custody of supplied packs only, not an authenticated provider receipt, complete task-wide evidence, or semantic accuracy. Budget-crossing judgments are preserved in the input receipt but excluded from eligible projection."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, default=run.HERE / "fixtures.json")
    parser.add_argument("--azdaja", type=Path, default=Path("target/debug/azdaja"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-only", action="store_true", help="explicitly retain missing judgments as unjudged")
    args = parser.parse_args(argv)
    scratch = Path(os.environ.get("JCODE_SCRATCH_DIR", str(Path.home() / ".jcode/scratch")))
    artifact = project(args.receipt, args.fixtures, args.azdaja, scratch, args.audit_only)
    run.checkpoint_writer(args.output)(artifact)
    print(json.dumps({"receipt_replay_consistent": True, "complete": artifact["evaluation"]["complete"],
                      "occurrences": artifact["evaluation"]["occurrences"],
                      "unique_judged": artifact["evaluation"]["unique_judged"],
                      "raw_counts": artifact["evaluation"]["raw_counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError, AdapterError, subprocess.SubprocessError):
        print("offline receipt audit failed; no successful result emitted")
        raise SystemExit(2)
