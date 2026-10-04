import unittest

import pandas as pd

from src.preprocessing import (
    encode_popularity,
    parse_best_time,
    parse_ticket_price,
    preprocess_dataset,
    score_time,
)
from src.saw import calculate_ranking, normalize_matrix
from src.utils import DEFAULT_WEIGHTS


class PreprocessingTest(unittest.TestCase):
    def test_parse_ticket_price(self):
        self.assertEqual(parse_ticket_price("Gratis"), 0)
        self.assertEqual(parse_ticket_price("Rp10.000"), 10000)
        self.assertEqual(parse_ticket_price("Rp10.000 - Rp30.000"), 20000)
        self.assertEqual(parse_ticket_price("Rp50.000 - Rp100.000"), 75000)

    def test_encode_popularity(self):
        self.assertEqual(encode_popularity("tersembunyi"), 1)
        self.assertEqual(encode_popularity("populer"), 3)
        self.assertEqual(encode_popularity("sangat_populer"), 5)

    def test_parse_time_and_scoring(self):
        self.assertIn(7, parse_best_time("Mei - September"))
        self.assertEqual(parse_best_time("Oktober-April"), {10, 11, 12, 1, 2, 3, 4})
        self.assertEqual(score_time("Mei - September", "Juli"), 5)
        self.assertEqual(score_time("Mei - September", "April"), 3)
        self.assertEqual(score_time("Mei - September", "Desember"), 1)

    def test_duplicate_removal(self):
        df = pd.DataFrame(
            [
                [1, "A", "Bali", "Alam", "Desc", "Mei - September", "Gratis", "populer"],
                [1, "A", "Bali", "Alam", "Desc", "Mei - September", "Gratis", "populer"],
            ],
            columns=["id", "destination", "province", "type", "description", "best_time", "ticket_range", "popularity"],
        )
        self.assertEqual(len(preprocess_dataset(df)), 1)


class SawTest(unittest.TestCase):
    def test_normalization_and_ranking(self):
        df = pd.DataFrame(
            [
                [1, "A", "Bali", "Alam", "Desc", "Mei - September", "Gratis", "sangat_populer"],
                [2, "B", "Bali", "Budaya", "Desc", "Januari - Maret", "Rp100.000", "populer"],
                [3, "C", "Bali", "Alam", "Desc", "Juli", "Rp50.000", "tersembunyi"],
            ],
            columns=["id", "destination", "province", "type", "description", "best_time", "ticket_range", "popularity"],
        )
        processed = preprocess_dataset(df)
        result = calculate_ranking(processed, "Alam", "Juli", DEFAULT_WEIGHTS, "Semua")
        ranking = result["ranking"]
        self.assertTrue(ranking["saw_score"].between(0, 1).all())
        self.assertTrue(ranking["saw_score"].is_monotonic_decreasing)
        self.assertEqual(ranking.iloc[0]["destination"], "A")

    def test_same_price_cost_normalization_is_one(self):
        matrix = pd.DataFrame(
            {
                "ticket_price": [10000, 10000],
                "popularity_score": [1, 5],
                "type_score": [5, 5],
                "time_score": [3, 5],
            }
        )
        normalized = normalize_matrix(matrix)
        self.assertTrue((normalized["norm_price"] == 1).all())


if __name__ == "__main__":
    unittest.main()
