"""One sealed row651 run through native judge_many. Default/offline never infer."""
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import time
from bench.jev.angle_lab import native as n

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PACK_DIR=HERE/'row651/candidate255'
BINARY_SHA='13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32'
MAX_REQUESTS,MAX_INPUT,MAX_SECONDS=112,4_000_000,1200
MAX_QUESTIONS,MAX_STATE,MAX_REQUEST=255,70_000,90_000
MODEL=n.MODEL


def check(ok, reason):
    if not ok: raise n.Stop(reason)


def validate_pack(pack):
    check(isinstance(pack,dict) and set(pack)=={'state','questions'},'pack_shape')
    check(isinstance(pack['state'],dict) and set(pack['state'])=={'records'},'state_shape')
    records=pack['state']['records']; questions=pack['questions']
    check(isinstance(records,dict) and isinstance(questions,dict) and set(records)==set(questions),'question_record_coverage')
    check(1<=len(questions)<=MAX_QUESTIONS,'question_cap')
    request=dict(pack,model=MODEL); raw=n.canonical(request)
    check(len(n.canonical(pack['state']))<=MAX_STATE and len(raw)<=MAX_REQUEST,'request_cap')
    check(not n.SECRET.search(raw.decode()),'credential_pattern')
    for qid,q in questions.items():
        check(isinstance(qid,str) and isinstance(q,dict) and set(q)=={'type','instructions'} and q['type']=='noul' and isinstance(q['instructions'],str),'question_contract')
    return request


def packs():
    manifest=n.strict_loads((PACK_DIR/'MANIFEST.json').read_bytes())
    source=(ROOT/'bench/oolong/context-1048576.txt').read_bytes()
    check(n.sha(source)==manifest['source_sha256']=='78e61364029606a211e8d6fced3fefea42f37651bc2c4b84ef54856e1e70f4fe','source_identity')
    ledger=n.strict_loads((PACK_DIR/'occurrence-ledger.json').read_bytes())['records']
    expected={r['id']:r for r in ledger}; check(len(expected)==len(ledger)==17469,'ledger_coverage')
    for r in ledger:
        raw=source[r['byte_start']:r['byte_end']]
        check(raw.decode()==r['text'] and n.sha(raw)==r['record_sha256'],'source_span')
    out=[]; seen=set(); offset=0
    for index,item in enumerate(manifest['packs'],1):
        check(item['file']==f'pack-{index:03d}.json','pack_filename')
        raw=(PACK_DIR/item['file']).read_bytes(); check(n.sha(raw)==item['sha256'],'pack_hash')
        pack=n.strict_loads(raw); validate_pack(pack)
        source_ids=[r['id'] for r in ledger[offset:offset+len(pack['questions'])]]
        check(set(pack['questions'])==set(source_ids) and item['first_id']==source_ids[0] and item['last_id']==source_ids[-1], 'contiguous_source_membership')
        check(list(pack['questions'])==sorted(pack['questions']),'canonical_wire_order')
        offset+=len(source_ids)
        check(not seen.intersection(pack['questions']),'duplicate_question')
        for qid,text in pack['state']['records'].items(): check(qid in expected and text==expected[qid]['text'],'pack_source')
        seen.update(pack['questions']); out.append((item['file'][:-5],pack))
    check(len(out)==MAX_REQUESTS and seen==set(expected),'full_pack_coverage')
    return out


