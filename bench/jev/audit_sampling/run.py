"""Post-hoc finite-population feasibility, with no inference and an actual CLI check."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import statistics
import sys
import tempfile
import time

from bench.jev.angle_lab import native as n
from bench.jev.row651_labels import audit
from .estimator import estimate

HERE = Path(__file__).resolve().parent
SIZES = (100, 500, 2000)
REPLICATES = 2000
Z = 1.959963984540054
BINARY_SHA = '13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32'
CELL = '''sample_result = None
assert sha256(prediction_payload) == expected_prediction_hash, "prediction binding"
assert sha256(audit_payload) == expected_audit_hash, "audit binding"
ps = json.loads(prediction_payload)
ys = json.loads(audit_payload)
by_id = {}
psum = 0.0
for row in ps:
    assert row["id"] not in by_id, "duplicate prediction ID"
    assert row["p"] >= 0 and row["p"] <= 1, "probability"
    by_id[row["id"]] = row["p"]
    psum += row["p"]
seen = {}
residuals = []
ysum = 0
for row in ys:
    assert row["id"] in by_id, "unknown audit ID"
    assert row["id"] not in seen, "duplicate audit ID"
    assert isinstance(row["label"], bool), "label"
    seen[row["id"]] = True
    y = 1 if row["label"] else 0
    ysum += y
    residuals.append(y - by_id[row["id"]])
N = len(ps)
a = len(ys)
assert a > 1 and a <= N, "audit size"
rmean = sum(residuals) / a
rvar = sum([(r - rmean) ** 2 for r in residuals]) / (a - 1)
corrected = psum + N * rmean
if a == N:
    corrected = ysum
se = N * ((1 - a / N) * rvar / a) ** 0.5
sample_result = {"population_size":N,"audit_size":a,"corrected_total":corrected,
    "uniform_total":N * ysum / a,"estimated_standard_error":se,
    "prediction_hash":sha256(prediction_payload),"audit_hash":sha256(audit_payload),
    "stats":judge_stats(),"approximate_not_exact":True}
FINAL(sample_result)
'''


def selected_indices(size, replicate, population):
    seed = int.from_bytes(hashlib.sha256(f'audit-sampling-v1|{size}|{replicate}'.encode()).digest(), 'big')
    return random.Random(seed).sample(range(population), size)


def variance(values):
    return statistics.variance(values)


def required_labels(population, residual_variance, rmse):
    # Solve N² S² (1/n - 1/N) <= rmse², not a deployable confidence bound.
    if residual_variance == 0:
        return 1
    return min(population, max(1, math.ceil(1 / (1 / population + rmse ** 2 / (population ** 2 * residual_variance)))))


def simulate(rows, deadline):
    ids = [r['id'] for r in rows]
    y = [int(r['gold_ham']) for r in rows]
    p = [r['p_ham'] for r in rows]
    N, total = len(rows), sum(y)
    # Strict input validation is independent from the fast simulation below.
    estimate([{'id':r['id'], 'p':r['p_ham']} for r in rows],
             [{'id':r['id'], 'label':r['gold_ham']} for r in rows])
    auxiliaries = {'raw_p': p, 'hard_0_5': [int(v >= .5) for v in p],
                   'constant_0_5': [.5] * N, 'inverse_p': [1-v for v in p],
                   'uniform_only': [0] * N}
    residuals = {k:[label - pred for label,pred in zip(y,values)] for k,values in auxiliaries.items()}
    totals = {k:math.fsum(v) for k,v in auxiliaries.items()}
    var = {k:variance(v) for k,v in residuals.items()}
    population = {'n':N, 'gold_total':total, 'prediction_total':totals['raw_p'],
                  'residual_variances':var, 'raw_p_variance_ratio':var['raw_p']/var['uniform_only'],
                  'oracle_required_labels':{str(target):{k:required_labels(N,v,target) for k,v in var.items()}
                                           for target in (100,50)}}
    summaries, replicates = {}, []
    for size in SIZES:
        observed = {k:[] for k in auxiliaries}
        coverage = {k:0 for k in auxiliaries}
        for rep in range(REPLICATES):
            if time.monotonic() > deadline:
                raise ValueError('diagnostic deadline')
            indices = selected_indices(size,rep,N)
            row = {'size':size, 'replicate':rep,
                   'sample_ids_sha256':n.sha(n.canonical([ids[i] for i in indices])), 'arms':{}}
            for arm in auxiliaries:
                values = [residuals[arm][i] for i in indices]
                mean = math.fsum(values) / size
                value = totals[arm] + N * mean
                sv = math.fsum((v-mean)**2 for v in values) / (size-1)
                se = N * math.sqrt((1-size/N)*sv/size)
                error = value-total
                covered = abs(error) <= Z*se
                observed[arm].append(error)
                coverage[arm] += covered
                row['arms'][arm] = {'estimate':value, 'standard_error':se, 'signed_error':error,
                                    'normal_reference_covers':covered}
            if not math.isclose(row['arms']['constant_0_5']['estimate'],row['arms']['uniform_only']['estimate'],abs_tol=1e-8):
                raise ValueError('constant predictor must equal plain auditing')
            replicates.append(row)
        summaries[str(size)] = {arm:{'empirical_bias':math.fsum(errors)/REPLICATES,
            'empirical_rmse':math.sqrt(math.fsum(e*e for e in errors)/REPLICATES),
            'normal_reference_95_coverage':coverage[arm]/REPLICATES,
            'exact_design_rmse':N*math.sqrt((1-size/N)*var[arm]/size),
            'interval_is_finite_sample_guarantee':False} for arm,errors in observed.items()}
        baseline = summaries[str(size)]['uniform_only']['empirical_rmse']
        for value in summaries[str(size)].values():
            value['empirical_mse_ratio_to_uniform'] = (value['empirical_rmse']/baseline)**2
    return population, summaries, replicates


def public_workflow(binary, predictions, labels, scratch, evidence_path=None):
    binary = binary.resolve(strict=True)
    if n.sha(binary.read_bytes()) != BINARY_SHA:
        raise ValueError('retained binary identity')
    reference = estimate(predictions,labels)
    events = []
    with tempfile.TemporaryDirectory(prefix='audit-sampling-',dir=scratch) as folder:
        work = Path(folder)
        config = work/'config.toml'
        config.write_text('sub_llm_cmd="/usr/bin/false"\ndefault_model="offline"\ncell_timeout=30\noutput_cap=262144\nmax_calls_per_cell=1\n[judge]\nenabled=false\n')
        trace = work/'trace.jsonl'
        env = {'PATH':'/usr/bin:/bin','HOME':str(work),'TMPDIR':str(work),
               'AZDAJA_HOME':str(work/'state'),'AZDAJA_CONFIG':str(config),
               'AZDAJA_MODEL_TRACE':str(trace),'RLM_DEPTH':'0'}
        sid = None
        def command(args,code='',expect_success=True):
            start = time.monotonic()
            result = n.bounded_process([str(binary),*args],code=code,cwd=work,env=env,timeout=40)
            events.append({'command':args[0],'exit':result.returncode,'stdout':result.stdout,
                           'stderr':result.stderr,'seconds':time.monotonic()-start})
            if expect_success and result.returncode:
                raise ValueError('offline public '+args[0])
            return result
        def load(name,data):
            path = work/(name+'.json');path.write_bytes(n.canonical(data))
            command(['load',sid,str(path),name])
            return n.sha(path.read_bytes())
        try:
            sid = command(['start']).stdout.strip()
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',sid):raise ValueError('session ID')
            ph = load('prediction_payload',predictions)
            ah = load('audit_payload',labels)
            manifest_code = f'expected_prediction_hash = "{ph}"\nexpected_audit_hash = "{ah}"\n'
            command(['exec',sid],manifest_code+CELL)
            first = n.strict_loads(command(['final',sid]).stdout)
            for key in ('corrected_total','uniform_total','estimated_standard_error'):
                if not math.isclose(first[key],reference[key],rel_tol=1e-11,abs_tol=1e-7):
                    raise ValueError('Python/evaluator disagreement')
            if first['prediction_hash']!=ph or first['audit_hash']!=ah or first['stats']['attempts']!=0:
                raise ValueError('custody or inference attempt')
            command(['exec',sid],'FINAL(sample_result)\n')
            second = n.strict_loads(command(['final',sid]).stdout)
            if first != second:raise ValueError('persistent reentry')
            bad = [dict(r) for r in labels];bad[0]['id']='unknown-audit-id'
            bad_hash=load('audit_payload',bad)
            rejected=command(['exec',sid],f'expected_audit_hash = "{bad_hash}"\n'+CELL,False)
            if rejected.returncode==0 or 'unknown audit ID' not in (rejected.stdout+rejected.stderr):
                raise ValueError('unknown audit ID was not rejected')
            # Never consume a previous final after invalid reentry. This private session is killed.
        finally:
            try:
                if sid:command(['kill',sid])
            finally:
                if evidence_path is not None:
                    with evidence_path.open('xb') as stream:
                        stream.write(n.canonical({'binary_sha256':BINARY_SHA,'events':events,
                            'trace_bytes':trace.stat().st_size if trace.exists() else 0})+b'\n')
        if trace.exists() and trace.read_bytes().strip():raise ValueError('unexpected model trace')
        return {'status':'passed','binary_sha256':BINARY_SHA,'sample_labels_loaded':len(labels),
                'unobserved_gold_loaded':0,'reference':reference,'evaluator':first,
                'persistent_reentry_equal':True,'changed_id_rejected':True,'cleanup_exit':events[-1]['exit'],
                'new_provider_calls':0,'trace_empty':True,'events':events,'cell':CELL,
                'prediction_payload_sha256':ph,'audit_payload_sha256':ah}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--azdaja',type=Path,required=True)
    args=parser.parse_args()
    if os.path.lexists(args.output) or not args.output.parent.is_dir():parser.error('new output directory required')
    if n.sha(args.azdaja.resolve(strict=True).read_bytes()) != BINARY_SHA:parser.error('retained binary identity')
    args.output.mkdir(mode=0o700)
    start=time.monotonic()
    files=('PLAN.md','estimator.py','run.py','test_estimator.py','test_run.py')
    hashes={f:n.sha((HERE/f).read_bytes()) for f in files}
    inputs=audit.audit()
    rows=inputs['occurrence_ledger']
    population,summaries,replicates=simulate(rows,start+600)
    indices=selected_indices(500,0,len(rows))
    predictions=[{'id':r['id'],'p':r['p_ham']} for r in rows]
    labels=[{'id':rows[i]['id'],'label':rows[i]['gold_ham']} for i in indices]
    # Source-only inputs and all simulated outcomes survive a public-interface failure.
    for name,value in (('replicates.json',replicates),('sample500.json',labels),('predictions.json',predictions)):
        with (args.output/name).open('xb') as f:f.write(n.canonical(value)+b'\n')
    try:
        public=public_workflow(args.azdaja,predictions,labels,Path(os.environ['JCODE_SCRATCH_DIR']),
                               args.output/'public-commands.json')
    except BaseException as error:
        with (args.output/'failure.json').open('xb') as stream:
            stream.write(n.canonical({'status':'stopped','exception_type':type(error).__name__,
                'implementation_sha256':hashes,'new_inference_requests':0})+b'\n')
        raise
    passed=(population['raw_p_variance_ratio']<=.5 and
            all(s['raw_p']['empirical_mse_ratio_to_uniform']<=.60 for s in summaries.values()))
    result={'schema':'azdaja.audit_sampling.stage0.v1','status':'completed','post_hoc':True,
            'new_inference_requests':0,'population':population,'samples':summaries,
            'feasibility_bar_passed':passed,'exact_count_claim':False,'generalization_established':False,
            'runtime_seconds':time.monotonic()-start,'python_version':sys.version,
            'prng':'stdlib random.Random SHA256 seed, sample without replacement, fixed all repetitions',
            'source_hashes':{k:inputs[k] for k in ('official_snapshot_sha256','unlabeled_context_sha256','receipt_sha256','checked_native_replay_sha256')},
            'input_audit_sha256':n.sha(n.canonical(inputs)), 'implementation_sha256':hashes,
            'public_workflow_status':public['status'], 'oracle_cost_is_not_real_labeling_cost':True,
            'prior_typed_cost':inputs['native_workflow'],
            'limits':['Known public panel, not fresh independent efficacy.','Official labels simulate a trusted audit; no new human audit performed.',
                      'Intervals are normal references, not finite-sample guarantees.','Prediction and sampling errors can both be large.',
                      'No exact answer, adaptive stopping, automatic approval, new RLM primitive or exclusive RLM advantage.']}
    for name,digest in hashes.items():
        if n.sha((HERE/name).read_bytes())!=digest:raise ValueError('implementation changed during measurement')
    if time.monotonic()-start>600:raise ValueError('diagnostic total deadline')
    for name,value in (('result.json',result),('public-workflow.json',public)):
        with (args.output/name).open('xb') as f:f.write(n.canonical(value)+b'\n')
    print(json.dumps({'status':result['status'],'feasibility_bar_passed':passed,
                      'variance_ratio':population['raw_p_variance_ratio'],'new_inference_requests':0,
                      'public_workflow':public['status']}))


if __name__=='__main__':main()
