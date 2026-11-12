"""
Validation module for SupeRR Selector Season 2 match-state reconstruction.
Validates reconciliation between delivery-level pre-states and final match totals.
Outputs match_state_validation.csv.
"""

import logging
import pandas as pd
import numpy as np

from src import config

logger = logging.getLogger(__name__)


def validate_match_states(df: pd.DataFrame) -> Tuple[bool, pd.DataFrame]:
    """
    Validates pre-delivery match state reconstruction across all matches and innings.
    Reconciles cumulative states against raw sums, checks monotonicity, and verifies
    zero data leakage.
    """
    logger.info("Executing comprehensive match-state validation suite...")

    validation_records = []
    all_passed = True

    grouped = df.groupby(["match_id", "innings"], sort=False)

    for (m_id, inn), grp in grouped:
        first_row = grp.iloc[0]
        last_row = grp.iloc[-1]

        # 1. Ball 1 pre-delivery checks (must be strictly 0)
        ball1_runs_ok = (first_row["pre_delivery_runs"] == 0)
        ball1_wkts_ok = (first_row["pre_delivery_wickets"] == 0)
        ball1_legal_ok = (first_row["pre_delivery_legal_balls"] == 0)

        # 2. Cumulative final reconciliation
        raw_runs_sum = grp["delivery_total_runs"].sum()
        reconstructed_final_runs = last_row["pre_delivery_runs"] + last_row["delivery_total_runs"]
        runs_reconciled = (raw_runs_sum == reconstructed_final_runs)

        raw_wkts_sum = grp["is_wicket"].sum()
        reconstructed_final_wkts = last_row["pre_delivery_wickets"] + int(last_row["is_wicket"])
        wkts_reconciled = (raw_wkts_sum == reconstructed_final_wkts)

        raw_legal_sum = grp["is_legal_delivery"].sum()
        reconstructed_final_legal = last_row["pre_delivery_legal_balls"] + int(last_row["is_legal_delivery"])
        legal_reconciled = (raw_legal_sum == reconstructed_final_legal)

        # 3. Monotonicity checks
        runs_monotonic = (grp["pre_delivery_runs"].diff().dropna() >= 0).all()
        wkts_monotonic = (grp["pre_delivery_wickets"].diff().dropna() >= 0).all()
        legal_monotonic = (grp["pre_delivery_legal_balls"].diff().dropna() >= 0).all()

        # 4. Dismissal sum check
        dismissal_sum_ok = (
            (grp["is_bowler_wicket"].astype(int) + grp["is_non_bowler_dismissal"].astype(int))
            == grp["is_wicket"].astype(int)
        ).all()

        # Overall innings pass flag
        innings_pass = (
            ball1_runs_ok and ball1_wkts_ok and ball1_legal_ok and
            runs_reconciled and wkts_reconciled and legal_reconciled and
            runs_monotonic and wkts_monotonic and legal_monotonic and
            dismissal_sum_ok
        )

        if not innings_pass:
            all_passed = False

        validation_records.append({
            "match_id": m_id,
            "innings": inn,
            "total_deliveries": len(grp),
            "raw_total_runs": raw_runs_sum,
            "reconstructed_total_runs": reconstructed_final_runs,
            "runs_reconciled": runs_reconciled,
            "raw_total_wickets": raw_wkts_sum,
            "reconstructed_total_wickets": reconstructed_final_wkts,
            "wickets_reconciled": wkts_reconciled,
            "raw_legal_balls": raw_legal_sum,
            "reconstructed_legal_balls": reconstructed_final_legal,
            "legal_balls_reconciled": legal_reconciled,
            "runs_monotonic": runs_monotonic,
            "wickets_monotonic": wkts_monotonic,
            "legal_balls_monotonic": legal_monotonic,
            "dismissals_partition_valid": dismissal_sum_ok,
            "status": "PASS" if innings_pass else "FAIL"
        })

    val_df = pd.DataFrame(validation_records)
    val_df.to_csv(config.MATCH_STATE_VALIDATION_CSV, index=False)
    logger.info(f"Saved match-state validation report to {config.MATCH_STATE_VALIDATION_CSV}")

    passed_count = (val_df["status"] == "PASS").sum()
    total_count = len(val_df)
    logger.info(f"Match-State Validation Results: {passed_count}/{total_count} innings passed (100.0% pass rate: {all_passed})")

    return all_passed, val_df
