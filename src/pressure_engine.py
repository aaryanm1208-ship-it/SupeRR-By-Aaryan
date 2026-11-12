"""
Pressure Intelligence Engine for SupeRR Selector Season 2.
Implements Model A (Chasing), Model B (First-Innings), and Model C (Unified Contextual Framework).
Calculates continuous pressure scores [0, 100] and discrete tiers: NORMAL, ELEVATED, HIGH, EXTREME.
"""

import logging
import pandas as pd
import numpy as np

from src import config, pressure_features

logger = logging.getLogger(__name__)

# Standard Category Boundaries
TIER_NORMAL = "NORMAL"
TIER_ELEVATED = "ELEVATED"
TIER_HIGH = "HIGH"
TIER_EXTREME = "EXTREME"


def score_to_tier(score_series: pd.Series, t_elevated=35.0, t_high=55.0, t_extreme=75.0) -> pd.Series:
    """Discretizes continuous pressure score into 4 standard intensity tiers."""
    return pd.Series(
        np.select(
            [score_series >= t_extreme, score_series >= t_high, score_series >= t_elevated],
            [TIER_EXTREME, TIER_HIGH, TIER_ELEVATED],
            default=TIER_NORMAL
        ),
        index=score_series.index,
        dtype="string"
    )


def compute_model_a_chasing(df: pd.DataFrame) -> pd.DataFrame:
    """
    MODEL A: Second-Innings Chasing Pressure Engine.
    Evaluates required run rate, wickets in hand, runs required, and balls remaining.
    """
    logger.info("Computing Model A (Chasing Pressure)...")
    res = df.copy()

    is_inn2 = res["innings"] == 2
    rrr = res["pre_delivery_required_run_rate"].fillna(0.0).astype(float)
    crr = res["pre_delivery_current_run_rate"].fillna(0.0).astype(float)
    w_lost = res["pre_delivery_wickets"].astype(float)
    balls_rem = res["pre_delivery_balls_remaining"].astype(float)
    runs_req = res["pre_delivery_runs_required"].fillna(0.0).astype(float)
    is_contested = res["is_contested_chase"]

    # 1. Rate Demand Component: 0 at RRR <= 8.0, 100 at RRR >= 14.0
    c_rate = np.clip((rrr - 8.0) / (14.0 - 8.0), 0.0, 1.0) * 100.0

    # 2. Resource Depletion Component (wickets + balls consumed relative to scheduled innings length)
    if "innings_scheduled_legal_balls" in res.columns:
        sched_balls = res["innings_scheduled_legal_balls"].astype(float).clip(lower=30.0)
    else:
        sched_balls = pd.Series(120.0, index=res.index)
    c_res = (0.5 * (w_lost / 9.0) + 0.5 * (1.0 - (balls_rem / sched_balls))) * 100.0

    # 3. Rate Strain Component (RRR - CRR)
    c_diff = np.clip((rrr - crr) / 5.0, 0.0, 1.0) * 100.0

    # 4. Late Chase Criticality Component (balls_rem <= 36 and close match)
    urgency_balls = np.clip((36.0 - balls_rem) / 36.0, 0.0, 1.0)
    urgency_rate = np.clip(rrr / 12.0, 0.0, 1.0)
    c_urgency = urgency_balls * urgency_rate * 100.0

    # Raw Composite Score
    cpi = 0.40 * c_rate + 0.25 * c_res + 0.20 * c_diff + 0.15 * c_urgency

    # If chase is already achieved or game is dead blowout, scale down appropriately
    cpi = np.where(runs_req == 0, 0.0, cpi)
    cpi = np.where((~is_contested) & (balls_rem <= 18) & (rrr > 30.0), np.clip(cpi * 0.5, 0.0, 60.0), cpi)

    # Assign strictly to Innings 2
    res["pressure_score_model_a"] = np.where(is_inn2, np.clip(cpi, 0.0, 100.0), np.nan)
    res["pressure_tier_model_a"] = np.where(
        is_inn2,
        score_to_tier(pd.Series(res["pressure_score_model_a"])),
        pd.NA
    )
    return res


