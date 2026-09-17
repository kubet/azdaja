import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from bench.jev.asymmetry.criteria import run as r
from bench.jev.angle_lab import native as n


def fake():
    c=object.__new__(r.Campaign); c.stopped=False; c.started=time.monotonic()
    c.receipt={'typed_calls_started':0,'known_typed_input_tokens':0,'known_typed_output_tokens':0,
               'typed_unknown_usage':0,'typed_unknown_output_usage':0,'logical_llm_calls':0}
    c.checkpoint=lambda:None
    return c


class CriteriaRunTests(unittest.TestCase):
    def test_default_and_unacknowledged_live_never_admit(self):
        for args, code in (([],0),(['--live'],2)):
            p=subprocess.run([sys.executable,'-B','-m','bench.jev.asymmetry.criteria.run',*args],capture_output=True,cwd=r.p.ROOT,timeout=10)
            self.assertEqual(p.returncode,code)
            if not args: self.assertEqual(json.loads(p.stdout)['provider_calls'],0)
            else: self.assertIn(b'live requires acknowledgement',p.stderr)

    def test_configuration_is_typed_only_and_unknown_usage_stops(self):
        c=fake()
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            c.work=Path(tmp); c.configure(False)
            text=(c.work/'config.toml').read_text()
            self.assertIn('sub_llm_cmd="/usr/bin/false"',text)
            self.assertIn('enabled=false',text)
            with self.assertRaisesRegex(n.Stop,'generation_disabled'): c.generate('x',{})
            for field in ('typed_unknown_usage','typed_unknown_output_usage'):
                c.receipt[field]=1
                with self.assertRaisesRegex(n.Stop,'input_or_unknown_budget'): c.configure(True)
                c.receipt[field]=0
            c.receipt['known_typed_input_tokens']=100
            c.configure(True)
            self.assertIn('max_input_tokens_per_cell=249900',(c.work/'config.toml').read_text())

    def test_actual_retained_noul_shape_and_hostile_mutations(self):
        raw=n.strict_loads((r.p.ROOT/'bench/jev/second_reader/results/row651-live-20260917/pack-001-observation.json').read_bytes())
        actual=next(iter(raw['observation']['answers'].values()))
        self.assertIn('noul',actual)
        for value, good in ((actual,True),({'type':'noul','noul':True},False),
                            ({'type':'noul','noul':1.1},False),({'type':'noul','noul':float('nan')},False),
                            ({'type':'noul','value':.5},False)):
            body={'model':n.MODEL,'answers':{'q':copy.deepcopy(value)}}
            if good: r.validate_body(body,{'questions':{'q':{}}})
            else:
                with self.assertRaisesRegex(n.Stop,'noul_domain'): r.validate_body(body,{'questions':{'q':{}}})

    def test_caps_crossing_poison_and_no_second_request(self):
        c=fake();c.receipt['typed_calls_started']=r.REQUESTS
        with patch.object(n.Campaign,'typed') as send:
            with self.assertRaisesRegex(n.Stop,'request_cap'): c.typed('x',{})
            send.assert_not_called()
        c=fake()
        def crossed(*args):
            c.receipt['known_typed_output_tokens']=r.MAX_OUTPUT+1
            return {'model':n.MODEL,'answers':{'q':{'type':'noul','noul':.5}}}
        with patch.object(n.Campaign,'typed',side_effect=crossed) as send:
            with self.assertRaisesRegex(n.Stop,'token_cap'): c.typed('x',{'questions':{'q':{}}})
            with self.assertRaisesRegex(n.Stop,'session_stopped'): c.typed('y',{})
            self.assertEqual(send.call_count,1)
            self.assertEqual(c.receipt['known_typed_output_tokens'],r.MAX_OUTPUT+1)

    def test_incomplete_panel_cannot_be_complete(self):
        c=fake();c.receipt['confirmed_typed_requests']=0
        with self.assertRaisesRegex(n.Stop,'incomplete_panel'): c.finish('completed')

    def test_exclusive_marker_blocks_new_output_before_campaign(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            root=Path(tmp); manifest=root/'FROZEN.json'
            prepared=[('criteria-01',{'state':{},'questions':{'q':{'type':'noul','instructions':'x'}}})]
            manifest.write_bytes(n.canonical({'files':{},'panel':r.identities(prepared),'caps':r.CAPS}))
            manifest.with_suffix('.started').write_text('preserve')
            with patch.object(r,'rows',return_value=prepared),patch.object(r,'inventory',return_value={}),patch.object(r,'Campaign') as create:
                with self.assertRaises(FileExistsError):
                    r.main(['--live','--acknowledge-provider-calls','--azdaja','/unused','--credential-state-root',str(root),'--manifest',str(manifest),'--output',str(root/'new')])
                create.assert_not_called()
            self.assertEqual(manifest.with_suffix('.started').read_text(),'preserve')


if __name__=='__main__': unittest.main()
