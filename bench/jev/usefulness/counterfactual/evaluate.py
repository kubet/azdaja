#!/usr/bin/env python3
"""Score already-frozen rankings, never generate or tune them."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHODS = {'raw_bm25', 'normalized_bm25', 'passage_rrf', 'mmr_diverse'}
KS = (1, 2, 4, 8, 16)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError('nonfinite JSON')

    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs, parse_constant=nonfinite)


def index(items, key):
    if not isinstance(items, list) or not items:
        raise ValueError('missing rows')
    result = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get(key), str) or not item[key]:
            raise ValueError('invalid row identity')
        if item[key] in result:
            raise ValueError('duplicate row identity')
        result[item[key]] = item
    return result


def complete_order(order, universe):
    if (not isinstance(order, list) or any(not isinstance(x, str) for x in order)
            or len(order) != len(universe) or set(order) != set(universe)):
        raise ValueError('ranking is not the exact candidate universe')


def coverage(order, groups, texts, k):
    selected = order[:k]
    covered = [bool(set(group).intersection(selected)) for group in groups]
    return {'selected_ids': selected, 'covered_groups': sum(covered), 'total_groups': len(groups),
            'coverage_fraction': sum(covered) / len(groups), 'complete': all(covered),
            'missing_groups': [group for group, hit in zip(groups, covered) if not hit],
            'selected_text_bytes': sum(len(texts[source].encode('utf-8')) for source in selected)}


def score(rankings, corpus, tasks, evaluation, diagnostic):
    sources = index(corpus['items'], 'id')
    questions = index(tasks['tasks'], 'id')
    gold = index(evaluation['tasks'], 'task_id')
    rows = index(rankings['tasks'], 'task_id')
    if set(questions) != set(gold) or set(rows) != set(questions):
        raise ValueError('task coverage mismatch')
    if rankings.get('schema_version') != 2 or rankings.get('source_only') is not True:
        raise ValueError('not a frozen source-only ranking')
    texts = {key: value['text'] for key, value in sources.items()}
    if any(not isinstance(value, str) for value in texts.values()):
        raise ValueError('invalid source text')
    result = {}
    for task_id in sorted(rows):
        row, task, expected = rows[task_id], questions[task_id], gold[task_id]
        question = task['question']
        if (row.get('question') != question or row.get('question_sha256')
                != hashlib.sha256(question.encode('utf-8')).hexdigest()):
            raise ValueError('query identity mismatch')
        groups = expected['required_evidence_groups']
        if (not isinstance(groups, list) or not groups
                or any(not isinstance(group, list) or not group
                       or any(not isinstance(source, str) or source not in sources for source in group)
                       or len(set(group)) != len(group) for group in groups)):
            raise ValueError('invalid evidence groups')
        if not isinstance(row.get('rankings'), dict) or set(row['rankings']) != METHODS:
            raise ValueError('method coverage mismatch')
        result[task_id] = {}
        for method, ordering in row['rankings'].items():
            complete_order(ordering, sources)
            result[task_id][method] = {str(k): coverage(ordering, groups, texts, k) for k in KS}
    # The retained live diagnostic supplies exactly Q1. No other Jev rows invented.
    if 'Q1' not in rows or diagnostic.get('k') != 4:
        raise ValueError('missing original comparison')
    retained_raw = [row['id'] for row in diagnostic['bm25']]
    retained_jev = [row['id'] for row in diagnostic['typed_ranking']]
    complete_order(retained_raw, sources)
    complete_order(retained_jev, sources)
    if retained_raw != rows['Q1']['rankings']['raw_bm25']:
        raise ValueError('raw baseline differs from retained experiment')
    result['Q1']['jev_retained'] = {
        str(k): coverage(retained_jev, gold['Q1']['required_evidence_groups'], texts, k) for k in KS}
    summary = {}
    for method in sorted(METHODS):
        summary[method] = {}
        for k in KS:
            values = [result[task_id][method][str(k)] for task_id in result]
            summary[method][str(k)] = {
                'tasks': len(values),
                'macro_group_coverage': sum(value['coverage_fraction'] for value in values) / len(values),
                'fully_covered_tasks': sum(value['complete'] for value in values),
                'covered_groups': sum(value['covered_groups'] for value in values),
                'total_groups': sum(value['total_groups'] for value in values),
                'mean_selected_text_bytes': sum(value['selected_text_bytes'] for value in values) / len(values)}
    return {'by_task': result, 'all_seven_lexical': summary,
            'jev_tasks_measured': ['Q1'], 'all_seven_jev_comparison': None,
            'shortlist_conditioned_final_answer_quality': None,
            'raw_reference_exact_order_reproduced': True,
            'new_provider_calls': 0, 'held_out': False, 'inferential_guarantee': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rankings', type=Path, default=HERE / 'rankings.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error('output already exists')
    corpus, tasks = HERE.parent / 'corpus.json', HERE.parent / 'tasks.json'
    evaluation = HERE.parent / 'evaluation.json'
    diagnostic = HERE.parent / 'results/native-20260916/retrieval-diagnostic.json'
    frozen = load(args.rankings)
    if frozen['inputs'] != {'corpus_sha256': sha(corpus), 'tasks_sha256': sha(tasks)}:
        raise ValueError('input file identity mismatch')
    if frozen['implementation'] != {'retrieve_sha256': sha(HERE / 'retrieve.py'), 'plan_sha256': sha(HERE / 'PLAN.md')}:
        raise ValueError('ranking code or plan identity mismatch')
    result = score(frozen, load(corpus), load(tasks), load(evaluation), load(diagnostic))
    result['file_sha256'] = {name: sha(path) for name, path in {
        'rankings': args.rankings, 'corpus': corpus, 'tasks': tasks, 'evaluation': evaluation,
        'retained_live_diagnostic': diagnostic, 'evaluator': Path(__file__)}.items()}
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2, sort_keys=True, allow_nan=False)
        output.write('\n')
    print(json.dumps({'Q1_at_4': {method: values['4'] for method, values in result['by_task']['Q1'].items()},
                      'all_seven_at_4': {method: values['4'] for method, values in result['all_seven_lexical'].items()}}, indent=2))


if __name__ == '__main__':
    main()
