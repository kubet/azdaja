import copy
import unittest
from unittest.mock import patch
from bench.jev.asymmetry.threshold import transfer as t


class TransferTests(unittest.TestCase):
    def test_signed_count_and_asymmetric_errors(self):
        rows = [{'id': 'a', 'gold_ham': True, 'p_ham': .74},
                {'id': 'b', 'gold_ham': True, 'p_ham': .6},
                {'id': 'c', 'gold_ham': False, 'p_ham': .65}]
        old, new = t.confusion(rows, 50), t.confusion(rows, 74)
        self.assertEqual((old['false_positives'], old['false_negatives'], old['signed_count_error']), (1, 0, 1))
        self.assertEqual((new['false_positives'], new['false_negatives'], new['signed_count_error']), (0, 1, -1))
        self.assertEqual(new['correct'], 2)

    def test_normalization_ignores_date_but_not_message_meaning(self):
        a = 'Date: 2025-01-01 || User: 1 || Instance: HELLO  Café\n'
        b = 'Date: 2026-04-09 || User: 99 || Instance: hello cafe\u0301\n'
        self.assertEqual(t.normalized_message(a), t.normalized_message(b))
        self.assertNotEqual(t.normalized_message(a), t.normalized_message(b.replace('hello', 'not hello')))
        self.assertNotEqual(a, b)
        with self.assertRaises(ValueError): t.normalized_message('missing marker')

    def test_bad_probability_gold_and_duplicates_reject(self):
        row = {'id': 'a', 'gold_ham': True, 'p_ham': .75}
        for field, value in [('p_ham', True), ('p_ham', float('nan')), ('p_ham', 1.1), ('gold_ham', 1)]:
            altered = dict(row); altered[field] = value
            with self.assertRaises(ValueError): t.confusion([altered], 74)
        with self.assertRaises(ValueError): t.confusion([row, row], 74)
        self.assertIsNone(t.confusion([], 74)['accuracy'])

    def test_committed_freeze_and_changed_digest_reject_before_headline(self):
        with patch.object(t.headline, 'audit', side_effect=AssertionError('headline must not load')):
            commit, freeze, rows = t.frozen_policy()
            self.assertTrue(commit.startswith('cdbbd0e'))
            self.assertEqual(freeze['selection']['selected']['threshold_cents'], 74)
            self.assertEqual(len(rows), 227)
            with patch.object(t, 'FREEZE_SHA', '0' * 64):
                with self.assertRaisesRegex(ValueError, 'freeze changed'): t.frozen_policy()


if __name__ == '__main__': unittest.main()
