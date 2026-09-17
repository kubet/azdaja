# Exact-source selection: actual native result, 2026-09-17

**Decision: do not promote typed selection as a quality-preserving replacement for `llm`.** The actual workflow completed, but the predeclared useful-output bar failed. Faster execution did not compensate for losing a task that the matched generative baseline answered correctly. No rerun or outcome-driven threshold was used.

The source-find, semantic-select, exact-copy pattern follows TypeSafe's [pre-parsed value extraction cookbook](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md). The pattern is not claimed as Azdaja novelty. This study tests its usefulness through Azdaja's actual native boundary with a stronger matched selector baseline.

## What was executed

Methods/panel were frozen at `9f38455` before inference. The binary was the private source-built all-feature installation from runtime source `ed0403baea72d0f2656e405a2e7454dd4393f24e`, SHA-256 `0aefe8e63c385b6f926d0f4264440b308d3eaca5c30c9cce6d1d4b0493a7f237`. It is not a published release asset. All source excerpts are from released public source `ca320c3607116447a506d6c8429489f1b30157a9`.

The public `start → load → exec → final → re-entry → kill` workflow ran real `judge_many` and `llm`. Both received identical question/source/candidate packs and selected occurrence IDs. Independent evaluator-side code copied the exact spans into tables. Every native table matched ordinary Python projection of the same choices. Sources, full typed distributions, and tables survived re-entry. The disabled/no-key probe made zero attempts. Cleanup returned 0.

| Observation | Typed Jev | Matched generative selector | Fixed lexical control |
|---|---:|---:|---:|
| Correct value/sentinel **and** provenance | **17/18** | **18/18** | **7/18** |
| Unjudged rows | 0 | 0 | 0 |
| Incorrect selected literal on unresolved gold | 0 | 0 | Not a promotion candidate |
| End-to-end block seconds | 1.153, 1.404, 1.162 | 2.982, 2.505, 2.529 | Not a matched semantic latency claim |
| Median block seconds | 1.162 | 2.529 | Not measured for benefit |

Typed/baseline median ratio was **0.459**, approximately 54% lower in these three observations. This is not a population latency guarantee. The predeclared bar also required no loss against the baseline. **Quality bar: failed. Benefit bar: failed.** The process status `completed` means the protocol completed, not that quality passed.

There were three typed HTTP requests covering 18 questions, three same-cell cache hits without new requests, and three logical generative calls with three entered turns and no setup/failure events in the retained trace. Returned typed model string was `jev-1.13.0`; native generative trace reported `OpenAI` / `gpt-5.6-sol`. These strings do not authenticate immutable model weights. Known typed usage was 18,128 input and 1,707 output tokens, with zero requests missing input usage. The generative trace reported 14,316 input and 123 output tokens, with zero reported cache-read/write tokens. Provider token accounting and prices are not interchangeable. Billing and dollar savings were not inferred.

## The actual failure, not an aggregate excuse

`s18` asks for one XDG home variable without specifying configuration, state, or data. The source names all three. Correct result: `ambiguous`. The generative selector returned `ambiguous`; Jev returned `no_match`.

The retained typed distribution was `no_match: 0.50`, `ambiguous: 0.28`, a `HOME` candidate: `0.20`, and 0.02 across other outcomes. Returned confidence was 0.41. This is a distinction between **evidence of multiple applicable alternatives** and **absence of a value**, not a copied-value hallucination. All 12 literal selections were correct with supporting occurrences. Five of six absence/underdetermination results were correct.

Preserving the full source and distribution makes the error inspectable. It does not fix it. A post-hoc uncertainty threshold or extra generative call could change this result, but would be a different, untested policy. Neither was applied. The single error arrived in the final block, so the two-error early-stop condition was never reached, and no unresolved case was falsely turned into a selected literal.

## Requirement-to-observation map

| Requirement / changed output | Concrete check | Observed behavior |
|---|---|---|
| Genuine useful table, not envelope counts | Frozen 18-row value/sentinel + occurrence grader | Typed 17/18, baseline 18/18, bar failed |
| No privileged control or forced generative retyping | Actual request/prompt payload comparison | Same source, candidates, questions and instructions; both select IDs |
| Public repository sources only | Git blob/line-bound check for every excerpt | All 18 tasks match pinned public source, 12 unique source records |
| Do not assume parser coverage | Candidate omission, duplicate, Unicode and wrong-valid-ID tests | Missing candidate remains `not_covered`; wrong ID remains wrong |
| Preserve alternatives and uncertainty | Actual final re-entry compared to all input packs and typed observations | All original candidates and full distributions retained |
| Actual native projection, not host-precomputed result | Real `exec` loops compared to independent Python materialization | All 36 semantic-arm rows and 18 lexical rows match their choices |
| Ordinary use remains possible | Disabled/no-key public probe | 0 attempts, no semantic call |
| Exact per-cell cache accounting | Repeated same actual `judge_many` input in each typed cell | 1 provider request + 1 cache hit per block |
| Budgets and progressive stopping | Actual receipt + timeout/crossing/stop regressions | 3 requests/18 questions, 3 generative turns, 12.36 seconds, no retries by runner, no cap crossing |
| Source/method/model identity | Frozen input digests, per-request native digest, model checks | Exact campaign hashes and strings retained |
| Failure cleanup and no credential in model state | No-follow bounded key read, isolated child env, outer owner cleanup, artifact scan | Ephemeral credential removed; no credential-shaped artifact copied |
| Non-overwriting outputs and no stale-state fallback | Occupied/symlink, timeout, method-change, invalid ID regressions | Rejected before inappropriate reuse/call |
| Public offline replay of final result | `python3 -B -m bench.jev.span_selection.replay` | Reconstructs 17/18 vs 18/18 and failed benefit with zero provider calls |
| Replay does not accept an edited success label | Four changed/rehashed artifact witnesses | Rejects corrupt response, false win, wrong native table and unmatched baseline state |

Before inference, all 25 kernel/runner tests passed with the actual installed binary and zero skips. After inference, the complete 30-test set including the five retained-result tests passed with zero skips. Independent read-only review checked all 18 gold/source occurrences before the call. These tests establish the specific workflow and accounting paths, not general semantic reliability.

After completion, the independent read-only reviewer rechecked frozen hashes, matched requests, source/distribution re-entry, all reconstructed grades and usage. It independently confirmed 17/18 versus 18/18, the s18 loss, the 0.459 latency ratio, 18,128 known typed input tokens and zero unknown-usage attempts. It performed no new inference. This is an independent agent review, not a human quality rating.

## Reproduce without inference

```bash
python3 -B -m bench.jev.span_selection.replay
AZDAJA_BINARY=/absolute/path/to/azdaja PYTHONDONTWRITEBYTECODE=1 \
  python3 -B -m unittest bench.jev.span_selection.test_kernel \
  bench.jev.span_selection.test_runner bench.jev.span_selection.test_replay -v
```

`results/native-20260917/MANIFEST.json` binds the 50 retained artifacts, method commit and historical runtime build. The replay verifies retained result consistency and re-grades the fixed panel. It does not replay live calls or authenticate provider-originated bytes. A fully fabricated coherent bundle is outside that claim.

This is a small authored, clustered development panel, not an independent sample or benchmark win. The earlier seven-task no-final-answer-gain result and retrieval counterfactual remain unchanged. **Product implication:** keep the typed leaf optional, preserve its evidence and alternatives, and do not replace generative selection or add a mandatory confidence gate on the strength of this screen.
