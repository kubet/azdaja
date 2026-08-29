# Visibility operations

Agent-executable operations for Azdaja visibility. Prepared procedures, drafted copy, and tested commands. **Nothing in this file authorizes posting, replying, emailing, submitting forms, requesting votes, or running paid model inference.** Every externally visible action requires a separate explicit operator go, mirrors `docs/launch-package.md`, and must re-check the venue's current rules immediately before acting. Every public number used in any copy below must link the receipt that supports it (`BENCHMARKS.md` update policy).

## Evidence base

Why these five operations and not a broader channel checklist — measured, sources in the session research record:

- A Hacker News front-page day yields a mean of **121 stars in 24 h / 289 in a week** across 138 AI-tool launches ([arXiv:2511.04453](https://arxiv.org/abs/2511.04453)); of ten 200+ point Show HN AI tools spot-checked, **five never reached 2,000 stars**. HN is ignition, not an engine, and the operator runs HN manually.
- In ten verified 0→2k cases (2025–26), the dominant primary drivers were **wave-riding with one falsifiable headline number** (4/10) and HN/demo (3/10); directory listing was primary exactly once. Every multi-thousand-star comparable had **≥3 distinct attention waves, and the biggest was never the first**.
- The closest comparable (`alexzhang13/rlm`, 5.5k stars) crossed 2k only after **a funded lab amplified the idea** (paper + Prime Intellect blog + 161-pt HN inside one week). The null comparable (LOTUS: strong paper, no launch mechanics) plateaued under 2k for two years.
- The durable channel is a **citable recurring benchmark**: aider's leaderboard is linked by 2,300+ files on GitHub. Azdaja's equivalent surface is `BENCHMARKS.md`.

Consequence: agent effort goes to (1) amplifiers, (2) the recurring receipt, (3) precise conversation surfacing, (4) deep content, (5) launch-day support. Directory work is complete or gated in `docs/listings.md` and is not repeated here.

---

## OP-1 · Amplifier outreach

**Goal:** one technical acknowledgment (reply, citation, repost, or issue comment) from a person who owns the RLM/long-context conversation. This is the highest-expected-value operation in this file.

**Targets, hooks, and verified routes:** see the routes table at the end of this section. The hook is always the same shape: *Azdaja is a production, fail-closed implementation of the idea this person owns, measured under a protocol they know, with hash-bound receipts they can audit or attack.*


**Guardrails:** claims must match `BENCHMARKS.md` verbatim framing ("private, single-arm, validation-derived"); never imply endorsement afterward without written permission; if a target publishes criticism, the response is a repository correction, not a rebuttal thread.

**Acceptance:** five notes sent by the operator; each logged below with date and route; any reply answered within 24 h with evidence, not marketing.


<!-- ROUTES:BEGIN -->

| Target | Verified route(s) | Priority + note |
|---|---|---|
| **Oolong authors** (Bertsch et al., the benchmark Azdaja is measured on) | Leaderboard site <https://oolongbench.github.io/> Contact section carries a standing invitation — "Have a model you'd like us to evaluate? Reach out" — with the contact email printed there; repo <https://github.com/abertsch72/oolong> has issues enabled, results-submission issue appropriate | **1st** — the only target with an explicit standing invitation, and the deliverable is results, not a pitch |
| **Alex L. Zhang** (RLM paper first author) | Bio at <https://alexzhang13.github.io> explicitly invites email ("reach out to talk about anything"), address printed obfuscated in the bio; X `@a1zhang`; author emails also on page 1 of <https://arxiv.org/pdf/2512.24601> | **2nd** — a direct implementation of his paper; a warm reply compounds every other channel |
| **Latent Space / swyx** | Published pitch route `tips@latent.space` (<https://www.latent.space/about>; do not use the sponsorship address); ~1 month lead-time guidance; secondary: LLM Paper Club (lu.ma/llm-paper-club) — the RLM paper is exactly their material | **3rd** — purpose-built pitch route, widest payoff if it lands |
| **RAH authors** (Lumer, Sen, Paul, Subbiah — PwC) | Author emails printed under each name on page 1 of <https://arxiv.org/html/2606.13643v1> (Lumer corresponding; GitHub `EliasLumer`) | Their RAH code is announced but unreleased — an independent open implementation is citable validation and a natural comparison point when it ships |
| **Prime Intellect** | Discord `discord.gg/primeintellect` (site footer) — the right venue; the contact form at primeintellect.ai/contact is sales-qualified, don't use it; X `@PrimeIntellect` | Post in the community as a technical project, not a pitch |
| **Simon Willison** | No pitch route exists (verified: about page, link-blog post, contact tag). Most active on Mastodon `@simon@simonwillison.net` and Bluesky; a concise public @-mention with the runnable 50 MiB demo is the only defensible route | Pitch the reproducible demo, never the benchmark |
| **Andrej Karpathy** | X `@karpathy` only; no pitch policy | Public @-mention at most; expect nothing |

<!-- ROUTES:END -->

**Send log:** (append-only)

| Date | Target | Route | Sent by | Reply |
|---|---|---|---|---|

---

## OP-2 · Recurring receipt cycle

**Goal:** every major frontier-model release produces one new versioned receipt row in `BENCHMARKS.md` and one drafted post — the aider-style compounding surface. Historical rows stay immutable; corrections are additive (`BENCHMARKS.md` update policy).

**Release triggers (endpoints verified live 2026-08-28):**

```bash
# OpenAI news feed (RSS, HTTP 200 verified)
curl -s https://openai.com/news/rss.xml
# Anthropic model releases surface fastest through Claude Code releases
curl -s https://api.github.com/repos/anthropics/claude-code/releases/latest
# HN as a catch-all trigger for any lab's launch
curl -s 'https://hn.algolia.com/api/v1/search_by_date?query="context window"&tags=story&hitsPerPage=10'
```

**Procedure on trigger:**

1. Confirm the release is a frontier model reachable through an installed harness route (the measured route is subscription OAuth; no API keys — `bench/oolong/run.py` fails closed on key-shaped env vars).
2. Draft the run plan: which fixture (row-645 cheap diagnostic first, gold `Answer: 132`; row-651 hard, gold `Answer: 8638`), repetitions, timeout ≥1800 for the 1 MiB row. **Inference is spend and requires explicit operator authorization per run** — the runner's `--yes-run-inference` flag exists precisely for that.
3. Keep two artifact tiers separate. Rows 645 and 651 are **diagnostics**: label them as such and never turn a one-shot or three-repetition diagnostic into a headline or recurring receipt row. A **campaign** row requires the repository's pre-declared fixture, arms, gates, scoring, and ceremony before the first inference call.
4. After a terminal, validated campaign result: add a versioned receipt row to `BENCHMARKS.md` linking the JSONL artifact; never edit a historical row.
5. Draft (not post) the announcement: one sentence, the number, the receipt link, the limitation line. Queue in `docs/outreach/`.

**Known blocker (2026-08-28):** the row-645 gate validation runs recorded in `bench/results/gate-645.jsonl` and `gate-645-hardened.jsonl` are **0/6 correct** against gold `Answer: 132`. Base repetitions 1–2 exited after an `invalid_prompt` provider-policy refusal; base repetition 3 returned `Answer: 133`; hardened repetitions 1–2 returned `Answer: 131` and `Answer: 133`; hardened repetition 3 exited after a Jcode subscription-turn timeout. These are execution and strict-score observations, not one established root cause. Diagnose and fix forward before any new public row. No new receipt is publishable while the cheap diagnostic fails.

**Acceptance:** a model release is followed within ~72 h by either a new receipt row plus drafted post, or a logged decision not to run (with reason). The published row text itself must say whether it is a **diagnostic** or a **campaign** result.

---

## OP-3 · Conversation surfacing

**Goal:** ≤5 precisely chosen threads per week where Azdaja is a *genuine answer to a live problem*, each with a drafted evidence-bearing reply for the operator to review and post manually. This is monitoring plus drafting, never automated posting.

**Tooling:** `tools/visibility_sweep.py` (read-only, stdlib-only, tested end-to-end 2026-08-28 — the live run produced a 52-item queue). Writes `docs/outreach/queue-YYYY-MM-DD.md` and omits URLs already present in earlier queue files unless `--include-seen` is explicit.

```bash
python3 tools/visibility_sweep.py
```

**Verified query surface (hit counts at last test):** `anthropics/claude-code` open issues — 267 for `"context limit"`, 214 for `"large file" context`; `openai/codex` — 860 for `"context window"`; `google-gemini/gemini-cli` — 24; opencode moved to `anomalyco/opencode` (202k stars) and the sweep targets the new org. HN queries: `"context rot"`, `"recursive language model"`. Reddit has no reliable unauthenticated API surface from this environment — Reddit threads are found and read in-app only.

**Rules of engagement for a drafted reply:**

1. Answer the person's actual problem first; Azdaja appears only if it concretely solves it.
2. Disclose authorship in the same sentence that names the tool.
3. Link at most one URL, and only `BENCHMARKS.md` or an exact reproduction command.
4. Never draft for threads that are vendor bug reports with no workaround angle; never draft more than 5/week — the credibility budget is the scarce resource.
5. The operator reads the venue's self-promotion rules in-app immediately before posting. A drafted reply expires unposted after 7 days.

**Cadence:** weekly. A recurring agent session can run the sweep and the drafting; posting is always the operator.

**Acceptance:** queue file exists weekly; every posted reply logged in the queue file with a link; zero removed-by-moderator events (one removal pauses the operation for review).

---

## OP-4 · Content production

**OP-4 accepted-artifact:** `docs/outreach/op4-scorer-postmortem.md`; article SHA-256 `02d0c2426f4173c110b5d7708a494f8b41b5d7baad27404ffcbd6baeae91c9df`; acceptance report SHA-256 `d99b6f4bfa7342aadbaffb1d32686e831e558f24ef11b8662e04bc6a55308687`.

**Goal:** the three deep pieces behind the saga, written by an agent from frozen repository evidence, reviewed and published by the operator on `azdaja.dev` (saga page pattern: `site/saga.html`).

| Piece | Working title | Source material (all in-repo) | Target |
|---|---|---|---|
| Eval integrity | Five ways our own scorer tried to lie to us | `docs/launch-saga.md` scorer-kills section; `bench/results/` scorer receipts | ~1,800 words; the piece that earns citations from the post-benchmark-scandal audience |
| Failure autopsies | Completed but wrong: Answer: 0 against a gold of 5,815 | `AUTOPSY.md` rows 1, 2, 6 verbatim; the erratum as an honesty exhibit | ~1,500 words + one X-thread cut |
| Cost receipts | 5,400 root tokens against 9.9M characters | `bench/results/cost-evidence-public.json`; `bench/delta/README.md`; `docs/token-context-crossover.svg` | ~1,200 words; candidate to become the recurring OP-2 post format |

**Standards:** every number links its receipt; jargon gets defined on first use (the saga rewrite's cold-reader bar); no piece publishes while any of its claims lacks a receipt; drafts live in `docs/outreach/` until the operator moves them to `site/`.

**Acceptance:** an outside reader (not the author, not the agent) can retell each piece's core claim unaided.

---

## OP-5 · Launch-day copilot

**Goal:** during the operator's manual Show HN run, an agent session holds the thread state so the operator's 12-hour presence is sustainable.

**Procedure:**

1. Watch the thread: `https://hn.algolia.com/api/v1/items/<story-id>` (poll ≤ every 5 min).
2. Classify each new top-level comment against the objection sheet in `docs/launch-package.md`; for covered objections, draft the reply from the sheet; for novel technical questions, draft from repository evidence with file/receipt links; flag anything the sheet cannot answer honestly as "operator judgment".
3. The operator posts every reply personally. The agent never posts, never votes, never suggests vote coordination.
4. Valid critiques get same-day repository commits (correction, erratum, or issue) — link the commit in the reply draft.

**Acceptance:** median operator response latency under 20 minutes across the first 6 hours; every conceded critique has a repository artifact.

---

## Cadence summary

| Operation | Rhythm | Agent share | Operator share |
|---|---|---|---|
| OP-1 outreach | once, then per-reply | research, drafts, log | sends, relationship |
| OP-2 receipt cycle | per model release | trigger watch, run prep, receipt row, post draft | inference authorization, posting |
| OP-3 surfacing | weekly | sweep, shortlist, drafts | rule check, posting |
| OP-4 content | one piece per 1–2 weeks | full drafts from evidence | review, publish |
| OP-5 copilot | launch days | thread watch, classification, drafts | posting, judgment |

## Global guardrails

- No vote solicitation or coordination, anywhere, ever.
- No unmeasured claim in any copy; the framing of the benchmark result is fixed by `BENCHMARKS.md` and is not paraphrased upward.
- External actions (post, email, form, PR, invite request, inference spend) each require an explicit operator go at the moment of action.
- One moderator removal or credible spam accusation pauses the responsible operation pending review.
- Agents working in this repository respect the Azdaja activation contract and the `bench/oolong` inference ceremony; no benchmark inference without the documented acknowledgement flag and operator authorization.

## Ownership heartbeat

While a release or visibility operation is active, the owning agent records a local checkpoint every 15 minutes in `~/Library/Caches/jcode/azdaja-visibility-heartbeat.log` with UTC time, run ID, commit SHA, current OP, state, completed check, blocker, next action, and next deadline. A heartbeat records state; work advances only under the operation's own authorization. It never sends, posts, replies, submits, spends inference, launches HN, or mutates an external listing. External polling stays at each operation's stated cadence rather than multiplying every 15 minutes. A missed deadline or changed evidence digest marks the operation `BLOCKED`; resumption requires a new run ID plus an exact check that the cited blocker or digest is current.
