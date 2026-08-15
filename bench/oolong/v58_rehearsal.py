#!/usr/bin/env python3
"""OAuth-free synthetic rehearsal for both terminal-78 and abort-10 V58 paths."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,platform,shutil,subprocess,sys
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent
def loadmod(name:str,path:Path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise RuntimeError(f"cannot load {path}")
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
run=loadmod("oolong_v58_runner_for_rehearsal",HERE/"v58_run.py")
reporter=loadmod("oolong_v58_report_for_rehearsal",HERE/"v58_report.py")
validator=loadmod("oolong_v58_validator_for_rehearsal",HERE/"v58_validate.py")
class RehearsalError(RuntimeError):pass

def mkdir(path:Path)->None:path.mkdir(mode=0o700,parents=True,exist_ok=False)
def response(question:str)->str:
    kind=run.requested_kind(question)
    if kind is None:raise RehearsalError("question has no unique requested form")
    return f"{kind}: synthetic\n"
def paths(root:Path,schedule:dict[str,Any])->dict[str,Path]:
    output=root/"inference.jsonl"
    return {"output":output,"schedule":Path(str(output)+".schedule.json"),"claims_root":Path(str(output)+".claims"),"claims":Path(str(output)+".claims")/schedule["schedule_id"],"checkpoint":Path(str(output)+".checkpoint.json"),"terminal":Path(str(output)+".terminal.json"),"work":root/"work","runs":root/"work"/("schedule-"+schedule["schedule_id"])/"runs"}
def synthesize(root:Path,schedule:dict[str,Any],questions:dict[str,str],fixtures:dict[str,Any],count:int,pass_checkpoint:bool)->tuple[list[dict[str,Any]],dict[str,Path]]:
    mkdir(root);p=paths(root,schedule);mkdir(p["claims_root"]);mkdir(p["claims"]);mkdir(p["work"]);(p["work"]/("schedule-"+schedule["schedule_id"])).mkdir(mode=0o700);p["runs"].mkdir(mode=0o700);run.atomic_json(p["schedule"],schedule);rows=[]
    candidate_seen=0
    for job in schedule["jobs"][:count]:
        if job["arm"]=="jcode-azdaja":candidate_seen+=1
        execution=(not (job["arm"]=="jcode-azdaja" and candidate_seen==26)) if pass_checkpoint else job["ordinal"]<=7
        text=response(questions[job["fixture_id"]]) if execution else ""
        run_dir=p["runs"]/f"r001-{job['ordinal']:03d}-{job['arm']}";run_dir.mkdir(mode=0o700)
        if job["arm"]=="jcode-azdaja":stdout=text
        elif job["arm"]=="jcode-native":stdout=json.dumps({"type":"done","text":text,"provider":"OpenAI","model":run.MODEL})+"\n"
        else:stdout=json.dumps({"type":"message_end","message":{"role":"assistant","provider":run.legacy.PRIME_PROVIDER,"model":run.MODEL,"api":"openai-codex-responses","content":[{"type":"text","text":text}]}})+"\n"
        contents={"stdout":("stdout.ndjson",stdout),"stderr":("stderr.log","")}
        if job["arm"]=="jcode-azdaja" and (execution or pass_checkpoint):
            contents.update({"azdaja_model_trace":("azdaja-model-usage.jsonl",json.dumps({"schema_version":2,"event":"model_attempt","timestamp_ms":1,"depth":0,"request_id":"synthetic","attempt":1,"category":"turn","outcome":"succeeded","provider":"OpenAI OAuth","model":run.MODEL,"failed_attempts_before_success":0,"degraded_transport":False,"input_tokens":1})+"\n"),"azdaja_solo_trace":("azdaja-solo-trace.log","synthetic-solo-trace\n")})
        artifacts={}
        for key,(name,content) in contents.items():
            artifact=run_dir/name;data=content.encode();fd=os.open(artifact,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,data);os.fsync(fd);os.close(fd);artifacts[key]={"path":str(artifact),"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data),"mode":"0600","credential_redacted":True,"contains_private_raw_trajectory":False,"exact_text_preserved":True}
        route_evidence=run.legacy.parse_azdaja_route_evidence(Path(artifacts["azdaja_model_trace"]["path"])) if "azdaja_model_trace" in artifacts else None
        runtime_route=run.legacy.runtime_assertion(job["arm"],stdout,route_evidence,repair_model=run.MODEL)
        staged_skill=None
        if job["arm"]=="jcode-azdaja":
            staged_skill={"asserted_after":True,"files":{name:{"source_sha256":value[0],"source_bytes":value[1],"staged_sha256":value[0],"staged_bytes":value[1],"source_sha256_after":value[0],"staged_sha256_after":value[0],"staged_matches_source":True,"unchanged_during_arm":True} for name,value in run.COMPONENTS.items()}}
        row={"record_type":"inference","schedule_id":schedule["schedule_id"],"run_id":job["run_id"],"fixture_id":job["fixture_id"],"row_sha256":job["row_sha256"],"context_sha256":job["context_sha256"],"execution_ordinal":job["ordinal"],"repetition":1,"arm":job["arm"],"candidate_sha256":run.CANDIDATE_SHA256,"controller_sha256":schedule["configuration"]["controller"]["sha256"],"execution_success":execution,"response":text,"success":None,"score":None,"scoring_status":"deferred","model":run.MODEL,"reasoning":run.REASONING,"provider":run.legacy.JCODE_PROVIDER if job["arm"].startswith("jcode") else run.legacy.PRIME_PROVIDER,"executables":run.legacy.expected_row_executables(job["arm"],schedule["configuration"]["executables"]),"trajectory_artifacts":artifacts,"staged_skill":staged_skill,"cleanup_errors":[],"auth_assertion":{"asserted":True},"task_context_integrity":{"asserted_before":True,"asserted_after":True,"errors":[],"expected_sha256":job["context_sha256"]},"tool_access_policy_assertion":{"asserted":True},"product_execution_asserted":execution if job["arm"]=="jcode-azdaja" else False,"trace_capture_assertion":{"asserted":execution},"credential_cleanup_assertion":{"asserted":True},"runtime_route_assertion":runtime_route,"root_context_leak_assertion":run.legacy.scan_context_file_against_solo_trace(fixtures[job["fixture_id"]].context_path,Path(artifacts["azdaja_solo_trace"]["path"]),expected_context_sha256=job["context_sha256"],exact_transcript_preserved=True) if job["arm"]=="jcode-azdaja" and "azdaja_solo_trace" in artifacts else None,"fixture":{"row":str(fixtures[job["fixture_id"]].row_path),"context":str(fixtures[job["fixture_id"]].context_path),"row_sha256":job["row_sha256"],"context_sha256":job["context_sha256"],"context_bytes":fixtures[job["fixture_id"]].context_path.stat().st_size,"context_chars":len(fixtures[job["fixture_id"]].context_path.read_text()),"context_lines":len(fixtures[job["fixture_id"]].context_path.read_text().splitlines())}}
        run.atomic_json(p["claims"]/(job["run_id"]+".json"),{"schedule_id":schedule["schedule_id"],"run_id":job["run_id"],"ordinal":job["ordinal"],"pid":os.getpid()});run.append_row(p["output"],row);run.atomic_json(p["claims"]/(job["run_id"]+".done.json"),{"schedule_id":schedule["schedule_id"],"run_id":job["run_id"],"row_sha256":hashlib.sha256(run.canonical_bytes(row)).hexdigest()});rows.append(row)
    summary=run.checkpoint_summary(rows,schedule,questions);status="pass" if summary["passed"] else "abort";run.atomic_json(p["checkpoint"],{"schema_version":1,"record_type":"oolong_v58_checkpoint","schedule_id":schedule["schedule_id"],"status":status,"summary":summary})
    if pass_checkpoint != summary["passed"]:raise RehearsalError("synthetic checkpoint outcome mismatch")
    return rows,p

def runtime_closure(prime:Path)->dict[str,Any]:
    return run.current_runtime_closure(prime,Path.home().resolve())

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser();p.add_argument("--bundle-root",required=True);p.add_argument("--public-manifest",required=True);p.add_argument("--azdaja-skill",required=True);p.add_argument("--jcode",required=True);p.add_argument("--prime-agent",required=True);p.add_argument("--production-root",default="/private/tmp/azdaja-v58-oolong-frozen-v1");p.add_argument("--yes-rehearse",action="store_true");a=p.parse_args(argv)
    if not a.yes_rehearse:raise RehearsalError("refusing rehearsal without --yes-rehearse")
    bundle=Path(a.bundle_root).resolve()
    if bundle.exists():raise RehearsalError("rehearsal bundle already exists")
    if Path(a.production_root).resolve()!=Path("/private/tmp/azdaja-v58-oolong-frozen-v1"):raise RehearsalError("production target mismatch")
    suite=run.load_public_suite(Path(a.public_manifest));skill,candidate=run.validate_candidate(Path(a.azdaja_skill));jcode=Path(run.legacy.ensure_executable(a.jcode,"jcode"));prime=Path(run.legacy.ensure_executable(a.prime_agent,"prime-agent"))
    if str(jcode)!=run.JCODE_PATH or run.sha256_file(jcode)!=run.JCODE_SHA256:raise RehearsalError("Jcode mismatch")
    executables={"jcode":run.legacy.executable_identity(str(jcode),"jcode"),"prime-agent":run.legacy.executable_identity(str(prime),"prime-agent"),"azdaja":run.legacy.executable_identity(str(skill/"azdaja"),"azdaja")};schedule=run.build_schedule(suite,candidate,executables);questions={f.fixture_id:f.question for f in suite.fixtures};fixtures={f.fixture_id:f for f in suite.fixtures};mkdir(bundle)
    terminal_rows,tp=synthesize(bundle/"terminal-78",schedule,questions,fixtures,78,True);terminal=run.terminal_validate(tp["output"],schedule,tp["claims"],tp["runs"],tp["checkpoint"],questions);run.atomic_json(tp["terminal"],terminal);validation=validator.build_validation(run.load_json(tp["terminal"],"runner terminal"),run.terminal_validate(tp["output"],schedule,tp["claims"],tp["runs"],tp["checkpoint"],questions));run.atomic_json(tp["terminal"].with_name("independent-terminal.json"),validation)
    synthetic_scores=[]
    candidate_index=0
    for row in terminal_rows:
        correct=True
        if row["arm"]=="jcode-azdaja":candidate_index+=1;correct=candidate_index<=24
        synthetic_scores.append({"run_id":row["run_id"],"fixture_id":row["fixture_id"],"arm":row["arm"],"execution_ordinal":row["execution_ordinal"],"execution_success":row["execution_success"],"strict_correct":correct})
    score_stub={"record_type":"oolong_v58_scores","campaign":"v58-low-candidate-first-v1","schedule_id":schedule["schedule_id"],"candidate_sha256":run.CANDIDATE_SHA256,"terminal_receipt":terminal,"scores":synthetic_scores};gate=reporter.build_report(score_stub,schedule,terminal_rows)
    if gate["gates"]["continuation_pass"] is not True:raise RehearsalError("synthetic 25/24 report gate did not pass")
    _,ap=synthesize(bundle/"abort-10",schedule,questions,fixtures,10,False)
    resume_refused=False
    try:
        abort_rows=run.validate_prefix(ap["output"],schedule,ap["claims"])
        run.enforce_checkpoint_startup(abort_rows,schedule,questions,ap["checkpoint"])
    except run.CheckpointAbort:resume_refused=True
    if not resume_refused:raise RehearsalError("sealed abort resume was not refused before OAuth")
    receipt={"schema_version":1,"record_type":"oolong_v58_target_bound_rehearsal","production_root":str(Path(a.production_root).resolve()),"schedule_id":schedule["schedule_id"],"schedule_sha256":hashlib.sha256(run.canonical_bytes(schedule)+b"\n").hexdigest(),"runner_sha256":run.sha256_file(HERE/"v58_run.py"),"adapter_sha256":run.sha256_file(HERE/"run.py"),"validator_sha256":run.sha256_file(HERE/"v58_validate.py"),"scorer_sha256":run.sha256_file(HERE/"v58_score.py"),"reporter_sha256":run.sha256_file(HERE/"v58_report.py"),"rehearsal_sha256":run.sha256_file(Path(__file__).resolve()),"public_manifest_sha256":run.PUBLIC_MANIFEST_SHA256,"candidate_sha256":run.CANDIDATE_SHA256,"candidate_components":candidate["components"],"jcode":executables["jcode"],"prime_agent":executables["prime-agent"],"runtime_closure":runtime_closure(prime),"model":run.MODEL,"reasoning":run.REASONING,"terminal_78":{"passed":True,"receipt":terminal,"independent_validation":validation},"abort_10":{"passed":True,"rows":10,"status":"abort","resume_refused_before_oauth":True},"synthetic_final_gate":{"execution_n":25,"strict_exact_n":24,"passed":True}}
    run.atomic_json(bundle/"receipt.json",receipt);print(bundle/"receipt.json");return 0
if __name__=="__main__":
    try:raise SystemExit(main())
    except (RehearsalError,run.V58Error,run.CheckpointAbort) as exc:print(f"error: {exc}",file=sys.stderr);raise SystemExit(2)
