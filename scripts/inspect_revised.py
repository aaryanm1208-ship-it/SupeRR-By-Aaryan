import os
import pandas as pd

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"

def inspect_revised_matches():
    matches_df = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
    bbb_df = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)

    rev_matches = matches_df[matches_df['revised_target'].notnull() | matches_df['first_inn_revised_overs'].notnull() | matches_df['second_inn_revised_overs'].notnull()]
    print(f"Total matches with revised fields: {len(rev_matches)}")
    print(rev_matches[['match_id', 'match_date', 'first_inn_revised_overs', 'second_inn_revised_overs', 'revised_target', 'result']].to_string())

    # Check 1st innings total runs in bbb for these matches vs revised target
    for idx, r in rev_matches.iterrows():
        m_id = r['match_id']
        m_bbb = bbb_df[bbb_df['match_id'] == m_id]
        if len(m_bbb) > 0:
            inn1 = m_bbb[m_bbb['innings'] == 1]
            inn2 = m_bbb[m_bbb['innings'] == 2]
            # total runs in inn 1: runs + extras1_runs + extras_2_runs
            tot_runs_1 = (inn1['runs'] + inn1['extras1_runs'] + inn1['extras_2_runs']).sum()
            tot_runs_2 = (inn2['runs'] + inn2['extras1_runs'] + inn2['extras_2_runs']).sum() if len(inn2) > 0 else 0
            max_ov_1 = inn1['overid'].max() if len(inn1) > 0 else 0
            max_ov_2 = inn2['overid'].max() if len(inn2) > 0 else 0
            print(f"Match {m_id}: Inn1 runs={tot_runs_1} (overs={max_ov_1}), Inn2 runs={tot_runs_2} (overs={max_ov_2}), revised_target={r['revised_target']}, revised_overs=({r['first_inn_revised_overs']}, {r['second_inn_revised_overs']}), result='{r['result']}'")

if __name__ == '__main__':
    inspect_revised_matches()
