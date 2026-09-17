#!/usr/bin/env python3
"""Offline, full-portfolio CUAD expert-annotation presence preparation.

No legal conclusions are inferred. Presence means a nonempty official expert
answer list, not an independent finding that the legal clause exists.
Outputs must go to a NEW directory. Generate in scratch and obtain root review
before publishing under fixtures/. Source contexts are never transformed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

COMMIT = "67faa0e6023b04fcaae6cc09497ab00e5d63a2a2"
ZIP_SHA256 = "f8161d18bea4e9c05e78fa6dda61c19c846fb8087ea969c172753bc2f45b999a"
SOURCE_SHA256 = "007b6a40b0c65247f881627375c3d2e9b6aeeb5dfa89957494feed0765a1a073"
SOURCE_BYTES = 7378232
RAW_BYTES = 4779822
RAW_CHARACTERS = 4778515
FIELDS = (
    ("assignment", "Anti-Assignment"),
    ("change_control", "Change Of Control"),
    ("termination", "Termination For Convenience"),
    ("liability_cap", "Cap On Liability"),
    ("liability_uncapped", "Uncapped Liability"),
)
QUERIES = {
    "transfer_exposure": "assignment OR change_control",
    "exit_with_uncapped": "termination AND liability_uncapped",
    "mixed_liability": "liability_cap AND liability_uncapped",
    "transfer_without_convenience": "(assignment OR change_control) AND NOT termination",
}
FILENAMES = ("corpus.json", "questions.json", "gold.json", "source-manifest.json")


class InvalidSource(ValueError):
    """Pinned source or retained expert annotation failed validation."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise InvalidSource(message)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def decode(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object)


def validate_source(source):
    """Audit structure and EVERY retained span, without dropping or relabeling.

    Kept separate from the byte pin so tests can exercise malformed annotations.
    Returns the retained questions in official document and fixed field order.
    """
    docs = source.get("data")
    require(isinstance(docs, list) and len(docs) == 102, "expected exactly 102 contracts")
    titles, question_ids, retained, errors = set(), set(), [], []
    byte_count = char_count = 0
    for index, doc in enumerate(docs):
        doc_id = "d%03d" % index
        title = doc.get("title")
        require(isinstance(title, str) and title not in titles, doc_id + ": duplicate/invalid title")
        titles.add(title)
        paragraphs = doc.get("paragraphs")
        require(isinstance(paragraphs, list) and len(paragraphs) == 1, doc_id + ": expected one full context")
        paragraph = paragraphs[0]
        text = paragraph.get("context")
        require(isinstance(text, str), doc_id + ": invalid context")
        byte_count += len(text.encode("utf-8"))
        char_count += len(text)
        qas = paragraph.get("qas")
        require(isinstance(qas, list), doc_id + ": missing questions")
        selected = {}
        for qa in qas:
            qid = qa.get("id")
            require(isinstance(qid, str) and qid not in question_ids, doc_id + ": duplicate/invalid question ID")
            question_ids.add(qid)
            require(qid.startswith(title + "__"), doc_id + ": question ID/title mismatch")
            category = qid[len(title) + 2:]
            if category not in dict(FIELDS).values():
                continue
            require(category not in selected, doc_id + ": duplicate category " + category)
            selected[category] = qa
            require(isinstance(qa.get("question"), str), qid + ": missing question text")
            answers = qa.get("answers")
            require(isinstance(answers, list), qid + ": invalid answers")
            if type(qa.get("is_impossible")) is not bool or qa["is_impossible"] != (not answers):
                errors.append(qid + ": annotation presence/is_impossible disagreement")
            for answer_index, answer in enumerate(answers):
                location = "%s answer[%d]" % (qid, answer_index)
                if not isinstance(answer, dict) or set(answer) != {"answer_start", "text"}:
                    errors.append(location + ": invalid span keys")
                    continue
                start, span = answer["answer_start"], answer["text"]
                if (type(start) is not int or not isinstance(span, str) or not span
                        or start < 0 or start + len(span) > len(text)
                        or text[start:start + len(span)] != span):
                    errors.append(location + ": invalid gold substring alignment " + repr(answer))
        require(set(selected) == {category for _, category in FIELDS}, doc_id + ": missing/extra retained categories")
        retained.append([selected[category] for _, category in FIELDS])
    require(not errors, "INVALID GOLD (no annotations dropped or relabeled):\n" + "\n".join(errors))
    require(byte_count == RAW_BYTES and char_count == RAW_CHARACTERS, "full-context byte/character totals differ")
    for field_index, (key, _) in enumerate(FIELDS):
        require(len({qas[field_index]["question"] for qas in retained}) == 1, key + ": inconsistent official questions")
    return retained


def query_sets(records):
    result = {key: [] for key in QUERIES}
    for record in records:
        p = {key: value["present"] for key, value in record["annotations"].items()}
        transfer = p["assignment"] or p["change_control"]
        matches = (transfer, p["termination"] and p["liability_uncapped"],
                   p["liability_cap"] and p["liability_uncapped"], transfer and not p["termination"])
        for name, match in zip(QUERIES, matches):
            if match:
                result[name].append(record["id"])
    return result


