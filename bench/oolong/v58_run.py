#!/usr/bin/env python3
"""V58-only, goldless, candidate-first OOLONG inference controller.

This module never loads expected answers and never scores.  It accepts only the
precommitted public manifest and evaluated V58 bundle.  A separate scorer may
consume its terminal receipt after the encrypted gold image is attached.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import secrets
import stat
import sys
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("azdaja_oolong_legacy_v58", HERE / "run.py")
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load historical OOLONG adapter")
legacy = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = legacy
_SPEC.loader.exec_module(legacy)

MODEL = "gpt-5.6-luna"
REASONING = "low"
ARMS = ("jcode-native", "prime-agent", "jcode-azdaja")
FIXTURE_COUNT = 26
ROW_COUNT = 78
SEED = 20260813
TIMEOUT_SECONDS = 600
JCODE_PATH = "/Users/vukasinkubet/.jcode/builds/versions/0.75.3/jcode"
JCODE_SHA256 = "f01c442265d22e9dead7f227b2ec115ab99164e876ff354a72988a9311bf3c4f"
PUBLIC_MANIFEST_SHA256 = "bbf624cec245d971879ad3c1058148a1d188eadeb546f2cc6f860f8c74584eb4"
PUBLIC_IDENTITY_SHA256 = "a94741cfe6bfd37f012d09333430751c0604fa04232016e66a5b4223d4bb388c"
SOURCE_MANIFEST_SHA256 = "933566c8b875149fe0b35b394024344f87059face8a567ca1cf7a2106368e941"
GOLD_SHA256 = "b9f8bab8a9e190f416688310a45542381360aae874369ada7e9dc8ac14a504bc"
CANDIDATE_SHA256 = "0fb0c6b52e5ad22dc1ea7b12bd44ff264c728e1df55f7c5b3746f6e08283d5cf"
COMPONENTS = {
    "SKILL.md": ("c4990d75786c2c9a822abeb4d905fdc70ee129dcaf39df444568d77792015c0d", 6402),
    "azdaja": ("1d1e70b4e8720792553e89726a33472825d55a2365a504744cf9a747697c3224", 6434288),
    "config.toml": ("ca3f153c8a5a80c3727473fea90452ade5c556a24d026fb54084257791fd8eb8", 481),
}
CHECKPOINT_POLICY = {
    "candidate_count": 10,
    "minimum_execution_n": 8,
    "minimum_recognition_n": 7,
    "failure_exit_code": 3,
    "recognition": "question-derived exact KIND: VALUE with optional single LF",
}
FINAL_GATE = {"fixed_denominator_n": 26, "minimum_execution_n": 25, "minimum_strict_exact_n": 24}
FORBIDDEN_PUBLIC_KEYS = {"answer", "answer_type", "expected", "expected_kind", "expected_value", "expected_canonical"}
MAX_EXACT_RESPONSE_BYTES = 1 << 20


class V58Error(RuntimeError):
    pass


class CheckpointAbort(V58Error):
    pass


@dataclass(frozen=True)
class PublicFixture:
    fixture_id: str
    row_path: Path
    context_path: Path
    question: str
    row_sha256: str
    context_sha256: str
    legacy_fixture: Any


@dataclass(frozen=True)
class PublicSuite:
    path: Path
    sha256: str
    document: dict[str, Any]
    fixtures: tuple[PublicFixture, ...]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def require_private_file(path: Path, label: str) -> None:
    meta = path.lstat()
    if not stat.S_ISREG(meta.st_mode) or stat.S_ISLNK(meta.st_mode):
        raise V58Error(f"{label} is not a regular file")
    if meta.st_mode & 0o077:
        raise V58Error(f"{label} is not owner-only")


def require_private_dir(path: Path, label: str) -> None:
    meta = path.lstat()
    if not stat.S_ISDIR(meta.st_mode) or stat.S_ISLNK(meta.st_mode):
        raise V58Error(f"{label} is not a directory")
    if meta.st_mode & 0o077:
        raise V58Error(f"{label} is not owner-only")


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_json(path: Path, value: Any) -> None:
    if path.exists():
        raise V58Error(f"refusing to replace existing {path.name}")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    tmp = path.parent / f".{path.name}.{os.getpid()}.{secrets.token_hex(8)}.tmp"
    data = canonical_bytes(value) + b"\n"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        view=memoryview(data)
        while view:
            written=os.write(fd,view)
            if written<=0:raise OSError("short write")
            view=view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        os.link(tmp,path)
    except FileExistsError as exc:
        tmp.unlink()
        raise V58Error(f"refusing to replace existing {path.name}") from exc
    tmp.unlink()
    fsync_dir(path.parent)


def append_row(path: Path, row: dict[str, Any]) -> None:
    data = canonical_bytes(row) + b"\n"
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        view=memoryview(data)
        while view:
            written=os.write(fd,view)
            if written<=0:raise OSError("short append")
            view=view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    fsync_dir(path.parent)


def load_json(path: Path, label: str) -> dict[str, Any]:
    require_private_file(path, label)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise V58Error(f"cannot load {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise V58Error(f"{label} must be an object")
    return value


def load_public_suite(path: Path) -> PublicSuite:
    raw_path=path.expanduser()
    require_private_file(raw_path,"public manifest")
    path=raw_path.resolve()
    if sha256_file(path) != PUBLIC_MANIFEST_SHA256:
        raise V58Error("public manifest hash mismatch")
    doc = load_json(path, "public manifest")
    if doc.get("gold_sha256") != GOLD_SHA256 or len(doc.get("fixtures", [])) != FIXTURE_COUNT:
        raise V58Error("public manifest commitment/count mismatch")
    identity = dict(doc)
    identity.pop("gold_sha256", None)
    if hashlib.sha256(canonical_bytes(identity)).hexdigest() != PUBLIC_IDENTITY_SHA256:
        raise V58Error("public manifest identity mismatch")
    root = path.parent
    require_private_dir(root, "public root")
    fixtures: list[PublicFixture] = []
    seen: set[str] = set()
    for entry in doc["fixtures"]:
        if not isinstance(entry, dict):
            raise V58Error("public fixture entry is not an object")
        fixture_id = entry.get("fixture_id")
        if not isinstance(fixture_id, str) or not fixture_id or fixture_id in seen:
            raise V58Error("invalid/duplicate public fixture id")
        seen.add(fixture_id)
        raw_row_path=root/entry["row"]
        raw_context_path=root/entry["context"]
        require_private_file(raw_row_path,"public row")
        require_private_file(raw_context_path,"public context")
        row_path=raw_row_path.resolve()
        context_path=raw_context_path.resolve()
        if root not in row_path.parents or root not in context_path.parents:
            raise V58Error("public fixture escapes root")
        if sha256_file(row_path) != entry.get("row_sha256"):
            raise V58Error("public row hash mismatch")
        if sha256_file(context_path) != entry.get("context_sha256"):
            raise V58Error("public context hash mismatch")
        row = load_json(row_path, "public row")
        if FORBIDDEN_PUBLIC_KEYS & set(row):
            raise V58Error("public row contains a gold/expected field")
        question = row.get("question")
        if not isinstance(question, str) or not question:
            raise V58Error("public question is missing")
        metadata = dict(row)
        metadata["question"] = question
        legacy_fixture = legacy.Fixture(
            row_path=row_path,
            context_path=context_path,
            metadata=metadata,
            expected_kind="",
            expected_value="",
            expected_canonical="",
            row_sha256=entry["row_sha256"],
            context_sha256=entry["context_sha256"],
            context_bytes=context_path.stat().st_size,
            context_chars=len(context_path.read_text(encoding="utf-8")),
            context_lines=len(context_path.read_text(encoding="utf-8").splitlines()),
        )
        fixtures.append(PublicFixture(fixture_id, row_path, context_path, question, entry["row_sha256"], entry["context_sha256"], legacy_fixture))
    return PublicSuite(path, PUBLIC_MANIFEST_SHA256, doc, tuple(fixtures))


def validate_candidate(skill: Path) -> tuple[Path, dict[str, Any]]:
    legacy.MODEL = MODEL
    legacy.REASONING = REASONING
    skill = legacy.validate_skill(str(skill))
    identity = legacy.candidate_identity(skill)
    if identity.get("sha256") != CANDIDATE_SHA256:
        raise V58Error("candidate aggregate is not exact V58")
    for name, (expected_sha, expected_bytes) in COMPONENTS.items():
        got = identity.get("components", {}).get(name, {})
        if got.get("sha256") != expected_sha or got.get("bytes") != expected_bytes:
            raise V58Error(f"candidate component mismatch: {name}")
    config = (skill / "config.toml").read_text(encoding="utf-8")
    if 'default_model = "gpt-5.6-luna"' not in config or 'jcode_reasoning = "low"' not in config:
        raise V58Error("candidate configuration is not Luna/low")
    legacy.MODEL = MODEL
    legacy.REASONING = REASONING
    legacy.configure_azdaja_repair_model(MODEL)
    return skill, identity


def controller_identity() -> dict[str, Any]:
    path = Path(__file__).resolve()
    adapter=HERE/"run.py"
    return {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size,"adapter_path":str(adapter.resolve()),"adapter_sha256":sha256_file(adapter),"adapter_bytes":adapter.stat().st_size}


def build_schedule(suite: PublicSuite, candidate: dict[str, Any], executables: dict[str, Any]) -> dict[str, Any]:
    import random
    rng = random.Random(SEED)
    order = list(suite.fixtures)
    rng.shuffle(order)
    jobs: list[dict[str, Any]] = []
    def add(item: PublicFixture, arm: str) -> None:
        jobs.append({"ordinal": len(jobs) + 1, "fixture_id": item.fixture_id, "row_sha256": item.row_sha256, "context_sha256": item.context_sha256, "repetition": 1, "arm": arm})
    for item in order[:10]: add(item, "jcode-azdaja")
    for item in order[:10]:
        controls = ["jcode-native", "prime-agent"]; rng.shuffle(controls)
        for arm in controls: add(item, arm)
    for item in order[10:]: add(item, "jcode-azdaja")
    for item in order[10:]:
        controls = ["jcode-native", "prime-agent"]; rng.shuffle(controls)
        for arm in controls: add(item, arm)
    identity = {"schema_version": 1, "record_type": "oolong_v58_frozen_schedule", "campaign": "v58-low-candidate-first-v1", "suite": {"manifest_sha256": suite.sha256, "identity_sha256": PUBLIC_IDENTITY_SHA256, "source_manifest_sha256": SOURCE_MANIFEST_SHA256, "gold_sha256": GOLD_SHA256, "fixtures": [{"fixture_id": f.fixture_id, "row_sha256": f.row_sha256, "context_sha256": f.context_sha256} for f in suite.fixtures]}, "configuration": {"model": MODEL, "reasoning": REASONING, "arms": list(ARMS), "repetitions": 1, "seed": SEED, "timeout_seconds": TIMEOUT_SECONDS, "candidate": candidate, "controller": controller_identity(), "executables": executables}, "checkpoint_policy": CHECKPOINT_POLICY, "final_gate": FINAL_GATE, "jobs": jobs}
    schedule_id = hashlib.sha256(canonical_bytes(identity)).hexdigest()
    for job in jobs:
        job["run_id"] = hashlib.sha256(b"oolong-v58-run-v1\0" + schedule_id.encode() + canonical_bytes(job)).hexdigest()
    identity["schedule_id"] = schedule_id
    return identity


def requested_kind(question: str) -> str | None:
    matches = re.findall(r"(?i)form ['\"]([A-Za-z][A-Za-z0-9 _-]{0,63}): [^'\"\r\n]+['\"]", question)
    if len(matches) != 1:
        return None
    return matches[0]


def gold_blind_recognized(question: str, response: str) -> bool:
    if not isinstance(question, str) or not isinstance(response, str) or "\r" in response:
        return False
    kind = requested_kind(question)
    if kind is None:
        return False
    value = r"[A-Za-z0-9](?:[A-Za-z0-9 _-]{0,253}[A-Za-z0-9])?"
    return re.fullmatch(re.escape(kind) + r": " + value + r"\n?", response) is not None


def checkpoint_summary(rows: list[dict[str, Any]], schedule: dict[str, Any], questions: dict[str, str]) -> dict[str, Any]:
    if schedule.get("checkpoint_policy") != CHECKPOINT_POLICY:
        raise V58Error("checkpoint policy mismatch")
    candidates = [r for r in rows if r.get("arm") == "jcode-azdaja"][:10]
    execution = sum(r.get("execution_success") is True for r in candidates)
    recognition = sum(r.get("execution_success") is True and gold_blind_recognized(questions[r["fixture_id"]], r.get("response", "")) for r in candidates)
    reached = len(candidates) == 10
    return {"candidate_count": len(candidates), "execution_n": execution, "recognition_n": recognition, "reached": reached, "passed": reached and execution >= 8 and recognition >= 7}


def enforce_checkpoint_startup(rows: list[dict[str, Any]], schedule: dict[str, Any], questions: dict[str, str], checkpoint: Path) -> dict[str, Any] | None:
    if checkpoint.exists():
        marker=load_json(checkpoint,"checkpoint marker")
        recomputed=checkpoint_summary(rows,schedule,questions)
        expected_status="pass" if recomputed["passed"] else "abort"
        if len(rows)<10 or marker.get("schedule_id")!=schedule["schedule_id"] or marker.get("summary")!=recomputed or marker.get("status")!=expected_status:
            raise V58Error("checkpoint marker does not match exact prefix")
        if marker.get("status")=="abort":raise CheckpointAbort("checkpoint is permanently aborted")
        return marker
    if len(rows)>=10:
        if len(rows)>10:raise V58Error("post-checkpoint rows exist without a durable marker")
        summary=checkpoint_summary(rows,schedule,questions);marker={"schema_version":1,"record_type":"oolong_v58_checkpoint","schedule_id":schedule["schedule_id"],"status":"pass" if summary["passed"] else "abort","summary":summary};atomic_json(checkpoint,marker)
        if not summary["passed"]:raise CheckpointAbort("checkpoint failed")
        return marker
    return None


def exact_final(arm: str, stdout: str) -> str:
    if arm == "jcode-azdaja":
        final=stdout
    else:
        final=None
        assembled=""
        for obj in legacy.json_objects(stdout):
            if arm=="prime-agent" and obj.get("type")=="message_end":
                message=obj.get("message")
                if isinstance(message,dict) and message.get("role")=="assistant" and isinstance(message.get("content"),list):
                    value="".join(part.get("text","") for part in message["content"] if isinstance(part,dict) and part.get("type")=="text")
                    if value:final=value
            elif arm=="jcode-native":
                typ=obj.get("type") or obj.get("ev")
                if typ in {"text_delta","assistant_text_delta"} and isinstance(obj.get("text"),str):assembled+=obj["text"]
                for key in ("response","output_text","text","content"):
                    if typ in {"result","message_end","assistant","final","done"} and isinstance(obj.get(key),str):final=obj[key]
        if final is None:final=assembled
    if len(final.encode("utf-8"))>MAX_EXACT_RESPONSE_BYTES:raise V58Error("exact final response exceeds safety limit")
    return final


def load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    require_private_file(path, "inference rows")
    rows=[]
    for n,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line: raise V58Error(f"blank row {n}")
        obj=json.loads(line)
        if not isinstance(obj,dict): raise V58Error(f"invalid row {n}")
        rows.append(obj)
    return rows


def expected_claim_names(schedule: dict[str, Any], count: int | None = None) -> set[str]:
    jobs=schedule["jobs"] if count is None else schedule["jobs"][:count]
    return {name for j in jobs for name in (j["run_id"]+".json", j["run_id"]+".done.json")}


def recover_trailing_done(output: Path, schedule: dict[str, Any], claims: Path) -> bool:
    """Materialize only a missing done receipt for an already durable final row."""
    rows=load_rows(output)
    if not rows or not claims.exists():return False
    count=len(rows);job=schedule["jobs"][count-1];done_path=claims/(job["run_id"]+".done.json")
    if done_path.exists():return False
    expected=expected_claim_names(schedule,count-1)|{job["run_id"]+".json"}
    actual={p.name for p in claims.iterdir()}
    if actual!=expected:raise V58Error("indeterminate claim/row/done state; retry forbidden")
    row=rows[-1]
    envelope={"record_type":"inference","schedule_id":schedule["schedule_id"],"run_id":job["run_id"],"fixture_id":job["fixture_id"],"row_sha256":job["row_sha256"],"context_sha256":job["context_sha256"],"execution_ordinal":job["ordinal"],"repetition":1,"arm":job["arm"],"candidate_sha256":CANDIDATE_SHA256,"controller_sha256":schedule["configuration"]["controller"]["sha256"],"model":MODEL,"reasoning":REASONING,"executables":legacy.expected_row_executables(job["arm"],schedule["configuration"]["executables"]),"scoring_status":"deferred","score":None,"success":None}
    if any(row.get(key)!=value for key,value in envelope.items()) or type(row.get("execution_success")) is not bool or not isinstance(row.get("response"),str):raise V58Error("durable trailing row envelope is invalid")
    claim=load_json(claims/(job["run_id"]+".json"),"claim")
    if any(claim.get(key)!=value for key,value in {"schedule_id":schedule["schedule_id"],"run_id":job["run_id"],"ordinal":job["ordinal"]}.items()):raise V58Error("trailing claim mismatch")
    atomic_json(done_path,{"schedule_id":schedule["schedule_id"],"run_id":job["run_id"],"row_sha256":hashlib.sha256(canonical_bytes(row)).hexdigest()})
    return True


def validate_prefix(output: Path, schedule: dict[str, Any], claims: Path) -> list[dict[str, Any]]:
    rows=load_rows(output)
    if len(rows)>ROW_COUNT: raise V58Error("too many rows")
    for i,row in enumerate(rows):
        job=schedule["jobs"][i]
        for key,val in {"record_type":"inference","schedule_id":schedule["schedule_id"],"run_id":job["run_id"],"fixture_id":job["fixture_id"],"row_sha256":job["row_sha256"],"context_sha256":job["context_sha256"],"execution_ordinal":job["ordinal"],"repetition":1,"arm":job["arm"],"candidate_sha256":CANDIDATE_SHA256,"controller_sha256":schedule["configuration"]["controller"]["sha256"],"model":MODEL,"reasoning":REASONING,"executables":legacy.expected_row_executables(job["arm"],schedule["configuration"]["executables"]),"scoring_status":"deferred","score":None,"success":None}.items():
            if row.get(key)!=val: raise V58Error(f"row {i+1} mismatch: {key}")
        if type(row.get("execution_success")) is not bool or not isinstance(row.get("response"),str): raise V58Error(f"row {i+1} terminal fields invalid")
        claim=load_json(claims/(job["run_id"]+".json"),"claim")
        done=load_json(claims/(job["run_id"]+".done.json"),"done")
        if claim.get("schedule_id")!=schedule["schedule_id"] or claim.get("run_id")!=job["run_id"] or claim.get("ordinal")!=job["ordinal"]: raise V58Error("claim mismatch")
        if done.get("schedule_id")!=schedule["schedule_id"] or done.get("run_id")!=job["run_id"] or done.get("row_sha256")!=hashlib.sha256(canonical_bytes(row)).hexdigest(): raise V58Error("done receipt mismatch")
    actual={p.name for p in claims.iterdir()} if claims.exists() else set()
    if actual != expected_claim_names(schedule,len(rows)): raise V58Error("claim/done file set is not exact prefix")
    return rows


def validate_artifact_prefix(rows: list[dict[str, Any]], schedule: dict[str, Any], work_runs: Path) -> dict[str, bool]:
    legacy.MODEL=MODEL;legacy.REASONING=REASONING;legacy.configure_azdaja_repair_model(MODEL)
    expected_dirs={f"r001-{j['ordinal']:03d}-{j['arm']}" for j in schedule["jobs"][:len(rows)]}
    entries=list(work_runs.iterdir())
    if {p.name for p in entries}!=expected_dirs:raise V58Error("artifact directory entry set mismatch")
    for entry in entries:require_private_dir(entry,"artifact directory")
    integrity_gate=True;route_gate=True;leak_gate=True;credential_cleanup_gate=True
    for index,row in enumerate(rows):
        job=schedule["jobs"][index]
        expected_provider=legacy.JCODE_PROVIDER if row["arm"].startswith("jcode") else legacy.PRIME_PROVIDER
        if row.get("model")!=MODEL or row.get("reasoning")!=REASONING or row.get("provider")!=expected_provider:raise V58Error("row model/reasoning/provider mismatch")
        if row.get("executables")!=legacy.expected_row_executables(job["arm"],schedule["configuration"]["executables"]):raise V58Error("row executable binding mismatch")
        if row["arm"]=="jcode-azdaja":
            staged=row.get("staged_skill")
            if not isinstance(staged,dict) or staged.get("asserted_after") is not True:raise V58Error("candidate staged-skill assertion missing")
            files=staged.get("files")
            for name,(expected_sha,expected_bytes) in COMPONENTS.items():
                item=files.get(name) if isinstance(files,dict) else None
                if not isinstance(item,dict) or any(item.get(key)!=value for key,value in {"source_sha256":expected_sha,"source_bytes":expected_bytes,"staged_sha256":expected_sha,"staged_bytes":expected_bytes,"source_sha256_after":expected_sha,"staged_sha256_after":expected_sha,"staged_matches_source":True,"unchanged_during_arm":True}.items()):raise V58Error(f"candidate staged component mismatch: {name}")
        run_dir=work_runs/f"r001-{job['ordinal']:03d}-{job['arm']}";require_private_dir(run_dir,"artifact directory")
        artifacts=row.get("trajectory_artifacts");required_artifacts={"stdout","stderr"};allowed_artifacts=set(required_artifacts)
        if row["arm"]=="jcode-azdaja":allowed_artifacts|={"azdaja_model_trace","azdaja_solo_trace"}
        if row["arm"]=="jcode-azdaja" and row.get("execution_success") is True:required_artifacts=set(allowed_artifacts)
        if not isinstance(artifacts,dict) or not required_artifacts<=set(artifacts) or not set(artifacts)<=allowed_artifacts:raise V58Error("row trajectory artifact allowlist mismatch")
        artifact_names=set()
        for metadata in artifacts.values():
            if not isinstance(metadata,dict) or not isinstance(metadata.get("path"),str) or metadata.get("mode")!="0600" or metadata.get("credential_redacted") is not True or metadata.get("contains_private_raw_trajectory") is not False:raise V58Error("artifact metadata invalid")
            artifact=Path(metadata["path"])
            if artifact.parent.resolve()!=run_dir.resolve():raise V58Error("artifact path escapes run directory")
            require_private_file(artifact,"trajectory artifact")
            if sha256_file(artifact)!=metadata.get("sha256") or artifact.stat().st_size!=metadata.get("bytes"):raise V58Error("trajectory artifact hash/size mismatch")
            artifact_names.add(artifact.name)
        actual_names={p.name for p in run_dir.iterdir()}
        if actual_names!=artifact_names or len(actual_names)!=len(artifacts):raise V58Error("retained artifact file set mismatch")
        stdout_meta=artifacts["stdout"]
        if stdout_meta.get("exact_text_preserved") is True:
            try:exact=exact_final(row["arm"],Path(stdout_meta["path"]).read_text(encoding="utf-8"))
            except V58Error:
                if not (row.get("execution_success") is False and row.get("response")=="" and isinstance(row.get("failure"),dict) and row["failure"].get("kind")=="response_too_large"):raise
            else:
                if exact!=row.get("response"):raise V58Error("row response is not exact retained final output")
        elif not (row.get("execution_success") is False and row.get("response")=="" and isinstance(row.get("failure"),dict) and row["failure"].get("kind")=="raw_output_redacted"):
            raise V58Error("non-exact stdout was not failed closed")
        cleanup=row.get("credential_cleanup_assertion")
        if row.get("cleanup_errors") not in ([],None) or not isinstance(cleanup,dict) or cleanup.get("asserted") is not True:credential_cleanup_gate=False
        context_integrity=row.get("task_context_integrity")
        if not isinstance(row.get("auth_assertion"),dict) or row["auth_assertion"].get("asserted") is not True:integrity_gate=False
        if not isinstance(context_integrity,dict) or context_integrity.get("asserted_before") is not True or context_integrity.get("asserted_after") is not True or context_integrity.get("errors")!=[] or context_integrity.get("expected_sha256")!=job["context_sha256"] or not isinstance(row.get("tool_access_policy_assertion"),dict) or row["tool_access_policy_assertion"].get("asserted") is not True:integrity_gate=False
        if row["arm"]=="jcode-azdaja" and row.get("execution_success") is True and (row.get("product_execution_asserted") is not True or not isinstance(row.get("trace_capture_assertion"),dict) or row["trace_capture_assertion"].get("asserted") is not True):integrity_gate=False
        route=row.get("runtime_route_assertion")
        stdout_text=Path(stdout_meta["path"]).read_text(encoding="utf-8")
        route_evidence=None
        if row["arm"]=="jcode-azdaja" and isinstance(artifacts.get("azdaja_model_trace"),dict):route_evidence=legacy.parse_azdaja_route_evidence(Path(artifacts["azdaja_model_trace"]["path"]))
        recomputed_route=legacy.runtime_assertion(row["arm"],stdout_text,route_evidence,repair_model=MODEL)
        if recomputed_route!=route:raise V58Error("independent runtime-route recomputation mismatch")
        if row.get("execution_success") is True and recomputed_route.get("asserted") is not True:route_gate=False
        if row["arm"]=="jcode-azdaja":
            leak=row.get("root_context_leak_assertion");solo=artifacts.get("azdaja_solo_trace")
            if isinstance(solo,dict):
                fixture=row.get("fixture")
                if not isinstance(fixture,dict) or fixture.get("context_sha256")!=job["context_sha256"] or not isinstance(fixture.get("context"),str):raise V58Error("candidate context envelope mismatch")
                context=Path(fixture["context"]);require_private_file(context,"public context")
                if sha256_file(context)!=job["context_sha256"]:raise V58Error("candidate context bytes changed")
                rescanned=legacy.scan_context_file_against_solo_trace(context,Path(solo["path"]),expected_context_sha256=job["context_sha256"],exact_transcript_preserved=solo.get("exact_text_preserved") is True)
                if rescanned!=leak:raise V58Error("independent root-context rescan mismatch")
            if not isinstance(leak,dict) or leak.get("asserted") is not True or leak.get("leak_detected") is not False or leak.get("scan_complete") is not True or leak.get("missing_reasons")!=[]:leak_gate=False
    return {"integrity_gate":integrity_gate,"route_gate":route_gate,"leak_gate":leak_gate,"credential_cleanup_gate":credential_cleanup_gate}


def terminal_validate(output: Path, schedule: dict[str, Any], claims: Path, work_runs: Path, checkpoint: Path, questions: dict[str, str]) -> dict[str, Any]:
    legacy.MODEL=MODEL;legacy.REASONING=REASONING;legacy.configure_azdaja_repair_model(MODEL)
    rows=validate_prefix(output,schedule,claims)
    if len(rows)!=ROW_COUNT: raise V58Error("terminal validation requires 78 rows")
    marker=load_json(checkpoint,"checkpoint marker")
    recomputed = checkpoint_summary(rows, schedule, questions)
    if marker.get("schedule_id") != schedule["schedule_id"] or marker.get("status")!="pass" or marker.get("summary") != recomputed or recomputed.get("passed") is not True: raise V58Error("terminal checkpoint did not pass exactly")
    gates=validate_artifact_prefix(rows,schedule,work_runs)
    return {"schema_version":1,"record_type":"oolong_v58_terminal_no_gold_receipt","schedule_id":schedule["schedule_id"],"schedule_sha256":hashlib.sha256(canonical_bytes(schedule)+b"\n").hexdigest(),"inference_sha256":sha256_file(output),"rows":78,"claims":78,"done":78,"artifact_directories":78,"checkpoint":marker,"candidate_sha256":CANDIDATE_SHA256,"public_manifest_sha256":PUBLIC_MANIFEST_SHA256,"gold_sha256":GOLD_SHA256,"integrity_gate":gates["integrity_gate"],"route_gate":gates["route_gate"],"leak_gate":gates["leak_gate"],"credential_cleanup_gate":gates["credential_cleanup_gate"],"validated":True}


def deterministic_tree_identity(root: Path) -> dict[str, Any]:
    root=root.resolve();h=hashlib.sha256();count=0;total=0
    for path in sorted(root.rglob("*"),key=lambda item:item.relative_to(root).as_posix()):
        rel=path.relative_to(root).as_posix()
        if "__pycache__" in path.parts or path.suffix==".pyc" or path.name==".DS_Store":continue
        meta=path.lstat()
        if stat.S_ISLNK(meta.st_mode):
            target=os.readlink(path);h.update(b"L\\0"+rel.encode()+b"\\0"+target.encode()+b"\\n");count+=1
        elif stat.S_ISREG(meta.st_mode):
            digest=sha256_file(path);h.update(b"F\\0"+rel.encode()+b"\\0"+str(meta.st_size).encode()+b"\\0"+digest.encode()+b"\\n");count+=1;total+=meta.st_size
        elif not stat.S_ISDIR(meta.st_mode):raise V58Error(f"runtime tree has unsupported entry: {path}")
    return {"path":str(root),"tree_sha256":h.hexdigest(),"entries":count,"regular_file_bytes":total,"exclusions":["__pycache__","*.pyc",".DS_Store"]}


def current_runtime_closure(prime: Path, source_home: Path) -> dict[str, Any]:
    node_raw=shutil.which("node")
    if not node_raw:raise V58Error("node executable is unavailable")
    node=Path(node_raw).resolve();kernel_launcher=source_home/".prime"/"agent"/"kernel-venv"/"bin"/"python";kernel_python=kernel_launcher.resolve()
    if not kernel_launcher.exists():raise V58Error("kernel launcher is unavailable")
    for path,label in ((prime,"prime-agent runtime"),(node,"node runtime"),(kernel_python,"kernel python")):
        meta=path.lstat()
        if not stat.S_ISREG(meta.st_mode) or stat.S_ISLNK(meta.st_mode):raise V58Error(f"{label} is not a regular resolved file")
    def version(command:list[str])->str:
        probe=subprocess.run(command,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace",timeout=30)
        value=(probe.stdout+"\n"+probe.stderr).strip()
        if probe.returncode!=0 or not value:raise V58Error(f"runtime version probe failed: {command[0]}")
        return value
    purelib_probe=subprocess.run([str(kernel_launcher),"-c","import sysconfig; print(sysconfig.get_paths()['purelib'])"],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace",timeout=30)
    purelib=Path(purelib_probe.stdout.strip())
    if purelib_probe.returncode!=0 or not purelib.is_dir():raise V58Error("kernel purelib probe failed")
    return {"prime":{"path":str(prime),"sha256":sha256_file(prime),"bundle":deterministic_tree_identity(prime.parent)},"node":{"path":str(node),"sha256":sha256_file(node),"version":version([str(node),"--version"])},"kernel_python":{"path":str(kernel_python),"launcher_path":str(kernel_launcher),"launcher_target":os.readlink(kernel_launcher) if kernel_launcher.is_symlink() else None,"sha256":sha256_file(kernel_python),"version":version([str(kernel_launcher),"--version"]),"site_packages":deterministic_tree_identity(purelib)},"kernel":{"sysname":os.uname().sysname,"nodename":os.uname().nodename,"release":os.uname().release,"version":os.uname().version,"machine":os.uname().machine}}


def validate_rehearsal_receipt(path: Path, schedule: dict[str, Any], output: Path, work: Path, executables: dict[str, Any], source_home: Path) -> dict[str, Any]:
    receipt=load_json(path,"target-bound rehearsal receipt")
    production=Path("/private/tmp/azdaja-v58-oolong-frozen-v1")
    if output!=production/"inference.jsonl" or work!=production/"work" or receipt.get("production_root")!=str(production):
        raise V58Error("production root is not the rehearsed fixed target")
    expected={"runner_sha256":sha256_file(Path(__file__).resolve()),"adapter_sha256":sha256_file(HERE/"run.py"),"validator_sha256":sha256_file(HERE/"v58_validate.py"),"scorer_sha256":sha256_file(HERE/"v58_score.py"),"reporter_sha256":sha256_file(HERE/"v58_report.py"),"rehearsal_sha256":sha256_file(HERE/"v58_rehearsal.py"),"public_manifest_sha256":PUBLIC_MANIFEST_SHA256,"candidate_sha256":CANDIDATE_SHA256,"schedule_id":schedule["schedule_id"],"schedule_sha256":hashlib.sha256(canonical_bytes(schedule)+b"\n").hexdigest(),"model":MODEL,"reasoning":REASONING}
    for key,value in expected.items():
        if receipt.get(key)!=value:raise V58Error(f"stale/mismatched rehearsal receipt: {key}")
    if receipt.get("jcode")!=executables["jcode"] or receipt.get("prime_agent")!=executables["prime-agent"]:
        raise V58Error("rehearsal executable binding mismatch")
    if receipt.get("candidate_components")!=schedule["configuration"]["candidate"].get("components"):
        raise V58Error("rehearsal candidate component mismatch")
    prime=Path(executables["prime-agent"]["path"])
    if receipt.get("runtime_closure")!=current_runtime_closure(prime,source_home):raise V58Error("rehearsal runtime closure mismatch")
    terminal_rehearsal=receipt.get("terminal_78",{})
    if terminal_rehearsal.get("passed") is not True or terminal_rehearsal.get("independent_validation",{}).get("validated") is not True or terminal_rehearsal.get("independent_validation",{}).get("validator_sha256")!=expected["validator_sha256"] or receipt.get("abort_10")!={"passed":True,"resume_refused_before_oauth":True,"rows":10,"status":"abort"} or receipt.get("synthetic_final_gate")!={"execution_n":25,"passed":True,"strict_exact_n":24}:
        raise V58Error("rehearsal outcomes are incomplete")
    return receipt


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser()
    p.add_argument("--public-manifest",required=True);p.add_argument("--output",required=True);p.add_argument("--work-dir",required=True);p.add_argument("--azdaja-skill",required=True);p.add_argument("--jcode",required=True);p.add_argument("--prime-agent",required=True);p.add_argument("--rehearsal-receipt",required=True);p.add_argument("--resume",action="store_true");p.add_argument("--yes-run-inference",action="store_true")
    return p


def main(argv: list[str] | None=None) -> int:
    args=parser().parse_args(argv)
    if not args.yes_run_inference: raise V58Error("refusing inference without --yes-run-inference")
    suite=load_public_suite(Path(args.public_manifest));skill,candidate=validate_candidate(Path(args.azdaja_skill))
    source_home=Path(os.environ["HOME"]).resolve();jcode=legacy.ensure_executable(args.jcode,"jcode");prime=legacy.ensure_executable(args.prime_agent,"prime-agent")
    if str(Path(jcode).resolve()) != JCODE_PATH or sha256_file(Path(jcode)) != JCODE_SHA256:
        raise V58Error("Jcode path/hash is not the required v0.75.3 build")
    executables={"jcode":legacy.executable_identity(jcode,"jcode"),"prime-agent":legacy.executable_identity(prime,"prime-agent"),"azdaja":legacy.executable_identity(str(skill/"azdaja"),"azdaja")}
    schedule=build_schedule(suite,candidate,executables);output=Path(args.output).resolve();schedule_path=Path(str(output)+".schedule.json");claims_root=Path(str(output)+".claims");claims=claims_root/schedule["schedule_id"];work=Path(args.work_dir).resolve();work_runs=work/("schedule-"+schedule["schedule_id"])/"runs";checkpoint=Path(str(output)+".checkpoint.json");terminal=Path(str(output)+".terminal.json")
    validate_rehearsal_receipt(Path(args.rehearsal_receipt).resolve(),schedule,output,work,executables,source_home)
    if not args.resume:
        if output.parent.exists() or any(p.exists() for p in (output,schedule_path,claims_root,work,checkpoint,terminal)):raise V58Error("the complete fresh campaign root must not exist")
        output.parent.mkdir(mode=0o700,parents=True,exist_ok=False);claims.mkdir(mode=0o700,parents=True);work_runs.mkdir(mode=0o700,parents=True);atomic_json(schedule_path,schedule)
    else:
        require_private_dir(output.parent,"campaign root")
        frozen=load_json(schedule_path,"schedule")
        if frozen!=schedule: raise V58Error("resume schedule mismatch")
    if args.resume:recover_trailing_done(output,schedule,claims)
    rows=validate_prefix(output,schedule,claims);questions={f.fixture_id:f.question for f in suite.fixtures}
    validate_artifact_prefix(rows,schedule,work_runs)
    enforce_checkpoint_startup(rows,schedule,questions,checkpoint)
    if terminal.exists() and len(rows)!=ROW_COUNT:raise V58Error("premature terminal receipt exists; refusing before OAuth")
    if len(rows)==ROW_COUNT:
        recomputed_terminal=terminal_validate(output,schedule,claims,work_runs,checkpoint,questions)
        if terminal.exists():
            if load_json(terminal,"terminal receipt")!=recomputed_terminal:raise V58Error("existing terminal receipt mismatch")
        else:atomic_json(terminal,recomputed_terminal)
        return 1 if any(not r["execution_success"] for r in rows) else 0
    auth_jcode=legacy.preflight_jcode(source_home,jcode);auth_prime=legacy.preflight_prime(source_home);by_id={f.fixture_id:f for f in suite.fixtures};legacy.MODEL=MODEL;legacy.REASONING=REASONING
    run_args=SimpleNamespace(model=MODEL,reasoning=REASONING,timeout=TIMEOUT_SECONDS,jcode=jcode,prime_agent=prime,azdaja_skill=str(skill),work_dir=str(work),executable_identities=executables,oolong_private_frozen_suite=True,arms=list(ARMS),repetitions=1,seed=SEED)
    root=HERE.parents[1]
    for job in schedule["jobs"][len(rows):]:
        if job["ordinal"]==11 and not checkpoint.exists(): raise V58Error("control phase reached without checkpoint marker")
        if job["arm"].startswith("jcode"): auth_jcode=legacy.preflight_jcode(source_home,jcode)
        else: auth_prime=legacy.preflight_prime(source_home)
        claim_path=claims/(job["run_id"]+".json");atomic_json(claim_path,{"schedule_id":schedule["schedule_id"],"run_id":job["run_id"],"ordinal":job["ordinal"],"pid":os.getpid()})
        fixture=by_id[job["fixture_id"]]
        row=legacy.run_one(arm_name=job["arm"],repetition=1,ordinal=job["ordinal"],fixture=fixture.legacy_fixture,prompt=None,args=run_args,root=root,source_home=source_home,skill=skill,auth_jcode=auth_jcode,auth_prime=auth_prime,work_root=work_runs,defer_scoring=True,return_exact_response=True)
        response=row.pop("_exact_response",None)
        stdout_meta=row.get("trajectory_artifacts",{}).get("stdout",{})
        if not isinstance(response,str) or stdout_meta.get("exact_text_preserved") is not True:
            response="";row["execution_success"]=False;row["failure"]={"kind":"raw_output_redacted","normalized_kind":"other_execution","message":"exact raw final response could not be retained without credential redaction"}
        elif len(response.encode("utf-8"))>MAX_EXACT_RESPONSE_BYTES:
            response="";row["execution_success"]=False;row["failure"]={"kind":"response_too_large","normalized_kind":"other_execution","message":"exact final response exceeded the frozen safety limit"}
        elif row.get("execution_success") is True and response=="":
            row["execution_success"]=False;row["failure"]={"kind":"exact_response_missing","normalized_kind":"other_execution","message":"successful process had no exact final-response event"}
        row["response"]=response
        row.update({"record_type":"inference","schedule_id":schedule["schedule_id"],"run_id":job["run_id"],"fixture_id":job["fixture_id"],"row_sha256":job["row_sha256"],"context_sha256":job["context_sha256"],"candidate_sha256":CANDIDATE_SHA256,"controller_sha256":schedule["configuration"]["controller"]["sha256"],"success":None,"score":None,"scoring_status":"deferred"})
        append_row(output,row);atomic_json(claims/(job["run_id"]+".done.json"),{"schedule_id":schedule["schedule_id"],"run_id":job["run_id"],"row_sha256":hashlib.sha256(canonical_bytes(row)).hexdigest()});rows.append(row)
        if job["ordinal"]==10:
            summary=checkpoint_summary(rows,schedule,questions);atomic_json(checkpoint,{"schema_version":1,"record_type":"oolong_v58_checkpoint","schedule_id":schedule["schedule_id"],"status":"pass" if summary["passed"] else "abort","summary":summary})
            if not summary["passed"]: return 3
    atomic_json(terminal,terminal_validate(output,schedule,claims,work_runs,checkpoint,questions));return 1 if any(not r["execution_success"] for r in rows) else 0


if __name__=="__main__":
    try: raise SystemExit(main())
    except CheckpointAbort as exc:
        print(f"error: {exc}",file=sys.stderr);raise SystemExit(3)
    except (V58Error,legacy.BenchError) as exc:
        print(f"error: {exc}",file=sys.stderr);raise SystemExit(2)
