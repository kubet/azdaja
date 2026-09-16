#!/usr/bin/env python3
"""Source-only deterministic lexical sensitivity check. No provider access."""
import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
import re
import time

HERE = Path(__file__).resolve().parent
K1, B, RRF_K, MMR_LAMBDA = 1.2, 0.75, 60, 0.75
STOP = frozenset('a an and are as at be by for from has have in is it its of on or that the their these this to was were will with'.split())
WORD = re.compile(r'\w+', re.UNICODE)
CAMEL = re.compile(r'(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])')
METHODS = ('raw_bm25', 'normalized_bm25', 'passage_rrf', 'mmr_diverse')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def strict_load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError('nonfinite JSON value')

    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs,
                      parse_constant=invalid_constant)


def words(text):
    return [word.lower() for word in WORD.findall(text)]


def norm_words(text):
    result = []
    for word in WORD.findall(text):
        parts = [part for chunk in word.split('_') for part in CAMEL.split(chunk)]
        # One occurrence contributes each distinct original/part term once.
        for term in dict.fromkeys([word.lower()] + [part.lower() for part in parts]):
            if term and term not in STOP:
                result.append(term)
    return result


def validate(corpus, tasks):
    for obj, key, text_key in ((corpus, 'items', 'text'), (tasks, 'tasks', 'question')):
        if not isinstance(obj, dict) or not isinstance(obj.get(key), list) or not obj[key]:
            raise ValueError('malformed or empty schema')
        seen = set()
        for item in obj[key]:
            if (not isinstance(item, dict) or not isinstance(item.get('id'), str)
                    or not item['id'].strip() or not isinstance(item.get(text_key), str)):
                raise ValueError('malformed schema')
            if item['id'] in seen:
                raise ValueError('duplicate IDs')
            seen.add(item['id'])


def bm25(query, documents):
    if (not isinstance(query, list) or any(not isinstance(t, str) for t in query)
            or not isinstance(documents, list)
            or any(not isinstance(d, list) or any(not isinstance(t, str) for t in d)
                   for d in documents)):
        raise ValueError('BM25 requires token lists, not string documents')
    count = len(documents)
    average = sum(map(len, documents)) / count if count else 0
    frequencies = Counter(term for document in documents for term in set(document))
    scores = []
    for document in documents:
        terms, score = Counter(document), 0.0
        for term in sorted(set(query)):
            tf = terms[term]
            if tf and average:
                idf = math.log(1 + (count - frequencies[term] + 0.5)
                               / (frequencies[term] + 0.5))
                score += idf * tf * (K1 + 1) / (tf + K1 * (1 - B + B * len(document) / average))
        scores.append(score)
    return scores


def order(ids, scores):
    return sorted(range(len(ids)), key=lambda index: (-scores[index], ids[index]))


def passages(document):
    return [document[start:start + 128] for start in range(0, len(document), 64)] or [[]]


def passage_max_scores(query, documents):
    flattened, owners = [], []
    for index, document in enumerate(documents):
        windows = passages(document)
        flattened.extend(windows)
        owners.extend([index] * len(windows))
    scores = [0.0] * len(documents)
    # Shared passage-corpus IDF and average length, not per-document statistics.
    for owner, score in zip(owners, bm25(query, flattened)):
        scores[owner] = max(scores[owner], score)
    return scores


def cosine(left, right):
    dot = sum(left[key] * right.get(key, 0) for key in sorted(left))
    denominator = math.sqrt(sum(x*x for x in left.values()) * sum(x*x for x in right.values()))
    return dot / denominator if denominator else 0.0


def mmr_order(ids, relevance, vectors):
    largest = max(relevance, default=0)
    normalized = [value / largest if largest else 0.0 for value in relevance]
    chosen, remaining, selected_scores = [], set(range(len(ids))), []
    while remaining:
        scores = {
            index: MMR_LAMBDA * normalized[index] - (1 - MMR_LAMBDA)
            * max((cosine(vectors[index], vectors[other]) for other in chosen), default=0.0)
            for index in remaining
        }
        best = min(remaining, key=lambda index: (-scores[index], ids[index]))
        chosen.append(best)
        selected_scores.append(scores[best])
        remaining.remove(best)
    return chosen, selected_scores


def rank(ids, texts, question):
    raw = [words(text) for text in texts]
    normalized = [norm_words(text) for text in texts]
    raw_scores = bm25(words(question), raw)
    normal_query = norm_words(question)
    normal_scores = bm25(normal_query, normalized)
    passage_scores = passage_max_scores(normal_query, normalized)
    fused_scores = [0.0] * len(ids)
    for ordering in (order(ids, normal_scores), order(ids, passage_scores)):
        for position, index in enumerate(ordering, start=1):
            fused_scores[index] += 1 / (RRF_K + position)
    mmr, _ = mmr_order(ids, normal_scores, [Counter(document) for document in normalized])
    return {
        'raw_bm25': [ids[i] for i in order(ids, raw_scores)],
        'normalized_bm25': [ids[i] for i in order(ids, normal_scores)],
        'passage_rrf': [ids[i] for i in order(ids, fused_scores)],
        'mmr_diverse': [ids[i] for i in mmr],
    }


def run(corpus_path, tasks_path):
    corpus, tasks = strict_load(corpus_path), strict_load(tasks_path)
    validate(corpus, tasks)
    ids = [item['id'] for item in corpus['items']]
    texts = [item['text'] for item in corpus['items']]
    started = time.perf_counter()
    results = []
    for task in tasks['tasks']:
        question = task['question']
        rankings = rank(ids, texts, question)
        assert all(len(rows) == len(ids) and set(rows) == set(ids) for rows in rankings.values())
        results.append({'task_id': task['id'], 'question': question,
                        'question_sha256': hashlib.sha256(question.encode('utf-8')).hexdigest(),
                        'rankings': rankings})
    elapsed = time.perf_counter() - started
    return {
        'schema_version': 2, 'source_only': True,
        'inputs': {'corpus_sha256': digest(corpus_path), 'tasks_sha256': digest(tasks_path)},
        'implementation': {'retrieve_sha256': digest(__file__), 'plan_sha256': digest(HERE / 'PLAN.md')},
        'methods': {
            'raw_bm25': {'k1': K1, 'b': B, 'query_terms': 'unique raw Unicode words'},
            'normalized_bm25': {'k1': K1, 'b': B, 'stoplist': sorted(STOP),
                                'duplicate_original_parts_per_occurrence': False},
            'passage_rrf': {'rrf_k': RRF_K, 'window': 128, 'stride': 64, 'weight': 'equal',
                            'idf_population': 'all corpus passages'},
            'mmr_diverse': {'lambda': MMR_LAMBDA, 'sequence': 'full greedy',
                            'similarity': 'term-frequency cosine'},
        },
        'timing': {'scope': 'one local run excluding I/O', 'seconds': elapsed, 'not_production_latency': True},
        'tasks': results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, default=HERE.parent / 'corpus.json')
    parser.add_argument('--tasks', type=Path, default=HERE.parent / 'tasks.json')
    parser.add_argument('--output', type=Path, default=HERE / 'rankings.json')
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error('output already exists')
    result = run(args.corpus, args.tasks)
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(result, output, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        output.write('\n')
    print(json.dumps({'written': str(args.output), 'tasks': len(result['tasks']), 'source_only': True}))


if __name__ == '__main__':
    main()
