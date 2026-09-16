"""Network-free tests of real adapter paths, including actual child custody."""
import base64
import copy
from dataclasses import replace
import io
import json
import os
import subprocess
import sys
import time
import unittest
from unittest.mock import Mock, patch

import adapter
from adapter import AdapterError, Client, Limits, canonical_bytes, strict_json_loads

KEY = "offline-test-credential-not-present-in-any-fixture"
REAL_POPEN = subprocess.Popen


def questions():
    return {
        "n": {"type": "noul", "instructions": "Is it true?", "criteria": {"true": "yes", "false": "no"}},
        "c": {"type": "choice", "instructions": ["Pick"], "criteria": {"a": None, "b": "other"}},
        "s": {"type": "score", "instructions": {"task": "rate"}, "criteria": ["low", "high"]},
    }


def response():
    return {"model": "jev-1.12", "answers": {
        "n": {"type": "noul", "noul": 0.75},
        "c": {"type": "choice", "choice": "a", "probabilities": {"a": 0.8, "b": 0.2}, "confidence": 0.8},
        "s": {"type": "score", "score": 0.25, "legend": {"0": "low", "1": "high"},
              "probabilities": {"0": 0.75, "1": 0.25}, "confidence": 0.75},
    }, "usage": {"input_tokens": 100, "output_tokens": 20}}


def fake_client(body=None, **kwargs):
    value = canonical_bytes(response()) if body is None else body
    return Client(KEY, enabled=True, transport=lambda *_: value, **kwargs)


