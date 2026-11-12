import os
import json
import logging
import pandas as pd
import numpy as np

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"
LOG_DIR = r"logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, "phase0_validation.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

def log_and_assert(condition, success_msg, failure_msg):
    if condition:
        logging.info(f"PASS: {success_msg}")
        print(f"PASS: {success_msg}")
    else:
        logging.error(f"FAIL: {failure_msg}")
        print(f"FAIL: {failure_msg}")
        raise AssertionError(failure_msg)

def run_phase0_validation():
    logging.info("==================================================")
    logging.info("PHASE 0: RIGOROUS DATA INTEGRITY AND VALIDATION SUITE")
    logging.info("==================================================")

    # 1. File existence
    required_files = [
        "competitions.csv", "teams.csv", "matches.csv",
        "playing_eleven.csv", "competition_team_player_mapping.csv",
        "ball_by_ball.csv", "Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf"
    ]
    for rf in required_files:
        p = os.path.join(DATA_DIR, rf)
        log_and_assert(os.path.exists(p) and os.path.getsize(p) > 0,
                       f"File {rf} exists and is non-empty ({os.path.getsize(p):,} bytes).",
                       f"File {rf} missing or empty!")

    # Load datasets
    comp = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
    teams = pd.read_csv(os.path.join(DATA_DIR, "teams.csv"))
    matches = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
    pe = pd.read_csv(os.path.join(DATA_DIR, "playing_eleven.csv"))
    ctp = pd.read_csv(os.path.join(DATA_DIR, "competition_team_player_mapping.csv"))
    bbb = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)

    # 2. Row count assertions
    log_and_assert(len(comp) == 141, f"competitions.csv has expected 141 rows (actual={len(comp)}).", "Unexpected row count in competitions.csv")
    log_and_assert(len(teams) == 353, f"teams.csv has expected 353 rows (actual={len(teams)}).", "Unexpected row count in teams.csv")
    log_and_assert(len(matches) == 883, f"matches.csv has expected 883 rows (actual={len(matches)}).", "Unexpected row count in matches.csv")
    log_and_assert(len(pe) == 28381, f"playing_eleven.csv has expected 28,381 rows (actual={len(pe)}).", "Unexpected row count in playing_eleven.csv")
    log_and_assert(len(ctp) == 6413, f"competition_team_player_mapping.csv has expected 6,413 rows (actual={len(ctp)}).", "Unexpected row count in CTP mapping")
    log_and_assert(len(bbb) == 200999, f"ball_by_ball.csv has expected 200,999 rows (actual={len(bbb)}).", "Unexpected row count in ball_by_ball.csv")

    # 3. Primary Key Uniqueness
    log_and_assert(comp['comp_id'].is_unique, "competitions.csv comp_id is strictly unique (PK verified).", "comp_id not unique in competitions")
    log_and_assert(matches['match_id'].is_unique, "matches.csv match_id is strictly unique (PK verified).", "match_id not unique in matches")
    log_and_assert(not teams.duplicated(subset=['comp_id', 'team_id']).any(), "teams.csv (comp_id, team_id) composite key is strictly unique.", "Duplicate team in competition")

    # 4. Foreign Key Referential Integrity (Zero orphans)
    log_and_assert(len(set(teams['comp_id']) - set(comp['comp_id'])) == 0, "All teams.comp_id exist in competitions.", "Orphan comp_id in teams")
    log_and_assert(len(set(matches['comp_id']) - set(comp['comp_id'])) == 0, "All matches.comp_id exist in competitions.", "Orphan comp_id in matches")
    all_teams = set(teams['team_id'])
    log_and_assert(len(set(matches['home_team_id'].dropna()) - all_teams) == 0, "All matches.home_team_id exist in teams.", "Orphan home_team_id")
    log_and_assert(len(set(matches['away_team_id'].dropna()) - all_teams) == 0, "All matches.away_team_id exist in teams.", "Orphan away_team_id")
    log_and_assert(len(set(matches['win_team_id'].dropna()) - all_teams) == 0, "All matches.win_team_id exist in teams.", "Orphan win_team_id")
    log_and_assert(len(set(pe['match_id']) - set(matches['match_id'])) == 0, "All playing_eleven.match_id exist in matches.", "Orphan match_id in PE")
    log_and_assert(len(set(pe['player_id']) - set(ctp['player_id'])) == 0, "All playing_eleven.player_id exist in CTP mapping.", "Orphan player_id in PE")
    log_and_assert(len(set(bbb['match_id']) - set(matches['match_id'])) == 0, "All ball_by_ball.match_id exist in matches.", "Orphan match_id in BBB")
    all_players = set(ctp['player_id'])
    log_and_assert(len(set(bbb['striker_id']) - all_players) == 0, "All strikers exist in CTP players.", "Orphan striker_id")
    log_and_assert(len(set(bbb['non_striker_id']) - all_players) == 0, "All non-strikers exist in CTP players.", "Orphan non_striker_id")
    log_and_assert(len(set(bbb['bowler_id']) - all_players) == 0, "All bowlers exist in CTP players.", "Orphan bowler_id")
    log_and_assert(len(set(bbb['dismissed_player_id'].dropna()) - all_players) == 0, "All dismissed players exist in CTP players.", "Orphan dismissed_player_id")

    # 5. Abandoned Matches Integrity
    missing_bbb_matches = set(matches['match_id']) - set(bbb['match_id'])
    log_and_assert(len(missing_bbb_matches) == 16, f"Exactly 16 matches in matches.csv have no ball-by-ball records.", "Unexpected count of missing BBB matches")
    missing_results = matches[matches['match_id'].isin(missing_bbb_matches)]['result'].unique()
    log_and_assert(list(missing_results) == ['Match Abandoned'], "All 16 missing BBB matches have status 'Match Abandoned'.", "Non-abandoned match missing BBB data!")

    # 6. Player Name Discrepancy & Homonym Checks
    p_names = ctp.groupby('player_id')['player_name'].nunique()
    log_and_assert((p_names == 1).all(), "Every player_id maps to exactly ONE canonical player_name in CTP mapping.", "Player ID maps to multiple names!")
    n_ids = ctp.groupby('player_name')['player_id'].nunique()
    shared_names = n_ids[n_ids > 1].index.tolist()
    log_and_assert(len(shared_names) == 7, f"Exactly 7 player names are shared by multiple player IDs: {shared_names}", "Unexpected homonym count")

    # 7. Cricket Rules & Scorecard Logic Verification
    # Legality
    legal_mask = ~bbb['extras_type'].isin(['wide', 'Overstep', 'other', 'Penalty'])
    illegal_mask = bbb['extras_type'].isin(['wide', 'Overstep', 'other'])
    penalty_mask = bbb['extras_type'] == 'Penalty'
    log_and_assert(legal_mask.sum() == 192444, f"Total legal deliveries = 192,444 (actual={legal_mask.sum()}).", "Unexpected legal delivery count")
    log_and_assert(illegal_mask.sum() == 8554, f"Total illegal deliveries (wide/nb) = 8,554 (actual={illegal_mask.sum()}).", "Unexpected illegal delivery count")
    log_and_assert(penalty_mask.sum() == 1, f"Total penalty delivery events = 1 (actual={penalty_mask.sum()}).", "Unexpected penalty count")

    # Wickets
    bowler_wkts = bbb['dismissal_type'].isin(['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']).sum()
    non_bowler_wkts = bbb['dismissal_type'].isin(['RunOut', 'Retire Out', 'Obstracting the field', 'Obstructing the field']).sum()
    total_wkts = bbb['is_wicket'].sum()
    log_and_assert(total_wkts == 10881, f"Total dismissals = 10,881 (actual={total_wkts}).", "Unexpected total wickets")
    log_and_assert(bowler_wkts == 10272, f"Total bowler-credited wickets = 10,272 (actual={bowler_wkts}).", "Unexpected bowler wickets")
    log_and_assert(non_bowler_wkts == 609, f"Total non-bowler dismissals = 609 (actual={non_bowler_wkts}).", "Unexpected non-bowler wickets")
    log_and_assert(bowler_wkts + non_bowler_wkts == total_wkts, "Bowler wickets + non-bowler wickets equals total wickets exactly.", "Wicket sum mismatch")

    # Super Overs
    so_deliveries = bbb[bbb['innings'].isin([3, 4])]
    log_and_assert(len(so_deliveries) == 38, f"Total super over deliveries = 38 (actual={len(so_deliveries)}).", "Unexpected super over balls")

    # Competition filtering taxonomy
    ipl_comps = comp[comp['comp_name'].str.contains('IPL', case=False, na=False)]['comp_id'].tolist()
    t20i_comps = comp[comp['match_format'] == 'T20I']['comp_id'].tolist()
    unrelated_comps = comp[(comp['match_format'] == 'T20') & (~comp['comp_name'].str.contains('IPL', case=False, na=False))]['comp_id'].tolist()
    log_and_assert(len(ipl_comps) == 5, f"Identified 5 IPL seasons (comp_ids={ipl_comps}).", "Unexpected IPL competition count")
    log_and_assert(len(t20i_comps) == 134, f"Identified 134 T20I competitions.", "Unexpected T20I competition count")
    log_and_assert(unrelated_comps == [2670, 3289], f"Identified exactly 2 unrelated non-IPL/non-T20I competitions (comp_ids={unrelated_comps}).", "Unexpected unrelated competitions")

    logging.info("==================================================")
    logging.info("ALL PHASE 0 VALIDATION TESTS PASSED WITH 100% SUCCESS!")
    logging.info("==================================================")

if __name__ == '__main__':
    run_phase0_validation()
