from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import reproduce
import verify


def scenario(name: str, prompt_bytes: int = 10_000, rss: int | None = 123_456) -> dict[str, object]:
    return {
        "kind": "scenario",
        "scenario": name,
        "answer": reproduce.EXPECTED_ANSWERS[name],
        **reproduce.FIXED_INVARIANTS,
        "root_prompt_bytes": prompt_bytes,
        "reaped_children_high_water_bytes": rss,
    }


def good_records() -> list[dict[str, object]]:
    scenarios = [scenario(name) for name in sorted(reproduce.SCENARIOS)]
    return scenarios + [
        {
            "kind": "summary",
            "scenarios": 3,
            "cleanup": "passed",
            "surviving_sessions": 0,
            "rss_available": True,
            "peak_reaped_children_high_water_bytes": 123_456,
        }
    ]


class RecordTests(unittest.TestCase):
    def test_parse_only_structured_lines(self):
        records = reproduce.parse_structured(
            "noise\n{not json}\n" + "\n".join(json.dumps(record) for record in good_records())
        )
        scenarios, summary = reproduce.validate_records(records)
        self.assertEqual([record["scenario"] for record in scenarios], ["build", "repo", "transcript"])
        self.assertEqual(summary["cleanup"], "passed")

    def test_validation_rejects_duplicate_or_missing_scenario(self):
        records = good_records()
        with self.assertRaisesRegex(ValueError, "exactly one"):
            reproduce.validate_records([records[0], records[0], records[1], records[-1]])

    def test_validation_rejects_unbounded_prompt(self):
        records = good_records()
        records[0]["root_prompt_bytes"] = 64 * 1024
        with self.assertRaisesRegex(ValueError, "outside the accepted bound"):
            reproduce.validate_records(records)

    def test_validation_rejects_wrong_answer(self):
        records = good_records()
        records[0]["answer"] = "Answer: 42"
        with self.assertRaisesRegex(ValueError, "answer mismatch"):
            reproduce.validate_records(records)

    def test_validation_accepts_platform_without_rss(self):
        records = [scenario(name, rss=None) for name in sorted(reproduce.SCENARIOS)]
        records.append(
            {
                "kind": "summary",
                "scenarios": 3,
                "cleanup": "passed",
                "surviving_sessions": 0,
                "rss_available": False,
                "peak_reaped_children_high_water_bytes": None,
            }
        )
        reproduce.validate_records(records)


class OutputTests(unittest.TestCase):
    def test_command_output_redacts_repository_root_before_hashing(self):
        raw = b"Compiling azdaja (" + bytes(reproduce.ROOT) + b")\n"
        sanitized = reproduce.sanitize_command_output(raw)
        self.assertEqual(sanitized, b"Compiling azdaja (<repo>)\n")
        self.assertNotIn(bytes(reproduce.ROOT), sanitized)

    def test_overwrite_refusal_and_force(self):
        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "receipt.json"
            missing = Path(directory) / "summary.md"
            existing.write_text("old")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                reproduce.ensure_new_outputs([existing, missing], force=False)
            reproduce.ensure_new_outputs([existing, missing], force=True)

    def test_atomic_write_replaces_complete_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result"
            output.write_bytes(b"old")
            reproduce.atomic_write(output, b"new")
            self.assertEqual(output.read_bytes(), b"new")
            self.assertEqual(list(Path(directory).glob("*.tmp-*")), [])


class VerifierTests(unittest.TestCase):
    def test_source_manifest_detects_hash_tamper(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.rs"
            source.write_text("fn main() {}\n")
            manifest = [
                {
                    "path": "source.rs",
                    "bytes": source.stat().st_size,
                    "sha256": reproduce.sha256(source),
                }
            ]
            verify.validate_source_manifest(manifest, root, ["source.rs"])
            tampered = copy.deepcopy(manifest)
            tampered[0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                verify.validate_source_manifest(tampered, root, ["source.rs"])

    def test_source_manifest_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root.parent / "outside.rs"
            outside.write_text("outside")
            self.addCleanup(lambda: outside.unlink(missing_ok=True))
            manifest = [{"path": "../outside.rs", "bytes": 7, "sha256": reproduce.sha256(outside)}]
            with self.assertRaisesRegex(ValueError, "unsafe source path"):
                verify.validate_source_manifest(manifest, root, ["../outside.rs"])

    def test_command_tamper_detection(self):
        output_hash = reproduce.sha256_bytes(b"output")
        records = [
            {
                "argv": reproduce.BUILD_CMD,
                "env": {},
                "exit_code": 0,
                "elapsed_seconds": 1.0,
                "output_sha256": output_hash,
            },
            {
                "argv": reproduce.TEST_CMD,
                "env": reproduce.TEST_ENV,
                "exit_code": 0,
                "elapsed_seconds": 2.0,
                "output_sha256": output_hash,
            },
        ]
        verify.validate_command_records(records)
        tampered = copy.deepcopy(records)
        tampered[1]["argv"] = ["echo", "pretend"]
        with self.assertRaisesRegex(ValueError, "invocation mismatch"):
            verify.validate_command_records(tampered)

    def test_binary_and_log_artifacts_require_strict_schema(self):
        good = {"path": "file", "bytes": 1, "sha256": "a" * 64}
        verify.validate_file_artifact(good, "artifact")
        bad = dict(good, extra=True)
        with self.assertRaisesRegex(ValueError, "schema keys mismatch"):
            verify.validate_file_artifact(bad, "artifact")

    def test_log_binds_each_command_output_hash(self):
        build_output = b"build output\n"
        test_output = b"test output\n"
        data = (
            reproduce.BUILD_LOG_HEADER
            + build_output
            + reproduce.TEST_LOG_HEADER
            + test_output
        )
        commands = [
            {"output_sha256": reproduce.sha256_bytes(build_output)},
            {"output_sha256": reproduce.sha256_bytes(test_output)},
        ]
        artifact = {"bytes": len(data), "sha256": reproduce.sha256_bytes(data)}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.log"
            path.write_bytes(data)
            verify.validate_log_contents(path, artifact, commands)
            commands[1]["output_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "test output hash disagrees"):
                verify.validate_log_contents(path, artifact, commands)

    def test_log_rejects_host_user_path(self):
        data = (
            reproduce.BUILD_LOG_HEADER
            + b"Compiling (/Users/example/project)\n"
            + reproduce.TEST_LOG_HEADER
            + b"ok\n"
        )
        commands = [
            {"output_sha256": reproduce.sha256_bytes(b"Compiling (/Users/example/project)\n")},
            {"output_sha256": reproduce.sha256_bytes(b"ok\n")},
        ]
        artifact = {"bytes": len(data), "sha256": reproduce.sha256_bytes(data)}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.log"
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "host user path"):
                verify.validate_log_contents(path, artifact, commands)


if __name__ == "__main__":
    unittest.main()
