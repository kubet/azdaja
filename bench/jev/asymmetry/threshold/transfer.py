"""Apply the already-committed row645-only threshold once, with overlap accounting."""
import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import unicodedata

from bench.jev.angle_lab import native as n
from bench.jev.asymmetry.threshold import train
from bench.jev.row651_labels import audit as headline

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FREEZE = HERE / 'training-freeze.json'
FREEZE_SHA = '8239f182ff7ea3b0263ecc02eb9cfeb22f1e8b10943230f655f96261df05f50f'
FREEZE_COMMIT = 'cdbbd0e'
TRAIN_SOURCE = ROOT / 'bench/oolong/context-131072.txt'


def frozen_policy():
    raw = FREEZE.read_bytes()
    if n.sha(raw) != FREEZE_SHA:
        raise ValueError('training freeze changed')
    commit = subprocess.check_output(['git', 'rev-parse', FREEZE_COMMIT], cwd=ROOT, text=True).strip()
    committed = subprocess.check_output(['git', 'cat-file', 'blob',
        commit + ':bench/jev/asymmetry/threshold/training-freeze.json'], cwd=ROOT)
    if raw != committed:
        raise ValueError('freeze is not the committed pre-transfer bytes')
    freeze = n.strict_loads(raw)
    for value in freeze['training_inputs'].values():
        if n.sha(Path(value['path']).read_bytes()) != value['sha256']:
            raise ValueError('frozen training input changed')
    rows = train.load_training_rows(train.DEFAULT_RESULT)
    selected, candidates = train.select(rows)
    if freeze['selection']['selected'] != selected or freeze['selection']['candidates'] != candidates:
        raise ValueError('training selection does not replay')
    return commit, freeze, rows


def text_message(raw):
    text = raw.decode('utf-8') if isinstance(raw, bytes) else raw
    if 'Instance:' not in text:
        raise ValueError('source record lacks Instance marker')
    return text.split('Instance:', 1)[1].strip()


def normalized_message(raw):
    return ' '.join(unicodedata.normalize('NFKC', text_message(raw)).casefold().split())


def confusion(rows, cents):
    threshold = cents / 100
    if type(cents) is not int or not 0 <= cents <= 100:
        raise ValueError('threshold domain')
    seen = set()
    for r in rows:
        if type(r.get('id')) is not str or r['id'] in seen or type(r.get('gold_ham')) is not bool:
            raise ValueError('row identity or gold')
        seen.add(r['id'])
        p = r.get('p_ham')
        if type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1:
            raise ValueError('probability domain')
    fp = [r['id'] for r in rows if r['p_ham'] >= threshold and not r['gold_ham']]
    fn = [r['id'] for r in rows if r['p_ham'] < threshold and r['gold_ham']]
    gold = sum(r['gold_ham'] for r in rows)
    positives = sum(r['p_ham'] >= threshold for r in rows)
    return {'n': len(rows), 'threshold_cents': cents, 'gold_ham': gold, 'predicted_ham': positives,
            'false_positives': len(fp), 'false_negatives': len(fn),
            'correct': len(rows) - len(fp) - len(fn),
            'accuracy': (len(rows) - len(fp) - len(fn)) / len(rows) if rows else None,
            'signed_count_error': positives - gold, 'absolute_count_error': abs(positives - gold),
            'false_positive_ids': fp, 'false_negative_ids': fn}


def evaluate(commit, freeze, training):
    # This is the first headline-data access in the transfer path, after the freeze guard.
    official = headline.audit()
    rows = official['occurrence_ledger']
    source = headline.prepare.SOURCE.read_bytes()
    train_source = TRAIN_SOURCE.read_bytes()
    train_result = n.strict_loads(train.DEFAULT_RESULT.read_bytes())
    if n.sha(train_source) != train_result['unlabeled_context_sha256']:
        raise ValueError('training source changed')
    lines = train_source.splitlines(keepends=True)
    full, texts, norms = set(), set(), set()
    for row in training:
        raw = lines[int(row['id'][1:]) - 1]
        if n.sha(raw) != row['source_sha256']:
            raise ValueError('training occurrence source differs')
        full.add(n.sha(raw)); texts.add(n.sha(text_message(raw).encode()))
        norms.add(n.sha(normalized_message(raw).encode()))
    groups = {'exact_record_overlap': [], 'exact_message_overlap': [],
              'normalized_message_overlap': [], 'normalized_message_unseen': []}
    enriched = []
    for r in rows:
        raw = source[r['byte_start']:r['byte_end']]
        if n.sha(raw) != r['record_sha256']:
            raise ValueError('headline occurrence source differs')
        overlap = {'exact_record_overlap': n.sha(raw) in full,
                   'exact_message_overlap': n.sha(text_message(raw).encode()) in texts,
                   'normalized_message_overlap': n.sha(normalized_message(raw).encode()) in norms}
        for key, present in overlap.items():
            if present:
                groups[key].append(r)
        if not overlap['normalized_message_overlap']:
            groups['normalized_message_unseen'].append(r)
        enriched.append(dict(r, **overlap))
    cents = freeze['selection']['selected']['threshold_cents']
    scores = {key: {'original': confusion(group, 50), 'transferred': confusion(group, cents)}
              for key, group in {'all': rows, **groups}.items()}
    return {'schema': 'azdaja.asymmetry.threshold_transfer.v1', 'provider_calls': 0,
            'freeze_commit': commit, 'freeze_sha256': FREEZE_SHA,
            'training_threshold_cents': cents, 'threshold_tuned_on_headline': False,
            'post_hoc_coordinator_had_seen_headline_result': True,
            'full_headline_retains_all_overlaps': True, 'scores': scores,
            'overlap': {'training_occurrences': len(training), 'training_unique_full_records': len(full),
                        'training_unique_exact_messages': len(texts), 'training_unique_normalized_messages': len(norms),
                        'counts': {key: len(group) for key, group in groups.items()},
                        'normalization': 'Instance field only, NFKC, casefold, split/join whitespace; no labels'},
            'input_hashes': {'row651_verified_audit': n.sha(n.canonical(official)),
                             'row645_source': n.sha(train_source), 'row651_source': n.sha(source)},
            'occurrence_ledger': enriched}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--replay', action='store_true', help='Verify an existing fixed-policy result, not reselect a threshold.')
    args = p.parse_args()
    commit, freeze, training = frozen_policy()
    if args.replay:
        old = n.strict_loads(args.output.read_bytes())
        if old != evaluate(commit, freeze, training):
            raise ValueError('retained transfer does not replay')
        print(json.dumps({'status': 'replay_consistent', 'provider_calls': 0})); return
    if os.path.lexists(args.output) or not args.output.parent.is_dir():
        p.error('new output with existing parent required')
    with (HERE / 'TRANSFER.started').open('xb') as stream:
        stream.write(n.canonical({'freeze_commit': commit, 'freeze_sha256': FREEZE_SHA,
                                 'selection_already_committed': True}) + b'\n')
        stream.flush(); os.fsync(stream.fileno())
    result = evaluate(commit, freeze, training)
    with args.output.open('xb') as stream:
        stream.write(n.canonical(result) + b'\n')
    print(json.dumps({'status': 'completed_once', 'threshold': result['training_threshold_cents'] / 100,
                     'scores': {k: {a: {x: y for x, y in score.items() if not x.endswith('_ids')}
                                       for a, score in scores.items()} for k, scores in result['scores'].items()},
                     'overlap': result['overlap']}))


if __name__ == '__main__':
    main()
