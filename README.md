# SupeRR Selector Season 2: Elite Pressure Performance Intelligence System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)]()
[![Code Quality: Audited](https://img.shields.io/badge/Audit-Certified%20100%25-brightgreen.svg)]()

> **Master Analytical Submission for SupeRR Selector Season 2 — Round 1 Challenge**  
> An uncompromising, evidence-driven sports analytics intelligence system identifying and ranking the **10 most reliable batters** and **10 most reliable bowlers** under high and extreme pressure situations, derived exclusively from supplied historical IPL (2022–2026) and Senior Men's T20I ball-by-ball data.

---

## Table of Contents
1. [Core Results & Top 10 Rankings](#core-results--top-10-rankings)
2. [Key Innovations & Quantitative Breakthroughs](#key-innovations--quantitative-breakthroughs)
3. [Repository Architecture](#repository-architecture)
4. [Installation & Requirements](#installation--requirements)
5. [End-to-End Execution Guide](#end-to-end-execution-guide)
6. [Testing & Verification Suite](#testing--verification-suite)
7. [Mathematical Methodology](#mathematical-methodology)
8. [Submission Artifacts Checklist](#submission-artifacts-checklist)

---

## Core Results & Top 10 Rankings

### The 10 Most Reliable Batters Under Pressure

| Rank | Player Name | Tactical Archetype | Composite Rating | Pressure Balls | Pressure Matches | Pressure SR | Shrunk SR (EB) | Normal SR | SR Delta | Pressure RPD | Positive Impact % | 95% Bootstrap CI (SR) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Namboori Tilak Varma** | Middle-Overs Aggressor & Finisher | **74.1** | 312 | 23 | 183.0 | 180.0 | 138.7 | **+44.3** | 43.9 | 69.6% | [163.6, 200.3] |
| **2** | **Dhruv Jurel** | High-Leverage Death Finisher | **71.4** | 130 | 14 | 206.2 | 195.5 | 144.5 | **+61.6** | 38.3 | 57.1% | [170.8, 237.7] |
| **3** | **Rinku Singh** | Elite Clutch Chaser / Finisher | **69.8** | 234 | 19 | 176.1 | 173.0 | 146.9 | **+29.2** | 68.7 | 68.4% | [150.0, 200.0] |
| **4** | **David Miller** | Proven Match-Winner / Enforcer | **68.1** | 352 | 30 | 181.8 | 179.3 | 132.5 | **+49.3** | 40.0 | 63.3% | [157.3, 209.0] |
| **5** | **Gareth Delany** | Dynamic High-SR Disruptor | **67.1** | 116 | 10 | 177.6 | 171.7 | 105.1 | **+72.5** | 41.2 | 80.0% | [131.0, 214.3] |
| **6** | **Tim David** | High-Power Boundary Specialist | **65.6** | 320 | 31 | 194.4 | 190.5 | 179.2 | **+15.2** | 36.6 | 64.5% | [169.8, 218.4] |
| **7** | **Suryakumar Yadav** | 360-Degree Pressure Controller | **64.4** | 243 | 18 | 188.9 | 184.5 | 166.0 | **+22.9** | 32.8 | 72.2% | [163.5, 213.3] |
| **8** | **Ashutosh Sharma** | Clutch Lower-Order Impact Hitter | **60.9** | 121 | 14 | 190.1 | 181.9 | 155.1 | **+35.0** | 32.9 | 57.1% | [146.8, 230.9] |
| **9** | **Ayush Badoni** | Crisis Stabilizer / Late Accelerant | **59.4** | 148 | 12 | 158.8 | 157.2 | 136.2 | **+22.6** | 58.8 | 66.7% | [126.3, 190.0] |
| **10** | **Sikandar Raza** | All-Phase Counter-Attacking Anchor | **59.1** | 158 | 12 | 170.9 | 167.4 | 126.5 | **+44.4** | 38.6 | 66.7% | [139.7, 202.6] |

---

### The 10 Most Reliable Bowlers Under Pressure

| Rank | Player Name | Tactical Archetype | Composite Rating | Pressure Legal Balls | Pressure Matches | Pressure Econ | Phase-Adj Econ | Runs Saved / Over | Pressure Wickets | Dot Ball % | Clutch Spell % | 95% Bootstrap CI (Econ) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Mujeeb Ur Rahman** | Powerplay & Middle Control Spinner | **74.6** | 280 | 22 | 6.69 | 6.85 | **+1.80** | 25 | 45.4% | 72.7% | [5.61, 7.82] |
| **2** | **Mohammad Nawaz** | Clutch Defensive Arm-Ball Specialist | **70.8** | 344 | 24 | 6.75 | 7.26 | **+1.39** | 27 | 38.4% | 75.0% | [5.71, 7.79] |
| **3** | **Rashid Khan** | High-Volume Elite Match-Winner | **70.7** | 945 | 58 | 6.96 | 7.13 | **+1.52** | 62 | 38.2% | 72.4% | [6.48, 7.42] |
| **4** | **Abrar Ahmed** | High-Spin Mystery Strike Weapon | **69.8** | 230 | 16 | 6.03 | 6.29 | **+2.36** | 18 | 43.0% | 62.5% | [4.94, 7.25] |
| **5** | **Sufiyan Muqeem** | Rapid Wrist-Spin Run Suppressor | **69.3** | 144 | 10 | 5.17 | 5.50 | **+3.15** | 9 | 45.1% | 80.0% | [3.83, 7.08] |
| **6** | **Mitchell Santner** | Defensive Anchor & Pressure Bleeder | **67.4** | 601 | 40 | 6.89 | 7.12 | **+1.53** | 38 | 38.4% | 70.0% | [6.32, 7.47] |
| **7** | **Sunil Narine** | Franchise Suffocator & Boundary Wall | **66.1** | 507 | 31 | 6.75 | 6.97 | **+1.68** | 25 | 35.1% | 61.3% | [5.84, 7.58] |
| **8** | **Haris Rauf** | High-Pace Middle/Death Enforcer | **63.5** | 358 | 32 | 8.06 | 7.51 | **+1.14** | 28 | 37.4% | 53.1% | [7.28, 8.89] |
| **9** | **Matheesha Pathirana** | Sling-Action Death Overs Wicket-Taker | **63.1** | 422 | 36 | 8.22 | 7.63 | **+1.02** | 36 | 36.7% | 58.3% | [7.38, 9.07] |
| **10** | **Jasprit Bumrah** | Benchmark Precision & Run Saver | **58.2** | 578 | 48 | 7.62 | 7.13 | **+1.52** | 23 | 36.7% | 50.0% | [6.86, 8.37] |

---

## Key Innovations & Quantitative Breakthroughs

1. **Pre-Delivery Causal Reconstruction**:
   - Zero future information leakage. All pressure metrics use exclusively match state information known *before* the bowler bowls.
   - Reconciled **1,652 / 1,652 innings (100.0% pass rate)**.
2. **Phase-Adjusted Economy Rate (PAER)**:
   - Resolves the structural bias against death bowlers. Average pressure economy in death overs is **10.46 rpo** vs **8.01 rpo** in middle overs.
   - Bowlers are evaluated on **Runs Saved Above Average per Over (RSAA/over)** relative to phase-specific baselines.
3. **Empirical Bayes Shrinkage**:
   - Regularizes extreme observed strike rates and economy rates from smaller sample sizes toward population priors ($w_i = n_i / (n_i + K)$), eliminating random sample noise.
4. **Cluster Bootstrap Resampling (1,000 Draws)**:
   - Resamples entire matches to preserve delivery correlation, generating rigorous 95% confidence intervals and standard errors.
5. **Decoupled Asymmetric Role-Specific Pressure (Model C)**:
   - Distinguishes batter pressure (climbing chases, collapse recovery) from bowler pressure (razor-thin margins in the death overs).

---

## Repository Architecture

```
.
├── FINAL_SUBMISSION/               # Official submission directory
│   ├── methodology_report.pdf      # Complete 8-page publication PDF report
│   ├── methodology_report.md       # Complete research methodology text
│   ├── FINAL_RESULTS_SUMMARY.md    # Executive briefing summary
│   ├── batter_rankings_final.csv   # Top 86 eligible batters ranked
│   ├── bowler_rankings_final.csv   # Top 154 eligible bowlers ranked
│   ├── ranking_explanations.csv    # Deep tactical & statistical justifications
│   ├── pressure_definition_report.md # Mathematical derivation of Models A, B, C, D
│   ├── robustness_report.md        # 5-pillar statistical sensitivity suite
│   └── final_submission_checklist.md # Complete audit certification
├── src/                            # Modular production pipeline
│   ├── config.py                   # Global constants and hyperparameters
│   ├── loaders.py                  # Validated schema ingestion
│   ├── competition_filter.py       # IPL & Senior Men's T20I filtering
│   ├── cricket_rules.py            # MCC Law scoring engine
│   ├── match_state.py              # Pre-delivery causal state engine
│   ├── preprocessing.py            # Master preprocessing pipeline
│   ├── pressure_features.py        # Causal pressure feature engineering
│   ├── pressure_engine.py          # Models A, B, C, D mathematical engines
│   ├── batting_analysis.py         # Batting metrics, EB shrinkage, bootstrap
│   ├── bowling_analysis.py         # Bowling metrics, phase par, EB shrinkage
│   ├── player_ratings.py           # 5-dimensional composite rating engine
│   ├── ranking_pipeline.py         # Execution runner for Phases 3, 4, 5
│   ├── robustness_testing.py       # 5-pillar statistical sensitivity suite
│   ├── visualization.py            # 12 publication-grade figures generator
│   ├── generate_pdf_report.py      # ReportLab PDF report compiler
│   ├── validation.py               # Reconciliations and assertions
│   └── reporting.py                # Audit trail generators
├── tests/                          # 36 unit and integration tests
│   ├── test_cricket_rules.py
│   ├── test_match_state.py
│   ├── test_preprocessing.py
│   ├── test_competitions.py
│   ├── test_pressure_engine.py
│   ├── test_pressure_features.py
│   ├── test_pressure_sensitivity.py
│   ├── test_batting_analysis.py
│   ├── test_bowling_analysis.py
│   ├── test_player_ratings.py
│   └── test_robustness.py
├── outputs/
│   ├── processed/                  # Parquet analytical feature stores
│   ├── reports/                    # Generated markdown and PDF reports
│   ├── rankings/                   # Intermediate and final CSV rankings
│   └── figures/                    # 12 publication-grade PNG visualizations
├── main.py                         # Master end-to-end execution script
├── requirements.txt                # Pinned dependency manifest
└── README.md                       # Master documentation
```

---

## Installation & Requirements

Python 3.10 or higher is required.

Install dependencies:
```powershell
python -m pip install -r requirements.txt
```

---

## End-to-End Execution Guide

To reproduce the entire analytics pipeline from original raw CSV files to final PDF report and submission packaging, run:

```powershell
python main.py
```

The pipeline executes sequentially:
1. **Phase 1**: Ingestion, schema typing, competition filtering, MCC-compliant scoring, pre-delivery match state calculation.
2. **Phase 2**: Multi-model causal pressure feature engineering (Models A, B, C, D) and tier calibration.
3. **Phases 3, 4, 5**: Batter and bowler intelligence, Empirical Bayes shrinkage, cluster bootstrap, 5-dimensional composite ratings, and final rankings.
4. **Phase 6**: Robustness testing across models, thresholds, competitions, eras, and bootstrap rank bounds.
5. **Phase 7**: Generation of all 12 publication-grade visualizations in `outputs/figures/`.
6. **Phase 8**: Compilation of `outputs/reports/methodology_report.pdf` using ReportLab.
7. **Phase 10**: Population and packaging of `FINAL_SUBMISSION/`.

---

## Testing & Verification Suite

Execute the entire test suite (36 unit and integration tests):
```powershell
python -m unittest discover tests
```

Expected output:
```
Ran 36 tests in ~6s
OK
```

---

## Submission Artifacts Checklist

- [x] `FINAL_SUBMISSION/methodology_report.pdf`
- [x] `FINAL_SUBMISSION/methodology_report.md`
- [x] `FINAL_SUBMISSION/FINAL_RESULTS_SUMMARY.md`
- [x] `FINAL_SUBMISSION/batter_rankings_final.csv`
- [x] `FINAL_SUBMISSION/bowler_rankings_final.csv`
- [x] `FINAL_SUBMISSION/ranking_explanations.csv`
- [x] `FINAL_SUBMISSION/pressure_definition_report.md`
- [x] `FINAL_SUBMISSION/robustness_report.md`
- [x] `FINAL_SUBMISSION/final_submission_checklist.md`
- [x] 12 Publication PNG Charts in `outputs/figures/`
- [x] 100% Passing Test Suite in `tests/`
- [x] Deterministic Reproducibility via `python main.py`
