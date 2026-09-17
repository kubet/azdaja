"""Portable replay source custody, not historical binary authentication."""
import copy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bench.jev.angle_lab import native as n
from bench.jev.second_reader import replay_large as replay


class PortableSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR'])
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'checkout'; self.root.mkdir()
        self.origin = '/original/machine/repo/'
        self.files = {'bench/jev/angle_lab/native.py':b'fixture native source',
                      'bench/jev/fixture.json':b'{}'}
        for name, raw in self.files.items():
            p = self.root/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
        self.receipt = {'binary_sha256':replay.run.BINARY_SHA,
            'frozen_files':{self.origin+k:n.sha(v) for k,v in self.files.items()}}
        self.receipt['frozen_files']['/original/machine/private/binary'] = replay.run.BINARY_SHA
        seal_path = self.root/replay._SEAL_RELATIVE
        seal_path.parent.mkdir(parents=True,exist_ok=True)
        seal_raw = n.canonical({'files':dict(self.receipt['frozen_files'])})
        seal_path.write_bytes(seal_raw)
        self.seal_sha = n.sha(seal_raw)
        self.receipt['frozen_files'][self.origin+replay._SEAL_RELATIVE] = self.seal_sha
        pin = patch.object(replay,'_SEAL_SHA',self.seal_sha)
        pin.start();self.addCleanup(pin.stop)

    def test_relocated_bytes_pass_without_any_original_file_or_binary_reads(self):
        original = Path.open
        def guarded(path, *args, **kwargs):
            if str(path).startswith('/original/machine/'):
                raise AssertionError('original machine read')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', guarded):
            scope = replay.portable_sources(self.receipt, self.root)
        self.assertEqual(scope['source_files_verified'],3)
        self.assertFalse(scope['runtime_binary_bytes_verified'])
        self.assertEqual(scope['runtime_binary_identity_recorded'],replay.run.BINARY_SHA)
        self.assertFalse(scope['recorded_absolute_paths_used_for_lookup'])

    def test_missing_or_changed_local_source_has_no_original_fallback(self):
        path = self.root/'bench/jev/fixture.json'
        path.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'relocated source changed'):
            replay.portable_sources(self.receipt,self.root)
        path.unlink()
        with self.assertRaisesRegex(ValueError,'missing relocated source'):
            replay.portable_sources(self.receipt,self.root)

    def test_traversal_duplicate_anchors_and_external_omissions_reject(self):
        for name, digest in ((self.origin+'../escape',n.sha(b'x')),
                             (self.origin+'bench/./jev/fixture.json',n.sha(b'{}')),
                             ('/another/repo/bench/jev/angle_lab/native.py',n.sha(b'x')),
                             ('/another/external',replay.run.BINARY_SHA),
                             ('relative/path',n.sha(b'x'))):
            r = copy.deepcopy(self.receipt); r['frozen_files'][name] = digest
            with self.assertRaises(ValueError): replay.portable_sources(r,self.root)
        r = copy.deepcopy(self.receipt); del r['frozen_files']['/original/machine/private/binary']
        with self.assertRaisesRegex(ValueError,'frozen source coverage'):
            replay.portable_sources(r,self.root)

    def test_receipt_cannot_omit_sources_or_rewrite_the_original_seal(self):
        r = copy.deepcopy(self.receipt)
        del r['frozen_files'][self.origin+'bench/jev/fixture.json']
        with self.assertRaisesRegex(ValueError,'frozen source coverage'):
            replay.portable_sources(r,self.root)
        (self.root/replay._SEAL_RELATIVE).write_bytes(b'{"files":{}}')
        with self.assertRaisesRegex(ValueError,'original pre-run seal changed'):
            replay.portable_sources(self.receipt,self.root)

    def test_symlink_source_cannot_escape_the_current_checkout(self):
        p = self.root/'bench/jev/fixture.json'; p.unlink()
        outside = Path(self.temp.name)/'outside'; outside.write_bytes(b'{}')
        p.symlink_to(outside)
        with self.assertRaises(ValueError): replay.portable_sources(self.receipt,self.root)

    def test_runtime_identity_mismatch_and_nonhex_digests_reject(self):
        for field in ('runtime','digest'):
            r = copy.deepcopy(self.receipt)
            if field == 'runtime':r['binary_sha256']='a'*64
            else:r['frozen_files'][self.origin+'bench/jev/fixture.json']='z'*64
            with self.assertRaises(ValueError): replay.portable_sources(r,self.root)


if __name__=='__main__':unittest.main()
