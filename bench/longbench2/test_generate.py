import copy
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import sys
import tempfile
import unittest
from unittest import mock
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("azdaja_lb2_generate", HERE / "generate.py")
GENERATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GENERATE
assert SPEC.loader is not None
SPEC.loader.exec_module(GENERATE)


class GenerateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        if os.name == "posix":
            self.root.chmod(0o700)
        self.saved = {
            "EXPECTED_SOURCE_COUNT": GENERATE.EXPECTED_SOURCE_COUNT,
            "EXPECTED_COUNT": GENERATE.EXPECTED_COUNT,
            "CELL_COUNTS": GENERATE.CELL_COUNTS,
            "SELECTED_DOMAIN_COUNTS": GENERATE.SELECTED_DOMAIN_COUNTS,
            "SELECTED_SUB_DOMAIN_COUNTS": GENERATE.SELECTED_SUB_DOMAIN_COUNTS,
            "SOURCE_FILES": copy.deepcopy(GENERATE.SOURCE_FILES),
        }
        self.rows = self.fixture_rows()
        GENERATE.EXPECTED_SOURCE_COUNT = len(self.rows)
        GENERATE.EXPECTED_COUNT = 2
        GENERATE.CELL_COUNTS = dict(Counter((x["difficulty"], x["length"]) for x in self.rows))
        selected = [x for x in self.rows if x["difficulty"] == "hard" and x["length"] == "long"]
        GENERATE.SELECTED_DOMAIN_COUNTS = dict(Counter(x["domain"] for x in selected))
        GENERATE.SELECTED_SUB_DOMAIN_COUNTS = dict(Counter(x["sub_domain"] for x in selected))
        self.data_path = self.write_source(self.rows)
        self.readme = self.write_and_pin("README.md", b"fixture upstream readme\n")
        self.gitattributes = self.write_and_pin(".gitattributes", b"*.json filter=lfs\n")
        self.key = self.private_file(self.root / "random.key", bytes(range(32)))

    def tearDown(self):
        for key, value in self.saved.items():
            setattr(GENERATE, key, value)
        self.temporary.cleanup()

    @staticmethod
    def fixture_rows():
        cells = [
            ("easy", "long"), ("easy", "medium"), ("easy", "short"),
            ("hard", "long"), ("hard", "long"), ("hard", "medium"),
            ("hard", "short"),
        ]
        domains = [
            "Single-Document QA", "Multi-Document QA", "Long In-context Learning",
            "Code Repository Understanding", "Multi-Document QA",
            "Long Structured Data Understanding", "Long-dialogue History Understanding",
        ]
        subs = ["Academic", "Governmental", "New language translation", "Code repo QA",
                "Literary", "Table QA", "Dialogue history QA"]
        answers = ["B", "C", "D", "A", "D", "B", "C"]
        result = []
        for i, ((difficulty, length), domain, sub, answer) in enumerate(zip(cells, domains, subs, answers)):
            # Dict insertion order intentionally mirrors the exact pinned upstream schema.
            result.append({
                "_id": f"{i + 1:024x}",
                "domain": domain,
                "sub_domain": sub,
                "difficulty": difficulty,
                "length": length,
                "question": f"Question {i}? Unicode snowman ☃\nand line two",
                "choice_A": f"alpha {i}",
                "choice_B": f"beta {i}",
                "choice_C": f"gamma {i}",
                "choice_D": f"delta {i}",
                "answer": answer,
                "context": f"Exact context {i}\nwith spacing  and tabs\tkept.",
            })
        return result

    def private_file(self, path, data):
        path.write_bytes(data)
        if os.name == "posix":
            path.chmod(0o600)
        return path

    def write_source_bytes(self, data):
        path = self.private_file(self.root / "data.json", data)
        GENERATE.SOURCE_FILES["data.json"] = {
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "git_oid": "0" * 40, "lfs_oid_sha256": hashlib.sha256(data).hexdigest(),
        }
        return path

    def write_source(self, rows):
        data = json.dumps(rows, ensure_ascii=False, indent=2).encode("utf-8")
        return self.write_source_bytes(data)

    def write_and_pin(self, name, data):
        path = self.private_file(self.root / name, data)
        GENERATE.SOURCE_FILES[name] = {
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "git_oid": "1" * 40,
        }
        return path

    def seal(self, suffix="one", key=None):
        return GENERATE.seal_suite(
            data_path=self.data_path, readme_path=self.readme,
            gitattributes_path=self.gitattributes,
            requirements_lock=HERE / "requirements.lock",
            out_public=self.root / f"public-{suffix}", out_gold=self.root / f"gold-{suffix}",
            key_path=self.key if key is None else key,
        )

    def test_pinned_provenance_constants_and_stdlib_lock(self):
        saved = self.saved["SOURCE_FILES"]
        self.assertEqual(GENERATE.SOURCE_REVISION, "2b48e494f2c7a2f0af81aae178e05c7e1dde0fe9")
        self.assertEqual(saved["data.json"]["sha256"], "15d61c22d92c96900b3c4948b6aeea218d3214b676a65df48e7b8555604c7fe2")
        self.assertEqual(saved["data.json"]["bytes"], 465490535)
        self.assertEqual(saved["README.md"]["sha256"], "9fdd1a3ebe86507253c124a18e9f78c898ce6341c12990af17ab868b8f600c35")
        self.assertEqual(saved[".gitattributes"]["sha256"], "b3ca89743b410b60a97ba9486e44b205c70f6fb35024ef02198cf766dfdffb18")
        lock = (HERE / "requirements.lock").read_bytes()
        self.assertEqual(hashlib.sha256(lock).hexdigest(), GENERATE.REQUIREMENTS_LOCK_SHA256)
        self.assertNotIn(b"==", lock)

    def test_seal_preserves_exact_fields_and_separates_gold(self):
        manifest_path, gold_path = self.seal()
        self.assertNotEqual(manifest_path.parent, gold_path.parent)
        self.assertNotIn(manifest_path.parent, gold_path.parents)
        manifest_bytes = manifest_path.read_bytes()
        gold_bytes = gold_path.read_bytes()
        manifest = json.loads(manifest_bytes)
        gold = json.loads(gold_bytes)
        self.assertEqual(manifest_bytes, GENERATE.canonical_json_bytes(manifest))
        self.assertEqual(gold_bytes, GENERATE.canonical_json_bytes(gold))
        self.assertEqual(len(manifest["fixtures"]), 2)
        self.assertEqual(len(gold["fixtures"]), 2)
        self.assertEqual(manifest["configuration"]["domain_counts"],
                         GENERATE.SELECTED_DOMAIN_COUNTS)
        self.assertEqual(manifest["configuration"]["sub_domain_counts"],
                         GENERATE.SELECTED_SUB_DOMAIN_COUNTS)
        self.assertEqual(
            set(path.name for path in manifest_path.parent.iterdir()),
            {"manifest.json", "payloads", *GENERATE.PUBLIC_NOTICE_FILES},
        )
        self.assertEqual(set(path.name for path in gold_path.parent.iterdir()), {"gold.json"})
        for name, expected in GENERATE.PUBLIC_NOTICE_FILES.items():
            notice = manifest_path.parent / name
            self.assertEqual(notice.stat().st_size, expected["bytes"])
            self.assertEqual(hashlib.sha256(notice.read_bytes()).hexdigest(), expected["sha256"])
        self.assertEqual(
            manifest["provenance_commitments"]["public_notice_files"],
            {name: value["sha256"] for name, value in GENERATE.PUBLIC_NOTICE_FILES.items()},
        )
        self.assertEqual(hashlib.sha256(gold_bytes).hexdigest(), manifest["gold_sha256"])
        identity = dict(manifest)
        del identity["gold_sha256"]
        self.assertEqual(hashlib.sha256(GENERATE.canonical_json_bytes(identity)).hexdigest(),
                         gold["manifest_identity_sha256"])
        gold_by_id = {item["id"]: item for item in gold["fixtures"]}
        selected_by_ordinal = {i: row for i, row in enumerate(self.rows)
                               if row["difficulty"] == "hard" and row["length"] == "long"}
        for public in manifest["fixtures"]:
            self.assertRegex(public["id"], r"^lb2-[0-9a-f]{32}$")
            payload_path = manifest_path.parent / public["payload"]
            payload_bytes = payload_path.read_bytes()
            payload = json.loads(payload_bytes)
            self.assertEqual(payload_bytes, GENERATE.canonical_json_bytes(payload))
            self.assertEqual(hashlib.sha256(payload_bytes).hexdigest(), public["payload_sha256"])
            gold_item = gold_by_id[public["id"]]
            source = selected_by_ordinal[gold_item["source_ordinal"]]
            self.assertEqual(payload, {
                "question": source["question"], "context": source["context"],
                "choices": {label: source[f"choice_{label}"] for label in GENERATE.CHOICE_LABELS},
            })
            self.assertEqual(gold_item["answer"], source["answer"])
        if os.name == "posix":
            for root in (manifest_path.parent, gold_path.parent, manifest_path.parent / "payloads"):
                self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)
            for path in [
                manifest_path, gold_path,
                *(manifest_path.parent / "payloads").iterdir(),
                *(manifest_path.parent / name for name in GENERATE.PUBLIC_NOTICE_FILES),
            ]:
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_public_tree_has_no_gold_identity_or_answer_fields(self):
        manifest_path, _ = self.seal()
        manifest = json.loads(manifest_path.read_text())
        public_values = [manifest]
        public_values.extend(json.loads((manifest_path.parent / x["payload"]).read_text())
                             for x in manifest["fixtures"])
        keys = set()
        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    keys.add(key); walk(child)
            elif isinstance(value, list):
                for child in value: walk(child)
        for value in public_values: walk(value)
        for forbidden in ("answer", "source_id", "source_ordinal", "raw_row_sha256",
                          "canonical_row_sha256", "randomization_key_sha256"):
            self.assertNotIn(forbidden, keys)
        self.assertFalse((manifest_path.parent / "gold.json").exists())

    def test_fixture_ids_are_randomized_by_owner_secret_and_do_not_use_source_ids(self):
        first, _ = self.seal("first")
        second_key = self.private_file(self.root / "other.key", bytes(reversed(range(32))))
        second, _ = self.seal("second", key=second_key)
        first_ids = {x["id"] for x in json.loads(first.read_text())["fixtures"]}
        second_ids = {x["id"] for x in json.loads(second.read_text())["fixtures"]}
        self.assertTrue(first_ids.isdisjoint(second_ids))
        for row in self.rows:
            self.assertTrue(all(row["_id"] not in identity for identity in first_ids | second_ids))

    def test_schema_count_and_cell_drift_fail_closed(self):
        broken = copy.deepcopy(self.rows)
        broken[0]["extra"] = "schema drift"
        self.data_path = self.write_source(broken)
        with self.assertRaisesRegex(GENERATE.SealError, "schema/order drift"):
            self.seal("schema")
        self.assertFalse((self.root / "public-schema").exists())

        broken = copy.deepcopy(self.rows[:-1])
        self.data_path = self.write_source(broken)
        with self.assertRaisesRegex(GENERATE.SealError, "exactly"):
            self.seal("count")
        self.assertFalse((self.root / "public-count").exists())

        broken = copy.deepcopy(self.rows)
        broken[0]["difficulty"] = "hard"
        self.data_path = self.write_source(broken)
        with self.assertRaisesRegex(GENERATE.SealError, "cell drift"):
            self.seal("cell")
        self.assertFalse((self.root / "public-cell").exists())

    def test_duplicate_rows_ids_payloads_and_invalid_answer_fail(self):
        cases = []
        duplicate_id = copy.deepcopy(self.rows); duplicate_id[1]["_id"] = duplicate_id[0]["_id"]
        cases.append((duplicate_id, "duplicate upstream"))
        duplicate_payload = copy.deepcopy(self.rows)
        for field in ("question", "context", "choice_A", "choice_B", "choice_C", "choice_D"):
            duplicate_payload[1][field] = duplicate_payload[0][field]
        cases.append((duplicate_payload, "duplicate question/context/choices"))
        bad_answer = copy.deepcopy(self.rows); bad_answer[0]["answer"] = "E"
        cases.append((bad_answer, "answer must"))
        for i, (rows, message) in enumerate(cases):
            self.data_path = self.write_source(rows)
            with self.assertRaisesRegex(GENERATE.SealError, message):
                self.seal(f"bad-{i}")

    def test_duplicate_keys_nonfinite_and_trailing_json_fail(self):
        row = json.dumps(self.rows[0], ensure_ascii=False)
        duplicated = ("[" + row[:-1] + ', "answer":"A"}' + "]").encode()
        GENERATE.EXPECTED_SOURCE_COUNT = 1
        self.data_path = self.write_source_bytes(duplicated)
        with self.assertRaisesRegex(GENERATE.SealError, "duplicate JSON key"):
            GENERATE.load_and_validate_source(self.data_path)

        nonfinite = b'[{"x":NaN}]'
        self.data_path = self.write_source_bytes(nonfinite)
        with self.assertRaisesRegex(GENERATE.SealError, "non-finite"):
            GENERATE.load_and_validate_source(self.data_path)

        trailing = json.dumps(self.rows).encode() + b" garbage"
        GENERATE.EXPECTED_SOURCE_COUNT = len(self.rows)
        self.data_path = self.write_source_bytes(trailing)
        with self.assertRaisesRegex(GENERATE.SealError, "trailing content"):
            GENERATE.load_and_validate_source(self.data_path)

        trailing_comma = (json.dumps(self.rows)[:-1] + ", ]").encode()
        self.data_path = self.write_source_bytes(trailing_comma)
        with self.assertRaisesRegex(GENERATE.SealError, "trailing array comma"):
            GENERATE.load_and_validate_source(self.data_path)

    def test_hash_lock_mode_symlink_and_output_tampering_fail(self):
        self.data_path.write_bytes(self.data_path.read_bytes() + b" ")
        with self.assertRaisesRegex(GENERATE.SealError, "source data.json drift"):
            self.seal("hash")
        self.data_path = self.write_source(self.rows)

        if os.name == "posix":
            self.data_path.chmod(0o644)
            with self.assertRaisesRegex(GENERATE.SealError, "0600"):
                self.seal("mode")
            self.data_path.chmod(0o600)
            target = self.root / "real-data.json"
            self.data_path.rename(target)
            self.data_path.symlink_to(target)
            with self.assertRaisesRegex(GENERATE.SealError, "symlink"):
                self.seal("link")
            self.data_path.unlink(); target.rename(self.data_path)
            self.readme.chmod(0o644)
            with self.assertRaisesRegex(GENERATE.SealError, "0600"):
                self.seal("companion-mode")
            self.readme.chmod(0o600)

        lock = self.private_file(self.root / "requirements.lock", b"changed\n")
        with self.assertRaisesRegex(GENERATE.SealError, "requirements lock drift"):
            GENERATE.seal_suite(
                data_path=self.data_path, readme_path=self.readme,
                gitattributes_path=self.gitattributes, requirements_lock=lock,
                out_public=self.root / "public-lock", out_gold=self.root / "gold-lock",
                key_path=self.key,
            )
        existing = self.root / "public-existing"; existing.mkdir()
        with self.assertRaisesRegex(GENERATE.SealError, "already exists"):
            GENERATE.seal_suite(
                data_path=self.data_path, readme_path=self.readme,
                gitattributes_path=self.gitattributes, requirements_lock=HERE / "requirements.lock",
                out_public=existing, out_gold=self.root / "gold-existing", key_path=self.key,
            )

    def test_output_parent_must_be_exact_owner_only(self):
        if os.name != "posix":
            self.skipTest("POSIX ownership/mode contract")
        shared = self.root / "shared"
        shared.mkdir(mode=0o755)
        shared.chmod(0o755)
        with self.assertRaisesRegex(GENERATE.SealError, "parent mode must be 0700"):
            GENERATE.seal_suite(
                data_path=self.data_path, readme_path=self.readme,
                gitattributes_path=self.gitattributes,
                requirements_lock=HERE / "requirements.lock",
                out_public=shared / "public", out_gold=self.root / "gold-shared",
                key_path=self.key,
            )

    def test_mkdtemp_failure_cleans_fd_relative_temporary_directory(self):
        real = GENERATE._mkdir_temp_at
        created_names = []
        def injected(parent, *, prefix):
            if created_names:
                raise OSError("injected second mkdir failure")
            name, fd = real(parent, prefix=prefix)
            created_names.append(name)
            return name, fd
        with mock.patch.object(GENERATE, "_mkdir_temp_at", side_effect=injected):
            with self.assertRaisesRegex(OSError, "injected"):
                self.seal("mkdir-race")
        self.assertEqual(len(created_names), 1)
        self.assertFalse((self.root / created_names[0]).exists())
        abandoned = list(self.root.glob(created_names[0] + ".abandoned-*"))
        self.assertEqual(len(abandoned), 1)
        self.assertTrue(abandoned[0].is_dir())
        shutil.rmtree(abandoned[0])
        self.assertFalse((self.root / "public-mkdir-race").exists())
        self.assertFalse((self.root / "gold-mkdir-race").exists())

    def test_gold_publication_race_never_replaces_or_deletes_racer_target(self):
        real = GENERATE._rename_noreplace_at
        racer = self.root / "gold-gold-race"
        sentinel = racer / "racer.txt"
        def injected(parent, source_name, target_name):
            if target_name == racer.name:
                racer.mkdir(mode=0o700)
                sentinel.write_text("owned by racer")
                sentinel.chmod(0o600)
            return real(parent, source_name, target_name)
        with mock.patch.object(GENERATE, "_rename_noreplace_at", side_effect=injected):
            with self.assertRaisesRegex(GENERATE.SealError, "already exists"):
                self.seal("gold-race")
        self.assertEqual(sentinel.read_text(), "owned by racer")
        self.assertFalse((self.root / "public-gold-race").exists())

    def test_public_publication_race_leaves_durable_gold_and_racer_untouched(self):
        real = GENERATE._rename_noreplace_at
        public = self.root / "public-public-race"
        gold = self.root / "gold-public-race"
        racer_identity = []
        def injected(parent, source_name, target_name):
            if target_name == public.name:
                public.mkdir(mode=0o700)
                metadata = public.stat()
                racer_identity.append((metadata.st_dev, metadata.st_ino))
            return real(parent, source_name, target_name)
        with mock.patch.object(GENERATE, "_rename_noreplace_at", side_effect=injected):
            with self.assertRaisesRegex(GENERATE.SealError, "already exists"):
                self.seal("public-race")
        metadata = public.stat()
        self.assertEqual((metadata.st_dev, metadata.st_ino), racer_identity[0])
        self.assertEqual(list(public.iterdir()), [])
        self.assertEqual({path.name for path in gold.iterdir()}, {"gold.json"})
        self.assertEqual(stat.S_IMODE((gold / "gold.json").stat().st_mode), 0o600)

    def test_parent_path_swap_is_detected_while_held_fd_tree_is_not_redirected(self):
        public_parent = self.root / "public-parent"
        gold_parent = self.root / "gold-parent"
        public_parent.mkdir(mode=0o700); gold_parent.mkdir(mode=0o700)
        if os.name == "posix":
            public_parent.chmod(0o700); gold_parent.chmod(0o700)
        moved = self.root / "gold-parent-moved"
        replacement_marker = gold_parent / "replacement.txt"
        real = GENERATE._verify_parent_handle
        swapped = []
        gold_checks = []
        def injected(parent, label):
            if label == "gold output parent":
                gold_checks.append(True)
            if label == "gold output parent" and len(gold_checks) == 2 and not swapped:
                gold_parent.rename(moved)
                gold_parent.mkdir(mode=0o700)
                replacement_marker.write_text("racer parent")
                replacement_marker.chmod(0o600)
                swapped.append(True)
            return real(parent, label)
        with mock.patch.object(GENERATE, "_verify_parent_handle", side_effect=injected):
            with self.assertRaisesRegex(GENERATE.SealError, "swapped"):
                GENERATE.seal_suite(
                    data_path=self.data_path, readme_path=self.readme,
                    gitattributes_path=self.gitattributes,
                    requirements_lock=HERE / "requirements.lock",
                    out_public=public_parent / "public", out_gold=gold_parent / "gold",
                    key_path=self.key,
                )
        self.assertEqual(replacement_marker.read_text(), "racer parent")
        self.assertFalse((gold_parent / "gold").exists())
        self.assertFalse((public_parent / "public").exists())
        leftovers = list(moved.iterdir())
        self.assertEqual(len(leftovers), 1)
        self.assertIn(".abandoned-", leftovers[0].name)
        shutil.rmtree(leftovers[0])

    def test_cleanup_name_swap_never_deletes_racer_replacement(self):
        real_cleanup = GENERATE._cleanup_temp_at
        real_mkdir = GENERATE._mkdir_temp_at
        created = []
        def mkdir_injected(parent, *, prefix):
            if created:
                raise OSError("injected before second temporary")
            name, fd = real_mkdir(parent, prefix=prefix)
            created.append((parent.path, name))
            return name, fd
        swapped = []
        def cleanup_injected(parent, name, temp_fd):
            if not swapped:
                held = parent.path / name
                kidnapped = parent.path / (name + ".kidnapped")
                held.rename(kidnapped)
                held.mkdir(mode=0o700)
                marker = held / "racer.txt"
                marker.write_text("do not delete")
                marker.chmod(0o600)
                swapped.append((held, kidnapped, marker))
            return real_cleanup(parent, name, temp_fd)
        with mock.patch.object(GENERATE, "_mkdir_temp_at", side_effect=mkdir_injected), \
             mock.patch.object(GENERATE, "_cleanup_temp_at", side_effect=cleanup_injected):
            with self.assertRaisesRegex(OSError, "injected"):
                self.seal("cleanup-swap")
        held, kidnapped, marker = swapped[0]
        self.assertEqual(marker.read_text(), "do not delete")
        self.assertTrue(kidnapped.is_dir())
        shutil.rmtree(held)
        shutil.rmtree(kidnapped)

    def test_post_quarantine_empty_racer_survives_without_conditional_rmdir(self):
        real_mkdir = GENERATE._mkdir_temp_at
        created = []
        def mkdir_injected(parent, *, prefix):
            if created:
                raise OSError("injected before second temporary")
            name, fd = real_mkdir(parent, prefix=prefix)
            created.append((parent.path, name))
            return name, fd
        racer = []
        def hook(parent, quarantine, temp_fd):
            del temp_fd
            # The original name is free only after the atomic quarantine move.
            original = quarantine.split(".abandoned-", 1)[0]
            os.mkdir(original, mode=0o700, dir_fd=parent.fd)
            metadata = os.stat(original, dir_fd=parent.fd, follow_symlinks=False)
            racer.append((parent.path / original, (metadata.st_dev, metadata.st_ino)))
        with mock.patch.object(GENERATE, "_mkdir_temp_at", side_effect=mkdir_injected), \
             mock.patch.object(GENERATE, "_cleanup_quarantine_hook", side_effect=hook):
            with self.assertRaisesRegex(OSError, "injected"):
                self.seal("post-quarantine-race")
        racer_path, identity = racer[0]
        metadata = racer_path.stat()
        self.assertEqual((metadata.st_dev, metadata.st_ino), identity)
        self.assertEqual(list(racer_path.iterdir()), [])
        quarantines = list(self.root.glob(created[0][1] + ".abandoned-*"))
        self.assertEqual(len(quarantines), 1)
        self.assertTrue(quarantines[0].is_dir())
        racer_path.rmdir()
        shutil.rmtree(quarantines[0])

    def test_only_rfc_json_whitespace_is_accepted_around_source_array(self):
        GENERATE.EXPECTED_SOURCE_COUNT = len(self.rows)
        for forbidden in ("\v", "\f", "\u00a0", "\u2003"):
            encoded = (forbidden + json.dumps(self.rows)).encode("utf-8")
            self.data_path = self.write_source_bytes(encoded)
            with self.subTest(forbidden=repr(forbidden)):
                with self.assertRaisesRegex(GENERATE.SealError, "top-level JSON array"):
                    GENERATE.load_and_validate_source(self.data_path)

    def test_separately_rooted_constraint_and_key_validation(self):
        with self.assertRaisesRegex(GENERATE.SealError, "separately rooted"):
            GENERATE.seal_suite(
                data_path=self.data_path, readme_path=self.readme,
                gitattributes_path=self.gitattributes, requirements_lock=HERE / "requirements.lock",
                out_public=self.root / "same", out_gold=self.root / "same", key_path=self.key,
            )
        short = self.private_file(self.root / "short.key", b"short")
        with self.assertRaisesRegex(GENERATE.SealError, "exactly 32"):
            self.seal("short-key", key=short)


if __name__ == "__main__":
    unittest.main()
