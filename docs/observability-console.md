# Virtual-memory observability console

Status: implemented for the v0.1.5 CLI.

## Product thesis

Azdaja does not promise "infinite context." It provides:

- complete local custody of one UTF-8 source;
- a bounded model-facing surface;
- deterministic parsing and reduction before semantic work;
- explicit, bounded model subcalls;
- fail-closed coverage contracts and auditable runtime receipts.

The console must make those properties visible. Minimal means that every displayed cell answers an operational question. It does not mean an empty status card.

## Research basis

The design combines:

- Recursive Language Models and Recursive Agent Harnesses for externalized context, programmatic inspection, bounded recursion, and explicit subcall accounting;
- MemGPT and classical virtual-memory working-set theory for resident state, model-facing working sets, faults, pressure, and thrashing language;
- Lost in the Middle, RULER, LongBench v2, InfiniteBench, NoLiMa, and HELMET for the limits of raw context length as a quality signal;
- OpenTelemetry GenAI conventions and OpenInference for spans, attempts, token usage, latency, errors, and route identity;
- Obsidian local graph, Shneiderman's overview/zoom/filter/details-on-demand, Furnas fisheye views, and information foraging for local focus with global context;
- Shannon entropy and compression as distributional and redundancy measures, never as semantic truth or confidence;
- CLI Guidelines, Ratatui, Crossterm, NO_COLOR, and WCAG principles for terminal behavior and accessibility.

## Vocabulary

Use one metaphor consistently: virtual memory.

- **resident**: complete source retained locally;
- **working set**: source-derived evidence deliberately exposed to model calls;
- **held local**: source bytes not exposed to a model;
- **map**: positional source buckets with measured exposure states;
- **recall**: a model-facing semantic call;
- **coverage**: a specifically defined structural or record denominator, never generic confidence;
- **pressure**: resource pressure against a measured configured limit;
- **fault**: a typed failed attempt or missing required evidence, not any ordinary cache miss.

Avoid mixing brain, nest, lake, graph, cache, and memory metaphors in the primary UI. An Obsidian-like constellation is an aesthetic influence, not the data model.

## Evidence tiers

Every nontrivial metric has an authority tier.

1. `exact-local`: aggregate computed from the complete resident source without revealing content.
2. `exact-structural`: offsets, ranges, counts, ledgers, and positional buckets without revealing text.
3. `bounded-sample`: the escaped, overlap-guarded structural sample visible to the root model.
4. `selected-evidence`: source-derived evidence deliberately included in child prompts.
5. `model-derived`: semantic labels, clusters, disagreements, or confidence-like estimates.
6. `benchmark-only`: metrics requiring gold relevance judgments or a native full-context control.

The primary view uses tiers 1 and 2. Other tiers appear only when observed and are labelled in detail views.

## Primary observability questions

The first screen answers, in order:

1. Is memory healthy and private?
2. How much source is resident?
3. How much source-derived material crossed the model boundary?
4. What deterministic and semantic work occurred?
5. Is the requested coverage proven, partial, failed, or not applicable?
6. What did the run cost in calls, tokens, latency, and retries?
7. What is the next useful action?

## Honest metrics

### Always safe and exact

- source bytes, UTF-8 characters, physical lines, nonempty lines;
- resident session state bytes;
- source age and idle expiry;
- session count and configured session limit;
- root prompt characters and bounded structural-sample characters;
- child call count, entered turns, attempts, retries, and typed failures;
- child prompt and response characters;
- input, output, cache-read, cache-write, and reasoning tokens when provider usage is authoritative;
- deterministic evaluator time, model-call wall time, snapshot load/save time;
- projection ledger occurrence count, selected occurrence count, unique targets, callers, and expanded outputs.

### Source entropy

Exact byte entropy:

```text
H_byte = -sum(p_b * log2(p_b)), b in 0..255
```

Range: `0..8 bits/byte`. Compute with 256 counters while the source is loaded. It measures byte-distribution spread. It does not measure meaning, importance, truth, uncertainty, or model difficulty.

Display only in an expanded source detail row as `byte entropy 4.8 / 8`, with the label `source texture` or an explicit `H₀ byte` label. Do not use a mysterious headline "entropy score."

Optional later metrics:

- normalized lexical entropy using the same Unicode-alphanumeric run policy as lexical relevance;
- effective vocabulary `2^H_lex`;
- deterministic zstd level-3 compression ratio and space saving.

Compression is a redundancy proxy for one fixed compressor, not Kolmogorov complexity.

### Model-facing working set

Track two denominators separately:

- total child-prompt bytes, including instructions;
- source-derived evidence bytes with exact provenance.

```text
exposure = source_derived_evidence_bytes / source_bytes
held_local = 1 - exposure
virtualization_gain = source_bytes / max(root_prompt_bytes + child_prompt_bytes, 1)
```

If exact provenance is unavailable, show total prompt bytes and label source exposure `unmeasured`. Never infer precise source exposure from arbitrary prompt length.

### Coverage and reduction

For exact character ranges:

```text
range_coverage = union(selected_ranges).chars / source_chars
range_reduction = source_chars / max(selected_chars, 1)
```

For declared records:

```text
record_coverage = expanded_occurrences / ledger_occurrences
selection_rate = selected_occurrences / ledger_occurrences
reuse_yield = 1 - unique_targets / max(selected_occurrences, 1)
```

Render coverage states as:

- `verified 100%` only when a complete denominator and validated expansion exist;
- `partial 12.4% selected` when selection is measured but semantic completeness is not claimed;
- `unproven` when arbitrary code or prompts bypass provenance helpers;
- `failed` when a required coverage contract did not validate;
- `n/a` when no exhaustive contract was requested.

### Semantic uncertainty

