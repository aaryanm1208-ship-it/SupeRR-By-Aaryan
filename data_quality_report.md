# SupeRR Selector Season 2 — Phase 0 Data Quality & Integrity Audit Report
**Project:** Elite Pressure Performance Intelligence System  
**Evaluation Target:** SupeRR Selector Season 2 Round 1 Challenge  
**Author:** Principal Sports Data Scientist & Quantitative Analyst  
**Date of Audit:** November 12, 2026  
**Status:** PASSED (All 38 Data Quality & Referential Assertions Verified)

---

## 1. Executive Summary

Phase 0 of the SupeRR Selector Season 2 pressure performance analytics architecture establishes the foundational integrity, referential consistency, and cricket domain correctness of the supplied historical data pack. The challenge mandates identifying and ranking the Top 10 most reliable batters and Top 10 most reliable bowlers under match pressure, derived exclusively from historical IPL and T20 International (T20I) data from 2022 onwards.

To ensure absolute statistical defensibility and prevent data leakage, artifact pollution, or biased player rankings, an exhaustive automated data profiling and validation pipeline was executed across all six supplied CSV files and the accompanying problem statement specification.

### Key Audit Findings:
1. **Source Data Completeness:** The data pack contains 6 relational CSV files totaling 42.6 MB and 200,999 ball-by-ball records across 883 matches, spanning January 22, 2022, to November 1, 2026.
2. **Zero Referential Orphans:** Every foreign key across all 6 tables was audited against its parent table with zero orphan records detected across all entity boundaries (100% referential integrity).
3. **Player Identity Homonym Hazard:** Exactly 1,217 unique `player_id` entities exist. Every `player_id` maps to exactly one canonical name. However, **7 distinct player names represent multiple distinct players** (e.g., two distinct `Rashid Khan` IDs, two distinct `Abdul Samad` IDs). Inferring player identity from names is strictly prohibited; all pipeline operations must bind to authoritative `player_id`.
4. **Delivery Legality & Extras Taxonomy:** Wides (7,714), front-foot no-balls (`Overstep`: 576), and other no-balls (`other`: 264) are confirmed to be illegal deliveries, adding uncounted balls to overs. Byes (529) and leg-byes (2,748) are confirmed to be legal deliveries. Exactly 1 penalty run event was detected.
5. **Scorecard Attribution Rules:** Bowler-credited dismissals account for 10,272 wickets (`Caught`, `Bowled`, `LBW`, `Stump`, `Hit Wicket`). Non-bowler dismissals account for 609 events (`RunOut`, `Retire Out`, `Obstructing the field`). Extras are correctly bifurcated between bowler-charged extras and fielding extras.
6. **Match Context & Incomplete Matches:** 16 matches in `matches.csv` have zero ball-by-ball records; all 16 are confirmed to have been officially abandoned before play commenced. Exactly 34 matches contain DLS revisions or reduced overs, where revised overs are encoded in **legal balls** (e.g., 90.0 balls = 15 overs, 48.0 balls = 8 overs). Super overs are isolated to innings 3 and 4 (38 balls total).
7. **Competition Filtering:** Of 141 competitions in `competitions.csv`, exactly 5 correspond to IPL (2022, 2023, 2024, 2025, 2026; 371 matches) and 134 correspond to official T20Is (482 matches). Exactly 2 regional competitions (comp_ids 2670 and 3289; 30 matches) are neither IPL nor T20I and are formally documented for exclusion from primary rankings.

---

## 2. Dataset Inventory & Architecture

The relational schema comprises six interconnected tables located in `6af458274c1e8_data_pack/Data Pack`:

| Table Name | File Size (Bytes) | Row Count | Column Count | Primary Key / Grain | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `competitions.csv` | 7,624 | 141 | 4 | `comp_id` | Tournament and series metadata including format and season. |
| `teams.csv` | 6,922 | 353 | 3 | `(comp_id, team_id)` | Teams participating in each competition. |
| `matches.csv` | 123,864 | 883 | 22 | `match_id` | Match-level fixture details, venue, toss, revised conditions, and results. |
| `playing_eleven.csv` | 966,287 | 28,381 | 9 | `(match_id, player_id)`* | Team sheets, nominal batting order, playing status, and impact player flags. |
| `competition_team_player_mapping.csv` | 462,969 | 6,413 | 6 | `(comp_id, team_id, player_id)` | Authoritative player entity directory and canonical display names. |
| `ball_by_ball.csv` | 41,071,837 | 200,999 | 33 | `(match_id, innings, overid, over_ball_num)` | Granular delivery-level telemetry, pitch trajectory, outcomes, and dismissals. |

