# Independent JEV experiment review

Date: 2026-09-16. Reviewer: independent falsification reviewer (`mouse`). Final verification window: 18:38–18:43 UTC. This review concerns the exact snapshots listed below, not subsequent edits or live results.

## Outcome update after local receipt inspection, 18:49 UTC

**The actual bounded pilot is blocked: two recorded inference attempts, zero validated judgments, and no baseline.** The offline verdict below is historical and limited to the tested local contracts. It did not establish provider compatibility. Both stopped runs remain immutable evidence. The amendment prohibits more setup/retry cycles, so this review recommends no further live calls for this campaign. See the addendum for the evidence limits and an offline-only future alias-policy design.

## Offline verdict before inspection of live receipts

Latest follow-up at 19:06 UTC: the two later future-policy findings were fixed and independently rechecked. All 67 inspected offline tests passed. Both stopped receipts replay to 68 unjudged occurrences, never a complete semantic result. The final section records this newer offline-only verdict and its separate hashes. The live outcome above is unchanged.

**No remaining critical blocker was found for the narrowly bounded, synthetic pilot in the reviewed snapshots. This is not approval for production, automatic pruning, semantic reliability claims, or a claimed cost/speed advantage.**

The initial artifacts were not acceptable. Independent review found an executable S4 fail-open counterexample, false-positive safety tests, contradictory gold, and a nonworking custody bridge. The coordinator revised those artifacts. The final verdict follows reinspection, review of every one of the 66 gold cases, and independently executed offline acceptance checks, not a green-test total alone.

The reviewer made no network/API calls, accessed no real credentials, spawned no agents, edited no implementation files, and made no commits. This document is the only repository file written by the reviewer. Test-created synthetic files and local evaluator sessions were temporary. No reviewer-run test invoked the real TypeSafe worker or a live model.

## Exact reviewed artifacts

SHA-256 identities captured after final offline verification:

| Artifact | SHA-256 |
|---|---|
| `docs/research/jev-experiment-protocol-20260916.md` | `70a784fe2206278e6fd539630e47ef354d97c4c073590614a8800d8a2ff9e5d3` |
| `bench/jev/run.py` | `a4b068552e415a492e35ed599bd7b2f60ddd0114689bac8f0c14e2f49ea9f7ae` |
| `bench/jev/test_run.py` | `5511158e601a892a46a5baded2fabdd671dacf9bd630312164d190aa10f937b6` |
| `bench/jev/adapter.py` | `f694a771d85ddf9ac572e72821bdaca06f02b6e32f2a236c2abb261704cc452a` |
| `bench/jev/test_adapter.py` | `d9bd4c1e0815b0198c72d7394eb7117202229ba190e3810acba10216685972fd` |
| `bench/jev/fixtures.json` | `3fe530372fefe2dd62e823bad9eeec8aad10a1783328a502805851ebd733929f` |
| `bench/jev/FIXTURES.md` | `4f34c085a6209e6aa047234e04bb290ef7fe832e5eae9918731235a683afa128` |
| `bench/jev/bridge.py` | `07843f9d7fad1a5d1cea0d504923c5d5f3e4ebb04b54169b5e934284cda6ca2d` |
| `bench/jev/test_bridge.py` | `46f5ef85967ee54c7354b3502c66857c63cfc1950e77ef91f8082a18b0a9b390` |
| Tested `target/debug/azdaja` binary | `74e74287c6824eeb2420d11191026e72956bee60e409bfbb5716ae85392bb84b` |

Line references below refer to these snapshots. The native evaluator binary was exercised, but this review is not a full audit of the Rust runtime or its build provenance.

## What was actually executed

