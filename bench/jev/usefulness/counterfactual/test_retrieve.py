import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
import retrieve


class RetrievalTests(unittest.TestCase):
    def test_literal_bm25_scores_and_unique_query_terms(self):
        docs = [['alpha', 'beta'], ['gamma', 'beta'], ['delta', 'beta']]
        expected = math.log(8 / 3)
        self.assertAlmostEqual(retrieve.bm25(['alpha'], docs)[0], expected, places=13)
        self.assertEqual(retrieve.bm25(['alpha'], docs)[1:], [0.0, 0.0])
        self.assertEqual(retrieve.bm25(['alpha'], docs), retrieve.bm25(['alpha', 'alpha'], docs))

    def test_raw_reference_does_not_use_normalized_query(self):
        result = retrieve.rank(['a', 'b'], ['cat', 'the'], 'the')
        self.assertEqual(result['raw_bm25'], ['b', 'a'])
        self.assertEqual(result['normalized_bm25'], ['a', 'b'])

    def test_every_method_id_ties_survive_reordered_input(self):
        ids, texts = ['z', 'a', 'b'], ['same'] * 3
        forward = retrieve.rank(ids, texts, 'same')
        reverse = retrieve.rank(ids[::-1], texts[::-1], 'same')
        self.assertEqual(forward, reverse)
        for value in forward.values():
            self.assertEqual(value, ['a', 'b', 'z'])

    def test_identifier_parts_and_negation_no_plain_word_duplication(self):
        self.assertEqual(retrieve.norm_words('HTTPServer config_path'),
                         ['httpserver', 'http', 'server', 'config_path', 'config', 'path'])
        self.assertEqual(retrieve.norm_words('the safe safe'), ['safe', 'safe'])
        self.assertEqual(retrieve.norm_words('not-safe no never without cannot'),
                         ['not', 'safe', 'no', 'never', 'without', 'cannot'])
        self.assertEqual(retrieve.words('ČĆ_é'), ['čć_é'])

    def test_bm25_rejects_passage_string_list_as_documents(self):
        with self.assertRaisesRegex(ValueError, 'token lists'):
            retrieve.bm25(['needle'], ['needle', 'hay'])

    def test_passage_scores_cover_all_tokens_and_shared_idf(self):
        docs = [['alpha', 'beta'], ['gamma', 'beta'], ['delta', 'beta']]
        result = retrieve.passage_max_scores(['alpha'], docs)
        self.assertAlmostEqual(result[0], math.log(8 / 3), places=13)
        self.assertEqual(result[1:], [0.0, 0.0])
        late = retrieve.passage_max_scores(['needle'], [['hay'] * 128 + ['needle'], ['hay'] * 129])
        self.assertGreater(late[0], 0)
        self.assertEqual(late[1], 0)

    def test_passage_boundaries_and_empty_text(self):
        self.assertEqual([len(x) for x in retrieve.passages(['x'] * 192)], [128, 128, 64])
        self.assertEqual([len(x) for x in retrieve.passages(['x'] * 128)], [128, 64])
        self.assertEqual(retrieve.passages([]), [[]])
        self.assertEqual(retrieve.passage_max_scores(['x'], [[], []]), [0.0, 0.0])

    def test_mmr_diversifies_before_a_higher_scoring_duplicate(self):
        ids = ['a', 'b', 'c']
        vectors = [Counter({'shared': 1}), Counter({'shared': 1}), Counter({'distinct': 1})]
        selected, _ = retrieve.mmr_order(ids, [1.0, 0.99, 0.85], vectors)
        self.assertEqual([ids[index] for index in selected], ['a', 'c', 'b'])

    def test_mmr_zero_relevance_tie_uses_ids_not_input_index(self):
        ids = ['z', 'a', 'b']
        selected, _ = retrieve.mmr_order(ids, [0.0] * 3, [Counter()] * 3)
        self.assertEqual([ids[i] for i in selected], ['a', 'b', 'z'])

    def test_schema_rejects_duplicates_missing_nonstring_and_empty_universes(self):
        valid_task = {'tasks': [{'id': 'q', 'question': 'x'}]}
        for items in ([], [{'id': 'x', 'text': 'x'}, {'id': 'x', 'text': 'y'}],
                      [{'id': True, 'text': 'x'}], [{'id': ' ', 'text': 'x'}],
                      [{'id': 'x'}], [{'id': 'x', 'text': False}]):
            with self.subTest(items=items), self.assertRaises(ValueError):
                retrieve.validate({'items': items}, valid_task)

    def test_strict_json_duplicate_keys_and_nonfinite_values(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            path = Path(directory) / 'input.json'
            for body in ('{"id":"a","id":"b"}', '{"value":NaN}', '{"value":Infinity}'):
                path.write_text(body)
                with self.subTest(body=body), self.assertRaises(ValueError):
                    retrieve.strict_load(path)

    def test_metadata_does_not_enter_ranking(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            corpus, tasks = Path(directory) / 'corpus.json', Path(directory) / 'tasks.json'
            corpus.write_text(json.dumps({'items': [{'id': 'a', 'text': 'alpha'}, {'id': 'b', 'text': 'beta'}]}))
            tasks.write_text(json.dumps({'tasks': [{'id': 'q', 'question': 'alpha'}]}))
            before = retrieve.run(corpus, tasks)['tasks']
            corpus.write_text(json.dumps({'items': [{'id': 'a', 'text': 'alpha', 'path': 'irrelevant'}, {'id': 'b', 'text': 'beta', 'path': 'alpha'}]}))
            tasks.write_text(json.dumps({'tasks': [{'id': 'q', 'question': 'alpha', 'requested_facts': 'beta'}]}))
            self.assertEqual(before, retrieve.run(corpus, tasks)['tasks'])

    def test_public_cli_existing_and_dangling_output_rejected_before_inputs(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as directory:
            output = Path(directory) / 'keep.json'
            output.write_text('keep original')
            dangling = Path(directory) / 'dangling.json'
            dangling.symlink_to(Path(directory) / 'absent-target')
            for path in (output, dangling):
                result = subprocess.run([sys.executable, '-B', str(Path(retrieve.__file__)),
                                         '--corpus', str(Path(directory) / 'missing-corpus'),
                                         '--output', str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn('output already exists', result.stderr)
            self.assertEqual(output.read_text(), 'keep original')
            self.assertFalse((Path(directory) / 'absent-target').exists())


if __name__ == '__main__':
    unittest.main()
