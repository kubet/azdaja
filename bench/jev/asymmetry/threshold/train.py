#!/usr/bin/env python3
"""Select and freeze the row645-only asymmetry decision threshold offline."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
DEFAULT_RESULT = ROOT / "bench/jev/row645_labels/result.json"
DEFAULT_AUDIT = ROOT / "bench/jev/row645_labels/audit.py"
DEFAULT_PLAN = HERE / "PLAN.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_training_rows(result_path: Path) -> list[dict[str, Any]]:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    data = json.loads(result_path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    if data.get("schema") != "azdaja.row645_official_item_gold.v1":
        raise ValueError("training input is not the audited row645 official-label result")
    rows = data.get("occurrence_ledger")
    if not isinstance(rows, list) or len(rows) != 227:
        raise ValueError("expected exactly the original 227 row645 judgments")
    required = {"id", "p_ham", "gold_ham"}
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("row must be a mapping")
        if not required <= row.keys():
            raise ValueError("row645 ledger row lacks p_ham or gold_ham")
        if type(row["id"]) is not str or not row["id"] or row["id"] in seen:
            raise ValueError("invalid or duplicate ID")
        seen.add(row["id"])
        if type(row["p_ham"]) not in (int, float) or not math.isfinite(row["p_ham"]) or not 0 <= row["p_ham"] <= 1:
            raise ValueError("p_ham must be a probability in [0, 1]")
        if not isinstance(row["gold_ham"], bool):
            raise ValueError("gold_ham must be boolean")
    if data.get("may_occurrences") != 227 or data.get("aligned_official_ham") != 132:
        raise ValueError("row645 official-label aggregate does not match the audited 227-row input")
    if sum(row["gold_ham"] for row in rows) != 132:
        raise ValueError("row645 per-item labels disagree with aggregate")
    return rows


def score(rows: Iterable[dict[str, Any]], threshold_cents: int) -> dict[str, Any]:
    """Score unchanged semantics: predict ham exactly when p_ham >= threshold."""
    rows = list(rows)
    if type(threshold_cents) is not int or not 0 <= threshold_cents <= 100:
        raise ValueError("threshold cents must be an integer in [0,100]")
    threshold = threshold_cents / 100
    false_positive_ids = [
        row["id"] for row in rows if row["p_ham"] >= threshold and not row["gold_ham"]
    ]
    false_negative_ids = [
        row["id"] for row in rows if row["p_ham"] < threshold and row["gold_ham"]
    ]
    return {
        "threshold": f"{threshold:.2f}",
        "threshold_cents": threshold_cents,
        "false_positives": len(false_positive_ids),
        "false_negatives": len(false_negative_ids),
        "total_fp_fn": len(false_positive_ids) + len(false_negative_ids),
        "correct": len(rows) - len(false_positive_ids) - len(false_negative_ids),
        "false_positive_ids": false_positive_ids,
        "false_negative_ids": false_negative_ids,
    }


def select(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidates = [score(rows, cents) for cents in range(101)]
    selected = min(
        candidates,
        key=lambda candidate: (
            candidate["total_fp_fn"],
            abs(candidate["threshold_cents"] - 50),
            -candidate["threshold_cents"],
        ),
    )
    return selected, candidates


def train(result_path: Path = DEFAULT_RESULT, audit_path: Path = DEFAULT_AUDIT,
          plan_path: Path = DEFAULT_PLAN, output_path: Path = HERE / "training-freeze.json") -> dict[str, Any]:
    rows = load_training_rows(result_path)
    selected, candidates = select(rows)
    freeze = {
        "schema_version": 1,
        "schema": "azdaja.asymmetry.threshold_training_freeze.v1",
        "status": "stable_training_freeze",
        "selection": {
            "dataset": "original row645",
            "observations": len(rows),
            "labels": "official gold_ham from audited row645 result",
            "probability_field": "p_ham",
            "prediction_semantics": "p_ham >= threshold",
            "threshold_grid": "0.00..1.00 inclusive, step 0.01",
            "primary_objective": "minimize total FP+FN",
            "tie_break": ["closest to 0.50", "larger threshold"],
            "selected": selected,
            "candidates": candidates,
        },
        "training_inputs": {
            "plan": {"path": str(plan_path), "sha256": sha256_file(plan_path)},
            "script": {"path": str(Path(__file__)), "sha256": sha256_file(Path(__file__))},
            "row645_result": {"path": str(result_path), "sha256": sha256_file(result_path)},
            "row645_audit_source": {"path": str(audit_path), "sha256": sha256_file(audit_path)},
        },
        "post_hoc_disclosure": (
            "Post-hoc training after previous headline results were known to the coordinator; "
            "not preregistered blind generalization. Do not transfer to row651 until root commits "
            "this freeze and explicitly authorizes one offline transfer."
        ),
        "transfer_guardrails": {
            "row651_applied": False,
            "required_overlap_audit": ["exact full source record", "normalized message text"],
            "overlap_excluded_from_full_headline_score": False,
        },
    }
    with output_path.open("x", encoding="utf-8") as out:
        out.write(json.dumps(freeze, sort_keys=True, indent=2) + "\n")
    return freeze


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output", type=Path, default=HERE / "training-freeze.json")
    args = parser.parse_args()
    freeze = train(args.result, args.audit, args.plan, args.output)
    print(json.dumps({"selected_threshold": freeze["selection"]["selected"]["threshold"],
                      "total_fp_fn": freeze["selection"]["selected"]["total_fp_fn"],
                      "output": str(args.output)}))


if __name__ == "__main__":
    main()
