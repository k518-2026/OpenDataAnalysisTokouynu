"""
Dataset Catalog and Daily Rotation Selector for OpenDataAnalysisTokouynu.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.config import CATALOG_DIR
from src.fetchers.base import DatasetResearchAngle, EducationDataset

logger = logging.getLogger(__name__)


class DatasetCatalog:
    """Manages the repository of Japanese public open datasets and angles."""

    def __init__(self, catalog_dir: Optional[Path] = None):
        self.catalog_dir = catalog_dir or CATALOG_DIR
        self._datasets: Dict[str, EducationDataset] = {}
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
        Selects the next dataset and research angle based on posting history rotation.
        Ensures a fresh, non-duplicate academic paper topic every single day.
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
            # Return first angle or None
            angle = ds.research_angles[0] if ds.research_angles else None
            return ds, angle

        # Filter by topic if requested
        candidates = list(self._datasets.values())
        if target_topic and target_topic != "all":
            candidates = [d for d in candidates if d.category == target_topic]

        if not candidates:
            logger.warning(f"No datasets match topic filter: {target_topic}")
            candidates = list(self._datasets.values())

        # Build list of all available (dataset, angle) pairs
        all_pairs: List[Tuple[EducationDataset, DatasetResearchAngle]] = []
        for ds in candidates:
            if ds.research_angles:
                for angle in ds.research_angles:
                    all_pairs.append((ds, angle))
            else:
                # Fallback pseudo-angle
                pseudo_angle = DatasetResearchAngle(
                    id="general_empirical_analysis",
                    title=f"Empirical Statistical Analysis of {ds.title}",
                    focus_metrics=ds.metrics[:3],
                    research_questions=[f"What are the longitudinal trends and disparities in {ds.title}?"],
                    hypotheses=["Longitudinal indicators exhibit statistically significant structural changes."],
                    theoretical_framework="Quantitative Policy Evaluation and Longitudinal Trend Modeling",
                )
                all_pairs.append((ds, pseudo_angle))

        # Check against history
        # History entry has {"dataset_id": ..., "angle_id": ..., "date": ...}
        posted_angle_keys = set()
        for item in posted_history:
            d_id = item.get("dataset_id", "")
            a_id = item.get("angle_id", "")
            posted_angle_keys.add(f"{d_id}::{a_id}")

        # Find unposted pairs first
        unposted = [
            (ds, ang) for ds, ang in all_pairs if f"{ds.id}::{ang.id}" not in posted_angle_keys
        ]
        if unposted:
            logger.info(f"Found {len(unposted)} unposted research angle(s). Selecting first in rotation.")
            return unposted[0]

        # If all have been posted, cycle back to the least recently posted pair
        logger.info("All research angles have been posted once. Selecting least recently posted topic.")
        # Find which pair appeared earliest in posted_history
        pair_to_last_index = {}
        for idx, item in enumerate(posted_history):
            key = f"{item.get('dataset_id')}::{item.get('angle_id')}"
            pair_to_last_index[key] = idx

        # Sort all pairs by last posted index (oldest index first)
        sorted_pairs = sorted(
            all_pairs,
            key=lambda pair: pair_to_last_index.get(f"{pair[0].id}::{pair[1].id}", -1)
        )
        return sorted_pairs[0]
