"""
Unit tests for Pressure Intelligence Engine (Models A, B, C, and Role-Specific Pressure).
Verifies mathematical bounds, tier mappings, and role asymmetry.
"""

import unittest
import pandas as pd
import numpy as np

from src import pressure_engine, pressure_features


class TestPressureEngine(unittest.TestCase):

    def test_score_to_tier_boundaries(self):
        scores = pd.Series([0.0, 34.9, 35.0, 54.9, 55.0, 74.9, 75.0, 100.0])
        tiers = pressure_engine.score_to_tier(scores)
        expected = pd.Series([
            "NORMAL", "NORMAL", "ELEVATED", "ELEVATED", "HIGH", "HIGH", "EXTREME", "EXTREME"
        ])
        pd.testing.assert_series_equal(tiers, expected, check_names=False, check_dtype=False)

    def test_model_a_chasing_monotonicity_and_bounds(self):
        # As RRR increases from 6 to 16 with same balls/wickets, score must strictly increase
        df = pd.DataFrame({
            "match_id": [1, 1, 1],
            "innings": [2, 2, 2],
            "overid": [16, 16, 16],
            "over_ball_num": [1, 1, 1],
            "innings_ball_num": [91, 91, 91],
            "pre_delivery_runs": [120, 120, 120],
            "pre_delivery_wickets": [4, 4, 4],
            "pre_delivery_legal_balls": [90, 90, 90],
            "pre_delivery_balls_remaining": [30, 30, 30],
            "pre_delivery_runs_required": [30.0, 50.0, 80.0],
            "pre_delivery_required_run_rate": [6.0, 10.0, 16.0],
            "pre_delivery_current_run_rate": [8.0, 8.0, 8.0],
            "runs": [1, 1, 1],
            "is_wicket": [False, False, False]
        })
        feat = pressure_features.extract_pressure_features(df)
        res = pressure_engine.compute_model_a_chasing(feat)
        scores = res["pressure_score_model_a"].values

        # Must be strictly increasing with RRR
        self.assertLess(scores[0], scores[1])
        self.assertLess(scores[1], scores[2])
        # Must be bounded in [0, 100]
        self.assertTrue((scores >= 0.0).all() and (scores <= 100.0).all())

    def test_model_b_first_innings_collapse_response(self):
        # Compare 0 wickets vs 4 wickets in over 6 (end of powerplay)
        df = pd.DataFrame({
            "match_id": [1, 1],
            "innings": [1, 1],
            "overid": [6, 6],
            "over_ball_num": [1, 1],
            "innings_ball_num": [31, 31],
            "pre_delivery_runs": [45, 45],
            "pre_delivery_wickets": [0, 4],
            "pre_delivery_legal_balls": [30, 30],
            "pre_delivery_balls_remaining": [90, 90],
            "pre_delivery_runs_required": [np.nan, np.nan],
            "pre_delivery_required_run_rate": [np.nan, np.nan],
            "pre_delivery_current_run_rate": [9.0, 9.0],
            "runs": [1, 1],
            "is_wicket": [False, False]
        })
        feat = pressure_features.extract_pressure_features(df)
        res = pressure_engine.compute_model_b_first_innings(feat)
        scores = res["pressure_score_model_b"].values

        # 4 wickets down in powerplay must produce significantly higher pressure than 0 down
        self.assertGreater(scores[1] - scores[0], 25.0)

    def test_role_pressure_asymmetry(self):
        # Scenario: Chasing team needs 18 off 12 balls with 7 wickets in hand (RRR = 9.0)
        # Batters are comfortably on track; Defending bowlers are in EXTREME danger of boundary loss
        df = pd.DataFrame({
            "match_id": [1],
            "innings": [2],
            "overid": [19],
            "over_ball_num": [1],
            "innings_ball_num": [109],
            "pre_delivery_runs": [160],
            "pre_delivery_wickets": [3],
            "pre_delivery_legal_balls": [108],
            "pre_delivery_balls_remaining": [12],
            "pre_delivery_runs_required": [18.0],
            "pre_delivery_required_run_rate": [9.0],
            "pre_delivery_current_run_rate": [8.88],
            "runs": [1],
            "is_wicket": [False]
        })
        feat = pressure_features.extract_pressure_features(df)
        m_a = pressure_engine.compute_model_a_chasing(feat)
        m_b = pressure_engine.compute_model_b_first_innings(m_a)
        res = pressure_engine.compute_model_c_contextual(m_b)

        p_bat = res["batter_pressure_score"].iloc[0]
        p_bowl = res["bowler_pressure_score"].iloc[0]

        # Bowler pressure must be significantly higher than batter pressure in this close finish!
        self.assertGreater(p_bowl, p_bat)


if __name__ == "__main__":
    unittest.main()
