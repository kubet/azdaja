"""Offline acceptance tests for the standalone HTML review queue."""
import base64
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "jev_review_queue.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


queue = load("queue_under_test", SCRIPT)
# Reuse just the existing synthetic fixture, without inheriting/discovering its tests.
support = load("batch_review_fixture", ROOT / "tests" / "test_jev_batch_review.py")


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.order = []
        self.sources = {}
        self.details = {}
        self.sections = {}
        self.section = None
        self.window = None
        self.source = False
        self.criteria = ""
        self.styles = []
        self.in_style = False
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "section":
            self.section = attrs["id"]
        if tag == "style":
            self.in_style = True
            self.styles.append("")
        if tag == "details" and attrs.get("id", "").startswith("window-"):
            self.window = attrs["id"].removeprefix("window-")
            self.order.append(self.window)
            self.sources[self.window] = ""
            self.details[self.window] = ""
            self.sections[self.window] = self.section
        if tag == "pre" and attrs.get("class") == "source":
            self.source = True

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        if tag == "pre":
            self.source = False
        if tag == "details":
            self.window = None
        if tag == "section":
            self.section = None

    def handle_data(self, data):
        if self.in_style:
            self.styles[-1] += data
        if self.window is not None:
            self.details[self.window] += data
            if self.source:
                self.sources[self.window] += data
        if self.section == "criteria":
            self.criteria += data


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.fixture = support.ReportTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.output = self.root / "queue.html"
        # Default tests exercise scratch under output's parent, independent of host env.
        environment = mock.patch.dict(os.environ, {"JCODE_SCRATCH_DIR": ""})
        environment.start()
        self.addCleanup(environment.stop)

    def export(self):
        queue.export(self.fixture.plan, self.fixture.job, self.output)
        text = self.output.read_text(encoding="utf-8")
        return text, Document(text)

    def rebind(self):
        f = self.fixture
        data = b"".join(f.review._encode(r) + b"\n" for r in f.rows)
        (f.plan / "plan.jsonl").write_bytes(data)
        f.manifest["binding"]["input_sha256"] = hashlib.sha256(data).hexdigest()
        f.manifest["binding"]["requests"] = [
            {"id": r["id"], "request_sha256": f.request_hash(r)} for r in f.rows
        ]
        f.save(f.job / "manifest.json", f.manifest)

    def make_plan(self, sources, question="Does this contain consent?"):
        files = []
        for index, (name, data) in enumerate(sources):
            directory = self.root / f"custom-{index}"
            directory.mkdir()
            path = directory / name
            path.write_bytes(data)
            files.append(path)
        f = self.fixture
        f.plan = self.root / "custom-plan"
        f.review.prepare(question, f.plan, files)
        f.rows = [json.loads(line) for line in (f.plan / "plan.jsonl").read_bytes().splitlines()]
        self.rebind()

    def assert_full_identity(self, document):
        f = self.fixture
        self.assertEqual(len(document.order), len(f.rows))
        self.assertEqual(set(document.order), {r["id"] for r in f.rows})
        for row in f.rows:
            state, ident = row["state"], row["id"]
            raw = document.sources[ident].encode("utf-8")
            self.assertEqual(raw, state["text"].encode("utf-8"))
            self.assertEqual(len(raw), state["end_byte"] - state["start_byte"])
            for value in (ident, state["source_name"], state["source_sha256"],
                          f'[{state["start_byte"]}, {state["end_byte"]})'):
                self.assertIn(value, document.details[ident])
        sources = json.loads((f.plan / "sources.json").read_text())
        for source in sources:
            prefix = f'{source["source_index"]:06d}-'
            raw = b"".join(document.sources[key].encode("utf-8")
                           for key in sorted(document.sources) if key.startswith(prefix))
            self.assertEqual(len(raw), source["size_bytes"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), source["source_sha256"])

    def test_full_coverage_exact_audit_fields_stable_ties_and_extremes(self):
        f = self.fixture
        self.assertEqual(len(f.rows), 4)
        for index, p in enumerate([0.8, 1, 0.8, 0]):
            f.record(index, p)
        text, doc = self.export()
        self.assertEqual(doc.order, [f.rows[i]["id"] for i in (1, 0, 2, 3)])
        self.assert_full_identity(doc)
        self.assertIn("2 source occurrences, 4 of 4 windows", text)
        total = sum(len(r["state"]["text"].encode()) for r in f.rows)
        self.assertIn(f"{total} UTF-8 bytes", text)
        self.assertIn("Completed: 4. Unknown: 0. Pending: 0.", text)
        self.assertIn("Probability is not truth.", text)
        self.assertIn(f.rows[0]["questions"]["match"]["instructions"], doc.criteria)
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o600)
        self.assertEqual(text.count("Source occurrence "), 2)
        self.assertNotIn(str(self.root), text)
        for i, p in enumerate([0.8, 1, 0.8, 0]):
            self.assertIn(f"raw noul: {p}", doc.details[f.rows[i]["id"]])

    def test_unknown_ambiguous_and_pending_retained_separately(self):
        f = self.fixture
        f.record(0, 0.5)  # A middle value is still shown, never silently filtered.
        failed = f.record(1)
        failed.update(status="failed", observation=None)
        f.save(f.job / "000001.result.json", failed)
        f.record(2)
        (f.job / "000002.result.json").unlink()
        text, doc = self.export()
        self.assert_full_identity(doc)
        self.assertIn("Completed: 1. Unknown: 2. Pending: 1.", text)
        self.assertEqual([doc.sections[r["id"]] for r in f.rows],
                         ["completed", "unknown", "unknown", "pending"])
        self.assertIn("unknown_inflight", doc.details[f.rows[2]["id"]])
        for row in f.rows[1:]:
            self.assertIn("raw noul: null", doc.details[row["id"]])

    def test_all_pending_is_full_coverage_not_empty_queue(self):
        text, doc = self.export()
        self.assert_full_identity(doc)
        self.assertIn("Completed: 0. Unknown: 0. Pending: 4.", text)

    def test_hostile_names_sources_questions_and_answers_are_inert(self):
        hostile = '\n</code></pre></details><script>alert("x")</script>'
        hostile += '<img src="https://evil.invalid/a" onerror="alert(1)">'
        hostile += '<a href="javascript:alert(1)">x</a>&amp;\r\nž🐉\rEND'
        hostile += '</style><style>body{display:none}</style>'
        name = '<img src=x onerror="alert(1)">&.txt'
        question = 'Is <script>alert("criteria")</script> present?'
        self.make_plan([(name, hostile.encode())], question)
        record = self.fixture.record(0, 0.1234567890123456)
        record["observation"]["answers"]["match"]["extra"] = hostile
        self.fixture.save(self.fixture.job / "000000.result.json", record)
        text, doc = self.export()
        self.assert_full_identity(doc)
        self.assertIn(question, doc.criteria)
        self.assertIn("raw noul: 0.1234567890123456", text)
        self.assertIn("&lt;script&gt;", text)
        self.assertIn("&#13;", text)
        for tag, attrs in doc.tags:
            self.assertNotIn(tag, {"script", "link", "img", "iframe", "object",
                                   "embed", "base", "form", "input", "button", "svg", "math"})
            for key, value in attrs.items():
                self.assertFalse(key.lower().startswith("on"))
                self.assertNotIn(key.lower(), {"src", "srcset", "action", "style"})
                if key == "href":
                    self.assertTrue(value.startswith("#"))
        policies = [attrs["content"] for tag, attrs in doc.tags
                    if tag == "meta" and attrs.get("http-equiv") == "Content-Security-Policy"]
        self.assertEqual(len(policies), 1)
        self.assertIn("default-src 'none'", policies[0])
        self.assertIn("script-src 'none'", policies[0])
        self.assertEqual(doc.styles, [queue.STYLE])
        digest = base64.b64encode(hashlib.sha256(doc.styles[0].encode()).digest()).decode()
        directives = dict(part.strip().split(" ", 1) for part in policies[0].split(";"))
        self.assertEqual(directives["style-src"], f"'sha256-{digest}'")
        self.assertEqual(directives["style-src-attr"], "'none'")
        self.assertNotIn("unsafe-inline", policies[0])
        self.assertNotIn("url(", doc.styles[0].lower())
        self.assertNotIn("@import", doc.styles[0].lower())
        self.assertEqual([attrs for tag, attrs in doc.tags if tag == "style"], [{}])

    def test_coverage_collapsed_and_wrapping_styles_keep_all_text(self):
        text, doc = self.export()
        coverage = [attrs for tag, attrs in doc.tags
                    if tag == "details" and attrs.get("id") == "coverage-sources"]
        self.assertEqual(coverage, [{"id": "coverage-sources"}])
        self.assertIn("Full-source coverage (2 source occurrences)", text)
        self.assertIn("pre { white-space: pre-wrap; overflow-wrap: anywhere;", doc.styles[0])
        self.assert_full_identity(doc)
        start = text.index('<details id="coverage-sources">')
        end = text.index('</details>', start)
        self.assertLess(end, text.index('<section id="completed">'))
        self.assertEqual(text[start:end].count("Source occurrence "), 2)

    def test_nul_text_rejected_before_render_in_source_name_criteria_and_raw_answer(self):
        f = self.fixture
        original_rows = json.dumps(f.rows)
        original_sources = (f.plan / "sources.json").read_text()
        for channel in ("source", "name", "criteria", "raw_answer"):
            with self.subTest(channel=channel):
                f.rows = json.loads(original_rows)
                sources = json.loads(original_sources)
                first_source = [r for r in f.rows if r["id"].startswith("000000-")]
                if channel == "source":
                    state = first_source[0]["state"]
                    state["text"] = "\0" + state["text"][1:]
                    digest = hashlib.sha256(b"".join(r["state"]["text"].encode()
                                                   for r in first_source)).hexdigest()
                    sources[0]["source_sha256"] = digest
                    for row in first_source:
                        row["state"]["source_sha256"] = digest
                elif channel == "name":
                    sources[0]["source_name"] = "name\0.txt"
                    for row in first_source:
                        row["state"]["source_name"] = "name\0.txt"
                elif channel == "criteria":
                    for row in f.rows:
                        row["questions"]["match"]["instructions"] += "\0"
                f.save(f.plan / "sources.json", sources)
                self.rebind()
                record = f.record(0)
                if channel == "raw_answer":
                    record["observation"]["answers"]["match"]["extra"] = {"nested": ["text\0"]}
                    f.save(f.job / "000000.result.json", record)
                # Prove this targets the HTML boundary, not another binding failure.
                f.review.report(f.plan, f.job, self.root / (channel + ".jsonl"))
                with mock.patch.object(queue, "_render") as render:
                    with self.assertRaisesRegex(ValueError, "NUL.*UTF-8 HTML"):
                        self.export()
                    render.assert_not_called()
                self.assertFalse(self.output.exists())
                self.assertEqual(list(self.root.glob("jev-review-queue-*")), [])

    def test_unicode_boundaries_full_bytes_before_any_render(self):
        data = ('\nž🐉e\u0301\r\n&<>"\t' * 11000).encode()
        self.make_plan([("unicode.txt", data)])
        self.assertGreater(len(self.fixture.rows), 1)
        render = queue._render
        seen = []

        def inspect(rows, criteria):
            self.assertEqual(b"".join(r["text"].encode() for r in rows), data)
            offset = 0
            for row in rows:
                self.assertEqual(row["start_byte"], offset)
                offset += len(row["text"].encode())
                self.assertEqual(row["end_byte"], offset)
                self.assertEqual(row["source_sha256"], hashlib.sha256(data).hexdigest())
            seen.append(True)
            return render(rows, criteria)

        with mock.patch.object(queue, "_render", side_effect=inspect):
            _, doc = self.export()
        self.assertEqual(seen, [True])
        self.assert_full_identity(doc)

    def test_changed_last_source_rejected_before_render_even_if_input_rebound(self):
        f = self.fixture
        f.rows[-1]["state"]["text"] = "X" + f.rows[-1]["state"]["text"][1:]
        self.rebind()
        with mock.patch.object(queue, "_render") as render:
            with self.assertRaises(ValueError):
                self.export()
            render.assert_not_called()
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.root.glob("jev-review-queue-*")), [])

    def test_changed_response_binding_is_rejected(self):
        f = self.fixture
        item = f.record(3)
        item["observation"]["_azdaja"]["request_sha256"] = "0" * 64
        f.save(f.job / "000003.result.json", item)
        with mock.patch.object(queue, "_render") as render:
            with self.assertRaises(ValueError):
                self.export()
            render.assert_not_called()
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.root.glob("jev-review-queue-*")), [])

    def test_mixed_criteria_rejected_despite_valid_individual_bindings(self):
        f = self.fixture
        f.rows[-1]["questions"]["match"]["instructions"] = "A different meaning entirely"
        self.rebind()
        for i in range(len(f.rows)):
            f.record(i)
        # The frozen report accepts the job, but global ranking must reject it.
        f.review.report(f.plan, f.job, self.root / "valid-mixed.jsonl")
        with mock.patch.object(queue, "_render") as render:
            with self.assertRaisesRegex(ValueError, "identical noul match"):
                self.export()
            render.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_wrong_question_shape_rejected_even_for_pending_jobs(self):
        for question in ({"match": {"type": "bool", "instructions": "Q"}},
                         {"match": {"type": "noul", "instructions": ""}},
                         {"other": {"type": "noul", "instructions": "Q"}}):
            with self.subTest(question=question):
                for row in self.fixture.rows:
                    row["questions"] = question
                self.rebind()
                with self.assertRaises(ValueError):
                    self.export()
                self.assertFalse(self.output.exists())

    def test_occupied_dangling_and_live_symlink_outputs_unchanged(self):
        target = self.root / "target"
        for kind in ("file", "directory", "dangling", "live"):
            with self.subTest(kind=kind):
                self.output = self.root / (kind + ".html")
                if kind == "file":
                    self.output.write_bytes(b"keep exactly")
                elif kind == "directory":
                    self.output.mkdir()
                else:
                    if kind == "live":
                        target.write_bytes(b"target stays")
                    self.output.symlink_to(target)
                before = self.output.lstat()
                with mock.patch.object(queue._review, "report") as report:
                    with self.assertRaises(ValueError):
                        self.export()
                    report.assert_not_called()
                self.assertEqual(self.output.lstat(), before)
                if kind == "file":
                    self.assertEqual(self.output.read_bytes(), b"keep exactly")
                elif kind == "dangling":
                    self.assertFalse(target.exists())
                elif kind == "live":
                    self.assertEqual(target.read_bytes(), b"target stays")

    def test_exclusive_helper_rejects_output_created_during_validation(self):
        render = queue._render

        def occupy(rows, criteria):
            self.output.symlink_to(self.root / "absent")
            return render(rows, criteria)

        with mock.patch.object(queue, "_render", side_effect=occupy):
            with self.assertRaises(FileExistsError):
                self.export()
        self.assertTrue(self.output.is_symlink())
        self.assertFalse((self.root / "absent").exists())
        self.assertEqual(list(self.root.glob("jev-review-queue-*")), [])

    def test_private_temporary_snapshot_report_and_cleanup_success_and_failure(self):
        scratch = self.root / "scratch"
        scratch.mkdir()
        original_report = queue._review.report
        seen = []

        def inspect(plan, job, output):
            self.assertEqual(output.parent.parent, scratch)
            self.assertEqual(output.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(plan.stat().st_mode & 0o777, 0o700)
            for name in ("plan.jsonl", "sources.json"):
                self.assertEqual((plan / name).stat().st_mode & 0o777, 0o600)
                self.assertEqual((plan / name).read_bytes(), (self.fixture.plan / name).read_bytes())
            original_report(plan, job, output)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            seen.append(output.parent)

        with mock.patch.dict(os.environ, {"JCODE_SCRATCH_DIR": str(scratch)}):
            with mock.patch.object(queue._review, "report", side_effect=inspect):
                self.export()
            self.assertEqual(list(scratch.iterdir()), [])
            self.output = self.root / "failure.html"
            with mock.patch.object(queue, "_render", side_effect=ValueError("render failed")):
                with self.assertRaises(ValueError):
                    self.export()
            self.assertEqual(list(scratch.iterdir()), [])
        self.assertEqual(len(seen), 1)
        self.assertFalse(seen[0].exists())
        self.assertFalse(self.output.exists())

    def test_unsafe_source_and_response_file_symlinks_rejected(self):
        for path in (self.fixture.plan / "sources.json", self.fixture.job / "manifest.json"):
            with self.subTest(path=path.name):
                saved = path.with_suffix(".saved")
                path.rename(saved)
                path.symlink_to(saved)
                try:
                    with self.assertRaises((ValueError, OSError)):
                        self.export()
                    self.assertFalse(self.output.exists())
                finally:
                    path.unlink()
                    saved.rename(path)

    def test_deterministic_export_and_no_network_even_when_all_completed(self):
        import socket

        for index in range(len(self.fixture.rows)):
            self.fixture.record(index, 0.7)
        with mock.patch.object(socket, "socket", side_effect=AssertionError("network forbidden")):
            with mock.patch.object(socket, "create_connection", side_effect=AssertionError("network forbidden")):
                first, first_doc = self.export()
                self.output = self.root / "second.html"
                second, second_doc = self.export()
        self.assertEqual(first, second)
        self.assertEqual(first_doc.order, sorted(first_doc.order))
        self.assert_full_identity(second_doc)

    def test_original_paths_not_required_and_prepared_inputs_remain_unchanged(self):
        f = self.fixture
        paths = [f.plan / "plan.jsonl", f.plan / "sources.json", f.job / "manifest.json"]
        before = {path: (path.read_bytes(), path.stat()) for path in paths}
        for directory in (self.root / "0", self.root / "1"):
            (directory / "same.txt").unlink()
        _, doc = self.export()
        self.assert_full_identity(doc)
        for path, (data, metadata) in before.items():
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(path.stat().st_mtime_ns, metadata.st_mtime_ns)
            self.assertEqual(path.stat().st_mode, metadata.st_mode)

    def test_cli_malformed_schema_and_non_html_output_fail_cleanly(self):
        import io

        f = self.fixture
        for destination, malformed in ((self.root / "wrong.txt", False),
                                       (self.output, True)):
            with self.subTest(destination=destination.name):
                if malformed:
                    f.rows[-1]["id"] = 42
                    self.rebind()
                error = io.StringIO()
                with mock.patch("sys.stderr", error), mock.patch.object(queue, "_render") as render:
                    code = queue.main(["--plan", str(f.plan), "--job", str(f.job),
                                       "--output", str(destination)])
                self.assertEqual(code, 2)
                self.assertIn("no provider was contacted", error.getvalue())
                self.assertNotIn("Traceback", error.getvalue())
                render.assert_not_called()
                self.assertFalse(destination.exists())
                self.assertEqual(list(self.root.glob("jev-review-queue-*")), [])

    def test_actual_cli_outside_repo_isolated_stdlib_and_required_arguments(self):
        f = self.fixture
        f.record(0)
        env = {"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1"}
        command = [sys.executable, "-I", "-S", "-B", str(SCRIPT)]
        args = ["--plan", str(f.plan), "--job", str(f.job), "--output", str(self.output)]
        completed = subprocess.run(command + args, cwd=self.root, env=env,
                                   capture_output=True, text=True, timeout=30)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assert_full_identity(Document(self.output.read_text()))
        before = self.output.read_bytes()
        occupied = subprocess.run(command + args, cwd=self.root, env=env,
                                  capture_output=True, text=True, timeout=30)
        self.assertEqual(occupied.returncode, 2)
        self.assertEqual(self.output.read_bytes(), before)
        for omit in (0, 2, 4):
            missing = subprocess.run(command + args[:omit] + args[omit + 2:],
                                     cwd=self.root, env=env, capture_output=True,
                                     text=True, timeout=30)
            self.assertEqual(missing.returncode, 2)
        self.assertEqual(list(self.root.glob("jev-review-queue-*")), [])


if __name__ == "__main__":
    unittest.main()
