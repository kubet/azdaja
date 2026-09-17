"""Provider-free audit of a terminal, source-identical suffix continuation.

Imports only pure runner helpers. Never constructs a Campaign or invokes a model.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import statistics

from bench.jev.angle_lab import native as n
from bench.jev.asymmetry.baseline import run as b, continue_run as c

HERE = Path(__file__).resolve().parent
ROOT = b.ROOT
FROZEN_LABELS = ROOT / 'bench/jev/row651_labels/result.json'
EXPECTED = 17469
GOLD_SHA256 = '65f5bf14c9c3546cc030b95adcfaaa10ec3b40586fdc06f7bdfc469f92242e13'
THRESHOLD_FREEZE = HERE.parent / 'threshold/training-freeze.json'
THRESHOLD_SHA256 = '8239f182ff7ea3b0263ecc02eb9cfeb22f1e8b10943230f655f96261df05f50f'
SCHEMA = 'azdaja.asymmetry.baseline.replay.v3'
COUNTERS = ('entered_turns', 'physical_attempt_events', 'setup_attempts',
            'failed_identity_unknown_events', 'logical_request_ids', 'succeeded_events')


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def equal(a, b):
    """JSON equality without Python's True == 1 alias."""
    return canonical(a) == canonical(b)


def strict_loads(raw):
    value = n.strict_loads(raw)
    # parse_constant rejects NaN literals, but JSON's 1e999 also overflows.
    canonical(value)
    return value


def load(path):
    return strict_loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def packs():
    # baseline.run has rows(), not packs(). Its underlying large_run.packs()
    # reconstructs source spans and its rows() binds the original Jev requests.
    return b.rows()


def validate_raw(text, expected):
    require(type(text) is str, 'raw text type')
    answer = strict_loads(text)
    require(type(answer) is dict and set(answer) == set(expected), 'raw answer coverage')
    require(all(type(v) is str and v in ('yes', 'no') for v in answer.values()),
            'raw answer domain')
    return answer


def _check_freeze(folder, receipt, prepared):
    files = receipt.get('frozen_files')
    require(type(files) is dict and files, 'frozen files missing')
    for path, digest in files.items():
        p = Path(path)
        require(p.is_file() and sha(p) == digest, 'frozen source changed: ' + path)
    seals = {}
    for name in ('FROZEN', 'CONTINUATION-FROZEN'):
        path = HERE / (name + '.json')
        require(str(path.resolve()) in files and sha(path) == files[str(path.resolve())],
                name + ' manifest missing')
        marker = path.with_suffix('.started')
        require(marker.is_file() and not marker.is_symlink(), name + '.started missing')
        require(equal(load(marker), {'automatic_retry': False, 'seal_sha256': sha(path)}),
                name + ' started seal binding')
        seals[name] = load(path)
        for source, digest in seals[name]['files'].items():
            require(files.get(source) == digest, 'manifest inventory binding')
    original, suffix = seals['FROZEN'], seals['CONTINUATION-FROZEN']
    require(original['schema'] == 'azdaja.asymmetry.baseline_freeze.v1'
            and original['instruction'] == b.INSTRUCTION
            and original['maximum_logical_calls'] == 112
            and equal(original['panel'], b.panel_identity(prepared)), 'original frozen panel')
    require(equal(suffix['suffix'], b.panel_identity(prepared[25:]))
            and suffix['deadline_unix'] == c.DEADLINE, 'continuation frozen panel')
    require(equal(files, {**suffix['files'], str((HERE / 'CONTINUATION-FROZEN.json').resolve()):
                          sha(HERE / 'CONTINUATION-FROZEN.json')}), 'continuation inventory')


class _TraceView:
    """Read-only in-memory path protocol for the native summarizer."""
    def __init__(self, events):
        self.text = '\n'.join(canonical(e).decode() for e in events)

    def exists(self):
        return True

    def read_text(self):
        return self.text


def summary(events):
    return n.usage_summary(_TraceView(events))


def _trace(path):
    require(path.is_file(), 'model trace missing')
    events = [strict_loads(line) for line in path.read_text().splitlines() if line.strip()]
    require(all(type(e) is dict for e in events), 'trace event object')
    identities = [(e.get('request_id'), e.get('attempt')) for e in events]
    require(len(set(identities)) == len(identities), 'duplicate native attempt ID')
    for e in events:
        require(e.get('outcome') in ('succeeded', 'failed'), 'trace outcome')
        seconds(e.get('latency_ms'), 'native latency')
    # Keep native setup, failure, identity-unknown and missing-usage accounting.
    result = n.usage_summary(path)
    return events, result


