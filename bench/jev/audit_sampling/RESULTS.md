# Random-audit count estimation: retained stage-0 result

**Result:** the fixed feasibility bar passed on the already observed row651
population. Using unchanged Jev probabilities as auxiliary predictions reduced
count-estimation variance relative to uniform label auditing. This is a
**post-hoc, approximate, finite-population diagnostic**, not an exact OOLONG
answer, fresh generalization result, production feature or new RLM primitive.

## What changed, and what did not

The prior raw probability sum was 9,287.38 against 8,638 gold, an error of
+649.38. No model output, probability, threshold, prompt, source or label changed.
The experiment instead estimates the model's total error from a **uniform random
sample of trusted labels** and adds that correction to the full prediction sum:

`sum(p) + N/n * sum_sample(y - p)`.

This is the classical survey difference estimator and the mean case of
[prediction-powered inference](https://arxiv.org/html/2301.09633), not our
invention. Fixed-population unbiasedness comes from the sampling design, **not**
from trusting model calibration or treating model answers as gold.

## Fixed comparison

17,469 occurrence IDs, unchanged official labels, 2,000 fixed PRNG replications
at each of three audit sizes. All arms use the same sample in each replication.
All 6,000 outcomes are retained, including negative controls and failures to
improve individual estimates. Counts below are count RMSE, not item accuracy.

| Trusted occurrence labels | Jev-assisted RMSE | Uniform-only RMSE | MSE ratio | Approximate 95% interval coverage, assisted |
|---:|---:|---:|---:|---:|
| 100 | 292.25 | 861.48 | 0.1151 | **92.9%** |
| 500 | 125.56 | 385.40 | 0.1061 | 95.5% |
| 2,000 | 60.54 | 179.08 | 0.1143 | 94.95% |

The exact finite-population variance ratio is **0.109733**. The constant predictor
reduces algebraically to uniform auditing. The inverse predictor is worse than
uniform auditing, so an auxiliary model is not automatically beneficial.

Using all known labels to solve the variance formula gives an **oracle** budget
of 799 sampled occurrence labels versus 5,310 for count RMSE 100. For RMSE 50,
it is 2,810 versus 11,110. These are not deployable guarantees, measured annotation
labor, dollar savings or evidence that 799 labels suffice on a new corpus.

### The actual Azdaja sample did not beat uniform auditing

The preselected size500/replicate0 was run through real Azdaja
`start → load → exec → final → exec → final → invalid reload → kill`.
Only predictions and the 500 sampled labels entered the evaluator.

- Corrected estimate: **8,694.83152**, error **+56.83152**.
- Same sample's uniform estimate: **8,594.748**, error **−43.252**.
- Therefore uniform auditing was closer on this particular sample.
- The evaluator matched ordinary Python, preserved the result across re-entry,
  rejected an unknown audit ID, and cleaned up successfully.
- Both payload hashes were checked inside the evaluator. No unobserved gold was
  loaded. Typed attempts and model-trace events were zero.

The expected-risk reduction is supported by the fixed-population formula and
all retained replications, not by selecting an especially good public sample.

## Costs, performance and limits

- **Zero new inference requests.** Original computation plus the public workflow
  took 6.17 seconds on this machine. This excludes acquiring trusted labels.
- Predictions were reused from the prior 112-request Jev run: 2,749,030 input and
  357,302 output tokens, about 210 seconds. Its retained input-price estimate was
  $0.11545926. Billing is unknown and this is not a new end-to-end paid-cost study.
- `prior_typed_cost.matched_generative_baseline=false` is an unchanged field from
  that original receipt. A later matched generative baseline exists in
  `../asymmetry/RESULTS.md`; this diagnostic neither erases nor reruns it.
- Official labels simulate a trusted audit. No human audit was performed.
- There are only 4,998 distinct message texts among 17,469 occurrences. Uniform
  occurrence sampling has a valid fixed-population variance without assuming IID
  messages, but real annotators may reuse duplicate labels. A deduplicated or
  stratified human-effort baseline is still needed.
- The normal reference interval **undercovered at n=100**. It is not a
  finite-sample confidence guarantee or safe stopping rule. No production
  uncertainty gate follows from its nominal 95% label.
- The coordinator already knew this population's errors. Methods were fixed
  before this computation, not before all knowledge of outcomes. The result is
  post-hoc and has no independent-corpus validation.
- Exact counting, per-item approval, automatic planning and an RLM-specific moat
  remain unproven. Ordinary Python obtains the same estimator.

## Reproduction and requirement-to-check map

`RETENTION.json` binds six original result files. The measured implementation is
commit `5819ecb7cbf5c1f02c35bc45caecc960909065a6`; its five source hashes are also
inside `results-20260917/result.json`. No original result is rewritten by replay.
From the repository root, Python 3.9+ and Git suffice for retained-data replay:

```sh
python3 -B -m bench.jev.audit_sampling.replay --output /a/new/path/replay.json
```

This checks the official source and original native receipt, recomputes all
6,000 fixed replications, verifies the claims, and checks the retained public
command/results. It resolves 124 frozen source files inside this checkout and
checks their exact recorded hashes. It does **not** make new model calls, rerun
the native binary, or verify that unavailable historical executable's bytes.
The output explicitly reports `runtime_binary_bytes_verified=false`, the
recorded binary identity, and `validation_scope.mode=portable_retained_evidence`.
A new public execution additionally requires the exact retained binary
SHA256 `13fbd5bd15f12df039ff2481fba04d1577dffd1e632c269cd65940c0c758ac32`:

```sh
JCODE_SCRATCH_DIR=/a/private/scratch AZDAJA_BINARY=/path/to/exact/binary \
  python3 -B -m unittest bench.jev.audit_sampling.test_estimator \
  bench.jev.audit_sampling.test_run bench.jev.audit_sampling.test_replay \
  bench.jev.audit_sampling.test_portable -v
```

| Requirement | Concrete check and observed behavior |
|---|---|
| Correct estimator rather than calibrated-count assumption | Independent tiny-population exhaustive subset means/variances, census and constant-predictor tests passed. |
| Preserve multiplicity and valid inputs | Duplicate-content/distinct-ID, permutation, duplicate/unknown IDs, booleans and nonfinite rejection tests passed. |
| No selected outcomes | Fixed source-derived inputs, fixed 6,000 sample-ID hashes, every arm and all replications retained and recomputed. |
| Demonstrate an aggregate-risk improvement | Exact variance ratio 0.109733, MSE ratio below 0.60 at all three declared sizes. Inverse control worsens risk. |
| Exercise the intended execution boundary | Actual retained Azdaja binary consumed full predictions plus 500 labels, matched Python, persisted, rejected invalid re-entry, and killed its session. |
| No hidden provider usage | Disabled typed transport, generator `/usr/bin/false`, isolated environment, empty trace and zero judge attempts in actual execution. |
| Honest uncertainty | All coverage values retained, including 92.9% at n=100; no finite-sample guarantee. |
| Safe/reproducible outputs | Public CLI refuses existing files/directories and dangling symlinks. Replay rejects altered artifacts, false result/attempt fields and invalid command evidence. |

### Validation and review boundary

Root ran all 14 scoped tests with the exact retained binary: all passed, zero
skips. The full public replay passed under Python 3.14.5 and 3.9.6, recomputing
all 6,000 outcomes on the author's machine. Independent read-only review found no code blocker and
confirmed the stated narrow result. That reviewer ran nine tests successfully
but its native-binary test lacked AZDAJA_BINARY and did not execute. Do not
confuse that partial independent run with root's complete native test result.

### Portability correction after the initial push

The initial same-machine fresh-clone check was insufficient: a nested historical
replay still read the original checkout and executable via absolute paths.
With those paths forbidden, the actual public command failed. The repair adds
an explicit portable mode that checks relocated source bytes and retained
responses, but **does not pretend to validate missing executable bytes**.
The original default strict replay still checks them when available.

The guarded fresh-checkout command then passed with the original checkout,
historical binary, subprocesses and network forbidden. The initial 14 tests plus
six path/scope tests and the 11 existing label-audit tests passed as a 31-test
compatibility run. Independent review exposed an omitted-source acceptance gap;
the repaired verifier now requires the complete inventory from the exact
historical seal. The reviewer reran all six portable tests and independently
confirmed that removing a source entry is rejected.

A dedicated clean Ubuntu/Python3.9 workflow exercises the portable public command
without any private paths, executable or credentials. Its hosted verdict must be
checked separately, not inferred from local tests. Before publication of this
repair, all three hosted workflows on `c94966e` completed successfully, including
the full seven-job Rust/platform matrix. That result does not certify later
commits. New verifier hashes and guarded evidence are retained separately under
`portability/`; the original measurement retention manifest is unchanged.

No inference artifact, gold, frozen measured source or numerical result was
rewritten. The pre-fix **post-measurement verifier** versions remain retrievable
at Git revision `c94966e`; old `EVIDENCE.json` and `RETENTION.json` source hashes
remain historical rather than being relabeled. The portable report retains the
unchanged legacy numerical-summary hash **and separately reports its narrower
validation scope**. Matching a summary hash is not executable or provider
authentication.

## Remaining angles, ranked by the next falsifiable question

1. **Trusted-audit estimation:** repeat on a fresh, independently labeled corpus
   and compare actual labeling effort with uniform, duplicate-aware and simple
   stratified auditing. This stage supports doing that study, not deployment.
2. **Distinct-question state sharing:** compare many *different* decisions over
   one state in a batch versus the same decisions in separate requests, with
   identical prompts/models. Measure quality, token usage, wall time and actual
   pricing. Vendor parallelism claims and our item-classification run do not yet
   establish the gain for this workload.
3. **Semantic extraction followed by exact code:** let Jev propose source-bound
   predicates or fields, then use deterministic code for date, arithmetic and
   join rules. Test a fresh task against full-model answers and deterministic
   baselines. Keep unresolved extraction explicit, not silently false.
4. **Model-authored adaptive orchestration:** test whether an RLM actually chooses
   better plans than matched static Python using the same models and budget.
   Earlier host-authored orchestration is not evidence for this advantage.

Cache machinery is closed as commodity infrastructure. Memory/RAG/ingestion
work remains stopped per the later user instruction. No README marketing claim,
new live campaign, release, or automatic approval was added by this experiment.
