"""Future-study model-resolution policy. Synthetic transports only, no live rerun."""
from dataclasses import replace
import json
import unittest
from unittest.mock import patch

import adapter
from adapter import AdapterError, Client, Limits, canonical_bytes
import run
from test_adapter import KEY, questions, response
from test_run import fixtures, answer


class ModelResolutionTests(unittest.TestCase):
    def setUp(self):
        for target in ("socket.create_connection", "adapter.subprocess.Popen"):
            guard = patch(target, side_effect=AssertionError("unmocked network or child forbidden"))
            guard.start()
            self.addCleanup(guard.stop)

    def client(self, bodies, **kwargs):
        self.sent = []
        def transport(payload, *_):
            self.sent.append(json.loads(payload))
            return bodies[len(self.sent) - 1]
        return Client(KEY, enabled=True, model="jev-latest", transport=transport,
                      resolved_model_allowlist=("jev-1.12", "jev-1.13"), **kwargs)

    def error(self, code, fn):
        with self.assertRaises(AdapterError) as caught:
            fn()
        self.assertEqual(str(caught.exception), code)
        return caught.exception

    def test_exact_identity_is_still_default_and_failure_records_only_safe_model_metadata(self):
        client = Client(KEY, enabled=True, model="jev-1.13", transport=lambda *_: canonical_bytes(response()))
        err = self.error("response_model_mismatch", lambda: client.evaluate("state", questions()))
        self.assertEqual(err.metrics["returned_model"], "jev-1.12")
        self.assertIsNone(err.response)
        self.assertIsNone(client.resolved_model)

    def test_allowlisted_resolution_pins_only_after_valid_response_and_keeps_alias_on_wire(self):
        client = self.client([canonical_bytes(response())] * 2)
        self.assertIsNone(client.resolved_model)
        first = client.evaluate("state", questions())
        self.assertEqual(client.resolved_model, "jev-1.12")
        self.assertEqual(first["metrics"]["resolved_model_pin"], "jev-1.12")
        client.evaluate("state", questions())
        self.assertEqual([r["model"] for r in self.sent], ["jev-latest", "jev-latest"])

    def test_second_allowlisted_identity_change_stops_without_repin_or_retry(self):
        second = response()
        second["model"] = "jev-1.13"
        client = self.client([canonical_bytes(response()), canonical_bytes(second)])
        client.evaluate("state", questions())
        self.error("response_model_changed", lambda: client.evaluate("state", questions()))
        self.assertEqual(client.resolved_model, "jev-1.12")
        self.error("adapter_poisoned", lambda: client.evaluate("state", questions()))
        self.assertEqual(len(self.sent), 2)

    def test_unlisted_and_moving_alias_echo_are_rejected_unbound(self):
        for name in ("jev-9.99", "jev-latest", "jev-preview"):
            body = response()
            body["model"] = name
            client = self.client([canonical_bytes(body)])
            self.error("response_model_not_allowlisted", lambda: client.evaluate("state", questions()))
            self.assertIsNone(client.resolved_model)
            self.error("adapter_poisoned", lambda: client.evaluate("state", questions()))

    def test_malformed_first_response_never_pins(self):
        body = response()
        body["usage"]["input_tokens"] = True
        client = self.client([canonical_bytes(body)])
        self.error("invalid_usage", lambda: client.evaluate("state", questions()))
        self.assertIsNone(client.resolved_model)
        self.error("adapter_poisoned", lambda: client.evaluate("state", questions()))

    def test_budget_crossing_retains_valid_body_but_does_not_pin(self):
        client = self.client([canonical_bytes(response())], limits=replace(Limits(), max_input_tokens=99))
        err = self.error("reported_token_budget_exceeded", lambda: client.evaluate("state", questions()))
        self.assertEqual(err.response["usage"]["input_tokens"], 100)
        self.assertIsNone(client.resolved_model)
        self.assertNotIn("resolved_model_pin", err.metrics)

    def test_invalid_resolution_configuration_is_preflight_only(self):
        for allowed in ((), [], ("jev-latest",), ("jev-1.12", "jev-1.12"), ("bad",), (None,)):
            self.error("invalid_model_resolution_policy", lambda: Client(KEY, model="jev-latest", resolved_model_allowlist=allowed))
        self.error("invalid_model_resolution_policy", lambda: Client(KEY, model="jev-1.12", resolved_model_allowlist=("jev-1.12",)))
        client = Client(KEY, enabled=False, model="jev-latest", resolved_model_allowlist=("jev-1.12",))
        self.error("adapter_disabled_or_missing_key", lambda: client.evaluate("state", questions()))

    def test_alias_without_resolution_policy_is_rejected_before_transport(self):
        for alias in ("jev-latest", "jev-preview"):
            self.error("model_alias_requires_explicit_resolution_policy", lambda: Client(KEY, model=alias))

    def test_live_cli_cannot_guess_a_model_before_reading_credentials(self):
        with patch.object(run, "Client") as client, patch.object(run, "read_key") as key, patch("sys.stderr"):
            with self.assertRaises(SystemExit) as caught:
                run.main(["--live", "--receipt", "must-not-be-created.json"])
            self.assertEqual(caught.exception.code, 2)
            client.assert_not_called()
            key.assert_not_called()

    def test_json_escaping_characters_in_credentials_are_rejected_before_transport(self):
        for key in ('synthetic"quoted-token', 'synthetic\\backslash-token'):
            self.error("invalid_api_key", lambda: Client(key, enabled=True))

    def test_escaped_credential_echo_is_rejected_without_metadata_or_body_leak(self):
        body = response()
        body["model"] = KEY
        escaped = "".join("\\u%04x" % ord(c) for c in KEY)
        raw = canonical_bytes(body).replace(KEY.encode(), escaped.encode())
        self.assertNotIn(KEY.encode(), raw)
        client = self.client([raw])
        err = self.error("response_contains_credential", lambda: client.evaluate("state", questions()))
        self.assertIsNone(err.response)
        self.assertNotIn("returned_model", err.metrics)
        self.assertNotIn(KEY, str(err.metrics))
        self.assertIsNone(client.resolved_model)

    def test_wrong_gold_valid_response_pins_then_semantic_gate_stops(self):
        body = {"model": "jev-1.12", "answers": {"q0": answer("contradicted")},
                "usage": {"input_tokens": 10, "output_tokens": 1}}
        client = self.client([canonical_bytes(body)])
        receipt = run.run_campaign(client, fixtures(), {})
        self.assertEqual(client.resolved_model, "jev-1.12")
        self.assertEqual(receipt["stop_reason"], "smoke_label_error")
        self.assertEqual(len(self.sent), 1)
        self.assertEqual(receipt["calls"][0]["metrics"]["resolved_model_pin"], "jev-1.12")

    def test_checkpoint_failure_prevents_a_second_request(self):
        body = {"model": "jev-1.12", "answers": {"q0": answer("supported")},
                "usage": {"input_tokens": 10, "output_tokens": 1}}
        client = self.client([canonical_bytes(body)])
        def failing_checkpoint(receipt):
            if receipt["calls"] and receipt["calls"][-1]["status"] == "completed":
                raise OSError("synthetic checkpoint failure")
        with self.assertRaises(OSError):
            run.run_campaign(client, fixtures(), {}, failing_checkpoint)
        self.assertEqual(len(self.sent), 1)


if __name__ == "__main__":
    unittest.main()
