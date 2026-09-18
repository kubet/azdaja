#!/usr/bin/env python3
"""Rebuild the retained long-source review file. No credential or provider access."""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULTS = HERE / "results-20260918"
CORPUS = ROOT / "bench/jev/long_task/fixtures/corpus.json"
EXAMPLE = ROOT / "examples/jev_batch_review.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def replay(output):
    retention = load(HERE / "RETENTION.json")
    for name, expected in retention["files"].items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("invalid retained path")
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or sha(path) != expected:
            raise ValueError("retained artifact changed: " + name)
    receipt = load(RESULTS / "acceptance.json")
    if receipt["status"] != "passed" or receipt["native_live_summary"]["status"] != "completed":
        raise ValueError("not a completed retained job")
    if os.path.lexists(output):
        raise ValueError("output exists")
    output.mkdir(mode=0o700)
    sources = output / "sources"
    sources.mkdir(mode=0o700)
    corpus = load(CORPUS)
    files = []
    for i, doc in enumerate(corpus["contracts"]):
        path = sources / ("%03d.txt" % i)
        with path.open("xb") as f:
            f.write(doc["text"].encode("utf-8"))
        path.chmod(0o600)
        files.append(str(path))
    question = load(RESULTS / "question.json")["question"]
    spec = importlib.util.spec_from_file_location("batch_review", EXAMPLE)
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)
    example.prepare(question, output / "plan", files)
    manifest = load(RESULTS / "job/manifest.json")
    if sha(output / "plan/plan.jsonl") != manifest["binding"]["input_sha256"]:
        raise ValueError("reconstructed plan differs")
    example.report(output / "plan", RESULTS / "job", output / "review.jsonl")
    if sha(output / "review.jsonl") != receipt["review_sha256"]:
        raise ValueError("reconstructed review differs")
    rows = [json.loads(line) for line in (output / "review.jsonl").read_text().splitlines()]
    if len(rows) != receipt["completed_windows"] or any(row["status"] != "completed" for row in rows):
        raise ValueError("incomplete review")
    report = {
        "status": "replay_consistent", "new_provider_calls": 0,
        "completed_windows": len(rows), "source_files": len(files),
        "source_bytes": sum(p.stat().st_size for p in sources.iterdir()),
        "review_sha256": sha(output / "review.jsonl"),
        "historical_binary_bytes_verified": False,
        "provider_authenticity_independently_verified": False,
        "scope": "retained source/request/result binding and byte-identical review export",
    }
    with (output / "replay.json").open("x") as f:
        json.dump(report, f, sort_keys=True)
        f.write("\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = replay(args.output)
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        print("error: changed evidence or invalid/occupied output; no provider calls", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
