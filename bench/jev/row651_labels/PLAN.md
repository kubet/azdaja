# Post-run official-label audit

This is an offline follow-through to the single frozen row651 run, not a new model experiment. The official public dataset was fetched once after inference. The original inputs, questions, outputs, thresholds and receipts stay unchanged.

## Fixed analysis

1. Require the complete official validation row651 with `partial=false` and no truncated cells. Pin the complete response bytes. Require exact equality of all shared task metadata and the complete unlabeled source.
2. Align every labeled physical line by removing only the official ` || Label: ham/spam` suffix. Require every remaining byte, nonrecord line, line terminator, occurrence ID and source span to match. No fuzzy matching, deduplication, label inference or selective exclusions.
3. Run the existing full-row receipt verifier before consuming any prediction. Join by exact occurrence ID, require all 17,469 observations once, and retain original threshold 0.5. Require the label sum to match the official 8,638 aggregate.
4. Report the entire source-bound occurrence ledger, confusion matrix, exact false-positive/negative IDs, accuracy, Brier score, positive-probability reliability/ECE for equal-width 5 and 10 bins, and sum(p) minus gold. Empty bins remain visible. No bin/threshold/model/prompt selection from these results.
5. Keep exact-task failure, bytes/tokens, measured time and input-price estimate from the unchanged run. A calibration statistic is not an independent safety certificate. Occurrences can be dependent and public benchmark contamination/annotation ambiguity remain.
6. Test altered/truncated/reordered sources, missing/duplicate predictions, boolean/nonfinite probabilities, wrong gold types, exact endpoint bins, output overwrite/symlink refusal and the actual public offline CLI. Validate the other two flagged goals through their existing public measurement/report CLIs and mutation tests.

No new inference, generative baseline, bootstrap independence assumption, production confidence cutoff, README claim or reopening of stopped memory/RAG work is authorized by this analysis. Report source-fetch requests separately from model requests. Historical reports remain historical; the new labeled audit may supersede their explicit absence of per-item gold, but not their observed model results.
