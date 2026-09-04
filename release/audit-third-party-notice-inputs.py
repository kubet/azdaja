#!/usr/bin/env python3
"""Audit source inputs for the supported-target third-party notice closure.

This manifest is source-input evidence only. It does not establish notice semantic completeness.
"""
from __future__ import annotations
import argparse, hashlib, io, json, re, subprocess, sys, tarfile
from pathlib import Path

TARGETS = ("aarch64-apple-darwin", "x86_64-apple-darwin", "x86_64-unknown-linux-gnu")
REGISTRY = "registry+https://github.com/rust-lang/crates.io-index"
TREE_RE = re.compile(r"(?P<name>[A-Za-z0-9_.+-]+) v(?P<version>[^ ]+)(?: \([^)]*\))?$")
LEGAL_RE = re.compile(r"(?:^|/)(?:LICENSE|COPYING|NOTICE)(?:[._-].*)?$")

def sha256_bytes(data): return hashlib.sha256(data).hexdigest()
def lock_records(lock):
    text = lock.read_text(encoding="utf-8"); records = {}
    for block in text.split("[[package]]")[1:]:
        fields = dict(re.findall(r'^(name|version|source|checksum) = "([^"]+)"$', block, re.M))
        if fields.get("source", "").startswith(REGISTRY):
            if set(("name", "version", "checksum")) - fields.keys(): raise ValueError("malformed registry Cargo.lock record")
            key = (fields["name"], fields["version"])
            if key in records: raise ValueError("ambiguous duplicate lock record: %s@%s" % key)
            records[key] = fields["checksum"]
    if not records: raise ValueError("no registry Cargo.lock records")
    return records

def tree_union(root):
    union = set()
    for target in TARGETS:
        p = subprocess.run(["cargo", "tree", "--locked", "--offline", "--target", target, "--edges", "normal"], cwd=root, text=True, capture_output=True, check=True)
        found = set()
        for line in p.stdout.splitlines():
            m = TREE_RE.search(line)
            if m and m.group("name") != "azdaja": found.add((m.group("name"), m.group("version")))
        if not found: raise ValueError("empty cargo tree for " + target)
        union |= found
    return union

def archive(cache, name, version, checksum):
    candidates = sorted(cache.rglob(f"{name}-{version}.crate"))
    if len(candidates) != 1: raise ValueError(f"expected one archive for {name}@{version}, found {len(candidates)}")
    data = candidates[0].read_bytes()
    if sha256_bytes(data) != checksum: raise ValueError(f"archive checksum mismatch for {name}@{version}")
    return data

def evidence(data, name, version):
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        members = {m.name: m for m in tar.getmembers()}
        prefix = f"{name}-{version}/"
        cargo = [p for p in members if p == prefix + "Cargo.toml"]
        if len(cargo) != 1: raise ValueError("missing or ambiguous Cargo.toml")
        toml = tar.extractfile(members[cargo[0]]).read().decode("utf-8")
        license_match = re.search(r'^license\s*=\s*"([^"]+)"', toml, re.M)
        file_match = re.search(r'^license_file\s*=\s*"([^"]+)"', toml, re.M)
        path = file_match.group(1) if file_match else None
        if path and (Path(path).is_absolute() or ".." in Path(path).parts or "\\" in path): raise ValueError("malformed license path")
        legal = [prefix + path] if path else [p for p, member in members.items() if p.startswith(prefix) and member.isfile() and LEGAL_RE.search(p)]
        if not legal and not license_match: raise ValueError(f"missing license evidence for {name}@{version}")
        out = []
        for item in sorted(set(legal)):
            if item not in members or not members[item].isfile(): raise ValueError("missing legal file")
            out.append({"path": item[len(prefix):], "sha256": sha256_bytes(tar.extractfile(members[item]).read())})
        return {"name": name, "version": version, "license": license_match.group(1) if license_match else None, "license_files": out}

def build(root, cache):
    locks = lock_records(root / "Cargo.lock"); union = tree_union(root)
    if not union <= set(locks): raise ValueError("cargo tree closure drift from Cargo.lock")
    packages = []
    for name, version in sorted(union):
        packages.append({"checksum": locks[(name, version)], **evidence(archive(cache, name, version, locks[(name, version)]), name, version)})
    return {"schema": "azdaja.third_party_notice_input_evidence.v1", "claim": "source-input evidence only; does not establish notice semantic completeness", "targets": list(TARGETS), "cargo_lock_sha256": sha256_bytes((root / "Cargo.lock").read_bytes()), "packages": packages}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1]); ap.add_argument("--cache", type=Path, default=Path.home()/".cargo/registry/cache"); ap.add_argument("--manifest", type=Path, default=Path(__file__).with_name("third-party-notice-inputs.json")); ap.add_argument("--check", action="store_true"); a=ap.parse_args()
    try:
        actual=build(a.root, a.cache); expected=a.manifest.read_text(encoding="utf-8") if a.manifest.exists() else None; rendered=json.dumps(actual, indent=2, sort_keys=True)+"\n"
        if a.check:
            if expected != rendered: raise ValueError("manifest is missing or differs")
        else: a.manifest.write_text(rendered, encoding="utf-8")
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError, tarfile.TarError) as e: print("third-party INPUT audit failed: "+str(e), file=sys.stderr); return 1
    return 0
if __name__ == "__main__": raise SystemExit(main())
