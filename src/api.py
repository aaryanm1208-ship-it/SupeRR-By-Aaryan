"""
REST API Backend for SupeRR Selector Season 2.
Serves verified analytical datasets, player profiles, research outputs, and figures.
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from src import config

app = FastAPI(
    title="SupeRR Selector — Elite Cricket Pressure Intelligence API",
    description="Backend API for SupeRR Selector Season 2 Round 1 Analytics Platform",
    version="2.0.0"
)

# Enable CORS for local development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File Paths
RANKINGS_DIR = os.path.join(config.OUTPUT_DIR, "rankings")
REPORTS_DIR = os.path.join(config.OUTPUT_DIR, "reports")
FIGURES_DIR = os.path.join(config.OUTPUT_DIR, "figures")
FINAL_SUBMISSION_DIR = os.path.join(config.PROJECT_ROOT, "FINAL_SUBMISSION")
STATIC_DIR = os.path.join(config.PROJECT_ROOT, "static")


def load_csv_safe(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


# Cache dataframes in memory for sub-millisecond response times
_batters_df: Optional[pd.DataFrame] = None
_bowlers_df: Optional[pd.DataFrame] = None
_explanations_df: Optional[pd.DataFrame] = None
_bootstrap_df: Optional[pd.DataFrame] = None
_stability_df: Optional[pd.DataFrame] = None


def get_batters_data() -> pd.DataFrame:
    global _batters_df
    if _batters_df is None:
        p = os.path.join(FINAL_SUBMISSION_DIR, "batter_rankings_final.csv")
        if not os.path.exists(p):
            p = os.path.join(RANKINGS_DIR, "batter_rankings_final.csv")
        _batters_df = load_csv_safe(p)
    return _batters_df


def get_bowlers_data() -> pd.DataFrame:
    global _bowlers_df
    if _bowlers_df is None:
        p = os.path.join(FINAL_SUBMISSION_DIR, "bowler_rankings_final.csv")
        if not os.path.exists(p):
            p = os.path.join(RANKINGS_DIR, "bowler_rankings_final.csv")
        _bowlers_df = load_csv_safe(p)
    return _bowlers_df


def get_explanations_data() -> pd.DataFrame:
    global _explanations_df
    if _explanations_df is None:
        p = os.path.join(FINAL_SUBMISSION_DIR, "ranking_explanations.csv")
        if not os.path.exists(p):
            p = os.path.join(RANKINGS_DIR, "ranking_explanations.csv")
        _explanations_df = load_csv_safe(p)
    return _explanations_df


def get_bootstrap_data() -> pd.DataFrame:
    global _bootstrap_df
    if _bootstrap_df is None:
        p = os.path.join(REPORTS_DIR, "bootstrap_results.csv")
        _bootstrap_df = load_csv_safe(p)
    return _bootstrap_df


def sanitize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitizes NaN and infinite values for valid JSON serialization."""
    res = {}
    for k, v in d.items():
        if isinstance(v, (float, np.floating)):
            if np.isnan(v) or np.isinf(v):
                res[k] = None
            else:
                res[k] = round(float(v), 2)
        elif isinstance(v, (int, np.integer)):
            res[k] = int(v)
        elif pd.isna(v):
            res[k] = None
        else:
            res[k] = v
    return res


# ---------------- API ENDPOINTS ----------------

