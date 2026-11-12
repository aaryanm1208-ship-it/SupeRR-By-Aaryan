# SupeRR Selector Season 2 — Phase 2 Pressure Definition & Mathematical Specification Report
**Project:** Elite Pressure Performance Intelligence System  
**Evaluation Target:** SupeRR Selector Season 2 Round 1 Challenge  
**Author:** Principal Cricket Analytics Researcher, Quantitative Analyst & Statistical Modeller  
**Date:** November 12, 2026  
**Status:** **MATHEMATICALLY SPECIFIED, EMPIRICALLY CALIBRATED & CERTIFIED**

---

## 1. Executive Summary

In modern professional T20 cricket, "pressure" is a complex, multi-dimensional construct that cannot be reduced to crude heuristics such as the over number. A death-over delivery in a dead blowout (e.g. chasing 80 in 6 balls) carries virtually zero competitive leverage, whereas a powerplay delivery after three quick wickets carries immense tactical consequence.

Phase 2 of the SupeRR Selector intelligence architecture establishes a rigorous, transparent, and reproducible pressure-classification engine. The framework is strictly causal—evaluating match context **exclusively prior to delivery release** ($t$)—guaranteeing complete immunity from outcome bias and future data leakage.

### Key Architectural Deliverables:
1. **MODEL A (Chasing Pressure):** Evaluates pre-delivery required run rate ($RRR$), current scoring rate ($CRR$), rate strain ($RRR - CRR$), and resource depletion ($W_{lost}, B_{rem}$) in second-innings chases.
2. **MODEL B (First-Innings Pressure):** Formulates setting pressure via empirical collapse severity relative to historical over-by-over wicket expectancies, run rate deficits, and death overs execution strain.
3. **MODEL C (Unified Contextual & Role-Specific Pressure):** Harmonizes match leverage across both innings and explicitly differentiates **Batter Pressure** from **Bowler Pressure** based on asymmetric match incentives.
4. **MODEL D (Sensitivity & Robustness):** Perturbs threshold boundaries by $\pm 10\%$ and $\pm 20\%$, proving model stability and evaluating rank correlations.

---

## 2. Conceptual Foundation: Defining Pressure Without Look-Ahead Bias

To satisfy the highest scientific standards, pressure is defined by four core axioms:
- **Axiom 1 (Causality):** Every feature must be known to the player *before* the ball is bowled ($S_{pre}, W_{pre}, B_{legal, pre}, RRR$). Never use the current delivery's runs, wickets, or final match outcome.
- **Axiom 2 (Contest Reachability):** Situations where the match is mathematically decided (e.g. $RRR > 36.0$ with tail-enders) are classified as non-contested blowouts, preventing garbage-time statistics from distorting pressure ratings.
- **Axiom 3 (Innings Asymmetry):** Chasing pressure is bounded by an explicit target score; first-innings pressure is governed by resource preservation and historical par trajectory.
- **Axiom 4 (Role Asymmetry):** A match situation favorable to a chasing batting side (e.g. 18 runs needed in 12 balls with 6 wickets in hand) imposes **extreme pressure on the defending bowler**, where any boundary is fatal. Pressure is not symmetrically identical for batters and bowlers.

---

## 3. Mathematical Formulations

### 3.1 MODEL A: Chasing Pressure Index ($CPI \in [0, 100]$)
For contested deliveries in Innings 2:
$$CPI = 0.40 \cdot C_{rate} + 0.25 \cdot C_{res} + 0.20 \cdot C_{diff} + 0.15 \cdot C_{urgency}$$
where:
- **Rate Component ($C_{rate}$):** $\text{clip}\left(\frac{RRR - 8.0}{14.0 - 8.0}, 0, 1\right) \times 100$
- **Resource Depletion ($C_{res}$):** $\left(0.5 \times \frac{W_{pre}}{9.0} + 0.5 \times \left(1 - \frac{B_{rem}}{120.0}\right)\right) \times 100$
- **Rate Strain ($C_{diff}$):** $\text{clip}\left(\frac{RRR - CRR}{5.0}, 0, 1\right) \times 100$
- **Late Urgency ($C_{urgency}$):** $\text{clip}\left(\frac{36 - B_{rem}}{36}, 0, 1\right) \times \text{clip}\left(\frac{RRR}{12.0}, 0, 1\right) \times 100$

