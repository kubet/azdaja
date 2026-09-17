"""Bounded separate-request criteria experiment through Azdaja's public lifecycle."""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import time
from bench.jev.angle_lab import native as n
from bench.jev.asymmetry.criteria import prepare as p

HERE = Path(__file__).resolve().parent
BINARY_SHA = '13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32'
MAX_INPUT, MAX_OUTPUT, MAX_SECONDS = 250000, 100000, 180
REQUESTS, QUESTIONS = 12, 681
CAPS = dict(typed_requests=REQUESTS, questions=QUESTIONS, input_tokens=MAX_INPUT,
            output_tokens=MAX_OUTPUT, elapsed_seconds=MAX_SECONDS, generative_calls=0)
SCHEMA = 'azdaja.asymmetry.criteria.v2'


def require(condition, reason):
    if not condition:
        raise n.Stop(reason)


def rows():
    result = p.campaign_requests()
    require(len(result) == REQUESTS and sum(len(x['questions']) for _, x in result) == QUESTIONS, 'campaign_shape')
    return result


def inventory(binary):
    binary = Path(binary).resolve(strict=True)
    require(n.sha(binary.read_bytes()) == BINARY_SHA, 'binary_identity')
    files = [HERE/x for x in ('run.py','test_run.py','prepare.py','test_prepare.py','grade.py','test_grade.py','PLAN.md')]
    files += [Path(n.__file__), p.SOURCE, binary]
    files += [p.ROOT/x for x in ('bench/jev/span_selection/kernel.py','bench/jev/span_selection/run.py')]
    return {str(x.resolve(strict=True)):n.sha(x.read_bytes()) for x in files}


def identities(prepared):
    return [dict(name=name, request_sha256=n.sha(n.canonical(n.inspect_pack(pack))),
                 question_count=len(pack['questions']), ids=sorted(pack['questions'])) for name,pack in prepared]


def validate_body(body, pack):
    require(isinstance(body, dict) and body.get('model') == n.MODEL and
            isinstance(body.get('answers'), dict) and set(body['answers']) == set(pack['questions']), 'response_identity')
    for answer in body['answers'].values():
        value = answer.get('noul') if type(answer) is dict else None
        require(type(answer) is dict and answer.get('type') == 'noul' and type(value) in (int,float)
                and math.isfinite(value) and 0 <= value <= 1, 'noul_domain')


def validate_success_stats(stats, body, pack):
    require(type(stats) is dict, 'stats_shape')
    fixed = {'attempts':1,'provider_requests':1,'questions':len(pack['questions']),
             'cache_hits':0,'unknown_input_usage_requests':0}
    require(all(type(stats.get(k)) is int and stats[k] == v for k,v in fixed.items()), 'stats_accounting')
    require(stats.get('poisoned') is False and stats.get('enabled') is True and
            stats.get('transport_available') is True and stats.get('input_usage_complete') is True, 'stats_state')
    usage = body.get('usage', {})
    require(all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('input_tokens','output_tokens')), 'usage_domain')
    require(type(stats.get('known_input_tokens')) is int and stats['known_input_tokens'] == usage['input_tokens'], 'stats_usage')
    meta = body.get('_azdaja', {})
    require(meta.get('request_sha256') == n.sha(n.canonical(n.inspect_pack(pack))) and
            meta.get('cache_hit') is False and type(meta.get('provider_requests_this_call')) is int and
            meta['provider_requests_this_call'] == 1 and meta.get('new_request_usage') == usage and
            meta.get('original_usage') == usage, 'native_binding')
    require(type(meta.get('elapsed_ms')) is int and meta['elapsed_ms'] >= 0, 'native_latency')