*\*Note: 3 matches contain duplicate entries in `playing_eleven.csv`, detailed in Section 5.*

---

## 3. Entity Relationships and Referential Integrity Audit

A comprehensive referential integrity audit was conducted across every foreign key relation. Zero orphan keys were detected:

```
[competitions.csv] (comp_id)
       ▲               ▲
       │               │
  (comp_id)       (comp_id)
       │               │
  [teams.csv]     [matches.csv] (match_id)
       ▲               ▲             ▲
       │               │             │
   (team_id)      (match_id)    (match_id)
       │               │             │
[competition_team_player_mapping.csv]  [playing_eleven.csv]  [ball_by_ball.csv]
       ▲                                     │                     │
       └────────────────(player_id)──────────┴─────────────────────┘
```

### Automated Join Verification Results:
- `teams.comp_id` $\to$ `competitions.comp_id`: **0 orphan records** (100% valid).
- `matches.comp_id` $\to$ `competitions.comp_id`: **0 orphan records** (100% valid).
- `matches.home_team_id` $\to$ `teams.team_id`: **0 orphan records** (100% valid).
- `matches.away_team_id` $\to$ `teams.team_id`: **0 orphan records** (100% valid).
- `matches.win_team_id` $\to$ `teams.team_id`: **0 orphan records** (41 nulls attributable to No Result / Abandoned matches).
- `matches.toss_win_team_id` $\to$ `teams.team_id`: **0 orphan records** (15 nulls due to abandoned matches without toss).
- `playing_eleven.match_id` $\to$ `matches.match_id`: **0 orphan records** (100% valid).
- `playing_eleven.team_id` $\to$ `teams.team_id`: **0 orphan records** (100% valid).
- `playing_eleven.player_id` $\to$ `CTP.player_id`: **0 orphan records** (100% valid).
- `ball_by_ball.match_id` $\to$ `matches.match_id`: **0 orphan records** (100% valid).
- `ball_by_ball.batting_team_id` $\to$ `teams.team_id`: **0 orphan records** (100% valid).
- `ball_by_ball.bowling_team_id` $\to$ `teams.team_id`: **0 orphan records** (100% valid).
- `ball_by_ball.striker_id` $\to$ `CTP.player_id`: **0 orphan records** (100% valid).
- `ball_by_ball.non_striker_id` $\to$ `CTP.player_id`: **0 orphan records** (100% valid).
- `ball_by_ball.bowler_id` $\to$ `CTP.player_id`: **0 orphan records** (100% valid).
- `ball_by_ball.dismissed_player_id` $\to$ `CTP.player_id`: **0 orphan records** (100% valid).

---

## 4. Player Identity Discrepancy & Homonym Hazard

The challenge explicitly requires:
> *"Never infer player identities from names when stable player IDs are available."*

Profiling revealed two critical empirical reasons for this mandate:

### 1. Homonym Collisions (Same Name, Distinct Players):
Seven distinct player names map to multiple distinct `player_id` entities:
- **`Rashid Khan`**:
  - `player_id = 459`: International star leg-spinner (Afghanistan / Gujarat Titans).
  - `player_id = 6496`: Domestic/Associate player appearing in Asian regional tournaments.
- **`Abdul Samad`**:
  - `player_id = 4910`: Sunrisers Hyderabad middle-order batter.
  - `player_id = 6653`: Associate regional squad batter.
- **`Haider Ali`**:
  - `player_id = 3014`: Pakistan international batter.
  - `player_id = 6449`: Regional squad player.
- **`Mohammad Ali`**:
  - `player_id = 5304` vs `player_id = 5609`.
- **`Muhammad Farooq`**:
  - `player_id = 6445` vs `player_id = 6498`.
- **`Bashir Ahmad`**:
  - `player_id = 6652` vs `player_id = 7087`.
