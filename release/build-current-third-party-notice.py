#!/usr/bin/env python3
"""Deterministic offline current notices. Reuse the audited Cargo/archive readers."""
from __future__ import annotations

import argparse
import importlib.util
import io
import re
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC = importlib.util.spec_from_file_location("audit", HERE / "audit-third-party-notice-inputs.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)
TARGETS = audit.TARGETS
FEATURES = ("default", "typesafe")
HISTORICAL = "release/historical/THIRD-PARTY-NOTICES-pre-v0.1.17.md"
HISTORICAL_SHA256 = "393cfd092b543059d376b96134e7dadf2da5e2f5e76df84d9edbca42d22f62d2"
HISTORY_HEADING = "## Historical supplemental attributions (not current-scope evidence)"


def feature_closures(root, root_name, feature):
    if feature == "default":
        return audit.tree_closures(root, root_name)
    result = {}
    for target in TARGETS:
        command = ["cargo", "tree", "--locked", "--offline", "--target", target,
                   "--prefix", "none", "--format", "{p}", "--features", feature]
        result[target] = audit.parse_tree(
            subprocess.check_output(command, cwd=root, text=True), root_name)
    return result


def historical_supplement(root):
    path = root / HISTORICAL
    if path.is_symlink() or audit.sha256_bytes(path.read_bytes()) != HISTORICAL_SHA256:
        raise ValueError("historical notice original-byte hash mismatch")
    text = path.read_bytes().decode("utf-8")
    # These are framed records in a frozen Markdown artifact, not source/TOML parsing.
    # Preserve every non-named-file record, including embedded and supplemental terms.
    pattern = re.compile(
        r'^<a id="(?:additive-)?text-[0-9a-f]{64}"></a>\n'
        r'(?P<record>#{3,4} (?:Additive text|Text) `[0-9a-f]{64}`\n'
        r'.*?^- Kind\(s\): `(?P<kind>[^`]+)`\n.*?'
        r'^(?P<fence>`{4,5})text\n.*?^(?P=fence)\n)', re.M | re.S)
    matches = list(pattern.finditer(text))
    if len(matches) != text.count("- Kind(s): "):
        raise ValueError("historical attribution framing mismatch")
    retained = [m.group(0) for m in matches
                if m.group("kind") not in ("archive_named_legal_file", "named_legal_file")]
    return "\n".join(retained)


def build(root=ROOT, cache=None):
    cache = cache or Path.home() / ".cargo/registry/cache"
    history = historical_supplement(root)
    records = audit.lock_records(root / "Cargo.lock")
    root_name = audit.root_package_name(root)
    closures = {feature: feature_closures(root, root_name, feature) for feature in FEATURES}
    unions = {feature: set().union(*targets.values()) for feature, targets in closures.items()}
    union = set().union(*unions.values())
    missing = union - records.keys()
    if missing:
        raise ValueError(f"Cargo target closure drifts from registry lock records: {sorted(missing)}")
    packages, bodies = [], {}
    for name, version in sorted(union):
        record = records[(name, version)]
        data = audit.find_archive(cache, name, version, record["checksum"])
        evidence = audit.archive_evidence(data, name, version)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            for legal in evidence["license_files"]:
                raw = archive.extractfile(f"{name}-{version}/{legal['path']}").read()
                # UTF-8 round trips exactly, including CRLF, trailing LF, and BOM.
                text = raw.decode("utf-8")
                crlf = raw.count(b"\r\n")
                bodies[legal["sha256"]] = {
                    "bytes": len(raw), "text": text, "encoding": "UTF-8",
                    "line_endings": {"crlf": crlf, "lf": raw.count(b"\n") - crlf,
                                     "cr": raw.count(b"\r") - crlf},
                    "ends_with_lf": raw.endswith(b"\n"),
                }
        packages.append({**evidence, **record, "archive_sha256": audit.sha256_bytes(data),
                         "membership": {f: [t for t in TARGETS if (name, version) in closures[f][t]]
                                        for f in FEATURES}})
    version = audit.toml_string(audit.package_section((root / "Cargo.toml").read_text()), "version")
    return {
        "schema": "azdaja.third_party_notice_current.v3",
        "claim": "source-backed engineering evidence; not legal-sufficiency approval",
        "version": version,
        "features": list(FEATURES), "targets": list(TARGETS),
        "cargo_lock_sha256": audit.sha256_bytes((root / "Cargo.lock").read_bytes()),
        "cargo_manifest_sha256": audit.sha256_bytes((root / "Cargo.toml").read_bytes()),
        "feature_union_records": {f: len(unions[f]) for f in FEATURES},
        "target_counts": {f: {t: len(closures[f][t]) for t in TARGETS} for f in FEATURES},
        "supported_union_records": len(packages),
        "named_legal_files": sum(len(p["license_files"]) for p in packages),
        "historical": {"path": HISTORICAL, "sha256": HISTORICAL_SHA256,
                       "supplement_sha256": audit.sha256_bytes(history.encode("utf-8"))},
        "packages": packages, "bodies": bodies,
    }


def render(doc, root=ROOT):
    lines = ["# Azdaja third-party notices", "",
             f"**Candidate:** Azdaja v{doc['version']} public content snapshot",
             "**Supported release targets:** " + ", ".join(f"`{t}`" for t in doc["targets"]),
             "**Feature scope:** `default` and default + `typesafe`, separately qualified below.",
             "**Engineering status:** deterministic archive-derived corpus; not legal advice or legal-sufficiency approval.",
             "", f"- Bound inputs: `Cargo.lock` SHA-256 `{doc['cargo_lock_sha256']}`",
             f"- Cargo.toml SHA-256 `{doc['cargo_manifest_sha256']}`", "",
             "The root package is excluded. Each feature/target closure is resolved by offline, locked Cargo tree.",
             "Named legal files and declared license-file paths are inventoried from checksum-verified archives.",
             "Packaged declarations are verbatim, not rewritten as SPDX. Packages with no named legal file are explicitly listed below.",
             "This inventory is not a new audit of every source header or a claim of legal completeness.",
             "", "## Current feature-qualified package union", "",
             "| Package | Version | Exact packaged declaration | default targets | typesafe targets | Archive SHA-256 |",
             "|---|---:|---|---|---|---|"]
    for p in doc["packages"]:
        memberships = ["<br>".join(f"`{t}`" for t in p["membership"][f]) or "(absent)" for f in FEATURES]
        declaration = p['license'] if p['license'] is not None else '(no license expression)'
        lines.append(f"| `{p['name']}` | `{p['version']}` | `{declaration}` | " + " | ".join(memberships) + f" | `{p['archive_sha256']}` |")
    counts = doc["feature_union_records"]
    lines += ["", f"**Exact count:** default {counts['default']}; typesafe {counts['typesafe']}; "
              f"combined {doc['supported_union_records']} current package records; {doc['named_legal_files']} named legal-file occurrences.",
              "", "## Packages with no supplied named legal file", "",
              "These declarations do not substitute for supplied legal text or establish that no other obligations exist.", ""]
    for p in doc["packages"]:
        if not p["license_files"]:
            lines.append(f"- `{p['name']} {p['version']}`: `{p['license']}` (manifest declaration only).")
    lines += ["", "## Supplied legal files (deduplicated bodies)", "",
              "The machine index `release/current-third-party-notice.json` is authoritative for exact source bytes:",
              "UTF-8 encode each body text without newline conversion; occurrences reference its SHA-256 key.",
              "Rendering converts CRLF and lone CR to LF. All source trailing newlines are retained; when absent,",
              "one framing LF is added before the closing fence. Fences and framing LF are not source bytes.", ""]
    for digest, body in sorted(doc["bodies"].items()):
        text = body["text"].replace("\r\n", "\n").replace("\r", "\n")
        fence = "`" * max(3, 1 + max((len(m.group()) for m in re.finditer(r"`+", text)), default=0))
        lines += [f"### Body `{digest}`", "",
                  f"Source bytes: `{body['bytes']}`; source SHA-256 `{digest}`; "
                  f"line endings: `{body['line_endings']}`; ends with LF: `{str(body['ends_with_lf']).lower()}`.",
                  "", fence + "text\n" + text + ("" if text.endswith("\n") else "\n") + fence, ""]
    lines += ["## Occurrence attribution index", ""]
    for p in doc["packages"]:
        for legal in p["license_files"]:
            lines.append(f"- `{p['name']} {p['version']}` / `{legal['path']}` -> body `{legal['sha256']}` ({legal['bytes']} source bytes)")
    lines += ["", HISTORY_HEADING, "",
              f"The full former root notice is retained unchanged at [{HISTORICAL}]({HISTORICAL}).",
              f"Original SHA-256: `{HISTORICAL_SHA256}`. It contains historical scope/binding claims, not current ones.",
              "The following header, marker, embedded, supplemental, and font records are carried forward verbatim",
              "from that historical artifact. Named-file inventory does not supersede these attributions.",
              "They have NOT been re-audited as current or complete. Historical package/version/path labels are preserved.",
              "Their historical exact-byte claims are not new source verification claims. Current named-file normalization",
              "rules above do not reinterpret these frozen historical renderings.", "", historical_supplement(root)]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path.home() / ".cargo/registry/cache")
    parser.add_argument("--output", type=Path, default=HERE / "current-third-party-notice.json")
    parser.add_argument("--notice", type=Path, default=ROOT / "THIRD-PARTY-NOTICES.md")
    args = parser.parse_args()
    doc = build(ROOT, args.cache)
    audit.write_atomic(args.output, audit.render(doc))
    audit.write_atomic(args.notice, render(doc))


if __name__ == "__main__":
    main()
