"""
Unit tests for match state reconstruction and causal pre-delivery logic.
Verifies zero data leakage, correct DLS revised lengths, and target mathematics.
"""

import unittest
import pandas as pd
import numpy as np

from src import match_state, config


class TestMatchState(unittest.TestCase):

    def setUp(self):
        # Synthetic match with 2 innings to test complete state reconstruction
        self.deliveries = pd.DataFrame({
            "match_id": [1, 1, 1, 1, 1, 1, 1, 1],
            "innings": [1, 1, 1, 1, 2, 2, 2, 2],
            "overid": [1, 1, 1, 2, 1, 1, 1, 2],
            "over_ball_num": [1, 2, 3, 1, 1, 2, 3, 1],
            "innings_ball_num": [1, 2, 3, 4, 1, 2, 3, 4],
            "runs": [4, 0, 1, 6, 0, 4, 2, 6],
            "extras_type": [np.nan, "wide", np.nan, np.nan, "Overstep", np.nan, np.nan, np.nan],
            "extras1_runs": [0, 1, 0, 0, 1, 0, 0, 0],
            "extras_2_runs": [0, 0, 0, 0, 0, 0, 0, 0],
            "is_wicket": [False, False, True, False, False, False, True, False],
            "dismissal_type": [np.nan, np.nan, "Bowled", np.nan, np.nan, np.nan, "Caught", np.nan],
            "dismissed_player_id": [pd.NA, pd.NA, 101, pd.NA, pd.NA, pd.NA, 201, pd.NA],
            "striker_id": [101, 101, 101, 102, 201, 201, 201, 202],
            "non_striker_id": [102, 102, 102, 103, 202, 202, 202, 203],
            "bowler_id": [301, 301, 301, 302, 401, 401, 401, 402]
        })

        self.matches = pd.DataFrame({
            "match_id": [1],
            "first_inn_revised_overs": [np.nan],
            "second_inn_revised_overs": [np.nan],
            "revised_target": [np.nan]
        })

    def test_pre_delivery_zero_leakage_and_monotonicity(self):
        reconstructed = match_state.reconstruct_match_state(self.deliveries, self.matches)

        # 1. Innings 1 Ball 1 checks
        inn1 = reconstructed[reconstructed["innings"] == 1]
        ball1 = inn1.iloc[0]
        self.assertEqual(ball1["pre_delivery_runs"], 0)
        self.assertEqual(ball1["pre_delivery_wickets"], 0)
        self.assertEqual(ball1["pre_delivery_legal_balls"], 0)

        # 2. Innings 1 Ball 2: follows a 4 on ball 1 (legal)
        ball2 = inn1.iloc[1]
        self.assertEqual(ball2["pre_delivery_runs"], 4)
        self.assertEqual(ball2["pre_delivery_wickets"], 0)
        self.assertEqual(ball2["pre_delivery_legal_balls"], 1)

        # 3. Innings 1 Ball 3: follows a wide (1 extra, illegal) on ball 2
        ball3 = inn1.iloc[2]
        self.assertEqual(ball3["pre_delivery_runs"], 5)  # 4 + 1
        self.assertEqual(ball3["pre_delivery_wickets"], 0)
        self.assertEqual(ball3["pre_delivery_legal_balls"], 1)  # unchanged because wide is illegal

        # 4. Innings 1 Ball 4: follows a wicket + 1 run on ball 3
        ball4 = inn1.iloc[3]
        self.assertEqual(ball4["pre_delivery_runs"], 6)  # 5 + 1
        self.assertEqual(ball4["pre_delivery_wickets"], 1)
        self.assertEqual(ball4["pre_delivery_legal_balls"], 2)

        # 5. Monotonicity across innings
        self.assertTrue((inn1["pre_delivery_runs"].diff().dropna() >= 0).all())
        self.assertTrue((inn1["pre_delivery_wickets"].diff().dropna() >= 0).all())
        self.assertTrue((inn1["pre_delivery_legal_balls"].diff().dropna() >= 0).all())

    def test_target_and_required_run_rate(self):
        reconstructed = match_state.reconstruct_match_state(self.deliveries, self.matches)

        # Innings 1 total was: 4 + 1 (wide) + 1 + 6 = 12 runs
        # Target for Innings 2 should be: 12 + 1 = 13 runs
        inn2 = reconstructed[reconstructed["innings"] == 2]

        self.assertTrue((inn2["target"] == 13.0).all())
        self.assertTrue((inn2["target_status"] == "VALID_STANDARD_TARGET").all())

        # Ball 1 of chase: pre-delivery score is 0, so runs required = 13
        ball1 = inn2.iloc[0]
        self.assertEqual(ball1["pre_delivery_runs_required"], 13.0)
        self.assertEqual(ball1["pre_delivery_balls_remaining"], 120)
        # RRR = (13 / 120) * 6.0 = 0.65
        self.assertAlmostEqual(ball1["pre_delivery_required_run_rate"], 0.65, places=4)

    def test_revised_dls_target_and_reduced_overs(self):
        matches_rev = pd.DataFrame({
            "match_id": [1],
            "first_inn_revised_overs": [60.0],   # 10 overs
            "second_inn_revised_overs": [48.0],  # 8 overs
            "revised_target": [50.0]
        })
        reconstructed = match_state.reconstruct_match_state(self.deliveries, matches_rev)

        inn1 = reconstructed[reconstructed["innings"] == 1]
        self.assertTrue((inn1["innings_scheduled_legal_balls"] == 60).all())

        inn2 = reconstructed[reconstructed["innings"] == 2]
        self.assertTrue((inn2["innings_scheduled_legal_balls"] == 48).all())
        self.assertTrue((inn2["target"] == 50.0).all())
        self.assertTrue((inn2["target_status"] == "VALID_DLS_REVISED").all())

        # Ball 1 of chase: balls remaining should be 48
        ball1 = inn2.iloc[0]
        self.assertEqual(ball1["pre_delivery_balls_remaining"], 48)
        self.assertEqual(ball1["pre_delivery_runs_required"], 50.0)
        # RRR = (50 / 48) * 6.0 = 6.25
        self.assertAlmostEqual(ball1["pre_delivery_required_run_rate"], 6.25, places=4)


if __name__ == "__main__":
    unittest.main()
