import copy
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from . import audit as a


class FullRowLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = a.prepare.SOURCE.read_bytes()
        cls.metadata = a.n.strict_loads(a.prepare.ROW.read_bytes())
        cls.envelope = a.n.strict_loads((a.HERE / 'official-row651.json').read_bytes())

    def test_every_source_occurrence_aligns_with_exact_bytes(self):
        rows = a.align(self.envelope, self.source, self.metadata)
        self.assertEqual(len(rows), 17469)
        self.assertEqual(sum(r['gold_ham'] for r in rows), 8638)
        for row in rows:
            raw = self.source[row['byte_start']:row['byte_end']]
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['record_sha256'])
        self.assertEqual([r['id'] for r in rows], [r['id'] for r in a.prepare.occurrences()])

    def test_truncation_wrong_row_or_metadata_refuses(self):
        changes = [lambda d: d.update(partial=True),
                   lambda d: d['rows'][0].update(truncated_cells=['context_window_text_with_labels']),
                   lambda d: d['rows'][0].update(row_idx=650),
                   lambda d: d['rows'][0]['row'].update(context_window_id=-1),
                   lambda d: d['rows'][0]['row'].update(question='different task')]
        for change in changes:
            with self.subTest(change=change):
                data = copy.deepcopy(self.envelope)
                change(data)
                with self.assertRaises(ValueError):
                    a.align(data, self.source, self.metadata)

    def test_reordered_labeled_lines_refuse(self):
        data = copy.deepcopy(self.envelope)
        lines = data['rows'][0]['row']['context_window_text_with_labels'].splitlines(keepends=True)
        lines[4], lines[5] = lines[5], lines[4]
        data['rows'][0]['row']['context_window_text_with_labels'] = ''.join(lines)
        with self.assertRaisesRegex(ValueError, 'occurrence bytes changed'):
            a.align(data, self.source, self.metadata)

    def test_changed_source_record_or_nonrecord_refuses(self):
        for index in (0, 4):
            data = copy.deepcopy(self.envelope)
            lines = data['rows'][0]['row']['context_window_text_with_labels'].splitlines(keepends=True)
            lines[index] = 'EDIT' + lines[index]
            data['rows'][0]['row']['context_window_text_with_labels'] = ''.join(lines)
            with self.assertRaisesRegex(ValueError, '(nonrecord|occurrence) bytes changed'):
                a.align(data, self.source, self.metadata)

    def test_unlabeled_source_and_label_sum_must_match(self):
        data = copy.deepcopy(self.envelope)
        data['rows'][0]['row']['context_window_text'] += 'extra'
        with self.assertRaisesRegex(ValueError, 'unlabeled source differs'):
            a.align(data, self.source, self.metadata)
        data = copy.deepcopy(self.envelope)
        row = data['rows'][0]['row']
        row['context_window_text_with_labels'] = row['context_window_text_with_labels'].replace(
            ' || Label: ham', ' || Label: spam', 1)
        with self.assertRaisesRegex(ValueError, 'official aggregate disagreement'):
            a.align(data, self.source, self.metadata)

    def test_join_is_by_id_preserves_multiplicity_and_rejects_missing_extra_duplicate(self):
        rows = [{'id': 'a', 'gold_ham': True}, {'id': 'b', 'gold_ham': False}]
        self.assertEqual([r['p_ham'] for r in a.join(rows, {'b': .2, 'a': .8})], [.8, .2])
        for ledger, predictions in ((rows, {'a': .8}), (rows, {'a': .8, 'b': .2, 'c': .1}),
                                    (rows + [rows[0]], {'a': .8, 'b': .2})):
            with self.assertRaisesRegex(ValueError, 'prediction coverage'):
                a.join(ledger, predictions)

    def test_metrics_match_hand_computed_endpoint_and_threshold_example(self):
        rows = [{'id': 'a', 'p_ham': 0, 'gold_ham': False},
                {'id': 'b', 'p_ham': 1, 'gold_ham': True},
                {'id': 'c', 'p_ham': .5, 'gold_ham': False},
                {'id': 'd', 'p_ham': .2, 'gold_ham': True}]
        m = a.metrics(rows)
        self.assertEqual((m['correct'], m['false_positive_ids'], m['false_negative_ids']), (2, ['c'], ['d']))
        self.assertAlmostEqual(m['brier_score'], .2225)
        for count in ('5', '10'):
            self.assertAlmostEqual(m['positive_probability_reliability'][count]['ece'], .325)
            self.assertEqual(sum(b['n'] for b in m['positive_probability_reliability'][count]['bins']), 4)
            self.assertEqual(m['positive_probability_reliability'][count]['bins'][-1]['n'], 1)

    def test_malformed_probability_gold_duplicate_or_empty_never_scores(self):
        for p in (True, float('nan'), float('inf'), -0.1, 1.1, '0.9'):
            with self.assertRaisesRegex(ValueError, 'probability domain'):
                a.metrics([{'id': 'a', 'p_ham': p, 'gold_ham': True}])
        with self.assertRaisesRegex(ValueError, 'gold must be boolean'):
            a.metrics([{'id': 'a', 'p_ham': .9, 'gold_ham': 1}])
        row = {'id': 'a', 'p_ham': .9, 'gold_ham': True}
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            a.metrics([row, row])
        with self.assertRaisesRegex(ValueError, 'empty'):
            a.metrics([])

    def test_actual_public_audit_and_safe_output_refusals(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as directory:
            output = Path(directory) / 'result.json'
            command = [sys.executable, '-B', '-m', 'bench.jev.row651_labels.audit', '--output']
            first = subprocess.run(command + [str(output)], capture_output=True, text=True, timeout=20)
            self.assertEqual(first.returncode, 0, first.stderr)
            result = a.n.strict_loads(output.read_bytes())
            self.assertEqual(result['source_occurrences_aligned_byte_for_byte'], 17469)
            self.assertEqual(result['metrics']['predicted_ham'], 9245)
            self.assertEqual(result['metrics']['gold_ham'], 8638)
            self.assertFalse(result['native_workflow']['exact_task_pass'])
            self.assertEqual(result['new_inference_requests'], 0)
            before = output.read_bytes()
            again = subprocess.run(command + [str(output)], capture_output=True, text=True, timeout=20)
            self.assertNotEqual(again.returncode, 0)
            self.assertIn('output exists', again.stderr)
            self.assertEqual(output.read_bytes(), before)
            dangling = Path(directory) / 'dangling'
            target = Path(directory) / 'absent'
            dangling.symlink_to(target)
            again = subprocess.run(command + [str(dangling)], capture_output=True, text=True, timeout=20)
            self.assertNotEqual(again.returncode, 0)
            self.assertIn('output exists', again.stderr)
            self.assertFalse(target.exists())

    def test_changed_snapshot_refuses_before_any_score(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as directory:
            p = Path(directory) / 'snapshot.json'
            p.write_bytes((a.HERE / 'official-row651.json').read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'official snapshot changed'):
                a.audit(p)

    def test_frozen_report_recomputes_exactly_and_remains_a_count_failure(self):
        retained = a.n.strict_loads((a.HERE / 'result.json').read_bytes())
        self.assertEqual(a.audit(), retained)
        self.assertEqual((retained['metrics']['false_positives'],
                          retained['metrics']['false_negatives']), (641, 34))
        self.assertEqual(retained['metrics']['correct'], 16794)
        self.assertFalse(retained['native_workflow']['exact_task_pass'])


if __name__ == '__main__':
    unittest.main()
