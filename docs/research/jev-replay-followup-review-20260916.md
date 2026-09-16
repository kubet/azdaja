# Independent follow-up review: Jev offline receipt replay

Date: 2026-09-16. Reviewer: independent reviewer `mouse`.
Final verification: 19:38–19:39 UTC. Scope: offline replay and custody, not a new provider experiment.

## Verdict

**The concrete replay blockers reproduced during this follow-up are closed in the final snapshot identified below.** The independent final run passed **87 tests, zero skipped**, including the real local Monty evaluator. Separately constructed impossible receipts now fail at the intended checks. This supports a bounded claim about the tested offline receipt-processing paths, not a claim that every possible receipt is handled correctly.

**The live pilot remains blocked, with zero validated live judgments and no baseline comparison.** Neither successful synthetic campaigns nor passing custody checks change that outcome. No further live calls were made by this reviewer, and none are authorized by this review.

This is a new document. `jev-independent-review-20260916.md`, its historical verdict, and the original receipts remain unchanged. The reviewer made no implementation changes or commits and owns only this new review file. Test-generated temporary receipts and evaluator scratch state were isolated and cleaned up.

## 1. Scope and independence

The follow-up initially targeted successful and mixed-acceptance paths missing from the five original `test_audit.py` tests. I inspected `audit.py`, the relevant runner/adapter/bridge paths, and all added `test_complete_audit.py` code before running it. Previously inspected test modules and the evaluator binary were checked by hash before reuse.

The review did not treat a green suite as sufficient. It constructed self-consistent synthetic campaigns that could not have been emitted by the real adapter, then asked whether replay would nevertheless label them consistent and release ordinary judgments. These are internal-consistency falsifiers, not attempts to authenticate a provider response.

The coordinator implemented the fixes. The final legacy-alias compatibility finding was discovered and fixed by the coordinator, then independently checked here. Production memory behavior, recall ranking, and the coordinator's use-case document were not reviewed in this follow-up.

## 2. Executed findings and final disposition

The original vulnerable audit snapshot was `e5d6047f28249bc7eae583ac4cc467e936ff666192372e5c1bbdbd1375549b14`. A subsequent snapshot, `3f58b79c0c2ba37a6d379b4ddfa4f568954ce132c6efca5e2e94a4b71f99df7d`, closed the first failures but still admitted the deadline and invalid-model witnesses. These are superseded versions, not hashes of the current implementation.

| Finding | Actual witness or check | Final result |
|---|---|---|
| Missing completed transport evidence | A correct 79-call exact-model campaign with every completed event's `metrics={}` was accepted. `metrics=[]` also passed. This bypassed the old truthiness-gated transport check. | Direct rechecks reject both with `receipt transport evidence missing`. The suite also tests null, false, zero, empty string, and omission. |
| Completed response beyond the token budget | First response reported 1,000,001 input tokens, followed by 78 correct responses. Coherent totals and transport metrics still yielded `semantic_screen_passed` and 66 eligible ordinary judgments. | Rejected with `completed receipt exceeds resource envelope`. Known cumulative input is recomputed rather than trusting the recorded counter. |
| Alias binding before resource eligibility | The same over-budget first response in explicit allowlisted alias mode was accepted and pinned. | Rejected before replay binds the model. The positive alias control still preserves the requested alias on the wire and pins the concrete returned identity. |
| Missing deadline eligibility | A completed first call with `latency_ms=1201000` passed. A second witness with 79 latencies of 20,000 ms, totaling 1,580 seconds, also passed. | Both reject with `completed receipt exceeds resource envelope`. An alias first-response deadline witness rejects too. |
| Invalid requested-model grammar | Replaced the requested and returned model with `not-a-jev-model`, recomputed policy/request/response identity metrics, and retained valid answers. Replay accepted all 79 calls although the constructor rejects this identifier. | Rejected with `invalid receipt requested model`. |
| Impossible response byte count | A preserved typed response with `response_bytes=1` was accepted. | Rejected with `receipt response accounting mismatch`. The new structural JSON lower bound does not pretend to reconstruct the original response bytes. |
| Legacy alias compatibility could expose unpinned judgments | Coordinator-reported witness removed the allowlist and pin from an alias campaign and made the returned model the alias. Recomputed policy identity, or omission of the new policy marker, previously allowed compatibility behavior to bypass pinning. | Independently regenerated both marker variants. Both reject with `unresolved alias cannot expose retained judgments`. The two historical failed receipts still replay successfully as negative evidence with no retained judgments. |

Current check locations are `audit.py:62–75` for requested-model/resolution policy, `90–93` for legacy alias restrictions, `110–144` for transport evidence and cumulative latency lower bounds, and `145–172` for response accounting, resource eligibility, and pin ordering. Projection at `217–221` only releases completed ordinary-call judgments.

