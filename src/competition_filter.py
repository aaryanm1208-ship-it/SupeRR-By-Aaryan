"""
Competition filtering module for SupeRR Selector Season 2 Pressure Intelligence System.
Classifies competitions based on actual metadata into IPL, T20I, and Excluded categories.
Produces competition_audit.csv.
"""

import logging
import pandas as pd
from typing import Tuple

from src import config

logger = logging.getLogger(__name__)


def classify_competitions(comp_df: pd.DataFrame, matches_df: pd.DataFrame) -> pd.DataFrame:
    """
    Classifies competitions into 'IPL', 'T20I', or 'EXCLUDED' using competition metadata.
    IPL: Name contains 'IPL' or 'Indian Premier League' (case-insensitive)
    T20I: match_format == 'T20I'
    EXCLUDED: Regional / development competitions not meeting Senior Men's IPL or T20I status.
    """
    logger.info("Classifying competitions based on metadata...")
    df = comp_df.copy()

    # Calculate match count per competition
    match_counts = matches_df.groupby("comp_id")["match_id"].count().rename("match_count")
    df = df.merge(match_counts, on="comp_id", how="left")
    df["match_count"] = df["match_count"].fillna(0).astype(int)

    categories = []
    reasons = []

    for _, row in df.iterrows():
        comp_name = str(row["comp_name"])
        match_format = str(row["match_format"])

        if "ipl" in comp_name.lower() or "indian premier league" in comp_name.lower():
            categories.append("IPL")
            reasons.append("Retained: Official Indian Premier League competition.")
        elif match_format == "T20I":
            categories.append("T20I")
            reasons.append("Retained: Official Senior Men's T20 International competition.")
        else:
            categories.append("EXCLUDED")
            reasons.append("Excluded: Regional/development tournament; not Senior IPL or official T20I.")

    df["category"] = categories
    df["inclusion_decision"] = df["category"].apply(lambda c: "INCLUDED" if c in ["IPL", "T20I"] else "EXCLUDED")
    df["audit_rationale"] = reasons

    # Save competition audit report
    df.to_csv(config.COMPETITION_AUDIT_CSV, index=False)
    logger.info(f"Saved competition audit to {config.COMPETITION_AUDIT_CSV}")

    # Summary logging
    summary = df.groupby(["category", "inclusion_decision"])["match_count"].agg(["count", "sum"])
    logger.info(f"Competition Classification Summary:\n{summary}")

    return df


def filter_dataset_by_competition(
    comp_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    bbb_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Filters matches and deliveries to retain exclusively IPL and T20I competitions.
    Returns:
        (retained_competitions, retained_matches, retained_deliveries, excluded_deliveries)
    """
    comp_audit = classify_competitions(comp_df, matches_df)

    included_comp_ids = set(comp_audit[comp_audit["inclusion_decision"] == "INCLUDED"]["comp_id"])
    excluded_comp_ids = set(comp_audit[comp_audit["inclusion_decision"] == "EXCLUDED"]["comp_id"])

    logger.info(f"Included competition IDs: {len(included_comp_ids)}")
    logger.info(f"Excluded competition IDs: {len(excluded_comp_ids)} ({excluded_comp_ids})")

    # Filter matches
    retained_matches = matches_df[matches_df["comp_id"].isin(included_comp_ids)].copy().reset_index(drop=True)
    excluded_matches = matches_df[matches_df["comp_id"].isin(excluded_comp_ids)].copy().reset_index(drop=True)
    logger.info(f"Matches retained: {len(retained_matches)} (Excluded: {len(excluded_matches)})")

    retained_match_ids = set(retained_matches["match_id"])
    excluded_match_ids = set(excluded_matches["match_id"])

    # Filter deliveries
    retained_deliveries = bbb_df[bbb_df["match_id"].isin(retained_match_ids)].copy().reset_index(drop=True)
    excluded_deliveries = bbb_df[bbb_df["match_id"].isin(excluded_match_ids)].copy().reset_index(drop=True)
    logger.info(f"Deliveries retained: {len(retained_deliveries)} (Excluded: {len(excluded_deliveries)})")

    # Save excluded deliveries
    excluded_deliveries.to_csv(config.EXCLUDED_DELIVERIES_CSV, index=False)
    logger.info(f"Saved {len(excluded_deliveries)} excluded deliveries to {config.EXCLUDED_DELIVERIES_CSV}")

    retained_comps = comp_audit[comp_audit["inclusion_decision"] == "INCLUDED"].copy().reset_index(drop=True)

    return retained_comps, retained_matches, retained_deliveries, excluded_deliveries
