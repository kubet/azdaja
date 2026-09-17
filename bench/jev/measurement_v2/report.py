"""Reconstruct measurement outcomes from frozen inputs and retained native bodies."""
import argparse
import json
import math
from pathlib import Path
from bench.jev.angle_lab import native as n
from .run import HERE, BINARY_SHA, packs


def probability(value):
    if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=1:
        raise ValueError('probability domain')
    return value


def decisions(body,request):
    if body['model'] != n.MODEL or body['_azdaja']['request_sha256'] != n.sha(n.canonical(request)):
        raise ValueError('transport identity')
    if set(body['answers']) != set(request['questions']): raise ValueError('answer coverage')
    labels, ps = {}, {}
    for qid,q in request['questions'].items():
        answer=body['answers'][qid]
        if answer['type']!=q['type']: raise ValueError('answer type')
        if q['type']=='noul':
            ps[qid]=probability(answer['noul']); labels[qid]='yes' if ps[qid]>=.5 else 'no'
        else:
            probs=answer['probabilities']
            if set(probs)!=set(q['criteria']): raise ValueError('choice coverage')
            values=[probability(v) for v in probs.values()]
            if abs(math.fsum(values)-1)>1e-5: raise ValueError('choice sum')
            chosen=answer['choice']
            if chosen not in probs or probs[chosen] < max(values)-1e-9: raise ValueError('choice winner')
            probability(answer['confidence']); labels[qid]=chosen
    return labels,ps


def grade(gold,labels,ps=None):
    if set(labels)-set(gold): raise ValueError('unknown observed ID')
    ps=ps or {}
    result={}
    for lane,total in [('flat',100),('verifier',200)]:
        ids=[qid for qid in labels if gold[qid]['lane']==lane]
        wrong=[qid for qid in ids if labels[qid]!=gold[qid]['expected']]
        row={'observed':len(ids),'required':total,'complete':len(ids)==total,'correct':len(ids)-len(wrong),'errors':wrong}
        if lane=='flat':
            empty=[qid for qid in ids if gold[qid]['expected']=='no_match']
            row.update(no_match_observed=len(empty),no_match_correct=sum(labels[q]=='no_match' for q in empty),
                       first_window_control_correct=sum(gold[q]['expected']=='w0' for q in ids),
                       always_no_match_control_correct=len(empty))
            row['absolute_quality_bar_passed']=row['complete'] and row['correct']>=95 and row['no_match_correct']>=24
        else:
            bad=[q for q in ids if gold[q]['expected']=='no']; good=[q for q in ids if gold[q]['expected']=='yes']
            row.update(unsupported_observed=len(bad),supported_observed=len(good),
                       false_support=sum(labels[q]=='yes' for q in bad),false_flags=sum(labels[q]=='no' for q in good),
                       approved_actions=0,always_flag_false_support=0,always_flag_false_flags=len(good),
                       never_flag_false_support=len(bad),never_flag_false_flags=0)
            row['absolute_quality_bar_passed']=row['complete'] and row['false_support']==0 and row['false_flags']<=5
            if ps:
                if set(ps)!=set(ids): raise ValueError('probability coverage')
                for v in ps.values(): probability(v)
                row['brier_score']=math.fsum((ps[q]-(gold[q]['expected']=='yes'))**2 for q in ids)/len(ids)
                bins=[]
                for index in range(5):
                    group=[q for q in ids if min(4,int(ps[q]*5))==index]
                    bins.append({'lower':index/5,'upper':(index+1)/5,'n':len(group),
                        'mean_probability':math.fsum(ps[q] for q in group)/len(group) if group else None,
                        'observed_support_fraction':sum(gold[q]['expected']=='yes' for q in group)/len(group) if group else None})
                row['reliability_bins']=bins
                row['risk_coverage']=[]
                for threshold in (.6,.7,.8,.9,.95):
                    selected=[q for q in ids if max(ps[q],1-ps[q])>=threshold]
                    row['risk_coverage'].append({'threshold':threshold,'selected':len(selected),'total':len(ids),
                        'errors':sum(labels[q]!=gold[q]['expected'] for q in selected)})
                row['calibration_generalization_established']=False
        result[lane]=row
    return result


