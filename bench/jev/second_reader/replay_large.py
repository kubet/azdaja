"""Offline consistency replay of a terminal full-row receipt, not provider authentication."""
import argparse
import json
import math
from pathlib import Path, PurePosixPath
import statistics
from bench.jev.angle_lab import native as n
from bench.jev.second_reader import large_run as run

_SEAL_RELATIVE = 'bench/jev/second_reader/ROW651-FROZEN.json'
_SEAL_SHA = 'c6c4d7f840718466a2f12fb4c288b6fac104e21357717119090fd9ba3bc3cbb1'


def check(condition, why):
    if not condition: raise ValueError(why)


def portable_sources(receipt, root):
    """Check relocated source bytes, not the unavailable historical executable.

    Recorded absolute paths are data, never lookup locations in this mode.
    The separate scope record must accompany the legacy numerical summary.
    """
    root = Path(root).resolve(strict=True)
    files = receipt['frozen_files']
    check(type(files) is dict and files, 'frozen source inventory')
    seal_path = root/_SEAL_RELATIVE
    check(seal_path.is_file() and not seal_path.is_symlink()
          and root in seal_path.resolve(strict=True).parents, 'missing or escaped seal')
    seal_raw = seal_path.read_bytes()
    check(n.sha(seal_raw) == _SEAL_SHA, 'original pre-run seal changed')
    sealed = n.strict_loads(seal_raw)['files']
    anchors = [p for p in sealed if type(p) is str
               and p.endswith('/bench/jev/angle_lab/native.py')]
    check(len(anchors) == 1, 'source root anchor')
    origin = PurePosixPath(anchors[0]).parents[3]
    check(origin.is_absolute() and '..' not in origin.parts, 'source origin')
    expected = dict(sealed)
    expected[str(origin/_SEAL_RELATIVE)] = _SEAL_SHA
    check(files == expected, 'frozen source coverage')
    sources, external = 0, []
    for path, digest in files.items():
        check(type(path) is str and type(digest) is str and len(digest) == 64
              and all(c in '0123456789abcdef' for c in digest), 'frozen identity')
        old = PurePosixPath(path)
        check(old.is_absolute() and '..' not in old.parts and str(old) == path, 'frozen path')
        try:
            relative = old.relative_to(origin)
        except ValueError:
            external.append((path, digest))
            continue
        local = root.joinpath(*relative.parts)
        check(local.is_file() and not local.is_symlink(), 'missing relocated source')
        check(root in local.resolve(strict=True).parents, 'relocated source escape')
        check(n.sha(local.read_bytes()) == digest, 'relocated source changed')
        sources += 1
    check(len(external) == 1 and external[0][1] == receipt['binary_sha256'] == run.BINARY_SHA,
          'unexpected external frozen artifact')
    return {'mode':'portable_retained_evidence', 'source_files_verified':sources,
            'sealed_inventory_sha256':_SEAL_SHA,
            'runtime_binary_identity_recorded':receipt['binary_sha256'],
            'runtime_binary_bytes_verified':False, 'recorded_absolute_paths_used_for_lookup':False,
            'provider_authenticity_proven':False}