@app.get("/api/summary")
def get_summary():
    """Returns high-level platform summary and dataset metrics."""
    batters = get_batters_data()
    bowlers = get_bowlers_data()
    explanations = get_explanations_data()

    top_batter = batters.iloc[0] if len(batters) > 0 else {}
    top_bowler = bowlers.iloc[0] if len(bowlers) > 0 else {}

    return {
        "title": "SupeRR Selector",
        "subtitle": "Elite Pressure Performance Intelligence",
        "season": "Season 2 — Round 1 Challenge",
        "data_scope": {
            "competitions": 139,
            "matches_analyzed": 853,
            "deliveries_analyzed": 193988,
            "deliveries_unfiltered": 200999,
            "super_over_balls_isolated": 26,
            "innings_reconciled": 1652,
            "innings_reconciliation_pass_rate": "100.0%",
            "ipl_matches": 371,
            "t20i_matches": 482,
            "seasons": "2022–2026"
        },
        "dataset_scope": {
            "total_matches": 853,
            "total_deliveries": 193988,
            "eligible_batters": len(batters),
            "eligible_bowlers": len(bowlers),
            "super_over_balls": 26,
            "innings_verified": 1652
        },
        "cohort_counts": {
            "eligible_batters": len(batters),
            "total_batters_evaluated": 824,
            "eligible_bowlers": len(bowlers),
            "total_bowlers_evaluated": 596
        },
        "thresholds": {
            "batters": "≥ 75 pressure balls faced across ≥ 10 pressure matches",
            "bowlers": "≥ 90 pressure legal balls bowled across ≥ 10 pressure matches"
        },
        "top_performers": {
            "batter": {
                "rank": 1,
                "name": top_batter.get("striker_canonical_name", "Namboori Tilak Varma"),
                "id": int(top_batter.get("striker_id", 0)),
                "rating": round(float(top_batter.get("composite_rating", 0.0)), 1),
                "pressure_sr": round(float(top_batter.get("pressure_sr", 0.0)), 1),
                "sr_delta": round(float(top_batter.get("sr_delta", 0.0)), 1),
                "pressure_balls": int(top_batter.get("pressure_balls", 0)),
                "rpd": round(float(top_batter.get("pressure_rpd", 0.0)), 1),
                "positive_impact_pct": round(float(top_batter.get("positive_contribution_pct", 0.0)), 1),
                "tactical_archetype": "Middle-Overs Aggressor & Finisher"
            },
            "bowler": {
                "rank": 1,
                "name": top_bowler.get("bowler_canonical_name", "Mujeeb Ur Rahman"),
                "id": int(top_bowler.get("bowler_id", 0)),
                "rating": round(float(top_bowler.get("composite_rating", 0.0)), 1),
                "pressure_econ": round(float(top_bowler.get("pressure_econ", 0.0)), 2),
                "phase_adj_econ": round(float(top_bowler.get("phase_adj_econ", 0.0)), 2),
                "runs_saved_per_over": round(float(top_bowler.get("runs_saved_per_over", 0.0)), 2),
                "pressure_wickets": int(top_bowler.get("pressure_wickets", 0)),
                "dot_pct": round(float(top_bowler.get("pressure_dot_pct", 0.0)), 1),
                "clutch_spell_pct": round(float(top_bowler.get("clutch_spell_pct", 0.0)), 1),
                "tactical_archetype": "Powerplay & Middle Mystery Spinner"
            }
        },
        "pressure_par": {
            "death_overs_par_econ": 10.46,
            "middle_overs_par_econ": 8.01,
            "powerplay_par_econ": 8.46,
            "death_overs_par_sr": 144.77,
            "middle_overs_par_sr": 132.45
        },
        "key_findings": [
            "Tilak Varma (+44.3 SR delta) and Dhruv Jurel (+61.6 SR delta) are the foremost clutch batting accelerants in world cricket.",
            "Rinku Singh exhibits unprecedented wicket survival under pressure: 68.7 runs per dismissal (dismissed only 6 times in 234 pressure deliveries).",
            "Jasprit Bumrah concedes 7.62 rpo at the death, saving +1.52 runs/over relative to the 10.46 death par, matching Rashid Khan (+1.52 RSAA).",
            "Mujeeb Ur Rahman chokes scoring under pressure with a 6.69 economy and 45.4% dot ball rate across 280 legal deliveries.",
            "Pre-delivery causal reconstruction completely prevents future leakage: 1,652 out of 1,652 innings mathematically verified."
        ]
    }


