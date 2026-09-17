import copy
import unittest

from bench.jev.span_selection import kernel as k


def fixture(text='default `alpha`; example `beta`; repeated `alpha`.'):
    return {'schema_version': 1, 'source_commit': 'a' * 40, 'tasks': [
        {'id': 's01', 'block': 1, 'family': 'GOLD_FAMILY_SENTINEL', 'question': 'Which value is the default?',
         'candidate_kind': 'quoted_literal', 'expected': 'MUST_NOT_REACH_MODEL',
         'source': {'path': 'docs/a.md', 'commit': 'a' * 40, 'start_line': 1, 'end_line': 1,
                    'text': text, 'sha256': k.sha(text.encode()), 'rationale': 'SECRET_GOLD'}}]}


class KernelTests(unittest.TestCase):
    def test_duplicate_occurrences_and_unicode_offsets(self):
        text = 'Žđ `alpha` then `alpha`'
        rows = k.candidates(text, 'quoted_literal')
        self.assertEqual([r['text'] for r in rows], ['alpha', 'alpha'])
        self.assertEqual([r['start'] for r in rows], [4, 17])
        self.assertEqual(rows[0]['byte_start'], 6)
        self.assertNotEqual(rows[0]['id'], rows[1]['id'])
        for row in rows:
            self.assertEqual(text.encode()[row['byte_start']:row['byte_end']].decode(), row['text'])

    def test_versions_and_quote_escape_are_verbatim(self):
        self.assertEqual([r['text'] for r in k.candidates('v0.1.17 1.95 2.3.4-rc1 a2.3', 'version')],
                         ['v0.1.17', '1.95', '2.3.4-rc1'])
        self.assertEqual(k.candidates('"a\\\"b"', 'quoted_literal')[0]['text'], 'a\\\"b')
        self.assertEqual(k.candidates('```\ncode\n```', 'quoted_literal'), [])

    def test_no_candidate_truncation(self):
        with self.assertRaisesRegex(ValueError, 'refusing to truncate'):
            k.candidates(' '.join('`x`' for _ in range(129)), 'quoted_literal')

    def test_family_and_gold_never_enter_model_pack(self):
        pack = k.prepare(fixture())
        raw = k.canonical({'state': pack, 'questions': k.questions(pack)}).decode()
        for hidden in ('GOLD_FAMILY_SENTINEL', 'MUST_NOT_REACH_MODEL', 'SECRET_GOLD', 'family', 'rationale'):
            self.assertNotIn(hidden, raw)
        self.assertIn('Which value is the default?', raw)

    def test_rejects_mutated_source_and_duplicate_task_ids(self):
        doc = fixture()
        doc['tasks'][0]['source']['text'] += '!'
        with self.assertRaisesRegex(ValueError, 'source digest'):
            k.prepare(doc)
        doc = fixture()
        doc['tasks'].append(copy.deepcopy(doc['tasks'][0]))
        with self.assertRaisesRegex(ValueError, 'task identity'):
            k.prepare(doc)

    def test_strict_response_json_and_id_coverage(self):
        for raw in ('{"s01":"c000","s01":"c001"}', '{"a":NaN}', '{"a":Infinity}'):
            with self.assertRaises(ValueError):
                k.strict_loads(raw)
        pack = k.prepare(fixture())
        for selected in ({}, {'s01': 'c000', 's02': 'c000'}, {'s01': 'invented'}, {'s01': True}):
            with self.assertRaises(ValueError):
                k.materialize(pack, selected)

    def test_copying_wrong_valid_id_is_not_correctness(self):
        pack = k.prepare(fixture())
        correct = pack['tasks'][0]['candidates'][0]
        gold = {'tasks': [{'id': 's01', 'expected': 'alpha', 'acceptable_spans': [
            {'start': correct['start'], 'end': correct['end']}]}]}
        k.validate_gold(pack, gold)
        wrong = k.materialize(pack, {'s01': 'c001'})
        self.assertEqual(wrong[0]['value'], 'beta')
        self.assertEqual(k.grade(wrong, gold)['correct'], 0)
        unsupported_duplicate = k.materialize(pack, {'s01': 'c002'})
        report = k.grade(unsupported_duplicate, gold)
        self.assertTrue(report['rows'][0]['value_correct'])
        self.assertFalse(report['rows'][0]['provenance_correct'])

    def test_sentinels_are_not_unjudged_and_preserve_source_pool(self):
        pack = k.prepare(fixture())
        before = copy.deepcopy(pack)
        for choice in k.SENTINELS:
            rows = k.materialize(pack, {'s01': choice})
            self.assertEqual(rows[0]['status'], choice)
            self.assertIsNone(rows[0]['value'])
            gold = {'tasks': [{'id': 's01', 'expected': choice, 'acceptable_spans': []}]}
            k.validate_gold(pack, gold)
            self.assertEqual(k.grade(rows, gold)['correct'], 1)
            self.assertEqual(k.grade([], gold)['unjudged'], 1)
        self.assertEqual(pack, before)

    def test_materializer_rejects_bad_offsets_and_changed_sources(self):
        for field, value in [('start', -1), ('end', 10000), ('byte_start', True), ('byte_end', -1), ('text', 'forged')]:
            pack = k.prepare(fixture())
            pack['tasks'][0]['candidates'][0][field] = value
            with self.assertRaises(ValueError):
                k.materialize(pack, {'s01': 'c000'})
        pack = k.prepare(fixture())
        pack['tasks'][0]['source']['text'] = 'other'
        with self.assertRaisesRegex(ValueError, 'changed source'):
            k.materialize(pack, {'s01': 'c000'})

    def test_omitted_candidate_is_not_a_claim_of_absent_source_value(self):
        pack = k.prepare(fixture())
        pack['tasks'][0]['candidates'] = [pack['tasks'][0]['candidates'][1]]
        criteria = k.questions(pack)['s01']['criteria']
        self.assertIn('absent from the supplied source', criteria['no_match'])
        self.assertIn('missing from the supplied candidates', criteria['not_covered'])
        rows = k.materialize(pack, {'s01': 'not_covered'})
        self.assertEqual(rows[0]['status'], 'not_covered')
        self.assertIsNone(rows[0]['value'])
        self.assertIn('alpha', pack['tasks'][0]['source']['text'])

    def test_literal_baseline_zero_overlap_ties_and_role_distance(self):
        pack = k.prepare(fixture('`alpha` then `beta`'))
        pack['tasks'][0]['question'] = 'Who signed?'  # no overlap
        self.assertEqual(k.lexical(pack), {'s01': 'no_match'})
        pack['tasks'][0]['question'] = 'alpha or beta?'
        self.assertEqual(k.lexical(pack), {'s01': 'ambiguous'})
        pack = k.prepare(fixture('default `alpha` ' + 'z' * 240 + ' example `beta`'))
        self.assertEqual(k.lexical(pack), {'s01': 'c000'})

    def test_gold_must_have_representable_provenance(self):
        pack = k.prepare(fixture())
        for gold in ({'tasks': []}, {'tasks': [{'id': 's01', 'expected': 'alpha', 'acceptable_spans': []}]},
                     {'tasks': [{'id': 's01', 'expected': 'no_match', 'acceptable_spans': [{'start': 9, 'end': 14}]}]}):
            with self.assertRaises(ValueError):
                k.validate_gold(pack, gold)


if __name__ == '__main__':
    unittest.main()
