import os
import json
import logging
import pandas as pd
import numpy as np

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"
LOG_DIR = r"logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
log_path = os.path.join(LOG_DIR, "phase0_validation.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

def run_phase0_deliverables():
    logging.info("Starting Phase 0 Data Dictionary, Inventory, and Validation Audit...")

    files = [
        "competitions.csv",
        "teams.csv",
        "matches.csv",
        "playing_eleven.csv",
        "competition_team_player_mapping.csv",
        "ball_by_ball.csv"
    ]

    inventory = {}
    dict_rows = []

    # Column descriptions mapping
    descriptions = {
        # competitions.csv
        ("competitions.csv", "comp_id"): "Unique identifier for the cricket tournament/series (Primary Key).",
        ("competitions.csv", "comp_name"): "Official name of the tournament or bilateral series.",
        ("competitions.csv", "match_format"): "Format of cricket ('T20I' for international, 'T20' for domestic/regional leagues).",
        ("competitions.csv", "season"): "Cricket season or calendar year (e.g., '2022', '2022/23', '2026').",

        # teams.csv
        ("teams.csv", "comp_id"): "Foreign Key referencing competitions.csv(comp_id).",
        ("teams.csv", "team_id"): "Unique identifier for the cricket team/franchise/national squad.",
        ("teams.csv", "team_name"): "Official team name.",

        # matches.csv
        ("matches.csv", "match_id"): "Unique identifier for each match (Primary Key).",
        ("matches.csv", "comp_id"): "Foreign Key referencing competitions.csv(comp_id).",
        ("matches.csv", "match_number"): "Match sequence number within the tournament or series.",
        ("matches.csv", "match_date"): "Scheduled start date of the match (YYYY-MM-DD).",
        ("matches.csv", "stage"): "Stage of the tournament (e.g. 'League', 'Final', 'Semi Final', 'Qualifier 1').",
        ("matches.csv", "venue_id"): "Unique identifier for the ground/stadium.",
        ("matches.csv", "venue_country"): "Host country where the match took place.",
        ("matches.csv", "home_team_id"): "Foreign Key referencing teams.csv(team_id) for the designated home team.",
        ("matches.csv", "home_team"): "Name of designated home team.",
        ("matches.csv", "away_team_id"): "Foreign Key referencing teams.csv(team_id) for the designated away team.",
        ("matches.csv", "away_team"): "Name of designated away team.",
        ("matches.csv", "home_team_captain_id"): "Foreign Key referencing player_id for home team captain.",
        ("matches.csv", "away_team_captain_id"): "Foreign Key referencing player_id for away team captain.",
        ("matches.csv", "toss_win_team_id"): "Foreign Key referencing teams.csv(team_id) for team winning the toss.",
        ("matches.csv", "toss_opted"): "Decision made by toss winner ('Batting' or 'Fielding').",
        ("matches.csv", "man_of_the_match"): "Foreign Key referencing player_id for Player of the Match awardee (0 if none).",
        ("matches.csv", "first_inn_revised_overs"): "Total legal balls scheduled for 1st innings after rain/weather reduction (e.g., 90.0 = 15 overs).",
        ("matches.csv", "second_inn_revised_overs"): "Total legal balls scheduled for 2nd innings after DLS revision (e.g., 90.0 = 15 overs).",
        ("matches.csv", "revised_target"): "DLS revised target score for the chasing team.",
        ("matches.csv", "knock_out"): "Binary indicator (1 if knockout/playoff match, 0 if league/group stage).",
        ("matches.csv", "win_team_id"): "Foreign Key referencing teams.csv(team_id) for winning team (null if No Result / Abandoned).",
        ("matches.csv", "result"): "Official text match outcome description.",

        # playing_eleven.csv
        ("playing_eleven.csv", "match_id"): "Foreign Key referencing matches.csv(match_id).",
        ("playing_eleven.csv", "team_id"): "Foreign Key referencing teams.csv(team_id).",
        ("playing_eleven.csv", "player_id"): "Foreign Key referencing competition_team_player_mapping.csv(player_id).",
        ("playing_eleven.csv", "batting_order"): "Nominal batting position or order listed in playing team sheet.",
        ("playing_eleven.csv", "is_played"): "Boolean flag: True if player was in the playing XI / took part in the match.",
        ("playing_eleven.csv", "is_captain"): "Boolean flag: True if player was designated team captain.",
        ("playing_eleven.csv", "is_wk"): "Boolean flag: True if player was designated wicketkeeper.",
        ("playing_eleven.csv", "is_impact"): "Flag indicating player was brought in as an IPL Impact Player (1=yes, 0=no).",
        ("playing_eleven.csv", "is_impact_off"): "Flag indicating player was substituted out as an IPL Impact Player (1=yes, 0=no).",

        # competition_team_player_mapping.csv
        ("competition_team_player_mapping.csv", "comp_id"): "Foreign Key referencing competitions.csv(comp_id).",
        ("competition_team_player_mapping.csv", "comp_name"): "Tournament name as registered in roster mapping.",
        ("competition_team_player_mapping.csv", "team_id"): "Foreign Key referencing teams.csv(team_id).",
        ("competition_team_player_mapping.csv", "team_name"): "Team name as registered in roster mapping.",
        ("competition_team_player_mapping.csv", "player_id"): "Authoritative unique player identifier across all datasets.",
        ("competition_team_player_mapping.csv", "player_name"): "Authoritative canonical player display name.",

        # ball_by_ball.csv
        ("ball_by_ball.csv", "match_id"): "Foreign Key referencing matches.csv(match_id).",
        ("ball_by_ball.csv", "innings"): "Innings number (1: 1st inn, 2: 2nd inn, 3: Super Over 1st inn, 4: Super Over 2nd inn).",
        ("ball_by_ball.csv", "overid"): "Over sequence number (1-indexed: 1 = 1st over, 20 = 20th over).",
        ("ball_by_ball.csv", "over_ball_num"): "Ball number within the over (increments on all deliveries including extras; 1 to 13).",
        ("ball_by_ball.csv", "innings_ball_num"): "Chronological ball sequence number within the innings (1 to 136).",
        ("ball_by_ball.csv", "batting_team_id"): "Foreign Key referencing teams.csv(team_id) for the batting side.",
        ("ball_by_ball.csv", "bowling_team_id"): "Foreign Key referencing teams.csv(team_id) for the bowling/fielding side.",
        ("ball_by_ball.csv", "striker_id"): "Foreign Key referencing player_id for batter facing the delivery.",
        ("ball_by_ball.csv", "striker_name"): "Display name of facing batter.",
        ("ball_by_ball.csv", "non_striker_id"): "Foreign Key referencing player_id for non-striker at bowler's end.",
        ("ball_by_ball.csv", "non_striker_name"): "Display name of non-striker.",
        ("ball_by_ball.csv", "bowler_id"): "Foreign Key referencing player_id for bowler delivering the ball.",
        ("ball_by_ball.csv", "bowler_name"): "Display name of bowler.",
        ("ball_by_ball.csv", "batting_type"): "Batting stance / hand ('RHB' = Right Hand Bat, 'LHB' = Left Hand Bat).",
        ("ball_by_ball.csv", "bowling_type"): "Bowling classification (e.g. 'Right-arm fast', 'Left-arm orthodox', etc.).",
        ("ball_by_ball.csv", "batting_order"): "Nominal batting order of the facing batter.",
        ("ball_by_ball.csv", "runs"): "Runs scored off the bat by the striker (0, 1, 2, 3, 4, 5, 6). Excludes extras.",
        ("ball_by_ball.csv", "is_four"): "Boolean flag: True if delivery resulted in a boundary four scored by the batter.",
        ("ball_by_ball.csv", "is_six"): "Boolean flag: True if delivery resulted in a boundary six scored by the batter.",
        ("ball_by_ball.csv", "is_wicket"): "Boolean flag: True if a dismissal occurred on this delivery.",
        ("ball_by_ball.csv", "dismissal_type_id"): "Numeric code for dismissal category.",
        ("ball_by_ball.csv", "dismissal_type"): "Dismissal category ('Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket', 'RunOut', etc.).",
        ("ball_by_ball.csv", "dismissed_player_id"): "Foreign Key referencing player_id for dismissed batter.",
        ("ball_by_ball.csv", "extras_type"): "Type of extra on delivery ('wide', 'Overstep', 'other', 'legbyes', 'byes', 'Penalty', or NaN).",
        ("ball_by_ball.csv", "extras1_runs"): "Primary extra runs awarded (wide run, no-ball run, bye runs, leg-bye runs, penalty).",
        ("ball_by_ball.csv", "extras_2_runs"): "Secondary extra runs on delivery (e.g., byes/leg-byes occurring on a no-ball).",
        ("ball_by_ball.csv", "pace_or_spin"): "Delivery categorization ('Pace' or 'Spin').",
        ("ball_by_ball.csv", "bowl_speed"): "Measured bowling release speed (km/h) when tracking is available (0 if unavailable).",
        ("ball_by_ball.csv", "stroke"): "Shot type played by batter (e.g., 'Cover Drive', 'Pull', 'Defended', etc.).",
        ("ball_by_ball.csv", "delivery_style"): "Pitch trajectory / movement (e.g., 'Inswing', 'Outswing', 'Off break', etc.).",
        ("ball_by_ball.csv", "over_or_around"): "Bowler delivery side relative to stumps ('Over' or 'Around').",
        ("ball_by_ball.csv", "on_or_off"): "Line of delivery relative to stumps ('Off-side', 'On-side', 'Straight').",
        ("ball_by_ball.csv", "delivery_ist_time"): "Timestamp of delivery recorded in Indian Standard Time (IST)."
    }

    key_types = {
        ("competitions.csv", "comp_id"): "Primary Key",
        ("teams.csv", "comp_id"): "Composite Key / FK",
        ("teams.csv", "team_id"): "Composite Key",
        ("matches.csv", "match_id"): "Primary Key",
        ("matches.csv", "comp_id"): "Foreign Key",
        ("matches.csv", "home_team_id"): "Foreign Key",
        ("matches.csv", "away_team_id"): "Foreign Key",
        ("matches.csv", "win_team_id"): "Foreign Key",
        ("matches.csv", "toss_win_team_id"): "Foreign Key",
        ("playing_eleven.csv", "match_id"): "Composite Key / FK",
        ("playing_eleven.csv", "player_id"): "Composite Key / FK",
        ("playing_eleven.csv", "team_id"): "Foreign Key",
        ("competition_team_player_mapping.csv", "comp_id"): "Foreign Key",
        ("competition_team_player_mapping.csv", "team_id"): "Foreign Key",
        ("competition_team_player_mapping.csv", "player_id"): "Foreign Key / Entity PK",
        ("ball_by_ball.csv", "match_id"): "Composite Key / FK",
        ("ball_by_ball.csv", "innings"): "Composite Key",
        ("ball_by_ball.csv", "overid"): "Composite Key",
        ("ball_by_ball.csv", "over_ball_num"): "Composite Key",
        ("ball_by_ball.csv", "batting_team_id"): "Foreign Key",
        ("ball_by_ball.csv", "bowling_team_id"): "Foreign Key",
        ("ball_by_ball.csv", "striker_id"): "Foreign Key",
        ("ball_by_ball.csv", "non_striker_id"): "Foreign Key",
        ("ball_by_ball.csv", "bowler_id"): "Foreign Key",
        ("ball_by_ball.csv", "dismissed_player_id"): "Foreign Key"
    }

    for fname in files:
        fpath = os.path.join(DATA_DIR, fname)
        size_bytes = os.path.getsize(fpath)
        logging.info(f"Processing {fname} ({size_bytes:,} bytes)...")
        
        df = pd.read_csv(fpath, low_memory=False)
        row_count, col_count = df.shape

        inventory[fname] = {
            "file_name": fname,
            "file_size_bytes": size_bytes,
            "row_count": row_count,
            "column_count": col_count,
            "columns": list(df.columns)
        }

        for col in df.columns:
            s = df[col]
            null_count = int(s.isnull().sum())
            null_pct = round(float(null_count / row_count) * 100, 2)
            distinct_count = int(s.nunique(dropna=False))
            dtype = str(s.dtype)
            
            # samples
            non_null_samples = s.dropna().unique()
            if len(non_null_samples) > 0:
                sample_str = "; ".join([str(x) for x in non_null_samples[:3]])
            else:
                sample_str = "None"

            ktype = key_types.get((fname, col), "Attribute")
            desc = descriptions.get((fname, col), "Standard match/delivery attribute.")

            dict_rows.append({
                "table_name": fname,
                "column_name": col,
                "data_type": dtype,
                "key_type": ktype,
                "nullable": null_count > 0,
                "null_count": null_count,
                "null_percentage": null_pct,
                "distinct_count": distinct_count,
                "sample_values": sample_str,
                "description": desc
            })

    # Save data_dictionary.csv
    dict_df = pd.DataFrame(dict_rows)
    dict_df.to_csv("data_dictionary.csv", index=False)
    logging.info(f"Saved data_dictionary.csv with {len(dict_df)} column definitions.")

    # Save dataset_inventory.json
    with open("dataset_inventory.json", "w") as jf:
        json.dump(inventory, jf, indent=2)
    logging.info("Saved dataset_inventory.json.")

if __name__ == '__main__':
    run_phase0_deliverables()
