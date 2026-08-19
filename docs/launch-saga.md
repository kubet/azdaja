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

## Why a dragon

Aždaja is a dragon in Serbian folklore. For this project, the image is also an architecture diagram: one persistent body holds the context; a root writes compact analysis code; multiple model-call heads handle bounded semantic questions; deterministic code joins their answers.

The useful part of the metaphor is not invincibility. Dragons in stories can lose heads. Ours certainly did. The useful part is that the body remembers.

It remembers every failed row in the denominator. It remembers every consumed scoring boundary. It remembers which schedule is terminal and which retry already happened. It preserves the evidence that makes a flattering reinterpretation impossible.

That is what we are releasing: not a claim that long context is solved, but a small context-virtualization tool and the scar tissue that made its boundaries legible. Azdaja can keep a large input local, give a model a bounded computational surface, delegate selected semantic work, and fail closed when the answer contract is incomplete.

The score is part of the launch. The deaths are part of it too.