Do not synthesize a generic confidence percentage.

When strict A/B classification is used, show the directly observed disagreement rate and adjudication count. Semantic entropy requires multiple sampled outputs plus a declared equivalence or clustering policy. If added later, label it `model-derived` and show the model, sample count, and policy.

## Source memory map

Use a fixed positional strip, not a force-directed graph. Divide the source into 24 to 48 equal byte or record buckets.

Glyphs:

- `░` resident and held local;
- `▒` deterministically selected or inspected with exact structural provenance;
- `▓` included as source-derived evidence in a model prompt;
- `█` included repeatedly or currently active;
- `·` no source loaded;
- `?` provenance unavailable.

Color is redundant: glyph and legend carry meaning. The default view may omit the legend when only `░` and `·` appear. Detail view always shows it.

Do not claim that arbitrary evaluator reads are mapped unless the evaluator actually records them. The map is about measured model-boundary exposure, not every local Python character access.

## Default console

Target 58 to 78 columns and five to eight meaningful rows.

```text
╭─ azdaja · virtual memory ─────────────────────────────────╮
│ status    ● awake · complete source stays local           │
│ route     gpt-5.6-luna · openai · medium                  │
│ resident  52.4 MiB · 104,857 records · 1 active           │
│ boundary  82.1 KiB exposed · 99.84% held local            │
│ map       ░░░░▒▒░░▓▓░░░░░░░░░░░░░░                       │
│ flow      source → scan → 8 recalls → verify → final      │
│ coverage  verified 100% · reuse 73% · 0 faults            │
╰────────────────────────────────────────────────────────────╯
last  5.4k root · 21.3k child · 8.2s   enter inspect · q quit
```

Only render fields backed by observations. For example, omit `boundary` until prompt provenance exists. Never fill gaps with zero when the correct value is unknown.

### Empty state

```text
╭─ azdaja · virtual memory ────────────────────────────────╮
│ status    ○ dormant · source stays local                 │
│ route     gpt-5.6-luna · openai · medium                 │
│ resident  no source loaded                               │
│ map       ························                      │
│ next      ask your agent about one large input           │
╰───────────────────────────────────────────────────────────╯
installations  jcode active · claude available · gemini absent
```

The integration row must distinguish:

- `active`: managed Azdaja integration validates on disk;
- `available`: host tool executable is detected, integration absent;
- `absent`: host tool not detected;
- `needs repair`: managed files exist but fail custody validation.

### Narrow fallback

Plain lines, no border, same semantics. Non-TTY output remains the stable machine-friendly help unless an explicit status or JSON command is requested.

## Interaction model

Use Ratatui 0.30 and Crossterm 0.29 for the installed interactive console. The dashboard refreshes owner-only state at a low fixed rate and exits cleanly on `q`, Esc, Ctrl-C, or terminal loss.

Primary keys:

- `j/k` or arrows: move through runs or sessions;
- Enter: inspect selected item;
- `d`: toggle measured details;
- `i`: integrations/install view;
- `r`: refresh;
- `q`: quit.

Do not add interaction without a visible key hint. Restore raw mode, cursor, and screen state on every exit path and panic boundary.

## Installer contract

The curl bootstrap remains line-oriented POSIX shell because the binary does not exist before download. It must never use a full-screen alternate-screen UI.

Immediate disclosure:

```text
Azdaja installer v0.1.5
Provider-free install. No model provider will be called.
Checking platform... macOS arm64 supported
Checking tools... jcode, claude, codex, opencode found
```

Detection language:

- `found` means executable detection;
- `integration present` means the managed files validate;
- never label a host directory or stale managed skill as the tool being installed;
- do not detect Gemini merely because `~/.gemini/skills/azdaja` exists.

Interactive selection:

```text
Select integrations

› [x] jcode      found · integration present
  [x] claude     found · integration present
  [x] codex      found · not integrated
  [ ] gemini     not found
  [x] opencode   found · integration present

↑/↓ or j/k move  Space toggle  a detected  n none  Enter install  q cancel
```

Before mutation, print the exact plan and destinations. Every long phase announces itself before work starts:

```text
Downloading azdaja v0.1.5...
Verifying SHA-256... ok
Staging files... ok
Writing command... ok
Writing jcode integration... ok
```

Non-TTY or explicit-target invocation uses durable lines only. `NO_COLOR` and `TERM=dumb` disable decoration. Errors name the failed stage, rollback result, occupied path, and exact repair command.

After standalone installation, `az install` may use the shared Ratatui component system for richer integration selection. The bootstrap itself must stay robust and inspectable.

## Anti-metrics and anti-patterns

Do not show:

- an unlabeled entropy or intelligence score;
- semantic coverage inferred from lexical selection;
- confidence inferred from token usage, latency, or entropy;
- a force-directed terminal hairball;
- fake pressure derived only from session count;
- fake source exposure derived only from total prompt size;
- a clean success badge after a recovered retry without showing degraded transport;
- raw source excerpts, rare strings, paths, hashes, or trace responses on the overview;
- spinners or cursor rewrites in non-TTY logs;
- color-only state;
- `installed` when the code only detected a tool or directory;
- silent download, verification, lock wait, staging, or rollback phases.

## Implementation order

1. Fix managed-skill activation wording and host/integration detection semantics.
2. Add a privacy-safe persistent run-summary schema containing aggregates only.
3. Instrument source statistics, prompt boundary, exact provenance, attempts, usage, and timings.
4. Build the Ratatui console from that schema with a narrow static fallback.
5. Rework bootstrap copy and progress while preserving the current atomic lifecycle.
6. Add the richer installed-binary integration selector.
7. Update dependency legal notices, package allowlists, docs, TTY tests, and release validation.
