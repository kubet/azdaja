# Exact-source selection development panel

This new 18-task panel tests an optional semantic leaf, not general RLM superiority. It is separate from the frozen seven-task study. Inputs are authored and nonrepresentative, with repeated source paragraphs. They are not independent random samples or a held-out benchmark.

## Source and input contract

Every source is an exact contiguous excerpt of public commit `ca320c3607116447a506d6c8429489f1b30157a9`. The runner verifies the text and line bounds against the Git blob before inference. `fixtures/sources.json` is a deduplicated index of precisely those source records.

Input records contain `id`, `block`, `family`, `question`, `source`, and `candidate_kind`. The kernel whitelists only IDs, questions, exact sources and candidate occurrences into model state. Block/family, gold, rationale and grader never enter either semantic arm. Gold is public for reproducibility but is read only by the host grader during the experiment.

Both models receive the same candidates and question instructions. They select occurrence IDs. Native evaluator code copies the exact source span into a table and preserves the complete source pool. `no_match` means absent within the specified excerpt, `ambiguous` means the question/source leaves distinct applicable values, and `not_covered` means a uniquely established source value is omitted by the parser. The latter has an offline contract test but no live panel case.

## Fixed blocks

Each block has two direct controls, two contextual-role cases, one absent-value case and one underdetermined case.

| Block | IDs | Roles |
|---|---|---|
| 1 | s01–s06 | Package/minimum Rust versions, installer URL, tagged source install, bounded absence, unspecified version category |
| 2 | s07–s12 | Command occurrence, supported-tool list order, Cargo-specific command occurrence, absent Docker integration, unspecified host selection |
| 3 | s13–s18 | Generative command/model defaults, Linux probe, explicit Jcode install, absent concrete cache path, unspecified XDG category |

Before any inference, root rejected the first author draft's reconstructed excerpts and ambiguous gold, replaced them with exact public contiguous source, corrected questions that did not determine a source occurrence, and validated every accepted span against the parser. The method/parser and lexical comparator were frozen before root read gold in `dec3a03`. Sentinel/source-validation amendments `ac3389e` and `7335542` also predate inference. The corrected task/gold freeze is the commit introducing this file and the runner. No score-driven editing is permitted.

## Reproduction

Run provider-free tests, including actual persistent evaluator execution:

```bash
AZDAJA_BINARY=/absolute/path/to/azdaja PYTHONDONTWRITEBYTECODE=1 \
  python3 -B -m unittest bench.jev.span_selection.test_kernel bench.jev.span_selection.test_runner -v
```

Run the complete offline public workflow into a new output directory:

```bash
python3 -B -m bench.jev.span_selection.run --offline \
  --azdaja /absolute/path/to/azdaja --scratch /private/scratch \
  --output /private/scratch/new-span-offline
```

Live mode requires a `typesafe`-enabled executable, configured generative provider, explicit `--live`, and `--key-file` pointing to an owned 0600 regular file. Read `PLAN.md` first. The runner never deletes a caller's credential file. The invoking owner must remove its own ephemeral credential in a `finally` block, including failure/cancellation. Do not put credentials in source, prompts, config, command arguments or receipts. Live mode is not part of the tests and must not be repeated to seek a better score.
