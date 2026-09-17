import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from bench.jev.long_task import run as r


class RunnerTests(unittest.TestCase):
    def test_actual_inventory_matches_project_build_inputs(self):
        inventory = r.inventory(Path(sys.executable))
        self.assertIn('Cargo.toml', inventory['files'])
        self.assertIn('Cargo.lock', inventory['files'])
        self.assertIn('src/judge.rs', inventory['files'])
        self.assertEqual('build.rs' in inventory['files'], (r.ROOT / 'build.rs').exists())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR'], prefix='long-run-test-')
        self.root = Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def event(self, **kwargs):
        value = dict(event='model_attempt', request_id='one', attempt=1, entered_turn=1,
                     outcome='succeeded', model=r.MODEL, provider='OpenAI', input_tokens=10, output_tokens=2)
        value.update(kwargs)
        return value
    def trace(self, rows, tail=b''):
        path = self.root / 'trace'
        path.write_bytes(b''.join(r.canonical(x) for x in rows) + tail)
        return path
    def test_default_cli_and_no_live_ack_are_provider_free(self):
        p = subprocess.run([sys.executable, '-B', str(r.HERE / 'run.py')], cwd=self.root,
                           capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)['provider_calls'], 0)
        with self.assertRaisesRegex(r.Stop, 'explicit_live_arguments'):
            r.main(['--live', '--binary', sys.executable])
    def test_environment_removes_keys_bridges_and_unrelated_home(self):
        with mock.patch.dict(os.environ, {'TYPESAFE_API_KEY':'synthetic', 'JCODE_SOCKET':'private',
                 'OPENAI_API_KEY':'synthetic', 'JCODE_RUNTIME_DIR':'old', 'AZDAJA_CONFIG':'old'}):
            env = r.environment(self.root, self.root)
        self.assertNotIn('TYPESAFE_API_KEY', env)
        self.assertNotIn('JCODE_SOCKET', env)
        self.assertNotIn('OPENAI_API_KEY', env)
        self.assertEqual(env['JCODE_RUNTIME_DIR'], str(self.root / 'runtime'))
        self.assertEqual(env['HOME'], str(self.root / 'home'))
    def test_setup_omitted_keys_and_unknown_usage_remain_distinct(self):
        setup = dict(event='model_attempt', request_id='one', attempt=1, outcome='failed')
        path = self.trace([setup, self.event(attempt=2)])
        summary = r.trace_summary(path)
        self.assertEqual(summary['setup_attempts'], 1)
        self.assertEqual(summary['entered_turns'], 1)
        self.assertEqual(summary['usage']['input_tokens']['known_total'], 10)
        self.assertEqual(summary['usage']['cache_read_tokens']['unknown_entered_events'], 1)
        r.usage_ok(summary)
        path = self.trace([self.event(input_tokens=None)])
        with self.assertRaisesRegex(r.Stop, 'unknown_entered_usage'):
            r.usage_ok(r.trace_summary(path))
    def test_partial_json_only_ignored_during_monitoring(self):
        path = self.trace([self.event()], b'{"partial":')
        self.assertEqual(r.trace_summary(path, partial=True)['events'], 1)
        with self.assertRaises(ValueError):
            r.trace_summary(path)
    def test_bool_negative_identity_duplicate_attempt_and_caps_rejected(self):
        for patch in ({'input_tokens':True}, {'output_tokens':-1}, {'provider':'other'}, {'entered_turn':True}):
            with self.assertRaises(r.Stop):
                r.trace_summary(self.trace([self.event(**patch)]))
        with self.assertRaisesRegex(r.Stop, 'duplicate_physical_attempt'):
            r.trace_summary(self.trace([self.event(), self.event()]))
        with self.assertRaisesRegex(r.Stop, 'known_usage_cap'):
            r.usage_ok(r.trace_summary(self.trace([self.event(input_tokens=r.MAX_INPUT+1)])))
    def test_private_copy_rejects_symlink_permissions_and_overwrite(self):
        source = self.root / 'synthetic-auth'
        source.write_bytes(b'{"synthetic":true}')
        source.chmod(0o600)
        target = self.root / 'target'
        self.assertEqual(r.opaque_copy(source, target), r.sha(source.read_bytes()))
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(FileExistsError):
            r.opaque_copy(source, target)
        link = self.root / 'link'
        link.symlink_to(source)
        with self.assertRaises(OSError):
            r.opaque_copy(link, self.root/'other')
        source.chmod(0o644)
        with self.assertRaises(r.Stop):
            r.opaque_copy(source, self.root/'other')
    def test_output_existing_and_dangling_are_preserved(self):
        path = self.root / 'out'
        r.save(path, {'original':True})
        with self.assertRaises(FileExistsError):
            r.save(path, {})
        self.assertEqual(r.loads(path.read_bytes()), {'original':True})
        link = self.root/'link'; link.symlink_to(self.root/'absent')
        with self.assertRaises(FileExistsError):
            r.save(link, {})
        self.assertFalse((self.root/'absent').exists())
    def footer(self, **updates):
        fields = ('attempts','successful_requests','failed_attempts','questions','cache_hits',
                  'known_input_tokens','known_output_tokens','unknown_input_usage_requests',
                  'unknown_output_usage_requests','total_wall_ns','provider_requests')
        cell = dict.fromkeys(fields, 0); cell.update(updates)
        row = dict(event='solo_runtime', request_id='id', outcome='succeeded', judge_cells=[cell])
        raw = b'\n=== solo runtime trace begin request_id="id" ===\n' + r.canonical(row) + b'=== solo runtime trace end request_id="id" ===\n'
        path = self.root/'solo'; path.write_bytes(raw)
        return path
    def test_only_host_footer_at_eof_is_accepted_and_stats_typed(self):
        path = self.footer()
        self.assertEqual(r.runtime_summary(path)['typed_totals']['attempts'], 0)
        path.write_bytes(path.read_bytes()+b'after footer')
        with self.assertRaises(r.Stop):r.runtime_summary(path)
        with self.assertRaises(r.Stop):r.runtime_summary(self.footer(attempts=True))
        with self.assertRaises(r.Stop):r.runtime_summary(self.footer(provider_requests=True))
        with self.assertRaises(r.Stop):r.runtime_summary(self.footer(unknown_input_usage_requests=1))
    def test_task_and_config_are_identical_except_declared_constraint(self):
        common = (r.HERE/'task.txt').read_text()
        for arm in r.ARMS:
            self.assertEqual(r.task(arm), common+'\n'+r.CONSTRAINTS[arm])
        self.assertIn('enabled=true', r.config())
        self.assertNotIn('gold.json', common)
        self.assertNotIn('374', common)
    def test_setup_failure_removes_already_copied_private_auth(self):
        source=self.root/'auth';source.write_bytes(b'{"synthetic":true}');source.chmod(0o600)
        result=r.run_arm(Path(sys.executable), 'optional_typed', self.root/'out', self.root/'private',
                         auth=source, attached=self.root/'missing')
        self.assertEqual(result['status'],'stopped')
        self.assertTrue(result['private_credentials_removed'])
        self.assertTrue(result['original_auth_unchanged'])
        self.assertFalse((self.root/'private/jcode').exists())
    def test_interrupt_is_terminal_and_cleans_private_auth(self):
        source=self.root/'auth';source.write_bytes(b'{"synthetic":true}');source.chmod(0o600)
        with mock.patch.object(r.subprocess, 'Popen', side_effect=KeyboardInterrupt):
            result=r.run_arm(Path(sys.executable), 'generative', self.root/'out', self.root/'private', auth=source, attached=None)
        self.assertTrue(result['interrupted'])
        self.assertTrue(result['private_credentials_removed'])
    def test_stubborn_owned_bridge_is_revalidated_before_kill(self):
        import signal
        state=self.root/'state'; base=state/'jcode-api';base.mkdir(parents=True)
        (base/'bridge.pid').write_text('123456')
        directory=self.root/'runtime';(base/'runtime-dir').write_text(str(directory))
        args='jcode api-bridge --api-socket '+str(directory/'api.sock')
        killed=[]
        def probe(argv, **kwargs):
            dead=signal.SIGKILL in killed
            return subprocess.CompletedProcess(argv, 1 if dead else 0,
                    args if argv[-1]=='args=' else 'R', '')
        with mock.patch.object(r.subprocess,'run',side_effect=probe), mock.patch.object(r.time,'sleep'), mock.patch.object(r.os,'kill',side_effect=lambda pid,sig:killed.append(sig)):
            self.assertTrue(r.stop_bridge(state))
        self.assertEqual(killed,[signal.SIGTERM,signal.SIGKILL])
    def test_started_marker_and_cleanup_failure_block_further_admission(self):
        methods=self.root/'methods';methods.mkdir()
        args=['--live','--acknowledge-provider-calls','--binary',sys.executable,
              '--output',str(self.root/'campaign'),'--auth-file',str(self.root/'auth'),
              '--attached-file',str(self.root/'attached')]
        receipt={'status':'stopped','cleanup_error':'Stop','elapsed_seconds':0}
        with mock.patch.object(r,'HERE',methods), mock.patch.object(r,'check_seal',return_value='a'*64), mock.patch.object(r,'run_arm',return_value=receipt) as entered:
            self.assertEqual(r.main(args),0)
            self.assertEqual(entered.call_count,1)
            terminal=r.loads((self.root/'campaign/terminal.json').read_bytes())
            self.assertFalse(terminal['all_completed'])
            args[5]=str(self.root/'another')
            with self.assertRaises(FileExistsError):r.main(args)
            self.assertEqual(entered.call_count,1)
    def test_actual_native_full_source_and_failure_through_controller(self):
        binary=os.environ.get('AZDAJA_LONG_BINARY')
        if not binary:self.skipTest('set AZDAJA_LONG_BINARY for actual public acceptance')
        script=self.root/'provider.py'
        fields=list(r.scoring.FIELDS);queries=list(r.scoring.QUERIES)
        code='''data=json.loads(ctx)
x=llm("local-only boundary witness")
rows=[]
for doc in data["contracts"]:
    fields={name:{"label":"unknown","quote":""} for name in FIELD_NAMES}
    rows.append({"id":doc["id"],"fields":fields})
ids=[doc["id"] for doc in data["contracts"]]
queries={name:{"yes":[],"no":[],"unknown":ids} for name in QUERY_NAMES}
FINAL({"source_sha256":sha256(ctx),"contracts":rows,"queries":queries})
'''.replace('FIELD_NAMES',repr(fields)).replace('QUERY_NAMES',repr(queries))
        script.write_text('import sys\np=sys.stdin.read()\nprint('+repr('```python\n'+code+'```')+' if "Available names:" in p else "local-only")\n')
        command=shlex_quote(sys.executable)+' '+shlex_quote(str(script))
        result=r.run_arm(Path(binary), 'generative', self.root/'out', self.root/'private',auth=None,attached=None,offline_provider=command)
        self.assertEqual(result['status'],'completed_outputs_pending_scoring',result)
        prediction=r.loads((self.root/'out/prediction.json').read_bytes())
        self.assertEqual(len(prediction['contracts']),102)
        self.assertEqual(prediction['source_sha256'],r.sha((r.HERE/'fixtures/corpus.json').read_bytes()))
        self.assertEqual(result['runtime']['typed_totals']['attempts'],0)
        script.write_text('import sys\nsys.stdin.read()\nprint("```python\\nFINAL({})\\n```")\n')
        failed=r.run_arm(Path(binary), 'optional_typed', self.root/'failed', self.root/'private2',auth=None,attached=None,offline_provider=command)
        self.assertEqual(failed['status'],'stopped')
        self.assertNotEqual(failed['exit'],0)


def shlex_quote(value):
    import shlex
    return shlex.quote(value)


if __name__ == '__main__':unittest.main()
