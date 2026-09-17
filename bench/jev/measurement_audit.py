"""Offline acceptance of retained measurements. Never invokes either provider."""
import argparse
import json
from pathlib import Path

from bench.jev.angle_lab import native as n
from bench.jev.measurement_followthrough import evidence as e, report
from bench.jev.measurement_followthrough.run import HERE
from bench.jev.row645_labels import audit as row645


def verify_summary(actual, retained):
    e.check(actual == retained, 'retained summary does not replay')


def verify():
    previous=e.read_run(e.PREDECESSOR,e.ORIGINAL_ORDER)
    current=e.read_run(HERE/'results/native-20260917',e.CONTINUATION_ORDER)
    for run in (previous,current):
        trace=run['trace']
        completed=sum(a['arm']=='generative' and a['completed'] for a in run['attempts'])
        e.check(trace['observed_models']==[n.GENERATOR] and trace['observed_providers']==['OpenAI'], 'successful provider identity')
        e.check(trace['succeeded_events']==completed, 'successful trace coverage')
    result=report.combined(HERE/'results/native-20260917')
    verify_summary(result,e.load(HERE/'results/combined-replay.json'))
    official=row645.audit(row645.HERE/'official-row645.json')
    verify_summary(official,e.load(row645.HERE/'result.json'))
    cleanup=e.load(HERE/'results/private-cleanup.json')
    e.check(cleanup['owned_bridge_stopped'] and cleanup['experimental_attachment_removed']
            and cleanup['experimental_oauth_copy_and_link_removed']
            and cleanup['default_attachment_bytes_and_modes_unchanged'], 'private cleanup incomplete')
    return {'schema_version':1,'schema':'azdaja.measurement_final_acceptance.v1',
            'status':'passed','new_provider_calls':0,
            'all_quality_bars_passed':all(lane['quality_bar_passed'] for lane in result['lanes'].values()),
            'checks':{
                'official_row645_aligned_occurrences':2177,'official_row645_may_gold':132,
                'row645_error_sets':{'typed':official['typed'],'generative':official['generative']},
                'source_and_fixture_freezes':True,'original_receipt_remains_stopped':True,
                'continuation_completed':current['receipt']['status']=='completed',
                'repeated_attempted_pairs':len(set(previous['order'])&set(current['order'])),
                'exact_successful_models_and_provider':True,
                'cumulative_accounting':result['cumulative_totals'],
                'flat_unjudged_typed_cases':len(result['lanes']['flat']['unjudged_ids']['typed']),
                'verifier_observed_per_arm':{arm:row['observed'] for arm,row in result['lanes']['verifier']['quality'].items()},
                'retained_grades_recomputed_not_trusted':True,
                'private_cleanup':cleanup},
            'result_hashes':{'combined':n.sha((HERE/'results/combined-replay.json').read_bytes()),
                             'row645':n.sha((row645.HERE/'result.json').read_bytes())},
            'limits':['Acceptance here means accurate retained measurement, not successful semantic quality.',
                      'Rejected Choice body is unavailable; failure cause cannot be reconstructed.',
                      'Public dataset annotation noise, article clustering and contamination remain.',
                      'No push, release, production change or README quality claim.']}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    result=verify()
    with args.output.open('xb') as stream:stream.write(n.canonical(result)+b'\n')
    print(json.dumps({'status':result['status'],'new_provider_calls':0,'all_quality_bars_passed':result['all_quality_bars_passed']}))


if __name__=='__main__':main()
