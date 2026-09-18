#!/usr/bin/env python3
"""Study-only stdin reader adapter. No retries, durable admission, no secret logging."""
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time
import urllib.request

MODEL = "anthropic/claude-sonnet-5"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def persist(path, data):
    # Readers never see a partially written result. link() preserves exclusive creation.
    fd, temporary = tempfile.mkstemp(prefix='.record-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.link(temporary, path)
        parent = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
    finally:
        os.unlink(temporary)


def totals(directory):
    results = [json.loads(p.read_text()) for p in directory.glob("*.result.json")]
    return {"attempts": len(list(directory.glob("*.intent.json"))),
            "known_input_tokens": sum(r.get("input_tokens") or 0 for r in results),
            "known_output_tokens": sum(r.get("output_tokens") or 0 for r in results),
            "known_cost": sum(r.get("cost") or 0 for r in results),
            "terminal_failure": any(r["status"] != "succeeded" or not r["usage_complete"] for r in results)}


def main():
    os.umask(0o077)
    directory = Path(os.environ["PERF_READER_LOG"])
    prompt = sys.stdin.read()
    if not prompt or len(prompt.encode()) > 262144:
        raise RuntimeError("reader_input_limit")
    with (directory / "lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        current = totals(directory)
        root_cost = float((directory.parent / "root-cost").read_text())
        if (current["attempts"] >= 160 or current["known_input_tokens"] >= 2000000
                or current["known_cost"] + root_cost >= 8 or current["terminal_failure"]
                or time.time() >= float(os.environ["PERF_DEADLINE"])):
            raise RuntimeError("reader_admission_stopped")
        index = current["attempts"]
        stem = directory / ("%04d" % index)
        persist(stem.with_suffix(".intent.json"), {"index": index, "model": MODEL,
                "prompt_sha256": digest(prompt.encode()), "prompt_bytes": len(prompt.encode()),
                "entered_at": time.time(), "request_timeout_seconds": 90})
        persist(stem.with_suffix(".prompt.json"), {"prompt": prompt})
    started = time.monotonic()
    result = {"index": index, "model": MODEL, "status": "failed", "usage_complete": False,
              "input_tokens": None, "output_tokens": None, "cost": None,
              "provider_request_id": None}
    answer = None
    try:
        # Only this provider's selected credential exists in the private copy.
        auth = json.loads(Path(os.environ["PERF_AUTH"]).read_text())["openrouter"]["key"]
        request = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps({"model": MODEL, "max_tokens": 8192, "usage": {"include": True},
                             "messages": [{"role": "user", "content": prompt}]}).encode(),
            headers={"Authorization": "Bearer " + auth, "Content-Type": "application/json"})
        remaining = max(.1, min(90, float(os.environ['PERF_DEADLINE']) - time.time()))
        with urllib.request.urlopen(request, timeout=remaining) as response:
            body = json.loads(response.read(16777216))
        usage = body.get("usage") or {}
        for source, target in (("prompt_tokens", "input_tokens"), ("completion_tokens", "output_tokens"), ("cost", "cost")):
            if number(usage.get(source)):
                result[target] = usage[source]
        result["usage_complete"] = all(result[k] is not None for k in ("input_tokens", "output_tokens", "cost"))
        result["provider_request_id"] = body.get("id")
        result["cache_usage"] = usage.get("prompt_tokens_details")
        answer = body["choices"][0]["message"]["content"]
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("invalid_visible_answer")
        result["answer_sha256"] = digest(answer.encode())
        result["status"] = "succeeded"
        # Visible completion only. Never retain provider reasoning blocks.
        persist(stem.with_suffix(".answer.json"), {"answer": answer})
    except Exception as error:
        result["error_category"] = type(error).__name__
    finally:
        result["seconds"] = time.monotonic() - started
        persist(stem.with_suffix(".result.json"), result)
    if result["status"] != "succeeded" or not result["usage_complete"]:
        print("reader_failed_or_unknown_usage; no automatic retry", file=sys.stderr)
        return 1
    sys.stdout.write(answer)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(type(error).__name__ + ": reader stopped before/at admission", file=sys.stderr)
        sys.exit(1)
