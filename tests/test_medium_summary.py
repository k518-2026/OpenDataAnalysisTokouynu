"""Unit tests for Medium executive summary generation."""
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

    # 1. Structure checks
    assert "# " in summary_md
    assert "### " in summary_md
    assert "Society for Educational Data Analysis (SEDA)" in summary_md
    assert "## 1. The Core Paradox (TL;DR)" in summary_md
    assert "## 2. Three Key Empirical Discoveries" in summary_md
    assert "## 3. Policy & Real-World Implications" in summary_md
    assert "Read the Full Peer-Reviewed Academic Paper" in summary_md
    assert wp_url in summary_md
    assert "seda68.wordpress.com" in summary_md
    assert "**Recommended Medium Tags**:" in summary_md

    # 2. Tofu / Subscript character checks
    tofu_chars = ["\u2080", "\u2081", "\u2082", "\u209a", "\u1d62"]
    for ch in tofu_chars:
        assert ch not in summary_md, f"Found Unicode subscript '{hex(ord(ch))}' in Medium summary"

    # 3. Standard APA notation
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
    assert "seda68.wordpress.com" in content


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
    assert len(content) > 300
    assert "seda68.wordpress.com" in content
    # Clean up test file
    out.unlink()
