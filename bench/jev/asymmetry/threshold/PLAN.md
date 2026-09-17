# Threshold training freeze plan

## Scope

This directory contains the post-hoc threshold selection workflow for the asymmetry experiment. It is the only directory this task may modify. The workflow must not inspect, load, or use `row651` predictions during selection.

## Selection rule

1. Use only the original 227 `row645` judgments and official labels, as represented by the audited `bench/jev/row645_labels/audit.py` source and `result.json`.
2. Evaluate thresholds exactly `0.00, 0.01, ..., 1.00`.
3. Preserve unchanged `p >= threshold` prediction semantics.
4. Select the threshold minimizing total `FP + FN` on row645.
5. Break ties by choosing the threshold closest to `0.50`, then the larger threshold.
6. Do not fit a count target, calibration curve, or rerun any provider.

## Reproducibility and status

`train.py` will record exact hashes for this plan, the training script, and the training input files, plus the selected threshold and full candidate score table in `training-freeze.json`.

This is post-hoc training after previous headline results were known to the coordinator. It was not preregistered blind generalization. The resulting freeze must not be applied to row651 until the root coordinator commits this freeze and explicitly authorizes one offline transfer.

## Deferred transfer safeguards

The later row651 transfer must include an overlap audit by exact full source record and normalized message text because rows may share corpus. Overlap must not be excluded from the full headline score.
