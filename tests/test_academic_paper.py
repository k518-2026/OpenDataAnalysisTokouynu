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
    assert "Society for Educational Data Analysis (SEDA)" in paper.authors

    # Check Markdown formatting with in-paper figures
    md = paper.to_markdown(figure_paths=["fig1.png", "fig2.png"])
    assert f"# {paper.title}" in md
    assert "Society for Educational Data Analysis (SEDA)" in md
    assert "## 1. Introduction & Background" in md
    assert "## 4. Quantitative Results & Empirical Findings" in md
    assert "![Figure 1](fig1.png)" in md
    assert "![Figure 2](fig2.png)" in md
    assert "## 7. References" in md

    # Check HTML formatting with in-paper figures
    html = paper.to_html(figure_urls=["cid:fig_0", "cid:fig_1"])
    assert '<div class="academic-paper-container"' in html
    assert f">{paper.title}</h1>" in html
    assert "Society for Educational Data Analysis (SEDA)" in html
    assert '4. Quantitative Results & Empirical Findings' in html
    assert '<figure style="margin: 24px 0; text-align: center;">' in html
    assert '<img src="cid:fig_0"' in html

    # Test EduReportBuilder for APA 7th Table 1, Table 2 (ANOVA), and Table 3 (VIF)
    from src.reporter import EduReportBuilder
    builder = EduReportBuilder()
    full_html = builder.build_article_html(paper, res, ds, figure_urls=["cid:fig_0"])
    assert "Table 1" in full_html
    assert "Descriptive Statistics and Bivariate Zero-Correlation" in full_html
    assert "Table 2" in full_html
    assert "Two-Way Factorial Analysis of Variance (ANOVA)" in full_html
    assert "Table 3" in full_html
    assert "Multivariate OLS Multiple Regression" in full_html
    assert "VIF Diagnostics" in full_html
    assert "BF<sub>10</sub>" in full_html


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


def test_pdf_generation_with_figures(tmp_path):
    from src.pdf.pdf_generator_en import AcademicPaperPdfGeneratorEn
    from src.visualizer import EduDataVisualizer

    catalog = DatasetCatalog()
    ds = catalog.get("japan_mext_ict_informatization")
    analyzer = EduDataAnalyzer()
    res = analyzer.analyze(ds)
    gen = AcademicPaperGeneratorEn()
    paper = gen.generate(ds, res)

    # Generate figures
    viz = EduDataVisualizer(output_dir=tmp_path)
    figs = viz.generate_figures(ds, res)
    assert len(figs) > 0

    # Generate PDF with figures
    pdf_gen = AcademicPaperPdfGeneratorEn(output_dir=tmp_path)
    pdf_path = pdf_gen.generate(paper, figure_paths=figs)
    assert pdf_path is not None
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000  # Non-empty PDF


