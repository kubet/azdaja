"""Replay the fixed second-reader policies from retained native observations, no inference."""
import argparse
import json
import math
from pathlib import Path
from bench.jev.angle_lab import native as n
from bench.jev.second_reader import policy_run as run
from bench.jev.second_reader import policy_study as study


def check(condition, reason):
    if not condition: raise ValueError(reason)


def replay(folder):
    folder=Path(folder); receipt=n.strict_loads((folder/'receipt.json').read_bytes())
    check(receipt['status']=='completed' and receipt['cleanup_exit']==0,'completed clean native run required')
    for path,digest in receipt['frozen_files'].items(): check(n.sha(Path(path).read_bytes())==digest,'frozen source changed')
    expected=run.rows(); rows=receipt['panel_rows']
    check(len(rows)==len(expected)==12 and receipt['binary_sha256']==run.BINARY_SHA,'run identity')
    ledger=n.strict_loads((run.ROOT/'bench/jev/row645_labels/result.json').read_bytes())['occurrence_ledger']
    gold={r['id']:r['gold_ham'] for r in ledger}; old_p={r['id']:r['p_ham'] for r in ledger}
    original={r['id']:r['typed_ham'] for r in ledger}; baseline={r['id']:r['direct_ham'] for r in ledger}
    check(len(gold)==len(ledger)==227,'gold duplicate coverage')
    for field in (gold,original,baseline): check(all(type(v) is bool for v in field.values()),'ledger label type')
    disagreement={i for i in gold if original[i]!=baseline[i]}; check(len(disagreement)==4,'original disagreement count')
    observations={f'v{i}':{} for i in range(3)}; adjudicated={}; inputs=outputs=0
    calls={r['name']:r for r in receipt['calls']};check(len(calls)==12,'call coverage')
    for row,(name,arm,pack) in zip(rows,expected):
        check(row['name']==name and row['arm']==arm and row['status']=='completed','panel sequence')
        check(row['pack_sha256']==n.sha(n.canonical(pack)) and row['ids']==sorted(pack['questions']),'pack identity')
        call=calls[name];check(call['arm']==arm,'call arm')
        if arm=='generative':
            prompt=n.strict_loads((folder/(name+'-prompt.json')).read_bytes())
            check(prompt['payload']==pack,'blind adjudication source equality')
            raw=n.strict_loads((folder/(name+'-raw.json')).read_bytes())['text']; body=n.strict_loads(raw)
            study.validate_values(body,pack['questions'],False)
            adjudicated={qid.removeprefix('original_'):value=='yes' for qid,value in body.items()}
            check(set(adjudicated)==disagreement,'adjudication restricted to original disagreements')
        else:
            request=n.strict_loads((folder/(name+'-request.json')).read_bytes());check(request==dict(pack,model=n.MODEL),'typed source equality')
            result=n.strict_loads((folder/(name+'-observation.json')).read_bytes());check('failure' not in result,'failed typed response')
            body=result['observation'];meta=body['_azdaja'];stats=result['stats'];usage=body['usage']
            check(body['model']==n.MODEL and meta['request_sha256']==n.sha(n.canonical(request)),'typed response identity')
            check(set(body['answers'])==set(pack['questions']),'typed answer coverage')
            check(stats['provider_requests']==1 and stats['unknown_input_usage_requests']==0,'typed transport')
            check(meta['cache_hit'] is False and meta['provider_requests_this_call']==1,'not a fresh typed response')
            check(all(type(usage.get(k)) is int and usage[k]>=0 for k in ('input_tokens','output_tokens')),'usage types')
            check(stats['known_input_tokens']==usage['input_tokens']==call['known_input_tokens'],'input accounting')
            check(call['reported_output_tokens']==usage['output_tokens'] and meta['original_usage']==meta['new_request_usage']==usage,'output accounting')
            check(call['questions']==len(pack['questions']) and call['request_bytes']==len(n.canonical(request)),'call request accounting')
            for qid,answer in body['answers'].items():
                check(set(answer)=={'type','noul'} and answer['type']=='noul','noul shape')
                value=answer['noul'];check(type(value) in (int,float) and math.isfinite(value) and 0<=value<=1,'noul domain')
                variant,record=qid.split('_',1);check(record not in observations[variant],'duplicate observation')
                observations[variant][record]=value
            inputs+=usage['input_tokens'];outputs+=usage['output_tokens']
        check(row['response_sha256']==n.sha(n.canonical(body)),'response binding')
    check(receipt['typed_calls_started']==receipt['confirmed_typed_requests']==11 and receipt['typed_questions']==681,'typed total')
    check(receipt['typed_unknown_usage']==receipt['typed_unknown_output_usage']==0,'unknown usage')
    check(receipt['known_typed_input_tokens']==inputs and receipt['known_typed_output_tokens']==outputs,'usage total')
    trace=n.usage_summary(folder/'model-trace.jsonl')
    check(trace==receipt['generative_trace'] and trace['succeeded_events']==1 and trace['logical_request_ids']==receipt['logical_llm_calls']==1,'generative trace')
    check(1<=trace['entered_turns']<=2 and trace['observed_models']==[n.GENERATOR] and trace['observed_providers']==['OpenAI'],'generative identity')
    check(calls['adjudication']['usage']==trace['usage'],'generative call usage')
    phrasing=study.detached_grade(observations,gold)
    agreement={i:baseline[i] for i in gold if i not in disagreement}
    escalation=study.detached_adjudication_grade(agreement,adjudicated,gold)
    escalation.update(disagreement_ids=sorted(disagreement),new_labels=adjudicated,baseline_correct=sum(baseline[i]==gold[i] for i in gold),original_typed_correct=sum(original[i]==gold[i] for i in gold))
    fresh_v0=observations['v0']; phrasing['original_vs_fresh_v0']={
        'changed_labels':[i for i in gold if original[i]!=(fresh_v0[i]>=.5)],
        'mean_absolute_probability_change':sum(abs(fresh_v0[i]-old_p[i]) for i in gold)/len(gold),
        'interpretation':'new call and changed batch composition; not isolated wording effect'}
    old_errors={i for i in gold if original[i]!=gold[i]}
    phrasing['error_set_shifts_vs_original']={v:{'new_errors':sorted(set(stats['errors'])-old_errors),'resolved_errors':sorted(old_errors-set(stats['errors']))} for v,stats in phrasing['variants'].items()}
    return {'schema':'azdaja.second_reader.policy_replay.v1','consistent':True,'complete_panel':True,
        'adjudication':escalation,'phrasing':phrasing,'quality_scope':'known development panel; no generalization or safe-approval claim',
        'typed_requests':11,'typed_questions':681,'known_input_tokens':inputs,'known_output_tokens':outputs,
        'typed_seconds':sum(c['seconds'] for c in calls.values() if c['arm']=='typed'),
        'adjudication_seconds':calls['adjudication']['seconds'],'generative_trace':trace,
        'elapsed_seconds':receipt['elapsed_seconds'],'input_estimate_usd':inputs*.042/1e6,'billing_known':False,
        'retained_hashes':{str(p.relative_to(folder)):n.sha(p.read_bytes()) for p in sorted(folder.rglob('*')) if p.is_file() and 'private-work' not in p.parts}}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('receipt_dir',type=Path);ap.add_argument('--output',type=Path)
    args=ap.parse_args();report=replay(args.receipt_dir)
    if args.output:
        with args.output.open('xb') as f:f.write(n.canonical(report)+b'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='retained_hashes'},indent=2))


if __name__=='__main__':main()
