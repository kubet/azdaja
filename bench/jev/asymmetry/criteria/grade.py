"""Source-bound offline replay. Probability, billing, and agreement are not authority."""
from __future__ import annotations
import argparse
from decimal import Decimal
import math
import os
from pathlib import Path
import statistics
from bench.jev.angle_lab import native as n
from bench.jev.asymmetry.criteria import run as r

GOLD = r.p.ROOT/'bench/jev/row645_labels/result.json'
GOLD_SHA = 'd6669f2e4b5be492721a51923f3b4a02eb03fbfbc5d9749663df7dcae1438827'


def need(value, message):
    if not value:
        raise ValueError(message)


def load(path):
    return n.strict_loads(Path(path).read_bytes())


def confusion(predicted,gold):
    need(set(predicted)==set(gold) and all(type(v) in (bool,type(None)) for v in predicted.values()),'score coverage/domain')
    judged = {k:v for k,v in predicted.items() if v is not None}
    tp = sum(v and gold[k] for k,v in judged.items())
    fp = sum(v and not gold[k] for k,v in judged.items())
    fn = sum(not v and gold[k] for k,v in judged.items())
    tn = sum(not v and not gold[k] for k,v in judged.items())
    unknown = len(gold)-len(judged)
    return dict(observed=len(gold),judged=len(judged),unresolved=unknown,tp=tp,fp=fp,fn=fn,tn=tn,
                errors=fp+fn,coverage=len(judged)/len(gold) if gold else None,
                accuracy_on_judged=(tp+tn)/len(judged) if judged else None,known_ham=tp+fp,
                signed_count_error=None if unknown else tp+fp-sum(gold.values()),
                decision_range_due_only_to_unresolved=[tp+fp,tp+fp+unknown],automatic_approval=False)


def score(values,gold):
    need(set(values)==set(gold) and all(type(v) is bool for v in gold.values()),'label coverage/domain')
    for row in values.values():
        need(type(row) is dict and set(row)==set(r.p.ARMS),'arm coverage')
        need(all(type(v) in (int,float) and math.isfinite(v) and 0<=v<=1 for v in row.values()),'probability domain')
    predictions = {a:{k:(v[a]>=.5 if a!='inverse_spam' else v[a]<.5) for k,v in values.items()} for a in r.p.ARMS}
    out = {}
    for arm,pred in predictions.items():
        out[arm] = confusion(pred,gold)
        out[arm]['sum_ham_probability'] = str(sum(Decimal(str(v[arm])) if arm!='inverse_spam' else 1-Decimal(str(v[arm])) for v in values.values()))
        out[arm]['corrected_vs_fresh_control'] = sum(pred[k]==gold[k] and predictions['control'][k]!=gold[k] for k in gold)
        out[arm]['regressed_vs_fresh_control'] = sum(pred[k]!=gold[k] and predictions['control'][k]==gold[k] for k in gold)
    for arm in ('control','criteria_ham'):
        pred = {k:predictions[arm][k] if predictions[arm][k]==predictions['inverse_spam'][k] else None for k in gold}
        out[arm+'_inverse_agreement'] = confusion(pred,gold)
    return out


def integer(value):
    return type(value) is int and value>=0


