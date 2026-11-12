"""
Batting performance intelligence engine under pressure situations.
SupeRR Selector Season 2 — Elite Pressure Performance Intelligence System.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional
from src import config


def compute_batter_aggregates(
    df: pd.DataFrame,
    pressure_tiers: List[str] = ["HIGH", "EXTREME"],
    baseline_tier: str = "NORMAL"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes aggregated batting performance under baseline vs pressure tiers.
    
    Returns:
        (batter_metrics_df, batter_tier_breakdown_df)
    """
    # Filter deliveries where striker faced the ball
    bf = df[df["is_ball_faced"] == True].copy()
    bf["is_striker_out"] = (bf["is_wicket"] == 1) & (bf["dismissed_player_id"] == bf["striker_id"])
    bf["is_boundary"] = (bf["runs"] >= 4)
    bf["is_four_hit"] = (bf["is_four"] == 1)
    bf["is_six_hit"] = (bf["is_six"] == 1)
    bf["is_dot"] = (bf["runs"] == 0) & (bf["extras1_runs"] == 0)

    # 1. Tier breakdown
    tier_grouped = bf.groupby(["striker_id", "striker_canonical_name", "batter_pressure_tier"]).agg(
        balls=("runs", "count"),
        runs=("runs", "sum"),
        matches=("match_id", "nunique"),
        outs=("is_striker_out", "sum"),
        boundaries=("is_boundary", "sum"),
        fours=("is_four_hit", "sum"),
        sixes=("is_six_hit", "sum"),
        dots=("is_dot", "sum")
    ).reset_index()

    tier_grouped["strike_rate"] = (tier_grouped["runs"] / tier_grouped["balls"]) * 100.0
    tier_grouped["runs_per_dismissal"] = tier_grouped["runs"] / np.maximum(tier_grouped["outs"], 1)
    tier_grouped["boundary_pct"] = (tier_grouped["boundaries"] / tier_grouped["balls"]) * 100.0
    tier_grouped["dot_pct"] = (tier_grouped["dots"] / tier_grouped["balls"]) * 100.0

    # 2. Pressure vs Baseline Aggregates
    bf_press = bf[bf["batter_pressure_tier"].isin(pressure_tiers)]
    bf_base = bf[bf["batter_pressure_tier"] == baseline_tier]
    bf_all = bf

    def agg_subset(data: pd.DataFrame, prefix: str) -> pd.DataFrame:
        agg = data.groupby(["striker_id", "striker_canonical_name"]).agg(
            balls=("runs", "count"),
            runs=("runs", "sum"),
            matches=("match_id", "nunique"),
            outs=("is_striker_out", "sum"),
            boundaries=("is_boundary", "sum"),
            fours=("is_four_hit", "sum"),
            sixes=("is_six_hit", "sum"),
            dots=("is_dot", "sum")
        ).reset_index()
        
        agg[f"{prefix}_balls"] = agg["balls"]
        agg[f"{prefix}_runs"] = agg["runs"]
        agg[f"{prefix}_matches"] = agg["matches"]
        agg[f"{prefix}_outs"] = agg["outs"]
        agg[f"{prefix}_boundaries"] = agg["boundaries"]
        agg[f"{prefix}_fours"] = agg["fours"]
        agg[f"{prefix}_sixes"] = agg["sixes"]
        agg[f"{prefix}_dots"] = agg["dots"]
        
        agg[f"{prefix}_sr"] = (agg[f"{prefix}_runs"] / agg[f"{prefix}_balls"]) * 100.0
        agg[f"{prefix}_rpd"] = agg[f"{prefix}_runs"] / np.maximum(agg[f"{prefix}_outs"], 1)
        agg[f"{prefix}_boundary_pct"] = (agg[f"{prefix}_boundaries"] / agg[f"{prefix}_balls"]) * 100.0
        agg[f"{prefix}_dot_pct"] = (agg[f"{prefix}_dots"] / agg[f"{prefix}_balls"]) * 100.0
        
        cols = ["striker_id", "striker_canonical_name"] + [c for c in agg.columns if c.startswith(prefix)]
        return agg[cols]

    p_agg = agg_subset(bf_press, "pressure")
    b_agg = agg_subset(bf_base, "normal")
    all_agg = agg_subset(bf_all, "overall")

    # Merge subsets
    merged = pd.merge(all_agg, p_agg, on=["striker_id", "striker_canonical_name"], how="left").fillna(0)
    merged = pd.merge(merged, b_agg, on=["striker_id", "striker_canonical_name"], how="left").fillna(0)

    # Compute deltas
    merged["sr_delta"] = merged["pressure_sr"] - merged["normal_sr"]
    merged["rpd_delta"] = merged["pressure_rpd"] - merged["normal_rpd"]
    merged["relative_sr_ratio"] = np.where(
        merged["normal_sr"] > 0,
        merged["pressure_sr"] / merged["normal_sr"],
        1.0
    )
    merged["boundary_pct_delta"] = merged["pressure_boundary_pct"] - merged["normal_boundary_pct"]
    merged["dot_pct_delta"] = merged["pressure_dot_pct"] - merged["normal_dot_pct"]

    return merged, tier_grouped


