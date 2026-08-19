# The dragon that learned to count its dead

*A launch saga about grep disease, five scorer kills, and a 199-row mortality war.*

Azdaja began with a simple idea: a language model should not have to swallow a huge document every time it wants to answer one question. Keep the complete UTF-8 input in a local evaluator. Let code do exact selection and reduction. Send only bounded semantic work to model calls. Accept a final answer only after the result is structurally complete.

The implementation fit in one binary. Learning where it broke took considerably longer.

> **Launch result:** **68.64164968987583%** on a fixed 199-row, validation-derived RAH slice, with 185 execution successes (valid predictions) and 14 retained failures counted as zero.

That is a private, single-arm diagnostic—not an official leaderboard result, not a claim of model superiority, and not evidence that every large-context task becomes easier. The fixed denominator matters: a dead row is not quietly removed from the average.

## The grep-disease autopsy

We called one 30-row stress slice the disease scout. Its hard rules included a semantic-path check and zero final answers from the grep shortcut. The early read was tempting: perhaps the long-context system was sick because roots were searching for a convenient string instead of doing the semantic work.

Path instrumentation killed that story.

Across the retained later disease-scout artifacts, accepted final answers took the intended semantic path and the grep-path count stayed at zero. Yet successive scouts still died when seven failures made the required 24-of-30 execution floor mathematically unreachable. One stopped at 16 successes in 23 retained rows; the next at 18 in 25. A later paired scout finally completed both 30-row arms at 24 and 27 executions, but neither cleared its preregistered completed-row score gate.

The disease was not one bad search command. It was a stack of contracts:

- model-authored parsing could collapse multiple physical records into one;
- semantic manifests could be incomplete or malformed;
- transport and route evidence could fail closed;
- outer row deadlines could expire after substantial work;
- a high completed-row score could disguise an unacceptable fixed-denominator result.

So the treatment changed. Exact line scanning became a typed operation with explicit admission rules. Semantic work moved behind complete, positional manifests. Occurrences, representatives, and expanded outputs received separate accounting. Execution and correctness stayed separate. No partial score was allowed to resurrect an invalid schedule.

The autopsy's most useful finding was negative: **zero grep finals did not mean the system was healthy**. Removing a shortcut is not the same as proving a pipeline.

## Five scorer kills—all ours

We use “scorer” here as shorthand for the whole fail-closed measurement path: terminal validator, scorer, and score custodian. These were our integration and control-plane defects. They were not misconduct by a benchmark author, provider, or model team.

1. **The missing handoff.** A completed LongBench job reached its terminal path, but the validator did not receive the already-captured public payload bytes it needed for its leak check. The cohort stayed frozen; the control code was repaired forward.
2. **The byte-order assumption.** Another 189-row LongBench run was rejected because its validator demanded one JSON key order even though the product emitted a valid, duplicate-free field order. That run remained terminal-invalid and unscored.
3. **The nullable-telemetry trap.** A RULER effort sweep completed 60 fixed inference rows. Its one-shot scorer then assumed a retained failed row had usage telemetry. It did not, so the scorer stopped without a report. The failed scorer record remained immutable; only an explicitly authorized, separately rehearsed retained-evidence scorer produced the later aggregate.
4. **The unsupported value type.** A 199-row RAH run passed no-score validation, then its frozen scorer encountered a valid released answer type it did not support. Again: no improvised score, no replaced row, no silent parser change. A separately authorized repair had to reproduce the exact input shapes synthetically before it could score the retained evidence once.
5. **The ceremony that never exercised the ceremony.** A later full exam completed, but the score custodian and diagnostic calculator disagreed about an output filename and one report-envelope field. Identity checks had passed; the exact production layout had never actually been executed end to end. The mechanical attempt was retained, the custody rule was clarified, and the repaired path had to prove first success and second-success refusal.

Five kills taught one rule: a scoring test that merely imports the scorer is not a scoring rehearsal. The real preflight must execute the frozen filenames, directory shape, report envelope, sentinel behavior, and refusal path over synthetic data. Otherwise “exactly once” can mean “exactly once, incorrectly.”

## The mortality war

