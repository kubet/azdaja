"""New, bounded raw-response diagnostic. Never scores or repairs the old panel."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from decimal import Decimal
from bench.jev.angle_lab import native as n

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REQUEST = ROOT/'bench/jev/measurement_v2/results/native-20260917/flat-02-typed-request.json'


def inventory():
    build = n.strict_loads((HERE/'probe-build.json').read_bytes())
    binary = Path(build['test_binary'])
    if n.sha(binary.read_bytes()) != build['test_binary_sha256']:
        raise n.Stop('probe_binary_changed')
    files = [HERE/'PLAN.md', HERE/'diagnostic_probe.rs', HERE/'probe-build.json', Path(__file__),
             ROOT/'src/judge.rs', ROOT/'src/credentials.rs', ROOT/'Cargo.lock',
             ROOT/'bench/jev/angle_lab/native.py', ROOT/'bench/jev/span_selection/kernel.py',
             ROOT/'bench/jev/span_selection/run.py', REQUEST, binary]
    return binary, {str(p.resolve()): n.sha(p.read_bytes()) for p in files}


def numbers(path):
    body = json.loads(path.read_text(), parse_float=Decimal, parse_int=Decimal)
    rows = []
    for qid, answer in sorted(body['answers'].items()):
        ps = answer.get('probabilities', {})
        total = sum(ps.values(), Decimal(0))
        rows.append({'id':qid,'option_count':len(ps),'decimal_sum':str(total),
                     'absolute_sum_error':str(abs(total - 1)),
                     'probabilities':{k:str(v) for k,v in ps.items()}})
    return {'returned_model':body['model'], 'usage':{k:int(v) for k,v in body['usage'].items()},
            'distributions':rows, 'failed_sum_ids':[r['id'] for r in rows if Decimal(r['absolute_sum_error']) > Decimal('0.000001')]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--seal', action='store_true'); mode.add_argument('--live', action='store_true')
    ap.add_argument('--acknowledge-provider-calls', action='store_true')
    ap.add_argument('--credential-state-root', type=Path)
    ap.add_argument('--manifest', type=Path, default=HERE/'DIAGNOSTIC-FROZEN.json')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    if not (args.seal or args.live):
        print(json.dumps({'status':'offline_plan','provider_calls':0,'maximum_new_requests':3,'old_panel_repaired':False}))
        return 0
    binary, files = inventory()
    if args.seal:
        manifest = {'schema':'azdaja.second_reader.diagnostic_freeze.v1','files':files,
                    'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                    'requests_max':3,'input_tokens_max':100000,'elapsed_seconds_max':120,'old_panel_repaired':False}
        with args.manifest.open('xb') as stream: stream.write(n.canonical(manifest)+b'\n')
        print(json.dumps({'status':'sealed','provider_calls':0})); return 0
    if not args.acknowledge_provider_calls or not args.credential_state_root or not args.output:
        ap.error('live requires acknowledgement, credential root and new output')
    if os.path.lexists(args.output): ap.error('output exists')
    if not args.output.parent.is_dir(): ap.error('output parent must already exist')
    manifest = n.strict_loads(args.manifest.read_bytes())
    if manifest['files'] != files: raise n.Stop('diagnostic_manifest_changed')
    with args.manifest.with_suffix('.started').open('xb') as stream:
        stream.write(n.canonical({'manifest_sha256':n.sha(args.manifest.read_bytes()),'automatic_retry':False})+b'\n')
        stream.flush(); os.fsync(stream.fileno())
    args.output.mkdir(mode=0o700)
    env = {k:v for k,v in os.environ.items() if not n.re.search(r'(API.?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|AUTHORIZATION)', k, n.re.I)}
    env['AZDAJA_HOME'] = str(args.credential_state_root.resolve(strict=True))
    env['AZDAJA_SECOND_READER_ACK'] = 'one-fresh-diagnostic-request'
    env['AZDAJA_SECOND_READER_REQUEST'] = str(REQUEST.resolve())
    env['AZDAJA_SECOND_READER_REQUEST_SHA'] = files[str(REQUEST.resolve())]
    start = time.monotonic(); total_input = 0; rows = []
    for index in range(1, 4):
        if time.monotonic()-start >= 90 or total_input >= 70000: break
        if inventory()[1] != files: raise n.Stop('diagnostic_source_changed')
        out = args.output/f'attempt-{index:02d}'; out.mkdir(mode=0o700)
        env['AZDAJA_SECOND_READER_OUTPUT'] = str(out.resolve())
        completed = n.bounded_process([str(binary),'--exact','judge::second_reader_probe::capture_once','--ignored','--nocapture'],
                                      code='',cwd=out,env=env,timeout=30)
        if n.SECRET.search(completed.stdout+completed.stderr): raise n.Stop('credential_in_diagnostic_log')
        with (out/'test-process.json').open('xb') as stream:
            stream.write(n.canonical({'exit':completed.returncode,'stdout':completed.stdout,'stderr':completed.stderr})+b'\n')
        if completed.returncode != 0 or not (out/'receipt.json').exists():
            rows.append({'attempt':index,'status':'process_failed'}); break
        receipt = n.strict_loads((out/'receipt.json').read_bytes())
        if receipt['stats']['attempts'] != 1: raise n.Stop('diagnostic_attempt_accounting')
        total_input += receipt['stats']['known_input_tokens']
        row = {'attempt':index,'receipt_sha256':n.sha((out/'receipt.json').read_bytes()),'verdict':receipt['verdict'],'stats':receipt['stats']}
        if receipt['capture']['raw_retained']:
            if n.sha((out/'response.raw.json').read_bytes()) != receipt['capture']['raw_sha256']: raise n.Stop('raw_identity')
            row['numerical_diagnostics'] = numbers(out/'response.raw.json')
        rows.append(row)
        with (out/'analysis.json').open('xb') as stream: stream.write(n.canonical(row)+b'\n')
        if not receipt['verdict']['accepted'] or receipt['stats']['unknown_input_usage_requests'] or total_input > 100000: break
    summary = {'schema':'azdaja.second_reader.diagnostic_campaign.v1','attempts':rows,'known_input_tokens':total_input,
               'elapsed_seconds':time.monotonic()-start,'original_rejected_body_recovered':False,'old_panel_repaired':False,
               'semantic_grading_performed':False,'billing':'not_inferred'}
    with (args.output/'summary.json').open('xb') as stream: stream.write(n.canonical(summary)+b'\n')
    print(json.dumps({'attempts':len(rows),'known_input_tokens':total_input,'verdicts':[r.get('verdict') for r in rows]}))
    return 0

if __name__ == '__main__': raise SystemExit(main())
