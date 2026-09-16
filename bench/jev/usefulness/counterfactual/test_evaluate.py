import copy
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent))
import evaluate


def fixture():
    corpus = {'items': [{'id': 'a', 'text': 'å'}, {'id': 'b', 'text': 'b'}, {'id': 'c', 'text': 'xyz'}]}
    tasks = {'tasks': [{'id': 'Q1', 'question': 'first'}, {'id': 'Q2', 'question': 'second'}]}
    gold = {'tasks': [{'task_id': 'Q1', 'required_evidence_groups': [['a', 'b'], ['c']]},
                      {'task_id': 'Q2', 'required_evidence_groups': [['a']]}]}
    rankings = {'schema_version': 2, 'source_only': True, 'tasks': []}
    for task in tasks['tasks']:
        rankings['tasks'].append({'task_id': task['id'], 'question': task['question'],
                                 'question_sha256': hashlib.sha256(task['question'].encode()).hexdigest(),
                                 'rankings': {method: ['a', 'b', 'c'] for method in evaluate.METHODS}})
    diagnostic = {'k': 4, 'bm25': [{'id': source} for source in ['a', 'b', 'c']],
                  'typed_ranking': [{'id': source} for source in ['c', 'a', 'b']]}
    return rankings, corpus, tasks, gold, diagnostic


class EvaluationTests(unittest.TestCase):
    def test_or_groups_do_not_double_count_and_bytes_are_utf8(self):
        texts = {'a': 'å', 'b': 'b', 'c': 'xyz'}
        result = evaluate.coverage(['a', 'b', 'c'], [['a', 'b'], ['c']], texts, 2)
        self.assertEqual(result['covered_groups'], 1)
        self.assertEqual(result['coverage_fraction'], 0.5)
        self.assertEqual(result['selected_text_bytes'], 3)
        self.assertEqual(result['missing_groups'], [['c']])
        self.assertFalse(result['complete'])

    def test_macro_not_micro_and_no_invented_jev_tasks(self):
        result = evaluate.score(*fixture())
        self.assertEqual(result['all_seven_lexical']['raw_bm25']['1']['macro_group_coverage'], 0.75)
        self.assertEqual(result['all_seven_lexical']['raw_bm25']['1']['covered_groups'], 2)
        self.assertEqual(result['all_seven_lexical']['raw_bm25']['1']['total_groups'], 3)
        self.assertEqual(result['jev_tasks_measured'], ['Q1'])
        self.assertNotIn('jev_retained', result['by_task']['Q2'])
        self.assertIsNone(result['shortlist_conditioned_final_answer_quality'])

    def test_missing_duplicate_extra_candidate_refused(self):
        for order in (['a', 'b'], ['a', 'a', 'c'], ['a', 'b', 'c', 'd'], ['a', 'b', 3]):
            data = fixture()
            data[0]['tasks'][0]['rankings']['normalized_bm25'] = order
            with self.subTest(order=order), self.assertRaisesRegex(ValueError, 'candidate universe'):
                evaluate.score(*data)

    def test_changed_question_duplicate_task_and_missing_method_refused(self):
        data = fixture()
        data[0]['tasks'][0]['question'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'query identity'):
            evaluate.score(*data)
        data = fixture()
        data[0]['tasks'].append(copy.deepcopy(data[0]['tasks'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate row'):
            evaluate.score(*data)
        data = fixture()
        del data[0]['tasks'][0]['rankings']['passage_rrf']
        with self.assertRaisesRegex(ValueError, 'method coverage'):
            evaluate.score(*data)

    def test_raw_reference_mismatch_is_not_comparable(self):
        data = fixture()
        data[4]['bm25'].reverse()
        with self.assertRaisesRegex(ValueError, 'retained experiment'):
            evaluate.score(*data)

    def test_gold_must_refer_to_real_sources(self):
        data = fixture()
        data[3]['tasks'][0]['required_evidence_groups'] = [['invented']]
        with self.assertRaisesRegex(ValueError, 'evidence groups'):
            evaluate.score(*data)

    def test_output_preflight_precedes_missing_input(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            path = Path(directory) / 'keep.json'
            path.write_text('keep')
            result = subprocess.run([sys.executable, '-B', str(Path(evaluate.__file__)),
                                     '--rankings', str(Path(directory) / 'absent'),
                                     '--output', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('output already exists', result.stderr)
            self.assertEqual(path.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
