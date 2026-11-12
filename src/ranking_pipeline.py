"""
Ranking Pipeline Orchestrator for Phases 3, 4, and 5.
SupeRR Selector Season 2 — Elite Pressure Performance Intelligence System.
"""

import os
import pandas as pd
import numpy as np
from src import config
from src.batting_analysis import build_batter_performance_dataset
from src.bowling_analysis import build_bowler_performance_dataset
from src.player_ratings import compute_batter_composite_ratings, compute_bowler_composite_ratings, generate_player_explanations


def df_to_markdown(df: pd.DataFrame) -> str:
    """Simple robust markdown table generator without tabulate dependency."""
    headers = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in df.iterrows():
        formatted_vals = []
        for v in row:
            if isinstance(v, float):
                formatted_vals.append(f"{v:.2f}")
            else:
                formatted_vals.append(str(v))
        lines.append("| " + " | ".join(formatted_vals) + " |")
    return "\n".join(lines)


def run_ranking_pipeline():
    """Runs batting analysis, bowling analysis, ratings, and rankings generation."""
    print("=== EXECUTING PHASES 3, 4, & 5: PLAYER PERFORMANCE INTELLIGENCE & RANKINGS ===")
    
    # 1. Load Model C Pressure Deliveries
    pressure_path = os.path.join(config.PROCESSED_DIR, "pressure_deliveries_model_c.parquet")
    print(f"Loading pressure deliveries from: {pressure_path}")
    df_deliveries = pd.read_parquet(pressure_path)
    print(f"Loaded {len(df_deliveries):,} deliveries.")

    rankings_dir = os.path.join(config.OUTPUT_DIR, "rankings")

    # Create directories if needed
    os.makedirs(config.PROCESSED_DIR, exist_ok=True)
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    os.makedirs(rankings_dir, exist_ok=True)

    # 2. Phase 3: Batter Performance Intelligence
    print("\n[PHASE 3] Computing Batter Performance Metrics & Bootstrap Resampling...")
    eligible_batters, full_batter_metrics, batter_audit = build_batter_performance_dataset(
        df_deliveries,
        min_pressure_balls=75,
        min_pressure_matches=10,
        n_bootstrap=1000,
        random_seed=42
    )
    print(f"Total Batters Evaluated: {len(full_batter_metrics):,}")
    print(f"Eligible Batters (>=75 balls, >=10 matches): {len(eligible_batters):,}")

    # Save Phase 3 Artifacts
    full_batter_metrics.to_parquet(os.path.join(config.PROCESSED_DIR, "batter_metrics.parquet"), index=False)
    batter_audit.to_csv(os.path.join(config.REPORTS_DIR, "batter_eligibility_audit.csv"), index=False)

    # Provisional Batting Rankings (by shrunk strike rate)
    prov_batters = eligible_batters.sort_values(by="pressure_sr_eb", ascending=False).reset_index(drop=True)
    prov_batters["provisional_rank"] = prov_batters.index + 1
    prov_batters.to_csv(os.path.join(rankings_dir, "batter_rankings_provisional.csv"), index=False)

    # Batting Analysis Report
    with open(os.path.join(config.REPORTS_DIR, "batting_analysis_report.md"), "w", encoding="utf-8") as f:
        f.write("# Phase 3 Batting Performance Intelligence Report\n\n")
        f.write("## 1. Executive Summary\n")
        f.write(f"- Total unique batters evaluated: {len(full_batter_metrics):,}\n")
        f.write(f"- Eligible batters meeting sample thresholds (>= 75 pressure balls across >= 10 matches): {len(eligible_batters)}\n")
        f.write(f"- Total pressure balls faced by eligible cohort: {int(eligible_batters['pressure_balls'].sum()):,}\n")
        f.write(f"- Mean pressure strike rate across eligible cohort: {eligible_batters['pressure_sr'].mean():.2f}\n")
        f.write(f"- Mean baseline strike rate across eligible cohort: {eligible_batters['normal_sr'].mean():.2f}\n")
        f.write(f"- Mean clutch strike rate delta: {eligible_batters['sr_delta'].mean():+.2f}\n\n")
        f.write("## 2. Top 15 Eligible Batters by Empirical Bayes Shrunk Strike Rate\n\n")
        top15_b = prov_batters.head(15)[[
            "provisional_rank", "striker_canonical_name", "pressure_balls", "pressure_matches",
            "pressure_sr", "pressure_sr_eb", "normal_sr", "sr_delta", "pressure_rpd", "positive_contribution_pct"
        ]]
        f.write(df_to_markdown(top15_b))
        f.write("\n\n## 3. Methodology & Statistical Verification\n")
        f.write("- **Empirical Bayes Shrinkage**: Strike rates and runs per dismissal are shrunk toward the population prior mean based on individual sample size $n_i / (n_i + K)$ to avoid sample noise.\n")
        f.write("- **Match-Level Cluster Bootstrap**: 1,000 resamples per eligible batter clustered at the match level to compute 95% confidence intervals and standard errors.\n")
        f.write("- **Multi-Tier Decomposition**: Analyzed progression across Normal, Elevated, High, and Extreme pressure.\n")

    # 3. Phase 4: Bowler Performance Intelligence
    print("\n[PHASE 4] Computing Bowler Performance Metrics & Bootstrap Resampling...")
    eligible_bowlers, full_bowler_metrics, bowler_audit = build_bowler_performance_dataset(
        df_deliveries,
        min_pressure_balls=90,
        min_pressure_matches=10,
        n_bootstrap=1000,
        random_seed=42
    )
    print(f"Total Bowlers Evaluated: {len(full_bowler_metrics):,}")
    print(f"Eligible Bowlers (>=90 legal balls, >=10 matches): {len(eligible_bowlers):,}")

    # Save Phase 4 Artifacts
    full_bowler_metrics.to_parquet(os.path.join(config.PROCESSED_DIR, "bowler_metrics.parquet"), index=False)
    bowler_audit.to_csv(os.path.join(config.REPORTS_DIR, "bowler_eligibility_audit.csv"), index=False)

    # Provisional Bowling Rankings (by shrunk economy)
    prov_bowlers = eligible_bowlers.sort_values(by="pressure_econ_eb", ascending=True).reset_index(drop=True)
    prov_bowlers["provisional_rank"] = prov_bowlers.index + 1
    prov_bowlers.to_csv(os.path.join(rankings_dir, "bowler_rankings_provisional.csv"), index=False)

    # Bowling Analysis Report
    with open(os.path.join(config.REPORTS_DIR, "bowling_analysis_report.md"), "w", encoding="utf-8") as f:
        f.write("# Phase 4 Bowling Performance Intelligence Report\n\n")
        f.write("## 1. Executive Summary\n")
        f.write(f"- Total unique bowlers evaluated: {len(full_bowler_metrics):,}\n")
        f.write(f"- Eligible bowlers meeting sample thresholds (>= 90 pressure legal balls across >= 10 matches): {len(eligible_bowlers)}\n")
        f.write(f"- Total pressure legal balls bowled by eligible cohort: {int(eligible_bowlers['pressure_legal_balls'].sum()):,}\n")
        f.write(f"- Mean pressure economy across eligible cohort: {eligible_bowlers['pressure_econ'].mean():.2f}\n")
        f.write(f"- Mean baseline economy across eligible cohort: {eligible_bowlers['normal_econ'].mean():.2f}\n")
        f.write(f"- Mean clutch economy delta: {eligible_bowlers['econ_delta'].mean():+.2f}\n\n")
        f.write("## 2. Top 15 Eligible Bowlers by Empirical Bayes Shrunk Economy\n\n")
        top15_bw = prov_bowlers.head(15)[[
            "provisional_rank", "bowler_canonical_name", "pressure_legal_balls", "pressure_matches",
            "pressure_econ", "pressure_econ_eb", "normal_econ", "econ_delta", "pressure_wickets", "clutch_spell_pct"
        ]]
        f.write(df_to_markdown(top15_bw))
        f.write("\n\n## 3. Methodology & Statistical Verification\n")
        f.write("- **Phase-Adjusted Economy Rate**: Bowlers are evaluated against phase-specific baseline expectation (Death par 10.46, Middle par 8.01, Powerplay par 8.46) to eliminate structural bias against death bowlers.\n")
        f.write("- **Empirical Bayes Shrinkage**: Economy rates and wicket rates are shrunk toward population priors.\n")
        f.write("- **Match-Level Cluster Bootstrap**: 1,000 resamples per eligible bowler to compute 95% confidence intervals.\n")

    # 4. Phase 5: Player Ratings & Final Rankings
    print("\n[PHASE 5] Computing Multi-Dimensional Composite Ratings & Generating Final Top 10...")
    final_rated_batters = compute_batter_composite_ratings(eligible_batters, df_deliveries)
    final_rated_bowlers = compute_bowler_composite_ratings(eligible_bowlers, df_deliveries)

    # Explanations
    ranking_explanations = generate_player_explanations(final_rated_batters, final_rated_bowlers)

    # Save Final Rankings & Ratings
    final_rated_batters.to_csv(os.path.join(rankings_dir, "batter_rankings_final.csv"), index=False)
    final_rated_bowlers.to_csv(os.path.join(rankings_dir, "bowler_rankings_final.csv"), index=False)
    ranking_explanations.to_csv(os.path.join(rankings_dir, "ranking_explanations.csv"), index=False)

    # Combine player ratings into single file
    ratings_batters = final_rated_batters[[
        "rank", "striker_id", "striker_canonical_name", "composite_rating",
        "pressure_balls", "pressure_matches", "pressure_sr", "pressure_sr_eb",
        "normal_sr", "sr_delta", "pressure_rpd", "positive_contribution_pct"
    ]].rename(columns={"striker_id": "player_id", "striker_canonical_name": "player_name"})
    ratings_batters["category"] = "BATTER"

    ratings_bowlers = final_rated_bowlers[[
        "rank", "bowler_id", "bowler_canonical_name", "composite_rating",
        "pressure_legal_balls", "pressure_matches", "pressure_econ", "pressure_econ_eb",
        "phase_adj_econ", "runs_saved_per_over", "pressure_wickets", "clutch_spell_pct"
    ]].rename(columns={"bowler_id": "player_id", "bowler_canonical_name": "player_name", "pressure_legal_balls": "pressure_balls"})
    ratings_bowlers["category"] = "BOWLER"

    combined_ratings = pd.concat([ratings_batters, ratings_bowlers], ignore_index=True)
    combined_ratings.to_csv(os.path.join(rankings_dir, "player_ratings.csv"), index=False)

    # Excluded player audit
    excluded_b = batter_audit[~batter_audit["is_eligible"]].copy().rename(
        columns={"striker_id": "player_id", "striker_canonical_name": "player_name"}
    )
    excluded_b["category"] = "BATTER"

    excluded_bw = bowler_audit[~bowler_audit["is_eligible"]].copy().rename(
        columns={"bowler_id": "player_id", "bowler_canonical_name": "player_name", "pressure_legal_balls": "pressure_balls"}
    )
    excluded_bw["category"] = "BOWLER"

    excluded_combined = pd.concat([excluded_b, excluded_bw], ignore_index=True)
    excluded_combined.to_csv(os.path.join(rankings_dir, "excluded_player_audit.csv"), index=False)

    print("\n--- TOP 10 BATTERS UNDER PRESSURE ---")
    print(final_rated_batters.head(10)[[
        "rank", "striker_canonical_name", "composite_rating", "pressure_balls", "pressure_matches",
        "pressure_sr", "pressure_sr_eb", "normal_sr", "sr_delta", "pressure_rpd", "positive_contribution_pct"
    ]].to_string(index=False))

    print("\n--- TOP 10 BOWLERS UNDER PRESSURE ---")
    print(final_rated_bowlers.head(10)[[
        "rank", "bowler_canonical_name", "composite_rating", "pressure_legal_balls", "pressure_matches",
        "pressure_econ", "phase_adj_econ", "runs_saved_per_over", "pressure_wickets", "clutch_spell_pct"
    ]].to_string(index=False))

    print("\nSuccessfully completed Phases 3, 4, & 5! All artifacts generated.")
    return final_rated_batters, final_rated_bowlers, ranking_explanations


if __name__ == "__main__":
    run_ranking_pipeline()

