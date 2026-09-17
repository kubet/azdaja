"""Replay frozen cumulative evidence. Incomplete panels cannot become wins."""
import argparse
import json
import math
from pathlib import Path
from . import evidence as e
from .run import HERE
from bench.jev.angle_lab import native as n
from bench.jev.measurement_v2 import report as original_report


def combined(directory=None):
    previous = e.predecessor()
    runs = [previous]
    manifest = None
    if directory is not None:
        manifest = e.load(HERE/'FROZEN.json')
        for path, digest in manifest['files'].items():
            e.check(n.sha(Path(path).read_bytes()) == digest, 'continuation frozen bytes changed')
        current = e.read_run(directory, e.CONTINUATION_ORDER)
        receipt = current['receipt']
        e.check(receipt['predecessor_receipt_sha256'] == n.sha((e.PREDECESSOR/'receipt.json').read_bytes()), 'predecessor binding')
        e.check(receipt['carried_totals'] == previous['totals'], 'carried accounting')
        e.check(receipt['original_study_status'] == 'stopped', 'original failure hidden')
        e.check(receipt['cumulative_totals'] == {key: value+current['totals'][key] for key,value in previous['totals'].items()}, 'cumulative accounting')
        runs.append(current)
    return summarize(runs, manifest)


def summarize(runs, manifest=None):
    labels = {'typed':{},'generative':{}}
    ps, attempted, seen = {}, [], set()
    for run in runs:
        e.check(not seen.intersection(run['order']), 'repeat across campaigns')
        seen.update(run['order'])
        for arm in labels:
            e.check(not set(labels[arm]).intersection(run['labels'][arm]), 'duplicate outcome')
            labels[arm].update(run['labels'][arm])
        ps.update(run['probabilities']); attempted.extend(run['attempts'])
    totals = {key:sum(r['totals'][key] for r in runs) for key in runs[0]['totals']}
    entered = sum(r['trace']['entered_turns'] for r in runs)
    elapsed = sum(r['receipt']['elapsed_seconds'] for r in runs)
    e.check(totals['typed_calls_started']<=12 and totals['logical_llm_calls']<=12 and entered<=24
            and totals['known_typed_input_tokens']<=n.MAX_INPUT, 'cumulative resource envelope')
    # Small finish/checkpoint overhead may occur after the last eligible request.
    e.check(sum(a['whole_operation_seconds'] for a in attempted)<=1800.1, 'cumulative active lower bound')
    gold = e.load(e.ORIGINAL/'fixtures/gold.json')
    grades = {arm:original_report.grade(gold, answers, ps if arm=='typed' else None) for arm,answers in labels.items()}
    lanes = {}
    for lane in ('flat','verifier'):
        ids = [qid for qid,g in gold.items() if g['lane']==lane]
        t,g = grades['typed'][lane],grades['generative'][lane]
        matched = set(q for q in ids if q in labels['typed'] and q in labels['generative'])
        perarm = {}
        matchedpacks = {a['fixture'] for a in attempted if a['lane']==lane and a['completed'] and a['arm']=='typed'} & {
                        a['fixture'] for a in attempted if a['lane']==lane and a['completed'] and a['arm']=='generative'}
        for arm in labels:
            allrows = [a for a in attempted if a['lane']==lane and a['arm']==arm]
            rows = [a for a in allrows if a['fixture'] in matchedpacks and a['completed']]
            perarm[arm] = {
                'attempts':len(allrows),'completed_batches':sum(a['completed'] for a in allrows),
                'attempted_questions':sum(a['questions'] for a in allrows),
                'whole_operation_seconds_all_attempts':sum(a['whole_operation_seconds'] for a in allrows),
                'native_seconds_all_known_calls':sum(a['native_call_seconds'] or 0 for a in allrows),
                'matched_whole_operation_seconds':sum(a['whole_operation_seconds'] for a in rows),
                'matched_native_call_seconds':sum(a['native_call_seconds'] or 0 for a in rows),
                'known_input_tokens_all_attempts':sum(a['input_tokens'] for a in allrows),
                'known_output_tokens_all_attempts':sum(a['output_tokens'] for a in allrows),
                'unknown_input_requests':sum(a['unknown_input_requests'] for a in allrows),
                'unknown_output_requests':sum(a['unknown_output_requests'] for a in allrows)}
        quality = t['absolute_quality_bar_passed'] and g['complete'] and t['correct']>=g['correct']
        denominator=perarm['generative']['matched_whole_operation_seconds']
        ratio=perarm['typed']['matched_whole_operation_seconds']/denominator if denominator else None
        complete=t['complete'] and g['complete']
        lanes[lane]={'quality':{'typed':t,'generative':g},'metrics':perarm,
                     'matched_cases':len(matched),'matched_batches':sorted(matchedpacks),
                     'matched_correct':{arm:sum(labels[arm][q]==gold[q]['expected'] for q in matched) for arm in labels},
                     'unjudged_ids':{arm:sorted(set(ids)-set(labels[arm])) for arm in labels},
                     'full_panel_complete':complete,'quality_bar_passed':quality,
                     'speed_ratio_matched_whole_operations':ratio,
                     'full_panel_speed_bar_passed':complete and ratio is not None and ratio<=.75,
                     'quality_and_speed_benefit_bar_passed':quality and ratio is not None and ratio<=.75}
    traceusage = {field:{metric:sum(r['trace']['usage'][field][metric] for r in runs)
                        for metric in runs[0]['trace']['usage'][field]} for field in runs[0]['trace']['usage']}
    ledger = [{'id':qid,'lane':g['lane'],'expected':g['expected'],
               'typed':labels['typed'].get(qid),'generative':labels['generative'].get(qid),
               'noul':ps.get(qid),'automatic_approval':False} for qid,g in sorted(gold.items())]
    return {'schema_version':1,'schema':'azdaja.measurement_followthrough.replay.v1',
            'replay_consistent':True,'original_study_status':'stopped',
            'continuation_status':runs[-1]['receipt']['status'] if len(runs)>1 else 'not_run',
            'lanes':lanes,'cumulative_totals':totals,'entered_generative_turns':entered,
            'summed_campaign_elapsed_seconds':elapsed,'generative_usage':traceusage,
            'typed_documented_input_cost_estimate_usd':totals['known_typed_input_tokens']*.042/1e6,
            'typed_input_cost_estimate_complete':totals['typed_unknown_usage']==0,
            'typed_output_usage_complete':totals['typed_unknown_output_usage']==0,
            'billing_known':False,'generative_dollars_known':False,
            'verifier_sum_noul':math.fsum(ps.values()),'verifier_observed_probabilities':len(ps),
            'failures':[f for r in runs for f in r['failures']], 'ledger':ledger,
            'automatic_approval_authorized':False,'official_rah_submission':False,
            'general_advantage_established':False,
            'limits':['Original native Choice rejection permanently excludes25typed judgments; no retry or renormalization.',
                      'Short selected SQuAD2 paragraphs, not million-token retrieval or independent n=300replications.',
                      'Official annotation operational gold, possible annotation noise, article dependence and training contamination.',
                      'Failure timing counts in attempted cost/latency; matched speed uses only identical completed pack pairs.',
                      'Raw failed Choice body unavailable; rejection magnitude and cause cannot be reconstructed.',
                      'Native validation and local hashes are not provider-authenticated attestations.']}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--continuation',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); result=combined(args.continuation)
    with args.output.open('xb') as stream: stream.write(n.canonical(result)+b'\n')
    print(json.dumps({'replay_consistent':True,'original_study_status':'stopped',
                      'continuation_status':result['continuation_status'],'cumulative_totals':result['cumulative_totals'],
                      'bars':{k:{f:v[f] for f in ('full_panel_complete','quality_bar_passed','quality_and_speed_benefit_bar_passed')} for k,v in result['lanes'].items()}}))


if __name__=='__main__': main()
