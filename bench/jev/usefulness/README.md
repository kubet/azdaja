# Small developer-usefulness panel

**Purpose:** can an answer help a developer avoid a wrong implementation or release decision, with the right evidence and caveats? This is seven nonrepresentative development examples, not a generality proof, quality benchmark, or evidence that Jev improves work. No model responses existed when these tasks were curated.

**Observed native run:** [results, final-answer quality, one-query retrieval gain and limitations](RESULTS.md). The blanket answer-review policy did not outperform full-context self-review.

## Inputs and practical angles

Give every arm only `corpus.json` and `tasks.json`. Keep `evaluation.json`, this rubric and `grade.py` out of model inputs. Corpus: 16 verbatim excerpts, 27,296 UTF-8 bytes including JSON/provenance, from public tracked files at `d851113`. Every item pins full revision, file, inclusive line range, Git blob OID, file SHA-256 and excerpt SHA-256. Hashes apply to exact UTF-8 bytes including retained line endings. No local memory, private notes, research/jev papers, or synthetic benchmark fixture statements are included.

| Task | Useful decision and failure mode |
| --- | --- |
| Q1 | Whether absence of recalled disagreement justifies deleting compatibility code. Zero omitted candidates is not exhaustive counterevidence search. |
| Q2 | How to transfer reviewed connected decisions across clones without losing context, publishing private content accidentally, or promising commands in an older installed binary. |
| Q3 | How to recover safely from an import error without deleting history based on a false rollback assumption. |
| Q4 | Which store a wrapper will use under five real configurations. Numeric “memory” summaries are plausible keyword-rich but irrelevant evidence for note truth/storage routing. |
| Q5 | Whether installed hooks imply activation or security containment. Must acknowledge tension between two README passages, not cherry-pick one. |
| Q6 | Whether a historical config is today's default and whether parsed equality permits migration. The authentic old config is a plausible exact-keyword distractor. |
| Q7 | Whether Unix tests, Windows compilation and digests justify Windows runtime/confidentiality/authorship claims. |

Q1 requires a source-backed *class* of missed evidence, not an invented actual memory record. Q3 supplies a documented failure-sequence witness. Q1, Q2, Q4, Q5, Q6 and Q7 require combining evidence or recognizing insufficiency. Q5 asks about the documentation contract; the corpus cannot prove implementation compliance.

## Run and judge

From the repository root, with base commit available locally:

```sh
python3 -B bench/jev/usefulness/grade.py --verify --self-test
python3 -B bench/jev/usefulness/grade.py --responses /path/to/answers.json
```

Answers are a JSON **array**, one object per task:

```json
[{"task_id":"Q1","answer":"Source-cited explanation with IDs such as [E12].","sources":["E12"],"facts":{}}]
```

This shape example is deliberately incomplete, not a gold response. Populate exactly the typed `requested_facts` in each task, and cite only sources actually used. List IDs in `sources` and place them beside the prose claims they support. The 32 fact checks are evaluation fields, not 32 mandatory API calls.

The offline checker validates tracked provenance and exact excerpt bytes. For responses it reports missing and contradicted structured facts, unknown IDs, missing evidence groups, empty prose and missing listed citations. Each evidence group needs at least one listed member. It accepts any order for activation scopes and rejects booleans masquerading as numbers. Wrong/missing mechanical results exit 1. It **does not** understand prose, infer entailment, or grant a quality pass. Correct facts pasted beside all source IDs can pass mechanical checks and still fail the task. Self-tests are deliberately manufactured grader tests, never end-to-end quality results.

### Human rubric, applied blind to arm

Read the actual prose against `human_required_points` in `evaluation.json`. For each task record:

1. **Accuracy (0–2):** 2 = correct recommendation and material facts, 1 = limited imprecision without unsafe recommendation, 0 = wrong or materially contradictory answer.
2. **Evidence (0–2):** 2 = citations actually entail key claims, distinguish scope and version, 1 = useful but incomplete attribution, 0 = invented/misused evidence or citation dumping without a supported explanation.
3. **Completeness/usefulness (0–2):** 2 = covers all required points and gives actionable decision/recovery, 1 = misses a material point, 0 = omits central caveat/counterexample or gives unusable advice.

A task succeeds only with all requested facts correct, necessary source coverage, and **2/2/2 human scores**. If an unanticipated valid alternative source path exists, record an adjudication rather than secretly editing the frozen gold or penalizing an arm. Unsafe deletion, treating candidate coverage as global completeness, unsupported runtime/confidentiality guarantees, or contradicted prose is a task failure even if structured fields are right. Record omitted required points and contradicted claim text explicitly. Report successful tasks / 7 and per-task failures first, not confidence or retrieval hit rate. Never collapse infrastructure failure into a successful answer.

## Bounded first live comparison

Use the same frozen questions, complete corpus and final-answer contract for Azdaja-only generative reasoning, native typed judge + RLM, and competent plain Python + Jev. Permit ordinary exact parsing, full-text search, source joining and direct reading to every arm. Do not force a weak top-k selector, suppress inconvenient sources, or deny the plain-Python baseline batching/caching/full-corpus reasoning.

Freeze and log root-model identity, root turns/tokens, wall-clock budget, provider identities, HTTP requests, typed question counts and failures **before** running. The initial study should cap TypeSafe usage at **6 HTTP requests and 64 submitted questions total across arms, including retries**, not per task. Batch semantic work; do not classify all 7×16 task/source pairs (112 questions). These small inputs permit the complete corpus to be available locally without a retrieval bottleneck. The 32 fixed fact fields need not each become a judge question. Allocate the shared service budget symmetrically to the two Jev arms; the Azdaja-only arm makes no TypeSafe calls. Stop and report budget exhaustion rather than silently increasing limits. Root-generation budgets must also be explicit and comparable. This directory implements no provider runner and performs no HTTP calls.

## Limits

Curated, leading implementation-review questions are easier and less representative than open-ended feature work. Most sources are documentation contracts, not independent runtime observations; only recall has implementation excerpts. Historic config bytes are authentic migration artifacts, not evidence of a user's actual installation. The panel measures source-grounded decision answers, not whether a produced patch builds or helps users. Current repository behavior may differ from the pinned snapshot. All arms can read the whole small corpus and may tie. A tie or loss is informative. Seven tasks and one run cannot establish superiority, productivity gain, security assurance, or broad model generality. A successful grader/provenance check is only harness validation; live final answers and blind prose judgment are still required.
