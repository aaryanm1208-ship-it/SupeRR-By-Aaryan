import os
import pandas as pd

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"

def check_delivery_ordering():
    bbb_df = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)

    print("Checking chronological ordering in ball_by_ball.csv:")
    # Check if innings_ball_num is strictly increasing per match_id and innings
    grouped = bbb_df.groupby(['match_id', 'innings'])
    
    non_monotonic_ibn = 0
    non_monotonic_over = 0
    total_innings = len(grouped)

    for (m_id, inn), grp in grouped:
        ibn = grp['innings_ball_num'].values
        if not (np.diff(ibn) > 0).all():
            non_monotonic_ibn += 1
        # Check (overid, over_ball_num)
        ov = grp['overid'].values
        obn = grp['over_ball_num'].values
        # (ov * 100 + obn)
        ov_tuple = ov * 100 + obn
        if not (np.diff(ov_tuple) > 0).all():
            non_monotonic_over += 1

    print(f"Total innings: {total_innings}")
    print(f"Innings with non-monotonic innings_ball_num: {non_monotonic_ibn}")
    print(f"Innings with non-monotonic (overid, over_ball_num): {non_monotonic_over}")

if __name__ == '__main__':
    import numpy as np
    check_delivery_ordering()