@app.get("/api/batters")
def get_batters(
    search: Optional[str] = None,
    sort_by: str = "rank",
    order: str = "asc",
    min_balls: int = 0,
    min_rating: float = 0.0,
    limit: int = 100
):
    """Returns all eligible batters with filtering and sorting."""
    df = get_batters_data().copy()
    if df.empty:
        return {"total": 0, "batters": []}

    # Filter
    if search and isinstance(search, str) and search.strip():
        df = df[df["striker_canonical_name"].str.contains(search.strip(), case=False, na=False)]
    if min_balls and min_balls > 0:
        df = df[df["pressure_balls"] >= min_balls]
    if min_rating and min_rating > 0:
        df = df[df["composite_rating"] >= min_rating]

    # Sort
    valid_sort_cols = {
        "rank": "rank",
        "name": "striker_canonical_name",
        "composite_rating": "composite_rating",
        "pressure_sr": "pressure_sr",
        "pressure_sr_eb": "pressure_sr_eb",
        "normal_sr": "normal_sr",
        "sr_delta": "sr_delta",
        "pressure_balls": "pressure_balls",
        "pressure_matches": "pressure_matches",
        "pressure_runs": "pressure_runs",
        "pressure_rpd": "pressure_rpd",
        "positive_contribution_pct": "positive_contribution_pct",
        "death_pressure_pct": "death_pressure_pct"
    }
    col = valid_sort_cols.get(sort_by, "rank")
    ascending = (order.lower() == "asc")
    df = df.sort_values(by=col, ascending=ascending)

    records = []
    for _, r in df.head(limit).iterrows():
        records.append({
            "rank": int(r["rank"]),
            "player_id": int(r["striker_id"]),
            "player_name": r["striker_canonical_name"],
            "composite_rating": round(float(r["composite_rating"]), 1),
            "pressure_balls": int(r["pressure_balls"]),
            "pressure_matches": int(r["pressure_matches"]),
            "pressure_runs": int(r["pressure_runs"]),
            "pressure_sr": round(float(r["pressure_sr"]), 1),
            "pressure_sr_eb": round(float(r["pressure_sr_eb"]), 1),
            "normal_sr": round(float(r["normal_sr"]), 1),
            "sr_delta": round(float(r["sr_delta"]), 1),
            "pressure_rpd": round(float(r["pressure_rpd"]), 1),
            "pressure_rpd_eb": round(float(r["pressure_rpd_eb"]), 1),
            "pressure_boundary_pct": round(float(r["pressure_boundary_pct"]), 1),
            "pressure_dot_pct": round(float(r["pressure_dot_pct"]), 1),
            "positive_contribution_pct": round(float(r["positive_contribution_pct"]), 1),
            "boot_sr_ci_lower": round(float(r.get("boot_sr_ci_lower", 0.0)), 1),
            "boot_sr_ci_upper": round(float(r.get("boot_sr_ci_upper", 0.0)), 1),
            "death_pressure_balls": int(r.get("death_pressure_balls", 0)),
            "death_pressure_pct": round(float(r.get("death_pressure_pct", 0.0)), 1),
            "ipl_pressure_balls": int(r.get("ipl_pressure_balls", 0)),
            "ipl_pressure_sr": round(float(r.get("ipl_pressure_sr", 0.0)), 1),
            "t20i_pressure_balls": int(r.get("t20i_pressure_balls", 0)),
            "t20i_pressure_sr": round(float(r.get("t20i_pressure_sr", 0.0)), 1),
            "tactical_archetype": "High-Leverage Death Finisher" if r.get("death_pressure_pct", 0) > 40 else "Middle-Overs Aggressor"
        })

    return {
        "total": len(df),
        "count": len(records),
        "batters": records
    }


