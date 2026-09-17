"""Recompute the retained stage-0 statistics without inference or a native binary."""
import argparse
import json
import math
import os
from pathlib import Path
import time

from bench.jev.angle_lab import native as n
from bench.jev.row651_labels import audit
from . import run
from .estimator import estimate

HERE = Path(__file__).resolve().parent
FILES = ('result.json', 'replicates.json', 'sample500.json', 'predictions.json',
         'public-workflow.json', 'public-commands.json')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def equal(actual, expected, path='value'):
    """Exact structure/identity, with a narrow cross-Python floating tolerance."""
    if type(expected) is float:
        require(type(actual) in (int, float) and math.isfinite(actual)
                and math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-9), path)
    elif type(expected) is dict:
        require(type(actual) is dict and actual.keys() == expected.keys(), path)
        for key, value in expected.items():
            equal(actual[key], value, path + '.' + key)
    elif type(expected) is list:
        require(type(actual) is list and len(actual) == len(expected), path)
        for index, (a, e) in enumerate(zip(actual, expected)):
            equal(a, e, path + '.' + str(index))
    else:
        require(type(actual) is type(expected) and actual == expected, path)


def check_workflow(public, commands, predictions, labels):
    for key, expected in {'status':'passed', 'binary_sha256':run.BINARY_SHA,
        'sample_labels_loaded':500, 'unobserved_gold_loaded':0,
        'persistent_reentry_equal':True, 'changed_id_rejected':True,
        'cleanup_exit':0, 'new_provider_calls':0, 'trace_empty':True,
        'cell':run.CELL}.items():
        equal(public[key], expected, 'public.' + key)
    reference = estimate(predictions, labels)
    equal(public['reference'], reference, 'public.reference')
    ph, ah = n.sha(n.canonical(predictions)), n.sha(n.canonical(labels))
    equal(public['prediction_payload_sha256'], ph, 'prediction hash')
    equal(public['audit_payload_sha256'], ah, 'audit hash')
    evaluator = public['evaluator']
    for key in ('corrected_total', 'uniform_total', 'estimated_standard_error'):
        equal(evaluator[key], reference[key], 'evaluator.' + key)
    for key, value in {'population_size':len(predictions), 'audit_size':500,
                       'prediction_hash':ph, 'audit_hash':ah,
                       'approximate_not_exact':True}.items():
        equal(evaluator[key], value, 'evaluator.' + key)
    equal(evaluator['stats']['attempts'], 0, 'typed attempts')
    equal(commands, {'binary_sha256':run.BINARY_SHA, 'events':public['events'],
                     'trace_bytes':0}, 'command retention')
    events = public['events']
    equal([e['command'] for e in events],
          ['start','load','load','exec','final','exec','final','load','exec','kill'],
          'public lifecycle')
    for i, event in enumerate(events):
        require(type(event['exit']) is int, 'command exit type')
        require(event['exit'] != 0 if i == 8 else event['exit'] == 0, 'command exit')
        require(type(event['seconds']) in (int,float) and math.isfinite(event['seconds'])
                and event['seconds'] >= 0, 'command duration')
    require('unknown audit ID' in events[8]['stdout'] + events[8]['stderr'], 'invalid reentry')
    equal(n.strict_loads(events[4]['stdout']), evaluator, 'first final')
    equal(n.strict_loads(events[6]['stdout']), evaluator, 'persistent final')


def verify(folder):
    folder = Path(folder)
    manifest = n.strict_loads((HERE/'RETENTION.json').read_bytes())
    require(set(manifest['files']) == set(FILES), 'retention inventory')
    artifacts = {}
    for name in FILES:
        path = folder/name
        require(path.is_file() and not path.is_symlink(), 'artifact file')
        raw = path.read_bytes()
        equal(n.sha(raw), manifest['files'][name], 'retention.' + name)
        artifacts[name] = n.strict_loads(raw)
    result = artifacts['result.json']
    require(set(result['implementation_sha256']) ==
            {'PLAN.md','estimator.py','run.py','test_estimator.py','test_run.py'}, 'implementation inventory')
    for name, digest in result['implementation_sha256'].items():
        equal(n.sha((HERE/name).read_bytes()), digest, 'implementation.' + name)
    inputs = audit.audit(portable=True)
    scope = inputs.pop('validation_scope')
    equal(scope['runtime_binary_bytes_verified'], False, 'portable runtime scope')
    equal(scope['recorded_absolute_paths_used_for_lookup'], False, 'portable source lookup')
    equal(scope['source_files_verified'], 124, 'portable source coverage')
    equal(result['input_audit_sha256'], n.sha(n.canonical(inputs)), 'source replay')
    equal(result['source_hashes'], {k:inputs[k] for k in
        ('official_snapshot_sha256','unlabeled_context_sha256','receipt_sha256',
         'checked_native_replay_sha256')}, 'source identities')
    equal(result['prior_typed_cost'], inputs['native_workflow'], 'historical cost')
    rows = inputs['occurrence_ledger']
    population, summaries, replicates = run.simulate(rows, time.monotonic()+600)
    equal(result['population'], population, 'population')
    equal(result['samples'], summaries, 'summaries')
    equal(artifacts['replicates.json'], replicates, 'all fixed replicates')
    predictions = [{'id':r['id'], 'p':r['p_ham']} for r in rows]
    labels = [{'id':rows[i]['id'],'label':rows[i]['gold_ham']}
              for i in run.selected_indices(500,0,len(rows))]
    equal(artifacts['predictions.json'], predictions, 'all predictions')
    equal(artifacts['sample500.json'], labels, 'fixed audit sample')
    check_workflow(artifacts['public-workflow.json'], artifacts['public-commands.json'], predictions, labels)
    passed = (population['raw_p_variance_ratio'] <= .5 and
              all(s['raw_p']['empirical_mse_ratio_to_uniform'] <= .60 for s in summaries.values()))
    for key, value in {'status':'completed','post_hoc':True,'new_inference_requests':0,
        'feasibility_bar_passed':passed,'exact_count_claim':False,
        'generalization_established':False,'public_workflow_status':'passed',
        'oracle_cost_is_not_real_labeling_cost':True}.items():
        equal(result[key], value, 'claim.' + key)
    return {'schema':'azdaja.audit_sampling.replay.v1', 'replay_consistent':True,
            'all_replicates_checked':len(replicates), 'new_inference_requests':0,
            'feasibility_bar_passed':passed, 'generalization_established':False,
            'retained_native_commands_checked':10, 'new_native_commands':0,
            'raw_p_variance_ratio':population['raw_p_variance_ratio'],
            'validation_scope':scope,
            'legacy_numerical_summary_matches':True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=HERE/'results-20260917')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if os.path.lexists(args.output) or not args.output.parent.is_dir():
        parser.error('new output file required')
    result = verify(args.results)
    with args.output.open('xb') as stream:
        stream.write(n.canonical(result)+b'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
