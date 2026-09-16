# Optional Jev research prototype

**Status: experimental, opt-in, not integrated into Azdaja's production model path. The live semantic screen is blocked, not passed or semantically failed.** See the [decision and evidence](../../docs/research/jev-decision-20260916.md).

The TypeSafe skill is installed project-locally at `.agents/skills/typesafe-ai/`. Existing `llm`, `llm_batch`, hooks, and core Rust behavior are unchanged by this work.

**Use-case scope:** this prototype judges supplied claim/evidence packs. It does not implement semantic memory retrieval, discover repository dependencies, or establish evidence-pack completeness. The [request-to-evidence map and concrete memory hypothesis](../../docs/research/jev-request-evidence-map-20260916.md) distinguish those future applications from tested behavior.

**Broader engine follow-up:** the user clarified that reranking is one application of a general optional capability exposed beside `llm`. The separate [engine laboratory](engine_lab/README.md) now demonstrates typed manifest execution in persistent Monty with 20 guarded provider-free tests. Read the [engine research and architecture](../../docs/research/jev-engine-design-20260916.md) for the multi-application direction, matched-Python equality, and deliberate semantic failure cases. This does not reopen the live campaign or install a native `judge` function.

## What exists

- `adapter.py`: stdlib-only, explicit activation, typed Choice/Noul/Score validation, bounded fixed-origin transport, isolated killable worker, no retries, and sanitized failures.
- `run.py`: 66 frozen synthetic cases, progressive stopping, exclusive checkpoint receipts, uncertainty/coverage accounting, and invariance checks. Default execution is offline and never reads credentials.
- `bridge.py`: real Azdaja CLI execution with an offline provider. Monty recomputes hashes, checks every occurrence, and reduces exact counts. This is not a semantic oracle.
- `audit.py`: no-network replay of saved judgments/failures through current deterministic policy, historical implementation-hash checks against Git, and source-bound projection through the real evaluator. It does not replay HTTP calls or authenticate provider provenance.
- Tests: hostile contracts, exact error assertions, actual child timeout/reaping, source/gold separation, early stops, alias drift, receipt tampering, and real evaluator custody.

The follow-up adds complete and partially accepted synthetic campaign replay. Its [final validation receipt](results/validation-followup-final-20260916.json) records 87 offline tests, with no failures or skips. The 67- and 81-test receipts remain historical snapshots. Injected oracle outputs test plumbing, not Jev quality. Replay rejects missing transport evidence, impossible declared resource/timing bounds and unresolved aliases with retained judgments. Its duration and response-size checks are conservative consistency bounds, not authenticated raw-body or wall-clock reconstruction.

## Recorded live outcome

| Named run | Result | Validated judgments |
|---|---|---:|
| `pilot-20260916` at `71f2c22` | Requested `jev-1.12`, received HTTP 400 | 0 |
| `pilot-alias-20260916` at `0b6bf32` | Explicitly requested advertised `jev-latest`, stopped at response model mismatch | 0 |

One separately recorded metadata GET advertised `jev-latest` and `jev-preview`. There were **two credentialed inference attempts**, no automatic retries, and no holdout or baseline calls. Both runs have unknown usage. Numeric zero in their reported-token totals means no usable usage was retained, not zero billing.

The second rejected response is represented by byte count and SHA-256 only. Its returned identity, answer, and usage were not preserved or fully validated. Do not infer them from the hash. The historical files remain available in the recorded Git revisions. Subsequent offline hardening did not rerun or rewrite those experiments.

The saved `custody-alias-20260916.json` projects the stopped receipt into the real evaluator: 66 supplied packs plus two exact duplicate controls, **68 unjudged occurrences**, zero judged cases, `complete: false`. Strict mode rejects the missing judgments. Explicit audit mode retains the full incomplete ledger without inventing answers.

## Safe local commands

Python 3.10+, Git with the recorded source revisions, Rust/Cargo to build the evaluator, and repository files are required. No Python package installation is needed for the prototype.

```bash
cargo build --locked --bin azdaja
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s bench/jev -p 'test_*.py' -v
python3 -B bench/jev/run.py
```

Replay and project a preserved receipt with no API access. The output path must not already exist:

```bash
python3 -B bench/jev/audit.py \
  --receipt bench/jev/results/pilot-alias-20260916.json \
  --azdaja target/debug/azdaja \
  --audit-only \
  --output "$JCODE_SCRATCH_DIR/jev-local-audit.json"
```

Omit `--audit-only` to require complete judgment coverage. The recorded failed receipts must then fail, not produce a passing result. Source retention proves custody of selected packs, not completeness of a broader task or model attention.

