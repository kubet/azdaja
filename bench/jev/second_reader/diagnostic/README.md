# Flat-02 second-reader diagnostic

This directory is the bounded, provider-free investigation of the rejected
`flat-02` typed Choice batch. It owns no production code and does not alter a
validator, normalize a response, rerun the old measurement, or fill its
missing judgments.

## Run

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest bench.jev.second_reader.diagnostic.test_diagnostic -v
python3 -B -m bench.jev.second_reader.diagnostic.audit \
  --output "$JCODE_SCRATCH_DIR/flat-02-diagnostic-report.json"
```

The script reads only the checked-in fixture, receipt, retained successful
observations, and current `src/judge.rs`. It makes zero provider calls and
reads zero credentials. The report is safe to publish as a summary because it
does not retain the discarded body or reproduce provider prompts.

## Observed boundary

The predecessor receipt has one stopped typed operation, `flat-02`, containing
25 question IDs. The retained observation contains only:

```json
{"failure":"judge: probabilities must sum to one", "stats": {"...":"..."}}
```

Therefore the evidence supports **one rejected batch with 25 unjudged
questions**, not 25 independently observed failed responses. There is no
retained rejected response body, failing question ID, actual sum, or raw byte
sequence. The recorded message is the validator's error envelope. It does not
justify attributing the failure to rounding, provider serialization, Jev,
Azdaja, or a particular question. The exact cause is not recoverable from the
retained evidence.

The companion `audit-report.json` is generated rather than checked in. It
audits the 11 retained successful typed observations, covering 275 successful
judgments:

- 75 Choice answers and 200 Noul answers.
- Every retained Choice has an exact probability domain and finite
  probabilities in `[0, 1]`, an argmax winner, and a Rust-order binary64 sum
  within the validator's `1e-6` tolerance. Option cardinalities are 70
  four-option answers and 5 three-option answers.
- It reports the maximum absolute sum residual, minimum tolerance margin,
  winner gaps, option cardinalities, and human-visible decimal precision. The
  numbers describe retained successful records only. They say nothing about
  the discarded `flat-02` body.

## Native requirement audit

`audit.py` binds its inventory to the current `src/judge.rs` hash and records
line ranges for every native requirement. The actual Rust test seams remain
the authority for behavior. Run both existing provider-free suites separately:

```sh
cargo +1.95.0 test --locked --offline --features typesafe --test judge_native
cargo +1.95.0 test --locked --offline --features typesafe --lib judge::tests
```

The public CLI suite covers default-disable, argument rejection before
transport, missing-key failure, config round-trip, ordinary execution
recovery, and credential isolation. The Rust unit suite covers injected
transport paths for malformed or duplicate JSON, exact answer coverage,
question and answer types, finite `[0,1]` probabilities, exact Choice
domains, sum tolerance, Choice argmax, Score legend/distribution/weighted
score, usage accounting, request/response byte limits, credential scans,
deadlines, poisoning, caching, and input budgets. Those tests establish the
current implementation's behavior, but cannot reconstruct a body discarded by
the old live run.

## Exact focused production tests to propose to root

Do not add them here because this directory owns no production or test files.
Root can add a narrow `src/judge.rs` test through the existing
`with_dependencies` seam:

1. Build one 25-question Choice request matching `flat-02` and inject a
   response whose failing question has a sum residual of `1.1e-6`; assert the
   exact error `judge: probabilities must sum to one`, `attempts == 1`,
   `questions == 25`, `poisoned == true`, and an empty cache.
2. Repeat with a residual below the `1e-6` boundary and assert acceptance,
   then separately mutate one option key, the chosen option, and a non-finite
   or out-of-range value. This isolates sum tolerance from domain, argmax, and
   range failures without normalization.
3. Add a retention-contract test at the transport boundary, not a validator
   change: on a rejected response, persist only bounded metadata plus the raw
   byte hash by default, and only persist the exact bytes when an explicit
   diagnostic flag and private destination are present. Assert that the
   failure remains terminal and no answer is cached or promoted.

These witnesses can prove new behavior. They cannot prove what the discarded
old body contained.

## Suggested one-call raw-retention design

If root authorizes a fresh diagnostic request, keep it separate from the old
measurement and stop at the first transport error or malformed distribution.
Use the exact `flat-02` request bytes and model, one provider request, the
existing per-call timeout and input-token cap, and no retry. Never use the new
result to repair the old 25 rows or to make a semantic quality claim.

Capture at the Rust transport boundary **before parsing**, while retaining the
original bytes unchanged for diagnosis. The default receipt should contain
only: source manifest digest, binary digest, request digest and byte count,
provider/model identifier as returned if safe, attempt ordinal, HTTP status
class, elapsed time, response byte count, raw-body SHA-256, validation phase,
and sanitized error text. A private raw-body sidecar should require all of:

- an explicit diagnostic opt-in, a new non-existing path, no symlink, owner-only
  directory and `0600` file permissions;
- a hard byte cap of `max_response_bytes + 1`, a wall-clock cap, one request,
  and no retry or fallback;
- no authorization header, API key, request state, or question text in the
  receipt or filename;
- a separate publication derivative that is withheld if it contains a
  credential-shaped token or other secret indicator. Do not mutate the private
  original before computing its hash or passing it to the unchanged validator.

`redact_typesafe_keys` is defense in depth only. It cannot identify arbitrary
secrets, so a clean redaction scan is not permission to publish the raw body.
The raw sidecar must stay private and uncommitted unless a human explicitly
reviews its contents.

The source manifest should pin the exact Rust source, binary, fixture pack,
request bytes, diagnostic script, and configuration. Budgets should make the
experiment auditable: at most three newly authorized diagnostic calls as a
campaign ceiling, one target cell, 25 questions, one attempt per call,
existing 20-second call timeout, existing 100k input-token limit, and the
response cap. This is evidence collection, not a live measurement extension.

## Best investigation step

The best next step is one explicitly authorized, isolated diagnostic call with
the above raw-retention contract and an instrumented copy of the exact Rust
path. If it fails, the retained bytes can identify the question and numerical
condition. If it succeeds, that still does not explain the discarded historical
body. Offline evidence should remain the stopping point unless root chooses
that narrowly bounded call.