The missing-metrics exception is deliberately narrow: genuine preflight failures or interruptions without retained responses do not need fabricated transport evidence. The synthetic `credential_in_request_state` control exercised the real runner/adapter preflight, made zero transport attempts, and remained auditable.

### Boundary behavior verified

- Exactly 1,000,000 reported input tokens remains eligible in the synthetic replay control.
- The latency check subtracts 0.0005 ms per rounded measurement and allows a small floating-point tolerance. A control whose rounded sum marginally exceeds 1,200,000 ms but whose conservative lower bound does not exceed it remains accepted.
- A final `elapsed_seconds=1201` does not alone cause rejection. Post-response bookkeeping can extend runtime, so final elapsed time is not equated with the last response's eligibility time.
- Structural size-bound examples cover strings, escapes, Unicode, collections, scalars, UTF-8/16/32, and both ASCII-escaped and direct-Unicode JSON output. This tests conservativeness, not exact wire reconstruction.

## 3. What the final tests actually exercised

The independent final command used a cleared environment, explicit local paths, `PYTHONDONTWRITEBYTECODE=1`, disabled Git lazy fetch and prompts, and disabled global/system Git configuration:

```sh
python3 -B -m unittest test_adapter test_run test_bridge \
  test_model_resolution test_audit test_complete_audit -v
```

`PYTHONPATH` was explicitly set to `bench/jev` for this invocation. Result at 19:38:58 UTC: **87 tests passed in 8.624 seconds, zero skipped**.

| Module | Tests |
|---|---:|
| `test_adapter` | 17 |
| `test_run` | 20 |
| `test_bridge` | 12 |
| `test_model_resolution` | 13 |
| `test_audit` | 5 |
| `test_complete_audit` | 20 |
| **Total** | **87** |

Earlier independent runs of 81 total tests and 24 scoped audit tests describe intermediate verification runs. The 87-test run above is the final full-suite result. The frozen original review's older counts are not rewritten.

The new complete-campaign controls execute the actual `run.main`, adapter validation, campaign policy, replay, and real local evaluator. Only the credential reader and HTTP transport are replaced. The apparent `--live` argument in these tests exercises the CLI branch under an explicitly injected synthetic transport, not a live request. Socket/HTTPS guards and a subprocess allowlist prevent the adapter worker from being launched. The evaluator uses an isolated home/configuration and `/usr/bin/false` as its provider command.

The previously inspected adapter tests also exercise actual local sleeping processes to check kill/reap behavior. They do not obtain timeout coverage merely by having a parent mock raise an exception.

### Observable custody and stopping outcomes

- **Complete control:** 79 synthetic requests, 66 unique ordinary judgments, and 68 preserved occurrences including two duplicate controls. Raw and accepted counts are supported 23, contradicted 22, insufficient 23. Baseline remains `not_run`, and `semantic_efficacy_established` remains false.
- **Mixed acceptance:** complete coverage still means all supplied packs have judgments, not that every judgment is accepted. The real evaluator retained all 68 occurrences while accepting exactly 34 and leaving 34 unaccepted, without changing their labels.
- **Semantic stop:** a deliberately wrong accepted label on `c01` stopped after seven requests. Audit-only projection retained that wrong label and its accepted flag instead of using fixture gold to repair it. Strict projection rejected incomplete custody. Sixty occurrences remained unjudged.
- **Token crossing:** two responses reporting 600,000 input tokens each stopped with reported total 1,200,000. The crossing response and usage remained in the receipt but were excluded from eligible projection. Only `s01` was projected, producing two supported occurrences because of its duplicate, plus 66 unjudged occurrences.
- **Historical failures:** both original receipts replay as stopped with zero validated judgments. Strict incomplete projection fails. The failed alias receipt's audit-only real evaluator output retains all 68 occurrences as unjudged rather than calling the ledger complete.

In addition to the suite, I independently regenerated ten targeted checks: nine impossible receipts were rejected with the expected codes and the rounding/postprocessing control was accepted. I then independently regenerated the two unpinned-alias marker variants and replayed both original negative receipts.

## 4. Version and evidence identity

These are current offline follow-up hashes, not the implementation identity of the original live attempts.

| Current artifact | SHA-256 |
|---|---|
| `bench/jev/audit.py` | `6b48c57125aa1135cc6510a14b615afbbf05bde997c3d4ee7b608858752211c0` |
| `bench/jev/test_complete_audit.py` | `02ea00ae651ea4bb55f9235b94f869f7379351b833c7cac24003763cd41ced03` |
| `bench/jev/adapter.py` | `26fd3b4564db43b3469cffa1f8efee00e6c1237f7bfede13dbec8f5df0b6565d` |
| `bench/jev/run.py` | `7dd60ca25a5f96f80c0297522766bfa9464885d7251c385c273af61ab90e83ab` |
| `bench/jev/bridge.py` | `07843f9d7fad1a5d1cea0d504923c5d5f3e4ebb04b54169b5e934284cda6ca2d` |
| Tested `target/debug/azdaja` | `74e74287c6824eeb2420d11191026e72956bee60e409bfbb5716ae85392bb84b` |

