"""
Integration tests for the complete Phase 1 Data Engineering pipeline.
Verifies Parquet files, Super Over isolation, zero leakage, and abandoned match handling.
"""

import unittest
import pandas as pd
import pyarrow.parquet as pq

from src import config


class TestPreprocessingIntegration(unittest.TestCase):

    def test_output_files_exist_and_non_empty(self):
        self.assertTrue(config.PROCESSED_DELIVERIES_PARQUET.exists())
        self.assertTrue(config.PROCESSED_MATCHES_PARQUET.exists())
        self.assertTrue(config.SUPER_OVER_PARQUET.exists())
        self.assertTrue(config.EXCLUDED_DELIVERIES_CSV.exists())
        self.assertTrue(config.COMPETITION_AUDIT_CSV.exists())
        self.assertTrue(config.MATCH_STATE_VALIDATION_CSV.exists())
        self.assertTrue(config.PREPROCESSING_REPORT_MD.exists())

    def test_parquet_row_counts_and_schemas(self):
        deliv = pd.read_parquet(config.PROCESSED_DELIVERIES_PARQUET)
        matches = pd.read_parquet(config.PROCESSED_MATCHES_PARQUET)
        super_overs = pd.read_parquet(config.SUPER_OVER_PARQUET)
        excluded = pd.read_csv(config.EXCLUDED_DELIVERIES_CSV)

        # Exact row count checks
        self.assertEqual(len(deliv), 193988)
        self.assertEqual(len(matches), 853)
        self.assertEqual(len(super_overs), 26)
        self.assertEqual(len(excluded), 6985)

        # Super Overs strictly excluded from primary deliveries
        self.assertNotIn(3, deliv["innings"].unique())
        self.assertNotIn(4, deliv["innings"].unique())
        self.assertTrue(set(super_overs["innings"].unique()).issubset({3, 4}))

    def test_validation_report_100_percent_pass(self):
        val_df = pd.read_csv(config.MATCH_STATE_VALIDATION_CSV)
        self.assertEqual(len(val_df), 1652)
        # 100% of innings must pass all mathematical reconciliation checks
        self.assertTrue((val_df["status"] == "PASS").all())
        self.assertTrue(val_df["runs_reconciled"].all())
        self.assertTrue(val_df["wickets_reconciled"].all())
        self.assertTrue(val_df["legal_balls_reconciled"].all())
        self.assertTrue(val_df["runs_monotonic"].all())
        self.assertTrue(val_df["wickets_monotonic"].all())
        self.assertTrue(val_df["legal_balls_monotonic"].all())
        self.assertTrue(val_df["dismissals_partition_valid"].all())

    def test_abandoned_matches_handling(self):
        matches = pd.read_parquet(config.PROCESSED_MATCHES_PARQUET)
        deliv = pd.read_parquet(config.PROCESSED_DELIVERIES_PARQUET)

        abandoned = matches[matches["result"] == "Match Abandoned"]
        self.assertEqual(len(abandoned), 19)

        # Of the 19 abandoned matches:
        # Exactly 16 were abandoned before play commenced (0 deliveries in ball_by_ball)
        # Exactly 3 were abandoned mid-match due to weather (partial 1st innings bowled)
        deliv_match_ids = set(deliv["match_id"])
        abandoned_without_play = abandoned[~abandoned["match_id"].isin(deliv_match_ids)]
        abandoned_with_play = abandoned[abandoned["match_id"].isin(deliv_match_ids)]

        self.assertEqual(len(abandoned_without_play), 16)
        self.assertEqual(len(abandoned_with_play), 3)

    def test_zero_future_leakage_and_boundary_conditions(self):
        deliv = pd.read_parquet(config.PROCESSED_DELIVERIES_PARQUET)

        # Check Ball 1 of all innings: pre-delivery stats must be strictly 0
        ball1_rows = deliv.groupby(["match_id", "innings"]).first()
        self.assertTrue((ball1_rows["pre_delivery_runs"] == 0).all())
        self.assertTrue((ball1_rows["pre_delivery_wickets"] == 0).all())
        self.assertTrue((ball1_rows["pre_delivery_legal_balls"] == 0).all())

        # Check required columns exist
        required_cols = [
            "match_id", "innings", "overid", "over_ball_num", "innings_ball_num",
            "striker_id", "non_striker_id", "bowler_id",
            "is_legal_delivery", "is_ball_faced", "delivery_total_runs", "bowler_charged_runs",
            "is_bowler_wicket", "is_non_bowler_dismissal", "innings_stage",
            "pre_delivery_runs", "pre_delivery_wickets", "pre_delivery_legal_balls",
            "innings_scheduled_legal_balls", "pre_delivery_balls_remaining",
            "target", "target_status", "pre_delivery_runs_required",
            "pre_delivery_required_run_rate", "pre_delivery_current_run_rate",
            "match_state_uncertainty"
        ]
        for col in required_cols:
            self.assertIn(col, deliv.columns)


if __name__ == "__main__":
    unittest.main()
