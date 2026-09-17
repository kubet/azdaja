# CUAD source attribution and scope

The raw contract contexts, question definitions and expert annotations in `fixtures/` are a complete projection of the official CUAD test split by The Atticus Project, pinned to repository commit `67faa0e6023b04fcaae6cc09497ab00e5d63a2a2`.

- Source: https://github.com/The-Atticus-Project/cuad/tree/67faa0e6023b04fcaae6cc09497ab00e5d63a2a2
- Archive: https://raw.githubusercontent.com/The-Atticus-Project/cuad/67faa0e6023b04fcaae6cc09497ab00e5d63a2a2/data.zip
- Project description: https://github.com/The-Atticus-Project/cuad/blob/67faa0e6023b04fcaae6cc09497ab00e5d63a2a2/readme.md
- Dataset card and CC BY 4.0 designation: https://huggingface.co/datasets/theatticusproject/cuad
- License: https://creativecommons.org/licenses/by/4.0/

Changes: split the official test JSON into source-only contexts, source-only five-category questions and detached expert labels/spans. Retained every one of the 102 raw contract contexts unchanged, in source order. Added stable local document IDs and four exact Boolean query definitions. Hashes and byte counts are in `fixtures/source-manifest.json`; `prepare.py` validates against the pinned original test bytes before producing these files.

This evaluation measures agreement with expert annotations and exact cited source spans. It is not legal advice or an assertion that annotations are perfect, that the source was absent from model training, or that these 102 documents represent every contract workload.
