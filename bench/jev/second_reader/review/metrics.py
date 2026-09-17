"""Descriptive metrics for the fixed row645 two-prediction panel.

This module is intentionally provider-free. It consumes retained occurrence
records and does not alter official labels or infer new gold labels.
"""
from __future__ import annotations

from collections import Counter
from math import fsum, isfinite
from numbers import Real
from typing import Any, Iterable, Mapping

Record = Mapping[str, Any]


def _records(records: Iterable[Record]) -> list[Record]:
    result = list(records)
    if not result:
        raise ValueError("at least one record is required")
    seen_ids: set[str] = set()
    for record in result:
        for key in ("id", "p_ham", "gold_ham", "typed_ham", "direct_ham"):
            if key not in record:
                raise KeyError(key)
        record_id = record["id"]
        if not isinstance(record_id, str) or not record_id:
            raise TypeError("id must be a non-empty string")
        if record_id in seen_ids:
            raise ValueError(f"duplicate id: {record_id}")
        seen_ids.add(record_id)

        raw_probability = record["p_ham"]
        if isinstance(raw_probability, bool) or not isinstance(raw_probability, Real):
            raise TypeError("p_ham must be a real number, not bool")
        probability = float(raw_probability)
        if not isfinite(probability):
            raise ValueError("p_ham must be finite")
        if not 0.0 <= probability <= 1.0:
            raise ValueError("p_ham must be in [0, 1]")

        for key in ("gold_ham", "typed_ham", "direct_ham"):
            if type(record[key]) is not bool:
                raise TypeError(f"{key} must be exactly bool")
        if record["typed_ham"] != (probability >= 0.5):
            raise ValueError("typed_ham must equal (p_ham >= 0.5)")
    return result


def brier_score(records: Iterable[Record]) -> float:
    """Return Brier score for retained ham probabilities and official gold."""
    checked = _records(records)
    return fsum(
        (float(record["p_ham"]) - int(bool(record["gold_ham"]))) ** 2
        for record in checked
    ) / len(checked)


def _bin_index(value: float, bin_count: int) -> int:
    if not isinstance(bin_count, int) or bin_count <= 0:
        raise ValueError("bin_count must be a positive integer")
    return min(bin_count - 1, int(value * bin_count))


def _empty_bins(bin_count: int) -> list[dict[str, Any]]:
    if not isinstance(bin_count, int) or bin_count <= 0:
        raise ValueError("bin_count must be a positive integer")
    precision = max(1, len(str(bin_count)) - 1)
    return [
        {
            "index": index,
            "lower": index / bin_count,
            "upper": (index + 1) / bin_count,
            "interval": (
                f"[{index / bin_count:.{precision}f}, "
                f"{(index + 1) / bin_count:.{precision}f}"
                + ("]" if index == bin_count - 1 else ")")
            ),
        }
        for index in range(bin_count)
    ]


def positive_probability_ece(records: Iterable[Record], bin_count: int) -> dict[str, Any]:
    """ECE for the binary positive probability p_ham.

    Bins are predeclared equal-width intervals [i/K, (i+1)/K), except that
    the final interval is closed at 1.0. The target rate is official gold_ham.
    """
    checked = _records(records)
    bins = _empty_bins(bin_count)
    for bucket in bins:
        bucket["count"] = 0
        bucket["mean_probability"] = None
        bucket["observed_positive_rate"] = None
        bucket["absolute_gap"] = None
        bucket["weighted_gap"] = 0.0

    assignments: list[list[Record]] = [[] for _ in bins]
    for record in checked:
        assignments[_bin_index(float(record["p_ham"]), bin_count)].append(record)

    total = len(checked)
    for bucket, members in zip(bins, assignments):
        bucket["count"] = len(members)
        if members:
            mean_probability = fsum(float(r["p_ham"]) for r in members) / len(members)
            observed_rate = fsum(int(bool(r["gold_ham"])) for r in members) / len(members)
            gap = abs(mean_probability - observed_rate)
            bucket["mean_probability"] = mean_probability
            bucket["observed_positive_rate"] = observed_rate
            bucket["absolute_gap"] = gap
            bucket["weighted_gap"] = len(members) / total * gap

    return {
        "definition": "binary positive-probability ECE; p_ham versus official gold_ham",
        "binning": "equal width; [lower, upper) except final [lower, 1.0]",
        "bin_count": bin_count,
        "ece": fsum(bucket["weighted_gap"] for bucket in bins),
        "bins": bins,
    }