1. **Initial S4 falsification, without importing transport code.** Executed AST-selected runner functions with an explicitly synthetic client. One wrong, abstained challenge label became the same wrong, automatically accepted label under each S4 variant. Runner snapshot `1585fdbe8d7dff937c9d8712acb9bb30e683de3c95726696b7c26e00726a8915` returned `pilot_gates_passed` after 79 requests with **three wrong auto-accepted variant judgments**. This was a demonstrated defect, not a hypothetical concern.
2. **Initial cancellation-path falsification.** Executed only the extracted `_fetch` function with a fake process that raised `KeyboardInterrupt`. The old path did not kill the process. No real process or network was used for this witness.
3. **Revised adapter and runner:** 34 inspected tests passed independently. These included genuine local sleeping-child timeout and interrupted-communication tests, not a manually raised timeout or an inherited parent-only HTTP mock.
4. **First bridge acceptance attempt:** three validation tests passed, but the real evaluator test failed. Actual Monty output identified `next(generator, None)` as `TypeError: 'list' object is not an iterator`. Static inspection separately found hardcoded zero label counts and discarded known judgments in partial mode. These failures were reported before further revision.
5. **Final complete offline suite:** **49 tests passed, zero skipped**, consisting of 17 adapter, 20 runner, and 12 bridge tests. An earlier final-snapshot run passed 46 tests. A subsequent hash check detected three added runner regression tests and paired reporting, which were inspected before the full 49-test rerun. The bridge tests used the actual local evaluator binary. Process environments excluded real credentials and the bridge explicitly configured `/usr/bin/false` as its provider.
6. **Additional independent checks:** loaded the actual final fixture file through its schema validator and checked all 66 ordinary request packs for exact claim/evidence equality, positional question IDs, and the permitted question fields. Also exercised a real adapter instance with a synthetic injected transport through `run_campaign`: a 150-token reported budget crossed on the second 100-token response, stopped immediately, and retained that response plus cumulative usage of 200 tokens.

The final suite was run equivalently to the following, after inspecting all discovered test files for network paths:

```python
# Run with python3 -B and PYTHONDONTWRITEBYTECODE=1.
import os, unittest
from pathlib import Path
scratch = os.environ.get("JCODE_SCRATCH_DIR", str(Path.home() / ".jcode/scratch"))
os.environ.clear()
os.environ.update({
    "PATH": os.defpath,
    "JCODE_SCRATCH_DIR": scratch,
    "AZDAJA_BINARY": str(Path("target/debug/azdaja").resolve()),
    "PYTHONDONTWRITEBYTECODE": "1",
})
suite = unittest.defaultTestLoader.discover("bench/jev", pattern="test_*.py")
result = unittest.TextTestRunner(verbosity=2).run(suite)
assert result.wasSuccessful()
```

The adapter suite prohibits unmocked child creation and socket connection attempts. Its only actual Python subprocesses execute a fixed local sleep program. Worker HTTP handling is tested directly in-process with a mocked connection and synthetic byte streams. These checks do not contact the provider.

## Resolved critical findings and verification

| Finding | Final implementation and evidence | Assessment |
|---|---|---|
| S4 checked label stability but allowed a wrong abstention to become a wrong acceptance | `run.py:273–297` now compares labels and acceptance and rejects any wrong accepted variant. `test_run.py:197–214` exercises both the original counterexample and correct-label acceptance drift. | Resolved for tested paths. |
| Mocked timeout did not actually test process timeout/reaping; parent-only HTTP mock could disappear in a child | `test_adapter.py:43–58,196–294` denies unintended transport, tests the worker directly, and checks real sleeping children are gone after timeout/interruption. | Resolved. No unsafe draft suite was run. |
| Short fake key `k` appeared in `input_tokens`, masking malformed-response tests with a credential error | Final tests use a distinctive synthetic key and assert exact validator codes (`test_adapter.py:17,53–58,89–121`). | Resolved. |
| Non-timeout interruption could leave the worker running | `adapter.py:217–223,260–267` kills/reaps on abnormal communication exit. Actual local children are tested for `KeyboardInterrupt`, `SystemExit`, and `OSError`. | Resolved for those local lifecycle paths. Remote provider cancellation is not established. |
| Cumulative reported-token crossing lost usage and the validated response | `adapter.py:313–329` preserves both; `run.py:298–306,400–403` retains and accounts for preserved responses. Tested at both adapter level and adapter-to-runner boundary. | Resolved for retention and aggregate usage. See the summary-denominator caveat below. |
| Campaign remaining time did not constrain the next request | `adapter.py:294–307,320–321` caps the timeout by remaining time and rejects post-response overrun. The remaining-time test verifies the propagated bound. | Resolved for reviewed paths. |
| Fresh workers could execute changed on-disk code while receipts recorded an earlier hash | `adapter.py:26–29,257–259,304–306` captures worker source once, executes that captured source with isolated Python, and records its hash. | Resolved for ordinary mid-campaign working-tree edits. |
| Bridge could not run in the actual evaluator and hardcoded zero counts | `bridge.py:26–70` uses supported native bindings and explicit loops. Actual tests assert three supported occurrences, mixed-label counts, and distinct raw/accepted totals. | Resolved in the tested binary. |
| Custody checks occurred only on the host; partial audit dropped known occurrences | Native evaluator recomputes source/payload hashes, checks order and duplicate relationships, and emits every known/unjudged occurrence (`bridge.py:28–69`). Negative tests assert evaluator-specific failures, not merely any exception. Partial mode retains two known supported occurrences and one unjudged occurrence. | Resolved for tested cases. |
| Gold inversion and repeated scope/open-world mistakes | Every final case was reread after correction. See the gold audit below. | Prior concrete blockers resolved. |