def build(source_bytes, manifest_bytes):
    require(len(source_bytes) == SOURCE_BYTES and sha256(source_bytes) == SOURCE_SHA256,
            "source mutation: official-test.json byte length or SHA-256 differs from pin")
    original_manifest = decode(manifest_bytes)
    require(original_manifest.get("commit") == COMMIT, "source manifest commit mismatch")
    require(original_manifest.get("zip_sha256") == ZIP_SHA256, "source manifest ZIP hash mismatch")
    require(original_manifest.get("url") == "https://raw.githubusercontent.com/The-Atticus-Project/cuad/" + COMMIT + "/data.zip", "source manifest URL mismatch")
    source = decode(source_bytes)
    retained = validate_source(source)
    contracts, records, documents = [], [], []
    for index, (doc, qas) in enumerate(zip(source["data"], retained)):
        doc_id, title, text = "d%03d" % index, doc["title"], doc["paragraphs"][0]["context"]
        contracts.append({"id": doc_id, "title": title, "text": text})
        records.append({"id": doc_id, "annotations": {
            key: {"question_id": qa["id"], "present": bool(qa["answers"]),
                  "answers": [{"answer_start": a["answer_start"], "text": a["text"]} for a in qa["answers"]]}
            for (key, _), qa in zip(FIELDS, qas)}})
        documents.append({"id": doc_id, "text_sha256": sha256(text.encode("utf-8")),
                          "text_bytes": len(text.encode("utf-8")), "text_characters": len(text),
                          "title_sha256": sha256(title.encode("utf-8")),
                          "title_bytes": len(title.encode("utf-8")), "title_characters": len(title)})
    return {
        "corpus.json": {"schema": {"version": 1, "encoding": "UTF-8", "contract_fields": ["id", "title", "text"]}, "contracts": contracts},
        "questions.json": {"schema_version": 1, "questions": [
            {"key": key, "category": category, "question": qa["question"]}
            for (key, category), qa in zip(FIELDS, retained[0])]},
        "gold.json": {"schema_version": 1,
                      "semantics": "Official expert-annotation presence only. Structural analytics, not legal risk or conclusions.",
                      "contracts": records, "query_expressions": QUERIES.copy(), "query_sets": query_sets(records)},
        "source-manifest.json": {
            "schema_version": 1, "repository": "The-Atticus-Project/cuad", "commit": COMMIT,
            "zip_sha256": ZIP_SHA256, "license": "CC-BY-4.0",
            "dataset_card": "https://github.com/The-Atticus-Project/cuad/blob/" + COMMIT + "/readme.md",
            "license_card": "https://huggingface.co/datasets/cuad/blob/main/README.md",
            "attribution": "CUAD: Contract Understanding Atticus Dataset, The Atticus Project and contributors.",
            "source_file": "official-test.json", "source_sha256": SOURCE_SHA256,
            "source_bytes": len(source_bytes), "source_characters": len(source_bytes.decode("utf-8")),
            "input_manifest_sha256": sha256(manifest_bytes), "input_manifest": original_manifest,
            "contracts": 102, "retained_questions": 510, "raw_text_bytes": RAW_BYTES,
            "raw_text_characters": RAW_CHARACTERS, "order": "official test order", "documents": documents},
    }


def validate_bundle(bundle, source_bytes, manifest_bytes):
    """Require exact coverage, raw source equality, IDs, annotations and query sets.

    Exact typed canonical equality also rejects bool/int substitution, injected
    gold metadata, missing/extra keys and reordered or duplicate records.
    """
    expected = build(source_bytes, manifest_bytes)
    require(set(bundle) == set(FILENAMES), "missing/extra output files")
    for filename in FILENAMES:
        require(encode(bundle[filename]) == encode(expected[filename]), filename + ": differs from exact pinned-source projection")


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def prepare(source_path, manifest_path, output_dir):
    source_bytes, manifest_bytes = Path(source_path).read_bytes(), Path(manifest_path).read_bytes()
    bundle = build(source_bytes, manifest_bytes)
    validate_bundle(bundle, source_bytes, manifest_bytes)
    output = Path(output_dir)
    # Atomic exclusive directory creation rejects existing directories, files,
    # and symlinks. Never modify or clean up someone else's destination.
    output.mkdir(parents=False, exist_ok=False)
    for filename in FILENAMES:
        with (output / filename).open("xb") as stream:
            stream.write(encode(bundle[filename]))
    validate_bundle({name: decode((output / name).read_bytes()) for name in FILENAMES}, source_bytes, manifest_bytes)
    return bundle


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new exclusive directory, scratch first")
    args = parser.parse_args(argv)
    try:
        bundle = prepare(args.source, args.source_manifest, args.output)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print("PREPARATION FAILED: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps({"contracts": 102, "answers": 510, "raw_text_bytes": RAW_BYTES,
                      "invalid_gold": [], "query_counts": {key: len(ids) for key, ids in bundle["gold.json"]["query_sets"].items()},
                      "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
