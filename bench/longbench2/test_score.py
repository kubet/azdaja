from __future__ import annotations

import copy
import hashlib
import importlib.util
import itertools
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("azdaja_lb2_score", HERE / "score.py")
SCORE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCORE
assert SPEC.loader is not None
SPEC.loader.exec_module(SCORE)


def private_json(path: Path, value: object) -> None:
    path.write_bytes(SCORE.canonical_json_file_bytes(value))
    path.chmod(0o600)


def private_text(path: Path, data: bytes) -> None:
    path.write_bytes(data)
    path.chmod(0o600)


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class ScoreTests(unittest.TestCase):
    def make_artifacts(self, root: Path, *, failed_job: int | None = None):
        root.chmod(0o700)
        public_root = root / "public"
        gold_root = root / "gold-root"
        runs_root = root / "runs-root"
        for sealed_root in (public_root, gold_root, runs_root):
            sealed_root.mkdir(mode=0o700)
        payload_dir = public_root / "payloads"
        payload_dir.mkdir(mode=0o700)
        for name in SCORE.PUBLIC_NOTICE_FILES:
            private_text(public_root / name, (HERE / name).read_bytes())
        domain_values = [
            domain
            for domain, count in SCORE.SELECTED_DOMAIN_COUNTS.items()
            for _ in range(count)
        ]
        sub_domain_values = [
            sub_domain
            for sub_domain, count in SCORE.SELECTED_SUB_DOMAIN_COUNTS.items()
            for _ in range(count)
        ]
        answer_values = [SCORE.CHOICE_LABELS[index % 4] for index in range(SCORE.EXPECTED_FIXTURES)]
        self.assertEqual(len(domain_values), SCORE.EXPECTED_FIXTURES)
        fixtures = []
        gold_fixtures = []
        answers = {}
        for index in range(SCORE.EXPECTED_FIXTURES):
            fixture_id = f"lb2-{index:032x}"
            payload = {
                "question": f"Synthetic private question {index}?",
                "context": f"Synthetic private context {index}.",
                "choices": {label: f"choice {label} {index}" for label in SCORE.CHOICE_LABELS},
            }
            payload_path = payload_dir / f"{fixture_id}.json"
            private_json(payload_path, payload)
            answer = answer_values[index]
            answers[fixture_id] = answer
            fixtures.append({
                "id": fixture_id,
                "domain": domain_values[index],
                "sub_domain": sub_domain_values[index],
                "payload": f"payloads/{fixture_id}.json",
                "payload_sha256": SCORE.sha256_path(payload_path),
                "payload_bytes": payload_path.stat().st_size,
            })
            gold_fixtures.append({
                "id": fixture_id,
                "answer": answer,
                "source_ordinal": index,
                "source_id": f"{index:024x}",
                "raw_row_sha256": sha(f"raw row {index}"),
                "canonical_row_sha256": sha(f"canonical row {index}"),
                "payload_sha256": SCORE.sha256_path(payload_path),
            })
        identity = {
            "schema_version": SCORE.SCHEMA_VERSION,
            "record_type": "lb2_hard_long_public_manifest",
            "suite_id": SCORE.SUITE_ID,
            "source": {
                "name": SCORE.SOURCE_NAME,
                "url": SCORE.SOURCE_URL,
                "revision": SCORE.SOURCE_REVISION,
            },
            "configuration": {
                "difficulty": "hard",
                "length": "long",
                "source_row_count": SCORE.EXPECTED_SOURCE_COUNT,
                "fixture_count": SCORE.EXPECTED_FIXTURES,
                "payload_schema": ["question", "context", "choices"],
                "choice_labels": list(SCORE.CHOICE_LABELS),
                "domain_counts": SCORE.SELECTED_DOMAIN_COUNTS,
                "sub_domain_counts": SCORE.SELECTED_SUB_DOMAIN_COUNTS,
            },
            "provenance_commitments": {
                "data_json_sha256": SCORE.SOURCE_FILES["data.json"]["sha256"],
                "readme_sha256": SCORE.SOURCE_FILES["README.md"]["sha256"],
                "gitattributes_sha256": SCORE.SOURCE_FILES[".gitattributes"]["sha256"],
                "requirements_lock_sha256": SCORE.REQUIREMENTS_LOCK_SHA256,
                "public_notice_files": {
                    name: metadata["sha256"]
                    for name, metadata in SCORE.PUBLIC_NOTICE_FILES.items()
                },
            },
            "fixtures": fixtures,
        }
        gold = {
            "schema_version": SCORE.SCHEMA_VERSION,
            "record_type": "lb2_hard_long_gold",
            "suite_id": SCORE.SUITE_ID,
            "manifest_identity_sha256": SCORE.sha256_bytes(SCORE.canonical_json_file_bytes(identity)),
            "fixtures": gold_fixtures,
            "provenance": {
                "source": {
                    "name": SCORE.SOURCE_NAME,
                    "url": SCORE.SOURCE_URL,
                    "revision": SCORE.SOURCE_REVISION,
                    "files": SCORE.SOURCE_FILES,
                },
                "source_file_sha256": SCORE.SOURCE_FILES["data.json"]["sha256"],
                "source_file_bytes": SCORE.SOURCE_FILES["data.json"]["bytes"],
                "source_row_count": SCORE.EXPECTED_SOURCE_COUNT,
                "filter": {"difficulty": "hard", "length": "long", "selected_count": 63},
                "randomization_key_sha256": "9" * 64,
                "requirements_lock_sha256": SCORE.REQUIREMENTS_LOCK_SHA256,
            },
        }
        gold_path = gold_root / "gold.json"
        private_json(gold_path, gold)
        manifest = dict(identity)
        manifest["gold_sha256"] = SCORE.sha256_path(gold_path)
        manifest_path = public_root / "manifest.json"
        private_json(manifest_path, manifest)

        schedule = {
            "schema_version": SCORE.SCHEMA_VERSION,
            "record_type": "lb2_frozen_schedule",
            "suite": {
                "suite_id": SCORE.SUITE_ID,
                "manifest_sha256": SCORE.sha256_path(manifest_path),
                "fixtures": [
                    {
                        "fixture_id": item["id"],
                        "payload_sha256": item["payload_sha256"],
                        "domain": item["domain"],
                        "sub_domain": item["sub_domain"],
                    }
                    for item in fixtures
                ],
            },
            "configuration": {
                "model": SCORE.MODEL,
                "reasoning": SCORE.REASONING,
                "arms": list(SCORE.ARMS),
                "repetitions": 1,
                "seed": SCORE.DEFAULT_BOOTSTRAP_SEED,
                "timeout_seconds": 60,
                "candidate": None,
                "controller": {
                    "path": "/sealed/controller.py", "sha256": "b" * 64, "bytes": 12
                },
                "executables": {
                    "jcode": {
                        "path": "/bin/jcode", "sha256": "c" * 64,
                        "bytes": 13, "version": "jcode test",
                        "version_command": ["/bin/jcode", "--version"],
                    },
                    "azdaja": {
                        "path": "/bin/azdaja", "sha256": "d" * 64,
                        "bytes": 14, "version": "azdaja test",
                        "version_command": ["/bin/azdaja", "--version"],
                    },
                    "prime-agent": {
                        "path": "/bin/prime-agent", "sha256": "e" * 64,
                        "bytes": 15, "version": "prime-agent test",
                        "version_command": ["/bin/prime-agent", "--version"],
                    },
                },
            },
            "jobs": [],
        }
        candidate_components = {
            "SKILL.md": {"sha256": "1" * 64, "bytes": 101},
            "azdaja": {"sha256": "2" * 64, "bytes": 102},
            "config.toml": {"sha256": "3" * 64, "bytes": 103},
        }
        schedule["configuration"]["candidate"] = {
            "components": candidate_components,
            "sha256": SCORE.sha256_bytes(SCORE.canonical_json_bytes(candidate_components)),
        }
        rng = __import__("random").Random(schedule["configuration"]["seed"])
        fixture_order = list(fixtures)
        rng.shuffle(fixture_order)
        ordinal = 0
        for fixture in fixture_order:
            arm_order = list(SCORE.ARMS)
            rng.shuffle(arm_order)
            for arm in arm_order:
                ordinal += 1
                schedule["jobs"].append({
                    "ordinal": ordinal,
                    "fixture_id": fixture["id"],
                    "payload_sha256": fixture["payload_sha256"],
                    "domain": fixture["domain"],
                    "sub_domain": fixture["sub_domain"],
                    "repetition": 1,
                    "arm": arm,
                })
        schedule_id = SCORE.sha256_bytes(SCORE.canonical_json_bytes(schedule))
        for job in schedule["jobs"]:
            job["run_id"] = SCORE.sha256_bytes(
                SCORE.RUN_ID_DOMAIN
                + schedule_id.encode("ascii")
                + SCORE.canonical_json_bytes(job)
            )
        schedule["schedule_id"] = schedule_id
        runs_path = runs_root / "runs.jsonl"
        schedule_path = Path(str(runs_path) + ".schedule.json")
        private_json(schedule_path, schedule)

        rows = []
        for job in schedule["jobs"]:
            answer = answers[job["fixture_id"]]
            if job["arm"] == "jcode-native":
                response = f"The correct answer is ({answer})"
                route = {
                    "asserted": True, "provider": "OpenAI", "model": SCORE.MODEL,
                    "expected_provider": "OpenAI", "expected_model": SCORE.MODEL,
                }
                latency = 1.0
                usage = {
                    "input_tokens": 100, "output_tokens": 10,
                    "cache_read_tokens": 3, "cache_write_tokens": 2,
                    "total_tokens": 110,
                }
            elif job["arm"] == "jcode-azdaja":
                response = f"Reasoning first. The correct answer is ({answer})"
                route = {
                    "asserted": True,
                    "routes": [{"provider": "openai", "model": SCORE.MODEL}],
                    "expected_provider": "OpenAI subscription OAuth",
                    "expected_model": SCORE.MODEL,
                    "transport_error_rows": 0,
                    "authority": "structurally valid successful rows in AZDAJA_MODEL_TRACE",
                }
                latency = 2.0
                usage = {
                    "input_tokens": 200, "output_tokens": 20,
                    "cache_read_tokens": 6, "cache_write_tokens": 4,
                    "total_tokens": 220,
                }
            else:
                response = f"I choose {answer}."
                route = {
                    "asserted": True,
                    "routes": [{
                        "provider": "openai-codex", "model": SCORE.MODEL,
                        "api": "openai-codex-responses",
                    }],
                    "expected_provider": "openai-codex",
                    "expected_model": SCORE.MODEL,
                    "expected_api": "openai-codex-responses",
                }
                latency = 3.0
                usage = {
                    "input_tokens": 300, "output_tokens": 30,
                    "cache_read_tokens": 9, "cache_write_tokens": 6,
                    "total_tokens": 345,
                }
            lifecycle = (
                {
                    "asserted": True,
                    "process_result_asserted": True,
                    "exit_code": 0,
                    "timed_out": False,
                    "nonempty_result": True,
                    "valid_depth_zero_model_calls": 1,
                    "requirement": "successful nonempty result and >=1 valid depth-0 model trace row",
                }
                if job["arm"] == "jcode-azdaja"
                else {"asserted": True, "requirement": "not applicable: control arm"}
            )
            execution_success = job["ordinal"] != failed_job
            provider_cli = "openai" if job["arm"].startswith("jcode") else "openai-codex"
            auth = {
                "asserted": True,
                "method": "subscription-oauth",
                "issuer": "https://auth.openai.com",
                "audience": "https://api.openai.com/v1",
                "plan_present_and_paid": True,
                "account_id_present": True,
                "expires_at_ms": 9_999_999_999_999,
                "credential_source": (
                    "~/.jcode/openai-auth.json" if job["arm"].startswith("jcode")
                    else "~/.prime/agent/auth.json:openai-codex"
                ),
                "provider_cli": provider_cli,
                "model_cli": SCORE.MODEL,
                **(
                    {"cli_auth_status_asserted_oauth": True, "cli_auth_status": "active"}
                    if job["arm"].startswith("jcode")
                    else {"credential_type_asserted": "oauth"}
                ),
            }
            required_traces = (
                ["azdaja_model_trace", "azdaja_solo_trace"]
                if job["arm"] == "jcode-azdaja" else []
            )
            context_hash = job["payload_sha256"]
            context_integrity = {
                "asserted_before": True, "asserted_after": True,
                "expected_sha256": context_hash,
                "source_sha256_before": context_hash,
                "source_sha256_after_copy": context_hash,
                "staged_sha256_before": context_hash,
                "staged_sha256_after": context_hash,
                "source_sha256_after": context_hash,
                "staged_mode_before": "0444", "staged_mode_after": "0444",
                "task_directory_single_file_before": True,
                "task_directory_single_file_after": True,
                "random_context_filename": True,
                "errors": [],
            }
            relevant_names = (
                ("jcode", "azdaja") if job["arm"] == "jcode-azdaja"
                else (("jcode",) if job["arm"] == "jcode-native" else ("prime-agent",))
            )
            row = {
                "schema_version": SCORE.SCHEMA_VERSION,
                "benchmark": SCORE.SUITE_ID,
                "record_type": "inference",
                "schedule_id": schedule_id,
                "run_id": job["run_id"],
                "fixture_id": job["fixture_id"],
                "payload_sha256": job["payload_sha256"],
                "execution_ordinal": job["ordinal"],
                "arm": job["arm"],
                "repetition": 1,
                "model": SCORE.MODEL,
                "reasoning": SCORE.REASONING,
                "candidate_sha256": schedule["configuration"]["candidate"]["sha256"],
                "controller_sha256": "b" * 64,
                "schedule_seed": schedule["configuration"]["seed"],
                "timeout_seconds": schedule["configuration"]["timeout_seconds"],
                "executables": {
                    name: schedule["configuration"]["executables"][name]
                    for name in relevant_names
                },
                "success": None,
                "score": None,
                "scoring_status": "deferred",
                "execution_success": execution_success,
                "response": response,
                "latency_seconds": latency,
                "started_at_unix_s": 1_000_000_000,
                "fresh_session": True,
                "serial": True,
                "hidden_context_and_official_question_identical_across_arms": True,
                "timed_out": not execution_success,
                "exit_code": 0,
                "auth_assertion": auth,
                "runtime_route_assertion": route,
                "product_lifecycle_assertion": lifecycle,
                "product_execution_asserted": True,
                "trace_capture_assertion": {
                    "asserted": True, "required": required_traces,
                    "captured": required_traces, "missing": [],
                },
                "task_context_integrity": context_integrity,
                "tool_access_policy_assertion": {
                    "asserted": True, "events_scanned": 0, "violations": [],
                    "policy": "no network or external dataset access in executed tool command/code events",
                    "enforcement": "post-hoc event detection only; not OS-level containment",
                    "containment_asserted": False,
                },
                "credential_cleanup_assertion": {
                    "asserted": True, "credential_homes_deleted": True,
                    "retained_entries": [], "retention_allowlist": [],
                },
                "cleanup_errors": [],
                "root_usage": dict(usage),
                "azdaja_model_usage": (
                    {
                        "calls": 1,
                        **dict(usage),
                        "routes": [f"openai/{SCORE.MODEL}"],
                        "depth_counts": {"0": 1},
                        "depth_usage": {"0": dict(usage)},
                        "all_rows_valid": True,
                    }
                    if job["arm"] == "jcode-azdaja" else None
                ),
                "efficiency_evidence": (
                    {
                        "valid": True, "missing_fields": [], "reasons": [],
                        "required_authority": "all valid AZDAJA_MODEL_TRACE rows at every depth",
                        "calls_included": 1, "depth_counts": {"0": 1},
                    }
                    if job["arm"] == "jcode-azdaja"
                    else {
                        "valid": True, "missing_fields": [], "reasons": [],
                        "required_authority": "provider usage events",
                    }
                ),
                "usage": usage,
                "failure": (
                    None if execution_success
                    else {"kind": "timeout", "message": "timed out", "stderr": ""}
                ),
            }
            rows.append(row)
        runs_path.write_bytes(b"".join(SCORE.canonical_json_file_bytes(row) for row in rows))
        runs_path.chmod(0o600)

        claims_root = Path(str(runs_path) + ".claims")
        claims_root.mkdir(mode=0o700)
        claims = claims_root / schedule_id
        claims.mkdir(mode=0o700)
        for row, job in zip(rows, schedule["jobs"]):
            private_json(claims / (job["run_id"] + ".json"), {
                "schedule_id": schedule_id,
                "run_id": job["run_id"],
                "ordinal": job["ordinal"],
                "pid": 123,
            })
            private_json(claims / (job["run_id"] + ".done.json"), {
                "schedule_id": schedule_id,
                "run_id": job["run_id"],
                "row_sha256": SCORE.sha256_bytes(SCORE.canonical_json_bytes(row)),
            })
        return {
            "manifest_path": manifest_path,
            "gold_path": gold_path,
            "runs_path": runs_path,
            "schedule_path": schedule_path,
            "claims_root": claims_root,
            "claims": claims,
            "manifest": manifest,
            "gold": gold,
            "schedule": schedule,
            "rows": rows,
            "fixtures": fixtures,
        }

    def rewrite_rows_and_receipts(self, artifacts) -> None:
        artifacts["runs_path"].write_bytes(
            b"".join(SCORE.canonical_json_file_bytes(row) for row in artifacts["rows"])
        )
        artifacts["runs_path"].chmod(0o600)
        for row, job in zip(artifacts["rows"], artifacts["schedule"]["jobs"]):
            private_json(artifacts["claims"] / (job["run_id"] + ".done.json"), {
                "schedule_id": artifacts["schedule"]["schedule_id"],
                "run_id": job["run_id"],
                "row_sha256": SCORE.sha256_bytes(SCORE.canonical_json_bytes(row)),
            })


    def test_official_metric_is_pinned_and_strict_metric_rejects_extra_text(self):
        accepted_official = (
            "The correct answer is (A)",
            "Reasoning. The correct answer is (A). trailing",
            "**The correct answer is (A)**",
            "The correct answer is A",
        )
        for response in accepted_official:
            with self.subTest(response=response):
                self.assertEqual(SCORE.official_extract_answer(response), "A")
        for response in ("A", "(A)", "the correct answer is (A)", "The correct answer is (a)"):
            with self.subTest(response=response):
                self.assertIsNone(SCORE.official_extract_answer(response))
        self.assertIsNone(SCORE.strict_extract_answer("  The correct answer is (B)\n"))
        self.assertEqual(SCORE.strict_extract_answer("The correct answer is (B)"), "B")
        self.assertIsNone(SCORE.strict_extract_answer("Reasoning. The correct answer is (B)"))
        self.assertIsNone(SCORE.strict_extract_answer("**The correct answer is (B)**"))

    def test_complete_report_fixed_denominators_efficiency_and_disclosure(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            report = SCORE.build_report(
                artifacts["manifest_path"], artifacts["gold_path"], artifacts["runs_path"],
                bootstrap_resamples=200,
            )
            self.assertTrue(report["integrity"]["terminal_complete_before_gold_read"])
            self.assertTrue(report["integrity"]["manifest_gold_hash_cycle_checked"])
            self.assertFalse(report["disclosure"]["official_longbench_v2_leaderboard_result"])
            self.assertFalse(report["disclosure"]["blind_or_secret_gold"])
            self.assertTrue(report["disclosure"]["publicly_joinable_to_upstream_answers"])
            self.assertIn("not an official leaderboard result", report["disclosure"]["statement"])
            self.assertEqual(report["integrity"]["scheduled_jobs"], 189)
            native = report["arms"]["jcode-native"]["overall"]
            azdaja = report["arms"]["jcode-azdaja"]["overall"]
            prime = report["arms"]["prime-agent"]["overall"]
            self.assertEqual(native["scheduled_n_fixed_denominator"], 63)
            self.assertEqual(native["end_to_end_fixed_denominator"]["strict_mcq_correct_n"], 63)
            self.assertEqual(azdaja["answer_scoring_all_terminal_outputs"]["official_longbench_v2_correct_n"], 63)
            self.assertEqual(azdaja["end_to_end_fixed_denominator"]["strict_mcq_correct_n"], 0)
            self.assertEqual(prime["end_to_end_fixed_denominator"]["official_longbench_v2_correct_n"], 0)
            self.assertEqual(native["wall_seconds_all_attempts"]["p50"], 1.0)
            self.assertEqual(native["wall_seconds_all_attempts"]["p95"], 1.0)
            tokens = native["tokens_all_attempts_unconditional"]
            self.assertEqual(tokens["unconditional_totals"]["total_tokens"], 63 * 110)
            self.assertEqual(tokens["unconditional_total_tokens_p50"], 110.0)
            self.assertEqual(len(report["comparisons"]), 3)
            pair = report["comparisons"]["jcode-native__minus__jcode-azdaja"]
            self.assertEqual(pair["paired_fixture_n"], 63)
            self.assertEqual(pair["resamples"], 200)
            self.assertEqual(pair["metrics"]["end_to_end_strict_correct"]["delta"], 1.0)

    def test_execution_and_answer_failures_are_separate(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory), failed_job=1)
            report = SCORE.build_report(
                artifacts["manifest_path"], artifacts["gold_path"], artifacts["runs_path"],
                bootstrap_resamples=10,
            )
            arm = artifacts["schedule"]["jobs"][0]["arm"]
            summary = report["arms"][arm]["overall"]
            self.assertEqual(summary["execution"]["failed_n"], 1)
            self.assertEqual(summary["failure_separation"]["execution_failure_n"], 1)
            self.assertEqual(
                summary["end_to_end_fixed_denominator"]["denominator_n"],
                SCORE.EXPECTED_FIXTURES,
            )
            first = report["scores"][0]
            self.assertEqual(first["failure_class"], "execution_failure")
            self.assertFalse(first["end_to_end_strict_correct"])

    def test_gold_is_not_touched_until_schedule_results_and_claims_complete(self):
        mutations = ("model", "partial", "claim", "done", "row")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
                artifacts = self.make_artifacts(Path(directory))
                if mutation == "model":
                    schedule = artifacts["schedule"]
                    schedule["configuration"]["model"] = "wrong-model"
                    private_json(artifacts["schedule_path"], schedule)
                elif mutation == "partial":
                    artifacts["rows"].pop()
                    artifacts["runs_path"].write_bytes(
                        b"".join(SCORE.canonical_json_file_bytes(row) for row in artifacts["rows"])
                    )
                elif mutation == "claim":
                    next(artifacts["claims"].glob("*.json")).unlink()
                elif mutation == "done":
                    done = next(artifacts["claims"].glob("*.done.json"))
                    value = json.loads(done.read_text())
                    value["row_sha256"] = "0" * 64
                    private_json(done, value)
                else:
                    artifacts["rows"][0]["model"] = "wrong-model"
                    self.rewrite_rows_and_receipts(artifacts)
                with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold touched")) as opened:
                    with self.assertRaises(SCORE.ScoreError):
                        SCORE.build_report(
                            artifacts["manifest_path"], artifacts["gold_path"], artifacts["runs_path"],
                            bootstrap_resamples=1,
                        )
                    opened.assert_not_called()

    def test_missing_gold_path_is_not_resolved_on_incomplete_run(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            artifacts["rows"].pop()
            artifacts["runs_path"].write_bytes(
                b"".join(SCORE.canonical_json_file_bytes(row) for row in artifacts["rows"])
            )
            missing = Path(directory) / "missing-gold-root" / "gold.json"
            with self.assertRaisesRegex(SCORE.ScoreError, "owner-only gold root"):
                SCORE.build_report(
                    artifacts["manifest_path"], missing, artifacts["runs_path"],
                    bootstrap_resamples=1,
                )

    def test_route_lifecycle_usage_and_latency_are_validated_before_gold(self):
        mutations = {
            "route": lambda row: row.update(runtime_route_assertion={"asserted": True, "provider": "OpenAI", "model": "wrong"}),
            "lifecycle": lambda row: row.update(product_lifecycle_assertion={"asserted": "yes"}),
            "usage": lambda row: row["usage"].update(total_tokens=-1),
            "usage_arithmetic": lambda row: row["usage"].update(total_tokens=999),
            "latency": lambda row: row.update(latency_seconds=float("inf")),
        }
        # Job 0 uses jcode-native in the deterministic fixture/permutation setup.
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
                artifacts = self.make_artifacts(Path(directory))
                mutate(artifacts["rows"][0])
                self.rewrite_rows_and_receipts(artifacts)
                with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold touched")) as opened:
                    with self.assertRaises(SCORE.ScoreError):
                        SCORE.build_report(
                            artifacts["manifest_path"], artifacts["gold_path"], artifacts["runs_path"],
                            bootstrap_resamples=1,
                        )
                    opened.assert_not_called()

    def test_missing_usage_is_reported_as_non_unconditional_not_silently_zero(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            row = artifacts["rows"][0]
            row["efficiency_evidence"] = (
                {
                    "valid": False, "missing_fields": list(SCORE.USAGE_FIELDS),
                    "reasons": ["missing trace"], "required_authority": "trace",
                    "calls_included": 0, "depth_counts": {},
                }
                if row["arm"] == "jcode-azdaja"
                else {
                    "valid": False, "missing_fields": list(SCORE.USAGE_FIELDS),
                    "reasons": ["missing provider usage"],
                    "required_authority": "provider usage events",
                }
            )
            row["usage"] = {field: None for field in SCORE.USAGE_FIELDS}
            row["execution_success"] = False
            row["failure"] = {"kind": "usage_evidence", "message": "missing", "stderr": ""}
            self.rewrite_rows_and_receipts(artifacts)
            report = SCORE.build_report(
                artifacts["manifest_path"], artifacts["gold_path"], artifacts["runs_path"],
                bootstrap_resamples=5,
            )
            arm = artifacts["schedule"]["jobs"][0]["arm"]
            tokens = report["arms"][arm]["overall"]["tokens_all_attempts_unconditional"]
            self.assertEqual(tokens["missing_usage_n"], 1)
            self.assertIsNone(tokens["unconditional_totals"])
            self.assertIsNone(tokens["unconditional_total_tokens_p50"])

    def test_manifest_duplicate_malformed_and_payload_tamper_are_rejected(self):
        mutations = ("duplicate_id", "duplicate_hash", "payload_tamper", "extra_fixture_field")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
                artifacts = self.make_artifacts(Path(directory))
                manifest = artifacts["manifest"]
                if mutation == "duplicate_id":
                    manifest["fixtures"][1]["id"] = manifest["fixtures"][0]["id"]
                elif mutation == "duplicate_hash":
                    manifest["fixtures"][1]["payload_sha256"] = manifest["fixtures"][0]["payload_sha256"]
                elif mutation == "payload_tamper":
                    path = artifacts["manifest_path"].parent / manifest["fixtures"][0]["payload"]
                    private_text(path, path.read_bytes() + b" ")
                else:
                    manifest["fixtures"][0]["answer"] = "A"
                private_json(artifacts["manifest_path"], manifest)
                with self.assertRaises(SCORE.ScoreError):
                    SCORE.load_public_manifest(artifacts["manifest_path"])

    def test_duplicate_json_keys_and_noncanonical_rows_are_rejected(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            root = Path(directory)
            root.chmod(0o700)
            duplicate = root / "duplicate.json"
            private_text(duplicate, b'{"a":1,"a":2}\n')
            with self.assertRaisesRegex(SCORE.ScoreError, "duplicate JSON object key"):
                SCORE.load_json_object(duplicate, "duplicate")
            artifacts = self.make_artifacts(root)
            data = artifacts["runs_path"].read_bytes()
            artifacts["runs_path"].write_bytes(data.replace(b'{"arm"', b'{ "arm"', 1))
            artifacts["runs_path"].chmod(0o600)
            with self.assertRaisesRegex(SCORE.ScoreError, "not canonical"):
                SCORE.load_run_rows(artifacts["runs_path"])

    def test_claim_set_rejects_missing_extra_and_tampered_receipts(self):
        cases = ("missing", "extra", "claim_tamper", "done_tamper")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
                artifacts = self.make_artifacts(Path(directory))
                job = artifacts["schedule"]["jobs"][0]
                claim = artifacts["claims"] / (job["run_id"] + ".json")
                done = artifacts["claims"] / (job["run_id"] + ".done.json")
                if case == "missing":
                    claim.unlink()
                elif case == "extra":
                    private_json(artifacts["claims"] / "orphan.json", {})
                elif case == "claim_tamper":
                    value = json.loads(claim.read_text())
                    value["ordinal"] += 1
                    private_json(claim, value)
                else:
                    value = json.loads(done.read_text())
                    value["row_sha256"] = "f" * 64
                    private_json(done, value)
                with self.assertRaises(SCORE.ScoreError):
                    SCORE.validate_claims(
                        artifacts["claims_root"], artifacts["rows"],
                        artifacts["schedule"]["jobs"], artifacts["schedule"],
                    )

    def test_gold_hash_cycle_pins_duplicates_and_leak_safe_code(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            manifest, fixtures = SCORE.load_public_manifest(artifacts["manifest_path"])
            gold, answers = SCORE.load_gold(
                artifacts["gold_path"], artifacts["manifest_path"], manifest, fixtures
            )
            self.assertEqual(len(answers), 63)
            self.assertNotIn("randomization_key", gold["provenance"])

            tampered = copy.deepcopy(gold)
            tampered["manifest_identity_sha256"] = SCORE.sha256_path(artifacts["manifest_path"])
            private_json(artifacts["gold_path"], tampered)
            manifest["gold_sha256"] = SCORE.sha256_path(artifacts["gold_path"])
            private_json(artifacts["manifest_path"], manifest)
            with self.assertRaises(SCORE.ScoreError):
                SCORE.load_gold(
                    artifacts["gold_path"], artifacts["manifest_path"], manifest, fixtures
                )
        source = (HERE / "score.py").read_text(encoding="utf-8")
        self.assertNotIn("SELECTED_ANSWER_COUNTS", source)

    def test_independent_generator_contract_and_requirements_pin(self):
        generator_spec = importlib.util.spec_from_file_location(
            "azdaja_lb2_generate_for_score_test", HERE / "generate.py"
        )
        generator = importlib.util.module_from_spec(generator_spec)
        sys.modules[generator_spec.name] = generator
        assert generator_spec.loader is not None
        generator_spec.loader.exec_module(generator)
        for name in (
            "SUITE_ID", "SCHEMA_VERSION", "EXPECTED_SOURCE_COUNT", "SOURCE_NAME",
            "SOURCE_URL", "SOURCE_REVISION", "SOURCE_FILES", "REQUIREMENTS_LOCK_SHA256",
            "PUBLIC_NOTICE_FILES", "SELECTED_DOMAIN_COUNTS", "SELECTED_SUB_DOMAIN_COUNTS",
        ):
            self.assertEqual(getattr(SCORE, name), getattr(generator, name))
        self.assertEqual(
            SCORE.sha256_path(HERE / "requirements.lock"), SCORE.REQUIREMENTS_LOCK_SHA256
        )

    def test_paired_bootstrap_is_deterministic_and_fixture_paired(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            manifest, fixtures = SCORE.load_public_manifest(artifacts["manifest_path"])
            jobs, arms = SCORE.validate_schedule(
                artifacts["schedule"], artifacts["manifest_path"], fixtures
            )
            score_rows = SCORE.build_score_rows(
                artifacts["rows"], jobs, fixtures,
                {item["id"]: artifacts["gold"]["fixtures"][i]["answer"] for i, item in enumerate(artifacts["fixtures"])},
            )
            first = SCORE.paired_comparisons(score_rows, fixtures, arms, seed=7, resamples=100)
            second = SCORE.paired_comparisons(score_rows, fixtures, arms, seed=7, resamples=100)
            self.assertEqual(first, second)
            for document in first.values():
                self.assertEqual(document["paired_fixture_n"], 63)
                self.assertEqual(document["resamples"], 100)

    def test_private_exclusive_report_creation(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            root = Path(directory)
            root.chmod(0o700)
            output = root / "report.json"
            SCORE.atomic_create_private_json(output, {"private": True})
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertEqual(output.read_bytes(), b'{"private":true}\n')
            with self.assertRaises(SCORE.ScoreError):
                SCORE.atomic_create_private_json(output, {"private": False})
            self.assertEqual(output.read_bytes(), b'{"private":true}\n')

    def test_private_mode_and_symlink_rejections(self):
        if os.name != "posix":
            self.skipTest("POSIX permission/symlink test")
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            artifacts["manifest_path"].chmod(0o644)
            with self.assertRaisesRegex(SCORE.ScoreError, "owner-only"):
                SCORE.load_public_manifest(artifacts["manifest_path"])
            artifacts["manifest_path"].chmod(0o600)
            link = Path(directory) / "manifest-link.json"
            link.symlink_to(artifacts["manifest_path"])
            with self.assertRaisesRegex(SCORE.ScoreError, "filename must be exactly"):
                SCORE.load_public_manifest(link)


    def test_exact_public_gold_root_inventory_and_lexical_separation(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            extra = artifacts["manifest_path"].parent / "unexpected.txt"
            private_text(extra, b"unexpected")
            with self.assertRaisesRegex(SCORE.ScoreError, "root inventory drift"):
                SCORE.load_public_manifest(artifacts["manifest_path"])
            extra.unlink()
            manifest, fixtures = SCORE.load_public_manifest(artifacts["manifest_path"])
            gold_extra = artifacts["gold_path"].parent / "backup.json"
            private_json(gold_extra, {})
            with self.assertRaisesRegex(SCORE.ScoreError, "exactly gold.json"):
                SCORE.load_gold(
                    artifacts["gold_path"], artifacts["manifest_path"], manifest, fixtures
                )
            gold_extra.unlink()
            nested_runs = artifacts["manifest_path"].parent / "runs.jsonl"
            with self.assertRaisesRegex(SCORE.ScoreError, "distinct and non-nested"):
                SCORE.build_report(
                    artifacts["manifest_path"], artifacts["gold_path"], nested_runs,
                    bootstrap_resamples=1,
                )

    def test_hardlinks_and_lexical_ancestor_symlinks_are_rejected(self):
        if os.name != "posix":
            self.skipTest("POSIX link security test")
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            hardlink = artifacts["manifest_path"].parent / "manifest-hardlink.json"
            os.link(artifacts["manifest_path"], hardlink)
            with self.assertRaisesRegex(SCORE.ScoreError, "inventory drift"):
                SCORE.load_public_manifest(artifacts["manifest_path"])
            hardlink.unlink()
            alias = Path(directory) / "public-alias"
            alias.symlink_to(artifacts["manifest_path"].parent, target_is_directory=True)
            with self.assertRaisesRegex(SCORE.ScoreError, "unsafe"):
                SCORE.load_public_manifest(alias / "manifest.json")

    def test_exact_seeded_order_candidate_and_component_identities(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            manifest, fixtures = SCORE.load_public_manifest(artifacts["manifest_path"])
            schedule = copy.deepcopy(artifacts["schedule"])
            # Build a fully self-consistent alternate schedule identity whose
            # first two fixture triplets violate the frozen seeded algorithm.
            schedule.pop("schedule_id")
            for job in schedule["jobs"]:
                job.pop("run_id")
            schedule["jobs"][:3], schedule["jobs"][3:6] = (
                schedule["jobs"][3:6], schedule["jobs"][:3]
            )
            for ordinal, job in enumerate(schedule["jobs"], 1):
                job["ordinal"] = ordinal
            schedule_id = SCORE.sha256_bytes(SCORE.canonical_json_bytes(schedule))
            for job in schedule["jobs"]:
                job["run_id"] = SCORE.sha256_bytes(
                    SCORE.RUN_ID_DOMAIN + schedule_id.encode() + SCORE.canonical_json_bytes(job)
                )
            schedule["schedule_id"] = schedule_id
            with self.assertRaisesRegex(SCORE.ScoreError, "exact seeded"):
                SCORE.validate_schedule(
                    schedule, artifacts["manifest_path"], fixtures,
                    manifest_sha256=SCORE.sha256_bytes(SCORE.canonical_json_file_bytes(manifest)),
                )
            malformed_candidate = copy.deepcopy(
                artifacts["schedule"]["configuration"]["candidate"]
            )
            malformed_candidate["components"].pop("SKILL.md")
            with self.assertRaisesRegex(SCORE.ScoreError, "candidate"):
                SCORE._validate_candidate_identity(malformed_candidate)

    def test_success_evidence_and_schedule_row_bindings_are_fail_closed(self):
        mutations = {
            "seed": lambda row: row.update(schedule_seed=-1),
            "timeout_binding": lambda row: row.update(timeout_seconds=61),
            "executables": lambda row: row.update(executables={}),
            "empty_response": lambda row: row.update(response=""),
            "timed_out": lambda row: row.update(timed_out=True),
            "exit_code": lambda row: row.update(exit_code=1),
            "auth": lambda row: row["auth_assertion"].update(asserted=False),
            "trace": lambda row: row["trace_capture_assertion"].update(captured=["tampered"]),
            "context": lambda row: row["task_context_integrity"].update(staged_sha256_after="0" * 64),
            "tool": lambda row: row["tool_access_policy_assertion"].update(asserted=False),
            "cleanup": lambda row: row["credential_cleanup_assertion"].update(credential_homes_deleted=False),
            "zero_usage": lambda row: row["usage"].update(input_tokens=0, total_tokens=row["usage"]["output_tokens"]),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
                artifacts = self.make_artifacts(Path(directory))
                mutate(artifacts["rows"][0])
                self.rewrite_rows_and_receipts(artifacts)
                with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold touched")) as opened:
                    with self.assertRaises(SCORE.ScoreError):
                        SCORE.build_report(
                            artifacts["manifest_path"], artifacts["gold_path"], artifacts["runs_path"],
                            bootstrap_resamples=1,
                        )
                    opened.assert_not_called()

    def test_official_ambiguity_and_false_positive_diagnostics(self):
        repeated = SCORE.official_answer_diagnostics(
            "The correct answer is (A). The correct answer is (A)"
        )
        self.assertTrue(repeated["multiple_matches"])
        self.assertFalse(repeated["contradictory"])
        contradictory = SCORE.official_answer_diagnostics(
            "The correct answer is (A), but The correct answer is (B)"
        )
        self.assertTrue(contradictory["contradictory"])
        negated = SCORE.official_answer_diagnostics(
            "It is not true that The correct answer is (C)"
        )
        self.assertTrue(negated["possible_negated_false_positive"])
        # The compatibility metric deliberately preserves upstream first-match
        # behavior while surfacing, rather than silently hiding, ambiguity.
        self.assertEqual(
            SCORE.official_extract_answer("The correct answer is (A); The correct answer is (B)"),
            "A",
        )

    def test_gold_is_captured_once_so_post_read_swap_cannot_change_answers(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            manifest, fixtures = SCORE.load_public_manifest(artifacts["manifest_path"])
            original_read_at = SCORE._read_private_regular_at
            original_answer = artifacts["gold"]["fixtures"][0]["answer"]
            swapped_answer = next(label for label in SCORE.CHOICE_LABELS if label != original_answer)
            tampered = copy.deepcopy(artifacts["gold"])
            tampered["fixtures"][0]["answer"] = swapped_answer
            calls = 0

            def capture_then_swap(directory_fd, relative, label, **kwargs):
                nonlocal calls
                result = original_read_at(directory_fd, relative, label, **kwargs)
                if relative == "gold.json" and label == "owner-only gold":
                    calls += 1
                    private_json(artifacts["gold_path"], tampered)
                return result

            with mock.patch.object(SCORE, "_read_private_regular_at", side_effect=capture_then_swap):
                _, answers = SCORE.load_gold(
                    artifacts["gold_path"], artifacts["manifest_path"], manifest, fixtures
                )
            self.assertEqual(calls, 1)
            fixture_id = artifacts["gold"]["fixtures"][0]["id"]
            self.assertEqual(answers[fixture_id], original_answer)
            self.assertNotEqual(answers[fixture_id], swapped_answer)


    def test_cli_rejects_report_output_collocated_with_public_before_reading_inputs(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            root = Path(directory)
            root.chmod(0o700)
            public = root / "public"
            gold = root / "gold"
            runs = root / "runs"
            for item in (public, gold, runs):
                item.mkdir(mode=0o700)
            with mock.patch.object(SCORE, "build_report", side_effect=AssertionError("inputs read")) as build:
                code = SCORE.main([
                    "--manifest", str(public / "manifest.json"),
                    "--gold", str(gold / "gold.json"),
                    "--runs", str(runs / "runs.jsonl"),
                    "--output", str(public / "report.json"),
                    "--bootstrap-resamples", "1",
                ])
            self.assertEqual(code, 2)
            build.assert_not_called()


    def test_schedule_aliasing_gold_is_rejected_before_any_artifact_touch(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            root = Path(directory)
            root.chmod(0o700)
            public = root / "public"
            gold = root / "gold"
            runs = root / "runs"
            for item in (public, gold, runs):
                item.mkdir(mode=0o700)
            manifest = public / "manifest.json"
            gold_path = gold / "gold.json"
            runs_path = runs / "runs.jsonl"
            with mock.patch.object(
                SCORE, "load_public_manifest", side_effect=AssertionError("artifact touched")
            ) as load_public, mock.patch.object(
                SCORE, "read_private_regular_once", side_effect=AssertionError("artifact touched")
            ) as reader:
                with self.assertRaisesRegex(SCORE.ScoreError, "must not alias gold"):
                    SCORE.build_report(
                        manifest, gold_path, runs_path,
                        schedule_path=gold_path,
                        claims_root=root / "claims",
                        bootstrap_resamples=1,
                    )
            load_public.assert_not_called()
            reader.assert_not_called()

    def test_treatment_trace_usage_root_depth_calls_routes_are_reconciled(self):
        mutations = {
            "calls": lambda row: row["azdaja_model_usage"].update(calls=2),
            "depth_count": lambda row: row["azdaja_model_usage"]["depth_counts"].update({"0": 2}),
            "depth_arithmetic": lambda row: row["azdaja_model_usage"]["depth_usage"]["0"].update(total_tokens=999),
            "depth_aggregate": lambda row: row["azdaja_model_usage"]["depth_usage"]["0"].update(input_tokens=201),
            "root": lambda row: row["root_usage"].update(input_tokens=201),
            "route": lambda row: row["azdaja_model_usage"].update(routes=["other/model"]),
            "zero_depth0": lambda row: row["azdaja_model_usage"]["depth_counts"].update({"0": 0}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
                artifacts = self.make_artifacts(Path(directory))
                row = next(item for item in artifacts["rows"] if item["arm"] == "jcode-azdaja")
                mutate(row)
                self.rewrite_rows_and_receipts(artifacts)
                with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold touched")) as gold:
                    with self.assertRaises(SCORE.ScoreError):
                        SCORE.build_report(
                            artifacts["manifest_path"], artifacts["gold_path"], artifacts["runs_path"],
                            bootstrap_resamples=1,
                        )
                    gold.assert_not_called()

    def test_execution_failure_taxonomy_and_shape_are_exact(self):
        mutations = {
            "unknown_kind": lambda row: row["failure"].update(kind="mystery"),
            "answer_kind": lambda row: row["failure"].update(kind="wrong_answer"),
            "extra_field": lambda row: row["failure"].update(code=1),
            "timeout_contradiction": lambda row: row.update(timed_out=False),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
                artifacts = self.make_artifacts(Path(directory), failed_job=1)
                mutate(artifacts["rows"][0])
                self.rewrite_rows_and_receipts(artifacts)
                with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold touched")) as gold:
                    with self.assertRaises(SCORE.ScoreError):
                        SCORE.build_report(
                            artifacts["manifest_path"], artifacts["gold_path"], artifacts["runs_path"],
                            bootstrap_resamples=1,
                        )
                    gold.assert_not_called()

    def test_atomic_report_uses_temp_noreplace_and_directory_fsync(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            root = Path(directory)
            root.chmod(0o700)
            output = root / "report.json"
            real_fsync = os.fsync
            fsync_calls = []

            def counted(fd):
                fsync_calls.append(fd)
                return real_fsync(fd)

            with mock.patch.object(SCORE.os, "fsync", side_effect=counted):
                SCORE.atomic_create_private_json(output, {"ok": True})
            self.assertGreaterEqual(len(fsync_calls), 2)
            self.assertEqual({entry.name for entry in root.iterdir()}, {"report.json"})
            self.assertEqual(output.read_bytes(), b'{"ok":true}\n')
            with self.assertRaisesRegex(SCORE.ScoreError, "already exists"):
                SCORE.atomic_create_private_json(output, {"ok": False})
            self.assertEqual(output.read_bytes(), b'{"ok":true}\n')

    def test_broadened_official_false_positive_diagnostics(self):
        echoed = SCORE.official_answer_diagnostics(
            'The instruction says: "The correct answer is (A)"'
        )
        self.assertTrue(echoed["possible_quoted_or_instruction_echo"])
        hypothetical = SCORE.official_answer_diagnostics(
            "Hypothetically, The correct answer is (B)"
        )
        self.assertTrue(hypothetical["possible_hypothetical_or_attributed_false_positive"])
        corrected = SCORE.official_answer_diagnostics(
            "The correct answer is (C), however that was a mistake"
        )
        self.assertTrue(corrected["possible_subsequent_correction"])
        near = SCORE.official_answer_diagnostics("the correct answer is (d)")
        self.assertEqual(near["case_insensitive_near_miss_n"], 1)


    def test_exact_top_level_inference_row_schema_rejects_extra_and_missing_pre_gold(self):
        for mutation in ("extra", "missing"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
                artifacts = self.make_artifacts(Path(directory))
                if mutation == "extra":
                    artifacts["rows"][0]["uncommitted_extra"] = True
                else:
                    del artifacts["rows"][0]["fresh_session"]
                self.rewrite_rows_and_receipts(artifacts)
                with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold touched")) as gold:
                    with self.assertRaisesRegex(SCORE.ScoreError, "top-level schema mismatch"):
                        SCORE.build_report(
                            artifacts["manifest_path"], artifacts["gold_path"], artifacts["runs_path"],
                            bootstrap_resamples=1,
                        )
                    gold.assert_not_called()

    def test_treatment_depth0_must_have_positive_tokens_even_if_aggregate_reconciles(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            artifacts = self.make_artifacts(Path(directory))
            row = next(item for item in artifacts["rows"] if item["arm"] == "jcode-azdaja")
            full = dict(row["usage"])
            zero = {
                "input_tokens": 0, "output_tokens": 0,
                "cache_read_tokens": 0, "cache_write_tokens": 0,
                "total_tokens": 0,
            }
            row["root_usage"] = zero
            row["azdaja_model_usage"].update(
                calls=2,
                depth_counts={"0": 1, "1": 1},
                depth_usage={"0": zero, "1": full},
            )
            row["efficiency_evidence"].update(
                calls_included=2, depth_counts={"0": 1, "1": 1}
            )
            self.rewrite_rows_and_receipts(artifacts)
            with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold touched")) as gold:
                with self.assertRaisesRegex(SCORE.ScoreError, "lacks positive token usage"):
                    SCORE.build_report(
                        artifacts["manifest_path"], artifacts["gold_path"], artifacts["runs_path"],
                        bootstrap_resamples=1,
                    )
                gold.assert_not_called()


if __name__ == "__main__":
    unittest.main()
