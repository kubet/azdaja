#!/usr/bin/env python3
from __future__ import annotations
import argparse,ast,hashlib,importlib.util,json,os,stat,statistics,sys
from datetime import datetime
from pathlib import Path
import numpy as np
from dateutil import parser as date_parser

PROD_ROOT=Path('/private/tmp/azdaja-rah199-69dxj70n')
PROD_SOURCE=Path('/private/tmp/azdaja-oolong-source-fb1ycbh1')
ADAPTER=Path('/Users/vukasinkubet/dev/azdaja/bench/oolong/run.py')
MODEL='gpt-5.6-luna';EXPECTED=199
FROZEN_SCORER_SHA='1f88500c5b76d2d60edd97ce72d742cc323b5704c7af9096a1721f3baf298353'
BOOTSTRAP_REPLICATES=100000
class E(RuntimeError):pass
def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def shab(b):return hashlib.sha256(b).hexdigest()
def sha(p):return shab(p.read_bytes())
def create(p,b):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 try:os.write(fd,b);os.fsync(fd)
 finally:os.close(fd)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def read_json(p):
 b=p.read_bytes();v=json.loads(b)
 if b!=canon(v):raise E(f'noncanonical {p.name}')
 return v,b
def paths(root,source,rehearsal):
 return {'root':root,'source':source,'public':root/'public','schedule':root/'output/schedule.json','results':root/'output/results.jsonl','completion':root/'output/completion.json','work':root/'work','output':root/('output/scores.rehearsal.json' if rehearsal else 'output/scores.repaired.json'),'consumed':root/('output/gold.rehearsal.consumed' if rehearsal else 'output/gold.repaired-score.consumed')}
def validate(p):
 sched,sb=read_json(p['schedule']);ident=dict(sched);sid=ident.pop('schedule_id')
 if sid!=shab(canon(ident)) or sched.get('total_jobs')!=EXPECTED or sched.get('arm')!='jcode-azdaja' or sched.get('reasoning')!='low' or sched.get('scorer_sha256')!=FROZEN_SCORER_SHA:raise E('schedule')
 jobs=sched.get('jobs');raw=p['results'].read_bytes();lines=raw.splitlines()
 if len(jobs)!=EXPECTED or len(lines)!=EXPECTED or raw!=b'\n'.join(lines)+b'\n':raise E('cardinality')
 rows=[json.loads(x) for x in lines];ad=load('rah_repaired_score_adapter',ADAPTER)
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
   if route.get('asserted') is not True or route.get('expected_model')!=MODEL:raise E(f'row {i} route')
   stdout=r.get('trajectory_artifacts',{}).get('stdout');q=Path(stdout.get('path','')) if isinstance(stdout,dict) else Path('');expected=p['work']/f'r001-{i:03d}-jcode-azdaja'/'stdout.ndjson'
   if q!=expected or sha(q)!=stdout.get('sha256') or q.stat().st_size!=stdout.get('bytes') or stat.S_IMODE(q.stat().st_mode)!=0o600:raise E(f'row {i} stdout')
   if ad.extract_final_exact('jcode-azdaja',q.read_text())!=r.get('response'):raise E(f'row {i} response')
  elif not isinstance(r.get('failure'),dict):raise E(f'row {i} failure')
 comp,cb=read_json(p['completion'])
 if comp!={'schema_version':1,'record_type':'rah199_completion','schedule_id':sid,'rows':EXPECTED,'results_sha256':shab(raw)}:raise E('completion')
 manifest=json.loads((p['public']/'manifest.json').read_text());fixtures=manifest.get('fixtures')
 if not isinstance(fixtures,list) or len(fixtures)!=EXPECTED or len({x.get('fixture_id') for x in fixtures})!=EXPECTED:raise E('manifest')
 return sched,sb,jobs,rows,raw,cb,manifest
def official_gold(raw):
 if not isinstance(raw,str):raise E('gold answer must be string')
 if 'datetime' in raw:
  try:return datetime.strptime(raw,'[datetime.date(%Y, %m, %d)]')
  except ValueError as e:raise E('unsupported datetime gold') from e
 try:v=ast.literal_eval(raw)
 except (SyntaxError,ValueError) as e:raise E('unsupported literal gold') from e
 if not isinstance(v,list) or not v:raise E('unsupported gold container')
 g=v[0]
 if type(g) is int or isinstance(g,str):return g
 raise E('unsupported gold value')
