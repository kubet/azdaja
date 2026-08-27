# Agent memory and uncertainty research

Status: the first product slice is implemented, with the v0.1.14 scope clarified below. This note records what the evidence supports, what it does not support, and how the implementation is tested.

## Executive decision

Azdaja should add **inspectable, scope-first evidence records**, not a generic second brain, graph UI, vector store, automatic reflection loop, or uncalibrated confidence score.

The shipped slice is `az memory`:

- user-authored JSONL records under the owner-only state root;
- typed kinds: `decision`, `observation`, `failure`, `hypothesis`, and `disagreement`;
- bounded tags and explicit `supports`, `supersedes`, `derived-from`, and `related-to` links;
- manual provenance and backlinks on `show`;
- `az memory list --kind disagreement`, with the fixed caveat that entries are manually recorded local records, not independent agent disagreement receipts;
- current canonical working-directory scope by default;
- a separate `--global` ledger only when explicitly requested;
- append-only logical history capped at 256 records and 512 KiB per ledger;
- no automatic prompt injection, model-authored memory, cross-project merge, semantic ranking, calibrated confidence, automatic wisdom-of-agents, or automatic memory retrieval/injection.

This is deliberately smaller than an Obsidian vault. The value being tested is inspectability, custody, provenance, and deterministic scope. No claim is made that links or atomic records universally improve reasoning.

## Current v0.1.14 capability boundary

Implemented: a manual, bounded, local memory ledger; `az memory list --kind disagreement` for manually recorded local disagreement records; and exact byte entropy only.

Explicitly not implemented: automatic wisdom-of-agents, independent agent disagreement receipts, semantic entropy, calibrated confidence, or automatic memory retrieval/injection. The research references below are design constraints, not claims that Azdaja now performs collective intelligence, semantic uncertainty estimation, or long-term autonomous memory management.

## Evidence and limits

