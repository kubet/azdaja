# Optional Jev research prototype

**Status: experimental, opt-in, not integrated into Azdaja's production model path. The live semantic screen is blocked, not passed or semantically failed.** See the [decision and evidence](../../docs/research/jev-decision-20260916.md).

The TypeSafe skill is installed project-locally at `.agents/skills/typesafe-ai/`. Existing `llm`, `llm_batch`, hooks, and core Rust behavior are unchanged by this work.

## What exists

- `adapter.py`: stdlib-only, explicit activation, typed Choice/Noul/Score validation, bounded fixed-origin transport, isolated killable worker, no retries, and sanitized failures.
- `run.py`: 66 frozen synthetic cases, progressive stopping, exclusive checkpoint receipts, uncertainty/coverage accounting, and invariance checks. Default execution is offline and never reads credentials.
- `bridge.py`: real Azdaja CLI execution with an offline provider. Monty recomputes hashes, checks every occurrence, and reduces exact counts. This is not a semantic oracle.
- `audit.py`: no-network replay of saved judgments/failures through current deterministic policy, historical implementation-hash checks against Git, and source-bound projection through the real evaluator. It does not replay HTTP calls or authenticate provider provenance.
- Tests: hostile contracts, exact error assertions, actual child timeout/reaping, source/gold separation, early stops, alias drift, receipt tampering, and real evaluator custody.

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
