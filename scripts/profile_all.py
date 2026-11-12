import os
import json
import pandas as pd
import numpy as np

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"

def run_profiling():
    print("--- 1. PROFILING COMPETITIONS ---")
    comp_df = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
    print(f"Competitions shape: {comp_df.shape}")
    print(f"Unique comp_id: {comp_df['comp_id'].nunique()}")
    print("Competitions breakdown by match_format:")
    print(comp_df['match_format'].value_counts())
    print("\nCompetitions breakdown by season:")
    print(comp_df['season'].value_counts().sort_index())
    print("\nSample competitions:")
    print(comp_df.head(10))
    # Check IPL competitions
    ipl_comps = comp_df[comp_df['comp_name'].str.contains('IPL|Indian Premier League', case=False, na=False)]
    print("\nIPL competitions in competitions.csv:")
    print(ipl_comps)

    print("\n--- 2. PROFILING TEAMS ---")
    teams_df = pd.read_csv(os.path.join(DATA_DIR, "teams.csv"))
    print(f"Teams shape: {teams_df.shape}")
    print(f"Unique comp_id in teams: {teams_df['comp_id'].nunique()}")
    print(f"Unique team_id in teams: {teams_df['team_id'].nunique()}")
    print(f"Duplicate (comp_id, team_id): {teams_df.duplicated(subset=['comp_id', 'team_id']).sum()}")
    
    print("\n--- 3. PROFILING MATCHES ---")
    matches_df = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
    print(f"Matches shape: {matches_df.shape}")
    print(f"Unique match_id: {matches_df['match_id'].nunique()}")
    print(f"Duplicates in match_id: {matches_df['match_id'].duplicated().sum()}")
    print("Matches null counts:")
    print(matches_df.isnull().sum()[matches_df.isnull().sum() > 0])
    print(f"Match date range: {matches_df['match_date'].min()} to {matches_df['match_date'].max()}")
    print("Result sample / value counts (top 10):")
    print(matches_df['result'].value_counts().head(10))
    # Check ties / super overs / no results
    print("Non-standard results:")
    print(matches_df[matches_df['result'].str.contains('Tie|Super|No Result|D/L|abandon', case=False, na=False)]['result'].value_counts())
    print("Revised target non-null count:", matches_df['revised_target'].notnull().sum())
    print("first_inn_revised_overs non-null count:", matches_df['first_inn_revised_overs'].notnull().sum())
    print("second_inn_revised_overs non-null count:", matches_df['second_inn_revised_overs'].notnull().sum())
    if matches_df['revised_target'].notnull().sum() > 0:
        print("Sample revised matches:")
        print(matches_df[matches_df['revised_target'].notnull()][['match_id', 'match_date', 'first_inn_revised_overs', 'second_inn_revised_overs', 'revised_target', 'result']].head(10))

    print("\n--- 4. PROFILING PLAYING ELEVEN ---")
    pe_df = pd.read_csv(os.path.join(DATA_DIR, "playing_eleven.csv"))
    print(f"Playing eleven shape: {pe_df.shape}")
    print(f"Unique match_id: {pe_df['match_id'].nunique()}")
    print(f"Unique player_id: {pe_df['player_id'].nunique()}")
    print(f"Duplicate (match_id, player_id): {pe_df.duplicated(subset=['match_id', 'player_id']).sum()}")
    print("is_played value counts:")
    print(pe_df['is_played'].value_counts(dropna=False))
    print("is_impact value counts:")
    print(pe_df['is_impact'].value_counts(dropna=False))
    print("is_impact_off value counts:")
    print(pe_df['is_impact_off'].value_counts(dropna=False))

    print("\n--- 5. PROFILING COMPETITION TEAM PLAYER MAPPING ---")
    ctp_df = pd.read_csv(os.path.join(DATA_DIR, "competition_team_player_mapping.csv"))
    print(f"CTP shape: {ctp_df.shape}")
    print(f"Unique player_id: {ctp_df['player_id'].nunique()}")
    print(f"Unique player_name: {ctp_df['player_name'].nunique()}")
    # Check if any player_id has multiple player_names
    p_names = ctp_df.groupby('player_id')['player_name'].nunique()
    multi_names = p_names[p_names > 1]
    print(f"Player IDs with multiple names: {len(multi_names)}")
    if len(multi_names) > 0:
        print(ctp_df[ctp_df['player_id'].isin(multi_names.index)].drop_duplicates(subset=['player_id', 'player_name']))
    # Check if any player_name has multiple player_ids
    n_ids = ctp_df.groupby('player_name')['player_id'].nunique()
    multi_ids = n_ids[n_ids > 1]
    print(f"Player names with multiple IDs: {len(multi_ids)}")
    if len(multi_ids) > 0:
        print(ctp_df[ctp_df['player_name'].isin(multi_ids.index)].drop_duplicates(subset=['player_name', 'player_id']))

if __name__ == '__main__':
    run_profiling()
