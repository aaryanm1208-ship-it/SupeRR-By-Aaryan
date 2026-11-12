"""
Professional Visual Analytics Engine for SupeRR Selector Season 2.
Generates 12 publication-grade figures in outputs/figures/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from src import config

# Publication style configuration
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "axes.edgecolor": "#CBD5E1",
    "axes.linewidth": 1.2,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
    "axes.labelweight": "semibold",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "grid.color": "#F1F5F9",
    "grid.linestyle": "--",
    "grid.linewidth": 0.8,
    "figure.titlesize": 16,
    "figure.titleweight": "bold",
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight"
})

FIGURES_DIR = os.path.join(config.OUTPUT_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def fig01_top_batters_rating(top_batters: pd.DataFrame):
    """Figure 1: Top 10 Batters Composite Rating and Key Metrics."""
    fig, ax = plt.subplots(figsize=(11, 6))
    df = top_batters.head(10).sort_values(by="rank", ascending=False)
    
    y = np.arange(len(df))
    bars = ax.barh(y, df["composite_rating"], color="#1E3A8A", edgecolor="#172554", height=0.65)
    
    # Value labels
    for bar, (_, r) in zip(bars, df.iterrows()):
        w = bar.get_width()
        ax.text(w + 1.0, bar.get_y() + bar.get_height()/2.0,
                f"{w:.1f}  (SR: {r['pressure_sr']:.1f} | Δ: {r['sr_delta']:+.1f})",
                va="center", ha="left", fontsize=9.5, fontweight="bold", color="#0F172A")
        
    ax.set_yticks(y)
    ax.set_yticklabels([f"#{r['rank']} {r['striker_canonical_name']}" for _, r in df.iterrows()], fontweight="semibold")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Batting Pressure Composite Rating (0 - 100)")
    ax.set_title("Figure 1: Top 10 Most Reliable Batters Under Pressure", pad=15)
    ax.grid(axis="x", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig01_top_batters_composite_rating.png"))
    plt.close()


def fig02_top_bowlers_rating(top_bowlers: pd.DataFrame):
    """Figure 2: Top 10 Bowlers Composite Rating and Key Metrics."""
    fig, ax = plt.subplots(figsize=(11, 6))
    df = top_bowlers.head(10).sort_values(by="rank", ascending=False)
    
    y = np.arange(len(df))
    bars = ax.barh(y, df["composite_rating"], color="#047857", edgecolor="#064E3B", height=0.65)
    
    for bar, (_, r) in zip(bars, df.iterrows()):
        w = bar.get_width()
        ax.text(w + 1.0, bar.get_y() + bar.get_height()/2.0,
                f"{w:.1f}  (Econ: {r['pressure_econ']:.2f} | Adj: {r['phase_adj_econ']:.2f} | {int(r['pressure_wickets'])} Wkts)",
                va="center", ha="left", fontsize=9.5, fontweight="bold", color="#0F172A")
        
    ax.set_yticks(y)
    ax.set_yticklabels([f"#{r['rank']} {r['bowler_canonical_name']}" for _, r in df.iterrows()], fontweight="semibold")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Bowling Pressure Composite Rating (0 - 100)")
    ax.set_title("Figure 2: Top 10 Most Reliable Bowlers Under Pressure", pad=15)
    ax.grid(axis="x", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig02_top_bowlers_composite_rating.png"))
    plt.close()


def fig03_batter_sr_scatter(all_batters: pd.DataFrame, top_batters: pd.DataFrame):
    """Figure 3: Pressure Strike Rate vs Normal Strike Rate Scatter."""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    ax.scatter(all_batters["normal_sr"], all_batters["pressure_sr"],
               color="#94A3B8", alpha=0.6, s=50, label="Other Eligible Batters")
    
    top10_ids = set(top_batters.head(10)["striker_id"])
    top = all_batters[all_batters["striker_id"].isin(top10_ids)]
    ax.scatter(top["normal_sr"], top["pressure_sr"],
               color="#DC2626", s=130, edgecolor="#7F1D1D", linewidth=1.5, label="Top 10 Batters", zorder=5)
    
    # Annotate Top 10
    for _, r in top.iterrows():
        ax.annotate(r["striker_canonical_name"], (r["normal_sr"], r["pressure_sr"]),
                    xytext=(6, 4), textcoords="offset points", fontsize=8.5, fontweight="bold", color="#1E293B")
        
    # Identity line (y = x)
    lims = [100, 220]
    ax.plot(lims, lims, "--", color="#64748B", linewidth=1.2, label="Par Line (Pressure SR = Normal SR)")
    
    ax.set_xlim(100, 210)
    ax.set_ylim(80, 230)
    ax.set_xlabel("Baseline Normal Strike Rate (Low + Moderate Pressure)")
    ax.set_ylabel("High & Extreme Pressure Strike Rate")
    ax.set_title("Figure 3: Batter Scoring Acceleration Under Pressure", pad=15)
    ax.legend(frameon=True, facecolor="#FFFFFF", framealpha=0.9, loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig03_batter_strike_rate_scatter.png"))
    plt.close()


def fig04_bowler_econ_scatter(all_bowlers: pd.DataFrame, top_bowlers: pd.DataFrame):
    """Figure 4: Pressure Economy vs Normal Economy Scatter."""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    ax.scatter(all_bowlers["normal_econ"], all_bowlers["pressure_econ"],
               color="#94A3B8", alpha=0.6, s=50, label="Other Eligible Bowlers")
    
    top10_ids = set(top_bowlers.head(10)["bowler_id"])
    top = all_bowlers[all_bowlers["bowler_id"].isin(top10_ids)]
    ax.scatter(top["normal_econ"], top["pressure_econ"],
               color="#059669", s=130, edgecolor="#064E3B", linewidth=1.5, label="Top 10 Bowlers", zorder=5)
    
    for _, r in top.iterrows():
        ax.annotate(r["bowler_canonical_name"], (r["normal_econ"], r["pressure_econ"]),
                    xytext=(6, 4), textcoords="offset points", fontsize=8.5, fontweight="bold", color="#1E293B")
        
    lims = [5, 12]
    ax.plot(lims, lims, "--", color="#64748B", linewidth=1.2, label="Par Line (Pressure Econ = Normal Econ)")
    
    ax.set_xlim(5, 11)
    ax.set_ylim(4.5, 12.5)
    ax.set_xlabel("Baseline Normal Economy Rate (Low + Moderate Pressure)")
    ax.set_ylabel("High & Extreme Pressure Economy Rate")
    ax.set_title("Figure 4: Bowler Economy Control Under Pressure", pad=15)
    ax.legend(frameon=True, facecolor="#FFFFFF", framealpha=0.9, loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig04_bowler_economy_rate_scatter.png"))
    plt.close()


def fig05_clutch_deltas(all_batters: pd.DataFrame, all_bowlers: pd.DataFrame):
    """Figure 5: Distribution of Clutch Deltas (Batter SR Delta & Bowler Economy Delta)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Batters
    sr_deltas = all_batters["sr_delta"]
    ax1.hist(sr_deltas, bins=25, color="#3B82F6", edgecolor="#1D4ED8", alpha=0.75)
    ax1.axvline(0, color="#EF4444", linestyle="--", linewidth=1.5, label="Zero Delta Line")
    ax1.axvline(sr_deltas.mean(), color="#1E3A8A", linestyle="-", linewidth=2.0, label=f"Mean Delta ({sr_deltas.mean():+.1f})")
    ax1.set_xlabel("Pressure Strike Rate Delta (Pressure SR - Normal SR)")
    ax1.set_ylabel("Number of Eligible Batters")
    ax1.set_title("Batting Clutch Delta Distribution")
    ax1.legend(frameon=True)
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    # Bowlers (Runs Saved Above Average per Over)
    rsaa = all_bowlers["runs_saved_per_over"]
    ax2.hist(rsaa, bins=25, color="#10B981", edgecolor="#047857", alpha=0.75)
    ax2.axvline(0, color="#EF4444", linestyle="--", linewidth=1.5, label="Par Baseline (0.00)")
    ax2.axvline(rsaa.mean(), color="#064E3B", linestyle="-", linewidth=2.0, label=f"Mean RSAA ({rsaa.mean():+.2f})")
    ax2.set_xlabel("Runs Saved Above Average per Over (vs Phase Par)")
    ax2.set_ylabel("Number of Eligible Bowlers")
    ax2.set_title("Bowling Run Suppression Distribution")
    ax2.legend(frameon=True)
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("Figure 5: Distribution of Clutch Value-Add Across Cohort", y=1.03)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig05_clutch_delta_distributions.png"))
    plt.close()


