import copy
import os
from pathlib import Path
import tempfile
import unittest

from bench.jev.long_task_salvage import extract as e


class ExtractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR'], prefix='leaf-extraction-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.public = self.root / 'public'
        self.private = self.root / 'jev-long-recovery-private-synthetic'
        self.sessions = self.private / 'generative/state/jcode-api/home/sessions'
        self.sessions.mkdir(parents=True)
        (self.public / 'generative').mkdir(parents=True)
        self.trace = self.public / 'generative/model-trace.jsonl'
        self.rows = []
        for index in range(75):
            sid = 'session_fixture_' + str(index)
            messages = [dict(role='user', display_role='system', content=[dict(type='text', text='PRIVATE_BOOTSTRAP')]),
                        self.message('user', '  wrapper\nsource-%d\n ' % index),
                        self.message('assistant', ' exact response %d\n' % index)]
            messages[-1]['content'] += [dict(type='reasoning_trace', text='PRIVATE_REASONING'),
                                       dict(type='open_a_i_reasoning', encrypted_content='PRIVATE_CIPHERTEXT')]
            self.write_session(index, {'id': sid, 'messages': messages, 'env_snapshots': 'PRIVATE_METADATA'})
            self.rows.append(dict(event='model_attempt', depth=1, outcome='succeeded',
                                  request_id='request-' + str(index), session_id=sid,
                                  timestamp_ms=int(e.timestamp(messages[-1])) + 1))
        self.write_trace()

    def message(self, role, value):
        return dict(role=role, content=[dict(type='text', text=value)], timestamp='2026-09-17T20:00:00.000000Z')

    def path(self, index):
        return self.sessions / ('session_fixture_%d.json' % index)

    def write_session(self, index, value):
        self.path(index).write_bytes(e.canonical(value))

    def read_session(self, index):
        return e.load(self.path(index).read_bytes())

    def write_trace(self):
        self.trace.write_bytes(b''.join(e.canonical(row) for row in self.rows))

    def extract(self):
        return e.extract(self.public, self.private, 'generative')

    def test_exact_text_order_hashes_and_no_private_metadata(self):
        before = {p: e.sha(p.read_bytes()) for p in [self.trace, *self.sessions.iterdir()]}
        value = self.extract()
        self.assertEqual((value['leaf_count'], value['unique_prompt_count']), (75, 75))
        first = value['records'][value['trace_order'][0]]
        self.assertEqual(first['prompt'], '  wrapper\nsource-0\n ')
        self.assertEqual(first['response'], ' exact response 0\n')
        self.assertEqual(first['occurrences'][0]['session_file_sha256'], before[self.path(0)])
        self.assertEqual(value['model_trace_sha256'], before[self.trace])
        self.assertEqual([x['trace_index'] for x in value['trace_mapping']], list(range(75)))
        self.assertNotIn(b'PRIVATE_', e.canonical(value))
        self.assertEqual(before, {p: e.sha(p.read_bytes()) for p in before})

    def test_bound_root_prefix_excluded(self):
        value = self.read_session(0)
        value['messages'][1:1] = [self.message('user', 'ROOT_PROMPT_NOT_LEAF'), self.message('assistant', 'ROOT_CODE_NOT_LEAF')]
        self.write_session(0, value)
        root = dict(self.rows[0], depth=0, request_id='root-request')
        self.rows.insert(0, root)
        self.write_trace()
        result = self.extract()
        self.assertEqual(result['leaf_count'], 75)
        self.assertNotIn(b'ROOT_PROMPT_NOT_LEAF', e.canonical(result))
        self.assertNotIn(b'ROOT_CODE_NOT_LEAF', e.canonical(result))
        self.assertEqual(result['trace_mapping'][0]['trace_index'], 1)

    def test_unbound_extra_turn_rejected(self):
        value = self.read_session(0)
        value['messages'][1:1] = [self.message('user', 'extra'), self.message('assistant', 'extra')]
        self.write_session(0, value)
        with self.assertRaisesRegex(e.Refused, 'unbound_session_turns'):
            self.extract()

    def test_duplicate_prompt_same_response_retains_multiplicity(self):
        first, second = self.read_session(0), self.read_session(1)
        second['messages'] = copy.deepcopy(first['messages'])
        self.write_session(1, second)
        result = self.extract()
        self.assertEqual(result['unique_prompt_count'], 74)
        self.assertEqual(len(result['trace_order']), 75)
        self.assertEqual(result['trace_order'][0], result['trace_order'][1])
        self.assertEqual(len(result['records'][result['trace_order'][0]]['occurrences']), 2)

    def test_duplicate_prompt_conflicting_response_rejected(self):
        first, second = self.read_session(0), self.read_session(1)
        second['messages'][-2] = copy.deepcopy(first['messages'][-2])
        self.write_session(1, second)
        with self.assertRaisesRegex(e.Refused, 'conflicting_duplicate_prompt'):
            self.extract()

    def test_multiple_text_blocks_or_tools_rejected(self):
        original = self.read_session(0)
        for extra in (dict(type='text', text='extra'), dict(type='tool_use', name='x')):
            value = copy.deepcopy(original)
            value['messages'][-1]['content'].append(extra)
            self.write_session(0, value)
            with self.assertRaises(e.Refused):
                self.extract()

    def test_missing_leaf_or_duplicate_identity_rejected(self):
        original = copy.deepcopy(self.rows)
        self.rows.pop()
        self.write_trace()
        with self.assertRaisesRegex(e.Refused, 'leaf_count'):
            self.extract()
        self.rows = original
        self.rows[-1] = dict(self.rows[0])
        self.write_trace()
        with self.assertRaisesRegex(e.Refused, 'duplicate_leaf_identity|unbound_session_turns'):
            self.extract()

    def test_timestamp_mismatch_rejected(self):
        self.rows[0]['timestamp_ms'] += 2000
        self.write_trace()
        with self.assertRaisesRegex(e.Refused, 'trace_turn_time_binding'):
            self.extract()

    def test_path_escape_and_symlink_rejected(self):
        original = self.rows[0]['session_id']
        self.rows[0]['session_id'] = '../outside'
        self.write_trace()
        with self.assertRaisesRegex(e.Refused, 'session_id'):
            self.extract()
        self.rows[0]['session_id'] = original
        self.write_trace()
        self.path(0).unlink()
        self.path(0).symlink_to(self.path(1))
        with self.assertRaisesRegex(e.Refused, 'symlink_refused'):
            self.extract()

    def test_secret_shaped_payload_rejected_before_output(self):
        value = self.read_session(0)
        value['messages'][-1]['content'][0]['text'] = 'sk-' + 'X' * 32
        self.write_session(0, value)
        with self.assertRaisesRegex(e.Refused, 'secret_shaped_output_refused'):
            self.extract()
        output = self.root / 'refused.json'
        with self.assertRaisesRegex(e.Refused, 'secret_shaped_output_refused'):
            e.save(output, {'response': 'apikey_synthetic_synthetic'})
        self.assertFalse(output.exists())

    def test_exclusive_private_output(self):
        value = self.extract()
        output = self.root / 'out.json'
        digest = e.save(output, value)
        self.assertEqual(digest, e.sha(output.read_bytes()))
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(FileExistsError):
            e.save(output, value)

    def test_duplicate_json_keys_and_failed_trace_rejected(self):
        with self.assertRaisesRegex(e.Refused, 'duplicate_json_key'):
            e.load(b'{"x":1,"x":2}')
        self.rows[0]['outcome'] = 'failed'
        self.write_trace()
        with self.assertRaisesRegex(e.Refused, 'unexpected_trace_event'):
            self.extract()


if __name__ == '__main__':
    unittest.main()
