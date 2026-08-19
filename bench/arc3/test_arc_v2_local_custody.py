#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("arc3_driver_arc_v2", HERE / "driver.py")
assert SPEC and SPEC.loader
DRIVER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DRIVER
SPEC.loader.exec_module(DRIVER)


class FakeVc33Game:
    """Provider-free official-feedback-shaped fake that wins after three actions."""

    def __init__(self) -> None:
        self.turn = 0
        self.closed = False
        self._observation = self._make_observation()

    def _make_observation(self) -> DRIVER.Observation:
        won = self.turn == 3
        return DRIVER.Observation(
            game_id="vc33",
            state="WIN" if won else "NOT_FINISHED",
            levels_completed=self.turn,
            win_levels=7,
            available_actions=() if won else ("ACTION4",),
            public_state={
                "frame": [[self.turn, 33], [4, self.turn]],
                "full_reset": False,
                "fake_official_feedback": True,
            },
        )

    @property
    def observation(self) -> DRIVER.Observation:
        return self._observation

    def step(self, action: DRIVER.Action) -> DRIVER.Observation:
        if self.closed or action != DRIVER.Action("ACTION4", {}):
            raise DRIVER.GateError("fake game action drift")
        self.turn += 1
        self._observation = self._make_observation()
        return self._observation

    def close(self) -> None:
        self.closed = True


class FakeModel:
    def __init__(self, *, fail_after: int | None = None) -> None:
        self.calls = 0
        self.fail_after = fail_after
        self.closed = False

    def choose(self, observation, *, turn, history_path, advisory):
        del observation, turn, history_path, advisory
        if self.fail_after is not None and self.calls >= self.fail_after:
            raise DRIVER.GateError("simulated crash after durable action")
        self.calls += 1
        return DRIVER.Action("ACTION4", {})

    def close(self) -> None:
        self.closed = True


