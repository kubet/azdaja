import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from bench.jev.asymmetry.baseline import continue_run as c

class RecoveryTests(unittest.TestCase):
    def test_actual_prefix_has25_known_turns_and_exact_answer_coverage(self):
        receipt,answers,trace=c.check_prefix()
        self.assertEqual(len(answers),25)
        self.assertEqual(trace['entered_turns'],25)
        self.assertEqual(sum(len(a) for a in answers),sum(len(p['questions']) for _,p in c.b.rows()[:25]))
        self.assertTrue(all(trace['usage'][f]['unknown_entered_events']==0 for f in ('input_tokens','output_tokens')))
        self.assertEqual(receipt['calls'][-1]['status'],'attempted')
    def test_prefix_cannot_be_regenerated_or_call112_budget_reset(self):
        x=c.Campaign.__new__(c.Campaign)
        with patch.object(c.b.Campaign,'generate') as invoke:
            for name in ('pack-001','pack-025','pack-113'):
                with self.assertRaisesRegex(c.n.Stop,'prefix_may_not_be_regenerated'):x.generate(name,{})
            invoke.assert_not_called()
        trace=c.n.usage_summary(c.PREVIOUS/'model-trace.jsonl')
        bad=copy.deepcopy(trace);bad['usage']['input_tokens']['unknown_entered_events']=1
        with self.assertRaisesRegex(c.n.Stop,'generative_unknown_usage'):c.b.check_usage(bad)
        self.assertEqual(c.DEADLINE-c.STARTED,7200)
    def test_changed_recovered_answer_and_prompt_rejected(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            d=Path(tmp)
            for p in c.PREVIOUS.iterdir():
                if p.is_file():shutil.copyfile(p,d/p.name)
            fp=d/'external-final-read.json';v=c.load(fp);v['stdout']='{}';fp.write_bytes(c.n.canonical(v))
            side=c.load(d/'external-interruption.json');side['external_final_read_sha256']=c.n.sha(fp.read_bytes())
            (d/'external-interruption.json').write_bytes(c.n.canonical(side))
            with self.assertRaisesRegex(c.n.Stop,'generative_answer_coverage'):c.check_prefix(d)
            shutil.copyfile(c.PREVIOUS/'external-final-read.json',fp)
            shutil.copyfile(c.PREVIOUS/'external-interruption.json',d/'external-interruption.json')
            p=d/'pack-001-prompt.json';v=c.load(p);v['instruction']='changed';p.write_bytes(c.n.canonical(v))
            with self.assertRaisesRegex(c.n.Stop,'prefix_prompt'):c.check_prefix(d)
    def test_default_and_unacknowledged_never_create_campaign(self):
        with patch.object(c,'Campaign') as campaign:
            self.assertEqual(c.main([]),0)
            with self.assertRaisesRegex(c.n.Stop,'acknowledgement_required'):
                c.main(['--live','--azdaja','not-used'])
            campaign.assert_not_called()
    def test_exclusive_admission_blocks_repeat_output_before_any_campaign(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            d=Path(tmp);seal=d/'seal.json';seal.write_bytes(c.n.canonical({'files':{},'suffix':[],'deadline_unix':c.DEADLINE}))
            seal.with_suffix('.started').write_bytes(b'keep')
            profile=d/'profile';profile.mkdir();(profile/'openai-auth.json').write_bytes(b'{}')
            with patch.object(c,'SEAL',seal),patch.object(c,'inventory',return_value={}),patch.object(c.b,'rows',return_value=[]),patch.object(c,'Campaign') as campaign:
                with self.assertRaises(FileExistsError):
                    c.main(['--live','--acknowledge-provider-calls','--azdaja','unused','--output',str(d/'out'),'--private-jcode-home',str(profile)])
                campaign.assert_not_called()
            self.assertEqual(seal.with_suffix('.started').read_bytes(),b'keep')
    def test_supervisor_deadline_reaps_real_local_child(self):
        from bench.jev.asymmetry.baseline import continuation_supervisor as s
        import sys,time
        with tempfile.TemporaryDirectory(dir=os.environ.get('JCODE_SCRATCH_DIR')) as tmp:
            started=time.monotonic()
            result=s.supervise([sys.executable,'-c','import time;time.sleep(30)'],time.time()+.2,Path(tmp)/'absent')
            self.assertLess(time.monotonic()-started,3)
            self.assertEqual(result['stop_reason'],'absolute_campaign_deadline')
            self.assertLess(result['child_exit'],0)
            self.assertFalse(result['campaign_completed'])
        with patch.object(s.subprocess,'Popen') as child:
            with self.assertRaisesRegex(c.n.Stop,'original_campaign_deadline'):s.supervise([],time.time()-1,Path('absent'))
            child.assert_not_called()
if __name__=='__main__':unittest.main()
