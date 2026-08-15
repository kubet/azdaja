#!/usr/bin/env python3
import argparse,ast,hashlib,importlib.util,json,os,re,stat,statistics,sys
from pathlib import Path
ROOT=Path('/private/tmp/azdaja-rah199-69dxj70n');PUBLIC=ROOT/'public';SOURCE=Path('/private/tmp/azdaja-oolong-source-fb1ycbh1');AD=Path('/Users/vukasinkubet/dev/azdaja/bench/oolong/run.py');SCHEDULE=ROOT/'output/schedule.json';RESULTS=ROOT/'output/results.jsonl';COMPLETION=ROOT/'output/completion.json';OUTPUT=ROOT/'output/scores.json';CONSUMED=ROOT/'output/gold.consumed';WORK=ROOT/'work'
class E(RuntimeError):pass
def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def shab(b):return hashlib.sha256(b).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def rj(p):
 b=p.read_bytes();v=json.loads(b)
 if b!=canon(v):raise E(f'noncanonical {p}')
 return v,b
def validate():
 sched,sb=rj(SCHEDULE);ident=dict(sched);sid=ident.pop('schedule_id')
 if sid!=shab(canon(ident)) or sched.get('total_jobs')!=199 or sched.get('arm')!='jcode-azdaja' or sched.get('reasoning')!='low':raise E('schedule')
 jobs=sched.get('jobs');raw=RESULTS.read_bytes();lines=raw.splitlines()
 if len(jobs)!=199 or len(lines)!=199 or raw!=b'\n'.join(lines)+b'\n':raise E('cardinality')
 rows=[json.loads(x) for x in lines];ad=load('oolong_score_adapter',AD)
 for i,(j,r) in enumerate(zip(jobs,rows),1):
  for k in ('fixture_id','payload_sha256','context_len','dataset','task_group'):
   if r.get(k)!=j.get(k):raise E(f'row {i} {k}')
  if r.get('execution_ordinal')!=i or r.get('schedule_id')!=sid or r.get('benchmark')!='rah199' or r.get('reasoning')!='low' or r.get('fresh_session') is not True or r.get('serial') is not True:raise E(f'row {i} binding')
  cleanup=r.get('credential_cleanup_assertion',{});leak=r.get('root_context_leak_assertion',{})
  if cleanup.get('asserted') is not True or cleanup.get('credential_homes_deleted') is not True or r.get('cleanup_errors')!=[]:raise E(f'row {i} cleanup')
  if leak.get('applicable') is not True or leak.get('leak_detected') is not False or leak.get('scan_complete') is not True:raise E(f'row {i} leak')
  if r.get('execution_success'):
   if r.get('failure') is not None or r.get('exit_code')!=0 or r.get('timed_out') is not False:raise E(f'row {i} success')
   route=r.get('runtime_route_assertion',{})
   if route.get('asserted') is not True or route.get('expected_model')!='gpt-5.6-luna':raise E(f'row {i} route')
   stdout=r.get('trajectory_artifacts',{}).get('stdout');p=Path(stdout.get('path','')) if isinstance(stdout,dict) else Path('');expected=WORK/f'r001-{i:03d}-jcode-azdaja'/'stdout.ndjson'
   if p!=expected or sha(p)!=stdout.get('sha256') or p.stat().st_size!=stdout.get('bytes') or stat.S_IMODE(p.stat().st_mode)!=0o600:raise E(f'row {i} stdout')
   if ad.extract_final_exact('jcode-azdaja',p.read_text())!=r.get('response'):raise E(f'row {i} response')
  elif not isinstance(r.get('failure'),dict):raise E(f'row {i} failure')
 comp,cb=rj(COMPLETION)
 if comp!={'schema_version':1,'record_type':'rah199_completion','schedule_id':sid,'rows':199,'results_sha256':shab(raw)}:raise E('completion')
 return sched,sb,jobs,rows,raw,cb
def requested_field(q):
 x=re.findall(r"(?i)form\s+['\"]([A-Za-z][A-Za-z0-9_-]*)\s*:",q);return x[-1].capitalize() if x else None
def gold_value(raw):
 v=ast.literal_eval(raw)
 if not isinstance(v,list) or len(v)!=1 or not (type(v[0]) is int or isinstance(v[0],str)):raise E('unsupported gold')
 return v[0]
