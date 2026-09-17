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
