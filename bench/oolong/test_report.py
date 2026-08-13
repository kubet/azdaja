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
    def make_artifacts(self, root: Path, repetitions: int = 2):
        raw = root / "suite.jsonl"
        suite_path = root / "manifest.json"
        fixture_ids = ["f-1", "f-2"]
        fixture_rows = []
        for index, fixture_id in enumerate(fixture_ids, 1):
            row_path = root / f"row-{index}.json"
            private_json(
                row_path,
                {
                    "source": "oolongbench/oolong-synth",
                    "question": "Return the count as an Answer line.",
                    "answer": "[1]",
                    "test_fixture_index": index,
                },
            )
            fixture_rows.append((index, fixture_id, row_path))
        suite = {
            "schema_version": 1,
            "source": "oolongbench/oolong-synth",
            "split": "validation",
            "upstream_commit": "0" * 40,
            "fixtures": [
                {
                    "fixture_id": fixture_id,
                    "row": row_path.name,
                    "row_sha256": REPORT.sha256_path(row_path),
                    "context_sha256": str(index + 2) * 64,
                    "dataset": "spam",
                    "context_window_id": 10000 + index,
                }
                for index, fixture_id, row_path in fixture_rows
            ],
        }
        private_json(suite_path, suite)
        schedule = {
            "schema_version": 1,
            "record_type": "oolong_frozen_schedule",
            "suite": {
                "manifest_sha256": REPORT.sha256_path(suite_path),
                "source": "oolongbench/oolong-synth",
                "split": "validation",
                "upstream_commit": "0" * 40,
                "fixtures": [
                    {
                        "fixture_id": item["fixture_id"],
                        "row_sha256": item["row_sha256"],
                        "context_sha256": item["context_sha256"],
                    }
                    for item in suite["fixtures"]
                ],
            },
            "configuration": {
                "model": "test-model",
                "reasoning": "medium",
                "arms": ["arm-a", "arm-b"],
                "repetitions": repetitions,
                "seed": 7,
                "timeout_seconds": 30,
                "candidate": None,
                "controller": {
                    "path": "/controller",
                    "sha256": "a" * 64,
                    "bytes": 1,
                },
                "executables": {},
            },
            "jobs": [],
        }
        ordinal = 0
        for repetition in range(1, repetitions + 1):
            for fixture in schedule["suite"]["fixtures"]:
                for arm in schedule["configuration"]["arms"]:
                    ordinal += 1
                    schedule["jobs"].append(
                        {
                            "ordinal": ordinal,
                            "fixture_id": fixture["fixture_id"],
                            "row_sha256": fixture["row_sha256"],
                            "context_sha256": fixture["context_sha256"],
                            "repetition": repetition,
                            "arm": arm,
                        }
                    )
        schedule_id = hashlib.sha256(REPORT.canonical_json_bytes(schedule)).hexdigest()
        for job in schedule["jobs"]:
            job["run_id"] = hashlib.sha256(
                b"oolong-run-v1\0"
                + schedule_id.encode("ascii")
                + REPORT.canonical_json_bytes(job)
            ).hexdigest()
        schedule["schedule_id"] = schedule_id
        private_json(Path(str(raw) + ".schedule.json"), schedule)

        rows = []
        scores = []
        for job in schedule["jobs"]:
            key = (job["fixture_id"], job["repetition"], job["arm"])
            execution_success = key != ("f-2", repetitions, "arm-a")
            if job["arm"] == "arm-a":
                correct = job["fixture_id"] == "f-1"
                latency = 2.0
                tokens = 10
            else:
                correct = not (
                    job["fixture_id"] == "f-1" and job["repetition"] == repetitions
                )
                latency = 4.0
                tokens = 20
            usage_valid = execution_success
            row = {
                "schema_version": 1,
                "benchmark": "oolong",
                "record_type": "inference",
                "schedule_id": schedule_id,
                "run_id": job["run_id"],
                "fixture_id": job["fixture_id"],
                "row_sha256": job["row_sha256"],
                "context_sha256": job["context_sha256"],
                "execution_ordinal": job["ordinal"],
                "arm": job["arm"],
                "repetition": job["repetition"],
                "model": "test-model",
                "reasoning": "medium",
                "candidate_sha256": None,
                "controller_sha256": "a" * 64,
                "success": None,
                "score": None,
                "scoring_status": "deferred",
                "execution_success": execution_success,
                "latency_seconds": latency,
                "runtime_route_assertion": {"asserted": execution_success},
                "efficiency_evidence": {"valid": usage_valid},
                "usage": (
                    {
                        "input_tokens": tokens - 2,
                        "output_tokens": 2,
                        "cache_read_tokens": 0,
                        "cache_write_tokens": 0,
                        "total_tokens": tokens,
                    }
                    if usage_valid
                    else None
                ),
                "failure": (
                    None
                    if execution_success
                    else {"kind": "timeout", "message": "timed out"}
                ),
                "response": "Answer: 1" if correct else "Answer: 0",
            }
            score = {
                "run_id": job["run_id"],
                "ordinal": job["ordinal"],
                "fixture_id": job["fixture_id"],
                "arm": job["arm"],
                "repetition": job["repetition"],
                "execution_success": execution_success,
                "score": {
                    "correct": correct,
                    "strict_exact": True,
                    "expected": "Answer: 1",
                    "parsed_value": 1 if correct else 0,
                    "parse_error": (
                        None if correct
                        else "output was not exactly the canonical gold answer"
                    ),
                },
                "success": execution_success and correct,
            }
            rows.append(row)
            scores.append(score)
        raw.write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )
        raw.chmod(0o600)
        claims_root = Path(str(raw) + ".claims")
        claims_root.mkdir(mode=0o700)
        claims = claims_root / schedule_id
        claims.mkdir(mode=0o700)
        if os.name == "posix":
            claims_root.chmod(0o700)
            claims.chmod(0o700)
        for row, job in zip(rows, schedule["jobs"]):
            private_json(
                claims / (job["run_id"] + ".json"),
                {
                    "schedule_id": schedule_id,
                    "run_id": job["run_id"],
                    "ordinal": job["ordinal"],
                    "pid": 123,
                },
            )
            private_json(
                claims / (job["run_id"] + ".done.json"),
                {
                    "schedule_id": schedule_id,
                    "run_id": job["run_id"],
                    "row_sha256": hashlib.sha256(
                        REPORT.canonical_json_bytes(row)
                    ).hexdigest(),
                },
            )
        scores_document = {
            "schema_version": 1,
            "record_type": "oolong_deferred_scores",
            "schedule_id": schedule_id,
            "manifest_sha256": REPORT.sha256_path(suite_path),
            "inference_jsonl_sha256": REPORT.sha256_path(raw),
            "scores": scores,
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
            self.assertEqual(result["bootstrap"]["cluster_by"], "dataset+context_window_id")
            self.assertEqual(result["bootstrap"]["cluster_count"], 2)
            arm_a = result["arms"]["arm-a"]
            self.assertEqual(arm_a["scheduled_n"], 4)
            self.assertEqual(arm_a["execution"]["completed_n"], 3)
            self.assertEqual(arm_a["exact_success"], {"n": 2, "rate": 0.5})
            self.assertEqual(
                arm_a["failure"]["taxonomy"], {"strict_score": 1, "timeout": 1}
            )
            self.assertEqual(arm_a["wall_seconds_all_attempts"]["p95"], 2.0)
            self.assertEqual(arm_a["tokens_all_attempts"]["missing_usage_n"], 1)
            self.assertIsNone(
                arm_a["tokens_all_attempts"]["unconditional_total_tokens"]
            )
            self.assertEqual(arm_a["route_integrity"]["failed_n"], 1)
            pair = result["comparisons"]["arm-a__vs__arm-b"]
            self.assertEqual(pair["paired_n"], 4)
            self.assertEqual(pair["both_correct_n"], 1)
            self.assertAlmostEqual(pair["accuracy"]["delta"], 0.25)
            self.assertAlmostEqual(pair["latency_geometric_ratio"]["value"], 2.0)
            self.assertAlmostEqual(pair["token_geometric_ratio"]["value"], 2.0)
            self.assertTrue(any("only 2" in warning for warning in result["warnings"]))

    def test_bootstrap_is_deterministic_and_falls_back_to_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            raw, _, _, _, _ = self.make_artifacts(Path(directory))
            first = REPORT.build_report(raw, bootstrap_iterations=60)
            second = REPORT.build_report(raw, bootstrap_iterations=60)
            self.assertEqual(first, second)
            self.assertEqual(first["bootstrap"]["seed"], REPORT.BOOTSTRAP_SEED)
            self.assertEqual(first["bootstrap"]["cluster_by"], "fixture_id")
            self.assertTrue(any("falls back" in item for item in first["warnings"]))

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
            raw, _, _, _, _ = self.make_artifacts(root)
            original = raw.read_text(encoding="utf-8")
            raw.write_text("\n".join(original.splitlines()[:-1]) + "\n", encoding="utf-8")
            raw.chmod(0o600)
            with self.assertRaisesRegex(REPORT.ReportError, "incomplete"):
                REPORT.build_report(raw, bootstrap_iterations=5)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, _, _, _, scores = self.make_artifacts(root)
            scores["inference_jsonl_sha256"] = "f" * 64
            private_json(Path(str(raw) + ".scores.json"), scores)
            with self.assertRaisesRegex(REPORT.ReportError, "raw inference SHA-256"):
                REPORT.build_report(raw, bootstrap_iterations=5)

    def test_rejects_row_identity_and_score_identity_disagreement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, _, _, rows, scores = self.make_artifacts(root)
            rows[0]["fixture_id"] = "other"
            raw.write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
            raw.chmod(0o600)
            scores["inference_jsonl_sha256"] = REPORT.sha256_path(raw)
            private_json(Path(str(raw) + ".scores.json"), scores)
            with self.assertRaisesRegex(REPORT.ReportError, "fixture_id mismatch"):
                REPORT.build_report(raw, bootstrap_iterations=5)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, _, _, _, scores = self.make_artifacts(root)
            scores["scores"][0]["fixture_id"] = "other"
            private_json(Path(str(raw) + ".scores.json"), scores)
            with self.assertRaisesRegex(REPORT.ReportError, "score row 1 field fixture_id"):
                REPORT.build_report(raw, bootstrap_iterations=5)

    def test_rejects_schedule_identity_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, _, schedule, _, _ = self.make_artifacts(root)
            schedule["configuration"]["timeout_seconds"] = 99
            private_json(Path(str(raw) + ".schedule.json"), schedule)
            with self.assertRaisesRegex(REPORT.ReportError, "schedule SHA-256"):
                REPORT.build_report(raw, bootstrap_iterations=5)

    @unittest.skipUnless(os.name == "posix", "POSIX permissions")
    def test_all_three_artifacts_must_be_owner_only(self):
        for suffix, label in (
            ("", "raw suite output"),
            (".schedule.json", "frozen schedule"),
            (".scores.json", "suite scores"),
        ):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                raw, _, _, _, _ = self.make_artifacts(Path(directory))
                target = Path(str(raw) + suffix)
                target.chmod(0o644)
                with self.assertRaisesRegex(REPORT.ReportError, label):
                    REPORT.build_report(raw, bootstrap_iterations=5)

    def test_claim_and_completion_receipts_are_exact_and_complete(self):
        mutations = (
            "missing_claim", "missing_done", "claim_tamper", "done_tamper", "orphan"
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                raw, _, schedule, _, _ = self.make_artifacts(root)
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
                    REPORT.build_report(raw, bootstrap_iterations=5)

    @unittest.skipUnless(os.name == "posix", "POSIX permissions")
    def test_claim_directories_and_files_must_be_private_non_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, _, schedule, _, _ = self.make_artifacts(root)
            claims_root = Path(str(raw) + ".claims")
            claims_root.chmod(0o755)
            with self.assertRaisesRegex(REPORT.ReportError, "claims root must be owner-only"):
                REPORT.build_report(raw, bootstrap_iterations=5)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, _, schedule, _, _ = self.make_artifacts(root)
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
                REPORT.build_report(raw, bootstrap_iterations=5)

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
            raw, _, _, _, _ = self.make_artifacts(root)
            link = root / "linked.jsonl"
            link.symlink_to(raw)
            # Give the link spelling private regular sidecar copies; the raw
            # lstat check must still reject the link itself before reading it.
            for suffix in (".schedule.json", ".scores.json"):
                copied = Path(str(link) + suffix)
                copied.write_bytes(Path(str(raw) + suffix).read_bytes())
                copied.chmod(0o600)
            with self.assertRaisesRegex(REPORT.ReportError, "non-symlink"):
                REPORT.build_report(link, bootstrap_iterations=5)

    def test_score_success_must_be_derived_exactly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, _, _, _, scores = self.make_artifacts(root)
            scores["scores"][0]["success"] = False
            private_json(Path(str(raw) + ".scores.json"), scores)
            with self.assertRaisesRegex(REPORT.ReportError, "success mismatch"):
                REPORT.build_report(raw, bootstrap_iterations=5)


if __name__ == "__main__":
    unittest.main()
