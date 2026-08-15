#!/usr/bin/env python3
import hashlib,importlib.util,json,os,sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path('/private/tmp/azdaja-rah199-69dxj70n');PUBLIC=ROOT/'public';AD=Path('/Users/vukasinkubet/dev/azdaja/bench/oolong/run.py');SKILL=Path('/private/tmp/azdaja-querycap-ruler10-diff-4mkappao/candidates/querycap512');J=Path.home()/'.jcode/builds/versions/0.75.3/jcode';MODEL='gpt-5.6-luna';REASONING='low'
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def create(p,b):fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,b);os.fsync(fd);os.close(fd)
def append(p,x):fd=os.open(p,os.O_WRONLY|os.O_APPEND);os.write(fd,canon(x));os.fsync(fd);os.close(fd)
def main():
 ad=load('rah199_adapter',AD);ad.MODEL=MODEL;ad.REASONING=REASONING;skill=ad.validate_skill(str(SKILL));sched=json.loads((ROOT/'output/schedule.json').read_text());ident=dict(sched);sid=ident.pop('schedule_id')
 if hashlib.sha256(canon(ident)).hexdigest()!=sid or sched['total_jobs']!=199 or sched['public_manifest_sha256']!=sha(PUBLIC/'manifest.json') or sched['scorer_sha256']!=sha(ROOT/'score_once.py'):raise RuntimeError('frozen schedule mismatch')
 manifest=json.loads((PUBLIC/'manifest.json').read_text());by={x['fixture_id']:x for x in manifest['fixtures']};candidate=ad.skill_component_hashes(skill);candidate['binary_identity']=ad.executable_identity(str(skill/'azdaja'),'azdaja')
 if candidate!=sched['candidate']:raise RuntimeError('candidate mismatch')
 jident=ad.executable_identity(str(J.resolve()),'jcode');auth=ad.preflight_jcode(Path.home(),str(J.resolve()))
 if jident!=sched['jcode']:raise RuntimeError('jcode mismatch')
 out=ROOT/'output/results.jsonl';create(out,b'')
 for job in sched['jobs']:
  x=by[job['fixture_id']];meta=json.loads((PUBLIC/x['row']).read_text());cp=PUBLIC/x['context'];text=cp.read_text();fixture=SimpleNamespace(row_path=PUBLIC/x['row'],context_path=cp,metadata=meta,expected_kind=None,expected_value=None,expected_canonical=None,row_sha256=x['row_sha256'],context_sha256=x['context_sha256'],context_bytes=cp.stat().st_size,context_chars=len(text),context_lines=len(text.splitlines()))
  args=SimpleNamespace(timeout=sched['timeout_seconds'],seed=sched['seed'],jcode=str(J.resolve()),prime_agent='prime-agent',executable_identities={'jcode':jident,'azdaja':candidate['binary_identity']},oolong_private_frozen_suite=True)
  row=ad.run_one(arm_name='jcode-azdaja',repetition=1,ordinal=job['ordinal'],fixture=fixture,prompt=None,args=args,root=Path('/'),source_home=Path.home(),skill=skill,auth_jcode=auth,auth_prime={},work_root=ROOT/'work',defer_scoring=True,return_exact_response=True);row['response']=row.pop('_exact_response');row.update({'benchmark':'rah199','fixture_id':x['fixture_id'],'id':x['id'],'payload_sha256':x['context_sha256'],'context_len':x['context_len'],'dataset':x['dataset'],'task_group':x['task_group'],'task':x['task'],'answer_type':x['answer_type'],'schedule_id':sid,'candidate_identity':candidate});append(out,row);print(json.dumps({'ordinal':job['ordinal'],'fixture_id':x['fixture_id'],'context_len':x['context_len'],'execution_success':row['execution_success'],'latency_seconds':row['latency_seconds']},sort_keys=True),flush=True)
 comp={'schema_version':1,'record_type':'rah199_completion','schedule_id':sid,'rows':199,'results_sha256':sha(out)};create(ROOT/'output/completion.json',canon(comp));print(json.dumps(comp,sort_keys=True))
if __name__=='__main__':main()