class Campaign(n.Campaign):
    def left(self):
        value=MAX_SECONDS-(time.monotonic()-self.started)
        check(value>0,'campaign_deadline'); return value

    def configure(self,enabled):
        remaining=MAX_INPUT-self.receipt['known_typed_input_tokens']
        check(not enabled or (remaining>0 and not self.receipt['typed_unknown_usage']),'typed_budget_or_unknown_usage')
        timeout=max(1,min(120,int(self.left())))
        text=f'''sub_llm_cmd="/usr/bin/false"
default_model="{MODEL}"
sub_timeout={timeout}
cell_timeout={timeout}
output_cap=262144
max_calls_per_cell=1
[judge]
enabled={str(enabled).lower()}
model="{MODEL}"
expected_model="{MODEL}"
key_env="TYPESAFE_API_KEY"
timeout_secs=20
max_requests_per_cell=1
max_questions_per_cell={MAX_QUESTIONS}
max_input_tokens_per_cell={max(1,remaining)}
max_request_bytes={MAX_REQUEST}
max_response_bytes=262144
'''
        path=self.work/'config.toml'; path.write_text(text); os.chmod(path,0o600)

    def checkpoint(self):
        self.receipt.update(experiment_schema='azdaja.second_reader.row651.v1',automatic_approval_authorized=False,
                            requested_model=MODEL,caps={'requests':MAX_REQUESTS,'input_tokens':MAX_INPUT,'seconds':MAX_SECONDS,
                            'questions':MAX_QUESTIONS,'state_bytes':MAX_STATE,'request_bytes':MAX_REQUEST})
        super().checkpoint()

    @n.terminal
    def typed(self,name,pack):
        check(n.IDENTIFIER.fullmatch(name) and self.receipt['typed_calls_started']<MAX_REQUESTS,'request_admission')
        request=validate_pack(pack); self.configure(True)
        self.save(name+'-request.json',request)
        self.load('request_payload',dict(name=name,state=request['state'],questions=request['questions']))
        self.receipt['typed_calls_started']+=1; self.receipt['typed_questions']+=len(request['questions'])
        self.receipt['typed_unknown_usage']+=1; self.receipt['typed_unknown_output_usage']+=1; self.checkpoint()
        started=time.monotonic(); result=n.strict_loads(self.cell(name,n.JUDGE_CODE))
        self.save(name+'-observation.json',result); stats=result['stats']
        for field in ('provider_requests','known_input_tokens','unknown_input_usage_requests'):
            check(type(stats.get(field)) is int and stats[field]>=0,'accounting_type')
        check(stats['provider_requests']<=1 and stats['unknown_input_usage_requests']<=stats['provider_requests'],'accounting_shape')
        self.receipt['confirmed_typed_requests']+=stats['provider_requests']
        self.receipt['known_typed_input_tokens']+=stats['known_input_tokens']
        self.receipt['typed_unknown_usage']+=stats['unknown_input_usage_requests']-1
        if stats['provider_requests']==0: self.receipt['typed_unknown_output_usage']-=1
        call={'name':name,'arm':'typed','seconds':time.monotonic()-started,'request_bytes':len(n.canonical(request)),
              'questions':len(request['questions']),'provider_requests':stats['provider_requests'],'known_input_tokens':stats['known_input_tokens']}
        self.receipt['calls'].append(call); self.checkpoint()
        check('failure' not in result,'typed_contract_or_resource_failure')
        body=result['observation']; usage=body.get('usage')
        check(body['model']==MODEL and body['_azdaja']['request_sha256']==n.sha(n.canonical(request)) and stats['provider_requests']==1,'typed_identity')
        check(set(body['answers'])==set(request['questions']),'answer_coverage')
        for a in body['answers'].values():
            check(set(a)=={'type','noul'} and a['type']=='noul' and type(a['noul']) in (int,float) and math.isfinite(a['noul']) and 0<=a['noul']<=1,'answer_domain')
        check(isinstance(usage,dict) and all(type(usage.get(k)) is int and usage[k]>=0 for k in ('input_tokens','output_tokens')),'usage_contract')
        check(usage['input_tokens']==stats['known_input_tokens'] and not stats['unknown_input_usage_requests'],'usage_identity')
        self.receipt['known_typed_output_tokens']+=usage['output_tokens']; self.receipt['typed_unknown_output_usage']-=1
        call.update(reported_output_tokens=usage['output_tokens'],native_elapsed_ms=body['_azdaja']['elapsed_ms'],response_json_bytes=len(n.canonical(body)))
        self.checkpoint(); check(self.receipt['known_typed_input_tokens']<=MAX_INPUT,'input_budget_crossed')
        retained=n.strict_loads(self.cell(name+'-reentry','FINAL(observations['+repr(name)+'])\n'))
        check(retained==body,'reentry_identity')
        return body

    def generate(self,*args,**kwargs):
        raise n.Stop('generative_disabled_for_full_run')


