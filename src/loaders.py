"""
Data loading module for SupeRR Selector Season 2 Pressure Intelligence System.
Loads all source CSV files with explicit dtypes, key checks, and logging.
"""

import logging
import pandas as pd
from typing import Dict, Tuple

from src import config

logger = logging.getLogger(__name__)


def load_competitions() -> pd.DataFrame:
    """Loads competitions.csv and validates primary key uniqueness."""
    path = config.COMPETITIONS_FILE
    logger.info(f"Loading competitions from {path}")
    df = pd.read_csv(path, dtype=config.DTYPES_COMPETITIONS)
    logger.info(f"Loaded competitions: {len(df)} rows, {len(df.columns)} columns")
    if not df["comp_id"].is_unique:
        raise ValueError("Primary key comp_id in competitions.csv is not unique!")
    return df


def load_teams() -> pd.DataFrame:
    """Loads teams.csv and validates composite key uniqueness."""
    path = config.TEAMS_FILE
    logger.info(f"Loading teams from {path}")
    df = pd.read_csv(path, dtype=config.DTYPES_TEAMS)
    logger.info(f"Loaded teams: {len(df)} rows, {len(df.columns)} columns")
    if df.duplicated(subset=["comp_id", "team_id"]).any():
        raise ValueError("Composite key (comp_id, team_id) in teams.csv is not unique!")
    return df


def load_matches() -> pd.DataFrame:
    """Loads matches.csv and validates primary key uniqueness."""
    path = config.MATCHES_FILE
    logger.info(f"Loading matches from {path}")
    df = pd.read_csv(path, dtype=config.DTYPES_MATCHES)
    logger.info(f"Loaded matches: {len(df)} rows, {len(df.columns)} columns")
    if not df["match_id"].is_unique:
        raise ValueError("Primary key match_id in matches.csv is not unique!")
    return df


def load_playing_eleven() -> pd.DataFrame:
    """
    Loads playing_eleven.csv and deduplicates the 3 known matches with duplicate records.
    Deduplication keeps is_played == True and the lowest non-null batting_order.
    """
    path = config.PLAYING_ELEVEN_FILE
    logger.info(f"Loading playing_eleven from {path}")
    df = pd.read_csv(path, dtype=config.DTYPES_PLAYING_ELEVEN)
    orig_len = len(df)
    logger.info(f"Loaded playing_eleven: {orig_len} raw rows, {len(df.columns)} columns")

    # Audit and handle duplicates
    dup_mask = df.duplicated(subset=["match_id", "player_id"], keep=False)
    if dup_mask.any():
        dup_count = dup_mask.sum()
        dup_matches = df.loc[dup_mask, "match_id"].unique()
        logger.warning(
            f"Found {dup_count} duplicate playing_eleven entries across matches: {list(dup_matches)}. "
            "Deduplicating by prioritizing confirmed playing status and lowest batting order."
        )
        # Sort so that is_played=True comes first, then lower batting order
        df = df.sort_values(by=["match_id", "player_id", "is_played", "batting_order"], ascending=[True, True, False, True])
        df = df.drop_duplicates(subset=["match_id", "player_id"], keep="first").reset_index(drop=True)
        logger.info(f"playing_eleven after deduplication: {len(df)} rows (removed {orig_len - len(df)} duplicate rows)")

    return df


def load_player_mapping() -> pd.DataFrame:
    """Loads competition_team_player_mapping.csv and validates authoritative player mapping."""
    path = config.PLAYER_MAPPING_FILE
    logger.info(f"Loading player mapping from {path}")
    df = pd.read_csv(path, dtype=config.DTYPES_PLAYER_MAPPING)
    logger.info(f"Loaded player mapping: {len(df)} rows, {len(df.columns)} columns")

    # Validate that every player_id has exactly one canonical display name
    names_per_id = df.groupby("player_id")["player_name"].nunique()
    if not (names_per_id == 1).all():
        bad_ids = names_per_id[names_per_id > 1].index.tolist()
        raise ValueError(f"Player IDs with multiple names detected in player mapping: {bad_ids}")

    return df


def load_ball_by_ball() -> pd.DataFrame:
    """Loads ball_by_ball.csv and validates delivery sequence."""
    path = config.BALL_BY_BALL_FILE
    logger.info(f"Loading ball_by_ball from {path} (low_memory=False)")
    df = pd.read_csv(path, dtype=config.DTYPES_BALL_BY_BALL, low_memory=False)
    logger.info(f"Loaded ball_by_ball: {len(df)} rows, {len(df.columns)} columns")
    return df


def load_all_datasets() -> Dict[str, pd.DataFrame]:
    """Loads and validates all six datasets into a dictionary."""
    logger.info("--- Starting Full Dataset Loading ---")
    data = {
        "competitions": load_competitions(),
        "teams": load_teams(),
        "matches": load_matches(),
        "playing_eleven": load_playing_eleven(),
        "player_mapping": load_player_mapping(),
        "ball_by_ball": load_ball_by_ball()
    }
    logger.info("--- All Datasets Loaded Successfully ---")
    return data
