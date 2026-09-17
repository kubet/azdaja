"""Explicit source-identical suffix recovery. No model call may repeat a prefix pack."""
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import time
from bench.jev.asymmetry.baseline import run as b
from bench.jev.angle_lab import native as n

HERE=b.HERE
PREVIOUS=HERE/'results/native-20260917'
SEAL=HERE/'CONTINUATION-FROZEN.json'
STARTED=1789666845.946793
DEADLINE=STARTED+b.MAX_SECONDS


def load(p): return n.strict_loads(Path(p).read_bytes())

def check_prefix(folder=PREVIOUS):
    receipt=load(folder/'receipt.json'); side=load(folder/'external-interruption.json')
    b.check(receipt['status']=='running' and receipt['logical_llm_calls']==25,'prefix_shape')
    for field,name in [('original_receipt_sha256','receipt.json'),('model_trace_sha256','model-trace.jsonl'),('external_final_read_sha256','external-final-read.json')]:
        b.check(side[field]==n.sha((folder/name).read_bytes()),'interruption_binding')
    b.check(side['status']=='externally_stopped' and side['cleanup_exit']==0 and side['new_provider_calls']==0
            and side['recovered_pack']=='pack-025' and side['original_started_unix']==STARTED
            and side['recovered_final_validated'] is True and side['original_receipt_unchanged'] is True,'interruption_contract')
    final=load(folder/'external-final-read.json')
    b.check(final.get('command')=='final' and type(final.get('exit')) is int and final['exit']==0
            and type(final.get('new_model_requests')) is int and final['new_model_requests']==0
            and final.get('stderr')=='','recovered_final_envelope')
    for path,digest in receipt['frozen_files'].items():
        b.check(n.sha(Path(path).read_bytes())==digest,'prefix_source_changed')
    prepared=b.rows(); answers=[]
    b.check([c['name'] for c in receipt['calls']]==[p[0] for p in prepared[:25]],'prefix_call_order')
    b.check([r['name'] for r in receipt['panel_rows']]==[p[0] for p in prepared[:25]],'prefix_panel_order')
    for i,(name,pack) in enumerate(prepared[:25]):
        prompt=load(folder/(name+'-prompt.json'))
        b.check(prompt=={'instruction':b.INSTRUCTION,'payload':{'state':pack['state'],'questions':pack['questions']}},'prefix_prompt')
        text=load(folder/(name+'-raw.json'))['text'] if i<24 else load(folder/'external-final-read.json')['stdout']
        answer=b.validate_answer(text,pack['questions'])
        if i<24:
            binding={'name':name,'answer':answer,'ids':sorted(pack['questions'])}
            b.check(load(folder/(name+'-answer.json'))==answer and load(folder/(name+'-reentry.json'))==
                    {'answer':answer,'attempts':0,'binding_sha256':n.sha(n.canonical(binding))},'prefix_reentry')
            b.check(receipt['calls'][i]['status']=='completed','prefix_call_incomplete')
        else: b.check(side['recovered_answer_sha256']==n.sha(n.canonical(answer)),'recovered_answer')
        answers.append(answer)
    trace=n.usage_summary(folder/'model-trace.jsonl')
    b.check(trace==side['accounted_trace'] and trace['entered_turns']==trace['succeeded_events']==trace['logical_request_ids']==25
            and trace['observed_models']==[b.GENERATOR] and trace['observed_providers']==['OpenAI'],'prefix_trace')
    b.check_usage(trace)
    return receipt,answers,trace


def inventory(binary):
    check_prefix()
    files=b.inventory(binary)
    paths=[Path(__file__),HERE/'test_continue.py',HERE/'continuation_supervisor.py',HERE/'CONTINUATION.md',HERE/'FROZEN.json',HERE/'FROZEN.started']
    paths += [p for p in PREVIOUS.iterdir() if p.is_file()]
    files.update({str(p.resolve()):n.sha(p.read_bytes()) for p in paths})
    return files


class Campaign(b.Campaign):
    def generate(self,name,pack):
        b.check(name in {'pack-%03d'%i for i in range(26,113)},'prefix_may_not_be_regenerated')
        return super().generate(name,pack)