## Final gold and leakage audit

All cases **s01–s06, c01–c30, and h01–h30**, including their rationales, were individually reviewed. The final labels are defensible under the intended ordinary reading of the supplied evidence. This is a reviewer judgment, not a measured inter-annotator agreement statistic or proof that natural-language gold is infallible.

Important repaired cases include:

- `s01/s02/c14/c24`: explicit release, memory, migration, and incident-owner identity. The erroneous successful-migration/contradicted pairing was corrected by changing the claim to failed completion.
- `c17/c18`: an explicit iff rule and an exhaustive negative signature index distinguish supported from contradicted without treating a missing match in an open index as negation.
- `c21`: a claim about build reproducibility, not the ambiguous claim that compiler success proves it.
- `c29/c30`: a complete referenced test report specifies the only tested revision.
- `h01–h03`: signing-key identity and effective revocation time.
- `h10`: the analysis explicitly rules out the cache miss as a contributor, rather than merely naming another possible cause.
- `h13–h15`: a global release-artifact claim, not a claim restricted to already listed rows. An omitted artifact remains genuinely unknown.
- `h16–h18`: the behavior of a specific parser version on a specific fixture, not a universal property allegedly proved by one test or an execution event disproved by skipping the test.
- `h19/h23`: explicit collection timing and actual execution evidence, rather than substituting export timing or a normative approval requirement for the claimed event.
- `h25–h27`: exact source revision identity, not ambiguous ancestry or inclusion.
- `h28–h30`: remaining expired records, with explicit exhaustive scope in the empty-set case.

No direct gold metadata is added to model state or question identifiers in `run.py:101–120`. The final 66 ordinary packs contain precisely their supplied claim and evidence. S4 padding copies the evidence and appends the frozen irrelevant sentence rather than deleting original content.

**Residual shortcut risk is substantial.** The holdout contains ten closely related triples. Challenge also contains paired cases. Words such as “complete,” “only,” “explicitly,” and “not supplied” often reveal the intended evidentiary operation. The task can therefore reward template recognition without demonstrating robust reasoning on messy real sources. Splitting by surface wording and withholding outcomes does not make cases statistically independent. This panel is suitable for cheap falsification or deciding whether a larger study is worthwhile, not for estimating production precision.

## What custody establishes, and what it does not

The real bridge verifies local source-string hashes, payload-string hashes, occurrence order, exact duplicate consistency, manifest coverage, and raw/accepted label counts. Unicode and duplicate multiplicity are exercised. Strict mode fails on missing judgments; audit mode exposes them as unjudged without erasing known rows. The tested negative cases fail inside the evaluator, which matters because host-only validation would not test the claimed runtime boundary.

These checks **do not establish**:

- that a source pack contains every fact needed for a broader task;
- that a remote model read or attended to every supplied byte;
- that a label is semantically correct;
- that a source-bound manifest is an authenticated provider receipt;
- that a live adapter receipt has already been mapped into and replayed through this bridge;
- that the complete production runtime is regression-free.

The bridge accepts a supplied label/acceptance manifest. Its synthetic oracle tests establish custody and arithmetic, not efficacy. The runner correctly reports `semantic_screen_passed`, with custody and baseline explicitly outside that result (`run.py:248,296–297`). No automatic evidence pruning is implemented in these reviewed paths.

