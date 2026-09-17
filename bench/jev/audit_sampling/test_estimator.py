import itertools
import math
import unittest

from .estimator import estimate


class EstimatorTests(unittest.TestCase):
    def test_all_subsets_unbiased_and_variance(self):
        p = [0.2, 0.7, 0.4, 0.9, 0.1]
        y = [True, False, True, True, False]
        predictions = [{"id": str(i), "p": p[i]} for i in range(len(p))]
        for n in (2, 3):
            values = []
            for indexes in itertools.combinations(range(len(p)), n):
                audits = [{"id": str(i), "label": y[i]} for i in indexes]
                values.append(estimate(predictions, audits)["corrected_total"])
            residual = [float(y[i]) - p[i] for i in range(len(p))]
            mean = sum(residual) / len(residual)
            S2 = sum((x - mean) ** 2 for x in residual) / (len(residual) - 1)
            expected = sum(y)
            self.assertAlmostEqual(sum(values) / len(values), expected)
            observed_var = sum((x - expected) ** 2 for x in values) / len(values)
            theoretical = len(p) ** 2 * (1 - n / len(p)) * S2 / n
            self.assertAlmostEqual(observed_var, theoretical)

    def test_special_cases_and_comparisons(self):
        labels = [True, False, True, False]
        pred = [{"id": str(i), "p": 0.5} for i in range(4)]
        audits = [{"id": str(i), "label": labels[i]} for i in (0, 1)]
        result = estimate(pred, audits)
        self.assertAlmostEqual(result["corrected_total"], result["uniform_total"])
        self.assertAlmostEqual(result["estimated_standard_error"], math.sqrt(2.0))
        inverse = estimate([{"id": str(i), "p": 1 - labels[i]} for i in range(4)], audits)
        self.assertGreater(inverse["estimated_standard_error"], result["estimated_standard_error"])
        perfect = estimate([{"id": str(i), "p": float(labels[i])} for i in range(4)], audits)
        self.assertEqual(perfect["corrected_total"], sum(labels))
        self.assertEqual(perfect["estimated_standard_error"], 0.0)
        census = estimate(pred, [{"id": str(i), "label": labels[i]} for i in range(4)])
        self.assertEqual(census["corrected_total"], sum(labels))
        self.assertEqual(census["estimated_standard_error"], 0.0)
        self.assertTrue(census["census"])
        singleton = estimate(pred, [{"id": "0", "label": True}])
        self.assertIsNone(singleton["estimated_standard_error"])
        self.assertIsNone(singleton["normal_reference_95"])

    def test_duplicate_content_ids_are_multiplicities_and_permutations_harmless(self):
        pred = [{"id": "a", "p": 0.2}, {"id": "b", "p": 0.2}, {"id": "c", "p": 0.8}]
        a = [{"id": "a", "label": True}, {"id": "c", "label": False}]
        b = [{"id": "c", "label": False}, {"id": "a", "label": True}]
        self.assertEqual(estimate(pred, a), estimate(pred, b))

    def test_malformed_inputs_rejected(self):
        good_p = [{"id": "a", "p": 0.5}]
        good_a = [{"id": "a", "label": True}]
        cases = [
            ([{"id": "a", "p": True}], good_a),
            ([{"id": "a", "p": math.nan}], good_a),
            ([{"id": "", "p": 0.5}], good_a),
            ([{"id": "a", "p": 0.5}, {"id": "a", "p": 0.2}], good_a),
            (good_p, [{"id": "a", "label": 1}]),
            (good_p, [{"id": "a", "label": True, "x": 1}]),
            (good_p, [{"id": "b", "label": True}]),
            (good_p, [{"id": "a", "label": True}, {"id": "a", "label": False}]),
        ]
        for predictions, audited in cases:
            with self.assertRaises(ValueError):
                estimate(predictions, audited)


if __name__ == "__main__":
    unittest.main()
