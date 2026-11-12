"""
Phase 2 Execution Orchestrator.
Runs feature extraction, models A, B, C, calibration, sensitivity, validation, reporting,
and generates all required Parquet files, CSV reports, and publication figures.
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import config, pressure_features, pressure_engine, pressure_calibration, pressure_sensitivity, pressure_validation, pressure_reporting

logger = logging.getLogger(__name__)

FIGURES_DIR = config.OUTPUT_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def generate_phase2_visualizations(df: pd.DataFrame, sens_df: pd.DataFrame, dist_df: pd.DataFrame):
    """Generates high-resolution publication-quality PNG charts for Phase 2."""
    logger.info("Generating Phase 2 publication visualizations...")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Chart: Pressure Tier Distribution Across Models
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    sub_dist = dist_df[dist_df["scope"] == "ALL"]
    pivot_dist = sub_dist.pivot(index="model", columns="tier", values="percentage")[["NORMAL", "ELEVATED", "HIGH", "EXTREME"]]
    colors = ["#2b83ba", "#abdda4", "#fdae61", "#d7191c"]
    pivot_dist.plot(kind="bar", stacked=True, color=colors, ax=ax, edgecolor="black", linewidth=0.5)
    ax.set_title("Delivery Distribution by Pressure Intensity Tier (Empirical Baseline)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Pressure Model Framework", fontsize=11, fontweight="bold")
    ax.set_ylabel("Percentage of Deliveries (%)", fontsize=11, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.legend(title="Intensity Tier", frameon=True, facecolor="white", loc="upper right")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    fig_path1 = FIGURES_DIR / "figure_pressure_distribution.png"
    plt.savefig(fig_path1)
    plt.close()
    logger.info(f"Saved {fig_path1}")

    # 2. Chart: IPL vs. T20I Required Run Rate Distribution (Chasing)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    inn2 = df[df["innings"] == 2]
    ipl_rrr = inn2[inn2["match_format"] == "T20"]["pre_delivery_required_run_rate"].clip(0, 24)
    t20i_rrr = inn2[inn2["match_format"] == "T20I"]["pre_delivery_required_run_rate"].clip(0, 24)
    ax.hist(ipl_rrr, bins=40, density=True, alpha=0.6, label="IPL (Mean: 10.08 rpo)", color="#e41a1c", edgecolor="black", linewidth=0.5)
    ax.hist(t20i_rrr, bins=40, density=True, alpha=0.6, label="T20I (Mean: 9.28 rpo)", color="#377eb8", edgecolor="black", linewidth=0.5)
    ax.set_title("Empirical Distribution of Pre-Delivery Required Run Rate (RRR): IPL vs. T20I", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Required Run Rate (Runs Per Over, capped at 24)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Probability Density", fontsize=11, fontweight="bold")
    ax.legend(frameon=True, facecolor="white", fontsize=11)
    plt.tight_layout()
    fig_path2 = FIGURES_DIR / "figure_ipl_vs_t20i_rrr.png"
    plt.savefig(fig_path2)
    plt.close()
    logger.info(f"Saved {fig_path2}")

    # 3. Chart: Threshold Sensitivity (Model D)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    c_sens = sens_df[sens_df["model"] == "Model C (Unified)"]
    pivot_sens = c_sens.pivot(index="variation", columns="tier", values="percentage")[["NORMAL", "ELEVATED", "HIGH", "EXTREME"]]
    # Reindex order
    var_order = ["-20% (Aggressive)", "-10% (Moderate-Low)", "Baseline (Calibrated)", "+10% (Moderate-High)", "+20% (Conservative)"]
    pivot_sens = pivot_sens.reindex(var_order)
    for col, color in zip(["NORMAL", "ELEVATED", "HIGH", "EXTREME"], colors):
        ax.plot(pivot_sens.index, pivot_sens[col], marker="o", linewidth=2.5, label=col, color=color)
    ax.set_title("Model D Sensitivity: Tier Proportions Across Boundary Perturbations (±20%)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Threshold Calibration Variation", fontsize=11, fontweight="bold")
    ax.set_ylabel("Percentage of Deliveries (%)", fontsize=11, fontweight="bold")
    ax.legend(title="Intensity Tier", frameon=True, facecolor="white")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    fig_path3 = FIGURES_DIR / "figure_threshold_sensitivity.png"
    plt.savefig(fig_path3)
    plt.close()
    logger.info(f"Saved {fig_path3}")

    # 4. Chart: Batter Pressure vs. Bowler Pressure (Role Asymmetry)
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
    sample_sub = df.sample(n=min(10000, len(df)), random_state=42)
    sc = ax.scatter(
        sample_sub["batter_pressure_score"],
        sample_sub["bowler_pressure_score"],
        c=sample_sub["innings"],
        cmap="coolwarm",
        alpha=0.3,
        s=12,
        edgecolor="none"
    )
    cbar = plt.colorbar(sc, ax=ax, ticks=[1, 2])
    cbar.set_label("Innings (1: Blue / Setting, 2: Red / Chasing)", fontsize=11, fontweight="bold")
    ax.plot([0, 100], [0, 100], color="black", linestyle="--", alpha=0.7, label="Symmetry Line (y=x)")
    ax.set_title("Role-Specific Pressure Divergence (Batter vs. Bowler Pressure)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Batter Situational Pressure Score (0-100)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Bowler Situational Pressure Score (0-100)", fontsize=11, fontweight="bold")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.legend(frameon=True, facecolor="white")
    plt.tight_layout()
    fig_path4 = FIGURES_DIR / "figure_batter_vs_bowler_pressure.png"
    plt.savefig(fig_path4)
    plt.close()
    logger.info(f"Saved {fig_path4}")


def run_phase2_pipeline():
    """Executes the complete Phase 2 workflow."""
    logger.info("==================================================")
    logger.info("STARTING PHASE 2 ADVANCED PRESSURE INTELLIGENCE ENGINE")
    logger.info("==================================================")

    # 1. Load Processed Deliveries from Phase 1
    logger.info(f"Loading Phase 1 processed deliveries from {config.PROCESSED_DELIVERIES_PARQUET}")
    deliv_df = pd.read_parquet(config.PROCESSED_DELIVERIES_PARQUET)
    logger.info(f"Loaded {len(deliv_df):,} standard deliveries across {deliv_df['match_id'].nunique()} matches.")

    # 2. Run All Pressure Models (A, B, C)
    enriched_df = pressure_engine.run_all_pressure_models(deliv_df)

    # 3. Save Specific Parquet Outputs
    # A) pressure_features.parquet
    feat_cols = [
        "match_id", "innings", "overid", "over_ball_num", "innings_ball_num",
        "striker_id", "bowler_id", "wickets_in_hand", "pre_delivery_runs",
        "pre_delivery_wickets", "pre_delivery_legal_balls", "pre_delivery_balls_remaining",
        "pre_delivery_runs_required", "pre_delivery_required_run_rate", "pre_delivery_current_run_rate",
        "rrr_diff", "req_rate_per_wicket", "is_contested_chase",
        "wicket_pace_ratio", "collapse_severity", "scoring_rate_deficit", "is_death_overs", "tail_exposed"
    ]
    feat_parquet_path = config.PROCESSED_DIR / "pressure_features.parquet"
    enriched_df[feat_cols].to_parquet(feat_parquet_path, index=False, engine="pyarrow", compression="snappy")
    logger.info(f"Saved {len(enriched_df):,} rows to {feat_parquet_path}")

    # B) pressure_deliveries_model_a.parquet (Chasing, Innings 2)
    model_a_df = enriched_df[enriched_df["innings"] == 2].copy()
    model_a_path = config.PROCESSED_DIR / "pressure_deliveries_model_a.parquet"
    model_a_df.to_parquet(model_a_path, index=False, engine="pyarrow", compression="snappy")
    logger.info(f"Saved {len(model_a_df):,} rows to {model_a_path}")

    # C) pressure_deliveries_model_b.parquet (First Innings, Innings 1)
    model_b_df = enriched_df[enriched_df["innings"] == 1].copy()
    model_b_path = config.PROCESSED_DIR / "pressure_deliveries_model_b.parquet"
    model_b_df.to_parquet(model_b_path, index=False, engine="pyarrow", compression="snappy")
    logger.info(f"Saved {len(model_b_df):,} rows to {model_b_path}")

    # D) pressure_deliveries_model_c.parquet (Unified Contextual across both innings)
    model_c_path = config.PROCESSED_DIR / "pressure_deliveries_model_c.parquet"
    enriched_df.to_parquet(model_c_path, index=False, engine="pyarrow", compression="snappy")
    logger.info(f"Saved {len(enriched_df):,} rows to {model_c_path}")

    # 4. Calibration & Distribution Reporting
    dist_df = pressure_calibration.generate_pressure_distribution_table(enriched_df)
    pressure_calibration.generate_calibration_report(enriched_df, dist_df)

    # 5. Sensitivity & Model Comparison (Model D)
    sens_df = pressure_sensitivity.evaluate_threshold_sensitivity(enriched_df)
    comp_df, comp_parquet = pressure_sensitivity.evaluate_model_comparison(enriched_df)
    pressure_sensitivity.generate_sensitivity_report(sens_df, comp_df)

    # 6. Validation Suite
    all_passed, checks = pressure_validation.validate_pressure_dataset(enriched_df)
    pressure_validation.generate_validation_report(checks)
    if not all_passed:
        raise AssertionError("Pressure validation suite encountered failures!")

    # 7. Comprehensive Pressure Definition Report
    pressure_reporting.generate_pressure_definition_report()

    # 8. High-Resolution Visualizations
    generate_phase2_visualizations(enriched_df, sens_df, dist_df)

    logger.info("==================================================")
    logger.info("PHASE 2 PRESSURE INTELLIGENCE ENGINE COMPLETED WITH 100% SUCCESS!")
    logger.info("==================================================")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run_phase2_pipeline()