def compute_batter_match_consistency(df: pd.DataFrame, pressure_tiers: List[str] = ["HIGH", "EXTREME"]) -> pd.DataFrame:
    """
    Computes match-level consistency and dispersion metrics for batters in pressure situations.
    Evaluates:
      - Strike rate standard deviation across matches
      - Strike rate IQR across matches
      - Positive contribution frequency (matches with SR >= 130 or 15+ runs at SR >= 120)
      - Median match strike rate
    """
    bf_press = df[(df["is_ball_faced"] == True) & (df["batter_pressure_tier"].isin(pressure_tiers))].copy()
    bf_press["is_striker_out"] = (bf_press["is_wicket"] == 1) & (bf_press["dismissed_player_id"] == bf_press["striker_id"])

    # Match-level aggregation per batter
    match_batting = bf_press.groupby(["striker_id", "striker_canonical_name", "match_id"]).agg(
        match_balls=("runs", "count"),
        match_runs=("runs", "sum"),
        match_outs=("is_striker_out", "sum")
    ).reset_index()

    match_batting["match_sr"] = (match_batting["match_runs"] / match_batting["match_balls"]) * 100.0

    # Define positive contribution in pressure:
    # A positive contribution requires either:
    # 1. Match SR >= 135 with >= 5 balls, OR
    # 2. Match runs >= 15 with Match SR >= 120
    match_batting["is_positive_contribution"] = (
        ((match_batting["match_sr"] >= 135.0) & (match_batting["match_balls"] >= 5)) |
        ((match_batting["match_runs"] >= 15.0) & (match_batting["match_sr"] >= 120.0))
    ).astype(int)

    # Compute consistency statistics per batter
    consistency = match_batting.groupby(["striker_id", "striker_canonical_name"]).agg(
        pressure_match_count=("match_id", "count"),
        match_sr_mean=("match_sr", "mean"),
        match_sr_median=("match_sr", "median"),
        match_sr_std=("match_sr", lambda x: float(np.std(x, ddof=1)) if len(x) > 1 else 0.0),
        match_sr_iqr=("match_sr", lambda x: float(np.percentile(x, 75) - np.percentile(x, 25)) if len(x) >= 4 else 0.0),
        positive_contribution_matches=("is_positive_contribution", "sum"),
        positive_contribution_rate=("is_positive_contribution", "mean")
    ).reset_index()

    consistency["positive_contribution_pct"] = consistency["positive_contribution_rate"] * 100.0
    return consistency


