#!/usr/bin/env python3
"""Serial, low-load snapshot benchmark. Writes JSON; makes no model calls."""
import argparse,json,os,re,statistics,subprocess,tempfile,time,platform,math
from pathlib import Path

def timed(cmd,env,stdin=b""):
    full=["/usr/bin/time","-l",*cmd] if Path("/usr/bin/time").exists() and platform.system()=="Darwin" else cmd
    t=time.perf_counter();p=subprocess.run(full,input=stdin,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env);wall=(time.perf_counter()-t)*1000
    if p.returncode: raise RuntimeError(f"{cmd}: {p.stderr.decode(errors='replace')}")
    m=re.search(rb"(\d+)\s+maximum resident set size",p.stderr)
    return wall,int(m.group(1)) if m else None,p.stdout.decode()
def pct(v,p): return sorted(v)[min(len(v)-1,max(0,math.ceil(len(v)*p)-1))]
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--binary",default="target/release/azdaja");ap.add_argument("--sizes-mb",default="1,10,100");ap.add_argument("--repeats",type=int,default=5);ap.add_argument("--output");a=ap.parse_args();binary=str(Path(a.binary).resolve());rows=[]
    with tempfile.TemporaryDirectory(prefix="azdaja-bench-") as td:
      td=Path(td);cfg=td/"config.toml";cfg.write_text("sub_llm_cmd=\"cat\"\ndefault_model=\"mock\"\noutput_cap=8192\nmax_depth=1\nsub_timeout=2\nmax_sessions=4\ncell_timeout=30\nidle_timeout=1800\nclean_patterns=[]\n");env=os.environ|{"AZDAJA_HOME":str(td/"state"),"AZDAJA_CONFIG":str(cfg)}
      for mb in map(int,a.sizes_mb.split(",")):
        f=td/f"{mb}mb.txt";f.write_bytes(b"x"*(mb*1_000_000));loads=[];execs=[];py=[];rss=[];snap=[]
        for _ in range(a.repeats):
          _,r,sid=timed([binary,"start"],env);sid=sid.strip();w,r,_=timed([binary,"load",sid,str(f),"ctx"],env);loads.append(w);rss.append(r);snap.append((td/"state"/sid/"state.monty").stat().st_size);w,r,_=timed([binary,"exec",sid],env,b"len(ctx)\n");execs.append(w);rss.append(r);timed([binary,"kill",sid],env);w,r,_=timed(["python3","-c","import sys; d=open(sys.argv[1],'rb').read(); print(len(d))",str(f)],env);py.append(w)
        rows.append({"size_mb":mb,"repeats":a.repeats,"load_ms":{"median":statistics.median(loads),"p95":pct(loads,.95)},"snapshot_exec_ms":{"median":statistics.median(execs),"p95":pct(execs,.95)},"direct_python_read_ms":{"median":statistics.median(py),"p95":pct(py,.95)},"snapshot_bytes":int(statistics.median(snap)),"peak_rss_bytes":max((x for x in rss if x is not None),default=None)})
    out={"schema":1,"azdaja":subprocess.check_output([binary,"--version"],text=True).strip(),"host":{"os":platform.platform(),"machine":platform.machine(),"cpu":platform.processor()},"results":rows};text=json.dumps(out,indent=2);print(text);Path(a.output).write_text(text+"\n") if a.output else None
if __name__=="__main__":main()