Exact expansion can amplify semantic error. If a unique judgment is wrong and occurs 1,000 times, correct duplicate expansion repeats that error 1,000 times. Conversely, different wrong labels can cancel in an aggregate count. Therefore neither local accuracy nor an exact count match alone proves end-to-end semantic reliability.

## Statistical and performance limits

- The binomial bound implementation matches the reference calculations: zero errors in 30 observations gives approximately 9.503% one-sided 95% upper risk, and 299 independent zero-error observations are needed to put that reference bound below 1%.
- Those assumptions are not met by this hand-authored, clustered, adaptively stopped panel. `run.py:189–190` explicitly marks the bound invalid for the sampling design. The corrected `FIXTURES.md:17` rejects individual-case bootstrap inference.
- Paired contrast reporting in `run.py:208–223,260–261` now separates prediction flips, both-correct outcomes, individual errors, and unobserved pairs. The new regression deliberately flips both predictions incorrectly, proving that a flip is not automatically counted as correctness. Pairs are not labeled as additional independent observations.
- Choice confidence is another statistic of the same prediction distribution, not an independent witness that can be multiplied with the selected-option probability. Thresholding both does not establish calibrated acceptance risk on this task.
- Even a valid per-judgment error bound would not directly imply a reliable large exact aggregation. A union bound requires applicable risks for all contributing unique judgments. Dependence, distribution shift, and multiplicity remain important.
- Fixed S4 ordering, shared templates, cache effects, and changing service conditions can confound latency comparisons. A reduced HTTP count alone is not reduced billed inference work.
- No reviewer-run live inference, billing measurement, matched generative baseline, fallback/escalation workflow, or production dataset evaluation occurred. H1/H2 semantic efficacy, H3 work savings, and H4 comparative advantage remain unproven here.
- Local resource ceilings and process termination are not a guaranteed dollar cap or proof that a provider stops remote computation after a connection closes.

## Remaining nonblocking reporting work

1. **Budget-crossing denominator:** `run.py:258–259,298–306` preserves a fully validated crossing response but does not add its judgment to the stage summary. The independent integration check retained two validated responses while reporting one stage observation. The run correctly stops and cannot pass, so this is not the earlier promotion loophole. Nevertheless, any later quality report must explicitly disclose the excluded crossing observation or include it in a separately labeled all-validated-response summary. Do not present the completed-prefix accuracy as if it covered every observed model response.
2. **Live adapter-to-bridge linkage:** the isolated custody workflow is verified. A genuine source-bound live receipt replay, including any abstentions, remains a separate integration step. An offline oracle manifest cannot stand in for that evidence.
3. **Freeze and preserve outcomes:** use the reviewed fixture/policy/implementation identities or explicitly name a new snapshot. Preserve failed and interrupted receipts. Do not revise gold, prompts, or thresholds in response to prospective outcomes and still call the same panel a holdout.

## Offline recommendation before inspection of live receipts

The corrected offline harness and custody probe provide enough evidence to remove the specific pre-inference blockers found in this review. If the coordinator proceeds with an authorized bounded synthetic pilot, retain the frozen stop rules and report failures as results. No production promotion, automatic pruning, reliability guarantee, or speed/cost superiority claim is supported by this independent review.

## Addendum: blocked live outcome and future alias contract

Added 2026-09-16, approximately 18:49 UTC. This addendum is based only on local, scrubbed receipts, the named amendment, and the frozen validator. The reviewer made no discovery request, inference request, or other network call. It does not reclassify either failed attempt as successful or alter the original reviewed transport and receipt hashes.

### Observed outcome, not inferred efficacy

| Local evidence | What it establishes |
|---|---|
| `bench/jev/results/pilot-20260916.json` | Requested `jev-1.12`. Exactly one recorded inference attempt stopped with `http_400`. Smoke has zero validated observations. Baseline was not run. The rejected body was not preserved. |
| `bench/jev/results/model-discovery-20260916.json` | Records one non-inference `GET /v1/models`, HTTP 200, advertising `jev-latest` and `jev-preview`. This is not a semantic observation or proof of the cause of the previous 400. |
| `bench/jev/results/pilot-alias-20260916.json` | The explicitly amended run requested `jev-latest` and stopped on its first attempt with `response_model_mismatch`. It records a 218-byte response and its SHA-256, but no preserved response object or validated judgment. |
| `docs/research/jev-model-availability-amendment-20260916.md:24–28` | Bounds the new run, preserves the first failure, retains strict identity equality, and says any further setup/transport/schema failure ends the run without another discovery-and-retry cycle. |

