#!/usr/bin/env python3
import collections,hashlib,json,math,os,pathlib
import pyarrow.parquet as pq
SRC=pathlib.Path('/private/tmp/azdaja-oolong-source-fb1ycbh1');OUT=pathlib.Path('/private/tmp/azdaja-rah199-69dxj70n/public');REV='f0d59eaf0febf130664cfceb710436c8e3216b2b';BEACON='71ae91a73e70ffe6a3af9d0aa0e5a007d27a70080bf66d3b2039cca4cde87eb9';PREFIX=b"oolong-rah-v1\0";BLACK={('spam',131072,10004):'05e4419a7280c91b3bbf1ea97629bfc235ee0eb23e67e1f0eeb21fc38b485bf2',('spam',1048576,10012):'78e61364029606a211e8d6fced3fefea42f37651bc2c4b84ef54856e1e70f4fe'}
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def H(tag,value):return hashlib.sha256(PREFIX+REV.encode()+b'\0'+BEACON.encode()+b'\0'+tag.encode()+b'\0'+str(value).encode()).hexdigest()
def create(p,b):fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,b);os.fsync(fd);os.close(fd)
struct=['id','context_len','dataset','task_group','task','answer_type','input_subset','num_labels','context_window_id'];rows=[];shards=[]
for p in sorted(SRC.glob('*.parquet')):
 b=p.read_bytes();shards.append({'file':p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});rows+=pq.read_table(p,columns=struct).to_pylist()
if len(rows)!=1300 or len({r['id'] for r in rows})!=1300:raise SystemExit('source cardinality')
lengths=sorted({r['context_len'] for r in rows});expected=[2**x for x in range(10,23)]
if lengths!=expected:raise SystemExit(('lengths',lengths))
for L in lengths:
 if sum(r['context_len']==L for r in rows)!=100:raise SystemExit(('length count',L))
 for D in ('spam','trec_coarse'):
  cell=[r for r in rows if r['context_len']==L and r['dataset']==D]
  if len(cell)!=50 or len({r['context_window_id'] for r in cell})!=2:raise SystemExit(('cell',L,D))
excluded=[r for r in rows if (r['dataset'],r['context_len'],r['context_window_id']) in BLACK]
if len(excluded)!=50 or len({(r['dataset'],r['context_len'],r['context_window_id']) for r in excluded})!=2:raise SystemExit('blacklist')
elig=[r for r in rows if r not in excluded]
len_rank=sorted(lengths,key=lambda x:H('length',x));lquota={L:(16 if L in len_rank[:4] else 15) for L in lengths};datasets=sorted(['spam','trec_coarse'],key=lambda x:H('dataset',x));hundred=datasets[0];other=datasets[1];odd=sorted([L for L in lengths if lquota[L]==15],key=lambda x:H('odd-length',x));quota={}
for L in lengths:
 if lquota[L]==16:quota[(L,hundred)]=8;quota[(L,other)]=8
 elif L in odd[:5]:quota[(L,hundred)]=8;quota[(L,other)]=7
 else:quota[(L,hundred)]=7;quota[(L,other)]=8
if sum(quota.values())!=199 or sum(v for (L,D),v in quota.items() if D==hundred)!=100:raise SystemExit('quota')
selected=[];apportion=[]
for L in lengths:
 for D in datasets:
  pool=[r for r in elig if r['context_len']==L and r['dataset']==D];q=quota[(L,D)];groups=collections.defaultdict(list)
  for r in pool:groups[(r['task_group'],r['task'],r['answer_type'])].append(r)
  N=len(pool);alloc={};rema=[]
  for st,rs in groups.items():
   exact=q*len(rs)/N;base=math.floor(exact);alloc[st]=base;rema.append((-(exact-base),H('stratum',json.dumps(st,separators=(',',':'))),st))
  for _,_,st in sorted(rema)[:q-sum(alloc.values())]:alloc[st]+=1
  for st,n in alloc.items():selected+=sorted(groups[st],key=lambda r:H('row',r['id']))[:n]
  apportion.append({'context_len':L,'dataset':D,'eligible_n':N,'selected_n':q,'strata':[{'task_group':s[0],'task':s[1],'answer_type':s[2],'eligible_n':len(groups[s]),'selected_n':alloc[s]} for s in sorted(groups)]})
