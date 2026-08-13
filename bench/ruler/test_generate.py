import copy
import hashlib
from dataclasses import replace
import importlib.util
import json
import os
import stat
import sys
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("azdaja_ruler_generate", HERE / "generate.py")
GENERATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GENERATE
assert SPEC.loader is not None
SPEC.loader.exec_module(GENERATE)

SCORE_SPEC = importlib.util.spec_from_file_location("azdaja_ruler_score_for_generate", HERE / "score.py")
SCORE = importlib.util.module_from_spec(SCORE_SPEC)
sys.modules[SCORE_SPEC.name] = SCORE
assert SCORE_SPEC.loader is not None
SCORE_SPEC.loader.exec_module(SCORE)


class CharacterEncoding:
    def encode(self, text):
        return list(text)


class GenerateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        if os.name == "posix":
            self.root.chmod(0o700)
        self.master = bytes(range(32))
        self.plan = GENERATE.build_plan(self.master)

    def tearDown(self):
        self.temporary.cleanup()

    def private_dir(self, path):
        path.mkdir(mode=0o700, parents=True, exist_ok=False)
        if os.name == "posix":
            path.chmod(0o700)
        return path

    def private_file(self, path, data):
        path.write_bytes(data)
        if os.name == "posix":
            path.chmod(0o600)
        return path

    def write_plan(self):
        path = self.root / "plan.json"
        self.private_file(path, GENERATE.canonical_json_bytes(self.plan))
        return path

    @staticmethod
    def row(task, target_length, ordinal):
        if task == "niah_multikey_3":
            outputs = [f"00000000-0000-4000-8000-{target_length + ordinal:012x}"]
            query = f"11111111-1111-4111-8111-{target_length + ordinal:012x}"
            input_text = (
                "A special magic uuid is hidden within the following text. "
                "Make sure to memorize it. I will quiz you about the uuid afterwards.\n"
                + ("filler " * ordinal)
                + f"The special magic uuid for {query} is {outputs[0]}."
                + f"\nWhat is the special magic uuid for {query} mentioned in the provided text?"
            )
            answer_prefix = (
                f" The special magic uuid for {query} mentioned in the provided text is"
            )
            extra = {
                "token_position_answer": input_text.find(outputs[0]),
            }
            upstream_index = input_text.find(outputs[0])
        elif task == "vt":
            outputs = ["AAAAA", "BBBBB", "CCCCC", "DDDDD", "EEEEE"]
            query = "12345"
            context = (
                " AAAAA = BBBBB; BBBBB = CCCCC; CCCCC = DDDDD; DDDDD = EEEEE; EEEEE = 12345."
                + f" Target length {target_length}."
                + (" The grass is green." * ordinal)
            )
            input_text = (
                "Memorize and track the chain(s) of variable assignment hidden in the following text.\n\n"
                + context
                + f"\nQuestion: Find all variables that are assigned the value {query} in the text above."
            )
            answer_prefix = (
                f" Answer: According to the chain(s) of variable assignment in the text above, "
                f"5 variables are assigned the value {query}, they are: "
            )
            extra = {}
            upstream_index = ordinal
        else:
            outputs = ["aaaaaa", "bbbbbb", "cccccc"]
            cell_word = {8192: "dddddd", 32768: "eeeeee", 131072: "ffffff"}[target_length]
            context = (
                " aaaaaa bbbbbb cccccc aaaaaa bbbbbb aaaaaa cccccc bbbbbb aaaaaa "
                + cell_word
                + (" ..." * (ordinal + 1))
            )
            input_text = (
                "Read the following coded text and track the frequency of each coded word. "
                "Find the three most frequently appeared coded words. "
                + context
                + "\nQuestion: Do not provide any explanation. Please ignore the dots '....'. "
                "What are the three most frequently appeared words in the above coded text?"
            )
            answer_prefix = (
                " Answer: According to the coded text above, the three most frequently appeared words are:"
            )
            extra = {}
            upstream_index = ordinal
        payload = input_text + answer_prefix
        length = len(payload) + GENERATE.TASK_SPECS[task].reserve
        return {
            "index": upstream_index,
            "input": input_text,
            "outputs": outputs,
            "length": length,
            "length_w_model_temp": length,
            "answer_prefix": answer_prefix,
            **extra,
        }

    def write_pool(self, mutate=None):
        pool = self.private_dir(self.root / "pool")
        for target_length in GENERATE.LENGTHS:
            length_dir = self.private_dir(pool / str(target_length))
            for task in GENERATE.TASKS:
                task_dir = self.private_dir(length_dir / task)
                rows = [self.row(task, target_length, i) for i in range(GENERATE.POOL_SIZE)]
                if mutate is not None:
                    mutate(task, target_length, rows)
                encoded = b"".join(GENERATE.canonical_json_bytes(row) for row in rows)
                self.private_file(task_dir / "test.jsonl", encoded)
        return pool

    @staticmethod
    def provenance():
        upstream = {
            "url": GENERATE.RULER_URL,
            "commit": GENERATE.RULER_COMMIT,
            "files": dict(GENERATE.SOURCE_HASHES),
        }
        dependencies = {
            "requirements_lock_sha256": GENERATE.REQUIREMENTS_LOCK_SHA256,
            "python": {
                "implementation": "CPython",
                "version": "3.11.13",
                "executable": sys.executable,
                "build": ["test", "test"],
            },
            "platform": {
                "description": "test",
                "os": "Darwin",
                "release": "test",
                "machine": "test",
            },
            "packages": dict(GENERATE.LOCKED_VERSIONS),
            "wheels": {
                name: {"filename": f"{name}-{version}-py3-none-any.whl", "sha256": "a" * 64}
                for name, version in GENERATE.LOCKED_VERSIONS.items()
            },
            "site_packages_sha256": "b" * 64,
            "tokenizer": {
                "name": GENERATE.TOKENIZER,
                "blob_sha256": GENERATE.TOKENIZER_BLOB_SHA256,
                "cache_filename": GENERATE.TOKENIZER_CACHE_NAME,
            },
            "nltk_resources": dict(GENERATE.NLTK_RESOURCE_HASHES),
        }
        return upstream, dependencies

    def pool_bytes(self, pool):
        return {
            (task, target_length): GENERATE.read_pool_cell_bytes(pool, task, target_length)
            for target_length in GENERATE.LENGTHS
            for task in GENERATE.TASKS
        }

    @staticmethod
    def generation_receipts():
        return {
            (task, target_length): GENERATE.canonical_generation_receipt(
                task=task,
                target_length=target_length,
                seed=GENERATE._generator_seed(bytes(range(32)), task, target_length),
            )
            for target_length in GENERATE.LENGTHS
            for task in GENERATE.TASKS
        }


    def publish(self, *, pool, out, gold_out, plan_path, upstream, dependencies):
        license_bytes = b"pinned license test bytes\n"
        notice_bytes = b"third-party notice test bytes\n"
        source_hashes = dict(GENERATE.SOURCE_HASHES)
        source_hashes["LICENSE"] = hashlib.sha256(license_bytes).hexdigest()
        upstream = copy.deepcopy(upstream)
        upstream["files"] = source_hashes
        with mock.patch.object(GENERATE, "SOURCE_HASHES", source_hashes), mock.patch.object(
            GENERATE,
            "THIRD_PARTY_NOTICES_SHA256",
            hashlib.sha256(notice_bytes).hexdigest(),
        ):
            return GENERATE.publish_verified_suite(
                verified_pool_bytes=self.pool_bytes(pool),
                generation_receipts=self.generation_receipts(),
                out=out,
                gold_out=gold_out,
                plan_path=plan_path,
                encoding=CharacterEncoding(),
                upstream=upstream,
                dependencies=dependencies,
                ruler_license_bytes=license_bytes,
                third_party_notice_bytes=notice_bytes,
            )

    def test_plan_derives_all_seeds_and_rejects_tampering(self):
        same = GENERATE.build_plan(self.master)
        self.assertEqual(self.plan, same)
        self.assertEqual(len(self.plan["cells"]), 9)
        self.assertEqual(len({cell["generator_seed"] for cell in self.plan["cells"]}), 9)
        self.assertNotIn(42, {cell["generator_seed"] for cell in self.plan["cells"]})
        GENERATE.validate_plan(self.plan)
        changed = copy.deepcopy(self.plan)
        changed["cells"][0]["generator_seed"] += 1
        with self.assertRaisesRegex(GENERATE.SealError, "changed"):
            GENERATE.validate_plan(changed)
        with self.assertRaisesRegex(GENERATE.SealError, "32 bytes"):
            GENERATE.build_plan(b"short")
        wrong_type = copy.deepcopy(self.plan)
        wrong_type["schema_version"] = True
        with self.assertRaisesRegex(GENERATE.SealError, "changed"):
            GENERATE.validate_plan(wrong_type)
        with self.assertRaisesRegex(GENERATE.SealError, "lone Unicode surrogate"):
            GENERATE.parse_json_object(b'{"value":"\\ud800"}', "surrogate test")

    def test_exact_payload_validation_and_task_domains(self):
        row = self.row("vt", 8192, 7)
        raw = GENERATE.canonical_json_bytes(row).rstrip(b"\n")
        checked = GENERATE.validate_row(
            row,
            raw_bytes=raw,
            ordinal=7,
            task="vt",
            target_length=8192,
            encoding=CharacterEncoding(),
        )
        self.assertEqual(checked.payload, row["input"] + row["answer_prefix"])
        self.assertEqual(checked.payload_bytes, checked.payload.encode("utf-8"))
        self.assertEqual(checked.construction_tokens, len(checked.payload))

        wrong_length = dict(row, length=row["length"] + 1, length_w_model_temp=row["length"] + 1)
        with self.assertRaisesRegex(GENERATE.SealError, "exact payload token count"):
            GENERATE.validate_row(
                wrong_length,
                raw_bytes=raw,
                ordinal=7,
                task="vt",
                target_length=8192,
                encoding=CharacterEncoding(),
            )
        bad_gold = dict(row, outputs=["AAAAA", "BBBBB", "CCCCC", "DDDDD", "bad!!"])
        with self.assertRaisesRegex(GENERATE.SealError, "task-domain"):
            GENERATE.validate_row(
                bad_gold,
                raw_bytes=raw,
                ordinal=7,
                task="vt",
                target_length=8192,
                encoding=CharacterEncoding(),
            )

    def test_selection_is_deterministic_and_niah_covers_deciles(self):
        rows = []
        for ordinal in range(100):
            row = self.row("niah_multikey_3", 8192, ordinal)
            raw = GENERATE.canonical_json_bytes(row).rstrip(b"\n")
            rows.append(
                GENERATE.validate_row(
                    row,
                    raw_bytes=raw,
                    ordinal=ordinal,
                    task="niah_multikey_3",
                    target_length=8192,
                    encoding=CharacterEncoding(),
                )
            )
        first = GENERATE.select_rows(rows, "niah_multikey_3", 8192, self.master)
        second = GENERATE.select_rows(rows, "niah_multikey_3", 8192, self.master)
        self.assertEqual([item.ordinal for item, _ in first], [item.ordinal for item, _ in second])
        self.assertEqual([meta["decile"] for _, meta in first], list(range(10)))
        sorted_positions = sorted(row.token_position_answer for row in rows)
        for decile, (item, _) in enumerate(first):
            self.assertIn(item.token_position_answer, sorted_positions[decile * 10 : (decile + 1) * 10])

        vt_rows = []
        for ordinal in range(100):
            row = self.row("vt", 8192, ordinal)
            raw = GENERATE.canonical_json_bytes(row).rstrip(b"\n")
            vt_rows.append(
                GENERATE.validate_row(
                    row,
                    raw_bytes=raw,
                    ordinal=ordinal,
                    task="vt",
                    target_length=8192,
                    encoding=CharacterEncoding(),
                )
            )
        vt = GENERATE.select_rows(vt_rows, "vt", 8192, self.master)
        self.assertEqual(len(vt), 10)
        self.assertEqual(len({item.ordinal for item, _ in vt}), 10)
        # VT/FWE line-ordinal selection is precommitted before row contents exist.
        changed_hashes = [replace(item, raw_row_sha256=f"{item.ordinal:064x}") for item in vt_rows]
        changed = GENERATE.select_rows(changed_hashes, "vt", 8192, self.master)
        self.assertEqual([item.ordinal for item, _ in vt], [item.ordinal for item, _ in changed])

    def test_pool_is_exact_private_and_rejects_duplicate_json_keys(self):
        pool = self.write_pool()
        rows = GENERATE.load_pool_cell(pool, "fwe", 8192, CharacterEncoding())
        self.assertEqual(len(rows), 100)
        path = pool / "8192" / "fwe" / "test.jsonl"
        data = path.read_bytes()
        first, rest = data.split(b"\n", 1)
        malformed = first[:-1] + b',"input":"duplicate"}\n' + rest
        self.private_file(path, malformed)
        with self.assertRaisesRegex(GENERATE.SealError, "duplicate JSON key"):
            GENERATE.load_pool_cell(pool, "fwe", 8192, CharacterEncoding())

        if os.name == "posix":
            path.chmod(0o644)
            with self.assertRaisesRegex(GENERATE.SealError, "0600"):
                GENERATE.load_pool_cell(pool, "fwe", 8192, CharacterEncoding())

    def test_seal_separates_public_manifest_and_gold_with_two_way_commitments(self):
        plan_path = self.write_plan()
        pool = self.write_pool()
        upstream, dependencies = self.provenance()
        out = self.root / "sealed-public"
        gold_dir = self.private_dir(self.root / "private")
        gold_out = gold_dir / "gold.json"
        manifest_path, gold_path = self.publish(
            pool=pool,
            out=out,
            gold_out=gold_out,
            plan_path=plan_path,
            upstream=upstream,
            dependencies=dependencies,
        )
        manifest_bytes = manifest_path.read_bytes()
        gold_bytes = gold_path.read_bytes()
        manifest = json.loads(manifest_bytes)
        gold = json.loads(gold_bytes)
        self.assertEqual(manifest["suite_id"], GENERATE.SUITE_ID)
        self.assertEqual(
            set(manifest["redistribution_files"]),
            {"LICENSE.NVIDIA-RULER", "THIRD_PARTY_NOTICES.md"},
        )
        for filename, expected_hash in manifest["redistribution_files"].items():
            self.assertEqual(hashlib.sha256((out / filename).read_bytes()).hexdigest(), expected_hash)
        self.assertEqual(len(manifest["fixtures"]), 90)
        self.assertEqual(len(gold["fixtures"]), 90)
        self.assertEqual(hashlib.sha256(gold_bytes).hexdigest(), manifest["gold_sha256"])
        identity = dict(manifest)
        del identity["gold_sha256"]
        self.assertEqual(
            hashlib.sha256(GENERATE.canonical_json_bytes(identity)).hexdigest(),
            gold["manifest_identity_sha256"],
        )
        def all_keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key
                    yield from all_keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from all_keys(child)

        public_keys = set(all_keys(manifest))
        for forbidden in ("outputs", "generator_seed", "master_key_hex", "raw_row_sha256", "ordinal"):
            self.assertNotIn(forbidden, public_keys)
        public_ids = {item["id"] for item in manifest["fixtures"]}
        gold_ids = {item["id"] for item in gold["fixtures"]}
        self.assertEqual(public_ids, gold_ids)
        for fixture in gold["fixtures"]:
            raw = fixture["raw_row_utf8"].encode("utf-8")
            self.assertEqual(hashlib.sha256(raw).hexdigest(), fixture["raw_row_sha256"])
            parsed = GENERATE.parse_json_object(raw, "selected raw row")
            self.assertEqual(parsed["outputs"], fixture["outputs"])
            self.assertEqual(
                hashlib.sha256(GENERATE.canonical_json_bytes(parsed)).hexdigest(),
                fixture["canonical_row_sha256"],
            )
        # Contract test against the independent fail-closed scorer.
        if hasattr(SCORE, "EXPECTED_REDISTRIBUTION_FILES"):
            with mock.patch.object(
                SCORE, "EXPECTED_RULER_SOURCE_HASHES",
                gold["provenance"]["upstream"]["files"],
            ), mock.patch.object(
                SCORE, "EXPECTED_REDISTRIBUTION_FILES", manifest["redistribution_files"],
            ):
                score_manifest, score_fixtures = SCORE.load_public_manifest(manifest_path)
                _, score_gold = SCORE.load_gold(gold_path, score_manifest, score_fixtures)
            self.assertEqual(set(score_gold), public_ids)
        for fixture in manifest["fixtures"]:
            self.assertEqual(
                set(fixture),
                {
                    "id",
                    "task",
                    "target_length",
                    "payload",
                    "payload_sha256",
                    "payload_bytes",
                    "construction_tokens",
                    "row_length",
                },
            )
            payload = out / fixture["payload"]
            self.assertEqual(hashlib.sha256(payload.read_bytes()).hexdigest(), fixture["payload_sha256"])
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(manifest_path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(gold_path.stat().st_mode), 0o600)
            for fixture in manifest["fixtures"]:
                self.assertEqual(stat.S_IMODE((out / fixture["payload"]).stat().st_mode), 0o600)
        self.assertFalse((out / "gold.json").exists())
        self.assertTrue(os.path.samefile(gold_path, gold_out))
        self.assertTrue((out / "LICENSE.NVIDIA-RULER").is_file())
        self.assertTrue((out / "THIRD_PARTY_NOTICES.md").is_file())
        with self.assertRaisesRegex(GENERATE.SealError, "already exists|refusing overwrite"):
            self.publish(
                pool=pool,
                out=out,
                gold_out=gold_out,
                plan_path=plan_path,
                upstream=upstream,
                dependencies=dependencies,
            )

    def test_duplicate_payload_anywhere_fails_before_publication(self):
        plan_path = self.write_plan()

        def mutate(task, target_length, rows):
            if task == "vt" and target_length == 8192:
                rows[1] = copy.deepcopy(rows[0])
                rows[1]["index"] = 1

        pool = self.write_pool(mutate=mutate)
        upstream, dependencies = self.provenance()
        out = self.root / "sealed-public"
        gold_dir = self.private_dir(self.root / "gold-private")
        gold_out = gold_dir / "gold.json"
        with self.assertRaisesRegex(GENERATE.SealError, "duplicate payload hash"):
            self.publish(
                pool=pool,
                out=out,
                gold_out=gold_out,
                plan_path=plan_path,
                upstream=upstream,
                dependencies=dependencies,
            )
        self.assertFalse(out.exists())
        self.assertFalse(gold_out.exists())

    def test_authentic_task_shapes_and_semantic_tampering_fail_closed(self):
        for task in GENERATE.TASKS:
            row = self.row(task, 8192, 4)
            GENERATE.validate_row(
                row,
                raw_bytes=GENERATE.canonical_json_bytes(row).rstrip(b"\n"),
                ordinal=4,
                task=task,
                target_length=8192,
                encoding=CharacterEncoding(),
            )
        extra = self.row("vt", 8192, 4)
        extra["unofficial_config"] = {"num_chains": 2}
        with self.assertRaisesRegex(GENERATE.SealError, "exact row keys"):
            GENERATE.validate_row(
                extra, raw_bytes=b"{}", ordinal=4, task="vt", target_length=8192,
                encoding=CharacterEncoding(),
            )
        bad_vt = self.row("vt", 8192, 4)
        bad_vt["answer_prefix"] = bad_vt["answer_prefix"].replace("12345", "ABCDE")
        with self.assertRaisesRegex(GENERATE.SealError, "VT 1-chain/4-hop prefix"):
            GENERATE.validate_row(
                bad_vt, raw_bytes=b"{}", ordinal=4, task="vt", target_length=8192,
                encoding=CharacterEncoding(),
            )
        bad_niah = self.row("niah_multikey_3", 8192, 4)
        bad_niah["index"] += 1
        with self.assertRaisesRegex(GENERATE.SealError, "answer index/position"):
            GENERATE.validate_row(
                bad_niah, raw_bytes=b"{}", ordinal=4, task="niah_multikey_3",
                target_length=8192, encoding=CharacterEncoding(),
            )
        bad_fwe = self.row("fwe", 8192, 4)
        bad_fwe["outputs"] = list(reversed(bad_fwe["outputs"]))
        with self.assertRaisesRegex(GENERATE.SealError, "frequency order"):
            GENERATE.validate_row(
                bad_fwe, raw_bytes=b"{}", ordinal=4, task="fwe", target_length=8192,
                encoding=CharacterEncoding(),
            )

    def _make_git_source(self, files):
        source = self.private_dir(self.root / f"source-{len(list(self.root.iterdir()))}")
        for relative, data in files.items():
            path = source / relative
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(0o600)
        subprocess.run(["git", "init", "-q", str(source)], check=True)
        subprocess.run(["git", "-C", str(source), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(source), "config", "user.name", "test"], check=True)
        subprocess.run(["git", "-C", str(source), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(source), "commit", "-qm", "pinned"], check=True)
        commit = subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
        hashes = {relative: hashlib.sha256(data).hexdigest() for relative, data in files.items()}
        return source, commit, hashes

    def test_clean_archive_isolation_rejects_dirty_untracked_and_never_runs_fsmonitor(self):
        source, commit, hashes = self._make_git_source({"scripts/data/prepare.py": b"print('safe')\n"})
        marker = self.root / "fsmonitor-pwned"
        hook = self.root / "fsmonitor-hook.sh"
        hook.write_text(f"#!/bin/sh\ntouch '{marker}'\n")
        hook.chmod(0o700)
        subprocess.run(
            ["git", "-C", str(source), "config", "core.fsmonitor", str(hook)], check=True
        )
        with mock.patch.object(GENERATE, "RULER_COMMIT", commit), mock.patch.object(
            GENERATE, "SOURCE_HASHES", hashes
        ):
            receipt = GENERATE.validate_source(source)
            self.assertEqual(receipt["commit"], commit)
            self.assertFalse(marker.exists())
            snapshot = GENERATE.extract_pinned_source_archive(source, self.root / "snapshot")
            self.assertFalse((snapshot / ".git").exists())
            self.assertEqual((snapshot / "scripts/data/prepare.py").read_bytes(), b"print('safe')\n")
            (source / "shadow.py").write_text("malicious")
            with self.assertRaisesRegex(GENERATE.SealError, "exactly match"):
                GENERATE.validate_source(source)
            (source / "shadow.py").unlink()
            (source / "scripts/data/prepare.py").write_text("dirty")
            with self.assertRaisesRegex(GENERATE.SealError, "hash mismatch|exactly match"):
                GENERATE.validate_source(source)
        self.assertFalse(marker.exists())

    def test_pinned_commit_gitlink_is_rejected_without_checkout(self):
        source, commit, hashes = self._make_git_source({"prepare.py": b"safe\n"})
        subprocess.run(
            [
                "git", "-C", str(source), "update-index", "--add", "--cacheinfo",
                f"160000,{commit},vendor/submodule",
            ],
            check=True,
        )
        subprocess.run(["git", "-C", str(source), "commit", "-qm", "gitlink"], check=True)
        gitlink_commit = subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
        with mock.patch.object(GENERATE, "RULER_COMMIT", gitlink_commit), mock.patch.object(
            GENERATE, "SOURCE_HASHES", hashes
        ):
            with self.assertRaisesRegex(GENERATE.SealError, "submodule/gitlink"):
                GENERATE.validate_source(source)

    def test_locked_wheel_snapshot_rejects_pth_customization_and_traversal(self):
        wheelhouse = self.private_dir(self.root / "bad-wheelhouse")

        def bad_wheel(name, member):
            stream = GENERATE.io.BytesIO()
            with GENERATE.zipfile.ZipFile(stream, "w") as bundle:
                bundle.writestr(member, b"malicious")
            data = stream.getvalue()
            self.private_file(wheelhouse / name, data)
            return data

        for index, member in enumerate(("evil.pth", "sitecustomize.py", "../escape.py")):
            filename = f"bad{index}-1.0-py3-none-any.whl"
            data = bad_wheel(filename, member)
            dependencies = {
                "wheels": {
                    "bad": {"filename": filename, "sha256": hashlib.sha256(data).hexdigest()}
                }
            }
            destination = self.root / f"runtime-{index}"
            with self.assertRaisesRegex(GENERATE.SealError, "unsafe or unsupported"):
                GENERATE.materialize_wheel_snapshot(
                    wheelhouse=wheelhouse,
                    dependencies=dependencies,
                    destination=destination,
                )
            self.assertFalse((self.root / "escape.py").exists())

    def test_dependency_snapshot_safely_extracts_pinned_nltk_without_network_fallback(self):
        def archive(root_name):
            stream = GENERATE.io.BytesIO()
            with GENERATE.zipfile.ZipFile(stream, "w") as bundle:
                bundle.writestr(f"{root_name}/README", b"pinned")
            return stream.getvalue()

        punkt = archive("punkt")
        punkt_tab = archive("punkt_tab")
        source = self.private_dir(self.root / "dependency-source")
        tokenizer = self.private_dir(source / "tiktoken")
        nltk_source = self.private_dir(source / "nltk")
        tokenizers = self.private_dir(nltk_source / "tokenizers")
        self.private_file(tokenizer / GENERATE.TOKENIZER_CACHE_NAME, b"tokenizer")
        self.private_file(tokenizers / "punkt.zip", punkt)
        self.private_file(tokenizers / "punkt_tab.zip", punkt_tab)

        class FakeNltkData:
            path = []

            @staticmethod
            def find(relative):
                candidate = Path(FakeNltkData.path[0]) / relative
                if not candidate.is_dir():
                    raise LookupError(relative)
                return candidate

        fake_nltk = SimpleNamespace(data=FakeNltkData)
        hashes = {
            "tokenizers/punkt.zip": hashlib.sha256(punkt).hexdigest(),
            "tokenizers/punkt_tab.zip": hashlib.sha256(punkt_tab).hexdigest(),
        }
        with mock.patch.object(
            GENERATE, "TOKENIZER_BLOB_SHA256", hashlib.sha256(b"tokenizer").hexdigest()
        ), mock.patch.object(GENERATE, "NLTK_RESOURCE_HASHES", hashes), mock.patch.dict(
            sys.modules, {"nltk": fake_nltk}
        ):
            _, nltk_snapshot = GENERATE.materialize_dependency_snapshot(
                tokenizer_cache_dir=tokenizer,
                nltk_data=nltk_source,
                destination=self.root / "dependency-snapshot",
            )
        self.assertTrue((nltk_snapshot / "tokenizers/punkt/README").is_file())
        self.assertTrue((nltk_snapshot / "tokenizers/punkt_tab/README").is_file())
        stream = GENERATE.io.BytesIO()
        with GENERATE.zipfile.ZipFile(stream, "w") as bundle:
            bundle.writestr("../escape", b"bad")
        with self.assertRaisesRegex(GENERATE.SealError, "unsafe NLTK"):
            GENERATE._extract_nltk_zip(stream.getvalue(), self.root, "punkt")

    def test_internal_generation_uses_exact_interpreter_and_catches_false_zero(self):
        script = b'''import argparse\nfrom pathlib import Path\np=argparse.ArgumentParser()\np.add_argument("--save_dir")\np.add_argument("--task")\na,_=p.parse_known_args()\nout=Path(a.save_dir)/a.task/"test.jsonl"\nout.parent.mkdir(parents=True)\nout.write_bytes(b"exact-internal-pool\\n")\n'''
        source, commit, hashes = self._make_git_source({"scripts/data/prepare.py": script})
        with mock.patch.object(GENERATE, "RULER_COMMIT", commit), mock.patch.object(
            GENERATE, "SOURCE_HASHES", hashes
        ):
            GENERATE.validate_source(source)
            snapshot = GENERATE.extract_pinned_source_archive(source, self.root / "internal-source")
        cache = self.private_dir(self.root / "cache")
        nltk = self.private_dir(self.root / "nltk")
        plan = {"cells": [{"task": "vt", "target_length": 8192, "generator_seed": 123}]}
        with mock.patch.object(GENERATE, "TASKS", ("vt",)), mock.patch.object(
            GENERATE, "LENGTHS", (8192,)
        ):
            with mock.patch.object(GENERATE.shutil, "which", return_value=sys.executable):
                generated, receipts = GENERATE.generate_official_pool(
                    source_snapshot=snapshot,
                    reproduction_root=self.root / "generated",
                    plan=plan,
                    tokenizer_cache_dir=cache,
                    nltk_data=nltk,
                    site_packages=cache,
                )
            self.assertEqual(generated[("vt", 8192)], b"exact-internal-pool\n")
            self.assertEqual(receipts[("vt", 8192)]["generation_argv"][0], sys.executable)
            (snapshot / "scripts/data/prepare.py").write_text("# false zero: no output\n")
            with self.assertRaisesRegex(GENERATE.SealError, "success without output"):
                with mock.patch.object(GENERATE.shutil, "which", return_value=sys.executable):
                    GENERATE.generate_official_pool(
                        source_snapshot=snapshot,
                        reproduction_root=self.root / "false-zero",
                        plan=plan,
                        tokenizer_cache_dir=cache,
                        nltk_data=nltk,
                        site_packages=cache,
                    )

    def test_split_publication_fsync_failure_never_removes_published_gold(self):
        plan_path = self.write_plan()
        pool = self.write_pool()
        upstream, dependencies = self.provenance()
        out = self.root / "public-after-fsync-error"
        gold_dir = self.private_dir(self.root / "gold-after-fsync-error")
        gold_out = gold_dir / "gold.json"
        original = GENERATE.fsync_directory

        def fail_after_public_rename(path):
            if Path(path) == self.root.resolve() and out.exists():
                raise GENERATE.SealError("injected public parent fsync failure")
            return original(path)

        with mock.patch.object(GENERATE, "fsync_directory", side_effect=fail_after_public_rename):
            with self.assertRaisesRegex(GENERATE.SealError, "injected"):
                self.publish(
                    pool=pool, out=out, gold_out=gold_out, plan_path=plan_path,
                    upstream=upstream, dependencies=dependencies,
                )
        self.assertTrue((out / "manifest.json").is_file())
        self.assertTrue(gold_out.is_file())
        manifest = json.loads((out / "manifest.json").read_bytes())
        self.assertEqual(hashlib.sha256(gold_out.read_bytes()).hexdigest(), manifest["gold_sha256"])

    def test_raced_public_target_is_not_replaced_and_private_gold_rolls_back(self):
        plan_path = self.write_plan()
        pool = self.write_pool()
        upstream, dependencies = self.provenance()
        out = self.root / "raced-public"
        gold_dir = self.private_dir(self.root / "raced-private")
        gold_out = gold_dir / "gold.json"
        original = GENERATE.rename_directory_noreplace

        def race(source, target):
            target.mkdir(mode=0o700)
            return original(source, target)

        with mock.patch.object(GENERATE, "rename_directory_noreplace", side_effect=race):
            with self.assertRaisesRegex(GENERATE.SealError, "raced into existence"):
                self.publish(
                    pool=pool, out=out, gold_out=gold_out, plan_path=plan_path,
                    upstream=upstream, dependencies=dependencies,
                )
        self.assertTrue(out.is_dir())
        self.assertEqual(list(out.iterdir()), [])
        self.assertFalse(gold_out.exists())

    def test_documented_private_paths_and_build_only_cli(self):
        readme = (HERE / "README.md").read_text()
        self.assertIn('PUBLIC="$G/ruler-exact-mini-v1-public"', readme)
        self.assertIn('GOLD="$G/private/gold.json"', readme)
        self.assertNotIn("SEALED=/private/tmp", readme)
        self.assertIn('pwd -P', readme)
        private = self.private_dir(self.root / "private")
        public_target, gold_target = GENERATE.validate_public_gold_targets(
            self.root / "ruler-exact-mini-v1-public", private / "gold.json"
        )
        self.assertEqual(public_target.parent, self.root.resolve())
        self.assertEqual(gold_target.parent, private.resolve())
        parser = GENERATE.build_parser()
        self.assertIn("build", parser._subparsers._group_actions[0].choices)
        self.assertNotIn("seal", parser._subparsers._group_actions[0].choices)
        with self.assertRaisesRegex(GENERATE.SealError, "separate"):
            GENERATE.validate_public_gold_targets(self.root / "public", self.root / "gold.json")
        unsafe = self.root / "x;touch$IFS" / "marker"
        unsafe.mkdir(mode=0o700, parents=True)
        with self.assertRaisesRegex(GENERATE.SealError, "unsafe for pinned RULER"):
            GENERATE.require_shell_safe_build_path(unsafe, "malicious scratch")
        with mock.patch.object(GENERATE.subprocess, "run") as spawned:
            with self.assertRaisesRegex(GENERATE.SealError, "unsafe for pinned RULER"):
                GENERATE.generate_official_pool(
                    source_snapshot=unsafe,
                    reproduction_root=self.root / "never-spawned",
                    plan={"cells": []},
                    tokenizer_cache_dir=self.root,
                    nltk_data=self.root,
                    site_packages=self.root,
                )
            spawned.assert_not_called()
        with mock.patch.object(GENERATE.os, "name", "nt"):
            with self.assertRaisesRegex(GENERATE.SealError, "only on POSIX"):
                GENERATE.require_posix_security()

    def test_scratch_parent_is_private_and_random_mkdtemp_root_is_revalidated(self):
        scratch = self.private_dir(self.root / "scratch-parent")
        first = Path(tempfile.mkdtemp(prefix="azdaja-ruler-build-", dir=scratch))
        second = Path(tempfile.mkdtemp(prefix="azdaja-ruler-build-", dir=scratch))
        first.chmod(0o700)
        second.chmod(0o700)
        self.assertNotEqual(first, second)
        GENERATE.require_private_dir(first, "random scratch")
        if os.name == "posix":
            first.chmod(0o755)
            with self.assertRaisesRegex(GENERATE.SealError, "0700"):
                GENERATE.require_private_dir(first, "unsafe scratch")
            first.chmod(0o700)
        symlink = scratch / "symlink"
        symlink.symlink_to(first)
        with self.assertRaisesRegex(GENERATE.SealError, "must not be a symlink"):
            GENERATE.require_private_dir(symlink, "symlink scratch")

    def test_unisolated_runtime_and_site_customization_fail_before_build(self):
        with self.assertRaisesRegex(GENERATE.SealError, "-I -S -B"):
            GENERATE.require_isolated_runtime()
        fake_flags = SimpleNamespace(isolated=1, no_site=1, dont_write_bytecode=1)
        with mock.patch.object(GENERATE.sys, "flags", fake_flags), mock.patch.object(
            GENERATE.sys, "path", ["/trusted/stdlib", "/evil/site-packages"]
        ):
            with self.assertRaisesRegex(GENERATE.SealError, "unverified site-packages"):
                GENERATE.require_isolated_runtime()

    def test_design_arguments_are_frozen_and_lock_hash_is_pinned(self):
        good = SimpleNamespace(
            tasks=list(GENERATE.TASKS),
            lengths=list(GENERATE.LENGTHS),
            pool_size=100,
            per_cell=10,
        )
        GENERATE._require_exact_design_args(good)
        bad = SimpleNamespace(**vars(good))
        bad.tasks = ["vt"]
        with self.assertRaisesRegex(GENERATE.SealError, "frozen"):
            GENERATE._require_exact_design_args(bad)
        lock = HERE / "requirements.lock"
        self.assertEqual(hashlib.sha256(lock.read_bytes()).hexdigest(), GENERATE.REQUIREMENTS_LOCK_SHA256)
        notice = HERE / "THIRD_PARTY_NOTICES.md"
        self.assertEqual(
            hashlib.sha256(notice.read_bytes()).hexdigest(),
            GENERATE.THIRD_PARTY_NOTICES_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