class AdapterTests(unittest.TestCase):
    def setUp(self):
        # A missing mock cannot accidentally turn an offline test into an API call.
        self.net = patch("socket.create_connection", side_effect=AssertionError("network forbidden"))
        self.spawn = patch("adapter.subprocess.Popen", side_effect=AssertionError("unmocked child forbidden"))
        self.net.start()
        self.spawn.start()
        self.addCleanup(self.net.stop)
        self.addCleanup(self.spawn.stop)

    def assert_code(self, code, operation):
        with self.assertRaises(AdapterError) as caught:
            operation()
        self.assertEqual(str(caught.exception), code)
        self.assertNotIn(KEY, repr(caught.exception))
        return caught.exception

    def test_strict_json_and_insertion_order(self):
        self.assertEqual(canonical_bytes({"b": 1, "a": 2}), b'{"b":1,"a":2}')
        for raw, code in ((b'{"x":1,"x":2}', "duplicate_json_key"),
                          (b'{"x":NaN}', "nonfinite_json_number"),
                          (b'{"x":1e309}', "nonfinite_json_number"),
                          (b'\xff', "invalid_json"), (b'[] garbage', "invalid_json")):
            with self.subTest(raw=raw):
                self.assert_code(code, lambda: strict_json_loads(raw))

    def test_disabled_missing_key_never_enter_transport(self):
        transport = Mock(side_effect=AssertionError("must not enter"))
        for client in (Client(KEY, transport=transport), Client(None, enabled=True, transport=transport)):
            self.assert_code("adapter_disabled_or_missing_key", lambda: client.evaluate("state", questions()))
        transport.assert_not_called()

    def test_all_three_primitives_and_metrics(self):
        transport = Mock(return_value=canonical_bytes(response()))
        result = Client(KEY, enabled=True, transport=transport).evaluate({"evidence": "café"}, questions())
        payload, key, timeout, cap = transport.call_args.args
        self.assertNotIn(KEY.encode(), payload)
        self.assertEqual(key, KEY)
        self.assertLessEqual(timeout, 25)
        self.assertEqual(cap, 262144)
        self.assertEqual(result["response"], response())
        self.assertEqual(result["metrics"]["attempt"], 1)
        self.assertEqual(result["metrics"]["response_bytes"], len(canonical_bytes(response())))
        self.assertEqual(result["metrics"]["cumulative_reported_input_tokens"], 100)
        self.assertEqual(result["metrics"]["worker_source_sha256"], adapter.WORKER_SHA256)

    def test_malformed_contracts_fail_at_the_expected_validator(self):
        mutations = [
            (lambda r: r.update(extra=1), "response_envelope_mismatch"),
            (lambda r: r.update(model="jev-other"), "response_model_mismatch"),
            (lambda r: r["answers"].pop("n"), "answer_coverage_mismatch"),
            (lambda r: r["answers"].update(extra={}), "answer_coverage_mismatch"),
            (lambda r: r["answers"]["n"].update(type="choice"), "answer_shape_mismatch"),
            (lambda r: r["answers"]["n"].update(noul=True), "invalid_probability"),
            (lambda r: r["answers"]["n"].update(noul=-0.1), "invalid_probability"),
            (lambda r: r["answers"]["n"].update(noul=1.1), "invalid_probability"),
            (lambda r: r["answers"]["c"].update(confidence=False), "invalid_probability"),
            (lambda r: r["answers"]["c"]["probabilities"].update(z=0), "probability_domain_mismatch"),
            (lambda r: r["answers"]["c"]["probabilities"].update(a=0.6), "probability_sum_mismatch"),
            (lambda r: r["answers"]["c"].update(choice="b"), "choice_not_argmax"),
            (lambda r: r["answers"]["c"].update(choice={}), "choice_not_argmax"),
            (lambda r: r["answers"]["s"].update(score="0.25"), "invalid_score"),
            (lambda r: r["answers"]["s"].update(score=True), "invalid_score"),
            (lambda r: r["answers"]["s"].update(score=10**400), "invalid_score"),
            (lambda r: r["answers"]["s"].update(score=0.5), "score_expectation_mismatch"),
            (lambda r: r["answers"]["s"]["legend"].update({"1": "wrong"}), "score_legend_mismatch"),
            (lambda r: r["usage"].update(input_tokens=True), "invalid_usage"),
            (lambda r: r["usage"].update(input_tokens=-1), "invalid_usage"),
            (lambda r: r["usage"].pop("output_tokens"), "usage_shape_mismatch"),
        ]
        for mutate, code in mutations:
            with self.subTest(code=code, mutate=mutate):
                bad = response()
                mutate(bad)
                error = self.assert_code(code, lambda: fake_client(canonical_bytes(bad)).evaluate("state", questions()))
                self.assertIsNotNone(error.metrics["response_sha256"])
                self.assertIsNone(error.response)
        bad = canonical_bytes(response()).replace(b'0.75', b'NaN', 1)
        self.assert_code("nonfinite_json_number", lambda: fake_client(bad).evaluate("state", questions()))

    def test_unknown_usage_is_not_fabricated(self):
        body = response()
        body["usage"] = {"input_tokens": None, "output_tokens": None}
        result = fake_client(canonical_bytes(body)).evaluate("state", questions())
        self.assertEqual(result["response"]["usage"], body["usage"])

    def test_structured_criteria_supported(self):
        qs = questions()
        qs["n"]["criteria"]["true"] = {"definition": "yes"}
        qs["c"]["criteria"]["b"] = ["other", "none"]
        qs["s"]["criteria"][0] = {"meaning": "low"}
        body = response()
        body["answers"]["s"]["legend"]["0"] = {"meaning": "low"}
        self.assertEqual(fake_client(canonical_bytes(body)).evaluate("state", qs)["response"], body)

    def test_invalid_configuration_preflight(self):
        for key in ("", "header\r\ninjection", "with space", "é", "x" * 513):
            self.assert_code("invalid_api_key", lambda: Client(key))
        for model in ("", "https://elsewhere", "jev-a\nheader", False):
            self.assert_code("invalid_client_configuration", lambda: Client(KEY, model=model))
        for value in (0, -1, True, 1.5, float("nan"), 97):
            self.assert_code("invalid_limits", lambda: Client(KEY, limits=Limits(max_attempts=value)))
        self.assert_code("invalid_limits", lambda: Client(KEY, limits=Limits(timeout_seconds=float("inf"))))

    def test_request_shapes_and_oversize_are_rejected_before_transport(self):
        bad_questions = [({}, "invalid_questions"),
                         ({"q": {"type": "choice", "instructions": {}, "criteria": {"a": None}}}, "invalid_question"),
                         ({"q": {"type": "score", "instructions": "rate", "criteria": ["only"]}}, "invalid_criteria")]
        for qs, code in bad_questions:
            transport = Mock()
            self.assert_code(code, lambda: Client(KEY, True, transport=transport).evaluate("state", qs))
            transport.assert_not_called()
        for limits, state in ((Limits(max_request_bytes=10), "state"),
                              (Limits(max_total_request_bytes=10), "state"),
                              (Limits(max_total_estimated_tokens=10), "state"),
                              (Limits(), "x" * 65536)):
            transport = Mock()
            self.assert_code("resource_budget_exceeded", lambda: Client(KEY, True, limits=limits, transport=transport).evaluate(state, questions()))
            transport.assert_not_called()

    def test_attempt_budget_and_poison_after_error(self):
        transport = Mock(return_value=canonical_bytes(response()))
        client = Client(KEY, True, limits=Limits(max_attempts=1), transport=transport)
        client.evaluate("state", questions())
        self.assert_code("resource_budget_exceeded", lambda: client.evaluate("state", questions()))
        self.assert_code("adapter_poisoned", lambda: client.evaluate("state", questions()))
        self.assertEqual(transport.call_count, 1)

    def test_reported_token_crossing_keeps_response_and_metrics(self):
        transport = Mock(return_value=canonical_bytes(response()))
        client = Client(KEY, True, limits=Limits(max_input_tokens=150), transport=transport)
        client.evaluate("state", questions())
        error = self.assert_code("reported_token_budget_exceeded", lambda: client.evaluate("state", questions()))
        self.assertEqual(error.response["usage"]["input_tokens"], 100)
        self.assertEqual(error.metrics["cumulative_reported_input_tokens"], 200)
        self.assertEqual(error.metrics["attempt"], 2)
        self.assert_code("adapter_poisoned", lambda: client.evaluate("state", questions()))
        self.assertEqual(transport.call_count, 2)

    def test_credential_and_exception_hygiene(self):
        self.assert_code("response_contains_credential", lambda: fake_client(canonical_bytes({"error": KEY})).evaluate("state", questions()))
        transport = Mock()
        self.assert_code("credential_in_request_state", lambda: Client(KEY, True, transport=transport).evaluate(KEY, questions()))
        transport.assert_not_called()
        qs = {KEY: {"type": "unknown", "instructions": KEY}}
        self.assert_code("invalid_question", lambda: fake_client().evaluate("state", qs))
        failing = Client(KEY, True, transport=Mock(side_effect=ValueError(KEY)))
        error = self.assert_code("transport_failure", lambda: failing.evaluate("state", questions()))
        self.assertEqual(error.metrics["attempt"], 1)
        self.assertIsNone(error.metrics["response_bytes"])
        self.assert_code("adapter_poisoned", lambda: failing.evaluate("state", questions()))
        self.assertNotIn(KEY, repr(failing))

    def worker(self, status=200, body=b"{}", cap=64, raw=None):
        envelope = canonical_bytes({"payload": base64.b64encode(b'{"state":"test"}').decode(),
                                    "key": KEY, "timeout": 1, "max_response": cap})
        stdin = Mock(buffer=io.BytesIO(envelope if raw is None else raw))
        stdout = Mock(buffer=io.BytesIO())
        conn = Mock()
        conn.getresponse.return_value.status = status
        conn.getresponse.return_value.read.return_value = body
        with patch("adapter.http.client.HTTPSConnection", return_value=conn) as constructor, \
             patch("adapter.sys.stdin", stdin), patch("adapter.sys.stdout", stdout):
            adapter._worker_main()
        return stdout.buffer.getvalue(), conn, constructor

    def test_worker_fixed_origin_no_redirects_or_error_bodies(self):
        for status in (301, 302, 307, 308, 401, 422, 429, 529):
            with self.subTest(status=status):
                raw, conn, constructor = self.worker(status, body=KEY.encode())
                self.assertEqual(raw, f"__HTTP_STATUS_{status}__".encode())
                self.assertNotIn(KEY.encode(), raw)
                constructor.assert_called_once_with("api.typesafe.ai", timeout=1)
                self.assertEqual(conn.request.call_args.args[:2], ("POST", "/v1/systemone"))
                self.assertEqual(conn.request.call_count, 1)
                conn.getresponse.return_value.read.assert_not_called()
                conn.close.assert_called_once()

    def test_worker_bounds_success_input_and_output(self):
        raw, conn, _ = self.worker(body=b"a" * 65, cap=64)
        self.assertEqual(raw, b"__RESPONSE_TOO_LARGE__")
        conn.getresponse.return_value.read.assert_called_once_with(65)
        conn.close.assert_called_once()
        raw, conn, constructor = self.worker(raw=b"x" * (adapter.MAX_WORKER_INPUT + 1))
        self.assertEqual(raw, b"__WORKER_FAILURE__")
        constructor.assert_not_called()
        conn.close.assert_not_called()

    def test_parent_decodes_status_without_retry_or_secret_in_argv_env(self):
        for status in (302, 401, 422, 429, 529):
            process = Mock(returncode=0)
            process.communicate.return_value = (f"__HTTP_STATUS_{status}__".encode(), None)
            with patch("adapter.subprocess.Popen", return_value=process) as popen:
                self.assert_code(f"http_{status}", lambda: Client(KEY, True).evaluate("state", questions()))
            self.assertEqual(popen.call_count, 1)
            self.assertNotIn(KEY, repr(popen.call_args))
            self.assertNotIn("TYPESAFE_API_KEY", popen.call_args.kwargs["env"])
            self.assertEqual(popen.call_args.args[0][1:3], ["-I", "-c"])
            self.assertEqual(popen.call_args.args[0][3], adapter.WORKER_SOURCE)

    def test_real_sleeping_child_is_killed_and_reaped_at_deadline(self):
        children = []
        def offline_factory(argv, **kwargs):
            child = REAL_POPEN([sys.executable, "-I", "-c", "import time; time.sleep(30)"], **kwargs)
            children.append(child)
            return child
        started = time.monotonic()
        with patch("adapter.subprocess.Popen", side_effect=offline_factory):
            self.assert_code("request_deadline_exceeded", lambda: Client(KEY, True, limits=Limits(timeout_seconds=0.05)).evaluate("state", questions()))
        self.assertLess(time.monotonic() - started, 2)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].returncode)
        with self.assertRaises(ProcessLookupError): os.kill(children[0].pid, 0)

    def test_real_child_cleanup_on_interrupted_communicate(self):
        for error_type in (KeyboardInterrupt, SystemExit, OSError):
            with self.subTest(error=error_type):
                children = []
                def offline_factory(argv, **kwargs):
                    child = REAL_POPEN([sys.executable, "-I", "-c", "import time; time.sleep(30)"], **kwargs)
                    original = child.communicate
                    calls = []
                    def communicate(*a, **k):
                        calls.append(1)
                        if len(calls) == 1:
                            raise error_type()
                        return original(*a, **k)
                    child.communicate = communicate
                    children.append((child, calls))
                    return child
                with patch("adapter.subprocess.Popen", side_effect=offline_factory):
                    if error_type is OSError:
                        self.assert_code("adapter_failure", lambda: Client(KEY, True).evaluate("state", questions()))
                    else:
                        with self.assertRaises(error_type): Client(KEY, True).evaluate("state", questions())
                child, calls = children[0]
                self.assertEqual(len(calls), 2)
                self.assertIsNotNone(child.returncode)
                with self.assertRaises(ProcessLookupError): os.kill(child.pid, 0)

    def test_campaign_remaining_time_caps_request_timeout(self):
        timeouts = []
        def transport(payload, key, timeout, cap):
            timeouts.append(timeout)
            return canonical_bytes(response())
        client = Client(KEY, True, transport=transport, limits=Limits(max_elapsed_seconds=1))
        client._started = time.monotonic() - 0.8
        client.evaluate("state", questions())
        self.assertLessEqual(timeouts[0], 0.2)
        client._started = time.monotonic() - 2
        self.assert_code("resource_budget_exceeded", lambda: client.evaluate("state", questions()))
        self.assertEqual(len(timeouts), 1)


if __name__ == "__main__":
    unittest.main()
