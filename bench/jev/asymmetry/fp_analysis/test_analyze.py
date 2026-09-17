import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from bench.jev.asymmetry.fp_analysis import analyze


class AnalysisTests(unittest.TestCase):
    def test_frozen_counts_spans_hashes_and_deterministic_outputs(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as directory:
            out = Path(directory)
            import subprocess
            cmd = ["python3", "-B", str(Path(analyze.__file__)), "--output-dir", str(out)]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            first = (out / "analysis.json").read_bytes()
            summary = json.loads(first)
            repeats = summary['repeated_message_dependence']
            self.assertEqual(repeats['full_record']['unique'], 17469)
            self.assertEqual(repeats['exact_instance']['unique'], 5009)
            self.assertEqual(repeats['exact_instance']['errors_in_repeated_groups'], 675)
            self.assertEqual(repeats['normalized_instance']['unique'], 4997)
            self.assertEqual(sum(g['gold_spam_n'] for g in summary['lexical_clusters']), 8831)
            self.assertEqual(sum(g['gold_ham_n'] for g in summary['lexical_clusters']), 8638)
            errors = [json.loads(line) for line in (out / "errors.jsonl").read_text().splitlines()]
            self.assertEqual(len(errors), 675)
            self.assertEqual(sum(not row["gold_ham"] for row in errors), 641)
            self.assertEqual(sum(row["gold_ham"] for row in errors), 34)
            for row in errors:
                self.assertEqual(len(row["record_sha256"]), 64)
                self.assertLess(row["byte_start"], row["byte_end"])
                self.assertTrue(row["raw"].startswith("Date:"))
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.assertEqual(first, (out / "analysis.json").read_bytes())

    def test_metadata_uniqueness_cannot_mask_message_repetition(self):
        rows = [{'record_sha256': str(i), 'instance': s, 'p_ham': .8, 'gold_ham': False}
                for i, s in enumerate(['Hello  THERE', 'hello there', 'different'])]
        exact = analyze.dependence(rows, lambda r: r['instance'])
        norm = analyze.dependence(rows, lambda r: analyze.normalized(r['instance']))
        self.assertEqual(exact['unique'], 3)
        self.assertEqual(norm['unique'], 2)
        self.assertEqual(norm['errors_in_repeated_groups'], 2)
        self.assertEqual(norm['duplicate_occurrences_beyond_first'], 1)

    def test_changed_frozen_result_refuses_before_output(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as directory:
            root = Path(directory)
            bad = root / 'bad.json'
            bad.write_bytes(analyze.DEFAULT_RESULT.read_bytes() + b' ')
            output = root / 'out'
            p = subprocess.run(['python3', '-B', str(Path(analyze.__file__)), '--result', str(bad),
                                '--output-dir', str(output)], capture_output=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn(b'frozen result changed', p.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