if len(selected)!=199 or len({r['id'] for r in selected})!=199:raise SystemExit('selected')
selids={r['id'] for r in selected};blackids={r['id'] for r in excluded};payload={};blackctx={}
for p in sorted(SRC.glob('*.parquet')):
 pf=pq.ParquetFile(p)
 for rg in range(pf.metadata.num_row_groups):
  tab=pf.read_row_group(rg,columns=['id','context_window_text','question']).to_pylist()
  for x in tab:
   if x['id'] in selids:payload[x['id']]=x
   if x['id'] in blackids:
    h=hashlib.sha256(x['context_window_text'].encode()).hexdigest();blackctx[x['id']]=h
for key,want in BLACK.items():
 ids={r['id'] for r in excluded if (r['dataset'],r['context_len'],r['context_window_id'])==key}
 if {blackctx[i] for i in ids}!={want}:raise SystemExit(('blacklist hash',key))
fixtures=[];ctx_written={}
for r in sorted(selected,key=lambda r:r['id']):
 x=payload[r['id']];text=x['context_window_text'];cb=text.encode();ch=hashlib.sha256(cb).hexdigest();cname=f'context-{ch}.txt'
 if ch not in ctx_written:create(OUT/cname,cb);ctx_written[ch]=cname
 meta={k:r[k] for k in struct};meta.update(source='oolongbench/oolong-synth',split='validation',dataset_revision=REV,question=x['question'],context_file=cname,context_sha256=ch,context_bytes=len(cb),context_chars=len(text),context_lines=len(text.splitlines()))
 fid=f"rah-{r['id']}";data=canon(meta);create(OUT/(fid+'.json'),data);fixtures.append({'fixture_id':fid,'id':r['id'],'row':fid+'.json','row_sha256':hashlib.sha256(data).hexdigest(),'context':cname,'context_sha256':ch,'context_len':r['context_len'],'dataset':r['dataset'],'task_group':r['task_group'],'task':r['task'],'answer_type':r['answer_type']})
audit={'schema_version':1,'record_type':'rah199_selection_audit','claim_scope':'preregistered validation-derived subset, not official full OOLONG','dataset_revision':REV,'beacon_kind':'completed same-binary OOLONG results SHA-256','beacon':BEACON,'hash_domain':'oolong-rah-v1\0','source_shards':shards,'source_invariants':{'rows':1300,'lengths':lengths,'per_length':100,'per_dataset_length':50},'exclusion':{'exact_composites':[list(k) for k in BLACK],'context_hashes':list(BLACK.values()),'removed_rows':50,'removed_windows':2},'length_quotas':{str(k):v for k,v in lquota.items()},'dataset_totals':{d:sum(q for (L,x),q in quota.items() if x==d) for d in datasets},'apportionment':apportion,'selected_ids':[r['id'] for r in sorted(selected,key=lambda r:r['id'])],'selected_n':199,'gold_fields_deserialized':False,'context_window_text_with_labels_deserialized':False}
adata=canon(audit);create(OUT/'selection-audit.json',adata)
manifest={'schema_version':1,'record_type':'rah199_public_manifest','claim_scope':'preregistered validation-derived subset, not official full OOLONG','source':'oolongbench/oolong-synth','split':'validation','dataset_revision':REV,'gold_in_public':False,'selection_audit_sha256':hashlib.sha256(adata).hexdigest(),'fixture_n':199,'unique_context_n':len(ctx_written),'fixtures':fixtures};mdata=canon(manifest);create(OUT/'manifest.json',mdata)
print(json.dumps({'selected_n':199,'unique_context_n':len(ctx_written),'manifest_sha256':hashlib.sha256(mdata).hexdigest(),'selection_audit_sha256':hashlib.sha256(adata).hexdigest(),'length_quotas':lquota,'dataset_totals':audit['dataset_totals']},sort_keys=True))