Both receipts report `usage_complete: false`. Numeric zero sums and zero input-cost estimates mean **no retained validated usage**, not zero billing or free inference. With no validated judgments, accuracy, accepted-error risk, and coverage are undefined, not 0% or 100%. The correct outcome is **setup/response-contract blocked**, not a semantic accuracy failure. No matched baseline or end-to-end performance claim is available.

The frozen validator checks `response["model"] != requested_model` at `adapter.py:137–138`, before checking answers and usage. Therefore the mismatch establishes only that the returned value was not exactly the requested identifier after envelope parsing. The local receipt does **not** preserve the returned identity, prove it was a concrete version string, or establish that the remaining answer/usage contract was valid. An alias resolving to a concrete model is a plausible compatibility explanation, not a fact reconstructible from 218 bytes and a hash. Likewise, the unavailable requested pin is consistent with the first 400 but is not its proven cause.

The offline review did not catch this alias-compatibility assumption before these attempts. Fail-closed stopping worked, but green offline tests were not evidence of a working vendor integration. Do not recover discarded judgments by inventing a response body, silently relax the old run's contract, or issue another call merely to fill this evidentiary gap.

Additional evidence SHA-256 values at inspection:

| Artifact | SHA-256 |
|---|---|
| `docs/research/jev-model-availability-amendment-20260916.md` | `7116f97ccf90513ec779209640a22c0a4fba8baa4fe4394cd439afac1851b64c` |
| `bench/jev/results/pilot-20260916.json` | `1041260d6de17ba26d0bbbbfc9cb4f3a35d2fc7a50ed45d1a96504d180c8ddaa` |
| `bench/jev/results/pilot-alias-20260916.json` | `f0b01dd126147b6332e56254610f4a720a77387553ccb24fba6d5477d4a126a4` |
| `bench/jev/results/model-discovery-20260916.json` | `835f40489a9c2ef170978bfecfef750f840ce197b677e3e680d6284d99a1d929` |

### Safest future design: explicit resolution with a campaign-scoped consistency pin

Version boundary checked at approximately 18:51 UTC: both failed receipts and the amendment retained the hashes above. The working-tree `adapter.py` and `run.py` had meanwhile changed during the coordinator's future-policy work. The recorded 49-test verdict and original source hashes remain historical. This follow-up has not independently audited or tested that newer implementation. Preserve the exact v1 sources at retrievable recorded revisions, and do not apply the v1 verdict to a v2 working tree.

This is a proposed contract for a **new, separately versioned implementation and experiment**, not a tested implementation or permission to resume the stopped pilot.

