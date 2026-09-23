"""Unit tests for statistical analyzer."""
import pytest
from src.analyzer import EduDataAnalyzer
from src.fetchers.catalog import DatasetCatalog

def test_analyzer_computations():
    catalog = DatasetCatalog()
    ds = catalog.get("japan_national_assessment_math")
    assert ds is not None
    angle = ds.research_angles[0]

    analyzer = EduDataAnalyzer()
    res = analyzer.analyze(ds, angle)

    # Check descriptive stats
    assert len(res.descriptive_stats) > 0
    stat0 = res.descriptive_stats[0]
    assert stat0.count > 0
    assert stat0.mean > 0

    # Check trend regressions
    assert len(res.trend_regressions) > 0
    reg0 = res.trend_regressions[0]
    assert 0.0 <= reg0.r_squared <= 1.0
    assert 0.0 <= reg0.p_value <= 1.0

    # Check narrative
    assert len(res.summary_narrative) > 50
    assert "Mean =" in res.summary_narrative

    # Check multivariate regression with VIF control
    assert len(res.multivariate_regressions) > 0
    for mv in res.multivariate_regressions:
        assert mv.max_vif < 5.0
        assert mv.is_clean_vif is True
        for pred, vif in mv.vif_values.items():
            assert vif < 5.0

    # Check empirical discoveries
    assert len(res.empirical_discoveries) > 0
    assert "VIF" in res.summary_narrative
