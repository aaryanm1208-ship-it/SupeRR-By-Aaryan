"""
Bowling performance intelligence engine under pressure situations.
SupeRR Selector Season 2 — Elite Pressure Performance Intelligence System.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional
from src import config


def compute_bowler_aggregates(
    df: pd.DataFrame,
    pressure_tiers: List[str] = ["HIGH", "EXTREME"],
    baseline_tier: str = "NORMAL"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes aggregated bowling performance under baseline vs pressure tiers.
    
    Returns:
        (bowler_metrics_df, bowler_tier_breakdown_df)
    """
    # Filter deliveries bowled
    b = df[df["is_legal_delivery"] == True].copy()
    b["is_dot"] = (b["bowler_charged_runs"] == 0)
    b["is_boundary"] = (b["bowler_charged_runs"] >= 4)
    b["is_four_conceded"] = (b["bowler_charged_runs"] == 4)
    b["is_six_conceded"] = (b["bowler_charged_runs"] == 6)

    # 1. Tier breakdown
    tier_grouped = b.groupby(["bowler_id", "bowler_canonical_name", "bowler_pressure_tier"]).agg(
        legal_balls=("bowler_charged_runs", "count"),
        runs_conceded=("bowler_charged_runs", "sum"),
        matches=("match_id", "nunique"),
        wickets=("is_bowler_wicket", "sum"),
        dots=("is_dot", "sum"),
        boundaries=("is_boundary", "sum"),
        fours=("is_four_conceded", "sum"),
        sixes=("is_six_conceded", "sum")
    ).reset_index()

    tier_grouped["overs"] = tier_grouped["legal_balls"] / 6.0
    tier_grouped["economy"] = np.where(tier_grouped["overs"] > 0, tier_grouped["runs_conceded"] / tier_grouped["overs"], 0.0)
    tier_grouped["strike_rate"] = np.where(tier_grouped["wickets"] > 0, tier_grouped["legal_balls"] / tier_grouped["wickets"], np.nan)
    tier_grouped["average"] = np.where(tier_grouped["wickets"] > 0, tier_grouped["runs_conceded"] / tier_grouped["wickets"], np.nan)
    tier_grouped["dot_pct"] = (tier_grouped["dots"] / tier_grouped["legal_balls"]) * 100.0
    tier_grouped["boundary_pct"] = (tier_grouped["boundaries"] / tier_grouped["legal_balls"]) * 100.0

    # 2. Pressure vs Baseline Aggregates
    b_press = b[b["bowler_pressure_tier"].isin(pressure_tiers)]
    b_base = b[b["bowler_pressure_tier"] == baseline_tier]
    b_all = b

    def agg_subset(data: pd.DataFrame, prefix: str) -> pd.DataFrame:
        agg = data.groupby(["bowler_id", "bowler_canonical_name"]).agg(
            legal_balls=("bowler_charged_runs", "count"),
            runs_conceded=("bowler_charged_runs", "sum"),
            matches=("match_id", "nunique"),
            wickets=("is_bowler_wicket", "sum"),
            dots=("is_dot", "sum"),
            boundaries=("is_boundary", "sum"),
            fours=("is_four_conceded", "sum"),
            sixes=("is_six_conceded", "sum")
        ).reset_index()

        agg[f"{prefix}_legal_balls"] = agg["legal_balls"]
        agg[f"{prefix}_overs"] = agg["legal_balls"] / 6.0
        agg[f"{prefix}_runs_conceded"] = agg["runs_conceded"]
        agg[f"{prefix}_matches"] = agg["matches"]
        agg[f"{prefix}_wickets"] = agg["wickets"]
        agg[f"{prefix}_dots"] = agg["dots"]
        agg[f"{prefix}_boundaries"] = agg["boundaries"]
        agg[f"{prefix}_fours"] = agg["fours"]
        agg[f"{prefix}_sixes"] = agg["sixes"]

        agg[f"{prefix}_econ"] = np.where(agg[f"{prefix}_overs"] > 0, agg[f"{prefix}_runs_conceded"] / agg[f"{prefix}_overs"], 0.0)
        agg[f"{prefix}_sr"] = np.where(agg[f"{prefix}_wickets"] > 0, agg[f"{prefix}_legal_balls"] / agg[f"{prefix}_wickets"], np.nan)
        agg[f"{prefix}_avg"] = np.where(agg[f"{prefix}_wickets"] > 0, agg[f"{prefix}_runs_conceded"] / agg[f"{prefix}_wickets"], np.nan)
        agg[f"{prefix}_dot_pct"] = (agg[f"{prefix}_dots"] / agg[f"{prefix}_legal_balls"]) * 100.0
        agg[f"{prefix}_boundary_pct"] = (agg[f"{prefix}_boundaries"] / agg[f"{prefix}_legal_balls"]) * 100.0

        cols = ["bowler_id", "bowler_canonical_name"] + [c for c in agg.columns if c.startswith(prefix)]
        return agg[cols]

    p_agg = agg_subset(b_press, "pressure")
    b_agg = agg_subset(b_base, "normal")
    all_agg = agg_subset(b_all, "overall")

    # Merge subsets
    merged = pd.merge(all_agg, p_agg, on=["bowler_id", "bowler_canonical_name"], how="left").fillna(0)
    merged = pd.merge(merged, b_agg, on=["bowler_id", "bowler_canonical_name"], how="left").fillna(0)

    # Compute deltas
    merged["econ_delta"] = merged["normal_econ"] - merged["pressure_econ"]  # positive = improvement
    merged["dot_pct_delta"] = merged["pressure_dot_pct"] - merged["normal_dot_pct"]
    merged["boundary_pct_delta"] = merged["normal_boundary_pct"] - merged["pressure_boundary_pct"]  # positive = suppressed boundaries
    merged["wicket_rate_pressure"] = merged["pressure_wickets"] / np.maximum(merged["pressure_legal_balls"], 1)
    merged["wicket_rate_normal"] = merged["normal_wickets"] / np.maximum(merged["normal_legal_balls"], 1)
    merged["wicket_rate_delta"] = merged["wicket_rate_pressure"] - merged["wicket_rate_normal"]

    return merged, tier_grouped


