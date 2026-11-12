"""
Unit tests for competition filtering and audit taxonomy.
Verifies senior IPL and T20I inclusion and regional tournament exclusions.
"""

import unittest
import pandas as pd

from src import loaders, competition_filter, config


class TestCompetitions(unittest.TestCase):

    def setUp(self):
        self.comps = loaders.load_competitions()
        self.matches = loaders.load_matches()

    def test_competition_classification_counts(self):
        comp_audit = competition_filter.classify_competitions(self.comps, self.matches)

        ipl_comps = comp_audit[comp_audit["category"] == "IPL"]
        t20i_comps = comp_audit[comp_audit["category"] == "T20I"]
        excluded_comps = comp_audit[comp_audit["category"] == "EXCLUDED"]

        # 5 IPL seasons: 2022 to 2026
        self.assertEqual(len(ipl_comps), 5)
        self.assertEqual(set(ipl_comps["comp_id"]), {1358, 1715, 2193, 2725, 3298})
        self.assertEqual(ipl_comps["match_count"].sum(), 371)

        # 134 T20I series
        self.assertEqual(len(t20i_comps), 134)
        self.assertEqual(t20i_comps["match_count"].sum(), 482)

        # 2 Excluded regional competitions
        self.assertEqual(len(excluded_comps), 2)
        self.assertEqual(set(excluded_comps["comp_id"]), {2670, 3289})
        self.assertEqual(excluded_comps["match_count"].sum(), 30)

    def test_filter_dataset_by_competition(self):
        bbb = loaders.load_ball_by_ball()
        retained_comps, retained_matches, retained_bbb, excluded_bbb = (
            competition_filter.filter_dataset_by_competition(self.comps, self.matches, bbb)
        )

        self.assertEqual(len(retained_comps), 139)
        self.assertEqual(len(retained_matches), 853)
        self.assertEqual(len(retained_bbb), 194014)
        self.assertEqual(len(excluded_bbb), 6985)
        self.assertEqual(len(retained_bbb) + len(excluded_bbb), len(bbb))

        # Ensure no excluded comp_id appears in retained matches
        self.assertNotIn(2670, set(retained_matches["comp_id"]))
        self.assertNotIn(3289, set(retained_matches["comp_id"]))


if __name__ == "__main__":
    unittest.main()
