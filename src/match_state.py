"""
Match state reconstruction module for SupeRR Selector Season 2.
Reconstructs the precise match state immediately BEFORE every delivery.
Ensures zero data leakage and strict chronological invariance.
"""

import logging
import pandas as pd
import numpy as np

from src import config, cricket_rules

logger = logging.getLogger(__name__)


def reconstruct_match_state(
    deliveries_df: pd.DataFrame,
    matches_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Reconstructs delivery-level match state immediately BEFORE each delivery.
    Operates strictly on standard innings (1 and 2).
    """
    logger.info("Starting vectorized match-state reconstruction across deliveries...")

    # Ensure deliveries are sorted strictly chronologically
    df = deliveries_df.sort_values(
        by=["match_id", "innings", "innings_ball_num", "overid", "over_ball_num"]
    ).copy().reset_index(drop=True)

    # 1. Delivery-level scoring attributes
    df["is_legal_delivery"] = cricket_rules.is_legal_delivery_series(df["extras_type"])
    df["is_ball_faced"] = cricket_rules.is_ball_faced_series(df["extras_type"])
    df["total_extras"] = df["extras1_runs"] + df["extras_2_runs"]
    df["delivery_total_runs"] = df["runs"] + df["total_extras"]
    df["bowler_charged_runs"] = cricket_rules.get_bowler_charged_runs_series(
        df["runs"], df["extras_type"], df["extras1_runs"]
    )
    df["is_bowler_wicket"] = cricket_rules.is_bowler_wicket_series(
        df["is_wicket"], df["dismissal_type"]
    )
    df["is_non_bowler_dismissal"] = cricket_rules.is_non_bowler_dismissal_series(
        df["is_wicket"], df["dismissal_type"]
    )
    df["innings_stage"] = cricket_rules.get_innings_stage_series(df["overid"])

    # 2. Vectorized Pre-Delivery Cumulative Calculations: cumsum() - current_val
    grp = df.groupby(["match_id", "innings"], sort=False)
    
    # Pre-delivery runs
    cum_runs = grp["delivery_total_runs"].cumsum()
    df["pre_delivery_runs"] = cum_runs - df["delivery_total_runs"]

    # Pre-delivery wickets
    cum_wickets = grp["is_wicket"].cumsum()
    df["pre_delivery_wickets"] = cum_wickets - df["is_wicket"].astype(int)

    # Pre-delivery legal balls
    cum_legal = grp["is_legal_delivery"].cumsum()
    df["pre_delivery_legal_balls"] = cum_legal - df["is_legal_delivery"].astype(int)

    # 3. Attach Match Metadata (Revised Overs, Revised Target)
    meta_cols = ["match_id", "first_inn_revised_overs", "second_inn_revised_overs", "revised_target"]
    df = df.merge(matches_df[meta_cols], on="match_id", how="left")

    # 4. Compute 1st Innings Totals
    inn1_totals = (
        df[df["innings"] == 1]
        .groupby("match_id")["delivery_total_runs"]
        .sum()
        .rename("inn1_total_runs")
    )
    df = df.merge(inn1_totals, on="match_id", how="left")

    # 5. Scheduled Legal Balls per Innings
    is_inn1 = df["innings"] == 1
    is_inn2 = df["innings"] == 2

    sched_inn1 = np.where(
        df["first_inn_revised_overs"].notna() & (df["first_inn_revised_overs"] > 0),
        df["first_inn_revised_overs"].fillna(config.STANDARD_T20_LEGAL_BALLS).astype(int),
        config.STANDARD_T20_LEGAL_BALLS
    )
    sched_inn2 = np.where(
        df["second_inn_revised_overs"].notna() & (df["second_inn_revised_overs"] > 0),
        df["second_inn_revised_overs"].fillna(config.STANDARD_T20_LEGAL_BALLS).astype(int),
        config.STANDARD_T20_LEGAL_BALLS
    )
    df["innings_scheduled_legal_balls"] = np.where(is_inn1, sched_inn1, sched_inn2)

    # 6. Pre-Delivery Balls Remaining
    df["pre_delivery_balls_remaining"] = np.maximum(
        0, df["innings_scheduled_legal_balls"] - df["pre_delivery_legal_balls"]
    )

    # 7. Target Score Determination
    has_rev_target = is_inn2 & df["revised_target"].notna() & (df["revised_target"] > 0)
    has_std_target = is_inn2 & (~has_rev_target) & df["inn1_total_runs"].notna()

    target_series = pd.Series(np.nan, index=df.index, dtype="float64")
    target_series = target_series.mask(has_rev_target, df["revised_target"])
    target_series = target_series.mask(has_std_target, df["inn1_total_runs"] + 1)
    df["target"] = target_series

    target_status = pd.Series("NOT_APPLICABLE_FIRST_INNINGS", index=df.index, dtype="string")
    target_status = target_status.mask(has_rev_target, "VALID_DLS_REVISED")
    target_status = target_status.mask(has_std_target, "VALID_STANDARD_TARGET")
    target_status = target_status.mask(is_inn2 & df["target"].isna(), "MISSING_TARGET")
    df["target_status"] = target_status

    # 8. Pre-Delivery Runs Required
    runs_req = np.where(
        is_inn2 & df["target"].notna(),
        np.maximum(0.0, df["target"] - df["pre_delivery_runs"]),
        np.nan
    )
    df["pre_delivery_runs_required"] = runs_req

    # 9. Required Run Rate
    rem_balls = df["pre_delivery_balls_remaining"]
    req_rr = pd.Series(np.nan, index=df.index, dtype="float64")

    cond_active = is_inn2 & df["target"].notna() & (rem_balls > 0) & (df["pre_delivery_runs_required"] > 0)
    cond_achieved = is_inn2 & df["target"].notna() & (df["pre_delivery_runs_required"] == 0)
    cond_exhausted = is_inn2 & df["target"].notna() & (rem_balls == 0) & (df["pre_delivery_runs_required"] > 0)

    req_rr = req_rr.mask(cond_active, (df["pre_delivery_runs_required"] / rem_balls) * 6.0)
    req_rr = req_rr.mask(cond_achieved, 0.0)
    req_rr = req_rr.mask(cond_exhausted, 36.0)
    df["pre_delivery_required_run_rate"] = req_rr

    # 10. Current Run Rate
    legal_so_far = df["pre_delivery_legal_balls"]
    df["pre_delivery_current_run_rate"] = np.where(
        legal_so_far > 0,
        (df["pre_delivery_runs"] / legal_so_far) * 6.0,
        0.0
    )

    # 11. Uncertainty Flag
    uncertainty = pd.Series("NONE", index=df.index, dtype="string")
    uncertainty = uncertainty.mask(is_inn2 & df["target"].isna(), "AMBIGUOUS_OR_MISSING_TARGET")
    uncertainty = uncertainty.mask(cond_exhausted, "SCHEDULED_OVERS_EXHAUSTED")
    df["match_state_uncertainty"] = uncertainty

    # Clean temporary columns
    df = df.drop(columns=["first_inn_revised_overs", "second_inn_revised_overs", "revised_target", "inn1_total_runs"])

    logger.info("Match-state reconstruction completed with 100% vector efficiency.")
    return df
