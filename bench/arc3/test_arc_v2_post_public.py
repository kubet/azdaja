#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
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
RUNNER_SPEC = importlib.util.spec_from_file_location("arc_v2_post_public_test_runner", HERE / "arc_v2_post_public.py")
assert RUNNER_SPEC and RUNNER_SPEC.loader
RUNNER = importlib.util.module_from_spec(RUNNER_SPEC)
sys.modules[RUNNER_SPEC.name] = RUNNER
RUNNER_SPEC.loader.exec_module(RUNNER)
BINDER_SPEC = importlib.util.spec_from_file_location("arc_v2_post_public_test_binder", HERE / "bind_arc_v2_post_public.py")
assert BINDER_SPEC and BINDER_SPEC.loader
BINDER = importlib.util.module_from_spec(BINDER_SPEC)
sys.modules[BINDER_SPEC.name] = BINDER
BINDER_SPEC.loader.exec_module(BINDER)


class FakeGame:
    calls: list[str] = []
    sentinel: Path | None = None

    def __init__(self, game_id: str, api_key: str) -> None:
        if api_key != "fake-test-key-never-forwarded":
            raise RUNNER.GateError("fake API key drift")
        if self.sentinel is None or not self.sentinel.exists():
            raise RUNNER.GateError("game constructed before exactly-once sentinel")
        type(self).calls.append(game_id)
        self.game_id = game_id
        self.turn = 0
        self.closed = False
        self._observation = self._make_observation()

    def _make_observation(self):
        won = self.turn == 3
        return RUNNER.CORE.Observation(
            game_id=self.game_id,
            state="WIN" if won else "NOT_FINISHED",
            levels_completed=self.turn,
            win_levels=3,
            available_actions=() if won else ("ACTION4",),
            public_state={
                "frame": [[self.turn, len(self.game_id)], [4, self.turn]],
                "full_reset": False,
                "fake_official_feedback": True,
            },
        )

    @property
    def observation(self):
        return self._observation

    def step(self, action):
        if self.closed or action != RUNNER.CORE.Action("ACTION4", {}):
            raise RUNNER.GateError("fake game action drift")
        self.turn += 1
        self._observation = self._make_observation()
        return self._observation

    def close(self) -> None:
        self.closed = True


class FakeModel:
    calls_at_construction = 0
    sentinel: Path | None = None

    def __init__(self, *args, **kwargs) -> None:
        del args, kwargs
        if self.sentinel is None or not self.sentinel.exists():
            raise RUNNER.GateError("model constructed before exactly-once sentinel")
        type(self).calls_at_construction += 1
        self.calls = 0
        self.closed = False

    def choose(self, observation, *, turn, history_path, advisory):
        del observation, turn, history_path, advisory
        self.calls += 1
        return RUNNER.CORE.Action("ACTION4", {})

    def close(self) -> None:
        self.closed = True


