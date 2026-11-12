"""
Comprehensive API endpoint verification for SupeRR Selector platform.
Directly tests the route functions without depending on async event loops.
"""

import unittest
import os
from src.api import (
    get_summary,
    get_batters,
    get_bowlers,
    get_player_detail,
    get_explanations,
    get_research_data,
    get_figures_catalog,
    download_file
)

class TestSupeRRSelectorAPI(unittest.TestCase):

    def test_summary_endpoint(self):
        data = get_summary()
        self.assertIn("dataset_scope", data)
        self.assertEqual(data["dataset_scope"]["total_matches"], 853)
        self.assertEqual(data["dataset_scope"]["total_deliveries"], 193988)
        self.assertEqual(data["dataset_scope"]["eligible_batters"], 86)
        self.assertEqual(data["dataset_scope"]["eligible_bowlers"], 154)
        self.assertIn("top_performers", data)
        self.assertEqual(data["top_performers"]["batter"]["name"], "Namboori Tilak Varma")
        self.assertEqual(data["top_performers"]["bowler"]["name"], "Mujeeb Ur Rahman")
        self.assertIn("pressure_par", data)
        self.assertIn("key_findings", data)

    def test_batters_endpoint_default(self):
        data = get_batters()
        self.assertEqual(data["total"], 86)
        self.assertGreater(len(data["batters"]), 0)
        top_batter = data["batters"][0]
        self.assertEqual(top_batter["rank"], 1)
        self.assertEqual(top_batter["player_name"], "Namboori Tilak Varma")
        self.assertAlmostEqual(top_batter["pressure_sr"], 183.0, places=1)

    def test_batters_search_and_filter(self):
        # Search Tilak
        data = get_batters(search="Tilak")
        self.assertEqual(len(data["batters"]), 1)
        self.assertEqual(data["batters"][0]["player_name"], "Namboori Tilak Varma")

        # Search Rinku
        data = get_batters(search="Rinku")
        self.assertEqual(len(data["batters"]), 1)
        self.assertEqual(data["batters"][0]["player_name"], "Rinku Singh")

        # Filter by min_balls
        data = get_batters(min_balls=150)
        for b in data["batters"]:
            self.assertGreaterEqual(b["pressure_balls"], 150)

    def test_bowlers_endpoint_default(self):
        data = get_bowlers()
        self.assertEqual(data["total"], 154)
        top_bowler = data["bowlers"][0]
        self.assertEqual(top_bowler["rank"], 1)
        self.assertEqual(top_bowler["player_name"], "Mujeeb Ur Rahman")

    def test_bowlers_search_and_filter(self):
        # Search Bumrah
        data = get_bowlers(search="Bumrah")
        self.assertEqual(len(data["bowlers"]), 1)
        self.assertEqual(data["bowlers"][0]["player_name"], "Jasprit Bumrah")

        # Filter by death specialists
        data = get_bowlers(role="death")
        for b in data["bowlers"]:
            self.assertGreater(b["death_pressure_pct"], 40.0)

    def test_player_detail_endpoint(self):
        # Test batter (Tilak Varma, id 7897)
        data = get_player_detail("BATTER", 7897)
        self.assertEqual(data["player_name"], "Namboori Tilak Varma")
        self.assertIn("core_metrics", data)
        self.assertIn("phase_split", data)
        self.assertIn("competition_split", data)
        self.assertIn("justification", data)
        self.assertIsNotNone(data["justification"])

        # Test bowler (Mujeeb Ur Rahman, id 6450)
        data = get_player_detail("BOWLER", 6450)
        self.assertEqual(data["player_name"], "Mujeeb Ur Rahman")
        self.assertIn("core_metrics", data)
        self.assertIn("phase_split", data)
        self.assertIn("competition_split", data)

    def test_explanations_endpoint(self):
        data = get_explanations()
        self.assertIn("explanations", data)
        self.assertEqual(len(data["explanations"]), 20)

    def test_research_endpoint(self):
        data = get_research_data()
        self.assertIn("model_correlations", data)
        self.assertIn("bootstrap_results", data)
        self.assertIn("batters_model_c_vs_a", data["model_correlations"])

    def test_figures_endpoint(self):
        data = get_figures_catalog()
        self.assertEqual(len(data), 12)
        for fig in data:
            self.assertIn("id", fig)
            self.assertIn("title", fig)
            self.assertIn("filename", fig)
            self.assertTrue(os.path.exists(os.path.join("outputs", "figures", fig["filename"])))

    def test_download_endpoint(self):
        res = download_file("methodology_report.pdf")
        self.assertTrue(os.path.exists(res.path))

        res_csv = download_file("batter_rankings_final.csv")
        self.assertTrue(os.path.exists(res_csv.path))

if __name__ == "__main__":
    unittest.main()