def compute_bowler_match_consistency(df: pd.DataFrame, pressure_tiers: List[str] = ["HIGH", "EXTREME"]) -> pd.DataFrame:
    """
    Computes match-level consistency and dispersion metrics for bowlers in pressure situations.
    Evaluates:
      - Economy standard deviation across matches
      - Economy IQR across matches
      - Clutch spell frequency (matches with Economy <= 7.50 in pressure overs or taking >= 2 wickets)
    """
    b_press = df[(df["is_legal_delivery"] == True) & (df["bowler_pressure_tier"].isin(pressure_tiers))].copy()

    # Match-level aggregation per bowler
    match_bowling = b_press.groupby(["bowler_id", "bowler_canonical_name", "match_id"]).agg(
        match_balls=("bowler_charged_runs", "count"),
        match_runs=("bowler_charged_runs", "sum"),
        match_wickets=("is_bowler_wicket", "sum")
    ).reset_index()

    match_bowling["match_overs"] = match_bowling["match_balls"] / 6.0
    match_bowling["match_econ"] = match_bowling["match_runs"] / match_bowling["match_overs"]

    # Define clutch spell in pressure:
    # Match economy <= 7.50 with >= 6 balls bowled, OR taking >= 2 wickets under pressure
    match_bowling["is_clutch_spell"] = (
        ((match_bowling["match_econ"] <= 7.50) & (match_bowling["match_balls"] >= 6)) |
        (match_bowling["match_wickets"] >= 2)
    ).astype(int)

    consistency = match_bowling.groupby(["bowler_id", "bowler_canonical_name"]).agg(
        pressure_match_count=("match_id", "count"),
        match_econ_mean=("match_econ", "mean"),
        match_econ_median=("match_econ", "median"),
        match_econ_std=("match_econ", lambda x: float(np.std(x, ddof=1)) if len(x) > 1 else 0.0),
        match_econ_iqr=("match_econ", lambda x: float(np.percentile(x, 75) - np.percentile(x, 25)) if len(x) >= 4 else 0.0),
        clutch_spells=("is_clutch_spell", "sum"),
        clutch_spell_rate=("is_clutch_spell", "mean")
    ).reset_index()

    consistency["clutch_spell_pct"] = consistency["clutch_spell_rate"] * 100.0
    return consistency


def compute_bowler_competition_splits(df: pd.DataFrame, pressure_tiers: List[str] = ["HIGH", "EXTREME"]) -> pd.DataFrame:
    """Computes IPL vs T20I performance splits for bowlers under pressure."""
    b_press = df[(df["is_legal_delivery"] == True) & (df["bowler_pressure_tier"].isin(pressure_tiers))].copy()
    b_press["comp_type"] = np.where(b_press["match_format"] == "T20I", "t20i", "ipl")

    comp_agg = b_press.groupby(["bowler_id", "bowler_canonical_name", "comp_type"]).agg(
        legal_balls=("bowler_charged_runs", "count"),
        runs_conceded=("bowler_charged_runs", "sum"),
        matches=("match_id", "nunique"),
        wickets=("is_bowler_wicket", "sum")
    ).reset_index()

    comp_agg["overs"] = comp_agg["legal_balls"] / 6.0
    comp_agg["econ"] = comp_agg["runs_conceded"] / comp_agg["overs"]

    # Pivot to wide format
    ipl_split = comp_agg[comp_agg["comp_type"] == "ipl"].rename(columns={
        "legal_balls": "ipl_pressure_balls", "runs_conceded": "ipl_pressure_runs",
        "matches": "ipl_pressure_matches", "wickets": "ipl_pressure_wickets", "econ": "ipl_pressure_econ"
    }).drop(columns=["comp_type", "overs"])

    t20i_split = comp_agg[comp_agg["comp_type"] == "t20i"].rename(columns={
        "legal_balls": "t20i_pressure_balls", "runs_conceded": "t20i_pressure_runs",
        "matches": "t20i_pressure_matches", "wickets": "t20i_pressure_wickets", "econ": "t20i_pressure_econ"
    }).drop(columns=["comp_type", "overs"])

    splits = pd.merge(ipl_split, t20i_split, on=["bowler_id", "bowler_canonical_name"], how="outer").fillna(0)
    return splits


