"""
Configuration module for SupeRR Selector Season 2 Pressure Intelligence System.
Defines paths, cricket domain constants, schemas, and competition rules.
"""

import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "6af458274c1e8_data_pack" / "Data Pack"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
PROCESSED_DIR = OUTPUT_DIR / "processed"
REPORTS_DIR = OUTPUT_DIR / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Raw Source File Paths
COMPETITIONS_FILE = DATA_DIR / "competitions.csv"
TEAMS_FILE = DATA_DIR / "teams.csv"
MATCHES_FILE = DATA_DIR / "matches.csv"
PLAYING_ELEVEN_FILE = DATA_DIR / "playing_eleven.csv"
PLAYER_MAPPING_FILE = DATA_DIR / "competition_team_player_mapping.csv"
BALL_BY_BALL_FILE = DATA_DIR / "ball_by_ball.csv"

# Output File Paths
PROCESSED_DELIVERIES_PARQUET = PROCESSED_DIR / "processed_deliveries.parquet"
PROCESSED_MATCHES_PARQUET = PROCESSED_DIR / "processed_matches.parquet"
SUPER_OVER_PARQUET = PROCESSED_DIR / "super_over_deliveries.parquet"
EXCLUDED_DELIVERIES_CSV = PROCESSED_DIR / "excluded_deliveries.csv"

COMPETITION_AUDIT_CSV = REPORTS_DIR / "competition_audit.csv"
MATCH_STATE_VALIDATION_CSV = REPORTS_DIR / "match_state_validation.csv"
PREPROCESSING_REPORT_MD = REPORTS_DIR / "preprocessing_report.md"

# Cricket Domain Constants
STANDARD_T20_LEGAL_BALLS = 120
BALLS_PER_OVER = 6

# Extras Classification
ILLEGAL_EXTRAS = {"wide", "Overstep", "other"}
FIELDING_EXTRAS = {"byes", "legbyes", "Penalty"}
BOWLER_CHARGED_EXTRAS = {"wide", "Overstep", "other"}

# Dismissal Categorization
BOWLER_CREDITED_DISMISSALS = {
    "Bowled",
    "Caught",
    "LBW",
    "Stump",
    "Hit Wicket"
}

NON_BOWLER_DISMISSALS = {
    "RunOut",
    "Retire Out",
    "Obstructing the field",
    "Obstracting the field"  # spelling variant in source data
}

# Innings Stages (based on overid: 1-indexed, 1 to 20)
STAGE_POWERPLAY = "Powerplay"  # Overs 1 to 6
STAGE_MIDDLE = "Middle"        # Overs 7 to 15
STAGE_DEATH = "Death"          # Overs 16 to 20

# Dtypes for Loading
DTYPES_COMPETITIONS = {
    "comp_id": "int64",
    "comp_name": "string",
    "match_format": "string",
    "season": "string"
}

DTYPES_TEAMS = {
    "comp_id": "int64",
    "team_id": "int64",
    "team_name": "string"
}

DTYPES_MATCHES = {
    "match_id": "int64",
    "comp_id": "int64",
    "match_number": "float64",  # Some may be missing/text
    "match_date": "string",
    "stage": "string",
    "venue_id": "int64",
    "venue_country": "string",
    "home_team_id": "Int64",
    "home_team": "string",
    "away_team_id": "Int64",
    "away_team": "string",
    "home_team_captain_id": "Int64",
    "away_team_captain_id": "Int64",
    "toss_win_team_id": "Int64",
    "toss_opted": "string",
    "man_of_the_match": "Int64",
    "first_inn_revised_overs": "float64",
    "second_inn_revised_overs": "float64",
    "revised_target": "float64",
    "knock_out": "int64",
    "win_team_id": "Int64",
    "result": "string"
}

DTYPES_PLAYING_ELEVEN = {
    "match_id": "int64",
    "team_id": "int64",
    "player_id": "int64",
    "batting_order": "float64",
    "is_played": "bool",
    "is_captain": "boolean",
    "is_wk": "boolean",
    "is_impact": "int64",
    "is_impact_off": "int64"
}

DTYPES_PLAYER_MAPPING = {
    "comp_id": "int64",
    "comp_name": "string",
    "team_id": "int64",
    "team_name": "string",
    "player_id": "int64",
    "player_name": "string"
}

DTYPES_BALL_BY_BALL = {
    "match_id": "int64",
    "innings": "int64",
    "overid": "int64",
    "over_ball_num": "int64",
    "innings_ball_num": "int64",
    "batting_team_id": "int64",
    "bowling_team_id": "int64",
    "striker_id": "int64",
    "striker_name": "string",
    "non_striker_id": "int64",
    "non_striker_name": "string",
    "bowler_id": "int64",
    "bowler_name": "string",
    "batting_type": "string",
    "bowling_type": "string",
    "batting_order": "float64",
    "runs": "int64",
    "is_four": "bool",
    "is_six": "bool",
    "is_wicket": "bool",
    "dismissal_type_id": "float64",
    "dismissal_type": "string",
    "dismissed_player_id": "Int64",
    "extras_type": "string",
    "extras1_runs": "int64",
    "extras_2_runs": "int64",
    "pace_or_spin": "string",
    "bowl_speed": "float64",
    "stroke": "string",
    "delivery_style": "string",
    "over_or_around": "string",
    "on_or_off": "string",
    "delivery_ist_time": "string"
}
