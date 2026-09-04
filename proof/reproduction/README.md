# First-party proof bundle

This directory gives reviewers one offline command for checking Azdaja's recorded first-party evidence. The command validates a retained live receipt and a provider-free receipt. It does not replay the live provider calls.

From a full-history clone of the published repository:

```sh
git clone https://github.com/kubet/azdaja.git
cd azdaja
./proof/reproduction/run.sh
```

The verifier itself uses only Python 3.9+, Git, and files in this checkout. It performs no provider call, downloads nothing, and does not rewrite a receipt. A successful run prints one JSON object with this stable shape:

```json
{"artifacts_verified": 25, "bundle_source_commit": "<40-hex-source-commit>", "classification": "narrow first-party reproducible evidence", "git_binding": true, "live_fable": {"exact_results": 3, "monty_executions": 3, "provider_calls": 3}, "provider_free": {"scenarios": 3, "surviving_sessions": 0}, "schema": "azdaja.first_party_proof_verification.v1"}
```

Shallow clones and source archives can lack the historical commits named by the receipts. If Git reports a shallow checkout, run `git fetch --unshallow` before verification. A nonzero exit means the evidence was not verified. Read the `proof verification failed:` diagnostic rather than treating a partial check as a pass.

## What it verifies

- every file named by `manifest.json` is a regular file with the recorded byte count and SHA-256 digest;
- the artifact set is unchanged from the manifest's source commit;
- the existing live Fable verifier accepts its source-bound receipt;
- the existing provider-free verifier accepts its receipt and captured raw log;
- the expected exact answers, input sizes, bounded prompt sizes, call counts, Monty execution counts, cleanup state, and live fixture SHA-256 values match the receipts;
- `README.md`, `BENCHMARKS.md`, and `site/proof.html` expose the receipt, manifest, runner, verifier, source commit, and recorded live timings;
- changed hashes, sizes, paths, schemas, totals, answers, fixture identities, or claim boundaries fail closed.

The verifier requires a Git checkout that contains the commits named by the two receipts and the bundle manifest. It does not require network access.

## Evidence map

- `manifest.json`: source-bound artifact inventory and hashes
- `fixtures/spec.json`: live fixture hashes plus the explicit provider-free v2 digest limitation
- `receipts/fable/index.json`: exact live receipt and summary hashes
- `receipts/provider-free/index.json`: exact provider-free receipt, summary, and log hashes
- `expected/invariants.json`: deterministic values checked across both proof paths
- `verify.py`: stdlib-only fail-closed verifier
- `test_verify.py`: artifact tamper, path escape, schema, and current-bundle tests
- `../../docs/release/notice-audit-2026-09-04.md`: exact third-party notice metadata limitation that prevents calling this a complete verification capsule

## Provenance map

| Evidence | Measurement source | Retained receipt SHA-256 | Claim scope |
|---|---|---|---|
| Live Fable suite | `2514d26a245a5d1c9f6bb1f351391b69a616c3b1` | `966b92bd3153c519bd3e4e9d62152a590ab848b77a2c84729d0c38cbaa86b508` | One provider-generated observation per synthetic task |
| Provider-free acceptance | `fe91f98d4c49d5aca59c4911c12869c9a05d22ea` | `ebcc0632ef458a90b90eb0b95ed3343df85e66d9ed22633173e2ce3fdb1ec08b` | Deterministic scripted transport with retained raw log |
| Shared release binary | recorded by both receipts | `3111c880bcf2cbf738282bf826bd5649e175fa5a0efc0b3ace5b077425f0921a` | Binary identity only, not a security attestation |
| Offline verifier bundle | `manifest.json` field `source_commit` | every listed artifact is byte-counted and SHA-256-bound | Narrow first-party reproducible evidence |

## Optional replays

Provider-free replay performs no model inference. A first Cargo build may need its declared Rust dependencies if they are not already cached:

```sh
python3 bench/product_50mb/reproduce.py \
  --receipt "$PWD/provider-free.json" \
  --summary "$PWD/provider-free.md" \
  --log "$PWD/provider-free.txt"
python3 bench/product_50mb/verify.py \
  "$PWD/provider-free.json" \
  --binary target/release/azdaja \
  --log "$PWD/provider-free.txt" \
  --require-binary --require-log
```

The live replay is opt-in, makes three Claude Fable calls, can vary in timing and provider behavior, and must never be treated as byte-identical reproduction:

```sh
python3 bench/live_fable_suite/run.py \
  --yes-run-inference \
  --receipt "$PWD/live-fable.json" \
  --summary "$PWD/live-fable.md"
```

## Claim boundary

This is **narrow first-party reproducible evidence**, not a complete verification capsule and not an independent replication. Deterministic hashes and invariants can be checked exactly. The live receipt is a timestamped observation, not a promise about future provider behavior. The provider-free v2 receipt records exact byte counts and generator provenance but does not retain generated-input SHA-256 values.

The bundle does not establish general model quality, arbitrary-input support, comparative superiority, statistical significance, production readiness, operating-system sandboxing, legal compliance, or completeness of third-party notice metadata.