def top_label_ece(records: Iterable[Record], bin_count: int) -> dict[str, Any]:
    """ECE for top-label confidence, where correctness is panel prediction vs gold."""
    checked = _records(records)
    bins = _empty_bins(bin_count)
    for bucket in bins:
        bucket["count"] = 0
        bucket["mean_confidence"] = None
        bucket["observed_accuracy"] = None
        bucket["absolute_gap"] = None
        bucket["weighted_gap"] = 0.0

    assignments: list[list[tuple[float, int]]] = [[] for _ in bins]
    for record in checked:
        probability = float(record["p_ham"])
        prediction_ham = probability >= 0.5
        confidence = max(probability, 1.0 - probability)
        correct = int(prediction_ham == bool(record["gold_ham"]))
        assignments[_bin_index(confidence, bin_count)].append((confidence, correct))

    total = len(checked)
    for bucket, members in zip(bins, assignments):
        bucket["count"] = len(members)
        if members:
            mean_confidence = fsum(item[0] for item in members) / len(members)
            accuracy = fsum(item[1] for item in members) / len(members)
            gap = abs(mean_confidence - accuracy)
            bucket["mean_confidence"] = mean_confidence
            bucket["observed_accuracy"] = accuracy
            bucket["absolute_gap"] = gap
            bucket["weighted_gap"] = len(members) / total * gap

    return {
        "definition": "top-label ECE; max(p_ham, 1-p_ham) versus prediction correctness",
        "binning": "equal width; [lower, upper) except final [lower, 1.0]",
        "bin_count": bin_count,
        "ece": fsum(bucket["weighted_gap"] for bucket in bins),
        "bins": bins,
    }


def agreement_table(records: Iterable[Record]) -> dict[str, Any]:
    """Return prediction-pair/gold counts and disagreement escalation summary."""
    checked = _records(records)
    counts: Counter[tuple[bool, bool, bool]] = Counter(
        (
            bool(record["typed_ham"]),
            bool(record["direct_ham"]),
            bool(record["gold_ham"]),
        )
        for record in checked
    )

    rows = []
    for typed_ham in (False, True):
        for direct_ham in (False, True):
            for gold_ham in (False, True):
                rows.append(
                    {
                        "typed_ham": typed_ham,
                        "direct_ham": direct_ham,
                        "gold_ham": gold_ham,
                        "count": counts[(typed_ham, direct_ham, gold_ham)],
                    }
                )

    agreement_ids = [
        record["id"] for record in checked if bool(record["typed_ham"]) == bool(record["direct_ham"])
    ]
    disagreement_ids = [
        record["id"] for record in checked if bool(record["typed_ham"]) != bool(record["direct_ham"])
    ]
    agreement_error_ids = [
        record["id"]
        for record in checked
        if bool(record["typed_ham"]) == bool(record["direct_ham"])
        and bool(record["typed_ham"]) != bool(record["gold_ham"])
    ]
    disagreement_error_ids = [
        record["id"]
        for record in checked
        if bool(record["typed_ham"]) != bool(record["direct_ham"])
        and bool(record["typed_ham"]) != bool(record["gold_ham"])
        and bool(record["direct_ham"]) != bool(record["gold_ham"])
    ]
    agreement_count = len(agreement_ids)
    disagreement_count = len(disagreement_ids)
    agreement_error_count = len(agreement_error_ids)
    return {
        "rows": rows,
        "agreement_count": agreement_count,
        "disagreement_count": disagreement_count,
        "agreement_ids": agreement_ids,
        "disagreement_ids": disagreement_ids,
        "agreement_error_ids": agreement_error_ids,
        "disagreement_error_ids": disagreement_error_ids,
        "actual_error_floor_on_agreement": {
            "meaning": "errors remaining when only model disagreements are escalated",
            "count": agreement_error_count,
            "rate_among_agreements": (
                agreement_error_count / agreement_count if agreement_count else None
            ),
            "rate_of_panel": agreement_error_count / len(checked),
        },
        "hypothetical_oracle_ceiling_if_all_disagreements_resolved": {
            "hypothetical": True,
            "meaning": "If a perfect oracle resolved every disagreement, agreement errors would remain",
            "resolved_disagreements": disagreement_count,
            "remaining_errors": agreement_error_count,
            "correct_count_ceiling": len(checked) - agreement_error_count,
            "accuracy_ceiling": (len(checked) - agreement_error_count) / len(checked),
        },
    }


def summarize(records: Iterable[Record]) -> dict[str, Any]:
    """Compute the requested fixed-panel metrics in one JSON-serializable object."""
    checked = _records(records)
    return {
        "n": len(checked),
        "brier_score": brier_score(checked),
        "positive_probability_ece": {
            "5": positive_probability_ece(checked, 5),
            "10": positive_probability_ece(checked, 10),
        },
        "top_label_ece": {
            "5": top_label_ece(checked, 5),
            "10": top_label_ece(checked, 10),
        },
        "agreement": agreement_table(checked),
    }
