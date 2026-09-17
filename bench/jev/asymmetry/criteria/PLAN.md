# Separated criteria and inverse-question study

This is one later exploratory intervention on the already observed row645 development set, not a repair or replacement of earlier frozen receipts and not a row651 intervention. No new memory/RAG work. Criteria are designed after aggregate/error inspection, not blind model selection.

## Fixed inputs and treatment

Use all227 physical May occurrences of the exact hashed `bench/oolong/context-131072.txt`. Preserve raw lines, duplicates, dates and occurrence IDs. Gold is detached and read only by the grader. Four contiguous blocks have63,63,63,38 records. Each block gets THREE SEPARATE requests with byte-identical state, not three framings in the same question batch. Arms are historical control, same question plus explicit true/false criteria, and inverse spam with swapped criteria. Exact wording is frozen in prepare.py. The inverse explicitly asks 'Is this spam?'.

Block orders rotate deterministically: control/ham/spam, ham/spam/control, spam/control/ham, control/ham/spam. This avoids complete treatment-order confounding but is not randomized replication and does not establish independent errors.12requests total,681Noul questions. No arm sees sibling questions or outputs. All state and question bytes count toward observed input usage. Questions are not assumed free.

## Predeclared outcomes

Primary: FP+FN of each arm versus the fresh control on the identical227 occurrences, using p>=.5 for ham and spam<.5 for ham from the inverse. Report FP,FN,paired corrections/regressions,count bias,sum ham probability. Secondary: two agreement policies, control/inverse and criteria/inverse. If ham and inverse-spam decisions conflict, mark UNKNOWN, never silently negative. .5/.5 is disagreement. Report unresolved coverage and errors among agreed decisions. Shared wrong agreements remain wrong. Neither arm nor agreement authorizes approval. Decision count range from unresolved entries is not a confidence interval or truth bound.

A lower descriptive error count is a development-panel improvement only. No generalization, statistical superiority, calibration theorem, semantic independence, or production adoption follows. Duplicated message texts mean227 occurrences are not227 independent observations. Do not tune thresholds or wording after this run. Failed/partial arms are retained and excluded from matched triplets explicitly.

## Operational contract

Retained native binary SHA13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32, requested/returned Jev identity jev-1.13.0. Same actual start/load/exec/final/reentry/reduction/kill public path as earlier experiments. Store request bytes, body, judge_stats, custody checks, final reentry and exact reduction. Direct typed HTTP is NOT generative model tracing. Require no generative trace file and0logical llm calls. Validate per-cell attempts=1/provider_requests=1/cache_hits=0/questions=count and native request/body identity. Retain observed usage even on crossing failure. Completed terminal receipts must remain within180seconds including cleanup. A stopped receipt may finish cleanup later, but only calls completed within the original deadline are quality-eligible.

Ceilings:12typed requests,681questions,250000reported input tokens,100000reported output tokens,180seconds wall from native campaign creation, one request per cell and no retries. Stop on invalid shape, missing/unknown usage, changed code/model, lost source binding, deadline or budget crossing. Preserved crossing response is not quality-eligible. Budget is a stop envelope, not a billing guarantee. Input-price estimate uses documented $0.042/M only, not an invoice.

## Admission and reproducibility

Public commands use `python3 -B -m bench.jev.asymmetry.criteria.run`.
Default prints offline plan only. `--offline --azdaja <retained binary> --output <fresh directory>` exercises every prepared pack and final reduction without inference or credentials. It is not quality evidence. `--seal --azdaja <binary>` freezes all code/tests/plan/source and binary. Commit seal before admission. `--live --acknowledge-provider-calls --azdaja <binary> --credential-state-root <private attached root> --output <fresh directory>` requires exact seal and atomically exclusive `.started` marker. No stopped campaign is restarted with a new output. The private attached root is never committed. Clean it with actual detach after terminal and preserve the user's original attachment.

Replay uses `python3 -B -m bench.jev.asymmetry.criteria.grade --receipt-dir <terminal folder> --output <fresh report>`. It checks runtime/caps, frozen source, native calls/stats, complete IDs, all reported/unknown usage, actual reentry and final reduction. Hash consistency is evidence custody, not provider authenticity. Fault tests cover forged completion, missing calls, altered source/answer/usage/runtime, budget crossing, deadline, unknown usage, and safe output refusal. Actual offline public execution must pass before any live call.