- **`Basil Hameed`**:
  - `player_id = 3538` vs `player_id = 6537`.

*Analytical Treatment:* Merging or aggregating on player names would catastrophically conflate two distinct human beings. All downstream feature engineering and rating algorithms bind strictly to `player_id`.

### 2. Spelling Inconsistency Across Tables:
In `ball_by_ball.csv`, `player_id = 4458` is rendered as `'Aneurin Donald'`, whereas in `competition_team_player_mapping.csv` the same ID is registered as `'AHT Donald'`. The authoritative canonical name mapping is resolved directly from `competition_team_player_mapping.csv`.

---

## 5. Completeness, Null Analysis & Anomalies

### 5.1 Matches Missing Delivery Data
There are 883 matches in `matches.csv` but only 867 distinct `match_id` values in `ball_by_ball.csv`.
- An audit of the 16 missing matches confirmed that **100% had official result `'Match Abandoned'`**.
- In these fixtures, adverse weather prevented a single ball from being bowled. These matches contain zero playing telemetry and are excluded from delivery-level feature engineering without data loss.

### 5.2 Playing Eleven Duplicate Entries
In `playing_eleven.csv`, 75 duplicate rows exist across three specific matches:
- `match_id = 28962`: 29 duplicate player entries.
- `match_id = 13613`: 24 duplicate player entries.
- `match_id = 21176`: 22 duplicate player entries.
- *Root Cause:* In these three matches, player line-ups were logged twice with slightly differing nominal batting orders.
- *Analytical Treatment:* When joining playing sheets, duplicates must be deduplicated by selecting the record with `is_played == True` and the lowest non-null `batting_order`.

### 5.3 Weather-Affected Fixtures & Revised Target Representation
In `matches.csv`, 34 matches contain non-null values in `first_inn_revised_overs`, `second_inn_revised_overs`, or `revised_target`.
- **Unit of Measurement:** `first_inn_revised_overs` and `second_inn_revised_overs` are stored as **total scheduled legal balls**, not decimal overs.
  - Example: `114.0` = 19.0 overs ($19 \times 6$).
  - Example: `90.0` = 15.0 overs ($15 \times 6$).
  - Example: `48.0` = 8.0 overs ($8 \times 6$).
  - Example: `30.0` = 5.0 overs ($5 \times 6$).
- **Chase Target Formula:**
  $$\text{Target} = \begin{cases} \text{revised\_target}, & \text{if } \text{revised\_target is not null} \\ S_1 + 1, & \text{otherwise} \end{cases}$$
  where $S_1$ is the total first-innings runs scored by the batting team.

---

## 6. Official Cricket Scoring Rules & Delivery Logic

### 6.1 Delivery Sequence and Monotonicity
Verification confirmed that within every single match and innings:
- `innings_ball_num` strictly increments from 1 up to a maximum of 136.
- `(overid, over_ball_num)` is strictly chronological.
- `overid` is 1-indexed (1 to 20).
- `over_ball_num` is 1-indexed (1 to 13), incrementing on every bowled ball including illegal deliveries.

### 6.2 Legal Deliveries vs. Illegal Extras
A delivery counts as a legal delivery if and only if it is not an illegal extra:
$$\text{Is\_Legal} = (\text{extras\_type} \notin \{\text{'wide'}, \text{'Overstep'}, \text{'other'}, \text{'Penalty'}\})$$

Empirical distribution across 200,999 balls:
- **Legal Deliveries:** 192,444 deliveries (95.74%).
- **Illegal Deliveries:** 8,554 deliveries (4.26%):
  - Wides (`wide`): 7,714 balls.
  - Front-foot No-balls (`Overstep`): 576 balls.
  - Other No-balls (`other`): 264 balls (beamers, field restriction violations).
- **Penalty Runs (`Penalty`):** 1 delivery event (5 penalty runs awarded).

### 6.3 Batter Ball-Faced Accounting
A batter faces a delivery if and only if the delivery is not a wide and not a penalty:
$$\text{Is\_Ball\_Faced} = (\text{extras\_type} \notin \{\text{'wide'}, \text{'Penalty'}\})$$
- Batters face legal deliveries, no-balls (`Overstep`, `other`), byes, and leg-byes.
- Batters do NOT face wides.
- Batter runs credited strictly equal `runs`. Extras are never credited to the batter.

