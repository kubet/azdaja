"""Provider-free cache economics and invalidation. No incremental optimizer claim."""
import copy
import json
from pathlib import Path
import time
from bench.jev.angle_lab.native import canonical, sha


def key(request):
    return sha(canonical(request))


def oracle(request):
    """Transparent injected oracle, not a Jev latency or efficacy measurement."""
    state = request['state']
    if state['text'] == 'transport_failure':
        return {'status':'transport_failure'}
    if state['text'] == 'unjudged':
        return {'status':'unjudged'}
    yes = state['text'] == request['question']['match']
    if request['question']['negate']:
        yes = not yes
    return {'status':'ok','noul':.96 if yes else .04}


class Cache:
    def __init__(self, enabled=True, broken=False):
        self.enabled, self.broken = enabled, broken
        self.raw = {}
        self.calls = self.lookups = self.input_bytes = self.output_bytes = 0

    def judge(self, request):
        self.lookups += 1
        identity = key(request['state']) if self.broken else key(request)
        if self.enabled and identity in self.raw:
            return json.loads(self.raw[identity])
        self.calls += 1
        self.input_bytes += len(canonical(request))
        result = oracle(request)
        raw = canonical(result)
        self.output_bytes += len(raw)
        if self.enabled and result['status'] == 'ok':
            self.raw[identity] = raw
        return copy.deepcopy(result)


def request(text='allow', repo='repo-a', **changes):
    result = {'state':{'text':text,'repo':repo,'tenant':'tenant-a'},
              'question':{'match':'allow','negate':False},
              'schema':['noul'],'model':'jev-1.13.0','contract':'native-v1'}
    result.update(changes)
    return result


def negative_and_mutation_checks():
    base=request()
    changed=request(question={'match':'allow','negate':True})
    broken=Cache(broken=True)
    a,b=broken.judge(base),broken.judge(changed)
    assert a == b and b != oracle(changed)
    proper=Cache()
    first=proper.judge(base)
    for field, value in [('state',{'text':'deny','repo':'repo-a','tenant':'tenant-a'}),
                         ('question',{'match':'allow','negate':True}),
                         ('schema',['noul','v2']),('model','concrete-model-b'),('contract','native-v2')]:
        mutated=copy.deepcopy(base); mutated[field]=value
        before=proper.calls
        assert proper.judge(mutated) == oracle(mutated)
        assert proper.calls == before + 1
    # Same content and question in a different repo must never share observations.
    before=proper.calls; proper.judge(request(repo='repo-b')); assert proper.calls==before+1
    before=proper.calls
    for text in ['transport_failure','unjudged']:
        proper.judge(request(text)); proper.judge(request(text))
    assert proper.calls==before+4
    # Changing only the derivation threshold reuses raw probabilities, not booleans.
    assert first['noul']>=.9 and not first['noul']>=.99
    return {'bad_key_wrong_answer_reproduced':True,'evidence_question_schema_model_contract_scope_miss':True,
            'failure_and_unjudged_not_cached':True,'threshold_recomputed_from_raw':True}


def experiment(n):
    # Occurrence ID is outside semantic input. Repeated content deduplicates within scope.
    rows=[{'occurrence':i,'text':'allow' if i%2==0 else 'deny','repo':f'repo-{i%3}'} for i in range(n)]
    variants=[('cold',None,.9),('unchanged',None,.9),('one_evidence_change',0,.9),
              ('threshold_change',None,.99),('instruction_change',None,.9)]
    result={}
    reference=[]
    for name, changed, threshold in variants:
        negated=name=='instruction_change'
        # Independently compute every output without calling oracle/cache/key.
        reference.append([{'id':r['occurrence'],'accepted':
            ((('deny' if r['occurrence']==changed else r['text'])=='allow') != negated)
            and threshold <= .96} for r in rows])
    for arm in ['recompute','plain_exact_cache']:
        engine=Cache(enabled=arm!='recompute'); outputs=[]; stages=[]
        start=time.perf_counter()
        for name,changed,threshold in variants:
            before=engine.calls; out=[]
            for r in rows:
                state='deny' if r['occurrence']==changed else r['text']
                req=request(state,r['repo'],question={'match':'allow','negate':name=='instruction_change'})
                raw=engine.judge(req)
                out.append({'id':r['occurrence'],'accepted':raw['noul']>=threshold})
            outputs.append(out); stages.append({'stage':name,'calls':engine.calls-before,'outputs_sha256':sha(canonical(out))})
        assert outputs==reference
        result[arm]={'oracle_evaluations':engine.calls,'lookups':engine.lookups,'input_bytes':engine.input_bytes,
                     'output_bytes':engine.output_bytes,'local_seconds':time.perf_counter()-start,
                     'stage_results':stages,'all_occurrence_arrays_match_independent_reference':True}
    return {'occurrences':n,'scoped_unique_inputs':6,'arms':result,
            'distinct_incremental_engine_measured':False,'jev_requests':0}


if __name__=='__main__':
    print(json.dumps({'checks':negative_and_mutation_checks(),'scales':[experiment(n) for n in (1000,10000)],
                      'interpretation':'Injected-oracle mechanism and local timings only. Plain cache is the baseline to beat.'},indent=2))
