import os
import json
import pandas as pd
import numpy as np

DATA_DIR = r"6af458274c1e8_data_pack\Data Pack"

files = [
    "competitions.csv",
    "teams.csv",
    "matches.csv",
    "playing_eleven.csv",
    "competition_team_player_mapping.csv",
    "ball_by_ball.csv"
]

inventory = {}

print("=== STARTING DATASET INVENTORY ===")
for f in files:
    path = os.path.join(DATA_DIR, f)
    size_bytes = os.path.getsize(path)
    # read sample
    df_sample = pd.read_csv(path, nrows=5)
    print(f"\nFile: {f} ({size_bytes:,} bytes)")
    print(f"Columns ({len(df_sample.columns)}): {list(df_sample.columns)}")
    print("Sample row:")
    print(df_sample.iloc[0].to_dict())