def fig06_match_consistency(top_batters: pd.DataFrame, top_bowlers: pd.DataFrame):
    """Figure 6: Match Consistency & Impact Rate for Top 10."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Batters
    tb = top_batters.head(10).sort_values(by="rank", ascending=False)
    y_b = np.arange(len(tb))
    ax1.barh(y_b, tb["positive_contribution_pct"], color="#6366F1", edgecolor="#4338CA", height=0.6)
    for i, (_, r) in enumerate(tb.iterrows()):
        ax1.text(r["positive_contribution_pct"] + 1.5, i, f"{r['positive_contribution_pct']:.1f}%",
                 va="center", fontsize=9, fontweight="bold", color="#1E1B4B")
    ax1.set_yticks(y_b)
    ax1.set_yticklabels([f"#{r['rank']} {r['striker_canonical_name']}" for _, r in tb.iterrows()])
    ax1.set_xlim(0, 100)
    ax1.set_xlabel("High-Impact Contribution Rate (%)")
    ax1.set_title("Top 10 Batters Match Impact Frequency")
    ax1.grid(axis="x", linestyle="--", alpha=0.6)
    
    # Bowlers
    tbw = top_bowlers.head(10).sort_values(by="rank", ascending=False)
    y_bw = np.arange(len(tbw))
    ax2.barh(y_bw, tbw["clutch_spell_pct"], color="#14B8A6", edgecolor="#0F766E", height=0.6)
    for i, (_, r) in enumerate(tbw.iterrows()):
        ax2.text(r["clutch_spell_pct"] + 1.5, i, f"{r['clutch_spell_pct']:.1f}%",
                 va="center", fontsize=9, fontweight="bold", color="#134E4A")
    ax2.set_yticks(y_bw)
    ax2.set_yticklabels([f"#{r['rank']} {r['bowler_canonical_name']}" for _, r in tbw.iterrows()])
    ax2.set_xlim(0, 100)
    ax2.set_xlabel("Clutch Spell Frequency (%) [Econ <= 7.50 or >= 2 Wkts]")
    ax2.set_title("Top 10 Bowlers Clutch Spell Frequency")
    ax2.grid(axis="x", linestyle="--", alpha=0.6)
    
    plt.suptitle("Figure 6: Match-by-Match Reliability & Consistency Profiles", y=1.03)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig06_match_consistency_dispersion.png"))
    plt.close()


def fig07_eb_shrinkage(all_batters: pd.DataFrame, all_bowlers: pd.DataFrame):
    """Figure 7: Empirical Bayes Shrinkage Visualization."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Batters: Raw vs EB Shrunk SR vs Balls
    ax1.scatter(all_batters["pressure_balls"], all_batters["pressure_sr"],
                color="#EF4444", alpha=0.6, s=40, label="Raw Observed SR")
    ax1.scatter(all_batters["pressure_balls"], all_batters["pressure_sr_eb"],
                color="#1E3A8A", alpha=0.8, s=40, label="EB Shrunk SR")
    for _, r in all_batters.head(20).iterrows():
        ax1.plot([r["pressure_balls"], r["pressure_balls"]], [r["pressure_sr"], r["pressure_sr_eb"]],
                 color="#94A3B8", linestyle=":", linewidth=1)
    ax1.axhline(all_batters["pressure_sr"].mean(), color="#0F172A", linestyle="--", linewidth=1.5, label="Population Prior Mean")
    ax1.set_xlabel("Pressure Balls Faced")
    ax1.set_ylabel("Pressure Strike Rate")
    ax1.set_title("Batting Strike Rate Empirical Bayes Shrinkage")
    ax1.legend(frameon=True)
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    # Bowlers: Raw vs EB Shrunk Economy vs Balls
    ax2.scatter(all_bowlers["pressure_legal_balls"], all_bowlers["pressure_econ"],
                color="#F97316", alpha=0.6, s=40, label="Raw Observed Economy")
    ax2.scatter(all_bowlers["pressure_legal_balls"], all_bowlers["pressure_econ_eb"],
                color="#047857", alpha=0.8, s=40, label="EB Shrunk Economy")
    for _, r in all_bowlers.head(20).iterrows():
        ax2.plot([r["pressure_legal_balls"], r["pressure_legal_balls"]], [r["pressure_econ"], r["pressure_econ_eb"]],
                 color="#94A3B8", linestyle=":", linewidth=1)
    ax2.axhline(all_bowlers["pressure_econ"].mean(), color="#0F172A", linestyle="--", linewidth=1.5, label="Population Prior Mean")
    ax2.set_xlabel("Pressure Legal Balls Bowled")
    ax2.set_ylabel("Pressure Economy Rate")
    ax2.set_title("Bowling Economy Empirical Bayes Shrinkage")
    ax2.legend(frameon=True)
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("Figure 7: Bayesian Regularization Preventing Small-Sample Distortion", y=1.03)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig07_empirical_bayes_shrinkage.png"))
    plt.close()


