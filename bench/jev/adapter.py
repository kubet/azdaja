"""Opt-in, bounded TypeSafe experiment transport. No network on import.

Client.evaluate returns {response, metrics}. AdapterError carries sanitized
metrics and, only after complete contract validation, an optional response.
Injected transports are an offline test seam, not an alternative live backend.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass, fields
import hashlib
import http.client
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Callable

HOST = "api.typesafe.ai"
API_PATH = "/v1/systemone"
MAX_WORKER_INPUT = 100_000
MODEL_ID = re.compile(r"jev-[A-Za-z0-9.-]{1,64}\Z")
MODEL_ALIASES = {"jev-latest", "jev-preview"}
# Capture once at module import. A concurrently edited working tree cannot change
# the fresh worker's implementation halfway through a live campaign.
WORKER_SOURCE = Path(__file__).read_text(encoding="utf-8") if "__file__" in globals() else ""
WORKER_SHA256 = hashlib.sha256(WORKER_SOURCE.encode("utf-8")).hexdigest()


class AdapterError(Exception):
    def __init__(self, message: str, *, response=None, metrics=None, details=None):
        super().__init__(message)
        self.response = response
        self.metrics = metrics
        self.details = details


def canonical_bytes(value: Any) -> bytes:
    """Stable insertion-preserving JSON. Criteria order is experimentally meaningful."""
    try:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeError):
        raise AdapterError("invalid_json_value") from None


def strict_json_loads(data: bytes | str) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise AdapterError("duplicate_json_key")
            result[key] = value
        return result

    def floating(text):
        number = float(text)
        if not math.isfinite(number):
            raise AdapterError("nonfinite_json_number")
        return number

    def constant(_):
        raise AdapterError("nonfinite_json_number")

    try:
        return json.loads(data, object_pairs_hook=pairs, parse_float=floating, parse_constant=constant)
    except AdapterError:
        raise
    except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
        raise AdapterError("invalid_json") from None


@dataclass(frozen=True)
class Limits:
    max_attempts: int = 96
    max_request_bytes: int = 65536
    max_response_bytes: int = 262144
    max_questions: int = 8
    timeout_seconds: float = 25
    max_total_request_bytes: int = 1048576
    max_input_tokens: int = 1000000
    max_total_estimated_tokens: int = 1000000
    max_elapsed_seconds: float = 1200


def validate_limits(limits):
    if not isinstance(limits, Limits):
        raise AdapterError("invalid_limits")
    defaults = Limits()
    for field in fields(limits):
        value = getattr(limits, field.name)
        fractional = field.name in ("timeout_seconds", "max_elapsed_seconds")
        if (isinstance(value, bool) or not isinstance(value, (int, float) if fractional else int)
                or not math.isfinite(value) or value <= 0 or value > getattr(defaults, field.name)):
            raise AdapterError("invalid_limits")


def probability(value):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not 0 <= value <= 1 or not math.isfinite(value)):
        raise AdapterError("invalid_probability")
    return value


def description(value, nullable=False):
    if nullable and value is None:
        return True
    return isinstance(value, (str, dict, list)) and bool(value) and (not isinstance(value, str) or bool(value.strip()))


def validate_questions(questions, limit):
    if (not isinstance(questions, dict) or not 1 <= len(questions) <= limit
            or any(not isinstance(k, str) or not k.strip() for k in questions)):
        raise AdapterError("invalid_questions")
    for q in questions.values():
        if (not isinstance(q, dict) or set(q) - {"type", "instructions", "criteria"}
                or q.get("type") not in ("noul", "choice", "score")
                or not description(q.get("instructions"))):
            raise AdapterError("invalid_question")
        kind, criteria = q["type"], q.get("criteria")
        if kind == "noul":
            if criteria is not None and (not isinstance(criteria, dict) or set(criteria) - {"true", "false"}
                                         or any(not description(v) for v in criteria.values())):
                raise AdapterError("invalid_criteria")
        elif kind == "choice":
            if (not isinstance(criteria, dict) or not 1 <= len(criteria) <= 255
                    or any(not isinstance(k, str) or not k.strip() or not description(v, True) for k, v in criteria.items())):
                raise AdapterError("invalid_criteria")
        elif not isinstance(criteria, list) or not 2 <= len(criteria) <= 255 or any(not description(v) for v in criteria):
            raise AdapterError("invalid_criteria")


def validate_response(response, questions, model):
    if not isinstance(response, dict) or set(response) != {"model", "answers", "usage"}:
        raise AdapterError("response_envelope_mismatch")
    if response["model"] != model:
        raise AdapterError("response_model_mismatch")
    answers = response["answers"]
    if not isinstance(answers, dict) or set(answers) != set(questions):
        raise AdapterError("answer_coverage_mismatch")
    for qid, question in questions.items():
        answer = answers[qid]
        kind = question["type"]
        shapes = {"noul": {"type", "noul"},
                  "choice": {"type", "choice", "probabilities", "confidence"},
                  "score": {"type", "score", "probabilities", "confidence", "legend"}}
        if not isinstance(answer, dict) or set(answer) != shapes[kind] or answer["type"] != kind:
            raise AdapterError("answer_shape_mismatch")
        if kind == "noul":
            probability(answer["noul"])
            continue
        probability(answer["confidence"])
        expected = set(question["criteria"]) if kind == "choice" else {str(i) for i in range(len(question["criteria"]))}
        distribution = answer["probabilities"]
        if not isinstance(distribution, dict) or set(distribution) != expected:
            raise AdapterError("probability_domain_mismatch")
        for value in distribution.values():
            probability(value)
        if abs(sum(distribution.values()) - 1) > 1e-5:
            raise AdapterError("probability_sum_mismatch")
        if kind == "choice":
            choice = answer["choice"]
            if not isinstance(choice, str) or choice not in expected or distribution[choice] != max(distribution.values()):
                raise AdapterError("choice_not_argmax")
        else:
            score = answer["score"]
            if (isinstance(score, bool) or not isinstance(score, (int, float))
                    or not 0 <= score <= len(question["criteria"]) - 1 or not math.isfinite(score)):
                raise AdapterError("invalid_score")
            if answer["legend"] != {str(i): v for i, v in enumerate(question["criteria"])}:
                raise AdapterError("score_legend_mismatch")
            if abs(score - sum(int(k) * p for k, p in distribution.items())) > 1e-4:
                raise AdapterError("score_expectation_mismatch")
    usage = response["usage"]
    if not isinstance(usage, dict) or set(usage) != {"input_tokens", "output_tokens"}:
        raise AdapterError("usage_shape_mismatch")
    for value in usage.values():
        if value is not None and (type(value) is not int or value < 0 or value > 2**63 - 1):
            raise AdapterError("invalid_usage")


def _worker_main():
    """Fixed-origin worker. The parent enforces an independent wall-clock deadline."""
    connection = None
    try:
        raw = sys.stdin.buffer.read(MAX_WORKER_INPUT + 1)
        if len(raw) > MAX_WORKER_INPUT:
            raise AdapterError("worker_input_too_large")
        envelope = strict_json_loads(raw)
        payload = base64.b64decode(envelope["payload"], validate=True)
        if len(payload) > Limits().max_request_bytes:
            raise AdapterError("worker_payload_too_large")
        cap = envelope["max_response"]
        if type(cap) is not int or not 1 <= cap <= Limits().max_response_bytes:
            raise AdapterError("worker_cap_invalid")
        connection = http.client.HTTPSConnection(HOST, timeout=envelope["timeout"])
        connection.request("POST", API_PATH, body=payload,
                           headers={"Authorization": "Bearer " + envelope["key"], "Content-Type": "application/json"})
        response = connection.getresponse()
        if response.status != 200:
            # Do not read a hostile error body and do not follow Location headers.
            sys.stdout.buffer.write(f"__HTTP_STATUS_{response.status}__".encode("ascii"))
            return
        body = response.read(cap + 1)
        if len(body) > cap:
            sys.stdout.buffer.write(b"__RESPONSE_TOO_LARGE__")
            return
        sys.stdout.buffer.write(body)
    except Exception:
        sys.stdout.buffer.write(b"__WORKER_FAILURE__")
    finally:
        if connection is not None:
            connection.close()


def _terminate(proc):
    if proc.poll() is None:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
    proc.communicate()  # The isolated worker never spawns descendants.


class Client:
    def __init__(self, api_key: str | None, enabled=False, model="jev-1.12", limits=None,
                 transport: Callable | None = None, resolved_model_allowlist: tuple[str, ...] | None = None):
        # TypeSafe token syntax and test tokens need no JSON-escaping characters.
        # Reject quotes/backslashes rather than let serialized containment miss them.
        if (api_key is not None and (not isinstance(api_key, str)
                                    or not re.fullmatch(r"[A-Za-z0-9_-]{1,512}", api_key))):
            raise AdapterError("invalid_api_key")
        if type(enabled) is not bool or not isinstance(model, str) or not MODEL_ID.fullmatch(model):
            raise AdapterError("invalid_client_configuration")
        if model in MODEL_ALIASES and resolved_model_allowlist is None:
            raise AdapterError("model_alias_requires_explicit_resolution_policy")
        if resolved_model_allowlist is not None:
            if (model not in MODEL_ALIASES or not isinstance(resolved_model_allowlist, tuple)
                    or not 1 <= len(resolved_model_allowlist) <= 8
                    or any(not isinstance(m, str) or not MODEL_ID.fullmatch(m) or m in MODEL_ALIASES
                           for m in resolved_model_allowlist)
                    or len(set(resolved_model_allowlist)) != len(resolved_model_allowlist)):
                raise AdapterError("invalid_model_resolution_policy")
        # Future-study option only. Exact requested/returned identity remains default.
        # An allowlist must be declared before results, never learned from correctness.
        self.resolved_model_allowlist = resolved_model_allowlist
        self.resolved_model = None
        self.api_key, self.enabled, self.model = api_key, enabled, model
        self.limits = limits if limits is not None else Limits()
        validate_limits(self.limits)
        self.transport = transport
        self._attempt = self._total_request = self._total_estimated = self._reported_input = 0
        self._started = time.monotonic()
        self._poisoned = False

    def _fetch(self, payload, timeout):
        if self.transport is not None:
            try:
                result = self.transport(payload, self.api_key, timeout, self.limits.max_response_bytes)
            except Exception:
                raise AdapterError("transport_failure") from None
            if not isinstance(result, bytes) or len(result) > self.limits.max_response_bytes:
                raise AdapterError("response_too_large_or_invalid")
            return result
        envelope = canonical_bytes({"payload": base64.b64encode(payload).decode("ascii"), "key": self.api_key,
                                    "timeout": timeout, "max_response": self.limits.max_response_bytes})
        # Isolated Python and an allowlist prevent credential/proxy/PYTHONPATH inheritance.
        child_env = {"PATH": os.defpath}
        for name in ("SYSTEMROOT", "WINDIR"):
            if name in os.environ:
                child_env[name] = os.environ[name]
        proc = subprocess.Popen([sys.executable, "-I", "-c", WORKER_SOURCE, "--worker"],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                env=child_env, close_fds=True)
        try:
            stdout, _ = proc.communicate(envelope, timeout=timeout)
        except subprocess.TimeoutExpired:
            _terminate(proc)
            raise AdapterError("request_deadline_exceeded") from None
        except BaseException:
            _terminate(proc)
            raise
        if proc.returncode != 0:
            raise AdapterError("transport_failure")
        if len(stdout) > self.limits.max_response_bytes or stdout == b"__RESPONSE_TOO_LARGE__":
            raise AdapterError("response_too_large")
        match = re.fullmatch(rb"__HTTP_STATUS_([1-5][0-9]{2})__", stdout)
        if match:
            raise AdapterError("http_" + match[1].decode("ascii"))
        if stdout == b"__WORKER_FAILURE__":
            raise AdapterError("transport_failure")
        return stdout

    def evaluate(self, state, questions):
        metrics = None
        started = None
        if self._poisoned:
            raise AdapterError("adapter_poisoned")
        try:
            if not self.enabled or not self.api_key:
                raise AdapterError("adapter_disabled_or_missing_key")
            validate_questions(questions, self.limits.max_questions)
            if not isinstance(state, (str, dict, list)) or not state:
                raise AdapterError("invalid_state")
            payload = canonical_bytes({"state": state, "model": self.model, "questions": questions})
            if self.api_key.encode() in payload:
                raise AdapterError("credential_in_request_state")
            estimated = len(payload) * len(questions)  # Conservative proxy, not a tokenizer or billing guarantee.
            remaining = self.limits.max_elapsed_seconds - (time.monotonic() - self._started)
            if (len(payload) > self.limits.max_request_bytes or self._attempt >= self.limits.max_attempts
                    or self._total_request + len(payload) > self.limits.max_total_request_bytes
                    or self._total_estimated + estimated > self.limits.max_total_estimated_tokens
                    or remaining <= 0):
                raise AdapterError("resource_budget_exceeded")
            self._attempt += 1
            self._total_request += len(payload)
            self._total_estimated += estimated
            started = time.monotonic()
            metrics = {"attempt": self._attempt, "request_bytes": len(payload), "response_bytes": None,
                       "estimated_input_tokens": estimated, "request_sha256": hashlib.sha256(payload).hexdigest(),
                       "worker_source_sha256": WORKER_SHA256}
            raw = self._fetch(payload, min(self.limits.timeout_seconds, remaining))
            metrics.update(response_bytes=len(raw), response_sha256=hashlib.sha256(raw).hexdigest())
            if self.api_key.encode() in raw:
                raise AdapterError("response_contains_credential")
            response = strict_json_loads(raw)
            if self.api_key.encode() in canonical_bytes(response):
                raise AdapterError("response_contains_credential")
            returned_model = response.get("model") if isinstance(response, dict) else None
            if isinstance(returned_model, str) and MODEL_ID.fullmatch(returned_model):
                metrics["returned_model"] = returned_model
            expected_model = self.model
            if self.resolved_model_allowlist is not None:
                if not isinstance(returned_model, str) or returned_model not in self.resolved_model_allowlist:
                    raise AdapterError("response_model_not_allowlisted")
                if self.resolved_model is not None and returned_model != self.resolved_model:
                    raise AdapterError("response_model_changed")
                expected_model = returned_model
            validate_response(response, questions, expected_model)
            reported = response["usage"]["input_tokens"]
            if reported is not None:
                self._reported_input += reported
            metrics["cumulative_reported_input_tokens"] = self._reported_input
            metrics["latency_ms"] = round((time.monotonic() - started) * 1000, 3)
            if self._reported_input > self.limits.max_input_tokens:
                raise AdapterError("reported_token_budget_exceeded", response=response, metrics=metrics)
            if time.monotonic() - self._started > self.limits.max_elapsed_seconds:
                raise AdapterError("campaign_deadline_exceeded", response=response, metrics=metrics)
            if self.resolved_model_allowlist is not None:
                # Pin only after the complete response AND post-response budgets pass.
                self.resolved_model = returned_model
                metrics["resolved_model_pin"] = returned_model
            return {"response": response, "metrics": metrics}
        except BaseException as exc:
            self._poisoned = True
            if metrics is not None and started is not None:
                metrics["latency_ms"] = round((time.monotonic() - started) * 1000, 3)
            if isinstance(exc, AdapterError):
                exc.metrics = metrics
                raise
            if not isinstance(exc, Exception):
                raise
            raise AdapterError("adapter_failure", metrics=metrics) from None


if __name__ == "__main__" and sys.argv[1:] == ["--worker"]:
    _worker_main()
