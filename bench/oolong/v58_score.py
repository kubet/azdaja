#!/usr/bin/env python3
"""One-shot scorer for a terminal V58 OOLONG campaign.

Gold is accepted only after an independent no-gold terminal revalidation.  The
score output contains booleans and aggregates, never expected answer text.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("oolong_v58_runner_for_score",HERE/"v58_run.py")
if SPEC is None or SPEC.loader is None: raise RuntimeError("cannot load V58 runner")
run=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=run;SPEC.loader.exec_module(run)

class ScoreError(RuntimeError): pass

def sha(path: Path)->str:return run.sha256_file(path)
def load(path: Path,label: str)->dict[str,Any]:return run.load_json(path,label)

def strict_correct(response: str, canonical: str)->bool:
    return response==canonical or response==canonical+"\n"

def validate_gold(path: Path)->dict[str,dict[str,Any]]:
    run.require_private_file(path,"detached gold")
    if sha(path)!=run.GOLD_SHA256: raise ScoreError("detached gold hash mismatch")
    doc=load(path,"detached gold")
    if doc.get("record_type")!="oolong_v58_detached_gold" or doc.get("public_manifest_identity_sha256")!=run.PUBLIC_IDENTITY_SHA256 or doc.get("source_manifest_sha256")!=run.SOURCE_MANIFEST_SHA256: raise ScoreError("detached gold identity mismatch")
    entries=doc.get("fixtures")
    if not isinstance(entries,list) or len(entries)!=run.FIXTURE_COUNT: raise ScoreError("detached gold count mismatch")
    by_id={}
    for item in entries:
        if not isinstance(item,dict) or not isinstance(item.get("fixture_id"),str) or item["fixture_id"] in by_id: raise ScoreError("invalid/duplicate gold fixture")
        if not isinstance(item.get("expected_canonical"),str) or not item["expected_canonical"]: raise ScoreError("invalid expected canonical")
        by_id[item["fixture_id"]]=item
    return by_id

def main(argv: list[str]|None=None)->int:
    p=argparse.ArgumentParser();p.add_argument("--public-manifest",required=True);p.add_argument("--schedule",required=True);p.add_argument("--inference",required=True);p.add_argument("--claims",required=True);p.add_argument("--work-runs",required=True);p.add_argument("--checkpoint",required=True);p.add_argument("--terminal-receipt",required=True);p.add_argument("--gold",required=True);p.add_argument("--output",required=True);p.add_argument("--yes-score-once",action="store_true");a=p.parse_args(argv)
    if not a.yes_score_once: raise ScoreError("refusing score without --yes-score-once")
    out=Path(a.output).resolve();root=Path("/private/tmp/azdaja-v58-oolong-frozen-v1")
    if out!=root/"scores.json" or Path(a.inference).resolve()!=root/"inference.jsonl" or Path(a.schedule).resolve()!=root/"inference.jsonl.schedule.json" or Path(a.terminal_receipt).resolve()!=root/"independent-terminal.json":raise ScoreError("scorer paths are not the fixed production target")
    if out.exists(): raise ScoreError("score output already exists; scoring is one-shot")
    suite=run.load_public_suite(Path(a.public_manifest));questions={f.fixture_id:f.question for f in suite.fixtures};schedule_path=Path(a.schedule).resolve();schedule=load(schedule_path,"schedule")
    current_controller=run.controller_identity()
    if schedule.get("configuration",{}).get("controller")!=current_controller:raise ScoreError("scorer runner/adapter differs from frozen schedule")
    if Path(a.claims).resolve()!=root/"inference.jsonl.claims"/schedule["schedule_id"] or Path(a.work_runs).resolve()!=root/"work"/("schedule-"+schedule["schedule_id"])/"runs" or Path(a.checkpoint).resolve()!=root/"inference.jsonl.checkpoint.json":raise ScoreError("scorer claim/work/checkpoint paths mismatch")
    terminal_path=Path(a.terminal_receipt).resolve();validation=load(terminal_path,"independent terminal validation")
    terminal=validation.get("runner_terminal")
    recomputed=run.terminal_validate(Path(a.inference).resolve(),schedule,Path(a.claims).resolve(),Path(a.work_runs).resolve(),Path(a.checkpoint).resolve(),questions)
    expected_validator_sha=sha(HERE/"v58_validate.py")
    if validation.get("record_type")!="oolong_v58_independent_terminal_validation" or validation.get("validated") is not True or validation.get("validator_sha256")!=expected_validator_sha or validation.get("runner_sha256")!=current_controller["sha256"] or validation.get("adapter_sha256")!=current_controller["adapter_sha256"] or terminal!=recomputed or recomputed.get("validated") is not True: raise ScoreError("terminal receipt does not match independent validation")
    if validation.get("schedule_sha256")!=sha(schedule_path) or validation.get("inference_sha256")!=sha(Path(a.inference).resolve()): raise ScoreError("terminal artifact hash mismatch")
    gold=validate_gold(Path(a.gold).expanduser());rows=run.load_rows(Path(a.inference).resolve())
    if set(gold)!={f.fixture_id for f in suite.fixtures}: raise ScoreError("gold/public fixture set mismatch")
    scores=[]
    for row in rows:
        expected=gold[row["fixture_id"]];correct=strict_correct(row["response"],expected["expected_canonical"])
        scores.append({"run_id":row["run_id"],"fixture_id":row["fixture_id"],"arm":row["arm"],"execution_ordinal":row["execution_ordinal"],"execution_success":row["execution_success"],"strict_correct":correct})
    scorer=Path(__file__).resolve();record={"schema_version":1,"record_type":"oolong_v58_scores","campaign":"v58-low-candidate-first-v1","schedule_id":schedule["schedule_id"],"schedule_sha256":sha(schedule_path),"inference_sha256":sha(Path(a.inference).resolve()),"terminal_receipt_sha256":sha(terminal_path),"validator_sha256":expected_validator_sha,"terminal_receipt":terminal,"public_manifest_sha256":run.PUBLIC_MANIFEST_SHA256,"gold_sha256":run.GOLD_SHA256,"candidate_sha256":run.CANDIDATE_SHA256,"runner_sha256":schedule["configuration"]["controller"]["sha256"],"scorer_sha256":sha(scorer),"scores":scores}
    run.atomic_json(out,record);return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except (ScoreError,run.V58Error) as exc:print(f"error: {exc}",file=sys.stderr);raise SystemExit(2)
