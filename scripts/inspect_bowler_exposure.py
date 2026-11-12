import pandas as pd
import numpy as np

deliv = pd.read_parquet("outputs/processed/pressure_deliveries_model_c.parquet")

# Bowler pressure mask
p_mask_bowl = deliv["bowler_pressure_tier"].isin(["HIGH", "EXTREME"])
p_deliv_bowl = deliv[p_mask_bowl]
print(f"Total pressure deliveries for bowlers: {len(p_deliv_bowl):,} ({len(p_deliv_bowl)/len(deliv)*100:.1f}%)")

bowler_exp = deliv.groupby("bowler_id").agg(
    total_balls=("is_legal_delivery", "sum"),
    total_matches=("match_id", "nunique"),
    pressure_balls=("is_legal_delivery", lambda s: (s & p_mask_bowl.loc[s.index]).sum()),
    pressure_matches=("match_id", lambda s: deliv.loc[s.index].loc[p_mask_bowl.loc[s.index], "match_id"].nunique())
).reset_index()

print("\n--- BOWLER PRESSURE BALLS DISTRIBUTION ---")
print(bowler_exp["pressure_balls"].describe(percentiles=[0.5, 0.75, 0.85, 0.9, 0.95, 0.98]))

print("\nBowlers with >= 60 pressure balls:", (bowler_exp["pressure_balls"] >= 60).sum())
print("Bowlers with >= 90 pressure balls:", (bowler_exp["pressure_balls"] >= 90).sum())
print("Bowlers with >= 120 pressure balls:", (bowler_exp["pressure_balls"] >= 120).sum())
print("Bowlers with >= 150 pressure balls:", (bowler_exp["pressure_balls"] >= 150).sum())
print("Bowlers with >= 180 pressure balls:", (bowler_exp["pressure_balls"] >= 180).sum())

ctp = pd.read_csv("6af458274c1e8_data_pack/Data Pack/competition_team_player_mapping.csv")
name_map = ctp.groupby("player_id")["player_name"].first().to_dict()
bowler_exp["player_name"] = bowler_exp["bowler_id"].map(name_map)
print("\nTop 20 bowlers by pressure balls bowled:")
print(bowler_exp.sort_values(by="pressure_balls", ascending=False)[["bowler_id", "player_name", "total_balls", "pressure_balls", "pressure_matches"]].head(20).to_string())