def prediction(response,kind,gold):
 m=re.fullmatch(re.escape(kind)+r': ([^\r\n]+)\n?',response)
 if not m:return None
 s=m.group(1)
 if type(gold) is int:return int(s) if re.fullmatch(r'[0-9]+',s) else None
 return s
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--validate-no-gold',action='store_true');g.add_argument('--yes-score-once',action='store_true');a=p.parse_args();sched,sb,jobs,rows,raw,cb=validate()
 if a.validate_no_gold:
  print(json.dumps({'status':'valid-no-gold','rows':199,'execution_success':sum(r.get('execution_success') is True for r in rows)},sort_keys=True));return
 if OUTPUT.exists() or CONSUMED.exists():raise E('scoring consumed')
 fd=os.open(CONSUMED,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,canon({'results_sha256':shab(raw),'source_parquet_sha256':{p.name:sha(p) for p in sorted(SOURCE.glob('*.parquet'))}}));os.fsync(fd);os.close(fd)
 import pyarrow.parquet as pq
 answers={}
 for pth in sorted(SOURCE.glob('*.parquet')):
  for x in pq.read_table(pth,columns=['id','answer']).to_pylist():answers[x['id']]=x['answer']
 manifest=json.loads((PUBLIC/'manifest.json').read_text());by={x['fixture_id']:x for x in manifest['fixtures']};scored=[]
 for j,r in zip(jobs,rows):
  x=by[j['fixture_id']];meta=json.loads((PUBLIC/x['row']).read_text());gold=gold_value(answers[meta['id']]);kind=requested_field(meta['question']) or ('Answer' if type(gold) is int else 'Label');pred=prediction(r.get('response','') if r.get('execution_success') else '',kind,gold);exact=pred==gold;official=(0.75**abs(gold-pred)) if type(gold) is int and type(pred) is int else (1.0 if exact else 0.0);use=r.get('azdaja_model_usage') or {}
  scored.append({'fixture_id':j['fixture_id'],'context_len':j['context_len'],'dataset':j['dataset'],'task_group':j['task_group'],'execution_success':r.get('execution_success') is True,'valid_prediction':pred is not None,'strict_exact':exact,'official_score':official,'latency_seconds':r.get('latency_seconds'),'root_total_tokens':use.get('total_tokens')})
 lat=[x['latency_seconds'] for x in scored if isinstance(x['latency_seconds'],(int,float))];lengths=sorted({x['context_len'] for x in scored});by_length=[{'context_len':L,'n':sum(x['context_len']==L for x in scored),'mean_official_score':sum(x['official_score'] for x in scored if x['context_len']==L)/sum(x['context_len']==L for x in scored)} for L in lengths];report={'schema_version':1,'record_type':'rah199_score','formula':'numeric: 0.75 ** abs(y-y_hat); categorical: exact; failure/invalid: 0','parser':'preregistered canonical one-line Answer/Label parser','schedule_id':sched['schedule_id'],'fixed_denominator_n':199,'execution_success_n':sum(x['execution_success'] for x in scored),'valid_prediction_n':sum(x['valid_prediction'] for x in scored),'strict_exact_n':sum(x['strict_exact'] for x in scored),'official_mean_score':sum(x['official_score'] for x in scored)/199,'official_score_percent':100*sum(x['official_score'] for x in scored)/199,'median_latency_seconds_all_attempts':statistics.median(lat),'zero_root_context_leaks':True,'equal_weight_length_bucket_macro':sum(x['mean_official_score'] for x in by_length)/len(by_length),'by_length':by_length,'rows':scored,'inputs':{'public_manifest_sha256':sha(PUBLIC/'manifest.json'),'schedule_sha256':shab(sb),'results_sha256':shab(raw),'completion_sha256':shab(cb),'scorer_sha256':sha(Path(__file__).resolve())}}
 fd=os.open(OUTPUT,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,canon(report));os.fsync(fd);os.close(fd);print(str(OUTPUT))
if __name__=='__main__':
 try:main()
 except Exception as e:print(f'score error: {type(e).__name__}: {e}',file=sys.stderr);raise SystemExit(2)
