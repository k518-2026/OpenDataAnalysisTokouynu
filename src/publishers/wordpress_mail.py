"""
WordPress Post by Email Publisher for OpenDataAnalysisTokouynu.
Publishes articles by sending MIME emails with attached figures via SMTP.
"""
from __future__ import annotations

from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from pathlib import Path
import smtplib
from typing import List, Optional

from src.academic_paper_en import AcademicPaperEn
from src.analyzer import EmpiricalAnalysisResult
from src.config import Config
from src.fetchers.base import EducationDataset
from src.peer_review_en import PeerReviewReportEn
from src.publishers.base import BasePublisher
from src.reporter import EduReportBuilder

logger = logging.getLogger(__name__)


class WordPressMailPublisher(BasePublisher):
    """Publishes articles via WordPress Post by Email (SMTP)."""

    def __init__(self):
        self.builder = EduReportBuilder()

    def publish(
        self,
        paper: AcademicPaperEn,
        analysis: EmpiricalAnalysisResult,
        dataset: EducationDataset,
        figure_paths: List[Path],
        peer_review: Optional[PeerReviewReportEn] = None,
        pdf_path: Optional[Path] = None,
        dry_run: bool = False,
    ) -> Optional[str]:
        if dry_run:
            logger.info("Dry-run mode: Simulating WordPress email publication.")
            return "simulated://wordpress-email-sent"

        if not Config.WP_POST_EMAIL or not Config.SMTP_USER or not Config.SMTP_PASS:
            logger.error("SMTP or WP_POST_EMAIL credentials missing. Cannot publish via email.")
            return None

        # Build content HTML
        # In Post by Email, shortcodes can be placed in subject or body
        status_tag = f"[status {Config.WP_POST_STATUS}]"
        cat_tag = f"[category {Config.DEFAULT_CATEGORIES}]"

        html_body = self.builder.build_article_html(
            paper=paper,
            analysis=analysis,
            dataset=dataset,
            figure_urls=[],
            peer_review=peer_review,
        )

        full_html = f"{status_tag} {cat_tag}\n\n{html_body}"

        msg = MIMEMultipart("mixed")
        msg["Subject"] = paper.title
        msg["From"] = Config.SMTP_USER
        msg["To"] = Config.WP_POST_EMAIL

        # Attach HTML body
        msg.attach(MIMEText(full_html, "html", "utf-8"))

        # Attach image figures
        for fig_path in figure_paths:
            if fig_path.exists():
                with open(fig_path, "rb") as f:
                    img = MIMEImage(f.read(), name=fig_path.name)
                    img.add_header("Content-Disposition", "attachment", filename=fig_path.name)
                    msg.attach(img)

        # Attach PDF if available
        if pdf_path and pdf_path.exists():
            with open(pdf_path, "rb") as f:
                pdf_att = MIMEApplication(f.read(), _subtype="pdf")
                pdf_att.add_header("Content-Disposition", "attachment", filename=pdf_path.name)
                msg.attach(pdf_att)

        try:
            logger.info(f"Connecting to SMTP server {Config.SMTP_HOST}:{Config.SMTP_PORT}...")
            server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=30)
            server.ehlo()
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASS)
            server.sendmail(Config.SMTP_USER, [Config.WP_POST_EMAIL], msg.as_string())
            server.quit()
            logger.info("Successfully sent paper to WordPress via email.")
            return f"mailto:{Config.WP_POST_EMAIL}"
        except Exception as e:
            logger.error(f"Failed to publish via SMTP email: {e}")
            return None
