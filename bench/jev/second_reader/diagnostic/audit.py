"""Offline audit of the retained flat-02 native measurement evidence.

This module deliberately does not call a provider, read a credential, or
reconstruct the discarded flat-02 body.  Its numeric checks mirror the public
shape and the Rust validator's f64 accumulation closely enough to expose
which retained records are auditable, but the report labels those checks as
offline evidence rather than a replacement for invoking the private Rust
seam.
"""

from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ORIGINAL = ROOT / "bench/jev/measurement_v2"
PREDECESSOR = ORIGINAL / "results/native-20260917"
CONTINUATION = ROOT / "bench/jev/measurement_followthrough/results/native-20260917"
JUDGE = ROOT / "src/judge.rs"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def strict_loads(raw: bytes) -> Any:
    """Load JSON with the same duplicate-key refusal used by native helpers."""

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def invalid(_: str) -> Any:
        raise ValueError("nonfinite JSON number")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def load(path: Path) -> Any:
    return strict_loads(path.read_bytes())


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def finite_probability(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(float(value)) and 0 <= value <= 1


def rust_sum(values: list[Any]) -> float:
    """The validator's `let mut sum = 0.0; sum += probability(value)` order."""

    total = 0.0
    for value in values:
        total += float(value)
    return total


def decimal_places(value: Any) -> int:
    # JSON numbers in the retained files are finite binary floats after Rust
    # parsing. Decimal(str(x)) reports the human-visible precision retained in
    # the serialized observation, rather than pretending to recover provider
    # precision beyond the JSON representation.
    decimal = Decimal(str(value)).normalize()
    return max(0, -decimal.as_tuple().exponent)


def valid_id(value: Any) -> bool:
    return (isinstance(value, str) and 0 < len(value) <= 256
            and not value.isspace() and not any(ord(c) < 32 for c in value))


def inspect_pack(pack: dict[str, Any]) -> dict[str, Any]:
    questions = pack.get("questions")
    if not isinstance(questions, dict) or not questions:
        raise ValueError("empty questions")
    if set(pack) - {"state", "questions", "model"} or "state" not in pack:
        raise ValueError("pack shape")
    if not isinstance(pack["state"], (str, dict, list)):
        raise ValueError("state shape")
    if len(canonical(pack["state"])) > 24000 or len(questions) > 64:
        raise ValueError("pack budget")
    for qid, question in questions.items():
        if not valid_id(qid) or not isinstance(question, dict):
            raise ValueError("question identity")
        if set(question) - {"type", "instructions", "criteria"}:
            raise ValueError("question fields")
        if not isinstance(question.get("instructions"), (str, dict, list)):
            raise ValueError("instructions")
        kind = question.get("type")
        if kind not in {"noul", "choice", "score"}:
            raise ValueError("question type")
        if kind == "choice":
            criteria = question.get("criteria")
            if (not isinstance(criteria, dict) or len(criteria) < 2
                    or any(not valid_id(k) or not (isinstance(v, str) or v is None)
                           for k, v in criteria.items())):
                raise ValueError("choice criteria")
        elif kind == "score":
            criteria = question.get("criteria")
            if (not isinstance(criteria, list) or len(criteria) < 2
                    or any(not isinstance(v, str) for v in criteria)):
                raise ValueError("score criteria")
    request = dict(state=pack["state"], questions=questions, model="jev-1.13.0")
    request_raw = canonical(request)
    if len(request_raw) > 131072:
        raise ValueError("request bytes")
    return request


def source_requirements(source: str) -> list[dict[str, Any]]:
    """Return a line-bound inventory, not a claim that this script is Rust."""

    required = [
        ("config identity, key name, timeout, request/question/byte/token limits", 43, 77),
        ("state shape and question schema/count", 153, 170),
        ("request serialization and request byte limit", 171, 177),
        ("cell cache, request/question/input budgets", 178, 200),
        ("credential syntax and request secret scan", 201, 207),
        ("response byte limit, duplicate-free JSON, response secret scan", 212, 234),
        ("usage token shape and reported input budget", 234, 245),
        ("returned model, exact answer coverage, all answer kinds", 474, 551),
        ("deadline and post-transport deadline checks", 132, 141),
        ("sanitized transport errors and poison-on-failure behavior", 212, 222),
    ]
    lines = source.splitlines()
    result = []
    for name, start, end in required:
        result.append({"requirement": name, "source_lines": [start, end],
                       "source_text_present": bool(lines[start - 1:end])})
    return result


def choice_metrics(answer: dict[str, Any], criteria: dict[str, Any]) -> dict[str, Any]:
    probabilities = answer["probabilities"]
    values = list(probabilities.values())
    total = rust_sum(values)
    ranked = sorted((float(value), key) for key, value in probabilities.items())
    selected = answer["choice"]
    selected_probability = float(probabilities[selected])
    runner_up = ranked[-2][0] if len(ranked) > 1 else None
    return {
        "option_count": len(criteria),
        "sum_f64": total,
        "sum_delta_f64": total - 1.0,
        "abs_sum_delta_f64": abs(total - 1.0),
        "abs_sum_delta_ulps_at_one": abs(total - 1.0) / math.ulp(1.0),
        "selected_probability": selected_probability,
        "runner_up_probability": runner_up,
        "winner_gap": selected_probability - runner_up if runner_up is not None else None,
        "max_probability_decimal_places": max(decimal_places(v) for v in values),
        "all_values_finite_0_to_1": all(finite_probability(v) for v in values),
        "domain_exact": set(probabilities) == set(criteria) and len(probabilities) == len(criteria),
        "winner_is_argmax": all(selected_probability >= float(v) for v in values),
    }


def audit_observation(path: Path, pack: dict[str, Any], event: dict[str, Any] | None) -> dict[str, Any]:
    if event is None or event.get("status") != "completed":
        raise ValueError(f"missing completed receipt event: {path.name}")
    envelope = load(path)
    if set(envelope) != {"observation", "stats"}:
        raise ValueError(f"unexpected observation envelope: {path.name}")
    body = envelope["observation"]
    request = inspect_pack(pack)
    answers = body.get("answers")
    if set(body) != {"model", "answers", "usage", "_azdaja"}:
        raise ValueError(f"unexpected annotated body fields: {path.name}")
    if body["model"] != "jev-1.13.0" or set(answers) != set(request["questions"]):
        raise ValueError(f"identity or answer coverage: {path.name}")
    if body["_azdaja"].get("request_sha256") != sha256(canonical(request)):
        raise ValueError(f"request digest mismatch: {path.name}")
    usage = body["usage"]
    if (not isinstance(usage, dict)
            or any(type(v) is not int or v < 0 for v in usage.values())):
        raise ValueError(f"usage shape: {path.name}")
    stats = envelope["stats"]
    if (stats.get("provider_requests") != 1 or stats.get("attempts") != 1
            or stats.get("cache_hits") != 0 or stats.get("poisoned") is not False
            or stats.get("unknown_input_usage_requests") != 0):
        raise ValueError(f"native accounting: {path.name}")

    kinds = Counter()
    choices: list[dict[str, Any]] = []
    noul_count = 0
    score_count = 0
    for qid, question in request["questions"].items():
        answer = answers[qid]
        if not isinstance(answer, dict) or answer.get("type") != question["type"]:
            raise ValueError(f"answer type: {path.name}:{qid}")
        kind = question["type"]
        kinds[kind] += 1
        if kind == "choice":
            required = {"type", "choice", "probabilities", "confidence"}
            if set(answer) != required or not finite_probability(answer["confidence"]):
                raise ValueError(f"choice fields: {path.name}:{qid}")
            metrics = choice_metrics(answer, question["criteria"])
            if not (metrics["domain_exact"] and metrics["all_values_finite_0_to_1"]
                    and abs(metrics["sum_delta_f64"]) <= 1e-6
                    and answer["choice"] in answer["probabilities"]
                    and metrics["winner_is_argmax"]):
                raise ValueError(f"choice numeric contract: {path.name}:{qid}")
            choices.append({"id": qid, **metrics})
        elif kind == "noul":
            noul_count += 1
            if set(answer) != {"type", "noul"} or not finite_probability(answer["noul"]):
                raise ValueError(f"noul fields: {path.name}:{qid}")
        else:
            score_count += 1
            raise ValueError(f"unexpected score in measurement: {path.name}:{qid}")

    return {
        "file": str(path.relative_to(ROOT)),
        "fixture": path.name.removesuffix("-typed-observation.json"),
        "questions": len(answers),
        "answer_kinds": dict(kinds),
        "usage": usage,
        "choice_answers": len(choices),
        "noul_answers": noul_count,
        "score_answers": score_count,
        "choice_option_cardinalities": dict(Counter(m["option_count"] for m in choices)),
        "choice_sum_abs_delta_max": max((m["abs_sum_delta_f64"] for m in choices), default=None),
        "choice_sum_abs_delta_min": min((m["abs_sum_delta_f64"] for m in choices), default=None),
        "choice_sum_abs_delta_ulps_max": max((m["abs_sum_delta_ulps_at_one"] for m in choices), default=None),
        "choice_winner_gap_min": min((m["winner_gap"] for m in choices), default=None),
        "choice_winner_gap_max": max((m["winner_gap"] for m in choices), default=None),
        "choice_decimal_places_max": max((m["max_probability_decimal_places"] for m in choices), default=None),
        "choice_sum_tolerance_margin_min": min((1e-6 - m["abs_sum_delta_f64"] for m in choices), default=None),
        "choices": choices,
        "event_response_sha256": event["response_sha256"],
        "computed_response_sha256": sha256(canonical(body)),
        "stats": stats,
    }


def event_map(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {f"{row['fixture']}-{row['arm']}": row for row in receipt["benchmark_rows"]}


def audit() -> dict[str, Any]:
    packs = load(ORIGINAL / "fixtures/packs.json")
    by_name = {row["name"]: row["pack"] for row in packs}
    original_receipt = load(PREDECESSOR / "receipt.json")
    continuation_receipt = load(CONTINUATION / "receipt.json")
    events = event_map(original_receipt) | event_map(continuation_receipt)

    successes = []
    for directory in (PREDECESSOR, CONTINUATION):
        for path in sorted(directory.glob("*-typed-observation.json")):
            if not path.exists():
                continue
            if load(path).get("failure") is not None:
                continue
            stem = path.name.removesuffix("-typed-observation.json")
            fixture = stem.removesuffix("-typed")
            successes.append(audit_observation(path, by_name[fixture], events.get(f"{fixture}-typed")))

    failed_path = PREDECESSOR / "flat-02-typed-observation.json"
    failed = load(failed_path)
    flat02_ids = sorted(by_name["flat-02"]["questions"])
    failure_audit = {
        "file": str(failed_path.relative_to(ROOT)),
        "envelope_keys": sorted(failed),
        "recorded_reason": failed.get("failure"),
        "stats": failed.get("stats"),
        "batch_questions": len(flat02_ids),
        "unjudged_ids": flat02_ids,
        "failed_response_count": 0,
        "interpretation": "one rejected batch containing 25 unjudged questions; not 25 independently observed failed responses",
        "raw_body_retained": False,
        "exact_cause_recoverable": False,
    }
    source = JUDGE.read_text()
    all_choice = [m for row in successes for m in row["choices"]]
    aggregate = {
        "successful_typed_observations": len(successes),
        "successful_typed_questions": sum(row["questions"] for row in successes),
        "choice_questions": len(all_choice),
        "noul_questions": sum(row["noul_answers"] for row in successes),
        "option_cardinalities": dict(Counter(m["option_count"] for m in all_choice)),
        "sum_abs_delta_f64_max": max((m["abs_sum_delta_f64"] for m in all_choice), default=None),
        "sum_abs_delta_f64_median": statistics.median(m["abs_sum_delta_f64"] for m in all_choice) if all_choice else None,
        "sum_abs_delta_ulps_max": max((m["abs_sum_delta_ulps_at_one"] for m in all_choice), default=None),
        "sum_tolerance_margin_min": min((1e-6 - m["abs_sum_delta_f64"] for m in all_choice), default=None),
        "winner_gap_min": min((m["winner_gap"] for m in all_choice), default=None),
        "winner_gap_max": max((m["winner_gap"] for m in all_choice), default=None),
        "probability_decimal_places_max": max((m["max_probability_decimal_places"] for m in all_choice), default=None),
        "all_retained_choice_sums_within_rust_tolerance": all(abs(m["sum_delta_f64"]) <= 1e-6 for m in all_choice),
        "all_retained_choice_domains_exact": all(m["domain_exact"] for m in all_choice),
        "all_retained_choice_winners_argmax": all(m["winner_is_argmax"] for m in all_choice),
    }
    return {
        "schema": "azdaja.second_reader.flat02_diagnostic.v1",
        "mode": "offline_only",
        "provider_calls": 0,
        "credential_reads": 0,
        "source": {"path": str(JUDGE.relative_to(ROOT)), "sha256": sha256(JUDGE.read_bytes())},
        "source_requirements": source_requirements(source),
        "retained_success_audit": {"aggregate": aggregate, "observations": successes},
        "rejected_flat02": failure_audit,
        "evidence_boundary": {
            "known": [
                "The predecessor receipt has one stopped typed flat-02 event.",
                "Its retained failure says probabilities must sum to one.",
                "The corresponding pack contains 25 question IDs, all unjudged.",
                "Eleven successful typed observations retain complete annotated bodies and are auditable offline.",
            ],
            "unknown": [
                "The rejected body's actual probability values, failing question ID, sum, precision, and byte sequence.",
                "Whether provider serialization, one question's distribution, or another upstream condition produced the rejection.",
            ],
            "do_not_infer": "The discarded body cannot support a rounding, provider, model, or question-specific causal claim.",
        },
        "best_next_step": "Run at most one explicitly authorized diagnostic request with exact request/model and bounded raw response retention at the Rust transport boundary; stop on the first malformed distribution or transport error and never use it to fill the old 25 judgments.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write the JSON report here")
    args = parser.parse_args(argv)
    report = audit()
    raw = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(raw)
    else:
        sys.stdout.write(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
