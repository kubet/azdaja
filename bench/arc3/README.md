# ARC-AGI-3 paired MINI-PILOT preparation

**State: `FROZEN_PREP_ONLY_DO_NOT_LAUNCH`.** This directory contains a zero-inference preparation only. It must not make an ARC game request, model/provider request, or spend an ARC live token before both Track 1 full-199 confirmation and explicit owner authorization are recorded.

## Pinned authority

The requested upstreams were cloned into a private, gitignored preparation directory and are not vendored:

| Role | Authoritative repository | Commit | License |
|---|---|---|---|
| API agent quickstart (`ARC_API_KEY`, `ls20`, Arcade agent loop) | `https://github.com/arcprize/ARC-AGI-3-Agents.git` | `4743e7d0aaae0ded0d98a89a7e282e63564cd58b` | MIT |
| Official benchmarking/harness semantics | `https://github.com/arcprize/arc-agi-3-benchmarking.git` | `86d72170ce3155551712a9fafd290bab471d6eee` | MIT |

`toolkit-lock.json` records these identities, file hashes, the pinned official documentation, and the transitive `arc-agi` runtime reference. The Kaggle starter is not a driver or scoring authority here.

## Frozen comparison

`mini-pilot-manifest.json` freezes five public game IDs and one order:

`ls20`, `ft09`, `vc33`, `ar25`, `wa30`

Each game has official per-level human baseline actions, per-level action caps of exactly `ceil(5.0 × baseline)`, and a total cap equal to the sum of those level caps. That matches the pinned benchmarking agent's `MAX_ACTIONS_BASELINE_MULTIPLIER=5.0` semantics. The five rows span the official Agent Reasoning, Elementary Logic, and Orchestration examples plus distinct eight- and nine-level action profiles; the latter two semantic labels must be rechecked during an authorized preflight rather than inferred now.

The paired arm order is fixed for every game:

1. `jcode-native`
2. `jcode-azdaja`

Both use the same pinned Jcode binary, provider, `gpt-5.6-luna`, low reasoning, seed, action schema, game order, and read-only Jcode tool exposure. The only treatment delta is the managed Azdaja v0.1.1 skill. It may trigger once, after exactly two completed environment turns. Its only `-f` input is the accumulated owner-only `turn-history.jsonl`; the driver checks mode `0600`, owner, link count, inode, and unchanged bytes. Temporary Jcode OAuth state, session state, history, and managed-skill bytes are isolated per arm and removed.

## Registration and key binding

Official registration is interactive: visit <https://arcprize.org/platform>, log in with the owner's Google or GitHub account, open the profile's **API Keys** section, and create the free ARC key. No noninteractive registration path is documented, so no identity or secret was invented. No `ARC_API_KEY` was present in this preparation environment.

Bind an owner key for a future authorized shell without writing it to a repository or log:

```bash
read -rsp 'ARC_API_KEY: ' ARC_API_KEY; printf '\n'
export ARC_API_KEY
```

After the authorized run, use `unset ARC_API_KEY`. Never place it in `.env`, arguments, receipts, or retained output for this campaign.

## Gates

Provider-free manifest preflight:

```bash
python3 bench/arc3/driver.py preflight
```

The live path requires all of the following and fails before importing/constructing Arcade when any is absent:

- manifest status changed in a reviewed future commit to `FROZEN_AUTHORIZED_FOR_LIVE_MINI`;
- both manifest authorization booleans are true;
- a separate owner-only `0600` authorization JSON binds the exact manifest hash and asserts Track 1 full-199 plus ARC-live owner authorization;
- `ARC_API_KEY` is present only in the parent process environment;
- exact Jcode and platform Azdaja binary hashes match;
- the isolated managed skill's `SKILL.md`, `config.toml`, and binary hashes match.

Future command shape (do **not** run in the current frozen state):

```bash
python3 bench/arc3/driver.py live \
  --authorization /owner-only/path/arc3-authorization.json \
  --jcode "$(command -v jcode)" \
  --azdaja /owner-only/path/azdaja-v0.1.1-$(uname -s)-$(uname -m) \
  --owner-home "$HOME" \
  --output /owner-only/path/arc3-mini-result.json
```

## Offline stub dry run

`dry-run` uses an in-process `StubArcade`/`StubArcadeGame`, one deterministic model class shared by both arms, and one deterministic Azdaja-skill stub. It recognizes exactly one public game ID (`ls20`) but does not load or simulate the real game. It proves action submission, accumulated owner-only history, treatment-only tool input, local shadow RHAE, wasted-action accounting, paired deltas, and cleanup. It never reads an ARC key or opens a network client.

Committed `stub-dry-run-receipt.json` is the sole full-loop dry run for this preparation.

## Metrics and claim boundary

For each game, local shadow scoring uses the pinned official documentation: square per-level human/agent action efficiency, cap at `1.15`, then weight completed levels by one-indexed level number over all game levels. It also counts:

- **revisited states:** a post-action state hash seen previously;
- **repeated known controls:** the same action/data repeated from the same known pre-state.

Only within-game treatment-minus-control deltas are comparable. Stub RHAE numbers are pipeline fixtures, not ARC results. Future live per-game RHAE remains shadow telemetry, not an absolute ARC score, leaderboard result, superiority claim, or aggregate score claim.
