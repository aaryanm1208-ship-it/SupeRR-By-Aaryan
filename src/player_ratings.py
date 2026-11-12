"""
Composite Player Rating and Final Ranking Engine.
SupeRR Selector Season 2 — Elite Pressure Performance Intelligence System.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional
from src import config


def min_max_normalize(series: pd.Series, invert: bool = False, vmin: Optional[float] = None, vmax: Optional[float] = None) -> pd.Series:
    """Normalizes a series to 0-100 scale, with optional inversion."""
    s = series.astype(float)
    if vmin is None:
        vmin = s.min()
    if vmax is None:
        vmax = s.max()
    if vmax == vmin:
        return pd.Series(50.0, index=s.index)
    clipped = np.clip(s, vmin, vmax)
    res = (clipped - vmin) / (vmax - vmin) * 100.0
    return 100.0 - res if invert else res


def compute_batter_composite_ratings(
    eligible_batters: pd.DataFrame,
    df_deliveries: pd.DataFrame
) -> pd.DataFrame:
    """
    Computes multi-dimensional batting pressure composite score (0-100 scale) for eligible batters.
    
    Dimensions:
      1. Absolute Pressure Scoring Efficiency (35%):
         - Empirical Bayes Shrunk Pressure Strike Rate (70%)
         - Empirical Bayes Shrunk Runs Per Dismissal (30%)
      2. Clutch Value-Add / Elevation over Baseline (25%):
         - Strike Rate Delta (60%)
         - Boundary % Delta (20%)
         - Dot % Suppression (20%)
      3. Match-Level Consistency & Reliability (20%):
         - Positive Impact Match Percentage (70%)
         - Inverted Match Strike Rate Standard Deviation (30%)
      4. Sample Volume & Exposure Robustness (10%):
         - Log Pressure Balls Faced (60%)
         - Log Pressure Matches (40%)
      5. Contextual Difficulty & Phase Exposure (10%):
         - Proportion of Pressure Balls in Death Overs (50%)
         - Proportion of Pressure Balls in IPL (50%)
    """
    b = eligible_batters.copy()

    # Contextual percentages
    b["death_pressure_pct"] = np.where(b["pressure_balls"] > 0, (b["death_pressure_balls"] / b["pressure_balls"]) * 100.0, 0.0)
    b["ipl_pressure_pct"] = np.where(b["pressure_balls"] > 0, (b["ipl_pressure_balls"] / b["pressure_balls"]) * 100.0, 0.0)

    # 1. Absolute Pressure Scoring Efficiency (35%)
    # Elite benchmarks: SR 120-195, RPD 18-50
    s_abs_sr = min_max_normalize(b["pressure_sr_eb"], vmin=120.0, vmax=195.0)
    s_abs_rpd = min_max_normalize(b["pressure_rpd_eb"], vmin=18.0, vmax=50.0)
    b["score_abs_efficiency"] = 0.70 * s_abs_sr + 0.30 * s_abs_rpd

    # 2. Clutch Value-Add / Elevation (25%)
    s_clutch_sr = min_max_normalize(b["sr_delta"], vmin=-15.0, vmax=55.0)
    s_clutch_bp = min_max_normalize(b["boundary_pct_delta"], vmin=-5.0, vmax=15.0)
    s_clutch_dp = min_max_normalize(-b["dot_pct_delta"], vmin=-15.0, vmax=15.0)
    b["score_clutch_value"] = 0.60 * s_clutch_sr + 0.20 * s_clutch_bp + 0.20 * s_clutch_dp

    # 3. Match Consistency (20%)
    s_cons_rate = min_max_normalize(b["positive_contribution_pct"], vmin=20.0, vmax=80.0)
    s_cons_std = min_max_normalize(b["match_sr_std"], invert=True, vmin=35.0, vmax=110.0)
    b["score_consistency"] = 0.70 * s_cons_rate + 0.30 * s_cons_std

    # 4. Sample Volume (10%)
    s_vol_balls = min_max_normalize(np.log(b["pressure_balls"]), vmin=np.log(75), vmax=np.log(400))
    s_vol_matches = min_max_normalize(np.log(b["pressure_matches"]), vmin=np.log(10), vmax=np.log(45))
    b["score_sample_volume"] = 0.60 * s_vol_balls + 0.40 * s_vol_matches

    # 5. Context Difficulty (10%)
    s_ctx_death = min_max_normalize(b["death_pressure_pct"], vmin=20.0, vmax=90.0)
    s_ctx_ipl = min_max_normalize(b["ipl_pressure_pct"], vmin=0.0, vmax=100.0)
    b["score_context_difficulty"] = 0.50 * s_ctx_death + 0.50 * s_ctx_ipl

    # Composite Batting Rating
    b["composite_rating"] = (
        0.35 * b["score_abs_efficiency"] +
        0.25 * b["score_clutch_value"] +
        0.20 * b["score_consistency"] +
        0.10 * b["score_sample_volume"] +
        0.10 * b["score_context_difficulty"]
    )

    b["rank"] = b["composite_rating"].rank(ascending=False, method="min").astype(int)
    b = b.sort_values(by="rank", ascending=True).reset_index(drop=True)
    return b


def compute_bowler_composite_ratings(
    eligible_bowlers: pd.DataFrame,
    df_deliveries: pd.DataFrame
) -> pd.DataFrame:
    """
    Computes multi-dimensional bowling pressure composite score (0-100 scale) for eligible bowlers.
    Incorporates Phase-Adjusted Economy Rate (Runs Saved Above Average per Over) to account
    for phase difficulty (death overs vs middle overs).
    
    Dimensions:
      1. Phase-Adjusted Run Suppression (35%):
         - Runs Saved Above Average per Over (50%)
         - Phase-Adjusted Economy (25%)
         - Dot Ball % (25%)
      2. Wicket Threat & Strike Capability (25%):
         - Shrunk Wickets per Over (60%)
         - Balls per Wicket / Strike Rate (40%)
      3. Boundary Suppression & Quality Spells (15%):
         - Inverted Boundary % Conceded (50%)
         - Clutch Spell Rate (% matches <= 7.50 econ or >= 2 wkts) (50%)
      4. Match-Level Consistency (10%):
         - Inverted Match Economy Standard Deviation (100%)
      5. Sample Volume & Proven Breadth (15%):
         - Log Legal Balls (50%)
         - Log Matches (30%)
         - IPL Tournament Exposure % (20%)
    """
    bw = eligible_bowlers.copy()

    # Compute phase par economy from deliveries
    b_press = df_deliveries[(df_deliveries["is_legal_delivery"] == True) & (df_deliveries["bowler_pressure_tier"].isin(["HIGH", "EXTREME"]))].copy()
    stage_par = {}
    for s, g in b_press.groupby("innings_stage"):
        stage_par[s.lower()] = float(g["bowler_charged_runs"].sum() / (len(g) / 6.0))

    # Phase-adjusted calculations
    bw["pp_overs"] = bw["powerplay_pressure_legal_balls"] / 6.0
    bw["mid_overs"] = bw["middle_pressure_legal_balls"] / 6.0
    bw["death_overs"] = bw["death_pressure_legal_balls"] / 6.0
    bw["death_pressure_pct"] = np.where(bw["pressure_legal_balls"] > 0, (bw["death_pressure_legal_balls"] / bw["pressure_legal_balls"]) * 100.0, 0.0)
    bw["ipl_pressure_pct"] = np.where(bw["pressure_legal_balls"] > 0, (bw["ipl_pressure_balls"] / bw["pressure_legal_balls"]) * 100.0, 0.0)

    bw["expected_runs"] = (
        bw["pp_overs"] * stage_par.get("powerplay", 8.46) +
        bw["mid_overs"] * stage_par.get("middle", 8.01) +
        bw["death_overs"] * stage_par.get("death", 10.46)
    )
    bw["runs_saved"] = bw["expected_runs"] - bw["pressure_runs_conceded"]
    bw["runs_saved_per_over"] = bw["runs_saved"] / np.maximum(bw["pressure_overs"], 0.1)
    bw["phase_adj_econ"] = 8.65 - bw["runs_saved_per_over"]

    # 1. Phase-Adjusted Run Suppression (35%)
    s_abs_rsaa = min_max_normalize(bw["runs_saved_per_over"], vmin=-1.0, vmax=2.5)
    s_abs_econ = min_max_normalize(bw["phase_adj_econ"], invert=True, vmin=6.2, vmax=9.8)
    s_abs_dot = min_max_normalize(bw["pressure_dot_pct"], vmin=25.0, vmax=45.0)
    s_abs = 0.50 * s_abs_rsaa + 0.25 * s_abs_econ + 0.25 * s_abs_dot

    # 2. Wicket Threat & Strike Capability (25%)
    s_wkt_rate = min_max_normalize(bw["pressure_wkt_per_over_eb"], vmin=0.15, vmax=0.60)
    s_wkt_sr = min_max_normalize(bw["pressure_sr"].fillna(45.0), invert=True, vmin=10.0, vmax=35.0)
    s_wkt = 0.60 * s_wkt_rate + 0.40 * s_wkt_sr

    # 3. Boundary Suppression & Quality Spells (15%)
    s_bp_supp = min_max_normalize(bw["pressure_boundary_pct"], invert=True, vmin=8.0, vmax=24.0)
    s_clutch_spells = min_max_normalize(bw["clutch_spell_pct"], vmin=25.0, vmax=80.0)
    s_clutch = 0.50 * s_bp_supp + 0.50 * s_clutch_spells

    # 4. Match Consistency (10%)
    s_cons_std = min_max_normalize(bw["match_econ_std"], invert=True, vmin=2.0, vmax=6.5)
    s_cons = s_cons_std

    # 5. Sample Volume & Tournament Breadth (15%)
    s_vol_balls = min_max_normalize(np.log(bw["pressure_legal_balls"]), vmin=np.log(90), vmax=np.log(1000))
    s_vol_matches = min_max_normalize(np.log(bw["pressure_matches"]), vmin=np.log(10), vmax=np.log(60))
    s_vol_ipl = min_max_normalize(bw["ipl_pressure_pct"], vmin=0.0, vmax=100.0)
    s_vol = 0.50 * s_vol_balls + 0.30 * s_vol_matches + 0.20 * s_vol_ipl

    bw["score_abs_suppression"] = s_abs
    bw["score_wicket_threat"] = s_wkt
    bw["score_boundary_suppression"] = s_clutch
    bw["score_consistency"] = s_cons
    bw["score_sample_volume"] = s_vol

    # Composite Bowling Rating
    bw["composite_rating"] = (
        0.35 * s_abs +
        0.25 * s_wkt +
        0.15 * s_clutch +
        0.10 * s_cons +
        0.15 * s_vol
    )

    bw["rank"] = bw["composite_rating"].rank(ascending=False, method="min").astype(int)
    bw = bw.sort_values(by="rank", ascending=True).reset_index(drop=True)
    return bw


def generate_player_explanations(
    top_batters: pd.DataFrame,
    top_bowlers: pd.DataFrame
) -> pd.DataFrame:
    """
    Generates analytical justification narratives for each Top 10 batter and bowler.
    """
    explanations = []

    # Batters
    for _, row in top_batters.head(10).iterrows():
        rank = row["rank"]
        name = row["striker_canonical_name"]
        pid = row["striker_id"]
        balls = int(row["pressure_balls"])
        matches = int(row["pressure_matches"])
        sr = row["pressure_sr"]
        sr_eb = row["pressure_sr_eb"]
        norm_sr = row["normal_sr"]
        sr_delta = row["sr_delta"]
        rpd = row["pressure_rpd"]
        rpd_eb = row["pressure_rpd_eb"]
        cons_pct = row["positive_contribution_pct"]
        rating = row["composite_rating"]
        ci_low = row["boot_sr_ci_lower"]
        ci_high = row["boot_sr_ci_upper"]

        role = "Middle-to-Death Finisher" if row.get("death_pressure_pct", 0) > 40 else "Anchor-Aggressor / Middle Overs"

        narrative = (
            f"Rank {rank} ({name}): Dominant pressure performer scoring {sr:.1f} SR (EB shrunk: {sr_eb:.1f}) "
            f"across {balls} pressure balls in {matches} matches. Elevates scoring rate by {sr_delta:+.1f} SR "
            f"above baseline ({norm_sr:.1f} normal SR) while maintaining a prolific average of {rpd:.1f} runs per dismissal "
            f"(EB shrunk: {rpd_eb:.1f}). Delivers positive high-impact contributions in {cons_pct:.1f}% of pressure matches "
            f"with a rigorous 95% bootstrap CI of [{ci_low:.1f}, {ci_high:.1f}] SR."
        )

        explanations.append({
            "category": "BATTER",
            "rank": rank,
            "player_id": pid,
            "player_name": name,
            "composite_rating": round(float(rating), 2),
            "tactical_role": role,
            "sample_exposure": f"{balls} balls ({matches} matches)",
            "primary_metric": f"{sr:.1f} SR (EB: {sr_eb:.1f})",
            "clutch_elevation": f"{sr_delta:+.1f} SR delta",
            "reliability_metric": f"{rpd:.1f} RPD | {cons_pct:.1f}% impact rate",
            "statistical_justification": narrative
        })

    # Bowlers
    for _, row in top_bowlers.head(10).iterrows():
        rank = row["rank"]
        name = row["bowler_canonical_name"]
        pid = row["bowler_id"]
        balls = int(row["pressure_legal_balls"])
        matches = int(row["pressure_matches"])
        econ = row["pressure_econ"]
        econ_eb = row["pressure_econ_eb"]
        norm_econ = row["normal_econ"]
        econ_delta = row["econ_delta"]
        phase_adj = row["phase_adj_econ"]
        rsaa = row["runs_saved_per_over"]
        wkts = int(row["pressure_wickets"])
        cons_pct = row["clutch_spell_pct"]
        rating = row["composite_rating"]
        ci_low = row["boot_econ_ci_lower"]
        ci_high = row["boot_econ_ci_upper"]

        role = "Death Overs Specialist / Enforcer" if row.get("death_pressure_pct", 0) > 40 else "High-Leverage Control & Mystery Spinner"

        narrative = (
            f"Rank {rank} ({name}): Elite pressure bowler conceding only {econ:.2f} rpo (EB shrunk: {econ_eb:.2f}, "
            f"phase-adjusted: {phase_adj:.2f}) across {balls} pressure legal deliveries in {matches} matches. "
            f"Saves {rsaa:+.2f} runs per over above phase expectation while taking {wkts} pressure wickets. "
            f"Delivers clutch spells in {cons_pct:.1f}% of pressure matches with a 95% bootstrap CI of "
            f"[{ci_low:.2f}, {ci_high:.2f}] economy."
        )

        explanations.append({
            "category": "BOWLER",
            "rank": rank,
            "player_id": pid,
            "player_name": name,
            "composite_rating": round(float(rating), 2),
            "tactical_role": role,
            "sample_exposure": f"{balls} balls ({matches} matches)",
            "primary_metric": f"{econ:.2f} Econ (EB: {econ_eb:.2f}, Adj: {phase_adj:.2f})",
            "clutch_elevation": f"{rsaa:+.2f} runs saved/ov | {econ_delta:+.2f} delta",
            "reliability_metric": f"{wkts} wickets | {cons_pct:.1f}% clutch spells",
            "statistical_justification": narrative
        })

    return pd.DataFrame(explanations)

