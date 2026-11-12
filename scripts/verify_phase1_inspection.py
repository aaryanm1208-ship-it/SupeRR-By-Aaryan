import pandas as pd
import numpy as np

# Load Phase 1 outputs and Phase 0 raw files
comp_df = pd.read_csv("6af458274c1e8_data_pack/Data Pack/competitions.csv")
matches_df = pd.read_parquet("outputs/processed/processed_matches.parquet")
deliv_df = pd.read_parquet("outputs/processed/processed_deliveries.parquet")
comp_audit = pd.read_csv("outputs/reports/competition_audit.csv")

print("=== QUESTION 1 & 2: COMPETITION GENDER & SENIOR STATUS ===")
print("Comp names containing women / women's / ICC Women / U19:")
women_comps = comp_df[comp_df["comp_name"].str.contains("women|u19|under-19|girls", case=False, na=False)]
print(f"Count of women / youth competitions in raw competitions.csv: {len(women_comps)}")
if len(women_comps) > 0:
    print(women_comps[["comp_id", "comp_name", "match_format", "season"]])

# Let's inspect unique competition names in retained competitions
retained_comp_ids = set(matches_df["comp_id"].unique())
retained_comps_meta = comp_df[comp_df["comp_id"].isin(retained_comp_ids)]
print("\nRetained competition formats:", retained_comps_meta["match_format"].value_counts())
print("Retained competitions count:", len(retained_comps_meta))
print("Sample retained competition names:")
print(retained_comps_meta["comp_name"].head(15))

print("\n=== QUESTION 3: PENALTY EVENT TREATMENT ===")
pen_delivs = deliv_df[deliv_df["extras_type"] == "Penalty"]
print(f"Penalty events in processed deliveries: {len(pen_delivs)}")
if len(pen_delivs) > 0:
    cols = ["match_id", "innings", "overid", "over_ball_num", "runs", "extras1_runs", "extras_2_runs", 
            "delivery_total_runs", "bowler_charged_runs", "is_legal_delivery", "is_ball_faced"]
    print(pen_delivs[cols])

print("\n=== QUESTION 4: COMPLETE DISMISSAL VOCABULARY ===")
print("Dismissal type value counts in processed deliveries:")
print(deliv_df["dismissal_type"].value_counts(dropna=False))
print("\nCross-tab of dismissal_type vs is_bowler_wicket and is_non_bowler_dismissal:")
print(pd.crosstab(
    deliv_df["dismissal_type"].fillna("None"), 
    [deliv_df["is_bowler_wicket"], deliv_df["is_non_bowler_dismissal"]]
))

print("\n=== QUESTION 5 & 6: REVISED TARGETS & INNINGS LENGTHS ===")
rev_matches = matches_df[matches_df["revised_target"].notna() | matches_df["second_inn_revised_overs"].notna()]
print(f"Retained matches with revised targets / overs: {len(rev_matches)}")
sample_rev = rev_matches.iloc[0]
sample_m_id = sample_rev["match_id"]
sample_m_deliv = deliv_df[deliv_df["match_id"] == sample_m_id]
print(f"Sample match {sample_m_id}: revised_target = {sample_rev['revised_target']}, revised_overs = ({sample_rev['first_inn_revised_overs']}, {sample_rev['second_inn_revised_overs']})")
print("Target values in innings 1:", sample_m_deliv[sample_m_deliv["innings"] == 1]["target"].unique())
print("Target values in innings 2:", sample_m_deliv[sample_m_deliv["innings"] == 2]["target"].unique())
print("Scheduled balls in innings 1:", sample_m_deliv[sample_m_deliv["innings"] == 1]["innings_scheduled_legal_balls"].unique())
print("Scheduled balls in innings 2:", sample_m_deliv[sample_m_deliv["innings"] == 2]["innings_scheduled_legal_balls"].unique())

print("\n=== QUESTION 7: SUPER OVER EXCLUSION ===")
print("Innings values in processed_deliveries.parquet:", deliv_df["innings"].unique())

print("\n=== QUESTION 8: INCOMPLETE & ABANDONED MATCHES ===")
ab_matches = matches_df[matches_df["result"] == "Match Abandoned"]
print(f"Total abandoned matches in retained matches: {len(ab_matches)}")
deliv_mids = set(deliv_df["match_id"].unique())
print(f"Abandoned matches with 0 deliveries: {len(ab_matches[~ab_matches['match_id'].isin(deliv_mids)])}")
print(f"Abandoned matches with partial play: {len(ab_matches[ab_matches['match_id'].isin(deliv_mids)])}")

