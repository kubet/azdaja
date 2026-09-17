"""Gold-blind builders and adversarial outcome tests. Zero provider calls."""
import copy
import json
import math
import unittest
from . import native
from .gate import prepare_grade as gate
from .descent import run as descent
from .memory import slice as memory
from .reuse import run as reuse
from .verifier import prepare as verifier
from .verifier import grader


class LaneTests(unittest.TestCase):
    def test_canonical_raw_log_is_in_the_frozen_source_set(self):
        from . import campaign
        name='bench/jev/angle_lab/memory/raw.jsonl'
        self.assertEqual(campaign.inputs()[name], native.sha((campaign.ROOT/name).read_bytes()))

    def test_all_packs_use_the_actual_native_contract(self):
        data=descent.corpus()
        for pack in gate.packs()+[gate.calibration(),verifier.make_pack(),descent.flat_pack(data),
                                 descent.root_pack(data),memory.request(memory.load_raw())]:
            native.inspect_pack(pack)
            self.assertLessEqual(len(native.canonical(pack['state'])),24000)
            self.assertNotIn('gold',pack['state'])

    def test_all_may_occurrences_exact_and_calibration_disjoint(self):
        expected={qid:line for qid,line in gate.selected_records()}
        supplied={}
        for pack in gate.packs():
            self.assertFalse(set(supplied)&set(pack['state']['records']))
            supplied.update(pack['state']['records'])
        self.assertEqual(supplied,expected)
        self.assertEqual(len(supplied),227)
        self.assertFalse(set(supplied)&set(gate.calibration()['questions']))
        gold=json.loads((gate.HERE/'calibration-gold.json').read_text())['labels']
        self.assertEqual(set(gold),set(gate.calibration()['questions']))

    def test_aggregate_coincidence_not_per_record_accuracy(self):
        ids=[qid for qid,_ in gate.selected_records()]
        values={qid:float(i<132) for i,qid in enumerate(ids)}
        self.assertTrue(gate.grade(values)['exact_task_answer'])
        self.assertIsNone(gate.grade(values)['per_record_accuracy'])
        values[ids[0]],values[ids[-1]]=0.,1.
        self.assertTrue(gate.grade(values)['exact_task_answer'])
        for bad in [math.nan,True,1.1]:
            corrupt=dict(values); corrupt[ids[0]]=bad
            with self.assertRaisesRegex(ValueError,'finite probability'):
                gate.grade(corrupt)
        with self.assertRaisesRegex(ValueError,'coverage'):
            gate.grade({})

    def test_threshold_comes_from_calibration_only(self):
        labels=json.loads((gate.HERE/'calibration-gold.json').read_text())['labels']
        p={key:.9 if val=='yes' else .1 for key,val in labels.items()}
        self.assertEqual(gate.fit_threshold(p)['threshold'],.7)
        p={key:.5 for key in labels}
        self.assertIsNone(gate.fit_threshold(p)['threshold'])

    def test_verifier_requires_exact_ids_and_flags_corruption(self):
        gold=json.loads((verifier.ROOT/'gold.json').read_text())['labels']
        self.assertTrue(grader.grade(dict(reversed(list(gold.items()))))['screen_pass'])
        mutated=dict(gold); mutated['q06']='contradicted'
        self.assertEqual(grader.grade(mutated)['false_alarms'],['q06'])
        with self.assertRaisesRegex(ValueError,'coverage'):
            grader.grade({'q01':'contradicted'})
        # Rust-version evidence really includes Cargo line8. License task only has1:4.
        pack=verifier.make_pack(); sources={e['id']:e['text'] for e in pack['state']['evidence']}
        self.assertIn('rust-version = "1.95"',sources['e07'])
        self.assertNotIn('license',sources['e04'])
        self.assertIn('controls were not rerun',sources['e03'])

    def test_tree_reentry_driven_by_response_not_gold(self):
        data=descent.corpus()
        a={'choice':'b2','probabilities':{'b0':.02,'b1':.01,'b2':.95,'b3':.01,'no_match':.01}}
        child=descent.child_pack(data,'d01',a)
        self.assertEqual(set(child['state']['leaves']),{'b2_l0','b2_l1','b2_l2','b2_l3'})
        self.assertNotIn('b0_l3',child['questions']['greedy']['criteria'])
        b={'choice':'no_match','probabilities':{'b0':0.,'b1':0.,'b2':0.,'b3':0.,'no_match':1.}}
        self.assertIsNone(descent.child_pack(data,'d04',b))
        self.assertEqual(len(data['leaves']),16)
        self.assertFalse(descent.grade({'d01':['b2_l0'],'d02':['b1_l1'],
                                       'd03':['b0_l3'],'d04':[]})['rows'][2]['exact'])

    def test_memory_scope_before_prompt_and_same_budget(self):
        rows=memory.load_raw(); allowed=memory.eligible(rows)
        pack=memory.request(rows)
        self.assertEqual(set(pack['questions']),{r['event_id'] for r in allowed})
        self.assertNotIn('e13',pack['state']['events'])
        self.assertNotIn('e14',pack['state']['events'])
        for order in [memory.lexical(allowed),list(reversed(memory.lexical(allowed)))]:
            view=memory.select(rows,order)
            self.assertLessEqual(view['evidence_bytes'],memory.BUDGET)
            self.assertLessEqual(len(view['events']),memory.MAX_SELECTED)
            if 'e01' in view['selected_ids']: self.assertIn('e03',view['selected_ids'])
        with self.assertRaisesRegex(ValueError,'authorized'):
            memory.select(rows,[r['event_id'] for r in rows])
        same=[r for r in rows if r['git_attribution']['email']=='same@example.test']
        self.assertEqual({r['actor_id'] for r in same},{'actor-a','actor-b'})
        self.assertGreater(len({r['git_attribution']['email'] for r in rows if r['actor_id']=='actor-a'}),1)

    def test_cache_full_arrays_and_wrong_cache_witness(self):
        self.assertTrue(reuse.negative_and_mutation_checks()['bad_key_wrong_answer_reproduced'])
        report=reuse.experiment(1000)
        self.assertEqual(report['arms']['recompute']['oracle_evaluations'],5000)
        self.assertLess(report['arms']['plain_exact_cache']['oracle_evaluations'],5000)
        self.assertFalse(report['distinct_incremental_engine_measured'])


if __name__=='__main__':
    unittest.main()
