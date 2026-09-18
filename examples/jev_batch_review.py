#!/usr/bin/env python3
"""Prepare exact long-file windows and export native batch results for review.

No inference, embeddings, automatic approval, or confidence threshold lives here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import sys

MAX_STATE_BYTES = 64 * 1024
MAX_PLAN_BYTES = 64 * 1024 * 1024
MAX_SOURCE_BYTES = MAX_PLAN_BYTES
MAX_QUESTION_BYTES = 4096
WARNING = "Answer using only this source window; do not infer or use information outside it."


def _fresh_dir(path):
    path.mkdir(mode=0o700, parents=False)
    os.chmod(path, 0o700)


def _bytes(path, limit=MAX_PLAN_BYTES):
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as handle:
        before = os.fstat(handle.fileno())
        current = os.lstat(path)
        if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(current.st_mode) or (before.st_dev, before.st_ino) != (current.st_dev, current.st_ino):
            raise ValueError("input is not a bound regular file")
        if before.st_size > limit:
            raise ValueError("input exceeds size limit")
        data = handle.read(limit + 1)
        after = os.fstat(handle.fileno())
        current = os.lstat(path)
        if len(data) > limit or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) or stat.S_ISLNK(current.st_mode) or (after.st_dev, after.st_ino) != (current.st_dev, current.st_ino):
            raise ValueError("input changed while reading")
        return data


def _regular_bytes(path):
    data = _bytes(path, MAX_SOURCE_BYTES)
    if not data or b"\0" in data:
        raise ValueError("source is empty or binary")
    data.decode("utf-8")
    return data


def _create_private(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _no_dupes(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _loads(data):
    return json.loads(data, object_pairs_hook=_no_dupes, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def _json(path):
    return _loads(_bytes(path))


def _encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _request(source_sha, source_name, start, end, text, question):
    return {"id": "", "state": {"source_sha256": source_sha, "source_name": source_name, "start_byte": start, "end_byte": end, "text": text}, "questions": {"match": {"type": "noul", "instructions": question + "\n\n" + WARNING}}}


def prepare(question, output, files):
    if not isinstance(question, str) or not question.strip() or len(question.encode("utf-8")) > MAX_QUESTION_BYTES:
        raise ValueError("question must contain 1..4096 UTF-8 bytes")
    if not files:
        raise ValueError("no source files")
    _fresh_dir(output)
    records, metadata, seen = [], [], set()
    plan_size = 0
    try:
        for fi, raw in enumerate(files):
            path = Path(raw)
            resolved = path.resolve(strict=True)
            if resolved in seen:
                raise ValueError("duplicate source path")
            seen.add(resolved)
            data = _regular_bytes(path)
            source_sha = hashlib.sha256(data).hexdigest()
            # Names, not local absolute paths, are sent to the service.
            metadata.append({"source_index": fi, "source_name": path.name, "source_sha256": source_sha, "size_bytes": len(data)})
            start, ci = 0, 0
            while start < len(data):
                ident = f"{fi:06d}-{ci:06d}"
                base = _request(source_sha, path.name, start, len(data), "", question)
                base["id"] = ident
                budget = MAX_STATE_BYTES - len(_encode(base)) - 1
                end = min(len(data), start + MAX_STATE_BYTES)
                while end < len(data) and data[end] & 0xC0 == 0x80:
                    end -= 1
                raw_size, encoded_size = 0, 0
                # One linear pass. JSON escaping cost is known exactly.
                for character in data[start:end].decode("utf-8"):
                    size = len(character.encode("utf-8"))
                    escaped = 2 if character in '\\"\b\f\n\r\t' else (6 if ord(character) < 32 else size)
                    if encoded_size + escaped > budget:
                        break
                    raw_size += size
                    encoded_size += escaped
                end = start + raw_size
                if end <= start:
                    raise ValueError("cannot fit source character in request")
                if end < len(data):
                    newline = data.rfind(b"\n", start + 1, end)
                    if newline >= start + 1:
                        end = newline + 1
                request = _request(source_sha, path.name, start, end, data[start:end].decode("utf-8"), question)
                request["id"] = ident
                encoded = _encode(request) + b"\n"
                if len(encoded) > MAX_STATE_BYTES:
                    raise ValueError("serialized request bound violated")
                plan_size += len(encoded)
                if plan_size > MAX_PLAN_BYTES or len(records) >= 10000:
                    raise ValueError("plan exceeds bounded batch size")
                records.append(encoded)
                start, ci = end, ci + 1
        _create_private(output / "plan.jsonl", b"".join(records))
        _create_private(output / "sources.json", _encode(metadata) + b"\n")
    except BaseException:
        # Only these two files in our exclusively created directory are ours.
        for name in ("plan.jsonl", "sources.json"):
            try:
                (output / name).unlink()
            except FileNotFoundError:
                pass
        output.rmdir()
        raise


def _plan_rows(plan):
    data = _bytes(plan / "plan.jsonl")
    rows = [_loads(line) for line in data.splitlines()]
    sources = _json(plan / "sources.json")
    if not rows or not sources:
        raise ValueError("empty plan")
    cursor = 0
    for fi, source in enumerate(sources):
        if type(source["source_index"]) is not int or source["source_index"] != fi or type(source["size_bytes"]) is not int:
            raise ValueError("invalid source order")
        digest, offset, ci = hashlib.sha256(), 0, 0
        while cursor < len(rows) and rows[cursor]["id"].startswith(f"{fi:06d}-"):
            row = rows[cursor]
            s = row["state"]
            if set(row) != {"id", "state", "questions"} or set(s) != {"source_sha256", "source_name", "start_byte", "end_byte", "text"}:
                raise ValueError("invalid generated plan schema")
            text = s["text"].encode("utf-8")
            if row["id"] != f"{fi:06d}-{ci:06d}" or type(s["start_byte"]) is not int or type(s["end_byte"]) is not int or s["start_byte"] != offset or s["end_byte"] != offset + len(text) or not text or s["source_sha256"] != source["source_sha256"] or s["source_name"] != source["source_name"]:
                raise ValueError("plan source coverage mismatch")
            digest.update(text)
            offset += len(text)
            ci, cursor = ci + 1, cursor + 1
        if ci == 0 or offset != source["size_bytes"] or digest.hexdigest() != source["source_sha256"]:
            raise ValueError("plan source bytes/hash mismatch")
    if cursor != len(rows):
        raise ValueError("unaccounted source windows")
    return data, rows


def report(plan, job, output):
    if output.exists() or output.is_symlink():
        raise ValueError("output already exists")
    plan_bytes, rows = _plan_rows(plan)
    manifest = _json(job / "manifest.json")
    binding = manifest["binding"]
    if manifest["schema"] != "azdaja.judge_batch.job.v1" or binding["input_sha256"] != hashlib.sha256(plan_bytes).hexdigest() or len(binding["requests"]) != len(rows):
        raise ValueError("job input binding mismatch")
    result = []
    for index, row in enumerate(rows):
        request_sha = _canonical_hash({"model": binding["config"]["model"], "state": row["state"], "questions": row["questions"]})
        expected = {"schema": "azdaja.judge_batch.intent.v1", "index": index, "id": row["id"], "request_sha256": request_sha}
        if binding["requests"][index] != {"id": row["id"], "request_sha256": request_sha}:
            raise ValueError("manifest request binding mismatch")
        intent_path, result_path = job / f"{index:06d}.intent.json", job / f"{index:06d}.result.json"
        has_intent = os.path.lexists(intent_path)
        if has_intent:
            actual_intent = _json(intent_path)
            if actual_intent != expected or type(actual_intent["index"]) is not int:
                raise ValueError("intent mismatch")
        status, probability, answer = "unknown_inflight" if has_intent else "pending", None, None
        if os.path.lexists(result_path):
            item = _json(result_path)
            if not has_intent or item["schema"] != "azdaja.judge_batch.result.v1" or item["intent"] != expected or type(item["intent"]["index"]) is not int:
                raise ValueError("result intent mismatch")
            if item["status"] == "failed" and item["observation"] is None:
                status = "unknown"
            elif item["status"] == "completed":
                observation = item["observation"]
                if observation["_azdaja"]["request_sha256"] != request_sha or set(observation["answers"]) != {"match"}:
                    raise ValueError("observation binding mismatch")
                answer = observation["answers"]["match"]
                probability = answer["noul"]
                if answer["type"] != "noul" or type(probability) not in (int, float) or not math.isfinite(probability) or not 0 <= probability <= 1:
                    raise ValueError("invalid probability")
                status = "completed"
            else:
                raise ValueError("invalid result status")
        state = row["state"]
        result.append({"id": row["id"], "status": status, "p": probability, "raw_answer": answer, **state})
    _create_private(output, b"".join(_encode(row) + b"\n" for row in result))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--question", required=True)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("files", nargs="+")
    r = sub.add_parser("report")
    r.add_argument("--plan", required=True, type=Path)
    r.add_argument("--job", required=True, type=Path)
    r.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            prepare(args.question, args.output, args.files)
        else:
            report(args.plan, args.job, args.output)
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        print("error: invalid, changed, unsafe or occupied input/output; nothing was sent to a provider", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
