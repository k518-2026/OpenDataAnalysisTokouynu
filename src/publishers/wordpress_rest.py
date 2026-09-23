"""
WordPress REST API Publisher for OpenDataAnalysisTokouynu.
Publishes articles with media upload, featured images, and academic categorization.
"""
from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import List, Optional

import requests

from src.academic_paper_en import AcademicPaperEn
from src.analyzer import EmpiricalAnalysisResult
from src.config import Config
from src.fetchers.base import EducationDataset
from src.peer_review_en import PeerReviewReportEn
from src.publishers.base import BasePublisher
from src.reporter import EduReportBuilder

logger = logging.getLogger(__name__)


class WordPressRestPublisher(BasePublisher):
    """Publishes academic papers directly via WordPress REST API."""

    def __init__(self):
        self.site_url = Config.WP_SITE_URL.rstrip("/")
        self.user = Config.WP_USER
        self.password = Config.WP_APP_PASSWORD
        self.builder = EduReportBuilder()

    def _get_auth_header(self) -> dict:
        token = base64.b64encode(f"{self.user}:{self.password}".encode("utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {token}"}

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
            logger.info("Dry-run mode: Simulating WordPress REST API publication.")
            return f"{self.site_url}/simulated-post-{paper.dataset_id}"

        if not self.user or not self.password:
            logger.error("WP_USER or WP_APP_PASSWORD not configured. Cannot publish via REST API.")
            return None

        # 1. Upload media figures
        figure_urls: List[str] = []
        featured_media_id: Optional[int] = None

        headers = self._get_auth_header()

        for idx, fig_path in enumerate(figure_paths):
            try:
                media_id, source_url = self._upload_image(fig_path, headers)
                if source_url:
                    figure_urls.append(source_url)
                if idx == 0 and media_id:
                    featured_media_id = media_id
            except Exception as e:
                logger.warning(f"Failed to upload media {fig_path.name}: {e}")

        # 2. Upload PDF if available
        pdf_download_url: Optional[str] = None
        if pdf_path and pdf_path.exists():
            try:
                _, pdf_download_url = self._upload_pdf(pdf_path, headers)
            except Exception as e:
                logger.warning(f"Failed to upload PDF {pdf_path.name}: {e}")

        # If PDF upload is not supported, construct raw GitHub public URL as fallback
        if not pdf_download_url and pdf_path:
            pdf_download_url = (
                f"https://raw.githubusercontent.com/{Config.GITHUB_REPOSITORY}/"
                f"{Config.GITHUB_BRANCH}/reports/pdf/{pdf_path.name}"
            )

        # 3. Assemble full article HTML
        content_html = self.builder.build_article_html(
            paper=paper,
            analysis=analysis,
            dataset=dataset,
            figure_urls=figure_urls,
            peer_review=peer_review,
            pdf_download_url=pdf_download_url,
        )

        # 4. Resolve Categories
        category_ids = self._resolve_categories(Config.DEFAULT_CATEGORIES, headers)

        # 5. Create post
        post_endpoint = f"{self.site_url}/wp-json/wp/v2/posts"
        payload = {
            "title": paper.title,
            "content": content_html,
            "status": Config.WP_POST_STATUS,
            "categories": category_ids,
        }
        if featured_media_id:
            payload["featured_media"] = featured_media_id

        try:
            resp = requests.post(post_endpoint, json=payload, headers=headers, timeout=30)
            if resp.status_code in [200, 201]:
                post_data = resp.json()
                post_url = post_data.get("link", f"{self.site_url}/?p={post_data.get('id')}")
                logger.info(f"Successfully published article to WordPress: {post_url}")
                return post_url
            else:
                logger.error(f"WordPress REST API post failed ({resp.status_code}): {resp.text}")
                return None
        except Exception as e:
            logger.error(f"Error connecting to WordPress REST API: {e}")
            return None

    def _upload_image(self, file_path: Path, headers: dict) -> tuple[Optional[int], Optional[str]]:
        """Uploads an image file to WordPress Media Library."""
        endpoint = f"{self.site_url}/wp-json/wp/v2/media"
        media_headers = dict(headers)
        media_headers.update({
            "Content-Disposition": f'attachment; filename="{file_path.name}"',
            "Content-Type": "image/png",
        })

        with open(file_path, "rb") as f:
            data = f.read()

        resp = requests.post(endpoint, data=data, headers=media_headers, timeout=30)
        if resp.status_code in [200, 201]:
            j = resp.json()
            media_id = j.get("id")
            source_url = j.get("source_url")
            logger.info(f"Uploaded media {file_path.name} (ID: {media_id})")
            return media_id, source_url
        logger.warning(f"Media upload failed ({resp.status_code}): {resp.text}")
        return None, None

    def _upload_pdf(self, file_path: Path, headers: dict) -> tuple[Optional[int], Optional[str]]:
        """Uploads a PDF file to WordPress Media Library."""
        endpoint = f"{self.site_url}/wp-json/wp/v2/media"
        media_headers = dict(headers)
        media_headers.update({
            "Content-Disposition": f'attachment; filename="{file_path.name}"',
            "Content-Type": "application/pdf",
        })

        with open(file_path, "rb") as f:
            data = f.read()

        resp = requests.post(endpoint, data=data, headers=media_headers, timeout=30)
        if resp.status_code in [200, 201]:
            j = resp.json()
            media_id = j.get("id")
            source_url = j.get("source_url")
            return media_id, source_url
        return None, None

    def _resolve_categories(self, cat_names_str: str, headers: dict) -> List[int]:
        """Maps category names to IDs, creating new ones if not existing."""
        cat_names = [c.strip() for c in cat_names_str.split(",") if c.strip()]
        if not cat_names:
            return []

        cat_ids: List[int] = []
        endpoint = f"{self.site_url}/wp-json/wp/v2/categories"

        try:
            resp = requests.get(endpoint, params={"per_page": 100}, headers=headers, timeout=15)
            existing = {}
            if resp.status_code == 200:
                for c in resp.json():
                    existing[c["name"].lower()] = c["id"]

            for name in cat_names:
                if name.lower() in existing:
                    cat_ids.append(existing[name.lower()])
                else:
                    # Create new category
                    create_resp = requests.post(endpoint, json={"name": name}, headers=headers, timeout=15)
                    if create_resp.status_code in [200, 201]:
                        cat_ids.append(create_resp.json()["id"])
        except Exception as e:
            logger.warning(f"Category resolution error: {e}")

        return cat_ids
