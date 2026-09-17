#!/usr/bin/env python3
"""Exact local response lookup only. This program contains no network client."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('used', type=Path)
    args = parser.parse_args(argv)
    bundle = json.loads(args.bundle.read_bytes(), object_pairs_hook=unique)
    prompt = sys.stdin.buffer.read()
    key = sha(prompt)
    if prompt == bundle['root_prompt'].encode('utf-8'):
        reply = bundle['root_reply'].encode('utf-8')
        kind = 'retained_program_with_hash_only_correction'
    else:
        row = bundle['leaves'].get(key)
        if row is None or row['prompt'].encode('utf-8') != prompt:
            raise ValueError('unmatched retained leaf prompt')
        reply = row['reply'].encode('utf-8')
        if sha(reply) != row['reply_sha256']:
            raise ValueError('retained reply hash mismatch')
        kind = 'exact_retained_leaf_reply'
    # One file per expected unique prompt. Exclusive creation refuses any extra
    # evaluation or retry rather than returning a response twice unnoticed.
    record = {'prompt_sha256': key, 'reply_sha256': sha(reply), 'kind': kind,
              'new_provider_calls': 0}
    fd = os.open(args.used / (key + '.json'), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(record, stream, sort_keys=True)
    sys.stdout.buffer.write(reply)
    sys.stdout.buffer.flush()
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError):
        print('exact retained response lookup refused', file=sys.stderr)
        raise SystemExit(2)