An earlier fixed-199 candidate had **38 retained deaths**. Those zeros were not an accounting nuisance. They were the product problem.

The response was not to widen the denominator's exit door. We classified death before changing code. We separated candidate failures, provider-turn failures, containment failures, and controller uncertainty. We added an independent hard reaper so a wedged row became a row-local zero instead of freezing the campaign. The controller kept ordered append semantics and did not release a worker slot until cleanup was proved.

That controller survived a complete exam, but 15 rows still died: seven in the containment family, four at provider turns, and four in semantic candidate work. Ten of the 15 belonged to the broader provider-infrastructure family. The top recurring remediable mechanism was narrower: six eligible second attempts deterministically reopened the preserved workspace of attempt one and failed before doing useful work.

Only that class was changed. Each logical attempt received a fresh sibling workspace while retaining one benchmark repetition, one combined budget, the same row wall, and the original attempt-one evidence. Timeouts, semantic policies, prompts, and non-top mortality classes were left alone. That restraint matters: a taxonomy is not permission to tune everything that looks ugly.

A fresh 40-row mini gate then completed all rows with 37 execution successes. Its one bounded provider retry succeeded in the new attempt workspace. The next terminal campaign used a wholly fresh schedule, completed and ordered all 199 rows, ended with no owned processes, and accepted both bounded retries. Only after terminal validation did its score path produce a first successful aggregate.

Different schedules are not a paired causal experiment, so we do not credit every recovered row to the workspace fix. We can claim the narrower facts: the observed collision was reproduced, the specific mechanism was removed, and the retry path exercised successfully. The launch result is printed above.

## The ridge after launch

Against the paper's 64.38 bare-RLM reference, the launch number is
**+4.3 percentage points** after rounding. It is the highest bare-RLM number in
the class ladder we print, not proof of a global best-published result: our run
is a private, single-arm diagnostic, the literature values were not rerun as
controls, and no superiority follows. Codex at 71.75 is the visible next summit,
not a result we claim to have reached.

The token story has a missing row too. Provider receipts cover root usage for
198 of 199 rows: 5,403.36 mean total root tokens and a 4,723 median. We do not
impute the missing row or relabel that as an exact 6K, complete-campaign, cost,
or efficiency result. The [sanitized terminal receipt](../bench/results/gpt-rah199-mortality-v3-terminal-public.json)
binds those aggregates to the retained private evidence.

## The five-game second act

> Five-game diagnostic: local-shadow-RHAE Δ was 0.0 in each game; unchanged-feedback counts were 646 baseline vs 654 Ember (+8, +1.24% of the baseline raw count).

The v9 pilot contains one fixed-order pair per game, baseline then Ember, under the public identity Ember. It used seed 0, a fresh game/runtime per arm, the same pinned direct-Claude Sonnet common configuration, and per-level action caps of 5× the published human baselines. Ember alone staged the managed Azdaja skill, with one invocation after two completed turns. There was no randomization or replication, so the diagnostic has no variance or uncertainty estimate.

| Public game | Ember − baseline local shadow RHAE difference | Baseline unchanged-feedback actions | Ember unchanged-feedback actions |
|---|---:|---:|---:|
| ls20 | 0.0 | 92 | 103 |
| ft09 | 0.0 | 186 | 208 |
| vc33 | 0.0 | 0 | 0 |
| ar25 | 0.0 | 137 | 110 |
| wa30 | 0.0 | 231 | 233 |
| **Total (counts only)** | — | **646** | **654** |

An unchanged-feedback action is a non-`RESET` action whose official post-action feedback exactly equaled the immediately preceding official feedback. Ember recorded **+8 (+1.24% of the baseline raw count)**. Total actions were not retained, so this is not an action-normalized rate, efficiency result, or improvement claim. All five observed paired differences were 0.0, but the missing absolutes leave equal zero and equal nonzero arm scores indistinguishable. The separately hash-bound [v9 manifest](../bench/arc3/mini-pilot-live-manifest-v9.json) supplies method, lane, hashes, freshness, and scoring; the minimal [sanitized v9 result](../bench/results/arc3-ember-five-public-v9-result.json) is not self-describing and has no result sidecar.

