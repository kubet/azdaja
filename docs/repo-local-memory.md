# Repo-local project memory

## Current behavior

Inside a Git worktree, leaving both `AZDAJA_PROJECT_MEMORY` and `AZDAJA_HOME` unset selects the repo-local `.azdaja` store. The directory is created only when memory is explicitly added. The repository-local `.azdaja/.gitignore` contains `*`, so ordinary Git staging ignores its contents.

`AZDAJA_PROJECT_MEMORY` has three values:

- `on` forces project mode and errors outside a Git worktree.
- `off` refuses non-global memory operations without writing anything.
- `legacy` retains the previous cwd-scoped personal store.

When the switch is unset, an explicit `AZDAJA_HOME` retains legacy authoritative-root behavior. Explicit `on` takes precedence for project operations. `--global` always selects the personal-global store independently. Outside Git, the default retains the old scoped behavior. Same-repository subdirectories, `HOME` changes, and relocation preserve notes. Legacy storage displays a directory notice explaining that legacy access is explicit and that stores are not merged or migrated.

On Unix, newly created memory directories use mode `0700`; existing directories must belong to the current user and have no group or world permission bits. On Windows, directories inherit ACLs and reparse points are refused. This does not establish Windows ACL confidentiality.

## What memory does not do

There is no automatic harvesting, synchronization, Git publication, extraction, embedding, compression, majority voting, automatic file-rename tracking, or provider call. File associations are initially convention-based ordinary tags, for example:

```text
--tag file:src/cache.rs
```

They are not validated file anchors, and existing tag limits still apply.

Memory records should capture explicit decisions, hypotheses, and failures, with links using `supports`, `supersedes`, `derived-from`, or `related-to`. Recall includes bounded one-hop linked context even when that context does not match the query. Omission counts are explicit; not every contrary note is guaranteed to fit.

Storage and recall are bounded: at most 256 records and 512 KiB are stored; recall returns up to 4 primary and 8 contextual records, subject to a 64 KiB recall budget, with omissions possible.

## Research context

A-MEM motivates atomic notes, contextual metadata, links, and evolving organization, but its experiments are on long-term dialogue benchmarks rather than coding agents and do not prove coding benefit: <https://arxiv.org/html/2502.12110v11>.

LongMemEval motivates evaluating extraction, multi-session reasoning, knowledge updates, temporal reasoning, and abstention. It also shows that retrieval recall alone does not guarantee correct downstream answers, motivating end-to-end correctness scoring: <https://arxiv.org/html/2410.10813v2>.

These papers motivate design choices only. They do not establish adoption or improved coding accuracy. An exploratory Luna comparison did not establish a correctness or productivity gain: both arms completed one regression task, while neither completed the second within its deadline. Workflow blocks, concurrent repository changes and unsettled tool-action accounting limit interpretation. CLI latency has not yet been measured.

## Local validation

The examples below use a locally built, unreleased binary. Build it with:

```bash
cargo +1.95.0 build --locked --release --bin azdaja
./target/release/azdaja memory add hypothesis "Check whether cache keys include locale before changing caching." --tag file:src/cache.rs
./target/release/azdaja memory recall "cache locale"
```

The note and file tag above are illustrative, not a claim about this repository. Notes are shared within this worktree, not automatically between clones or machines. Review a note against current source before relying on it.

Fifteen project-memory CLI tests passed. The complete optimized all-target project suite, formatting, strict native Clippy, and three foreign-target compile checks also passed locally. This is not publication or foreign-platform runtime proof. The [acceptance evidence map](project-memory-evidence.md) connects requirements to checks in [`tests/project_memory.rs`](../tests/project_memory.rs).
