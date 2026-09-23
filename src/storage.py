"""
Storage and History Management for OpenDataAnalysisTokouynu.
Maintains machine-readable JSON history and human-readable Markdown archives.
"""
from __future__ import annotations

from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.academic_paper_en import AcademicPaperEn
from src.config import Config

logger = logging.getLogger(__name__)


class PaperStorage:
    """Manages paper posting history and archive synchronization."""

    def __init__(
        self,
        json_path: Optional[Path] = None,
        archive_path: Optional[Path] = None,
    ):
        self.json_path = json_path or Config.POSTED_PAPERS_PATH
        self.archive_path = archive_path or Config.PAPERS_ARCHIVE_PATH

    def load_history(self) -> List[Dict[str, Any]]:
        """Loads previous posting history from JSON."""
        if not self.json_path.exists():
            return []
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load history from {self.json_path}: {e}")
            return []

    def record_publication(
        self,
        paper: AcademicPaperEn,
        wp_url: Optional[str] = None,
        pdf_path: Optional[Path] = None,
        dry_run: bool = False,
    ) -> None:
        """Records a new published paper into history and updates PAPERS_ARCHIVE.md."""
        if dry_run:
            logger.info("Dry-run mode: Skipping persistent history update.")
            return

        history = self.load_history()
        today_str = datetime.now().strftime("%Y-%m-%d")

        new_entry = {
            "date": today_str,
            "title": paper.title,
            "dataset_id": paper.dataset_id,
            "angle_id": paper.angle_id,
            "wp_url": wp_url or "",
            "pdf_filename": pdf_path.name if pdf_path else "",
            "timestamp": datetime.now().isoformat(),
        }

        # Prepend to history (newest first)
        history.insert(0, new_entry)

        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            logger.info(f"Updated posting history in {self.json_path.name}")
        except Exception as e:
            logger.error(f"Failed to write history JSON: {e}")

        self._update_archive_markdown(history)

    def _update_archive_markdown(self, history: List[Dict[str, Any]]) -> None:
        """Re-generates PAPERS_ARCHIVE.md table in GitHub repository."""
        lines = [
            "# Published Empirical Research Papers Archive",
            "",
            "Autonomous daily empirical working papers derived from Japanese government open data.",
            "",
            f"**Total Published Papers**: `{len(history)}`  ",
            f"**Last Updated**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
            "",
            "| Date | Research Paper Title | Focus Topic | WP Post | PDF Download |",
            "| :--- | :--- | :--- | :---: | :---: |",
        ]

        for item in history:
            date = item.get("date", "")
            title = item.get("title", "")
            angle = item.get("angle_id", "")
            wp_url = item.get("wp_url", "")
            pdf_name = item.get("pdf_filename", "")

            wp_link = f"[Read Article]({wp_url})" if wp_url else "—"
            pdf_link = f"[PDF](../reports/pdf/{pdf_name})" if pdf_name else "—"

            lines.append(f"| {date} | **{title}** | `{angle}` | {wp_link} | {pdf_link} |")

        try:
            with open(self.archive_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            logger.info(f"Synchronized archive markdown: {self.archive_path.name}")
        except Exception as e:
            logger.error(f"Failed to update archive markdown: {e}")
