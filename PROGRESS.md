# Azdaja Speed Campaign Progress

## Current state

- The five-rule reset governs: frozen measurements/candidates remain byte-unchanged; inference is required for campaign evidence; benchmark harnesses stay unmodified; gold is scoring-only; results and leaks are reported truthfully.
- The reset-governed paired LongBench-v2 scout is complete on 30 identical public hard/long fixtures per arm (90 serial Luna/low turns): rebuilt Choice-v4r, Choice-v5, and native Jcode.
- Fixed-denominator official accuracy: native **21/30 (70.0%)**; v4r **14/30 (46.7%)**; v5 **14/30 (46.7%)**. Derived scoring is identical. Native wins the scout.
- Median all-attempt latency: native **13.078s**; v4r **11.092s**; v5 **11.091s**. v4r and v5 each executed/recognized 29/30; native executed/recognized 30/30.
- Both candidate arms had the same retained process-exit failure on `lb2-ec5a865e739ccacae26e111b655404d1`: relevance-choice query-term limit exceeded. Both candidates verified zero root-context leaks on 30/30 rows; native leak scanning is not applicable.
- v5 candidate commit `f8818f9b5da692d7dc1655187749afed63144189`; binary `d07da8db2ac48f5096dde788b9dacc503ea53305262f180fd63f520867993758`. v4r rebuild commit `94e90e5d259c30e660a2698ecd2f0a3c60ab3168`; binary `aaacca2602597c61870aff5a17e76914d9f33db2d20d473cff033d95648ef4b6`.

## Next three actions

1. Run the scout winner, native Jcode, through the required RULER smoke and require 20/20.
2. If RULER holds, run the 63-item LongBench step aiming to beat the frozen Azdaja baseline of 17 official correct.
3. After LongBench, continue to OOLONG/RAH in the requested order.

## Blocking

- No human blocker. RULER is the next required step; LongBench 63 is blocked on RULER 20/20, and OOLONG/RAH are blocked on LongBench completion.
- Gold was unavailable throughout all 90 inference turns and opened only by the terminal one-shot scorer after the no-gold validator passed 90/90.
