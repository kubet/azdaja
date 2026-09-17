# Random-audit aggregate estimates: stage 0

## Decision and scope

Can a cheap, biased decision model reduce the number of **trusted labels** needed
to estimate a corpus count, without assuming its probabilities are calibrated?
This is a different use of Jev from thresholding, confidence routing, or approving
individual answers. It produces an **approximate estimate**, never an exact
OOLONG answer or an automatic approval.

This is a disclosed **post-hoc finite-population diagnostic** on already observed
row651 predictions and official labels. The coordinator has seen their errors,
Brier score and count bias. This plan fixes the computation, not a blind new
quality trial. No model call, threshold tuning, label change, hidden outcome
selection, memory/RAG work, or modification to any frozen study is permitted.
There is no claim that the statistical method is new or exclusive to RLMs.

## Primary evidence

Angelopoulos, Bates, Fannjiang, Jordan and Zrnic, *Prediction-Powered Inference*,
[arXiv:2301.09633v4](https://arxiv.org/html/2301.09633), Sections 1.3/1.4 and
Appendix B, especially Corollary B.1. The mean case is the classical survey
**difference estimator**, not a new algorithm invented here. Appendix E.4 gives
an asymptotic finite-population interval. Nonasymptotic confidence sets require
additional machinery that this small diagnostic does **not** implement.

For fixed occurrence-level predictions p_i, fixed labels y_i and a uniform sample
S of n distinct occurrence IDs from N:

    corrected_total = sum_all(p_i) + (N/n) * sum_sample(y_i - p_i)
    uniform_total   = (N/n) * sum_sample(y_i)
    exact_design_variance = N^2 * (1 - n/N) * S_residual^2 / n

S_residual^2 uses denominator N-1. Both estimators are unbiased over uniform
samples of this fixed population. This does not assume independent message
contents. Repeated occurrences remain distinct sampling units and retain their
multiplicity. It does not justify convenience sampling, confidence-only auditing,
sampling unique messages without weights, model-generated gold, or generalizing
to an unseen corpus. Real annotators may reuse labels for duplicates, so occurrence
counts are **not** a measured human-effort or dollar cost.

## Fixed experiment

1. Replay the original native row651 receipt and byte-align the official source
   using the existing public audit. Consume all 17,469 occurrences, not a selected
   error slice. No new model observations.
2. Primary predictor: unchanged raw p_ham. Secondary controls: unchanged p>=0.5,
   constant 0.5 (must equal uniform auditing), and inverse 1-p (may be worse).
   Do not select the winner as a newly validated policy.
3. Audit sizes: 100, 500, 2,000. Exactly 2,000 independent deterministic PRNG
   replications per size, seeds SHA256(`audit-sampling-v1|n|replicate`). The same
   sample IDs are used for every arm. No outcome-dependent resampling or stopping.
4. Report full-population residual variance, exact design RMSE, simulated bias,
   RMSE, and approximate normal-interval coverage. Normal reference intervals are
   diagnostic, not finite-sample certificates. Retain all replicate outcomes and
   sample-ID digests. No interval-based production gate.
5. Solve the exact variance formula for the labels needed to reach count RMSE
   100 and 50. These are **oracle planning diagnostics** using all known labels,
   not deployable label budgets or guaranteed errors.
6. Execute size500/replicate0 through actual Azdaja start/load/exec/final/reentry/
   kill. Pass only all predictions and the 500 sampled labels into the evaluator,
   not the remaining gold. Verify payload hashes and ID coverage inside it,
   compare ordinary Python, then attempt a changed-ID reload and require rejection.
   Fresh private state, disabled typed transport, `/usr/bin/false` generator,
   empty model trace and zero judge attempts. Retain binary hash and all commands.

## Bars and limits

Feasibility passes only if raw-p exact variance is <= half uniform variance, its
simulated MSE ratio is <=0.60 at **each** fixed audit size, and the actual public
workflow agrees with ordinary Python. Otherwise stop this angle here. No
production feature or new live campaign follows automatically from a pass.
Sample variance zero on a small audit cannot prove no population errors.

The exercise is capped at 10 minutes CPU/wall time and zero inference requests.
Code has independent exhaustive tiny-population tests, anti-predictor controls,
strict IDs/types/nonfinite rejection, and exclusive output creation. Source data
and licenses remain under `../DATA-NOTICES.md`. A failure is retained, not repaired
by changing seeds, audit sizes or predictors after outcomes are observed.

If useful, the next *separate* study is a fresh >=100-case independently labeled
corpus with a predeclared audit budget and a genuinely external labeler. Compare
end-to-end estimation error, label acquisition time, total model time and actual
billed costs against uniform auditing and simple deterministic stratification.
That fresh study is not claimed by this diagnostic.
