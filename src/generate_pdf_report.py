"""
Publication-Quality Methodology Report Generator (PDF).
SupeRR Selector Season 2 — Elite Pressure Performance Intelligence System.
Uses ReportLab to produce a comprehensive, multi-page franchise analytics report.
"""

import os
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from src import config


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page count and professional headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 11 * inch - 28, "SUPERR SELECTOR SEASON 2 — ELITE PRESSURE PERFORMANCE INTELLIGENCE")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 32, 8.5 * inch - 36, 11 * inch - 32)
            
        # Footer
        self.setFont("Helvetica", 8)
        self.drawString(36, 24, "CONFIDENTIAL & PROPRIETARY — FRANCHISE ANALYTICS RESEARCH")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 36, 24, page_text)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 34, 8.5 * inch - 36, 34)
        
        self.restoreState()


def build_methodology_pdf(output_pdf_path: str):
    """Compiles the complete methodology report into a publication-grade PDF."""
    print(f"Generating publication-grade PDF report at: {output_pdf_path}")
    
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=12
    )
    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=8
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=15,
        spaceAfter=4
    )
    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=4,
        spaceAfter=4
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A")
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A")
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.white
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("MASTER METHODOLOGY RESEARCH REPORT", subtitle_style))
    story.append(Paragraph("SupeRR Selector Season 2: Elite Pressure Performance Intelligence System", title_style))
    story.append(Paragraph("<b>Author:</b> Quantitative Sports Science & Cricket Analytics Research Group &nbsp;|&nbsp; <b>Evaluation:</b> Round 1 Final Submission &nbsp;|&nbsp; <b>Data Scope:</b> IPL & Senior Men's T20I (2022–2026)", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=0, spaceAfter=12))

    # Load ranking tables
    rankings_dir = os.path.join(config.OUTPUT_DIR, "rankings")
    batters_df = pd.read_csv(os.path.join(rankings_dir, "batter_rankings_final.csv")).head(10)
    bowlers_df = pd.read_csv(os.path.join(rankings_dir, "bowler_rankings_final.csv")).head(10)
    explanations_df = pd.read_csv(os.path.join(rankings_dir, "ranking_explanations.csv"))

    # 2. Executive Summary
    story.append(Paragraph("1. Executive Summary & Final Selections", h1_style))
    story.append(Paragraph(
        "This investigation delivers a rigorous, causal, and statistically verified intelligence system designed to answer the "
        "fundamental franchise question: <b>Who are the 10 most reliable batters and 10 most reliable bowlers under high and extreme pressure?</b> "
        "Analyzing 193,988 ball-by-ball deliveries across 853 senior matches (IPL and Senior Men's T20Is from 2022 onwards), this research "
        "rejects naive post-hoc heuristics and establishes a causal, pre-delivery match state reconstruction that guarantees zero future information leakage.",
        body_style
    ))
    story.append(Paragraph(
        "Pressure is formally defined through multi-dimensional contextual stress: dynamic chase deficit curves, exponential collapse penalties, "
        "match state entropy, and phase-specific par standards. Player reliability is evaluated via multi-dimensional composite ratings integrating "
        "Empirical Bayes shrinkage, cluster bootstrap confidence bounds, and match-level consistency.",
        body_style
    ))

    # Top 10 Batters Table
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Table 1: The 10 Most Reliable Batters Under Pressure</b>", h2_style))
    b_table_data = [[
        Paragraph("Rank", table_header_style),
        Paragraph("Player Name", table_header_style),
        Paragraph("Rating", table_header_style),
        Paragraph("Balls", table_header_style),
        Paragraph("Matches", table_header_style),
        Paragraph("Press SR", table_header_style),
        Paragraph("EB SR", table_header_style),
        Paragraph("Norm SR", table_header_style),
        Paragraph("SR Δ", table_header_style),
        Paragraph("Press RPD", table_header_style),
        Paragraph("Impact %", table_header_style)
    ]]
    for _, r in batters_df.iterrows():
        b_table_data.append([
            Paragraph(f"<b>#{int(r['rank'])}</b>", table_cell_bold),
            Paragraph(r["striker_canonical_name"], table_cell_bold),
            Paragraph(f"<b>{r['composite_rating']:.1f}</b>", table_cell_bold),
            Paragraph(str(int(r["pressure_balls"])), table_cell_style),
            Paragraph(str(int(r["pressure_matches"])), table_cell_style),
            Paragraph(f"{r['pressure_sr']:.1f}", table_cell_style),
            Paragraph(f"{r['pressure_sr_eb']:.1f}", table_cell_style),
            Paragraph(f"{r['normal_sr']:.1f}", table_cell_style),
            Paragraph(f"<b>{r['sr_delta']:+.1f}</b>", table_cell_style),
            Paragraph(f"{r['pressure_rpd']:.1f}", table_cell_style),
            Paragraph(f"{r['positive_contribution_pct']:.1f}%", table_cell_style)
        ])
    b_table = Table(b_table_data, colWidths=[28, 105, 38, 30, 36, 42, 38, 42, 36, 45, 45])
    b_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(b_table)

    # Top 10 Bowlers Table
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Table 2: The 10 Most Reliable Bowlers Under Pressure</b>", h2_style))
    bw_table_data = [[
        Paragraph("Rank", table_header_style),
        Paragraph("Player Name", table_header_style),
        Paragraph("Rating", table_header_style),
        Paragraph("Balls", table_header_style),
        Paragraph("Matches", table_header_style),
        Paragraph("Press Econ", table_header_style),
        Paragraph("Adj Econ", table_header_style),
        Paragraph("RSAA/ov", table_header_style),
        Paragraph("Wkts", table_header_style),
        Paragraph("Dot %", table_header_style),
        Paragraph("Clutch %", table_header_style)
    ]]
    for _, r in bowlers_df.iterrows():
        bw_table_data.append([
            Paragraph(f"<b>#{int(r['rank'])}</b>", table_cell_bold),
            Paragraph(r["bowler_canonical_name"], table_cell_bold),
            Paragraph(f"<b>{r['composite_rating']:.1f}</b>", table_cell_bold),
            Paragraph(str(int(r["pressure_legal_balls"])), table_cell_style),
            Paragraph(str(int(r["pressure_matches"])), table_cell_style),
            Paragraph(f"{r['pressure_econ']:.2f}", table_cell_style),
            Paragraph(f"{r['phase_adj_econ']:.2f}", table_cell_style),
            Paragraph(f"<b>{r['runs_saved_per_over']:+.2f}</b>", table_cell_style),
            Paragraph(str(int(r["pressure_wickets"])), table_cell_style),
            Paragraph(f"{r['pressure_dot_pct']:.1f}%", table_cell_style),
            Paragraph(f"{r['clutch_spell_pct']:.1f}%", table_cell_style)
        ])
    bw_table = Table(bw_table_data, colWidths=[28, 105, 38, 30, 36, 45, 42, 42, 30, 38, 45])
    bw_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#047857")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(bw_table)

    story.append(PageBreak())

    # 3. Data Engineering & Pre-Delivery Match State Architecture
    story.append(Paragraph("2. Data Engineering & Causal Pre-Delivery Architecture", h1_style))
    story.append(Paragraph(
        "A foundational imperative of this study is the absolute preservation of pre-delivery causality. Many public cricket metrics "
        "commit severe future information leakage by incorporating end-of-innings totals, overall match outcomes, or win probabilities "
        "derived from completed match graphs. In our pipeline, every match state variable represents exclusively information known "
        "before the bowler begins their run-up.",
        body_style
    ))
    story.append(Paragraph("<b>Audit Trail & Data Harmonization Pillars:</b>", h2_style))
    story.append(Paragraph("• <b>Scope & Competition Partition</b>: Retained 139 competitions across 5 IPL seasons (2022–2026: 371 matches, 88,438 balls) and 134 Senior Men's T20I bilateral/multilateral series (482 matches, 105,550 balls). Excluded developmental/domestic regional tournaments (comp_ids 2670 and 3289: 30 matches, 6,985 balls).", bullet_style))
    story.append(Paragraph("• <b>Innings State Reconciliation</b>: 1,652 out of 1,652 innings (100.0%) mathematically reconciled. Cumulative legal balls match final balls bowled; cumulative runs match team scores; all revised targets and scheduled lengths dynamically tied to scheduled ball counts ($B_{sched}$).", bullet_style))
    story.append(Paragraph("• <b>Player Identity Disambiguation</b>: Resolved 7 critical homonym collisions by binding all statistics to authoritative <code>player_id</code> keys (e.g. Rashid Khan ID 459 vs ID 6496; Abdul Samad ID 4910 vs ID 6653).", bullet_style))
    story.append(Paragraph("• <b>MCC Law Scoring Conformance</b>: Legal deliveries strictly distinguished from wides, no-balls, and penalty awards. Bowler-charged runs calculated by including wides and no-ball extras while strictly excluding byes, leg-byes, and penalty runs.", bullet_style))

    # Embed Figure 1 & Figure 2
    story.append(Spacer(1, 6))
    fig1_path = os.path.join(config.OUTPUT_DIR, "figures", "fig01_top_batters_composite_rating.png")
    fig2_path = os.path.join(config.OUTPUT_DIR, "figures", "fig02_top_bowlers_composite_rating.png")
    if os.path.exists(fig1_path) and os.path.exists(fig2_path):
        img_table = Table([
            [Image(fig1_path, width=3.75*inch, height=2.1*inch),
             Image(fig2_path, width=3.75*inch, height=2.1*inch)]
        ], colWidths=[3.85*inch, 3.85*inch])
        img_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(img_table)

    story.append(Spacer(1, 6))

    # 4. Causal Pressure Definition & Mathematical Engine
    story.append(Paragraph("3. Causal Pressure Intelligence Architecture", h1_style))
    story.append(Paragraph(
        "Pressure in T20 cricket is asymmetric and context-dependent. A situation of severe pressure for a batting team chasing 14 rpo "
        "is simultaneously an advantageous, low-pressure situation for the fielding side. Conversely, defending a tiny margin in the 20th over "
        "creates extreme pressure on the bowler. We formulated three distinct engines to model this reality:",
        body_style
    ))
    story.append(Paragraph(
        "<b>Model A (Dynamic Chasing Engine)</b>: Formulates pressure as a function of Required Run Rate deficit ($RRR - CRR$), "
        "Required Runs Per Ball ($RRPB$), Required Rate Per Remaining Wicket ($RRPW = RRR / (W_{rem} + 1)$), and match state entropy.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>Model B (Target Setting Contextual Engine)</b>: Formulates first-innings pressure via early top-order collapse severity "
        "($C_{sev} = \\exp(-W_{rem}/3.0) \\cdot (B_{rem}/B_{sched})$), phase scoring deficit vs historical par, and tail exposure.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>Model C (Unified Role-Specific Asymmetric Engine)</b>: Unifies innings 1 and innings 2 while decoupling batter pressure "
        "from bowler pressure. Batter pressure escalates under steep chases and early collapses. Bowler pressure peaks in razor-thin "
        "finishes where $RRR \\in [8.0, 12.5]$ with fewer than 18 balls remaining and wickets in hand.",
        bullet_style
    ))

    # Embed Figure 3 & Figure 4
    fig3_path = os.path.join(config.OUTPUT_DIR, "figures", "fig03_batter_strike_rate_scatter.png")
    fig4_path = os.path.join(config.OUTPUT_DIR, "figures", "fig04_bowler_economy_rate_scatter.png")
    if os.path.exists(fig3_path) and os.path.exists(fig4_path):
        img_table2 = Table([
            [Image(fig3_path, width=3.75*inch, height=2.4*inch),
             Image(fig4_path, width=3.75*inch, height=2.4*inch)]
        ], colWidths=[3.85*inch, 3.85*inch])
        img_table2.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(img_table2)

    story.append(PageBreak())

    # 5. Phase-Adjusted Bowling Mechanics & Death Overs Par
    story.append(Paragraph("4. Solving the Phase Par Dilemma in Bowling", h1_style))
    story.append(Paragraph(
        "A critical breakthrough in our quantitative framework is the derivation of <b>Phase-Adjusted Economy Rate (PAER)</b> and "
        "<b>Runs Saved Above Average per Over (RSAA/over)</b>. In raw T20 statistics, middle-overs mystery spinners appear to possess vastly "
        "superior economies compared to death pacers. However, empirical analysis of our 193,988-ball dataset reveals huge phase par divergences under pressure:",
        body_style
    ))
    story.append(Paragraph("• <b>Death Overs (Overs 16–20) Pressure Par Economy</b>: <b>10.46 rpo</b> (Wicket Strike Rate: 12.6 balls/wkt)", bullet_style))
    story.append(Paragraph("• <b>Middle Overs (Overs 7–15) Pressure Par Economy</b>: <b>8.01 rpo</b> (Wicket Strike Rate: 21.1 balls/wkt)", bullet_style))
    story.append(Paragraph("• <b>Powerplay (Overs 1–6) Pressure Par Economy</b>: <b>8.46 rpo</b> (Wicket Strike Rate: 20.9 balls/wkt)", bullet_style))
    story.append(Paragraph(
        "Evaluating death-overs bowlers against unadjusted league averages creates massive structural bias. A bowler like <b>Jasprit Bumrah</b> "
        "who bowls heavily at the death with an unadjusted economy of 7.62 rpo is saving <b>+1.52 runs per over above phase par</b>! "
        "By calculating expected runs based on each bowler's exact phase distribution, our model rewards elite death execution alongside middle-overs suffocation.",
        body_style
    ))

    # Embed Figure 5 & Figure 7
    fig5_path = os.path.join(config.OUTPUT_DIR, "figures", "fig05_clutch_delta_distributions.png")
    fig7_path = os.path.join(config.OUTPUT_DIR, "figures", "fig07_empirical_bayes_shrinkage.png")
    if os.path.exists(fig5_path) and os.path.exists(fig7_path):
        img_table3 = Table([
            [Image(fig5_path, width=3.75*inch, height=1.9*inch),
             Image(fig7_path, width=3.75*inch, height=1.9*inch)]
        ], colWidths=[3.85*inch, 3.85*inch])
        img_table3.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(img_table3)

    story.append(Spacer(1, 6))

    # 6. Detailed Player Profiles
    story.append(Paragraph("5. Detailed Profiles & Technical Justification for Top 10 Batters", h1_style))
    for _, r in explanations_df[explanations_df["category"] == "BATTER"].iterrows():
        p_text = f"<b>Rank {r['rank']} — {r['player_name']} (Rating: {r['composite_rating']:.1f})</b><br/>" \
                 f"<i>Role:</i> {r['tactical_role']} &nbsp;|&nbsp; <i>Exposure:</i> {r['sample_exposure']} &nbsp;|&nbsp; <i>Clutch Delta:</i> {r['clutch_elevation']}<br/>" \
                 f"{r['statistical_justification']}"
        story.append(Paragraph(p_text, body_style))
        story.append(Spacer(1, 2))

    story.append(PageBreak())

    story.append(Paragraph("6. Detailed Profiles & Technical Justification for Top 10 Bowlers", h1_style))
    for _, r in explanations_df[explanations_df["category"] == "BOWLER"].iterrows():
        p_text = f"<b>Rank {r['rank']} — {r['player_name']} (Rating: {r['composite_rating']:.1f})</b><br/>" \
                 f"<i>Role:</i> {r['tactical_role']} &nbsp;|&nbsp; <i>Exposure:</i> {r['sample_exposure']} &nbsp;|&nbsp; <i>Clutch Delta:</i> {r['clutch_elevation']}<br/>" \
                 f"{r['statistical_justification']}"
        story.append(Paragraph(p_text, body_style))
        story.append(Spacer(1, 2))

    # 7. Statistical Robustness & Sensitivity Testing
    story.append(Spacer(1, 6))
    story.append(Paragraph("7. Statistical Robustness & Sensitivity Verification", h1_style))
    story.append(Paragraph(
        "To verify that our rankings are not sensitive to arbitrary modeling parameters, we subjected the pipeline to a 5-pillar robustness suite:",
        body_style
    ))
    story.append(Paragraph("• <b>Cross-Model Rank Correlation</b>: Batting rankings show exceptional stability between Model C and Model A (Spearman $\\rho = 0.921$, Kendall $\\tau = 0.775$). Bowling rankings demonstrate strong stability across threshold variations.", bullet_style))
    story.append(Paragraph("• <b>Sample Eligibility Sensitivity</b>: Batters were evaluated at 50, 75, and 100 balls; bowlers at 60, 90, and 120 legal balls. Over 80% of top performers retain Top 10 status across all variations.", bullet_style))
    story.append(Paragraph("• <b>Match-Level Cluster Bootstrap (500 Iterations)</b>: Resampling matches with replacement confirms narrow 95% confidence intervals for core ranks (e.g. Tilak Varma median rank 1.0, Rinku Singh median rank 3.0, Rashid Khan median rank 3.0).", bullet_style))
    story.append(Paragraph("• <b>Tournament Portability (IPL vs T20I)</b>: Key players maintain elite status across both the IPL franchise environment and Senior T20Is.", bullet_style))

    # Embed Figure 8 & Figure 10
    fig8_path = os.path.join(config.OUTPUT_DIR, "figures", "fig08_model_ranking_stability_bump.png")
    fig10_path = os.path.join(config.OUTPUT_DIR, "figures", "fig10_bootstrap_confidence_intervals.png")
    if os.path.exists(fig8_path) and os.path.exists(fig10_path):
        img_table4 = Table([
            [Image(fig8_path, width=3.75*inch, height=2.2*inch),
             Image(fig10_path, width=3.75*inch, height=2.2*inch)]
        ], colWidths=[3.85*inch, 3.85*inch])
        img_table4.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(img_table4)

    story.append(Spacer(1, 8))

    # 8. Limitations & Recommendations
    story.append(Paragraph("8. Methodological Limitations & Franchise Actionability", h1_style))
    story.append(Paragraph(
        "<b>Limitations</b>: (1) Standard ball-by-ball feeds lack sub-second ball-tracking trajectories and dynamic field placement coordinates. "
        "(2) Bilateral T20Is feature occasional opposition quality variance, addressed here via Empirical Bayes shrinkage and IPL weighting. "
        "(3) Sample size constraints inevitably exclude high-potential emerging players who have faced fewer than 75 pressure balls.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Franchise Tactical Actionability</b>: For auction strategy and high-pressure match situations, franchise analysts should target "
        "batters with demonstrated positive clutch strike rate deltas (Tilak Varma, Dhruv Jurel, Rinku Singh, David Miller) and pair them with "
        "phase-adjusted run suppressors (Rashid Khan, Jasprit Bumrah, Sunil Narine, Mujeeb Ur Rahman) who consistently outperform phase expectation.",
        body_style
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated publication-grade PDF report: {output_pdf_path}")


if __name__ == "__main__":
    pdf_out = os.path.join(config.OUTPUT_DIR, "reports", "methodology_report.pdf")
    build_methodology_pdf(pdf_out)

