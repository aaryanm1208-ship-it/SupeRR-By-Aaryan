import pandas as pd
import numpy as np

deliv = pd.read_parquet("outputs/processed/pressure_deliveries_model_c.parquet")
print(f"Loaded {len(deliv):,} deliveries.")

# Filter to pressure deliveries for batters (HIGH and EXTREME)
# Check balls faced
pressure_mask = deliv["batter_pressure_tier"].isin(["HIGH", "EXTREME"])
p_deliv = deliv[pressure_mask]
print(f"Total pressure deliveries for batters: {len(p_deliv):,} ({len(p_deliv)/len(deliv)*100:.1f}%)")

# Group by striker_id
batter_exp = deliv.groupby("striker_id").agg(
    total_balls=("is_ball_faced", "sum"),
    total_matches=("match_id", "nunique"),
    pressure_balls=("is_ball_faced", lambda s: (s & pressure_mask.loc[s.index]).sum()),
    pressure_matches=("match_id", lambda s: deliv.loc[s.index].loc[pressure_mask.loc[s.index], "match_id"].nunique())
).reset_index()

print("\n--- BATTER PRESSURE BALLS DISTRIBUTION ---")
print(batter_exp["pressure_balls"].describe(percentiles=[0.5, 0.75, 0.85, 0.9, 0.95, 0.98]))

print("\nBatters with >= 50 pressure balls:", (batter_exp["pressure_balls"] >= 50).sum())
print("Batters with >= 75 pressure balls:", (batter_exp["pressure_balls"] >= 75).sum())
print("Batters with >= 100 pressure balls:", (batter_exp["pressure_balls"] >= 100).sum())
print("Batters with >= 120 pressure balls:", (batter_exp["pressure_balls"] >= 120).sum())
print("Batters with >= 150 pressure balls:", (batter_exp["pressure_balls"] >= 150).sum())

# Let's inspect top 20 batters by pressure balls faced
ctp = pd.read_csv("6af458274c1e8_data_pack/Data Pack/competition_team_player_mapping.csv")
name_map = ctp.groupby("player_id")["player_name"].first().to_dict()
batter_exp["player_name"] = batter_exp["striker_id"].map(name_map)
print("\nTop 20 batters by pressure balls faced:")
print(batter_exp.sort_values(by="pressure_balls", ascending=False)[["striker_id", "player_name", "total_balls", "pressure_balls", "pressure_matches"]].head(20).to_string())

