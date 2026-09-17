# Exact-source selection development experiment

This is a new application hypothesis, not a retry of the frozen seven-task critic study. That result remains negative. No outcome is promised here.

## Hypothesis and useful output

Can native typed selection produce a correct structured developer-reference table from exact source spans, at lower observed latency than a competent generative closed-set selector? Code enumerates candidates, the semantic leaf selects their role, and code copies the exact source value with its occurrence/provenance. The output is the table, not a count of valid API envelopes. A wrong source-backed value is still wrong.

This does not test autonomous RLM plan discovery. Root-authored control code runs inside the actual persistent evaluator. Ordinary Python with the same selections is an explicit projection counterfactual and should produce the same table. No RLM-specific speedup or novelty claim follows from source custody or operator availability.

## Inputs and controls, frozen before inference

- Independent author supplies 18 tasks in three blocks of six, from exact public repository excerpts at released source `ca320c3607116447a506d6c8429489f1b30157a9`. Intended balance: six direct controls, six contextual-role cases, three absent values, three genuinely underdetermined values. Honest source constraints may require a documented amendment before inference, not after outcomes.
- Only task IDs, questions, exact source records and candidate occurrences enter model state. Family labels, gold, rationales, grader and earlier study outputs do not. Source metadata is identical for both semantic arms.
- Version candidates retain the optional `v`, two/three numeric components and optional suffix. Quote candidates copy inner single-backtick/single-quote/double-quote spans without unescaping. Identical values at different offsets remain separate. No top-k candidate truncation. Above 128 candidates or the byte envelope, stop before inference.
- Kernel/parser and baseline are frozen before root reviews new gold. Source gold and all methods are then reviewed and committed before any provider call. Both models are fresh with respect to these task answers, but this is an authored, small development panel, not representative or a held-out generalization claim.
- **Strong baseline:** native `llm`, same generative model as the prior study, selects only IDs from the identical source/candidate/question pack. Deterministic code copies its choices too. Do not compare source-copying Jev against a generative arm forced to retype values.
- **Typed arm:** native `judge_many`, Choice over each task's candidate IDs plus `no_match`, `ambiguous` and `not_covered`. These distinguish absent source values, unresolved source alternatives and a uniquely established value omitted by the parser. Preserve every returned probability and all source candidates. No confidence/entropy cutoff, automatic truth promotion, hidden evidence deletion or automatic escalation.
- **Cheap comparator:** frozen token-overlap over the question and each candidate's 100-character context. Remove only the fixed stoplist in `kernel.py`. Zero overlap gives no_match, tied distinct values give ambiguous, tied equal values choose the first occurrence. This is not a claimed state-of-the-art extractor; the closed-set generative selector is primary.
- Copying a selected span preserves bytes, not semantic correctness. Test an intentionally wrong but valid ID: projection must produce the wrong value and the grader must fail, not repair it from gold.

## Primary bar and progressive stopping

An acceptable row has the correct value/sentinel **and a supporting source occurrence**. Duplicates are judged by authored acceptable offsets, not string equality alone. Grading is executable, separate from model inputs. No subjective prose score is substituted for this structured-task result.

The development screen requires at least 17/18 correct typed rows, no typed false selection when the source is absent/underdetermined, and no loss against the generative baseline on the completed panel. Stop remaining inference as soon as two typed row errors make 17/18 impossible, or at the first false selection for unresolved gold. Report all observed rows, paired rows and unjudged rows explicitly. Early stopping cannot be presented as a full-panel comparison.

Even a quality pass is not a demonstrated benefit by itself. Require either a strict complete-panel quality gain or matched quality with typed end-to-end median block latency at most two thirds of the baseline's. Three block timings are descriptive, not a population latency guarantee. Unknown billing precludes dollar-savings claims. Failure of any bar is a negative result for this workload, not a reason to change the questions or rerun.

## Resource envelope

- At most **3 typed HTTP requests / 18 questions** and **3 logical generative calls**, one of each per block. No root retries. Existing `jcode-api` may use at most two entered inference turns per logical `llm`, independently of up to four session-setup attempts. Retain its native trace and distinguish logical requests, setup attempts and entered turns. Failed metadata may be unknown, and an entered-turn number is an ordinal, not a boolean.
- Requested generative model `gpt-5.6-sol`, provider `openai`, medium reasoning. Requested typed alias `jev-latest`, expected returned string `jev-1.13.0` observed previously. A mismatched string stops, not repins. A reported string is not authenticated immutable weights.
- At most 150,000 cumulative known typed input tokens, 131,072 request bytes, 262,144 response bytes, 20 seconds per typed request, 180 seconds per generative cell, 12 minutes for the entire run. Missing usage remains unknown. Preserve known crossing usage, stop further calls, never infer a dollar cap.
- Order is baseline then typed in block 1, typed then baseline in block 2, baseline then typed in block 3. Grade only after both outputs in a block, except transport/contract/resource failures stop immediately. No best-of sampling.
- Only the originally user-supplied host key may be used. Keep it out of state, prompts, code, config, receipts and child generative environments. Private temporary credential must be removed when the run ends. Output directory must be exclusively created, no overwriting frozen results.

## Public-interface acceptance

Run the actual source-built installed executable through start/load/exec/final, then re-enter to inspect the exact table, full typed distributions and original candidate pool. Compare native tables to an independent ordinary-Python projection of the identical selected IDs. Exercise disabled mode without a key before live opt-in. Preflight source digests against pinned Git objects and assert they do not change during the run. Keep source/binary/protocol/request hashes and actual failure/usage evidence.

Offline checks include duplicate occurrences, Unicode byte offsets, no-match/ambiguity, wrong-but-valid choices, unknown IDs, incomplete/extra answers, duplicate JSON keys, changed sources, malformed offsets, family/gold exclusion, output non-overwrite and the real persistent evaluator path. These establish workflow integrity, not model quality. All live efficacy claims depend on the subsequently recorded actual task outputs.

## Pre-inference clarification

Before any new provider call or root inspection of gold, `not_covered` was separated from `no_match`. A missing parser candidate must not be advertised as an absent source value. The version/quote parsers, deterministic scoring, task count and inference budget are unchanged from `dec3a03`. Candidate-omission behavior is an offline contract check in this panel, not a claimed live semantic result.