def compute_model_b_first_innings(df: pd.DataFrame) -> pd.DataFrame:
    """
    MODEL B: First-Innings Resource and Scoring Pressure Engine.
    Evaluates collapse severity, wicket pace, scoring rate strain, and death overs urgency.
    """
    logger.info("Computing Model B (First-Innings Pressure)...")
    res = df.copy()

    is_inn1 = res["innings"] == 1
    w_lost = res["pre_delivery_wickets"].astype(float)
    crr = res["pre_delivery_current_run_rate"].fillna(0.0).astype(float)
    overid = res["overid"].clip(1, 20)
    collapse_sev = res["collapse_severity"].fillna(0.0).astype(float)
    balls_consumed = res["pre_delivery_legal_balls"].astype(float)

    # 1. Collapse Component: based on early loss of wickets
    f_collapse = np.clip(collapse_sev * 2.0, 0.0, 1.0) * 100.0

    # 2. Resource Depletion: wickets lost relative to 8
    f_res = np.clip(w_lost / 8.0, 0.0, 1.0) * 100.0

    # 3. Scoring Deficit: lagging behind T20 par run rate (8.5 rpo) after initial over
    f_deficit = np.where(
        balls_consumed >= 18,
        np.clip((8.5 - crr) / 4.0, 0.0, 1.0) * 100.0,
        0.0
    )

    # 4. Death Overs Urgency (Dynamic: final 5 overs of scheduled innings or <= 30 balls remaining)
    if "innings_scheduled_legal_balls" in res.columns:
        sched_balls = res["innings_scheduled_legal_balls"].astype(float).clip(lower=30.0)
    else:
        sched_balls = pd.Series(120.0, index=res.index)
    sched_overs = sched_balls / 6.0
    death_threshold = np.maximum(1.0, sched_overs - 5.0)
    is_death = (overid > death_threshold) | (res["pre_delivery_balls_remaining"] <= 30.0)
    death_span = np.maximum(1.0, sched_overs - death_threshold)
    death_factor = np.where(
        is_death,
        np.clip((overid - death_threshold) / death_span, 0.2, 1.0) * (50.0 + 5.0 * np.minimum(w_lost, 8.0)),
        0.0
    )
    f_death = np.clip(death_factor, 0.0, 100.0)

    # Composite Score
    fpi = 0.35 * f_collapse + 0.25 * f_res + 0.20 * f_deficit + 0.20 * f_death

    # Assign strictly to Innings 1
    res["pressure_score_model_b"] = np.where(is_inn1, np.clip(fpi, 0.0, 100.0), np.nan)
    res["pressure_tier_model_b"] = np.where(
        is_inn1,
        score_to_tier(pd.Series(res["pressure_score_model_b"])),
        pd.NA
    )
    return res


