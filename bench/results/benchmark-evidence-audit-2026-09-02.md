# Benchmark evidence audit, 2026-09-02

This is a provider-free audit of committed evidence. No paid inference was run, and no historical benchmark receipt was rewritten.

## Safe cold-email wording

> In a frozen synthetic 1.3 MiB classification diagnostic, the committed r10 receipt records the same exact answer, `42`, for native and Azdaja arms. Azdaja used 10,938 versus 32,862 uncached tokens on Codex (66.7% lower) and 8,453 versus 70,397 on OpenCode (88.0% lower); recorded wall time was 10.784 versus 23.862 seconds and 8.151 versus 22.479 seconds, respectively.

Attribute this as a repository-reported, single-run diagnostic. Do not describe it as a fresh concurrent paired benchmark, a robustness result, or a general superiority claim. The two candidate arms ran in parallel, but the native rows were reused from frozen r8. Each candidate had one successful GPT-5.6 Luna inner call with complete five-field usage.

## Frozen 199-row accuracy receipt

`bench/results/rah199-public-manifest.json` contains exactly 199 fixtures, 199 distinct row hashes, and 50 distinct context hashes. The sanitized receipt at `bench/results/gpt-rah199-mortality-v3-terminal-public.json` reports a fixed-denominator score of `136.5968828828529 / 199 = 68.64164968987583%`, with 185 valid predictions and 14 retained failure zeros.

Its root-usage section is not a complete 199-row token aggregate: 198 rows have measured usage, one row is missing, and the measured total is 1,069,865 tokens (891,498 input plus 178,367 output). Do not turn this receipt into a complete per-row token or average-token claim. It is validation-derived, private, and not an official OOLONG leaderboard result.

## Checks performed

- `PYTHONDONTWRITEBYTECODE=1 python3 bench/delta/fixture.py` passed: 306 total records, 64 selected records, 7,655 compact evidence bytes, 1,306,163 context bytes, expected answer `42`.
- `PYTHONDONTWRITEBYTECODE=1 python3 bench/delta/validate.py` failed closed at `src/lib.rs hash` on current `main` and in a temporary worktree at the documented candidate commit `a642db83d54b5c80901aba1e1e183e7178481a0e`. At that commit, the actual `src/lib.rs` hash is `3e41e82420cc19327d4ce8108628dbdbc37248d1feda5a18bbeeffb2e5dfd69b`, while `bench/delta/plan.json` expects `9d48a9ce49af96c52132e9b36ec68b00659cc542e40481c7d8c2a04890f1f1e8`.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s bench/delta -p 'test_*.py' -v` ran 24 tests on current `main` with one error at the same source-hash gate. At the candidate worktree it ran 20 tests with one error at that gate.
- `cargo build --release --locked` passed.
- `AZDAJA_PRODUCT_BINARY=target/release/azdaja cargo test --release --locked --test product_50mb offline_scripted_harness_answers_three_real_world_50_mib_files_without_a_death -- --ignored --exact --test-threads=1` passed: 1 test.
- `cargo test --all --locked -- --test-threads=1` was attempted but timed out after 600 seconds with exit 124. Many completed suites were green, but this is not a full-suite pass.

## Recomputed artifact links

| Artifact | SHA-256 |
|---|---|
| `bench/results/gpt-rah199-mortality-v3-terminal-public.json` | `842475dcc8d3868af782e52716cd11ff4db7709e134b54c7980f00e5c8c26f8b` |
| `bench/results/rah199-public-manifest.json` | `4ecb211aecea8cd1cdf86e3bb78b52ef1788d5bb2b0f9d640c0c9c137fcd547c` |
| `bench/delta/plan.json` | `d221b7c38d32f1107a1c1eb9bb54d61aaf9744ef930bbd35329e844ede63026e` |
| `bench/delta/results/r8-result.json` | `114c8e4aa3917ee94548a160b0a29b72a9891da52140dbe7088a1515bdba7648` |
| `bench/delta/results/r10-result.json` | `8d63dc943d75a2d4eb911d2332d71ffa619f8466f13f04187edac22ddcbdc68e` |

The r10 receipt's baseline-result hash matches the recomputed r8 hash, and its plan hash matches the recomputed current plan hash. Its candidate token formulas also recompute exactly: Codex `10,398 + 275 + 265 = 10,938`; OpenCode `8,158 + 10 + 285 = 8,453`, with zero cache-read and cache-write tokens in both candidate rows. Raw stdout/stderr are not retained, so their embedded stdout digests cannot be independently recomputed from this checkout.

## Use decision

Use only the narrow r10 wording above, and label it as frozen repository evidence. Do not use the 68.64% accuracy figure as a leaderboard or superiority claim. Do not claim independent source/runtime hash validation until the `src/lib.rs` plan mismatch is corrected and the delta verifier and its full test set pass.
