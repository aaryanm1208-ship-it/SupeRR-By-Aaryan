import os
import pandas as pd
import numpy as np

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"

def inspect_bbb_and_t20():
    comp_df = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
    t20_comps = comp_df[comp_df['match_format'] == 'T20']
    print("All T20 competitions in competitions.csv:")
    print(t20_comps)

    print("\nLoading ball_by_ball.csv sample & basic stats...")
    # Read first 100,000 rows or full dataframe to check unique values
    # Let's inspect data types and nulls
    bbb_df = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)
    print(f"ball_by_ball shape: {bbb_df.shape}")
    print(f"Unique match_id in ball_by_ball: {bbb_df['match_id'].nunique()}")
    print("\nInnings value counts:")
    print(bbb_df['innings'].value_counts().sort_index())
    
    print("\nOverid min and max:")
    print(f"min: {bbb_df['overid'].min()}, max: {bbb_df['overid'].max()}")
    print("over_ball_num min and max:")
    print(f"min: {bbb_df['over_ball_num'].min()}, max: {bbb_df['over_ball_num'].max()}")
    print("innings_ball_num min and max:")
    print(f"min: {bbb_df['innings_ball_num'].min()}, max: {bbb_df['innings_ball_num'].max()}")

    print("\nruns value counts:")
    print(bbb_df['runs'].value_counts().sort_index())

    print("\nextras_type value counts:")
    print(bbb_df['extras_type'].value_counts(dropna=False))

    print("\nextras1_runs value counts:")
    print(bbb_df['extras1_runs'].value_counts(dropna=False))

    print("\nextras_2_runs value counts:")
    print(bbb_df['extras_2_runs'].value_counts(dropna=False))

    print("\nis_wicket value counts:")
    print(bbb_df['is_wicket'].value_counts(dropna=False))

    print("\ndismissal_type value counts:")
    print(bbb_df['dismissal_type'].value_counts(dropna=False))

    print("\nDismissal type vs is_wicket:")
    print(pd.crosstab(bbb_df['dismissal_type'].fillna('None'), bbb_df['is_wicket']))

    # Let's understand how runs, extras, and extras_type interact
    print("\nSample records for each extras_type:")
    for et in bbb_df['extras_type'].dropna().unique():
        sample = bbb_df[bbb_df['extras_type'] == et][['runs', 'extras_type', 'extras1_runs', 'extras_2_runs', 'is_wicket']].head(3)
        print(f"Extras type: {et}")
        print(sample)

if __name__ == '__main__':
    inspect_bbb_and_t20()
