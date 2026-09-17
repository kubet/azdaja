# Dataset attribution and evidence boundary

Selected source paragraphs, questions and annotations in `fixtures/` are adapted from
SQuAD2.0, by Pranav Rajpurkar, Robin Jia and Percy Liang, with Wikipedia contributors.
The dataset is distributed under **Creative Commons Attribution-ShareAlike4.0**:
https://creativecommons.org/licenses/by-sa/4.0/ . These selected/adapted data retain
that license. The code here is separate from the dataset licensing statement.

Official dataset and license statement: https://rajpurkar.github.io/SQuAD-explorer/ .
Original file: https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json .
File identity and exact original QA/paragraph identities are retained in the manifest,
sources and detached annotations. Changes: deterministic subset selection, raw
whitespace-boundary windows, anonymous runtime IDs, and question-answer support prompts.
No claim is made that these are official SQuAD scores or a RAH leaderboard submission.

The current TypeSafe model page, read2026-09-17, documents `jev-1.13.0` and $0.042/M
input tokens, with output tokens free: https://docs.typesafe.ai/models.md .
This is the source for the receipt's token-price estimate, not an invoice. The API
documents named independent questions but does not substantiate the proposed universal
100KB/255-question/sub-second end-to-end guarantees in this experiment.