1. **Disabled by default.** Ordinary mode requires a declared concrete requested identity and exact returned-identity equality. Reject known moving aliases before transport unless the caller explicitly opts into a separately named alias policy. A key, catalog response, model mismatch, or failed run must never turn that policy on automatically.
2. **Freeze the resolution policy before inference.** Record the exact requested alias, fixed endpoint, allowed returned-identity rules, policy version/hash, budgets, and continuation rule. Prefer an authorized concrete allowlist or documented provider mapping. If only a format/family restriction is available, identify the choice as trust-on-first-use (TOFU), not verified alias-to-version authorization. A regex cannot prove that an identifier denotes immutable weights or excludes every disallowed deployment. Reject unknown, malformed, or unpinnable identities rather than guessing.
3. **Separate requested alias from resolved identity.** Continue sending the frozen requested alias unless a different request strategy was explicitly preregistered. A returned concrete ID may not be requestable itself. Do not silently replace the request model with that ID, switch to `jev-preview`, change providers, or add discovery/fallback traffic.
4. **Validate before binding.** Parse strict bounded JSON, reject credential-bearing data, validate the envelope and a bounded typed identity, then validate every answer and usage field. Apply response/resource/deadline checks. Only a fully contract-valid, policy-eligible first result can atomically bind the campaign identity and be exposed as a judgment. A malformed, incomplete, oversized, over-budget, timed-out, or rejected response must not initialize the pin. Retain only permitted sanitized diagnostics for failures.
5. **Never select the identity using semantic outcomes.** A valid first response binds even if its label is wrong or its confidence causes abstention. The runner then applies the unchanged semantic stop rules. Waiting for a correct or high-confidence answer before pinning would be outcome-conditioned model selection. Use a field such as `binding_call_index`, not an ambiguous `first_autoaccepted_call`.
6. **Make drift terminal.** Once bound to A, every later response must have A under the same complete validation contract. B, an absent/nonstring ID, or an unresolved moving alias fails closed. Poison the campaign, preserve the failed attempt, and make no additional request. Never silently re-pin, reset the client, retry, or pool A/B results as one model. A moving alias echoed unchanged by the server is not a concrete consistency pin and should be reported as unpinnable under this policy.
7. **Keep the pin campaign-scoped and durable.** One client per request must not create independent fresh bindings. Keep requests sequential. Persist the binding identity, policy digest, binding call, and complete result in the checkpoint before permitting another request. Checkpoint failure prevents continuation. Any future resume path must restore and verify the same pin and policy, or refuse to resume. Starting a new process must not silently erase drift history.
8. **Distinguish identity consistency from immutability and authenticity.** A server-reported version string that stays constant proves only observed string consistency. Without a documented immutable deployment/revision guarantee, weight changes, routing changes, or other backend changes under the same identifier remain unresolved. State this in receipts and every reproducibility claim. A model catalog advertising only aliases does not supply the missing guarantee.
9. **Preserve useful diagnostics without leaking content.** Record the trusted requested alias, policy ID/hash, bounded validated returned ID when safe, binding state, per-call request/response hashes, stop code, and independently validated usage. Validate and redact decoded strings as well as raw bytes so JSON escaping cannot bypass credential checks. Do not interpolate an arbitrary returned model value or provider body into an exception or receipt. Identity-rejected judgments must never enter accepted outputs or semantic totals merely because their usage was recoverable.

A minimal state machine is `disabled/exact` or, after explicit opt-in, `unbound -> bound(A) -> stopped`. Any failure from unbound or bound is terminal for that campaign. There is no `bound(A) -> bound(B)` transition and no `stopped -> retry` transition. Binding is an identity-policy event, not an accuracy or confidence event.

### Required offline falsifiers for that future policy

These are proposed acceptance tests, **not tests claimed to have passed in the reviewed v1 implementation**:

- Default mode rejects alias requests before transport. Concrete exact-match behavior remains unchanged.
- Opt-in alias plus allowed concrete A and a fully valid response binds A. Subsequent A succeeds while the wire request remains the original alias.
- A first response with a plausible A but malformed probabilities, wrong question coverage, invalid usage, duplicate keys, wrong primitive, credential content, or exhausted resources fails without binding or returning judgments.
- A valid first response with wrong gold still binds A and then triggers the runner's semantic stop. A valid abstention also binds. No identity search occurs.
- A-to-B drift stops before any B judgment reaches reduction and permanently prevents another call. Constructing a new per-request client or restoring an incomplete checkpoint cannot bypass that rule.
- Returned `jev-latest`, `jev-preview`, missing/nonstring identity, or an unsupported purported version is rejected as invalid/unpinnable under the explicit policy. Whitespace/case normalization must not merge distinct identifiers unless the provider contract explicitly defines that normalization.
- A decoded model field containing a literal or JSON-escaped synthetic credential is not exposed in diagnostics. Errors remain fixed codes.
- First-response checkpoint failure, interrupt during binding, timeout, and concurrent-binding attempts cannot leave a continuing campaign with an undocumented or conflicting pin.
- Both prior v1 receipts retain their original hashes and stopped/zero-validated status. Offline v2 test success never mutates or upgrades them.

**Addendum conclusion:** stop the current pilot exactly as amended. An explicit, conservative TOFU consistency policy is a reasonable offline research direction, but it needs a new contract version and the above negative tests. It is not a retrospective explanation of the discarded body, a guarantee of immutable model identity, or authorization for another live attempt.

### Separate future-implementation audit, first candidate at 18:52–18:54 UTC

The coordinator subsequently requested an audit of the implemented future-only policy. This supersedes the earlier statement that that candidate had not yet been audited, without changing the historical v1 verdict or hashes.

Candidate identities:

