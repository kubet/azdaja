# Azdaja Scoreboard

## Defining campaign result

| Date | Protocol | Candidate | Root | Execution | Fixed-denominator score | 95% CI |
|---|---|---|---|---:|---:|---:|
| 2026-08-17 | RAH-199, fixed schedule `6fcbff4547b16472131c5d246929fd62aec5dd02407d6fa3812c3e1ab8093d20` | `99f8ee755f91a6fa2179c52903474db0cfd7d093` | Sol (`gpt-5.6-sol`) | 161/199 | **61.452662890467536%** | [54.88146552254204%, 67.87127651950791%] |

**161 completions averaging ~76% official; 38 deaths scored zero.** The exact completed-row average is 75.95701810685118%.

Binary SHA-256: `4ecb1e2178143b45e1bba8c30669b68adce68f30e8cf905d0bd500b28cb64225`. Results SHA-256: `89f81c5cdfaaa693c98592fdafd6223763d9fb92b15bf4b91c3efad468de4c1d`. Scores SHA-256: `8e1ada8a0e16caf04bccb2e2b2e128b6e3b82031536d654022e31b4c38db655d`.

Protocol citation: released OOLONG scoring/parser semantics at [`abertsch72/oolong@0bb7eab`](https://github.com/abertsch72/oolong/blob/0bb7eabe839218fee7fe8d007f41cfc2fd3ae24c/src/eval/eval_helpers.py), with the frozen schedule and scoring custody recorded in [`bench/results/rah199-99f-terminal-receipt.json`](bench/results/rah199-99f-terminal-receipt.json).

This is a preregistered validation-derived RAH slice, not official full OOLONG or a leaderboard result. The `99f8ee7` run is immutable and will not be retried, resumed, replaced, or rescored. The broader candidate campaign may continue only with separately frozen artifacts and schedules.

## Successor dispositions (not scores)

| Workstream | Disposition | Evidence boundary |
|---|---|---|
| MINI-RAH timeout-only successor | `NO_GO_NO_CANDIDATE` | The external 600-second row watchdog is not controlled by cell/sub-call timeouts; no candidate or MINI row exists. Commit [`5e66618`](https://github.com/kubet/azdaja/commit/5e66618388ab60f2209ddf1f2e4f07827f5a8aa4). |
| Agent-transport disease-10 scout | `INVALID_ABORT`, N/A | 8/20 zero-valued controller-failure rows retained, one unretained ninth row attempt interrupted with provider entry unknown, 0 agent-class calls, 0 score/gold invocations. [Receipt](bench/results/agent-transport-disease10-invalid-abort.json), SHA-256 `c19d3b7333d16467d6d8ba450f144a0b358d6c325fdaf4ea04997bd26cb2dcda`. |
| v0.1.1 two-platform public binary release | prepublication candidate, not a score | Exact Darwin arm64/Linux x86_64 candidate bytes and checksum plan exist; public tag/assets/curl remain blocked on reviewed GO. Immutable v0.1.0 is untouched. |
| ARC-AGI-3 paired MINI-PILOT | `PREP_READY_LIVE_BLOCKED`, not a score | Official Agents `4743e7d` and benchmarking `86d7217` are pinned; the five-game manifest is frozen at `32451563...fdef9`. One `ls20` Arcade/model/tool stub loop used 0 live requests, 0 provider inferences, and 0 ARC tokens. Live remains blocked on Track 1 full-199 confirmation plus explicit owner authorization. |

None of these rows changes, confirms, or extends the defining 61.452662890467536% result.
