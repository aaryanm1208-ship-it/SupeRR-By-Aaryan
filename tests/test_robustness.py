"""
Unit and integration tests for robustness and sensitivity testing (Phase 6).
"""

import unittest
import os
import pandas as pd


class TestRobustness(unittest.TestCase):

    def test_robustness_artifacts_exist(self):
        reports_dir = "outputs/reports"
        self.assertTrue(os.path.exists(os.path.join(reports_dir, "robustness_report.md")))
        self.assertTrue(os.path.exists(os.path.join(reports_dir, "ranking_stability.csv")))
        self.assertTrue(os.path.exists(os.path.join(reports_dir, "alternative_model_rankings.csv")))
        self.assertTrue(os.path.exists(os.path.join(reports_dir, "bootstrap_results.csv")))
        self.assertTrue(os.path.exists(os.path.join(reports_dir, "competition_rankings.csv")))
        self.assertTrue(os.path.exists(os.path.join(reports_dir, "season_rankings.csv")))

    def test_bootstrap_results_integrity(self):
        boot_df = pd.read_csv("outputs/reports/bootstrap_results.csv")
        self.assertEqual(len(boot_df), 20)  # 10 batters + 10 bowlers
        self.assertTrue((boot_df["prob_top_10"] >= 0.0).all())
        self.assertTrue((boot_df["prob_top_10"] <= 1.0).all())
        self.assertTrue((boot_df["rank_ci_lower"] <= boot_df["rank_ci_upper"]).all())


if __name__ == "__main__":
    unittest.main()
