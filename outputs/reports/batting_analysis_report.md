# Phase 3 Batting Performance Intelligence Report

## 1. Executive Summary
- Total unique batters evaluated: 824
- Eligible batters meeting sample thresholds (>= 75 pressure balls across >= 10 matches): 86
- Total pressure balls faced by eligible cohort: 12,719
- Mean pressure strike rate across eligible cohort: 142.67
- Mean baseline strike rate across eligible cohort: 121.36
- Mean clutch strike rate delta: +21.31

## 2. Top 15 Eligible Batters by Empirical Bayes Shrunk Strike Rate

| provisional_rank | striker_canonical_name | pressure_balls | pressure_matches | pressure_sr | pressure_sr_eb | normal_sr | sr_delta | pressure_rpd | positive_contribution_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Dhruv Jurel | 130.00 | 14.00 | 206.15 | 195.46 | 144.51 | 61.65 | 38.29 | 57.14 |
| 2 | Tim David | 320.00 | 31.00 | 194.38 | 190.50 | 179.15 | 15.22 | 36.59 | 64.52 |
| 3 | Suryakumar Yadav | 243.00 | 18.00 | 188.89 | 184.52 | 166.02 | 22.87 | 32.79 | 72.22 |
| 4 | Naman Dhir | 81.00 | 10.00 | 197.53 | 184.45 | 160.00 | 37.53 | 32.00 | 50.00 |
| 5 | Ashutosh Sharma | 121.00 | 14.00 | 190.08 | 181.95 | 155.13 | 34.95 | 32.86 | 57.14 |
| 6 | Namboori Tilak Varma | 312.00 | 23.00 | 183.01 | 180.04 | 138.67 | 44.35 | 43.92 | 69.57 |
| 7 | David Miller | 352.00 | 30.00 | 181.82 | 179.25 | 132.47 | 49.34 | 40.00 | 63.33 |
| 8 | Dinesh Karthik | 129.00 | 15.00 | 186.05 | 179.08 | 166.38 | 19.66 | 26.67 | 40.00 |
| 9 | Mohammad Nabi | 91.00 | 14.00 | 183.52 | 174.99 | 116.57 | 66.95 | 23.86 | 21.43 |
| 10 | Rinku Singh | 234.00 | 19.00 | 176.07 | 173.01 | 146.91 | 29.16 | 68.67 | 68.42 |
| 11 | Daryl Mitchell | 131.00 | 12.00 | 177.86 | 172.51 | 141.82 | 36.04 | 29.12 | 50.00 |
| 12 | Gareth Delany | 116.00 | 10.00 | 177.59 | 171.74 | 105.13 | 72.46 | 41.20 | 80.00 |
| 13 | Tristan Stubbs | 268.00 | 21.00 | 173.51 | 171.05 | 145.99 | 27.52 | 38.75 | 52.38 |
| 14 | Riyan Parag | 84.00 | 14.00 | 178.57 | 170.82 | 148.18 | 30.39 | 18.75 | 35.71 |
| 15 | Jaker Ali Anik | 130.00 | 10.00 | 172.31 | 167.96 | 116.89 | 55.41 | 24.89 | 70.00 |

## 3. Methodology & Statistical Verification
- **Empirical Bayes Shrinkage**: Strike rates and runs per dismissal are shrunk toward the population prior mean based on individual sample size $n_i / (n_i + K)$ to avoid sample noise.
- **Match-Level Cluster Bootstrap**: 1,000 resamples per eligible batter clustered at the match level to compute 95% confidence intervals and standard errors.
- **Multi-Tier Decomposition**: Analyzed progression across Normal, Elevated, High, and Extreme pressure.
