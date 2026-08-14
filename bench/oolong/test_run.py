import hashlib
import importlib.util
import json
import os
import secrets
import shutil
import stat
import sys
import tempfile
import types
import unittest
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("azdaja_oolong_run",HERE/"run.py")
RUN=importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name]=RUN
assert SPEC.loader is not None
SPEC.loader.exec_module(RUN)


class ControllerTests(unittest.TestCase):
    def test_fixture_integrity_prompt_and_strict_score(self):
        fixture=RUN.load_fixture(str(HERE/"row-645.json"),None)
        self.assertEqual(fixture.expected_canonical,"Answer: 132")
        self.assertEqual(fixture.context_sha256,"05e4419a7280c91b3bbf1ea97629bfc235ee0eb23e67e1f0eeb21fc38b485bf2")
        prompt=RUN.build_prompt(fixture)
        self.assertIn("do not access the network",prompt)
        self.assertNotIn(fixture.expected_canonical,prompt)
        self.assertTrue(RUN.strict_score("Answer: 132",fixture)["correct"])
        self.assertFalse(RUN.strict_score("Answer: 132\nextra",fixture)["correct"])

    def test_gold_parser_rejects_free_text(self):
        self.assertEqual(RUN.parse_gold("['ham']","which label?"),("Label","ham","Label: ham"))
        with self.assertRaises(RUN.BenchError):
            RUN.parse_gold("Answer: 132","how many?")

    @unittest.skipUnless(hasattr(os,"getuid"),"Unix-only private runtime")
    def test_cleanup_accepts_only_owned_short_runtime(self):
        uid=os.getuid();root=Path(tempfile.mkdtemp(prefix="azdaja-cleanup-test-"));errors=[]
        try:
            private=root/"azdaja-state"/"jcode-api";private.mkdir(parents=True,mode=0o700)
            runtime=Path("/tmp")/f"azdaja-{uid}"/f"r-{secrets.token_hex(8)}"
            runtime.mkdir(parents=True,mode=0o700);os.chmod(runtime.parent,0o700);os.chmod(runtime,0o700)
            (private/"runtime-dir").write_text(str(runtime),encoding="utf-8")
            RUN.cleanup_private_azdaja_daemon(root,errors)
            self.assertEqual(errors,[]);self.assertFalse(runtime.exists())
            victim=root/"must-survive";victim.mkdir();(private/"runtime-dir").write_text(str(victim),encoding="utf-8")
            RUN.cleanup_private_azdaja_daemon(root,errors)
            self.assertTrue(victim.exists());self.assertTrue(errors)
        finally:
            import shutil
            shutil.rmtree(root,ignore_errors=True)

    def test_private_artifact_is_owner_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"trace"
            meta=RUN.write_private_artifact(path,"private trajectory")
            self.assertEqual(meta["sha256"],RUN.sha256_path(path))
            if os.name=="posix":self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o600)


    def test_per_arm_task_copy_is_random_read_only_and_prompt_is_blind(self):
        fixture = RUN.load_fixture(str(HERE / "row-645.json"), None)
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "arm"
            run_dir.mkdir(mode=0o700)
            task_dir, copied, integrity = RUN.stage_task_context(fixture, run_dir)
            self.assertRegex(copied.name, r"^[0-9a-f]{32}\.txt$")
            self.assertEqual(list(task_dir.iterdir()), [copied])
            self.assertEqual(stat.S_IMODE(copied.stat().st_mode), 0o444)
            self.assertEqual(RUN.sha256_path(copied), fixture.context_sha256)
            prompt = RUN.build_prompt(fixture, copied)
            self.assertIn(copied.name, prompt)
            self.assertNotIn(str(task_dir), prompt)
            self.assertNotIn(str(fixture.context_path), prompt)
            for forbidden in (
                "oolongbench/oolong-synth", "validation", "117010248",
                fixture.context_sha256, "Trustworthy context metadata",
                str(fixture.context_bytes), str(fixture.context_chars),
                str(fixture.context_lines),
            ):
                self.assertNotIn(forbidden, prompt)
            finished = RUN.finalize_task_context_integrity(
                fixture, task_dir, copied, integrity
            )
            self.assertTrue(finished["asserted_after"])
            copied.chmod(0o644)
            changed = RUN.finalize_task_context_integrity(
                fixture, task_dir, copied, integrity
            )
            self.assertFalse(changed["asserted_after"])

    def test_authoritative_usage_accounting_and_missing_evidence(self):
        jcode = "\n".join(
            json.dumps(row)
            for row in (
                {"type": "tokens", "input": 10, "output": 2,
                 "cache_read_input": 3, "cache_creation_input": None},
                {"type": "tokens", "input": 5, "output": 1,
                 "cache_read_input": 0, "cache_creation_input": 4},
                {"type": "done", "usage": {"input_tokens": 999,
                 "output_tokens": 999}},
            )
        )
        self.assertEqual(
            RUN.parse_jcode_usage(jcode, "[Tokens] upload: 888 download: 888"),
            {"input_tokens": 15, "output_tokens": 3, "cache_read_tokens": 3,
             "cache_write_tokens": 4, "total_tokens": 18},
        )
        prime_rows = [
            {"type": "message_end", "message": {"role": "assistant", "usage": {
                "input": 2, "output": 3, "cacheRead": 5, "cacheWrite": 7,
                "totalTokens": 17}}},
            {"type": "message_end", "message": {"role": "assistant", "usage": {
                "input": 11, "output": 13, "cacheRead": 17, "cacheWrite": 19,
                "totalTokens": 60}}},
        ]
        self.assertEqual(
            RUN.sum_usage_fields(prime_rows, prime=True),
            {"input_tokens": 13, "output_tokens": 16, "cache_read_tokens": 22,
             "cache_write_tokens": 26, "total_tokens": 77},
        )
        missing = RUN.sum_usage_fields(
            prime_rows + [{"type": "message_end", "message": {"role": "assistant"}}],
            prime=True,
        )
        self.assertTrue(all(value is None for value in missing.values()))
        effective = RUN.combine_usage(
            RUN.parse_jcode_usage(jcode, ""), None, require_subusage=True
        )
        evidence = RUN.usage_evidence_assertion(
            effective,
            root_usage=RUN.parse_jcode_usage(jcode, ""),
            subusage_required=True,
            azdaja_usage=None,
        )
        self.assertFalse(evidence["valid"])

    def test_tool_event_scan_rejects_network_and_external_dataset_access(self):
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory) / "task"
            task.mkdir()
            context = task / "abc.txt"
            context.write_text("fixture", encoding="utf-8")
            safe = "\n".join(json.dumps(row) for row in (
                {"type": "tool_start", "id": "1", "name": "bash"},
                {"type": "tool_input", "delta": json.dumps(
                    {"command": f"wc -l {context}"})},
                {"type": "tool_exec", "id": "1", "name": "bash"},
            ))
            self.assertTrue(RUN.scan_tool_policy(
                "jcode-native", safe, task_dir=task, context_path=context
            )["asserted"])
            unsafe = "\n".join(json.dumps(row) for row in (
                {"type": "tool_start", "id": "2", "name": "bash"},
                {"type": "tool_input", "delta": json.dumps(
                    {"command": "python -c 'import requests; requests.get(\"https://x\")'"})},
                {"type": "tool_exec", "id": "2", "name": "bash"},
            ))
            policy = RUN.scan_tool_policy(
                "jcode-native", unsafe, task_dir=task, context_path=context
            )
            self.assertFalse(policy["asserted"])
            self.assertIn("network access", {v["category"] for v in policy["violations"]})
            prime = json.dumps({
                "type": "tool_execution_start", "toolName": "ipython",
                "args": {"code": "from datasets import load_dataset; load_dataset('x')"},
            })
            self.assertFalse(RUN.scan_tool_policy(
                "prime-agent", prime, task_dir=task, context_path=context
            )["asserted"])

    def test_retained_trajectory_is_fully_redacted_without_truncation(self):
        jwt = "eyJhbGciOiJub25lIn0.eyJzdWIiOiJzZWNyZXQifQ.signature"
        content = "x" * 20000 + "\n" + json.dumps({
            "type": "tokens", "input": 7, "output": 3,
            "access_token": jwt,
        })
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stdout.ndjson"
            metadata = RUN.write_private_artifact(path, content)
            retained = path.read_text(encoding="utf-8")
            self.assertGreater(len(retained), 16384)
            self.assertIn('"type": "tokens"', retained)
            self.assertIn('"input": 7', retained)
            self.assertNotIn(jwt, retained)
            self.assertIn("<redacted>", retained)
            self.assertTrue(metadata["credential_redacted"])
            self.assertFalse(metadata["contains_private_raw_trajectory"])

    def test_purge_retains_only_trajectory_and_deletes_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "arm"
            (run_dir / "home" / ".jcode").mkdir(parents=True)
            (run_dir / "home" / ".jcode" / "openai-auth.json").write_text("secret")
            (run_dir / "prime-home").mkdir()
            (run_dir / "task").mkdir()
            RUN.write_private_artifact(run_dir / "stdout.ndjson", "out")
            RUN.write_private_artifact(run_dir / "stderr.log", "err")
            errors = []
            result = RUN.purge_transient_run_state(
                run_dir, {"stdout.ndjson", "stderr.log"}, errors
            )
            self.assertEqual(errors, [])
            self.assertTrue(result["credential_homes_deleted"])
            self.assertEqual(
                {entry.name for entry in run_dir.iterdir()},
                {"stdout.ndjson", "stderr.log"},
            )

    def test_records_executable_and_staged_skill_component_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / "example-tool"
            executable.write_text("#!/bin/sh\necho example-tool-1.2.3\n", encoding="utf-8")
            executable.chmod(0o700)
            identity = RUN.executable_identity(str(executable), "example")
            self.assertEqual(identity["sha256"], RUN.sha256_path(executable))
            self.assertIn("example-tool-1.2.3", identity["version"])

            source_home = root / "source-home"
            auth = source_home / ".jcode" / "openai-auth.json"
            auth.parent.mkdir(parents=True)
            auth.write_text(json.dumps({
                "openai_accounts": [{"label": "active", "access_token": "private"}],
                "active_openai_account": "active",
            }), encoding="utf-8")
            skill = root / "skill"
            skill.mkdir()
            shutil.copyfile(executable, skill / "azdaja")
            (skill / "azdaja").chmod(0o700)
            (skill / "config.toml").write_text("config", encoding="utf-8")
            (skill / "SKILL.md").write_text("# azdaja", encoding="utf-8")
            manifest = RUN.make_isolated_jcode_home(
                source_home, root / "isolated-jcode", skill
            )
            self.assertIsNotNone(manifest)
            for filename in ("azdaja", "config.toml", "SKILL.md"):
                self.assertTrue(manifest["files"][filename]["staged_matches_source"])
            self.assertIn("example-tool-1.2.3", manifest["staged_binary_identity"]["version"])
            self.assertTrue(RUN.finalize_staged_skill_hashes(manifest)["asserted_after"])

    def test_direct_solo_run_one_uses_staged_product_and_all_trace_depths(self):
        fixture = RUN.load_fixture(str(HERE / "row-645.json"), None)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_home = root / "source-home"
            auth = source_home / ".jcode" / "openai-auth.json"
            auth.parent.mkdir(parents=True)
            auth.write_text(json.dumps({
                "openai_accounts": [{"label": "active", "access_token": "private"}],
                "active_openai_account": "active",
            }), encoding="utf-8")
            skill = root / "skill"
            skill.mkdir()
            binary = skill / "azdaja"
            binary.write_text("#!/bin/sh\necho azdaja-test-1.0\n", encoding="utf-8")
            binary.chmod(0o700)
            (skill / "config.toml").write_text("config", encoding="utf-8")
            (skill / "SKILL.md").write_text("# azdaja", encoding="utf-8")
            work = root / "work"
            work.mkdir()
            args = SimpleNamespace(
                timeout=10, seed=7, jcode="unused-jcode",
                executable_identities={},
            )

            def fake_execute(command, env, timeout, cwd):
                self.assertEqual(command[1], "solo")
                self.assertEqual(command[2], fixture.metadata["question"])
                self.assertEqual(command[3], "-f")
                self.assertEqual(command[5:9], ["--model", RUN.MODEL, "--sub-model", RUN.MODEL])
                self.assertEqual(Path(command[0]).parent.name, "azdaja")
                self.assertEqual(Path(env["AZDAJA_CONFIG"]), Path(command[0]).parent / "config.toml")
                self.assertEqual(Path(cwd) / command[4], next(Path(cwd).iterdir()))
                rows = [
                    {"timestamp_ms": 1, "depth": 0, "provider": "OpenAI",
                     "model": RUN.MODEL, "input_tokens": 10, "output_tokens": 2,
                     "cache_read_tokens": 3, "latency_ms": 4},
                    {"timestamp_ms": 2, "depth": 1, "provider": "OpenAI OAuth",
                     "model": RUN.MODEL, "input_tokens": 5, "output_tokens": 1,
                     "cache_read_tokens": 0, "latency_ms": 2},
                ]
                Path(env["AZDAJA_MODEL_TRACE"]).write_text(
                    "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
                )
                Path(env["AZDAJA_SOLO_TRACE"]).write_text(
                    "=== result ===\nAnswer: 132\n", encoding="utf-8"
                )
                return 0, "Answer: 132\n", "", False, 0.25

            with mock.patch.object(RUN, "execute", side_effect=fake_execute), \
                    mock.patch.object(RUN, "cleanup_run", return_value=[]):
                row = RUN.run_one(
                    arm_name="jcode-azdaja", repetition=1, ordinal=1,
                    fixture=fixture, prompt=None, args=args, root=root,
                    source_home=source_home, skill=skill,
                    auth_jcode={"asserted": True}, auth_prime={}, work_root=work,
                )
            self.assertTrue(row["success"])
            self.assertEqual(row["activation_mode"], "direct_solo_product")
            self.assertTrue(row["product_lifecycle_assertion"]["asserted"])
            self.assertEqual(
                row["usage"],
                {"input_tokens": 15, "output_tokens": 3,
                 "cache_read_tokens": 3, "cache_write_tokens": 0,
                 "total_tokens": 18},
            )
            self.assertEqual(row["root_usage"]["total_tokens"], 12)
            self.assertEqual(row["azdaja_model_usage"]["depth_counts"], {"0": 1, "1": 1})
            self.assertTrue(row["efficiency_evidence"]["valid"])
            self.assertTrue(row["trace_capture_assertion"]["asserted"])
            self.assertFalse(row["tool_access_policy_assertion"]["containment_asserted"])
            self.assertIsNone(row["task_prompt_sha256"])
            self.assertEqual(
                row["treatment_prompt_sha256"],
                RUN.hashlib.sha256(fixture.metadata["question"].encode()).hexdigest(),
            )
            arm_dir = Path(row["trajectory_run_directory"])
            self.assertEqual(
                {path.name for path in arm_dir.iterdir()},
                {"stdout.ndjson", "stderr.log", "azdaja-model-usage.jsonl",
                 "azdaja-solo-trace.log"},
            )

    def test_azdaja_trace_is_fail_closed_for_error_and_malformed_rows(self):
        valid = {
            "timestamp_ms": 1, "depth": 0, "provider": "OpenAI",
            "model": RUN.MODEL, "input_tokens": 1, "output_tokens": 2,
            "cache_read_tokens": 0, "latency_ms": 3,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.jsonl"
            path.write_text(json.dumps(valid) + "\nnot-json\n", encoding="utf-8")
            self.assertIsNone(RUN.parse_azdaja_usage(path))
            path.write_text(
                json.dumps(valid) + "\n" + json.dumps(
                    {"timestamp_ms": 2, "depth": 1, "error": "provider_call_failed"}
                ) + "\n", encoding="utf-8"
            )
            self.assertIsNone(RUN.parse_azdaja_usage(path))
            setup_error = {
                "timestamp_ms": 2,
                "depth": 1,
                "error": "provider_call_failed",
                "stage": "session_setup",
            }
            path.write_text(
                json.dumps(valid) + "\n" + json.dumps(setup_error) + "\n",
                encoding="utf-8",
            )
            setup_usage = RUN.parse_azdaja_usage(path)
            self.assertIsNone(setup_usage)
            route_evidence = RUN.parse_azdaja_route_evidence(path)
            self.assertEqual(route_evidence["depth_counts"], {"0": 1})
            self.assertEqual(route_evidence["transport_error_rows"], 1)
            self.assertEqual(route_evidence["routes"], [])
            self.assertEqual(route_evidence["route_rows"], [])
            self.assertFalse(
                RUN.runtime_assertion("jcode-azdaja", "", route_evidence)["asserted"]
            )
            self.assertFalse(
                RUN.direct_solo_lifecycle_assertion(
                    exit_code=0,
                    timed_out=False,
                    response="Answer: 1",
                    trace_usage=setup_usage,
                )["asserted"]
            )
            usage = RUN.usage_fields_from_azdaja(RUN.parse_azdaja_usage(path))
            self.assertFalse(RUN.direct_solo_usage_evidence(usage, None)["valid"])

    def test_actual_v43_trace_samples_are_conservative_across_adapter_parsers(self):
        fixtures = Path(__file__).resolve().parents[1] / "longbench2" / "fixtures"
        success = fixtures / "v43-rust-serde-success.jsonl"
        retry = fixtures / "v43-rust-serde-transient-retry.jsonl"
        self.assertEqual(
            hashlib.sha256(success.read_bytes()).hexdigest(),
            "41e4456b4a6601424ae03b3b3d0821a4866666a8e117cd5f6d6e5d51a17f754f",
        )
        self.assertEqual(
            hashlib.sha256(retry.read_bytes()).hexdigest(),
            "9294429a6354f9e42690adbf1b6ac453fd3d0657d035b357adbf9a9dcc3b8f5c",
        )
        success_route = RUN.parse_azdaja_route_evidence(success)
        self.assertEqual(len(success_route["route_rows"]), 1)
        self.assertTrue(RUN.runtime_assertion("jcode-azdaja", "", success_route)["asserted"])
        self.assertIsNotNone(RUN.parse_azdaja_usage(success))

        retry_route = RUN.parse_azdaja_route_evidence(retry)
        self.assertEqual(retry_route["routes"], [])
        self.assertEqual(retry_route["route_rows"], [])
        self.assertEqual(retry_route["transport_error_rows"], 1)
        self.assertFalse(RUN.runtime_assertion("jcode-azdaja", "", retry_route)["asserted"])
        self.assertIsNone(RUN.parse_azdaja_usage(retry))

        with tempfile.TemporaryDirectory() as directory:
            success_only_retry = Path(directory) / "success-only-retry.jsonl"
            success_only_retry.write_bytes(retry.read_bytes().splitlines(keepends=True)[1])
            route = RUN.parse_azdaja_route_evidence(success_only_retry)
            self.assertEqual(route["routes"], [])
            self.assertEqual(route["route_rows"], [])
            self.assertEqual(route["transport_error_rows"], 1)
            self.assertIsNone(RUN.parse_azdaja_usage(success_only_retry))

    def test_fresh_candidate_requires_exact_explicit_repair_model(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory)
            (skill / "config.toml").write_text(
                'default_model="gpt-5.6-luna"\n', encoding="utf-8"
            )
            self.assertEqual(
                RUN.configure_azdaja_repair_model_from_skill(skill), RUN.MODEL
            )
            with self.assertRaisesRegex(RUN.BenchError, "explicit"):
                RUN.configure_azdaja_repair_model_from_skill(
                    skill, require_explicit=True
                )
            (skill / "config.toml").write_text(
                'default_model="gpt-5.6-luna"\n'
                'jcode_repair_model=" gpt-5.4-mini "\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RUN.BenchError, "whitespace"):
                RUN.configure_azdaja_repair_model_from_skill(
                    skill, require_explicit=True
                )

    def test_v2_route_rows_require_typed_category_and_setup_error_shape(self):
        base = {
            "schema_version": 2,
            "event": "model_attempt",
            "timestamp_ms": 1,
            "depth": 0,
            "request_id": "request",
            "attempt": 1,
            "outcome": "succeeded",
            "provider": "OpenAI OAuth",
            "model": RUN.MODEL,
            "input_tokens": 1,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.jsonl"
            path.write_text(json.dumps(base) + "\n", encoding="utf-8")
            self.assertIsNone(RUN.parse_azdaja_route_evidence(path))
            failed = dict(base)
            failed.update({
                "category": "turn",
                "outcome": "failed",
                "error": "provider_call_failed",
                "stage": "session_setup",
            })
            path.write_text(json.dumps(failed) + "\n", encoding="utf-8")
            self.assertIsNone(RUN.parse_azdaja_route_evidence(path))
            downgraded = dict(base)
            downgraded.update({
                "schema_version": 1,
                "category": "repair",
                "model": "gpt-5.4-mini",
            })
            path.write_text(json.dumps(downgraded) + "\n", encoding="utf-8")
            evidence = RUN.parse_azdaja_route_evidence(path)
            self.assertEqual(evidence["route_rows"][0]["category"], "turn")
            self.assertFalse(
                RUN.runtime_assertion(
                    "jcode-azdaja", evidence,
                    repair_model="gpt-5.4-mini",
                )["asserted"]
            )

    def test_category_aware_route_assertion_requires_mini_only_for_root_repairs(self):
        original = RUN.AZDAJA_REPAIR_MODEL
        try:
            RUN.configure_azdaja_repair_model("gpt-5.4-mini")
            evidence = {
                "routes": ["openai/gpt-5.4-mini", f"openai/{RUN.MODEL}"],
                "route_rows": [
                    {"depth": 0, "category": "turn", "provider": "openai", "model": RUN.MODEL},
                    {"depth": 0, "category": "repair", "provider": "openai", "model": "gpt-5.4-mini"},
                    {"depth": 1, "category": "turn", "provider": "openai", "model": RUN.MODEL},
                ],
                "transport_error_rows": 0,
            }
            route = RUN.runtime_assertion("jcode-azdaja", "", evidence)
            self.assertTrue(route["asserted"])
            self.assertEqual(route["expected_repair_model"], "gpt-5.4-mini")
            evidence["route_rows"][0]["model"] = "gpt-5.4-mini"
            self.assertFalse(
                RUN.runtime_assertion("jcode-azdaja", "", evidence)["asserted"]
            )
            repair_only = {
                "routes": ["openai/gpt-5.4-mini"],
                "route_rows": [{
                    "depth": 0,
                    "category": "repair",
                    "provider": "openai",
                    "model": "gpt-5.4-mini",
                }],
                "transport_error_rows": 0,
            }
            self.assertFalse(
                RUN.runtime_assertion(
                    "jcode-azdaja", "", repair_only
                )["asserted"]
            )
        finally:
            RUN.configure_azdaja_repair_model(original)

    def test_exact_unicode_root_context_scan_and_no_text_retention(self):
        exact = "".join(chr(0x400 + index) for index in range(120))
        context = "prefix\r\n" + exact + "\nsuffix"
        transcript = "root:" + exact + ":reply"
        finding = RUN.exact_common_substring_scan(context, transcript)
        self.assertTrue(finding["leak_detected"])
        self.assertEqual(finding["verified_match_chars"], 100)
        self.assertFalse(finding["matched_text_retained"])
        self.assertNotIn(exact[:100], json.dumps(finding, ensure_ascii=False))
        decomposed = "e\u0301" * 60
        composed = "é" * 60
        self.assertFalse(
            RUN.exact_common_substring_scan(decomposed, composed)["leak_detected"]
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context_path = root / "context.txt"
            trace_path = root / "azdaja-solo-trace.log"
            raw = ("A\r\n" * 34).encode("utf-8")
            context_path.write_bytes(raw)
            trace_path.write_bytes(b"before" + raw + b"after")
            assertion = RUN.scan_context_file_against_solo_trace(
                context_path,
                trace_path,
                expected_context_sha256=RUN.sha256_path(context_path),
            )
            self.assertTrue(assertion["leak_detected"])
            self.assertEqual(assertion["normalization"], "none")

    def test_root_token_economy_authority_fallback_and_failure_normalization(self):
        native = "\n".join(json.dumps(row) for row in (
            {"type": "tool_output", "output": "ignore-update"},
            {"type": "tool_result", "content": "ignore-alias"},
            {"type": "tool_done", "output": "abcdefgh"},
            {"type": "done", "provider": "OpenAI", "model": RUN.MODEL},
        ))
        economy = RUN.tool_result_root_token_economy("jcode-native", native)
        self.assertEqual(economy["root_input_tokens"], 2.0)
        self.assertEqual(economy["authority_kind"], "character_fallback")
        usage = {"depth_usage": {"0": {"input_tokens": 17}}}
        self.assertEqual(
            RUN.azdaja_root_token_economy(usage, None)["root_input_tokens"], 17
        )
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "trace"
            request = "🦀abc"
            trace.write_bytes(
                (
                    f'=== root request begin request_id="r" model="m" '
                    f'request_chars={len(request)} ===\n{request}\n'
                    '=== root request end request_id="r" ===\n'
                ).encode("utf-8")
            )
            fallback = RUN.azdaja_root_token_economy(None, trace)
            self.assertEqual(fallback["root_input_tokens"], len(request) / 4)
            self.assertTrue(fallback["estimated"])
        cases = {
            "adapter_parser": {"kind": "execution", "message": "adapter response parser failed"},
            "transport": {"kind": "route_assertion", "message": "bad route"},
            "timeout": {"kind": "timeout", "message": "turn timed out"},
            "depth": {"kind": "execution", "message": "maximum recursion depth exceeded"},
            "monty_subset_tax": {"kind": "execution", "message": "Monty unsupported syntax"},
            "other_execution": {"kind": "controller", "message": "disk failure"},
            "root_context_leak": {"kind": "root_context_leak", "message": "leak"},
        }
        for expected, failure in cases.items():
            self.assertEqual(RUN.normalize_failure_kind(failure), expected)

    def test_control_root_economy_uses_only_canonical_terminal_events(self):
        prime = "\n".join(json.dumps(row) for row in (
            {"type": "tool_execution_update", "result": {"content": "ignore"}},
            {"type": "tool_result", "result": {"content": "ignore-alias"}},
            {"type": "tool_execution_end", "result": {
                "content": [{"type": "text", "text": "éé"}, {"text": "ab"}]
            }},
        ))
        economy = RUN.tool_result_root_token_economy("prime-agent", prime)
        self.assertEqual(economy["source_characters"], 4)
        self.assertEqual(economy["root_input_tokens"], 1.0)
        self.assertEqual(economy["result_events"], 1)

        malformed_jcode = "\n".join(json.dumps(row) for row in (
            {"type": "tool_done", "content": "wrong alias"},
            {"type": "done"},
        ))
        missing = RUN.tool_result_root_token_economy("jcode-native", malformed_jcode)
        self.assertTrue(missing["missing"])
        self.assertIsNone(missing["root_input_tokens"])
        self.assertEqual(missing["authority_kind"], "missing")
        self.assertEqual(missing["malformed_result_events"], 1)

        malformed_prime = json.dumps({
            "type": "tool_execution_end", "output": "wrong alias"
        })
        self.assertTrue(
            RUN.tool_result_root_token_economy("prime-agent", malformed_prime)["missing"]
        )

    def test_suite_campaign_profile_is_exact_and_has_78_rows(self):
        suite = SimpleNamespace(fixtures=tuple(range(RUN.CAMPAIGN_FIXTURE_COUNT)))
        args = SimpleNamespace(
            model=RUN.CAMPAIGN_MODEL,
            reasoning=RUN.CAMPAIGN_REASONING,
            arms=list(RUN.CAMPAIGN_ARMS),
            repetitions=RUN.CAMPAIGN_REPETITIONS,
            seed=RUN.CAMPAIGN_SEED,
            timeout=RUN.CAMPAIGN_TIMEOUT_SECONDS,
        )
        RUN.assert_campaign_profile(args, suite)
        self.assertEqual(RUN.CAMPAIGN_ROW_COUNT, 78)
        mutations = {
            "fixtures": (args, SimpleNamespace(fixtures=tuple(range(25)))),
            "arms": (SimpleNamespace(**{**vars(args), "arms": list(reversed(args.arms))}), suite),
            "seed": (SimpleNamespace(**{**vars(args), "seed": args.seed + 1}), suite),
            "timeout": (SimpleNamespace(**{**vars(args), "timeout": 601}), suite),
        }
        for label, (bad_args, bad_suite) in mutations.items():
            with self.subTest(label=label), self.assertRaises(RUN.BenchError):
                RUN.assert_campaign_profile(bad_args, bad_suite)

    def test_without_acknowledgement_never_invokes_a_cli(self):
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(RUN.subprocess, "run") as run, \
                mock.patch.object(RUN.subprocess, "Popen") as popen:
            with self.assertRaises(RUN.BenchError):
                RUN.main([
                    "--row", str(HERE / "row-645.json"),
                    "--output", str(Path(directory) / "result.jsonl"),
                ])
            run.assert_not_called()
            popen.assert_not_called()

    def test_generic_official_answer_prefixes_are_strict(self):
        kind, value, canonical = RUN.parse_gold(
            "[41714]", "Give your final answer in the form 'User: [X]'"
        )
        self.assertEqual((kind, value, canonical), ("User", 41714, "User: 41714"))
        fixture = types.SimpleNamespace(
            expected_kind=kind,
            expected_value=value,
            expected_canonical=canonical,
        )
        self.assertTrue(RUN.strict_score("User: 41714\n", fixture)["correct"])
        self.assertFalse(RUN.strict_score("Answer: 41714", fixture)["correct"])
        self.assertIn(
            "User", RUN.strict_score("Answer: 41714", fixture)["parse_error"]
        )

    def test_suite_manifest_and_schedule_are_hash_bound_and_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = root / "row.json"
            context = root / "context.txt"
            shutil.copy2(HERE / "row-645.json", row)
            shutil.copy2(HERE / "context-131072.txt", context)
            row.chmod(0o600)
            context.chmod(0o600)
            metadata = json.loads(row.read_text(encoding="utf-8"))
            entry = {
                "fixture_id": "f-1",
                "row": row.name,
                "context": context.name,
                "row_sha256": RUN.sha256_path(row),
                "context_sha256": RUN.sha256_path(context),
            }
            for key in (
                "dataset", "context_len", "context_window_id", "task_group", "task"
            ):
                entry[key] = metadata[key]
            manifest = root / "suite.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "source": "oolongbench/oolong-synth",
                        "split": metadata["split"],
                        "upstream_commit": "0" * 40,
                        "selection": "test",
                        "fixtures": [entry],
                    }
                ),
                encoding="utf-8",
            )
            manifest.chmod(0o600)
            suite = RUN.load_suite_manifest(str(manifest))
            args = SimpleNamespace(
                seed=7,
                repetitions=2,
                arms=["jcode-azdaja", "jcode-native"],
                model="gpt-5.6-luna",
                reasoning="medium",
                timeout=300,
            )
            components = {
                "azdaja": {"sha256": "a" * 64, "bytes": 1},
                "config.toml": {"sha256": "c" * 64, "bytes": 2},
                "SKILL.md": {"sha256": "d" * 64, "bytes": 3},
            }
            candidate = {
                "sha256": RUN.hashlib.sha256(
                    RUN.canonical_json_bytes(dict(sorted(components.items())))
                ).hexdigest(),
                "components": components,
            }
            controller = {"sha256": "b" * 64, "bytes": 1, "path": "/controller"}
            executable = {
                "path": "/azdaja", "sha256": "a" * 64, "bytes": 1,
                "version": "azdaja 1", "version_command": ["/azdaja", "--version"],
            }
            jcode = {
                "path": "/jcode", "sha256": "e" * 64, "bytes": 1,
                "version": "jcode 1", "version_command": ["/jcode", "--version"],
            }
            executables = {"azdaja": executable, "jcode": jcode}
            first = RUN.build_suite_schedule(suite, args, candidate, controller, executables)
            second = RUN.build_suite_schedule(suite, args, candidate, controller, executables)
            self.assertEqual(first, second)
            self.assertEqual(len(first["jobs"]), 4)
            self.assertEqual(len({job["run_id"] for job in first["jobs"]}), 4)
            args.model = "other-model"
            changed = RUN.build_suite_schedule(
                suite, args, candidate, controller, executables
            )
            self.assertNotEqual(first["schedule_id"], changed["schedule_id"])

    def test_suite_output_prefix_rejects_duplicates_and_scores_only_when_complete(self):
        jobs = [
            {
                "run_id": "r1",
                "fixture_id": "f",
                "row_sha256": "1" * 64,
                "context_sha256": "2" * 64,
                "ordinal": 1,
                "arm": "a",
                "repetition": 1,
            },
            {
                "run_id": "r2",
                "fixture_id": "f",
                "row_sha256": "1" * 64,
                "context_sha256": "2" * 64,
                "ordinal": 2,
                "arm": "b",
                "repetition": 1,
            },
        ]
        schedule = {
            "schedule_id": "s",
            "configuration": {
                "model": "m",
                "reasoning": "medium",
                "candidate": None,
                "controller": {"sha256": "c" * 64},
            },
            "jobs": jobs,
        }
        def terminal(job):
            return {
                "record_type": "inference",
                "schedule_id": "s",
                "run_id": job["run_id"],
                "fixture_id": "f",
                "row_sha256": "1" * 64,
                "context_sha256": "2" * 64,
                "execution_ordinal": job["ordinal"],
                "arm": job["arm"],
                "repetition": 1,
                "model": "m",
                "reasoning": "medium",
                "candidate_sha256": None,
                "controller_sha256": "c" * 64,
                "success": None,
                "score": None,
                "scoring_status": "deferred",
                "execution_success": True,
                "response": "Answer: 0",
            }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.jsonl"
            first = terminal(jobs[0])
            RUN.write_jsonl(output, first)
            self.assertEqual(len(RUN.validate_result_prefix(output, schedule)), 1)
            claims = Path(directory) / "claims"
            claims.mkdir(mode=0o700)
            RUN.atomic_create_private_json(
                claims / "r1.json",
                {"schedule_id": "s", "run_id": "r1", "ordinal": 1, "pid": 1},
            )
            RUN.atomic_create_private_json(
                claims / "r1.done.json",
                {
                    "schedule_id": "s",
                    "run_id": "r1",
                    "row_sha256": RUN.hashlib.sha256(
                        RUN.canonical_json_bytes(first)
                    ).hexdigest(),
                },
            )
            self.assertEqual(
                len(RUN.validate_result_prefix(output, schedule, claims)), 1
            )
            first["response"] = "tampered"
            output.write_text(json.dumps(first) + "\n", encoding="utf-8")
            output.chmod(0o600)
            with self.assertRaises(RUN.BenchError):
                RUN.validate_result_prefix(output, schedule, claims)
            output.unlink()
            RUN.write_jsonl(output, terminal(jobs[0]))
            RUN.write_jsonl(output, terminal(jobs[0]))
            with self.assertRaises(RUN.BenchError):
                RUN.validate_result_prefix(output, schedule)

    def test_model_id_rejects_provider_injection_before_subprocess(self):
        with mock.patch.object(RUN.subprocess, "run") as run, mock.patch.object(
            RUN.subprocess, "Popen"
        ) as popen:
            with self.assertRaises(RUN.BenchError):
                RUN.main(
                    [
                        "--row",
                        str(HERE / "row-645.json"),
                        "--output",
                        "/tmp/never-written.jsonl",
                        "--model",
                        "openai-oauth:gpt-5.6-luna",
                    ]
                )
            run.assert_not_called()
            popen.assert_not_called()


if __name__=="__main__":unittest.main()
