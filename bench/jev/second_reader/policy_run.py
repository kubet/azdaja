"""Bounded later policy study through the unchanged native Azdaja CLI."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from bench.jev.angle_lab import native as n
from bench.jev.second_reader import policy_study as p

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BINARY_SHA = '13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32'


def rows():
    # Selection deliberately uses original decisions only, never gold labels.
    ledger = n.strict_loads((ROOT/'bench/jev/row645_labels/result.json').read_bytes())['occurrence_ledger']
    disagreement = [r['id'] for r in ledger if r['typed_ham'] != r['direct_ham']]
    adjudication = p.adjudication_pack(p.selected_records(), disagreement)
    phrasing = p.packs()
    if len(phrasing) != 11 or len(adjudication['questions']) != 4:
        raise n.Stop('policy_panel_contract')
    return [('adjudication','generative',adjudication)] + [
        (f'phrasing-{i:02d}','typed',pack) for i,pack in enumerate(phrasing,1)]


def inventory(binary):
    if n.sha(binary.read_bytes()) != BINARY_SHA: raise n.Stop('binary_identity')
    files = [Path(__file__), HERE/'test_policy_run.py', HERE/'policy_study.py', HERE/'test_policy_study.py', HERE/'PLAN.md',
             ROOT/'bench/jev/row645_labels/result.json', ROOT/'bench/oolong/context-131072.txt',
             ROOT/'bench/jev/angle_lab/native.py', ROOT/'bench/jev/span_selection/kernel.py',
             ROOT/'bench/jev/span_selection/run.py', binary, Path(shutil.which('jcode')).resolve()]
    return {str(x.resolve()): n.sha(x.read_bytes()) for x in files}


class Campaign(n.Campaign):
    def left(self):
        value = 300 - (time.monotonic() - self.started)
        if value <= 0: raise n.Stop('policy_deadline')
        return value

    @n.terminal
    def typed(self, name, pack):
        if self.receipt['typed_calls_started'] >= 11: raise n.Stop('policy_typed_cap')
        return super().typed(name, pack)

    @n.terminal
    def generate(self, name, pack, instruction=None):
        if self.receipt['logical_llm_calls'] >= 1: raise n.Stop('policy_generation_cap')
        return super().generate(name, pack, instruction)

    def checkpoint(self):
        self.receipt.update(experiment_schema='azdaja.second_reader.policy.v1',
            automatic_approval_authorized=False, adjudicator='fresh_blind_same_model_request_not_independent_oracle',
            caps={'typed_requests':11,'generative_logical_requests':1,'generative_entered_turns':2,
                  'known_typed_input_tokens':1500000,'elapsed_seconds':300})
        super().checkpoint()


def exercise(campaign, live):
    campaign.start()
    campaign.receipt['panel_rows'] = []
    for name, arm, pack in rows():
        if not live:
            campaign.load('policy_payload',pack)
            value = n.strict_loads(campaign.cell(name+'-offline',
                'p=json.loads(policy_payload)\nFINAL({"hash":sha256(policy_payload),"ids":list(p["questions"].keys()),"attempts":judge_stats()["attempts"]})\n'))
            if value != {'hash':n.sha(n.canonical(pack)),'ids':sorted(pack['questions']),'attempts':0}:
                raise n.Stop('offline_policy_custody')
            continue
        row = {'name':name,'arm':arm,'status':'attempted','pack_sha256':n.sha(n.canonical(pack)),
               'ids':sorted(pack['questions'])}
        campaign.receipt['panel_rows'].append(row); campaign.checkpoint()
        start = time.monotonic()
        try:
            body = campaign.generate(name,pack) if arm == 'generative' else campaign.typed(name,pack)
            row.update(status='completed',response_sha256=n.sha(n.canonical(body)),whole_seconds=time.monotonic()-start)
            if arm == 'generative':
                if n.usage_summary(campaign.output/'model-trace.jsonl')['entered_turns'] > 2:
                    raise n.Stop('entered_turn_cap')
        except BaseException:
            row.update(status='stopped',whole_seconds=time.monotonic()-start)
            campaign.checkpoint(); raise
        campaign.checkpoint()
        print('JCODE_PROGRESS '+json.dumps({'current':len(campaign.receipt['panel_rows']),'total':12,'message':name+' completed'}),flush=True)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    mode=ap.add_mutually_exclusive_group()
    for x in ('seal','offline','live'): mode.add_argument('--'+x,action='store_true')
    ap.add_argument('--azdaja',type=Path); ap.add_argument('--output',type=Path)
    ap.add_argument('--manifest',type=Path,default=HERE/'POLICY-FROZEN.json')
    ap.add_argument('--credential-state-root',type=Path)
    ap.add_argument('--private-jcode-home',type=Path)
    ap.add_argument('--acknowledge-provider-calls',action='store_true'); args=ap.parse_args(argv)
    if not any((args.seal,args.offline,args.live)):
        print(json.dumps({'status':'offline_plan','provider_calls':0,'typed_requests_max':11,'generative_calls_max':1})); return 0
    if not args.azdaja: ap.error('--azdaja required')
    prepared=rows(); files=inventory(args.azdaja)
    if args.seal:
        with args.manifest.open('xb') as f: f.write(n.canonical({'schema':'azdaja.second_reader.policy_freeze.v1',
            'files':files,'rows':[{'name':a,'arm':b,'pack_sha256':n.sha(n.canonical(c))} for a,b,c in prepared],
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()})+b'\n')
        return 0
    if not args.output or os.path.lexists(args.output) or not args.output.parent.is_dir(): ap.error('new output with existing parent required')
    if args.live:
        if not args.acknowledge_provider_calls or not args.credential_state_root or not args.private_jcode_home:
            ap.error('live requires explicit acknowledgement and private attachment/OAuth roots')
        if not args.credential_state_root.is_dir() or not (args.private_jcode_home/'openai-auth.json').is_file():
            ap.error('private credential roots must exist before admission')
        seal=n.strict_loads(args.manifest.read_bytes())
        if seal['files'] != files or seal['rows'] != [{'name':a,'arm':b,'pack_sha256':n.sha(n.canonical(c))} for a,b,c in prepared]: raise n.Stop('policy_freeze_changed')
        with args.manifest.with_suffix('.started').open('xb') as f:
            f.write(n.canonical({'seal_sha256':n.sha(args.manifest.read_bytes()),'automatic_retry':False})+b'\n'); f.flush(); os.fsync(f.fileno())
        files[str(args.manifest.resolve())]=n.sha(args.manifest.read_bytes())
    c=Campaign(args.azdaja,args.output,files,authorized=True,attached_root=args.credential_state_root if args.live else None)
    for key in ('AZDAJA_JCODE_API_SOCKET','JCODE_API_SOCKET','JCODE_SOCKET','JCODE_RUNTIME_DIR'): c.env.pop(key,None)
    c.env['JCODE_HOME']=str(args.private_jcode_home.resolve(strict=True)) if args.live else str(c.work/'absent-jcode-profile')
    try:
        exercise(c,args.live)
        c.finish('completed' if args.live else 'offline_public_workflow_passed')
    except BaseException as error:
        c.finish('stopped',str(error) if isinstance(error,n.Stop) else type(error).__name__)
        print(json.dumps({'status':'stopped','reason':c.receipt.get('stop_reason')})); return 2
    print(json.dumps({'status':c.receipt['status'],'typed_attempts':c.receipt['typed_calls_started'],'logical_llm_calls':c.receipt['logical_llm_calls']}))
    return 0 if c.receipt.get('cleanup_exit') == 0 else 2

if __name__=='__main__': raise SystemExit(main())
