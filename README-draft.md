# README draft — current campaign result

## RAH-199

On 2026-08-17, candidate `99f8ee755f91a6fa2179c52903474db0cfd7d093` (binary SHA-256 `4ecb1e2178143b45e1bba8c30669b68adce68f30e8cf905d0bd500b28cb64225`) completed the fixed 199-row RAH schedule with Sol (`gpt-5.6-sol`) as root. Its exactly-once authorized scorer produced **61.452662890467536%** fixed-denominator official-semantics score, with 95% bootstrap CI **[54.88146552254204%, 67.87127651950791%]**.

**161 completions averaging ~76% official; 38 deaths scored zero.** Execution and valid-prediction counts were both 161/199; the completed-row average was 75.95701810685118%.

Protocol citation: schedule `6fcbff4547b16472131c5d246929fd62aec5dd02407d6fa3812c3e1ab8093d20`; released OOLONG parser/scoring semantics at [`abertsch72/oolong@0bb7eab`](https://github.com/abertsch72/oolong/blob/0bb7eabe839218fee7fe8d007f41cfc2fd3ae24c/src/eval/eval_helpers.py); public-safe custody and hashes in [`bench/results/rah199-99f-terminal-receipt.json`](bench/results/rah199-99f-terminal-receipt.json).

Scope: preregistered validation-derived RAH slice, not official full OOLONG, a leaderboard result, or a paired-control superiority claim. The scored run is frozen; subsequent candidates require new immutable bytes, schedules, outputs, and ledgers.
