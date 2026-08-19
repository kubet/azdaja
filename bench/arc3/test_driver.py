#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("arc3_driver", HERE / "driver.py")
assert SPEC and SPEC.loader
DRIVER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DRIVER
SPEC.loader.exec_module(DRIVER)


class DriverUnitTests(unittest.TestCase):
    def test_frozen_manifest_and_exact_five_x_caps(self) -> None:
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-manifest.json")
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(len(manifest["games"]), 5)
        for game in manifest["games"]:
            expected = [5 * item for item in game["human_level_baseline_actions"]]
            self.assertEqual(game["level_action_caps"], expected)
            self.assertEqual(game["max_actions"], sum(expected))

    def test_authorized_v2_preserves_v1_schedule_and_changes_only_gates(self) -> None:
        frozen, _ = DRIVER.verify_manifest(HERE / "mini-pilot-manifest.json")
        authorized, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v2.json")
        expected = json.loads(json.dumps(frozen))
        expected["schema_version"] = 2
        expected["status"] = "FROZEN_AUTHORIZED_FOR_LIVE_MINI"
        expected["launch_gate"]["track1_fixed_199_in_flight"] = True
        expected["launch_gate"]["arc_live_owner_authorized"] = True
        self.assertEqual(authorized, expected)
        self.assertFalse(authorized["launch_gate"]["track1_full_199_confirmed"])
        receipt = {
            "experiment_id": authorized["experiment_id"],
            "manifest_sha256": digest,
            "track1_fixed_199_in_flight": True,
            "arc_live_owner_authorized": True,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authorization.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            os.chmod(path, 0o600)
            DRIVER.authorization_gate(path, authorized, digest)

    def test_cap_drift_is_rejected(self) -> None:
        source = json.loads((HERE / "mini-pilot-manifest.json").read_text())
        source["games"][0]["level_action_caps"][0] += 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            data = (json.dumps(source, sort_keys=True, indent=2) + "\n").encode()
            path.write_bytes(data)
            path.with_suffix(".sha256").write_text(
                f"{DRIVER.sha256_bytes(data)}  manifest.json\n", encoding="ascii"
            )
            with self.assertRaisesRegex(DRIVER.GateError, "action cap"):
                DRIVER.verify_manifest(path)

    def test_shadow_rhae_uses_weighting_square_and_cap(self) -> None:
        self.assertAlmostEqual(DRIVER.shadow_rhae([10, 20], [10]), 1.0 / 3.0)
        self.assertAlmostEqual(DRIVER.shadow_rhae([10, 20], [1]), 1.15 / 3.0)
        self.assertAlmostEqual(
            DRIVER.shadow_rhae([10, 20], [20, 40]),
            (1 * 0.25 + 2 * 0.25) / 3,
        )

    def test_owner_history_and_stub_skill_are_file_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = DRIVER.OwnerHistory(root)
            try:
                history.append({"record_type": "start"})
                history.append({"record_type": "turn", "turn": 1})
                history.append({"record_type": "turn", "turn": 2})
                mode = stat.S_IMODE(history.path.stat().st_mode)
                self.assertEqual(mode, 0o600)
                skill = DRIVER.StubAzdajaSkill()
                self.assertEqual(skill.analyze(history.path, history.identity), "prefer ACTION4")
                self.assertEqual(skill.invocations, 1)
                self.assertEqual(skill.last_input_sha256, history.digest()[0])
            finally:
                history.close()

    def test_frozen_live_authorization_fails_closed(self) -> None:
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-manifest.json")
        receipt = {
            "experiment_id": manifest["experiment_id"],
            "manifest_sha256": digest,
            "track1_full_199_confirmed": True,
            "arc_live_owner_authorized": True,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authorization.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            os.chmod(path, 0o600)
            with self.assertRaisesRegex(DRIVER.GateError, "not owner-authorized"):
                DRIVER.authorization_gate(path, manifest, digest)

    def test_safe_env_aligns_jcode_managed_skill_home(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            env = DRIVER.safe_env(home, reasoning="low")
            self.assertEqual(Path(env["JCODE_HOME"]), home / ".jcode")

    def test_artifact_preflight_rejects_jcode_before_install(self) -> None:
        manifest, _ = DRIVER.verify_manifest(HERE / "mini-pilot-manifest.json")
        with tempfile.TemporaryDirectory() as directory:
            bad_jcode = Path(directory) / "jcode"
            bad_jcode.write_bytes(b"wrong-jcode")
            with self.assertRaisesRegex(DRIVER.GateError, "Jcode binary digest mismatch"):
                DRIVER.provider_free_live_artifact_preflight(
                    bad_jcode,
                    Path(directory) / "missing-azdaja",
                    manifest,
                )

    def test_materialized_managed_skill_validation(self) -> None:
        manifest, _ = DRIVER.verify_manifest(HERE / "mini-pilot-manifest.json")
        treatment = json.loads(json.dumps(manifest["treatment_only"]))
        with tempfile.TemporaryDirectory() as directory:
            skill_root = Path(directory) / ".jcode" / "skills" / "azdaja"
            skill_root.mkdir(parents=True)
            staged_binary = skill_root / "azdaja"
            staged_binary.write_bytes(b"pinned-azdaja-binary")
            digest = DRIVER.sha256_bytes(staged_binary.read_bytes())
            treatment["azdaja_binary_sha256"] = {
                "darwin-arm64": digest,
                "linux-x86_64": digest,
            }
            source_skill = (HERE.parents[1] / "assets" / "SKILL.md").read_text()
            installed_skill = (
                source_skill
                .replace("{{VERSION}}", treatment["azdaja_release"][1:])
                .replace("{{BIN}}", DRIVER.shell_quote(staged_binary))
            )
            (skill_root / "SKILL.md").write_text(installed_skill)
            (skill_root / "config.toml").write_bytes(
                (HERE.parents[1] / "assets" / "config.toml").read_bytes()
            )
            (skill_root / ".azdaja-managed").write_text("{}")
            DRIVER.validate_managed_skill(skill_root, treatment)


    def test_v3_is_full_completion_bound_claude_lane_and_preserves_games(self) -> None:
        previous, _ = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v2.json")
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v3.json")
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["games"], previous["games"])
        self.assertEqual(manifest["suite"]["game_order"], ["ls20", "ft09", "vc33", "ar25", "wa30"])
        self.assertEqual(manifest["suite"]["pair_order"], ["baseline", "ember"])
        self.assertEqual(manifest["privacy_contract"]["platform_pseudonym"], "Ember")
        self.assertTrue(manifest["launch_gate"]["track1_fixed_199_terminal_completed"])
        self.assertEqual(manifest["launch_gate"]["track1_fixed_denominator"], 199)
        self.assertTrue(manifest["launch_gate"]["track1_full_199_confirmed"])
        self.assertEqual(manifest["common_live_model_config"]["provider"], "claude")
        self.assertEqual(manifest["common_live_model_config"]["model"], "claude-sonnet-5")
        self.assertEqual(manifest["treatment_only"]["root_model"], "claude-sonnet-5")
        self.assertEqual(manifest["treatment_only"]["sub_model"], "claude-sonnet-5")
        evidence = manifest["owner_only_evidence"]
        self.assertFalse(evidence["known_bridge_socket_fast_path_provider_revalidation"])
        self.assertFalse(evidence["known_bridge_gap_fix_claimed"])

    def test_v3_authorization_binds_terminal_completion_and_owner_lane(self) -> None:
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v3.json")
        receipt = {
            "arc_live_owner_authorized": True,
            "claude_lane_owner_mandated": True,
            "experiment_id": manifest["experiment_id"],
            "manifest_sha256": digest,
            "track1_fixed_199_terminal_completed": True,
            "track1_fixed_denominator": 199,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authorization.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            os.chmod(path, 0o600)
            DRIVER.authorization_gate(path, manifest, digest)
            receipt["track1_fixed_denominator"] = 198
            path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(DRIVER.GateError, "not owner-authorized"):
                DRIVER.authorization_gate(path, manifest, digest)

    def test_v3_public_result_is_only_ember_per_game_delta(self) -> None:
        game_ids = ["ls20", "ft09", "vc33", "ar25", "wa30"]
        rows = []
        for index, game_id in enumerate(game_ids):
            rows.extend([
                {"arm": "baseline", "game_id": game_id, "common_model_config_sha256": "same", "action_cap": 10, "shadow_rhae_fraction": 0.25},
                {"arm": "ember", "game_id": game_id, "common_model_config_sha256": "same", "action_cap": 10, "shadow_rhae_fraction": 0.5 + index / 100},
            ])
        result = DRIVER.public_ember_result(rows, game_ids)
        self.assertEqual(set(result), {"identity", "arms", "games"})
        self.assertEqual(result["identity"], "Ember")
        self.assertEqual(result["arms"], ["baseline", "ember"])
        self.assertEqual([row["game_id"] for row in result["games"]], game_ids)
        self.assertTrue(all(set(row) == {"game_id", "ember_minus_baseline_rhae_delta"} for row in result["games"]))
        self.assertTrue(all(isinstance(row["ember_minus_baseline_rhae_delta"], float) for row in result["games"]))
        public = json.dumps(result, sort_keys=True).lower()
        for forbidden in ("azdaja", "repository", "treatment", "sha256", "path", "prompt", "response", "trace", "log", "gold", "oauth", "secret"):
            self.assertNotIn(forbidden, public)
        self.assertNotRegex(public, r"[0-9a-f]{64}")
        self.assertNotIn("/", public)

    def test_v3_safe_env_is_fresh_and_does_not_forward_arc_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            old = os.environ.get("ARC_API_KEY")
            os.environ["ARC_API_KEY"] = "must-not-be-forwarded"
            try:
                first = DRIVER.safe_env(Path(directory) / "arm-a", reasoning="low")
                second = DRIVER.safe_env(Path(directory) / "arm-b", reasoning="low")
            finally:
                if old is None:
                    os.environ.pop("ARC_API_KEY", None)
                else:
                    os.environ["ARC_API_KEY"] = old
            self.assertNotIn("ARC_API_KEY", first)
            for key in ("HOME", "JCODE_HOME", "JCODE_RUNTIME_DIR", "AZDAJA_HOME"):
                self.assertNotEqual(first[key], second[key])
            self.assertFalse(DRIVER.stop_ember_bridge(first))
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                DRIVER.parse_args(["live", "--arc-api-key", "forbidden"])

    def test_v3_owner_bundle_is_manually_staged_without_provider_execution(self) -> None:
        manifest, _ = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v3.json")
        treatment = json.loads(json.dumps(manifest["treatment_only"]))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle"
            bundle.mkdir()
            (bundle / "ember").write_bytes(b"owner-binary")
            (bundle / "SKILL.md").write_text("version {{VERSION}} binary {{BIN}}", encoding="utf-8")
            (bundle / "config.toml").write_text(
                'sub_llm_cmd="jcode-api"\ndefault_model="claude-sonnet-5"\njcode_provider="claude"\njcode_reasoning="low"\n',
                encoding="utf-8",
            )
            treatment["binary_sha256_by_platform"] = {DRIVER.platform_key(): DRIVER.sha256_bytes(b"owner-binary")}
            treatment["source_bundle_components_sha256"] = {
                name: DRIVER.sha256_bytes((bundle / name).read_bytes())
                for name in ("SKILL.md", "config.toml")
            }
            env = DRIVER.safe_env(root / "home", reasoning="low")
            Path(env["HOME"]).mkdir()
            staged = DRIVER.stage_ember_skill(bundle, env, treatment)
            self.assertTrue(staged.is_file())
            self.assertEqual(stat.S_IMODE(staged.stat().st_mode), 0o700)
            self.assertEqual(Path(env["AZDAJA_CONFIG"]), staged.parent / "config.toml")
            rendered = (staged.parent / "SKILL.md").read_text()
            self.assertNotIn("{{VERSION}}", rendered)
            self.assertNotIn("{{BIN}}", rendered)

    def test_output_is_owner_only_and_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            DRIVER.write_output(path, {"identity": "Ember", "arms": ["baseline", "ember"], "games": []})
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            with self.assertRaisesRegex(DRIVER.GateError, "output already exists"):
                DRIVER.write_output(path, {"identity": "Ember"})

    def test_ndjson_response_parser(self) -> None:
        text = '\n'.join([
            json.dumps({"type": "text_delta", "text": '{"action":'}),
            json.dumps({"type": "text_delta", "text": '"ACTION4","data":{}}'}),
        ])
        self.assertEqual(DRIVER.ndjson_response(text), '{"action":"ACTION4","data":{}}')

    def test_v4_direct_claude_manifest_is_fresh_and_separately_authorized(self) -> None:
        previous, _ = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v3.json")
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v4.json")
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["games"], previous["games"])
        self.assertEqual(manifest["suite"]["game_order"], ["ls20", "ft09", "vc33", "ar25", "wa30"])
        self.assertTrue(manifest["suite"]["fresh_game_instance_per_arm"])
        self.assertFalse(manifest["suite"]["reuse_prior_game_or_session"])
        self.assertEqual(manifest["common_live_model_config"]["provider"], "claude-code")
        self.assertEqual(manifest["common_live_model_config"]["model"], "sonnet")
        self.assertTrue(manifest["common_live_model_config"]["no_session_persistence"])
        self.assertEqual(manifest["owner_only_evidence"]["claude_v7_verdict"], "STOP_NO_FULL")
        self.assertTrue(manifest["owner_only_evidence"]["separate_arc_claude_lane_owner_authorized"])
        self.assertTrue(manifest["owner_only_evidence"]["bridge_helper_bypassed"])
        self.assertFalse(manifest["owner_only_evidence"]["helper_bug_persists"])
        self.assertFalse(manifest["execution_freshness"]["reuse_v3_game_session_output_or_runtime"])

    def test_direct_claude_model_choose_uses_input_without_duplicate_stdin(self) -> None:
        from unittest import mock
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "claude"
            binary.write_bytes(b"fake-claude")
            binary.chmod(0o700)
            config = {
                "claude_binary_sha256": DRIVER.sha256_bytes(binary.read_bytes()),
                "model": "sonnet",
            }
            failure_artifact = root / "retained.private"
            model = DRIVER.LiveClaudeModel(
                binary, config, root, root, DRIVER.safe_env(root / "home", reasoning="low"), failure_artifact
            )
            observation = DRIVER.Observation(
                game_id="ls20", state="NOT_FINISHED", levels_completed=0,
                win_levels=1, available_actions=("ACTION4",), public_state={"frame": []},
            )
            completed = __import__("subprocess").CompletedProcess(
                [], 0, stdout=b'{"action":"ACTION4","data":{}}\n', stderr=b""
            )
            with mock.patch.object(DRIVER.subprocess, "run", return_value=completed) as run:
                action = model.choose(observation, turn=1, history_path=root / "history", advisory=None)
            self.assertEqual(action, DRIVER.Action("ACTION4", {}))
            kwargs = run.call_args.kwargs
            self.assertIn("input", kwargs)
            self.assertNotIn("stdin", kwargs)
            command = run.call_args.args[0]
            self.assertEqual(command[command.index("--failure-artifact") + 1], str(failure_artifact))

    def test_direct_claude_model_choose_propagates_only_failure_enum(self) -> None:
        from unittest import mock
        categories = ("auth", "invalid_model", "cli_usage", "sandbox_permission", "rate_limit", "network", "other")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "claude"
            binary.write_bytes(b"fake-claude")
            binary.chmod(0o700)
            config = {"claude_binary_sha256": DRIVER.sha256_bytes(binary.read_bytes()), "model": "sonnet"}
            model = DRIVER.LiveClaudeModel(binary, config, root, root, DRIVER.safe_env(root / "home", reasoning="low"))
            observation = DRIVER.Observation(
                game_id="ls20", state="NOT_FINISHED", levels_completed=0,
                win_levels=1, available_actions=("ACTION4",), public_state={"frame": []},
            )
            for category in categories:
                with self.subTest(category=category):
                    completed = __import__("subprocess").CompletedProcess(
                        [], 2, stdout=b"private stdout", stderr=f"blocked: direct_claude_failure={category}\n".encode()
                    )
                    with mock.patch.object(DRIVER.subprocess, "run", return_value=completed):
                        with self.assertRaises(DRIVER.GateError) as caught:
                            model.choose(observation, turn=1, history_path=root / "history", advisory=None)
                    self.assertEqual(str(caught.exception), f"direct Claude action process failed: {category}")
                    self.assertNotIn("private stdout", str(caught.exception))
        self.assertEqual(DRIVER.direct_claude_failure_category("unstructured private error"), "other")

    def test_v9_fresh_identity_binds_valid_strict_empty_mcp_config(self) -> None:
        previous, _ = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v8.json")
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v9.json")
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["games"], previous["games"])
        freshness = manifest["execution_freshness"]
        self.assertEqual(freshness["manifest_generation"], "v9")
        self.assertFalse(freshness["reuse_v8_game_session_output_or_runtime"])
        self.assertEqual(freshness["output_filename"], "arc3-ember-five-public-v9-result.json")
        self.assertEqual(freshness["private_failure_artifact_filename"], "arc3-ember-five-public-v9.direct-claude-failure.private")
        self.assertEqual(manifest["common_live_model_config"]["strict_empty_mcp_config"], {"mcpServers": {}})
        evidence = manifest["owner_only_evidence"]
        self.assertEqual(evidence["v8_attempt_status"], "TERMINATED_INVALID_EMPTY_MCP_CONFIG_ZERO_ACTIONS_ZERO_PAIRS")
        self.assertTrue(evidence["valid_strict_empty_mcp_config_added"])
        self.assertRegex(manifest["common_live_model_config"]["driver_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["common_live_model_config"]["lane_wrapper_sha256"], DRIVER.sha256_bytes((HERE / "claude_lane.py").read_bytes()))

    def test_v9_authorization_binds_exact_private_artifact_and_v8_is_revoked(self) -> None:
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v9.json")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / manifest["execution_freshness"]["private_failure_artifact_filename"]
            receipt = {
                "arc_live_owner_authorized": True, "claude_v7_verdict": "STOP_NO_FULL",
                "experiment_id": manifest["experiment_id"], "manifest_sha256": digest,
                "output_identity": manifest["execution_freshness"]["output_identity"],
                "private_failure_artifact_path": str(artifact),
                "separate_arc_claude_lane_owner_authorized": True,
                "track1_fixed_199_terminal_completed": True, "track1_fixed_denominator": 199,
            }
            authorization = root / "authorization-v9.json"
            authorization.write_text(json.dumps(receipt), encoding="utf-8")
            os.chmod(authorization, 0o600)
            DRIVER.authorization_gate(authorization, manifest, digest, private_failure_artifact=artifact)
        v8, v8_digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v8.json")
        args = type("Args", (), {})()
        with self.assertRaisesRegex(DRIVER.GateError, "v8 execution identity is consumed"):
            DRIVER.run_pair(v8, v8_digest, live=True, args=args)

    def test_v8_private_failure_artifact_is_fresh_bound_and_non_gate_evidence(self) -> None:
        previous, _ = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v7.json")
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v8.json")
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["games"], previous["games"])
        freshness = manifest["execution_freshness"]
        self.assertEqual(freshness["manifest_generation"], "v8")
        self.assertFalse(freshness["reuse_v7_game_session_output_or_runtime"])
        self.assertEqual(freshness["output_filename"], "arc3-ember-five-public-v8-result.json")
        self.assertEqual(freshness["private_failure_artifact_filename"], "arc3-ember-five-public-v8.direct-claude-failure.private")
        self.assertTrue(freshness["private_failure_artifact_must_not_preexist"])
        evidence = manifest["owner_only_evidence"]
        self.assertEqual(evidence["v7_attempt_status"], "TERMINATED_CLASSIFIED_OTHER_ZERO_ACTIONS_ZERO_PAIRS")
        self.assertTrue(evidence["private_direct_cli_failure_artifact_added"])
        self.assertFalse(evidence["private_failure_artifact_is_gate"])
        self.assertTrue(evidence["private_failure_artifact_never_public_or_parent_stderr"])
        self.assertRegex(manifest["common_live_model_config"]["driver_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(manifest["common_live_model_config"]["lane_wrapper_sha256"], r"^[0-9a-f]{64}$")

    def test_v8_authorization_binds_exact_private_artifact_and_v7_is_revoked(self) -> None:
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v8.json")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / manifest["execution_freshness"]["private_failure_artifact_filename"]
            receipt = {
                "arc_live_owner_authorized": True,
                "claude_v7_verdict": "STOP_NO_FULL",
                "experiment_id": manifest["experiment_id"],
                "manifest_sha256": digest,
                "output_identity": manifest["execution_freshness"]["output_identity"],
                "private_failure_artifact_path": str(artifact),
                "separate_arc_claude_lane_owner_authorized": True,
                "track1_fixed_199_terminal_completed": True,
                "track1_fixed_denominator": 199,
            }
            authorization = root / "authorization-v8.json"
            authorization.write_text(json.dumps(receipt), encoding="utf-8")
            os.chmod(authorization, 0o600)
            DRIVER.authorization_gate(
                authorization, manifest, digest, private_failure_artifact=artifact
            )
            with self.assertRaisesRegex(DRIVER.GateError, "not owner-authorized"):
                DRIVER.authorization_gate(
                    authorization, manifest, digest,
                    private_failure_artifact=root / "wrong.private",
                )
        v7, v7_digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v7.json")
        args = type("Args", (), {})()
        with self.assertRaisesRegex(DRIVER.GateError, "v7 execution identity is consumed"):
            DRIVER.run_pair(v7, v7_digest, live=True, args=args)

    def test_v7_fresh_identity_binds_failure_classifier(self) -> None:
        previous, _ = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v6.json")
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v7.json")
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["games"], previous["games"])
        self.assertEqual(manifest["execution_freshness"]["manifest_generation"], "v7")
        self.assertFalse(manifest["execution_freshness"]["reuse_v6_game_session_output_or_runtime"])
        self.assertEqual(manifest["execution_freshness"]["output_filename"], "arc3-ember-five-public-v7-result.json")
        evidence = manifest["owner_only_evidence"]
        self.assertEqual(evidence["v6_attempt_status"], "TERMINATED_DIRECT_CLAUDE_NONZERO_ZERO_ACTIONS_ZERO_PAIRS")
        self.assertEqual(evidence["direct_cli_failure_categories"], ["auth", "invalid_model", "cli_usage", "sandbox_permission", "rate_limit", "network", "other"])
        self.assertRegex(manifest["common_live_model_config"]["driver_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(manifest["common_live_model_config"]["lane_wrapper_sha256"], r"^[0-9a-f]{64}$")

    def test_v7_authorization_is_fresh_and_v6_live_identity_is_revoked(self) -> None:
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v7.json")
        receipt = {
            "arc_live_owner_authorized": True,
            "claude_v7_verdict": "STOP_NO_FULL",
            "experiment_id": manifest["experiment_id"],
            "manifest_sha256": digest,
            "output_identity": manifest["execution_freshness"]["output_identity"],
            "separate_arc_claude_lane_owner_authorized": True,
            "track1_fixed_199_terminal_completed": True,
            "track1_fixed_denominator": 199,
        }
        with tempfile.TemporaryDirectory() as directory:
            authorization = Path(directory) / "authorization-v7.json"
            authorization.write_text(json.dumps(receipt), encoding="utf-8")
            os.chmod(authorization, 0o600)
            DRIVER.authorization_gate(authorization, manifest, digest)
        v6, v6_digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v6.json")
        args = type("Args", (), {})()
        with self.assertRaisesRegex(DRIVER.GateError, "v6 execution identity is consumed"):
            DRIVER.run_pair(v6, v6_digest, live=True, args=args)

    def test_v6_fresh_identity_binds_driver_stdin_fix(self) -> None:
        previous, _ = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v5.json")
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v6.json")
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["games"], previous["games"])
        self.assertEqual(manifest["execution_freshness"]["manifest_generation"], "v6")
        self.assertFalse(manifest["execution_freshness"]["reuse_v5_game_session_output_or_runtime"])
        self.assertEqual(manifest["execution_freshness"]["output_filename"], "arc3-ember-five-public-v6-result.json")
        self.assertEqual(manifest["owner_only_evidence"]["v5_attempt_status"], "TERMINATED_LOCAL_DRIVER_ERROR_ZERO_ACTIONS_ZERO_PAIRS")
        self.assertTrue(manifest["owner_only_evidence"]["driver_duplicate_stdin_input_fixed"])
        self.assertRegex(manifest["common_live_model_config"]["driver_sha256"], r"^[0-9a-f]{64}$")

    def test_v6_authorization_is_fresh_and_v5_live_identity_is_revoked(self) -> None:
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v6.json")
        receipt = {
            "arc_live_owner_authorized": True,
            "claude_v7_verdict": "STOP_NO_FULL",
            "experiment_id": manifest["experiment_id"],
            "manifest_sha256": digest,
            "output_identity": manifest["execution_freshness"]["output_identity"],
            "separate_arc_claude_lane_owner_authorized": True,
            "track1_fixed_199_terminal_completed": True,
            "track1_fixed_denominator": 199,
        }
        with tempfile.TemporaryDirectory() as directory:
            authorization = Path(directory) / "authorization-v6.json"
            authorization.write_text(json.dumps(receipt), encoding="utf-8")
            os.chmod(authorization, 0o600)
            DRIVER.authorization_gate(authorization, manifest, digest)
        v5, v5_digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v5.json")
        args = type("Args", (), {})()
        with self.assertRaisesRegex(DRIVER.GateError, "v5 execution identity is consumed"):
            DRIVER.run_pair(v5, v5_digest, live=True, args=args)

    def test_v5_fresh_identity_binds_local_stdin_fix(self) -> None:
        previous, _ = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v4.json")
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v5.json")
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["games"], previous["games"])
        self.assertEqual(manifest["suite"]["pair_order"], ["baseline", "ember"])
        self.assertEqual(manifest["execution_freshness"]["manifest_generation"], "v5")
        self.assertFalse(manifest["execution_freshness"]["reuse_v4_game_session_output_or_runtime"])
        self.assertEqual(manifest["execution_freshness"]["output_filename"], "arc3-ember-five-public-v5-result.json")
        self.assertEqual(manifest["owner_only_evidence"]["v4_attempt_status"], "TERMINATED_LOCAL_WRAPPER_ERROR_ZERO_ACTIONS_ZERO_PAIRS")
        self.assertTrue(manifest["owner_only_evidence"]["duplicate_stdin_input_fixed"])
        self.assertRegex(manifest["common_live_model_config"]["lane_wrapper_sha256"], r"^[0-9a-f]{64}$")

    def test_v5_authorization_is_fresh_and_v4_live_identity_is_revoked(self) -> None:
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v5.json")
        receipt = {
            "arc_live_owner_authorized": True,
            "claude_v7_verdict": "STOP_NO_FULL",
            "experiment_id": manifest["experiment_id"],
            "manifest_sha256": digest,
            "output_identity": manifest["execution_freshness"]["output_identity"],
            "separate_arc_claude_lane_owner_authorized": True,
            "track1_fixed_199_terminal_completed": True,
            "track1_fixed_denominator": 199,
        }
        with tempfile.TemporaryDirectory() as directory:
            authorization = Path(directory) / "authorization-v5.json"
            authorization.write_text(json.dumps(receipt), encoding="utf-8")
            os.chmod(authorization, 0o600)
            DRIVER.authorization_gate(authorization, manifest, digest)
        v4, v4_digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v4.json")
        args = type("Args", (), {})()
        with self.assertRaisesRegex(DRIVER.GateError, "v4 execution identity is consumed"):
            DRIVER.run_pair(v4, v4_digest, live=True, args=args)

    def test_v4_authorization_binds_stop_no_full_and_separate_arc_lane(self) -> None:
        manifest, digest = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v4.json")
        receipt = {
            "arc_live_owner_authorized": True,
            "claude_v7_verdict": "STOP_NO_FULL",
            "experiment_id": manifest["experiment_id"],
            "manifest_sha256": digest,
            "output_identity": manifest["execution_freshness"]["output_identity"],
            "separate_arc_claude_lane_owner_authorized": True,
            "track1_fixed_199_terminal_completed": True,
            "track1_fixed_denominator": 199,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authorization-v4.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            os.chmod(path, 0o600)
            DRIVER.authorization_gate(path, manifest, digest)
            receipt["separate_arc_claude_lane_owner_authorized"] = False
            path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(DRIVER.GateError, "not owner-authorized"):
                DRIVER.authorization_gate(path, manifest, digest)

    def test_v4_public_result_has_only_allowed_per_game_fields(self) -> None:
        game_ids = ["ls20", "ft09", "vc33", "ar25", "wa30"]
        rows = []
        for game_id in game_ids:
            rows.extend([
                {"arm": "baseline", "game_id": game_id, "common_model_config_sha256": "same", "action_cap": 10, "shadow_rhae_fraction": 0.25, "official_feedback_wasted_actions": 3},
                {"arm": "ember", "game_id": game_id, "common_model_config_sha256": "same", "action_cap": 10, "shadow_rhae_fraction": 0.5, "official_feedback_wasted_actions": 1},
            ])
        result = DRIVER.public_ember_result_v4(rows, game_ids, helper_bug_persists=False)
        expected = {"game_id", "ember_minus_baseline_rhae_delta", "baseline_wasted_actions", "ember_wasted_actions"}
        self.assertEqual(set(result), {"identity", "arms", "games"})
        self.assertTrue(all(set(row) == expected for row in result["games"]))
        self.assertTrue(all(row["baseline_wasted_actions"] == 3 and row["ember_wasted_actions"] == 1 for row in result["games"]))
        public = json.dumps(result, sort_keys=True).lower()
        for forbidden in ("aggregate", "absolute", "prompt", "response", "trace", "log", "gold", "oauth", "secret", "sha256", "path"):
            self.assertNotIn(forbidden, public)

    def test_v4_wasted_action_is_unchanged_official_feedback_count(self) -> None:
        manifest, _ = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v4.json")
        config = DRIVER.manifest_game(manifest, "ls20")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "baseline").mkdir()
            (root / "ember").mkdir()
            baseline = DRIVER.run_arm(
                arm="baseline", game_id="ls20", game_config=config,
                common_config=manifest["common_live_model_config"],
                treatment_config=manifest["treatment_only"],
                game=DRIVER.StubArcadeGame("ls20"), model=DRIVER.StubJcodeModel(),
                skill=None, root=root / "baseline",
            )
            ember = DRIVER.run_arm(
                arm="ember", game_id="ls20", game_config=config,
                common_config=manifest["common_live_model_config"],
                treatment_config=manifest["treatment_only"],
                game=DRIVER.StubArcadeGame("ls20"), model=DRIVER.StubJcodeModel(),
                skill=DRIVER.StubAzdajaSkill(), root=root / "ember",
            )
        self.assertEqual(baseline["official_feedback_wasted_actions"], 24)
        self.assertEqual(ember["official_feedback_wasted_actions"], 2)

    def test_v4_safe_env_and_direct_lane_command_do_not_forward_arc_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = os.environ.get("ARC_API_KEY")
            os.environ["ARC_API_KEY"] = "never-forward"
            try:
                env = DRIVER.safe_env(root / "arm", reasoning="low")
            finally:
                if old is None:
                    os.environ.pop("ARC_API_KEY", None)
                else:
                    os.environ["ARC_API_KEY"] = old
            self.assertNotIn("ARC_API_KEY", env)
            failure_artifact = root / "artifacts" / "failure.private"
            command = DRIVER.direct_claude_subcall_command(
                root / "bin" / "claude", root / "home", root / "runtime",
                failure_artifact,
            )
            self.assertIn("subcall", command)
            self.assertIn("{model}", command)
            self.assertNotIn("jcode-api", command)
            self.assertIn(str(failure_artifact), command)

    def test_v4_stages_ember_with_direct_lane_not_bridge(self) -> None:
        manifest, _ = DRIVER.verify_manifest(HERE / "mini-pilot-live-manifest-v4.json")
        treatment = json.loads(json.dumps(manifest["treatment_only"]))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle"
            bundle.mkdir()
            (bundle / "ember").write_bytes(b"owner-binary")
            (bundle / "SKILL.md").write_text("version {{VERSION}} binary {{BIN}}", encoding="utf-8")
            (bundle / "config.toml").write_text(
                'sub_llm_cmd="jcode-api"\ndefault_model="claude-sonnet-5"\njcode_provider="claude"\njcode_reasoning="low"\n',
                encoding="utf-8",
            )
            treatment["binary_sha256_by_platform"] = {DRIVER.platform_key(): DRIVER.sha256_bytes(b"owner-binary")}
            treatment["source_bundle_components_sha256"] = {
                name: DRIVER.sha256_bytes((bundle / name).read_bytes()) for name in ("SKILL.md", "config.toml")
            }
            env = DRIVER.safe_env(root / "home", reasoning="low")
            Path(env["HOME"]).mkdir()
            direct = "python lane.py subcall --model {model}"
            staged = DRIVER.stage_ember_skill(bundle, env, treatment, direct_lane_command=direct)
            config = __import__("tomllib").loads((staged.parent / "config.toml").read_text())
            self.assertEqual(config["sub_llm_cmd"], direct)
            self.assertNotIn("jcode-api", config["sub_llm_cmd"])



if __name__ == "__main__":
    unittest.main()
