# Official per-item label follow-through

Retrieved one complete public validation row from the official
[oolongbench/oolong-synth dataset](https://huggingface.co/datasets/oolongbench/oolong-synth)
on 2026-09-17, after the closed inference campaign. The source paper is
[Oolong: Evaluating Long Context Reasoning and Aggregation Capabilities](https://arxiv.org/abs/2511.02817),
Bertsch, Pratapa, Mitamura, Neubig and Gormley. The original repository benchmark
already retains its unlabeled row645 context. This adds the official labeled
reference, not new model inputs or new model outputs.

The earlier local fixture omitted `context_window_text_with_labels`. The official
dataset exposes it. Its unlabelled context, row ID, question and aggregate answer
match the retained fixture exactly. Every one of2177occurrences is aligned by
removing only the official ` || Label: ham/spam` suffix and comparing all remaining
bytes. No fuzzy text joins, positional assumptions without byte checks, deduplication,
model-generated gold or probability-derived labels are used.

`official-row645.json` retains the complete700,970byte API response and its checksum
is pinned in `audit.py`. `partial=false` and `truncated_cells=[]` are checked.
The returned labels were never sent to either model. The prior source audit and
the original model receipts remain unchanged. The old statement about missing
per-item gold is superseded for this official upstream follow-through.

Replay: `python3 -B -m bench.jev.row645_labels.audit --output NEW.json`.
The command is offline, refuses to overwrite an existing output, and produces
the complete227-occurrence gold/probability/decision ledger and exact error IDs.
Official dataset labels are benchmark annotations, not a fresh independent
adjudication of every ambiguous SMS message. No corrected-model rerun is warranted
without a demonstrated implementation defect.
