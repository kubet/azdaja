# Azdaja Scoreboard

## Defining campaign result

| Date | Protocol | Candidate | Root | Execution | Fixed-denominator score | 95% CI |
|---|---|---|---|---:|---:|---:|
| 2026-08-17 | RAH-199, fixed schedule `6fcbff4547b16472131c5d246929fd62aec5dd02407d6fa3812c3e1ab8093d20` | `99f8ee755f91a6fa2179c52903474db0cfd7d093` | Sol (`gpt-5.6-sol`) | 161/199 | **61.452662890467536%** | [54.88146552254204%, 67.87127651950791%] |

**161 completions averaging ~76% official; 38 deaths scored zero.** The exact completed-row average is 75.95701810685118%.

Binary SHA-256: `4ecb1e2178143b45e1bba8c30669b68adce68f30e8cf905d0bd500b28cb64225`. Results SHA-256: `89f81c5cdfaaa693c98592fdafd6223763d9fb92b15bf4b91c3efad468de4c1d`. Scores SHA-256: `8e1ada8a0e16caf04bccb2e2b2e128b6e3b82031536d654022e31b4c38db655d`.

Protocol citation: released OOLONG scoring/parser semantics at [`abertsch72/oolong@0bb7eab`](https://github.com/abertsch72/oolong/blob/0bb7eabe839218fee7fe8d007f41cfc2fd3ae24c/src/eval/eval_helpers.py), with the frozen schedule and scoring custody recorded in [`bench/results/rah199-99f-terminal-receipt.json`](bench/results/rah199-99f-terminal-receipt.json).

This is a preregistered validation-derived RAH slice, not official full OOLONG or a leaderboard result. The `99f8ee7` run is immutable and will not be retried, resumed, replaced, or rescored. The broader candidate campaign may continue only with separately frozen artifacts and schedules.
