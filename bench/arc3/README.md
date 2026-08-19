# ARC-AGI-3 bounded diagnostics and gated sources

**State:** completed local-shadow diagnostics plus offline-validated source for a separate post-public plan. Nothing on this page authorizes a game, model, provider, scorecard, or repository request.

## Benchmark card

**Claim boundary.** These are local shadow diagnostics, not official ARC scores, leaderboard results, or a statistical test. No new ARC, model, provider, scorecard, or repository request supports this card.

### Method

The v9 pilot contains one fixed-order pair per listed game (baseline, then Ember), with seed 0 and a fresh game/runtime per arm. Both arms used the same pinned direct-Claude Sonnet configuration and per-level action caps of 5× the published human baselines; Ember alone staged the managed Azdaja skill, with one invocation after two completed turns. The driver's local shadow RHAE is `Σ(completed level i × min((human_actions_i / agent_actions_i)^2, 1.15)) / Σ(all level i)`, with one-based level weights. See the [hash-bound v9 manifest](mini-pilot-live-manifest-v9.json) for the frozen configuration and scoring contract.

The sanitized v9 result retained only the per-game Ember-minus-baseline local-shadow-RHAE difference and the two unchanged-feedback counts. It did not retain absolute arm RHAE, completed levels, total or per-level actions, or the separate revisited-state and repeated-known-control diagnostics. The minimal result JSON is intentionally not self-describing: method, lane, hashes, freshness, and scoring come from the separately hash-bound manifest, and there is no result sidecar, timestamp, or uncertainty estimate.

### Five-game v9 pilot

| Game | Local shadow RHAE Δ (Ember − baseline) | Baseline unchanged-feedback actions | Ember unchanged-feedback actions |
|---|---:|---:|---:|
| `ls20` | 0.0 | 92 | 103 |
| `ft09` | 0.0 | 186 | 208 |
| `vc33` | 0.0 | 0 | 0 |
| `ar25` | 0.0 | 137 | 110 |
| `wa30` | 0.0 | 231 | 233 |
| **Total (counts only)** | — | **646** | **654** |

“Unchanged-feedback action” is the v9 published `wasted_actions` rule: a non-`RESET` action whose official post-action feedback exactly equaled the immediately preceding official feedback. Ember recorded **+8 (+1.24% of the baseline raw count)**. Because v9 retained no action totals, this is not an action-normalized rate or an efficiency/improvement claim. All five retained paired differences are 0.0, but the missing absolutes mean the result cannot distinguish equal zero from equal nonzero arm scores. One pair per game, with no randomization or replication, supports no variance, uncertainty, or general-performance claim.

The v9 manifest retains the historical `dry_run_stub` marker on `ls20`; schema-v9 stub execution is disabled, and the completed live path selected all five games. The frozen manifest is unchanged.

### Retrieval boundary

A retrieval-only follow-up made no game or provider request and started no new experiment. All ten closed scorecard detail requests returned HTTP 404 despite the pinned contract's open-or-closed description; the HTML route redirected to the generic ARC-AGI-3 page. It recovered no absolute arm RHAE, completed levels, or total actions, and those values are absent from the retained v9 artifacts. The memory-efficiency hypothesis therefore remains open.

### Separate fresh `vc33` smoke

This is a distinct pair, not a reconstruction of v9.

| Arm | Local shadow RHAE | Levels completed | Actions issued (per level) | Counters: unchanged / revisited / repeated known control | Journal | Termination |
|---|---:|---:|---|---|---|---|
| Baseline | 0.0 | 0 | 35 (`[35, 0, 0, 0, 0, 0, 0]`) | `0 / 0 / 0` | 36 records | `ACTION_BUDGET` |
| Ember | 0.0 | 0 | 35 (`[35, 0, 0, 0, 0, 0, 0]`) | `0 / 0 / 0` | 36 records | `ACTION_BUDGET` |

The paired local-shadow-RHAE difference was 0.0. Both arms issued 35 actions, completed zero levels, and had a zero local-shadow score in this smoke only. The three displayed counters are separate diagnostics, not a partition of one aggregate. The smoke does not supply the missing v9 absolutes or an official ARC score.

Evidence: [sanitized v9 result](../results/arc3-ember-five-public-v9-result.json), [v9 manifest](mini-pilot-live-manifest-v9.json), [sanitized retrieval receipt](../results/arc3-scorecard-interrogation-public-v1.json), and [sanitized `vc33` smoke receipt](../results/arc3-vc33-smoke-v2-public.json).

## Gated full-five source (not run)

The prepared plan is a new five-pair run in the fixed order `ls20`, `ft09`, `vc33`, `ar25`, `wa30`, each with a fresh baseline arm followed by a fresh Ember arm on the same pinned direct-Claude lane. It reuses no prior game, session, or smoke artifact and would retain owner-only local-shadow absolutes, actions, levels, the three diagnostic counters, and hash-chained journals.

It remains **HOLD / not run**. Before constructing any ARC or model client, the fail-closed runner requires both a fresh receipt proving `kubet/azdaja` is public and a separate exact owner-GO binding to that receipt and manifest. Every artifact path must also be fresh, distinct, absolute, owner-only, and hash-bound. The one-shot sentinel forbids a rerun. Source preparation and this documentation create no authorization.

Plan evidence: [`arc-v2-five-postlaunch-manifest.json`](arc-v2-five-postlaunch-manifest.json). No new ARC or provider run was performed for this card.

## Retained source components

- `toolkit-lock.json`, `mini-pilot-manifest.json`, and their sidecars retain the pinned public toolkit and original zero-inference MINI preparation.
- `mini-pilot-live-manifest-v2.json` through `mini-pilot-live-manifest-v8.json` remain historical schema fixtures; the v9 manifest binds the completed sanitized result above. Their sidecars remain hash-bound.
- `driver.py`, `claude_lane.py`, and the ARC unit tests contain the latest fail-closed driver and local-custody implementation.
- `arc-v2-local-custody-manifest.json` binds the completed, exactly-one-pair custody scope. It does not authorize the separate five-game package.
- `arc_v2_post_public.py`, `bind_arc_v2_post_public.py`, and `arc-v2-five-postlaunch-manifest.json` contain the reviewable full-five source package. Source availability does not satisfy its execution gates.

## Offline validation

The committed unit suite uses temporary directories, in-process fakes, and stub observations. It neither reads an ARC key nor opens an ARC, game, model, provider, scorecard, or repository client:

```bash
python3 -m unittest discover -s bench/arc3 -p 'test_*.py' -v
```

`driver.py` also retains a deterministic stub path. Stub local-shadow-RHAE and action-count values are pipeline fixtures, not ARC results.

## Custody and claim boundary

Action journals retain only the official before/after game feedback needed for local scoring and audit. Model prompts, model responses, authentication material, API keys, scorecard requests, and raw provider traces are forbidden. Files are created exclusively with restrictive permissions, hash chained, and bound into terminal receipts.

Every retained value here is local shadow telemetry, not an official ARC score, leaderboard result, superiority claim, or aggregate product claim. The full-five source remains gated, and this documentation intentionally provides no execution recipe for it.
