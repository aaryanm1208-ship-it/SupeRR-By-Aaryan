"""
Unit and integration tests for bowling performance intelligence (Phase 4).
"""

import unittest
import numpy as np
import pandas as pd
from src.bowling_analysis import (
    compute_bowler_aggregates,
    compute_bowler_match_consistency,
    apply_bowler_empirical_bayes_shrinkage,
    build_bowler_performance_dataset
)


class TestBowlingAnalysis(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        n = 120
        self.df = pd.DataFrame({
            "match_id": np.random.choice([201, 202, 203, 204], size=n),
            "bowler_id": np.random.choice([10, 20], size=n),
            "bowler_canonical_name": ["Bowler Alpha" if x == 10 else "Bowler Beta" for x in np.random.choice([10, 20], size=n)],
            "bowler_charged_runs": np.random.choice([0, 1, 2, 4, 6], size=n, p=[0.45, 0.25, 0.1, 0.15, 0.05]),
            "is_bowler_wicket": np.random.choice([0, 1], size=n, p=[0.92, 0.08]),
            "is_legal_delivery": np.ones(n, dtype=bool),
            "bowler_pressure_tier": np.random.choice(["NORMAL", "HIGH", "EXTREME"], size=n, p=[0.5, 0.3, 0.2]),
            "match_format": ["T20"] * n,
            "innings_stage": np.random.choice(["Powerplay", "Middle", "Death"], size=n)
        })

    def test_compute_bowler_aggregates(self):
        merged, tier_grouped = compute_bowler_aggregates(self.df)
        self.assertGreater(len(merged), 0)
        self.assertIn("pressure_econ", merged.columns)
        self.assertIn("normal_econ", merged.columns)
        self.assertIn("econ_delta", merged.columns)

    def test_compute_bowler_match_consistency(self):
        consistency = compute_bowler_match_consistency(self.df)
        self.assertIn("clutch_spell_pct", consistency.columns)
        self.assertIn("match_econ_std", consistency.columns)

    def test_apply_bowler_empirical_bayes_shrinkage(self):
        test_df = pd.DataFrame({
            "pressure_econ": [4.0, 12.0, 8.0],
            "pressure_legal_balls": [12, 120, 600]
        })
        shrunk, mu_0, k = apply_bowler_empirical_bayes_shrinkage(test_df, "pressure_econ", "pressure_legal_balls")
        # Extreme small sample economy (4.0 on 12 balls) must be shrunk towards mu_0
        self.assertLess(abs(shrunk.iloc[0] - mu_0), abs(test_df["pressure_econ"].iloc[0] - mu_0))


if __name__ == "__main__":
    unittest.main()