class Campaign(n.Campaign):
    def left(self):
        remaining = MAX_SECONDS - (time.monotonic() - self.started)
        require(remaining > 0, 'campaign_deadline')
        return remaining

    def configure(self, enabled):
        remaining = MAX_INPUT - self.receipt['known_typed_input_tokens']
        require(not enabled or (remaining > 0 and not self.receipt['typed_unknown_usage'] and
                                not self.receipt['typed_unknown_output_usage']), 'input_or_unknown_budget')
        timeout = max(1, min(20, math.floor(self.left())))
        text = f'''sub_llm_cmd="/usr/bin/false"
sub_timeout={timeout}
cell_timeout={timeout+5}
output_cap=262144
max_calls_per_cell=1
[judge]
enabled={str(enabled).lower()}
model="{n.MODEL}"
expected_model="{n.MODEL}"
key_env="TYPESAFE_API_KEY"
timeout_secs={timeout}
max_requests_per_cell=1
max_questions_per_cell=64
max_input_tokens_per_cell={max(1,remaining)}
max_request_bytes=131072
max_response_bytes=262144
'''
        path = self.work/'config.toml'
        with path.open('w') as stream:
            os.chmod(path,0o600)
            stream.write(text)

    def generate(self, *args, **kwargs):
        raise n.Stop('generation_disabled_for_criteria')

    def cell(self, name, code):
        value = super().cell(name,code)
        self.save(name+'-result.json',n.strict_loads(value))
        return value

    @n.terminal
    def typed(self, name, pack):
        require(self.receipt['typed_calls_started'] < REQUESTS, 'request_cap')
        require(self.receipt['known_typed_output_tokens'] < MAX_OUTPUT, 'output_budget')
        admitted = time.monotonic()-self.started
        status = 'failed'
        response = None
        try:
            response = super().typed(name,pack)
            require(self.receipt['known_typed_input_tokens'] <= MAX_INPUT and
                    self.receipt['known_typed_output_tokens'] <= MAX_OUTPUT, 'token_cap')
            self.left()
            validate_body(response,pack)
            raw = n.strict_loads((self.output/(name+'-observation.json')).read_bytes())
            validate_success_stats(raw['stats'],response,pack)
            status = 'completed'
            return response
        finally:
            for call in self.receipt.get('calls',[]):
                if call['name'] == name:
                    call.update(status=status, request_sha256=n.sha(n.canonical(n.inspect_pack(pack))),
                                admitted_elapsed_seconds=admitted, completed_elapsed_seconds=time.monotonic()-self.started)
                    if response is not None:
                        call['response_sha256'] = n.sha(n.canonical(response))
                    break
            self.checkpoint()

    def checkpoint(self):
        self.receipt.update(experiment_schema=SCHEMA, caps=CAPS, automatic_approval=False,
                            headline_fixture_intervention=False)
        super().checkpoint()

    def finish(self, status, reason=None):
        if status == 'completed':
            require(len(self.receipt.get('panel_rows',[])) == REQUESTS and
                    all(x.get('status') == 'completed' for x in self.receipt['panel_rows']) and
                    self.receipt['typed_calls_started'] == self.receipt.get('confirmed_typed_requests') == REQUESTS and
                    self.receipt.get('typed_questions') == QUESTIONS and
                    self.receipt.get('reduction') == {'observed':QUESTIONS,'expected':QUESTIONS,'complete':True,'attempts':0},
                    'incomplete_panel')
            require(self.receipt['logical_llm_calls'] == 0 and
                    not (self.output/'model-trace.jsonl').exists(), 'unexpected_generation')
        super().finish(status,reason)
        if status == 'completed' and time.monotonic()-self.started > MAX_SECONDS:
            self.receipt['status'] = 'stopped'
            self.receipt['stop_reason'] = 'campaign_deadline_during_cleanup'
            self.checkpoint()
        if self.receipt.get('cleanup_exit') != 0:
            self.receipt['status'] = 'stopped'
            self.receipt['stop_reason'] = 'cleanup_failed'
            self.checkpoint()