@app.get("/api/bowlers")
def get_bowlers(
    search: Optional[str] = None,
    sort_by: str = "rank",
    order: str = "asc",
    min_balls: int = 0,
    min_rating: float = 0.0,
    role: Optional[str] = None,
    limit: int = 200
):
    """Returns all eligible bowlers with filtering and sorting."""
    df = get_bowlers_data().copy()
    if df.empty:
        return {"total": 0, "bowlers": []}

    # Filter
    if search and isinstance(search, str) and search.strip():
        df = df[df["bowler_canonical_name"].str.contains(search.strip(), case=False, na=False)]
    if min_balls and min_balls > 0:
        df = df[df["pressure_legal_balls"] >= min_balls]
    if min_rating and min_rating > 0:
        df = df[df["composite_rating"] >= min_rating]
    if role and role.lower() == "death":
        df = df[df.get("death_pressure_pct", 0) > 40.0]
    elif role and role.lower() == "control":
        df = df[df.get("death_pressure_pct", 0) <= 40.0]

    # Sort
    valid_sort_cols = {
        "rank": "rank",
        "name": "bowler_canonical_name",
        "composite_rating": "composite_rating",
        "pressure_econ": "pressure_econ",
        "phase_adj_econ": "phase_adj_econ",
        "runs_saved_per_over": "runs_saved_per_over",
        "pressure_wickets": "pressure_wickets",
        "pressure_legal_balls": "pressure_legal_balls",
        "pressure_matches": "pressure_matches",
        "pressure_dot_pct": "pressure_dot_pct",
        "clutch_spell_pct": "clutch_spell_pct",
        "death_pressure_pct": "death_pressure_pct"
    }
    col = valid_sort_cols.get(sort_by, "rank")
    ascending = (order.lower() == "asc")
    df = df.sort_values(by=col, ascending=ascending)

    records = []
    for _, r in df.head(limit).iterrows():
        records.append({
            "rank": int(r["rank"]),
            "player_id": int(r["bowler_id"]),
            "player_name": r["bowler_canonical_name"],
            "composite_rating": round(float(r["composite_rating"]), 1),
            "pressure_legal_balls": int(r["pressure_legal_balls"]),
            "pressure_overs": round(float(r["pressure_overs"]), 1),
            "pressure_matches": int(r["pressure_matches"]),
            "pressure_runs_conceded": int(r["pressure_runs_conceded"]),
            "pressure_econ": round(float(r["pressure_econ"]), 2),
            "pressure_econ_eb": round(float(r["pressure_econ_eb"]), 2),
            "normal_econ": round(float(r["normal_econ"]), 2),
            "econ_delta": round(float(r["econ_delta"]), 2),
            "phase_adj_econ": round(float(r["phase_adj_econ"]), 2),
            "runs_saved_per_over": round(float(r["runs_saved_per_over"]), 2),
            "pressure_wickets": int(r["pressure_wickets"]),
            "pressure_dot_pct": round(float(r["pressure_dot_pct"]), 1),
            "pressure_boundary_pct": round(float(r["pressure_boundary_pct"]), 1),
            "clutch_spell_pct": round(float(r["clutch_spell_pct"]), 1),
            "boot_econ_ci_lower": round(float(r.get("boot_econ_ci_lower", 0.0)), 2),
            "boot_econ_ci_upper": round(float(r.get("boot_econ_ci_upper", 0.0)), 2),
            "death_pressure_balls": int(r.get("death_pressure_legal_balls", 0)),
            "death_pressure_pct": round(float(r.get("death_pressure_pct", 0.0)), 1),
            "ipl_pressure_balls": int(r.get("ipl_pressure_balls", 0)),
            "ipl_pressure_econ": round(float(r.get("ipl_pressure_econ", 0.0)), 2),
            "t20i_pressure_balls": int(r.get("t20i_pressure_balls", 0)),
            "t20i_pressure_econ": round(float(r.get("t20i_pressure_econ", 0.0)), 2),
            "tactical_archetype": "Death Overs Specialist / Enforcer" if r.get("death_pressure_pct", 0) > 40 else "Mystery Spinner / High-Leverage Control"
        })

    return {
        "total": len(df),
        "count": len(records),
        "bowlers": records
    }


