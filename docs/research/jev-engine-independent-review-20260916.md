# Independent review: optional typed-engine mechanism laboratory

Date: 2026-09-16. Reviewer: independent reviewer `mouse`.
Final independent suite: 20:28:14–20:28:18 UTC. Additional boundary checks: 20:29 UTC.

## Verdict and scope

**The four material staged-handoff failures reproduced during the initial review are closed in the final snapshot below.** The independent final run passed **20 tests, zero skipped**, and six separately reconstructed boundary probes rejected unsafe re-entry while preventing access to old bound answers. No remaining blocker was identified for the tested, preregistered mechanism paths.

This supports a narrow result: an explicitly enabled, backend-neutral, host-side typed-judgment kernel can exchange bounded request manifests and validated results with a real persistent Azdaja/Monty session, then perform exact programmed reductions. It is **not** a native `judge()` function, automatic planner, completed production integration, or evidence of Jev semantic efficacy or superiority to `llm`.

All backends in this experiment were injected synthetic oracles. No provider request, credential access, model download, or production-memory mutation was performed by this reviewer. The old live pilot remains stopped with **zero validated live judgments**, and this review does not authorize reopening it. The reviewer changed only this new review document, made no implementation edits or commits, and preserved both earlier independent reviews.

## 1. Protocol and independent procedure

I read `jev-engine-mechanism-protocol-20260916.md`, all engine laboratory code and fixtures, and the test guards. The protocol's current hash matches the retained object at commit `ba636ef`; that commit's tree contains no `bench/jev/engine_lab/` files. This establishes the retained protocol/code version boundary, not an independently observed wall-clock history of untracked files.

The initial 15-test suite passed, but additional real-evaluator probes exposed handoff failures. I reported those before the coordinator changed implementation. Execution was paused during revision and resumed only after the stable-source signal. The coordinator implemented the fixes; this reviewer did not.

Final independent command:

```sh
python3 -B -m bench.jev.engine_lab.run
```

The invocation used a cleared environment with explicit local paths and scratch location. Tests deny socket connections and HTTPS construction, allow only the fixed local evaluator's `start`, `load`, `exec`, `final`, and `kill` subprocess commands, and record forbidden-operation attempts so a caught exception cannot hide one. Evaluator sessions use private scratch state and `/usr/bin/false` as the generative-provider command.

Observed result: **20 tests passed in 4.053 seconds, zero failures, errors, or skips**, on Python 3.9.6/macOS. Temporary test sessions and files were cleaned up. I did not create another result receipt or modify the coordinator's receipts.

## 2. Initial failures, fixes, and direct rechecks

The initial vulnerable engine snapshot had kernel hash `0c6d0243df3a7bba01979266f81d9207be406982ccb9a0de3f3ebf118a404513` and Monty handoff hash `addd72371192134125527e637510c2600181dddca1675248f69e0dd461ec1c22`. Its 15 green tests were not sufficient evidence for M5/M6.

| Executed witness | Initial observed result | Final independently observed result |
|---|---|---|
| After kernel validation, replace a response's model with `wrong-model` and set `P(yes)=1.5`. | Real Monty bound all three rows. The invalid probability remained resident, and the reduction reported complete. | Rejected inside the evaluator as `response observation mismatch`; session stopped and old bound answers inaccessible. |
| Swap only valid `response_json` values between a true `r00` and false `r02` request, leaving request/source/contract metadata unchanged. | Binding succeeded and a complete three-record reduction made two wrong pair decisions. Typed shape checking alone would not detect this swap. | Rejected as `response observation mismatch`, including when the caller recomputes mutable response hashes and edits a returned copy of the trusted binding. |
| Inject the process helper's `ValueError` failure during re-entry after a previous successful bind. | `session.stopped` remained false and the old bound stage could still be used. | Session stopped; old bound access rejected. This is an injected process-error-path test, not a claim of a real elapsed timeout experiment. |
| Submit an oversized re-entry view after a previous successful bind. | Load rejected the input, but the session remained usable with old bound state. | Load rejected the input and poisoned the session, preventing old bound access. |

The fix is more than adding a caller-editable checksum. `kernel.py:172–180` records canonical binding bytes in the trusted engine instance, associating ticket, manifest, session, generation, source, request, contract, and response bytes. `trusted_binding()` returns a newly parsed copy, so editing that returned object cannot rewrite stored authority. `monty.py:23–60` checks incoming rows against that separately loaded authority before publishing `bound`.

