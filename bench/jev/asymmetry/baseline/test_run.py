import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from bench.jev.asymmetry.baseline import run as r
from bench.jev.angle_lab import native as n


def pack():
    return {'state': {'records': {'r0005': 'Date: example || Instance: hi\n'}},
            'questions': {'r0005': r.prepare.question('r0005')}}


def trace(completed=0, input_tokens=0, output_tokens=0, unknown=0):
    usage = {f: {'known_total': 0, 'observed_events': completed, 'unknown_entered_events': 0}
             for f in ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'reasoning_tokens')}
    usage['input_tokens'].update(known_total=input_tokens, unknown_entered_events=unknown)
    usage['output_tokens']['known_total'] = output_tokens
    return {'entered_turns': completed, 'physical_attempt_events': completed, 'setup_attempts': 0,
            'failed_identity_unknown_events': 0, 'logical_request_ids': completed,
            'succeeded_events': completed, 'usage': usage,
            'observed_models': [r.GENERATOR] if completed else [],
            'observed_providers': ['OpenAI'] if completed else []}


def fake_campaign(raw='{"r0005":"yes"}'):
    c = object.__new__(r.Campaign)
    c.stopped = False; c.started = time.monotonic()
    c.output = Path('/unused-offline-test')
    c.receipt = {'logical_llm_calls': 0, 'calls': [], 'status': 'running'}
    c.checkpoint = lambda: None
    saved = {}; loaded = {}; calls = []
    c.save = lambda name, value: saved.__setitem__(name, copy.deepcopy(value))
    c.configure = lambda enabled: r.check(not enabled, 'judge_disabled')
    c.load = lambda name, value: loaded.__setitem__(name, copy.deepcopy(value))
    def cell(name, code):
        calls.append(name)
        if name.endswith('-reentry'):
            value = loaded['binding_payload']
            return json.dumps({'binding_sha256': n.sha(n.canonical(value)), 'answer': value['answer'], 'attempts': 0})
        return raw
    c.cell = cell
    return c, saved, calls