REDUCE='''expected=json.loads(expected_ids_payload)
seen={}
ham=0
sum_p=0.0
for body in observations.values():
    for qid,answer in body["answers"].items():
        if qid in seen:
            raise ValueError("duplicate observed ID")
        seen[qid]=True
        p=answer["noul"]
        ham+=int(p>=0.5)
        sum_p+=p
complete=sorted(seen.keys())==sorted(expected)
FINAL({"observed":len(seen),"expected":len(expected),"complete":complete,"ham":ham,"sum_noul":sum_p,"answer":"Answer: "+str(ham) if complete else None,"attempts_in_reduction":judge_stats()["attempts"]})
'''


def exercise(campaign,rows,live):
    campaign.start(); expected=[qid for _,pack in rows for qid in pack['questions']]
    campaign.load('expected_ids_payload',expected)
    campaign.receipt['panel_rows']=[]
    for ordinal,(name,pack) in enumerate(rows,1):
        if not live:
            campaign.load('request_payload',pack)
            observed=n.strict_loads(campaign.cell(name+'-offline','p=json.loads(request_payload)\nFINAL({"sha256":sha256(request_payload),"ids":sorted(p["questions"]),"attempts":judge_stats()["attempts"]})\n'))
            check(observed=={'sha256':n.sha(n.canonical(pack)),'ids':sorted(pack['questions']),'attempts':0},'offline_custody')
        else:
            row={'name':name,'status':'attempted','pack_sha256':n.sha(n.canonical(pack)),'ids':sorted(pack['questions'])}
            campaign.receipt['panel_rows'].append(row); campaign.checkpoint(); start=time.monotonic()
            try:
                body=campaign.typed(name,pack)
                row.update(status='completed',response_sha256=n.sha(n.canonical(body)),whole_seconds=time.monotonic()-start)
            except BaseException:
                row.update(status='stopped',whole_seconds=time.monotonic()-start); campaign.checkpoint(); raise
            campaign.checkpoint()
        print('JCODE_PROGRESS '+json.dumps({'current':ordinal,'total':len(rows),'message':name+(' live' if live else ' offline')}),flush=True)
    campaign.configure(False)
    reduced=n.strict_loads(campaign.cell('final-reduction',REDUCE)); campaign.save('final-reduction.json',reduced)
    check(reduced['attempts_in_reduction']==0,'reduction_inferred')
    check(reduced['complete'] if live else (not reduced['complete'] and reduced['observed']==0),'reduction_coverage')
    campaign.receipt['native_reduction']=reduced
    if not live:
        # Exercise the actual full-size reduction, explicitly synthetic and never
        # mixed with provider observations or the live study's quality evidence.
        synthetic={name:{'answers':{qid:{'type':'noul','noul':0.25} for qid in pack['questions']}} for name,pack in rows}
        campaign.load('synthetic_payload',synthetic)
        campaign.cell('synthetic-bind','observations=json.loads(synthetic_payload)\nFINAL({"synthetic":True})\n')
        replay=n.strict_loads(campaign.cell('synthetic-reduction',REDUCE))
        check(replay=={'observed':len(expected),'expected':len(expected),'complete':True,'ham':0,'sum_noul':len(expected)/4,'answer':'Answer: 0','attempts_in_reduction':0},'synthetic_reduction')
        campaign.receipt['offline_synthetic_full_size_reduction']=replay
    campaign.checkpoint()


