# Counterfactual retrieval sensitivity plan

This is a deterministic, provider-free **post-study sensitivity check**, not a new held-out or preregistered efficacy study. The coordinator knew the prior study result. The first implementer was denied evaluator and result files. No method is tuned on coverage outcomes. Frozen live outputs are never edited. No additional inference is authorized by this diagnostic.

## Inputs fixed before valid ranking execution

- `../corpus.json`: SHA-256 `0a60662e873f9ca0ad545f1ee09d20095418e2110d207592cc9735dfa1cf621c`.
- `../tasks.json`: SHA-256 `db7f0cb90857b008e4e4cfec63f2909a56b3510215ed23ae499d07ade1bfd61b`.
- Ranking sees corpus `text` and exact task `question` strings only. IDs break ties and bind output. Paths, revisions, line ranges, hashes, requested facts and instruction metadata are not semantic ranking inputs.
- Each decoded question string is retained exactly and hashed as UTF-8, without trimming or Unicode normalization.

## Fixed methods

1. **raw_bm25:** `re.findall(r'\w+', text.lower(), flags=re.UNICODE)`, unique query terms, sorted before summation. BM25 `k1=1.2`, `b=0.75`, IDF `log(1+(N-df+0.5)/(df+0.5))`. This matches the original reference method, apart from deterministic summation order. Rank descending score, then ascending ID.
2. **normalized_bm25:** Original Unicode word tokens plus underscore and ASCII camelCase/acronym parts, lowercased. Hyphens already separate raw word tokens. Each distinct original/part is emitted once per original occurrence, so an ordinary unsplit token is not accidentally doubled. The fixed stoplist is exactly `a an and are as at be by for from has have in is it its of on or that the their these this to was were will with`. Negation tokens including `no`, `not`, `never`, `without`, `neither`, `nor`, `cannot` are not removed. Query uses unique normalized terms. Same BM25 constants and tie-breaking.
3. **passage_rrf:** Normalized document BM25 fused with maximum passage BM25. Windows are token indices `[start,start+128)` at every start in `range(0,len(tokens),64)`, including shorter overlapping tails. Empty documents supply one empty window. Passage IDF and mean length are computed over **all passages from all documents**, then each document takes its maximum window score. Equal-weight reciprocal-rank fusion of document and passage ranks with `k=60`, rank starts at 1. Final ties use ID.
4. **mmr_diverse:** Relevance is normalized BM25 divided by the maximum document score, all-zero relevance maps to zero. Similarity is term-frequency cosine over normalized document tokens. Select **all candidates** greedily using `0.75*relevance - 0.25*maximum_similarity_to_selected`. Every exact tie uses ascending ID, not input order. No tail is reranked by a different method.

No query expansion, learned embeddings, manual per-task adjustments or parameter search. These are plausible lexical alternatives, **not the strongest possible retrieval system**.

## Separate outcome scoring, fixed before disclosure

The root will evaluate frozen full rankings against existing required-evidence groups at `k=1,2,4,8,16`. A group is covered when any of its alternatives is selected. Report per-task counts, macro coverage, number of fully covered tasks and selected UTF-8 text bytes. No confidence interval or population-generalization claim. The existing Jev observation is available for Q1 only. All other Jev task cells remain unmeasured, never inferred from lexical results.

Top-4 matches the original comparison. Full-corpus coverage is an availability ceiling, not proof that an answer uses every source. No answer is generated from a shortlist here. This follow-up cannot establish downstream answer quality or an RLM advantage. The Jev request contained candidate metadata as well as text, while lexical ranking uses text alone, another limit to strict causal comparability.

Stop after one valid frozen ranking set and its evaluation. If inexpensive lexical selection matches the single-query gain, withdraw that gain as evidence of an advantage over these baselines. Otherwise report only that the narrow signal survived these specific controls. Do not add methods after observing gold outcomes.

## Pre-scoring implementation correction record

The initial draft passed five weak tests but was rejected on code inspection before coverage scoring. It normalized the raw reference query, passed token strings as BM25 documents for passage scoring, used input-index MMR ties and had a vacuous whole-universe diversity test. The exact draft code, plan and **unscored invalid output** remain under `invalid-draft/`, with hashes and rejection reasons. They are not a scored experimental arm.

The corrected implementation and literal non-gold tests specify corpus-wide passage statistics, distinct per-occurrence identifier parts and exact-ID tie rules before valid outputs are produced. Strict duplicate-key/nonfinite JSON rejection, complete ID universes, exact questions, code/plan/input digests and exclusive output creation protect comparison identity. These fixes and clarifications are not hidden parameter tuning or evidence of model efficacy.

## Reproduce without overwriting the frozen result

```sh
python3 -B -m unittest discover -s bench/jev/usefulness/counterfactual -p 'test_retrieve.py' -v
python3 -B bench/jev/usefulness/counterfactual/retrieve.py --output "$JCODE_SCRATCH_DIR/fresh-lexical-rankings.json"
```

Use a new output path. Timing is one local run excluding I/O, not production or comparative model latency. Every method keeps the complete candidate order available, irrespective of the diagnostic top-k cut.
