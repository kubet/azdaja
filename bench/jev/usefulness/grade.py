#!/usr/bin/env python3
"""Offline integrity and mechanical scoring only. Never a semantic prose judge."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))


def verify():
    corpus, tasks, gold = load('corpus.json'), load('tasks.json'), load('evaluation.json')
    assert (HERE / 'corpus.json').stat().st_size <= 35000
    rev = corpus['base_revision']
    assert tasks['base_revision'] == rev
    root = subprocess.check_output(['git', '-C', str(HERE), 'rev-parse', '--show-toplevel']).decode().strip()
    def git(*args):
        return subprocess.check_output(['git', '-C', root, *args])
    assert git('rev-parse', 'd851113').decode().strip() == rev
    ids = set()
    for item in corpus['items']:
        assert item['id'] not in ids
        ids.add(item['id'])
        assert item['revision'] == rev
        path = item['path']
        assert path == 'README.md' or path.startswith(('assets/', 'docs/', 'src/memory/'))
        assert 'research/' not in path and '.azdaja' not in Path(path).parts
        raw = git('show', f'{rev}:{path}')
        assert hashlib.sha256(raw).hexdigest() == item['file_sha256']
        assert git('rev-parse', f'{rev}:{path}').decode().strip() == item['git_blob_oid']
        lines = raw.splitlines(keepends=True)
        assert 1 <= item['line_start'] <= item['line_end'] <= len(lines)
        excerpt = b''.join(lines[item['line_start'] - 1:item['line_end']])
        assert excerpt == item['text'].encode('utf-8')
        assert hashlib.sha256(excerpt).hexdigest() == item['excerpt_sha256']
    by_id = {t['id']: t for t in tasks['tasks']}
    assert 6 <= len(by_id) == len(tasks['tasks']) <= 8
    assert len(gold['tasks']) == len(by_id)
    assert {g['task_id'] for g in gold['tasks']} == set(by_id)
    for g in gold['tasks']:
        assert set(g['expected_facts']) == set(by_id[g['task_id']]['requested_facts'])
        assert g['human_required_points']
        for group in g['required_evidence_groups']:
            assert group and set(group) <= ids
    return {'provenance': 'verified against tracked base blobs', 'corpus_bytes': (HERE / 'corpus.json').stat().st_size,
            'sources': len(ids), 'tasks': len(by_id), 'fact_checks': sum(len(g['expected_facts']) for g in gold['tasks'])}


def exact(value, expected):
    # JSON bools must not pass as integers. Activation scopes are an unordered set.
    if type(value) is not type(expected):
        return False
    if isinstance(expected, list):
        return all(isinstance(x, str) for x in value) and sorted(value) == sorted(expected)
    return value == expected


def grade(responses):
    if not isinstance(responses, list):
        raise ValueError('responses must be a JSON array')
    valid_sources = {i['id'] for i in load('corpus.json')['items']}
    gold = load('evaluation.json')['tasks']
    task_ids = {g['task_id'] for g in gold}
    seen = {}
    for response in responses:
        if not isinstance(response, dict) or response.get('task_id') not in task_ids:
            raise ValueError('unknown task or non-object response')
        if response['task_id'] in seen:
            raise ValueError('duplicate task response')
        seen[response['task_id']] = response
    rows = []
    for g in gold:
        r = seen.get(g['task_id'], {})
        facts = r.get('facts', {})
        sources = r.get('sources', [])
        prose = r.get('answer', '')
        if not isinstance(facts, dict) or not isinstance(sources, list) or not all(isinstance(x, str) for x in sources) or not isinstance(prose, str):
            raise ValueError('facts must be an object, sources a string array, answer a string')
        missing = sorted(set(g['expected_facts']) - set(facts))
        wrong = [k for k, v in g['expected_facts'].items() if k in facts and not exact(facts[k], v)]
        unknown = sorted(set(sources) - valid_sources)
        uncovered = [group for group in g['required_evidence_groups'] if not set(group).intersection(sources)]
        prose_cites = [s for s in sources if s not in prose]
        extras = sorted(set(facts) - set(g['expected_facts']))
        row = dict(task_id=g['task_id'],correct_facts=len(g['expected_facts'])-len(missing)-len(wrong),total_facts=len(g['expected_facts']),
                   missing_facts=missing,contradicted_facts=wrong,unexpected_facts=extras,uncovered_evidence_groups=uncovered,
                   unknown_sources=unknown,listed_sources_absent_from_prose=prose_cites,duplicate_sources=len(sources)!=len(set(sources)),
                   answer_present=bool(prose.strip()),human_review='REQUIRED: evidence entailment, prose contradictions, omissions and practical recommendation')
        row['mechanical_pass'] = not (missing or wrong or uncovered or unknown or prose_cites or extras or row['duplicate_sources']) and row['answer_present']
        rows.append(row)
    return {'mechanical_only': True, 'quality_pass': None, 'tasks': rows,
            'correct_facts': sum(r['correct_facts'] for r in rows), 'total_facts': sum(r['total_facts'] for r in rows),
            'mechanical_pass': all(r['mechanical_pass'] for r in rows)}


def self_test():
    gold = load('evaluation.json')['tasks']
    # Manufactured answers test grader mechanics, not task performance.
    good = [dict(task_id=g['task_id'], answer='GRADER TEST ONLY ' + ' '.join(group[0] for group in g['required_evidence_groups']),
                 sources=list(dict.fromkeys(group[0] for group in g['required_evidence_groups'])), facts=g['expected_facts']) for g in gold]
    assert grade(good)['mechanical_pass']
    assert not grade([])['mechanical_pass']
    for mutate in ('wrong', 'missing', 'evidence', 'unknown', 'empty', 'bool_as_int'):
        changed = json.loads(json.dumps(good))
        r = changed[0]
        if mutate == 'wrong': r['facts']['recall_proves_no_counterevidence'] = True
        if mutate == 'missing': del r['facts']['primary_cap']
        if mutate == 'evidence': r['sources'] = []
        if mutate == 'unknown': r['sources'].append('E999')
        if mutate == 'empty': r['answer'] = ''
        if mutate == 'bool_as_int': r['facts']['recall_proves_no_counterevidence'] = 0
        assert not grade(changed)['mechanical_pass'], mutate
    for bad in ([good[0], good[0]], [dict(task_id='Q999')], {}):
        try:
            grade(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('malformed responses accepted')
    return 'passed: positive mechanics, omissions, false facts, evidence, invented IDs, blank prose, strict types, malformed/duplicate tasks'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--responses', type=Path)
    args = parser.parse_args()
    if not (args.verify or args.self_test or args.responses):
        parser.error('choose --verify, --self-test or --responses FILE')
    output = {}
    if args.verify: output['verification'] = verify()
    if args.self_test: output['self_test'] = self_test()
    if args.responses:
        output['grading'] = grade(json.loads(args.responses.read_text(encoding='utf-8')))
    print(json.dumps(output, indent=2))
    if args.responses and not output['grading']['mechanical_pass']:
        raise SystemExit(1)
