import os
import pandas as pd

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"

def check_player_integrity():
    ctp = pd.read_csv(os.path.join(DATA_DIR, "competition_team_player_mapping.csv"))
    bbb = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)
    pe = pd.read_csv(os.path.join(DATA_DIR, "playing_eleven.csv"))

    ctp_pids = set(ctp['player_id'].unique())
    pe_pids = set(pe['player_id'].unique())
    
    strikers = set(bbb['striker_id'].dropna().unique())
    non_strikers = set(bbb['non_striker_id'].dropna().unique())
    bowlers = set(bbb['bowler_id'].dropna().unique())
    dismissed = set(bbb['dismissed_player_id'].dropna().unique())

    all_bbb_pids = strikers | non_strikers | bowlers | dismissed

    print(f"Unique players in CTP mapping: {len(ctp_pids)}")
    print(f"Unique players in playing_eleven: {len(pe_pids)}")
    print(f"Unique players in ball_by_ball: {len(all_bbb_pids)}")
    print(f"  - Strikers: {len(strikers)}")
    print(f"  - Non-strikers: {len(non_strikers)}")
    print(f"  - Bowlers: {len(bowlers)}")
    print(f"  - Dismissed: {len(dismissed)}")

    missing_in_ctp = all_bbb_pids - ctp_pids
    print(f"Players in ball_by_ball missing from CTP mapping: {len(missing_in_ctp)}")
    if missing_in_ctp:
        print("Missing player IDs:", missing_in_ctp)
        # sample in bbb
        sample_missing = bbb[bbb['striker_id'].isin(missing_in_ctp) | bbb['bowler_id'].isin(missing_in_ctp)]
        print(sample_missing[['match_id', 'striker_id', 'striker_name', 'bowler_id', 'bowler_name']].head())

    # Check player name consistency in ball_by_ball vs CTP mapping
    id_to_name_ctp = ctp.groupby('player_id')['player_name'].first().to_dict()
    
    # Check striker name discrepancies
    striker_map = bbb.groupby('striker_id')['striker_name'].unique()
    discrepancies = []
    for pid, names in striker_map.items():
        ctp_name = id_to_name_ctp.get(pid, "NOT IN CTP")
        if len(names) > 1 or (len(names) == 1 and names[0] != ctp_name):
            discrepancies.append((pid, list(names), ctp_name))
            
    print(f"Total striker ID to name discrepancies between BBB and CTP: {len(discrepancies)}")
    if discrepancies:
        print("Sample discrepancies (first 5):")
        for d in discrepancies[:5]:
            print(f"PID {d[0]}: BBB names={d[1]}, CTP name='{d[2]}'")

if __name__ == '__main__':
    check_player_integrity()
