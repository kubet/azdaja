"""Synthetic suffix mutations. Never read the live continuation or call a provider."""
import copy
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from . import replay as r
from bench.jev.span_selection.run import Stop as TraceStop


def save(path, value):
    path.write_bytes(r.canonical(value) + b'\n')


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage = tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR'))
        cls.template = Path(cls.storage.name) / 'synthetic-completed'
        cls.template.mkdir()
        cls.prepared = r.packs()
        prior, prefix, _ = r.c.check_prefix()
        events, _ = r._trace(r.c.PREVIOUS / 'model-trace.jsonl')
        receipt = copy.deepcopy(prior)
        receipt.update(status='completed', cleanup_exit=0, logical_llm_calls=112,
                       elapsed_seconds=3000, calls=[], panel_rows=[])
        seal = r.HERE / 'CONTINUATION-FROZEN.json'
        receipt['frozen_files'] = {**r.load(seal)['files'], str(seal.resolve()): r.sha(seal)}
        receipt['continuation'] = {'schema': 'azdaja.asymmetry.suffix_recovery.v1',
            'predecessor': str(r.c.PREVIOUS.relative_to(r.ROOT)), 'predecessor_logical_calls': 25,
            'interruption_sha256': r.sha(r.c.PREVIOUS / 'external-interruption.json'),
            'absolute_deadline_unix': r.c.DEADLINE, 'budgets_reset': False,
            'original_uninterrupted_run': False}
        ham = 0
        for i, (name, pack) in enumerate(cls.prepared):
            answer = prefix[i] if i < 25 else {q: 'yes' if int(q[1:]) % 3 else 'no' for q in pack['questions']}
            ham += sum(v == 'yes' for v in answer.values())
            if i >= 25:
                event = copy.deepcopy(events[0])
                event.update(request_id='synthetic-' + name, input_tokens=100, output_tokens=50, latency_ms=1200)
                events.append(event)
            if i < 24:
                call = copy.deepcopy(prior['calls'][i])
            else:
                before, after = r.summary(events[:i]), r.summary(events[:i + 1])
                call = {'name': name, 'arm': 'generative', 'status': 'completed',
                    'pack_sha256': r.n.sha(r.n.canonical(pack)),
                    'prompt_bytes': len(r.b.INSTRUCTION.encode()) + len(r.n.canonical(pack)),
                    'questions': len(pack['questions']), 'seconds': 1.5,
                    'answer_sha256': r.n.sha(r.n.canonical(answer)), 'usage': r._delta(after, before)}
                call.update({k: after[k] - before[k] for k in r.COUNTERS})
                if i == 24:
                    call.update(seconds=None, controller_latency_known=False,
                                recovered_native_latency_seconds=events[i]['latency_ms'] / 1000)
            receipt['calls'].append(call)
            receipt['panel_rows'].append({'name': name, 'status': 'completed',
                'pack_sha256': r.n.sha(r.n.canonical(pack)), 'ids': sorted(pack['questions'])})
            save(cls.template / (name + '-prompt.json'), {'instruction': r.b.INSTRUCTION, 'payload': pack})
            save(cls.template / (name + '-raw.json'), {'text': r.canonical(answer).decode()})
            save(cls.template / (name + '-answer.json'), answer)
            binding = {'name': name, 'answer': answer, 'ids': sorted(pack['questions'])}
            save(cls.template / (name + '-reentry.json'), {'answer': answer, 'attempts': 0,
                'binding_sha256': r.n.sha(r.n.canonical(binding))})
        receipt['generative_trace'] = r.summary(events)
        reduction = {'expected': 17469, 'observed': 17469, 'complete': True, 'ham': ham,
                     'answer': 'Answer: ' + str(ham), 'attempts_in_reduction': 0}
        receipt['native_reduction'] = reduction
        save(cls.template / 'final-reduction.json', reduction)
        save(cls.template / 'receipt.json', receipt)
        cls.events, cls.receipt = events, receipt
        (cls.template / 'model-trace.jsonl').write_bytes(b'\n'.join(r.canonical(e) for e in events) + b'\n')

    @classmethod
    def tearDownClass(cls):
        cls.storage.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR'))
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name) / 'receipt'
        shutil.copytree(self.template, self.folder)
        for owner in (r.b, r.c, r.n):
            guard = patch.object(owner, 'Campaign', side_effect=AssertionError('live Campaign forbidden'))
            guard.start()
            self.addCleanup(guard.stop)

    def change(self, name, fn):
        path = self.folder / name
        obj = r.load(path)
        fn(obj)
        save(path, obj)

    def rc(self, fn):
        self.change('receipt.json', fn)

    def reject(self, pattern):
        with self.assertRaisesRegex((ValueError, r.n.Stop), pattern):
            r.replay(self.folder)

    def write_events(self, events):
        (self.folder / 'model-trace.jsonl').write_bytes(b'\n'.join(r.canonical(e) for e in events) + b'\n')

    def test_complete_synthetic_suffix_and_three_same_id_matrices(self):
        out = r.replay(self.folder)
        self.assertTrue(out['complete_panel'])
        self.assertEqual(out['eligible_packs'], 112)
        m = out['metrics']
        for key in ('baseline', 'original_p_ge_0.5', 'declared_transferred'):
            self.assertEqual(m[key]['observed'], 17469)
            self.assertEqual(sum(m[key][k] for k in ('tp', 'tn', 'fp', 'fn')), 17469)
        self.assertNotEqual(m['baseline']['predicted_ham'], m['declared_transferred']['predicted_ham'])
        self.assertNotEqual(m['original_p_ge_0.5']['predicted_ham'], m['declared_transferred']['predicted_ham'])
        self.assertEqual(out['usage'], r.summary(self.events))
        self.assertEqual(out['timing']['unknown_controller_durations'], 1)
        self.assertIsNone(out['timing']['calls'][24]['controller_seconds'])
        self.assertIsNone(out['baseline_subscription_cost_usd'])

    def test_forged_completed_reduction_even_when_receipt_and_file_agree(self):
        for field, value in (('ham', -1), ('observed', 1), ('expected', 1), ('complete', False),
                             ('answer', 'Answer: 0'), ('attempts_in_reduction', 1)):
            with self.subTest(field=field):
                bad = {**self.receipt['native_reduction'], field: value}
                save(self.folder / 'final-reduction.json', bad)
                self.rc(lambda x: x.update(native_reduction=bad))
                self.reject('forged final reduction')

    def test_completed_full_wall_must_respect_original_deadline(self):
        self.rc(lambda x: x.update(elapsed_seconds=r.b.MAX_SECONDS + 1))
        self.reject('completed campaign deadline')

    def test_stopped_deadline_overrun_is_retained_without_completion(self):
        self.rc(lambda x: x.update(status='stopped', elapsed_seconds=r.b.MAX_SECONDS + 1))
        out = r.replay(self.folder)
        self.assertFalse(out['complete_panel'])
        self.assertTrue(out['partial'])
        self.assertEqual(out['timing']['interrupted_full_wall_seconds'], r.b.MAX_SECONDS + 1)
        self.assertEqual(out['usage'], r.summary(self.events))

    def test_prompt_instruction_source_and_question_mutations(self):
        path = self.folder / 'pack-026-prompt.json'
        original = r.load(path)
        qid = next(iter(original['payload']['questions']))
        for mutate in (lambda x: x.update(instruction='changed'),
                       lambda x: x['payload']['state']['records'].update({qid: 'changed source'}),
                       lambda x: x['payload']['questions'][qid].update(instructions='changed question')):
            obj = copy.deepcopy(original)
            mutate(obj)
            save(path, obj)
            self.reject('prompt source/question/instruction')

    def test_missing_trace_and_receipt_trace_mutation(self):
        (self.folder / 'model-trace.jsonl').unlink()
        self.reject('model trace missing')
        self.write_events(self.events)
        self.rc(lambda x: x['generative_trace'].update(entered_turns=999))
        self.reject('receipt trace mismatch')

    def test_invalid_usage_rejected_by_native(self):
        for value in (-1, True, '12'):
            events = copy.deepcopy(self.events)
            events[25]['input_tokens'] = value
            self.write_events(events)
            self.reject('generative_usage_contract')

    def test_call_trace_delta_mismatch(self):
        self.rc(lambda x: x['calls'][25]['usage']['input_tokens'].update(known_total=101))
        self.reject('call trace usage')

    def test_duplicate_trace_and_duplicate_panel_ids(self):
        self.write_events(self.events + [self.events[-1]])
        self.reject('duplicate native attempt ID')
        self.write_events(self.events)
        self.rc(lambda x: x['panel_rows'][26].update(name='pack-026'))
        self.reject('duplicate or unordered pack IDs')

    def test_raw_duplicate_key_and_missing_extra_ids(self):
        path = self.folder / 'pack-026-raw.json'
        answer = r.load(self.folder / 'pack-026-answer.json')
        qid = next(iter(answer))
        for text in ('{"%s":"yes","%s":"no"}' % (qid, qid),
                     r.canonical({k: v for k, v in answer.items() if k != qid}).decode(),
                     r.canonical({**answer, 'extra': 'yes'}).decode()):
            save(path, {'text': text})
            self.reject('invalid validated raw')

    def test_duplicate_receipt_key_rejected(self):
        (self.folder / 'receipt.json').write_text('{"status":"stopped","status":"completed"}')
        self.reject('duplicate JSON key')

    def test_answer_and_reentry_mutations(self):
        self.change('pack-026-reentry.json', lambda x: x.update(attempts=True))
        self.reject('native reentry mismatch')
        shutil.copyfile(self.template / 'pack-026-reentry.json', self.folder / 'pack-026-reentry.json')
        self.change('pack-026-answer.json', lambda x: x.update(extra='no'))
        self.reject('answer mismatch')

    def test_frozen_marker_missing_without_touching_real_marker(self):
        original = Path.is_file
        for marker in ('FROZEN.started', 'CONTINUATION-FROZEN.started'):
            with self.subTest(marker=marker), patch.object(Path, 'is_file',
                    lambda p: False if p.name == marker else original(p)):
                self.reject('frozen source changed|started missing')

    def test_frozen_source_and_gold_hash(self):
        source = str(r.b.prepare.SOURCE.resolve())
        self.rc(lambda x: x['frozen_files'].update({source: '0' * 64}))
        self.reject('frozen source changed')
        gold = Path(self.tmp.name) / 'result.json'
        gold.write_bytes(r.FROZEN_LABELS.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'gold hash'):
            r.replay(self.folder, labels=gold)

    def test_changed_reconstructed_source_and_duplicate_expected_ids(self):
        prepared = copy.deepcopy(self.prepared)
        q = next(iter(prepared[0][1]['questions']))
        prepared[0][1]['state']['records'][q] = 'forged source'
        with patch.object(r, 'packs', return_value=prepared):
            self.reject('original frozen panel')
        prepared = copy.deepcopy(self.prepared)
        prepared[1][1]['questions'][q] = prepared[0][1]['questions'][q]
        with patch.object(r, 'packs', return_value=prepared):
            self.reject('expected ID coverage')

    def test_missing_artifact_cannot_complete(self):
        (self.folder / 'pack-112-reentry.json').unlink()
        self.reject('completed receipt has partial artifacts')
        self.rc(lambda x: (x.update(status='stopped'), x.pop('native_reduction')))
        (self.folder / 'final-reduction.json').unlink()
        out = r.replay(self.folder)
        self.assertFalse(out['complete_panel'])
        self.assertTrue(out['partial'])
        self.assertEqual(out['eligible_packs'], 111)
        self.assertEqual(out['usage']['logical_request_ids'], 112)

    def test_stopped_failed_setup_unknown_usage_all_counted(self):
        events = copy.deepcopy(self.events[:25])
        setup = {**self.events[25], 'outcome': 'failed', 'entered_turn': None,
                 'attempt': 1, 'model': None, 'provider': None}
        failed = {**setup, 'attempt': 2, 'entered_turn': 1, 'latency_ms': None}
        for e in (setup, failed):
            for f in ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'reasoning_tokens'):
                e[f] = None
        events += [setup, failed]
        self.write_events(events)
        def mutate(x):
            before, after = r.summary(events[:25]), r.summary(events)
            x.update(status='stopped', logical_llm_calls=26, calls=x['calls'][:26],
                     panel_rows=x['panel_rows'][:26], generative_trace=after)
            x.pop('native_reduction')
            call = x['calls'][-1]
            call.update(status='attempted', usage=r._delta(after, before), seconds=None)
            call.update({k: after[k] - before[k] for k in r.COUNTERS})
            x['panel_rows'][-1]['status'] = 'attempted'
        self.rc(mutate)
        (self.folder / 'final-reduction.json').unlink()
        for name, _ in self.prepared[26:]:
            for kind in ('prompt', 'raw', 'answer', 'reentry'):
                (self.folder / (name + '-' + kind + '.json')).unlink()
        for kind in ('answer', 'reentry'):
            (self.folder / ('pack-026-' + kind + '.json')).unlink()
        save(self.folder / 'pack-026-raw.json', {'text': 'invalid model output'})
        out = r.replay(self.folder)
        self.assertTrue(out['partial'])
        self.assertEqual(out['usage']['physical_attempt_events'], 27)
        self.assertEqual(out['usage']['setup_attempts'], 1)
        self.assertEqual(out['usage']['failed_identity_unknown_events'], 2)
        self.assertEqual(out['usage']['usage']['input_tokens']['unknown_entered_events'], 1)
        self.assertEqual(out['eligible_packs'], 25)
        self.assertIsNotNone(out['artifacts'][-1]['raw_validation_error'])
        self.assertIsNone(out['timing']['native_event_seconds'][-1])

    def test_running_rejected_before_any_outcomes(self):
        self.rc(lambda x: x.update(status='running'))
        with patch.object(r, 'packs', side_effect=AssertionError('should not inspect artifacts')):
            self.reject('terminal status required')

    def test_interruption_binding_and_restored_latency(self):
        self.rc(lambda x: x['continuation'].update(interruption_sha256='forged'))
        self.reject('continuation interruption binding')
        save(self.folder / 'receipt.json', self.receipt)
        self.rc(lambda x: x['calls'][24].update(seconds=0))
        self.reject('recovered controller duration unknown')

    def test_cli_optional_positional_exclusive_and_dangling_safe(self):
        for option in (False, True):
            out = Path(self.tmp.name) / ('output-' + str(option) + '.json')
            args = (['--receipt-dir', str(self.folder)] if option else [str(self.folder)]) + ['--output', str(out)]
            with patch.object(r, 'replay', return_value={'metrics': {'baseline': {}}}) as invoke:
                self.assertEqual(r.main(args), 0)
                invoke.assert_called_once_with(self.folder)
                with self.assertRaisesRegex(ValueError, 'output exists'):
                    r.main(args)
        dangling = Path(self.tmp.name) / 'dangling'
        dangling.symlink_to(Path(self.tmp.name) / 'absent')
        with self.assertRaisesRegex(ValueError, 'output exists'):
            r.main(['--receipt-dir', str(self.folder), '--output', str(dangling)])
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            r.main([str(self.folder), '--receipt-dir', str(self.folder), '--output', str(dangling)])

    def test_small_paired_metrics_have_distinct_predictions(self):
        gold = {'a': {'gold_ham': True, 'p_ham': .6}, 'b': {'gold_ham': False, 'p_ham': .8},
                'c': {'gold_ham': False, 'p_ham': .1}, 'd': {'gold_ham': True, 'p_ham': .9}}
        m = r.metrics({'a': 'yes', 'b': 'no', 'c': 'yes', 'd': 'no'}, gold)
        self.assertEqual((m['baseline']['tp'], m['baseline']['fp'], m['baseline']['fn']), (1, 1, 1))
        self.assertEqual((m['original_p_ge_0.5']['tp'], m['original_p_ge_0.5']['fp']), (2, 1))
        self.assertEqual((m['declared_transferred']['tp'], m['declared_transferred']['fn']), (1, 1))
        p = m['paired']['original_p_ge_0.5']
        self.assertEqual((p['baseline_wins'], p['baseline_losses'], p['shared_errors']), (1, 2, 0))
        self.assertEqual(p['agreement_coverage'], .25)

    def test_successful_retry_preserves_failed_setup_and_unknown_cache(self):
        events = copy.deepcopy(self.events)
        success = events[25]
        setup = {**success, 'attempt': 1, 'entered_turn': None, 'outcome': 'failed',
                 'model': None, 'provider': None}
        failed = {**setup, 'attempt': 2, 'entered_turn': 1}
        for event in (setup, failed):
            for key in ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'reasoning_tokens'):
                event[key] = None
        failed.update(input_tokens=5, output_tokens=2)
        success.update(attempt=3, entered_turn=2)
        events[25:26] = [setup, failed, success]
        self.write_events(events)
        def mutate(x):
            before, after = r.summary(events[:25]), r.summary(events[:28])
            call = x['calls'][25]
            call.update(usage=r._delta(after, before))
            call.update({key: after[key] - before[key] for key in r.COUNTERS})
            x['generative_trace'] = r.summary(events)
        self.rc(mutate)
        out = r.replay(self.folder)
        self.assertTrue(out['complete_panel'])
        self.assertEqual(out['usage']['physical_attempt_events'], 114)
        self.assertEqual(out['usage']['setup_attempts'], 1)
        self.assertEqual(out['usage']['failed_identity_unknown_events'], 2)
        self.assertEqual(out['usage']['usage']['reasoning_tokens']['unknown_entered_events'], 1)

    def test_original_jev_request_and_source_hash_mutations(self):
        directory = Path(self.tmp.name) / 'typed'
        directory.mkdir()
        request = r.load(r.b.TYPED_RECEIPT / 'pack-001-request.json')
        request['state']['records'][next(iter(request['questions']))] = 'forged original request'
        save(directory / 'pack-001-request.json', request)
        with patch.object(r.b, 'TYPED_RECEIPT', directory):
            with self.assertRaisesRegex(r.n.Stop, 'prior_typed_request_differs'):
                r.packs()
        manifest = r.load(r.b.large_run.PACK_DIR / 'MANIFEST.json')
        manifest['source_sha256'] = '0' * 64
        save(directory / 'MANIFEST.json', manifest)
        with patch.object(r.b.large_run, 'PACK_DIR', directory):
            with self.assertRaisesRegex(r.n.Stop, 'source_identity'):
                r.packs()

    def test_rehashed_interruption_envelope_still_rejected(self):
        prior = Path(self.tmp.name) / 'predecessor'
        prior.mkdir()
        for path in r.c.PREVIOUS.iterdir():
            if path.is_file():
                shutil.copyfile(path, prior / path.name)
        final = r.load(prior / 'external-final-read.json')
        final['exit'] = False
        save(prior / 'external-final-read.json', final)
        side = r.load(prior / 'external-interruption.json')
        side['external_final_read_sha256'] = r.sha(prior / 'external-final-read.json')
        save(prior / 'external-interruption.json', side)
        receipt = copy.deepcopy(self.receipt)
        receipt['continuation'].update(predecessor=str(prior),
            interruption_sha256=r.sha(prior / 'external-interruption.json'))
        with self.assertRaisesRegex(r.n.Stop, 'recovered_final_envelope'):
            r._predecessor(receipt, self.events)

    def test_strict_json_nonfinite_and_duplicate_nested(self):
        for text in ('{"x":NaN}', '{"x":1e999}', '{"x":{"a":1,"a":2}}'):
            with self.assertRaises(ValueError):
                r.strict_loads(text)

    def test_runtime_identity_caps_and_missing_wall_are_not_optional(self):
        for field,value,reason in (('binary_sha256','forged','runtime identity'),
                                   ('generative_model','another-model','runtime identity'),
                                   ('requested_model','wrong','runtime identity'),
                                   ('caps',{},'runtime caps'),('elapsed_seconds',None,'missing full wall')):
            save(self.folder/'receipt.json',self.receipt)
            self.rc(lambda x:x.update({field:value}))
            self.reject(reason)

    def test_too_many_setup_attempts_cannot_be_a_successful_call(self):
        events=copy.deepcopy(self.events)
        success=events[25]
        setups=[]
        for attempt in range(1,6):
            setup={**success,'attempt':attempt,'outcome':'failed'}
            for key in ('entered_turn','model','provider','input_tokens','output_tokens',
                        'cache_read_tokens','cache_write_tokens','reasoning_tokens'):
                setup.pop(key,None)
            setups.append(setup)
        success.update(attempt=6,entered_turn=1)
        events[25:26]=setups+[success]
        self.write_events(events)
        # The native summarizer rejects this even before per-call replay.
        with self.assertRaisesRegex(TraceStop,'generative_transport_attempt_cap'):
            r.summary(events)


if __name__ == '__main__':
    unittest.main()
