# Whole-project engineering acceptance addendum

The scoped receipt in `results-20260918/retention.json` is unchanged. Its then-pending whole-project gate is resolved by `results-20260918/whole-result.json`.

- The first real `cargo test --all --locked --offline -- --test-threads=1` command **failed**, and its complete log is retained as `full-before.log`. The only failure was a second exact Cargo package allowlist in `tests/notice_distribution.rs` that had not yet included `src/solo_preflight.rs`. The CI allowlist had already been updated.
- The correction adds that single filename to the expected list. It does not remove or weaken an assertion, change runtime behavior, or alter existing package contents.
- The failed target and every unattempted integration target were then executed successfully. Previously passed targets were not repeated. `target-coverage.json` records the complete Cargo target set and exact continuation. All production-source hashes still match the earlier composed acceptance.
- Final target matrix: **719 passed, zero unresolved failures, five explicitly ignored, across 35 targets**. Of these, nine tests belong to the user's preserved untracked `memory_recall_precision` target. The tracked-source count is **710 passed**. Neither the untracked test nor other original files were added to the commit.
- Documentation tests, strict all-target/all-feature Clippy, formatting and the 49-artifact git-bound proof verifier pass. The feature-on public and installed checks remain those already retained in the scoped receipt.

This is complete target coverage assembled from a failed whole command and a successful targeted continuation, **not a claim that the first whole command passed**. Hosted CI will run the final tracked source as a fresh whole workflow. Its success must be observed at the published commit before calling that remote gate complete.

No new remote inference, live credential access, release, tag, or modification to the user's installation was required. The prior empirical results and original 40 files are unchanged.
