# Show HN launch package for Azdaja v0.1.13

Status: prepared only. Do not post or solicit votes without an explicit owner go-ahead.

## Title

Show HN: Azdaja - A local evaluator for language-model context

## First comment

Azdaja gives a language model a bounded Python evaluator over the complete local input instead of placing the whole input in the root prompt. The evaluator retains the UTF-8 source locally, limits what reaches the model, records aggregate observability, and fails closed when its contracts are not satisfied.

The product contract is intentionally direct: the complete source stays in a local evaluator, the model-facing root surface stays bounded, semantic subcalls are explicit, and record-aware runs either produce complete receipts or fail closed. Reproduction commands and receipts: https://github.com/kubet/azdaja/blob/v0.1.13/BENCHMARKS.md

An honest limitation: Azdaja changes the execution and context surface, not model quality. Semantic tasks can still be answered incorrectly, and fail-closed gates can convert a bad strategy into a refusal or timeout. v0.1.13 publishes standalone binaries for Apple Silicon macOS, Intel macOS, and x86_64 Linux. Windows is validated in CI but is not one of this release's public standalone payloads.

Install alternatives and checksums are in the README. Release: https://github.com/kubet/azdaja/releases/tag/v0.1.13

I would especially value attempts to break the receipt boundaries, find semantic work that passes without evidence, or show a simpler design with the same fail-closed properties.

## Objection sheet

### "The benchmark is single-arm or cherry-picked"

Agree that the retained fixed-199 diagnostic is not an official leaderboard result, paired comparison, or superiority claim. Do not use it as the launch headline. The public headline is the bounded local evaluator and its fail-closed record contract. Invite independent benchmark replication and link the exact receipts.

### "curl | sh is unsafe"

Agree that it is not everyone's preferred install path. Lead with the checksummed release assets and show Cargo as an alternative. Never pressure users to use the shell installer.

### "This is just RAG"

Azdaja does not claim to replace retrieval. Its product claim is a bounded local evaluator over the retained complete source, with explicit prompt, execution, receipt, and failure contracts. Retrieval can be one strategy inside a larger workflow, but it is not the whole contract.

### "Why not use a long context window?"

Azdaja is for workflows that need local source custody, deterministic reduction, explicit semantic calls, and record-level receipts. It is not a claim that every task should avoid direct context.

### "The sandbox is restrictive"

Yes. The restrictions are deliberate. The product chooses bounded, auditable, fail-closed behavior over arbitrary host access. Ask for concrete missing capabilities and evaluate them against that boundary.

### "Why Monty or Python at all?"

The local evaluator gives model-written analysis a constrained execution surface. The implementation trade is explicit: useful computation without granting arbitrary shell or filesystem access. The right criticism is whether the boundary is strong and usable, which is why the receipts and refusal tests are public.

## Launch discipline

- Post only after checking the live Show HN submission rules and title rendering.
- Preferred window from the retained research: Tuesday or Wednesday, 13:00-18:00 UTC.
- Stay available for at least 12 hours.
- Concede valid criticism quickly and correct public mistakes in the repository.
- Never ask for votes or coordinate voting.
- Do not quote an unmeasured successor benchmark score.
- Check each Reddit community's current in-app rules before any separate post. Rewrite per community instead of cross-posting identical copy.

## Live preflight

- [ ] Release URL and all six assets return successfully.
- [ ] `release/verify-published-release.sh 0.1.13` passes.
- [ ] README demo image loads from public `main`.
- [ ] Reproduction links point to immutable `v0.1.13` paths.
- [ ] First comment contains one honest limitation.
- [ ] No benchmark superiority claim appears in the title or first comment.
- [ ] Owner explicitly approves posting.
