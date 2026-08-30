# Show HN launch runbook for Azdaja v0.1.14

Status: prepared only. This file does not authorize submitting a story, posting a comment, replying, requesting votes, or coordinating engagement.

## Launch window

Target: Tuesday, 2026-09-01 at 15:30 UTC. The operator may move the time rather than post into an outage, broken install path, red exact-head CI, or an unavailable response window.

## Positioning boundary

The human-written submission should explain this architectural inversion:

- Azdaja is a local recursive evaluation layer implemented as an open-source Rust CLI.
- Complete input stays in a local Monty/Python evaluator.
- The model receives a bounded interface and can make explicit recursive subcalls.
- The product contract is local source custody, bounded root exposure, typed results, explicit semantic work, and fail-closed record coverage.
- The launch is about the interface boundary and its evidence, not a speed, cost, benchmark-superiority, or unlimited-context claim.

Do not use `harness-agnostic`, `infinite context`, `persistent memory`, `faster`, `cheaper`, `works with any model`, `production-proven`, or `benchmark-winning` unless new public evidence supports the exact phrase.

## Human-only drafting boundary

The operator writes the final HN title, first comment, and every reply in their own words immediately before use. Agents may verify facts, links, spelling, and claim boundaries, but must not generate text that is pasted into an HN comment as if it were the operator's voice.

The first comment should cover, in this order:

1. The concrete problem that motivated the project.
2. The evaluator/model boundary in plain language.
3. One install or reproduction path.
4. One honest limitation.
5. One narrow technical question for HN readers.

## T-24 hours

- [ ] Confirm the operator can remain available for at least 12 hours after submission.
- [ ] Confirm no other general launch post is scheduled within seven days.
- [ ] Read the current Show HN and HN guidelines from their primary pages.
- [ ] Verify the repository description, homepage, README, release, and first-run path tell the same bounded story.
- [ ] Verify no private outreach notes, targeting data, approval packets, host paths, or credentials appear in Git or public assets.

## T-30 minutes: proof gate

- [ ] Exact-head CI and current source/install integrity are terminal-success.
- [ ] `release/verify-published-release.sh 0.1.14` passes.
- [ ] A signed-out browser can open the homepage, README, release, checksums, provenance, saga, and scorer postmortem.
- [ ] A clean environment can complete one documented installation path.
- [ ] The release tag still resolves to the reviewed immutable v0.1.14 identity.
- [ ] Homepage canonical, social metadata, SoftwareApplication JSON-LD, robots policy, and sitemap are valid.
- [ ] The operator has independently written the title and first comment.

Abort the launch if any box fails. Repair the product or evidence rather than weakening the gate.

## Public proof links

- Homepage: https://azdaja.dev/
- Source: https://github.com/kubet/azdaja
- Release: https://github.com/kubet/azdaja/releases/tag/v0.1.14
- Receipts: https://github.com/kubet/azdaja/blob/v0.1.14/BENCHMARKS.md
- Launch saga: https://azdaja.dev/saga.html
- Scorer postmortem: https://azdaja.dev/op-4.html

## T+0 to T+6 hours

- Stay present and answer the technical question actually asked.
- Acknowledge valid limitations before explaining tradeoffs.
- Link one primary receipt rather than pasting a wall of evidence.
- Correct factual errors publicly and repair the canonical source.
- Do not argue about points, ranking, flags, or moderation.
- Never ask for votes, comments, reposts, or coordinated engagement.
- Do not use generated replies. If a response needs research, pause and return with a human-written answer.

## Diagnosis without gaming

- If the submission has no discussion, improve the product explanation later. Do not delete and repost.
- If readers click but do not install, repair onboarding before seeking another audience.
- If installs start but runs do not finish, repair the first-run path and prerequisites.
- If discussion centers on an unsupported claim, correct the claim and stop amplification.
- If a correctness or privacy defect appears, pause all visibility work until it is fixed and verified.

## Seven-day success metric

Count qualified outcomes, not impressions or votes:

- a completed independent installation and run,
- a substantive technical comment or correction,
- an article-attributed issue or discussion,
- an independent reproduction attempt,
- or a concrete integration question.

At day seven, choose exactly one next action: repair onboarding, deepen the strongest technical conversation, prepare one channel-specific follow-up, or pause for product work. Do not cross-post merely because the HN score was low.
