# Independent row651 live review

Date: 2026-09-17

## Scope

Read-only replay of `results/row651-live-20260917/` against the current frozen `large_run.py` and `packs()` source/pack checks. No runner, pack, PLAN, validator, binary, or receipt artifacts were modified.

## Hashes

- Runner: `bench/jev/second_reader/large_run.py`
  - SHA-256: `b87b3087859fc6e14e68d60c46f3b778c6c2a264ab53dddaa7becb5e62fbbe51`
- Receipt: `03ae785f69708ab66d69998158ce03bd7db2fed6bab9fb4eddfe4881dfd38d72`
- Native reduction: `f271af8e9878d39619cdc61f2aa72577f6cb2fb9d56a64881d70c1de4474c17f`
- Receipt frozen-file inventory contains the same runner hash and the expected binary hash.

## Independent checks

- Terminal receipt is `completed`, cleanup exit is `0`, elapsed time is `210.0126917079906` seconds.
- All 112 calls are present in contiguous `pack-001` through `pack-112` order. Each has exactly one provider request. There are 112 request, observation, and reentry-cell artifacts, with no failure envelopes or retry calls.
- Every retained request exactly equals its frozen pack plus model. All 112 request hashes, source pack hashes, and response hashes match independently recomputed canonical SHA-256 values.
- `packs()` revalidated all 112 packs, source spans, contiguous occurrence-ledger membership, canonical wire ordering, caps, and all 17,469 question IDs. Retained answers contain 17,469 unique IDs with exact expected-set coverage.
- Input usage is `2,749,030` tokens and output usage is `357,302` tokens, matching the receipt and per-call sums. Unknown input/output usage is zero. Generative calls are zero and billing is explicitly unknown.
- Every answer is a finite numeric `noul` in `[0,1]`, with exact answer-key coverage per pack. The native reduction reports `complete=true`, `observed=17469`, `expected=17469`, `attempts_in_reduction=0`, `ham=9245`, and `answer=Answer: 9245`.
- Replaying the reduction in the native scalar accumulation order gives `sum_noul=9287.380000000025`, exactly matching the reduction. A grouped per-pack summation differs by about `2.2e-11`, ordinary floating-point grouping residue, not a validator or data mismatch.
- The runner's typed path performed native reentry equality checks for every call. Reentry outputs are not independently reconstructable from the retained reentry-cell source files, so this report relies on the runner's completed assertions for that specific property.
- Secret-pattern scan of retained top-level artifacts is clean. No semantic comparison against the official label aggregate was performed.

## Conclusion

No concrete blocker found. The terminal receipt supports the claimed 112 one-call typed requests, complete 17,469-ID coverage, usage totals, hashes, native reduction, and no-retry/no-repair behavior. The historical rejected body remains unrecoverable and is not inferred here.

## Closed replay and core-quality check

- Existing bounded replays both pass from the repository root: `replay_large` and `replay_policy` returned successfully without writing artifacts.
- Row651 replay summary SHA-256 is `a0aebef2d01d12bb8442483dfe58c1750a8c0bf821b3494a559762219507406f`. It matches the terminal receipt on 112 confirmed requests, 17,469 observed and expected occurrences, 2,749,030 input tokens, 357,302 output tokens, ham count 9,245, and elapsed time. All 452 retained hashes match their terminal files.
- Row651 quality is not an exact-task pass: the detached official count is 8,638, so the observed threshold count 9,245 has signed error +607 and sum error +649.38. Per-item accuracy was not measured, and this is not evidence of provider authenticity or generalization. No official label was used to repair results.
- Policy replay summary SHA-256 is `a57e487fa8716cde9751d2017221bf695e66dcdad0731fa5e2d7d117b79c5103`. Its complete panel is consistent with the policy receipt: 11 typed requests, 681 typed questions, 73,841 typed input tokens, 15,026 typed output tokens, zero unknown usage, and one successful generative request with 1,418 input and 33 output tokens.
- Policy core quality: baseline typed labels are correct on 220/227. Fresh blind adjudication raises the detached full-panel result to 222/227, with no adjudicated errors but five retained agreement errors: `r0044`, `r0503`, `r1383`, `r1394`, and `r1747`. Approval remains false.
- Phrasing variants score v0 219/227, v1 220/227, and v2 220/227. Majority vote is 219/227. Unanimity covers 225/227 and contains six errors. The two exact-vote disagreements are `r0044` and `r0282`. The replay explicitly treats the fresh v0 batch-composition change as not an isolated wording effect.

Conclusion for the closed quality check: transport and accounting are reproduced, but quality claims must remain bounded. Row651 does not match the official aggregate, and the policy study does not authorize approval or establish generalization.