def compute_competition_splits(df: pd.DataFrame, pressure_tiers: List[str] = ["HIGH", "EXTREME"]) -> pd.DataFrame:
    """Computes IPL vs T20I performance splits for batters under pressure."""
    bf_press = df[(df["is_ball_faced"] == True) & (df["batter_pressure_tier"].isin(pressure_tiers))].copy()
    bf_press["is_striker_out"] = (bf_press["is_wicket"] == 1) & (bf_press["dismissed_player_id"] == bf_press["striker_id"])
    bf_press["comp_type"] = np.where(bf_press["match_format"] == "T20I", "t20i", "ipl")

    comp_agg = bf_press.groupby(["striker_id", "striker_canonical_name", "comp_type"]).agg(
        balls=("runs", "count"),
        runs=("runs", "sum"),
        matches=("match_id", "nunique"),
        outs=("is_striker_out", "sum")
    ).reset_index()

    comp_agg["sr"] = (comp_agg["runs"] / comp_agg["balls"]) * 100.0
    comp_agg["rpd"] = comp_agg["runs"] / np.maximum(comp_agg["outs"], 1)

    # Pivot to wide format
    ipl_split = comp_agg[comp_agg["comp_type"] == "ipl"].rename(columns={
        "balls": "ipl_pressure_balls", "runs": "ipl_pressure_runs", "matches": "ipl_pressure_matches",
        "outs": "ipl_pressure_outs", "sr": "ipl_pressure_sr", "rpd": "ipl_pressure_rpd"
    }).drop(columns=["comp_type"])

    t20i_split = comp_agg[comp_agg["comp_type"] == "t20i"].rename(columns={
        "balls": "t20i_pressure_balls", "runs": "t20i_pressure_runs", "matches": "t20i_pressure_matches",
        "outs": "t20i_pressure_outs", "sr": "t20i_pressure_sr", "rpd": "t20i_pressure_rpd"
    }).drop(columns=["comp_type"])

    splits = pd.merge(ipl_split, t20i_split, on=["striker_id", "striker_canonical_name"], how="outer").fillna(0)
    return splits


def compute_phase_splits(df: pd.DataFrame, pressure_tiers: List[str] = ["HIGH", "EXTREME"]) -> pd.DataFrame:
    """Computes Powerplay, Middle, and Death overs performance under pressure."""
    bf_press = df[(df["is_ball_faced"] == True) & (df["batter_pressure_tier"].isin(pressure_tiers))].copy()
    bf_press["is_striker_out"] = (bf_press["is_wicket"] == 1) & (bf_press["dismissed_player_id"] == bf_press["striker_id"])

    phase_agg = bf_press.groupby(["striker_id", "striker_canonical_name", "innings_stage"]).agg(
        balls=("runs", "count"),
        runs=("runs", "sum"),
        outs=("is_striker_out", "sum")
    ).reset_index()

    phase_agg["sr"] = (phase_agg["runs"] / phase_agg["balls"]) * 100.0

    pivoted = phase_agg.pivot_table(
        index=["striker_id", "striker_canonical_name"],
        columns="innings_stage",
        values=["balls", "runs", "sr"],
        fill_value=0
    )
    pivoted.columns = [f"{col[1].lower()}_pressure_{col[0]}" for col in pivoted.columns]
    return pivoted.reset_index()


def apply_empirical_bayes_shrinkage(
    eligible_df: pd.DataFrame,
    shrinkage_target_col: str = "pressure_sr",
    volume_col: str = "pressure_balls"
) -> Tuple[pd.Series, float, float]:
    """
    Applies Empirical Bayes shrinkage to regress individual rates toward sample mean.
    Uses inverse-variance weighting based on exposure.
    
    Formula:
        w_i = n_i / (n_i + K)
        shrunk_i = w_i * x_i + (1 - w_i) * mu_0
    where K is the estimated shrinkage parameter representing the ratio of
    within-player sampling variance to between-player prior variance.
    """
    x = eligible_df[shrinkage_target_col].values
    n = eligible_df[volume_col].values
    
    if len(eligible_df) == 0 or np.sum(n) == 0:
        return pd.Series(dtype=float, index=eligible_df.index), 150.0, 50.0

    # Population prior mean
    mu_0 = float(np.average(x, weights=n))
    
    # Between-player variance
    var_between = float(np.var(x, ddof=1))
    
    # Estimate average within-player sampling variance (binomial/poisson approx)
    # For strike rate: standard deviation of individual ball runs is approx 1.5 runs
    # Variance of SR on n balls is approx (1.5^2 / n) * 100^2
    avg_ball_var = 1.6 ** 2 * 10000.0
    k_shrink = float(avg_ball_var / max(var_between, 1.0))
    # Cap K to a reasonable cricket empirical shrinkage constant (e.g., ~40-60 balls)
    k_shrink = np.clip(k_shrink, 30.0, 80.0)

    weights = n / (n + k_shrink)
    shrunk_values = weights * x + (1.0 - weights) * mu_0

    return pd.Series(shrunk_values, index=eligible_df.index), mu_0, k_shrink


