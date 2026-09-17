# Long-task result: useful reads recovered, no Jev benefit demonstrated

2026-09-17. This is a full-source long-task attempt, not another short classification panel. The task covered **all 102 official CUAD test contracts**, 4,779,822 bytes of contract text, 510 annotated clause-presence fields and four dependent cross-field queries. Source bytes are not a measured source-token count. Input-token totals below include repeated instructions, source reads and intermediate work.

**Both live workflows failed at finalization. Neither invoked Jev.** A zero-inference recovery retained useful outputs from all 195 already-paid semantic reads, without changing their responses or the authored extraction/join logic. This does not turn the live failures into successes or establish a Jev speed, quality or cost advantage.

## What happened

1. The original pair hit a hidden 60-second root idle timeout despite a configured 120-second hard limit. Both failures and their unknown usage remain in `../long_task/results/initial-20260917/`.
2. A narrowly scoped opt-in-only deadline fix was independently reproduced before and after. The one separately sealed recovery pair used the same task/model and deducted the earlier spent time from its budgets. Default, feature-off and child deadlines were unchanged.
3. In that pair, both models first exceeded the existing 50-line program cap and used one root repair before semantic execution. Both initial and repaired programs chose generative readers, not Jev. The repaired programs completed 75 and 120 semantic reads respectively.
4. Both then called `sha256(ctx.encode("utf-8")).hexdigest()`. Azdaja's native helper takes text and already returns hexadecimal text. The programs failed at `FINAL`, after all paid reads. No paid root repair was performed.
5. Every leaf response survived in its exact trace-bound session. Extraction retained only the final user prompt and final assistant text, excluding private authentication, bootstrap messages and reasoning metadata. All 195 prompts/replies and their occurrence identities are retained under `records/`.
6. Offline recovery changed **only that one expression to `sha256(ctx)`**, then executed each otherwise unchanged program through the studied native binary. A local provider returned only exact retained replies to byte-identical prompts. All 75/120 expected replies were consumed exactly once, with no unmatched fallback, new inference or modified labels.

The failed live receipts are in `../long_task_recovery/results/native-20260917/`. The separately labeled offline outputs are in `results/offline-20260917/`.

## Whole-task resources, including failures

Both arms used `gpt-5.6-sol`, the same optional-engine orchestration contract and the same budgets. The generative control was forbidden typed judgments and had no attached key. The optional arm was allowed them but chose not to call them. These are two model-authored plans, **not a comparison between generative inference and actual Jev inference**.

| Observed resource | Generative control | Optional engine available |
|---|---:|---:|
| Live recovery-pair outcome | Failed at final hash | Failed at final hash |
| Live recovery workflow wall, including cleanup | 790.426 s | 586.670 s |
| Total workflow wall including original timeout | 851.986 s | 650.333 s |
| Recovery-pair generative requests | 77 | 122 |
| Of those: root / semantic children | 2 / 75 | 2 / 120 |
| Known recovery input tokens | 1,157,922 | 1,196,515 |
| Known recovery output tokens | 102,252 | 63,962 |
| Reported cache-read tokens, not added again | 15,232 | 15,360 |
| Typed attempts / questions | 0 / 0 | 0 / 0 |
| Earlier root requests with unknown usage | 1 | 1 |
| New inference during offline recovery | 0 | 0 |

The recovery pair has 2,354,437 known input and 166,214 known output tokens. Cumulative usage including the earlier failures is a **lower bound**, not a complete bill. Subscription billing is unknown. Offline lookup latency is not inference latency. There is no measured TypeSafe bill, cost ratio or Jev speedup here.

## Quality of the recovered work, not live successful answers

The original frozen expert annotations and grader scored every one of the 510 fields per arm. No cases were dropped after observing outcomes. Unknowns remain unknown.

| Recovered-output metric | Generative control | Optional engine available, Jev unused |
|---|---:|---:|
| Fields observed | 510 / 510 | 510 / 510 |
| Fields correct | 426 / 510 (83.53%) | 404 / 510 (79.22%) |
| Macro F1 | 0.7205 | 0.6226 |
| TP / TN / FP / FN | 146 / 280 / 43 / 38 | 129 / 275 / 36 / 55 |
| Unknown fields | 8 | 44 |
| Verbatim source-valid YES citations | 189 / 189 | 165 / 165 |
| YES citations supported by expert-span rule | 113 / 189 (59.79%) | 102 / 165 (61.82%) |
| Exact dependent query sets | 0 / 4 | 0 / 4 |
| Transfer exposure query F1 | 0.9275 | 0.9143 |
| Exit with uncapped liability query F1 | 0.4444 | 0.3333 |
| Mixed liability query F1 | 0.4828 | 0.4000 |
| Transfer without convenience termination F1 | 0.8864 | 0.7778 |