`monty.py:92–118` and `134–145` stop the session on process/load/bind abnormal exits. In addition to the four original witnesses, I independently tested injected `KeyboardInterrupt` during re-entry and a ticket issued by a different engine. Both rejected access and left old bound answers unavailable. All six targeted probes used the real local evaluator around the tested boundary; the process-error and interruption events themselves were deliberately injected.

These are consistency protections against mutable handoff views within a trusted-host design. They are not cryptographic provider authentication, protection against a host modifying private Python internals, or proof of immutable remote model weights.

## 3. Protocol-to-observation assessment

| Protocol mechanism | Concrete observation | Interpretation |
|---|---|---|
| **M1: supplied factorization with competent baseline** | 72 occurrences, 16 unique exact source requests, 2,556 `i < j` pairs, and 336 positive pairs. Full ordered Monty output equals both literal pair gold and matched Python output. | Factorization works for the explicitly supplied predicate. The independent direct-pair reference reads literal pair truth rather than invoking the unary feature extractor. Matched Python also uses 16 semantic questions, so no RLM advantage over that baseline is established. |
| **M2: chosen-feature collision** | Two relation tasks have identical chosen unary vectors but different positive relations. The caller-supplied direct branch performs three pair questions per task, six total, and returns the distinct gold edges. | These unary features are insufficient. The report now says `sufficiency_of_these_chosen_unary_features: falsified`. Neither automatic collision discovery nor impossibility of every unary representation is shown. |
| **M3: residual-only escalation** | Residual occurrence IDs are exactly `0`, `8`, `16`, representing two new unique expert requests. Unknown pairs fall from nine to three; the output remains incomplete. Known partial pairs agree with direct gold. | Unknown recovery is explicit and selective. The second backend is another synthetic profile, not a real generative `llm` call. A budget that prevents stage two preserves the first stage's nine unknown pairs rather than replacing them with false. |
| **M4: exact reuse and invalidation** | Cache-off requests/questions: 72. Cache-on: 16 backend calls/questions, including a second identical view with no additional backend calls. Changed nested state, instructions, option order, contract version, and model identity each cause a new request. Mutating a returned value does not alter cached evidence. | Reuse is one recorded observation reused across occurrences, not independent corroboration. Acceptance-threshold changes recompute reductions without a semantic call. |
| **M5: typed boundary and budgets** | Choice, Noul, and Score survive actual Monty handoff as structured data. Three questions are counted separately from one backend invocation. Disabled and call/question/request-byte preflight failures enter no backend. Malformed answers fail before becoming cached observations. | The interface is not limited to the all-pairs application's yes/no result. Partial backend failure retains prior successful observations but produces no complete stage, and the engine refuses another request. |
| **M6: persistent state and bound re-entry** | Source and intermediates persist in the same real evaluator session. Reordered rows bind by ID. Wrong session/generation/source/manifest/request/contract, extra/duplicate/missing rows, altered bodies, and foreign-engine tickets reject. | Tested source/request/result association is enforced under the trusted-host assumptions. The final poisoning checks prevent rejected re-entry from silently falling back to old variables. |

### Deliberately negative semantic result

Flipping one high-confidence accepted unary feature for `r00` causes **96 wrong pair decisions**, although the output is structurally complete and has no unknown pairs. The test preserves this failure instead of repairing it with gold. This directly refutes the idea that typed values or exact joins repair semantic errors.

A schema-valid, complete stage can therefore still be semantically wrong. A successful residual policy for low-confidence answers does not detect wrong answers that are confidently accepted.

### Accounting actually measured

The final suite reports:

- Cache off: 72 backend calls/questions, 47,360 serialized request bytes, and 14,372 serialized response bytes.
- Cache on after two views: 16 backend calls/questions, 10,549 request bytes, 3,193 response bytes, and 128 cache hits. The hits combine 56 within the first 72-occurrence view and 72 in the second view.
- Full reference ledger: 34,739 serialized bytes. Hand-selected root summary: 29 bytes.

These are serialization and logical-work observations, not provider token usage, billing, measured Jev latency, or automatic-planner context savings. The pair universe remains quadratic. A compact manually selected summary is not a substitute for proving that a model can discover, validate, and use the underlying program correctly.

## 4. Final artifact identity

All following hashes were observed on the independently tested snapshot. They identify this separate provider-free engine experiment, not the earlier live transport implementation.

