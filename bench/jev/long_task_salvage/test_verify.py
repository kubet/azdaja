import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from bench.jev.long_task_salvage import verify as v


class PortableVerificationTests(unittest.TestCase):
    def test_roundoff_is_not_a_license_to_change_counts_or_structure(self):
        self.assertTrue(v.equivalent({'f1': .72}, {'f1': .72 + 1e-16}))
        for a, b in [(426, 427), (0, False), (1, 1.0), ({'x': 1}, {}),
                     ([1, 2], [2, 1]), (.72, .72001), (float('nan'), float('nan'))]:
            self.assertFalse(v.equivalent(a, b))

    def test_changed_missing_escape_and_symlink_files_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as directory:
            root = Path(directory)
            (root / 'evidence').write_bytes(b'original')
            digest = v.r.base.sha(b'original')
            v.checked_files(root, {'evidence': digest})
            for entries in ({}, {'missing': digest}, {'../evidence': digest}, {'/evidence': digest}):
                with self.assertRaises(v.r.base.Stop):
                    v.checked_files(root, entries)
            (root / 'evidence').write_bytes(b'changed')
            with self.assertRaises(v.r.base.Stop):
                v.checked_files(root, {'evidence': digest})
            (root / 'link').symlink_to(root / 'evidence')
            with self.assertRaises(v.r.base.Stop):
                v.checked_files(root, {'link': v.r.base.sha(b'changed')})

    def test_actual_public_command_works_outside_repository_without_binary(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as directory:
            result = subprocess.run([sys.executable, '-B', str(v.HERE / 'verify.py')],
                                    cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = v.r.base.loads(result.stdout.encode())
            self.assertEqual(report['new_provider_calls'], 0)
            self.assertFalse(report['original_end_to_end_success'])
            self.assertFalse(report['jev_advantage_established'])
            self.assertEqual(report['arms']['generative']['correct'], 426)
            self.assertEqual(report['arms']['optional_typed']['correct'], 404)


if __name__ == '__main__':
    unittest.main()
