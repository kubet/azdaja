"""Offline stdlib grader tests against the approved complete CUAD fixtures."""
import ast
import copy
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("long_task_grade", HERE / "grade.py")
grader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(grader)
SCRATCH = Path(os.environ.get("JCODE_SCRATCH_DIR", str(Path.home() / ".jcode/scratch")))


class GradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = grader.load_json(HERE / "fixtures/corpus.json")
        cls.gold = grader.load_json(HERE / "fixtures/gold.json")
        cls.documents = {d["id"]: d for d in cls.corpus["contracts"]}
        cls.annotations = {d["id"]: d["annotations"] for d in cls.gold["contracts"]}
        cls.perfect = cls.prediction("gold")

    @classmethod
    def prediction(cls, mode):
        result = {"source_sha256": grader.CORPUS_SHA256, "contracts": [], "queries": {}}
        for doc_id in grader.IDS:
            fields = {}
            for key in grader.FIELDS:
                annotation = cls.annotations[doc_id][key]
                label = ("yes" if annotation["present"] else "no") if mode == "gold" else mode
                quote = ""
                if label == "yes":
                    if annotation["answers"]:
                        quote = max(annotation["answers"], key=lambda a: len(a["text"]))["text"][:600]
                    else:
                        quote = cls.documents[doc_id]["text"][:40]
                fields[key] = {"label": label, "quote": quote}
            result["contracts"].append({"id": doc_id, "fields": fields})
        cls.recompute_declared(result)
        return result

    @staticmethod
    def recompute_declared(prediction):
        prediction["queries"] = {key: {label: [] for label in grader.LABELS} for key in grader.QUERIES}
        by_id = {d["id"]: d["fields"] for d in prediction["contracts"] if isinstance(d, dict) and d.get("id") in grader.IDS}
        for doc_id in grader.IDS:
            fields = {key: by_id.get(doc_id, {}).get(key, {}).get("label") for key in grader.FIELDS}
            for name, label in grader.query_labels(fields).items():
                prediction["queries"][name][label].append(doc_id)

    def score(self, prediction):
        return grader.grade(prediction, self.corpus, self.gold)

    def positive_cell(self):
        for i, record in enumerate(self.gold["contracts"]):
            for key, annotation in record["annotations"].items():
                if annotation["present"]:
                    return i, key

    def test_perfect_official_annotations(self):
        report = self.score(self.perfect)
        self.assertTrue(report["structural"]["valid"], report["structural"]["errors"])
        self.assertEqual(report["structural"]["observed_cells"], 510)
        self.assertEqual(report["aggregate"]["accuracy"], 1)
        self.assertEqual(report["aggregate"]["macro_f1"], 1)
        self.assertEqual(report["aggregate"]["TP"], 184)
        self.assertEqual(report["aggregate"]["TN"], 326)
        self.assertEqual(report["citations"]["predicted_yes"], 184)
        self.assertEqual(report["citations"]["exact_citation_rate"], 1)
        self.assertEqual(report["citations"]["correctly_supported_citation_rate"], 1)
        self.assertTrue(all(s["exact_match"] for s in report["queries"]["scores"].values()))

    def test_all_no_is_structurally_valid_but_not_perfect(self):
        report = self.score(self.prediction("no"))
        self.assertTrue(report["structural"]["valid"])
        self.assertEqual(report["aggregate"]["FN"], 184)
        self.assertEqual(report["aggregate"]["TN"], 326)
        self.assertEqual(report["aggregate"]["accuracy"], 326 / 510)
        self.assertEqual(report["aggregate"]["macro_f1"], 0)
        self.assertEqual(report["citations"]["predicted_yes"], 0)
        self.assertEqual(report["citations"]["exact_citation_rate"], 0)
        for key in grader.QUERIES:
            self.assertEqual(report["queries"]["scores"][key]["FN"], len(self.gold["query_sets"][key]))
            self.assertEqual(report["queries"]["recomputed"][key]["no"], list(grader.IDS))

    def test_all_unknown_penalized_and_preserved(self):
        report = self.score(self.prediction("unknown"))
        self.assertTrue(report["structural"]["valid"])
        self.assertEqual(report["aggregate"]["unknown"], 510)
        self.assertEqual(report["aggregate"]["FN"], 184)
        self.assertEqual(report["aggregate"]["unknown_negative_penalty"], 326)
        self.assertEqual(report["aggregate"]["FP"], 0)
        self.assertEqual(report["aggregate"]["accuracy"], 0)
        self.assertEqual(report["aggregate"]["macro_f1"], 0)
        for key in grader.QUERIES:
            self.assertEqual(report["queries"]["recomputed"][key]["unknown"], list(grader.IDS))
            self.assertEqual(report["queries"]["scores"][key]["unknown"], 102)
            self.assertEqual(report["queries"]["scores"][key]["total"], 102)

    def test_all_yes_false_support_and_fixed_denominator(self):
        report = self.score(self.prediction("yes"))
        self.assertTrue(report["structural"]["valid"])
        self.assertEqual(report["aggregate"]["FP"], 326)
        self.assertEqual(report["citations"]["predicted_yes"], 510)
        self.assertEqual(report["citations"]["exact_citation_rate"], 1)
        self.assertEqual(report["citations"]["correctly_supported_citation_rate"], 184 / 510)
        self.assertEqual(report["aggregate"]["accuracy"], 184 / 510)

    def test_exact_unrelated_quote_not_expert_supported(self):
        prediction = copy.deepcopy(self.perfect)
        index, key = self.positive_cell()
        doc_id = grader.IDS[index]
        text, answers = self.documents[doc_id]["text"], self.annotations[doc_id][key]["answers"]
        quote = next(text[start:start + 40] for start in range(0, len(text) - 40, 40)
                     if not grader.citation(text, text[start:start + 40], answers)["supported"])
        prediction["contracts"][index]["fields"][key]["quote"] = quote
        report = self.score(prediction)
        self.assertTrue(report["structural"]["valid"])
        self.assertEqual(report["aggregate"]["accuracy"], 1)
        self.assertEqual(report["citations"]["exact_citation_rate"], 1)
        self.assertEqual(report["citations"]["supported_citations"], 183)

    def test_wrong_document_quote_preserves_correct_label(self):
        prediction = copy.deepcopy(self.perfect)
        index, key = self.positive_cell()
        doc_id = grader.IDS[index]
        quote = next(d["text"][:80] for d in self.corpus["contracts"] if d["text"][:80] not in self.documents[doc_id]["text"])
        prediction["contracts"][index]["fields"][key]["quote"] = quote
        report = self.score(prediction)
        self.assertFalse(report["structural"]["valid"])
        self.assertEqual(report["aggregate"]["accuracy"], 1)
        self.assertEqual(report["citations"]["predicted_yes"], 184)
        self.assertEqual(report["citations"]["exact_citations"], 183)
        self.assertTrue(report["matrix"][index]["fields"][key]["observed"])
        self.assertEqual(report["matrix"][index]["fields"][key]["label"], "yes")

    def test_bad_quote_types_and_lengths_do_not_discard_panel(self):
        for quote in ("", "a" * 19, "a" * 601, None, [], 42):
            prediction = copy.deepcopy(self.perfect)
            index, key = self.positive_cell()
            prediction["contracts"][index]["fields"][key]["quote"] = quote
            report = self.score(prediction)
            self.assertFalse(report["structural"]["valid"])
            self.assertEqual(report["aggregate"]["accuracy"], 1)
            self.assertEqual(report["structural"]["observed_cells"], 510)
        for label in ("no", "unknown"):
            prediction = self.prediction(label)
            prediction["contracts"][0]["fields"]["assignment"]["quote"] = "not empty"
            self.assertFalse(self.score(prediction)["structural"]["valid"])

    def test_all_occurrences_and_single_span_80_percent_boundary(self):
        quote = "ABCDEFGHIJKLMNOPQRST"
        text = quote + " gap " + quote
        supported = grader.citation(text, quote, [{"answer_start": 25, "text": quote[:16]}])
        self.assertEqual(supported["occurrences"], 2)
        self.assertEqual(supported["best_expert_overlap"], 0.8)
        self.assertTrue(supported["supported"])
        unsupported = grader.citation(text, quote, [{"answer_start": 25, "text": quote[:15]}])
        self.assertFalse(unsupported["supported"])
        split = grader.citation(quote, quote, [{"answer_start": 0, "text": quote[:10]}, {"answer_start": 10, "text": quote[10:]}])
        self.assertFalse(split["supported"])
        overlap = grader.citation("a" * 21, "a" * 20, [{"answer_start": 1, "text": "a" * 20}])
        self.assertEqual(overlap["occurrences"], 2)
        self.assertEqual(overlap["best_expert_overlap"], 1)

    def test_unicode_exactness_and_length(self):
        text = "é" * 20
        self.assertTrue(grader.citation(text, text, [{"answer_start": 0, "text": text}])["supported"])
        self.assertFalse(grader.citation(text, "e\u0301" * 20, [])["exact_substring"])
        self.assertFalse(grader.citation("é" * 19, "é" * 19, [])["quote_valid"])
        self.assertTrue(grader.citation("x" * 600, "x" * 600, [])["quote_valid"])
        self.assertFalse(grader.citation("x" * 601, "x" * 601, [])["quote_valid"])

    def test_forged_queries_never_change_recomputed_score(self):
        prediction = self.prediction("no")
        baseline = self.score(prediction)
        for key in grader.QUERIES:
            yes = set(self.gold["query_sets"][key])
            prediction["queries"][key] = {"yes": sorted(yes), "no": [i for i in grader.IDS if i not in yes], "unknown": []}
        forged = self.score(prediction)
        self.assertFalse(forged["structural"]["valid"])
        self.assertFalse(forged["queries"]["declared_consistent"])
        self.assertEqual(forged["queries"]["scores"], baseline["queries"]["scores"])
        self.assertEqual(forged["queries"]["recomputed"], baseline["queries"]["recomputed"])

    def test_duplicate_missing_extra_ids_keep_fullmatrix(self):
        prediction = copy.deepcopy(self.perfect)
        prediction["contracts"].append(copy.deepcopy(prediction["contracts"][0]))
        duplicate = self.score(prediction)
        self.assertFalse(duplicate["structural"]["valid"])
        self.assertEqual(duplicate["aggregate"]["accuracy"], 1)
        self.assertEqual(len(duplicate["matrix"]), 102)
        prediction = copy.deepcopy(self.perfect)
        prediction["contracts"].pop(0)
        missing = self.score(prediction)
        self.assertEqual(missing["structural"]["missing_ids"], ["d000"])
        self.assertEqual(missing["aggregate"]["unobserved"], 5)
        self.assertEqual(missing["aggregate"]["accuracy"], 505 / 510)
        self.assertTrue(all(c["label"] is None and not c["observed"] for c in missing["matrix"][0]["fields"].values()))
        prediction["contracts"].append({"id": "d102", "fields": {}})
        self.assertFalse(self.score(prediction)["structural"]["valid"])

    def test_missing_field_is_unobserved_not_no(self):
        prediction = copy.deepcopy(self.perfect)
        index, key = self.positive_cell()
        del prediction["contracts"][index]["fields"][key]
        report = self.score(prediction)
        self.assertEqual(report["per_field"][key]["FN"], 1)
        self.assertEqual(report["per_field"][key]["unobserved"], 1)
        self.assertIsNone(report["matrix"][index]["fields"][key]["label"])
        self.assertEqual(report["aggregate"]["accuracy"], 509 / 510)

    def test_extra_keys_wrong_hash_and_invalid_label(self):
        mutations = [lambda p: p.update(extra=True),
                     lambda p: p.update(source_sha256="wrong"),
                     lambda p: p["contracts"][0].update(extra=True),
                     lambda p: p["contracts"][0]["fields"].update(extra={}),
                     lambda p: p["contracts"][0]["fields"]["assignment"].update(extra=True)]
        for mutate in mutations:
            prediction = copy.deepcopy(self.perfect)
            mutate(prediction)
            report = self.score(prediction)
            self.assertFalse(report["structural"]["valid"])
            self.assertEqual(report["aggregate"]["accuracy"], 1)
        for value in ("YES", "true", True, 1, [], {}, None):
            prediction = copy.deepcopy(self.perfect)
            prediction["contracts"][0]["fields"]["assignment"]["label"] = value
            report = self.score(prediction)
            self.assertFalse(report["structural"]["valid"])
            self.assertEqual(report["aggregate"]["unobserved"], 1)
            self.assertEqual(report["aggregate"]["total"], 510)

    def test_queries_require_exact_partition(self):
        for kind in ("missing", "duplicate", "cross_duplicate", "extra", "wrong_type", "extra_key"):
            prediction = copy.deepcopy(self.perfect)
            partition = prediction["queries"]["transfer_exposure"]
            if kind == "missing":
                partition["yes"].pop()
            elif kind == "duplicate":
                partition["yes"].append(partition["yes"][0])
            elif kind == "cross_duplicate":
                partition["no"].append(partition["yes"][0])
            elif kind == "extra":
                partition["yes"].append("d102")
            elif kind == "wrong_type":
                partition["yes"] = "d000"
            else:
                partition["maybe"] = []
            report = self.score(prediction)
            self.assertFalse(report["structural"]["valid"])
            self.assertTrue(report["queries"]["scores"]["transfer_exposure"]["exact_match"])

    def test_three_valued_queries_all_243_combinations(self):
        for values in itertools.product(grader.LABELS, repeat=5):
            fields = dict(zip(grader.FIELDS, values))
            possible = []
            choices = [[True, False] if v == "unknown" else [v == "yes"] for v in values]
            for a, c, t, cap, uncapped in itertools.product(*choices):
                possible.append((a or c, t and uncapped, cap and uncapped, (a or c) and not t))
            expected = ["yes" if all(v[i] for v in possible) else "no" if not any(v[i] for v in possible) else "unknown" for i in range(4)]
            self.assertEqual(list(grader.query_labels(fields).values()), expected)

    def test_unknown_negative_penalizes_f1_without_false_positive(self):
        score = grader.metrics([(True, "yes"), (False, "unknown"), (True, "unknown"), (False, None)])
        self.assertEqual(score["TP"], 1)
        self.assertEqual(score["FN"], 1)
        self.assertEqual(score["FP"], 0)
        self.assertEqual(score["unknown_negative_penalty"], 2)
        self.assertEqual(score["f1"], 2 / 5)
        self.assertEqual(score["accuracy"], 1 / 4)

    def test_malformed_and_mutated_gold_rejected(self):
        for kind in ("missing_doc", "duplicate_doc", "missing_field", "bad_span", "presence", "query"):
            gold = copy.deepcopy(self.gold)
            if kind == "missing_doc":
                gold["contracts"].pop()
            elif kind == "duplicate_doc":
                gold["contracts"][1]["id"] = gold["contracts"][0]["id"]
            elif kind == "missing_field":
                del gold["contracts"][0]["annotations"]["assignment"]
            elif kind == "bad_span":
                index, key = self.positive_cell()
                gold["contracts"][index]["annotations"][key]["answers"][0]["answer_start"] += 1
            elif kind == "presence":
                gold["contracts"][0]["annotations"]["assignment"]["present"] = "yes"
            else:
                gold["query_sets"]["transfer_exposure"] = []
            with self.assertRaises(grader.InvalidGold):
                grader.grade(self.perfect, self.corpus, gold)
        corpus = copy.deepcopy(self.corpus)
        corpus["contracts"][0]["text"] += " "
        with self.assertRaises(grader.InvalidGold):
            grader.grade(self.perfect, corpus, self.gold)

    def test_totally_malformed_prediction_keeps_all_510_cells(self):
        for prediction in (None, [], 123, {}, {"contracts": [None, {}, {"id": []}]}):
            report = self.score(prediction)
            self.assertFalse(report["structural"]["valid"])
            self.assertEqual(len(report["matrix"]), 102)
            self.assertEqual(report["aggregate"]["unobserved"], 510)
            self.assertEqual(report["aggregate"]["accuracy"], 0)
            for partition in report["queries"]["recomputed"].values():
                self.assertEqual(partition["unknown"], list(grader.IDS))

    def test_offline_comparison_includes_invalid_panels(self):
        baseline = self.score(self.prediction("no"))
        prediction = copy.deepcopy(self.perfect)
        prediction["source_sha256"] = "bad"
        report = self.score(prediction)
        comparison = grader.compare_reports(baseline, report)
        self.assertEqual(comparison["accuracy_delta"], 1 - 326 / 510)
        self.assertEqual(comparison["macro_f1_delta"], 1)
        self.assertFalse(comparison["second_structurally_valid"])

    def test_strict_json_replay_and_exclusive_cli(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            tmp = Path(tmp)
            first, second, out = tmp / "first.json", tmp / "second.json", tmp / "report.json"
            first.write_bytes(grader.canonical(self.prediction("no")))
            second.write_bytes(grader.canonical(self.perfect))
            command = [sys.executable, str(HERE / "grade.py"), str(first), "--compare", str(second), "--output", str(out)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            content = out.read_bytes()
            report = json.loads(content)
            self.assertEqual(report["first"]["aggregate"]["total"], 510)
            self.assertEqual(report["second"]["aggregate"]["accuracy"], 1)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
            self.assertEqual(out.read_bytes(), content)
            for bad in ('{"contracts":[],"contracts":[]}', '{"x":NaN}', 'not JSON'):
                first.write_text(bad)
                report = grader.replay(first, self.corpus, self.gold)
                self.assertFalse(report["structural"]["valid"])
                self.assertEqual(report["aggregate"]["unobserved"], 510)
                self.assertIn("invalid prediction JSON", report["structural"]["errors"][0])

    def test_invalid_unicode_quote_still_serializes_complete_report(self):
        prediction = copy.deepcopy(self.perfect)
        index, key = self.positive_cell()
        prediction["contracts"][index]["fields"][key]["quote"] = "\ud800" * 20
        report = self.score(prediction)
        self.assertFalse(report["structural"]["valid"])
        self.assertEqual(report["aggregate"]["accuracy"], 1)
        replayed = json.loads(grader.canonical(report))
        self.assertEqual(replayed["aggregate"]["total"], 510)
        self.assertEqual(replayed["structural"]["observed_cells"], 510)

    def test_source_hash_binds_exact_ctx_not_official_archive_member(self):
        ctx = (HERE / "fixtures/corpus.json").read_bytes()
        self.assertEqual(hashlib.sha256(ctx).hexdigest(), grader.CORPUS_SHA256)
        self.assertEqual(self.perfect["source_sha256"], hashlib.sha256(ctx).hexdigest())
        changed_ctx_hash = hashlib.sha256(ctx + b"\n").hexdigest()
        for wrong_hash in (changed_ctx_hash, "007b6a40b0c65247f881627375c3d2e9b6aeeb5dfa89957494feed0765a1a073"):
            prediction = copy.deepcopy(self.perfect)
            prediction["source_sha256"] = wrong_hash
            report = self.score(prediction)
            self.assertFalse(report["structural"]["valid"])
            self.assertTrue(any("sha256(ctx)" in error for error in report["structural"]["errors"]))
            self.assertEqual(report["source_sha256"], hashlib.sha256(ctx).hexdigest())
            self.assertEqual(report["aggregate"]["accuracy"], 1)

    def test_reversed_contract_order_is_structural_only(self):
        baseline = self.score(self.perfect)
        prediction = copy.deepcopy(self.perfect)
        prediction["contracts"].reverse()
        report = self.score(prediction)
        self.assertFalse(report["structural"]["valid"])
        self.assertTrue(any("rows must follow source order" in error for error in report["structural"]["errors"]))
        self.assertEqual(report["structural"]["observed_cells"], 510)
        for key in ("matrix", "per_field", "aggregate", "citations", "queries"):
            self.assertEqual(report[key], baseline[key])

    def test_reversed_query_partition_order_is_structural_only(self):
        for label in grader.LABELS:
            with self.subTest(label=label):
                prediction = self.prediction("unknown") if label == "unknown" else copy.deepcopy(self.perfect)
                baseline = self.score(prediction)
                entries = prediction["queries"]["transfer_exposure"][label]
                self.assertGreater(len(entries), 1)
                entries.reverse()
                report = self.score(prediction)
                self.assertFalse(report["structural"]["valid"])
                self.assertFalse(report["queries"]["declared_consistent"])
                self.assertTrue(any("recomputed source-order list" in error for error in report["structural"]["errors"]))
                for key in ("matrix", "per_field", "aggregate", "citations"):
                    self.assertEqual(report[key], baseline[key])
                self.assertEqual(report["queries"]["recomputed"], baseline["queries"]["recomputed"])
                self.assertEqual(report["queries"]["scores"], baseline["queries"]["scores"])

    def test_python39_syntax(self):
        for path in (HERE / "grade.py", Path(__file__)):
            ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))


if __name__ == "__main__":
    unittest.main()