def fig08_model_ranking_bump(alt_batters: pd.DataFrame, top_batters: pd.DataFrame):
    """Figure 8: Ranking Stability Across Pressure Models (Model C vs Model A vs Model D)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    top10_ids = top_batters.head(10)["striker_id"].tolist()
    models = ["Model C (Unified)", "Model A (Chasing)", "Model D (Strict +20%)"]
    
    sub = alt_batters[(alt_batters["striker_id"].isin(top10_ids)) & (alt_batters["model"].isin(models))].copy()
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(top10_ids)))
    
    for i, pid in enumerate(top10_ids):
        p_df = sub[sub["striker_id"] == pid].sort_values(by="model", key=lambda x: x.map({m: j for j, m in enumerate(models)}))
        if len(p_df) >= 2:
            p_name = p_df["striker_canonical_name"].iloc[0]
            x_vals = [models.index(m) for m in p_df["model"]]
            y_vals = p_df["rank"].values
            ax.plot(x_vals, y_vals, marker="o", linewidth=2.2, markersize=7, color=colors[i], label=f"#{i+1} {p_name}")
            
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(["Model C\n(Primary Unified)", "Model A\n(Chasing Engine)", "Model D\n(Strict +20% Threshold)"], fontweight="semibold")
    ax.set_ylabel("Player Rank (Lower is Better)")
    ax.set_ylim(25, 0.5)  # Inverted
    ax.set_title("Figure 8: Top Batter Rank Stability Across Pressure Formulations", pad=15)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig08_model_ranking_stability_bump.png"))
    plt.close()


def fig09_ipl_vs_t20i(top_batters: pd.DataFrame, top_bowlers: pd.DataFrame):
    """Figure 9: IPL vs T20I Performance Breakdown."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Batters: IPL SR vs T20I SR
    tb = top_batters.head(8).sort_values(by="rank", ascending=False)
    y = np.arange(len(tb))
    ax1.barh(y - 0.18, tb["ipl_pressure_sr"], height=0.35, color="#F59E0B", label="IPL Pressure SR")
    ax1.barh(y + 0.18, tb["t20i_pressure_sr"], height=0.35, color="#3B82F6", label="T20I Pressure SR")
    ax1.set_yticks(y)
    ax1.set_yticklabels(tb["striker_canonical_name"])
    ax1.set_xlabel("Strike Rate")
    ax1.set_title("Top Batters: IPL vs T20I Strike Rate")
    ax1.legend(frameon=True, loc="lower right")
    ax1.grid(axis="x", linestyle="--", alpha=0.5)
    
    # Bowlers: IPL Econ vs T20I Econ
    tbw = top_bowlers.head(8).sort_values(by="rank", ascending=False)
    y_bw = np.arange(len(tbw))
    ax2.barh(y_bw - 0.18, tbw["ipl_pressure_econ"], height=0.35, color="#F59E0B", label="IPL Pressure Econ")
    ax2.barh(y_bw + 0.18, tbw["t20i_pressure_econ"], height=0.35, color="#10B981", label="T20I Pressure Econ")
    ax2.set_yticks(y_bw)
    ax2.set_yticklabels(tbw["bowler_canonical_name"])
    ax2.set_xlabel("Economy Rate")
    ax2.set_title("Top Bowlers: IPL vs T20I Economy Rate")
    ax2.legend(frameon=True, loc="upper right")
    ax2.grid(axis="x", linestyle="--", alpha=0.5)
    
    plt.suptitle("Figure 9: Cross-Tournament Portability (IPL vs Senior T20Is)", y=1.03)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig09_ipl_vs_t20i_performance.png"))
    plt.close()


