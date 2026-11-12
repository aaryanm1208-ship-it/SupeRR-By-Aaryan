"""
Unit and integration tests for pressure sensitivity, multi-model comparison, and output validation.
"""

import unittest
import pandas as pd

from src import config, pressure_sensitivity


class TestPressureSensitivity(unittest.TestCase):

    def setUp(self):
        self.deliv_c = pd.read_parquet(config.PROCESSED_DIR / "pressure_deliveries_model_c.parquet")

    def test_threshold_sensitivity_monotonicity(self):
        sens_df = pressure_sensitivity.evaluate_threshold_sensitivity(self.deliv_c)
        c_sens = sens_df[sens_df["model"] == "Model C (Unified)"]

        # EXTREME percentage must decrease as thresholds become more conservative
        extr_agg = c_sens[c_sens["tier"] == "EXTREME"]
        percentages = extr_agg["percentage"].values
        # Order: -20%, -10%, Baseline, +10%, +20%
        for i in range(len(percentages) - 1):
            self.assertGreaterEqual(percentages[i], percentages[i+1])

    def test_multi_model_agreement_and_correlations(self):
        comp_df, _ = pressure_sensitivity.evaluate_model_comparison(self.deliv_c)

        # Model A vs Model C in Innings 2 must have near-perfect correlation (>= 0.99)
        row_ac = comp_df[comp_df["comparison"].str.contains("Model A vs. Model C")].iloc[0]
        self.assertGreaterEqual(row_ac["spearman_correlation"], 0.99)

        # Model B vs Model C in Innings 1 must have near-perfect correlation (>= 0.99)
        row_bc = comp_df[comp_df["comparison"].str.contains("Model B vs. Model C")].iloc[0]
        self.assertGreaterEqual(row_bc["spearman_correlation"], 0.99)

    def test_parquet_deliverables_integrity(self):
        p_feat = config.PROCESSED_DIR / "pressure_features.parquet"
        p_a = config.PROCESSED_DIR / "pressure_deliveries_model_a.parquet"
        p_b = config.PROCESSED_DIR / "pressure_deliveries_model_b.parquet"
        p_c = config.PROCESSED_DIR / "pressure_deliveries_model_c.parquet"
        p_comp = config.PROCESSED_DIR / "pressure_model_comparison.parquet"

        self.assertTrue(p_feat.exists() and p_feat.stat().st_size > 0)
        self.assertTrue(p_a.exists() and p_a.stat().st_size > 0)
        self.assertTrue(p_b.exists() and p_b.stat().st_size > 0)
        self.assertTrue(p_c.exists() and p_c.stat().st_size > 0)
        self.assertTrue(p_comp.exists() and p_comp.stat().st_size > 0)

        df_a = pd.read_parquet(p_a)
        df_b = pd.read_parquet(p_b)
        df_c = pd.read_parquet(p_c)

        self.assertEqual(len(df_a), 91934)
        self.assertEqual(len(df_b), 102054)
        self.assertEqual(len(df_c), 193988)


if __name__ == "__main__":
    unittest.main()
