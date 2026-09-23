"""Unit tests for ThemeDuplicateChecker and anti-duplicate selection."""
import pytest
from src.duplicate_checker import ThemeDuplicateChecker
from src.fetchers.catalog import DatasetCatalog


def test_tokenization_and_stopwords():
    checker = ThemeDuplicateChecker()
    title = "An Empirical Investigation of Japanese Public Open Data on Mathematics Literacy Trends"
    tokens = checker.tokenize_title(title)
    # Stopwords like 'an', 'empirical', 'investigation', 'of', 'japanese', 'public', 'open', 'data', 'on', 'trends' should be filtered
    assert "mathematics" in tokens
    assert "literacy" in tokens
    assert "empirical" not in tokens
    assert "japanese" not in tokens


def test_title_duplicate_detection():
    checker = ThemeDuplicateChecker(title_similarity_threshold=0.55)
    history = [
        {
            "date": "2026-09-23",
            "title": "Gender Parity Trajectories in Collegiate Computing and Engineering Admissions in Japan",
            "dataset_id": "japan_stem_cs_enrollment",
            "angle_id": "female_stem_parity",
        },
        {
            "date": "2026-09-23",
            "title": "The Entrance Exam Washback Paradox: How High-Stakes Testing Standardized Python Adoption",
            "dataset_id": "japan_high_school_informatics",
            "angle_id": "entrance_exam_washback_paradox",
        },
    ]

    # Test 1: Substantially overlapping title should be detected as duplicate
    dup_title = "Gender Parity in Collegiate Computing and Engineering Admissions in Japan"
    res1 = checker.check_title_against_history(dup_title, history)
    assert res1.is_duplicate is True
    assert res1.similarity_score >= 0.55
    assert "Gender Parity" in res1.reason

    # Test 2: Completely distinct title should pass
    fresh_title = "MEXT Special Needs Resource Rooms and Assistive Technology in Primary Schools"
    res2 = checker.check_title_against_history(fresh_title, history)
    assert res2.is_duplicate is False
    assert res2.similarity_score < 0.55


def test_candidate_ranking_prioritizes_unposted_datasets():
    catalog = DatasetCatalog()
    checker = ThemeDuplicateChecker(dataset_cooldown=3)

    all_pairs = []
    for ds in catalog.list_datasets():
        for ang in ds.research_angles:
            all_pairs.append((ds, ang))

    # Simulate history where japan_stem_cs_enrollment was posted
    history = [
        {"dataset_id": "japan_stem_cs_enrollment", "angle_id": "female_stem_parity", "date": "2026-09-23"},
        {"dataset_id": "japan_high_school_informatics", "angle_id": "entrance_exam_washback_paradox", "date": "2026-09-23"},
    ]

    ranked = checker.filter_and_rank_candidates(all_pairs, history)
    assert len(ranked) > 0

    # The top candidate MUST NOT be from a recently posted dataset
    top_ds, top_ang = ranked[0]
    assert top_ds.id not in ["japan_stem_cs_enrollment", "japan_high_school_informatics"]
    assert top_ds.id in [
        "japan_mext_ict_informatization",
        "japan_national_assessment_math",
        "japan_school_absenteeism_bullying",
        "japan_special_needs_education",
        "japan_teacher_workload_survey",
        "japan_timss_math_science",
        "oecd_pisa_math_ict",
        "oecd_talis_teacher_survey",
        "unesco_world_ict_skills",
        "worldbank_education_indicators",
    ]


def test_dataset_cooldown_prevents_immediate_reuse():
    catalog = DatasetCatalog()
    checker = ThemeDuplicateChecker(dataset_cooldown=2)

    all_pairs = []
    for ds in catalog.list_datasets():
        for ang in ds.research_angles:
            all_pairs.append((ds, ang))

    # Place japan_national_assessment_math in recent history
    history = [
        {"dataset_id": "japan_national_assessment_math", "angle_id": "math_affective_gap", "date": "2026-09-24"},
    ]

    ranked = checker.filter_and_rank_candidates(all_pairs, history)
    top_ds, top_ang = ranked[0]
    # Even though japan_national_assessment_math has a second angle ('giga_device_impact'),
    # it must NOT be selected consecutively when other unposted datasets exist!
    assert top_ds.id != "japan_national_assessment_math"
