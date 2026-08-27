# Azdaja launch package

Prepared copy and operator checklist. Nothing in this file authorizes posting, emailing, submitting forms, requesting votes, or running paid benchmark inference.

## Show HN

### Title

```text
Show HN: Azdaja – LLMs analyze 50 MiB inputs via a local Python sandbox (Rust)
```

The title leads with the independently reproducible product contract. It contains no benchmark score and no unmeasured adjective.

### First comment

```text
Azdaja is a Rust CLI that keeps a complete UTF-8 input in a persistent local Monty/Python evaluator while the model works through bounded prompts, computed projections, and explicit semantic subcalls.

The release acceptance test runs three exact 52,428,800-byte inputs, one root turn each, zero child calls, and a root prompt below 65,536 bytes. Repro and receipt: https://github.com/kubet/azdaja/blob/main/BENCHMARKS.md

Honest limitation: this is not information-flow control. Model-authored code can select source material for a provider call, and evaluator memory has no configured ceiling. Use sanitized inputs or a separately trusted inference broker for stronger containment.

Release: https://github.com/kubet/azdaja/releases/tag/v0.1.14
Install: curl -fsSL https://azdaja.dev/install | sh
Cargo alternative: cargo install --git https://github.com/kubet/azdaja.git --tag v0.1.14 --locked

I will stay around to answer questions, reproduce failures, and correct anything the receipts do not support.
```

### Launch checklist

- Post on a Tuesday or Wednesday between 13:00 and 18:00 UTC.
- Confirm the release, installer, GIF, receipt links, and `BENCHMARKS.md` resolve from a signed-out browser.
- Re-run `release/verify-published-release.sh 0.1.14` immediately before posting.
- Keep the first comment ready before submitting the story.
- Stay available for at least 12 hours.
- Concede valid critiques quickly and add corrections to the repository.
- Never ask for votes or coordinate voting.
- Do not introduce an unmeasured benchmark score during discussion.

## Objection sheet

### “This is one single-arm benchmark.”

Correct. The 68.64% fixed-199 result is explicitly a private, validation-derived, single-arm diagnostic. The product claim is the provider-free 50 MiB acceptance contract. The benchmark artifacts are published for audit and replication, not as a superiority claim.

### “Why `curl | sh`?”

It is the shortest path, not the only path. The installer publishes named download, checksum, staging, and write phases and never calls a provider. A Cargo command and manually checksummed standalone binaries are documented beside it.

### “Is this just RAG?”

No. The complete source remains in one persistent evaluator. Deterministic code performs exact parsing and reduction, and the model can request semantic work over selected complete records. The system fails closed on missing authoritative-record coverage rather than silently sampling its way to an answer.

### “Why not use a 1M-token context window?”

The 50 MiB acceptance input does not fit in a 1M-token window. The durable claim is not a provider price comparison. It is that the root prompt remains below 65,536 bytes while the full source stays locally available to the evaluator.

### “Monty is experimental.”

Yes. It is snapshot-format-bound, evaluator memory has no configured ceiling, and snapshots are owner-only but unencrypted. Azdaja chooses a deliberately small fail-closed evaluator surface and documents that tradeoff.

### “Can the model leak source text?”

A selected provider call can expose selected source material. The bounded prompt is not an information-flow sandbox. Stronger containment requires a separately trusted inference broker.

### “Why should I trust the numbers?”

Every public number links to a frozen receipt or an exact provider-free acceptance test. `BENCHMARKS.md` lists scope, hashes, failures, source pins, and reproduction commands. Frozen validators intentionally block when bound source changes.

## Secondary channels

Do not cross-post identical copy. Each community gets its own framing and its rules must be read in-app immediately before posting.

### Lobsters

- Use the `show` tag.
- Lead with implementation and evaluation tradeoffs, not growth language.
- Do not post until account and self-promotion requirements are satisfied.

### r/LocalLLaMA

- Methodology angle: complete-source evaluator, fixed root prompt, receipts, and failure boundaries.
- Verify the current subreddit rules in-app before drafting final copy.
- Do not imply local inference. The measured default route used subscription OAuth to a frontier model.

### r/ClaudeAI

- Workflow angle: Claude integration, skill activation, large-file analysis, and explicit safety boundaries.
- Verify the current subreddit rules in-app before drafting final copy.

### Console.dev

- Prepare a short beta note around the v0.1.14 release and reproducible 50 MiB contract.
- Sending email requires a separate explicit authorization.

## Evidence links

- [Receipts leaderboard](../BENCHMARKS.md)
- [Release v0.1.14](https://github.com/kubet/azdaja/releases/tag/v0.1.14)
- [50 MiB acceptance test](../tests/product_50mb.rs)
- [50 MiB acceptance receipt](../bench/results/v0.1.2-product-acceptance-public.json)
- [Launch saga](launch-saga.md)
- [Installer lifecycle documentation](install.md)