@app.get("/api/player/{category}/{player_id}")
def get_player_detail(category: str, player_id: int):
    """Returns deep-dive analytics for a single player."""
    cat = category.upper()
    if cat == "BATTER":
        df = get_batters_data()
        match = df[df["striker_id"] == player_id]
        if match.empty:
            raise HTTPException(status_code=404, detail=f"Batter with ID {player_id} not found")
        row = match.iloc[0].to_dict()

        # Check narrative justification
        exp = get_explanations_data()
        exp_match = exp[(exp["category"] == "BATTER") & (exp["player_id"] == player_id)]
        justification = exp_match.iloc[0]["statistical_justification"] if not exp_match.empty else None

        return {
            "category": "BATTER",
            "player_id": player_id,
            "player_name": row["striker_canonical_name"],
            "rank": int(row["rank"]),
            "composite_rating": round(float(row["composite_rating"]), 1),
            "justification": justification,
            "core_metrics": {
                "pressure_balls": int(row["pressure_balls"]),
                "pressure_matches": int(row["pressure_matches"]),
                "pressure_runs": int(row["pressure_runs"]),
                "pressure_sr": round(float(row["pressure_sr"]), 1),
                "pressure_sr_eb": round(float(row["pressure_sr_eb"]), 1),
                "normal_sr": round(float(row["normal_sr"]), 1),
                "sr_delta": round(float(row["sr_delta"]), 1),
                "pressure_rpd": round(float(row["pressure_rpd"]), 1),
                "positive_contribution_pct": round(float(row["positive_contribution_pct"]), 1),
                "pressure_boundary_pct": round(float(row["pressure_boundary_pct"]), 1),
                "pressure_dot_pct": round(float(row["pressure_dot_pct"]), 1),
                "ci_lower": round(float(row.get("boot_sr_ci_lower", 0.0)), 1),
                "ci_upper": round(float(row.get("boot_sr_ci_upper", 0.0)), 1),
                "standard_error": round(float(row.get("boot_sr_se", 0.0)), 1)
            },
            "phase_split": {
                "death_balls": int(row.get("death_pressure_balls", 0)),
                "death_runs": int(row.get("death_pressure_runs", 0)),
                "death_sr": round(float(row.get("death_pressure_sr", 0.0)), 1),
                "middle_balls": int(row.get("middle_pressure_balls", 0)),
                "middle_runs": int(row.get("middle_pressure_runs", 0)),
                "middle_sr": round(float(row.get("middle_pressure_sr", 0.0)), 1),
                "powerplay_balls": int(row.get("powerplay_pressure_balls", 0)),
                "powerplay_runs": int(row.get("powerplay_pressure_runs", 0)),
                "powerplay_sr": round(float(row.get("powerplay_pressure_sr", 0.0)), 1)
            },
            "competition_split": {
                "ipl_balls": int(row.get("ipl_pressure_balls", 0)),
                "ipl_runs": int(row.get("ipl_pressure_runs", 0)),
                "ipl_sr": round(float(row.get("ipl_pressure_sr", 0.0)), 1),
                "t20i_balls": int(row.get("t20i_pressure_balls", 0)),
                "t20i_runs": int(row.get("t20i_pressure_runs", 0)),
                "t20i_sr": round(float(row.get("t20i_pressure_sr", 0.0)), 1)
            }
        }

    elif cat == "BOWLER":
        df = get_bowlers_data()
        match = df[df["bowler_id"] == player_id]
        if match.empty:
            raise HTTPException(status_code=404, detail=f"Bowler with ID {player_id} not found")
        row = match.iloc[0].to_dict()

        exp = get_explanations_data()
        exp_match = exp[(exp["category"] == "BOWLER") & (exp["player_id"] == player_id)]
        justification = exp_match.iloc[0]["statistical_justification"] if not exp_match.empty else None

        return {
            "category": "BOWLER",
            "player_id": player_id,
            "player_name": row["bowler_canonical_name"],
            "rank": int(row["rank"]),
            "composite_rating": round(float(row["composite_rating"]), 1),
            "justification": justification,
            "core_metrics": {
                "pressure_legal_balls": int(row["pressure_legal_balls"]),
                "pressure_overs": round(float(row["pressure_overs"]), 1),
                "pressure_matches": int(row["pressure_matches"]),
                "pressure_runs_conceded": int(row["pressure_runs_conceded"]),
                "pressure_econ": round(float(row["pressure_econ"]), 2),
                "phase_adj_econ": round(float(row["phase_adj_econ"]), 2),
                "runs_saved_per_over": round(float(row["runs_saved_per_over"]), 2),
                "pressure_wickets": int(row["pressure_wickets"]),
                "pressure_dot_pct": round(float(row["pressure_dot_pct"]), 1),
                "pressure_boundary_pct": round(float(row["pressure_boundary_pct"]), 1),
                "clutch_spell_pct": round(float(row["clutch_spell_pct"]), 1),
                "ci_lower": round(float(row.get("boot_econ_ci_lower", 0.0)), 2),
                "ci_upper": round(float(row.get("boot_econ_ci_upper", 0.0)), 2),
                "standard_error": round(float(row.get("boot_econ_se", 0.0)), 2)
            },
            "phase_split": {
                "death_balls": int(row.get("death_pressure_legal_balls", 0)),
                "death_runs": int(row.get("death_pressure_runs_conceded", 0)),
                "death_econ": round(float(row.get("death_pressure_econ", 0.0)), 2),
                "death_wickets": int(row.get("death_pressure_wickets", 0)),
                "middle_balls": int(row.get("middle_pressure_legal_balls", 0)),
                "middle_runs": int(row.get("middle_pressure_runs_conceded", 0)),
                "middle_econ": round(float(row.get("middle_pressure_econ", 0.0)), 2),
                "middle_wickets": int(row.get("middle_pressure_wickets", 0)),
                "powerplay_balls": int(row.get("powerplay_pressure_legal_balls", 0)),
                "powerplay_runs": int(row.get("powerplay_pressure_runs_conceded", 0)),
                "powerplay_econ": round(float(row.get("powerplay_pressure_econ", 0.0)), 2),
                "powerplay_wickets": int(row.get("powerplay_pressure_wickets", 0))
            },
            "competition_split": {
                "ipl_balls": int(row.get("ipl_pressure_balls", 0)),
                "ipl_runs": int(row.get("ipl_pressure_runs", 0)),
                "ipl_econ": round(float(row.get("ipl_pressure_econ", 0.0)), 2),
                "ipl_wickets": int(row.get("ipl_pressure_wickets", 0)),
                "t20i_balls": int(row.get("t20i_pressure_balls", 0)),
                "t20i_runs": int(row.get("t20i_pressure_runs", 0)),
                "t20i_econ": round(float(row.get("t20i_pressure_econ", 0.0)), 2),
                "t20i_wickets": int(row.get("t20i_pressure_wickets", 0))
            }
        }
    else:
        raise HTTPException(status_code=400, detail="Category must be 'BATTER' or 'BOWLER'")


