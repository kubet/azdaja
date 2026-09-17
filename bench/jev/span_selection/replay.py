#!/usr/bin/env python3
"""Replay this frozen complete panel offline. Not provider authentication or live replay."""
import argparse
import json
from pathlib import Path

from bench.jev.span_selection import kernel as k
from bench.jev.span_selection import run as r


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(directory):
    directory = Path(directory)
    load = lambda name: k.strict_loads((directory / name).read_text())
    manifest = load('MANIFEST.json')
    for name, expected in manifest['artifacts'].items():
        require(Path(name).name == name, 'artifact path')
        data = (directory / name).read_bytes()
        require(len(data) == expected['bytes'] and k.sha(data) == expected['sha256'], 'artifact digest: ' + name)
    receipt = load('receipt.json')
    for name, expected in receipt['input_hashes'].items():
        require(k.sha((r.HERE / name).read_bytes()) == expected, 'method/input drift: ' + name)
    inputs = k.strict_loads((r.HERE / 'fixtures/inputs.json').read_text())
    gold = k.strict_loads((r.HERE / 'fixtures/gold.json').read_text())
    k.verify_git_sources(inputs, r.ROOT)
    prepared = k.prepare(inputs)
    k.validate_gold(prepared, gold)
    require(load('prepared.json') == prepared, 'prepared source pool')
    require(load('questions.json') == k.questions(prepared), 'full question contract')
    sources = list({k.canonical(t['source']): t['source'] for t in inputs['tasks']}.values())
    require(k.strict_loads((r.HERE / 'fixtures/sources.json').read_text()) == sources, 'source index')
    retained = load('retained-state.json')
    require(retained['sources'] == prepared and retained['stats']['provider_requests'] == 0, 'source re-entry')
    all_rows = {'typed': [], 'baseline': []}
    known_tokens = 0
    observed_models = set()
    for block in (1, 2, 3):
        ids = {t['id'] for t in inputs['tasks'] if t['block'] == block}
        pack = {'tasks': [t for t in prepared['tasks'] if t['id'] in ids]}
        request = {'model': r.JUDGE_MODEL, 'state': pack, 'questions': k.questions(pack)}
        require(load(f'block{block}-typed-request.json') == request, 'typed pack mismatch')
        prompt = load(f'block{block}-baseline-prompt.json')
        require(prompt['payload'] == {'state': pack, 'questions': request['questions']}, 'unmatched model inputs')
        result = load(f'block{block}-typed-observation.json')
        observation, stats = result['observation'], result['stats']
        require(observation['model'] == r.EXPECTED_MODEL, 'typed identity')
        require(observation['_azdaja']['request_sha256'] == k.sha(k.canonical(request)), 'request binding')
        require(stats['provider_requests'] == 1 and stats['cache_hits'] == 1, 'request/cache accounting')
        require(stats['unknown_input_usage_requests'] == 0 and stats['known_input_tokens'] == observation['usage']['input_tokens'], 'usage accounting')
        require(result['cached']['answers'] == observation['answers'] and result['cached']['_azdaja']['cache_hit'], 'cached distributions')
        require(retained['observations'][f'block{block}-typed'] == observation, 'distribution re-entry')
        known_tokens += stats['known_input_tokens']
        require(known_tokens <= r.TOKEN_CAP, 'cumulative token envelope')
        observed_models.add(observation['model'])
        selections = {'typed': {tid: a['choice'] for tid, a in observation['answers'].items()},
                      'baseline': k.strict_loads(load(f'block{block}-baseline-raw.json')['text'])}
        for arm in ('typed', 'baseline'):
            rows = k.materialize(pack, selections[arm])
            table = {'rows': rows, 'source_pool': pack, 'selections': selections[arm]}
            name = f'block{block}-{arm}'
            require(load(name + '-table.json') == table, 'native table mismatch')
            require(retained['results'][name] == table, 'table re-entry')
            all_rows[arm].extend(rows)
        if block < 3:
            require(r.semantic_stop(k.grade(all_rows['typed'], gold)) is None, 'continued after semantic stop')
    grades = {arm: k.grade(rows, gold) for arm, rows in all_rows.items()}
    for arm in grades:
        require(grades[arm] == receipt[arm + '_grade'] and all_rows[arm] == receipt[arm + '_rows'], 'reported grades/rows')
    lexical = k.materialize(prepared, k.lexical(prepared))
    require(k.grade(lexical, gold) == receipt['lexical_projection'], 'lexical grade')
    comparison = r.final_quality(grades['typed'], grades['baseline'], receipt['block_seconds'])
    require(comparison == receipt['comparison'], 'reported comparison')
    require(receipt['known_typed_input_tokens'] == known_tokens and receipt['confirmed_typed_requests'] == 3, 'campaign accounting')
    require(receipt['typed_questions'] == 18 and receipt['typed_cells_started'] == receipt['logical_llm_calls'] == 3, 'call envelope')
    require(receipt['cleanup_exit'] == 0 and receipt['status'] == 'completed', 'workflow completion')
    trace = r.trace_summary(directory / 'model-trace.jsonl')
    require(trace == receipt['generative_trace'], 'trace reporting')
    require(trace['logical_request_ids'] == 3 and trace['observed_models'] == [r.GENERATOR], 'generative identity/count')
    return {'status': 'retained_panel_replayed', 'live_provider_calls': 0,
            'typed_correct': grades['typed']['correct'], 'baseline_correct': grades['baseline']['correct'],
            'rows_per_semantic_arm': 18, 'lexical_correct': k.grade(lexical, gold)['correct'],
            'known_typed_input_tokens': known_tokens, 'observed_typed_models': sorted(observed_models),
            'comparison': comparison, 'provider_authenticity_claim': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', type=Path, default=r.HERE / 'results/native-20260917')
    args = parser.parse_args()
    print(json.dumps(verify(args.directory), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
