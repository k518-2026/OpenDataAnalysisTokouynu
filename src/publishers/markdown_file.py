"""
Markdown File Publisher for OpenDataAnalysisTokouynu.
Persists research paper markdown and figures into the local repository reports/ directory.
"""
from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
import shutil
from typing import List, Optional

from src.academic_paper_en import AcademicPaperEn
from src.analyzer import EmpiricalAnalysisResult
from src.config import REPORTS_DIR
from src.fetchers.base import EducationDataset
from src.peer_review_en import PeerReviewReportEn
from src.publishers.base import BasePublisher
from src.reporter import EduReportBuilder

logger = logging.getLogger(__name__)


class MarkdownFilePublisher(BasePublisher):
    """Saves generated research papers locally in reports/ directory."""

    def __init__(self, reports_dir: Optional[Path] = None):
        self.reports_dir = reports_dir or REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)
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
        date_str = datetime.now().strftime("%Y-%m-%d")
        paper_folder = self.reports_dir / f"{date_str}_{paper.dataset_id}_{paper.angle_id}"
        paper_folder.mkdir(parents=True, exist_ok=True)

        # Copy figures into paper folder
        saved_figures = []
        for fig in figure_paths:
            if fig.exists():
                dst = paper_folder / fig.name
                shutil.copy2(fig, dst)
                saved_figures.append(dst)

        # Copy PDF if present
        if pdf_path and pdf_path.exists():
            shutil.copy2(pdf_path, paper_folder / pdf_path.name)

        # Generate markdown content
        md_content = self.builder.build_article_markdown(
            paper=paper,
            analysis=analysis,
            dataset=dataset,
            figure_paths=saved_figures,
            peer_review=peer_review,
        )

        md_file = paper_folder / "paper.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Persisted research paper to local folder: {paper_folder.name}")
        return str(md_file)
