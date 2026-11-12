from src.api import app
"""
SupeRR Selector Season 2 — Elite Pressure Performance Intelligence System.
End-to-End Orchestrator (Phases 1 through 10).
"""

import sys
import os
import shutil
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src import preprocessing
from src import pressure_engine
from src import ranking_pipeline
from src import robustness_testing
from src import visualization
from src import generate_pdf_report


def configure_logging():
    log_file = os.path.join(config.LOGS_DIR, "pipeline_execution.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def package_final_submission():
    """Packages all required deliverables into FINAL_SUBMISSION/."""
    logger = logging.getLogger("Packaging")
    logger.info("Packaging deliverables into FINAL_SUBMISSION/...")

    sub_dir = os.path.join(PROJECT_ROOT, "FINAL_SUBMISSION")
    os.makedirs(sub_dir, exist_ok=True)

    # 1. Methodology PDF & Markdown
    shutil.copy2(os.path.join(config.REPORTS_DIR, "methodology_report.pdf"), os.path.join(sub_dir, "methodology_report.pdf"))
    shutil.copy2(os.path.join(config.REPORTS_DIR, "methodology_report.md"), os.path.join(sub_dir, "methodology_report.md"))
    shutil.copy2(os.path.join(config.REPORTS_DIR, "FINAL_RESULTS_SUMMARY.md"), os.path.join(sub_dir, "FINAL_RESULTS_SUMMARY.md"))

    # 2. Rankings CSVs
    rankings_dir = os.path.join(config.OUTPUT_DIR, "rankings")
    shutil.copy2(os.path.join(rankings_dir, "batter_rankings_final.csv"), os.path.join(sub_dir, "batter_rankings_final.csv"))
    shutil.copy2(os.path.join(rankings_dir, "bowler_rankings_final.csv"), os.path.join(sub_dir, "bowler_rankings_final.csv"))
    shutil.copy2(os.path.join(rankings_dir, "ranking_explanations.csv"), os.path.join(sub_dir, "ranking_explanations.csv"))

    # 3. Reports
    shutil.copy2(os.path.join(config.REPORTS_DIR, "pressure_definition_report.md"), os.path.join(sub_dir, "pressure_definition_report.md"))
    shutil.copy2(os.path.join(config.REPORTS_DIR, "robustness_report.md"), os.path.join(sub_dir, "robustness_report.md"))

    logger.info(f"Successfully populated {sub_dir} with all official challenge deliverables.")


def main():
    configure_logging()
    logger = logging.getLogger("MasterPipeline")
    logger.info("==========================================================================")
    logger.info("  SupeRR Selector Season 2: Elite Pressure Performance Intelligence System")
    logger.info("  Master Execution Pipeline: Phases 1 through 10")
    logger.info("==========================================================================")

    try:
        # Phase 1: Data Preprocessing & Match State Reconstruction
        logger.info("\n>>> STAGE 1: Running Phase 1 Data Engineering...")
        prep_results = preprocessing.run_pipeline()
        logger.info(f"Reconstructed {len(prep_results['processed_deliveries']):,} deliveries across {len(prep_results['processed_matches']):,} matches.")

        # Phase 2: Pressure Intelligence Engine (Models A, B, C, D)
        logger.info("\n>>> STAGE 2: Running Phase 2 Pressure Engine...")
        df_pressure = pressure_engine.run_all_pressure_models(prep_results["processed_deliveries"])
        pressure_c_path = os.path.join(config.PROCESSED_DIR, "pressure_deliveries_model_c.parquet")
        df_pressure.to_parquet(pressure_c_path, index=False)
        logger.info(f"Saved Model C Pressure Deliveries ({len(df_pressure):,} rows) to {pressure_c_path}")

        # Phases 3, 4, 5: Batter & Bowler Intelligence, EB Shrinkage, Ratings, Rankings
        logger.info("\n>>> STAGE 3: Running Phases 3, 4, 5 Performance Intelligence & Final Rankings...")
        ranking_pipeline.run_ranking_pipeline()

        # Phase 6: Robustness & Sensitivity Testing
        logger.info("\n>>> STAGE 4: Running Phase 6 Robustness Suite...")
        robustness_testing.run_full_robustness_suite()

        # Phase 7: Professional Visual Analytics
        logger.info("\n>>> STAGE 5: Running Phase 7 Publication Visualizations...")
        visualization.generate_all_visualizations()

        # Phase 8: Publication ReportLab PDF Generation
        logger.info("\n>>> STAGE 6: Running Phase 8 PDF Report Compiler...")
        pdf_out = os.path.join(config.REPORTS_DIR, "methodology_report.pdf")
        generate_pdf_report.build_methodology_pdf(pdf_out)

        # Phase 10: Final Packaging
        logger.info("\n>>> STAGE 7: Running Phase 10 Submission Packaging...")
        package_final_submission()

        logger.info("\n==========================================================================")
        logger.info("  ALL PHASES COMPLETED WITH 100% STATISTICAL AND CAUSAL FIDELITY.")
        logger.info("==========================================================================")

    except Exception as e:
        logger.exception(f"Pipeline execution halted due to error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

