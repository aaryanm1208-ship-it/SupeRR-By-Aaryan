"""
Unit and integration tests for batting performance intelligence (Phase 3).
"""

import unittest
import numpy as np
import pandas as pd
from src.batting_analysis import (
    compute_batter_aggregates,
    compute_batter_match_consistency,
    apply_empirical_bayes_shrinkage,
    build_batter_performance_dataset
)


class TestBattingAnalysis(unittest.TestCase):

    def setUp(self):
        # Create minimal synthetic deliveries
        np.random.seed(42)
        n = 100
        self.df = pd.DataFrame({
            "match_id": np.random.choice([101, 102, 103, 104], size=n),
            "striker_id": np.random.choice([1, 2], size=n),
            "striker_canonical_name": ["Player One" if x == 1 else "Player Two" for x in np.random.choice([1, 2], size=n)],
            "runs": np.random.choice([0, 1, 2, 4, 6], size=n, p=[0.4, 0.3, 0.1, 0.15, 0.05]),
            "is_four": np.zeros(n),
            "is_six": np.zeros(n),
            "is_wicket": np.random.choice([0, 1], size=n, p=[0.95, 0.05]),
            "dismissed_player_id": [1 if np.random.rand() > 0.5 else 2 for _ in range(n)],
            "extras1_runs": np.zeros(n),
            "is_ball_faced": np.ones(n, dtype=bool),
            "is_legal_delivery": np.ones(n, dtype=bool),
            "batter_pressure_tier": np.random.choice(["NORMAL", "HIGH", "EXTREME"], size=n, p=[0.6, 0.25, 0.15]),
            "bowler_pressure_tier": np.random.choice(["NORMAL", "HIGH", "EXTREME"], size=n, p=[0.6, 0.25, 0.15]),
            "match_format": ["T20"] * n,
            "innings_stage": np.random.choice(["Middle", "Death"], size=n)
        })

    def test_compute_batter_aggregates(self):
        merged, tier_grouped = compute_batter_aggregates(self.df)
        self.assertGreater(len(merged), 0)
        self.assertIn("pressure_sr", merged.columns)
        self.assertIn("normal_sr", merged.columns)
        self.assertIn("sr_delta", merged.columns)

    def test_compute_batter_match_consistency(self):
        consistency = compute_batter_match_consistency(self.df)
        self.assertIn("positive_contribution_pct", consistency.columns)
        self.assertIn("match_sr_std", consistency.columns)

    def test_apply_empirical_bayes_shrinkage(self):
        test_df = pd.DataFrame({
            "pressure_sr": [200.0, 100.0, 150.0],
            "pressure_balls": [10, 100, 500]
        })
        shrunk, mu_0, k = apply_empirical_bayes_shrinkage(test_df, "pressure_sr", "pressure_balls")
        # Shrunk SR for small sample (10 balls) should be pulled strongly toward mu_0
        self.assertAlmostEqual(mu_0, float(np.average(test_df["pressure_sr"], weights=test_df["pressure_balls"])), places=2)
        self.assertLess(abs(shrunk.iloc[0] - mu_0), abs(test_df["pressure_sr"].iloc[0] - mu_0))


if __name__ == "__main__":
    unittest.main()
