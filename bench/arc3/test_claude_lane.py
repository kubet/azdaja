#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("arc3_claude_lane", HERE / "claude_lane.py")
assert SPEC and SPEC.loader
LANE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LANE)


class ClaudeLaneUnitTests(unittest.TestCase):
    def test_child_env_is_allowlisted_and_strips_arc_and_provider_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            binary = root / "bin" / "claude"
            old = dict(os.environ)
            os.environ["ARC_API_KEY"] = "forbidden"
            os.environ["ANTHROPIC_API_KEY"] = "forbidden"
            try:
                env = LANE.child_env(home, root, binary)
            finally:
                os.environ.clear()
                os.environ.update(old)
            self.assertNotIn("ARC_API_KEY", env)
            self.assertNotIn("ANTHROPIC_API_KEY", env)
            self.assertEqual(env["HOME"], str(home))
            self.assertEqual(env["TMPDIR"], str(root / "tmp"))

    def test_direct_command_uses_valid_strict_empty_mcp_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "bin" / "claude"
            command = LANE.base_command(binary, model="sonnet", structured=True)
        self.assertIn("--strict-mcp-config", command)
        index = command.index("--mcp-config")
        self.assertEqual(command[index + 1], '{"mcpServers":{}}')
        self.assertEqual(json.loads(command[index + 1]), {"mcpServers": {}})
        self.assertEqual(command.count("--mcp-config"), 1)

    def test_direct_command_is_fresh_no_tools_no_persistence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "bin" / "claude"
            command = LANE.base_command(binary, model="sonnet", structured=True)
        for flag in ("--print", "--safe-mode", "--no-session-persistence", "--tools", "--json-schema"):
            self.assertIn(flag, command)
        self.assertEqual(command[command.index("--tools") + 1], "")
        self.assertEqual(command[command.index("--model") + 1], "sonnet")
        self.assertNotIn("--resume", command)
        self.assertNotIn("--continue", command)

    def test_cli_failure_classifier_returns_only_fixed_enum(self) -> None:
        cases = {
            "auth": b"authentication login required",
            "invalid_model": b"invalid model selection",
            "cli_usage": b"error: unknown option; Usage:",
            "sandbox_permission": b"sandbox: operation not permitted",
            "rate_limit": b"HTTP 429 too many requests",
            "network": b"network connection timed out",
            "other": b"unclassified private detail",
        }
        for expected, private in cases.items():
            with self.subTest(expected=expected):
                category = LANE.classify_cli_failure(b"", private)
                self.assertEqual(category, expected)
                self.assertIn(category, LANE.FAILURE_CATEGORIES)
                self.assertNotIn(private.decode(), category)

    def test_main_relays_only_failure_enum(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = type("Args", (), {
                "mode": "action",
                "model": "sonnet",
                "failure_artifact": Path(directory) / "test-only",
            })()
            stderr = io.StringIO()
            with mock.patch.object(LANE, "parse_args", return_value=args), mock.patch.object(
                LANE, "action", side_effect=LANE.LaneError("rate_limit")
            ), mock.patch.object(sys, "stderr", stderr):
                self.assertEqual(LANE.main(), 2)
        self.assertEqual(stderr.getvalue(), "blocked: direct_claude_failure=rate_limit\n")

    def test_nonzero_cli_raises_only_classified_lane_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / "runtime"
            runtime.mkdir()
            claude = root / "claude"
            claude.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
            claude.chmod(0o700)
            failure_artifact = root / "retained.private"
            args = type("Args", (), {
                "claude": claude, "owner_home": root, "runtime_root": runtime,
                "model": "sonnet", "failure_artifact": failure_artifact,
            })()
            completed = __import__("subprocess").CompletedProcess([], 1, stdout=b"raw-stdout", stderr=b"sandbox: operation not permitted; private")
            with mock.patch.object(LANE.subprocess, "run", return_value=completed):
                with self.assertRaises(LANE.LaneError) as caught:
                    LANE.invoke(args, b"prompt", structured=False)
            self.assertEqual(caught.exception.category, "sandbox_permission")
            self.assertEqual(str(caught.exception), "sandbox_permission")
            retained = failure_artifact.read_bytes()
            self.assertEqual(list(runtime.iterdir()), [])
            self.assertEqual(
                retained,
                LANE.FAILURE_ARTIFACT_MAGIC
                + b"returncode=1\nstdout_length=10\nstderr_length=41\n\n"
                + b"raw-stdout"
                + b"sandbox: operation not permitted; private",
            )
            self.assertEqual(failure_artifact.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(LANE.LaneError):
                LANE.write_failure_artifact(failure_artifact, 9, b"new", b"new", runtime)
            self.assertEqual(failure_artifact.read_bytes(), retained)

    def test_invoke_passes_prompt_as_input_without_duplicate_stdin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / "runtime"
            runtime.mkdir()
            claude = root / "claude"
            claude.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
            claude.chmod(0o700)
            args = type("Args", (), {
                "claude": claude,
                "owner_home": root,
                "runtime_root": runtime,
                "model": "sonnet",
            })()
            completed = __import__("subprocess").CompletedProcess([], 0, stdout=b"{}", stderr=b"")
            with mock.patch.object(LANE.subprocess, "run", return_value=completed) as run:
                self.assertEqual(LANE.invoke(args, b"prompt", structured=False), b"{}")
            kwargs = run.call_args.kwargs
            self.assertEqual(kwargs["input"], b"prompt")
            self.assertNotIn("stdin", kwargs)

    def test_action_emits_only_exact_action_json(self) -> None:
        args = object()
        envelope = json.dumps({"structured_output": {"action": "ACTION4", "data": {}}}).encode()
        fake_stdin = mock.Mock()
        fake_stdin.buffer.read.return_value = b"private prompt"
        output = io.StringIO()
        with mock.patch.object(LANE, "invoke", return_value=envelope), mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", output):
            LANE.action(args)
        self.assertEqual(json.loads(output.getvalue()), {"action": "ACTION4", "data": {}})

    def test_sandbox_denies_owner_home_writes_except_disposable_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            disposable = Path(directory) / "disposable"
            profile = LANE.sandbox_profile(disposable)
            self.assertIn("(deny file-write*)", profile)
            self.assertIn(f'(allow file-write* (subpath "{disposable}"))', profile)


if __name__ == "__main__":
    unittest.main()
