# Retrieval counterfactual: useful signal, conditional application

**Decision:** the one-query Jev top-4 evidence-selection advantage survives these three additional lexical controls. It still does **not** establish better final answers or an RLM moat. A more useful competing workflow also emerged: simply widen normalized lexical retrieval to eight excerpts. That covered every required evidence group on all seven development tasks without a provider call.

## What was frozen and run

This is a **post-study sensitivity analysis**, not a new held-out trial. The root already knew the original result. A separate initial implementer was kept away from gold, but the root repaired correctness defects before any coverage scoring. The invalid, unscored draft is retained, not quietly replaced as a successful arm.

Corrected methods and tests were committed at `cc073cd`, then full source-only rankings at `a9c1ed7`, before evaluation. Parameters and reporting cuts are in [PLAN.md](PLAN.md). The evaluator compares exact corpus/task/question identities and all candidate IDs, then checks the raw BM25 ranking against the retained original order. No parameters or ranking output were changed after scoring.

Actual commands:

```sh
python3 -B -m unittest discover -s bench/jev/usefulness/counterfactual -p 'test_*.py' -v
python3 -B bench/jev/usefulness/counterfactual/retrieve.py --output "$JCODE_SCRATCH_DIR/new-rankings.json"
python3 -B bench/jev/usefulness/counterfactual/evaluate.py --rankings "$JCODE_SCRATCH_DIR/new-rankings.json" --output "$JCODE_SCRATCH_DIR/new-coverage.json"
```

Use fresh paths. Existing files, including dangling output symlinks, are refused. Twenty focused tests passed. Those tests check the computation, not AI usefulness. The actual coverage observations below are the result.

## Q1: same sixteen candidates, four selected

| Method | Selected source IDs | Required groups covered | Selected text bytes |
|---|---|---:|---:|
| Original BM25, exactly reproduced | E09, E15, E14, E03 | 2/4 | 7,319 |
| Identifier-normalized BM25 | E09, E14, E15, E16 | 2/4 | 8,370 |
| Document/passage reciprocal-rank fusion | E09, E14, E15, E16 | 2/4 | 8,370 |
| MMR diversity selection | E09, E14, E15, E08 | 2/4 | 7,871 |
| Jev, retained original live observation | E13, E09, E14, E12 | **4/4** | 8,016 |

All four lexical methods missed the two implementation excerpts E12/E13 at top-4. They show the actual lexical-candidate filter, linked-context selection and omission counting in `src/memory/recall.rs`. Jev selected both. This is a concrete cross-representation selection example: the natural-language decision requires implementation evidence, not just topically similar documentation. It does not establish why the model selected those items or that this behavior generalizes.

The selected-byte counts matter. Normalized BM25 and passage fusion used more top-4 text than Jev but covered fewer required groups, so this observation is not explained merely by Jev selecting more text. Nevertheless this is **not a matched byte-budget experiment**: document sizes differ and no fixed-byte selection procedure was tested. Jev also received candidate metadata, whereas these lexical methods use text only. A graph-aware, metadata-aware, embedding or tuned hybrid search baseline could behave differently.

## All seven tasks: lexical comparison only

Each lexical method had the same top-4 coverage counts on this panel, despite differing rankings:

| Task | Raw BM25 | Normalized BM25 | Passage fusion | MMR |
|---|---:|---:|---:|---:|
| Q1 | 2/4 | 2/4 | 2/4 | 2/4 |
| Q2 | 2/3 | 2/3 | 2/3 | 2/3 |
| Q3 | 1/1 | 1/1 | 1/1 | 1/1 |
| Q4 | 1/2 | 1/2 | 1/2 | 1/2 |
| Q5 | 2/2 | 2/2 | 2/2 | 2/2 |
| Q6 | 3/4 | 3/4 | 3/4 | 3/4 |
| Q7 | 2/2 | 2/2 | 2/2 | 2/2 |

That is **13/18 groups**, **77.38% macro task coverage**, and **3/7 fully covered tasks** for each method at top-4. Jev was not run for Q2 through Q7 retrieval, so there is no seven-task Jev retrieval comparison.

At the predeclared top-8 cut:

| Method | Macro task coverage | Fully covered tasks | Mean selected text bytes |
|---|---:|---:|---:|
| Raw BM25 | 92.86% | 6/7 | 12,039 |
| Normalized BM25 | **100%** | **7/7** | 12,337 |
| Passage fusion | **100%** | **7/7** | 12,226 |
| MMR | 96.43% | 6/7 | 11,772 |

For Q1 specifically, normalized top-8 covers 4/4 using 14,505 text bytes, versus retained Jev top-4's 8,016 bytes. That is a measured evidence-selection tradeoff, **not a measured dollar, latency or final-answer saving**. The complete `corpus.json` file is 27,296 bytes, containing 19,635 UTF-8 bytes of item text. The complete corpus already fit the original answer model's context.

Full rankings and every predeclared cut `1,2,4,8,16` remain in [rankings.json](rankings.json) and [evaluation-results.json](evaluation-results.json). The four-method local ranking run took about 0.103 seconds excluding I/O. It is a single measurement, not production latency and not directly comparable to model service latency. No new Jev or answer-model calls were made.

## What changes about the angle

1. **Do not pay for semantics by default.** If the inexpensive wider evidence set fits, retain it rather than force a tiny top-k or ask a judge to authorize looking at more source. On this panel, widening normalized lexical retrieval was enough for complete required-source availability.
2. **A conditional role remains:** use typed semantic selection when a tighter evidence budget matters and lexical ranking misses cross-representation evidence. The Q1 observation motivates that role but does not validate a general policy or automatic router.
3. **Keep the control boundary optional:** the RLM can choose exact retrieval, wider inspection, `judge_many`, or `llm`, while retaining complete source and distributions. These scripts do not implement autonomous orchestration, global budgets or an optimal planner.
4. **The answer-quality bar is unchanged.** The [closed live answer study](../RESULTS.md) found no improvement over ordinary self-review. No answer was generated from any shortlist in this follow-up. Claim/source checks, extraction repair, joins and memory assistance still need their own final-work comparisons.

These are dependent, hand-selected development tasks. Required-source groups are an authored coverage proxy, not the universe of all relevant evidence or proof of answer quality. No inferential interval, calibration claim, model-identity guarantee or new generalization claim is made. No more methods are added after seeing this result.