- `adapter.py`: `b4da89c08bd7ce4f2057395476d4de56a51039b8735d5ab0d724adff522458cd`.
- `run.py`: `dc5f43e0714759ac0a37548e4f0ffa8b9098933293cfdc330109e7d5cb718bc6`.
- New `test_model_resolution.py`: `65e6cde87041525f7487ba3acc06f3bfbb1e4c656c11ffdbfb19a2199d3653b3`.

After reading those files, the reviewer independently ran only the four inspected test modules: adapter, runner, bridge, and model resolution. **59 tests passed**, including ten new network-guarded resolution tests. No live calls occurred. New receipt-projection files being developed separately were not part of this requested alias audit.

For a single sequential client, the opt-in path implements a bounded predeclared concrete allowlist, keeps the requested alias on the wire, binds only after complete typed validation and post-response resource checks, rejects a later identity change even within the allowlist, and poisons after failure. Tests also showed that wrong-gold valid output binds before semantic stopping, a crossing response does not bind, and checkpoint failure prevents the next request. CLI opt-in and the policy hash are explicit. There is no resume path to assess.

Two additional reviewer-written, injected-transport witnesses identified residual differences from the safest proposed contract:

1. **Default alias echo is still accepted without a pin.** In this candidate, `adapter.py:234–245,331–338` accepts a client requesting `jev-latest` with no resolution allowlist. A fully typed response also naming `jev-latest` passes, after one transport invocation, while `resolved_model` remains `None`. This does not defeat the opt-in pin comparison. It means only resolution is opt-in, not alias use itself. Either reject known aliases before transport unless the explicit policy is configured, or label this legacy behavior as unpinned exact-string matching and never as concrete identity assurance.
2. **JSON escaping defeats the credential-in-state guard for some accepted key strings.** `adapter.py:231–232` accepts printable ASCII quote/backslash characters, but `adapter.py:304–306` searches unescaped key bytes in escaped JSON. A synthetic accepted key containing a quote and a backslash, used as the state, reached the injected transport and exactly equaled the decoded outgoing state. The same canonical-reserialization approach at `adapter.py:326` is not a general decoded-string scan for such keys. This is an existing guard limitation, not an alias-specific regression or a claim that the provider actually issues keys with those characters. Either reject unsupported credential syntax before use, or scan decoded JSON string values and object keys directly. No real credential was used or disclosed by this witness.

Both findings were sent immediately to the coordinator. The first candidate's green test count is not clearance for blanket default-alias or credential-redaction claims. This future-only work does not authorize another live call and does not change the stopped pilot outcome.

## Final offline follow-up, 19:03–19:06 UTC

**Both first-candidate witnesses are now resolved and independently rechecked. All 67 inspected offline tests passed, with zero skips. Both immutable stopped receipts replayed through the real evaluator to 68 unjudged occurrences and `complete: false`. No remaining blocker was found for these narrow offline claims. The live pilot remains blocked, with zero validated judgments and no baseline.**

This is a separate verdict on the final future-only implementation and the newly assigned receipt-audit boundary. It does not replace the original v1 source/receipt hashes, transform the two failed attempts into semantic evidence, validate an actual future alias mapping, or permit another live call.

### Current offline-only snapshot

| Artifact | SHA-256 |
|---|---|
| `bench/jev/adapter.py` | `26fd3b4564db43b3469cffa1f8efee00e6c1237f7bfede13dbec8f5df0b6565d` |
| `bench/jev/run.py` | `7dd60ca25a5f96f80c0297522766bfa9464885d7251c385c273af61ab90e83ab` |
| `bench/jev/test_model_resolution.py` | `d30a86e554d132a1f05654433fb6d0d18c3bc8960200820126a99041a206dddf` |
| `bench/jev/audit.py` | `e5d6047f28249bc7eae583ac4cc467e936ff666192372e5c1bbdbd1375549b14` |
| `bench/jev/test_audit.py` | `117622b95c086234cc58ed2b2a44ca29660763e21838dfa28f6ba5171057f840` |

The unchanged fixture, bridge, binary, other test modules, and frozen result receipts retain the separately recorded identities above. The receipt replay also successfully checked the recorded v1 `adapter.py` and `run.py` hashes against retained local Git objects for both recorded revisions. Thus the historical source evidence remains retrievable even though the working files implement the newer contract.

