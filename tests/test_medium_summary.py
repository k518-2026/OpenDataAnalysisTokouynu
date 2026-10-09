"""Unit tests for Medium executive summary generation adhering to Trust & Safety policies."""
from pathlib import Path
import pytest

from src.academic_paper_en import AcademicPaperGeneratorEn
from src.analyzer import EduDataAnalyzer
from src.fetchers.catalog import DatasetCatalog
from src.medium_summary import MediumSummaryBuilder, build_summary_from_report_dir, sanitize_text


def test_generate_summary_structure(tmp_path):
    catalog = DatasetCatalog()
    ds = catalog.get("japan_national_assessment_math")
    angle = ds.research_angles[0]

    analyzer = EduDataAnalyzer()
    res = analyzer.analyze(ds, angle)

    gen = AcademicPaperGeneratorEn()
    paper = gen.generate(ds, res, angle)

    builder = MediumSummaryBuilder()
    wp_url = "https://seda68.wordpress.com/2026/09/test-post"
    summary_md = builder.generate_summary(
        paper=paper,
        analysis=res,
        dataset=ds,
        wp_url=wp_url,
        figure_paths=[Path("trend.png"), Path("corr.png")],
    )

    # 1. Structure checks (Standalone deep-dive article)
    assert "# " in summary_md
    assert "### " in summary_md
    assert "Society for Educational Data Analysis (SEDA)" in summary_md
    assert "## 1. The Core Paradox & Empirical Context" in summary_md
    assert "## 2. Research Design & Dual Inferential Framework" in summary_md
    assert "## 3. Quantitative Discoveries & Statistical Evidence" in summary_md
    assert "## 4. Policy & Practical Implications" in summary_md
    assert "## 5. Methodological Limitations & Future Scope" in summary_md
    assert "### Citation & Academic Attribution" in summary_md
    assert "**Recommended Medium Tags**:" in summary_md

    # 2. Strict anti-spam checks: ZERO promotional off-site gateway links in article body
    assert "Read the Full Peer-Reviewed Academic Paper" not in summary_md
    assert "Read the Full Academic Paper on WordPress" not in summary_md
    assert "Download Publication-Ready PDF" not in summary_md
    assert "👉" not in summary_md
    assert "https://seda68.wordpress.com" not in summary_md

    # 3. Tofu / Subscript character checks
    tofu_chars = ["\u2080", "\u2081", "\u2082", "\u209a", "\u1d62"]
    for ch in tofu_chars:
        assert ch not in summary_md, f"Found Unicode subscript '{hex(ord(ch))}' in Medium summary"

    # 4. Standard APA notation
    assert "BF₁₀" not in summary_md
    assert "ηₚ²" not in summary_md


def test_generate_and_save(tmp_path):
    catalog = DatasetCatalog()
    ds = catalog.get("japan_mext_ict_informatization")
    analyzer = EduDataAnalyzer()
    res = analyzer.analyze(ds)
    gen = AcademicPaperGeneratorEn()
    paper = gen.generate(ds, res)

    builder = MediumSummaryBuilder()
    out_file = tmp_path / "medium_summary.md"
    saved_path = builder.generate_and_save(
        paper=paper,
        output_path=out_file,
        analysis=res,
        dataset=ds,
    )

    assert saved_path.exists()
    content = saved_path.read_text(encoding="utf-8")
    assert len(content) > 500
    # No off-site promotional links in markdown body
    assert "👉" not in content
    assert "Read the Full Academic Paper" not in content

    # Assert HTML counterpart also exists and contains interactive copy helper and Canonical URL setup
    html_path = out_file.with_suffix(".html")
    assert html_path.exists()
    html_text = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html_text
    assert "copyForMedium" in html_text
    assert "id=\"medium-article-content\"" in html_text
    assert "canonicalUrlInput" in html_text
    assert "copyCanonicalUrl" in html_text
    assert "Customize canonical link" in html_text
    assert "seda2030.wordpress.com" in html_text
    assert "<h1>" in html_text
    assert "<h2>" in html_text
    assert "<strong>" in html_text


def test_build_summary_from_report_dir(tmp_path):
    # Test on an existing report directory
    from src.config import REPORTS_DIR
    dirs = [d for d in REPORTS_DIR.iterdir() if d.is_dir() and (d / "paper.md").exists()]
    assert len(dirs) > 0, "At least one report directory must exist"

    sample_dir = dirs[0]
    out = build_summary_from_report_dir(
        report_dir=sample_dir,
        output_filename="test_medium_summary.md",
    )
    assert out is not None
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert len(content) > 500
    assert "👉" not in content
    assert "Read the Full Academic Paper" not in content
    
    html_out = out.with_suffix(".html")
    assert html_out.exists()
    html_text = html_out.read_text(encoding="utf-8")
    assert "canonicalUrlInput" in html_text
    assert "Customize canonical link" in html_text

    # Clean up test files
    out.unlink()
    html_out.unlink()
