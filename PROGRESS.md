# Azdaja Speed Campaign Progress

## Current state

- Frozen measurements and candidate binaries remain byte-unchanged. Benchmark harness sources remain unmodified; gold is scoring-only; every new inference row retains failures and leak evidence.
- **The holistic multiple-choice/choice line is closed.** On 30 identical LongBench-v2 hard/long rows, native Jcode scored 21/30 (70.0%) while v4r and v5 each scored 14/30 (46.7%): a measured **-23.3 percentage-point** boundary. v4r/v5 were faster (11.092s/11.091s medians versus native 13.078s), verified zero Azdaja root-context leaks 30/30, and historical fixed-63 context evidence is about 9.2x (~10x) cheaper (7,587 versus 69,717 mean root tokens), but holistic accuracy did not follow. Prime's separate below-chance 12/63 control corroborates that this is a task boundary, not a useful offline-gate win.
- v4r/v5 exact outputs matched on 26/30 rows and differed on four. Trace audit proves v5's structured contrastive `relevance_choice` path was invoked with the choices object on 30/30 rows; 29 completed and one hit the shared query-term limit. Because accuracy remained exactly 14/30, the finding is **active-but-null: synthetic recall gate uncorrelated with task accuracy**.
- Shipping rule: **no candidate ships on offline gates without an inference differential of at least 10 identical rows.** The active generic query-cap fix raises the finite hard cap from 256 to 512 under the unchanged 8,192-character safety envelope. Full tests/clippy/release build passed; a fresh 10-row RULER differential completed 10/10 for both predecessor and fix, with zero leaks, two differing outputs, and medians 13.924s versus 12.421s. It remains unpromoted and unscored.
- Fresh native RULER smoke completed 20/20 execution but scored **19/20** exact/full-coverage, not the requested 20/20; the miss was one 131K `niah_multikey_3` row returning `Ready.`. Median latency was 11.446s. Native root-context leak scanning is not applicable.
- Stable keyed prompt caching is **dead on the shipped OpenAI OAuth route**: Jcode v0.75.3 has no `prompt_cache_key` field in shipped config, and its request builder omits both cache key and retention whenever `is_chatgpt_mode` is true. The streamed 10-row candidate cache-read sequence was `0,0,0,1792,0,0,0,0,0,0`, so items 2+ did not hit. Do not cite keyed prompt caching as a future optimization again.

## Next three actions

1. Implement the product-mode warm-root daemon: lazy first use, `idle_timeout` shutdown, fresh logical task context over a reusable static prefix, hard zero cross-task content; benchmark mode stays cold and future smokes add an `azdaja-warm` arm.
2. Close the overdue low/medium/high root-effort sweep on a fresh RULER smoke and adopt only the cheapest effort that actually holds 20/20.
3. Under warm+tuned turns, compare short-input multi-turn peek-first snippets against the one-cell path; require 20/20 and fail-closed `FINAL` before any length-conditional adoption, then report the remaining effective provider knobs.

## Blocking

- Choice/LongBench candidate work is closed; no further LongBench candidate may precede the product-mode workstream.
- RULER parity is not yet established: native measured 19/20, and the active product fix has only a no-gold 10-row differential. OOLONG/RAH remain downstream of the product-mode RULER decision.
