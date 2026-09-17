import json
from pathlib import Path
import tempfile
import unittest

from bench.jev.angle_lab.native import canonical, sha
from bench.jev.second_reader.row651 import prepare as p


class Row651PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = p.occurrences()

    def test_full_source_binding_and_occurrence_identity(self):
        self.assertEqual(len(self.rows), 17469)
        self.assertEqual(self.rows[0]["id"], "r0005")
        self.assertEqual(self.rows[-1]["id"], "r17473")
        self.assertEqual(self.rows[0]["source_sha256"], p.SOURCE_SHA256)
        self.assertEqual(self.rows[-1]["source_sha256"], p.SOURCE_SHA256)
        source = p.SOURCE.read_bytes()
        for row in (self.rows[0], self.rows[1], self.rows[-1]):
            self.assertEqual(source[row["byte_start"] : row["byte_end"]].decode(), row["text"])

    def test_duplicate_occurrences_are_retained(self):
        # The frozen row happens to have no byte-identical full-line repeats.
        # Exercise the important contract with two source occurrences carrying
        # the same text: identity is the physical ID/span, never text-based
        # deduplication.
        first, second = self.rows[:2]
        duplicate_rows = [dict(first, id="r0005"), dict(second, id="r0006", text=first["text"])]
        pack = p.make_pack(duplicate_rows)
        self.assertEqual(list(pack["state"]["records"].values()), [first["text"], first["text"]])
        self.assertEqual(list(pack["state"]["records"]), ["r0005", "r0006"])
        self.assertNotEqual(duplicate_rows[0]["byte_start"], duplicate_rows[1]["byte_start"])

    def test_policies_are_exactly_bounded_and_cover_all_occurrences(self):
        expected = [row["id"] for row in self.rows]
        for policy, count in (("old64", 273), ("candidate255", 112)):
            packs = p.split(self.rows, policy)
            self.assertEqual(len(packs), count)
            flattened = [row["id"] for pack in packs for row in pack]
            self.assertEqual(flattened, expected)
            for pack_rows in packs:
                pack = p.make_pack(pack_rows)
                result = p.validate_pack(pack, policy)
                self.assertEqual(result["questions"], len(pack_rows))
                self.assertLessEqual(result["state_bytes"], p.POLICIES[policy]["max_state_bytes"])
                request_limit = p.POLICIES[policy]["max_request_bytes"]
                if request_limit is not None:
                    self.assertLessEqual(result["request_bytes"], request_limit)

    def test_pack_boundaries_are_atomic_and_contiguous(self):
        packs = p.split(self.rows, "candidate255")
        for left, right in zip(packs, packs[1:]):
            self.assertEqual(left[-1]["occurrence"] + 1, right[0]["occurrence"])
            self.assertEqual(left[-1]["byte_end"], right[0]["byte_start"])
        self.assertEqual(sum(len(pack) for pack in packs), len(self.rows))

    def test_packs_have_no_gold_or_label_fields_and_keep_instruction(self):
        pack = p.make_pack(self.rows[:3])
        raw = canonical(pack).decode()
        for forbidden in ("answer", "expected", "gold", "rationale", "official_ham"):
            self.assertNotIn(forbidden, raw)
        self.assertNotIn("official_question", raw)
        for qid, question in pack["questions"].items():
            self.assertEqual(question, p.question(qid))
            self.assertNotIn("criteria", question)

    def test_source_reconstruction_and_record_hashes(self):
        source = p.SOURCE.read_bytes()
        rebuilt = []
        for row in self.rows:
            raw = source[row["byte_start"] : row["byte_end"]]
            self.assertEqual(raw.decode(), row["text"])
            self.assertEqual(sha(raw), row["record_sha256"])
            rebuilt.append(raw)
        # The four non-record preamble lines are intentionally outside the
        # panel; every retained record is reconstructed exactly and in source
        # order from its independent byte span.
        self.assertEqual(sha(b"".join(rebuilt)), sha(b"".join(row["text"].encode() for row in self.rows)))

    def test_prepare_writes_source_only_artifacts_and_stats(self):
        with tempfile.TemporaryDirectory() as temp:
            result = p.prepare("candidate255", Path(temp))
            self.assertEqual(result["pack_count"], 112)
            self.assertEqual(result["occurrence_count"], 17469)
            self.assertEqual(result["official_question"], p.OFFICIAL_QUESTION)
            self.assertEqual(result["source_sha256"], p.SOURCE_SHA256)
            self.assertEqual(len(list(Path(temp).glob("pack-*.json"))), 112)
            manifest = json.loads((Path(temp) / "MANIFEST.json").read_text())
            self.assertEqual(sum(item["occurrences"] for item in manifest["packs"]), 17469)
            self.assertLessEqual(min(item["occurrences"] for item in manifest["packs"]), 51)
            self.assertEqual(manifest["deduplication"], "none; every source occurrence is retained")
            self.assertLessEqual(max(item["request_bytes"] for item in manifest["packs"]), 90000)
            expected = {row["id"] for row in self.rows}
            observed = set()
            cursor = 0
            for item in manifest["packs"]:
                pack = json.loads((Path(temp) / item["file"]).read_text())
                ids = set(pack["state"]["records"])
                expected_slice = {row["id"] for row in self.rows[cursor : cursor + item["occurrences"]]}
                self.assertEqual(ids, expected_slice)
                observed.update(ids)
                cursor += item["occurrences"]
            self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
