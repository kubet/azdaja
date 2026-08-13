import copy
import hashlib
import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("azdaja_oolong_report", HERE / "report.py")
REPORT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = REPORT
assert SPEC.loader is not None
SPEC.loader.exec_module(REPORT)


def private_json(path: Path, value: object) -> None:
    path.write_bytes(REPORT.canonical_json_bytes(value) + b"\n")
    path.chmod(0o600)


class ReportTests(unittest.TestCase):
    def make_artifacts(self, root: Path, repetitions: int = 1):
        self.assertEqual(repetitions, REPORT.CAMPAIGN_REPETITIONS)
        raw = root / "suite.jsonl"
        suite_path = root / "manifest.json"
        fixture_rows = []
        for index in range(1, REPORT.CAMPAIGN_FIXTURE_COUNT + 1):
            fixture_id = f"f-{index:02d}"
            row_path = root / f"row-{index:02d}.json"
            context_path = root / f"context-{index:02d}.txt"
            private_json(row_path, {
                "source": "oolongbench/oolong-synth",
                "question": "Return the count as an Answer line.",
                "answer": "[1]",
                "test_fixture_index": index,
            })
            context_path.write_text(f"fixture context {index}\n", encoding="utf-8")
            context_path.chmod(0o600)
            fixture_rows.append((index, fixture_id, row_path, context_path))
        suite = {
            "schema_version": 1,
            "source": "oolongbench/oolong-synth",
            "split": "validation",
            "upstream_commit": "0" * 40,
            "fixtures": [
                {
                    "fixture_id": fixture_id,
                    "row": row_path.name,
                    "context": context_path.name,
                    "row_sha256": REPORT.sha256_path(row_path),
                    "context_sha256": REPORT.sha256_path(context_path),
                    "dataset": "spam",
                    "context_window_id": 10000 + index,
                }
                for index, fixture_id, row_path, context_path in fixture_rows
            ],
        }
        private_json(suite_path, suite)

        def executable(name, sha, size=1):
            path = "/" + name
            return {
                "path": path, "sha256": sha, "bytes": size,
                "version": name + " 1", "version_command": [path, "--version"],
            }
        components = {
            "azdaja": {"sha256": "d" * 64, "bytes": 4},
            "config.toml": {"sha256": "e" * 64, "bytes": 5},
            "SKILL.md": {"sha256": "f" * 64, "bytes": 6},
        }
        candidate = {
            "sha256": hashlib.sha256(REPORT.canonical_json_bytes({
                name: components[name] for name in sorted(components)
            })).hexdigest(),
            "components": components,
        }
        executables = {
            "jcode": executable("jcode", "b" * 64, 2),
            "prime-agent": executable("prime-agent", "c" * 64, 3),
            "azdaja": executable("azdaja", "d" * 64, 4),
        }
        schedule = {
            "schema_version": 1,
            "record_type": "oolong_frozen_schedule",
            "suite": {
                "manifest_sha256": REPORT.sha256_path(suite_path),
                "source": suite["source"],
                "split": suite["split"],
                "upstream_commit": suite["upstream_commit"],
                "fixtures": [{
                    "fixture_id": item["fixture_id"],
                    "row_sha256": item["row_sha256"],
                    "context_sha256": item["context_sha256"],
                } for item in suite["fixtures"]],
            },
            "configuration": {
                "model": REPORT.CAMPAIGN_MODEL,
                "reasoning": REPORT.CAMPAIGN_REASONING,
                "arms": list(REPORT.CAMPAIGN_ARMS),
                "repetitions": REPORT.CAMPAIGN_REPETITIONS,
                "seed": REPORT.CAMPAIGN_SEED,
                "timeout_seconds": REPORT.CAMPAIGN_TIMEOUT_SECONDS,
                "candidate": candidate,
                "controller": {"path": "/controller", "sha256": "a" * 64, "bytes": 1},
                "executables": executables,
            },
            "jobs": [],
        }
        ordinal = 0
        for fixture in schedule["suite"]["fixtures"]:
            for arm in schedule["configuration"]["arms"]:
                ordinal += 1
                schedule["jobs"].append({
                    "ordinal": ordinal,
                    "fixture_id": fixture["fixture_id"],
                    "row_sha256": fixture["row_sha256"],
                    "context_sha256": fixture["context_sha256"],
                    "repetition": 1,
                    "arm": arm,
                })
        self.assertEqual(ordinal, REPORT.CAMPAIGN_ROW_COUNT)
        schedule_id = hashlib.sha256(REPORT.canonical_json_bytes(schedule)).hexdigest()
        for job in schedule["jobs"]:
            job["run_id"] = hashlib.sha256(
                b"oolong-run-v1\0" + schedule_id.encode("ascii")
                + REPORT.canonical_json_bytes(job)
            ).hexdigest()
        schedule["schedule_id"] = schedule_id
        private_json(Path(str(raw) + ".schedule.json"), schedule)

        rows = []
        scores = []
        for job in schedule["jobs"]:
            index = int(job["fixture_id"].split("-")[1])
            arm = job["arm"]
            execution_success = arm != "jcode-azdaja" and not (
                arm == "jcode-native" and index == REPORT.CAMPAIGN_FIXTURE_COUNT
            )
            correct = (
                index % 2 == 1 if arm == "jcode-native"
                else index != 1 if arm == "prime-agent"
                else True
            )
            latency = 2.0 if arm == "jcode-native" else 4.0
            tokens = 10 if arm == "jcode-native" else 20
            usage_valid = execution_success
            failure = None if execution_success else {
                "kind": "timeout", "normalized_kind": "timeout", "message": "timed out"
            }
            expected_executables = (
                {"jcode": executables["jcode"]}
                if arm == "jcode-native" else
                ({"prime-agent": executables["prime-agent"]}
                 if arm == "prime-agent" else
                 {"jcode": executables["jcode"], "azdaja": executables["azdaja"]})
            )
            trajectory_artifacts = {}
            trajectory_run_directory = None
            root_context_leak_assertion = {
                "applicable": False, "asserted": True, "scan_complete": True,
                "leak_detected": False,
                "minimum_match_chars": REPORT.ROOT_CONTEXT_LEAK_MIN_CHARS,
                "authority": "not applicable to a non-Azdaja control arm",
                "matched_text_retained": False,
            }
            if arm == "jcode-azdaja":
                run_directory = root / f"run-{job['ordinal']:03d}-jcode-azdaja"
                run_directory.mkdir(mode=0o700)
                trace = run_directory / "azdaja-solo-trace.log"
                trace.write_text(
                    "=== root request begin request_chars=20 ===\n"
                    "synthetic root input\n=== root request end ===\n",
                    encoding="utf-8",
                )
                trace.chmod(0o600)
                trace_sha = REPORT.sha256_path(trace)
                trajectory_artifacts = {
                    "azdaja_solo_trace": {
                        "path": str(trace), "sha256": trace_sha,
                        "source_sha256_before_redaction": trace_sha,
                        "bytes": trace.stat().st_size, "mode": "0600",
                        "exact_text_preserved": True,
                    }
                }
                trajectory_run_directory = str(run_directory)
                context_path = root / f"context-{index:02d}.txt"
                root_context_leak_assertion = REPORT.scan_context_file_against_solo_trace(
                    context_path, trace,
                    expected_context_sha256=REPORT.sha256_path(context_path),
                    exact_transcript_preserved=True,
                )
            row = {
                "schema_version": 1, "benchmark": "oolong", "record_type": "inference",
                "schedule_id": schedule_id, "run_id": job["run_id"],
                "fixture_id": job["fixture_id"], "row_sha256": job["row_sha256"],
                "context_sha256": job["context_sha256"],
                "execution_ordinal": job["ordinal"], "arm": arm, "repetition": 1,
                "model": REPORT.CAMPAIGN_MODEL, "reasoning": REPORT.CAMPAIGN_REASONING,
                "candidate_sha256": candidate["sha256"], "controller_sha256": "a" * 64,
                "executables": expected_executables,
                "success": None, "score": None, "scoring_status": "deferred",
                "execution_success": execution_success, "latency_seconds": latency,
                "runtime_route_assertion": {"asserted": execution_success},
                "efficiency_evidence": {"valid": usage_valid},
                "root_token_economy": {
                    "root_input_tokens": float(tokens / 2), "source_characters": tokens * 2,
                    "authority": "test canonical terminal result divided by 4",
                    "authority_kind": "character_fallback", "estimated": True,
                    "missing": False, "reasons": [],
                },
                "usage": ({
                    "input_tokens": tokens - 2, "output_tokens": 2,
                    "cache_read_tokens": 0, "cache_write_tokens": 0,
                    "total_tokens": tokens,
                } if usage_valid else None),
                "trajectory_artifacts": trajectory_artifacts,
                "trajectory_run_directory": trajectory_run_directory,
                "root_context_leak_assertion": root_context_leak_assertion,
                "failure": failure,
                "response": "Answer: 1" if correct else "Answer: 0",
            }
            score = {
                "run_id": job["run_id"], "ordinal": job["ordinal"],
                "fixture_id": job["fixture_id"], "arm": arm, "repetition": 1,
                "execution_success": execution_success,
                "score": {
                    "correct": correct, "strict_exact": True, "expected": "Answer: 1",
                    "parsed_value": 1 if correct else 0,
                    "parse_error": None if correct else "output was not exactly the canonical gold answer",
                },
                "success": execution_success and correct,
            }
            rows.append(row)
            scores.append(score)
        raw.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        raw.chmod(0o600)
        claims_root = Path(str(raw) + ".claims")
        claims_root.mkdir(mode=0o700)
        claims = claims_root / schedule_id
        claims.mkdir(mode=0o700)
        for row, job in zip(rows, schedule["jobs"]):
            private_json(claims / (job["run_id"] + ".json"), {
                "schedule_id": schedule_id, "run_id": job["run_id"],
                "ordinal": job["ordinal"], "pid": 123,
            })
            private_json(claims / (job["run_id"] + ".done.json"), {
                "schedule_id": schedule_id, "run_id": job["run_id"],
                "row_sha256": hashlib.sha256(REPORT.canonical_json_bytes(row)).hexdigest(),
            })
        scores_document = {
            "schema_version": 1, "record_type": "oolong_deferred_scores",
            "schedule_id": schedule_id, "manifest_sha256": REPORT.sha256_path(suite_path),
            "inference_jsonl_sha256": REPORT.sha256_path(raw), "scores": scores,
        }
        private_json(Path(str(raw) + ".scores.json"), scores_document)
        return raw, suite_path, schedule, rows, scores_document

    def test_metrics_pairing_usage_route_and_metadata_clusters(self):
        with tempfile.TemporaryDirectory() as directory:
            raw, suite, _, _, _ = self.make_artifacts(Path(directory))
            result = REPORT.build_report(
                raw, suite_manifest=suite, bootstrap_iterations=80
            )
            self.assertTrue(result["integrity"]["validated"])
            self.assertEqual(result["integrity"]["scheduled_rows"], 78)
            self.assertTrue(result["integrity"]["campaign_profile"]["certified"])
            self.assertEqual(result["bootstrap"]["cluster_by"], "dataset+context_window_id")
            self.assertEqual(result["bootstrap"]["cluster_count"], 26)
            native = result["arms"]["jcode-native"]
            self.assertEqual(native["scheduled_n"], 26)
            self.assertEqual(native["execution"]["completed_n"], 25)
            self.assertEqual(native["exact_success"], {"n": 13, "rate": 0.5})
            failure = native["failure"]
            self.assertEqual(failure["taxonomy"], {"strict_score": 12, "timeout": 1})
            self.assertEqual(failure["execution_failure_taxonomy"], {"timeout": 1})
            self.assertEqual(sum(failure["taxonomy"].values()), failure["taxonomy_denominator_n"])
            self.assertEqual(
                sum(failure["execution_failure_taxonomy"].values()),
                failure["execution_failure_taxonomy_denominator_n"],
            )
            self.assertEqual(
                native["completed_accuracy"],
                {"correct_n": 13, "completed_n": 25, "rate": 13 / 25},
            )
            self.assertEqual(
                native["fixed_denominator_e2e_accuracy"],
                {"correct_n": 13, "scheduled_n": 26, "rate": 0.5},
            )
            self.assertEqual(native["tokens_all_attempts"]["missing_usage_n"], 1)
            self.assertIsNone(native["tokens_all_attempts"]["unconditional_total_tokens"])
            self.assertEqual(native["route_integrity"]["failed_n"], 1)
            self.assertEqual(
                native["root_token_economy"]["recorded_total_root_input_tokens"], 130.0
            )
            pair = result["comparisons"]["jcode-native__vs__prime-agent"]
            self.assertEqual(pair["paired_n"], 26)
            self.assertEqual(pair["both_correct_n"], 12)
            self.assertAlmostEqual(pair["accuracy"]["delta"], 12 / 26)
            self.assertAlmostEqual(pair["latency_geometric_ratio"]["value"], 2.0)
            self.assertAlmostEqual(pair["token_geometric_ratio"]["value"], 2.0)


    def test_bootstrap_is_deterministic_for_campaign_clusters(self):
        with tempfile.TemporaryDirectory() as directory:
            raw, suite, _, _, _ = self.make_artifacts(Path(directory))
            first = REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=60)
            second = REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=60)
            self.assertEqual(first, second)
            self.assertEqual(first["bootstrap"]["seed"], REPORT.BOOTSTRAP_SEED)
            self.assertEqual(first["bootstrap"]["cluster_by"], "dataset+context_window_id")
            self.assertEqual(first["bootstrap"]["cluster_count"], 26)


    def test_campaign_report_requires_exact_suite_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            raw, _, _, _, _ = self.make_artifacts(Path(directory))
            with self.assertRaisesRegex(REPORT.ReportError, "campaign-certified"):
                REPORT.build_report(raw, bootstrap_iterations=5)

    def test_one_repetition_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            raw, suite, _, _, _ = self.make_artifacts(Path(directory), repetitions=1)
            result = REPORT.build_report(
                raw, suite_manifest=suite, bootstrap_iterations=20
            )
            self.assertTrue(any("only one repetition" in item for item in result["warnings"]))

    def test_rejects_incomplete_raw_and_score_hash_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, suite, _, _, _ = self.make_artifacts(root)
            original = raw.read_text(encoding="utf-8")
            raw.write_text("\n".join(original.splitlines()[:-1]) + "\n", encoding="utf-8")
            raw.chmod(0o600)
            with self.assertRaisesRegex(REPORT.ReportError, "incomplete"):
                REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=5)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, suite, _, _, scores = self.make_artifacts(root)
            scores["inference_jsonl_sha256"] = "f" * 64
            private_json(Path(str(raw) + ".scores.json"), scores)
            with self.assertRaisesRegex(REPORT.ReportError, "raw inference SHA-256"):
                REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=5)

    def test_rejects_row_identity_and_score_identity_disagreement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, suite, _, rows, scores = self.make_artifacts(root)
            rows[0]["fixture_id"] = "other"
            raw.write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
            raw.chmod(0o600)
            scores["inference_jsonl_sha256"] = REPORT.sha256_path(raw)
            private_json(Path(str(raw) + ".scores.json"), scores)
            with self.assertRaisesRegex(REPORT.ReportError, "fixture_id mismatch"):
                REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=5)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, suite, _, _, scores = self.make_artifacts(root)
            scores["scores"][0]["fixture_id"] = "other"
            private_json(Path(str(raw) + ".scores.json"), scores)
            with self.assertRaisesRegex(REPORT.ReportError, "score row 1 field fixture_id"):
                REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=5)

    def test_rejects_schedule_identity_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, suite, schedule, _, _ = self.make_artifacts(root)
            schedule["configuration"]["timeout_seconds"] = 99
            private_json(Path(str(raw) + ".schedule.json"), schedule)
            with self.assertRaisesRegex(REPORT.ReportError, "schedule SHA-256"):
                REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=5)

    @unittest.skipUnless(os.name == "posix", "POSIX permissions")
    def test_all_three_artifacts_must_be_owner_only(self):
        for suffix, label in (
            ("", "raw suite output"),
            (".schedule.json", "frozen schedule"),
            (".scores.json", "suite scores"),
        ):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                raw, suite, _, _, _ = self.make_artifacts(Path(directory))
                target = Path(str(raw) + suffix)
                target.chmod(0o644)
                with self.assertRaisesRegex(REPORT.ReportError, label):
                    REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=5)

    def test_claim_and_completion_receipts_are_exact_and_complete(self):
        mutations = (
            "missing_claim", "missing_done", "claim_tamper", "done_tamper", "orphan"
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                raw, suite, schedule, _, _ = self.make_artifacts(root)
                claims = Path(str(raw) + ".claims") / schedule["schedule_id"]
                first = schedule["jobs"][0]
                claim_path = claims / (first["run_id"] + ".json")
                done_path = claims / (first["run_id"] + ".done.json")
                if mutation == "missing_claim":
                    claim_path.unlink()
                    message = "exact scheduled 2N set"
                elif mutation == "missing_done":
                    done_path.unlink()
                    message = "exact scheduled 2N set"
                elif mutation == "claim_tamper":
                    claim = json.loads(claim_path.read_text(encoding="utf-8"))
                    claim["ordinal"] += 1
                    private_json(claim_path, claim)
                    message = "claim 1 ordinal mismatch"
                elif mutation == "done_tamper":
                    done = json.loads(done_path.read_text(encoding="utf-8"))
                    done["row_sha256"] = "f" * 64
                    private_json(done_path, done)
                    message = "completion 1 receipt mismatch"
                else:
                    private_json(claims / "orphan.done.json", {"orphan": True})
                    message = "exact scheduled 2N set"
                with self.assertRaisesRegex(REPORT.ReportError, message):
                    REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=5)

    @unittest.skipUnless(os.name == "posix", "POSIX permissions")
    def test_claim_directories_and_files_must_be_private_non_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, suite, schedule, _, _ = self.make_artifacts(root)
            claims_root = Path(str(raw) + ".claims")
            claims_root.chmod(0o755)
            with self.assertRaisesRegex(REPORT.ReportError, "claims root must be owner-only"):
                REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=5)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, suite, schedule, _, _ = self.make_artifacts(root)
            claims = Path(str(raw) + ".claims") / schedule["schedule_id"]
            first = schedule["jobs"][0]
            claim_path = claims / (first["run_id"] + ".json")
            real = claims / "saved-claim"
            claim_path.rename(real)
            # Move the target outside the claims directory so the entry-name
            # set remains exact and validation reaches the file symlink check.
            saved = real.read_bytes()
            real.unlink()
            outside = root / "outside-claim.json"
            outside.write_bytes(saved)
            outside.chmod(0o600)
            claim_path.symlink_to(outside)
            with self.assertRaisesRegex(REPORT.ReportError, "non-symlink"):
                REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=5)

    def test_manifest_fixture_identity_triples_are_unique_and_exact_before_scoring(self):
        for mutation, message in (("duplicate", "duplicate suite manifest fixture_id"),
                                  ("hash", "fixture identity triples mismatch")):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                _, manifest_path, schedule, _, _ = self.make_artifacts(root)
                document = json.loads(manifest_path.read_text(encoding="utf-8"))
                if mutation == "duplicate":
                    document["fixtures"][1] = copy.deepcopy(document["fixtures"][0])
                else:
                    document["fixtures"][0]["context_sha256"] = "9" * 64
                private_json(manifest_path, document)
                schedule["suite"]["manifest_sha256"] = REPORT.sha256_path(manifest_path)
                with self.assertRaisesRegex(REPORT.ReportError, message):
                    REPORT.validate_suite_manifest(manifest_path, schedule)

    def test_reporter_rejects_self_consistent_noncampaign_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, schedule, _, _ = self.make_artifacts(Path(directory))
            schedule.pop("schedule_id")
            for job in schedule["jobs"]:
                job.pop("run_id")
            schedule["configuration"]["model"] = "diagnostic-model"
            schedule_id = hashlib.sha256(REPORT.canonical_json_bytes(schedule)).hexdigest()
            for job in schedule["jobs"]:
                job["run_id"] = hashlib.sha256(
                    b"oolong-run-v1\0" + schedule_id.encode("ascii")
                    + REPORT.canonical_json_bytes(job)
                ).hexdigest()
            schedule["schedule_id"] = schedule_id
            with self.assertRaisesRegex(REPORT.ReportError, "campaign profile model mismatch"):
                REPORT.validate_schedule(schedule)

    def test_suite_rows_recompute_and_reject_stale_or_forged_scores(self):
        for mutation in ("stale", "forged"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                raw, suite, _, _, scores = self.make_artifacts(root)
                if mutation == "stale":
                    # Keep the terminal booleans consistent so only independent
                    # exact score-object recomputation detects the stale field.
                    scores["scores"][0]["score"]["parsed_value"] = 999
                else:
                    target = next(
                        item for item in scores["scores"]
                        if item["execution_success"] and not item["score"]["correct"]
                    )
                    target["score"] = {
                        "correct": True,
                        "strict_exact": True,
                        "expected": "Answer: 1",
                        "parsed_value": 1,
                        "parse_error": None,
                    }
                    target["success"] = True
                private_json(Path(str(raw) + ".scores.json"), scores)
                with self.assertRaisesRegex(
                    REPORT.ReportError, "independent strict_score recomputation"
                ):
                    REPORT.build_report(
                        raw, suite_manifest=suite, bootstrap_iterations=5
                    )

    def test_suite_row_fixture_hash_is_reverified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, suite_path, _, _, _ = self.make_artifacts(root)
            suite = json.loads(suite_path.read_text(encoding="utf-8"))
            row_path = root / suite["fixtures"][0]["row"]
            row_path.write_text(row_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
            row_path.chmod(0o600)
            with self.assertRaisesRegex(REPORT.ReportError, "row SHA-256 mismatch"):
                REPORT.build_report(
                    raw, suite_manifest=suite_path, bootstrap_iterations=5
                )

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_raw_and_sidecars_may_not_be_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, suite, _, _, _ = self.make_artifacts(root)
            link = root / "linked.jsonl"
            link.symlink_to(raw)
            # Give the link spelling private regular sidecar copies; the raw
            # lstat check must still reject the link itself before reading it.
            for suffix in (".schedule.json", ".scores.json"):
                copied = Path(str(link) + suffix)
                copied.write_bytes(Path(str(raw) + suffix).read_bytes())
                copied.chmod(0o600)
            with self.assertRaisesRegex(REPORT.ReportError, "non-symlink"):
                REPORT.build_report(link, suite_manifest=suite, bootstrap_iterations=5)

    def test_independent_root_context_gate_rejects_false_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o700)
            context = root / "context.txt"
            exact = "".join(chr(0x600 + index) for index in range(140))
            context.write_bytes(("prefix" + exact + "suffix").encode("utf-8"))
            context.chmod(0o600)
            run_dir = root / "run"
            run_dir.mkdir(mode=0o700)
            trace = run_dir / "azdaja-solo-trace.log"
            trace.write_bytes(("request:" + exact + ":reply").encode("utf-8"))
            trace.chmod(0o600)
            context_sha = REPORT.sha256_path(context)
            assertion = REPORT.scan_context_file_against_solo_trace(
                context,
                trace,
                expected_context_sha256=context_sha,
                exact_transcript_preserved=True,
            )
            row = {
                "arm": "jcode-azdaja",
                "execution_success": True,
                "failure": None,
                "root_context_leak_assertion": assertion,
                "trajectory_run_directory": str(run_dir),
                "trajectory_artifacts": {"azdaja_solo_trace": {
                    "path": str(trace),
                    "sha256": REPORT.sha256_path(trace),
                    "source_sha256_before_redaction": REPORT.sha256_path(trace),
                    "exact_text_preserved": True,
                    "bytes": trace.stat().st_size,
                }},
            }
            score = {"success": True}
            job = {
                "arm": "jcode-azdaja", "fixture_id": "fixture",
                "context_sha256": context_sha,
            }
            suite = {"fixtures": [{
                "fixture_id": "fixture", "context": context.name,
                "context_sha256": context_sha,
            }]}
            with self.assertRaises(REPORT.ReportError):
                REPORT.independently_validate_root_context_leaks(
                    root / "manifest.json", suite, [row], [score], [job]
                )
            row["execution_success"] = False
            row["failure"] = {
                "kind": "root_context_leak",
                "normalized_kind": "root_context_leak",
                "message": "root_context_leak",
            }
            score["success"] = False
            result = REPORT.independently_validate_root_context_leaks(
                root / "manifest.json", suite, [row], [score], [job]
            )
            self.assertEqual(result["leak_rows"], 1)

    def test_candidate_components_executable_binding_and_unicode_scan(self):
        components = {
            "azdaja": {"sha256": "a" * 64, "bytes": 11},
            "config.toml": {"sha256": "b" * 64, "bytes": 12},
            "SKILL.md": {"sha256": "c" * 64, "bytes": 13},
        }
        candidate = {
            "sha256": hashlib.sha256(
                REPORT.canonical_json_bytes({
                    name: components[name] for name in sorted(components)
                })
            ).hexdigest(),
            "components": components,
        }
        def executable(name, sha, size):
            path = "/" + name
            return {
                "path": path,
                "sha256": sha,
                "bytes": size,
                "version": name + " 1.0",
                "version_command": [path, "--version"],
            }
        configuration = {
            "controller": {"path": "/controller", "sha256": "d" * 64, "bytes": 1},
            "executables": {
                "jcode": executable("jcode", "e" * 64, 9),
                "azdaja": executable("azdaja", "a" * 64, 11),
            },
            "candidate": candidate,
        }
        REPORT.validate_frozen_identity_stamp(
            configuration, ["jcode-native", "jcode-azdaja"]
        )
        tampered = copy.deepcopy(configuration)
        tampered["candidate"]["components"]["azdaja"]["bytes"] = 99
        with self.assertRaises(REPORT.ReportError):
            REPORT.validate_frozen_identity_stamp(
                tampered, ["jcode-native", "jcode-azdaja"]
            )
        exact = "".join(chr(0x500 + index) for index in range(110))
        finding = REPORT.exact_common_substring_scan("x" + exact, exact + "y")
        self.assertTrue(finding["leak_detected"])
        self.assertFalse(finding["matched_text_retained"])
        self.assertNotIn(exact[:100], json.dumps(finding, ensure_ascii=False))

    def test_failed_azdaja_row_without_trace_blocks_mandatory_leak_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            raw, suite_path, schedule, rows, scores_document = self.make_artifacts(Path(directory))
            index = next(
                offset for offset, job in enumerate(schedule["jobs"])
                if job["arm"] == "jcode-azdaja"
            )
            rows[index]["trajectory_artifacts"] = {}
            rows[index]["execution_success"] = False
            scores_document["scores"][index]["execution_success"] = False
            scores_document["scores"][index]["success"] = False
            suite_document = REPORT.validate_suite_manifest(suite_path, schedule)
            with self.assertRaisesRegex(
                REPORT.ReportError, "mandatory exact root transcript authority"
            ):
                REPORT.independently_validate_root_context_leaks(
                    suite_path, suite_document, rows, scores_document["scores"], schedule["jobs"]
                )

    def test_score_success_must_be_derived_exactly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, suite, _, _, scores = self.make_artifacts(root)
            scores["scores"][0]["success"] = False
            private_json(Path(str(raw) + ".scores.json"), scores)
            with self.assertRaisesRegex(REPORT.ReportError, "success mismatch"):
                REPORT.build_report(raw, suite_manifest=suite, bootstrap_iterations=5)


if __name__ == "__main__":
    unittest.main()