### Closure of the two executable witnesses

- **Unpinned default aliases:** `adapter.py:238–239` now rejects a known requested alias without a resolution allowlist at construction, with `model_alias_requires_explicit_resolution_policy`. The original reviewer witness was rerun with a mock transport and observed **zero transport calls**. Both `jev-latest` and `jev-preview` are covered by the regression. The allowlisted opt-in path still binds only a permitted non-alias returned identity after complete validation and budget checks, and still poisons on identity drift.
- **Credential escaping:** `adapter.py:233–235` deliberately narrows accepted credential characters to `[A-Za-z0-9_-]`, length 1–512. The original synthetic quote/backslash witness now raises `invalid_api_key` before a client can transmit anything, with **zero transport calls**. Escaped echoes of otherwise accepted credentials remain covered by the decoded-and-reserialized response test. This establishes behavior for the deliberately accepted character set, not the completeness of that set for every possible provider credential format.
- **No guessed live model:** `run.py:360,366–367` requires an explicit `--model` for live mode before reading credentials or creating a client. The regression verifies both operations remain uncalled when the model argument is absent. This does not automatically verify account availability for an operator-supplied model.

### Newly audited stopped-receipt replay and projection

The reviewer read all of `audit.py` and `test_audit.py` before running them. `audit.verify` checks fixture, policy, protocol, historical implementation, and request identities, then reconstructs campaign control flow from the stored calls. Missing calls and post-stop calls fail. Recorded status, stages, calls, usage totals, usage completeness, and lack of production promotion must agree with the reconstruction (`audit.py:30–115`). The replay client uses retained data and never invokes the live adapter.

`audit.project` constructs the complete 66 local claim/evidence packs plus two exact duplicate controls. It projects only completed ordinary judgments, not rejected or budget-crossing responses (`audit.py:118–146`). This exclusion is explicitly disclosed in the artifact. Both actual stopped receipts have no eligible judgments, so the manifest is empty rather than populated from gold, inferred labels, or a fabricated response body.

The 67-test run included **17 adapter, 20 runner, 12 bridge, 13 model-resolution, and 5 receipt-audit tests**. The reviewer used an empty inherited environment except explicit safe paths/settings, the known local binary, disabled Git lazy fetching (`GIT_NO_LAZY_FETCH=1`), disabled Git terminal prompting, and disabled global/system Git configuration. Only the five fully inspected test modules were loaded. Adapter tests blocked unmocked sockets/children, and receipt-audit tests blocked socket connections and `Client.evaluate`. The bridge's evaluator subprocesses retained their own minimal environment and `/usr/bin/false` provider configuration.

In addition to the suite, the reviewer independently ran the following checks on **each** frozen receipt:

1. Changing its recorded status to `semantic_screen_passed` and clearing the stop reason was rejected with `receipt replay disagrees with recorded result`.
2. Real-Monty audit projection returned the following substantive result:

```json
{
  "receipt_replay_consistent": true,
  "complete": false,
  "occurrences": 68,
  "unique_judged": 0,
  "unjudged": 68,
  "semantic_efficacy_established": false
}
```

3. All 68 ledger rows were present, labeled `unjudged`, and had `accepted: false`. The two duplicate controls preserved the corresponding original packs. The tested strict projection rejected missing judgments instead of emitting a complete result.
4. Both original receipt hashes remained unchanged: `1041260d...cddaa` for the pinned-model failure and `f0b01dd1...126a4` for the alias failure, with full hashes retained in the earlier evidence table.

**Interpretation boundary:** successful replay means internal consistency of the supplied local evidence and the current replay rules. Historical source-hash verification does not execute every historical implementation or authenticate a provider response. These stopped-receipt tests do not establish behavior for every possible successful historical receipt, authenticate discarded bodies, recover unknown billing, or demonstrate semantic accuracy. In particular, a successful audit command is not a completed semantic campaign: consumers must honor the nested `complete: false`, zero judged count, and false efficacy flag.

**Final disposition:** the additional assignment is complete. Current offline-only alias safeguards and the stopped-receipt/partial-custody claims were independently verified. The original campaign stays stopped exactly as amended. No further live inference, production promotion, automatic pruning, or comparative performance claim follows from this work.
