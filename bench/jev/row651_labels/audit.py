"""Offline official-label audit of the unchanged, completed row651 native run."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from bench.jev.angle_lab import native as n
from bench.jev.second_reader import replay_large
from bench.jev.second_reader.row651 import prepare


HERE = Path(__file__).resolve().parent
RECEIPT = HERE.parent / 'second_reader/results/row651-live-20260917'
UPSTREAM_SHA = '469a5de6ca9b3e274837b5aba129e83e33e8ed1961a5a659521640fd33547f8c'
URL = ('https://datasets-server.huggingface.co/rows?dataset=oolongbench%2Foolong-synth'
       '&config=default&split=validation&offset=651&length=1')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def align(envelope, source, metadata):
    require(envelope.get('partial') is False and len(envelope['rows']) == 1,
            'partial official data')
    entry = envelope['rows'][0]
    require(type(entry.get('row_idx')) is int and entry['row_idx'] == 651
            and entry.get('truncated_cells') == [], 'truncated or different row')
    data = entry['row']
    for field in ('context_len', 'context_window_id', 'dataset', 'question',
                  'task_group', 'task', 'answer'):
        require(type(data[field]) is type(metadata[field]) and data[field] == metadata[field],
                'row metadata mismatch: ' + field)
    require(data['context_window_text'].encode('utf-8') == source, 'unlabeled source differs')
    rawlines = source.splitlines(keepends=True)
    labeled = data['context_window_text_with_labels'].encode('utf-8').splitlines(keepends=True)
    require(len(rawlines) == len(labeled), 'line coverage')
    ledger = []
    offset = 0
    for number, (raw, tagged) in enumerate(zip(rawlines, labeled), 1):
        if raw.startswith(b'Date:'):
            match = re.fullmatch(rb'(.*?) \|\| Label: (ham|spam)(\r?\n?)', tagged)
            require(match is not None, 'label suffix grammar')
            require(match[1] + match[3] == raw, 'occurrence bytes changed')
            ledger.append({'id': f'r{number:04d}', 'byte_start': offset,
                           'byte_end': offset + len(raw),
                           'record_sha256': hashlib.sha256(raw).hexdigest(),
                           'gold_ham': match[2] == b'ham'})
        else:
            require(raw == tagged, 'nonrecord bytes changed')
        offset += len(raw)
    require(len(ledger) == 17469 and len({r['id'] for r in ledger}) == 17469,
            'official occurrence coverage')
    require(ledger[0]['id'] == 'r0005' and ledger[-1]['id'] == 'r17473',
            'physical source identity')
    gold = n.strict_loads(data['answer'])
    require(type(gold) is list and len(gold) == 1 and type(gold[0]) is int,
            'official aggregate type')
    require(sum(r['gold_ham'] for r in ledger) == gold[0] == 8638,
            'official aggregate disagreement')
    return ledger


def metrics(rows):
    require(type(rows) is list and len(rows) > 0, 'empty metric rows')
    seen = set()
    for r in rows:
        require(type(r.get('id')) is str and r['id'] and r['id'] not in seen,
                'duplicate or invalid metric ID')
        seen.add(r['id'])
        require(type(r.get('gold_ham')) is bool, 'gold must be boolean')
        p = r.get('p_ham')
        require(type(p) in (int, float) and math.isfinite(p) and 0 <= p <= 1,
                'probability domain')
    fp = [r['id'] for r in rows if r['p_ham'] >= .5 and not r['gold_ham']]
    fn = [r['id'] for r in rows if r['p_ham'] < .5 and r['gold_ham']]
    gold = sum(r['gold_ham'] for r in rows)
    predicted = sum(r['p_ham'] >= .5 for r in rows)
    bins_by_count = {}
    for count in (5, 10):
        bins = []
        for index in range(count):
            group = [r for r in rows if min(count - 1, int(r['p_ham'] * count)) == index]
            mean_p = math.fsum(r['p_ham'] for r in group) / len(group) if group else None
            mean_y = sum(r['gold_ham'] for r in group) / len(group) if group else None
            bins.append({'lower': index / count, 'upper': (index + 1) / count,
                         'upper_inclusive': index == count - 1, 'n': len(group),
                         'mean_p_ham': mean_p, 'observed_ham_fraction': mean_y})
        bins_by_count[str(count)] = {
            'bins': bins,
            'ece': math.fsum(b['n'] / len(rows) * abs(b['mean_p_ham'] - b['observed_ham_fraction'])
                             for b in bins if b['n'])}
    correct = len(rows) - len(fp) - len(fn)
    return {'observed': len(rows), 'correct': correct, 'accuracy': correct / len(rows),
            'threshold': .5, 'gold_ham': gold, 'predicted_ham': predicted,
            'true_positives': gold - len(fn), 'true_negatives': len(rows) - gold - len(fp),
            'false_positives': len(fp), 'false_negatives': len(fn),
            'false_positive_ids': fp, 'false_negative_ids': fn,
            'signed_count_error': predicted - gold,
            'sum_noul': math.fsum(r['p_ham'] for r in rows),
            'sum_noul_minus_gold': math.fsum(r['p_ham'] for r in rows) - gold,
            'brier_score': math.fsum((r['p_ham'] - r['gold_ham']) ** 2 for r in rows) / len(rows),
            'positive_probability_reliability': bins_by_count}


def join(ledger, predictions):
    ids = [row['id'] for row in ledger]
    require(len(ids) == len(set(ids)) and set(ids) == set(predictions), 'prediction coverage')
    return [dict(row, p_ham=predictions[row['id']]) for row in ledger]


def audit(upstream=HERE / 'official-row651.json', folder=RECEIPT, *, portable=False):
    upstream, folder = Path(upstream), Path(folder)
    raw = upstream.read_bytes()
    require(n.sha(raw) == UPSTREAM_SHA, 'official snapshot changed')
    source = prepare.SOURCE.read_bytes()
    require(n.sha(source) == prepare.SOURCE_SHA256, 'unlabeled source hash changed')
    envelope = n.strict_loads(raw)
    ledger = align(envelope, source, n.strict_loads(prepare.ROW.read_bytes()))
    replay = replay_large.replay(folder, portable=True) if portable else replay_large.replay(folder)
    # The old hash identifies the unchanged numerical/artifact summary. The
    # separate validation scope is never represented by that historical hash.
    scope = replay.pop('validation_scope', None)
    require(replay['status'] == 'completed' and replay['complete_panel'], 'incomplete native run')
    receipt = n.strict_loads((folder / 'receipt.json').read_bytes())
    predictions = {}
    # Consume only observations already checked by the existing native receipt replay.
    for row in receipt['panel_rows']:
        body = n.strict_loads((folder / (row['name'] + '-observation.json')).read_bytes())['observation']
        require(not set(predictions).intersection(body['answers']), 'duplicate predictions')
        predictions.update({qid: a['noul'] for qid, a in body['answers'].items()})
    rows = join(ledger, predictions)
    result = metrics(rows)
    require(result['predicted_ham'] == replay['ham_count']
            and result['gold_ham'] == replay['official_count']
            and result['sum_noul'] == replay['sum_noul'], 'native replay disagrees with label audit')
    result = {'schema': 'azdaja.row651_official_item_gold.v1', 'status': 'passed',
            'new_inference_requests': 0, 'model_inputs_changed': False,
            'source_url': URL, 'official_snapshot_sha256': UPSTREAM_SHA,
            'labeled_context_sha256': n.sha(envelope['rows'][0]['row']['context_window_text_with_labels'].encode()),
            'unlabeled_context_sha256': n.sha(source),
            'source_occurrences_aligned_byte_for_byte': len(rows),
            'receipt_sha256': n.sha((folder / 'receipt.json').read_bytes()),
            'checked_native_replay_sha256': n.sha(n.canonical(replay)),
            'metrics': result, 'occurrence_ledger': rows,
            'native_workflow': {k: replay[k] for k in (
                'confirmed_typed_requests', 'elapsed_seconds', 'request_bytes',
                'known_input_tokens', 'known_output_tokens', 'known_input_estimate_usd',
                'billing_known', 'matched_generative_baseline', 'exact_task_pass')},
            'limits': ['Official annotations are the benchmark reference, not fresh human adjudication.',
                       'Metrics are occurrence-weighted on a public, potentially dependent/contaminated panel.',
                       'No inferential confidence interval or general calibration guarantee is claimed.',
                       'No model rerun, threshold change, production routing change or gold relabeling.']}
    if scope is not None:
        result['validation_scope'] = scope
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, default=HERE / 'official-row651.json')
    parser.add_argument('--receipt', type=Path, default=RECEIPT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--portable', action='store_true', help='Check retained evidence without the historical executable')
    args = parser.parse_args()
    require(not args.output.exists() and not args.output.is_symlink(), 'output exists')
    result = audit(args.upstream, args.receipt, portable=args.portable)
    with args.output.open('xb') as stream:
        stream.write(n.canonical(result) + b'\n')
    m = result['metrics']
    print(json.dumps({'status': result['status'], 'new_inference_requests': 0,
                      **{k: m[k] for k in ('observed', 'correct', 'accuracy', 'false_positives',
                                         'false_negatives', 'predicted_ham', 'gold_ham',
                                         'sum_noul', 'brier_score')},
                      'ece_5': m['positive_probability_reliability']['5']['ece'],
                      'ece_10': m['positive_probability_reliability']['10']['ece']}))


if __name__ == '__main__':
    main()
