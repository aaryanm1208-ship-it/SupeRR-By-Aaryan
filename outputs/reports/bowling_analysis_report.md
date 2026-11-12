# Phase 4 Bowling Performance Intelligence Report

## 1. Executive Summary
- Total unique bowlers evaluated: 596
- Eligible bowlers meeting sample thresholds (>= 90 pressure legal balls across >= 10 matches): 154
- Total pressure legal balls bowled by eligible cohort: 44,955
- Mean pressure economy across eligible cohort: 8.94
- Mean baseline economy across eligible cohort: 7.93
- Mean clutch economy delta: -1.01

## 2. Top 15 Eligible Bowlers by Empirical Bayes Shrunk Economy

| provisional_rank | bowler_canonical_name | pressure_legal_balls | pressure_matches | pressure_econ | pressure_econ_eb | normal_econ | econ_delta | pressure_wickets | clutch_spell_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sufiyan Muqeem | 144.00 | 10.00 | 5.17 | 6.53 | 6.86 | 1.69 | 9.00 | 80.00 |
| 2 | Abrar Ahmed | 230.00 | 16.00 | 6.03 | 6.78 | 6.74 | 0.71 | 18.00 | 62.50 |
| 3 | Sunil Narine | 507.00 | 31.00 | 6.75 | 7.04 | 6.36 | -0.38 | 25.00 | 61.29 |
| 4 | Rashid Khan | 945.00 | 58.00 | 6.96 | 7.11 | 6.89 | -0.06 | 62.00 | 72.41 |
| 5 | Sikandar Raza | 328.00 | 20.00 | 6.68 | 7.12 | 7.05 | 0.37 | 13.00 | 70.00 |
| 6 | Mitchell Santner | 601.00 | 40.00 | 6.89 | 7.13 | 7.20 | 0.31 | 38.00 | 70.00 |
| 7 | Mohammad Nawaz | 344.00 | 24.00 | 6.75 | 7.16 | 7.97 | 1.22 | 27.00 | 75.00 |
| 8 | Mujeeb Ur Rahman | 280.00 | 22.00 | 6.69 | 7.18 | 5.83 | -0.85 | 25.00 | 72.73 |
| 9 | Saim Ayub | 208.00 | 14.00 | 6.84 | 7.41 | 6.98 | 0.14 | 8.00 | 42.86 |
| 10 | Axar Patel | 776.00 | 53.00 | 7.35 | 7.49 | 7.53 | 0.18 | 38.00 | 50.94 |
| 11 | Maheesh Theekshana | 592.00 | 41.00 | 7.40 | 7.57 | 7.51 | 0.11 | 25.00 | 63.41 |
| 12 | Ravichandran Ashwin | 541.00 | 27.00 | 7.50 | 7.67 | 7.79 | 0.30 | 21.00 | 55.56 |
| 13 | Krunal Pandya | 396.00 | 26.00 | 7.47 | 7.70 | 7.34 | -0.13 | 19.00 | 46.15 |
| 14 | Gareth Delany | 182.00 | 12.00 | 7.25 | 7.74 | 6.49 | -0.77 | 8.00 | 50.00 |
| 15 | Adil Rashid | 295.00 | 21.00 | 7.46 | 7.76 | 7.53 | 0.07 | 15.00 | 47.62 |

## 3. Methodology & Statistical Verification
- **Phase-Adjusted Economy Rate**: Bowlers are evaluated against phase-specific baseline expectation (Death par 10.46, Middle par 8.01, Powerplay par 8.46) to eliminate structural bias against death bowlers.
- **Empirical Bayes Shrinkage**: Economy rates and wicket rates are shrunk toward population priors.
- **Match-Level Cluster Bootstrap**: 1,000 resamples per eligible bowler to compute 95% confidence intervals.
