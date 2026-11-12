"""
Pressure feature engineering module for SupeRR Selector Season 2.
Extracts strictly pre-delivery contextual indicators for first-innings and chasing states.
Ensures zero data leakage and full mathematical reproducibility.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Par scoring rates and expected wickets schedule by over (empirical T20 baseline)
# Expected cumulative wickets at the start of overid (1-indexed, 1 to 20)
EXPECTED_WICKETS_BY_OVER = {
    1: 0.08, 2: 0.30, 3: 0.60, 4: 0.90, 5: 1.18, 6: 1.45,
    7: 1.69, 8: 1.92, 9: 2.18, 10: 2.42, 11: 2.68, 12: 2.96,
    13: 3.23, 14: 3.53, 15: 3.85, 16: 4.15, 17: 4.45, 18: 4.83,
    19: 5.29, 20: 5.80
}

# Expected cumulative par score at the start of overid
EXPECTED_PAR_SCORE_BY_OVER = {
    1: 0.0, 2: 7.2, 3: 15.0, 4: 23.5, 5: 32.5, 6: 42.0,
    7: 51.0, 8: 60.0, 9: 69.0, 10: 78.0, 11: 87.0, 12: 96.0,
    13: 105.0, 14: 114.5, 15: 124.0, 16: 134.5, 17: 145.5, 18: 157.0,
    19: 169.0, 20: 182.0
}


def extract_pressure_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes pre-delivery pressure indicators across both innings.
    All inputs must be pre-delivery states.
    """
    logger.info("Extracting pre-delivery pressure feature representations...")
    feat = df.copy()

    # 1. Base Pre-Delivery Variables
    w_lost = feat["pre_delivery_wickets"].astype(float)
    w_in_hand = np.maximum(0.0, 10.0 - w_lost)
    balls_rem = feat["pre_delivery_balls_remaining"].astype(float)
    runs_before = feat["pre_delivery_runs"].astype(float)
    crr = feat["pre_delivery_current_run_rate"].astype(float)
    overid = feat["overid"].clip(1, 20)

    feat["wickets_in_hand"] = w_in_hand

    # 2. Second-Innings Chasing Features
    is_inn2 = feat["innings"] == 2
    rrr = feat["pre_delivery_required_run_rate"].astype(float)
    runs_req = feat["pre_delivery_runs_required"].astype(float)

    feat["rrr_diff"] = np.where(is_inn2, rrr - crr, np.nan)
    feat["req_runs_per_ball"] = np.where(is_inn2 & (balls_rem > 0), runs_req / balls_rem, np.nan)
    feat["req_rate_per_wicket"] = np.where(is_inn2 & (w_in_hand > 0), rrr / w_in_hand, np.nan)

    # Contest reachability: A chase is contested if the outcome is actively in doubt.
    # Blowouts: e.g. needing > 36 rpo with < 18 balls left, or target achieved (runs_req == 0)
    is_chase_achieved = is_inn2 & (runs_req == 0)
    is_chase_lost = is_inn2 & (
        ((balls_rem <= 18) & (rrr > 30.0)) |
        ((balls_rem <= 12) & (rrr > 24.0)) |
        ((w_in_hand <= 1) & (runs_req > 36.0) & (balls_rem <= 24))
    )
    feat["is_contested_chase"] = np.where(
        is_inn2,
        (~is_chase_achieved) & (~is_chase_lost),
        False
    )

    # 3. First-Innings Features
    is_inn1 = feat["innings"] == 1
    exp_wkts = overid.map(EXPECTED_WICKETS_BY_OVER).astype(float)
    exp_par_score = overid.map(EXPECTED_PAR_SCORE_BY_OVER).astype(float)

    # Wicket pace ratio: actual wickets lost relative to historical average at this over
    feat["wicket_pace_ratio"] = np.where(
        is_inn1,
        w_lost / np.maximum(0.5, exp_wkts),
        np.nan
    )

    # Collapse severity: non-linear trigger when top-order is lost early
    # E.g. in Powerplay (overs 1-6), 3 wickets down is acute collapse
    feat["collapse_severity"] = np.where(
        is_inn1,
        np.maximum(0.0, (w_lost - exp_wkts) / np.maximum(1.0, 10.0 - exp_wkts)),
        np.nan
    )

    # Scoring rate strain: how far below par T20 run rate (8.4 rpo) the team is scoring
    feat["scoring_rate_deficit"] = np.where(
        is_inn1,
        np.maximum(0.0, 8.4 - crr),
        np.nan
    )

    # Death overs acceleration urgency (last 5 overs of scheduled innings or <= 30 balls remaining)
    if "innings_scheduled_legal_balls" in feat.columns:
        sched_balls = feat["innings_scheduled_legal_balls"].astype(float).clip(lower=30.0)
    else:
        sched_balls = pd.Series(120.0, index=feat.index)
    sched_overs = sched_balls / 6.0
    feat["is_death_overs"] = (feat["overid"] > (sched_overs - 5.0)) | (balls_rem <= 30.0)
    feat["tail_exposed"] = w_lost >= 6

    logger.info("Pressure features extracted successfully.")
    return feat