def exercise(c, prepared, live=False):
    c.start()
    c.receipt['panel_rows'] = []
    c.receipt['synthetic_observations'] = not live
    for name, pack in prepared:
        c.configure(False)
        c.load('custody_payload',n.inspect_pack(pack))
        custody = n.strict_loads(c.cell(name+'-custody',
            'p = json.loads(custody_payload)\nFINAL({"request_sha256":sha256(json.dumps(p, sort_keys=True, separators=(",",":"), ensure_ascii=False)),"ids":sorted(p["questions"]),"attempts":judge_stats()["attempts"]})\n'))
        expected = dict(request_sha256=n.sha(n.canonical(n.inspect_pack(pack))), ids=sorted(pack['questions']), attempts=0)
        require(custody == expected, 'custody_mismatch')
        row = dict(name=name,status='attempted',request_sha256=expected['request_sha256'],question_count=len(pack['questions']))
        c.receipt['panel_rows'].append(row)
        c.checkpoint()
        if live:
            body = c.typed(name,pack)
            row.update(status='completed',response_sha256=n.sha(n.canonical(body)))
        else:
            c.load('offline_payload',dict(name=name,ids=sorted(pack['questions'])))
            c.cell(name+'-offline','p = json.loads(offline_payload)\nobservations[p["name"]] = {"answers":{qid:{"type":"noul","noul":0.5} for qid in p["ids"]}}\nFINAL({"synthetic":True,"attempts":judge_stats()["attempts"]})\n')
            row['status'] = 'synthetic'
        c.checkpoint()
    c.configure(False)
    expected_ids = [qid for _,pack in prepared for qid in pack['questions']]
    c.load('expected_payload',expected_ids)
    code = '''expected = json.loads(expected_payload)
seen = []
for body in observations.values():
    for qid in body["answers"]:
        seen.append(qid)
FINAL({"observed":len(seen),"expected":len(expected),"complete":sorted(seen)==sorted(expected),"attempts":judge_stats()["attempts"]})
'''
    c.receipt['reduction'] = n.strict_loads(c.cell('reduce',code))
    require(c.receipt['reduction'] == dict(observed=QUESTIONS,expected=QUESTIONS,complete=True,attempts=0), 'reduction_incomplete')
    c.checkpoint()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    modes = ap.add_mutually_exclusive_group()
    for mode in ('seal','offline','live'):
        modes.add_argument('--'+mode,action='store_true')
    ap.add_argument('--acknowledge-provider-calls',action='store_true')
    ap.add_argument('--azdaja',type=Path)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--credential-state-root',type=Path)
    ap.add_argument('--manifest',type=Path,default=HERE/'FROZEN.json')
    args = ap.parse_args(argv)
    if not any((args.seal,args.offline,args.live)):
        print(json.dumps(dict(status='offline_plan',provider_calls=0,caps=CAPS)))
        return 0
    if args.live and not args.acknowledge_provider_calls:
        ap.error('live requires acknowledgement')
    if not args.azdaja:
        ap.error('--azdaja required')
    if args.live and not args.credential_state_root:
        ap.error('live requires private --credential-state-root')
    prepared = rows()
    files = inventory(args.azdaja)
    if args.seal:
        seal = dict(schema='azdaja.asymmetry.criteria_seal.v2',files=files,panel=identities(prepared),caps=CAPS,
                    source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=p.ROOT,text=True).strip())
        with args.manifest.open('xb') as f:
            f.write(n.canonical(seal)+b'\n')
        print(json.dumps(dict(status='sealed',provider_calls=0)))
        return 0
    if not args.output or os.path.lexists(args.output) or not args.output.parent.is_dir():
        ap.error('new --output with existing parent required')
    if args.live:
        seal = n.strict_loads(args.manifest.read_bytes())
        require(seal.get('files') == files and seal.get('panel') == identities(prepared) and seal.get('caps') == CAPS, 'seal_changed')
        marker = dict(seal_sha256=n.sha(args.manifest.read_bytes()),automatic_retry=False)
        with args.manifest.with_suffix('.started').open('xb') as f:
            f.write(n.canonical(marker)+b'\n')
        files[str(args.manifest.resolve())] = marker['seal_sha256']
    c = Campaign(args.azdaja,args.output,files,authorized=True,attached_root=args.credential_state_root if args.live else None)
    for key in list(c.env):
        if 'SOCKET' in key.upper() or key.upper().endswith('_SOCK') or key in ('JCODE_RUNTIME_DIR','JCODE_HOME'):
            c.env.pop(key)
    c.env['JCODE_HOME'] = str(c.work/'absent-subscription')
    try:
        exercise(c,prepared,args.live)
        c.finish('completed' if args.live else 'offline_public_workflow_passed')
    except BaseException as exc:
        c.finish('stopped',str(exc) if isinstance(exc,n.Stop) else type(exc).__name__)
    print(json.dumps({k:c.receipt.get(k) for k in ('status','typed_calls_started','known_typed_input_tokens','stop_reason')}))
    return 0 if c.receipt['status'] in ('completed','offline_public_workflow_passed') else 2


if __name__ == '__main__':
    raise SystemExit(main())
