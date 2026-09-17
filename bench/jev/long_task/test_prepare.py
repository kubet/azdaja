"""Stdlib-only tests. Set CUAD_SOURCE_DIR to the pinned local input directory.

Run: PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s bench/jev/long_task -v
No downloads, credentials, model calls, or output files in the repository.
"""
import ast
import copy
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("long_task_prepare", HERE / "prepare.py")
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)
SOURCE_DIR = Path(os.environ.get("CUAD_SOURCE_DIR", str(Path.home() / ".jcode/scratch/jev-long-cuad-source-20260917")))


class PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_path = SOURCE_DIR / "official-test.json"
        cls.manifest_path = SOURCE_DIR / "source-manifest.json"
        cls.raw = cls.source_path.read_bytes()
        cls.manifest_raw = cls.manifest_path.read_bytes()
        cls.source = json.loads(cls.raw)
        cls.bundle = prepare.build(cls.raw, cls.manifest_raw)

    def reject_bundle(self, bundle):
        with self.assertRaises(prepare.InvalidSource):
            prepare.validate_bundle(bundle, self.raw, self.manifest_raw)

    def retained_qas(self, source):
        categories = {category for _, category in prepare.FIELDS}
        return [qa for doc in source["data"] for qa in doc["paragraphs"][0]["qas"]
                if qa["id"].rsplit("__", 1)[-1] in categories]

    def test_full_coverage_and_all_raw_texts_exact(self):
        corpus = self.bundle["corpus.json"]
        gold = self.bundle["gold.json"]
        ids = ["d%03d" % index for index in range(102)]
        self.assertEqual([d["id"] for d in corpus["contracts"]], ids)
        self.assertEqual([d["id"] for d in gold["contracts"]], ids)
        self.assertEqual(len(self.source["data"]), 102)
        self.assertEqual(sum(len(d["annotations"]) for d in gold["contracts"]), 510)
        self.assertEqual(sum(len(d["text"].encode("utf-8")) for d in corpus["contracts"]), 4779822)
        self.assertEqual(sum(len(d["text"]) for d in corpus["contracts"]), 4778515)
        for actual, source in zip(corpus["contracts"], self.source["data"]):
            self.assertEqual(actual["title"], source["title"])
            self.assertEqual(actual["text"], source["paragraphs"][0]["context"])
            self.assertEqual(actual["text"].encode("utf-8"), source["paragraphs"][0]["context"].encode("utf-8"))

    def test_all_510_annotations_and_every_exact_span(self):
        question_ids = []
        spans = 0
        positives = dict.fromkeys(dict(prepare.FIELDS), 0)
        for doc, record in zip(self.source["data"], self.bundle["gold.json"]["contracts"]):
            paragraph = doc["paragraphs"][0]
            qas = {qa["id"].rsplit("__", 1)[-1]: qa for qa in paragraph["qas"]}
            self.assertEqual(set(record["annotations"]), set(dict(prepare.FIELDS)))
            for key, category in prepare.FIELDS:
                qa, annotation = qas[category], record["annotations"][key]
                self.assertEqual(annotation["question_id"], qa["id"])
                question_ids.append(annotation["question_id"])
                self.assertIs(type(annotation["present"]), bool)
                self.assertEqual(annotation["present"], bool(qa["answers"]))
                self.assertEqual(annotation["present"], not qa["is_impossible"])
                self.assertEqual(annotation["answers"], qa["answers"])
                positives[key] += annotation["present"]
                for span in annotation["answers"]:
                    spans += 1
                    start, text = span["answer_start"], span["text"]
                    self.assertEqual(paragraph["context"][start:start + len(text)], text)
        self.assertEqual(len(question_ids), 510)
        self.assertEqual(len(set(question_ids)), 510)
        self.assertEqual(spans, 374)
        self.assertEqual(positives, dict(zip(dict(prepare.FIELDS), [72, 26, 29, 44, 13])))

    def test_questions_exact_including_unicode_whitespace(self):
        questions = self.bundle["questions.json"]["questions"]
        self.assertEqual([q["key"] for q in questions], list(dict(prepare.FIELDS)))
        for question in questions:
            for qa in self.retained_qas(self.source):
                if qa["id"].endswith("__" + question["category"]):
                    self.assertEqual(question["question"].encode("utf-8"), qa["question"].encode("utf-8"))
        self.assertIn("\xa0", questions[2]["question"])

    def test_gold_exclusion_is_structural_not_word_filter(self):
        corpus = self.bundle["corpus.json"]
        self.assertEqual(set(corpus), {"schema", "contracts"})
        self.assertEqual(corpus["schema"], {"version": 1, "encoding": "UTF-8", "contract_fields": ["id", "title", "text"]})
        for doc in corpus["contracts"]:
            self.assertEqual(set(doc), {"id", "title", "text"})
        # Legal vocabulary is meaningful SOURCE content, never evidence of leakage.
        self.assertTrue(any("assignment" in d["text"].lower() for d in corpus["contracts"]))
        for key in ("annotations", "answers", "answer_start", "present", "assignment", "query_sets"):
            candidate = copy.deepcopy(self.bundle)
            candidate["corpus.json"]["contracts"][0][key] = False
            self.reject_bundle(candidate)

    def test_hashes_counts_and_attribution(self):
        manifest = self.bundle["source-manifest.json"]
        self.assertEqual(manifest["source_sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(manifest["source_bytes"], len(self.raw))
        self.assertEqual(manifest["source_characters"], len(self.raw.decode("utf-8")))
        self.assertEqual(manifest["input_manifest_sha256"], hashlib.sha256(self.manifest_raw).hexdigest())
        self.assertEqual(manifest["license"], "CC-BY-4.0")
        self.assertEqual(manifest["commit"], "67faa0e6023b04fcaae6cc09497ab00e5d63a2a2")
        self.assertEqual(manifest["zip_sha256"], "f8161d18bea4e9c05e78fa6dda61c19c846fb8087ea969c172753bc2f45b999a")
        for doc, metadata in zip(self.bundle["corpus.json"]["contracts"], manifest["documents"]):
            self.assertEqual(doc["id"], metadata["id"])
            for field in ("text", "title"):
                self.assertEqual(metadata[field + "_sha256"], hashlib.sha256(doc[field].encode("utf-8")).hexdigest())
                self.assertEqual(metadata[field + "_bytes"], len(doc[field].encode("utf-8")))
                self.assertEqual(metadata[field + "_characters"], len(doc[field]))

    def test_query_sets_independent_set_algebra(self):
        sets = {key: {record["id"] for record in self.bundle["gold.json"]["contracts"]
                      if record["annotations"][key]["present"]} for key, _ in prepare.FIELDS}
        transfer = sets["assignment"] | sets["change_control"]
        expected = {
            "transfer_exposure": transfer,
            "exit_with_uncapped": sets["termination"] & sets["liability_uncapped"],
            "mixed_liability": sets["liability_cap"] & sets["liability_uncapped"],
            "transfer_without_convenience": transfer - sets["termination"],
        }
        self.assertEqual(self.bundle["gold.json"]["query_sets"], {key: sorted(ids) for key, ids in expected.items()})

    def test_query_truth_table_all_32_combinations(self):
        for bits in itertools.product((False, True), repeat=5):
            record = {"id": "d000", "annotations": {key: {"present": bit} for (key, _), bit in zip(prepare.FIELDS, bits)}}
            result = prepare.query_sets([record])
            a, c, t, cap, uncapped = bits
            wanted = (a or c, t and uncapped, cap and uncapped, (a or c) and not t)
            self.assertEqual(list(result.values()), [["d000"] if bit else [] for bit in wanted])

    def test_missing_extra_duplicate_and_reordered_document_ids(self):
        for filename in ("corpus.json", "gold.json"):
            for mutation in ("missing", "extra", "duplicate", "reorder", "wrong"):
                with self.subTest(filename=filename, mutation=mutation):
                    candidate = copy.deepcopy(self.bundle)
                    docs = candidate[filename]["contracts"]
                    if mutation == "missing":
                        docs.pop()
                    elif mutation == "extra":
                        docs.append(copy.deepcopy(docs[0]))
                    elif mutation == "duplicate":
                        docs[1]["id"] = docs[0]["id"]
                    elif mutation == "reorder":
                        docs.reverse()
                    else:
                        docs[0]["id"] = "d102"
                    self.reject_bundle(candidate)

    def test_missing_extra_duplicate_question_ids_and_keys(self):
        for mutation in ("missing", "extra", "duplicate", "wrong_key"):
            candidate = copy.deepcopy(self.bundle)
            questions = candidate["questions.json"]["questions"]
            if mutation == "missing":
                questions.pop()
            elif mutation == "extra":
                questions.append(copy.deepcopy(questions[0]))
            elif mutation == "duplicate":
                questions[1]["key"] = questions[0]["key"]
            else:
                questions[0]["key"] = "other"
            self.reject_bundle(candidate)
        candidate = copy.deepcopy(self.bundle)
        annotations = candidate["gold.json"]["contracts"][0]["annotations"]
        annotations["assignment"]["question_id"] = annotations["termination"]["question_id"]
        self.reject_bundle(candidate)
        for mutation in ("missing", "extra"):
            candidate = copy.deepcopy(self.bundle)
            annotations = candidate["gold.json"]["contracts"][0]["annotations"]
            if mutation == "missing":
                del annotations["assignment"]
            else:
                annotations["extra"] = annotations["assignment"]
            self.reject_bundle(candidate)

    def test_source_missing_extra_duplicate_ids(self):
        for mutation in ("missing_doc", "extra_doc", "duplicate_doc", "missing_qa", "duplicate_qa"):
            candidate = copy.deepcopy(self.source)
            docs = candidate["data"]
            qas = docs[0]["paragraphs"][0]["qas"]
            if mutation == "missing_doc":
                docs.pop()
            elif mutation == "extra_doc":
                docs.append(copy.deepcopy(docs[0]))
            elif mutation == "duplicate_doc":
                docs[1] = copy.deepcopy(docs[0])
            elif mutation == "missing_qa":
                qas.remove(next(q for q in qas if q["id"].endswith("__Anti-Assignment")))
            else:
                qas.append(copy.deepcopy(qas[0]))
            with self.assertRaises(prepare.InvalidSource):
                prepare.validate_source(candidate)

    def test_invalid_gold_reported_not_dropped(self):
        for change in ({"answer_start": -1}, {"answer_start": True}, {"answer_start": 10**9},
                       {"text": "not an official span"}, {"text": ""}, {"answer_start": 0.5}):
            candidate = copy.deepcopy(self.source)
            qa = next(q for q in self.retained_qas(candidate) if q["answers"])
            qa["answers"][0].update(change)
            with self.assertRaisesRegex(prepare.InvalidSource, "INVALID GOLD.*") as error:
                prepare.validate_source(candidate)
            self.assertIn(qa["id"], str(error.exception))
            self.assertIn("answer[0]", str(error.exception))
        candidate = copy.deepcopy(self.source)
        qa = self.retained_qas(candidate)[0]
        qa["is_impossible"] = not qa["is_impossible"]
        with self.assertRaisesRegex(prepare.InvalidSource, "INVALID GOLD"):
            prepare.validate_source(candidate)

    def test_source_byte_mutation_rejected_before_output(self):
        for raw in (self.raw + b"\n", self.raw.replace(b"SUPPLY", b"sUPPLY", 1), self.raw[:-1]):
            with self.assertRaisesRegex(prepare.InvalidSource, "source mutation"):
                prepare.build(raw, self.manifest_raw)
        with tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR", str(SOURCE_DIR.parent))) as tmp:
            bad_source, output = Path(tmp) / "bad.json", Path(tmp) / "out"
            bad_source.write_bytes(self.raw + b"\n")
            with self.assertRaises(prepare.InvalidSource):
                prepare.prepare(bad_source, self.manifest_path, output)
            self.assertFalse(output.exists())

    def test_manifest_pin_mutation(self):
        for key in ("commit", "zip_sha256", "url"):
            manifest = json.loads(self.manifest_raw)
            manifest[key] = "wrong"
            with self.assertRaises(prepare.InvalidSource):
                prepare.build(self.raw, json.dumps(manifest).encode("utf-8"))

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(prepare.InvalidSource, "duplicate JSON key"):
            prepare.decode(b'{"id":"d000","id":"d001"}')

    def test_mutated_text_gold_queries_and_metadata_rejected(self):
        for filename, key, value in (("corpus.json", "extra", "gold"), ("gold.json", "query_sets", {}),
                                     ("source-manifest.json", "raw_text_bytes", 0)):
            candidate = copy.deepcopy(self.bundle)
            candidate[filename][key] = value
            self.reject_bundle(candidate)
        candidate = copy.deepcopy(self.bundle)
        candidate["corpus.json"]["contracts"][0]["text"] += " "
        self.reject_bundle(candidate)
        for value in (True, 0):
            candidate = copy.deepcopy(self.bundle)
            annotation = candidate["gold.json"]["contracts"][0]["annotations"]["assignment"]
            annotation["present"] = not annotation["present"] if value is True else int(annotation["present"])
            self.reject_bundle(candidate)
        candidate = copy.deepcopy(self.bundle)
        annotation = next(a for r in candidate["gold.json"]["contracts"] for a in r["annotations"].values() if a["answers"])
        annotation["answers"][0]["answer_start"] += 1
        self.reject_bundle(candidate)

    def test_missing_extra_output_files(self):
        candidate = copy.deepcopy(self.bundle)
        del candidate["gold.json"]
        self.reject_bundle(candidate)
        candidate = copy.deepcopy(self.bundle)
        candidate["extra.json"] = {}
        self.reject_bundle(candidate)

    def test_safe_exclusive_output_and_determinism(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("JCODE_SCRATCH_DIR", str(SOURCE_DIR.parent))) as tmp:
            first, second = Path(tmp) / "first", Path(tmp) / "second"
            prepare.prepare(self.source_path, self.manifest_path, first)
            prepare.prepare(self.source_path, self.manifest_path, second)
            before = {p.name: p.read_bytes() for p in first.iterdir()}
            self.assertEqual(set(before), set(prepare.FILENAMES))
            self.assertEqual(before, {p.name: p.read_bytes() for p in second.iterdir()})
            for destination in (first, self.source_path):
                with self.assertRaises(FileExistsError):
                    prepare.prepare(self.source_path, self.manifest_path, destination)
            link = Path(tmp) / "link"
            link.symlink_to(first, target_is_directory=True)
            with self.assertRaises(FileExistsError):
                prepare.prepare(self.source_path, self.manifest_path, link)
            dangling = Path(tmp) / "dangling"
            dangling.symlink_to(Path(tmp) / "absent")
            with self.assertRaises(FileExistsError):
                prepare.prepare(self.source_path, self.manifest_path, dangling)
            self.assertFalse((Path(tmp) / "absent").exists())
            self.assertEqual(before, {p.name: p.read_bytes() for p in first.iterdir()})
            self.assertEqual(self.source_path.read_bytes(), self.raw)
            prepare.validate_bundle({name: prepare.decode(data) for name, data in before.items()}, self.raw, self.manifest_raw)

    def test_python39_syntax(self):
        for path in (HERE / "prepare.py", Path(__file__)):
            ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))

    def test_published_fixtures_if_present(self):
        fixtures = HERE / "fixtures"
        if fixtures.exists():
            self.assertEqual({p.name for p in fixtures.iterdir()}, set(prepare.FILENAMES))
            prepare.validate_bundle({name: prepare.decode((fixtures / name).read_bytes()) for name in prepare.FILENAMES}, self.raw, self.manifest_raw)


if __name__ == "__main__":
    unittest.main()
