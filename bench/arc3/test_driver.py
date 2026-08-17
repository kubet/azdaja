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

    def test_ndjson_response_parser(self) -> None:
        text = '\n'.join([
            json.dumps({"type": "text_delta", "text": '{"action":'}),
            json.dumps({"type": "text_delta", "text": '"ACTION4","data":{}}'}),
        ])
        self.assertEqual(DRIVER.ndjson_response(text), '{"action":"ACTION4","data":{}}')


if __name__ == "__main__":
    unittest.main()
