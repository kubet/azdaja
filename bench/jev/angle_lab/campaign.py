"""One frozen, bounded native campaign. Default execution is offline only."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import time
from . import native as n
from .gate import prepare_grade as gate
from .verifier import prepare as verifier, grader as verifier_grade
from .descent import run as descent
from .memory import slice as memory
from .reuse import run as reuse

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent


def inputs():
    files=[p for p in HERE.rglob('*') if p.is_file() and p.suffix in ('.py','.json','.jsonl','.md')
           and 'results' not in p.parts and 'rejected' not in p.parts and p.name!='FROZEN.json']
    files += [ROOT/'bench/oolong/row-645.json',ROOT/'bench/oolong/context-131072.txt',
              ROOT/'bench/jev/span_selection/kernel.py',ROOT/'bench/jev/span_selection/run.py']
    return {str(p.relative_to(ROOT)):n.sha(p.read_bytes()) for p in sorted(set(files))}


def seal(binary,path):
    manifest={'schema':'azdaja.angle_campaign.v1','files':inputs(),
              'binary_sha256':n.sha(Path(binary).read_bytes()),
              'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              'order':['calibration','gate-five-alternating-paired-blocks','cascade-residual',
                       'verifier-generative-then-typed','descent-flat-root-children','memory-lexical-then-typed-handoff','reuse'],
              'max_typed_requests':n.MAX_REQUESTS,'max_logical_llm_calls':n.MAX_GENERATIVE,
              'max_typed_input_tokens':n.MAX_INPUT,'max_seconds':n.MAX_SECONDS,
              'models':[n.MODEL,n.GENERATOR], 'rerun_permission':False}
    with open(path,'xb') as f: f.write(n.canonical(manifest)+b'\n')
    return manifest


def labels(body):
    return {qid:answer['choice'] for qid,answer in body['answers'].items()}


def probabilities(body):
    return {qid:answer['noul'] for qid,answer in body['answers'].items()}


def save_result(c,results,name,value):
    results[name]=value
    c.save(name+'-result.json',value)
    print(json.dumps({'stage':name,'complete':True}),flush=True)


def run(c):
    results={}
    c.start()
    fit=gate.fit_threshold(probabilities(c.typed('calibration',gate.calibration())))
    save_result(c,results,'calibration',fit)
    typed,baseline={},{}
    for i,pack in enumerate(gate.packs(),1):
        # Alternate order predeclared, no choice based on observed outputs.
        if i%2:
            baseline.update(c.generate(f'gate-{i}-direct',pack))
            typed.update(probabilities(c.typed(f'gate-{i}-typed',pack)))
        else:
            typed.update(probabilities(c.typed(f'gate-{i}-typed',pack)))
            baseline.update(c.generate(f'gate-{i}-direct',pack))
    tr,br=gate.grade(typed),gate.grade(baseline,False)
    save_result(c,results,'gate',{'typed':tr,'direct':br,
        'quality_bar_passed':tr['exact_task_answer'],
        'gate_replacement_advantage_established':False,
        'label_disagreement_ids':[k for k,p in typed.items() if (p>=.5)!=(baseline[k]=='yes')]})
    if fit['threshold'] is None:
        cascade={'status':'blocked_no_calibration_threshold'}
    else:
        threshold=fit['threshold']
        residual=[(key,text) for key,text in gate.selected_records() if max(typed[key],1-typed[key])<threshold]
        if len(residual)>64:
            cascade={'status':'blocked_residual_question_budget','residuals':len(residual)}
        else:
            try: pack=gate.request(residual) if residual else None
            except n.Stop: pack=None; cascade={'status':'blocked_residual_state_budget','residuals':len(residual)}
            else:
                corrections=c.generate('cascade-residual',pack) if pack else {}
                combined={key:('yes' if p>=.5 else 'no') for key,p in typed.items()}
                combined.update(corrections)
                cascade={'status':'completed','threshold':threshold,'residuals':len(residual),
                         'typed_autoaccepted':len(typed)-len(residual),'quality':gate.grade(combined,False),
                         'semantic_calibration_guarantee':False}
    save_result(c,results,'cascade',cascade)

    pack=verifier.make_pack()
    vb=c.generate('verifier-direct',pack)
    vt=labels(c.typed('verifier-typed',pack))
    save_result(c,results,'verifier',{'typed':verifier_grade.grade(vt),'direct':verifier_grade.grade(vb),
        'no_review':verifier_grade.grade({qid:'supported' for qid in pack['questions']}),
        'deterministic_abstain':verifier_grade.grade({qid:'insufficient' for qid in pack['questions']}),
        'mandatory_final_gate':False})

    start=time.perf_counter(); data=descent.corpus(); preprocessing=time.perf_counter()-start
    flat_body=c.typed('descent-flat',descent.flat_pack(data))
    root_body=c.typed('descent-root',descent.root_pack(data))
    flat={qid:descent.selections(answer,data['leaves'],2) for qid,answer in flat_body['answers'].items()}
    greedy,beam={},{}
    for qid in descent.QUERIES:
        pack=descent.child_pack(data,qid,root_body['answers'][qid])
        if pack:
            c.save('descent-'+qid+'-selected-pack.json',pack)
            selected=descent.leaf_selections(pack,c.typed('descent-'+qid,pack)['answers'])
            greedy[qid],beam[qid]=selected.get('greedy',[]),selected.get('beam',[])
        else: greedy[qid],beam[qid]=[],[]
    save_result(c,results,'descent',{'flat':descent.grade(flat),'greedy':descent.grade(greedy),
        'beam':descent.grade(beam),'leaves':len(data['leaves']),'preprocessing_seconds':preprocessing,
        'index_source_bytes':sum(len(v['text'].encode()) for v in data['leaves'].values()),
        'automatic_planner_or_million_source_claim':False})

    rows=memory.load_raw(); eligible=memory.eligible(rows)
    lexical=memory.select(rows,memory.lexical(eligible))
    c.save('memory-lexical-view.json',lexical)
    lexical_answer=c.generate('memory-lexical-handoff',memory.handoff_pack(lexical))
    raw=c.typed('memory-rank',memory.request(rows))
    ps=probabilities(raw)
    ranked=sorted(ps,key=lambda q:(-ps[q],q))
    typed_view=memory.select(rows,ranked)
    c.save('memory-typed-view.json',typed_view)
    typed_answer=c.generate('memory-typed-handoff',memory.handoff_pack(typed_view))
    save_result(c,results,'memory',{'lexical':memory.grade(lexical_answer),'typed_ranking':memory.grade(typed_answer),
        'lexical_selected':lexical['selected_ids'],'typed_selected':typed_view['selected_ids'],
        'lexical_bytes':lexical['evidence_bytes'],'typed_bytes':typed_view['evidence_bytes'],
        'budget_bytes':memory.BUDGET,'raw_evidence_preserved':len(rows),'scoped_candidates':len(eligible),
        'real_repository_fix_or_multiuser_authorization_claim':False})
    save_result(c,results,'reuse',{'controls':reuse.negative_and_mutation_checks(),
        'scales':[reuse.experiment(size) for size in (1000,10000)],
        'new_provider_calls':0,'incremental_engine_superiority_established':False})
    c.save('results.json',results)
    return results


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--azdaja',type=Path)
    ap.add_argument('--manifest',type=Path,default=HERE/'FROZEN.json')
    ap.add_argument('--seal',action='store_true')
    ap.add_argument('--live',action='store_true')
    ap.add_argument('--acknowledge-provider-calls',action='store_true')
    ap.add_argument('--credential-state-root',type=Path)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    if not args.live and not args.seal:
        print(json.dumps({'status':'offline_plan','provider_calls':0,'lanes':6,'gate_occurrences':len(gate.selected_records())}))
        return 0
    if not args.azdaja: ap.error('--azdaja is required')
    if args.seal:
        if args.live: ap.error('seal and live are separate operations')
        manifest=seal(args.azdaja,args.manifest)
        print(json.dumps({'status':'sealed','files':len(manifest['files']),'provider_calls':0}))
        return 0
    if not args.acknowledge_provider_calls or not args.output or not args.credential_state_root:
        ap.error('live requires explicit acknowledgement, new output and credential state root')
    manifest=n.strict_loads(args.manifest.read_text())
    if manifest['files']!=inputs() or manifest['binary_sha256']!=n.sha(args.azdaja.read_bytes()):
        raise n.Stop('manifest_changed')
    frozen={ROOT/name:h for name,h in manifest['files'].items()}
    frozen[args.manifest]=n.sha(args.manifest.read_bytes())
    marker=args.manifest.with_suffix('.started')
    with open(marker,'xb') as stream:
        stream.write(n.canonical({'manifest_sha256':n.sha(args.manifest.read_bytes()),'automatic_retry':False})+b'\n')
    c=n.Campaign(args.azdaja,args.output,frozen,authorized=True,attached_root=args.credential_state_root)
    try:
        run(c)
    except BaseException as error:
        reason=str(error) if isinstance(error,n.Stop) else type(error).__name__
        c.finish('stopped',reason)
        print(json.dumps({'status':'stopped','reason':reason,'typed_calls_started':c.receipt['typed_calls_started']}))
        return 2
    c.finish('completed')
    print(json.dumps({'status':c.receipt['status'],'typed_calls_started':c.receipt['typed_calls_started'],
                      'logical_llm_calls':c.receipt['logical_llm_calls'],
                      'known_typed_input_tokens':c.receipt['known_typed_input_tokens']}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
