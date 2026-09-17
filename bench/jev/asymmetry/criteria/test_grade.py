import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from bench.jev.asymmetry.criteria import grade as g
from bench.jev.asymmetry.criteria import run as r
from bench.jev.angle_lab import native as n


class CriteriaGradeTests(unittest.TestCase):
    def test_disagreement_is_unknown_and_shared_error_remains_error(self):
        values={'a':{'control':.9,'criteria_ham':.9,'inverse_spam':.1},
                'b':{'control':.8,'criteria_ham':.2,'inverse_spam':.8},
                'c':{'control':.1,'criteria_ham':.1,'inverse_spam':.9}}
        result=g.score(values,{'a':False,'b':False,'c':False})
        self.assertEqual(result['control']['fp'],2)
        self.assertEqual(result['criteria_ham']['fp'],1)
        self.assertEqual(result['control_inverse_agreement']['unresolved'],1)
        self.assertEqual(result['control_inverse_agreement']['fp'],1)
        self.assertIsNone(result['control_inverse_agreement']['signed_count_error'])
        self.assertEqual(result['control_inverse_agreement']['decision_range_due_only_to_unresolved'],[1,2])
        self.assertFalse(result['control_inverse_agreement']['automatic_approval'])

    def test_boundary_and_malformed_values(self):
        v={'a':{'control':.5,'criteria_ham':.5,'inverse_spam':.5}}
        result=g.score(v,{'a':True})
        self.assertEqual(result['control_inverse_agreement']['judged'],0)
        self.assertEqual(result['inverse_spam']['fn'],1)
        for bad in (True,float('nan'),float('inf'),-.1,1.1):
            changed=copy.deepcopy(v);changed['a']['control']=bad
            with self.assertRaises(ValueError):g.score(changed,{'a':True})
        with self.assertRaises(ValueError):g.score(v,{'a':1})
        with self.assertRaises(ValueError):g.score(v,{})

    def fixture(self, root, count=3):
        output=root/'receipt';output.mkdir()
        prepared=r.rows()
        binary=root/'test-not-executable';binary.write_bytes(b'offline test artifact, not an executable')
        identity=patch.object(r,'BINARY_SHA',n.sha(binary.read_bytes()))
        identity.start();self.addCleanup(identity.stop)
        files=r.inventory(binary)
        seal={'files':files,'panel':r.identities(prepared),'caps':r.CAPS}
        sealpath=root/'FROZEN.json';sealpath.write_bytes(n.canonical(seal))
        sealpath.with_suffix('.started').write_bytes(n.canonical({'seal_sha256':n.sha(sealpath.read_bytes()),'automatic_retry':False}))
        def put(name,value): (output/name).write_bytes(n.canonical(value)+b'\n')
        receipt=dict(experiment_schema=r.SCHEMA,status='stopped',synthetic_observations=False,binary_sha256=r.BINARY_SHA,
            requested_model=n.MODEL,caps=r.CAPS,logical_llm_calls=0,frozen_files={**files,str(sealpath):n.sha(sealpath.read_bytes())},
            panel_rows=[],calls=[],typed_calls_started=count,confirmed_typed_requests=count,
            known_typed_input_tokens=count*100,known_typed_output_tokens=count*63,
            typed_unknown_usage=0,typed_unknown_output_usage=0,typed_questions=sum(len(x['questions']) for _,x in prepared[:count]),elapsed_seconds=count+1)
        for i,(name,pack) in enumerate(prepared[:count]):
            request=n.inspect_pack(pack);reqsha=n.sha(n.canonical(request));usage={'input_tokens':100,'output_tokens':63}
            body={'model':n.MODEL,'answers':{qid:{'type':'noul','noul':.8} for qid in request['questions']},'usage':usage,
                '_azdaja':{'request_sha256':reqsha,'cache_hit':False,'provider_requests_this_call':1,
                'new_request_usage':usage,'original_usage':usage,'elapsed_ms':500}}
            stats={'attempts':1,'questions':len(pack['questions']),'cache_hits':0,'enabled':True,'transport_available':True,
                'poisoned':False,'input_usage_complete':True,'known_input_tokens':100,'provider_requests':1,'unknown_input_usage_requests':0}
            response_sha=n.sha(n.canonical(body))
            receipt['panel_rows'].append(dict(name=name,status='completed',request_sha256=reqsha,question_count=len(pack['questions']),response_sha256=response_sha))
            receipt['calls'].append(dict(name=name,arm='typed',status='completed',request_sha256=reqsha,response_sha256=response_sha,
                questions=len(pack['questions']),request_bytes=len(n.canonical(request)),provider_requests=1,known_input_tokens=100,
                reported_output_tokens=63,native_elapsed_ms=500,response_json_bytes=len(n.canonical(body)),seconds=.6,
                admitted_elapsed_seconds=i,completed_elapsed_seconds=i+.6))
            put(name+'-request.json',request);put(name+'-observation.json',{'observation':body,'stats':stats})
            put(name+'-reentry-result.json',body)
            put(name+'-custody-result.json',dict(request_sha256=reqsha,ids=sorted(pack['questions']),attempts=0))
        put('receipt.json',receipt)
        return output,receipt,put

    def test_source_bound_partial_replay_and_forgery_rejections(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            output,receipt,put=self.fixture(Path(tmp))
            out=g.replay(output)
            self.assertEqual(out['complete_triplets'],63);self.assertEqual(out['unobserved_triplets'],164)
            self.assertFalse(out['complete_panel']);self.assertEqual(out['confirmed_requests'],3)
            for field,value in (('status','completed'),('known_typed_input_tokens',301),('calls',[]),('binary_sha256','bad'),('requested_model','wrong'),('caps',{}),('elapsed_seconds',-1),('elapsed_seconds',True)):
                changed=copy.deepcopy(receipt);changed[field]=value;put('receipt.json',changed)
                with self.subTest(field=field),self.assertRaises(ValueError):g.replay(output)
            put('receipt.json',receipt)
            (output/'model-trace.jsonl').write_text('{}\n')
            with self.assertRaisesRegex(ValueError,'generative events'):g.replay(output)

    def test_valid_body_rehash_cannot_replace_native_reentry(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            output,receipt,put=self.fixture(Path(tmp))
            name=receipt['panel_rows'][0]['name'];raw=g.load(output/(name+'-observation.json'));body=raw['observation']
            body['answers'][next(iter(body['answers']))]['noul']=.1
            newhash=n.sha(n.canonical(body));receipt['panel_rows'][0]['response_sha256']=newhash
            receipt['calls'][0]['response_sha256']=newhash
            put(name+'-observation.json',raw);put('receipt.json',receipt)
            with self.assertRaisesRegex(ValueError,'reentry differs'):g.replay(output)

    def test_source_swap_rejected_even_with_valid_domain(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            output,receipt,put=self.fixture(Path(tmp))
            name=receipt['panel_rows'][0]['name'];request=g.load(output/(name+'-request.json'))
            request['state']={'records':{}};put(name+'-request.json',request)
            with self.assertRaisesRegex(ValueError,'request differs'):g.replay(output)

    def test_actual_stats_missing_or_over_budget_and_deadline_reject(self):
        for mutation in ('attempts','unknown','deadline','input','output'):
            with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
                output,receipt,put=self.fixture(Path(tmp));name=receipt['panel_rows'][0]['name']
                raw=g.load(output/(name+'-observation.json'))
                if mutation=='attempts':raw['stats']['attempts']=True
                elif mutation=='unknown':raw['stats']['unknown_input_usage_requests']=1
                elif mutation=='deadline':receipt['calls'][0]['completed_elapsed_seconds']=r.MAX_SECONDS+1
                else:
                    key=mutation+'_tokens';raw['observation']['usage'][key]=r.MAX_INPUT+1
                    raw['observation']['_azdaja']['new_request_usage'][key]=r.MAX_INPUT+1
                    raw['observation']['_azdaja']['original_usage'][key]=r.MAX_INPUT+1
                    if mutation=='input':raw['stats']['known_input_tokens']=r.MAX_INPUT+1;receipt['calls'][0]['known_input_tokens']=r.MAX_INPUT+1
                    else:receipt['calls'][0]['reported_output_tokens']=r.MAX_INPUT+1
                put(name+'-observation.json',raw);put('receipt.json',receipt)
                with self.subTest(mutation=mutation),self.assertRaises(ValueError):g.replay(output)

    def test_one_arm_is_not_a_complete_triplet(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            output,receipt,put=self.fixture(Path(tmp),count=1)
            out=g.replay(output);self.assertEqual(out['complete_triplets'],0)
            self.assertEqual(out['unobserved_triplets'],227);self.assertEqual(out['eligible_questions'],63)

    def test_public_output_refuses_existing_or_dangling_before_replay(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            root=Path(tmp)
            for name in ('exists','dangling'):
                out=root/name
                if name=='exists':out.write_text('preserve')
                else:out.symlink_to(root/'missing')
                with patch.object(g,'replay') as replay,self.assertRaises(SystemExit):
                    g.main(['--receipt-dir','/missing','--output',str(out)])
                replay.assert_not_called()

    def test_complete_panel_requires_actual_native_reduction(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            output,receipt,put=self.fixture(Path(tmp),count=12)
            receipt.update(status='completed',cleanup_exit=0,reduction=dict(observed=681,expected=681,complete=True,attempts=0))
            put('receipt.json',receipt);put('reduce-result.json',receipt['reduction'])
            out=g.replay(output)
            self.assertTrue(out['complete_panel']);self.assertEqual(out['complete_triplets'],227)
            receipt['elapsed_seconds']=r.MAX_SECONDS+1;put('receipt.json',receipt)
            with self.assertRaisesRegex(ValueError,'completed elapsed deadline'):g.replay(output)
            receipt['elapsed_seconds']=13;put('receipt.json',receipt)
            put('reduce-result.json',dict(observed=680,expected=681,complete=False,attempts=0))
            with self.assertRaisesRegex(ValueError,'final reduction'):g.replay(output)

    def test_correctly_failed_crossing_preserves_usage_but_is_not_quality_eligible(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            output,receipt,put=self.fixture(Path(tmp),count=3)
            name=receipt['panel_rows'][-1]['name'];raw=g.load(output/(name+'-observation.json'))
            receipt['panel_rows'][-1]['status']='attempted';receipt['calls'][-1]['status']='failed'
            receipt['calls'][-1]['reported_output_tokens']=r.MAX_OUTPUT+1
            receipt['known_typed_output_tokens']=126+r.MAX_OUTPUT+1
            for usage in (raw['observation']['usage'],raw['observation']['_azdaja']['new_request_usage'],raw['observation']['_azdaja']['original_usage']):
                usage['output_tokens']=r.MAX_OUTPUT+1
            put(name+'-observation.json',raw);put('receipt.json',receipt)
            result=g.replay(output)
            self.assertEqual(result['preserved_failed_bodies_excluded_from_quality'],1)
            self.assertEqual(result['complete_triplets'],0)
            self.assertEqual(result['known_output_tokens'],126+r.MAX_OUTPUT+1)

    def test_offline_receipt_never_becomes_quality_evidence(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            root=Path(tmp)
            (root/'receipt.json').write_text(json.dumps({'experiment_schema':'azdaja.asymmetry.criteria.v1','status':'offline_public_workflow_passed'}))
            with self.assertRaisesRegex(ValueError,'terminal live'):g.replay(root)

    def test_rehashed_empty_inventory_cannot_claim_source_binding(self):
        with tempfile.TemporaryDirectory(dir=os.environ['JCODE_SCRATCH_DIR']) as tmp:
            root=Path(tmp);output,receipt,put=self.fixture(root)
            sealpath=root/'FROZEN.json';seal=g.load(sealpath);seal['files']={}
            sealpath.write_bytes(n.canonical(seal));digest=n.sha(sealpath.read_bytes())
            sealpath.with_suffix('.started').write_bytes(n.canonical(dict(seal_sha256=digest,automatic_retry=False)))
            receipt['frozen_files']={str(sealpath):digest};put('receipt.json',receipt)
            with self.assertRaisesRegex(ValueError,'frozen binary missing'):g.replay(output)


if __name__=='__main__': unittest.main()