These matrices and verbatim citations are usable as **reviewable extraction drafts**, not approved legal conclusions. An exact quote proves that the words occurred, not that the clause was correctly interpreted. Expert-span support requires gold YES plus at least 80% overlap with one annotated span and is a dataset-based measure, not independent legal adjudication.

The optional-enabled plan was faster and less accurate. Neither passed the live success bar, neither achieved exact joined answers, and neither used Jev. A single public-dataset pair cannot establish generalization, independence, statistical significance or an RLM advantage. Public training-data contamination is not excluded.

## What was actually improved

- The root deadline now honors the configured opt-in planning window instead of silently ending at 60 seconds. The real follow-through progressed into all semantic reads.
- The optional root and repair prompts now state the exact native hash API. This is **documentation, not an AST preflight guard**. No new live run measured whether the model follows the clarification.
- All completed paid work was recovered into complete, source-bound outputs with **zero additional inference**. Failed receipts and earlier unknown usage were preserved.
- An independent reader verified the 75/120 exact-response consumption, one-expression change, fresh public grading and absence of typed use. `independent-review.json` records that bounded review.

The next useful comparison would need reliable finalization and **observed typed use on a long workflow**, with a matched generative stage and complete whole-task accounting. Merely enabling a capability is not treatment exposure. No additional campaign, forced decomposition, threshold search or memory/RAG work was run here.

## Requirement-to-observation map

| Requirement | Concrete boundary exercised | Observed result |
|---|---|---|
| Genuinely long source | Pinned full corpus through real `az solo -f`; exact public full-ctx hash/length check | 102 contracts, no source truncation |
| Useful dependent task | Model-authored extraction, abstention, citation and four joins; frozen full-matrix scorer | Complete matrices only after offline hash correction; no exact query sets |
| Optional, comparable engine | Same optional orchestration contract; host-owned per-cell typed accounting | Control and candidate both made zero typed evaluations |
| Whole-task speed and usage | Native model-attempt traces, runtime footers, arm wall including cleanup; cumulative failed predecessor | Table above; two earlier requests retain unknown usage |
| Preserve failed attempts | Exclusive admission markers and immutable initial/recovery receipts | Four original arm executions remain failed, not retried until success |
| Preserve paid semantic work | Exact final session text, trace IDs, response hashes and one-use lookup ledger | All 195 exact replies consumed, no extra inference |
| No semantic outcome editing | Exact authored code extracted from executed repair trace | One hash expression changed; labels, quotes, joins and readers unchanged |
| Reproducible scoring | Fresh public grader and portable evidence command below | 426/510 and 404/510, all 510 cells included per arm |
| Product boundary repair | Real public prompt capture and full-ctx execution, before/after clock tests | Explicit hash contract, unchanged disabled prompt, opt-in root deadline fixed |
| Safety and cleanup | Native receipts for both arms | Original authentication unchanged; private copies removed; owned bridges stopped |

## Reproduce without a provider or private machine

From the repository root, Python 3.9+ standard library only:

```sh
python3 -B -m bench.jev.long_task_salvage.verify
python3 -B -m bench.jev.long_task.grade \
  bench/jev/long_task_salvage/results/offline-20260917/generative/prediction.json
python3 -B -m bench.jev.long_task.grade \
  bench/jev/long_task_salvage/results/offline-20260917/optional_typed/prediction.json
```

The verifier checks retained hashes, exact response occurrence bindings, reconstructed lookup bundles, used-reply ledgers, the single program correction and fresh scoring. Derived float metrics allow at most `1e-15` absolute roundoff between Python versions. Counts, labels and structural fields are exact. It does not authenticate a remote provider, inspect private session files or verify unavailable historical executable bytes.

For full native offline execution, the specifically retained optimized binary with SHA-256 `bd483035a03570124570f68c44532bb9070815af06f556ada4b4fc2f6370d222` is required. This intentionally does not silently substitute a newer binary:

```sh
python3 -B -m bench.jev.long_task_salvage.replay \
  --binary "$STUDIED_AZDAJA_BINARY" \
  --failed-results "$PWD/bench/jev/long_task_recovery/results/native-20260917" \
  --records "$PWD/bench/jev/long_task_salvage/records" \
  --output "$JCODE_SCRATCH_DIR/new-long-task-offline-replay"
```

`JCODE_SCRATCH_DIR` must be an existing directory outside the repository. The output must not already exist. No key or subscription is needed. The duplicated large lookup bundles are reconstructed from retained text; their original hashes and exact programs remain in each `*-binding/` directory.
