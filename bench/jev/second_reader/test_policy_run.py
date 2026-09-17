import contextlib
import io
import unittest
from unittest.mock import patch
from . import policy_run as run
from bench.jev.angle_lab import native as n


class PolicyRunTests(unittest.TestCase):
    def test_default_has_no_admission(self):
        with patch.object(run,'rows',side_effect=AssertionError('no calls')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run.main([]),0)

    def test_fixed_rows_blind_four_then_complete_three_phrasings(self):
        rows=run.rows()
        self.assertEqual([arm for _,arm,_ in rows],['generative']+['typed']*11)
        first=rows[0][2]
        self.assertEqual(set(first['state']['records']),{'r0576','r1856','r0514','r1581'})
        self.assertEqual(len(first['questions']),4)
        qs=[q for _,_,p in rows[1:] for q in p['questions']]
        self.assertEqual(len(qs),681);self.assertEqual(len(set(qs)),681)
        for _,_,pack in rows: n.inspect_pack(pack)

    def test_caps_reject_before_inherited_provider_path(self):
        c=object.__new__(run.Campaign);c.stopped=False
        c.receipt={'typed_calls_started':11,'logical_llm_calls':1}
        with patch.object(c,'checkpoint'),patch.object(n.Campaign,'typed',side_effect=AssertionError('transport')):
            with self.assertRaisesRegex(n.Stop,'policy_typed_cap'):c.typed('x',{})
        c.stopped=False
        with patch.object(c,'checkpoint'),patch.object(n.Campaign,'generate',side_effect=AssertionError('transport')):
            with self.assertRaisesRegex(n.Stop,'policy_generation_cap'):c.generate('x',{})

    def test_exercise_has_one_generation_and_eleven_typed_calls(self):
        class Fake:
            output=None
            def __init__(self):self.receipt={};self.arms=[]
            def start(self):pass
            def checkpoint(self):pass
            def generate(self,name,pack):self.arms.append('generative');return {}
            def typed(self,name,pack):self.arms.append('typed');return {}
        c=Fake();c.output=run.HERE
        with patch.object(n,'usage_summary',return_value={'entered_turns':1}),contextlib.redirect_stdout(io.StringIO()):run.exercise(c,True)
        self.assertEqual(c.arms,['generative']+['typed']*11)
        self.assertEqual(len(c.receipt['panel_rows']),12)
        self.assertTrue(all(r['status']=='completed' for r in c.receipt['panel_rows']))


if __name__=='__main__':unittest.main()
