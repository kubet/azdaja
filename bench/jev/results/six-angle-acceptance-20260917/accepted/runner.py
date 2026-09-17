import hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
ROOT=Path('/Users/vukasinkubet/dev/azdaja')
S=Path(os.environ['JCODE_SCRATCH_DIR'])
PRIOR=S/'jev-angle-final-acceptance-20260917-1110'
OUT=S/'jev-angle-final-acceptance-20260917-1121'
OUT.mkdir(exist_ok=False)
SOURCE=PRIOR/'source'
TARGET=S/'azdaja-notice-remediation-20260917/target'
HEAD='e75d83660660e5e9fb199a3c00a7c5905df42f5b'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip()==HEAD
assert not subprocess.check_output(['git','status','--porcelain'],cwd=SOURCE,text=True).strip()
raw=(PRIOR/'receipt.json').read_bytes()
previous=json.loads(raw)
assert previous['source_commit']==HEAD and len(previous['checks'])==18
carried=[]
for check in previous['checks'][:-1]:
 assert check['status']=='passed' and check['exit']==0
 body=(PRIOR/(check['name']+'.log')).read_bytes()
 assert len(body)==check['log_bytes'] and hashlib.sha256(body).hexdigest()==check['log_sha256']
 carried.append(dict(check,observed_in_prior_run=PRIOR.name))
assert previous['checks'][-1]['name']=='all-targets-all-features' and previous['checks'][-1]['status']=='running'
ENV=dict(os.environ,CARGO_TARGET_DIR=str(TARGET),CARGO_NET_OFFLINE='true',RUSTUP_TOOLCHAIN='1.95.0',PYTHONDONTWRITEBYTECODE='1')
for key in list(ENV):
 if any(part in key.upper() for part in ('API_KEY','TOKEN','SECRET','PASSWORD')): ENV.pop(key,None)
ENV.pop('AZDAJA_CONFIG',None)
ENV['AZDAJA_HOME']=str(OUT/'acceptance-state-with-no-key')
record={'schema':'azdaja.final_source_followthrough.v1','source_commit':HEAD,'source_tree_clean':True,'live_provider_calls':0,'status':'running','checks':carried,'published_assets_modified':False,'publication_authorized':False,'default_capabilities':previous['default_capabilities'],'interrupted_predecessor':{'path':PRIOR.name,'receipt_sha256':hashlib.sha256(raw).hexdigest(),'tool_task':'4050589vvg','exit':124,'reason':'outer command deadline at600seconds; full suite incomplete; completed checks validated before carry'}}

def checkpoint():
 (OUT/'receipt.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')

def run(name,argv,env=None,cwd=SOURCE):
 start=time.monotonic();event={'name':name,'argv':argv,'status':'running'};record['checks'].append(event);checkpoint()
 print('JCODE_PROGRESS '+json.dumps({'message':'Running '+name,'kind':'checkpoint'}),flush=True)
 path=OUT/(name+'.log')
 with path.open('x') as log:
  p=subprocess.Popen(argv,cwd=cwd,env=env or ENV,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  for line in p.stdout:
   log.write(line);log.flush()
   if line.startswith('test result:'):
    print('JCODE_PROGRESS '+json.dumps({'message':name+': '+line.strip(),'kind':'checkpoint'}),flush=True)
  code=p.wait()
 raw=path.read_bytes();text=raw.decode(errors='replace')
 event.update(exit=code,seconds=time.monotonic()-start,status='passed' if code==0 else 'failed',log_sha256=hashlib.sha256(raw).hexdigest(),log_bytes=len(raw))
 counts=re.findall(r'test result: (?:ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored',text)
 if counts:event['rust_counts']=[{'passed':int(a),'failed':int(b),'ignored':int(c)} for a,b,c in counts]
 checkpoint()
 if code:raise RuntimeError(name+' failed with '+str(code))
 print('JCODE_PROGRESS '+json.dumps({'message':'Passed '+name,'kind':'checkpoint'}),flush=True)
 return text

try:
 run('all-targets-all-features',['cargo','+1.95.0','test','--locked','--offline','--all-targets','--all-features','--no-fail-fast'])
 run('final-feature-build',['cargo','+1.95.0','build','--locked','--offline','--all-features','--bin','azdaja'])
 binary=TARGET/'debug/azdaja'
 record['final_binary_sha256']=hashlib.sha256(binary.read_bytes()).hexdigest()
 home=OUT/'private home with spaces';home.mkdir()
 private=dict(ENV,HOME=str(home),AZDAJA_HOME=str(OUT/'private-state'))
 for key in ('XDG_CONFIG_HOME','XDG_STATE_HOME','XDG_DATA_HOME','AZDAJA_CLAUDE_ACTIVATION','AZDAJA_JCODE_ACTIVATION','RLM_DEPTH','CLAUDE_PLUGIN_ROOT'):
  private.pop(key,None)
 run('private-install',[str(binary),'install','claude'],private)
 installed=home/'.claude/skills/azdaja/azdaja'
 assert installed.is_file() and hashlib.sha256(installed.read_bytes()).hexdigest()==record['final_binary_sha256']
 record['actual_installed_binary_sha256']=hashlib.sha256(installed.read_bytes()).hexdigest()
 run('private-doctor',[str(installed),'doctor','claude'],private)
 installed_caps=json.loads(run('installed-capabilities',[str(installed),'doctor','--caps'],private))
 assert installed_caps['typed_judgments']['typesafe_compiled'] is True
 assert installed_caps['typed_judgments']['runtime_configuration_checked'] is False
 assert installed_caps['typed_judgments']['credentials_checked'] is False
 record['installed_capabilities']=installed_caps
 run('installed-offline-span',['python3','-B','-m','bench.jev.span_selection.run','--offline','--azdaja',str(installed),'--scratch',str(OUT),'--output',str(OUT/'installed-span-offline')],private)
 testenv=dict(ENV,AZDAJA_BINARY=str(installed),AZDAJA_INSTALLED_TEST_BINARY=str(installed),AZDAJA_ANGLE_BINARY=str(installed))
 run('installed-angle-packs-and-continuation',['python3','-B','-m','unittest','bench.jev.angle_lab.test_native','bench.jev.angle_lab.test_lanes','bench.jev.angle_followthrough.test_run','-v'],testenv)
 run('installed-native-and-result-tests',['python3','-B','-m','unittest','bench.jev.span_selection.test_kernel','bench.jev.span_selection.test_runner','bench.jev.span_selection.test_replay','-v'],testenv)
 run('installed-memory',['cargo','+1.95.0','test','--locked','--offline','--features','typesafe','--test','installed_project_memory','--','--ignored','--test-threads=1'],testenv)
 run('private-uninstall',[str(installed),'uninstall','claude'],private)
 assert not installed.exists()
 record['private_install_removed']=True
 record['source_tree_clean_after']=not bool(subprocess.check_output(['git','status','--porcelain'],cwd=SOURCE,text=True).strip())
 assert record['source_tree_clean_after']
 record['status']='passed'
except BaseException as e:
 record['status']='failed';record['failure']=str(e)
 checkpoint()
 raise
checkpoint()
print(json.dumps({'status':record['status'],'source_commit':HEAD,'checks':len(record['checks']),'binary_sha256':record.get('final_binary_sha256'),'publication_authorized':False}),flush=True)
