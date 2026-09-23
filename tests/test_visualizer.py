"""Unit tests for English academic visualizer."""
import pytest
from pathlib import Path
from src.analyzer import EduDataAnalyzer
from src.config import TEMP_DIR
from src.fetchers.catalog import DatasetCatalog
from src.visualizer import EduDataVisualizer

def test_visualizer_generates_images():
    catalog = DatasetCatalog()
    ds = catalog.get("japan_national_assessment_math")
    angle = ds.research_angles[0]

    analyzer = EduDataAnalyzer()
    res = analyzer.analyze(ds, angle)

    viz = EduDataVisualizer(output_dir=TEMP_DIR)
    figs = viz.generate_figures(ds, res)

    assert len(figs) >= 2
    for fig_path in figs:
        assert fig_path.exists()
        assert fig_path.stat().st_size > 1000


def test_visualizer_group_disparity_with_ci():
    catalog = DatasetCatalog()
    ds = catalog.get("japan_mext_ict_informatization")
    angle = ds.research_angles[0]

    analyzer = EduDataAnalyzer()
    res = analyzer.analyze(ds, angle)

    viz = EduDataVisualizer(output_dir=TEMP_DIR)
    disparity_fig = viz._plot_group_disparity(ds, res, res.raw_df)
    assert disparity_fig is not None
    assert disparity_fig.exists()
    assert disparity_fig.stat().st_size > 1000
