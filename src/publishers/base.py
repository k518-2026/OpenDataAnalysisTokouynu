"""
Publisher Base Class for OpenDataAnalysisTokouynu.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from src.academic_paper_en import AcademicPaperEn
from src.analyzer import EmpiricalAnalysisResult
from src.fetchers.base import EducationDataset
from src.peer_review_en import PeerReviewReportEn


class BasePublisher(ABC):
    """Abstract base class for publishing academic research articles."""

    @abstractmethod
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
        """
        Publishes the article.
        Returns the published URL (or local path) upon success, or None on failure.
        """
        pass
