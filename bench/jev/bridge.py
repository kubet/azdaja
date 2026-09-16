"""Offline, real-Azdaja custody and occurrence-accounting probe.

This does not establish semantic correctness or task-wide evidence completeness.
No provider is enabled. The evaluator, not the host, verifies hashes and joins.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import tempfile

try:
    from .adapter import canonical_bytes, strict_json_loads
except ImportError:
    from adapter import canonical_bytes, strict_json_loads

LABELS = ("supported", "contradicted", "insufficient")
HEX = re.compile(r"[0-9a-f]{64}\Z")
MAX_SOURCE_BYTES = 1024 * 1024
MAX_RECORDS = 256

# Only evaluator-supported Python. json and sha256 are Azdaja native bindings.
# Host validation below checks shapes, not the relational assertions in this cell.
CELL = '''s = json.loads(source)
m = json.loads(manifest)
source_hash = sha256(source)
assert source_hash == m["source_sha256"], "source hash mismatch"
by_id = {}
for entry in m["entries"]:
    cid = entry["case_id"]
    assert cid not in by_id, "duplicate manifest entry"
    by_id[cid] = entry
seen_raw = {}
ledger = []
missing = []
raw_counts = {"supported": 0, "contradicted": 0, "insufficient": 0, "unjudged": 0}
accepted_counts = {"supported": 0, "contradicted": 0, "insufficient": 0}
for i in range(len(s)):
    row = s[i]
    assert row["occurrence"] == i, "source order mismatch"
    cid = row["case_id"]
    raw = row["raw"]
    payload_hash = sha256(raw)
    if cid in seen_raw:
        assert seen_raw[cid] == raw, "duplicate content changed"
    seen_raw[cid] = raw
    label = "unjudged"
    accepted = False
    if cid in by_id:
        entry = by_id[cid]
        assert payload_hash == entry["payload_sha256"], "payload hash mismatch"
        label = entry["label"]
        accepted = entry["accepted"]
    else:
        missing.append(i)
    raw_counts[label] += 1
    if accepted:
        accepted_counts[label] += 1
    ledger.append({"occurrence": i, "case_id": cid, "payload_sha256": payload_hash,
                   "label": label, "accepted": accepted})
for cid in by_id:
    assert cid in seen_raw, "extra manifest entry"
assert audit_only or len(missing) == 0, "incomplete judgment"
assert sum(raw_counts.values()) == len(s), "occurrence accounting mismatch"
FINAL({"source_sha256": source_hash, "complete": len(missing) == 0,
       "occurrences": len(s), "unique_judged": len(by_id),
       "unjudged_occurrences": missing, "raw_counts": raw_counts,
       "accepted_counts": accepted_counts, "ledger": ledger})
'''


def _validate(source, manifest):
    """Shape and resource checks only. Custody relationships run inside Monty."""
    if not isinstance(source, list) or len(source) > MAX_RECORDS:
        raise ValueError("invalid source list")
    if (not isinstance(manifest, dict)
            or set(manifest) != {"schema_version", "source_sha256", "entries"}
            or type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1
            or not isinstance(manifest["source_sha256"], str)
            or not HEX.fullmatch(manifest["source_sha256"])):
        raise ValueError("invalid manifest")
    if not isinstance(manifest["entries"], list) or len(manifest["entries"]) > MAX_RECORDS:
        raise ValueError("invalid entries")
    for row in source:
        if (not isinstance(row, dict) or set(row) != {"occurrence", "case_id", "raw"}
                or type(row["occurrence"]) is not int or row["occurrence"] < 0
                or not isinstance(row["case_id"], str) or not 1 <= len(row["case_id"]) <= 128
                or not isinstance(row["raw"], str)):
            raise ValueError("invalid source row")
    for entry in manifest["entries"]:
        if (not isinstance(entry, dict)
                or set(entry) != {"case_id", "payload_sha256", "label", "accepted"}
                or not isinstance(entry["case_id"], str) or not 1 <= len(entry["case_id"]) <= 128
                or not isinstance(entry["payload_sha256"], str)
                or not HEX.fullmatch(entry["payload_sha256"])
                or entry["label"] not in LABELS or type(entry["accepted"]) is not bool):
            raise ValueError("invalid judgment")


def _run(binary, args, home, config, stdin=""):
    # Do not inherit credentials, proxy configuration, Python hooks, or live providers.
    env = {"PATH": "/usr/bin:/bin", "HOME": str(home), "TMPDIR": str(home.parent),
           "AZDAJA_HOME": str(home), "AZDAJA_CONFIG": str(config), "RLM_DEPTH": "0"}
    try:
        result = subprocess.run([str(binary), *args], input=stdin.encode("utf-8"),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=env, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError("offline evaluator process failed") from None
    if len(result.stdout) > 262144 or len(result.stderr) > 262144:
        raise ValueError("offline evaluator output exceeded limit")
    return result


def _private_write(path, content):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
        handle.write(content)


def evaluate(azdaja: Path, source_text: str, manifest: dict, scratch: Path,
             audit_only: bool = False) -> dict:
    if type(audit_only) is not bool:
        raise ValueError("invalid audit mode")
    if not isinstance(source_text, str) or len(source_text.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError("source size exceeded")
    source = strict_json_loads(source_text)
    _validate(source, manifest)
    manifest_text = canonical_bytes(manifest).decode("utf-8")
    if len(manifest_text.encode("utf-8")) > 262144:
        raise ValueError("manifest size exceeded")
    binary = azdaja.resolve(strict=True)
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="jev-custody-", dir=scratch) as tmp:
        root = Path(tmp)
        home = root / "home"
        home.mkdir(mode=0o700)
        config = root / "config.toml"
        _private_write(config, "sub_llm_cmd = '/usr/bin/false'\ndefault_model = 'offline-custody'\n"
                       "output_cap = 262144\ncell_timeout = 10\nmax_calls_per_cell = 1\n"
                       "max_depth = 1\nmax_sessions = 1\nclean_patterns = []\n")
        source_path, manifest_path = root / "source.json", root / "manifest.json"
        _private_write(source_path, source_text)
        _private_write(manifest_path, manifest_text)
        started = _run(binary, ["start"], home, config)
        if started.returncode != 0:
            raise ValueError("offline evaluator start failed")
        sid = started.stdout.decode("utf-8").strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", sid):
            raise ValueError("invalid offline session identifier")
        try:
            for path, name in ((source_path, "source"), (manifest_path, "manifest")):
                loaded = _run(binary, ["load", sid, str(path), name], home, config)
                if loaded.returncode != 0:
                    raise ValueError("offline evaluator load failed")
            executed = _run(binary, ["exec", sid], home, config,
                            "audit_only = " + str(audit_only) + "\n" + CELL)
            if executed.returncode != 0:
                raise ValueError("evaluator rejected custody")
            final = _run(binary, ["final", sid], home, config)
            if final.returncode != 0:
                raise ValueError("offline evaluator final missing")
            result = strict_json_loads(final.stdout)
            if not isinstance(result, dict):
                raise ValueError("offline evaluator final invalid")
            return result
        finally:
            killed = _run(binary, ["kill", sid], home, config)
            if killed.returncode != 0:
                raise ValueError("offline evaluator cleanup failed")
