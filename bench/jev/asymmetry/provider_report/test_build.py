import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from bench.jev.asymmetry.provider_report import build


class PublicReportTests(unittest.TestCase):
    def test_real_frozen_metrics_bins_and_request_only(self):
        files = build.materials()
        m = json.loads(files['metrics.json'])
        self.assertEqual((m['observed'], m['false_positives'], m['false_negatives']), (17469, 641, 34))
        self.assertEqual(m['sum_noul'], 9287.38)
        bins = list(csv.DictReader(io.StringIO(files['reliability.csv'].decode())))
        for n in ('5', '10'):
            self.assertEqual(sum(int(b['n']) for b in bins if b['bin_count'] == n), 17469)
        request = json.loads(files['failed-choice-request.json'])
        self.assertEqual(set(request), {'state', 'questions', 'model'})
        self.assertEqual(len(request['questions']), 25)
        self.assertNotIn('answers', request)
        self.assertIn('historical raw response was NOT retained', files['REPORT.md'].decode())
        self.assertIn('CC BY-SA 4.0', files['REPORT.md'].decode())
        for raw in files.values():
            self.assertNotIn(b'/Users/', raw)
            self.assertNotIn(b'Bearer ', raw)

    def test_source_mutation_refuses(self):
        original = build.REQUEST_SHA
        with patch.object(build, 'REQUEST_SHA', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'frozen failed request changed'):
                build.materials()
        self.assertEqual(build.REQUEST_SHA, original)

    def test_public_existing_output_preserved(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            dest = Path(tmp) / 'occupied'
            dest.mkdir()
            marker = dest / 'sentinel'
            marker.write_bytes(b'preserve')
            result = subprocess.run([sys.executable, '-B', '-m',
                'bench.jev.asymmetry.provider_report.build', '--output', str(dest)],
                cwd=build.ROOT, capture_output=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_bytes(), b'preserve')
            self.assertEqual(list(dest.iterdir()), [marker])


if __name__ == '__main__':
    unittest.main()
