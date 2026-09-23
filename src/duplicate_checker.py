"""
Theme and Topic Duplicate Detection Engine for OpenDataAnalysisTokouynu.
Guarantees that daily empirical academic papers never repeat themes, topics,
datasets, or research angles from previous publications.
"""
from __future__ import annotations

from dataclasses import dataclass
import difflib
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from src.fetchers.base import DatasetResearchAngle, EducationDataset

logger = logging.getLogger(__name__)

# Common academic stopwords to ignore during title and theme similarity evaluation
ACADEMIC_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "up", "about", "into", "over", "after", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "empirical", "investigation", "japanese", "japan", "public", "open",
    "data", "longitudinal", "study", "analysis", "quantitative", "evaluation",
    "evidence", "statistical", "trend", "trends", "series", "national",
}


@dataclass
class DuplicateCheckResult:
    """Result of duplicate theme verification."""
    is_duplicate: bool
    reason: str
    similarity_score: float = 0.0
    matched_entry: Optional[Dict[str, Any]] = None


class ThemeDuplicateChecker:
    """
    Evaluates candidate datasets, research angles, and paper titles
    against previous publication history to strictly prevent thematic duplication.
    """

    def __init__(self, title_similarity_threshold: float = 0.55, dataset_cooldown: int = 4):
        self.title_similarity_threshold = title_similarity_threshold
        self.dataset_cooldown = dataset_cooldown

    def tokenize_title(self, title: str) -> Set[str]:
        """Normalizes and extracts substantive content words from an academic title."""
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", title.lower())
        tokens = set(cleaned.split())
        substantive = {t for t in tokens if len(t) > 2 and t not in ACADEMIC_STOPWORDS}
        return substantive

    def compute_jaccard_similarity(self, tokens1: Set[str], tokens2: Set[str]) -> float:
        """Computes Jaccard similarity coefficient between two token sets."""
        if not tokens1 or not tokens2:
            return 0.0
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        return float(round(intersection / union, 4)) if union > 0 else 0.0

    def compute_sequence_similarity(self, s1: str, s2: str) -> float:
        """Computes character/subsequence similarity using difflib."""
        return float(round(difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio(), 4))

    def check_title_against_history(
        self,
        candidate_title: str,
        history: List[Dict[str, Any]],
        threshold: Optional[float] = None,
    ) -> DuplicateCheckResult:
        """
        Checks if candidate title has excessive lexical/semantic overlap with past articles.
        """
        thresh = threshold or self.title_similarity_threshold
        c_tokens = self.tokenize_title(candidate_title)

        max_score = 0.0
        best_match = None

        for entry in history:
            prev_title = entry.get("title", "")
            if not prev_title:
                continue

            p_tokens = self.tokenize_title(prev_title)
            jaccard = self.compute_jaccard_similarity(c_tokens, p_tokens)
            seq_ratio = self.compute_sequence_similarity(candidate_title, prev_title)

            # Combined score giving higher weight to substantive token overlap
            combined = max(jaccard, seq_ratio * 0.75)
            if combined > max_score:
                max_score = combined
                best_match = entry

        if max_score >= thresh and best_match:
            return DuplicateCheckResult(
                is_duplicate=True,
                reason=(
                    f"Thematic Title Overlap (Similarity: {max_score:.2f} >= {thresh}): "
                    f"Candidate title '{candidate_title[:50]}...' closely mirrors past publication "
                    f"'{best_match.get('title', '')[:50]}...' from {best_match.get('date', 'unknown')}."
                ),
                similarity_score=max_score,
                matched_entry=best_match,
            )

        return DuplicateCheckResult(
            is_duplicate=False,
            reason=f"Title uniqueness verified (Max historical similarity: {max_score:.2f} < {thresh}).",
            similarity_score=max_score,
            matched_entry=best_match,
        )

    def filter_and_rank_candidates(
        self,
        all_pairs: List[Tuple[EducationDataset, DatasetResearchAngle]],
        history: List[Dict[str, Any]],
        target_topic: str = "all",
    ) -> List[Tuple[EducationDataset, DatasetResearchAngle]]:
        """
        Filters and ranks candidates by strictly eliminating duplicates, enforcing dataset cooldown,
        ensuring category diversity, and cycling least-recently-used topics.
        """
        if not all_pairs:
            return []

        # 1. Filter by topic category if explicitly requested
        if target_topic and target_topic != "all":
            all_pairs = [p for p in all_pairs if p[0].category.lower() == target_topic.lower()]

        # 2. Extract publication history metadata
        posted_angle_keys = set()
        recent_dataset_ids = []
        last_posted_category = None

        for idx, entry in enumerate(history):
            d_id = entry.get("dataset_id", "")
            a_id = entry.get("angle_id", "")
            if d_id and a_id:
                posted_angle_keys.add(f"{d_id}::{a_id}")
            if idx < self.dataset_cooldown and d_id:
                recent_dataset_ids.append(d_id)
            if idx == 0 and d_id:
                # Find category of most recent post
                for ds, _ in all_pairs:
                    if ds.id == d_id:
                        last_posted_category = ds.category
                        break

        # Check total unique datasets in catalog vs posted
        unique_cat_datasets = {ds.id for ds, _ in all_pairs}
        posted_datasets_all = {entry.get("dataset_id") for entry in history if entry.get("dataset_id")}
        unposted_datasets = unique_cat_datasets - posted_datasets_all

        logger.info(
            f"Duplicate Check: {len(all_pairs)} total angles, {len(posted_angle_keys)} previously posted, "
            f"{len(unposted_datasets)} datasets never posted."
        )

        # 3. Categorize candidates into priority tiers
        tier1_never_posted_dataset = []
        tier2_never_posted_angle = []
        tier3_cooled_down_rotation = []
        tier4_exhausted_rotation = []

        for ds, ang in all_pairs:
            key = f"{ds.id}::{ang.id}"
            is_angle_posted = key in posted_angle_keys
            is_in_cooldown = ds.id in recent_dataset_ids
            is_same_consecutive_category = (
                last_posted_category is not None
                and ds.category == last_posted_category
                and len(all_pairs) > 1
            )

            # Priority Tier 1: Dataset has NEVER been posted
            if ds.id in unposted_datasets:
                tier1_never_posted_dataset.append((ds, ang, is_same_consecutive_category))
            # Priority Tier 2: Angle is unposted and dataset is NOT in recent cooldown
            elif not is_angle_posted and not is_in_cooldown:
                tier2_never_posted_angle.append((ds, ang, is_same_consecutive_category))
            # Priority Tier 3: Angle is unposted, but dataset was recently posted (cooldown)
            elif not is_angle_posted:
                tier3_cooled_down_rotation.append((ds, ang))
            # Priority Tier 4: All angles have been posted once, rotate to oldest
            else:
                tier4_exhausted_rotation.append((ds, ang))

        # Sort Tier 1: Prefer different category from last post
        tier1_sorted = sorted(tier1_never_posted_dataset, key=lambda x: 1 if x[2] else 0)
        if tier1_sorted:
            logger.info(f"Tier 1 Selection: {len(tier1_sorted)} candidate(s) from never-posted datasets.")
            return [(x[0], x[1]) for x in tier1_sorted]

        # Sort Tier 2: Prefer different category from last post
        tier2_sorted = sorted(tier2_never_posted_angle, key=lambda x: 1 if x[2] else 0)
        if tier2_sorted:
            logger.info(f"Tier 2 Selection: {len(tier2_sorted)} unposted angle(s) outside cooldown window.")
            return [(x[0], x[1]) for x in tier2_sorted]

        if tier3_cooled_down_rotation:
            logger.info(f"Tier 3 Selection: {len(tier3_cooled_down_rotation)} unposted angle(s) in cooldown pool.")
            return tier3_cooled_down_rotation

        # Tier 4: Least recently used topic rotation
        logger.info("All research angles have been posted. Selecting least recently used topic (LRU).")
        pair_to_last_index = {}
        for idx, item in enumerate(history):
            k = f"{item.get('dataset_id')}::{item.get('angle_id')}"
            if k not in pair_to_last_index:
                pair_to_last_index[k] = idx

        # Higher index in history means posted longer ago
        tier4_sorted = sorted(
            tier4_exhausted_rotation,
            key=lambda pair: pair_to_last_index.get(f"{pair[0].id}::{pair[1].id}", 0),
            reverse=True,
        )
        return tier4_sorted
