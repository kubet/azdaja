import json
import unittest
from pathlib import Path

import reference


HERE = Path(__file__).resolve().parent
CONTEXT = HERE.parent / "oolong" / "context-131072.txt"


class ReferenceMechanicsTests(unittest.TestCase):
    def test_row645_fits_exactly_one_compact_shard(self):
        built = reference.build(CONTEXT)
        self.assertEqual(built["selected_records"], 227)
        self.assertEqual(built["unique_items"], 226)
        self.assertEqual(built["workers"], 6)
        self.assertEqual(len(built["shards"]), 1)
        start, items, prompt = built["shards"][0]
        self.assertEqual(start, 0)
        self.assertEqual(len(items), 226)
        self.assertLessEqual(len(items), reference.MAX_ITEMS)
        self.assertLessEqual(len(prompt), reference.MAX_CHARS)
        self.assertIn('{"labels":"', prompt)
        self.assertNotIn("explanation", prompt.lower())

    def test_stable_deduplication_preserves_multiplicity(self):
        unique, multiplicities = reference.stable_unique(["a", "b", "a", "c", "b"])
        self.assertEqual(unique, ["a", "b", "c"])
        self.assertEqual(multiplicities, [2, 2, 1])
        self.assertEqual(reference.weighted_ham("HSH", multiplicities), 3)

    def test_compact_response_accepts_only_exact_positional_json(self):
        self.assertEqual(reference.parse_labels('{"labels":"HSH"}', 3), "HSH")
        for raw, expected in [
            ('{"labels":"HS"}', 3),
            ('{"labels":"HSX"}', 3),
            ('{"labels":"HSH","note":"x"}', 3),
            ('["H","S","H"]', 3),
            ('Answer: HSH', 3),
            (json.dumps({"azdaja_error": "provider_call_failed_retry_item"}), 3),
        ]:
            with self.assertRaises(reference.ReferenceError):
                reference.parse_labels(raw, expected)

    def test_sharding_obeys_both_item_and_character_caps(self):
        items = ["x" * 1000 for _ in range(300)]
        shards = reference.pack(items)
        self.assertGreater(len(shards), 1)
        self.assertEqual(sum(len(items) for _, items, _ in shards), 300)
        for _, shard, prompt in shards:
            self.assertLessEqual(len(shard), reference.MAX_ITEMS)
            self.assertLessEqual(len(prompt), reference.MAX_CHARS)

    def test_single_oversized_item_fails_closed(self):
        with self.assertRaises(reference.ReferenceError):
            reference.pack(["x" * reference.MAX_CHARS])

    def test_weighted_count_rejects_length_drift(self):
        with self.assertRaises(reference.ReferenceError):
            reference.weighted_ham("HH", [1])


if __name__ == "__main__":
    unittest.main()