### 6.4 Bowler-Charged Runs & Economy Accounting
Official Marylebone Cricket Club (MCC) Laws of Cricket and ICC Playing Conditions dictate:
$$\text{Bowler\_Charged\_Runs} = \text{runs} + \begin{cases} \text{extras1\_runs}, & \text{if extras\_type} \in \{\text{'wide'}, \text{'Overstep'}, \text{'other'}\} \\ 0, & \text{otherwise} \end{cases}$$
- Bowlers are charged for off-the-bat runs, wides, and no-balls.
- Bowlers are NOT charged for byes, leg-byes, or penalty runs.
- `extras_2_runs` occurs exclusively on no-balls (36 instances) where byes/leg-byes were run off a no-ball. These are fielding extras and are not charged to the bowler.
- **Bowler Economy Rate:**
  $$\text{Economy Rate} = \frac{\text{Bowler\_Charged\_Runs}}{\text{Legal\_Deliveries} / 6.0}$$

### 6.5 Dismissal Attribution
Of 10,881 total wickets:
- **Bowler-Credited Dismissals (10,272 wickets):**
  - `Caught`: 7,557
  - `Bowled`: 1,775
  - `LBW`: 709
  - `Stump`: 214
  - `Hit Wicket`: 17
- **Non-Bowler Dismissals (609 dismissals):**
  - `RunOut`: 600
  - `Retire Out`: 6
  - `Obstructing the field` / `Obstracting the field`: 3

---

## 7. Competition Filtering & Scope of Analysis

The master directive mandates:
> *"The final results must be derived exclusively from the supplied historical IPL and T20I data from 2022 onwards. Exclude unrelated competitions from the primary analysis."*

### Competition Classification Audit:
1. **IPL Competitions (Retained):**
   - `comp_id = 1358`: IPL 2022 (74 matches)
   - `comp_id = 1715`: IPL 2023 (74 matches)
   - `comp_id = 2193`: IPL 2024 (74 matches)
   - `comp_id = 2725`: IPL 2025 (75 matches)
   - `comp_id = 3298`: IPL 2026 (74 matches)
   - *Total IPL Matches:* **371 matches**
2. **T20 International Competitions (Retained):**
   - 134 competitions marked with `match_format == 'T20I'`
   - *Total T20I Matches:* **482 matches**
3. **Excluded Competitions (Formally Omitted):**
   - `comp_id = 2670`: Mens T20 Emerging Teams Asia Cup 2024 (15 matches)
   - `comp_id = 3289`: Asia Cup Rising Stars 2025 (15 matches)
   - *Total Excluded Matches:* **30 matches**
   - *Reason for Exclusion:* Regional development/emerging squads not meeting official Senior Men's IPL or T20I status.

---

## 8. Data Integrity Deliverables Summary

| Deliverable Artifact | File Location | Status | Verification Summary |
| :--- | :--- | :--- | :--- |
| **Data Dictionary** | `data_dictionary.csv` | Created | Complete 77-column audit detailing types, keys, nulls, distinct counts, and MCC cricket definitions. |
| **Dataset Inventory** | `dataset_inventory.json` | Created | Machine-readable schema specification and metadata across all 6 files. |
| **Validation Log** | `logs/phase0_validation.log` | Created | 38 automated test assertions logged with timestamps; 100% pass rate. |
| **Data Quality Report** | `data_quality_report.md` | Created | Comprehensive architectural reference document. |

---

## 9. Phase 0 Sign-Off and Next Steps

All Phase 0 entry criteria have been strictly satisfied:
1. Data schemas, column semantics, and entity relations are fully characterized.
2. The danger of player name homonyms has been demonstrated and mitigated via strict `player_id` binding.
3. Official cricket scoring rules for legal deliveries, balls faced, bowler runs, and wicket attributions have been verified.
4. Target competitions (IPL and T20I) and excluded series (2670, 3289) are formally partitioned.
5. Incomplete matches, super overs, and DLS revisions are mapped.

**Recommendation:** Data integrity audit is complete and certified. Proceed immediately to **Phase 1: Data Engineering** to construct `processed_deliveries.parquet` and `processed_matches.parquet`.
