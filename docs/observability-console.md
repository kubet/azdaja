# Virtual-memory observability console

Status: implemented on `main` for Azdaja v0.1.9.

## Product boundary

Azdaja keeps a complete UTF-8 source in a local evaluator and exposes selected evidence to model calls through explicit bounded operations. The console reports only what local state can support truthfully. It does not claim infinite context, infer one universal model route, or convert missing telemetry into a zero.

The UI has three distinct surfaces:

1. A bare interactive `azdaja` prints a static provider-free snapshot for the current canonical working directory and exits.
2. `az list` prints the current-folder live-session and source-summary table. When piped, it preserves stable raw session IDs for scripting. `az list --global` is the explicit user-global escape hatch.
3. `az map` opens the optional full-screen view and refreshes at a low fixed rate. `az map --global` selects the same global scope. Narrow or incapable terminals receive the static snapshot instead.

On a TTY, the bare snapshot may append a recent-project overview after the primary current-folder detail. Non-TTY output and explicit list, map, global, and machine-readable behavior are unchanged.

## Working-directory scope

The default console is intentionally project-shaped without persisting a project name. Azdaja canonicalizes the invoking working directory and uses it to select:

- sessions whose creation metadata binds them to that directory;
- aggregate source history written under a private hash-derived key in `observability/scopes`;
- the `scope` row shown in the static and full-screen views.

The path itself is not serialized into aggregate JSON. The global `observability/recent.json` remains an aggregate cross-folder history for explicit `--global` inspection and compatibility. New session operations (`load`, `exec`, `final`, and `kill`) require the same canonical directory as `start`. Older sessions without a binding remain readable, but are excluded from the default current-folder view and shown only globally; their completion history is also written globally rather than attributed to the invoking folder.

## Plain vocabulary

The implemented UI uses direct labels rather than theoretical shorthand:

- **new work**: this invocation's configured default model, runner, and thinking level;
- **live sessions**: current evaluator sessions and the default model persisted with each session;
- **source summary**: local numeric measurements for one loaded or completed source;
- **memory**: count and total measured bytes of source summaries;
- **pattern**: source summaries placed from repeated to varied;
- **variety**: byte-distribution variety expressed as a plain percentage;
- **recent**: the newest retained source summary;
- **measured details**: exact local measurements shown only on request.

`source`, `session`, `model`, `runner`, `variety`, `repetition`, `lines`, and `bytes` are preferred in user-facing text. The overview does not headline symbolic entropy notation, redundancy, or an inferred route.

## Configured defaults and observed work

The `new work` row is provenance for the current invocation's configuration. It answers: "What default would newly started work use now?" It does not answer which model every existing session used and does not claim an observed provider route.

A session persists its own default model when it is created. Two simultaneous sessions may therefore show different defaults. This can happen when configuration changes between starts or when a session is started with an explicit model. An individual model call can also override the session default. Because these states are intentionally distinct, the console never presents one observed universal route.

The configured runner label is derived from the current command configuration. Managed runners have plain labels such as `Jcode/OpenAI`, `Claude CLI`, `Codex CLI`, `Gemini CLI`, or `OpenCode`. Unrecognized commands are labeled `custom command`. The thinking label appears only when the configured runner exposes a value the console can parse.

## Source summaries and privacy

Numeric source summaries are separate from live sessions. A live session can exist without a measured source summary, and retained source summaries can remain after live work has finished.

The durable source-summary privacy contract excludes:

- source text;
- source paths;
- source hashes;
- prompts;
- responses.

This privacy claim is scoped to source summaries. Live-session state is not described as an anonymous aggregate. The UI may show a shortened session ID, running or idle state, age, evaluator-state size, source-load count, and the session's persisted default model.

For one source, the local summary records:

- source bytes;
- UTF-8 character count;
- physical line count;
- nonempty line count;
- exact Shannon byte entropy in thousandths of a bit per byte.

Model-boundary exposure and coverage remain `unmeasured` or `n/a` unless a future receipt records an explicit denominator and authority. They are never displayed as fake zero values.

## Default snapshot

The normal static snapshot uses these rows:

- `status`: healthy local metrics or a clear degraded-metrics warning;
- `new work`: current configured default provenance;
- `live`: running, idle, and slot counts;
- `memory`: source-summary count and measured bytes, labeled `numbers only`;
- `pattern`: `repeated ← … → varied · avg variety N%`;
- `recent`: newest loaded or finished source summary;
- `session`: up to three live sessions with status, age, and persisted default model;
- `next`: useful commands including `map`, `solo`, `list`, `list --global`, `doctor`, and `help`.

The overview uses `avg variety`, not entropy notation or redundancy terminology. The value is computed from local source-summary numbers only. It is not a model score, semantic score, compression ratio, or confidence estimate.

## Recent-project overview

The bare interactive snapshot may show at most three other recently active scopes. It merges candidates from local memory and observability state, orders them by activity, and excludes the current scope.

Scopes are represented only by stable short hash tokens. Raw paths and basename paths are never rendered. Memory-record and source-summary counts are bounded. Missing state omits the section; unsafe, corrupt, or oversized state degrades optional metrics rather than the primary current-folder detail.

The overview is an activity summary, not a confidence or quality score. It does not change evaluator or gate behavior.