def compute_bowler_phase_splits(df: pd.DataFrame, pressure_tiers: List[str] = ["HIGH", "EXTREME"]) -> pd.DataFrame:
    """Computes Powerplay, Middle, and Death overs performance under pressure for bowlers."""
    b_press = df[(df["is_legal_delivery"] == True) & (df["bowler_pressure_tier"].isin(pressure_tiers))].copy()

    phase_agg = b_press.groupby(["bowler_id", "bowler_canonical_name", "innings_stage"]).agg(
        legal_balls=("bowler_charged_runs", "count"),
        runs_conceded=("bowler_charged_runs", "sum"),
        wickets=("is_bowler_wicket", "sum")
    ).reset_index()

    phase_agg["overs"] = phase_agg["legal_balls"] / 6.0
    phase_agg["econ"] = phase_agg["runs_conceded"] / phase_agg["overs"]

    pivoted = phase_agg.pivot_table(
        index=["bowler_id", "bowler_canonical_name"],
        columns="innings_stage",
        values=["legal_balls", "runs_conceded", "wickets", "econ"],
        fill_value=0
    )
    pivoted.columns = [f"{col[1].lower()}_pressure_{col[0]}" for col in pivoted.columns]
    return pivoted.reset_index()


def apply_bowler_empirical_bayes_shrinkage(
    eligible_df: pd.DataFrame,
    target_col: str = "pressure_econ",
    volume_col: str = "pressure_legal_balls"
) -> Tuple[pd.Series, float, float]:
    """
    Applies Empirical Bayes shrinkage to bowler metrics (e.g. economy or wicket rate).
    """
    x = eligible_df[target_col].values
    n = eligible_df[volume_col].values
    
    if len(eligible_df) == 0 or np.sum(n) == 0:
        return pd.Series(dtype=float, index=eligible_df.index), 8.0, 50.0

    mu_0 = float(np.average(x, weights=n))
    var_between = float(np.var(x, ddof=1))
    
    # Within-bowler variance scaling for economy (per 6 balls)
    avg_over_var = 1.8 ** 2 * 36.0
    k_shrink = float(avg_over_var / max(var_between, 0.1))
    k_shrink = np.clip(k_shrink, 40.0, 100.0)

    weights = n / (n + k_shrink)
    shrunk_values = weights * x + (1.0 - weights) * mu_0

    return pd.Series(shrunk_values, index=eligible_df.index), mu_0, k_shrink


