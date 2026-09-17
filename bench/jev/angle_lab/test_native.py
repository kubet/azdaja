"""Offline tests. No transport is entered and no real credential is read."""
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from . import native as n

PACK = {'state': {'text': 'public source'}, 'questions': {
    'q': {'type': 'noul', 'instructions': 'Is text public?'}}}


class NativeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR'))
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.txt'
        self.source.write_text('frozen source')
        self.frozen = {str(self.source): n.sha(self.source.read_bytes())}

    def tearDown(self):
        self.temp.cleanup()

    def campaign(self):
        return n.Campaign(sys.executable, self.root / 'out', self.frozen, authorized=True)

    def test_authorization_before_output_or_process(self):
        with self.assertRaisesRegex(n.Stop, 'authorization'):
            n.Campaign(sys.executable, self.root / 'out', self.frozen)
        self.assertFalse((self.root / 'out').exists())

    def test_frozen_manifest_checked_before_output(self):
        self.source.write_text('mutation')
        with self.assertRaisesRegex(n.Stop, 'frozen_manifest_invalid'):
            self.campaign()
        self.assertFalse((self.root / 'out').exists())

    def test_dangling_output_symlink_refused(self):
        (self.root / 'out').symlink_to(self.root / 'missing')
        with self.assertRaisesRegex(n.Stop, 'output_exists'):
            self.campaign()
        self.assertFalse((self.root / 'missing').exists())

    def test_runtime_source_change_poisoned(self):
        c = self.campaign()
        self.source.write_text('mutation')
        with self.assertRaisesRegex(n.Stop, 'frozen_source_changed'):
            c.command(['--version'])
        self.assertTrue(c.stopped)
        with self.assertRaisesRegex(n.Stop, 'session_stopped'):
            c.start()

    def test_semantic_validation_error_is_terminal(self):
        c = self.campaign()
        with self.assertRaisesRegex(n.Stop, 'request_contract'):
            c.typed('bad', {'state': 'x', 'questions': {}})
        self.assertTrue(c.stopped)
        self.assertEqual(c.receipt['typed_calls_started'], 0)
        with self.assertRaisesRegex(n.Stop, 'session_stopped'):
            c.generate('not-allowed', PACK)
        with self.assertRaisesRegex(n.Stop, 'cannot_report'):
            c.finish('completed')

    def test_keyboard_interrupt_does_not_leave_usable_campaign(self):
        c = self.campaign()
        with patch.object(c, 'configure', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                c.typed('interrupted', PACK)
        self.assertTrue(c.stopped)
        self.assertEqual(c.receipt['status'], 'stopped')

    def test_output_limit_and_timeout_reap_local_children(self):
        for text, timeout, reason in [
            ("print('x'*300000)", 2, 'output_limit'),
            ('import time; time.sleep(30)', .08, 'deadline'),
        ]:
            created = []
            real = n.subprocess.Popen
            def spawn(*args, **kwargs):
                child = real(*args, **kwargs)
                created.append(child)
                return child
            start = time.monotonic()
            with patch.object(n.subprocess, 'Popen', side_effect=spawn):
                with self.assertRaisesRegex(n.Stop, reason):
                    n.bounded_process([sys.executable, '-c', text], code='', cwd=self.root,
                                      env={}, timeout=timeout)
            self.assertLess(time.monotonic() - start, 3)
            self.assertIsNotNone(created[0].returncode)

    def test_bounded_process_returns_actual_output(self):
        out = n.bounded_process([sys.executable, '-c', 'import sys; print(sys.stdin.read())'],
                               code='public', cwd=self.root, env={}, timeout=2)
        self.assertEqual(out.stdout.strip(), 'public')
        self.assertEqual(out.returncode, 0)

    def test_unknown_trace_usage_not_zero_and_retry_ordinals(self):
        path = self.root / 'trace.jsonl'
        events = [
            {'event': 'model_attempt', 'request_id': 'one', 'attempt': 1,
             'outcome': 'failed'},
            {'event': 'model_attempt', 'request_id': 'one', 'attempt': 2,
             'entered_turn': 1, 'outcome': 'failed'},
            {'event': 'model_attempt', 'request_id': 'one', 'attempt': 3,
             'entered_turn': 2, 'outcome': 'succeeded', 'model': n.GENERATOR,
             'provider': 'OpenAI', 'input_tokens': 10, 'output_tokens': 4},
        ]
        path.write_text('\n'.join(json.dumps(e) for e in events))
        trace = n.usage_summary(path)
        self.assertEqual(trace['entered_turns'], 2)
        self.assertEqual(trace['setup_attempts'], 1)
        self.assertEqual(trace['usage']['input_tokens']['known_total'], 10)
        self.assertEqual(trace['usage']['input_tokens']['unknown_entered_events'], 1)
        self.assertEqual(trace['usage']['cache_read_tokens']['unknown_entered_events'], 2)
        self.assertEqual(trace['succeeded_events'], 1)

    def test_pack_limits_and_credential_pattern(self):
        for pack, reason in [
            ({**PACK, 'model': 'jev-latest'}, 'request_contract'),
            ({**PACK, 'state': 'x' * 24001}, 'request_budget'),
            ({**PACK, 'state': 'apikey_synthetic_only'}, 'credential_pattern'),
        ]:
            with self.assertRaisesRegex(n.Stop, reason):
                n.inspect_pack(pack)

    def test_public_persistent_cli_without_any_model_turn(self):
        binary = os.environ.get('AZDAJA_ANGLE_BINARY')
        if not binary:
            self.skipTest('explicit tested binary required for public acceptance')
        c = n.Campaign(binary, self.root / 'out', self.frozen, authorized=True)
        c.start()
        c.load('source', {'items': ['a', 'b', 'a']})
        first = n.strict_loads(c.cell('count', 'items = json.loads(source)["items"]\nFINAL({"count":len(items),"unique":len(set(items)),"stats":judge_stats()})\n'))
        second = n.strict_loads(c.cell('retained', 'FINAL(items)\n'))
        self.assertEqual((first['count'], first['unique']), (3, 2))
        self.assertEqual(second, ['a', 'b', 'a'])
        self.assertEqual(first['stats']['attempts'], 0)
        c.finish('offline_workflow_passed')
        self.assertEqual(c.receipt['cleanup_exit'], 0)
        self.assertEqual(c.receipt['logical_llm_calls'], 0)

    def test_every_pack_reaches_native_credential_guard_without_transport(self):
        binary = os.environ.get('AZDAJA_ANGLE_BINARY')
        if not binary:
            self.skipTest('explicit tested binary required')
        from .gate import prepare_grade as gate
        from .verifier import prepare as verifier
        from .descent import run as descent
        from .memory import slice as memory
        c = n.Campaign(binary, self.root / 'out', self.frozen, authorized=True)
        caps = n.strict_loads(c.command(['doctor', '--caps']))
        if not caps['typed_judgments']['typesafe_compiled']:
            self.skipTest('explicit typesafe build required for native validator path')
        c.env['TYPESAFE_API_KEY'] = 'apikey_SYNTHETIC_PREFLIGHTONLY'
        c.start()
        tree = descent.corpus()
        packs = gate.packs() + [gate.calibration(), verifier.make_pack(), descent.flat_pack(tree),
                                descent.root_pack(tree), memory.request(memory.load_raw())]
        for i, pack in enumerate(packs):
            request = json.loads(json.dumps(pack))
            request['state']['_preflight_guard'] = c.env['TYPESAFE_API_KEY']
            c.configure(True)
            c.load('preflight', request)
            report = n.strict_loads(c.cell(f'guard-{i}',
                'p=json.loads(preflight)\nerror=None\ntry:\n    judge_many(p["state"],p["questions"])\nexcept Exception as e:\n    error=str(e)\nFINAL({"error":error,"stats":judge_stats()})\n'))
            self.assertEqual(report['error'], 'judge: credential leakage refused')
            self.assertEqual(report['stats']['attempts'], 0)
        c.finish('offline_native_pack_validation_passed')


if __name__ == '__main__':
    unittest.main()