class FakeSkill:
    def __init__(self) -> None:
        self.invocations = 0
        self.last_input_sha256 = None

    def analyze(self, history_path: Path, expected_identity: tuple[int, int]) -> str:
        fd = os.open(history_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            DRIVER.owner_file_assertion(fd, expected_identity=expected_identity)
            blocks = []
            while True:
                block = os.read(fd, 65536)
                if not block:
                    break
                blocks.append(block)
        finally:
            os.close(fd)
        data = b"".join(blocks)
        self.last_input_sha256 = DRIVER.sha256_bytes(data)
        self.invocations += 1
        return "fake evidence-bound advice"


class ArcV2LocalCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_path = HERE / "arc-v2-local-custody-manifest.json"
        cls.manifest, cls.manifest_sha256 = DRIVER.verify_manifest(cls.manifest_path)
        cls.game_config = cls.manifest["games"][0]

    def _run_fake_arm(self, root: Path, arm: str):
        game = FakeVc33Game()
        model = FakeModel()
        skill = None if arm == "baseline" else FakeSkill()
        work = root / f"{arm}-temp"
        work.mkdir(mode=0o700)
        journal = root / f"{arm}.actions.jsonl"
        receipt = root / f"{arm}.terminal.json"
        row = DRIVER.run_arm(
            arm=arm,
            game_id="vc33",
            game_config=self.game_config,
            common_config=self.manifest["common_live_model_config"],
            treatment_config=self.manifest["treatment_only"],
            game=game,
            model=model,
            skill=skill,
            root=work,
            action_journal_path=journal,
            terminal_receipt_path=receipt,
            terminal_receipt_context={
                "experiment_id": self.manifest["experiment_id"],
                "manifest_sha256": self.manifest_sha256,
            },
        )
        return row, journal, receipt

    def _assert_hash_chain(self, journal: Path) -> list[dict]:
        records = [json.loads(line) for line in journal.read_text().splitlines()]
        previous = DRIVER.ARC_V2_GENESIS_HASH
        for sequence, record in enumerate(records):
            self.assertEqual(record["sequence"], sequence)
            self.assertEqual(record["previous_record_sha256"], previous)
            claimed = record.pop("record_sha256")
            self.assertEqual(claimed, DRIVER.sha256_bytes(DRIVER.canonical_bytes(record)))
            previous = claimed
            record["record_sha256"] = claimed
        return records

    def test_manifest_is_exact_single_vc33_pair_and_five_game_run_is_held(self) -> None:
        self.assertEqual(self.manifest["schema_version"], 10)
        self.assertEqual(self.manifest["suite"]["game_order"], ["vc33"])
        self.assertEqual(self.manifest["suite"]["pair_order"], ["baseline", "ember"])
        self.assertEqual(self.manifest["suite"]["pairs"], 1)
        self.assertEqual(len(self.manifest["games"]), 1)
        self.assertEqual(self.manifest["games"][0]["level_action_caps"][0], 35)
        self.assertEqual(self.manifest["hold_gate"]["full_five_game_rerun"], "HOLD")
        self.assertFalse(self.manifest["launch_gate"]["full_five_game_rerun_authorized"])

        for mutation in ("game", "count", "order"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                changed = json.loads(json.dumps(self.manifest))
                if mutation == "game":
                    changed["games"][0]["game_id"] = "ls20"
                elif mutation == "count":
                    changed["games"].append(json.loads(json.dumps(changed["games"][0])))
                else:
                    changed["suite"]["pair_order"] = ["ember", "baseline"]
                path = Path(directory) / "manifest.json"
                data = (json.dumps(changed, sort_keys=True, indent=2) + "\n").encode()
                path.write_bytes(data)
                path.with_suffix(".sha256").write_text(
                    f"{DRIVER.sha256_bytes(data)}  manifest.json\n", encoding="ascii"
                )
                with self.assertRaises(DRIVER.GateError):
                    DRIVER.verify_manifest(path)

    def test_crash_after_action_retains_fsynced_owner_only_chain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / "temp"
            work.mkdir(mode=0o700)
            journal = root / "baseline.actions.jsonl"
            receipt = root / "baseline.terminal.json"
            game = FakeVc33Game()
            model = FakeModel(fail_after=1)
            with self.assertRaisesRegex(DRIVER.GateError, "simulated crash"):
                DRIVER.run_arm(
                    arm="baseline", game_id="vc33", game_config=self.game_config,
                    common_config=self.manifest["common_live_model_config"],
                    treatment_config=self.manifest["treatment_only"],
                    game=game, model=model, skill=None, root=work,
                    action_journal_path=journal,
                    terminal_receipt_path=receipt,
                    terminal_receipt_context={
                        "experiment_id": self.manifest["experiment_id"],
                        "manifest_sha256": self.manifest_sha256,
                    },
                )
            self.assertTrue(game.closed)
            self.assertTrue(model.closed)
            self.assertFalse(receipt.exists())
            self.assertEqual(stat.S_IMODE(journal.stat().st_mode), 0o600)
            records = self._assert_hash_chain(journal)
            self.assertEqual([row["record_type"] for row in records], ["start", "action"])
            self.assertEqual(
                set(records[0]),
                {
                    "record_type", "arm", "game_id", "turn", "state",
                    "levels_completed", "start_observation", "sequence",
                    "previous_record_sha256", "record_sha256",
                },
            )
            self.assertEqual(
                set(records[1]),
                {
                    "record_type", "arm", "game_id", "turn", "state", "action",
                    "levels_completed", "before_feedback", "after_feedback", "sequence",
                    "previous_record_sha256", "record_sha256",
                },
            )
            self.assertEqual(records[1]["turn"], 1)
            self.assertEqual(records[1]["action"], {"name": "ACTION4", "data": {}})
            self.assertIn("before_feedback", records[1])
            self.assertIn("after_feedback", records[1])
            self.assertEqual(records[1]["levels_completed"], {"before": 0, "after": 1, "change": 1})
            with self.assertRaisesRegex(DRIVER.GateError, "already exists"):
                DRIVER.OwnerActionJournal(journal, arm="baseline", game_id="vc33")

    def test_two_fake_arms_write_exact_receipts_and_pair_arithmetic_without_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline, baseline_journal, baseline_receipt = self._run_fake_arm(root, "baseline")
            ember, ember_journal, ember_receipt = self._run_fake_arm(root, "ember")
            rows = [baseline, ember]
            for row, journal, receipt in (
                (baseline, baseline_journal, baseline_receipt),
                (ember, ember_journal, ember_receipt),
            ):
                self.assertEqual(stat.S_IMODE(journal.stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o600)
                records = self._assert_hash_chain(journal)
                self.assertEqual(len(records), row["actions"] + 1)
                self.assertEqual(records[0]["record_type"], "start")
                self.assertTrue(all(item["record_type"] == "action" for item in records[1:]))
                terminal = json.loads(receipt.read_text())
                self.assertEqual(terminal["receipt_type"], "ARC_V2_ARM_TERMINAL_RECEIPT_V1")
                self.assertEqual(terminal["absolute_shadow_rhae"], row["shadow_rhae_fraction"])
                self.assertEqual(terminal["levels_completed"], 3)
                self.assertEqual(terminal["per_level_action_counts"], [1, 1, 1, 0, 0, 0, 0])
                self.assertEqual(sum(terminal["per_level_action_counts"]), terminal["total_actions_issued"])
                self.assertEqual(
                    set(terminal["wasted_actions"]),
                    {"aggregate", "revisited_states", "repeated_known_controls"},
                )
                self.assertEqual(terminal["termination_reason"], "GAME_WIN")
                self.assertEqual(terminal["action_journal"]["record_count"], 4)
                self.assertEqual(
                    terminal["action_journal"]["sha256"],
                    DRIVER.sha256_bytes(journal.read_bytes()),
                )
                self.assertFalse(terminal["platform_scorecard_retrieved"])

            receipt_paths = {"baseline": baseline_receipt, "ember": ember_receipt}
            receipt_hashes = {
                arm: DRIVER.sha256_bytes(receipt_paths[arm].read_bytes())
                for arm in DRIVER.ARC_V2_ARMS
            }
            paired = DRIVER.paired_terminal_receipt(
                rows,
                experiment_id=self.manifest["experiment_id"],
                manifest_sha256=self.manifest_sha256,
                receipt_paths=receipt_paths,
                receipt_sha256s=receipt_hashes,
            )
            expected_delta = ember["shadow_rhae_fraction"] - baseline["shadow_rhae_fraction"]
            self.assertEqual(
                paired["ember_minus_baseline_absolute_shadow_rhae_delta"], expected_delta
            )
            self.assertEqual([item["arm"] for item in paired["arms"]], ["baseline", "ember"])
            pair_path = root / "paired.terminal.json"
            DRIVER.write_owner_json(pair_path, paired, label="paired terminal receipt")
            self.assertEqual(stat.S_IMODE(pair_path.stat().st_mode), 0o600)

            private_artifacts = "\n".join(
                item.read_text() for item in (
                    baseline_journal, ember_journal, baseline_receipt,
                    ember_receipt, pair_path,
                )
            ).lower()
            for forbidden in (
                "model_prompt", "model prompt", "model_response", "model response",
                "oauth", "api_key", "arc_api_key", "authorization: bearer",
            ):
                self.assertNotIn(forbidden, private_artifacts)

    def test_authorization_binds_every_fresh_absolute_path_and_holds_full_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            failure = root / self.manifest["execution_freshness"]["private_failure_artifact_filename"]
            value = {
                "action_journal_paths": {
                    "baseline": str(root / "baseline.actions.jsonl"),
                    "ember": str(root / "ember.actions.jsonl"),
                },
                "arc_live_owner_authorized": True,
                "arc_v2_exactly_one_pair_owner_authorized": True,
                "direct_claude_failure_artifact_path": str(failure),
                "experiment_id": self.manifest["experiment_id"],
                "full_five_game_rerun_authorized": False,
                "manifest_sha256": self.manifest_sha256,
                "output_identity": self.manifest["execution_freshness"]["output_identity"],
                "output_path": str(root / "output.json"),
                "pair_count": 1,
                "pair_order": ["baseline", "ember"],
                "paired_receipt_path": str(root / "paired.receipt.json"),
                "selected_game_id": "vc33",
                "separate_arc_claude_lane_owner_authorized": True,
                "terminal_receipt_paths": {
                    "baseline": str(root / "baseline.receipt.json"),
                    "ember": str(root / "ember.receipt.json"),
                },
                "track1_fixed_199_terminal_completed": True,
                "track1_fixed_denominator": 199,
            }
            authorization = root / "authorization.json"
            authorization.write_text(json.dumps(value), encoding="utf-8")
            os.chmod(authorization, 0o600)
            accepted = DRIVER.authorization_gate(
                authorization,
                self.manifest,
                self.manifest_sha256,
                private_failure_artifact=failure,
            )
            self.assertEqual(accepted, value)
            value["pair_count"] = 2
            authorization.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(DRIVER.GateError):
                DRIVER.authorization_gate(
                    authorization,
                    self.manifest,
                    self.manifest_sha256,
                    private_failure_artifact=failure,
                )

    def test_fake_run_pair_executes_only_two_fresh_vc33_arms(self) -> None:
        class FakeLiveClaudeModel(FakeModel):
            def __init__(self, *args, **kwargs) -> None:
                del args, kwargs
                super().__init__()

        class FakeLiveArcadeGame(FakeVc33Game):
            instances = 0

            def __init__(self, game_id: str, api_key: str) -> None:
                self.assertion = (game_id, api_key)
                type(self).instances += 1
                super().__init__()

        class FakeLiveSkill(FakeSkill):
            def __init__(self, *args, **kwargs) -> None:
                del args, kwargs
                super().__init__()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            failure = root / self.manifest["execution_freshness"]["private_failure_artifact_filename"]
            output = root / "output.json"
            journals = {
                "baseline": root / "baseline.actions.jsonl",
                "ember": root / "ember.actions.jsonl",
            }
            receipts = {
                "baseline": root / "baseline.receipt.json",
                "ember": root / "ember.receipt.json",
            }
            paired_receipt = root / "paired.receipt.json"
            authorization_value = {
                "action_journal_paths": {key: str(value) for key, value in journals.items()},
                "arc_live_owner_authorized": True,
                "arc_v2_exactly_one_pair_owner_authorized": True,
                "direct_claude_failure_artifact_path": str(failure),
                "experiment_id": self.manifest["experiment_id"],
                "full_five_game_rerun_authorized": False,
                "manifest_sha256": self.manifest_sha256,
                "output_identity": self.manifest["execution_freshness"]["output_identity"],
                "output_path": str(output),
                "pair_count": 1,
                "pair_order": ["baseline", "ember"],
                "paired_receipt_path": str(paired_receipt),
                "selected_game_id": "vc33",
                "separate_arc_claude_lane_owner_authorized": True,
                "terminal_receipt_paths": {key: str(value) for key, value in receipts.items()},
                "track1_fixed_199_terminal_completed": True,
                "track1_fixed_denominator": 199,
            }
            authorization = root / "authorization.json"
            authorization.write_text(json.dumps(authorization_value), encoding="utf-8")
            os.chmod(authorization, 0o600)
            args = SimpleNamespace(
                authorization=authorization,
                direct_claude_failure_artifact=failure,
                output=output,
                ember_bundle=root / "fake-ember-bundle",
                azdaja=None,
                claude=root / "fake-claude",
                jcode=None,
                owner_home=root / "owner-home",
            )
            old_key = os.environ.get("ARC_API_KEY")
            os.environ["ARC_API_KEY"] = "fake-test-key-never-forwarded"
            try:
                with (
                    mock.patch.object(DRIVER, "provider_free_live_artifact_preflight", return_value={}),
                    mock.patch.object(DRIVER, "LiveClaudeModel", FakeLiveClaudeModel),
                    mock.patch.object(DRIVER, "LiveArcadeGame", FakeLiveArcadeGame),
                    mock.patch.object(DRIVER, "LiveAzdajaSkill", FakeLiveSkill),
                    mock.patch.object(DRIVER, "stage_ember_skill", return_value=root / "fake-ember"),
                    mock.patch.object(DRIVER, "platform_key", return_value="darwin-arm64"),
                ):
                    result = DRIVER.run_pair(
                        self.manifest, self.manifest_sha256, live=True, args=args
                    )
            finally:
                if old_key is None:
                    os.environ.pop("ARC_API_KEY", None)
                else:
                    os.environ["ARC_API_KEY"] = old_key
            self.assertEqual(FakeLiveArcadeGame.instances, 2)
            self.assertEqual(result["game_id"], "vc33")
            self.assertEqual(result["pair_order"], ["baseline", "ember"])
            self.assertEqual(result["pair_count"], 1)
            self.assertFalse(result["public_output_emitted"])
            self.assertTrue(all(path.exists() for path in (*journals.values(), *receipts.values())))
            self.assertTrue(paired_receipt.exists())
            self.assertFalse(failure.exists())
            DRIVER.write_output(output, result)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

    def test_pair_receipt_rejects_other_arm_count_or_game(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline, _, baseline_receipt = self._run_fake_arm(root, "baseline")
            with self.assertRaisesRegex(DRIVER.GateError, "baseline then ember"):
                DRIVER.paired_terminal_receipt(
                    [baseline],
                    experiment_id=self.manifest["experiment_id"],
                    manifest_sha256=self.manifest_sha256,
                    receipt_paths={"baseline": baseline_receipt},
                    receipt_sha256s={"baseline": DRIVER.sha256_bytes(baseline_receipt.read_bytes())},
                )


if __name__ == "__main__":
    unittest.main()