def verify(directory):
    directory=Path(directory)
    receipt=n.strict_loads((directory/'receipt.json').read_bytes())
    frozen=n.strict_loads((HERE/'FROZEN.json').read_bytes())
    for path,expected in frozen['files'].items():
        if n.sha(Path(path).read_bytes())!=expected: raise ValueError('frozen source changed')
    if receipt['binary_sha256']!=BINARY_SHA or receipt['requested_model']!=n.MODEL or receipt['generative_model']!=n.GENERATOR:
        raise ValueError('receipt model identity')
    gold=n.strict_loads((HERE/'fixtures/gold.json').read_bytes()); rows=packs()
    lookup={row['name']:row for row in rows}
    observed={'typed':{},'generative':{}}; ps={}; seen=set(); totals={'input_tokens':0,'output_tokens':0}
    measures={lane:{arm:{'whole_operation_seconds':0.,'native_call_seconds':0.,'input_tokens':0,'output_tokens':0,'calls':0} for arm in observed} for lane in ('flat','verifier')}
    for event in receipt['benchmark_rows']:
        name,arm=event['fixture'],event['arm']
        if name not in lookup or arm not in observed or (name,arm) in seen: raise ValueError('attempt sequence')
        seen.add((name,arm)); row=lookup[name]; pack=row['pack']; prefix=name+'-'+arm
        if event['input_sha256']!=n.sha(n.canonical(pack)) or event['question_ids']!=sorted(pack['questions']): raise ValueError('input binding')
        if event['automatic_approval_authorized'] or event['official_rah_submission']: raise ValueError('claim escalation')
        if event['status']!='completed': continue
        call=event['native_call']
        if call not in receipt['calls'] or call['name']!=prefix: raise ValueError('call evidence')
        if arm=='typed':
            request=n.strict_loads((directory/(prefix+'-request.json')).read_bytes())
            if request!=n.inspect_pack(pack): raise ValueError('request body changed')
            retained=n.strict_loads((directory/(prefix+'-observation.json')).read_bytes())
            body=retained['observation']; labels,probabilities=decisions(body,request)
            usage=body['usage']; stats=retained['stats']
            if any(type(usage[k]) is not int or usage[k]<0 for k in ('input_tokens','output_tokens')): raise ValueError('usage domain')
            if stats['provider_requests']!=1 or stats['known_input_tokens']!=usage['input_tokens'] or stats['unknown_input_usage_requests']!=0: raise ValueError('usage binding')
            for k in totals: totals[k]+=usage[k]
            if totals['input_tokens']>1500000: raise ValueError('token envelope')
            ps.update(probabilities)
            digest=n.sha(n.canonical(body))
        else:
            prompt=n.strict_loads((directory/(prefix+'-prompt.json')).read_bytes())
            if prompt['payload']!={'state':pack['state'],'questions':pack['questions']}: raise ValueError('unmatched inputs')
            labels=n.strict_loads(n.strict_loads((directory/(prefix+'-raw.json')).read_bytes())['text'])
            if set(labels)!=set(pack['questions']): raise ValueError('generative coverage')
            for qid,value in labels.items():
                q=pack['questions'][qid]; domain=('yes','no') if q['type']=='noul' else q['criteria']
                if type(value) is not str or value not in domain: raise ValueError('generative domain')
            digest=n.sha(n.canonical(labels))
            usage={k:call['usage'][k]['known_total'] for k in ('input_tokens','output_tokens')}
        if digest!=event['response_sha256']: raise ValueError('response binding')
        if set(observed[arm])&set(labels): raise ValueError('duplicate judgment')
        observed[arm].update(labels)
        target=measures[row['lane']][arm]; target['calls']+=1
        for k in ('input_tokens','output_tokens'): target[k]+=usage[k]
        for key,value in [('whole_operation_seconds',event['whole_operation_seconds']),('native_call_seconds',call['seconds'])]:
            if type(value) not in (int,float) or not math.isfinite(value) or value<0: raise ValueError('timing domain')
            target[key]+=value
    if receipt['status']=='completed' and (len(seen)!=2*len(rows) or any(len(x)!=300 for x in observed.values())):
        raise ValueError('false completion')
    if totals['input_tokens']!=receipt['known_typed_input_tokens'] or totals['output_tokens']!=receipt['known_typed_output_tokens']:
        raise ValueError('receipt usage mismatch')
    trace=n.usage_summary(directory/'model-trace.jsonl')
    if trace!=receipt['generative_trace']: raise ValueError('trace mismatch')
    grades={'typed':grade(gold,observed['typed'],ps),'generative':grade(gold,observed['generative'])}
    bars={}
    for lane in measures:
        t,g=grades['typed'][lane],grades['generative'][lane]
        bars[lane]={'complete':t['complete'] and g['complete'],
                    'quality_bar_passed':t['absolute_quality_bar_passed'] and g['complete'] and t['correct']>=g['correct'],
                    'speed_ratio_whole_operations':measures[lane]['typed']['whole_operation_seconds']/measures[lane]['generative']['whole_operation_seconds'] if measures[lane]['generative']['whole_operation_seconds'] else None}
    return {'schema_version':1,'schema':'azdaja.measurement_v2.replay.v1','replay_consistent':True,
            'status':receipt['status'],'quality':grades,'metrics':measures,'bars':bars,
            'known_typed_input_tokens':totals['input_tokens'],'known_typed_output_tokens':totals['output_tokens'],
            'typed_documented_cost_estimate_usd':totals['input_tokens']*.042/1e6,'billing_known':False,
            'generative_usage':trace['usage'],'generative_dollars_known':False,'official_rah_submission':False,
            'general_advantage_established':False,'automatic_approval_authorized':False,
            'limits':['Selected short SQuAD2 paragraphs, not million-token retrieval.',
                      'Official annotations are operational gold; possible annotation noise and training contamination.',
                      'Questions are clustered by article. Counts are not independent replications.',
                      'No production threshold or automatic approval is authorized.']}


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--run',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    result=verify(args.run)
    with args.output.open('xb') as stream: stream.write(n.canonical(result)+b'\n')
    print(json.dumps({'replay_consistent':True,'bars':result['bars'],'typed_cost_estimate_usd':result['typed_documented_cost_estimate_usd']}))


if __name__=='__main__': main()
