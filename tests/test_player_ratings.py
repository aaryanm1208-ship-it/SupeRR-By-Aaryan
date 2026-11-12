"""
Unit and integration tests for composite player ratings and rankings (Phase 5).
"""

import unittest
import numpy as np
import pandas as pd
from src.player_ratings import (
    min_max_normalize,
    compute_batter_composite_ratings,
    compute_bowler_composite_ratings,
    generate_player_explanations
)


class TestPlayerRatings(unittest.TestCase):

    def test_min_max_normalize(self):
        s = pd.Series([10.0, 20.0, 30.0])
        norm = min_max_normalize(s)
        self.assertAlmostEqual(norm.iloc[0], 0.0)
        self.assertAlmostEqual(norm.iloc[1], 50.0)
        self.assertAlmostEqual(norm.iloc[2], 100.0)

        # Inverted normalization
        inv = min_max_normalize(s, invert=True)
        self.assertAlmostEqual(inv.iloc[0], 100.0)
        self.assertAlmostEqual(inv.iloc[2], 0.0)

    def test_composite_rating_bounds(self):
        # Load final rankings to ensure values fall strictly between 0 and 100
        df_b = pd.read_csv("outputs/rankings/batter_rankings_final.csv")
        df_bw = pd.read_csv("outputs/rankings/bowler_rankings_final.csv")

        self.assertTrue((df_b["composite_rating"] >= 0).all())
        self.assertTrue((df_b["composite_rating"] <= 100).all())
        self.assertTrue((df_bw["composite_rating"] >= 0).all())
        self.assertTrue((df_bw["composite_rating"] <= 100).all())

        # Verify Top 10 ranks are 1 through 10
        self.assertEqual(list(df_b.head(10)["rank"]), list(range(1, 11)))
        self.assertEqual(list(df_bw.head(10)["rank"]), list(range(1, 11)))


if __name__ == "__main__":
    unittest.main()