Previously inspected, unchanged test identities:

```text
d9bd4c1e0815b0198c72d7394eb7117202229ba190e3810acba10216685972fd  test_adapter.py
5511158e601a892a46a5baded2fabdd671dacf9bd630312164d190aa10f937b6  test_run.py
46f5ef85967ee54c7354b3502c66857c63cfc1950e77ef91f8082a18b0a9b390  test_bridge.py
d30a86e554d132a1f05654433fb6d0d18c3bc8960200820126a99041a206dddf  test_model_resolution.py
117622b95c086234cc58ed2b2a44ca29660763e21838dfa28f6ba5171057f840  test_audit.py
```

Preserved original evidence:

| Frozen artifact | SHA-256 |
|---|---|
| `docs/research/jev-independent-review-20260916.md` | `3dac3b93abae35346a87ca8dabd20dd0ed8b9aed7a56c0da1d282685b5e98ee2` |
| `docs/research/jev-experiment-protocol-20260916.md` | `70a784fe2206278e6fd539630e47ef354d97c4c073590614a8800d8a2ff9e5d3` |
| `bench/jev/fixtures.json` | `3fe530372fefe2dd62e823bad9eeec8aad10a1783328a502805851ebd733929f` |
| `bench/jev/FIXTURES.md` | `4f34c085a6209e6aa047234e04bb290ef7fe832e5eae9918731235a683afa128` |
| `bench/jev/results/pilot-20260916.json` | `1041260d6de17ba26d0bbbbfc9cb4f3a35d2fc7a50ed45d1a96504d180c8ddaa` |
| `bench/jev/results/pilot-alias-20260916.json` | `f0b01dd126147b6332e56254610f4a720a77387553ccb24fba6d5477d4a126a4` |

The live v1 implementation identities remain `f694a771d85ddf9ac572e72821bdaca06f02b6e32f2a236c2abb261704cc452a` for the adapter and `a4b068552e415a492e35ed599bd7b2f60ddd0114689bac8f0c14e2f49ea9f7ae` for the runner. The current offline changes must not be retroactively attributed to those attempts.

## 5. Remaining proof limits

1. **No semantic efficacy result.** Synthetic responses deliberately use fixture gold. This is appropriate for testing plumbing and stopping, but the resulting accuracy is an oracle control, not evidence about Jev. Local typed accuracy would not, by itself, establish end-to-end exact aggregation reliability anyway.
2. **No provider authentication or exact wire reconstruction.** Replay checks recorded identities and relationships. The original response body is not retained for arbitrary byte-for-byte reconstruction, so the recorded response SHA cannot authenticate or independently reconstruct the body. A conservative size lower bound only rejects impossible sizes.
3. **Timing evidence is a lower bound.** Summed per-call measured latency omits between-call work. Passing the bound does not independently prove total campaign deadline compliance. Rejecting final elapsed time merely because post-response work exceeded the deadline would also be unsound.
4. **Unknown usage remains unknown.** Summing known usage is not proof of complete billing. Failed attempts and missing usage can be unaccounted. There is no measured baseline cost or latency superiority claim.
5. **Historical hashes are not historical execution.** Retained Git objects are checked against recorded implementation hashes, but replay runs the current verifier/runner. This is not a universal executable reconstruction of every historical version.
6. **Source custody is bounded to supplied packs.** Preserving all claim/evidence strings and duplicate occurrences does not prove task-wide evidence completeness, model attention to every token, or completeness of upstream retrieval. The follow-up does not establish production memory recall quality or authorize pruning.
7. **No new live compatibility evidence.** Model grammar and allowlisted identity consistency do not prove that an account can access a model, that the provider implements the assumed contract, or that a concrete alias resolution will succeed live. The original HTTP 400 and strict model-mismatch receipts remain negative results, not semantic errors or successes.
8. **No broad statistical promotion.** Small, clustered, synthetic, outcome-stopped fixtures do not justify deployment reliability bounds. Class confidence is not an independent correctness measurement. Exact occurrence counting in the evaluator does not eliminate semantic labeling uncertainty.

**Final disposition:** no remaining blocker found for the specifically reviewed offline replay and custody invariants. The experiment's substantive utility and comparative performance remain unproven. Preserve the frozen evidence, do not make more live calls under this study, and do not convert synthetic success into a production or efficacy claim.