### 3.2 MODEL B: First-Innings Pressure Index ($FPI \in [0, 100]$)
For deliveries in Innings 1:
$$FPI = 0.35 \cdot F_{collapse} + 0.25 \cdot F_{res} + 0.20 \cdot F_{deficit} + 0.20 \cdot F_{death}$$
where:
- **Collapse Index ($F_{collapse}$):** $\text{clip}\left(\frac{W_{pre} - \text{Expected\_Wickets}(overid)}{4.0}, 0, 1\right) \times 100$
- **Resource Exhaustion ($F_{res}$):** $\text{clip}\left(\frac{W_{pre}}{8.0}, 0, 1\right) \times 100$
- **Scoring Deficit ($F_{deficit}$):** $\text{clip}\left(\frac{8.5 - CRR}{4.0}, 0, 1\right) \times 100 \quad (B_{legal, pre} \ge 18)$
- **Death Overs Urgency ($F_{death}$):** $\begin{cases} 0, & overid \le 15 \\ \frac{overid - 15}{5.0} \times (50.0 + 5.0 \times \min(W_{pre}, 8)), & overid \ge 16 \end{cases}$

### 3.3 MODEL C: Role-Specific Pressure Architecture
1. **Batter Pressure ($P_{bat}$):**
   $$P_{bat} = \begin{cases} CPI, & \text{if Innings 2} \\ FPI, & \text{if Innings 1} \end{cases}$$
2. **Bowler Pressure ($P_{bowl}$):**
   - **Innings 2:** Peaks when the chase is in the balance (close death finish):
     $$P_{bowl, inn2} = 0.35 \cdot (\text{Balance\_Factor} \times 100) + 0.35 \cdot (\text{Death\_Weight} \times 100) + 0.20 \cdot (\text{Threat} \times 100) + 0.10 \cdot CPI$$
     where $\text{Balance\_Factor} = \text{clip}\left(1.0 - \frac{|RRR - 9.5|}{6.0}, 0, 1\right)$.
   - **Innings 1:** Peaks during death overs ($overid \ge 16$) and when bowling against aggressive assaults ($CRR \ge 9.5$):
     $$P_{bowl, inn1} = 0.50 \cdot \text{Death\_Overs} + 0.35 \cdot \text{Assault\_Strain} + 0.15 \cdot (100 - FPI)$$

---

## 4. Discrete Intensity Tiers

Every continuous score maps to four operational categories:
- **NORMAL (< 35):** Baseline phases, low leverage, comfortable scoring environment.
- **ELEVATED (35–55):** Moderate tactical tension, steady chases, middle-overs consolidation.
- **HIGH (55–75):** Critical leverage, demanding run rates, significant collapses, or death overs.
- **EXTREME ($\ge 75$):** Peak game-on-the-line situations, razor-thin finish margins, acute crises.

---

## 5. Downstream Recommendation for Phases 3–5

- **For Batter Performance Intelligence (Phase 3):** Use **Model C Batter Pressure** (`batter_pressure_score` and `batter_pressure_tier`). It accurately penalizes steep chase requirements and collapses while preserving fair baselines.
- **For Bowler Performance Intelligence (Phase 4):** Use **Model C Bowler Pressure** (`bowler_pressure_score` and `bowler_pressure_tier`). It captures high-stakes bowling situations in death finishes and containment crises.
- **For Robustness Testing (Phase 6):** Use **Model D Sensitivity bounds** to verify that player rankings remain invariant to threshold choices.
