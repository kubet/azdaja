#!/usr/bin/env python3
"""Recover authored outputs without inference; original live failures stay failed."""
import argparse
import os
from pathlib import Path
import re
import shlex
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from bench.jev.long_task import run as base, grade

BINARY_SHA256 = 'bd483035a03570124570f68c44532bb9070815af06f556ada4b4fc2f6370d222'
OLD = 'sha256(ctx.encode("utf-8")).hexdigest()'
NEW = 'sha256(ctx)'


def program_and_root(trace):
    root = re.findall(r'^=== root request begin [^\n]+ ===\n(.*?)\n=== root request end [^\n]+ ===$', trace, re.M | re.S)
    base.check(len(root) == 1, 'ambiguous_original_root')
    body = trace.split('\n=== repair code ===\n')
    base.check(len(body) == 2, 'ambiguous_executed_code')
    code = body[1].split('\n=== repair result outcome=', 1)[0].strip('\n')
    returned = re.findall(r'```python\s*\n(.*?)\n```', trace, re.S)
    base.check(len(returned) == 2 and returned[-1].strip('\n') == code, 'executed_code_not_model_reply')
    base.check(code.count(OLD) == 1, 'hash_correction_not_unique')
    fixed = code.replace(OLD, NEW)
    base.check(fixed.replace(NEW, OLD, 1) == code, 'nonmechanical_correction')
    return root[0], code, fixed


def bundle(records, trace):
    root, code, fixed = program_and_root(trace)
    leaves = {}
    for key, row in records['records'].items():
        base.check(base.sha(row['prompt'].encode()) == key
                   and base.sha(row['response'].encode()) == row['response_sha256'], 'record_digest')
        base.check(len(row['occurrences']) == 1, 'ambiguous_prompt_multiplicity')
        leaves[key] = {'prompt': row['prompt'], 'reply': row['response'], 'reply_sha256': row['response_sha256']}
    base.check(len(records['trace_order']) == len(leaves)
               and set(records['trace_order']) == set(leaves), 'record_coverage')
    return {'root_prompt': root, 'root_reply': '```python\n' + fixed + '\n```',
            'leaves': leaves, 'original_code': code, 'corrected_code': fixed,
            'original_code_sha256': base.sha(code.encode()), 'corrected_code_sha256': base.sha(fixed.encode()),
            'correction': {'old': OLD, 'new': NEW, 'occurrences': 1},
            'records_sha256': base.sha(base.canonical(records))}


def consumed(bundle_value, used):
    expected = {key: row['reply_sha256'] for key, row in bundle_value['leaves'].items()}
    expected[base.sha(bundle_value['root_prompt'].encode())] = base.sha(bundle_value['root_reply'].encode())
    actual = {}
    for path in used.glob('*.json'):
        row = base.loads(path.read_bytes())
        base.check(path.name == row['prompt_sha256'] + '.json' and row['new_provider_calls'] == 0, 'consumption_record')
        actual[row['prompt_sha256']] = row['reply_sha256']
    base.check(actual == expected, 'exact_response_consumption_incomplete')
    return {'root_local_reply': 1, 'exact_leaf_replies': len(expected) - 1,
            'new_provider_calls': 0, 'all_reply_hashes_match': True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--failed-results', type=Path, required=True)
    parser.add_argument('--records', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    binary = args.binary.resolve(strict=True)
    base.check(base.sha(binary.read_bytes()) == BINARY_SHA256, 'studied_binary_identity')
    base.check(args.output.is_absolute() and args.output.parent.is_dir() and not os.path.lexists(args.output), 'exclusive_output_required')
    args.output.mkdir(mode=0o700)
    scratch = Path(os.environ['JCODE_SCRATCH_DIR']).resolve(strict=True)
    base.check(scratch != ROOT and ROOT not in scratch.parents, 'private_scratch_inside_repository')
    private = Path(tempfile.mkdtemp(prefix='jev-long-salvage-private-', dir=str(scratch)))
    corpus = grade.load_json(base.HERE / 'fixtures/corpus.json')
    gold = grade.load_json(base.HERE / 'fixtures/gold.json')
    results = {}
    for arm, count in zip(base.ARMS, (75, 120)):
        previous = args.failed_results / arm
        original = base.loads((previous / 'receipt.json').read_bytes())
        base.check(original['status'] == 'stopped' and original['runtime']['typed_totals']['attempts'] == 0, 'not_original_failure')
        for name, digest in original['retained_files'].items():
            base.check(base.sha((previous / name).read_bytes()) == digest, 'original_artifact_changed')
        records = base.loads((args.records / (arm + '.json')).read_bytes())
        base.check(records['model_trace_sha256'] == base.sha((previous / 'model-trace.jsonl').read_bytes()), 'trace_binding')
        value = bundle(records, (previous / 'solo-trace.txt').read_text())
        base.check(len(value['leaves']) == count, 'leaf_count')
        folder = args.output / (arm + '-binding'); folder.mkdir()
        base.save(folder / 'bundle.json', value)
        used = folder / 'used'; used.mkdir()
        command = ' '.join(shlex.quote(str(p)) for p in
                           [sys.executable, '-B', HERE / 'provider.py', folder / 'bundle.json', used])
        receipt = base.run_arm(binary, arm, args.output / arm, private / arm,
                               auth=Path('unused'), attached=Path('unused'), offline_provider=command)
        # A bad replay remains visibly failed. Never invoke a provider to repair it.
        base.check(receipt['status'].startswith('completed'), 'offline_replay_failed_' + arm)
        consumption = consumed(value, used)
        report = grade.replay(args.output / arm / 'prediction.json', corpus, gold)
        base.save(args.output / arm / 'grade.json', report)
        results[arm] = {'scope': 'posthoc_hash_only_offline_salvage', 'original_live_status': 'stopped',
                        'new_provider_calls': 0, 'consumption': consumption,
                        'structural': report['structural'], 'aggregate': report['aggregate'],
                        'citations': report['citations'], 'query_scores': report['queries']['scores']}
    base.save(args.output / 'summary.json', {'schema': 'azdaja.long_task.offline_salvage.v1',
              'arms': results, 'jev_was_used': False, 'new_provider_calls': 0,
              'original_end_to_end_success': False, 'jev_advantage_established': False})
    print(base.canonical({'status': 'offline_salvage_completed', 'new_provider_calls': 0,
                         'original_end_to_end_success': False}).decode().strip())
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError, base.Stop) as error:
        print(base.canonical({'status': 'refused', 'reason': str(error) if isinstance(error, base.Stop) else type(error).__name__,
                              'new_provider_calls': 0}).decode().strip())
        raise SystemExit(2)