def attempt_parse(answer):
 confidence='low'
 if ':' not in answer:
  return (answer if len(answer)<20 else answer.split()[-1]),confidence
 candidate=answer.split(':')[-1].strip().replace('*','').replace('[','').replace(']','');confidence='med'
 if 'User:' in answer or 'Answer:' in answer or 'Date:' in answer or 'Label' in answer:confidence='high'
 if len(candidate)<20:confidence='vhigh'
 elif 'more common' in candidate:candidate='more common'
 elif 'less common' in candidate:candidate='less common'
 elif 'same frequency' in candidate:candidate='same frequency'
 return candidate,confidence
def official_score(raw_gold,answer_type,response):
 gold=official_gold(raw_gold);trimmed,confidence=attempt_parse(response);score=0.0;valid=bool(str(trimmed).strip())
 if str(trimmed)==str(gold):score=1.0
 elif str(trimmed) in ('more common','less common','same frequency') and str(trimmed) in str(gold):score=1.0
 elif answer_type=='ANSWER_TYPE.NUMERIC':
  try:score=0.75**abs(int(gold)-int(trimmed))
  except Exception:valid=False;confidence='low'
 elif answer_type=='ANSWER_TYPE.DATE':
  try:score=float(date_parser.parse(str(trimmed))==gold)
  except Exception:valid=False;confidence='low'
 return float(score),valid,confidence
def bootstrap_ci(values,seed,reps=BOOTSTRAP_REPLICATES):
 a=np.asarray(values,dtype=np.float64)
 if not len(a):raise E('empty bootstrap')
 rng=np.random.Generator(np.random.PCG64(seed));out=np.empty(reps,dtype=np.float64);step=5000
 for start in range(0,reps,step):
  n=min(step,reps-start);out[start:start+n]=a[rng.integers(0,len(a),size=(n,len(a)))].mean(axis=1)
 lo,hi=np.quantile(out,[0.025,0.975]);return {'method':'deterministic nonparametric percentile bootstrap over fixed-denominator items','replicates':reps,'seed':seed,'low':float(lo),'high':float(hi)}
def macro_bootstrap(by_length,seed,reps=BOOTSTRAP_REPLICATES):
 arrays=[np.asarray(v,dtype=np.float64) for _,v in sorted(by_length.items())];rng=np.random.Generator(np.random.PCG64(seed));out=np.empty(reps,dtype=np.float64);step=5000
 for start in range(0,reps,step):
  n=min(step,reps-start);total=np.zeros(n,dtype=np.float64)
  for a in arrays:total+=a[rng.integers(0,len(a),size=(n,len(a)))].mean(axis=1)
  out[start:start+n]=total/len(arrays)
 lo,hi=np.quantile(out,[0.025,0.975]);return {'method':'deterministic stratified percentile bootstrap within each length bucket','replicates':reps,'seed':seed,'low':float(lo),'high':float(hi)}
