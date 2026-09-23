"""Unit tests for Dataset Catalog and daily rotation."""
import pytest
from src.fetchers.catalog import DatasetCatalog

def test_catalog_loads_datasets():
    catalog = DatasetCatalog()
    datasets = catalog.list_datasets()
    assert len(datasets) > 0
    # Check that japan_national_assessment_math is present
    ds = catalog.get("japan_national_assessment_math")
    assert ds is not None
    assert "Mathematics" in ds.title
    assert len(ds.research_angles) >= 1
    assert len(ds.data) > 0

def test_catalog_daily_rotation():
    catalog = DatasetCatalog()
    history = []
    ds1, angle1 = catalog.select_next_dataset_and_angle(posted_history=history)
    assert ds1 is not None
    assert angle1 is not None

    # Simulate posting ds1 & angle1
    history.append({"dataset_id": ds1.id, "angle_id": angle1.id, "date": "2026-09-23"})
    ds2, angle2 = catalog.select_next_dataset_and_angle(posted_history=history)
    assert ds2 is not None
    assert angle2 is not None
    # Ensure rotation selected a different angle or dataset
    assert f"{ds1.id}::{angle1.id}" != f"{ds2.id}::{angle2.id}"
