import copy
import unittest
from . import report
from .run import HERE
from bench.jev.angle_lab import native as n


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.gold=n.strict_loads((HERE/'fixtures/gold.json').read_bytes())
        self.labels={k:v['expected'] for k,v in self.gold.items()}
        self.ps={k:float(v['expected']=='yes') for k,v in self.gold.items() if v['lane']=='verifier'}

    def test_perfect_and_asymmetric_falsifiers(self):
        result=report.grade(self.gold,self.labels,self.ps)
        self.assertTrue(result['flat']['absolute_quality_bar_passed'])
        self.assertTrue(result['verifier']['absolute_quality_bar_passed'])
        self.assertEqual(result['verifier']['brier_score'],0)
        bad=next(k for k,v in self.gold.items() if v['lane']=='verifier' and v['expected']=='no')
        self.labels[bad]='yes'; self.ps[bad]=.99
        result=report.grade(self.gold,self.labels,self.ps)['verifier']
        self.assertEqual(result['false_support'],1)
        self.assertFalse(result['absolute_quality_bar_passed'])
        self.assertEqual(result['approved_actions'],0)
        self.assertTrue(all(row['errors']==1 for row in result['risk_coverage']))

    def test_always_flag_is_not_a_usefulness_win(self):
        for key in self.ps: self.labels[key]='no'; self.ps[key]=0
        row=report.grade(self.gold,self.labels,self.ps)['verifier']
        self.assertEqual((row['false_support'],row['false_flags']),(0,100))
        self.assertFalse(row['absolute_quality_bar_passed'])

    def test_incomplete_never_passes_and_probabilities_cannot_be_omitted(self):
        missing=next(iter(self.ps)); self.labels.pop(missing); self.ps.pop(missing)
        self.assertFalse(report.grade(self.gold,self.labels,self.ps)['verifier']['absolute_quality_bar_passed'])
        self.ps['invented']=.7
        with self.assertRaisesRegex(ValueError,'probability coverage'):
            report.grade(self.gold,self.labels,self.ps)

    def test_boolean_nan_and_out_of_range_rejected(self):
        for value in [True,False,float('nan'),float('inf'),-.1,1.1]:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError,'probability domain'):
                report.probability(value)

    def test_valid_body_swap_fails_request_binding(self):
        pack={'state':'source-a','questions':{'q':{'type':'noul','instructions':'source claim'}}}
        request=n.inspect_pack(pack)
        body={'model':n.MODEL,'_azdaja':{'request_sha256':n.sha(n.canonical(request))},'answers':{'q':{'type':'noul','noul':.7}}}
        self.assertEqual(report.decisions(body,request)[0],{'q':'yes'})
        other=n.inspect_pack(dict(pack,state='source-b'))
        with self.assertRaisesRegex(ValueError,'transport identity'): report.decisions(body,other)
        body['answers']['q']['noul']=True
        with self.assertRaisesRegex(ValueError,'probability domain'): report.decisions(body,request)

    def test_choice_winner_must_match_complete_distribution(self):
        request=n.inspect_pack({'state':'source','questions':{'q':{'type':'choice','instructions':'which','criteria':{'a':'A','b':'B'}}}})
        body={'model':n.MODEL,'_azdaja':{'request_sha256':n.sha(n.canonical(request))},'answers':{'q':{'type':'choice','choice':'b','confidence':.8,'probabilities':{'a':.9,'b':.1}}}}
        with self.assertRaisesRegex(ValueError,'choice winner'): report.decisions(body,request)
        body['answers']['q']['choice']='a'
        self.assertEqual(report.decisions(body,request)[0],{'q':'a'})
        body['answers']['q']['probabilities']['b']=.4
        with self.assertRaisesRegex(ValueError,'choice sum'): report.decisions(body,request)


if __name__=='__main__': unittest.main()