def seconds(value, name):
    require(value is None or (type(value) in (float, int) and math.isfinite(value)
                             and value >= 0), name + ' invalid')
    return value


def _predecessor(receipt, events):
    cont = receipt.get('continuation')
    require(type(cont) is dict, 'continued receipt required')
    require(cont.get('schema') == 'azdaja.asymmetry.suffix_recovery.v1'
            and cont.get('budgets_reset') is False
            and cont.get('original_uninterrupted_run') is False
            and cont.get('predecessor_logical_calls') == 25
            and cont.get('absolute_deadline_unix') == c.DEADLINE, 'continuation contract')
    predecessor = Path(cont.get('predecessor', ''))
    if not predecessor.is_absolute():
        predecessor = ROOT / predecessor
    require(predecessor.is_dir() and not predecessor.is_symlink(), 'predecessor directory')
    side = load(predecessor / 'external-interruption.json')
    require(cont.get('interruption_sha256') == sha(predecessor / 'external-interruption.json'),
            'continuation interruption binding')
    require(side.get('schema') == 'azdaja.asymmetry.external_interruption.v1'
            and side.get('recovered_original_reentry') is False
            and side.get('continuation_performed') is False
            and side.get('original_campaign_deadline_unix') == c.DEADLINE,
            'interruption contract')
    # This checks the original running receipt's interruption envelope, successful
    # external final read, all 25 prompts/answers, original reentries, and trace.
    prior, answers, trace = c.check_prefix(predecessor)
    old_events, old_trace = _trace(predecessor / 'model-trace.jsonl')
    require(equal(old_trace, trace) and equal(events[:len(old_events)], old_events),
            'copied predecessor trace')
    require(all(receipt['frozen_files'].get(str(p.resolve())) == sha(p)
                for p in predecessor.iterdir() if p.is_file()), 'predecessor inventory binding')
    return prior, answers, side


def _delta(after, before):
    return {f: {k: value - before['usage'][f][k] for k, value in values.items()}
            for f, values in after['usage'].items()}


def _account_calls(calls, events):
    offset = 0
    previous = summary([])
    request_ids = set()
    audits = []
    for call in calls:
        count = call.get('physical_attempt_events')
        if count is None:
            require(call is calls[-1] and call['status'] == 'attempted', 'missing call trace')
            audits.append({'name': call['name'], 'trace_accounting': 'unavailable'})
            continue
        require(type(count) is int and count >= 0 and offset + count <= len(events),
                'call trace bounds')
        chunk = events[offset:offset + count]
        ids = {e['request_id'] for e in chunk}
        require(not ids.intersection(request_ids), 'request ID reused across calls')
        request_ids.update(ids)
        after = summary(events[:offset + count])
        for field in COUNTERS:
            require(equal(call.get(field), after[field] - previous[field]), 'call trace ' + field)
        require(equal(call.get('usage'), _delta(after, previous)), 'call trace usage')
        if call['status'] in ('completed', 'validated'):
            require(len(ids) == 1 and call['succeeded_events'] == 1
                    and 1 <= call['entered_turns'] <= 2
                    and call['setup_attempts'] <= 4
                    and call['physical_attempt_events'] == call['entered_turns'] + call['setup_attempts'],
                    'successful call identity')
            b.check_usage(after)
            require(after['observed_models'] == [b.GENERATOR]
                    and after['observed_providers'] == ['OpenAI'], 'successful model identity')
        audits.append({'name': call['name'], 'trace_accounting': 'verified',
                       'request_ids': sorted(ids), 'physical_attempt_events': count})
        offset += count
        previous = after
    # A stopped final cell can produce events after its finally checkpoint. Never
    # discard them or relabel them as a successful/eligible observation.
    return audits, events[offset:]


def _confusion(predictions, gold):
    tp = sum(p and g for p, g in zip(predictions, gold))
    tn = sum(not p and not g for p, g in zip(predictions, gold))
    fp = sum(p and not g for p, g in zip(predictions, gold))
    fn = sum(not p and g for p, g in zip(predictions, gold))
    count, target = sum(predictions), sum(gold)
    return {'observed': len(gold), 'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
            'correct': tp + tn, 'accuracy': (tp + tn) / len(gold) if gold else None,
            'predicted_ham': count, 'gold_ham': target, 'signed_count_error': count - target,
            'absolute_count_error': abs(count - target)}