class BaselineTests(unittest.TestCase):
    def test_public_default_and_missing_ack_do_not_admit(self):
        for args, code in (([], 0), (['--live'], 2)):
            out = subprocess.run([sys.executable, '-B', '-m', 'bench.jev.asymmetry.baseline.run', *args],
                                 cwd=r.ROOT, capture_output=True, timeout=10)
            self.assertEqual(out.returncode, code)
            if not args:
                self.assertEqual(json.loads(out.stdout)['provider_calls'], 0)
            else:
                self.assertIn(b'live requires acknowledgement', out.stderr)

    def test_all_actual_inputs_equal_prior_jev_requests(self):
        rows = r.rows()
        self.assertEqual(len(rows), 112)
        self.assertEqual(sum(len(p['questions']) for _, p in rows), 17469)
        self.assertTrue(any(len(p['questions']) > 64 for _, p in rows))
        for name, p in rows:
            old = n.strict_loads((r.TYPED_RECEIPT / (name + '-request.json')).read_bytes())
            self.assertEqual(n.canonical(p), n.canonical({'state': old['state'], 'questions': old['questions']}))

    def test_question_binding_not_just_shape(self):
        p = pack(); p['questions']['r0005']['instructions'] = 'Is it ham?'
        with self.assertRaisesRegex(n.Stop, 'question_source_binding'): r.validate_pack(p)
        p = pack(); p['questions']['r0005'] = r.prepare.question('r0006')
        with self.assertRaisesRegex(n.Stop, 'question_source_binding'): r.validate_pack(p)

    def test_answers_reorder_safely_but_bad_domains_and_coverage_reject(self):
        self.assertEqual(r.validate_answer('{"b":"no","a":"yes"}', ['a', 'b']), {'a': 'yes', 'b': 'no'})
        for raw in ('{}', '{"a":"yes","b":"no"}', '{"a":true}', '{"a":0.5}', '{"a":"maybe"}'):
            with self.assertRaises(n.Stop): r.validate_answer(raw, ['a'])
        with self.assertRaises(ValueError): r.validate_answer('{"a":"yes","a":"no"}', ['a'])

    def test_success_persists_raw_trace_and_reenters(self):
        c, saved, calls = fake_campaign()
        with patch.object(n, 'usage_summary', side_effect=[trace(), trace(1, 100, 3)]):
            self.assertEqual(c.generate('pack-001', pack()), {'r0005': 'yes'})
        self.assertEqual(calls, ['pack-001', 'pack-001-reentry'])
        self.assertEqual(saved['pack-001-raw.json'], {'text': '{"r0005":"yes"}'})
        self.assertEqual(c.receipt['calls'][0]['usage']['input_tokens']['known_total'], 100)
        self.assertEqual(c.receipt['calls'][0]['status'], 'completed')
        self.assertEqual(saved['pack-001-prompt.json']['payload'], pack())

    def test_crossing_and_unknown_accounting_preserved_then_no_next_call(self):
        for after, error in ((trace(1, r.MAX_INPUT + 1, 3), 'generative_token_cap'),
                             (trace(1, 100, 3, unknown=1), 'generative_unknown_usage')):
            c, saved, calls = fake_campaign()
            with patch.object(n, 'usage_summary', side_effect=[trace(), after]) as summary:
                with self.assertRaisesRegex(n.Stop, error): c.generate('pack-001', pack())
                self.assertTrue(c.stopped)
                self.assertIn('pack-001-raw.json', saved)
                self.assertEqual(c.receipt['calls'][0]['usage']['input_tokens']['known_total'], after['usage']['input_tokens']['known_total'])
                with self.assertRaisesRegex(n.Stop, 'session_stopped'): c.generate('pack-002', pack())
                self.assertEqual(summary.call_count, 2)
            self.assertEqual(calls, ['pack-001'])

    def test_invalid_model_and_response_stop_before_reentry(self):
        for raw, model in (('{"r0005":true}', r.GENERATOR), ('{"r0005":"yes"}', 'wrong-model')):
            c, saved, calls = fake_campaign(raw)
            after = trace(1, 100, 3); after['observed_models'] = [model]
            with patch.object(n, 'usage_summary', side_effect=[trace(), after]):
                with self.assertRaises(n.Stop): c.generate('pack-001', pack())
            self.assertEqual(calls, ['pack-001']); self.assertTrue(c.stopped)
            self.assertIn('pack-001-raw.json', saved)

    def test_failed_cell_retains_trace_and_cannot_continue(self):
        c, saved, calls = fake_campaign()
        c.cell = lambda *args: (_ for _ in ()).throw(n.Stop('process_deadline'))
        after = trace(1, 99, 0); after['succeeded_events'] = 0
        with patch.object(n, 'usage_summary', side_effect=[trace(), after]):
            with self.assertRaisesRegex(n.Stop, 'process_deadline'): c.generate('pack-001', pack())
        self.assertTrue(c.stopped)
        self.assertEqual(c.receipt['calls'][0]['usage']['input_tokens']['known_total'], 99)

    def test_typed_is_structurally_disabled(self):
        c = object.__new__(r.Campaign)
        with self.assertRaisesRegex(n.Stop, 'typed_disabled'): c.typed('a', pack())
        with self.assertRaisesRegex(n.Stop, 'judge_disabled'): c.configure(True)

    def test_incomplete_cannot_be_reported_complete(self):
        c, _, _ = fake_campaign()
        c.receipt['native_reduction'] = {'complete': False, 'observed': 17468}
        with self.assertRaisesRegex(n.Stop, 'final_reduction_incomplete'): c.finish('completed')

    def test_cell_deadline_is_shared(self):
        c, _, _ = fake_campaign()
        c.left = lambda: 1000
        invocations = []
        c.command = lambda args, code='', timeout=0: invocations.append((args[0], timeout)) or '{}'
        c.sid = 'fake'
        with patch.object(r.time, 'monotonic', side_effect=[0, 0, 119]):
            r.Campaign.cell(c, 'x', 'FINAL({})')
        self.assertEqual(invocations, [('exec', 120), ('final', 1)])

    def test_live_exercise_invokes_generation_not_offline(self):
        class Fake:
            receipt = {}
            def start(self): pass
            def checkpoint(self): pass
            def generate(self, name, p): self.generated.append(name)
            generated = []
        c = Fake()
        with patch.object(r, 'reduce_ids', return_value={'ham': 0}), contextlib.redirect_stdout(io.StringIO()):
            r.exercise(c, [('pack-001', pack())], True)
        self.assertEqual(c.generated, ['pack-001'])
        self.assertEqual(c.receipt['panel_rows'][0]['status'], 'completed')

    def test_started_marker_blocks_fresh_output_before_campaign(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            root = Path(tmp); home = root / 'profile'; home.mkdir()
            (home / 'openai-auth.json').write_text('{}')
            manifest = root / 'FROZEN.json'
            prepared = [('pack-001', pack())]
            manifest.write_bytes(n.canonical({'files': {}, 'panel': r.panel_identity(prepared), 'instruction': r.INSTRUCTION}))
            manifest.with_suffix('.started').write_text('preserve')
            with patch.object(r, 'rows', return_value=prepared), patch.object(r, 'inventory', return_value={}), \
                 patch.object(r, 'Campaign', side_effect=AssertionError('must not start')):
                with self.assertRaises(FileExistsError):
                    r.main(['--live', '--acknowledge-provider-calls', '--azdaja', '/unused',
                            '--output', str(root/'fresh'), '--manifest', str(manifest), '--private-jcode-home', str(home)])
            self.assertEqual(manifest.with_suffix('.started').read_text(), 'preserve')
            self.assertFalse((root/'fresh').exists())


if __name__ == '__main__': unittest.main()
