import os
import pandas as pd

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"

def investigate_extras_and_legals():
    bbb_df = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)

    print("Checking deliveries per over across complete overs:")
    # For overs with NO extras at all:
    clean_overs = bbb_df.groupby(['match_id', 'innings', 'overid']).filter(lambda x: x['extras_type'].isna().all())
    clean_counts = clean_overs.groupby(['match_id', 'innings', 'overid']).size()
    print("Clean overs ball counts (should all be 6):")
    print(clean_counts.value_counts())

    # Now let's see how many balls are in overs where extras_type has wide, Overstep, other, legbyes, byes
    print("\nFor each extras_type, what is the average / distribution of balls in the over?")
    for et in ['wide', 'Overstep', 'other', 'legbyes', 'byes', 'Penalty']:
        overs_with_et = bbb_df[bbb_df['extras_type'] == et][['match_id', 'innings', 'overid']].drop_duplicates()
        merged = bbb_df.merge(overs_with_et, on=['match_id', 'innings', 'overid'])
        # check number of balls in these overs
        counts = merged.groupby(['match_id', 'innings', 'overid']).size()
        print(f"\nOvers containing {et}: count of overs = {len(counts)}")
        print(counts.value_counts().head(5))

    # Let's check: does 'other' cause an over to have 7 balls?
    # Notice: 7 balls in an over with 1 'other' means 'other' did NOT count as a legal delivery!
    # Because in cricket, a normal over has 6 legal deliveries. If an over with 1 'other' and no other extras has 7 balls, then 'other' is an extra delivery (i.e., a no-ball)!
    other_only_overs = bbb_df.groupby(['match_id', 'innings', 'overid']).filter(
        lambda x: (x['extras_type'] == 'other').sum() == 1 and x['extras_type'].isin(['other', np.nan]).all()
    )
    other_counts = other_only_overs.groupby(['match_id', 'innings', 'overid']).size()
    print("\nOvers with EXACTLY ONE 'other' and no other extras:")
    print(other_counts.value_counts())

    # Let's check legbyes only overs:
    lb_only_overs = bbb_df.groupby(['match_id', 'innings', 'overid']).filter(
        lambda x: (x['extras_type'] == 'legbyes').sum() == 1 and x['extras_type'].isin(['legbyes', np.nan]).all()
    )
    lb_counts = lb_only_overs.groupby(['match_id', 'innings', 'overid']).size()
    print("\nOvers with EXACTLY ONE 'legbyes' and no other extras:")
    print(lb_counts.value_counts())

    # Let's check byes only overs:
    b_only_overs = bbb_df.groupby(['match_id', 'innings', 'overid']).filter(
        lambda x: (x['extras_type'] == 'byes').sum() == 1 and x['extras_type'].isin(['byes', np.nan]).all()
    )
    b_counts = b_only_overs.groupby(['match_id', 'innings', 'overid']).size()
    print("\nOvers with EXACTLY ONE 'byes' and no other extras:")
    print(b_counts.value_counts())

    # Let's check wide only overs:
    wide_only_overs = bbb_df.groupby(['match_id', 'innings', 'overid']).filter(
        lambda x: (x['extras_type'] == 'wide').sum() == 1 and x['extras_type'].isin(['wide', np.nan]).all()
    )
    wide_counts = wide_only_overs.groupby(['match_id', 'innings', 'overid']).size()
    print("\nOvers with EXACTLY ONE 'wide' and no other extras:")
    print(wide_counts.value_counts())

    # Let's check Overstep only overs:
    os_only_overs = bbb_df.groupby(['match_id', 'innings', 'overid']).filter(
        lambda x: (x['extras_type'] == 'Overstep').sum() == 1 and x['extras_type'].isin(['Overstep', np.nan]).all()
    )
    os_counts = os_only_overs.groupby(['match_id', 'innings', 'overid']).size()
    print("\nOvers with EXACTLY ONE 'Overstep' and no other extras:")
    print(os_counts.value_counts())

if __name__ == '__main__':
    investigate_extras_and_legals()
