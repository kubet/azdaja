"""Offline envelope tests. The real acceptance command is exercised separately."""
import contextlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from . import acceptance_cli as cli


class AcceptanceCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR"))
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.output = self.root / "result.json"
        self.argv = ["--scratch", str(self.root), "--azdaja", "/usr/bin/false", "--receipt", str(self.output)]

    def invoke(self, args=None, effect=None):
        stdout = io.StringIO()
        with mock.patch.object(cli, "run_checks", side_effect=effect) as check, contextlib.redirect_stdout(stdout):
            status = cli.main(self.argv if args is None else args)
        return status, json.loads(stdout.getvalue()), check

    def test_existing_receipt_rejected_before_any_checks(self):
        self.output.write_bytes(b"retained evidence")
        status, report, check = self.invoke()
        self.assertEqual((status, report["error_code"]), (2, "receipt_exists"))
        check.assert_not_called()
        self.assertEqual(self.output.read_bytes(), b"retained evidence")

    def test_dangling_receipt_symlink_is_not_followed(self):
        target = self.root / "missing-target"
        self.output.symlink_to(target)
        status, report, check = self.invoke()
        self.assertEqual((status, report["error_code"]), (2, "receipt_exists"))
        check.assert_not_called()
        self.assertTrue(self.output.is_symlink())
        self.assertFalse(target.exists())

    def test_missing_binary_stops_before_checks_and_output(self):
        args = self.argv[:]
        args[3] = str(self.root / "absent-binary")
        status, report, check = self.invoke(args)
        self.assertEqual((status, report["error_code"]), (2, "evaluator_missing_or_not_executable"))
        check.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_missing_scratch_stops_before_checks_and_output(self):
        args = self.argv[:]
        args[1] = str(self.root / "absent-scratch")
        status, report, check = self.invoke(args)
        self.assertEqual((status, report["error_code"]), (2, "scratch_directory_required"))
        check.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_failed_stage_is_a_failed_receipt_not_success(self):
        def fail(binary, scratch, report):
            report["stage"] = "synthetic_failure_path"
            raise cli.CheckFailed("synthetic_failure_path:unexpected_exit")
        status, report, _ = self.invoke(effect=fail)
        self.assertEqual(status, 2)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["error_code"], "synthetic_failure_path:unexpected_exit")
        self.assertEqual(json.loads(self.output.read_text()), report)
        self.assertFalse(report["semantic_efficacy_established"])

    def test_receipt_creation_race_never_overwrites(self):
        def race(binary, scratch, report):
            report["stage"] = "complete"
            self.output.write_bytes(b"concurrent evidence")
        status, report, _ = self.invoke(effect=race)
        self.assertEqual((status, report["error_code"]), (2, "receipt_write_failed"))
        self.assertEqual(self.output.read_bytes(), b"concurrent evidence")

    def test_success_envelope_has_private_file_and_no_efficacy_upgrade(self):
        def finish(binary, scratch, report):
            report["stage"] = "complete"
        status, report, _ = self.invoke(effect=finish)
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(self.output.read_text()), report)
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o600)
        for field in ("semantic_efficacy_established", "automatic_planning_established", "native_judge_function_implemented"):
            self.assertIs(report[field], False)

    def test_interruption_cannot_emit_success(self):
        stdout = io.StringIO()
        with mock.patch.object(cli, "run_checks", side_effect=KeyboardInterrupt), contextlib.redirect_stdout(stdout):
            with self.assertRaises(KeyboardInterrupt):
                cli.main(self.argv)
        self.assertFalse(self.output.exists())
        self.assertEqual(stdout.getvalue(), "")

    def test_audit_suite_selects_explicit_binary_in_fresh_process(self):
        selected = self.root / "selected-not-invoked"
        code = ("import sys; sys.path.insert(0, sys.argv[1]); "
                "from test_audit import ReceiptAuditTests; "
                "case = ReceiptAuditTests('test_actual_failed_receipts_replay_without_inference'); "
                "case.setUp(); print(case.binary); case.doCleanups()")
        env = {"PATH": "/usr/bin:/bin", "HOME": str(self.root),
               "JCODE_SCRATCH_DIR": str(self.root), "AZDAJA_BINARY": str(selected),
               "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run([sys.executable, "-B", "-c", code, str(cli.ROOT / "bench/jev")],
                                cwd=self.root, env=env, text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), str(selected.resolve()))
        self.assertFalse(selected.exists())

    def test_strict_parser_or_startup_error_is_not_a_valid_rejection(self):
        for diagnostic in ("unrecognized arguments: --output", "cannot open audit script"):
            result = subprocess.CompletedProcess([], 2, stdout="", stderr=diagnostic)
            with self.subTest(diagnostic=diagnostic), self.assertRaisesRegex(
                    cli.CheckFailed, "^strict_audit:unexpected_diagnostic$"):
                cli.validate_strict_rejection(result, self.output)

    def test_strict_fixed_envelope_still_requires_no_output(self):
        result = subprocess.CompletedProcess([], 2,
            stdout="offline receipt audit failed; no successful result emitted\n", stderr="")
        cli.validate_strict_rejection(result, self.output)
        self.output.write_text("must not exist")
        with self.assertRaisesRegex(cli.CheckFailed, "^strict_audit:unexpected_result$"):
            cli.validate_strict_rejection(result, self.output)


if __name__ == "__main__":
    unittest.main()
