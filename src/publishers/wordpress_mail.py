"""
WordPress Post by Email Publisher for OpenDataAnalysisTokouynu.
Publishes articles to WordPress (e.g. https://seda68.wordpress.com)
by sending MIME emails with inline figures and PDF attachments via SMTP.
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
        target_site = Config.WP_SITE_URL or "https://seda68.wordpress.com"

        if dry_run:
            logger.info(f"Dry-run mode: Simulating WordPress email publication to {target_site} via {Config.WP_POST_EMAIL or 'post-by-email'}.")
            return f"{target_site}/simulated-mail-post-{paper.dataset_id}"

        if not Config.WP_POST_EMAIL or not Config.SMTP_USER or not Config.SMTP_PASS:
            logger.error("SMTP or WP_POST_EMAIL credentials missing. Cannot publish via email.")
            return None

        # Shortcodes for WordPress Post by Email
        status_tag = f"[status {Config.WP_POST_STATUS}]"
        cat_tag = f"[category {Config.DEFAULT_CATEGORIES}]"
        tag_list = ", ".join(paper.keywords[:5])
        tags_code = f"[tags {tag_list}]"

        # Map figure paths to CID URLs for clean inline rendering
        cid_urls: List[str] = []
        for idx in range(len(figure_paths)):
            cid_urls.append(f"cid:fig_{idx}")

        # Construct raw public GitHub link for PDF fallback
        pdf_download_url = None
        if pdf_path:
            pdf_download_url = (
                f"https://raw.githubusercontent.com/{Config.GITHUB_REPOSITORY}/"
                f"{Config.GITHUB_BRANCH}/reports/pdf/{pdf_path.name}"
            )

        html_body = self.builder.build_article_html(
            paper=paper,
            analysis=analysis,
            dataset=dataset,
            figure_urls=cid_urls,
            peer_review=peer_review,
            pdf_download_url=pdf_download_url,
        )

        full_html = f"{status_tag} {cat_tag} {tags_code}\n\n{html_body}"

        # Setup MIME multipart/related container so CID images resolve inline
        msg = MIMEMultipart("related")
        msg["Subject"] = paper.title
        msg["From"] = Config.SMTP_USER
        msg["To"] = Config.WP_POST_EMAIL

        # Alternative part for text/html
        msg_alt = MIMEMultipart("alternative")
        msg_alt.attach(MIMEText(full_html, "html", "utf-8"))
        msg.attach(msg_alt)

        # Attach image figures with CIDs
        for idx, fig_path in enumerate(figure_paths):
            if fig_path.exists():
                with open(fig_path, "rb") as f:
                    img = MIMEImage(f.read(), name=fig_path.name)
                    img.add_header("Content-ID", f"<fig_{idx}>")
                    img.add_header("Content-Disposition", "inline", filename=fig_path.name)
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
            logger.info(f"Successfully posted paper to {target_site} via email ({Config.WP_POST_EMAIL}).")
            return f"{target_site}/?p=latest"
        except Exception as e:
            logger.error(f"Failed to publish via SMTP email: {e}")
            return None