def compute_model_c_contextual(df: pd.DataFrame) -> pd.DataFrame:
    """
    MODEL C: Unified Contextual Match-Leverage & Role-Specific Pressure Framework.
    Computes:
    - Shared Match Leverage (SML): Overall tension / criticality of the delivery.
    - Batter Pressure (P_bat): Situational strain on the batting side.
    - Bowler Pressure (P_bowl): Situational demand and error-penalty on the bowling side.
    """
    logger.info("Computing Model C (Unified Contextual Pressure)...")
    res = df.copy()

    is_inn1 = res["innings"] == 1
    is_inn2 = res["innings"] == 2

    # Model A & Model B baseline scores
    cpi = res["pressure_score_model_a"].fillna(0.0)
    fpi = res["pressure_score_model_b"].fillna(0.0)

    # 1. Shared Match Leverage (SML)
    sml = np.where(is_inn2, cpi, fpi)

    # 2. Role-Specific: Batter Pressure (P_bat)
    # Batters face high pressure in steep chases (inn 2) or collapses/death overs (inn 1)
    p_bat = sml.copy()

    # 3. Role-Specific: Bowler Pressure (P_bowl)
    # In Innings 2: Bowlers face maximum pressure in CLOSE FINISHES!
    # (e.g. chasing team needs 20 off 18 with 6 wickets in hand - batter is comfortable, bowler is on edge)
    rrr = res["pre_delivery_required_run_rate"].fillna(0.0).astype(float)
    balls_rem = res["pre_delivery_balls_remaining"].astype(float)
    runs_req = res["pre_delivery_runs_required"].fillna(0.0).astype(float)
    w_lost = res["pre_delivery_wickets"].astype(float)
    overid = res["overid"].clip(1, 20)
    crr = res["pre_delivery_current_run_rate"].fillna(0.0).astype(float)

    # Bowler chase pressure: high when game is in balance (RRR between 7 and 13) and balls remaining are low
    # Margin of error is razor thin
    balance_factor = np.clip(1.0 - (np.abs(rrr - 9.5) / 6.0), 0.0, 1.0)
    death_weight = np.clip((120.0 - balls_rem) / 120.0, 0.0, 1.0)
    wickets_in_hand = np.maximum(1.0, 10.0 - w_lost)
    batting_threat = np.clip(wickets_in_hand / 7.0, 0.2, 1.0)

    bowl_pressure_inn2 = (
        0.35 * (balance_factor * 100.0) +
        0.35 * (death_weight * 100.0) +
        0.20 * (batting_threat * 100.0) +
        0.10 * np.clip(cpi, 0.0, 100.0)
    )
    # If match is already won or dead blowout, bowler pressure drops
    bowl_pressure_inn2 = np.where(runs_req == 0, 0.0, bowl_pressure_inn2)
    bowl_pressure_inn2 = np.where((balls_rem <= 18) & (rrr > 30.0), 10.0, bowl_pressure_inn2)

    # In Innings 1: Bowlers face pressure when batters are scoring freely (CRR >= 9.5) or in death overs (overs 16-20)
    bowl_assault_inn1 = np.clip((crr - 7.5) / 4.0, 0.0, 1.0) * 100.0
    bowl_death_inn1 = np.where(overid >= 16, ((overid - 15.0) / 5.0) * 80.0, 0.0)
    bowl_pressure_inn1 = 0.50 * bowl_death_inn1 + 0.35 * bowl_assault_inn1 + 0.15 * (100.0 - fpi)

    p_bowl = np.where(is_inn2, bowl_pressure_inn2, bowl_pressure_inn1)

    # Attach Model C fields
    res["pressure_score_model_c"] = np.clip(sml, 0.0, 100.0)
    res["pressure_tier_model_c"] = score_to_tier(pd.Series(res["pressure_score_model_c"]))

    res["batter_pressure_score"] = np.clip(p_bat, 0.0, 100.0)
    res["batter_pressure_tier"] = score_to_tier(pd.Series(res["batter_pressure_score"]))

    res["bowler_pressure_score"] = np.clip(p_bowl, 0.0, 100.0)
    res["bowler_pressure_tier"] = score_to_tier(pd.Series(res["bowler_pressure_score"]))

    logger.info("Model C contextual scoring completed.")
    return res


def run_all_pressure_models(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """Executes feature extraction and all pressure models (A, B, C) in sequence."""
    logger.info("--- Starting Full Pressure Modeling Engine ---")
    feat_df = pressure_features.extract_pressure_features(deliveries_df)
    m_a = compute_model_a_chasing(feat_df)
    m_b = compute_model_b_first_innings(m_a)
    m_c = compute_model_c_contextual(m_b)
    logger.info("--- All Pressure Models Executed Successfully ---")
    return m_c
