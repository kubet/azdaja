#!/usr/bin/env python3
"""Check retained first-party recovery evidence. No model, binary or private files."""
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from bench.jev.long_task_salvage import replay as r


def equivalent(a, b):
    """Only derived floating metrics allow cross-Python summation roundoff."""
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equivalent(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(equivalent(x, y) for x, y in zip(a, b))
    if isinstance(a, float):
        return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= 1e-15
    return a == b


def checked_files(root, entries):
    r.base.check(type(entries) is dict and bool(entries), 'empty_inventory')
    for name, digest in entries.items():
        path = Path(name)
        r.base.check(not path.is_absolute() and '..' not in path.parts, 'inventory_path')
        target = root / path
        r.base.check(not any(p.is_symlink() for p in (target, *target.parents)), 'inventory_symlink')
        r.base.check(target.is_file() and r.base.sha(target.read_bytes()) == digest, 'artifact_changed:' + name)


def verify():
    retention = r.base.loads((HERE / 'RETENTION.json').read_bytes())
    checked_files(ROOT, retention['files'])
    output = HERE / 'results/offline-20260917'
    original = ROOT / 'bench/jev/long_task_recovery/results/native-20260917'
    summary = r.base.loads((output / 'summary.json').read_bytes())
    r.base.check(summary['new_provider_calls'] == 0 and summary['jev_was_used'] is False
                 and summary['original_end_to_end_success'] is False
                 and summary['jev_advantage_established'] is False, 'scope_overclaim')
    corpus = r.grade.load_json(r.base.HERE / 'fixtures/corpus.json')
    gold = r.grade.load_json(r.base.HERE / 'fixtures/gold.json')
    arms = {}
    for arm, count in zip(r.base.ARMS, (75, 120)):
        previous = original / arm
        receipt = r.base.loads((previous / 'receipt.json').read_bytes())
        checked_files(previous, receipt['retained_files'])
        r.base.check(receipt['status'] == 'stopped' and receipt['runtime']['typed_totals']['attempts'] == 0
                     and receipt['runtime']['typed_totals']['total_wall_ns'] == 0, 'live_status_changed')
        trace = (previous / 'model-trace.jsonl').read_bytes()
        events = [r.base.loads(line) for line in trace.splitlines() if line.strip()]
        expected = [(i, e) for i, e in enumerate(events) if e['depth'] == 1]
        records = r.base.loads((HERE / 'records' / (arm + '.json')).read_bytes())
        r.base.check(records['model_trace_sha256'] == r.base.sha(trace)
                     and len(expected) == count == len(records['trace_mapping']), 'public_trace_binding')
        for (index, event), mapping, key in zip(expected, records['trace_mapping'], records['trace_order']):
            r.base.check(mapping['trace_index'] == index and mapping['prompt_sha256'] == key
                         and mapping['request_id'] == event['request_id']
                         and mapping['session_id'] == event['session_id']
                         and event['outcome'] == 'succeeded', 'response_occurrence_binding')
            r.base.check(records['records'][key]['occurrences'] ==
                         [{k: v for k, v in mapping.items() if k != 'prompt_sha256'}], 'occurrence_changed')
        bundle = r.bundle(records, (previous / 'solo-trace.txt').read_text())
        binding = output / (arm + '-binding')
        metadata = r.base.loads((binding / 'binding.json').read_bytes())
        r.base.check(r.base.sha(r.base.canonical(bundle)) == metadata['bundle_sha256'], 'reconstructed_bundle_changed')
        for name in ('original', 'corrected'):
            r.base.check((binding / (name + '-program.py')).read_text() == bundle[name + '_code'], 'program_changed')
        consumption = r.consumed(bundle, binding / 'used')
        recovered = r.base.loads((output / arm / 'receipt.json').read_bytes())
        checked_files(output / arm, recovered['retained_files'])
        r.base.check(recovered['offline_stub'] is True and recovered['status'].startswith('completed'), 'not_offline_recovery')
        fresh = r.grade.replay(output / arm / 'prediction.json', corpus, gold)
        retained = r.base.loads((output / arm / 'grade.json').read_bytes())
        r.base.check(equivalent(fresh, retained), 'fresh_grade_changed')
        expected_summary = {'scope': 'posthoc_hash_only_offline_salvage', 'original_live_status': 'stopped',
                            'new_provider_calls': 0, 'consumption': consumption,
                            'structural': fresh['structural'], 'aggregate': fresh['aggregate'],
                            'citations': fresh['citations'], 'query_scores': fresh['queries']['scores']}
        r.base.check(equivalent(expected_summary, summary['arms'][arm]), 'summary_changed')
        arms[arm] = {'correct': fresh['aggregate']['correct'], 'total': fresh['aggregate']['total'],
                     'accuracy': fresh['aggregate']['accuracy'], 'exact_leaf_replies': count,
                     'live_status': receipt['status'], 'typed_attempts': 0}
    return {'status': 'retained_evidence_consistent', 'files_checked': len(retention['files']), 'arms': arms,
            'new_provider_calls': 0, 'original_end_to_end_success': False, 'jev_advantage_established': False,
            'limits': 'First-party retained evidence, not independent provider authentication. Private session files and historical executable bytes are not required or verified here.'}


if __name__ == '__main__':
    try:
        print(r.base.canonical(verify()).decode().strip())
    except (OSError, ValueError, KeyError, TypeError, r.base.Stop) as error:
        print(r.base.canonical({'status': 'refused', 'reason': str(error) if isinstance(error, r.base.Stop)
                               else type(error).__name__, 'new_provider_calls': 0}).decode().strip())
        raise SystemExit(2)