def replay(folder, *, portable=False):
    folder=Path(folder); receipt=n.strict_loads((folder/'receipt.json').read_bytes())
    check(receipt['status'] in ('completed','stopped'),'terminal status required')
    check(receipt['binary_sha256']==run.BINARY_SHA,'binary identity')
    scope = portable_sources(receipt, run.ROOT) if portable else None
    if not portable:
        for path,digest in receipt['frozen_files'].items():
            check(n.sha(Path(path).read_bytes())==digest,'frozen source changed')
    check(receipt['logical_llm_calls']==0 and receipt['generative_trace']['entered_turns']==0,'unexpected generation')
    prepared=dict(run.packs()); rows=receipt.get('panel_rows',[])
    check([r['name'] for r in rows]==list(prepared)[:len(rows)],'attempt order/coverage')
    check(len(rows)<=run.MAX_REQUESTS,'attempt cap')
    calls={x['name']:x for x in receipt['calls']}
    check(len(calls)==len(receipt['calls']),'duplicate calls')
    seen={}; input_tokens=0; output_tokens=0; unknown_output=0; durations=[]; native_ms=[]; request_bytes=0
    confirmed=0; eligible_packs=0
    for row in rows:
        name=row['name']; pack=prepared[name]
        check(row['pack_sha256']==n.sha(n.canonical(pack)) and row['ids']==sorted(pack['questions']),'pack binding')
        request_path=folder/(name+'-request.json'); observation_path=folder/(name+'-observation.json')
        if not request_path.exists():
            check(row['status']=='stopped','missing request'); continue
        request=n.strict_loads(request_path.read_bytes())
        check(request==dict(pack,model=run.MODEL),'request/source equality')
        request_bytes+=len(n.canonical(request))
        if not observation_path.exists():
            check(row['status']=='stopped','missing observation'); unknown_output+=1; continue
        observation=n.strict_loads(observation_path.read_bytes()); stats=observation['stats']
        for k in ('provider_requests','known_input_tokens','unknown_input_usage_requests'):
            check(type(stats.get(k)) is int and stats[k]>=0,'stats type')
        confirmed+=stats['provider_requests']; input_tokens+=stats['known_input_tokens']
        if 'failure' in observation:
            check(row['status']=='stopped','failed response completed'); unknown_output+=int(stats['provider_requests']>0); continue
        body=observation['observation']; metadata=body['_azdaja']
        check(body['model']==run.MODEL and metadata['request_sha256']==n.sha(n.canonical(request)),'response identity')
        check(stats['provider_requests']==1 and stats['unknown_input_usage_requests']==0,'response accounting')
        usage=body['usage']
        check(all(type(usage.get(k)) is int and usage[k]>=0 for k in ('input_tokens','output_tokens')),'usage types')
        check(usage['input_tokens']==stats['known_input_tokens'],'usage disagreement'); output_tokens+=usage['output_tokens']
        check(set(body['answers'])==set(pack['questions']),'answer coverage')
        for a in body['answers'].values():
            check(set(a)=={'type','noul'} and a['type']=='noul' and type(a['noul']) in (int,float) and math.isfinite(a['noul']) and 0<=a['noul']<=1,'answer domain')
        if row['status']=='completed':
            check(input_tokens<=run.MAX_INPUT,'ineligible input crossing')
            check(row['response_sha256']==n.sha(n.canonical(body)),'response binding')
            call=calls[name]
            check(call['questions']==len(pack['questions']) and call['request_bytes']==len(n.canonical(request)),'call request binding')
            check(call['known_input_tokens']==usage['input_tokens'] and call['reported_output_tokens']==usage['output_tokens'],'call usage')
            check(call['provider_requests']==1 and call['native_elapsed_ms']==metadata['elapsed_ms'],'call identity')
            check(type(call['seconds']) in (int,float) and math.isfinite(call['seconds']) and call['seconds']>=0,'call duration')
            check(type(metadata['elapsed_ms']) is int and 0<=metadata['elapsed_ms']<=20000 and call['seconds']+.002>=metadata['elapsed_ms']/1000,'native duration')
            check(metadata['cache_hit'] is False and metadata['provider_requests_this_call']==1,'unexpected cached response')
            check(metadata['original_usage']==usage and metadata['new_request_usage']==usage,'native usage identity')
            check(not set(seen).intersection(body['answers']),'duplicate eligible observations')
            seen.update({k:v['noul'] for k,v in body['answers'].items()}); eligible_packs+=1
            durations.append(call['seconds']); native_ms.append(metadata['elapsed_ms'])
        else: check(row['status']=='stopped','unknown row status')
    check(confirmed==receipt['confirmed_typed_requests'],'confirmed request total')
    check(input_tokens==receipt['known_typed_input_tokens'] and output_tokens==receipt['known_typed_output_tokens'],'total usage')
    check(unknown_output==receipt['typed_unknown_output_usage'],'unknown output total')
    check(receipt['typed_calls_started']<=len(rows),'started count')
    check(type(receipt['elapsed_seconds']) in (int,float) and math.isfinite(receipt['elapsed_seconds']) and receipt['elapsed_seconds']+.001>=sum(durations),'impossible wall time')
    check(sum(native_ms)/1000<=run.MAX_SECONDS+.112,'cumulative native deadline')
    full=eligible_packs==112 and len(seen)==17469
    ham=sum(p>=.5 for p in seen.values()); sum_p=math.fsum(seen.values())
    if receipt['status']=='completed':
        check(full and receipt['typed_calls_started']==confirmed==112,'false completion')
        check(receipt['cleanup_exit']==0 and receipt['typed_unknown_usage']==0,'incomplete cleanup or usage')
        reduction=n.strict_loads((folder/'final-reduction.json').read_bytes())
        check(reduction==receipt['native_reduction'],'reduction receipt mismatch')
        check(reduction['complete'] is True and reduction['observed']==reduction['expected']==17469 and reduction['ham']==ham,'reduction count')
        check(abs(reduction['sum_noul']-sum_p)<1e-7 and reduction['answer']==f'Answer: {ham}' and reduction['attempts_in_reduction']==0,'reduction values')
    # Official answer is detached and consulted only after all observations are checked.
    row=n.strict_loads((run.ROOT/'bench/oolong/row-651.json').read_bytes())
    answer=n.strict_loads(row['answer'])
    check(isinstance(answer,list) and len(answer)==1 and type(answer[0]) is int,'official answer contract')
    gold=answer[0]
    retained={str(p.relative_to(folder)):n.sha(p.read_bytes()) for p in sorted(folder.rglob('*')) if p.is_file() and 'private-work' not in p.parts}
    result = {'schema':'azdaja.second_reader.row651_replay.v1','consistent':True,'status':receipt['status'],
        'complete_panel':full,'observed_occurrences':len(seen),'expected_occurrences':17469,
        'eligible_packs':eligible_packs,'attempted_packs':len(rows),'confirmed_typed_requests':confirmed,
        'threshold':.5,'ham_count':ham,'sum_noul':sum_p,'official_count':gold,
        'exact_task_pass':full and ham==gold,'signed_count_error':ham-gold if full else None,
        'sum_noul_minus_gold':sum_p-gold if full else None,'per_item_accuracy_measured':False,
        'known_input_tokens':input_tokens,'known_output_tokens':output_tokens,
        'unknown_input_attempts':receipt['typed_unknown_usage'],'unknown_output_attempts':unknown_output,
        'request_bytes':request_bytes,'elapsed_seconds':receipt['elapsed_seconds'],
        'median_native_ms':statistics.median(native_ms) if native_ms else None,
        'median_call_seconds':statistics.median(durations) if durations else None,
        'known_input_estimate_usd':input_tokens*.042/1e6,'billing_known':False,
        'matched_generative_baseline':False,'provider_authenticity_proven':False,
        'agreement_authorizes_approval':False,'retained_hashes':retained}
    if scope is not None:
        result['validation_scope'] = scope
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('receipt_dir',type=Path); ap.add_argument('--output',type=Path)
    ap.add_argument('--portable',action='store_true',help='Check relocated source and retained data, not historical executable bytes')
    args=ap.parse_args(); result=replay(args.receipt_dir,portable=args.portable)
    if args.output:
        with args.output.open('xb') as f: f.write(n.canonical(result)+b'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='retained_hashes'},indent=2)); return 0


if __name__=='__main__': raise SystemExit(main())
