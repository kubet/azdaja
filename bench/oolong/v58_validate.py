#!/usr/bin/env python3
"""Independent goldless terminal validator for frozen V58 OOLONG evidence."""
from __future__ import annotations
import argparse,importlib.util,sys
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("oolong_v58_runner_for_validator",HERE/"v58_run.py")
if SPEC is None or SPEC.loader is None:raise RuntimeError("cannot load V58 runner")
run=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=run;SPEC.loader.exec_module(run)
class ValidationError(RuntimeError):pass

def build_validation(runner_terminal:dict[str,Any],recomputed:dict[str,Any])->dict[str,Any]:
    if runner_terminal!=recomputed or recomputed.get("validated") is not True:raise ValidationError("runner terminal differs from independent recomputation")
    return {"schema_version":1,"record_type":"oolong_v58_independent_terminal_validation","validator_sha256":run.sha256_file(Path(__file__).resolve()),"runner_terminal":recomputed,"validated":True}

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser();p.add_argument("--public-manifest",required=True);p.add_argument("--schedule",required=True);p.add_argument("--inference",required=True);p.add_argument("--claims",required=True);p.add_argument("--work-runs",required=True);p.add_argument("--checkpoint",required=True);p.add_argument("--runner-terminal",required=True);p.add_argument("--output",required=True);p.add_argument("--yes-validate-once",action="store_true");a=p.parse_args(argv)
    if not a.yes_validate_once:raise ValidationError("refusing validation without --yes-validate-once")
    out=Path(a.output).resolve();root=Path("/private/tmp/azdaja-v58-oolong-frozen-v1")
    expected_paths={"output":root/"independent-terminal.json","inference":root/"inference.jsonl","schedule":root/"inference.jsonl.schedule.json","claims_root":root/"inference.jsonl.claims","checkpoint":root/"inference.jsonl.checkpoint.json","runner_terminal":root/"inference.jsonl.terminal.json"}
    claims_path=Path(a.claims).resolve()
    if out!=expected_paths["output"] or Path(a.inference).resolve()!=expected_paths["inference"] or Path(a.schedule).resolve()!=expected_paths["schedule"] or expected_paths["claims_root"] not in claims_path.parents or Path(a.checkpoint).resolve()!=expected_paths["checkpoint"] or Path(a.runner_terminal).resolve()!=expected_paths["runner_terminal"]:raise ValidationError("validator paths are not the fixed production target")
    if out.exists():raise ValidationError("validation output already exists")
    suite=run.load_public_suite(Path(a.public_manifest));questions={f.fixture_id:f.question for f in suite.fixtures};schedule=run.load_json(Path(a.schedule).resolve(),"schedule")
    current_controller=run.controller_identity()
    if schedule.get("configuration",{}).get("controller")!=current_controller:raise ValidationError("validator runner/adapter differs from frozen schedule")
    if claims_path!=expected_paths["claims_root"]/schedule["schedule_id"] or Path(a.work_runs).resolve()!=root/"work"/("schedule-"+schedule["schedule_id"])/"runs":raise ValidationError("validator claim/work paths mismatch")
    recomputed=run.terminal_validate(Path(a.inference).resolve(),schedule,Path(a.claims).resolve(),Path(a.work_runs).resolve(),Path(a.checkpoint).resolve(),questions);runner_terminal=run.load_json(Path(a.runner_terminal).resolve(),"runner terminal")
    record=build_validation(runner_terminal,recomputed);record.update({"runner_sha256":current_controller["sha256"],"adapter_sha256":current_controller["adapter_sha256"],"schedule_sha256":run.sha256_file(Path(a.schedule).resolve()),"inference_sha256":run.sha256_file(Path(a.inference).resolve()),"runner_terminal_sha256":run.sha256_file(Path(a.runner_terminal).resolve()),"public_manifest_sha256":run.PUBLIC_MANIFEST_SHA256,"gold_sha256":run.GOLD_SHA256})
    run.atomic_json(out,record);return 0
if __name__=="__main__":
    try:raise SystemExit(main())
    except (ValidationError,run.V58Error) as exc:print(f"error: {exc}",file=sys.stderr);raise SystemExit(2)