def run_match_level_bootstrap(
    df: pd.DataFrame,
    eligible_player_ids: List[int],
    n_iterations: int = 1000,
    random_seed: int = 42,
    pressure_tiers: List[str] = ["HIGH", "EXTREME"]
) -> pd.DataFrame:
    """
    Performs match-level cluster bootstrap resampling to obtain 95% confidence intervals
    for pressure strike rate and pressure runs per dismissal.
    Preserves intra-match ball dependencies.
    """
    rng = np.random.default_rng(random_seed)
    
    bf_press = df[
        (df["is_ball_faced"] == True) &
        (df["batter_pressure_tier"].isin(pressure_tiers)) &
        (df["striker_id"].isin(eligible_player_ids))
    ].copy()
    bf_press["is_striker_out"] = (bf_press["is_wicket"] == 1) & (bf_press["dismissed_player_id"] == bf_press["striker_id"])

    # Aggregate to player-match level
    pm_df = bf_press.groupby(["striker_id", "match_id"]).agg(
        runs=("runs", "sum"),
        balls=("runs", "count"),
        outs=("is_striker_out", "sum")
    ).reset_index()

    bootstrap_results = []

    for pid in eligible_player_ids:
        sub = pm_df[pm_df["striker_id"] == pid]
        m_count = len(sub)
        if m_count == 0:
            continue

        runs_arr = sub["runs"].values
        balls_arr = sub["balls"].values
        outs_arr = sub["outs"].values

        # Sample match indices with replacement (n_iterations x m_count)
        sampled_indices = rng.choice(m_count, size=(n_iterations, m_count), replace=True)

        boot_runs = runs_arr[sampled_indices].sum(axis=1)
        boot_balls = balls_arr[sampled_indices].sum(axis=1)
        boot_outs = outs_arr[sampled_indices].sum(axis=1)

        # Avoid div by 0
        valid_mask = boot_balls > 0
        boot_sr = np.where(valid_mask, (boot_runs / boot_balls) * 100.0, np.nan)
        boot_rpd = np.where(boot_outs > 0, boot_runs / boot_outs, boot_runs)

        boot_sr_valid = boot_sr[~np.isnan(boot_sr)]
        boot_rpd_valid = boot_rpd[~np.isnan(boot_rpd)]

        sr_ci_lower = float(np.percentile(boot_sr_valid, 2.5)) if len(boot_sr_valid) > 0 else np.nan
        sr_ci_upper = float(np.percentile(boot_sr_valid, 97.5)) if len(boot_sr_valid) > 0 else np.nan
        sr_se = float(np.std(boot_sr_valid, ddof=1)) if len(boot_sr_valid) > 1 else np.nan

        rpd_ci_lower = float(np.percentile(boot_rpd_valid, 2.5)) if len(boot_rpd_valid) > 0 else np.nan
        rpd_ci_upper = float(np.percentile(boot_rpd_valid, 97.5)) if len(boot_rpd_valid) > 0 else np.nan
        rpd_se = float(np.std(boot_rpd_valid, ddof=1)) if len(boot_rpd_valid) > 1 else np.nan

        bootstrap_results.append({
            "striker_id": pid,
            "boot_sr_ci_lower": sr_ci_lower,
            "boot_sr_ci_upper": sr_ci_upper,
            "boot_sr_se": sr_se,
            "boot_rpd_ci_lower": rpd_ci_lower,
            "boot_rpd_ci_upper": rpd_ci_upper,
            "boot_rpd_se": rpd_se
        })

    return pd.DataFrame(bootstrap_results)


