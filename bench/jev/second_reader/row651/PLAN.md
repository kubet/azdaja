# Row651 second-reader panel proposal

## Root freeze requested

This owned directory prepares one deterministic, source-only ham
classification panel for the native Jev row651 fixture.  No provider,
credential, inference, retry, or grading path is entered.

The builder verifies the row binding and full source SHA-256
`78e61364029606a211e8d6fced3fefea42f37651bc2c4b84ef54856e1e70f4fe`, then
enumerates every `Date:` line.  It retains the physical source-line ID and
exact UTF-8 half-open byte span for each occurrence.  Duplicate messages are
separate occurrences and are never deduplicated.  The scope is all 17,469
records, with no month filter.

The question is one exact prior-gate NOUL question per occurrence.  Its
instruction is copied from `bench/jev/angle_lab/gate/prepare_grade.py`.
The prior shape has no explicit `criteria` member, so this panel does not
invent one.  The official aggregate question is retained in `MANIFEST.json`
only.  Neither the official answer nor per-record labels enter any pack.

## Pack policy comparison

Counts below use canonical compact JSON, contiguous greedy packing, and
atomic source-record boundaries:

| policy | question cap | state cap | request cap | packs | largest state | largest request | rough bytes/4 | rough bytes/3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `old64` | 64 | 24,000 | none | 273 | 11,790 | 37,819 | 9,443.75 | 12,591.67 |
| `candidate255` | 255 | 70,000 | 90,000 | 112 | 27,121 | 89,991 | 22,486.75 | 29,982.33 |

The candidate request cap binds first.  Its largest pack has 160 questions,
not 255.  The `/4` and `/3` values are explicitly rough serialized-byte
estimates and are not tokenizer bounds.  Root should freeze the policy before
any native subclass runner is admitted.  `candidate255` is the default output
policy because it satisfies the requested proposed subclass limits; `old64`
can be generated independently with `--policy old64`.

## Artifact contract

`occurrence-ledger.json` is the raw full occurrence ledger.  Each entry has
the source hash, record hash, physical line identity, exact byte span, and
exact line text.  `MANIFEST.json` records source identity, official question,
scope, frozen limits, per-pack state/question/request byte statistics, rough
estimates, and pack hashes.  Packs contain only `state.records` and matching
NOUL `questions`.

The builder is deliberately fail-closed on source drift, row drift, changed
instruction text, noncontiguous or over-budget packs, and nonempty output
directories.  Poisoned or missing model outputs and retry behavior remain the
native root runner's contract and are not simulated here.
