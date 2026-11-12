import os
import pandas as pd

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"

def inspect_details():
    matches_df = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
    comp_df = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
    bbb_df = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)

    # 1. Match count per competition
    match_comp = matches_df.merge(comp_df, on='comp_id', how='left')
    print("Matches by match_format:")
    print(match_comp['match_format'].value_counts(dropna=False))

    print("\nMatches in non-T20I T20 competitions:")
    t20_matches = match_comp[match_comp['match_format'] == 'T20']
    print(t20_matches.groupby(['comp_id', 'comp_name', 'season'])['match_id'].count())

    # 2. Check match_ids in matches.csv vs ball_by_ball.csv
    matches_in_m = set(matches_df['match_id'])
    matches_in_bbb = set(bbb_df['match_id'])
    print(f"\nTotal matches in matches.csv: {len(matches_in_m)}")
    print(f"Total matches in ball_by_ball.csv: {len(matches_in_bbb)}")
    print(f"Matches in matches.csv but NOT in ball_by_ball.csv: {len(matches_in_m - matches_in_bbb)}")
    missing_bbb_matches = matches_df[matches_df['match_id'].isin(matches_in_m - matches_in_bbb)]
    print("Results of matches missing in ball_by_ball:")
    print(missing_bbb_matches['result'].value_counts(dropna=False))

    # 3. Check what 'other' extras_type is
    print("\nDetailed look at extras_type == 'other':")
    other_extras = bbb_df[bbb_df['extras_type'] == 'other']
    print(other_extras[['runs', 'extras_type', 'extras1_runs', 'extras_2_runs', 'is_wicket', 'dismissal_type']].head(10))
    print("extras1_runs value counts for 'other':")
    print(other_extras['extras1_runs'].value_counts())
    print("extras_2_runs value counts for 'other':")
    print(other_extras['extras_2_runs'].value_counts())

    # 4. Check what legal deliveries are:
    # When is a ball legal? Wide is illegal, Overstep (no ball) is illegal.
    # What about 'other'? Is 'other' a no-ball or what?
    # Let's check over_ball_num progression within an over!
    print("\nSample overs with extras:")
    sample_over = bbb_df[(bbb_df['match_id'] == 13511) & (bbb_df['innings'] == 1) & (bbb_df['overid'] == 1)]
    print(sample_over[['overid', 'over_ball_num', 'innings_ball_num', 'runs', 'extras_type', 'extras1_runs', 'extras_2_runs']])

    # Let's inspect an over with a wide
    wide_rows = bbb_df[bbb_df['extras_type'] == 'wide'].head(2)
    for idx, r in wide_rows.iterrows():
        m_id, inn, ov = r['match_id'], r['innings'], r['overid']
        ov_df = bbb_df[(bbb_df['match_id'] == m_id) & (bbb_df['innings'] == inn) & (bbb_df['overid'] == ov)]
        print(f"\nOver with wide (match {m_id}, inn {inn}, over {ov}):")
        print(ov_df[['overid', 'over_ball_num', 'innings_ball_num', 'striker_name', 'bowler_name', 'runs', 'extras_type', 'extras1_runs', 'extras_2_runs', 'is_wicket']])

    # Let's inspect an over with 'other'
    other_rows = bbb_df[bbb_df['extras_type'] == 'other'].head(2)
    for idx, r in other_rows.iterrows():
        m_id, inn, ov = r['match_id'], r['innings'], r['overid']
        ov_df = bbb_df[(bbb_df['match_id'] == m_id) & (bbb_df['innings'] == inn) & (bbb_df['overid'] == ov)]
        print(f"\nOver with 'other' (match {m_id}, inn {inn}, over {ov}):")
        print(ov_df[['overid', 'over_ball_num', 'innings_ball_num', 'striker_name', 'bowler_name', 'runs', 'extras_type', 'extras1_runs', 'extras_2_runs', 'is_wicket']])

if __name__ == '__main__':
    inspect_details()