The retrieval-only interrogation made no game or provider request and started no new experiment. All ten closed scorecard detail requests returned HTTP 404 despite the pinned contract's open-or-closed description, and the HTML route redirected to the generic ARC-AGI-3 page. It recovered no absolute per-arm local shadow RHAE, levels completed, or total actions, and those values are absent from retained v9 artifacts. The [sanitized interrogation receipt](../bench/results/arc3-scorecard-interrogation-public-v1.json) contains no scorecard identifiers, credential, host path, or raw log.

A separate fresh `vc33` smoke was a distinct pair, not a reconstruction of v9. Baseline and Ember each issued 35 actions with per-level counts `[35, 0, 0, 0, 0, 0, 0]`, completed zero levels, had local shadow RHAE 0.0, recorded `0 / 0 / 0` in the separate unchanged-feedback / revisited-state / repeated-known-control counters, emitted 36 journal records, and stopped at `ACTION_BUDGET`. The observed paired local-shadow-RHAE difference was 0.0. This says only that both arms had a zero local-shadow score and completed zero levels in that smoke; it does not supply the missing v9 absolutes or an official ARC score. The [sanitized smoke receipt](../bench/results/arc3-vc33-smoke-v2-public.json) preserves that boundary without publishing journal streams.

The memory-efficiency hypothesis remains open. A fresh five-pair package is held as gated post-public source: it cannot construct an ARC or model client until an independent public-visibility receipt and exact owner-GO binding validate, and it reuses no smoke artifact. No new ARC or provider run supports this documentation. The detailed [benchmark card](../bench/arc3/README.md#benchmark-card) carries the audit table and not-run boundary.

The separate transport scout's 0.00/0.00 tie came from 20 pre-inference setup
failures, with zero successful provider turns and zero agent-class calls. It
observed no root choice, so it is neither genuine disuse nor a discoverability
measurement. A repaired activation study is post-launch v0.2 roadmap material
only; it is not authorized here. The
[sanitized post-mortem](transport-flip-postmortem.md) records that boundary.

## The first run became a benchmark

The one-line installer now keeps the managed executable named `azdaja` and atomically adds `az` as its short PATH alias without replacing a foreign path. Its three-line output reports both names and ends with `az doctor`. Bare `az` and `azdaja` print the same exact five-line help, led by the short command; on an interactive color terminal only, a 16-row indexed truecolor half-block banner precedes it. Non-TTY output, `NO_COLOR`, and `TERM=dumb` remain text-only. Cargo installation remains honestly `azdaja`-only.

That source change supersedes the previously retained v0.1.2 release candidate. Its 16-cell matrix and native real-adapter receipt remain immutable historical evidence for the old bytes, not release validation for current source. New Darwin arm64 and Linux x86-64 assets, checksums, native exact-help/alias checks, and the full release matrix are required before readiness. The [readiness supersession receipt](../bench/results/v0.1.2-candidate-readiness-superseded-public.json) repeats no old candidate hash as final.

The provider-free [alias delta receipt](../bench/results/install-alias-delta-v0.1.2-public.json) covers both supported platform selectors across each detected harness, `all`, no-harness refusal, and already-installed update. It proves local installer branches, exact five-line help, `doctor --caps`, solo parity, idempotence, and foreign-path refusal through `az`; it is not a native cross-platform or provider validation.

## Why a dragon

Aždaja is a dragon in Serbian folklore. For this project, the image is also an architecture diagram: one persistent body holds the context; a root writes compact analysis code; multiple model-call heads handle bounded semantic questions; deterministic code joins their answers.

The useful part of the metaphor is not invincibility. Dragons in stories can lose heads. Ours certainly did. The useful part is that the body remembers.

It remembers every failed row in the denominator. It remembers every consumed scoring boundary. It remembers which schedule is terminal and which retry already happened. It preserves the evidence that makes a flattering reinterpretation impossible.

That is what we are releasing: not a claim that long context is solved, but a small context-virtualization tool and the scar tissue that made its boundaries legible. Azdaja can keep a large input local, give a model a bounded computational surface, delegate selected semantic work, and fail closed when the answer contract is incomplete.

The score is part of the launch. The deaths are part of it too.
