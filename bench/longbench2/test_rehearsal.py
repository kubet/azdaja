#!/usr/bin/env python3
"""Real subprocess tests for the offline pre-freeze rehearsal and production gate."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REHEARSAL = HERE / "rehearsal.py"
RUNNER = HERE / "run.py"
TMP_PARENT = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp")


class PreFreezeRehearsalSubprocessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(dir=TMP_PARENT)
        self.root = Path(self.temporary.name)
        self.root.chmod(0o700)
        self.manifest = self.root / "target-manifest.json"
        self.manifest.write_bytes(b'{"synthetic_target_for_rehearsal_test":true}\n')
        self.manifest.chmod(0o600)
        self.candidate = self.root / "candidate"
        self.candidate.mkdir(mode=0o700)
        for name, data in (
            ("SKILL.md", b"# synthetic test candidate\n"),
            ("config.toml", b"synthetic = true\n"),
        ):
            (self.candidate / name).write_bytes(data)
            (self.candidate / name).chmod(0o600)
        self.azdaja = self.candidate / "azdaja"
        self.jcode = self.root / "jcode"
        prime_root = self.root / "prime-package"
        (prime_root / "dist" / "bundle").mkdir(parents=True, mode=0o700)
        self.prime = prime_root / "dist" / "bundle" / "cli.js"
        (prime_root / "package.json").write_text(
            json.dumps({"name": "prime-agent", "bin": {"prime-agent": "dist/bundle/cli.js"}})
        )
        (prime_root / "package.json").chmod(0o600)
        for path in (self.azdaja, self.jcode, self.prime):
            path.write_bytes(b"#!/bin/sh\necho synthetic-version\n")
            path.chmod(0o700)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def command(self, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(REHEARSAL), *(str(value) for value in arguments)],
            cwd=HERE.parents[1], text=True, capture_output=True, timeout=60,
        )

    def create_bundle(self) -> Path:
        bundle = self.root / "bundle"
        result = self.command(
            "run", "--bundle", bundle,
            "--target-manifest", self.manifest,
            "--target-candidate", self.candidate,
            "--target-jcode", self.jcode,
            "--target-prime-agent", self.prime,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return bundle

    def test_positive_subprocess_builds_and_reopens_exact_bundle(self) -> None:
        bundle = self.create_bundle()
        receipt_path = bundle / "final-receipt.json"
        result = self.command("verify", "--receipt", receipt_path)
        self.assertEqual(result.returncode, 0, result.stderr)
        binding = json.loads(result.stdout)
        self.assertEqual(binding["record_type"], "lb2_pre_freeze_rehearsal_binding")
        rows = (bundle / "runs.jsonl").read_bytes().splitlines()
        self.assertEqual(len(rows), 60)
        claim_roots = list((bundle / "claims").iterdir())
        self.assertEqual(len(claim_roots), 1)
        claims = list(claim_roots[0].iterdir())
        self.assertEqual(sum(path.name.endswith(".json") and not path.name.endswith(".done.json") for path in claims), 60)
        self.assertEqual(sum(path.name.endswith(".done.json") for path in claims), 60)
        self.assertEqual(len(list((bundle / "artifacts").iterdir())), 60)
        terminal = json.loads((bundle / "terminal-validation.json").read_text())
        self.assertEqual(
            terminal["trace_sample_counts"],
            {"v43_success": 10, "v43_transient_timeout_retry": 10},
        )
        report = json.loads((bundle / "report.json").read_text())
        self.assertFalse(report["benchmark_result"])
        self.assertTrue(report["integrity"]["terminal_validated_before_gold_open"])
        self.assertTrue(report["integrity"]["shared_score_core"])
        self.assertTrue(report["integrity"]["exact_synthetic_oracle_asserted"])
        terminal_rows = [json.loads(line) for line in (bundle / "runs.jsonl").read_text().splitlines()]
        self.assertEqual(len(terminal_rows), 60)
        self.assertTrue(all(row["auth_assertion"] == {
            "asserted": False, "offline_rehearsal": True,
            "oauth_used": False, "inference_used": False,
        } for row in terminal_rows))
        self.assertEqual(report["envelope_compatible_gate"]["arms"]["jcode-azdaja"]["correct_n"], 10)

    def test_tampered_artifact_is_refused_by_real_verifier_subprocess(self) -> None:
        bundle = self.create_bundle()
        response = next((bundle / "artifacts").glob("*/stdout.ndjson"))
        response.write_bytes(response.read_bytes() + b"tamper")
        response.chmod(0o600)
        result = self.command("verify", "--receipt", bundle / "final-receipt.json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("drifted", result.stderr)

    def test_production_missing_receipt_refuses_before_artifacts_or_auth(self) -> None:
        output = self.root / "never-created.jsonl"
        work = self.root / "never-created-work"
        result = subprocess.run(
            [
                "python3", str(RUNNER), "--manifest", str(self.manifest),
                "--output", str(output), "--work-dir", str(work),
                "--azdaja-skill", str(self.candidate), "--jcode", str(self.jcode),
                "--prime-agent", str(self.prime), "--yes-run-inference",
            ],
            cwd=HERE.parents[1], text=True, capture_output=True, timeout=30,
            env={**os.environ, "HOME": str(self.root / "no-oauth-home")},
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires --pre-freeze-rehearsal-receipt", result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse(Path(str(output) + ".schedule.json").exists())
        self.assertFalse(Path(str(output) + ".claims").exists())
        self.assertFalse(work.exists())


if __name__ == "__main__":
    unittest.main()
