# ARC-AGI-3 offline preparation and gated ARC-v2 sources

**State: source and offline validation only.** Nothing in this directory is a
public ARC result, an authorization to play a game, or permission to make a
model/provider request.

## Retained components

- `toolkit-lock.json`, `mini-pilot-manifest.json`, and their sidecars retain the
  pinned public toolkit and original zero-inference MINI preparation.
- `mini-pilot-live-manifest-v2.json` through `mini-pilot-live-manifest-v9.json`
  are historical schema fixtures still exercised by `test_driver.py`; their
  sidecars remain hash-bound for that compatibility coverage.
- `driver.py`, `claude_lane.py`, and the ARC unit tests contain the latest
  fail-closed driver and local-custody implementation.
- `arc-v2-local-custody-manifest.json` binds the completed, exactly-one-pair
  custody scope. It does not authorize the separate five-game package.
- `arc_v2_post_public.py`, `bind_arc_v2_post_public.py`, and
  `arc-v2-five-postlaunch-manifest.json` contain the reviewable five-game
  source package. Source availability does not satisfy its execution gates.

The pinned public game order is `ls20`, `ft09`, `vc33`, `ar25`, `wa30`.
Per-level and total action caps remain exactly five times the published human
baselines. Both arms use the same game order, model lane, seed, action schema,
and fresh runtime rules; only the treatment arm stages the managed skill.

## Offline validation

The committed unit suite uses temporary directories, in-process fakes, and
stub observations. It neither reads an ARC key nor opens an ARC, game, model,
provider, scorecard, or repository client:

```bash
python3 -m unittest discover -s bench/arc3 -p 'test_*.py' -v
```

`driver.py` also retains the original deterministic stub path. Stub RHAE and
wasted-action values are pipeline fixtures, not ARC results.

## Five-game gate

The full five-game package is deliberately inert before publication. Its
manifest records both the post-public visibility binding and explicit GO
binding as false. The runner must reject execution before constructing an ARC
client or model process unless all of the following independently validate:

1. a fresh, locally supplied repository metadata receipt proves the required
   public visibility and is bound to the expected repository;
2. an explicit post-public GO marker binds that receipt and the exact manifest;
3. every output, journal, terminal receipt, failure artifact, and one-shot
   sentinel path is fresh, distinct, absolute, and mode-restricted; and
4. the exact driver, lane, runner, binder, model binary, and treatment bundle
   hashes match their frozen values.

The binder performs no network operation; metadata collection remains outside
this repository. The authorization receipt and execution artifacts are never
committed. A consumed sentinel makes the package refuse any rerun.

## Custody and claim boundary

Action journals retain only the official before/after game feedback needed for
local scoring and audit. Model prompts, model responses, authentication
material, API keys, scorecard requests, and raw provider traces are forbidden.
Files are created exclusively with restrictive permissions, hash chained, and
bound into terminal receipts.

Any future retained score is local shadow telemetry, not an official ARC score,
leaderboard result, superiority claim, or aggregate product claim. The
five-game rerun remains gated; this documentation intentionally provides no
execution recipe for it.