## Reproduce the delivered acceptance paths

The public acceptance command runs the real entry points rather than relying on the retained test totals:

```bash
# Use an existing private scratch directory and a NEW receipt path.
python3 -B bench/jev/acceptance_cli.py \
  --scratch "$JCODE_SCRATCH_DIR" \
  --azdaja target/debug/azdaja \
  --receipt "$JCODE_SCRATCH_DIR/jev-public-acceptance.json"
```

If your environment does not supply `JCODE_SCRATCH_DIR`, pass another existing private directory. The script also works from outside the repository when invoked by absolute path. Use an absolute `--azdaja` path in that case. Python, the already built local evaluator, `/usr/bin/false`, Git and the retained source revisions are required. This is a Unix local workflow. It does not install anything, build the evaluator, or run live inference.

It executes the offline default, the original experiment suite, the separate engine command, both saved-receipt audit and strict paths, and ordinary Azdaja `start/load/exec/final/kill` on the actual `Cargo.toml`. It probes the currently absent native `judge_many` capability and verifies that ordinary execution still works afterward. Existing output files and symlinks are rejected **before** any tests run. A creation race cannot overwrite a file either. Failed checks exit 2 and cannot emit a passed receipt. Strict-mode parser/startup diagnostics are rejected, but the legacy audit CLI's fixed failure message does not distinguish every internal cause. The original suite separately exercises the real strict projection API.

**A pass means these experimental/public-interface behaviors reproduced. It does not mean native integration or live usefulness passed.** The original experiment has 87 tests and the staged engine has 20, not 107 engine tests. Backend answers remain synthetic. Both old live receipts must stay incomplete. The command compares experimental source hashes with the retained acceptance reference. A differently built evaluator is recorded as such and must satisfy the same behavioral checks, without inheriting the old binary's review verdict. The audit tests now honor the explicitly selected evaluator instead of silently using the default path. The host, local binary and repository are trusted.

Envelope tests, which do not replace the public workflow above:

```bash
python3 -B -m unittest bench.jev.acceptance_cli_tests -v
```

The real Rust library regression command remains separate: `cargo test --locked --offline --lib`. Its last retained result is 191 passed and one explicitly ignored stress test. See the [whole-result acceptance map](../../docs/research/jev-whole-result-acceptance-20260916.md) for the requirement-by-requirement limits.

## Future live use is a new study

Do not replay the old live commands as a recovery loop. First establish an account-available request model and its allowed returned identity with the provider. `jev-1.12` is a historical experiment assumption, not an advertised available model for this account.

Current hardening requires an explicit CLI `--model` before reading a live credential. Concrete requests require exact returned identity. Known aliases require an explicit predeclared allowlist, for example:

```bash
# FUTURE STUDY ONLY. Values must be independently established, not guessed.
python3 -B bench/jev/run.py --live \
  --model "$REQUESTABLE_ALIAS" \
  --allow-resolved-model "$CONFIRMED_RETURNED_MODEL" \
  --key-file "$PRIVATE_KEY_FILE" \
  --receipt bench/jev/results/new-named-study.json
```

The allowlist must be a small set of non-alias `jev-*` identifiers. The first fully schema-valid, budget-eligible response pins one ID. A subsequent change stops and poisons the client, even if both IDs were allowlisted. Requests keep the original alias on the wire. An echoed moving alias is rejected, not treated as an immutable pin. This policy was tested offline only. It ensures observed string consistency, not authenticated alias mapping or fixed backend weights.

A credential file must be a private, owner-held regular file, not a symlink. The adapter accepts only `[A-Za-z0-9_-]` token characters. Never put a real key in argv, fixtures, a receipt, a prompt, or Git. The temporary credential used for this investigation is not an installation or a new Azdaja default.

## Acceptance is intentionally difficult

The [frozen protocol](../../docs/research/jev-experiment-protocol-20260916.md) and [model-availability amendment](../../docs/research/jev-model-availability-amendment-20260916.md) define the historical runs. Briefly: all six smoke labels correct, then at least 27/30 challenge labels correct, zero wrong auto-accepted decisions, and at least 15/30 accepted at selected probability >= .98 and confidence >= .90. Holdout and invariance require prior stages to pass. There is no post-hoc threshold search or oracle fallback.

A fully validated response that crosses a resource limit is retained for usage and audit but excluded from budget-eligible stage judgments/projection. That exclusion must be disclosed in any later accuracy report.

Hand-authored paired cases, holdout triples, early stopping, and tiny samples prevent population-level safety claims. Type correctness, exact duplicate expansion, and a green offline suite cannot establish semantic accuracy, speedup, cost reduction, or an Azdaja moat.
