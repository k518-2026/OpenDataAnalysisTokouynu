"""
OpenDataAnalysisTokouynu - Main Pipeline Entry Point.
Executes data selection, statistical modeling, English academic paper synthesis,
visualization, PDF compilation, WordPress publication, and history synchronization.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import io
import logging
from pathlib import Path
import sys

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.academic_paper_en import AcademicPaperGeneratorEn
from src.analyzer import EduDataAnalyzer
from src.config import Config, REPORTS_DIR, TEMP_DIR
from src.fetchers.catalog import DatasetCatalog
from src.duplicate_checker import ThemeDuplicateChecker
from src.pdf.pdf_generator_en import AcademicPaperPdfGeneratorEn
from src.publishers.markdown_file import MarkdownFilePublisher
from src.publishers.wordpress_mail import WordPressMailPublisher
from src.publishers.wordpress_rest import WordPressRestPublisher
from src.storage import PaperStorage
from src.visualizer import EduDataVisualizer

# Force UTF-8 on Windows stdout/stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("OpenDataAnalysisTokouynu")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Daily Japanese Open Data Empirical Analysis & English Paper Publisher"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without posting to WordPress or altering remote history.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore recent rotation history and force topic execution.",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="",
        help="Filter topic category: 'math', 'info', 'policy', 'all', etc.",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="",
        help="Target a specific dataset ID (e.g. 'japan_national_assessment_math').",
    )
    parser.add_argument(
        "--angle",
        type=str,
        default="",
        help="Target a specific research angle ID.",
    )
    parser.add_argument(
        "--publisher",
        type=str,
        default="",
        help="Override publisher type: 'wordpress_rest', 'wordpress_mail', or 'markdown_only'.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logger.info("================================================================")
    logger.info("🚀 Starting OpenDataAnalysisTokouynu Daily Paper Pipeline")
    logger.info("================================================================")

    # 1. Initialize core system components
    catalog = DatasetCatalog()
    analyzer = EduDataAnalyzer()
    visualizer = EduDataVisualizer(output_dir=TEMP_DIR)
    paper_gen = AcademicPaperGeneratorEn()
    pdf_gen = AcademicPaperPdfGeneratorEn()
    storage = PaperStorage()
    md_publisher = MarkdownFilePublisher()

    # Load history
    history = [] if args.force else storage.load_history()

    # 2. Select dataset and research angle
    topic = (args.topic or Config.DEFAULT_TOPIC or "all").strip().strip("'\"").lower()
    target_dataset = args.dataset.strip().strip("'\"") if args.dataset else ""
    target_angle = args.angle.strip().strip("'\"") if args.angle else ""

    dataset, angle = catalog.select_next_dataset_and_angle(
        posted_history=history,
        target_dataset_id=target_dataset,
        target_angle_id=target_angle,
        target_topic=topic,
    )

    if not dataset:
        logger.error("No valid dataset found in catalog to process. Exiting.")
        sys.exit(1)

    logger.info(f"Target Dataset: {dataset.id} - '{dataset.title}'")
    if angle:
        logger.info(f"Target Research Angle: {angle.id} - '{angle.title}'")

    # 3. Statistical Analysis
    logger.info("Executing empirical statistical analysis (Descriptive, OLS, Relational, Multivariate VIF)...")
    analysis = analyzer.analyze(dataset, angle)
    logger.info(
        f"Calculated {len(analysis.descriptive_stats)} metric descriptive models, "
        f"{len(analysis.trend_regressions)} trend regressions, "
        f"{len(analysis.relational_regressions)} relational models, "
        f"{len(analysis.multivariate_regressions)} multivariate VIF models."
    )

    # 4. Generate Publication Figures (in English)
    logger.info("Rendering publication-quality visual charts in English...")
    figure_paths = visualizer.generate_figures(dataset, analysis)
    logger.info(f"Generated {len(figure_paths)} visual figures.")

    # 5. English Academic Paper Generation (IMRaD)
    logger.info("Synthesizing English academic paper...")
    paper = paper_gen.generate(dataset, analysis, angle)
    logger.info(f"Paper Title: '{paper.title}' ({len(paper.abstract.split())} words in abstract)")

    # 5.5 Duplicate Theme Verification against Historical Publications
    checker = ThemeDuplicateChecker()
    dup_res = checker.check_title_against_history(paper.title, history)
    if dup_res.is_duplicate:
        if args.force:
            logger.warning(f"⚠️ DUPLICATE THEME WARNING (Ignored via --force): {dup_res.reason}")
        else:
            logger.warning(f"⚠️ DUPLICATE THEME OVERLAP DETECTED: {dup_res.reason}")
            # Differentiate title subtitle to ensure distinct archival presence
            paper.title = f"{paper.title}: A Distinct Longitudinal Evaluation"
            logger.info(f"Differentiated Paper Title to resolve theme collision: '{paper.title}'")
    else:
        logger.info(f"✅ Theme Duplicate Verification Passed: {dup_res.reason}")

    # 6. Generate PDF Working Paper (with in-paper figures)
    logger.info("Compiling PDF working paper document with in-paper figures...")
    pdf_path = pdf_gen.generate(paper, figure_paths=figure_paths)
    if pdf_path:
        logger.info(f"Compiled PDF: {pdf_path.name}")

    # 7. Always persist locally to reports/
    local_md = md_publisher.publish(
        paper=paper,
        analysis=analysis,
        dataset=dataset,
        figure_paths=figure_paths,
        peer_review=None,
        pdf_path=pdf_path,
        dry_run=args.dry_run,
    )

    # 9. WordPress Publishing
    raw_publisher = args.publisher or Config.BLOG_PUBLISHER_TYPE or "wordpress_mail"
    pub_type = raw_publisher.strip().strip("'\"").lower()
    published_url = None

    logger.info(f"Selected Publisher Mode: '{pub_type}'")

    if pub_type == "wordpress_mail":
        logger.info(f"Publishing to WordPress via Post by Email (SMTP) to {Config.WP_SITE_URL}...")
        mail_publisher = WordPressMailPublisher()
        published_url = mail_publisher.publish(
            paper=paper,
            analysis=analysis,
            dataset=dataset,
            figure_paths=figure_paths,
            peer_review=None,
            pdf_path=pdf_path,
            dry_run=args.dry_run,
        )
        if not published_url and not args.dry_run:
            logger.error("❌ Failed to send email to WordPress. Please check WP_POST_EMAIL, SMTP_USER, and SMTP_PASS secrets.")
            sys.exit(1)

    elif pub_type == "wordpress_rest":
        logger.info(f"Publishing to WordPress via REST API to {Config.WP_SITE_URL}...")
        rest_publisher = WordPressRestPublisher()
        published_url = rest_publisher.publish(
            paper=paper,
            analysis=analysis,
            dataset=dataset,
            figure_paths=figure_paths,
            peer_review=None,
            pdf_path=pdf_path,
            dry_run=args.dry_run,
        )
        if not published_url and not args.dry_run:
            logger.error("❌ Failed to publish via WordPress REST API. Please check WP_USER and WP_APP_PASSWORD secrets.")
            sys.exit(1)

    elif pub_type == "markdown_only":
        logger.info("Publisher set to local markdown only. Skipping external web publication.")
        published_url = local_md

    else:
        logger.error(f"❌ Unknown publisher type: '{pub_type}'. Expected 'wordpress_mail', 'wordpress_rest', or 'markdown_only'.")
        sys.exit(1)

    # 10. Update persistent history and PAPERS_ARCHIVE.md
    if not args.dry_run and published_url:
        storage.record_publication(
            paper=paper,
            wp_url=published_url,
            pdf_path=pdf_path,
            dry_run=args.dry_run,
        )

    logger.info("================================================================")
    logger.info("🎉 Pipeline Execution Complete!")
    logger.info(f"Article Link: {published_url or 'N/A'}")
    logger.info("================================================================")


if __name__ == "__main__":
    main()