def metrics(observed, goldmap):
    ids = sorted(observed)
    gold = [goldmap[q]['gold_ham'] for q in ids]
    base = [observed[q] == 'yes' for q in ids]
    result = {'baseline': _confusion(base, gold), 'paired': {}}
    for label, threshold in (('original_p_ge_0.5', .5), ('declared_transferred', .74)):
        jev = [goldmap[q]['p_ham'] >= threshold for q in ids]
        result[label] = {**_confusion(jev, gold), 'threshold': threshold}
        agreement = sum(x == y for x, y in zip(base, jev))
        shared = sum(x != g and y != g for x, y, g in zip(base, jev, gold))
        result['paired'][label] = {
            'observed': len(ids), 'baseline_wins': sum(x == g and y != g for x, y, g in zip(base, jev, gold)),
            'baseline_losses': sum(x != g and y == g for x, y, g in zip(base, jev, gold)),
            'shared_errors': shared, 'joint_correct': sum(x == g and y == g for x, y, g in zip(base, jev, gold)),
            'agreements': agreement, 'disagreements': len(ids) - agreement,
            'agreement_coverage': agreement / len(ids) if ids else None,
            'agreement_error_rate': shared / agreement if agreement else None}
    result['observed_ids'] = ids
    return result


def replay(folder, labels=FROZEN_LABELS, typed=None):
    folder = Path(folder)
    require(folder.is_dir() and not folder.is_symlink(), 'receipt directory required')
    receipt = load(folder / 'receipt.json')
    # Reject RUNNING before reading any answer or trace.
    require(receipt.get('status') in ('completed', 'stopped'), 'terminal status required')
    require(receipt.get('experiment_schema') == 'azdaja.asymmetry.row651_baseline.v1', 'schema')
    require(receipt.get('binary_sha256') == b.BINARY_SHA
            and receipt.get('requested_model') == b.MODEL
            and receipt.get('generative_model') == b.GENERATOR, 'runtime identity')
    require(equal(receipt.get('caps'), dict(logical_calls=b.MAX_LOGICAL, entered_turns=b.MAX_ENTERED,
            known_input_tokens=b.MAX_INPUT, known_output_tokens=b.MAX_OUTPUT,
            seconds=b.MAX_SECONDS, cell_seconds=b.CELL_SECONDS)), 'runtime caps')
    elapsed = seconds(receipt.get('elapsed_seconds'), 'full wall')
    require(elapsed is not None, 'missing full wall')
    require(receipt['status'] != 'completed' or elapsed <= b.MAX_SECONDS,
            'completed campaign deadline')
    require(receipt.get('no_controller_retry') is True
            and receipt.get('automatic_approval_authorized') is False
            and receipt.get('input_match') == 'exact_prior_typed_state_and_questions'
            and receipt.get('typed_calls_started') == 0
            and receipt.get('confirmed_typed_requests') == 0, 'campaign policy contract')
    require(not receipt.get('generative_trace_invalid'), 'invalid retained trace')
    labels = Path(labels)
    require(labels.is_file() and sha(labels) == GOLD_SHA256, 'gold hash')
    gold = load(labels)['occurrence_ledger']
    require(type(gold) is list and len(gold) == EXPECTED, 'label coverage')
    goldmap = {x['id']: x for x in gold}
    require(len(goldmap) == EXPECTED, 'duplicate gold ids')
    require(sha(THRESHOLD_FREEZE) == THRESHOLD_SHA256, 'threshold freeze hash')
    freeze = load(THRESHOLD_FREEZE)
    require(freeze['selection']['selected']['threshold_cents'] == 74, 'transferred threshold')
    prepared = packs()
    require(len(prepared) == 112, 'expected pack coverage')
    expected_ids = [qid for _, pack in prepared for qid in pack['questions']]
    require(len(expected_ids) == len(set(expected_ids)) == EXPECTED
            and set(expected_ids) == set(goldmap), 'expected ID coverage')
    _check_freeze(folder, receipt, prepared)
    events, trace = _trace(folder / 'model-trace.jsonl')
    require(equal(trace, receipt.get('generative_trace')), 'receipt trace mismatch')
    prior, prior_answers, side = _predecessor(receipt, events)
    calls, rows = receipt.get('calls'), receipt.get('panel_rows')
    require(type(calls) is list and type(rows) is list and 25 <= len(calls) <= len(rows) <= 112,
            'call/panel coverage')
    require(len(rows) <= len(calls) + 1 and receipt.get('logical_llm_calls') == len(calls),
            'logical admission count')
    names = [name for name, _ in prepared]
    require([x.get('name') for x in calls] == names[:len(calls)]
            and [x.get('name') for x in rows] == names[:len(rows)], 'duplicate or unordered pack IDs')
    for i in range(24):
        require(equal(calls[i], prior['calls'][i]), 'predecessor call changed')
    recovered = calls[24]
    require(recovered.get('seconds') is None and recovered.get('controller_latency_known') is False,
            'recovered controller duration unknown')
    old_trace_count = side['accounted_trace']['physical_attempt_events']
    require(recovered.get('recovered_native_latency_seconds') == events[old_trace_count - 1]['latency_ms'] / 1000,
            'recovered native latency binding')
    audits, unassigned = _account_calls(calls, events)
    require(not unassigned or receipt['status'] == 'stopped', 'unassigned complete trace')
    observed, artifacts, timing = {}, [], []
    retained_bytes = dict.fromkeys(('prompt', 'raw', 'answer', 'reentry'), 0)
    for i, row in enumerate(rows):
        name, pack = prepared[i]
        require(row.get('status') in ('attempted', 'completed')
                and equal(row.get('ids'), sorted(pack['questions']))
                and row.get('pack_sha256') == n.sha(n.canonical(pack)), 'panel binding')
        call = calls[i] if i < len(calls) else None
        if call:
            require(call.get('status') in ('attempted', 'validated', 'completed')
                    and call.get('arm') == 'generative'
                    and call.get('pack_sha256') == n.sha(n.canonical(pack))
                    and call.get('questions') == len(pack['questions'])
                    and call.get('prompt_bytes') == len(b.INSTRUCTION.encode()) + len(n.canonical(pack)),
                    'call request binding')
            timing.append({'name': name, 'controller_seconds': seconds(call.get('seconds'), 'controller seconds'),
                           'recovered_native_latency_seconds': call.get('recovered_native_latency_seconds')})
        paths = {key: folder / (name + '-' + key + '.json') for key in ('prompt', 'raw', 'answer', 'reentry')}
        present = {key: p.is_file() for key, p in paths.items()}
        for key, path in paths.items():
            if present[key]:
                retained_bytes[key] += path.stat().st_size
        if present['prompt']:
            require(equal(load(paths['prompt']), {'instruction': b.INSTRUCTION, 'payload': pack}),
                    'retained prompt source/question/instruction mismatch')
        answer, error = None, None
        if present['raw']:
            require(present['prompt'] and call is not None, 'raw without admitted prompt')
            try:
                answer = validate_raw(load(paths['raw'])['text'], pack['questions'])
            except (ValueError, KeyError, TypeError) as exc:
                require(call['status'] == 'attempted' and receipt['status'] == 'stopped'
                        and not present['answer'] and not present['reentry'], 'invalid validated raw')
                error = str(exc)
        if present['answer']:
            require(answer is not None and equal(load(paths['answer']), answer), 'answer mismatch')
            require(call.get('answer_sha256') == n.sha(n.canonical(answer)), 'answer hash')
        if present['reentry']:
            require(answer is not None and present['answer'], 'reentry without validated answer')
            binding = {'name': name, 'answer': answer, 'ids': sorted(pack['questions'])}
            require(equal(load(paths['reentry']), {'answer': answer, 'attempts': 0,
                        'binding_sha256': n.sha(n.canonical(binding))}), 'native reentry mismatch')
        if i < 25 and answer is not None:
            require(equal(answer, prior_answers[i]), 'recovered answer differs from predecessor')
        eligible = all(present.values()) and call is not None and call['status'] == row['status'] == 'completed'
        if receipt['status'] == 'completed':
            require(eligible, 'completed receipt has partial artifacts')
        if eligible:
            require(answer is not None and not set(answer).intersection(observed), 'duplicate answer ID')
            observed.update(answer)
        artifacts.append({'name': name, 'eligible': eligible, 'present': present, 'raw_validation_error': error})
    for ending in ('prompt', 'raw', 'answer', 'reentry'):
        require(all(p.name[:-len('-' + ending + '.json')] in names[:len(rows)]
                    for p in folder.glob('pack-*-' + ending + '.json')), 'orphan retained artifact')
    ham = sum(v == 'yes' for v in observed.values())
    complete = receipt['status'] == 'completed'
    reduction_path = folder / 'final-reduction.json'
    if complete or reduction_path.exists() or 'native_reduction' in receipt:
        require(reduction_path.is_file(), 'final reduction missing')
        reduction = load(reduction_path)
        expected_reduction = {'expected': EXPECTED, 'observed': len(observed),
            'complete': len(observed) == EXPECTED, 'ham': ham,
            'answer': 'Answer: ' + str(ham) if len(observed) == EXPECTED else None, 'attempts_in_reduction': 0}
        require(equal(reduction, expected_reduction) and equal(receipt.get('native_reduction'), reduction),
                'forged final reduction')
    if complete:
        require(len(calls) == len(rows) == 112 and len(observed) == EXPECTED
                and type(receipt.get('cleanup_exit')) is int
                and receipt['cleanup_exit'] == 0, 'completed full-panel contract')
        b.check_usage(trace)
    durations = [t['controller_seconds'] for t in timing if t['controller_seconds'] is not None]
    texts = Counter(pack['state']['records'][qid].split('Instance:', 1)[-1].strip()
                    for _, pack in prepared for qid in pack['questions'] if qid in observed)
    return {'schema': SCHEMA, 'consistent': True, 'status': receipt['status'],
        'complete_panel': complete, 'partial': not complete, 'observed_occurrences': len(observed),
        'expected_occurrences': EXPECTED, 'unknown_observations': EXPECTED - len(observed),
        'eligible_packs': sum(a['eligible'] for a in artifacts), 'attempted_packs': len(calls),
        'metrics': metrics(observed, goldmap), 'usage': trace, 'call_trace_audit': audits,
        'unassigned_trace_events': len(unassigned), 'artifacts': artifacts,
        'retained_artifact_bytes': retained_bytes,
        'provenance': {'receipt_sha256': sha(folder / 'receipt.json'),
            'model_trace_sha256': sha(folder / 'model-trace.jsonl'),
            'gold_sha256': GOLD_SHA256, 'threshold_freeze_sha256': THRESHOLD_SHA256},
        'timing': {'calls': timing, 'known_controller_seconds_sum': sum(durations) if durations else None,
            'unknown_controller_durations': len(timing) - len(durations),
            'median_controller_seconds': statistics.median(durations) if durations else None,
            'native_event_seconds': [e['latency_ms'] / 1000 if e.get('latency_ms') is not None else None for e in events],
            'interrupted_full_wall_seconds': seconds(receipt.get('elapsed_seconds'), 'full wall'),
            'wall_includes_interruption_and_recovery': True},
        'identical_text_dependence': {'unique_observed_texts': len(texts),
            'repeated_occurrences': sum(v - 1 for v in texts.values()), 'independence_established': False},
        'billing_known': False, 'baseline_subscription_cost_usd': None, 'cost_ratio': None,
        'caveats': ['Historical paired observations, not a randomized concurrent comparison.',
            'All three confusion matrices use exactly the same observed IDs, not positive-only subsets.',
            'Repeated identical texts are dependent occurrences, not independent replications.',
            'The frozen row645 threshold is 0.74. Training/test source-message overlap and prior headline knowledge prevent a blind independent transfer claim.',
            'Agreement can be jointly wrong. Partial artifacts and unassigned trace remain explicit.',
            'Subscription per-request billing is unknown. No dollar parity or 1000x claim is established.',
            'Controller time, native latency and interrupted full wall are distinct. Unknown durations are null.']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipt_dir', nargs='?', type=Path)
    parser.add_argument('--receipt-dir', dest='receipt_dir_opt', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    require((args.receipt_dir is None) != (args.receipt_dir_opt is None), 'provide exactly one receipt directory')
    require(not os.path.lexists(args.output), 'output exists')
    result = replay(args.receipt_dir_opt or args.receipt_dir)
    # O_EXCL also rejects dangling symlinks and races after validation.
    with args.output.open('xb') as stream:
        stream.write(canonical(result) + b'\n')
    print(json.dumps(result['metrics']['baseline']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