@app.get("/api/explanations")
def get_explanations():
    """Returns official justification narratives for Top 10 players."""
    df = get_explanations_data()
    return {"explanations": df.to_dict(orient="records")}


@app.get("/api/research")
def get_research_data():
    """Returns robustness metrics, model correlations, and bootstrap distribution summary."""
    boot_df = get_bootstrap_data()
    return {
        "model_correlations": {
            "batters_model_c_vs_a": {"spearman_rho": 0.921, "kendall_tau": 0.775},
            "bowlers_model_c_vs_a": {"spearman_rho": 0.519, "kendall_tau": 0.381}
        },
        "bootstrap_results": boot_df.to_dict(orient="records") if not boot_df.empty else []
    }


@app.get("/api/figures")
def get_figures_catalog():
    """Returns catalog of the 12 publication-grade figures with interpretations."""
    catalog = [
        {
            "id": "fig01",
            "title": "Top 10 Batters Composite Rating",
            "filename": "fig01_top_batters_composite_rating.png",
            "description": "Rankings of the 10 most reliable batters under high & extreme pressure, showing composite ratings (0-100), observed pressure strike rate, and strike rate delta over normal baseline.",
            "takeaway": "Namboori Tilak Varma leads with a 74.1 composite score, pairing an explosive 183.0 pressure strike rate with a massive +44.3 clutch elevation over baseline."
        },
        {
            "id": "fig02",
            "title": "Top 10 Bowlers Composite Rating",
            "filename": "fig02_top_bowlers_composite_rating.png",
            "description": "Rankings of the 10 most reliable bowlers under pressure, detailing phase-adjusted economy, raw pressure economy, runs saved per over, and wicket tallies.",
            "takeaway": "Mujeeb Ur Rahman (74.6) and Mohammad Nawaz (70.8) lead overall run suffocation, while Rashid Khan provides unmatched volume (945 balls, 62 wickets)."
        },
        {
            "id": "fig03",
            "title": "Batter Strike Rate Elevation Scatter",
            "filename": "fig03_batter_strike_rate_scatter.png",
            "description": "Pressure Strike Rate plotted against Normal Baseline Strike Rate for all 86 eligible batters. The dashed par line denotes zero delta.",
            "takeaway": "Top 10 batters populate the top-left quadrant of the scatter, dramatically elevating their scoring speed under pressure while inferior performers deflate below the par line."
        },
        {
            "id": "fig04",
            "title": "Bowler Economy Control Scatter",
            "filename": "fig04_bowler_economy_rate_scatter.png",
            "description": "High & Extreme Pressure Economy plotted against Normal Baseline Economy for all 154 eligible bowlers.",
            "takeaway": "Elite pressure suppressors hold economy rates between 5.17 and 7.62 rpo even when match situations escalate into extreme difficulty."
        },
        {
            "id": "fig05",
            "title": "Clutch Delta Distributions",
            "filename": "fig05_clutch_delta_distributions.png",
            "description": "Dual histograms showing the distribution of Batting Strike Rate Deltas and Bowling Runs Saved Above Average per Over across the entire eligible cohort.",
            "takeaway": "The cohort exhibits a broad spread, confirming that true pressure performance is rare and highly differentiated from average baseline ability."
        },
        {
            "id": "fig06",
            "title": "Match Reliability & Impact Frequency",
            "filename": "fig06_match_consistency_dispersion.png",
            "description": "Match-level high-impact contribution rate (%) for Top 10 Batters, alongside clutch spell frequency (%) for Top 10 Bowlers.",
            "takeaway": "Top batters deliver positive game-altering impacts in 57% to 80% of pressure matches, proving their success is not an artifact of a single outlier innings."
        },
        {
            "id": "fig07",
            "title": "Empirical Bayes Shrinkage Effect",
            "filename": "fig07_empirical_bayes_shrinkage.png",
            "description": "Raw observed rates vs Empirical Bayes shrunk rates plotted against sample exposure (balls).",
            "takeaway": "Bayesian regularization pulls small-sample extremes toward population priors while preserving the dominance of high-volume veterans."
        },
        {
            "id": "fig08",
            "title": "Model Ranking Stability Bump Chart",
            "filename": "fig08_model_ranking_stability_bump.png",
            "description": "Bump chart tracking the ranking stability of the Top 10 Batters across Model C (Unified), Model A (Chasing), and Model D (Strict +20% threshold).",
            "takeaway": "Top 10 players demonstrate remarkable ordinal stability across distinct mathematical formulations, confirming methodological robustness."
        },
        {
            "id": "fig09",
            "title": "Cross-Tournament Portability (IPL vs T20I)",
            "filename": "fig09_ipl_vs_t20i_performance.png",
            "description": "Paired bar comparison illustrating player performance in the IPL franchise environment versus Senior T20 International fixtures.",
            "takeaway": "Elite performers demonstrate cross-context adaptability, excelling against both elite IPL bowling attacks and international tournament pressure."
        },
        {
            "id": "fig10",
            "title": "Bootstrap 95% Confidence Intervals",
            "filename": "fig10_bootstrap_confidence_intervals.png",
            "description": "Forest plot presenting 95% match-level cluster bootstrap confidence bounds for Top 10 Batters (SR) and Bowlers (Economy).",
            "takeaway": "Cluster bootstrapping over matches accounts for delivery correlation, confirming statistically defensible margins separating elite players from average peers."
        },
        {
            "id": "fig11",
            "title": "Pressure Tier Progression Trajectory",
            "filename": "fig11_pressure_tier_progression.png",
            "description": "Performance trajectories across escalating pressure tiers (Normal → Elevated → High → Extreme).",
            "takeaway": "Top batters maintain positive strike rate slopes as pressure rises, whereas average batters show steep degradation."
        },
        {
            "id": "fig12",
            "title": "Efficiency vs Uncertainty Frontier",
            "filename": "fig12_performance_vs_uncertainty.png",
            "description": "Player Composite Rating plotted against Bootstrap Standard Error, delineating the frontier between certainty and upside.",
            "takeaway": "High-volume stalwarts (Rashid Khan, David Miller) occupy the low-uncertainty high-rating quadrant, while dynamic risers offer ceiling upside."
        }
    ]
    return catalog


