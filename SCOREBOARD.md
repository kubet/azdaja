# Azdaja Scoreboard

## Current canonical fixed-199 diagnostic

| Status | Protocol | Fixed-denominator score | Execution / valid predictions | Retained failure zeros |
|---|---|---:|---:|---:|
| Permanent, terminal, scored exactly once, closed | RAH-protocol Oolong, fixed 199 rows | **68.64164968987583%** | 185/199 | 14 |

The completed-row mean is 73.83615290965021%; multiplying it by the fixed execution fraction (185/199) yields the fixed-denominator result above. All 199 scheduled rows reached terminal accounting, every failure remains a zero, and the score is frozen. The [sanitized terminal receipt](bench/results/gpt-rah199-mortality-v3-terminal-public.json) binds the retained hashes, exclusive gold-access sentinel, one successful scorer invocation, and `TERMINAL_COMPLETED_SCORED_ONCE_CLOSED` status.

This is a private, single-arm, validation-derived diagnostic, not official full OOLONG, a leaderboard result, a paired comparison, or evidence of superiority or general capability. Root usage is provider-reported for 198 of 199 rows; the missing row is not imputed, so the measured ~5.4K mean is not a complete fixed-199 aggregate.

For class context, the RAH paper ([arXiv:2606.13643](https://arxiv.org/abs/2606.13643)) reports Oolong-Synthetic results for its 199-sample, 13-bucket protocol with a GPT-5 backbone. This is the same bounded numeric ladder shown in the README:

| Source | Label | System class | Oolong score |
|---|---|---|---:|
| Paper | RLM | Model recursion without agent tools | **64.38%** |
| This repository | Azdaja — single-arm diagnostic; not paper/leaderboard | Bare RLM layer | **68.64%** |
| Paper | Codex, No Retriever | Coding agent | **71.75%** |
| Paper | RAH, GPT-5 | Recursive Agent Harness | **81.36%** |

The exact Azdaja diagnostic is 4.26164968987583 percentage points above the displayed 64.38% paper RLM reference (4.3 points rounded). That arithmetic does not rerun the controls, isolate a cause, or establish equivalence. The next displayed class is Codex at 71.75%, which Azdaja has not reached.

## Current install and release boundary

| Surface | Latest retained result | Boundary / receipt |
|---|---|---|
| Current-source installer and `az` alias | Provider-free local fixtures pass, including complete-set custody preflight and zero-mutation hardlink, symlink, unknown-target, inode/link/mode, and late multi-target refusal coverage | The exact-source [integration acceptance receipt](bench/results/integration-acceptance-v0.1.2-local.json) supersedes the immutable historical alias-delta receipt for current-source claims. Selector tests are not native cross-platform binary or provider validation. |
| Current-source 50 MiB acceptance | Three scripted 52,428,800-byte cases pass through the release binary under the unchanged 90-second watchdog | This gate is release-only and explicitly ignored in ordinary debug tests; active push/PR CI builds with `cargo build --release --locked` and runs the exact ignored test with `AZDAJA_PRODUCT_BINARY=target/release/azdaja`. |
| v0.1.2 candidate readiness | `REBUILD_AND_CROSS_PLATFORM_RETEST_REQUIRED` | The [supersession receipt](bench/results/v0.1.2-candidate-readiness-superseded-public.json) makes the retained pre-change binaries and earlier install/adapter matrices historical only. New native assets, checksums, and a fresh release matrix are required before release readiness. |

Installation itself makes no provider call. `Config::load` support for adjacent managed `azdaja-config.toml` is integrated and tested; the old receipt's pending label is immutable historical state, not a current-source limitation. `doctor --caps` is local; only an explicit passing `doctor` exercises and validates the configured route. The old [alias-delta receipt](bench/results/install-alias-delta-v0.1.2-public.json), historical v0.1.2 [install matrix](bench/results/install-matrix-v0.1.2-final-public.json), and [real-adapter receipt](bench/results/install-real-adapters-v0.1.2-final-public.json) remain evidence for their bound old bytes, not the current source.

## Current ARC-AGI-3 local-shadow boundary

The five-game v9 diagnostic retained a 0.0 Ember-minus-baseline **local shadow RHAE** difference for each game and unchanged-feedback counts of 646 for baseline and 654 for Ember (+8, or +1.24% relative to the baseline raw count). It retained no absolute arm scores, completed levels, total actions, per-level actions, or separate waste diagnostics, so it cannot distinguish equal zero from equal nonzero scores and does not support an efficiency or improvement claim.

A retrieval-only follow-up made no game or provider request and recovered none of the missing absolutes. A separate fresh `vc33` smoke recorded 0.0 local shadow RHAE, zero completed levels, 35 actions, three zero diagnostic counters, 36 journal records, and `ACTION_BUDGET` for each arm; it does not reconstruct v9. The prepared full-five source remains **HOLD / not run** and requires its separate fail-closed authorization gates.

Evidence: [ARC benchmark card](bench/arc3/README.md#benchmark-card), [sanitized v9 result](bench/results/arc3-ember-five-public-v9-result.json), [retrieval receipt](bench/results/arc3-scorecard-interrogation-public-v1.json), and [fresh `vc33` smoke receipt](bench/results/arc3-vc33-smoke-v2-public.json). These are local shadow diagnostics, not official ARC scores, leaderboard results, or evidence of general product performance. No new ARC, model, provider, scorecard, or repository request supports this section.

## Historical immutable RAH-199 result (superseded as the top-line result)

The following earlier campaign measurements, hashes, and then-current successor dispositions are preserved as immutable evidence. They are historical and do not replace or modify the current canonical fixed-199 result above.

### Defining campaign result

| Date | Protocol | Candidate | Root | Execution | Fixed-denominator score | 95% CI |
|---|---|---|---|---:|---:|---:|
| 2026-08-17 | RAH-199, fixed schedule `6fcbff4547b16472131c5d246929fd62aec5dd02407d6fa3812c3e1ab8093d20` | `99f8ee755f91a6fa2179c52903474db0cfd7d093` | Sol (`gpt-5.6-sol`) | 161/199 | **61.452662890467536%** | [54.88146552254204%, 67.87127651950791%] |

**161 completions averaging ~76% official; 38 deaths scored zero.** The exact completed-row average is 75.95701810685118%.

Binary SHA-256: `4ecb1e2178143b45e1bba8c30669b68adce68f30e8cf905d0bd500b28cb64225`. Results SHA-256: `89f81c5cdfaaa693c98592fdafd6223763d9fb92b15bf4b91c3efad468de4c1d`. Scores SHA-256: `8e1ada8a0e16caf04bccb2e2b2e128b6e3b82031536d654022e31b4c38db655d`.

Protocol citation: released OOLONG scoring/parser semantics at [`abertsch72/oolong@0bb7eab`](https://github.com/abertsch72/oolong/blob/0bb7eabe839218fee7fe8d007f41cfc2fd3ae24c/src/eval/eval_helpers.py), with the frozen schedule and scoring custody recorded in [`bench/results/rah199-99f-terminal-receipt.json`](bench/results/rah199-99f-terminal-receipt.json).

This is a preregistered validation-derived RAH slice, not official full OOLONG or a leaderboard result. The `99f8ee7` run is immutable and will not be retried, resumed, replaced, or rescored. The broader candidate campaign may continue only with separately frozen artifacts and schedules.

### Successor dispositions (not scores)

| Workstream | Disposition | Evidence boundary |
|---|---|---|
| MINI-RAH timeout-only successor | `NO_GO_NO_CANDIDATE` | The external 600-second row watchdog is not controlled by cell/sub-call timeouts; no candidate or MINI row exists. Commit [`5e66618`](https://github.com/kubet/azdaja/commit/5e66618388ab60f2209ddf1f2e4f07827f5a8aa4). |
| Agent-transport disease-10 scout | `INVALID_ABORT`, N/A | 8/20 zero-valued controller-failure rows retained, one unretained ninth row attempt interrupted with provider entry unknown, 0 agent-class calls, 0 score/gold invocations. [Receipt](bench/results/agent-transport-disease10-invalid-abort.json), SHA-256 `c19d3b7333d16467d6d8ba450f144a0b358d6c325fdaf4ea04997bd26cb2dcda`. |
| v0.1.1 two-platform public binary release | prepublication candidate, not a score | Exact Darwin arm64/Linux x86_64 candidate bytes and checksum plan exist; public tag/assets/curl remain blocked on reviewed GO. Immutable v0.1.0 is untouched. |
| ARC-AGI-3 paired MINI-PILOT | `PREP_READY_LIVE_BLOCKED`, not a score | Official Agents `4743e7d` and benchmarking `86d7217` are pinned; the five-game manifest is frozen at `32451563...fdef9`. One `ls20` Arcade/model/tool stub loop used 0 live requests, 0 provider inferences, and 0 ARC tokens. Live remains blocked on Track 1 full-199 confirmation plus explicit owner authorization. |

None of these rows changes, confirms, or extends the defining 61.452662890467536% result.
