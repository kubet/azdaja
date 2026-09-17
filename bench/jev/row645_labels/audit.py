"""Align official labeled OOLONG row645 to every original source occurrence."""
import argparse
import json
import math
from pathlib import Path
import re

from bench.jev.angle_lab import native as n
from bench.jev.measurement_v2 import row645_audit as original

HERE=Path(__file__).resolve().parent
UPSTREAM_SHA='35d64e33db07b959a44806925b4a725aa2dc324eaad6734e2bcabc6ccb4c4728'
LABELED_SHA='8caaf42eb608818c6c98afa3034af6844e8761578bde7fa60dab71b0f9441251'
URL='https://datasets-server.huggingface.co/rows?dataset=oolongbench%2Foolong-synth&config=default&split=validation&offset=645&length=1'


def require(condition,reason):
    if not condition: raise ValueError(reason)


def align(envelope,source,row):
    require(envelope['partial'] is False and len(envelope['rows'])==1,'partial official data')
    entry=envelope['rows'][0]
    require(entry['row_idx']==645 and entry['truncated_cells']==[],'truncated or different row')
    data=entry['row']
    for field in ('id','context_len','dataset','context_window_id','question','task_group','task','answer'):
        require(data[field]==row[field],'row metadata mismatch: '+field)
    require(data['context_window_text'].encode()==source,'unlabeled source differs')
    rawlines=source.decode().splitlines(keepends=True)
    labeled=data['context_window_text_with_labels'].splitlines(keepends=True)
    require(len(rawlines)==len(labeled),'line coverage')
    labels={}
    for index,(raw,tagged) in enumerate(zip(rawlines,labeled),1):
        if not raw.startswith('Date:'):
            require(raw==tagged,'nonrecord bytes changed')
            continue
        match=re.fullmatch(r'(.*) \|\| Label: (ham|spam)(\n?)',tagged)
        require(match is not None,'label suffix grammar')
        require(match[1]+match[3]==raw,'occurrence bytes changed')
        labels[f'r{index:04d}']=match[2]
    require(len(labels)==2177,'record coverage')
    return labels


def confusion(ledger,field):
    fp=[r['id'] for r in ledger if r[field] and not r['gold_ham']]
    fn=[r['id'] for r in ledger if not r[field] and r['gold_ham']]
    return {'observed':len(ledger),'correct':len(ledger)-len(fp)-len(fn),
            'predicted_ham':sum(r[field] for r in ledger),'false_positive_ids':fp,
            'false_negative_ids':fn,'false_positives':len(fp),'false_negatives':len(fn)}


def audit(upstream):
    upstream=Path(upstream); raw=upstream.read_bytes()
    require(n.sha(raw)==UPSTREAM_SHA,'upstream snapshot changed')
    envelope=n.strict_loads(raw)
    labeled=envelope['rows'][0]['row']['context_window_text_with_labels']
    require(n.sha(labeled.encode())==LABELED_SHA,'labeled context identity')
    row=n.strict_loads(original.ROW.read_bytes()); source=original.SOURCE.read_bytes()
    labels=align(envelope,source,row)
    previous=original.audit()
    ledger=[]
    lines=source.decode().splitlines(keepends=True)
    for entry in previous['occurrence_ledger']:
        item=dict(entry,gold=labels[entry['id']],gold_ham=labels[entry['id']]=='ham')
        item['source_line_number']=int(entry['id'][1:])
        require(n.sha(lines[item['source_line_number']-1].encode())==entry['source_sha256'],'ledger source binding')
        ledger.append(item)
    total=sum(r['gold_ham'] for r in ledger)
    require(total==previous['official_aggregate_gold']==132,'aligned gold aggregate')
    typed=confusion(ledger,'typed_ham'); direct=confusion(ledger,'direct_ham')
    fp_t=set(typed['false_positive_ids']);fp_g=set(direct['false_positive_ids'])
    bins=[]
    for index in range(5):
        group=[r for r in ledger if min(4,int(r['p_ham']*5))==index]
        bins.append({'lower':index/5,'upper':(index+1)/5,'n':len(group),
                     'mean_p_ham':math.fsum(r['p_ham'] for r in group)/len(group) if group else None,
                     'observed_ham_fraction':sum(r['gold_ham'] for r in group)/len(group) if group else None})
    return {'schema_version':1,'schema':'azdaja.row645_official_item_gold.v1','provider_calls':0,
            'source_url':URL,'official_snapshot_sha256':UPSTREAM_SHA,'labeled_context_sha256':LABELED_SHA,
            'unlabeled_context_sha256':n.sha(source),'all_2177_occurrences_aligned_byte_for_byte':True,
            'may_occurrences':len(ledger),'aligned_official_ham':total,
            'shared_parser_or_reduction_defect_found':False,
            'typed':typed,'generative':direct,'shared_false_positive_ids':sorted(fp_t&fp_g),
            'typed_only_false_positive_ids':sorted(fp_t-fp_g),'generative_only_false_positive_ids':sorted(fp_g-fp_t),
            'sum_noul':math.fsum(r['p_ham'] for r in ledger),'sum_noul_minus_gold':previous['sum_noul_minus_gold'],
            'brier_score':math.fsum((r['p_ham']-r['gold_ham'])**2 for r in ledger)/len(ledger),
            'reliability_bins':bins,'calibration_generalization_established':False,
            'model_inputs_changed':False,'rerun_performed':False,
            'previous_audit_sha256':n.sha(n.canonical(previous)),
            'input_hashes':previous['input_hashes'],'occurrence_ledger':ledger,
            'interpretation':'Both models have7official-label false positives and0false negatives, but only5false positives are shared. Identical139 totals did not imply identical record sets or a shared counting bug. Official annotations are the benchmark reference, not an independent adjudication of every message.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,default=HERE/'official-row645.json')
    ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    result=audit(args.upstream)
    with args.output.open('xb') as stream:stream.write(n.canonical(result)+b'\n')
    print(json.dumps({k:result[k] for k in ('may_occurrences','aligned_official_ham','typed','generative','sum_noul','sum_noul_minus_gold','brier_score','shared_parser_or_reduction_defect_found')}))


if __name__=='__main__':main()
