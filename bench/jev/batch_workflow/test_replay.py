import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from . import replay as r


class RetainedBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR'))
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)

    def cli(self, output):
        return subprocess.run([sys.executable, '-B', str(r.HERE / 'replay.py'), '--output', str(output)],
                              cwd=self.work, capture_output=True, text=True, timeout=15)

    def test_actual_public_cli_outside_repo_rebuilds_all_sources(self):
        p = self.cli(self.work / 'out')
        self.assertEqual(p.returncode, 0, p.stderr)
        result = json.loads(p.stdout)
        self.assertEqual((result['source_files'], result['source_bytes'], result['completed_windows']),
                         (102, 4779822, 138))
        self.assertEqual(result['new_provider_calls'], 0)
        self.assertFalse(result['historical_binary_bytes_verified'])
        self.assertFalse(result['provider_authenticity_independently_verified'])
        self.assertEqual(r.sha(self.work / 'out/review.jsonl'), result['review_sha256'])

    def test_existing_and_dangling_outputs_are_refused(self):
        occupied = self.work / 'occupied'
        occupied.write_bytes(b'keep')
        self.assertEqual(self.cli(occupied).returncode, 2)
        self.assertEqual(occupied.read_bytes(), b'keep')
        dangling = self.work / 'dangling'
        dangling.symlink_to(self.work / 'absent')
        self.assertEqual(self.cli(dangling).returncode, 2)
        self.assertTrue(dangling.is_symlink())

    def test_changed_retained_observation_refuses_before_output(self):
        root = self.work / 'copied'
        retention = r.load(r.HERE / 'RETENTION.json')
        for name in retention['files']:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(r.ROOT / name, target)
        here = root / r.HERE.relative_to(r.ROOT)
        shutil.copyfile(r.HERE / 'RETENTION.json', here / 'RETENTION.json')
        (here / 'results-20260918/job/000000.result.json').write_text('{}\n')
        with mock.patch.object(r, 'ROOT', root), mock.patch.object(r, 'HERE', here):
            with self.assertRaisesRegex(ValueError, 'retained artifact changed'):
                r.replay(self.work / 'out')
        self.assertFalse((self.work / 'out').exists())

    def test_replay_never_opens_network_or_launches_a_provider(self):
        with mock.patch('socket.socket', side_effect=AssertionError('network forbidden')), \
             mock.patch('subprocess.Popen', side_effect=AssertionError('process forbidden')):
            result = r.replay(self.work / 'out')
        self.assertEqual(result['status'], 'replay_consistent')


if __name__ == '__main__':
    unittest.main()