def run_bowler_match_level_bootstrap(
    df: pd.DataFrame,
    eligible_bowler_ids: List[int],
    n_iterations: int = 1000,
    random_seed: int = 42,
    pressure_tiers: List[str] = ["HIGH", "EXTREME"]
) -> pd.DataFrame:
    """
    Performs match-level cluster bootstrap resampling for bowlers under pressure
    to calculate 95% confidence intervals for pressure economy and wickets.
    """
    rng = np.random.default_rng(random_seed)

    b_press = df[
        (df["is_legal_delivery"] == True) &
        (df["bowler_pressure_tier"].isin(pressure_tiers)) &
        (df["bowler_id"].isin(eligible_bowler_ids))
    ].copy()

    pm_df = b_press.groupby(["bowler_id", "match_id"]).agg(
        runs=("bowler_charged_runs", "sum"),
        balls=("bowler_charged_runs", "count"),
        wickets=("is_bowler_wicket", "sum")
    ).reset_index()

    bootstrap_results = []

    for bid in eligible_bowler_ids:
        sub = pm_df[pm_df["bowler_id"] == bid]
        m_count = len(sub)
        if m_count == 0:
            continue

        runs_arr = sub["runs"].values
        balls_arr = sub["balls"].values
        wickets_arr = sub["wickets"].values

        sampled_indices = rng.choice(m_count, size=(n_iterations, m_count), replace=True)

        boot_runs = runs_arr[sampled_indices].sum(axis=1)
        boot_balls = balls_arr[sampled_indices].sum(axis=1)
        boot_wkts = wickets_arr[sampled_indices].sum(axis=1)

        valid_mask = boot_balls > 0
        boot_econ = np.where(valid_mask, boot_runs / (boot_balls / 6.0), np.nan)
        boot_wkt_per_over = np.where(valid_mask, (boot_wkts * 6.0) / boot_balls, np.nan)

        boot_econ_valid = boot_econ[~np.isnan(boot_econ)]
        boot_wkt_valid = boot_wkt_per_over[~np.isnan(boot_wkt_per_over)]

        econ_ci_lower = float(np.percentile(boot_econ_valid, 2.5)) if len(boot_econ_valid) > 0 else np.nan
        econ_ci_upper = float(np.percentile(boot_econ_valid, 97.5)) if len(boot_econ_valid) > 0 else np.nan
        econ_se = float(np.std(boot_econ_valid, ddof=1)) if len(boot_econ_valid) > 1 else np.nan

        wkt_ci_lower = float(np.percentile(boot_wkt_valid, 2.5)) if len(boot_wkt_valid) > 0 else np.nan
        wkt_ci_upper = float(np.percentile(boot_wkt_valid, 97.5)) if len(boot_wkt_valid) > 0 else np.nan
        wkt_se = float(np.std(boot_wkt_valid, ddof=1)) if len(boot_wkt_valid) > 1 else np.nan

        bootstrap_results.append({
            "bowler_id": bid,
            "boot_econ_ci_lower": econ_ci_lower,
            "boot_econ_ci_upper": econ_ci_upper,
            "boot_econ_se": econ_se,
            "boot_wkt_ci_lower": wkt_ci_lower,
            "boot_wkt_ci_upper": wkt_ci_upper,
            "boot_wkt_se": wkt_se
        })

    return pd.DataFrame(bootstrap_results)


def build_bowler_performance_dataset(
    df: pd.DataFrame,
    min_pressure_balls: int = 90,
    min_pressure_matches: int = 10,
    n_bootstrap: int = 1000,
    random_seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Executes the complete Phase 4 Bowler Performance pipeline.
    
    Returns:
        (eligible_bowlers_df, full_bowler_metrics_df, eligibility_audit_df)
    """
    # 1. Compute aggregates and tier breakdown
    full_metrics, tier_breakdown = compute_bowler_aggregates(df)

    # 2. Compute match consistency
    consistency = compute_bowler_match_consistency(df)
    full_metrics = pd.merge(full_metrics, consistency.drop(columns=["bowler_canonical_name"]), on="bowler_id", how="left")

    # 3. Compute competition splits
    comp_splits = compute_bowler_competition_splits(df)
    full_metrics = pd.merge(full_metrics, comp_splits.drop(columns=["bowler_canonical_name"]), on="bowler_id", how="left").fillna(0)

    # 4. Compute phase splits
    phase_splits = compute_bowler_phase_splits(df)
    full_metrics = pd.merge(full_metrics, phase_splits.drop(columns=["bowler_canonical_name"]), on="bowler_id", how="left").fillna(0)

    # 5. Build eligibility audit
    full_metrics["meets_ball_threshold"] = full_metrics["pressure_legal_balls"] >= min_pressure_balls
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
        "bowler_id", "bowler_canonical_name", "pressure_legal_balls", "pressure_matches",
        "pressure_runs_conceded", "pressure_wickets", "pressure_econ", "normal_econ",
        "is_eligible", "eligibility_status"
    ]].copy()

    # Filter eligible
    eligible_df = full_metrics[full_metrics["is_eligible"]].copy()

    # 6. Apply Empirical Bayes shrinkage
    shrunk_econ, mu_econ, k_econ = apply_bowler_empirical_bayes_shrinkage(eligible_df, "pressure_econ", "pressure_legal_balls")
    eligible_df["pressure_econ_eb"] = shrunk_econ

    eligible_df["pressure_wkt_per_over"] = (eligible_df["pressure_wickets"] * 6.0) / eligible_df["pressure_legal_balls"]
    shrunk_wkt, mu_wkt, k_wkt = apply_bowler_empirical_bayes_shrinkage(eligible_df, "pressure_wkt_per_over", "pressure_legal_balls")
    eligible_df["pressure_wkt_per_over_eb"] = shrunk_wkt

    # 7. Run cluster bootstrap
    boot_df = run_bowler_match_level_bootstrap(
        df,
        eligible_bowler_ids=eligible_df["bowler_id"].tolist(),
        n_iterations=n_bootstrap,
        random_seed=random_seed
    )
    eligible_df = pd.merge(eligible_df, boot_df, on="bowler_id", how="left")

    return eligible_df, full_metrics, audit_df

