"""
Data models for OpenDataAnalysisTokouynu.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd


@dataclass
class DatasetResearchAngle:
    """A specific academic research angle / research question for a dataset."""
    id: str
    title: str
    focus_metrics: List[str]
    research_questions: List[str]
    hypotheses: List[str]
    theoretical_framework: str
    target_group: Optional[str] = None


@dataclass
class EducationDataset:
    """Represents an open dataset of Japanese educational / public statistics."""
    id: str
    title: str
    title_ja: str
    category: str
    source_name: str
    source_url: str
    description: str
    unit: str
    time_col: str
    group_col: Optional[str]
    metrics: List[str]
    data: List[Dict[str, Any]]
    research_angles: List[DatasetResearchAngle] = field(default_factory=list)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert raw data dicts to a pandas DataFrame."""
        return pd.DataFrame(self.data)
