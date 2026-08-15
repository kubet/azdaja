#!/usr/bin/env python3
"""Reporter and continuation-gate evaluator for scored V58 OOLONG evidence."""
from __future__ import annotations
import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("oolong_v58_runner_for_report",HERE/"v58_run.py")
if SPEC is None or SPEC.loader is None:raise RuntimeError("cannot load V58 runner")
run=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=run;SPEC.loader.exec_module(run)
class ReportError(RuntimeError):pass

def build_report(scores:dict[str,Any],schedule:dict[str,Any],inference_rows:list[dict[str,Any]]|None=None)->dict[str,Any]:
    if scores.get("record_type")!="oolong_v58_scores" or scores.get("campaign")!="v58-low-candidate-first-v1":raise ReportError("score campaign mismatch")
    if scores.get("schedule_id")!=schedule.get("schedule_id") or scores.get("candidate_sha256")!=run.CANDIDATE_SHA256:raise ReportError("score schedule/candidate mismatch")
    rows=scores.get("scores")
    if not isinstance(rows,list) or len(rows)!=run.ROW_COUNT:raise ReportError("score row count mismatch")
    jobs={j["run_id"]:j for j in schedule.get("jobs",[])}
    if len(jobs)!=run.ROW_COUNT or {r.get("run_id") for r in rows}!=set(jobs):raise ReportError("score run set mismatch")
    inference_by_id=None
    if inference_rows is not None:
        if len(inference_rows)!=run.ROW_COUNT:raise ReportError("inference row count mismatch")
        inference_by_id={r.get("run_id"):r for r in inference_rows}
        if len(inference_by_id)!=run.ROW_COUNT or set(inference_by_id)!=set(jobs):raise ReportError("inference run set mismatch")
    for row in rows:
        job=jobs[row["run_id"]]
        expected={"fixture_id":job["fixture_id"],"arm":job["arm"],"execution_ordinal":job["ordinal"]}
        if any(row.get(k)!=v for k,v in expected.items()) or type(row.get("execution_success")) is not bool or type(row.get("strict_correct")) is not bool:raise ReportError("score envelope mismatch")
        if inference_by_id is not None:
            inf=inference_by_id[row["run_id"]]
            if any(inf.get(k)!=v for k,v in {**expected,"execution_success":row["execution_success"]}.items()):raise ReportError("score/inference envelope mismatch")
    metrics={}
    for arm in run.ARMS:
        group=[r for r in rows if r.get("arm")==arm]
        if len(group)!=run.FIXTURE_COUNT:raise ReportError(f"fixed denominator mismatch: {arm}")
        execution=sum(r["execution_success"] for r in group);strict=sum(r["execution_success"] and r["strict_correct"] for r in group)
        metrics[arm]={"denominator_n":26,"execution_n":execution,"strict_exact_n":strict,"execution_rate":execution/26,"strict_exact_rate":strict/26}
    terminal=scores.get("terminal_receipt")
    if not isinstance(terminal,dict) or terminal.get("validated") is not True:raise ReportError("missing terminal validation")
    integrity=all(terminal.get(k) is True for k in ("integrity_gate","route_gate","leak_gate","credential_cleanup_gate"));cand=metrics["jcode-azdaja"];continuation=integrity and cand["execution_n"]>=25 and cand["strict_exact_n"]>=24
    return {"schema_version":1,"record_type":"oolong_v58_report","campaign":"v58-low-candidate-first-v1","schedule_id":schedule["schedule_id"],"candidate_sha256":run.CANDIDATE_SHA256,"model":run.MODEL,"reasoning":run.REASONING,"metrics":metrics,"gates":{"fixed_denominator_n":26,"minimum_execution_n":25,"minimum_strict_exact_n":24,"execution_gate":cand["execution_n"]>=25,"strict_exact_gate":cand["strict_exact_n"]>=24,"integrity_gate":terminal.get("integrity_gate") is True,"route_gate":terminal.get("route_gate") is True,"leak_gate":terminal.get("leak_gate") is True,"credential_cleanup_gate":terminal.get("credential_cleanup_gate") is True,"continuation_pass":continuation},"authorization":{"rah_authorized":False,"publication_authorized":False,"release_authorized":False,"note":"A PASS is private fresh-suite evidence only and does not authorize RAH, release, publication, or a superiority claim."}}

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser();p.add_argument("--scores",required=True);p.add_argument("--schedule",required=True);p.add_argument("--inference",required=True);p.add_argument("--terminal-receipt",required=True);p.add_argument("--output",required=True);p.add_argument("--yes-report-once",action="store_true");a=p.parse_args(argv)
    if not a.yes_report_once:raise ReportError("refusing report without --yes-report-once")
    out=Path(a.output).resolve();root=Path("/private/tmp/azdaja-v58-oolong-frozen-v1")
    if out!=root/"report.json" or Path(a.scores).resolve()!=root/"scores.json" or Path(a.schedule).resolve()!=root/"inference.jsonl.schedule.json" or Path(a.inference).resolve()!=root/"inference.jsonl" or Path(a.terminal_receipt).resolve()!=root/"independent-terminal.json":raise ReportError("reporter paths are not the fixed production target")
    if out.exists():raise ReportError("report output already exists")
    score_path=Path(a.scores).resolve();schedule_path=Path(a.schedule).resolve();scores=run.load_json(score_path,"scores");schedule=run.load_json(schedule_path,"schedule")
    current_controller=run.controller_identity()
    if schedule.get("configuration",{}).get("controller")!=current_controller:raise ReportError("reporter runner/adapter differs from frozen schedule")
    if scores.get("schedule_sha256")!=run.sha256_file(schedule_path):raise ReportError("score schedule hash mismatch")
    if scores.get("scorer_sha256")!=run.sha256_file(HERE/"v58_score.py") or scores.get("validator_sha256")!=run.sha256_file(HERE/"v58_validate.py") or scores.get("runner_sha256")!=schedule.get("configuration",{}).get("controller",{}).get("sha256"):raise ReportError("score controller binding mismatch")
    validation_path=Path(a.terminal_receipt).resolve();validation=run.load_json(validation_path,"independent terminal validation")
    if scores.get("terminal_receipt_sha256")!=run.sha256_file(validation_path) or validation.get("record_type")!="oolong_v58_independent_terminal_validation" or validation.get("validated") is not True or validation.get("validator_sha256")!=run.sha256_file(HERE/"v58_validate.py") or validation.get("runner_terminal")!=scores.get("terminal_receipt"):raise ReportError("score/terminal validation binding mismatch")
    inference_path=Path(a.inference).resolve()
    if scores.get("inference_sha256")!=run.sha256_file(inference_path):raise ReportError("score inference hash mismatch")
    report=build_report(scores,schedule,run.load_rows(inference_path));report.update({"scores_sha256":run.sha256_file(score_path),"schedule_sha256":run.sha256_file(schedule_path),"reporter_sha256":run.sha256_file(Path(__file__).resolve()),"scorer_sha256":scores.get("scorer_sha256"),"runner_sha256":scores.get("runner_sha256"),"terminal_receipt_sha256":scores.get("terminal_receipt_sha256"),"gold_sha256":run.GOLD_SHA256})
    run.atomic_json(out,report);return 0
if __name__=="__main__":
    try:raise SystemExit(main())
    except (ReportError,run.V58Error) as exc:print(f"error: {exc}",file=sys.stderr);raise SystemExit(2)
