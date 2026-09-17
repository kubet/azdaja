"""Independent provider-free row645 source and retained-judgment audit."""
import argparse
from collections import Counter
import datetime
import json
import math
from pathlib import Path
import re
from bench.jev.angle_lab import native as n

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'bench/oolong/context-131072.txt'
ROW=ROOT/'bench/oolong/row-645.json'
RESULT=ROOT/'bench/jev/angle_lab/results/continuation-completed'


def audit():
    raw=SOURCE.read_bytes(); text=raw.decode('utf-8'); row=n.strict_loads(ROW.read_bytes())
    if n.sha(raw)!=row['context_sha256'] or len(raw)!=row['context_bytes']:
        raise ValueError('official source identity')
    records=[]; nonrecords=[]
    pattern=re.compile(r'Date: ([A-Za-z]{3}) (\d{2}), (\d{4}) \|\| User: (\d+) \|\| Instance:(.*)\Z')
    months={name:index+1 for index,name in enumerate(('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'))}
    for physical,line in enumerate(text.splitlines(keepends=True),1):
        clean=line.removesuffix('\n').removesuffix('\r')
        match=pattern.fullmatch(clean)
        if match:
            month,day,year,user,message=match.groups()
            datetime.date(int(year),months[month],int(day))
            records.append({'id':f'r{physical:04d}','raw':line,'month':month,'message':message})
        elif clean.startswith('Date:'):
            raise ValueError('malformed record')
        else:
            nonrecords.append({'line':physical,'text':clean})
    # Independent LF framing must not disagree with Python's broader Unicode splitlines.
    lf_records=[line for line in text.split('\n') if line.startswith('Date:')]
    if [r['raw'].removesuffix('\n').removesuffix('\r') for r in records]!=lf_records:
        raise ValueError('record boundary disagreement')
    header=re.search(r'contain (\d+) text messages, one per line',text)
    if not header or len(records)!=int(header.group(1)):
        raise ValueError('record coverage')
    selected=[r for r in records if months[r['month']]==5]
    expected={r['id']:r['raw'] for r in selected}
    submitted={}; probabilities={}; direct={}; files={str(SOURCE.relative_to(ROOT)):n.sha(raw),str(ROW.relative_to(ROOT)):n.sha(ROW.read_bytes())}
    for i in range(1,6):
        def load(suffix):
            path=RESULT/f'gate-{i}-{suffix}.json'; data=path.read_bytes()
            files[str(path.relative_to(ROOT))]=n.sha(data)
            return n.strict_loads(data)
        request=load('typed-request'); observation=load('typed-observation'); prompt=load('direct-prompt'); answer=load('direct-raw')
        body=observation['observation']; entries=request['state']['records']
        if set(submitted)&set(entries) or set(entries)!=set(request['questions']): raise ValueError('duplicate or incomplete pack')
        if prompt['payload']!={'state':request['state'],'questions':request['questions']}: raise ValueError('unmatched models')
        if body['_azdaja']['request_sha256']!=n.sha(n.canonical(request)) or body['model']!='jev-1.13.0': raise ValueError('response identity')
        if set(body['answers'])!=set(entries): raise ValueError('answer coverage')
        submitted.update(entries)
        for key,value in body['answers'].items():
            p=value['noul']
            if value['type']!='noul' or type(p) not in (int,float) or not math.isfinite(p) or not 0<=p<=1: raise ValueError('probability')
            probabilities[key]=p
        labels=n.strict_loads(answer['text'])
        if set(labels)!=set(entries) or any(v not in ('yes','no') for v in labels.values()): raise ValueError('direct coverage')
        direct.update(labels)
    if submitted!=expected or set(probabilities)!=set(expected) or set(direct)!=set(expected): raise ValueError('submitted source mismatch')
    typed_set={key for key,p in probabilities.items() if p>=.5}; direct_set={key for key,v in direct.items() if v=='yes'}
    official=int(n.strict_loads(row['answer'])[0])
    mass=math.fsum(probabilities.values())
    duplicates=Counter(r['message'] for r in selected)
    return {'schema_version':1,'schema':'azdaja.row645_forensic_audit.v1','provider_calls':0,
            'official_question':row['question'],'official_aggregate_gold':official,'full_records':len(records),
            'may_occurrences':len(selected),'unique_may_messages':len(duplicates),
            'duplicate_message_occurrences':sum(c-1 for c in duplicates.values()),
            'complete_source_and_exact_model_input_equality':True,'month_filter_calendar_checked':True,
            'all_occurrences_preserved':True,'framing_implementations_agree':True,
            'shared_parser_or_reduction_defect_found':False,'aligned_official_per_item_gold_in_fixture':False,
            'typed_threshold_count':len(typed_set),'direct_count':len(direct_set),'shared_positive_count':len(typed_set&direct_set),
            'typed_only_positive':sorted(typed_set-direct_set),'direct_only_positive':sorted(direct_set-typed_set),
            'sum_noul':mass,'sum_noul_minus_gold':mass-official,
            'exactly_seven_false_positives_identified':False,'calibration_established':False,
            'interpretation':'Net aggregate error is not an identified false-positive set. Marginal expectation sums need no independence, but calibration and count variance are not established by one scalar gold.',
            'non_record_lines':nonrecords,'input_hashes':files,
            'occurrence_ledger':[{'id':r['id'],'source_sha256':n.sha(r['raw'].encode()),'message_sha256':n.sha(r['message'].encode()),'p_ham':probabilities[r['id']],'typed_ham':r['id'] in typed_set,'direct_ham':r['id'] in direct_set} for r in selected]}


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    result=audit()
    with args.output.open('xb') as stream: stream.write(n.canonical(result)+b'\n')
    print(json.dumps({k:result[k] for k in ('full_records','may_occurrences','typed_threshold_count','direct_count','shared_positive_count','sum_noul','sum_noul_minus_gold','shared_parser_or_reduction_defect_found')}))


if __name__=='__main__': main()