# Mount Static Files and Figures
if os.path.exists(FIGURES_DIR):
    app.mount("/figures", StaticFiles(directory=FIGURES_DIR), name="figures")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_index():
    """Serves the main single page web application."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"status": "Frontend initialized. Index file pending compilation."})


@app.get("/download/{filename}")
def download_artifact(filename: str):
    """Secure endpoint to download official submission reports and datasets."""
    allowed_files = {
        "methodology_report.pdf": os.path.join(FINAL_SUBMISSION_DIR, "methodology_report.pdf"),
        "methodology_report.md": os.path.join(FINAL_SUBMISSION_DIR, "methodology_report.md"),
        "FINAL_RESULTS_SUMMARY.md": os.path.join(FINAL_SUBMISSION_DIR, "FINAL_RESULTS_SUMMARY.md"),
        "batter_rankings_final.csv": os.path.join(FINAL_SUBMISSION_DIR, "batter_rankings_final.csv"),
        "bowler_rankings_final.csv": os.path.join(FINAL_SUBMISSION_DIR, "bowler_rankings_final.csv"),
        "ranking_explanations.csv": os.path.join(FINAL_SUBMISSION_DIR, "ranking_explanations.csv"),
        "final_submission_checklist.md": os.path.join(FINAL_SUBMISSION_DIR, "final_submission_checklist.md"),
        "submission_checklist.md": os.path.join(FINAL_SUBMISSION_DIR, "final_submission_checklist.md")
    }
    if filename not in allowed_files:
        raise HTTPException(status_code=404, detail="File not found or access restricted.")
    
    file_path = allowed_files[filename]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} does not exist on disk.")
    
    return FileResponse(file_path, filename=filename)

download_file = download_artifact


