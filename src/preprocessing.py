"""
Main preprocessing orchestrator for SupeRR Selector Season 2.
Coordinates data loading, competition filtering, Super Over isolation,
match-state reconstruction, validation, and parquet serialization.
"""

import logging
import pandas as pd
from typing import Dict, Tuple

from src import config, loaders, competition_filter, match_state, validation, reporting

logger = logging.getLogger(__name__)


def run_pipeline() -> Dict[str, pd.DataFrame]:
    """
    Executes the complete Phase 1 Data Engineering pipeline.
    Returns dictionary containing processed dataframes.
    """
    logger.info("==================================================")
    logger.info("STARTING PHASE 1 DATA ENGINEERING PIPELINE")
    logger.info("==================================================")

    # 1. Load All Datasets
    raw_data = loaders.load_all_datasets()
    comp_df = raw_data["competitions"]
    teams_df = raw_data["teams"]
    matches_df = raw_data["matches"]
    pe_df = raw_data["playing_eleven"]
    ctp_df = raw_data["player_mapping"]
    bbb_df = raw_data["ball_by_ball"]

    raw_counts = {k: len(v) for k, v in raw_data.items()}

    # 2. Filter Competitions (IPL + T20I only)
    retained_comps, retained_matches, retained_deliveries, excluded_deliveries = (
        competition_filter.filter_dataset_by_competition(comp_df, matches_df, bbb_df)
    )

    # Attach competition metadata to retained matches
    comp_meta = comp_df[["comp_id", "comp_name", "match_format", "season"]]
    retained_matches = retained_matches.merge(comp_meta, on="comp_id", how="left")

    # 3. Super Over Isolation
    so_mask = retained_deliveries["innings"].isin([3, 4])
    super_over_df = retained_deliveries[so_mask].copy().reset_index(drop=True)
    standard_deliveries = retained_deliveries[~so_mask].copy().reset_index(drop=True)

    logger.info(f"Isolated {len(super_over_df)} Super Over deliveries into super_over_deliveries.parquet")
    logger.info(f"Retained {len(standard_deliveries)} standard innings (1 and 2) deliveries for processing")

    # Save Super Over Parquet
    super_over_df.to_parquet(config.SUPER_OVER_PARQUET, index=False, engine="pyarrow")
    logger.info(f"Saved Super Over parquet to {config.SUPER_OVER_PARQUET}")

    # 4. Attach Competition and Canonical Player Metadata to Deliveries
    # Attach comp_name, match_format, season via match_id
    delivery_comp_meta = retained_matches[["match_id", "comp_id", "comp_name", "match_format", "season"]]
    standard_deliveries = standard_deliveries.merge(delivery_comp_meta, on="match_id", how="left")

    # Authoritative canonical player display name map
    canon_names = ctp_df.groupby("player_id")["player_name"].first().to_dict()
    standard_deliveries["striker_canonical_name"] = standard_deliveries["striker_id"].map(canon_names)
    standard_deliveries["non_striker_canonical_name"] = standard_deliveries["non_striker_id"].map(canon_names)
    standard_deliveries["bowler_canonical_name"] = standard_deliveries["bowler_id"].map(canon_names)
    standard_deliveries["dismissed_canonical_name"] = standard_deliveries["dismissed_player_id"].map(canon_names)

    # 5. Reconstruct Match State immediately BEFORE each delivery
    processed_deliveries = match_state.reconstruct_match_state(standard_deliveries, retained_matches)

    # 6. Validate Match State Reconstruction
    validation_passed, val_df = validation.validate_match_states(processed_deliveries)
    if not validation_passed:
        logger.error("CRITICAL: Match state validation encountered failures! Check match_state_validation.csv.")
        raise AssertionError("Match state validation failed reconciliation!")

    # 7. Persist Primary Parquet Outputs
    logger.info("Persisting processed datasets to Parquet (Snappy compressed)...")
    processed_deliveries.to_parquet(
        config.PROCESSED_DELIVERIES_PARQUET, index=False, engine="pyarrow", compression="snappy"
    )
    logger.info(f"Saved {len(processed_deliveries):,} rows to {config.PROCESSED_DELIVERIES_PARQUET}")

    retained_matches.to_parquet(
        config.PROCESSED_MATCHES_PARQUET, index=False, engine="pyarrow", compression="snappy"
    )
    logger.info(f"Saved {len(retained_matches):,} rows to {config.PROCESSED_MATCHES_PARQUET}")

    # 8. Generate Preprocessing Report
    comp_audit_df = pd.read_csv(config.COMPETITION_AUDIT_CSV)
    reporting.generate_preprocessing_report(
        raw_counts=raw_counts,
        comp_audit_df=comp_audit_df,
        matches_df=retained_matches,
        processed_deliveries_df=processed_deliveries,
        super_over_df=super_over_df,
        excluded_df=excluded_deliveries,
        val_df=val_df
    )

    logger.info("==================================================")
    logger.info("PHASE 1 DATA ENGINEERING COMPLETED SUCCESSFULLY!")
    logger.info("==================================================")

    return {
        "processed_deliveries": processed_deliveries,
        "processed_matches": retained_matches,
        "super_overs": super_over_df,
        "excluded_deliveries": excluded_deliveries,
        "validation_report": val_df
    }
