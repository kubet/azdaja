"""Finite-population audit estimators."""
import math


_PREDICTION_KEYS = {"id", "p"}
_AUDIT_KEYS = {"id", "label"}
_Z95 = 1.959963984540054


def _validate_predictions(predictions):
    if not isinstance(predictions, list) or not predictions:
        raise ValueError("predictions must be a non-empty list")
    seen = set()
    for row in predictions:
        if not isinstance(row, dict) or set(row) != _PREDICTION_KEYS:
            raise ValueError("each prediction must have exactly id and p")
        ident, probability = row["id"], row["p"]
        if not isinstance(ident, str) or not ident:
            raise ValueError("prediction id must be a non-empty string")
        if ident in seen:
            raise ValueError("duplicate prediction id")
        seen.add(ident)
        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise ValueError("prediction p must be a number")
        if not math.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError("prediction p must be finite and in [0, 1]")
    return seen


def _validate_audited(audited, prediction_ids):
    if not isinstance(audited, list) or not audited:
        raise ValueError("audited must be a non-empty list")
    seen = set()
    for row in audited:
        if not isinstance(row, dict) or set(row) != _AUDIT_KEYS:
            raise ValueError("each audit must have exactly id and label")
        ident, label = row["id"], row["label"]
        if not isinstance(ident, str) or not ident:
            raise ValueError("audit id must be a non-empty string")
        if ident in seen:
            raise ValueError("duplicate audit id")
        if ident not in prediction_ids:
            raise ValueError("audit id is not in predictions")
        if not isinstance(label, bool):
            raise ValueError("audit label must be bool")
        seen.add(ident)
    return seen


def estimate(predictions, audited):
    """Estimate a binary-outcome total from a uniform, trusted-label audit.

    The caller owns the sampling design and label quality. The normal interval
    is an asymptotic reference, not a finite-sample or optional-stopping bound.
    """
    prediction_ids = _validate_predictions(predictions)
    audited_ids = _validate_audited(audited, prediction_ids)
    if len(audited_ids) > len(prediction_ids):
        raise ValueError("audit cannot exceed population")
    by_id = {row["id"]: row["p"] for row in predictions}
    n, N = len(audited), len(predictions)
    labels = [1.0 if row["label"] else 0.0 for row in audited]
    prediction_total = math.fsum(by_id.values())
    uniform_total = (N / n) * sum(labels)
    if n == N:
        corrected_total = sum(labels)
        se = 0.0
        census = True
    else:
        residuals = [label - by_id[row["id"]] for row, label in zip(audited, labels)]
        corrected_total = prediction_total + (N / n) * math.fsum(residuals)
        if n < 2:
            se = None
        else:
            mean = sum(residuals) / n
            variance = sum((value - mean) ** 2 for value in residuals) / (n - 1)
            se = N * math.sqrt((1 - n / N) * variance / n)
        census = False
    normal_reference_95 = None if se is None else [corrected_total - _Z95 * se, corrected_total + _Z95 * se]
    return {
        "population_size": N,
        "audit_size": n,
        "prediction_total": prediction_total,
        "uniform_total": uniform_total,
        "corrected_total": corrected_total,
        "estimated_standard_error": se,
        "normal_reference_95": normal_reference_95,
        "interval_is_finite_sample_guarantee": False,
        "census": census,
    }
