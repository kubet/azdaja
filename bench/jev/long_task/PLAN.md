# Fresh long-task native RLM comparison

Status: prospective, no inference admitted until source, executable, methods and admission seal are retained. This is not a rerun of an old closed panel.

## User outcome

Produce a complete, cited contract-screening matrix and four dependent set queries from all 102 official CUAD test contracts. Compare actual native `az solo` model-authored workflows, not just leaf-call speed. This is annotation-based screening, not legal advice or deep legal reasoning.

## Frozen source and output

- Official CUAD commit `67faa0e6023b04fcaae6cc09497ab00e5d63a2a2`, test JSON SHA256 `007b6a40b0c65247f881627375c3d2e9b6aeeb5dfa89957494feed0765a1a073`.
- All 102 full contexts in official order, 4,779,822 raw UTF-8 bytes and 4,778,515 characters. The loaded JSON wrapper has its own exact hash. This is NOT a claim of a measured million source tokens. Report provider token usage, not bytes/4 as a tokenizer measurement.
- Five official clause categories for every contract, 510 cells. Source-only corpus and category definitions go to each arm. Expert presence annotations and 374 exact expert spans remain in a detached scorer.
- Every cell is yes/no/unknown. Yes must include a 20..600-character verbatim quote from that same contract. No/unknown must have an empty quote. Source equality, quote validity and expert-span support are separate checks.
- Four queries use the returned matrix: assignment OR change_control; termination AND liability_uncapped; liability_cap AND liability_uncapped; (assignment OR change_control) AND NOT termination. Each query partitions all 102 IDs into yes/no/unknown using three-valued logic. Missing cells never become no.
- Output schema is fixed before admission. All cases, including failures and abstentions, remain in denominators. No outcome-driven exclusions.

## Arms and fairness

Run once each, serially in declared order: `generative`, then `optional_typed`.

Both use the SAME new native optional-engine planner contract, model `gpt-5.6-sol`, OpenAI subscription route, medium reasoning, the same complete context, task, schema, generative limits, and enabled compiled typed capability metadata. The generative control's task forbids `judge_many`; its private state root has no attached TypeSafe key and its environment has no TypeSafe key. Its host-trusted typed attempts must be zero. The optional arm may choose `judge_many`, ordinary `llm`/`llm_batch`, or combinations without an imposed threshold or decomposition. Only that arm gets an opaque private copy of an existing attached credential.

This is a prospectively instruction-restricted capability ablation. It is NOT a comparison to the old default solo prompt, which forces a different repeated-manifest policy. No host-authored semantic loop, secretly supplied solution, extra root repair or outcome-tuned prompt is allowed. Standard native bounded transport/setup recovery is retained and fully counted. A control attempting the forbidden typed route is a protocol failure, not silently repaired by the controller.

The model authors its program, partitions, dependent calls and reductions. The controller only supplies source, budgets, isolation, execution and grading. It never supplies gold, candidate gold spans, useful final labels or a preselected winning plan. Both arms may inspect every source byte. No source truncation is introduced by the controller.

## Resource and admission policy

- One `solo` invocation per arm. Exclusive campaign and per-arm started markers, exact executable/method/input hash seal, no overwrite and no rerun after entry.
- Maximum 150 generative child calls per cell, 120 seconds per generative request, 1800 seconds per native cell, 2100 seconds total per arm including planning and cleanup. Controller does not restart a failed arm. Native repair is permitted only by the product's unspent-evidence policy; typed physical attempts prohibit root repair.
- Generative observed input ceiling 6,000,000 and output ceiling 500,000 per arm, at most 160 observed logical request IDs including root/repair calls. Monitor actual trace events and stop on known crossing or unknown entered-turn input/output. Tokens from an already entered/in-flight call remain accounted even if they cross a ceiling. This is an observed-usage stop, not a provider-side hard spending limit. Completion-only native attempt traces may not record an in-flight call after hard interruption, so interrupted totals are lower bounds with that unknown explicitly retained.
- Typed maximum 160 requests, 4096 individual questions, 90,000 serialized request bytes, 262,144 response bytes, 4,000,000 known input tokens, 30-second request timeout, and the shared cell deadline. These are safety ceilings, not a suggested plan. Failed typed transport poisons the cell. No controller retry.
- A supervisor outlives the interactive tool's 600-second limit, has an absolute deadline, bounded outputs, progress/checkpoints, and terminates/reaps only its own process group and identified private API bridge.
- Fresh private state, source-only cwd, isolated Jcode runtime and opaque authentication copies outside the repository. No global config/install/auth mutation. All private credential copies removed after the run. No secret bytes, config attachments or auth stores in published receipts.

## Measurements and prospective success bar

Primary quality: complete 510-cell coverage, fixed-denominator accuracy, per-category confusion matrices and macro-F1, explicit unknown/unobserved counts, exact quote validity and expert-span-supported citation rate, plus each dependent query's exact-ID set precision/recall and consistency with the returned matrix. An answer cannot win by dropping difficult cases or producing faster incomplete output.

A bounded workflow benefit requires BOTH arms to finish valid complete outputs, optional accuracy no more than 0.01 below control, macro-F1 no more than 0.02 below, supported-positive citation rate no more than 0.02 below, no dependent-query macro-F1 loss greater than 0.02, and at least 20% lower complete wall time. These are engineering stop bars on one fixed corpus, not significance tests. Report exact metrics even when the bar fails. Also report raw runtimes and ratios without treating a failed/partial arm as a speed win.

Timing is cold invocation through final validation and owned cleanup, including root planning, children, deterministic code and retries. Report setup separately. Record every actual logical/physical/setup/entered generative event and identity, input/output/cache/reasoning known values and unknown counts. Host-owned typed snapshots report attempts, successful/failed requests, questions, cache hits, input/output known/unknown and evaluation wall time. Do not trust model-authored accounting. Hard interruption without a native footer means typed accounting is unknown, not zero.

TypeSafe input-price arithmetic may be shown at $0.042/M with a dated documentation reference. It is an estimate, not a bill. Subscription billing is unknown. No dollar ratio or 1000x cost-parity claim.

## Controls and limits

Provider-free tests exercise the actual public solo CLI with local deterministic root stubs, full input hash, capabilities, default-disabled preservation, feature-off availability, trusted stats and failure handling. They prove integration, NOT live quality. Scorer mutations cover source mismatch, duplicate/missing/extra IDs, wrong quotes, unknowns, forged joins and unchanged gold/source custody.

A constant no/unknown output is a negative scoring control, not a competitive static model baseline. No exclusive RLM advantage, superiority to a matched static extraction system, cross-corpus generalization or statistical significance follows from this pair. Corpus/annotations may be in training data. Clause presence is defined by CUAD annotations, which are not infallible legal truth. Root/fixture authors have seen aggregate gold, models do not receive it. Time ordering/cache/load is a possible one-pair confound.

If native integration, public offline rehearsal, source/scorer validation or resource admission fails, retain the failure and stop before inference. If a live arm fails, retain it, run the other arm only under its original independent admission, and report no successful paired benefit. No post-hoc optimization of this panel. No README claims, provider outreach, memory/RAG work or release.
