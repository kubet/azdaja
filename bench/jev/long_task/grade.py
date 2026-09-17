#!/usr/bin/env python3
"""Strict offline CUAD presence-screening replay, not legal conclusions.

Annotation correctness and structural/citation validity are separate: bad quotes
never remove a panel or erase its predicted label. Missing/malformed labels stay
unobserved in a complete 102 x 5 matrix. Unknown gold positives count as FN.
Unknown gold negatives are separately reported and add one F1 denominator
penalty, just like an incorrect prediction, without being called false positives.
All accuracy denominators remain fixed. Query truth uses strong Kleene logic.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

FIELDS = ("assignment", "change_control", "termination", "liability_cap", "liability_uncapped")
QUERIES = ("transfer_exposure", "exit_with_uncapped", "mixed_liability", "transfer_without_convenience")
IDS = tuple("d%03d" % i for i in range(102))
# The task source is ctx: the exact published corpus.json bytes, not the
# original official-test.json archive member (tracked only in provenance).
CORPUS_SHA256 = "13becf55040029ba2521a62e91ced46591375ca63c53e88a4ad3ec94ee006310"
GOLD_SHA256 = "a31d13ccc5eb6e36ba7bb1fee4b176374bb524687a8424f73a48129c514b1e29"
LABELS = ("yes", "no", "unknown")


class InvalidGold(ValueError):
    pass


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8", errors="backslashreplace")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load_json(path):
    def invalid_constant(value):
        raise ValueError("non-JSON numeric constant: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def validate_fixtures(corpus, gold):
    # Content pins validate official annotation provenance, not just plausible
    # substrings. Canonical hashes tolerate JSON formatting, not semantic edits.
    try:
        if hashlib.sha256(canonical(corpus)).hexdigest() != CORPUS_SHA256:
            raise InvalidGold("corpus differs from the complete pinned official source projection")
        if hashlib.sha256(canonical(gold)).hexdigest() != GOLD_SHA256:
            raise InvalidGold("gold differs from the pinned official expert annotations")
        if [d["id"] for d in corpus["contracts"]] != list(IDS):
            raise InvalidGold("invalid corpus document IDs")
        if [d["id"] for d in gold["contracts"]] != list(IDS):
            raise InvalidGold("invalid gold document IDs")
        question_ids = set()
        for doc, record in zip(corpus["contracts"], gold["contracts"]):
            if set(record["annotations"]) != set(FIELDS):
                raise InvalidGold("invalid gold categories")
            for annotation in record["annotations"].values():
                if type(annotation["present"]) is not bool or annotation["present"] != bool(annotation["answers"]):
                    raise InvalidGold("invalid gold presence")
                qid = annotation["question_id"]
                if qid in question_ids:
                    raise InvalidGold("duplicate gold question ID")
                question_ids.add(qid)
                for answer in annotation["answers"]:
                    start, text = answer["answer_start"], answer["text"]
                    if type(start) is not int or start < 0 or not text or doc["text"][start:start + len(text)] != text:
                        raise InvalidGold("invalid gold span alignment")
        return {d["id"]: d for d in corpus["contracts"]}, {d["id"]: d["annotations"] for d in gold["contracts"]}
    except InvalidGold:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise InvalidGold("malformed fixtures: " + str(error)) from error


def tri_or(a, b):
    if "yes" in (a, b):
        return "yes"
    return "no" if a == b == "no" else "unknown"


def tri_and(a, b):
    if "no" in (a, b):
        return "no"
    return "yes" if a == b == "yes" else "unknown"


def tri_not(a):
    return {"yes": "no", "no": "yes"}.get(a, "unknown")


def query_labels(fields):
    p = {key: fields.get(key) or "unknown" for key in FIELDS}
    transfer = tri_or(p["assignment"], p["change_control"])
    return dict(zip(QUERIES, (
        transfer,
        tri_and(p["termination"], p["liability_uncapped"]),
        tri_and(p["liability_cap"], p["liability_uncapped"]),
        tri_and(transfer, tri_not(p["termination"])),
    )))


def citation(text, quote, expert_answers):
    """Evaluate ALL overlapping exact occurrences, not just the first match.

    Python string matching is codepoint-exact, and hence UTF-8 byte-exact for
    these unchanged valid Unicode strings. Length/overlap units are characters.
    Support requires >=80% overlap with ONE expert span, not a union of spans.
    """
    if not isinstance(quote, str) or not quote:
        return {"exact_substring": False, "quote_valid": False, "supported": False,
                "best_expert_overlap": 0.0, "occurrences": 0}
    start, occurrences, best_overlap = 0, 0, 0
    while True:
        position = text.find(quote, start)
        if position < 0:
            break
        occurrences += 1
        for answer in expert_answers:
            left = max(position, answer["answer_start"])
            right = min(position + len(quote), answer["answer_start"] + len(answer["text"]))
            best_overlap = max(best_overlap, max(0, right - left))
        start = position + 1
    valid = 20 <= len(quote) <= 600 and occurrences > 0
    return {"exact_substring": occurrences > 0, "quote_valid": valid,
            "supported": valid and best_overlap * 5 >= len(quote) * 4,
            "best_expert_overlap": best_overlap / len(quote), "occurrences": occurrences}


def metrics(pairs):
    """Pairs are (gold bool, predicted label or None for unobserved)."""
    result = dict.fromkeys(("TP", "TN", "FP", "FN", "unknown", "unobserved",
                           "unknown_negative", "unobserved_negative"), 0)
    for truth, label in pairs:
        if label in (None, "unknown"):
            kind = "unobserved" if label is None else "unknown"
            result[kind] += 1
            if truth:
                result["FN"] += 1
            else:
                result[kind + "_negative"] += 1
        else:
            result[("TP" if truth else "FP") if label == "yes" else ("FN" if truth else "TN")] += 1
    penalty = result["unknown_negative"] + result["unobserved_negative"]
    denominator = 2 * result["TP"] + result["FP"] + result["FN"] + penalty
    result.update({"total": len(pairs), "correct": result["TP"] + result["TN"],
                   "unknown_negative_penalty": penalty,
                   "accuracy": (result["TP"] + result["TN"]) / len(pairs) if pairs else 0.0,
                   "f1": 2 * result["TP"] / denominator if denominator else 1.0})
    return result


def _keys(value, expected, where, errors):
    if not isinstance(value, dict):
        errors.append(where + ": expected object")
        return False
    missing, extra = set(expected) - set(value), set(value) - set(expected)
    if missing:
        errors.append(where + ": missing keys " + repr(sorted(missing)))
    if extra:
        errors.append(where + ": extra keys " + repr(sorted(extra)))
    return True


def grade(prediction, corpus, gold):
    documents, annotations = validate_fixtures(corpus, gold)
    errors, panels, seen = [], {}, set()
    observed_order = []
    if not _keys(prediction, ("source_sha256", "contracts", "queries"), "output", errors):
        prediction = {}
    if prediction.get("source_sha256") != CORPUS_SHA256:
        errors.append("source_sha256: missing or incorrect sha256(ctx) corpus-byte hash")
    records = prediction.get("contracts")
    if not isinstance(records, list):
        errors.append("contracts: expected array")
        records = []
    for index, record in enumerate(records):
        where = "contracts[%d]" % index
        if not _keys(record, ("id", "fields"), where, errors):
            continue
        doc_id = record.get("id")
        if not isinstance(doc_id, str) or doc_id not in IDS:
            errors.append(where + ": invalid document ID " + repr(doc_id))
            continue
        if doc_id in seen:
            errors.append(where + ": duplicate document ID " + doc_id + "; first occurrence retained")
            continue
        seen.add(doc_id)
        observed_order.append(doc_id)
        fields = record.get("fields")
        if not _keys(fields, FIELDS, doc_id + ".fields", errors):
            continue
        panels[doc_id] = fields
    if observed_order != [doc_id for doc_id in IDS if doc_id in seen]:
        errors.append("contracts: unique recognized document rows must follow source order")
    missing_ids = [doc_id for doc_id in IDS if doc_id not in seen]
    if missing_ids:
        errors.append("contracts: missing IDs " + ",".join(missing_ids))
    matrix, per_field_pairs = [], {key: [] for key in FIELDS}
    partitions = {key: {label: [] for label in LABELS} for key in QUERIES}
    predicted_yes = exact_citations = supported_citations = 0
    for doc_id in IDS:
        cells, labels = {}, {}
        for key in FIELDS:
            where = doc_id + "." + key
            raw = panels.get(doc_id, {}).get(key)
            truth = annotations[doc_id][key]["present"]
            label, quote = None, None
            if raw is not None:
                if _keys(raw, ("label", "quote"), where, errors):
                    proposed = raw.get("label")
                    if isinstance(proposed, str) and proposed in LABELS:
                        label = proposed
                    else:
                        errors.append(where + ": invalid label")
                    quote = raw.get("quote")
            else:
                errors.append(where + ": unobserved field")
            info = {"exact_substring": False, "quote_valid": False, "supported": False,
                    "best_expert_overlap": 0.0, "occurrences": 0}
            if label == "yes":
                predicted_yes += 1
                info = citation(documents[doc_id]["text"], quote, annotations[doc_id][key]["answers"])
                exact_citations += info["quote_valid"]
                supported_citations += truth and info["supported"]
                if not info["quote_valid"]:
                    errors.append(where + ": YES quote must be 20..600 characters and exact substring of same document")
            elif label in ("no", "unknown") and quote != "":
                errors.append(where + ": no/unknown quote must be empty string")
            labels[key] = label
            cells[key] = {"gold_present": truth, "label": label, "observed": label is not None,
                          "quote": quote, "correct": label == ("yes" if truth else "no"), **info}
            per_field_pairs[key].append((truth, label))
        for key, label in query_labels(labels).items():
            partitions[key][label].append(doc_id)
        matrix.append({"id": doc_id, "fields": cells})
    declared_queries = prediction.get("queries")
    query_structure_errors = []
    declared_consistent = True
    if _keys(declared_queries, QUERIES, "queries", query_structure_errors):
        for name in QUERIES:
            declared = declared_queries.get(name)
            if not _keys(declared, LABELS, "queries." + name, query_structure_errors):
                declared_consistent = False
                continue
            ids_seen = set()
            for label in LABELS:
                entries = declared.get(label)
                if not isinstance(entries, list):
                    query_structure_errors.append("queries." + name + "." + label + ": expected array")
                    declared_consistent = False
                    continue
                clean_ids = set()
                for doc_id in entries:
                    if not isinstance(doc_id, str) or doc_id not in IDS or doc_id in ids_seen:
                        query_structure_errors.append("queries." + name + ": invalid/duplicate ID " + repr(doc_id))
                    else:
                        clean_ids.add(doc_id)
                        ids_seen.add(doc_id)
                if entries != partitions[name][label]:
                    query_structure_errors.append("queries." + name + "." + label + ": must match recomputed source-order list")
                    declared_consistent = False
                if clean_ids != set(partitions[name][label]):
                    declared_consistent = False
            if ids_seen != set(IDS):
                query_structure_errors.append("queries." + name + ": incomplete 102-ID partition")
    else:
        declared_consistent = False
    if query_structure_errors:
        declared_consistent = False
    errors.extend(query_structure_errors)
    if not declared_consistent:
        errors.append("queries: declared sets differ from recomputed three-valued partitions or are malformed")
    per_field = {key: metrics(pairs) for key, pairs in per_field_pairs.items()}
    aggregate = metrics([pair for pairs in per_field_pairs.values() for pair in pairs])
    aggregate["macro_f1"] = sum(m["f1"] for m in per_field.values()) / len(FIELDS)
    query_scores = {}
    for name in QUERIES:
        positives = set(gold["query_sets"][name])
        labels = {doc_id: label for label, ids in partitions[name].items() for doc_id in ids}
        score = metrics([(doc_id in positives, labels[doc_id]) for doc_id in IDS])
        score["exact_match"] = not partitions[name]["unknown"] and set(partitions[name]["yes"]) == positives
        score["gold_yes"] = sorted(positives)
        query_scores[name] = score
    return {"source_sha256": CORPUS_SHA256,
            "semantics": "Expert-annotation presence screening with quotes, not legal conclusions.",
            "structural": {"valid": not errors, "errors": errors, "missing_ids": missing_ids,
                           "observed_cells": sum(c["observed"] for row in matrix for c in row["fields"].values()),
                           "expected_cells": 510},
            "matrix": matrix, "per_field": per_field, "aggregate": aggregate,
            "citations": {"predicted_yes": predicted_yes, "exact_citations": exact_citations,
                          "supported_citations": supported_citations,
                          "exact_citation_rate": exact_citations / predicted_yes if predicted_yes else 0.0,
                          "correctly_supported_citation_rate": supported_citations / predicted_yes if predicted_yes else 0.0,
                          "definition": "Rates over all predicted YES. Exact requires 20..600 chars in same document. Supported additionally requires gold YES and >=80% character overlap with one expert span at any exact occurrence."},
            "queries": {"declared_consistent": declared_consistent, "recomputed": partitions, "scores": query_scores},
            "scoring": {"accuracy_denominator": 510,
                        "f1": "2TP/(2TP+FP+FN+unknown_negative+unobserved_negative). Unknown/unobserved positives are FN. Empty denominator scores 1.",
                        "unknowns": "Missing/malformed labels remain null and unobserved. Queries treat these as unknown using strong Kleene logic."}}


def compare_reports(first, second):
    """No structural filter: even invalid panels remain in offline comparison."""
    return {"accuracy_delta": second["aggregate"]["accuracy"] - first["aggregate"]["accuracy"],
            "macro_f1_delta": second["aggregate"]["macro_f1"] - first["aggregate"]["macro_f1"],
            "exact_citation_rate_delta": second["citations"]["exact_citation_rate"] - first["citations"]["exact_citation_rate"],
            "supported_citation_rate_delta": second["citations"]["correctly_supported_citation_rate"] - first["citations"]["correctly_supported_citation_rate"],
            "first_structurally_valid": first["structural"]["valid"],
            "second_structurally_valid": second["structural"]["valid"]}


def replay(path, corpus, gold):
    try:
        prediction = load_json(path)
    except (ValueError, UnicodeError) as error:
        report = grade(None, corpus, gold)
        report["structural"]["errors"].insert(0, "invalid prediction JSON: " + str(error))
        return report
    return grade(prediction, corpus, gold)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prediction", type=Path)
    parser.add_argument("--fixtures", type=Path, default=Path(__file__).parent / "fixtures")
    parser.add_argument("--compare", type=Path, help="second offline prediction, never a model request")
    parser.add_argument("--output", type=Path, help="exclusive new report file, otherwise stdout")
    args = parser.parse_args(argv)
    try:
        corpus = load_json(args.fixtures / "corpus.json")
        gold = load_json(args.fixtures / "gold.json")
        report = replay(args.prediction, corpus, gold)
        if args.compare:
            second = replay(args.compare, corpus, gold)
            report = {"first": report, "second": second, "comparison": compare_reports(report, second)}
        data = canonical(report)
        if args.output:
            with args.output.open("xb") as stream:
                stream.write(data)
        else:
            sys.stdout.write(data.decode("utf-8"))
    except (OSError, ValueError, TypeError) as error:
        print("GRADING FAILED: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
