import os
import json
import inspect
import re
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

import run


class DeltaRunnerContractTests(unittest.TestCase):
    def test_fixture_is_large_compact_clear_and_exact(self):
        validated = run.FIXTURE.validate()
        self.assertGreater(validated["context_bytes"], 1_000_000)
        self.assertEqual(validated["total_records"], 306)
        self.assertEqual(validated["selected_records"], 64)
        self.assertEqual(validated["unique_decision_evidence"], 64)
        self.assertEqual(validated["expected_answer"], 42)
        self.assertLess(validated["compact_evidence_bytes"], 65_536)

    def test_primary_uncached_formula_is_exact(self):
        usage = {
            "input": 100,
            "output": 7,
            "reasoning": 3,
            "cache": {"read": 40, "write": 5},
        }
        self.assertEqual(run.usage_uncached_total(usage), 75)
        self.assertEqual(run.usage_gross_total(usage), 115)
        usage["cache"]["read"] = 101
        with self.assertRaises(ValueError):
            run.usage_uncached_total(usage)
        self.assertEqual(run.integer_delta(10, 7), 3)
        self.assertIsNone(run.integer_delta(None, 7))

    def test_opencode_usage_normalizes_fresh_and_cached_input(self):
        raw = (
            json.dumps({"type": "text", "part": {"type": "text", "text": "Answer: 149"}})
            + "\n"
            + json.dumps({
                "type": "step_finish",
                "part": {
                    "type": "step-finish",
                    "reason": "stop",
                    "cost": 0,
                    "tokens": {
                        "input": 10,
                        "output": 7,
                        "reasoning": 3,
                        "cache": {"read": 40, "write": 5},
                    },
                },
            })
        ).encode()
        answer, usage = run.parse_opencode(raw)
        self.assertEqual(answer, 149)
        self.assertEqual(usage["input"], 50)
        self.assertEqual(usage["cache"]["read"], 40)
        self.assertEqual(run.usage_uncached_total(usage), 25)
        self.assertEqual(run.usage_gross_total(usage), 65)

    def test_candidate_cell_has_one_pinned_semantic_call(self):
        for model in ("gpt-5.6-luna", "openai/gpt-5.6-luna"):
            cell = run.candidate_cell(model)
            self.assertEqual(cell.count("llm_batch("), 1)
            self.assertIn("workers=6", cell)
            self.assertIn(f'model="{model}"', cell)
            self.assertEqual(cell.count("FINAL("), 1)
            self.assertIn('FINAL("Answer: " + str(ham))', cell)

    def test_followup_launches_only_the_direct_candidate_driver(self):
        invoke_source = inspect.getsource(run.invoke_candidate_direct)
        main_source = inspect.getsource(run.main)
        self.assertIn('command = [str(work / "azdaja-evaluate")]', invoke_source)
        self.assertNotIn("CODEX", invoke_source)
        self.assertNotIn("OPENCODE", invoke_source)
        self.assertIn("pool.submit(invoke_candidate_direct, campaign, harness)", main_source)
        self.assertNotIn("pool.submit(invoke,", main_source)

    def test_driver_is_owner_executable_and_one_lifecycle(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            work = root / "work"
            work.mkdir(mode=0o700)
            home = root / "home"
            xdg = root / "xdg"
            binary = home / ".agents/skills/azdaja/azdaja"
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"fake")
            binary.chmod(0o500)
            env = {"HOME": str(home), "XDG_CONFIG_HOME": str(xdg)}
            run.write_candidate_driver(work, env, "codex")
            driver = work / "azdaja-evaluate"
            text = driver.read_text()
            self.assertEqual(stat.S_IMODE(driver.stat().st_mode), 0o500)
            for command in (
                '"$AZDAJA" start',
                '"$AZDAJA" load "$sid"',
                '"$AZDAJA" exec "$sid"',
                '"$AZDAJA" final "$sid"',
                '"$AZDAJA" kill "$sid"',
            ):
                self.assertEqual(text.count(command), 1)
            self.assertEqual(text.count("llm_batch("), 1)
            self.assertIn(f"AZDAJA={binary}", text)
            self.assertEqual(driver.stat().st_uid, os.getuid())

    def test_candidate_driver_completes_with_one_fake_structured_provider_call(self):
        labels = "".join("H" if label else "S" for _, label in run.FIXTURE.records() if label is not None)
        self.assertEqual(len(labels), 64)
        with tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR")) as temporary:
            campaign = Path(temporary)
            try:
                for harness in ("codex", "opencode"):
                    work, env, trace = run.prepare_arm(campaign, harness, "candidate")
                    fake_dir = work.parent / "fake-provider"
                    fake_dir.mkdir(mode=0o700)
                    fake = fake_dir / harness
                    payload = json.dumps({"labels": labels})
                    if harness == "codex":
                        body = (
                            "#!/bin/sh\n"
                            f"printf '%s\\n' {run.shlex.quote(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': payload}}))}\n"
                            f"printf '%s\\n' {run.shlex.quote(json.dumps({'type': 'turn.completed', 'usage': {'input_tokens': 50, 'cached_input_tokens': 40, 'cache_write_input_tokens': 5, 'output_tokens': 7, 'reasoning_output_tokens': 3}}))}\n"
                        )
                        command = f'{fake} --json {{isolated_env}} -C {{sandbox_dir}}'
                        config = Path(env["HOME"]) / ".agents/skills/azdaja/config.toml"
                    else:
                        body = (
                            "#!/bin/sh\n"
                            f"printf '%s\\n' {run.shlex.quote(json.dumps({'type': 'text', 'part': {'type': 'text', 'text': payload}}))}\n"
                            f"printf '%s\\n' {run.shlex.quote(json.dumps({'type': 'step_finish', 'part': {'type': 'step-finish', 'reason': 'stop', 'cost': 0, 'tokens': {'input': 10, 'output': 7, 'reasoning': 3, 'cache': {'read': 40, 'write': 5}}}}))}\n"
                        )
                        command = f'{fake} --format json --model {{model}}'
                        config = Path(env["XDG_CONFIG_HOME"]) / "opencode/skills/azdaja/config.toml"
                    fake.write_text(body)
                    fake.chmod(0o500)
                    text = config.read_text()
                    text = re.sub(r'^sub_llm_cmd = .*$', f'sub_llm_cmd = {json.dumps(command)}', text, count=1, flags=re.MULTILINE)
                    config.chmod(0o600)
                    config.write_text(text)
                    completed = subprocess.run(
                        [str(work / "azdaja-evaluate")],
                        cwd=work,
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=30,
                        check=False,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertEqual(completed.stdout.strip(), "Answer: 42")
                    summary = run.trace_summary(trace)
                    self.assertEqual(summary["attempts"], 1)
                    self.assertEqual(summary["successes"], 1)
                    self.assertEqual(summary["failures"], 0)
                    self.assertEqual(summary["measured_uncached_tokens"], 25)
            finally:
                shutil.rmtree(campaign, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
