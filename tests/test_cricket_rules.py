"""
Unit tests for cricket scoring engine and rules.
Tests legal deliveries, balls faced, bowler runs, and wicket attributions.
"""

import unittest
import pandas as pd
import numpy as np

from src import cricket_rules, config


class TestCricketRules(unittest.TestCase):

    def test_legal_delivery_accounting(self):
        extras = pd.Series([np.nan, "wide", "Overstep", "other", "legbyes", "byes", "Penalty"])
        legal = cricket_rules.is_legal_delivery_series(extras)
        expected = pd.Series([True, False, False, False, True, True, False])
        pd.testing.assert_series_equal(legal, expected, check_names=False)

    def test_ball_faced_accounting(self):
        extras = pd.Series([np.nan, "wide", "Overstep", "other", "legbyes", "byes", "Penalty"])
        faced = cricket_rules.is_ball_faced_series(extras)
        # Batters face legal balls, no-balls, byes, leg-byes; they do NOT face wides or penalties
        expected = pd.Series([True, False, True, True, True, True, False])
        pd.testing.assert_series_equal(faced, expected, check_names=False)

    def test_bowler_charged_runs(self):
        runs = pd.Series([4, 0, 1, 0, 0, 0, 0])
        extras_type = pd.Series([np.nan, "wide", "Overstep", "other", "legbyes", "byes", "Penalty"])
        extras1 = pd.Series([0, 1, 1, 1, 4, 1, 5])
        
        # Bowler is charged for:
        # ball 0: 4 (runs) + 0 = 4
        # ball 1: 0 + 1 (wide) = 1
        # ball 2: 1 + 1 (no-ball) = 2
        # ball 3: 0 + 1 (other nb) = 1
        # ball 4: 0 + 0 (legbyes NOT charged) = 0
        # ball 5: 0 + 0 (byes NOT charged) = 0
        # ball 6: 0 + 0 (penalty NOT charged) = 0
        bowler_runs = cricket_rules.get_bowler_charged_runs_series(runs, extras_type, extras1)
        expected = pd.Series([4, 1, 2, 1, 0, 0, 0])
        pd.testing.assert_series_equal(bowler_runs, expected, check_names=False)

    def test_bowler_credit_wickets(self):
        is_wkt = pd.Series([True, True, True, True, True, True, True, True, False])
        d_type = pd.Series([
            "Caught", "Bowled", "LBW", "Stump", "Hit Wicket",
            "RunOut", "Retire Out", "Obstructing the field", "Caught"
        ])
        bowler_wkts = cricket_rules.is_bowler_wicket_series(is_wkt, d_type)
        expected = pd.Series([True, True, True, True, True, False, False, False, False])
        pd.testing.assert_series_equal(bowler_wkts, expected, check_names=False)

    def test_non_bowler_dismissals(self):
        is_wkt = pd.Series([True, True, True, True, True, True])
        d_type = pd.Series(["RunOut", "Retire Out", "Obstructing the field", "Obstracting the field", "Caught", "Bowled"])
        non_bowler = cricket_rules.is_non_bowler_dismissal_series(is_wkt, d_type)
        expected = pd.Series([True, True, True, True, False, False])
        pd.testing.assert_series_equal(non_bowler, expected, check_names=False)

    def test_innings_stages(self):
        overs = pd.Series([1, 6, 7, 15, 16, 20])
        stages = cricket_rules.get_innings_stage_series(overs)
        expected = pd.Series([
            config.STAGE_POWERPLAY, config.STAGE_POWERPLAY,
            config.STAGE_MIDDLE, config.STAGE_MIDDLE,
            config.STAGE_DEATH, config.STAGE_DEATH
        ])
        pd.testing.assert_series_equal(stages, expected, check_names=False)


if __name__ == "__main__":
    unittest.main()
