"""
Unit tests for pressure feature extraction.
Verifies RRR calculations, zero remaining balls, first-innings collapse indices, and contest reachability.
"""

import unittest
import pandas as pd
import numpy as np

from src import pressure_features


class TestPressureFeatures(unittest.TestCase):

    def setUp(self):
        self.sample_df = pd.DataFrame({
            "match_id": [1, 1, 1, 2, 2],
            "innings": [1, 1, 1, 2, 2],
            "overid": [3, 6, 18, 15, 20],
            "over_ball_num": [1, 1, 1, 1, 6],
            "innings_ball_num": [13, 31, 103, 85, 120],
            "pre_delivery_runs": [15, 42, 140, 110, 150],
            "pre_delivery_wickets": [1, 3, 6, 4, 8],
            "pre_delivery_legal_balls": [12, 30, 102, 84, 119],
            "pre_delivery_balls_remaining": [108, 90, 18, 36, 1],
            "pre_delivery_runs_required": [np.nan, np.nan, np.nan, 45.0, 4.0],
            "pre_delivery_required_run_rate": [np.nan, np.nan, np.nan, 7.5, 24.0],
            "pre_delivery_current_run_rate": [7.5, 8.4, 8.24, 7.86, 7.56],
            "runs": [1, 0, 4, 1, 2],
            "is_wicket": [False, False, False, False, False]
        })

    def test_feature_extraction_dimensions_and_types(self):
        feat = pressure_features.extract_pressure_features(self.sample_df)

        expected_cols = [
            "wickets_in_hand", "rrr_diff", "req_runs_per_ball", "req_rate_per_wicket",
            "is_contested_chase", "wicket_pace_ratio", "collapse_severity",
            "scoring_rate_deficit", "is_death_overs", "tail_exposed"
        ]
        for col in expected_cols:
            self.assertIn(col, feat.columns)

        # Innings 1 rows have NaN for chase features
        inn1 = feat[feat["innings"] == 1]
        self.assertTrue(inn1["rrr_diff"].isna().all())

        # Innings 2 rows have non-null chase features
        inn2 = feat[feat["innings"] == 2]
        self.assertTrue(inn2["rrr_diff"].notna().all())
        self.assertTrue(inn2["is_contested_chase"].all())

    def test_first_innings_collapse_indices(self):
        feat = pressure_features.extract_pressure_features(self.sample_df)
        inn1 = feat[feat["innings"] == 1]

        # Over 6 with 3 wickets down (expected is 1.45)
        row_ov6 = inn1.iloc[1]
        self.assertGreater(row_ov6["wicket_pace_ratio"], 1.5)
        self.assertGreater(row_ov6["collapse_severity"], 0.1)

        # Over 18 with 6 wickets down: death overs and tail exposed
        row_ov18 = inn1.iloc[2]
        self.assertTrue(row_ov18["is_death_overs"])
        self.assertTrue(row_ov18["tail_exposed"])

    def test_zero_remaining_balls_handling(self):
        edge_df = pd.DataFrame({
            "match_id": [3],
            "innings": [2],
            "overid": [20],
            "over_ball_num": [6],
            "innings_ball_num": [120],
            "pre_delivery_runs": [150],
            "pre_delivery_wickets": [7],
            "pre_delivery_legal_balls": [120],
            "pre_delivery_balls_remaining": [0],
            "pre_delivery_runs_required": [2.0],
            "pre_delivery_required_run_rate": [36.0],
            "pre_delivery_current_run_rate": [7.5],
            "runs": [1],
            "is_wicket": [False]
        })
        feat = pressure_features.extract_pressure_features(edge_df)
        self.assertEqual(feat.iloc[0]["wickets_in_hand"], 3.0)
        self.assertTrue(feat.iloc[0]["is_death_overs"])


if __name__ == "__main__":
    unittest.main()
