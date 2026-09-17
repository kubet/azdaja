import copy
import unittest
from . import audit as a


class OfficialGoldTests(unittest.TestCase):
    def setUp(self):
        self.source=a.original.SOURCE.read_bytes()
        self.row=a.n.strict_loads(a.original.ROW.read_bytes())
        self.data=a.n.strict_loads((a.HERE/'official-row645.json').read_bytes())

    def test_exact_2177_alignment_and_actual_false_positives(self):
        labels=a.align(self.data,self.source,self.row)
        self.assertEqual(len(labels),2177)
        result=a.audit(a.HERE/'official-row645.json')
        self.assertEqual(result['aligned_official_ham'],132)
        for arm in ('typed','generative'):
            self.assertEqual((result[arm]['false_positives'],result[arm]['false_negatives']),(7,0))
        self.assertEqual(len(result['shared_false_positive_ids']),5)
        self.assertEqual(result['sum_noul'],138.02)
        self.assertFalse(result['rerun_performed'])

    def test_truncation_and_wrong_row_refused(self):
        for mutation in (lambda d:d.update(partial=True),lambda d:d['rows'][0].update(truncated_cells=['context_window_text_with_labels']),lambda d:d['rows'][0].update(row_idx=646)):
            data=copy.deepcopy(self.data);mutation(data)
            with self.assertRaises(ValueError):a.align(data,self.source,self.row)

    def test_reordered_labeled_occurrences_refused(self):
        data=copy.deepcopy(self.data);row=data['rows'][0]['row']
        lines=row['context_window_text_with_labels'].splitlines(keepends=True)
        lines[4],lines[5]=lines[5],lines[4]
        row['context_window_text_with_labels']=''.join(lines)
        with self.assertRaisesRegex(ValueError,'occurrence bytes changed'):a.align(data,self.source,self.row)

    def test_message_edit_cannot_keep_label_alignment(self):
        data=copy.deepcopy(self.data);row=data['rows'][0]['row']
        row['context_window_text_with_labels']=row['context_window_text_with_labels'].replace('Compliments to you.','Altered message.',1)
        with self.assertRaisesRegex(ValueError,'occurrence bytes changed'):a.align(data,self.source,self.row)

    def test_equal_counts_are_not_equal_errors(self):
        rows=[{'id':'a','gold_ham':True,'left':True,'right':True},
              {'id':'b','gold_ham':False,'left':True,'right':False},
              {'id':'c','gold_ham':False,'left':False,'right':True}]
        left=a.confusion(rows,'left');right=a.confusion(rows,'right')
        self.assertEqual(left['predicted_ham'],right['predicted_ham'])
        self.assertNotEqual(left['false_positive_ids'],right['false_positive_ids'])


if __name__=='__main__':unittest.main()