| Source | What it supports | What it does not prove | Azdaja decision |
| --- | --- | --- | --- |
| [Kleppmann et al., Local-first software, Onward! 2019](https://doi.org/10.1145/3359591.3359737) | Local custody, offline access, privacy, preservation, and user ownership are useful design principles. | Local-first is not a controlled proof of better productivity or correctness. | Keep owner-readable local files and no required service. |
| [W3C PROV overview](https://www.w3.org/TR/prov-overview/) and [PROV-DM](https://www.w3.org/TR/prov-dm/) | Provenance describes entities, activities, agents, and derivations so evidence can be assessed. | Provenance metadata alone does not make a claim true. | Keep explicit `manual` provenance and typed links. |
| [Obsidian internal links](https://help.obsidian.md/Linking+notes+and+files/Internal+links), [backlinks](https://help.obsidian.md/Plugins/Backlinks), and [properties](https://help.obsidian.md/Editing+and+formatting/Properties) | Plain local files, typed properties, explicit links, and incoming-link inspection are useful interaction patterns. | Graph view or backlinks are not evidence of semantic relevance or causal productivity gain. | Keep typed records and backlinks. Defer graph visualization and graph-distance retrieval. |
| [Packer et al., MemGPT](https://arxiv.org/abs/2310.08560) | Bounded working memory plus slower external memory is a useful systems metaphor for long contexts. | Paging memory into a prompt does not establish privacy, correctness, or useful retrieval for every task. | Keep an external ledger, but do not inject it automatically. |
| [Park et al., Generative Agents](https://arxiv.org/abs/2304.03442) | Observation, planning, reflection, and retrieval contributed in a simulated social-world task. | Its ablations do not justify automatic reflection in a developer tool. | Do not add automatic reflection in this slice. |
| [Liu et al., Lost in the Middle](https://arxiv.org/abs/2307.03172) | Relevant evidence can be missed when buried in long contexts, even with long-context models. | The result varies by model, task, and placement. | Deterministically scope and bound records before any future retrieval. |
| [Kuhn, Gal, Farquhar, Semantic Uncertainty](https://arxiv.org/abs/2302.09664) and [Farquhar et al., Nature 2024](https://www.nature.com/articles/s41586-024-07421-0) | Semantic uncertainty needs repeated answers and equivalence classes over meanings; it can help detect some confabulations. | Low semantic entropy can still be a shared systematic error, and byte entropy is unrelated to model correctness. | Keep byte entropy labeled as source distribution only. Do not emit confidence from it. |
| [Wang et al., Self-Consistency](https://arxiv.org/abs/2203.11171) | Diverse sampled reasoning paths and answer aggregation can improve some reasoning benchmarks. | Majority agreement can be confidently wrong and is not calibrated by itself. | Preserve a `disagreement` record as evidence, never collapse it into quality. |
| [Huang et al., Mirror-Consistency](https://aclanthology.org/2024.findings-emnlp.135/) | Minority inconsistency can carry uncertainty information and can help calibration in studied settings. | The method is not a universal confidence guarantee and needs repeated model samples. | Keep minority views representable, but require explicit human-authored records. |
| [Bahuguna, When Self-Consistency Backfires](https://arxiv.org/abs/2608.11403) | Recent evidence reports majority-vote and token-entropy gates failing on a hard-science setting for small models. | It is one model/task study and not a universal negative theorem. | Never make agreement or token/byte entropy an unconditional acceptance gate. |

## Entropy taxonomy

Azdaja currently computes exact **zero-order byte entropy** for locally loaded UTF-8 source:

```text
H_byte = -sum(p_b * log2(p_b)), b in 0..255
```

That is a descriptive histogram in bits per byte. It is not:

- token predictive entropy;
- semantic entropy over meaning classes;
- answer correctness probability;
- calibration;
- semantic diversity or relevance;
- compression ratio.

A useful future uncertainty receipt would need repeated model outputs, a declared equivalence procedure, a sample denominator, and an evaluation set with labels. Until those exist, Azdaja should show disagreement or missing evidence as a reason to review or abstain, not as a numeric quality headline.

## Ledger contract

`az memory add` is explicit because silent memory writes are hard to audit and can poison future context. Records are not automatically fed to `solo`, `exec`, or provider prompts. The file is JSONL so an owner can inspect, copy, diff, or archive it without a proprietary database.

The default path is a hash-derived filename under `memory/scopes`. The canonical path is used to select the ledger but is never serialized into a record. `--global` uses a separate `memory/global.jsonl`; it does not merge all project ledgers.

Writes use the existing private directory, private file, lock, and atomic replacement primitives. Reads reject malformed JSONL, unknown schema, duplicate IDs, missing link targets, oversized ledgers, symlinks, and unsafe files. The logical history is append-only even though the bounded rewrite is atomic. When the bound is reached, the command refuses rather than silently deleting evidence.

## Acceptance map

- Scope isolation and path-free records: `tests/cli_ux.rs::memory_cli_is_scope_first_linked_and_global_only_when_explicit`, `src/memory.rs::scope_ledgers_are_isolated_and_show_backlinks`.
- Links and backlinks: the same CLI test plus the memory unit test, including a `disagreement` record.
- Corruption and symlink fail-closed behavior: `src/memory.rs::corrupt_and_unsafe_ledgers_fail_closed`.
- Concurrent writers and the 256-record bound: `src/memory.rs::large_concurrent_append_stress_stops_at_the_256_record_bound` with 300 concurrent writers.
- Public help and invalid usage through both binary names: `tests/cli_ux.rs` and `tests/e2e.rs::command_help_usage_and_bare_text_are_identical_through_both_names`.
- Whole-result compatibility: the optimized 119-test E2E suite, the 142-test library suite, the dashboard/TUI suite, installer/distribution tests, clippy, packaging, and release-asset checks.

The next research step, if needed, is not “add a graph.” It is a representative labeled task that compares deterministic scope-first retrieval against broader retrieval and measures correctness, leakage, latency, and memory poisoning. Without that task, automatic retrieval remains intentionally out of scope.
