"""Bounded supervisor for the explicit continuation, independent of a tool's short wait."""
import argparse
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time
from bench.jev.asymmetry.baseline import continue_run as c


def stop_owned_bridge(output):
    state=Path(output)/'private-work/state/jcode-api'
    pidfile=state/'bridge.pid'; runtimefile=state/'runtime-dir'
    if not pidfile.exists() or not runtimefile.exists():return False
    pid=int(pidfile.read_text()); socket=str(Path(runtimefile.read_text().strip())/'api.sock')
    probe=subprocess.run(['ps','-p',str(pid),'-o','args='],capture_output=True,text=True)
    if probe.returncode:return False
    args=shlex.split(probe.stdout.strip())
    c.b.check(args[:2]==['jcode','api-bridge'] and '--api-socket' in args and
              args[args.index('--api-socket')+1]==socket,'owned_bridge_identity')
    os.kill(pid,signal.SIGTERM)
    return True


def supervise(command,deadline,output,*,env=None):
    remaining=deadline-time.time()
    c.b.check(remaining>0,'original_campaign_deadline')
    child=subprocess.Popen(command,stdin=subprocess.DEVNULL,env=env,start_new_session=True)
    reason=None; stopped_bridge=False
    try:
        code=child.wait(timeout=remaining)
    except subprocess.TimeoutExpired:
        reason='absolute_campaign_deadline'
        stopped_bridge=stop_owned_bridge(output)
        os.killpg(child.pid,signal.SIGTERM)
        try:code=child.wait(timeout=5)
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
    except BaseException as exc:
        reason='supervisor_'+type(exc).__name__
        try:stopped_bridge=stop_owned_bridge(output)
        except (OSError,ValueError,subprocess.SubprocessError,c.n.Stop):stopped_bridge=False
        finally:
            if child.poll() is None:os.killpg(child.pid,signal.SIGTERM)
            try:code=child.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
    return {'schema':'azdaja.asymmetry.continuation_supervisor.v1','child_exit':code,
            'stop_reason':reason,'absolute_deadline_unix':deadline,'finished_unix':time.time(),
            'owned_bridge_stop_requested':stopped_bridge,'campaign_completed':code==0 and reason is None}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--supervise',action='store_true');ap.add_argument('--acknowledge-provider-calls',action='store_true')
    ap.add_argument('--azdaja',type=Path);ap.add_argument('--output',type=Path);ap.add_argument('--private-jcode-home',type=Path)
    args=ap.parse_args(argv)
    if not args.supervise:
        print(json.dumps({'status':'offline_plan','new_provider_calls':0}));return 0
    c.b.check(args.acknowledge_provider_calls and args.azdaja and args.output and args.private_jcode_home,'explicit_live_arguments')
    c.b.check(not os.path.lexists(args.output),'new_output_required')
    # The child owns the exclusive continuation marker before any model admission.
    command=[sys.executable,'-B','-m','bench.jev.asymmetry.baseline.continue_run','--live','--acknowledge-provider-calls',
             '--azdaja',str(args.azdaja),'--output',str(args.output),'--private-jcode-home',str(args.private_jcode_home)]
    result=supervise(command,c.DEADLINE,args.output)
    destination=args.output/'supervisor-result.json' if args.output.is_dir() else args.output.with_suffix('.supervisor.json')
    with destination.open('xb') as f:f.write(c.n.canonical(result)+b'\n')
    print(json.dumps(result),flush=True)
    return 0 if result['campaign_completed'] else 2

if __name__=='__main__':raise SystemExit(main())
