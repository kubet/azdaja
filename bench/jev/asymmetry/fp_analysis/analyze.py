#!/usr/bin/env python3
"""Deterministic, offline characterization of the frozen row651 errors.

This script only reads the frozen result, the unchanged Oolong context, and
optionally writes new artifacts beside this file.  Lexical clusters are
descriptive heuristics, not relabels or causal findings.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import unicodedata
from decimal import Decimal
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DEFAULT_RESULT = ROOT / "bench/jev/row651_labels/result.json"
DEFAULT_SOURCE = ROOT / "bench/oolong/context-1048576.txt"
RESULT_SHA = "65f5bf14c9c3546cc030b95adcfaaa10ec3b40586fdc06f7bdfc469f92242e13"

CLUSTERS = (
    ("paid_or_subscription_service", r"\b(?:charged|charge|cost|£|gbp|premium|subscription|unsubscribe|stop|club tones?|ringtone|tone|service you ordered|top up)\b"),
    ("prize_competition_or_promotion", r"\b(?:won|win|winner|prize|draw|competition|comp|voucher|free entry|offer|claim|guaranteed|cash|reward)\b"),
    ("adult_or_dating_chat", r"\b(?:horny|sexy|babes?|hunks?|adult|chat|cum over|naughty|dating|gaytext|hot pic)\b"),
    ("account_payment_or_security", r"\b(?:account|statement|points|bank|payment|invoice|password|security|identifier|user id)\b"),
    ("sports_or_trivia", r"\b(?:football|soccer|cricket|rugby|hockey|quiz|trivia|correct or incorrect|answer|reply end)\b"),
    ("delivery_or_transaction_notice", r"\b(?:order|ordered|delivered|delivery|received|reference|booking|ticket|appointment|outbid|bid)\b"),
    ("ordinary_personal_conversation", r"\b(?:sorry|missed your call|call later|love you|good morning|want me to|are you available|talk when|see you)\b"),
)
COMPILED = tuple((name, re.compile(pattern, re.I)) for name, pattern in CLUSTERS)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def instance(raw: str) -> str:
    marker = " || Instance: "
    return (raw.split(marker, 1)[1] if marker in raw else raw).rstrip("\r\n")


def normalized(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def dependence(rows, key):
    counts = collections.Counter(key(r) for r in rows)
    errors = [r for r in rows if (r["p_ham"] >= .5) != r["gold_ham"]]
    error_counts = collections.Counter(key(r) for r in errors)
    return {"unique": len(counts), "repeated_groups": sum(v > 1 for v in counts.values()),
            "occurrences_in_repeated_groups": sum(v for v in counts.values() if v > 1),
            "duplicate_occurrences_beyond_first": len(rows) - len(counts),
            "max_group_size": max(counts.values(), default=0),
            "errors_in_repeated_groups": sum(counts[key(r)] > 1 for r in errors),
            "distinct_error_groups": len(error_counts)}


def cluster(text: str) -> str:
    for name, pattern in COMPILED:
        if pattern.search(text):
            return name
    return "other"


def template(text: str) -> str:
    """Stable coarse template key, retaining words but masking volatile fields."""
    s = text.lower()
    s = re.sub(r"https?://\S+|www\.\S+", "<url>", s)
    s = re.sub(r"\b(?:\+?\d[\d .()/-]{6,}\d)\b", "<phone>", s)
    s = re.sub(r"\b\d+\b", "<num>", s)
    s = re.sub(r"\b[a-f0-9]{5,}\b", "<code>", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def percentile(values, q: float):
    if not values:
        return None
    values = sorted(values)
    return values[min(len(values) - 1, int(q * (len(values) - 1)))]


def distribution(rows, kind: str):
    bins = [(0.0, .1), (.1, .2), (.2, .3), (.3, .4), (.4, .5), (.5, .6), (.6, .7), (.7, .8), (.8, .9), (.9, 1.0000001)]
    out = []
    for lo, hi in bins:
        selected = [r for r in rows if lo <= r["p_ham"] < hi]
        out.append({"lower": lo, "upper": min(1.0, hi), "n": len(selected), "ids": [r["id"] for r in selected]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--output-dir", type=Path, default=HERE)
    args = ap.parse_args()
    result_bytes = args.result.read_bytes()
    if sha256(result_bytes) != RESULT_SHA:
        raise ValueError("frozen result changed")
    source = args.source.read_bytes()
    result = json.loads(result_bytes)
    rows = result["occurrence_ledger"]
    assert sha256(source) == result["unlabeled_context_sha256"]
    assert len(source) == 2693859
    enriched = []
    for row in rows:
        raw_bytes = source[row["byte_start"]:row["byte_end"]]
        assert sha256(raw_bytes) == row["record_sha256"]
        raw = raw_bytes.decode("utf-8")
        assert raw.startswith("Date:") and raw.endswith("\n")
        enriched.append({**row, "raw": raw.rstrip("\r\n"), "instance": instance(raw),
                         "cluster": cluster(instance(raw)), "template": template(instance(raw))})
    errors = [r for r in enriched if (r["p_ham"] >= .5) != r["gold_ham"]]
    fps = [r for r in errors if not r["gold_ham"]]
    fns = [r for r in errors if r["gold_ham"]]
    error_ids = {r["id"] for r in errors}
    assert len(rows) == 17469 and len(fps) == 641 and len(fns) == 34

    def summarize(key):
        groups = collections.defaultdict(list)
        for r in enriched:
            groups[r[key]].append(r)
        out = []
        for value, group in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
            e = [r for r in group if r["id"] in error_ids]
            fp = [r for r in e if not r["gold_ham"]]
            fn = [r for r in e if r["gold_ham"]]
            controls = len(group) - len(e)
            gold_ham = sum(r["gold_ham"] for r in group)
            gold_spam = len(group) - gold_ham
            out.append({"key": value, "denominator_n": len(group), "error_n": len(e),
                        "fp_n": len(fp), "fn_n": len(fn), "control_n": controls,
                        "gold_ham_n": gold_ham, "gold_spam_n": gold_spam,
                        "false_positive_rate": len(fp) / gold_spam if gold_spam else None,
                        "false_negative_rate": len(fn) / gold_ham if gold_ham else None,
                        "error_rate": len(e) / len(group),
                        "error_prevalence": len(e) / len(errors),
                        "error_to_correct_ratio": (len(e) / controls if controls else None),
                        "enrichment_vs_panel": (len(e) / len(group)) / (len(errors) / len(enriched)),
                        "example_ids": [r["id"] for r in sorted(e, key=lambda x: x["id"])[:3]]})
        return out

    d = Decimal
    sum_noul = sum((d(str(r["p_ham"])) for r in enriched), d(0))
    confident = [r for r in errors if max(r["p_ham"], 1 - r["p_ham"]) >= .9]
    summary = {
        "schema": "azdaja.row651_error_characterization.v1",
        "inputs": {"result_sha256": sha256(result_bytes), "source_sha256": sha256(source),
                   "result_path": str(args.result), "source_path": str(args.source), "threshold": .5},
        "denominators": {"observed_n": len(enriched), "gold_ham_n": sum(r["gold_ham"] for r in enriched),
                         "gold_spam_n": sum(not r["gold_ham"] for r in enriched), "error_n": len(errors),
                         "fp_n": len(fps), "fn_n": len(fns), "correct_control_n": len(enriched) - len(errors)},
        "metrics": {"fpr": len(fps) / sum(not r["gold_ham"] for r in enriched),
                    "fnr": len(fns) / sum(r["gold_ham"] for r in enriched),
                    "sumNoul": float(sum_noul), "sumNoul_decimal": str(sum_noul),
                    "sumNoul_minus_gold": float(sum_noul - d(sum(r["gold_ham"] for r in enriched))),
                    "confident_error_n": len(confident), "confident_error_fraction": len(confident) / len(errors),
                    "fp_confident_n": sum(r["p_ham"] >= .9 for r in fps), "fp_confident_fraction": sum(r["p_ham"] >= .9 for r in fps) / len(fps),
                    "fn_confident_n": sum(r["p_ham"] <= .1 for r in fns), "fn_confident_fraction": sum(r["p_ham"] <= .1 for r in fns) / len(fns)},
        "confidence_distribution": {"all_errors": distribution(errors, "error"), "false_positives": distribution(fps, "fp"), "false_negatives": distribution(fns, "fn")},
        "lexical_clusters": summarize("cluster"), "template_clusters": summarize("template"),
        "repeated_message_dependence": {
            "full_record": dependence(enriched, lambda r: r["record_sha256"]),
            "exact_instance": dependence(enriched, lambda r: r["instance"]),
            "normalized_instance": dependence(enriched, lambda r: normalized(r["instance"])),
            "normalization": "Instance only, NFKC, casefold, whitespace collapse; dates/users excluded"},
    }
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "analysis.json").write_bytes(canonical(summary) + b"\n")
    with (out / "errors.jsonl").open("w", encoding="utf-8") as f:
        for r in sorted(errors, key=lambda x: x["id"]):
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"status": "passed", "observed": len(rows), "fp": len(fps), "fn": len(fns), "sumNoul": str(sum_noul)}))


if __name__ == "__main__":
    main()
