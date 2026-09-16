# Native useful-work development run, 2026-09-16

Frozen before obtaining new model answers. This is a NEW study, not a retry or repair of the two historical stopped synthetic campaigns.

## Question and arms

Does a native typed critic help Azdaja deliver correct, useful final developer answers on the seven fixed repository tasks? This small full-context panel can tie. It does not establish an RLM advantage over competent Python, large-corpus gains, general efficacy, calibration, or a moat.

1. Obtain one common initial draft via the actual Azdaja `llm` callable with all corpus and tasks. This is an actual output, not an oracle or gold answer.
2. **Self-review baseline:** same generative model, all evidence/tasks/draft, one review-and-correction call covering all seven answers. This is stronger than comparing Jev against an unreviewed draft.
3. **Distribution-informed review:** native `judge_many` evaluates each draft answer against the complete task and corpus using a fixed `choice` question: adequate / material_error / incomplete. Retain the entire distribution, not only the winning label. One generative review call receives all seven raw observations plus all evidence, tasks and drafts. It may accept, reject or investigate the critic's suggestions, but must justify final claims from source. No probability threshold drops tasks, evidence or alternatives. This matches the baseline's one correction opportunity and makes the extra typed call an explicit cost that must earn its place through final quality. This amendment was made before any new model calls, following the user's explicit request to preserve uncertainty and avoid arbitrary enforcement.
4. **Retrieval diagnostic:** one native batch ranks the 16 corpus excerpts for task Q1 using Noul, top 4 with stable source-ID tie breaks. Compare required-source coverage to a reproducible BM25 top 4. Do not use this diagnostic to replace or tune the final-answer corpus. Ranking is not completeness and cannot prove the broader engine hypothesis.

The initial draft is shared to control for differing draft errors. Baseline and typed review each receive at most one correction opportunity. Host-authored Monty control code is fixed, not automatically discovered by an RLM. The comparison isolates this review policy, not the value of Monty versus Python. Plain Python plus the same calls can implement this plan and remains a required future counterfactual before any RLM-specific performance claim.

## Inputs and budgets

Only `corpus.json` and `tasks.json` are model inputs. Never evaluation.json, grade.py, rubric, raw credentials, local memory, or unrelated repository files. Both inputs pin public source at d851113. Ground-truth authoring predates all new answers.

- Generative model: requested `gpt-5.6-sol`, Jcode subscription route `openai`, reasoning `medium`, record actual model/usage when available. Maximum 3 logical `llm` calls (draft + self review + distribution-informed review), each at most 180 seconds. Existing transport can internally enter up to 2 turns per ordinary llm call, so physical attempts are traced and bounded by that existing limit. No root retry of a failed call. At most 48 KiB per raw answer, no quality-driven reruns.
- TypeSafe: requested `jev-latest`, record actual returned identifier without claiming immutable weights. Planned 2 HTTP requests and 23 questions. Hard study ceiling 6 requests / 64 questions including failures, 250,000 known reported input tokens, 131,072 bytes per request, 262,144 bytes per response, 20 seconds per HTTP request. No automatic retries. Unknown usage is explicitly unknown, not free.
- Whole run: 12-minute wall limit. A transport/schema/deadline/resource error stops remaining TypeSafe work, preserves partial outputs and unknown usage, and cannot count as a completed quality result.
- Every native session is private scratch state, never the user's installed configuration. Save public prompts, programs, final outputs, raw validated observations, model trace, source/binary identities and timestamps. No key in artifacts. Preserve historical receipts and original binary.

## Acceptance and stop bars

Report final successful tasks / 7, fact failures, missing essential source groups, and blind prose accuracy/evidence/usefulness using the frozen rubric. Mechanical success alone is not a quality pass. Judge responses blinded to arm; one reviewer is still fallible, not a human study. Do not select the winning response per task after seeing scores.

No efficacy promotion if typed review loses any task the self-review baseline passes, leaves a dangerous false recommendation, or provides no useful quality/cost improvement. A tie with additional calls is negative for this workload. Cost requires observed accounting and prices, not request counts alone. Unknown billing prevents a dollar-saving claim. A small positive result is only a development observation requiring replication and harder task families.

The purpose of running is to decide where the feature is useful, not to force a win. Stop and investigate a failed contract instead of burning calls trying to reach a favorable score.
