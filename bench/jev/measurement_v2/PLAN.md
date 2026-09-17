# Requested Jev measurement follow-through, 2026-09-17

Scope replaces the cancelled ingestion/RAG work. No memory changes, new application angles,
skill rewrites, README claims, publication or production source changes are authorized here.

## 1. Retained row645 audit before any rerun

Independently check the exact official task, full source record framing, every May record,
original occurrence indices, duplicate multiplicity, and equality to both submitted inputs.
Compare positive occurrence sets, not merely totals. Recompute all 227 retained probabilities,
threshold count and `sum(noul)` against the official scalar132. The signed difference is a
net count error, not proof of exactly seven false positives. Opposite errors can cancel.
Only use independently aligned official per-item labels to name false positives. A scalar gold
cannot identify the seven. Fix and rerun only a demonstrated code/fixture defect under a new
explicit amendment, preserving prior receipts. A matching probability sum is an aggregate
consistency observation, not a calibration certificate. No unconditional Poisson-binomial CI.

## 2. Fresh flat raw-text selection, n=100

Use the official SQuAD2 development file, 4,370,528 bytes, SHA256
`80a5225e94905956a6446d296ca1093975c4d3b3260f1d6c8f68bc2ab77182d8`, from
https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json.
Dataset and selected/adapted excerpts are CC BY-SA4.0, with attribution to Rajpurkar,
Jia and Liang and Wikipedia contributors. The official website states this dataset license.
The repository's MIT software license is not substituted for the dataset license.

Deterministic SHA256 ordering of `jev-measurement-v2/` plus official QA ID, before outputs.
Only complete paragraphs of at most700 UTF-8 bytes. At most one QA per distinct paragraph,
no paragraph reuse across the two panels. Choose75 answerable and25 official impossible cases.
Split the complete paragraph into disjoint raw windows at whitespace boundaries, targeting
240 UTF-8 bytes per window. Preserve all bytes including separators, offsets and source hash.
Require at least2 windows. Eligible answerable cases require every official annotated answer
span to lie entirely within the same window and no exact answer string in another window.
This avoids silently grading several supported alternatives as one. It is a selected,
short-paragraph development panel, not million-token search or an official SQuAD score.

Model sees only raw windows and the question, never gold/answer offsets/impossible flag.
Choice options are every window plus `no_match`. No summaries, heading-only representation,
learned retrieval, discarded window or tree. Both models receive identical evidence/questions.
Group25 cases per pack, reducing pack size only if the existing24KB state/64question contract
requires it; fail admission if the declared total request cap would be exceeded.

Report exact window accuracy, answerable accuracy, no-match recall, source coverage and every
error. Finite-panel success bar: at least95/100 overall,24/25 no-match, and no more total errors
than the matched generative arm. Speed benefit bar is typed call-wall total <=75% of generative,
with preprocessing and actual load/exec/final costs separately retained. This is not a claim
of population noninferiority or a novel RLM primitive.

## 3. Flag-only verifier, n=200 including100 planted bad claims

Use100 further answerable and100 further official impossible questions over disjoint eligible
paragraphs from the same source. For answerable questions propose the first official answer.
For impossible questions propose the first official `plausible_answers` text, yielding an
adversarial unsupported answer already annotated by the dataset. These are evidence-support
claims, not necessarily false in the outside world. Require valid exact span for each proposed
answer and retain original annotations separately from provider inputs.

Question: does the supplied paragraph establish that this proposed answer correctly answers
this question? Noul for Jev, yes/no for the matched generative call, complete raw paragraph.
A returned result may flag or veto for inspection only. A high value never grants approval,
permission or ground truth. The research operating point is p>=.5 as predicted support,
not a production policy. Report false support among100 unsupported claims and false flags
among100 supported claims, including all errors and the always-flag/never-flag controls.
Finite-panel success bar: zero false supports, <=5 false flags and no worse than baseline.
A small positive count is a measured failure of this declared strict bar, not evidence that
all verification is useless. Retain Brier score and five fixed-bin reliability statistics,
plus fixed confidence coverage/risk at .6/.7/.8/.9/.95, with no posthoc threshold selection.
Article/paragraph dependence and possible training contamination remain explicit.

## 4. Admission, cost and receipts

Use unchanged accepted Azdaja source e75d836 and binary SHA256
`13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32`, native
`judge_many` and `llm`, returned Jev identity `jev-1.13.0`, generative model `gpt-5.6-sol`.
Each arm uses identical packs. Alternate typed-first and generative-first by pack ordinal.
Maximum12 typed requests,12 logical generative calls,24 entered generative turns under the
existing bounded retry contract,1,500,000 reported typed input tokens, and1,800 wall seconds.
No automatic retry of a stopped study, no gold-driven repair call. Freeze all code, source,
selected fixtures and binary hashes before provider admission. A sealed start marker prevents
silent re-entry. Any identity/schema/coverage/source/budget failure stops with retained usage.
Cost uses measured tokens and documented prices, not inferred invoices. Generative dollars
remain unknown without an applicable price. CPU-only preflight must finish before live timing.

Reuse the actual native lifecycle and immutable observations/trace receipts. Add one benchmark
row per attempted matched pack with source/model/arm/request/response/usage/timing/status hashes.
This follows repository benchmark evidence conventions but is not a RAH leaderboard submission
or official protocol-compliant score merely because its JSON format resembles existing rows.
Provider-free replay must reconstruct outcomes from retained request/response bodies and reject
rehashed changed grades, gold leakage, missing calls and source/body mismatches. Preserve all
historical small-panel results without rebranding them as larger-sample evidence.
