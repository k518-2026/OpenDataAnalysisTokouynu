"""
Dataset Catalog and Daily Rotation Selector for OpenDataAnalysisTokouynu.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.config import CATALOG_DIR
from src.duplicate_checker import ThemeDuplicateChecker
from src.fetchers.base import DatasetResearchAngle, EducationDataset

logger = logging.getLogger(__name__)


class DatasetCatalog:
    """Manages the repository of Japanese public open datasets and angles."""

    def __init__(self, catalog_dir: Optional[Path] = None):
        self.catalog_dir = catalog_dir or CATALOG_DIR
        self._datasets: Dict[str, EducationDataset] = {}
        self.duplicate_checker = ThemeDuplicateChecker()
        self.load_all()

    def load_all(self) -> None:
        """Loads all JSON dataset files from the catalog directory."""
        self._datasets.clear()
        json_files = list(self.catalog_dir.glob("*.json"))
        logger.info(f"Loading data catalog from {self.catalog_dir} (found {len(json_files)} files)")

        for filepath in json_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    raw = json.load(f)

                angles = []
                for a in raw.get("research_angles", []):
                    angles.append(
                        DatasetResearchAngle(
                            id=a.get("id", ""),
                            title=a.get("title", ""),
                            focus_metrics=a.get("focus_metrics", []),
                            research_questions=a.get("research_questions", []),
                            hypotheses=a.get("hypotheses", []),
                            theoretical_framework=a.get("theoretical_framework", ""),
                            target_group=a.get("target_group"),
                        )
                    )

                dataset = EducationDataset(
                    id=raw["id"],
                    title=raw.get("title", raw.get("title_en", raw["id"])),
                    title_ja=raw.get("title_ja", raw.get("title", "")),
                    category=raw.get("category", "general"),
                    source_name=raw.get("source_name", "Official Japanese Government Statistics"),
                    source_url=raw.get("source_url", ""),
                    description=raw.get("description", ""),
                    unit=raw.get("unit", ""),
                    time_col=raw.get("time_col", "Year"),
                    group_col=raw.get("group_col"),
                    metrics=raw.get("metrics", []),
                    data=raw.get("data", []),
                    research_angles=angles,
                )
                self._datasets[dataset.id] = dataset
            except Exception as e:
                logger.error(f"Failed to load dataset {filepath.name}: {e}")

        logger.info(f"Successfully loaded {len(self._datasets)} datasets.")

    def get(self, dataset_id: str) -> Optional[EducationDataset]:
        """Retrieve a specific dataset by ID."""
        return self._datasets.get(dataset_id)

    def list_datasets(self) -> List[EducationDataset]:
        """List all loaded datasets."""
        return list(self._datasets.values())

    def select_next_dataset_and_angle(
        self,
        posted_history: List[Dict[str, str]],
        target_dataset_id: str = "",
        target_angle_id: str = "",
        target_topic: str = "all",
    ) -> Tuple[Optional[EducationDataset], Optional[DatasetResearchAngle]]:
        """
        Selects the next dataset and research angle with strict duplicate prevention.
        Prioritizes never-posted datasets, enforces dataset cooldown, maintains category diversity,
        and avoids thematic overlap with all historical publications.
        """
        # If explicitly specified by user:
        if target_dataset_id:
            ds = self.get(target_dataset_id)
            if not ds:
                logger.warning(f"Target dataset '{target_dataset_id}' not found.")
                return None, None

            if target_angle_id:
                for angle in ds.research_angles:
                    if angle.id == target_angle_id:
                        return ds, angle

            # If no angle specified, find an unposted angle for this dataset
            posted_angle_ids = {
                item.get("angle_id") for item in posted_history if item.get("dataset_id") == ds.id
            }
            unposted_angles = [a for a in ds.research_angles if a.id not in posted_angle_ids]
            if unposted_angles:
                return ds, unposted_angles[0]

            # Return first angle or None
            angle = ds.research_angles[0] if ds.research_angles else None
            return ds, angle

        # Build list of all candidate (dataset, angle) pairs
        candidates = list(self._datasets.values())
        all_pairs: List[Tuple[EducationDataset, DatasetResearchAngle]] = []
        for ds in candidates:
            if ds.research_angles:
                for angle in ds.research_angles:
                    all_pairs.append((ds, angle))
            else:
                pseudo_angle = DatasetResearchAngle(
                    id="general_empirical_analysis",
                    title=f"Empirical Statistical Analysis of {ds.title}",
                    focus_metrics=ds.metrics[:3],
                    research_questions=[f"What are the longitudinal trends and disparities in {ds.title}?"],
                    hypotheses=["Longitudinal indicators exhibit statistically significant structural changes."],
                    theoretical_framework="Quantitative Policy Evaluation and Longitudinal Trend Modeling",
                )
                all_pairs.append((ds, pseudo_angle))

        if not all_pairs:
            return None, None

        # Filter and rank using ThemeDuplicateChecker
        ranked_candidates = self.duplicate_checker.filter_and_rank_candidates(
            all_pairs=all_pairs,
            history=posted_history,
            target_topic=target_topic,
        )

        if ranked_candidates:
            selected_ds, selected_angle = ranked_candidates[0]
            logger.info(
                f"Selected Next Research Topic: '{selected_ds.id}' (Category: {selected_ds.category}) "
                f"-> Angle: '{selected_angle.id}' ('{selected_angle.title[:50]}...')"
            )
            return selected_ds, selected_angle

        return all_pairs[0]