def build_batter_performance_dataset(
    df: pd.DataFrame,
    min_pressure_balls: int = 75,
    min_pressure_matches: int = 10,
    n_bootstrap: int = 1000,
    random_seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Executes the complete Phase 3 Batter Performance pipeline.
    
    Returns:
        (eligible_batters_df, full_batter_metrics_df, eligibility_audit_df)
    """
    # 1. Compute aggregates and tier breakdown
    full_metrics, tier_breakdown = compute_batter_aggregates(df)

    # 2. Compute match consistency
    consistency = compute_batter_match_consistency(df)
    full_metrics = pd.merge(full_metrics, consistency.drop(columns=["striker_canonical_name"]), on="striker_id", how="left")

    # 3. Compute competition splits
    comp_splits = compute_competition_splits(df)
    full_metrics = pd.merge(full_metrics, comp_splits.drop(columns=["striker_canonical_name"]), on="striker_id", how="left").fillna(0)

    # 4. Compute phase splits
    phase_splits = compute_phase_splits(df)
    full_metrics = pd.merge(full_metrics, phase_splits.drop(columns=["striker_canonical_name"]), on="striker_id", how="left").fillna(0)

    # 5. Build eligibility audit
    full_metrics["meets_ball_threshold"] = full_metrics["pressure_balls"] >= min_pressure_balls
    full_metrics["meets_match_threshold"] = full_metrics["pressure_matches"] >= min_pressure_matches
    full_metrics["is_eligible"] = full_metrics["meets_ball_threshold"] & full_metrics["meets_match_threshold"]

    conditions = [
        full_metrics["is_eligible"],
        (~full_metrics["meets_ball_threshold"]) & (~full_metrics["meets_match_threshold"]),
        (~full_metrics["meets_ball_threshold"]),
        (~full_metrics["meets_match_threshold"])
    ]
    choices = [
        "ELIGIBLE",
        f"INSUFFICIENT_BALLS_AND_MATCHES (<{min_pressure_balls} balls, <{min_pressure_matches} matches)",
        f"INSUFFICIENT_PRESSURE_BALLS (<{min_pressure_balls} balls)",
        f"INSUFFICIENT_PRESSURE_MATCHES (<{min_pressure_matches} matches)"
    ]
    full_metrics["eligibility_status"] = np.select(conditions, choices, default="EXCLUDED")

    audit_df = full_metrics[[
        "striker_id", "striker_canonical_name", "pressure_balls", "pressure_matches",
        "pressure_runs", "pressure_sr", "normal_sr", "is_eligible", "eligibility_status"
    ]].copy()

    # Filter eligible
    eligible_df = full_metrics[full_metrics["is_eligible"]].copy()

    # 6. Apply Empirical Bayes shrinkage
    shrunk_sr, mu_sr, k_sr = apply_empirical_bayes_shrinkage(eligible_df, "pressure_sr", "pressure_balls")
    eligible_df["pressure_sr_eb"] = shrunk_sr

    shrunk_rpd, mu_rpd, k_rpd = apply_empirical_bayes_shrinkage(eligible_df, "pressure_rpd", "pressure_balls")
    eligible_df["pressure_rpd_eb"] = shrunk_rpd

    # 7. Run cluster bootstrap
    boot_df = run_match_level_bootstrap(
        df,
        eligible_player_ids=eligible_df["striker_id"].tolist(),
        n_iterations=n_bootstrap,
        random_seed=random_seed
    )
    eligible_df = pd.merge(eligible_df, boot_df, on="striker_id", how="left")

    return eligible_df, full_metrics, audit_df

