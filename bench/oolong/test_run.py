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
            self.assertIsNotNone(setup_usage)
            self.assertEqual(setup_usage["calls"], 1)
            route_evidence = RUN.parse_azdaja_route_evidence(path)
            self.assertEqual(route_evidence["depth_counts"], {"0": 1})
            self.assertEqual(route_evidence["transport_error_rows"], 1)
            self.assertTrue(
                RUN.runtime_assertion("jcode-azdaja", "", route_evidence)["asserted"]
            )
            self.assertTrue(
                RUN.direct_solo_lifecycle_assertion(
                    exit_code=0,
                    timed_out=False,
                    response="Answer: 1",
                    trace_usage=route_evidence,
                )["asserted"]
            )
            usage = RUN.usage_fields_from_azdaja(RUN.parse_azdaja_usage(path))
            self.assertFalse(RUN.direct_solo_usage_evidence(usage, None)["valid"])

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
            candidate = {"sha256": "a" * 64, "components": {}}
            controller = {"sha256": "b" * 64, "bytes": 1, "path": "/controller"}
            first = RUN.build_suite_schedule(suite, args, candidate, controller, {})
            second = RUN.build_suite_schedule(suite, args, candidate, controller, {})
            self.assertEqual(first, second)
            self.assertEqual(len(first["jobs"]), 4)
            self.assertEqual(len({job["run_id"] for job in first["jobs"]}), 4)
            args.model = "other-model"
            changed = RUN.build_suite_schedule(suite, args, candidate, controller, {})
            self.assertNotEqual(first["schedule_id"], changed["schedule_id"])

    def test_suite_output_prefix_rejects_duplicates_and_scores_only_when_complete(self):
        schedule = {
            "schedule_id": "s",
            "jobs": [
                {"run_id": "r1", "fixture_id": "f", "ordinal": 1, "arm": "a", "repetition": 1},
                {"run_id": "r2", "fixture_id": "f", "ordinal": 2, "arm": "b", "repetition": 1},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out.jsonl"
            RUN.write_jsonl(
                output,
                {"schedule_id": "s", "run_id": "r1", "fixture_id": "f", "response": "Answer: 0"},
            )
            self.assertEqual(len(RUN.validate_result_prefix(output, schedule)), 1)
            RUN.write_jsonl(
                output,
                {"schedule_id": "s", "run_id": "r1", "fixture_id": "f", "response": "Answer: 0"},
            )
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