## Empty state

A truly empty snapshot stays useful without inventing measurements:

```text
new work  <configured model> via <configured runner>
live      none · <N> slots free
memory    none yet · summaries keep numbers, not source text
pattern   appears after the first source
recent    no source summary yet
```

The configured `new work` row remains visible because it is known before any session exists. The constellation and average variety do not render a misleading zero.

## Narrow state

Narrow terminals preserve the same meaning in sanitized line-oriented output. Values may be truncated, but the labels remain `status`, `scope`, `new work`, `live`, `memory`, `pattern`, `recent`, and `session`. A terminal that is too small for the full-screen map receives this static fallback rather than a clipped interactive layout.

Control characters from configuration or state are removed before rendering. Tabs become spaces. Color obeys terminal capability and `NO_COLOR`.

## Live-session and source-summary table

`az list` is the detailed table for both kinds of local state.

The first section is `live sessions`. Each row contains a stable session ID, running or idle state, age, persisted default model, state size, and load/completion counts as space allows.

The second section is `source summaries · local numbers only`. Each row identifies loaded or finished state and reports local source measurements. This section is independent of the live-session section. If there are no source summaries, it says `none measured yet`.

## Labeled source-variety constellation

The constellation is a compact plot of local numeric source summaries. Every point is one summary.

- Horizontal position is the plain `repeated ← source variety → varied` axis.
- Vertical position is a labeled absolute source-size band: `<64 KiB`, `≥64 KiB`, `≥1 MiB`, or `≥16 MiB`.
- `●` marks the selected or newest summary.
- `○` marks an earlier summary.
- A digit marks overlapping summaries.

The overview strip and the full constellation use only local aggregate numbers. They do not use source text, semantic embeddings, prompts, responses, provider telemetry, or model judgments. The plot is not a semantic graph and distance between points is not semantic similarity.

When live sessions are present, selection follows the live-session list and measured details use that session's source summary if one exists. When only retained summaries are present, selection follows the summary history.

## Entropy is details-on-demand

Exact Shannon byte entropy is retained as a local measurement:

```text
H_byte = -sum(p_b * log2(p_b)), b in 0..255
```

Its range is `0..8 bits/byte`. The overview does not show this equation, an `H₀` label, or an exact entropy number. It translates the measurement into the plain variety axis and `avg variety` summary.

In `az map`, Enter or `d` opens measured details. That view can show:

- `entropy`: exact local bits per byte, with the caveat that higher means more byte variety;
- `variety`: a plain percentage, labeled distribution only and not quality;
- `repetition`: the complementary estimate, labeled as not file compression;
- line density and source-size details.

Entropy is deterministic and exact for the locally measured source bytes. Its interpretation is deliberately narrow. It does not measure semantic diversity, relevance, difficulty, confidence, model quality, model-boundary exposure, or coverage. Encodings and compression can change it without changing meaning.

## Full-screen behavior

`az map` refreshes every two seconds and supports:

- arrows or `j/k` to select;
- Enter to inspect;
- `d` to toggle measured details;
- `i` to inspect validated local integrations;
- `r` to refresh;
- `q`, Esc, or Ctrl-C to exit.

Normal exit and panic restore raw mode, cursor visibility, and the previous terminal screen. Read or validation failures are sanitized and displayed as local errors. A corrupt or unsafe source-summary sidecar degrades observability without making core live-session state unavailable.

## Entropy, uncertainty, and collective-agent boundaries

The console computes exact Shannon entropy over the empirical UTF-8 byte histogram:

```text
H_byte = -sum(p_b * log2(p_b)), b in 0..255
```

This is a source-text distribution measurement. It is not the semantic entropy of sampled model answers and cannot be interpreted as calibrated correctness probability. Semantic entropy needs repeated answers plus semantic-equivalence clustering. Self-consistency and multi-agent debate show why repeated proposals can help on some tasks, but agreement can still share a common error. In Azdaja, disagreement is therefore a candidate escalation or abstention signal, never a headline “quality” number.

The implemented `az memory` ledger applies the narrow local-first pattern without changing the evaluator: inspectable JSONL records, typed kinds and tags, explicit `supports`/`supersedes`/`derived-from`/`related-to` links, manual provenance, bounded append-only history, and scope-first deterministic retrieval. It supports a separate explicit global ledger, but never merges project ledgers implicitly and never injects records into a model. A graph view, vector store, automatic reflection loop, and model-authored memory remain out of scope until an acceptance task measures benefit and leakage.

## Non-goals

The v0.1.9 console does not claim:

- one observed universal model or provider route;
- semantic similarity from constellation distance;
- token usage or cost without authoritative provider data;
- model-boundary exposure without a recorded ledger;
- coverage without an explicit denominator;
- answer quality from byte variety;
- privacy guarantees for fields outside the source-summary contract.

Research references: [semantic entropy](https://www.nature.com/articles/s41586-024-07421-0), [self-consistency](https://arxiv.org/abs/2203.11171), [multi-agent debate](https://arxiv.org/abs/2305.14325), [Obsidian backlinks](https://help.obsidian.md/plugins/backlinks), and [Obsidian properties](https://help.obsidian.md/Editing+and+formatting/Properties).
