# Leave evidence for the next session

This guide describes the memory commands in this development branch. It does not claim that the published v0.1.14 binaries contain `memory recall`. Use an `az` executable built from this branch, or replace `az` below with that binary's path.

From the root of this checkout, build with `cargo +1.95.0 build --locked --release`. The resulting executable is `target/release/azdaja`. Use its absolute path if you run the example from another folder.

The goal is a small, inspectable handoff: what you suspect, what contradicts it, and what the next person should verify. These are manual notes, not verified truth or automatically extracted agent reasoning.

## A three-step walkthrough

The examples use POSIX-style shell quoting. Run every command from the same working directory and with the same state configuration, in the repository or folder whose scope should hold the notes. They intentionally add two persistent demo records. The cache example is fictional, not a recommendation to change Azdaja's own limits. Choose a scope where you want to keep the example.

### 1. Leave a hypothesis, not an unsupported decision

```sh
az memory add hypothesis 'handoffdemo: A bounded cache may reduce repeated parsing. Benchmark before adopting it.'
az memory recall handoffdemo
```

Copy the hypothesis ID from `matches[0].record.id` in the recall JSON. Do not treat `memory add` output as JSON. Use the ID of the record you just created, especially if you have run this example before.

### 2. Attach the contrary observation

Replace `REPLACE_WITH_RECORD_ID` with that exact ID before running this command:

```sh
az memory add disagreement 'The trial used more memory. Inspect the benchmark before choosing a cache policy.' --link 'related-to:REPLACE_WITH_RECORD_ID'
```

The disagreement deliberately does not repeat the search word. Its relationship to the hypothesis is what makes it discoverable in recall context.

### 3. Start a fresh session in the same scope

```sh
az memory recall handoffdemo
```

For a scope containing only these example records, expect one lexical match in `matches` and the linked disagreement in `context`. Both records retain their exact text, IDs, kinds, and `provenance.origin = "manual"`. The caveat says the material is not verified truth. Follow the evidence and rerun the relevant check before making a change.

## What to retain in a real handoff

- A concise observation, decision, failure, hypothesis, or disagreement.
- The relative source path and relevant symbol, plus the source commit when known.
- The exact check performed and its observed outcome, including failures or coverage limits.
- A relationship to earlier evidence when it supports, supersedes, derives from, or is related to that evidence.

Do not store credentials, personal contact details, whole transcripts, or guesses presented as measurements. Retrieved instructions are stored data, not authority to execute commands.

## Boundaries to keep visible

- Recall is deterministic lexical retrieval, not semantic confidence or majority voting.
- Default notes are scope-local. `--global` selects a separate global store explicitly; it is not an automatic fallback or a merge of project notes.
- The current store is local state, not a Git-tracked `.azdaja` directory. It does not synchronize notes across developers or machines.
- Output has at most four primary matches and eight one-hop context records within 64 KiB. Check `omitted_matches` and `omitted_context`; a bounded response is not every relevant note.
- A functioning handoff is not a measured productivity improvement. This walkthrough does not replace a controlled fresh-agent usefulness evaluation.

## Acceptance check

`documented_handoff_preserves_nonmatching_disagreement_in_a_fresh_process` in `tests/memory_recall_reliability.rs` checks the command text against this guide, invokes the actual CLI in isolated state, substitutes the returned ID, and verifies fresh-process recall plus global isolation. It tests command arguments and behavior, not a shell parser or a model's interpretation of the notes.