def fig10_bootstrap_cis(top_batters: pd.DataFrame, top_bowlers: pd.DataFrame):
    """Figure 10: Forest Plot of 95% Bootstrap Confidence Intervals."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Batters SR CI
    tb = top_batters.head(10).sort_values(by="rank", ascending=False)
    y = np.arange(len(tb))
    sr_vals = tb["pressure_sr"].values
    ci_low = tb["boot_sr_ci_lower"].values
    ci_high = tb["boot_sr_ci_upper"].values
    xerr = [sr_vals - ci_low, ci_high - sr_vals]
    
    ax1.errorbar(sr_vals, y, xerr=xerr, fmt="o", color="#1E3A8A", ecolor="#64748B",
                 elinewidth=2.0, capsize=4, markersize=8, label="95% Bootstrap CI")
    ax1.set_yticks(y)
    ax1.set_yticklabels([f"#{r['rank']} {r['striker_canonical_name']}" for _, r in tb.iterrows()])
    ax1.set_xlabel("Pressure Strike Rate (with 95% Match Cluster CI)")
    ax1.set_title("Top 10 Batters Strike Rate Confidence Bounds")
    ax1.grid(True, linestyle="--", alpha=0.6)
    
    # Bowlers Econ CI
    tbw = top_bowlers.head(10).sort_values(by="rank", ascending=False)
    y_bw = np.arange(len(tbw))
    econ_vals = tbw["pressure_econ"].values
    bw_ci_low = tbw["boot_econ_ci_lower"].values
    bw_ci_high = tbw["boot_econ_ci_upper"].values
    bw_xerr = [econ_vals - bw_ci_low, bw_ci_high - econ_vals]
    
    ax2.errorbar(econ_vals, y_bw, xerr=bw_xerr, fmt="o", color="#047857", ecolor="#64748B",
                 elinewidth=2.0, capsize=4, markersize=8, label="95% Bootstrap CI")
    ax2.set_yticks(y_bw)
    ax2.set_yticklabels([f"#{r['rank']} {r['bowler_canonical_name']}" for _, r in tbw.iterrows()])
    ax2.set_xlabel("Pressure Economy Rate (with 95% Match Cluster CI)")
    ax2.set_title("Top 10 Bowlers Economy Rate Confidence Bounds")
    ax2.grid(True, linestyle="--", alpha=0.6)
    
    plt.suptitle("Figure 10: Statistical Defensibility & Bootstrap Uncertainty Bounds", y=1.03)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig10_bootstrap_confidence_intervals.png"))
    plt.close()


def fig11_tier_progression(df_deliveries: pd.DataFrame, top_batters: pd.DataFrame, top_bowlers: pd.DataFrame):
    """Figure 11: Performance Trajectory Across Pressure Tiers."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    tiers = ["NORMAL", "ELEVATED", "HIGH", "EXTREME"]
    
    # Batters top 5
    top5_b_names = top_batters.head(5)["striker_canonical_name"].tolist()
    bf = df_deliveries[df_deliveries["is_ball_faced"] == True].copy()
    
    for name in top5_b_names:
        sub = bf[bf["striker_canonical_name"] == name]
        sr_list = []
        for t in tiers:
            t_sub = sub[sub["batter_pressure_tier"] == t]
            sr = (t_sub["runs"].sum() / len(t_sub) * 100.0) if len(t_sub) >= 10 else np.nan
            sr_list.append(sr)
        ax1.plot(range(len(tiers)), sr_list, marker="o", linewidth=2.2, label=name)
        
    ax1.set_xticks(range(len(tiers)))
    ax1.set_xticklabels(tiers, fontweight="semibold")
    ax1.set_ylabel("Strike Rate")
    ax1.set_xlabel("Pressure Tier")
    ax1.set_title("Top Batters: Scoring Rate Trajectory Across Tiers")
    ax1.legend(frameon=True)
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    # Bowlers top 5
    top5_bw_names = top_bowlers.head(5)["bowler_canonical_name"].tolist()
    bw = df_deliveries[df_deliveries["is_legal_delivery"] == True].copy()
    
    for name in top5_bw_names:
        sub = bw[bw["bowler_canonical_name"] == name]
        econ_list = []
        for t in tiers:
            t_sub = sub[sub["bowler_pressure_tier"] == t]
            econ = (t_sub["bowler_charged_runs"].sum() / (len(t_sub) / 6.0)) if len(t_sub) >= 10 else np.nan
            econ_list.append(econ)
        ax2.plot(range(len(tiers)), econ_list, marker="s", linewidth=2.2, label=name)
        
    ax2.set_xticks(range(len(tiers)))
    ax2.set_xticklabels(tiers, fontweight="semibold")
    ax2.set_ylabel("Economy Rate")
    ax2.set_xlabel("Pressure Tier")
    ax2.set_title("Top Bowlers: Economy Rate Trajectory Across Tiers")
    ax2.legend(frameon=True)
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("Figure 11: Performance Trajectory Across Escalating Pressure Tiers", y=1.03)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig11_pressure_tier_progression.png"))
    plt.close()


