import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from . import installed as i


class InstalledAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_existing_and_dangling_outputs_refuse_before_any_process(self):
        for kind in ('file', 'link', 'directory'):
            out = self.root / kind
            if kind == 'file':
                out.write_bytes(b'keep')
            elif kind == 'link':
                out.symlink_to(self.root / 'missing')
            else:
                out.mkdir()
            with mock.patch('subprocess.run', side_effect=AssertionError('process forbidden')):
                with self.assertRaisesRegex(ValueError, 'output exists'):
                    i.run(Path(sys.executable), out)
        self.assertEqual((self.root/'file').read_bytes(), b'keep')
        self.assertTrue((self.root/'link').is_symlink())

    def test_default_public_cli_requires_explicit_binary_and_new_output(self):
        p = subprocess.run([sys.executable, '-B', str(Path(i.__file__))], cwd=self.root,
                           capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_private_copy_preserves_bytes_and_uses_owner_only_permissions(self):
        source = self.root/'source'
        source.mkdir()
        (source/'record.json').write_bytes(b'{"original":true}\n')
        target = self.root/'target'
        i.private_copy(source, target)
        self.assertEqual(i.inventory(source), i.inventory(target))
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((target/'record.json').stat().st_mode), 0o600)

    def test_private_copy_refuses_source_symlink(self):
        source = self.root/'source'
        source.mkdir()
        (source/'linked').symlink_to(self.root/'outside')
        with self.assertRaisesRegex(ValueError, 'unsafe retained job'):
            i.private_copy(source, self.root/'target')
        self.assertFalse((self.root/'outside').exists())


if __name__ == '__main__':
    unittest.main()
