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


def test_paper_has_no_japanese_characters():
    import re
    cjk_pattern = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]')

    catalog = DatasetCatalog()
    analyzer = EduDataAnalyzer()
    gen = AcademicPaperGeneratorEn()

    # Test all datasets
    for ds in catalog.list_datasets():
        res = analyzer.analyze(ds)
        paper = gen.generate(ds, res)

        full_text = f"{paper.title} {paper.abstract} {paper.section_1_intro} {paper.section_2_hypotheses} {paper.section_3_method} {paper.section_4_results} {paper.section_5_discussion} {paper.section_6_limitations}"
        match = cjk_pattern.search(full_text)
        assert match is None, f"Found Japanese text in paper for {ds.id}: {match.group() if match else ''}"