| Artifact | SHA-256 |
|---|---|
| `bench/jev/engine_lab/__init__.py` | `50962f22e7640082c9a133ac995ae274a3c19f3b8c421d87d40b9163d9263a51` |
| `bench/jev/engine_lab/kernel.py` | `5e8c1a312a0585cfa06cc14eb218dcb7247e04ccbd0b95d39f55a44026f99de4` |
| `bench/jev/engine_lab/monty.py` | `1e1e42b81136864b0c1a6f804d507cc6fb368c61e12e4141305cd0ee5ed74653` |
| `bench/jev/engine_lab/run.py` | `98291890380135a0067b3fe3e5bf546c3d4ff661767767f260355a5e77dab994` |
| `bench/jev/engine_lab/scenarios.py` | `a1c860b1a89366f28865f85157cf7531143495973d38c4e46364f3af74fa1ad0` |
| `bench/jev/engine_lab/tests.py` | `7d39a8b98dc859a161f3e26862fcdac0947a00e9b60c958f5c285b15708491f1` |
| `bench/jev/engine_lab/fixtures.json` | `81badd8e7d7914e10954989fce74a8685d53c88ef6dffadf29739703e5904489` |
| `bench/jev/adapter.py` | `26fd3b4564db43b3469cffa1f8efee00e6c1237f7bfede13dbec8f5df0b6565d` |
| `bench/jev/bridge.py` | `07843f9d7fad1a5d1cea0d504923c5d5f3e4ebb04b54169b5e934284cda6ca2d` |
| `target/debug/azdaja` | `74e74287c6824eeb2420d11191026e72956bee60e409bfbb5716ae85392bb84b` |
| `docs/research/jev-engine-mechanism-protocol-20260916.md` | `67a18386a5c70e9c08bc7be369ea19a090b23513ed8e45b3ae468f884ffac424` |

The following prior artifacts were preserved, not rewritten:

| Preserved artifact | SHA-256 |
|---|---|
| `docs/research/jev-independent-review-20260916.md` | `3dac3b93abae35346a87ca8dabd20dd0ed8b9aed7a56c0da1d282685b5e98ee2` |
| `docs/research/jev-replay-followup-review-20260916.md` | `2e64ad732d36555713dc936b13ba8e9f27b0e266fabafedc7cc4db452c54bea8` |
| `bench/jev/results/pilot-20260916.json` | `1041260d6de17ba26d0bbbbfc9cb4f3a35d2fc7a50ed45d1a96504d180c8ddaa` |
| `bench/jev/results/pilot-alias-20260916.json` | `f0b01dd126147b6332e56254610f4a720a77387553ccb24fba6d5477d4a126a4` |

## 5. What remains unproven

1. **Automatic planning:** the programs, factorization contract, residual policy, and fallback branch are handwritten. The engine does not establish how a model would discover safe decomposition on unseen task families or formats.
2. **Jev or competing-leaf quality:** oracle responses deliberately consult fixture gold. This tests mechanics, not the quality of any remote model. Arbitrary declared thresholds and confidence fields are not calibrated guarantees.
3. **End-to-end economic benefit:** plain Python with the same cache and decomposition matches semantic work and output. No Jev-versus-generative-leaf or adaptive-versus-static-plan cost/quality comparison was run.
4. **Production exposure:** no Rust/core `llm` behavior was changed, no native external `judge()` was added, and no production memory or retrieval integration was validated. Reranking remains one possible application, not the scope of the general typed interface.
5. **Broader threat model:** the host, registered callbacks, handwritten evaluator program, and private engine registry are trusted. Binding hashes preserve recorded bytes and associations, not semantic truth or provider provenance. Backend names/contracts are declarations, not immutable-weight attestations.
6. **General resource isolation:** tested limits cover declared call/question/request-byte and individual payload bounds. Injected callbacks are synchronous trusted code, not independently isolated arbitrary providers. Aggregate serialized re-entry can still hit the evaluator load limit after work has occurred; the verified behavior is fail-closed, not guaranteed completion for every legal combination of limits. The injected failure/interruption probes are not real engine-level timeout measurements.
7. **Task-wide evidence completeness and statistical reliability:** exact occurrence accounting applies to the supplied source and declared pair universe. It does not establish retrieval recall, evidence sufficiency outside that source, confidence calibration, or deployment error bounds.

**Final disposition:** the bounded mechanism prototype meets the specifically exercised protocol paths after correction of the initial handoff blockers. Preserve the negative controls and the equal Python baseline. The next gate is a separately authorized study that holds task quality and plans comparable while testing actual leaves and automatic planning. No live-study reopening or production promotion follows from this review.
