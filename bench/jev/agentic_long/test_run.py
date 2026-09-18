"""Offline boundary tests. These do not establish model usefulness."""
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bench.jev.agentic_long import reader, run
from bench.jev.agentic_long.verify import verify


class AccountingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def event(self, identity='one', **changes):
        part = {'id': identity, 'cost': .25, 'tokens': {'total': 100, 'input': 10,
                'output': 5, 'reasoning': 2, 'cache': {'read': 80, 'write': 3}}}
        part.update(changes)
        return {'type': 'step_finish', 'sessionID': 'session', 'part': part}

    def test_cache_not_added_to_total_and_duplicates_not_charged_twice(self):
        path = self.root / 'events'
        row = json.dumps(self.event())
        path.write_text(row + '\n' + row + '\n{"partial":')
        actual = run.root_usage(path)
        self.assertEqual(actual['steps'], 1)
        self.assertEqual(actual['total'], 100)
        self.assertEqual(actual['cache_read'], 80)
        self.assertEqual(actual['known_cost'], .25)

    def test_conflicting_identity_is_rejected(self):
        path = self.root / 'events'
        path.write_text(json.dumps(self.event()) + '\n' + json.dumps(self.event(cost=.5)))
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            run.root_usage(path)

    def test_unknown_and_malformed_usage_is_not_zero(self):
        for cost in (None, -1, True, float('nan')):
            path = self.root / 'events'
            path.write_text(json.dumps(self.event(cost=cost)))
            actual = run.root_usage(path)
            self.assertEqual(actual['missing_usage'], 1)
            self.assertEqual(actual['known_cost'], 0)

    def test_reader_success_and_unresolved_intent_stay_separate(self):
        directory = self.root / 'readers'
        directory.mkdir()
        for i in range(2):
            (directory / ('%04d.intent.json' % i)).write_text('{}')
        (directory / '0000.result.json').write_text(json.dumps({'status': 'succeeded',
            'usage_complete': True, 'input_tokens': 20, 'output_tokens': 5, 'cost': .1}))
        actual = run.reader_usage(directory)
        self.assertEqual((actual['attempts'], actual['unresolved']), (2, 1))
        self.assertEqual(actual['known_input_tokens'], 20)

    def test_failed_unknown_reader_closes_admission(self):
        directory = self.root / 'readers'
        directory.mkdir()
        (directory / '0000.intent.json').write_text('{}')
        (directory / '0000.result.json').write_text(json.dumps({'status': 'failed',
            'usage_complete': False, 'input_tokens': None, 'output_tokens': None, 'cost': None}))
        (self.root / 'root-cost').write_text('0')
        with patch.dict(os.environ, PERF_READER_LOG=str(directory), PERF_DEADLINE='9999999999'), patch('sys.stdin', io.StringIO('source')), patch('urllib.request.urlopen') as network:
            with self.assertRaisesRegex(RuntimeError, 'admission_stopped'):
                reader.main()
            network.assert_not_called()
        self.assertTrue(reader.totals(directory)['terminal_failure'])

    def test_preparation_refuses_changed_binary_and_existing_output(self):
        with patch.object(run, 'BINARY_SHA', 'bad'):
            with self.assertRaisesRegex(ValueError, 'release_bytes'):
                run.prepare(self.root / 'out', self.root, self.root, self.root)
        with self.assertRaisesRegex(ValueError, 'new_and_outside'):
            run.prepare(self.root, self.root, self.root, self.root)

    def test_readmission_refused_before_credential_access(self):
        (self.root / 'admission.json').write_text('{}')
        (self.root / 'execution-intent.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'already_attempted'):
            run.execute(self.root, Path('/nonexistent'), Path('/nonexistent-secret'))

    def test_save_never_overwrites_original(self):
        path = self.root / 'result'
        run.save(path, {'first': True})
        with self.assertRaises(FileExistsError):
            run.save(path, {'first': False})
        self.assertEqual(json.loads(path.read_text()), {'first': True})

    def test_unknown_transport_usage_retained_and_not_returned_as_answer(self):
        directory = self.root / 'readers'
        directory.mkdir()
        (self.root / 'root-cost').write_text('0')
        auth = self.root / 'synthetic-auth.json'
        auth.write_text(json.dumps({'openrouter': {'key': 'synthetic-not-real'}}))
        response = io.BytesIO(json.dumps({'id': 'local-only', 'choices': [
            {'message': {'content': 'visible'}}]}).encode())
        with patch.dict(os.environ, PERF_READER_LOG=str(directory), PERF_AUTH=str(auth),
                        PERF_DEADLINE='9999999999'), patch('sys.stdin', io.StringIO('source')), \
             patch('sys.stdout', io.StringIO()) as output, \
             patch('urllib.request.urlopen', return_value=response) as network:
            self.assertEqual(reader.main(), 1)
            self.assertEqual(network.call_count, 1)
            self.assertEqual(output.getvalue(), '')
        result = json.loads((directory / '0000.result.json').read_text())
        self.assertFalse(result['usage_complete'])
        self.assertIsNone(result['input_tokens'])
        self.assertEqual(len(list(directory.glob('*.intent.json'))), 1)

    def test_exact_utf8_evidence_and_coverage_not_character_offsets(self):
        (self.root / 'corpus').mkdir()
        raw = 'é clause'.encode()
        (self.root / 'corpus/000.txt').write_bytes(raw)
        (self.root / 'risk.py').write_text('# not executed by structural check')
        (self.root / 'REPORT.md').write_text('000.txt 3 9 clause')
        rows = [{'file': '000.txt', 'size_bytes': len(raw),
                 'assignment': {'answer': 'yes', 'evidence': [{'start': 3, 'end': 9, 'quote': 'clause'}]},
                 'exclusivity': {'answer': 'no', 'evidence': []}}]
        path = self.root / 'risk.json'
        path.write_text(json.dumps(rows))
        self.assertTrue(verify(self.root, {'000.txt': None})['structural_acceptance'])
        rows[0]['assignment']['evidence'][0]['start'] = 2
        path.write_text(json.dumps(rows))
        self.assertFalse(verify(self.root, {'000.txt': None})['structural_acceptance'])
        self.assertFalse(verify(self.root, {'000.txt': None, '001.txt': None})['structural_acceptance'])


if __name__ == '__main__':
    unittest.main()