def score_once(p,rehearsal,sched,sb,jobs,rows,raw,cb,manifest):
 if p['output'].exists() or p['consumed'].exists():raise E('repaired scoring already consumed')
 sources=sorted(p['source'].glob('*.parquet'))
 if not sources:raise E('source parquet absent')
 create(p['consumed'],canon({'authorization':'owner override permits retained-transcript rescore after scorer-only failure','results_sha256':shab(raw),'source_parquet_sha256':{q.name:sha(q) for q in sources}}))
 import pyarrow.parquet as pq
 answers={}
 for q in sources:
  for x in pq.read_table(q,columns=['id','answer']).to_pylist():answers[x['id']]=x['answer']
 by_fixture={x['fixture_id']:x for x in manifest['fixtures']};scored=[]
 for j,r in zip(jobs,rows):
  x=by_fixture[j['fixture_id']];meta=json.loads((p['public']/x['row']).read_text());rid=meta['id']
  if rid not in answers:raise E('selected gold id absent')
  response=r.get('response','') if r.get('execution_success') else ''
  value,valid,confidence=official_score(answers[rid],meta['answer_type'],response)
  scored.append({'fixture_id':j['fixture_id'],'context_len':j['context_len'],'dataset':j['dataset'],'task_group':j['task_group'],'execution_success':r.get('execution_success') is True,'valid_prediction':valid,'parse_confidence':confidence,'official_score':value,'latency_seconds':r.get('latency_seconds')})
 lengths=sorted({x['context_len'] for x in scored});by_length={L:[x['official_score'] for x in scored if x['context_len']==L] for L in lengths};seed=int(shab(raw)[:16],16);bucket=[]
 for L in lengths:
  v=[x for x in scored if x['context_len']==L];vals=by_length[L];bucket.append({'context_len':L,'n':len(v),'execution_success_n':sum(x['execution_success'] for x in v),'valid_prediction_n':sum(x['valid_prediction'] for x in v),'mean_official_score':sum(vals)/len(vals),'score_percent':100*sum(vals)/len(vals),'ci95':bootstrap_ci(vals,seed^L)})
 vals=[x['official_score'] for x in scored];micro=sum(vals)/len(vals);macro=sum(x['mean_official_score'] for x in bucket)/len(bucket)
 report={'schema_version':1,'record_type':'rah199_repaired_score_rehearsal' if rehearsal else 'rah199_repaired_score','claim_scope':'synthetic exact-format rehearsal' if rehearsal else 'preregistered validation-derived subset, not official full OOLONG','schedule_id':sched['schedule_id'],'fixed_denominator_n':EXPECTED,'execution_success_n':sum(x['execution_success'] for x in scored),'valid_prediction_n':sum(x['valid_prediction'] for x in scored),'official_mean_score':micro,'official_score_percent':100*micro,'official_mean_ci95':bootstrap_ci(vals,seed),'equal_weight_length_bucket_macro':macro,'equal_weight_length_bucket_macro_percent':100*macro,'equal_weight_length_bucket_macro_ci95':macro_bootstrap(by_length,seed^0x524148),'by_length':bucket,'formula':'numeric: 0.75 ** abs(y-y_hat); categorical/comparison/date: official released scorer semantics; invalid/failure: 0','parser_source':{'url':'https://github.com/abertsch72/oolong/blob/0bb7eabe839218fee7fe8d007f41cfc2fd3ae24c/src/eval/eval_helpers.py','sha256':'247583a3b653b91c39fb88a102460802f1493175b23d05a7217aead0d685c64c'},'bootstrap':{'replicates':BOOTSTRAP_REPLICATES,'base_seed':seed},'rows':scored,'inputs':{'public_manifest_sha256':sha(p['public']/'manifest.json'),'schedule_sha256':shab(sb),'results_sha256':shab(raw),'completion_sha256':shab(cb),'repaired_scorer_sha256':sha(Path(__file__).resolve()),'frozen_failed_scorer_sha256':FROZEN_SCORER_SHA,'consumed_sentinel_sha256':sha(p['consumed'])}}
 create(p['output'],canon(report));print(str(p['output']))
def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--validate-no-gold',action='store_true');g.add_argument('--yes-score-repaired-once',action='store_true');ap.add_argument('--rehearsal-root',type=Path);ap.add_argument('--rehearsal-source',type=Path);a=ap.parse_args();rehearsal=a.rehearsal_root is not None or a.rehearsal_source is not None
 if rehearsal and (a.rehearsal_root is None or a.rehearsal_source is None):raise E('both rehearsal paths required')
 p=paths(a.rehearsal_root if rehearsal else PROD_ROOT,a.rehearsal_source if rehearsal else PROD_SOURCE,rehearsal);data=validate(p)
 if a.validate_no_gold:
  print(json.dumps({'status':'valid-no-gold','rehearsal':rehearsal,'rows':EXPECTED,'execution_success':sum(r.get('execution_success') is True for r in data[3])},sort_keys=True));return
 score_once(p,rehearsal,*data)
if __name__=='__main__':
 try:main()
 except Exception as e:print(f'score error: {type(e).__name__}: {e}',file=sys.stderr);raise SystemExit(2)
