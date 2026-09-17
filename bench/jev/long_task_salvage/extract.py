#!/usr/bin/env python3
"""Offline extraction of existing, trace-bound leaf text. Never calls a provider."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re

COUNTS = {'generative': 75, 'optional_typed': 120}
SECRET = re.compile(r'(?:apikey_[A-Za-z0-9]+_[A-Za-z0-9]+|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|Bearer\s+[A-Za-z0-9_.-]{24,})', re.I)
SESSION_ID = re.compile(r'session_[A-Za-z0-9_-]+\Z')


class Refused(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Refused(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate_json_key')
        out[key] = value
    return out


def load(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refused('nonfinite_json')))


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def safe_file(path):
    require(path.is_absolute(), 'absolute_path_required')
    require(not any(p.is_symlink() for p in [path, *path.parents]), 'symlink_refused')
    require(path.is_file(), 'regular_file_required')
    return path.read_bytes()


def text(message, role):
    require(type(message) is dict and message.get('role') == role
            and message.get('display_role') is None, 'message_role')
    content = message.get('content')
    require(type(content) is list and content, 'message_content')
    allowed = {'text'} if role == 'user' else {'text', 'reasoning_trace', 'open_a_i_reasoning'}
    require(all(type(block) is dict and block.get('type') in allowed for block in content), 'unexpected_content_block')
    blocks = [block for block in content if block['type'] == 'text']
    require(len(blocks) == 1 and set(blocks[0]) == {'type', 'text'}, 'ambiguous_text_blocks')
    value = blocks[0]['text']
    require(type(value) is str and value, 'empty_text')
    return value


def timestamp(message):
    value = message.get('timestamp')
    require(type(value) is str, 'message_timestamp')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(parsed.tzinfo is not None, 'timezone_required')
    return parsed.timestamp() * 1000


def extract(public, private, arm):
    require(arm in COUNTS, 'unknown_arm')
    require(private.name.startswith('jev-long-recovery-private-'), 'owned_private_root_required')
    raw_trace = safe_file(public / arm / 'model-trace.jsonl')
    rows = [load(line) for line in raw_trace.splitlines() if line.strip()]
    require(all(type(row) is dict and row.get('event') == 'model_attempt'
                and type(row.get('depth')) is int and row['depth'] in (0, 1)
                and row.get('outcome') == 'succeeded' for row in rows), 'unexpected_trace_event')
    leaves = [(i, row) for i, row in enumerate(rows) if row['depth'] == 1]
    require(len(leaves) == COUNTS[arm], 'leaf_count')
    seen_sessions, seen_requests, records, order, mapping = set(), set(), {}, [], []
    for trace_index, row in leaves:
        sid, rid = row.get('session_id'), row.get('request_id')
        require(type(sid) is str and SESSION_ID.fullmatch(sid), 'session_id')
        require(type(rid) is str and rid, 'request_id')
        require(sid not in seen_sessions and rid not in seen_requests, 'duplicate_leaf_identity')
        seen_sessions.add(sid)
        seen_requests.add(rid)
        path = private / arm / 'state/jcode-api/home/sessions' / (sid + '.json')
        raw_session = safe_file(path)
        session = load(raw_session)
        require(session.get('id') == sid, 'session_identity')
        messages = session.get('messages')
        require(type(messages) is list and len(messages) >= 3, 'session_messages')
        # Bootstrap system text is stored as a user/display_role=system message.
        # Never export it. Every other turn must match a public trace event.
        require(messages[0].get('role') == 'user' and messages[0].get('display_role') == 'system', 'bootstrap_role')
        associated = [event for event in rows if event.get('session_id') == sid]
        require(len(messages) == 1 + 2 * len(associated), 'unbound_session_turns')
        require(associated[-1] is row and all(event['depth'] == 0 for event in associated[:-1]), 'ambiguous_leaf_turn')
        for ordinal, event in enumerate(associated):
            user, assistant = messages[1 + ordinal * 2:3 + ordinal * 2]
            text(user, 'user')
            text(assistant, 'assistant')
            user_time, assistant_time = timestamp(user), timestamp(assistant)
            end = event.get('timestamp_ms')
            require(type(end) is int and user_time <= assistant_time <= end
                    and end - assistant_time <= 1000, 'trace_turn_time_binding')
        prompt = text(messages[-2], 'user')
        response = text(messages[-1], 'assistant')
        prompt_hash, response_hash = sha(prompt.encode()), sha(response.encode())
        occurrence = {'trace_index': trace_index, 'request_id': rid, 'session_id': sid,
                      'session_file_sha256': sha(raw_session)}
        if prompt_hash in records:
            require(records[prompt_hash]['prompt'] == prompt and records[prompt_hash]['response'] == response,
                    'conflicting_duplicate_prompt')
        else:
            records[prompt_hash] = {'prompt': prompt, 'response': response,
                                    'response_sha256': response_hash, 'occurrences': []}
        records[prompt_hash]['occurrences'].append(occurrence)
        order.append(prompt_hash)
        mapping.append({'prompt_sha256': prompt_hash, **occurrence})
    result = {'schema': 'azdaja.long_task.existing_leaf_text.v1', 'arm': arm,
              'model_trace_sha256': sha(raw_trace), 'leaf_count': len(leaves),
              'unique_prompt_count': len(records), 'records': records,
              'trace_order': order, 'trace_mapping': mapping,
              'prompt_policy': 'Exact final user text, including any protocol wrapper. No stripping or reconstruction.',
              'response_policy': 'Exact final assistant text block only. No reasoning, bootstrap text, or other session metadata.',
              'provider_calls': 0}
    require(not SECRET.search(canonical(result).decode()), 'secret_shaped_output_refused')
    return result


def save(path, bundle):
    raw = canonical(bundle)
    require(not SECRET.search(raw.decode()), 'secret_shaped_output_refused')
    require(path.is_absolute() and path.parent.is_dir()
            and not any(p.is_symlink() for p in path.parents), 'output_path')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return sha(raw)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public', type=Path, required=True)
    parser.add_argument('--private', type=Path, required=True)
    parser.add_argument('--arm', choices=COUNTS, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    result = extract(args.public, args.private, args.arm)
    digest = save(args.output, result)
    print(json.dumps({'arm': args.arm, 'output': str(args.output), 'sha256': digest,
                      'leaf_count': result['leaf_count'], 'unique_prompt_count': result['unique_prompt_count'], 'provider_calls': 0}))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'refused', 'reason': str(error) if isinstance(error, Refused) else type(error).__name__}))
        raise SystemExit(2)