def replay(directory):
    directory = Path(directory)
    receipt = load(directory/'receipt.json')
    need(receipt.get('experiment_schema')==r.SCHEMA and receipt.get('status') in ('completed','stopped')
         and receipt.get('synthetic_observations') is False,'not a terminal live criteria receipt')
    need(receipt.get('binary_sha256')==r.BINARY_SHA and receipt.get('requested_model')==n.MODEL and receipt.get('caps')==r.CAPS,'runtime identity/caps')
    need(receipt.get('logical_llm_calls')==0 and not (directory/'model-trace.jsonl').exists(),'generative events')
    elapsed=receipt.get('elapsed_seconds')
    need(type(elapsed) in (int,float) and math.isfinite(elapsed) and elapsed>=0,'elapsed domain')
    need(receipt['status']!='completed' or elapsed<=r.MAX_SECONDS,'completed elapsed deadline')
    files = receipt.get('frozen_files')
    need(type(files) is dict and bool(files),'missing frozen files')
    for path,digest in files.items():
        need(Path(path).is_file() and n.sha(Path(path).read_bytes())==digest,'frozen source changed')
    seals = [Path(x) for x in files if Path(x).name=='FROZEN.json']
    need(len(seals)==1,'seal missing')
    seal = load(seals[0]); marker = load(seals[0].with_suffix('.started'))
    need(marker.get('seal_sha256')==n.sha(seals[0].read_bytes()) and marker.get('automatic_retry') is False,'admission marker')
    prepared = r.rows()
    need(seal.get('panel')==r.identities(prepared) and seal.get('caps')==r.CAPS,'frozen panel')
    need(seal.get('files')=={k:v for k,v in files.items() if Path(k)!=seals[0]},'frozen inventory')
    binaries=[Path(path) for path,digest in seal['files'].items() if digest==r.BINARY_SHA]
    need(len(binaries)==1,'frozen binary missing')
    need(seal['files']==r.inventory(binaries[0]),'incomplete frozen source inventory')
    panel,calls = receipt.get('panel_rows'),receipt.get('calls')
    need(type(panel) is list and len(panel)<=r.REQUESTS and type(calls) is list,'panel/calls missing')
    need(len({x.get('name') for x in calls})==len(calls),'duplicate calls')
    callmap = {x['name']:x for x in calls}
    need(set(callmap)<=set(x.get('name') for x in panel),'extra calls')
    seen = {}; inputs=outputs=provider=admitted=questions=unknown_in=unknown_out=attempts=0
    durations=[]; failed_bodies=0; prior_end=0
    for index,row in enumerate(panel):
        name,pack = prepared[index]
        request = n.inspect_pack(pack); reqsha = n.sha(n.canonical(request)); qcount=len(pack['questions'])
        need(row.get('name')==name and row.get('request_sha256')==reqsha and row.get('question_count')==qcount,'identity binding')
        need(row.get('status') in ('completed','attempted'),'row status')
        if row['status']!='completed':
            need(index==len(panel)-1 and receipt['status']=='stopped','nonterminal failure')
        request_path = directory/(name+'-request.json')
        if request_path.exists():
            need(load(request_path)==request,'request differs')
        rawpath=directory/(name+'-observation.json')
        if not rawpath.exists():
            need(row['status']!='completed' and name not in callmap,'missing completed observation')
            # Admission before response is reflected as one unknown attempt only by receipt.
            continue
        need(request_path.exists() and name in callmap,'request/call evidence missing')
        raw=load(rawpath); stats=raw.get('stats'); call=callmap[name]
        need(type(stats) is dict and all(integer(stats.get(k)) for k in ('attempts','provider_requests','questions','known_input_tokens','unknown_input_usage_requests')),'raw stats domain')
        need(stats['attempts']<=1 and stats['provider_requests']<=stats['attempts'] and stats['questions']==qcount and stats['unknown_input_usage_requests']<=stats['provider_requests'],'raw stats accounting')
        need(call.get('status') in ('completed','failed') and call.get('arm')=='typed' and call.get('request_sha256')==reqsha,'call binding')
        need(call.get('provider_requests')==stats['provider_requests'] and call.get('known_input_tokens')==stats['known_input_tokens'] and
             call.get('questions')==qcount and call.get('request_bytes')==len(n.canonical(request)),'call accounting')
        begin,end=call.get('admitted_elapsed_seconds'),call.get('completed_elapsed_seconds')
        need(all(type(v) in (int,float) and math.isfinite(v) and v>=0 for v in (begin,end,call.get('seconds')))
             and prior_end<=begin<=end,'call timing')
        prior_end=end
        admitted+=1; questions+=qcount; attempts+=stats['attempts']; provider+=stats['provider_requests']; inputs+=stats['known_input_tokens']
        unknown_in+=stats['unknown_input_usage_requests']
        body=raw.get('observation')
        if isinstance(body,dict):
            usage=body.get('usage',{})
            need(all(integer(usage.get(k)) for k in ('input_tokens','output_tokens')),'body usage')
            need(usage['input_tokens']==stats['known_input_tokens'],'usage consistency')
            if 'reported_output_tokens' in call:
                need(call['reported_output_tokens']==usage['output_tokens'],'call output')
                outputs+=usage['output_tokens']
            else:
                unknown_out+=stats['provider_requests']
            if row['status']!='completed': failed_bodies+=1
        else:
            unknown_out+=stats['provider_requests']
        if row['status']!='completed':
            need(call['status']=='failed','failed row/call mismatch')
            continue
        need(call['status']=='completed' and body is not None,'completed evidence')
        try:
            r.validate_body(body,pack); r.validate_success_stats(stats,body,pack)
        except n.Stop as exc:
            raise ValueError(str(exc)) from exc
        need(end<=r.MAX_SECONDS and inputs<=r.MAX_INPUT and outputs<=r.MAX_OUTPUT,'completed resource envelope')
        need(row.get('response_sha256')==call.get('response_sha256')==n.sha(n.canonical(body)),'response binding')
        need(call.get('native_elapsed_ms')==body['_azdaja']['elapsed_ms'] and call.get('response_json_bytes')==len(n.canonical(body)),'call body metadata')
        need(load(directory/(name+'-reentry-result.json'))==body,'reentry differs')
        need(load(directory/(name+'-custody-result.json'))==dict(request_sha256=reqsha,ids=sorted(pack['questions']),attempts=0),'custody differs')
        for qid,answer in body['answers'].items():
            need(qid not in seen,'duplicate answer'); seen[qid]=answer['noul']
        durations.append(call['seconds'])
    # A transport killed before retaining stats can leave one explicitly unknown admission.
    remaining=receipt.get('typed_calls_started',-1)-admitted
    need(type(remaining) is int and remaining in (0,1) and (not remaining or receipt['status']=='stopped'),'unaccounted admission')
    if remaining:
        need(len(panel)>admitted and panel[-1]['status']=='attempted','missing failed admission')
        unknown_in+=1; unknown_out+=1; questions+=panel[-1]['question_count']
    need(receipt.get('known_typed_input_tokens')==inputs and receipt.get('known_typed_output_tokens')==outputs and
         receipt.get('confirmed_typed_requests')==provider and receipt.get('typed_unknown_usage')==unknown_in and
         receipt.get('typed_unknown_output_usage')==unknown_out and receipt.get('typed_questions')==questions,'usage totals')
    complete=receipt['status']=='completed'
    if complete:
        need(len(panel)==r.REQUESTS and len(seen)==r.QUESTIONS and admitted==provider==attempts==r.REQUESTS and
             not unknown_in and not unknown_out and receipt.get('cleanup_exit')==0,'false completion')
        reduction=dict(expected=r.QUESTIONS,observed=r.QUESTIONS,complete=True,attempts=0)
        need(receipt.get('reduction')==load(directory/'reduce-result.json')==reduction,'final reduction')
    need(n.sha(GOLD.read_bytes())==GOLD_SHA,'gold source changed')
    goldrows=load(GOLD)['occurrence_ledger']
    gold={x['id']:x['gold_ham'] for x in goldrows}
    need(set(gold)==set(x['id'] for x in r.p.occurrences()),'gold coverage')
    values={}
    for record in r.p.occurrences():
        rid=record['id']
        if all(rid+'__'+r.p.ARM_SUFFIX[a] in seen for a in r.p.ARMS):
            values[rid]={a:seen[rid+'__'+r.p.ARM_SUFFIX[a]] for a in r.p.ARMS}
    return dict(schema='azdaja.asymmetry.criteria_grade.v2',status=receipt['status'],complete_panel=complete,
                complete_triplets=len(values),unobserved_triplets=len(gold)-len(values),eligible_questions=len(seen),
                preserved_failed_bodies_excluded_from_quality=failed_bodies,known_input_tokens=inputs,known_output_tokens=outputs,
                confirmed_requests=provider,native_attempts=attempts,unknown_input_usage=unknown_in,unknown_output_usage=unknown_out,
                input_cost_estimate_usd=str(Decimal(inputs)*Decimal('.042')/1000000),billing_known=False,
                median_completed_call_seconds=statistics.median(durations) if durations else None,elapsed_seconds=receipt.get('elapsed_seconds'),
                scores=score(values,{k:gold[k] for k in values}),raw_probabilities=seen,
                development_panel_only=True,co_presented_arms=False,independent_observations_established=False,
                automatic_approval_authorized=False,new_provider_calls=0)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--receipt-dir',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args(argv)
    if os.path.lexists(args.output): ap.error('output exists')
    report=replay(args.receipt_dir)
    with args.output.open('xb') as f: f.write(n.canonical(report)+b'\n')
    print(n.canonical({k:report[k] for k in ('status','complete_triplets','scores')}).decode())


if __name__=='__main__': main()
