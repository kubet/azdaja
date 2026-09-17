import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from bench.jev.span_selection import kernel as k
from bench.jev.span_selection import replay
from bench.jev.span_selection import run as r


class ReplayTests(unittest.TestCase):
    def test_actual_retained_panel_keeps_negative_quality_result(self):
        result = replay.verify(r.HERE / 'results/native-20260917')
        self.assertEqual((result['typed_correct'], result['baseline_correct']), (17,18))
        self.assertFalse(result['comparison']['quality_bar_passed'])
        self.assertFalse(result['comparison']['observed_benefit_bar_passed'])
        self.assertEqual(result['live_provider_calls'],0)

    def mutation(self, filename, edit, expected, rehash=True):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            dst=Path(tmp)/'result';shutil.copytree(r.HERE/'results/native-20260917',dst)
            path=dst/filename;data=json.loads(path.read_text());edit(data)
            path.write_text(json.dumps(data,indent=2)+'\n')
            if rehash:
                manifest=json.loads((dst/'MANIFEST.json').read_text())
                manifest['artifacts'][filename]={'sha256':k.sha(path.read_bytes()),'bytes':path.stat().st_size}
                (dst/'MANIFEST.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,expected):
                replay.verify(dst)

    def test_digest_detects_changed_response(self):
        self.mutation('block1-typed-observation.json',lambda d:d['observation'].update(model='changed'),
                      'artifact digest',False)

    def test_rehashed_false_win_is_rejected(self):
        self.mutation('receipt.json',lambda d:d['comparison'].update(quality_bar_passed=True),
                      'reported comparison')

    def test_rehashed_native_table_is_not_authoritative(self):
        self.mutation('block1-typed-table.json',lambda d:d['rows'][0].update(start=0),
                      'native table mismatch')

    def test_rehashed_unmatched_baseline_inputs_are_rejected(self):
        self.mutation('block1-baseline-prompt.json',lambda d:d['payload']['state']['tasks'][0].update(question='different'),
                      'unmatched model inputs')


if __name__ == '__main__':
    unittest.main()
