import os
import pandas as pd
import numpy as np

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"

def inspect_other_and_balls():
    bbb_df = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)

    print("Checking deliveries per over across complete overs:")
    
    # Check 'other' extras_type
    other_df = bbb_df[bbb_df['extras_type'] == 'other']
    print(f"Total 'other' rows: {len(other_df)}")
    print("Runs breakdown for 'other':")
    print(other_df['runs'].value_counts())
    print("extras1_runs for 'other':")
    print(other_df['extras1_runs'].value_counts())
    print("extras_2_runs for 'other':")
    print(other_df['extras_2_runs'].value_counts())
    print("is_wicket for 'other':")
    print(other_df['is_wicket'].value_counts())
    print("dismissal_type for 'other':")
    print(other_df['dismissal_type'].value_counts())

    # In cricket, no-balls can be:
    # 1) Overstep (front foot)
    # 2) Other no-balls: above waist full toss (beamer), fielding restriction violation, bowler breaking stumps, etc.
    # Notice that for 'other', extras1_runs is ALWAYS 1 (264 out of 264)!
    # And the batter can score runs off it (runs: 0, 1, 2, 4, 6)!
    # And dismissal_type is RunOut! (Batters cannot be bowled, caught, or LBW off a no-ball, only RunOut!)
    # That is the exact rule of cricket for a NO-BALL!
    # Therefore, 'other' is indeed a No-Ball (non-overstep no-ball)!

    # Now let's check:
    # What are the total runs conceded on a ball?
    # Runs to batting team = runs (batter runs) + extras1_runs + extras_2_runs
    print("\nTotal runs calculation check:")
    print("Sample with wide:")
    print(bbb_df[bbb_df['extras_type'] == 'wide'][['runs', 'extras1_runs', 'extras_2_runs']].head(5))
    print("\nSample with Overstep:")
    print(bbb_df[bbb_df['extras_type'] == 'Overstep'][['runs', 'extras1_runs', 'extras_2_runs']].head(5))
    print("\nSample with legbyes:")
    print(bbb_df[bbb_df['extras_type'] == 'legbyes'][['runs', 'extras1_runs', 'extras_2_runs']].head(5))
    print("\nSample with byes:")
    print(bbb_df[bbb_df['extras_type'] == 'byes'][['runs', 'extras1_runs', 'extras_2_runs']].head(5))

    # What about bowler-charged runs?
    # In official cricket rules:
    # Bowler is charged for:
    # - batter runs (runs)
    # - wides (extras1_runs when extras_type == 'wide')
    # - no-balls (extras1_runs when extras_type in ['Overstep', 'other'])
    # Bowler is NOT charged for:
    # - byes
    # - leg byes
    # - penalty runs
    # What about extras_2_runs? When does extras_2_runs occur?
    print("\nAll rows where extras_2_runs > 0:")
    e2_df = bbb_df[bbb_df['extras_2_runs'] > 0]
    print(e2_df[['runs', 'extras_type', 'extras1_runs', 'extras_2_runs', 'is_four', 'is_six']].to_string())

if __name__ == '__main__':
    inspect_other_and_balls()