def seed(c,prepared):
    prior,answers,trace=check_prefix()
    c.started=time.monotonic()-(time.time()-STARTED)
    c.left()
    c.receipt['logical_llm_calls']=25
    c.receipt['calls']=copy.deepcopy(prior['calls'])
    c.receipt['panel_rows']=copy.deepcopy(prior['panel_rows'])
    c.receipt['continuation']={'schema':'azdaja.asymmetry.suffix_recovery.v1',
        'predecessor':str(PREVIOUS.relative_to(b.ROOT)),'predecessor_logical_calls':25,
        'interruption_sha256':n.sha((PREVIOUS/'external-interruption.json').read_bytes()),
        'absolute_deadline_unix':DEADLINE,'budgets_reset':False,'original_uninterrupted_run':False}
    shutil.copyfile(PREVIOUS/'model-trace.jsonl',c.output/'model-trace.jsonl')
    os.chmod(c.output/'model-trace.jsonl',0o600)
    c.receipt['generative_trace']=trace
    # The native usage records the recovered request, but controller latency was lost.
    events=[n.strict_loads(x) for x in (PREVIOUS/'model-trace.jsonl').read_text().splitlines()]
    e=events[-1]; last=c.receipt['calls'][-1]
    fields=('input_tokens','output_tokens','cache_read_tokens','cache_write_tokens','reasoning_tokens')
    last.update(usage={f:{'known_total':e[f],'observed_events':1,'unknown_entered_events':0} for f in fields},
        entered_turns=1,physical_attempt_events=1,setup_attempts=0,failed_identity_unknown_events=0,
        logical_request_ids=1,succeeded_events=1,status='validated',
        answer_sha256=n.sha(n.canonical(answers[-1])),seconds=None,
        recovered_native_latency_seconds=e['latency_ms']/1000,controller_latency_known=False)
    c.start()
    for (name,pack),answer in zip(prepared[:25],answers):
        for ending in ('-prompt.json','-cell.json'):
            c.save(name+ending,load(PREVIOUS/(name+ending)))
        text=load(PREVIOUS/(name+'-raw.json'))['text'] if name!='pack-025' else load(PREVIOUS/'external-final-read.json')['stdout']
        c.save(name+'-raw.json',{'text':text}); c.save(name+'-answer.json',answer)
        c.bind_answer(name,answer,sorted(pack['questions']))
        c.receipt['calls'][len([x for x in prepared[:25] if x[0]<name])]['status']='completed'
        next(x for x in c.receipt['panel_rows'] if x['name']==name)['status']='completed'
    c.checkpoint()


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    mode=ap.add_mutually_exclusive_group()
    for m in ('seal','offline','live'):mode.add_argument('--'+m,action='store_true')
    ap.add_argument('--acknowledge-provider-calls',action='store_true')
    ap.add_argument('--azdaja',type=Path);ap.add_argument('--output',type=Path)
    ap.add_argument('--private-jcode-home',type=Path)
    args=ap.parse_args(argv)
    if not any((args.seal,args.offline,args.live)):
        print(json.dumps({'status':'offline_plan','new_provider_calls':0,'allowed_suffix':[26,112]}));return 0
    b.check(args.azdaja is not None,'binary_required')
    if args.live:
        b.check(args.acknowledge_provider_calls and args.private_jcode_home is not None,'acknowledgement_required')
        b.check(time.time()<DEADLINE,'original_campaign_deadline')
    prepared=b.rows(); files=inventory(args.azdaja)
    if args.seal:
        with SEAL.open('xb') as f:f.write(n.canonical({'files':files,'suffix':b.panel_identity(prepared[25:]),'deadline_unix':DEADLINE})+b'\n')
        print(json.dumps({'status':'sealed','provider_calls':0,'remaining_calls':87}));return 0
    b.check(args.output is not None and not os.path.lexists(args.output) and args.output.parent.is_dir(),'new_output_required')
    if args.live:
        seal=load(SEAL)
        b.check(seal=={'files':files,'suffix':b.panel_identity(prepared[25:]),'deadline_unix':DEADLINE},'continuation_freeze_changed')
        b.check((args.private_jcode_home/'openai-auth.json').is_file(),'private_profile_missing')
        with SEAL.with_suffix('.started').open('xb') as f:
            f.write(n.canonical({'seal_sha256':n.sha(SEAL.read_bytes()),'automatic_retry':False})+b'\n');f.flush();os.fsync(f.fileno())
        files[str(SEAL.resolve())]=n.sha(SEAL.read_bytes())
    c=Campaign(args.azdaja,args.output,files,authorized=True)
    for key in list(c.env):
        if 'SOCKET' in key.upper() or key.upper().endswith('_SOCK') or key=='JCODE_RUNTIME_DIR':c.env.pop(key)
    c.env['JCODE_HOME']=str(args.private_jcode_home.resolve()) if args.live else str(c.work/'absent-subscription')
    try:
        seed(c,prepared)
        if not args.live:
            c.load('expected_prefix_ids',[qid for _,p in prepared[:25] for qid in p['questions']])
            code='seen=[qid for a in observations.values() for qid in a]\nassert sorted(seen)==sorted(json.loads(expected_prefix_ids))\nFINAL({"observed":len(seen),"judge_attempts":judge_stats()["attempts"]})\n'
            c.save('recovery-offline.json',n.strict_loads(c.cell('recovery-offline',code)))
            c.finish('offline_recovery_passed')
        else:
            for name,pack in prepared[25:]:
                c.receipt['panel_rows'].append({'name':name,'pack_sha256':n.sha(n.canonical(pack)),
                    'ids':sorted(pack['questions']),'status':'attempted'})
                c.checkpoint(); c.generate(name,pack)
                c.receipt['panel_rows'][-1]['status']='completed';c.checkpoint()
                print('JCODE_PROGRESS '+json.dumps({'current':int(name[-3:]),'total':112,'message':name+' completed'}),flush=True)
            b.reduce_ids(c,prepared);c.finish('completed')
    except BaseException as exc:
        c.finish('stopped',str(exc) if isinstance(exc,n.Stop) else type(exc).__name__)
    print(json.dumps({'status':c.receipt['status'],'logical_calls_including_predecessor':c.receipt['logical_llm_calls'],
        'new_calls':c.receipt['logical_llm_calls']-25,'stop_reason':c.receipt.get('stop_reason')}),flush=True)
    return 0 if c.receipt['status'] in ('completed','offline_recovery_passed') and c.receipt.get('cleanup_exit')==0 else 2

if __name__=='__main__':raise SystemExit(main())
