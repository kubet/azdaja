# Azdaja Speed Campaign Progress

## Current state

- Campaign reset: only frozen-measurement integrity, scoring-only gold access, truthful results, unmodified benchmark harnesses, and zero context leaks remain mandatory.
- Private main product is promoted V58 (Luna/low).
- Frozen LongBench medians: Azdaja 18.045s, native Jcode 14.542s, Prime Agent 29.261s. Azdaja is 1.241x native and already faster than Prime.
- Accuracy is the blocker: Azdaja 17/63 official and 24/63 derived versus native 34/63 official. Speed target passes; equal-or-better accuracy does not.
- Gold is detached. Existing frozen measurements will not be rerun or altered. New candidates may use disposable, gold-blind scouts; frozen evaluation is confirmation only.

## Next three actions

1. Implement a new product-only candidate that improves multiple-choice evidence selection and canonical final formatting; do not modify benchmark harness behavior.
2. Run locked tests plus cheap isolated synthetic/disposable scouts, with expected answers opened only by the scorer after inference.
3. Keep or kill by measured latency, accuracy, and leak results; iterate immediately on the next candidate.

## Blocking

- No current human blocker. LongBench gold remains detached and is needed only for a future one-shot scoring confirmation of a scout-qualified new candidate.
- Exact-v43 LongBench already has an immutable one-time score; it will not be rescored. If the user intended a different valid unscored v43 freeze, its exact root must be identified before any gold mount.
