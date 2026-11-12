import pandas as pd
import numpy as np

df = pd.read_parquet("outputs/processed/processed_deliveries.parquet")
print(f"Total processed deliveries: {len(df):,}")

inn1 = df[df["innings"] == 1]
inn2 = df[df["innings"] == 2]

print(f"Innings 1 deliveries: {len(inn1):,}")
print(f"Innings 2 deliveries: {len(inn2):,}")

print("\n--- INNINGS 2: REQUIRED RUN RATE (RRR) DISTRIBUTION ---")
rrr = inn2["pre_delivery_required_run_rate"].dropna()
print(rrr.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.85, 0.9, 0.95, 0.99]))

print("\n--- INNINGS 2: RRR BY INNINGS STAGE ---")
for stage in ["Powerplay", "Middle", "Death"]:
    sub = inn2[inn2["innings_stage"] == stage]["pre_delivery_required_run_rate"].dropna()
    print(f"Stage {stage} (n={len(sub):,}): mean={sub.mean():.2f}, 50%={sub.median():.2f}, 75%={sub.quantile(0.75):.2f}, 90%={sub.quantile(0.9):.2f}, 95%={sub.quantile(0.95):.2f}")

print("\n--- WICKETS LOST BEFORE DELIVERY ---")
print("Innings 1 wickets lost distribution:")
print(inn1["pre_delivery_wickets"].value_counts(normalize=True).sort_index().round(4))
print("\nInnings 2 wickets lost distribution:")
print(inn2["pre_delivery_wickets"].value_counts(normalize=True).sort_index().round(4))

print("\n--- INNINGS 1: RUN RATE AND SCORING BY OVER ---")
# Empirical run rate baseline per over in innings 1
ov_stats = inn1.groupby("overid").agg(
    balls=("runs", "count"),
    avg_score=("pre_delivery_runs", "mean"),
    avg_crr=("pre_delivery_current_run_rate", "mean"),
    avg_wkts=("pre_delivery_wickets", "mean")
).round(2)
print(ov_stats)

print("\n--- INNINGS 1: HISTORICAL RUN EXPECTANCY MATRIX (Overs remaining vs Wickets lost) ---")
# Let's inspect final innings 1 totals across matches
inn1_finals = inn1.groupby("match_id").agg(
    final_score=("pre_delivery_runs", "last"),
    final_ball_runs=("delivery_total_runs", "last")
)
inn1_finals["total_score"] = inn1_finals["final_score"] + inn1_finals["final_ball_runs"]

# Merge final score back to inn1 to calculate actual runs added from match state
inn1_merged = inn1[["match_id", "overid", "pre_delivery_wickets", "pre_delivery_runs"]].merge(
    inn1_finals[["total_score"]], on="match_id"
)
inn1_merged["runs_added_to_end"] = inn1_merged["total_score"] - inn1_merged["pre_delivery_runs"]

# Average expected runs added by (overid, wickets)
re_matrix = inn1_merged.groupby(["overid", "pre_delivery_wickets"])["runs_added_to_end"].agg(["count", "mean"]).round(1)
print("Sample run expectancy for over 6 (end of powerplay) by wickets down:")
if 6 in re_matrix.index.levels[0]:
    print(re_matrix.loc[6])

print("\nSample run expectancy for over 15 (end of middle overs) by wickets down:")
if 15 in re_matrix.index.levels[0]:
    print(re_matrix.loc[15])