def inventory(binary):
    check(n.sha(binary.read_bytes())==BINARY_SHA,'binary_identity')
    files=[Path(__file__),HERE/'test_large_run.py',HERE/'row651/prepare.py',HERE/'PLAN.md']+list(PACK_DIR.glob('*.json'))
    files += [ROOT/'bench/oolong/context-1048576.txt',ROOT/'bench/oolong/row-651.json',ROOT/'bench/jev/angle_lab/native.py',
              ROOT/'bench/jev/span_selection/kernel.py',ROOT/'bench/jev/span_selection/run.py',binary]
    return {str(p.resolve()):n.sha(p.read_bytes()) for p in sorted(set(files))}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__); mode=ap.add_mutually_exclusive_group()
    for name in ('seal','offline','live'): mode.add_argument('--'+name,action='store_true')
    ap.add_argument('--azdaja',type=Path); ap.add_argument('--output',type=Path)
    ap.add_argument('--manifest',type=Path,default=HERE/'ROW651-FROZEN.json')
    ap.add_argument('--credential-state-root',type=Path); ap.add_argument('--acknowledge-provider-calls',action='store_true'); args=ap.parse_args(argv)
    if not (args.seal or args.offline or args.live):
        print(json.dumps({'status':'offline_plan','provider_calls':0,'model':MODEL,'packs':112,'occurrences':17469})); return 0
    if not args.azdaja: ap.error('--azdaja required')
    prepared=packs(); files=inventory(args.azdaja)
    if args.seal:
        with args.manifest.open('xb') as f: f.write(n.canonical({'schema':'azdaja.second_reader.row651_freeze.v1','files':files,
             'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'binary_sha256':BINARY_SHA,'pack_count':112,
             'caps':{'requests':MAX_REQUESTS,'input_tokens':MAX_INPUT,'seconds':MAX_SECONDS}})+b'\n')
        return 0
    if not args.output or os.path.lexists(args.output) or not args.output.parent.is_dir(): ap.error('new output with existing parent required')
    if args.live:
        if not args.acknowledge_provider_calls or not args.credential_state_root: ap.error('explicit live acknowledgement and private attached root required')
        check(args.credential_state_root.is_dir(),'credential_root_absent')
        frozen=n.strict_loads(args.manifest.read_bytes()); check(frozen['files']==files and frozen['binary_sha256']==BINARY_SHA,'freeze_changed')
        with args.manifest.with_suffix('.started').open('xb') as f:
            f.write(n.canonical({'manifest_sha256':n.sha(args.manifest.read_bytes()),'automatic_retry':False})+b'\n'); f.flush(); os.fsync(f.fileno())
        files[str(args.manifest.resolve())]=n.sha(args.manifest.read_bytes())
    campaign=Campaign(args.azdaja,args.output,files,authorized=True,attached_root=args.credential_state_root if args.live else None)
    for key in ('AZDAJA_JCODE_API_SOCKET','JCODE_API_SOCKET','JCODE_SOCKET','JCODE_RUNTIME_DIR'): campaign.env.pop(key,None)
    campaign.env['JCODE_HOME']=str(campaign.work/'absent-jcode-home')
    try:
        exercise(campaign,prepared,args.live)
        campaign.finish('completed' if args.live else 'offline_public_workflow_passed')
    except BaseException as error:
        campaign.finish('stopped',str(error) if isinstance(error,n.Stop) else type(error).__name__)
        print(json.dumps({'status':'stopped','reason':campaign.receipt['stop_reason']})); return 2
    print(json.dumps({'status':campaign.receipt['status'],'typed_requests':campaign.receipt['confirmed_typed_requests'],
                      'known_input_tokens':campaign.receipt['known_typed_input_tokens'],'reduction':campaign.receipt['native_reduction']}))
    return 0 if campaign.receipt.get('cleanup_exit')==0 else 2

if __name__=='__main__': raise SystemExit(main())