class FakeSkill:
    def __init__(self, *args, **kwargs) -> None:
        del args, kwargs
        self.invocations = 0
        self.last_input_sha256 = None

    def analyze(self, history_path: Path, expected_identity: tuple[int, int]) -> str:
        fd = os.open(history_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            RUNNER.CORE.owner_file_assertion(fd, expected_identity=expected_identity)
            blocks = []
            while True:
                block = os.read(fd, 65536)
                if not block:
                    break
                blocks.append(block)
        finally:
            os.close(fd)
        self.last_input_sha256 = RUNNER.sha256_bytes(b"".join(blocks))
        self.invocations += 1
        return "fake evidence-bound advice"


class PostPublicArcV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_path = HERE / "arc-v2-five-postlaunch-manifest.json"
        cls.manifest, cls.manifest_sha256 = RUNNER.verify_manifest(cls.manifest_path)
        cls.now = dt.datetime(2026, 8, 20, 12, 0, 0, tzinfo=dt.timezone.utc)

    def _metadata(self, *, public: bool = True) -> dict:
        return {
            "id": 123456,
            "node_id": "R_kgDOFakeAzdaja",
            "full_name": "kubet/azdaja",
            "private": not public,
            "visibility": "public" if public else "private",
            "html_url": "https://github.com/kubet/azdaja",
            "default_branch": "main",
            "archived": False,
            "disabled": False,
            "updated_at": "2026-08-20T11:59:30Z",
        }

    def _bind(self, root: Path, *, now: dt.datetime | None = None):
        metadata = root / "github-metadata.json"
        metadata.write_text(json.dumps(self._metadata()), encoding="utf-8")
        os.chmod(metadata, 0o600)
        visibility = root / self.manifest["execution_freshness"]["visibility_receipt_filename"]
        private = root / "private"
        private.mkdir(mode=0o700)
        authorization = private / self.manifest["execution_freshness"]["authorization_filename"]
        _, approval = BINDER.bind(
            manifest_path=self.manifest_path,
            github_metadata_path=metadata,
            visibility_receipt_path=visibility,
            authorization_path=authorization,
            artifact_root=root,
            owner_go=RUNNER.OWNER_GO,
            now=now or self.now,
        )
        return metadata, visibility, authorization, approval

    def _hash_chain(self, path: Path) -> list[dict]:
        records = [json.loads(line) for line in path.read_text().splitlines()]
        previous = RUNNER.CORE.ARC_V2_GENESIS_HASH
        for sequence, record in enumerate(records):
            self.assertEqual(record["sequence"], sequence)
            self.assertEqual(record["previous_record_sha256"], previous)
            claimed = record.pop("record_sha256")
            self.assertEqual(claimed, RUNNER.sha256_bytes(RUNNER.canonical_bytes(record)))
            previous = claimed
            record["record_sha256"] = claimed
        return records

    def test_manifest_freezes_exact_five_game_and_ten_arm_order(self) -> None:
        self.assertEqual(self.manifest["schema_version"], 11)
        self.assertEqual(self.manifest["suite"]["game_order"], list(RUNNER.GAMES))
        self.assertEqual(self.manifest["suite"]["pair_order"], ["baseline", "ember"])
        self.assertEqual(self.manifest["suite"]["pairs"], 5)
        self.assertEqual(len(self.manifest["games"]), 5)
        self.assertTrue(all(game["dry_run_stub"] is False for game in self.manifest["games"]))
        self.assertFalse(self.manifest["custody_contract"]["platform_scorecard_retrieval"])
        self.assertFalse(self.manifest["execution_freshness"]["reuse_completed_vc33_smoke_artifacts"])
        expected = [(game, arm) for game in RUNNER.GAMES for arm in RUNNER.ARMS]
        self.assertEqual(len(expected), 10)
        for game in self.manifest["games"]:
            baselines = game["human_level_baseline_actions"]
            self.assertEqual(game["level_action_caps"], [5 * item for item in baselines])
            self.assertEqual(game["max_actions"], sum(game["level_action_caps"]))

    def test_private_metadata_or_missing_owner_go_cannot_create_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = root / "metadata.json"
            metadata.write_text(json.dumps(self._metadata(public=False)), encoding="utf-8")
            os.chmod(metadata, 0o600)
            visibility = root / self.manifest["execution_freshness"]["visibility_receipt_filename"]
            authorization = root / self.manifest["execution_freshness"]["authorization_filename"]
            with self.assertRaisesRegex(BINDER.GateError, "does not prove"):
                BINDER.bind(
                    manifest_path=self.manifest_path,
                    github_metadata_path=metadata,
                    visibility_receipt_path=visibility,
                    authorization_path=authorization,
                    artifact_root=root,
                    owner_go=RUNNER.OWNER_GO,
                    now=self.now,
                )
            self.assertFalse(visibility.exists())
            self.assertFalse(authorization.exists())
            metadata.write_text(json.dumps(self._metadata(public=True)), encoding="utf-8")
            os.chmod(metadata, 0o600)
            with self.assertRaisesRegex(BINDER.GateError, "owner GO"):
                BINDER.bind(
                    manifest_path=self.manifest_path,
                    github_metadata_path=metadata,
                    visibility_receipt_path=visibility,
                    authorization_path=authorization,
                    artifact_root=root,
                    owner_go="NOT_GO",
                    now=self.now,
                )

    def test_authorization_binds_fresh_public_receipt_and_every_fresh_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, visibility, authorization, approval = self._bind(root)
            self.assertEqual(stat.S_IMODE(visibility.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(authorization.stat().st_mode), 0o600)
            accepted, receipt, _ = RUNNER.authorization_gate(
                authorization, visibility, self.manifest, self.manifest_sha256,
                output_path=Path(approval["output_path"]),
                failure_artifact_path=Path(approval["direct_claude_failure_artifact_path"]),
                now=self.now,
            )
            self.assertEqual(accepted, approval)
            self.assertEqual(receipt["repository_visibility"], "PUBLIC")
            self.assertFalse(receipt["private"])
            all_paths = []
            for game_id in RUNNER.GAMES:
                for arm in RUNNER.ARMS:
                    all_paths += [
                        approval["action_journal_paths"][game_id][arm],
                        approval["terminal_receipt_paths"][game_id][arm],
                    ]
                all_paths.append(approval["paired_receipt_paths"][game_id])
            all_paths += [
                approval["output_path"], approval["direct_claude_failure_artifact_path"],
                approval["execution_sentinel_path"], approval["suite_terminal_receipt_path"],
            ]
            self.assertEqual(len(all_paths), 29)
            self.assertEqual(len(set(all_paths)), 29)
            Path(approval["output_path"]).write_text("collision", encoding="utf-8")
            with self.assertRaisesRegex(RUNNER.GateError, "absolute and fresh"):
                RUNNER.authorization_gate(
                    authorization, visibility, self.manifest, self.manifest_sha256,
                    output_path=Path(approval["output_path"]),
                    failure_artifact_path=Path(approval["direct_claude_failure_artifact_path"]),
                    now=self.now,
                )

    def test_stale_or_digest_changed_public_receipt_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, visibility, authorization, approval = self._bind(root, now=self.now)
            with self.assertRaisesRegex(RUNNER.GateError, "stale"):
                RUNNER.authorization_gate(
                    authorization, visibility, self.manifest, self.manifest_sha256,
                    output_path=Path(approval["output_path"]),
                    failure_artifact_path=Path(approval["direct_claude_failure_artifact_path"]),
                    now=self.now + dt.timedelta(seconds=601),
                )
            value = json.loads(visibility.read_text())
            value["repository_visibility"] = "PRIVATE"
            visibility.write_text(json.dumps(value), encoding="utf-8")
            os.chmod(visibility, 0o600)
            with self.assertRaisesRegex(RUNNER.GateError, "digest differs"):
                RUNNER.authorization_gate(
                    authorization, visibility, self.manifest, self.manifest_sha256,
                    output_path=Path(approval["output_path"]),
                    failure_artifact_path=Path(approval["direct_claude_failure_artifact_path"]),
                    now=self.now,
                )

    def test_live_missing_post_public_proof_refuses_before_artifact_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = SimpleNamespace(
                manifest=self.manifest_path,
                authorization=None,
                visibility_receipt=None,
                output=root / "never-created.output.json",
                direct_claude_failure_artifact=root / "never-created.failure.private",
                claude=root / "never-called-claude",
                ember_bundle=root / "never-read-ember",
                owner_home=root,
            )
            with mock.patch.object(RUNNER.CORE, "provider_free_live_artifact_preflight") as preflight:
                with self.assertRaisesRegex(RUNNER.GateError, "requires owner approval"):
                    RUNNER.execute_live(args, now=self.now)
            preflight.assert_not_called()
            self.assertFalse(args.output.exists())

    def test_fake_full_run_is_exactly_once_with_durable_local_custody(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, visibility, authorization, approval = self._bind(root)
            sentinel = Path(approval["execution_sentinel_path"])
            FakeGame.calls = []
            FakeGame.sentinel = sentinel
            FakeModel.calls_at_construction = 0
            FakeModel.sentinel = sentinel
            args = SimpleNamespace(
                manifest=self.manifest_path,
                authorization=authorization,
                visibility_receipt=visibility,
                output=Path(approval["output_path"]),
                direct_claude_failure_artifact=Path(approval["direct_claude_failure_artifact_path"]),
                claude=root / "fake-claude",
                ember_bundle=root / "fake-ember-bundle",
                owner_home=root / "owner-home",
            )
            preflight_calls = []
            old_key = os.environ.get("ARC_API_KEY")
            os.environ["ARC_API_KEY"] = "fake-test-key-never-forwarded"
            try:
                with (
                    mock.patch.object(
                        RUNNER.CORE, "provider_free_live_artifact_preflight",
                        side_effect=lambda *a, **k: preflight_calls.append((a, k)) or {},
                    ),
                    mock.patch.object(RUNNER.CORE, "LiveClaudeModel", FakeModel),
                    mock.patch.object(RUNNER.CORE, "LiveArcadeGame", FakeGame),
                    mock.patch.object(RUNNER.CORE, "LiveAzdajaSkill", FakeSkill),
                    mock.patch.object(RUNNER.CORE, "stage_ember_skill", return_value=root / "fake-ember"),
                    mock.patch.object(RUNNER.CORE, "platform_key", return_value="darwin-arm64"),
                ):
                    result = RUNNER.execute_live(args, now=self.now)
                    game_calls_after_first = list(FakeGame.calls)
                    model_calls_after_first = FakeModel.calls_at_construction
                    with self.assertRaisesRegex(RUNNER.GateError, "absolute and fresh"):
                        RUNNER.execute_live(args, now=self.now)
            finally:
                if old_key is None:
                    os.environ.pop("ARC_API_KEY", None)
                else:
                    os.environ["ARC_API_KEY"] = old_key
            self.assertEqual(len(preflight_calls), 1)
            self.assertEqual(game_calls_after_first, [game for game in RUNNER.GAMES for _ in RUNNER.ARMS])
            self.assertEqual(FakeGame.calls, game_calls_after_first)
            self.assertEqual(model_calls_after_first, 10)
            self.assertEqual(FakeModel.calls_at_construction, 10)
            self.assertEqual(result["game_order"], list(RUNNER.GAMES))
            self.assertEqual(result["pair_order_per_game"], list(RUNNER.ARMS))
            self.assertEqual(result["arm_count"], 10)
            self.assertFalse(result["platform_scorecard_retrieved"])
            self.assertEqual(stat.S_IMODE(sentinel.stat().st_mode), 0o600)
            sentinel_value = json.loads(sentinel.read_text())
            self.assertEqual(sentinel_value["arc_game_or_model_calls_before_sentinel"], 0)
            self.assertFalse(sentinel_value["rerun_permitted"])
            self.assertEqual(stat.S_IMODE(Path(approval["output_path"]).stat().st_mode), 0o600)

            for game_id in RUNNER.GAMES:
                pair = json.loads(Path(approval["paired_receipt_paths"][game_id]).read_text())
                self.assertEqual([item["arm"] for item in pair["arms"]], ["baseline", "ember"])
                self.assertFalse(pair["platform_scorecard_retrieved"])
                for arm in RUNNER.ARMS:
                    journal = Path(approval["action_journal_paths"][game_id][arm])
                    terminal_path = Path(approval["terminal_receipt_paths"][game_id][arm])
                    self.assertEqual(stat.S_IMODE(journal.stat().st_mode), 0o600)
                    self.assertEqual(stat.S_IMODE(terminal_path.stat().st_mode), 0o600)
                    records = self._hash_chain(journal)
                    self.assertEqual([record["record_type"] for record in records], ["start", "action", "action", "action"])
                    self.assertTrue(all("before_feedback" in record and "after_feedback" in record for record in records[1:]))
                    terminal = json.loads(terminal_path.read_text())
                    self.assertEqual(terminal["game_id"], game_id)
                    self.assertEqual(terminal["arm"], arm)
                    self.assertEqual(terminal["levels_completed"], 3)
                    self.assertEqual(sum(terminal["per_level_action_counts"]), terminal["total_actions_issued"])
                    self.assertEqual(
                        set(terminal["wasted_actions"]),
                        {"aggregate", "revisited_states", "repeated_known_controls"},
                    )
                    self.assertEqual(terminal["action_journal"]["record_count"], 4)
                    self.assertEqual(
                        terminal["action_journal"]["sha256"],
                        RUNNER.sha256_bytes(journal.read_bytes()),
                    )
                    self.assertFalse(terminal["platform_scorecard_retrieved"])
            suite = json.loads(Path(approval["suite_terminal_receipt_path"]).read_text())
            self.assertEqual([item["game_id"] for item in suite["pairs"]], list(RUNNER.GAMES))
            self.assertEqual(suite["termination_reason"], "ALL_FIVE_ORDERED_PAIRS_TERMINAL")
            self.assertFalse(suite["platform_scorecard_retrieved"])


if __name__ == "__main__":
    unittest.main()
