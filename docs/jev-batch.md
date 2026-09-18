# Checkpointed semantic batches

Development-source feature. From the repository root:

```sh
cargo build --locked --release --features typesafe
AZ="$PWD/target/release/azdaja"
```

The commands below use this build, not a potentially older installed `az` alias.

Use this when a long task has an explicit set of independent semantic questions: reviewing many documents, finding candidate passages, labeling records, or extracting choices from supplied alternatives. **The native runner executes the work list directly.** It does not depend on a planner deciding to use Jev or generating a correct finalization program.

The result is a source-linked review artifact, not an automatic approval. Full distributions are retained. A confident answer can still be wrong.

## Start with real files

The optional standard-library example makes a work list without a model call:

```sh
python3 examples/jev_batch_review.py prepare \
  --question 'Does this window describe an unresolved security incident?' \
  --output ./review-plan \
  ./incident-archive.txt ./handoff-notes.txt

# Checks the entire plan. No credentials, provider calls, or job directory.
"$AZ" jev batch --input ./review-plan/plan.jsonl
```

Select files you are authorized to send. `prepare` preserves exact UTF-8 source windows, hashes and byte offsets. It does not create embeddings, ingest agent memory, silently follow an entire repository, or claim that a window contains all relevant context. Cross-window qualifications and cross-document reasoning need further inspection.

## Explicit execution

Enable the existing native transport in a host-selected `AZDAJA_CONFIG` file:

```toml
[judge]
enabled = true
model = "jev-latest"
```

Supply `TYPESAFE_API_KEY` through your normal secret mechanism or the existing `az jev attach --stdin` flow. Never put the key in the plan or command arguments.

```sh
"$AZ" jev batch --input ./review-plan/plan.jsonl \
  --execute --output ./review-job \
  --max-requests 256 --max-input-tokens 2000000 --max-seconds 600
```

All three job limits must be explicit. Existing per-request byte, question and transport-time limits also apply. Default execution is sequential. No alternate provider, generative fallback or automatic paid retry is used. Progress is emitted on stderr and the final machine-readable summary on stdout.

Each validated result is saved before the next request. These immutable per-request files remain available if a later request fails. Stored observations are validated native response JSON, not the original HTTP wire bytes. Finalization is ordinary native code, with no extra model request or generated hash expression.

## Export a review file

```sh
python3 examples/jev_batch_review.py report \
  --plan ./review-plan --job ./review-job --output ./review.jsonl
```

Every prepared window is represented, with its source name, SHA-256, byte offsets,
verbatim text and raw answer. Failed or unfinished requests remain explicit unknowns.
The exporter verifies native request hashes and reconstructs every source hash before
writing. It does not discard low scores or convert a probability into an approval.
Existing output files are refused.

## Resume without repeating completed work

Use the **same plan, configuration and limits**:

```sh
"$AZ" jev batch --input ./review-plan/plan.jsonl \
  --execute --resume --output ./review-job \
  --max-requests 256 --max-input-tokens 2000000 --max-seconds 600
```

Completed records are validated and reused. Completed-job replay needs no credential and sends no requests. Untouched records may run only while the original limits allow it. The original wall deadline includes downtime and cannot be extended by restarting.

Before a request can leave the process, the runner durably records its intent. If the process is killed between that intent and durable completion, billing and completion may be unknown. Resume refuses to retry that request automatically. A new explicit job can repeat work, so creating a new directory is **not** a way to promise zero duplicate billing.

Provider failures and unknown input usage stop further admission. Reported-token limits cannot undo a response already billed. Known output usage and unknown counters remain visible. Token usage is not an invoice.

## Work-list format

One JSON object per line:

```json
{"id":"contract-07/section-12","state":{"source":"contract-07","text":"Neither party may assign this agreement without consent."},"questions":{"assignment_consent":{"type":"noul","instructions":"Does the supplied text require consent to assign this agreement?"}}}
```

IDs must be unique. Each row uses the existing `state` and `questions` contract from [typed judgments](typed-judgments.md), including `noul`, `choice` and `score`. Put complete question meaning in `instructions`, not just in question IDs. Keep source identity, exact text and relevant context in the supplied state. No threshold or semantic interpretation is imposed by the batch runner.

The whole input is validated before any request. Plans are bounded to 64 MiB and 10,000 records rather than silently truncated. This is a local, single-user job directory, not a secure multi-tenant queue. On supported private-storage platforms, job directories and files use owner-only permissions. Unsafe modes, links and simultaneous writers are refused, not silently repaired. Protect the input and result files as you would the original source.

## What this changes, and what it does not

- A selected long-job work list actually runs through the typed engine.
- Completed work becomes durable, usable output immediately.
- Restart does not re-request completed observations.
- Native finalization cannot fail because a model invented a Python hash API.
- This does **not** prove better model accuracy, calibrated confidence, a speedup over a matched workflow, or reliable automatic planning. The earlier failed CUAD planner runs remain failed. A source review queue still requires review.
