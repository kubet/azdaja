# Data notices for Jev research artifacts

These notices apply to retained inputs, selected excerpts, request copies, labels,
and corresponding source-bearing result files under `bench/jev/`. They supplement,
not replace, the original sources' terms. The repository's software license does
not relicense third-party data. Added 2026-09-17 before the first remote push of
this research. No frozen study artifact is changed by this notice.

## OOLONG-synth and SMS Spam Collection

The row645 and row651 experiments use the public validation split of
[oolongbench/oolong-synth](https://huggingface.co/datasets/oolongbench/oolong-synth),
introduced by Amanda Bertsch, Adithya Pratapa, Teruko Mitamura, Graham Neubig and
Matthew R. Gormley in
[Oolong: Evaluating Long Context Reasoning and Aggregation Capabilities (2025)](https://arxiv.org/abs/2511.02817).
The upstream [project](https://github.com/abertsch72/oolong) publishes its software
and associated documentation under the MIT license, copyright 2025 Amanda
Bertsch. The exact upstream notice is retained in `LICENSE.OOLONG-MIT`.
The Hugging Face dataset card does not itself declare a separate dataset license.
We do not interpret the software license as overriding underlying data rights.

The SMS messages and ham/spam annotations originate in **SMS Spam Collection**:
Tiago Almeida and José Hidalgo (2011), UCI Machine Learning Repository,
[DOI 10.24432/C5CC84](https://doi.org/10.24432/C5CC84).
The [official UCI dataset page](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)
states **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
[License and terms](https://creativecommons.org/licenses/by/4.0/).
Credit is also due to the source collections acknowledged there, including
Grumbletext, the NUS SMS Corpus, Caroline Tagg's thesis and the SMS Spam Corpus.
No endorsement by these authors or dataset providers is implied.

OOLONG adds synthetic occurrence/date framing, repetition and aggregate tasks.
Our retained derivatives select benchmark rows or records, attach stable IDs and
byte spans, partition requests, join official labels, and add model predictions
and measurements. These transformations are described in the associated plans.
They do not turn repeated occurrences into independent examples or convert
benchmark annotations into newly adjudicated truth. The unchanged upstream API
responses and their hashes are documented in `row645_labels/PROVENANCE.md` and
`row651_labels/RESULTS.md`.

This attribution covers source-bearing artifacts in `angle_lab/`,
`angle_followthrough/`, `row645_labels/`, `row651_labels/`, `second_reader/`,
`asymmetry/`, and any retained copies of their SMS inputs. Original benchmark
source files elsewhere in `bench/oolong/` retain the same upstream attribution.

## SQuAD 2.0 and Wikipedia-derived excerpts

The selected paragraphs, questions, answer spans, plausible answers and their
request copies in `measurement_v2/`, `measurement_followthrough/`, and the
Choice diagnostics/report derived from them retain **CC BY-SA 4.0**.
See [`measurement_v2/ATTRIBUTION.md`](measurement_v2/ATTRIBUTION.md) for authors,
source URLs, exact source hash, transformations and license link. This includes
copies in `second_reader/diagnostic/` and `asymmetry/provider_report/`.
Their dataset terms are not replaced by the repository MIT software license.

## Project-authored and synthetic evidence

Repository documentation excerpts retain the repository's applicable license.
Hand-authored synthetic claim panels and synthetic host/oracle tests are project
artifacts, not samples from a private user corpus. Real provider responses are
experimental observations, not independently verified facts. Author names and
paths inside synthetic fixtures are not authentication or real-user evidence.

This inventory records provenance and observed upstream terms. It is not a claim
of legal review, privacy certification, dataset-provider endorsement, or official
benchmark submission.