def fig12_rating_vs_uncertainty(all_batters: pd.DataFrame, all_bowlers: pd.DataFrame):
    """Figure 12: Rating vs Bootstrap Standard Error Frontier."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Batters
    ax1.scatter(all_batters["boot_sr_se"], all_batters["composite_rating"],
                color="#3B82F6", alpha=0.7, s=60, edgecolor="#1E3A8A")
    top_b = all_batters.head(10)
    ax1.scatter(top_b["boot_sr_se"], top_b["composite_rating"],
                color="#DC2626", s=120, edgecolor="#7F1D1D", zorder=5)
    for _, r in top_b.iterrows():
        ax1.annotate(r["striker_canonical_name"], (r["boot_sr_se"], r["composite_rating"]),
                     xytext=(5, 3), textcoords="offset points", fontsize=8.5, fontweight="bold")
    ax1.set_xlabel("Bootstrap Standard Error (SE) of Strike Rate (Uncertainty)")
    ax1.set_ylabel("Batting Composite Pressure Rating")
    ax1.set_title("Batters: Pressure Rating vs Estimation Certainty")
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    # Bowlers
    ax2.scatter(all_bowlers["boot_econ_se"], all_bowlers["composite_rating"],
                color="#10B981", alpha=0.7, s=60, edgecolor="#064E3B")
    top_bw = all_bowlers.head(10)
    ax2.scatter(top_bw["boot_econ_se"], top_bw["composite_rating"],
                color="#7C3AED", s=120, edgecolor="#4C1D95", zorder=5)
    for _, r in top_bw.iterrows():
        ax2.annotate(r["bowler_canonical_name"], (r["boot_econ_se"], r["composite_rating"]),
                     xytext=(5, 3), textcoords="offset points", fontsize=8.5, fontweight="bold")
    ax2.set_xlabel("Bootstrap Standard Error (SE) of Economy Rate (Uncertainty)")
    ax2.set_ylabel("Bowling Composite Pressure Rating")
    ax2.set_title("Bowlers: Pressure Rating vs Estimation Certainty")
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("Figure 12: Elite Efficiency vs Statistical Precision Frontier", y=1.03)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig12_performance_vs_uncertainty.png"))
    plt.close()


def generate_all_visualizations():
    """Generates all 12 publication-quality figures."""
    print("=== EXECUTING PHASE 7: GENERATING 12 PUBLICATION-GRADE VISUALIZATIONS ===")
    
    pressure_path = os.path.join(config.PROCESSED_DIR, "pressure_deliveries_model_c.parquet")
    df_deliveries = pd.read_parquet(pressure_path)
    
    rankings_dir = os.path.join(config.OUTPUT_DIR, "rankings")
    batters_final = pd.read_csv(os.path.join(rankings_dir, "batter_rankings_final.csv"))
    bowlers_final = pd.read_csv(os.path.join(rankings_dir, "bowler_rankings_final.csv"))
    
    alt_rankings = pd.read_csv(os.path.join(config.REPORTS_DIR, "alternative_model_rankings.csv"))
    alt_batters = alt_rankings[alt_rankings["category"] == "BATTER"].rename(columns={"player_id": "striker_id", "player_name": "striker_canonical_name"})
    
    print("Generating Figure 1: Top Batters Composite Rating...")
    fig01_top_batters_rating(batters_final)
    
    print("Generating Figure 2: Top Bowlers Composite Rating...")
    fig02_top_bowlers_rating(bowlers_final)
    
    print("Generating Figure 3: Batter Strike Rate Scatter...")
    fig03_batter_sr_scatter(batters_final, batters_final)
    
    print("Generating Figure 4: Bowler Economy Scatter...")
    fig04_bowler_econ_scatter(bowlers_final, bowlers_final)
    
    print("Generating Figure 5: Clutch Deltas...")
    fig05_clutch_deltas(batters_final, bowlers_final)
    
    print("Generating Figure 6: Match Consistency...")
    fig06_match_consistency(batters_final, bowlers_final)
    
    print("Generating Figure 7: Empirical Bayes Shrinkage...")
    fig07_eb_shrinkage(batters_final, bowlers_final)
    
    print("Generating Figure 8: Model Ranking Bump Chart...")
    fig08_model_ranking_bump(alt_batters, batters_final)
    
    print("Generating Figure 9: IPL vs T20I Breakdown...")
    fig09_ipl_vs_t20i(batters_final, bowlers_final)
    
    print("Generating Figure 10: Bootstrap Confidence Intervals...")
    fig10_bootstrap_cis(batters_final, bowlers_final)
    
    print("Generating Figure 11: Pressure Tier Progression...")
    fig11_tier_progression(df_deliveries, batters_final, bowlers_final)
    
    print("Generating Figure 12: Rating vs Uncertainty Frontier...")
    fig12_rating_vs_uncertainty(batters_final, bowlers_final)
    
    print("\nPhase 7 Complete! All 12 figures successfully generated in outputs/figures/.")


if __name__ == "__main__":
    generate_all_visualizations()

