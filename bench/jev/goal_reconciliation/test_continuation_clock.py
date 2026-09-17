"""Current test entry point for the frozen September 17 continuation.

Run with ``python3 -B -m unittest
bench.jev.goal_reconciliation.test_continuation_clock``.

The original test and controller are sealed evidence and stay unchanged. One
mock-only test needs an admission-time clock to reach its duplicate-marker
assertion. Override that clock in that test alone, not the process-wide clock,
the production deadline, the receipt, or any actual campaign. All other original
tests run unchanged. The separate expiry test proves that production still
rejects late admission before inventory, credentials, or campaign construction.
"""

import hashlib
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from bench.jev.asymmetry.baseline import continue_run as c
from bench.jev.asymmetry.baseline import test_continue as historical


class RecoveryTests(historical.RecoveryTests):
    def test_exclusive_admission_blocks_repeat_output_before_any_campaign(self):
        original_clock = c.time
        clock = SimpleNamespace(time=lambda: c.STARTED + 1)
        # The inherited witness already mocks Campaign and uses a temporary
        # duplicate marker. Keep those assertions, including zero construction.
        with patch.object(c, "time", clock):
            super().test_exclusive_admission_blocks_repeat_output_before_any_campaign()
        self.assertIs(c.time, original_clock)

    def test_expired_admission_stops_before_inventory_or_campaign(self):
        original_clock = c.time
        for now in (c.DEADLINE, c.DEADLINE + 1, c.DEADLINE + 365 * 86400):
            with self.subTest(now=now):
                with patch.object(c, "time", SimpleNamespace(time=lambda: now)), \
                     patch.object(c.b, "rows") as rows, \
                     patch.object(c, "inventory") as inventory, \
                     patch.object(c, "Campaign") as campaign:
                    with self.assertRaisesRegex(c.n.Stop, "original_campaign_deadline"):
                        c.main([
                            "--live", "--acknowledge-provider-calls",
                            "--azdaja", "not-opened",
                            "--output", "not-created",
                            "--private-jcode-home", "not-opened",
                        ])
                    rows.assert_not_called()
                    inventory.assert_not_called()
                    campaign.assert_not_called()
            self.assertIs(c.time, original_clock)

    def test_original_source_and_deadline_still_match_the_study_seal(self):
        seal = c.load(c.HERE / "CONTINUATION-FROZEN.json")
        self.assertEqual(c.DEADLINE, seal["deadline_unix"])
        for name in ("continue_run.py", "test_continue.py", "continuation_supervisor.py"):
            matches = [digest for path, digest in seal["files"].items()
                       if Path(path).name == name]
            self.assertEqual(len(matches), 1)
            self.assertEqual(hashlib.sha256((c.HERE / name).read_bytes()).hexdigest(),
                             matches[0])


if __name__ == "__main__":
    unittest.main()
