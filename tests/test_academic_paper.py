"""Unit tests for English academic paper generation."""
import pytest
from src.academic_paper_en import AcademicPaperGeneratorEn
from src.analyzer import EduDataAnalyzer
from src.fetchers.catalog import DatasetCatalog

def test_paper_generation_and_formatting():
    catalog = DatasetCatalog()
    ds = catalog.get("japan_national_assessment_math")
    angle = ds.research_angles[0]

    analyzer = EduDataAnalyzer()
    res = analyzer.analyze(ds, angle)

    gen = AcademicPaperGeneratorEn()
    paper = gen.generate(ds, res, angle)

    assert len(paper.title) > 10
    assert len(paper.abstract) > 50
    assert len(paper.keywords) >= 3
    assert len(paper.section_1_intro) > 50
    assert len(paper.section_4_results) > 50
    assert len(paper.references) >= 3

    # Check Markdown formatting
    md = paper.to_markdown()
    assert f"# {paper.title}" in md
    assert "## 1. Introduction & Background" in md
    assert "## 7. References" in md

    # Check HTML formatting
    html = paper.to_html()
    assert '<div class="academic-paper-container"' in html
    assert f">{paper.title}</h1>" in html
