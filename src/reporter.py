"""
Report and Article Assembly Engine for OpenDataAnalysisTokouynu.
Assembles the academic paper, publication-quality tables, visual figures,
and peer review assessments into WordPress-ready HTML and GitHub Markdown.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from src.academic_paper_en import AcademicPaperEn
from src.analyzer import EmpiricalAnalysisResult
from src.fetchers.base import EducationDataset
from src.peer_review_en import PeerReviewReportEn

logger = logging.getLogger(__name__)


class EduReportBuilder:
    """Constructs comprehensive HTML and Markdown publication content."""

    def build_article_html(
        self,
        paper: AcademicPaperEn,
        analysis: EmpiricalAnalysisResult,
        dataset: EducationDataset,
        figure_urls: List[str],
        peer_review: Optional[PeerReviewReportEn] = None,
        pdf_download_url: Optional[str] = None,
    ) -> str:
        """Assembles a full-featured HTML post for WordPress."""
        # 1. Download Buttons (if PDF available)
        btn_html = ""
        if pdf_download_url:
            btn_html = f"""
<div style="margin: 20px 0 28px 0; display: flex; gap: 12px; flex-wrap: wrap;">
  <a href="{pdf_download_url}" target="_blank" rel="noopener noreferrer" style="background: #1e3a8a; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 0.9em; display: inline-flex; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <svg style="width:16px;height:16px;margin-right:8px;fill:currentColor;" viewBox="0 0 20 20"><path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"/><path d="M8 11a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"/></svg>
    Download Full Academic Paper (PDF)
  </a>
</div>
"""

        # 2. Main Paper HTML
        paper_html = paper.to_html()

        # 3. Booktabs Statistical Summary Table
        table_html = self._build_booktabs_table_html(analysis, dataset)

        # 4. Figures HTML
        figures_html = ""
        if figure_urls:
            figures_html = '<div style="margin: 30px 0;">'
            for idx, url in enumerate(figure_urls):
                caption = f"Figure {idx + 1}: Quantitative Visualizer Output & Trend Trajectory"
                figures_html += f"""
<figure style="margin: 24px 0; text-align: center;">
  <img src="{url}" alt="{caption}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;" />
  <figcaption style="margin-top: 8px; font-size: 0.88em; color: #64748b; font-style: italic;">{caption}</figcaption>
</figure>
"""
            figures_html += "</div>"

        # 5. Peer Review Assessment
        review_html = peer_review.to_html() if peer_review else ""

        # 6. Metadata Footer
        meta_footer = f"""
<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 40px 0 20px 0;" />
<div style="font-size: 0.85em; color: #94a3b8; line-height: 1.6;">
  <strong>Source Citation:</strong> Data retrieved from official repository: <a href="{dataset.source_url}" target="_blank" rel="noopener noreferrer" style="color: #0284c7;">{dataset.source_name}</a>.<br />
  <strong>Automated Pipeline:</strong> Published autonomously via <em>OpenDataAnalysisTokouynu</em> (Daily Research Pipeline).
</div>
"""

        # Assemble everything
        # Insert table and figures within the results section or right after
        combined = f"""
{btn_html}
{paper_html}

<h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 1.4em;">Table 1. Parametric Descriptive & Inferential Statistics</h2>
{table_html}

{figures_html}

{review_html}

{meta_footer}
"""
        return combined

    def build_article_markdown(
        self,
        paper: AcademicPaperEn,
        analysis: EmpiricalAnalysisResult,
        dataset: EducationDataset,
        figure_paths: List[Path],
        peer_review: Optional[PeerReviewReportEn] = None,
    ) -> str:
        """Assembles a clean Markdown file for GitHub repo persistence."""
        lines = [paper.to_markdown()]

        lines.append("\n## Table 1. Statistical Summary")
        lines.append("| Metric | Count | Mean | SD | Median | IQR | Min | Max | Unit |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for ds in analysis.descriptive_stats:
            lines.append(
                f"| **{ds.metric}** | {ds.count} | {ds.mean} | {ds.std} | {ds.median} | {ds.iqr} | {ds.min_val} | {ds.max_val} | {ds.unit} |"
            )

        if figure_paths:
            lines.append("\n## Figures")
            for idx, p in enumerate(figure_paths):
                lines.append(f"![Figure {idx + 1}]({p.name})\n*Figure {idx + 1}: Longitudinal empirical trajectory.*")

        if peer_review:
            lines.append("\n" + peer_review.to_markdown())

        return "\n".join(lines)

    def _build_booktabs_table_html(
        self, analysis: EmpiricalAnalysisResult, dataset: EducationDataset
    ) -> str:
        """Constructs an academic booktabs-style HTML table."""
        rows = []
        for ds in analysis.descriptive_stats:
            # find corresponding regression if available
            reg = next((r for r in analysis.trend_regressions if r.metric == ds.metric), None)
            slope_str = f"{reg.slope:+.3f}" if reg else "—"
            r2_str = f"{reg.r_squared:.3f}" if reg else "—"
            p_str = f"{reg.p_value:.4f}" if reg else "—"

            rows.append(f"""
  <tr style="border-bottom: 1px solid #f1f5f9;">
    <td style="padding: 10px 14px; font-weight: 600; color: #1e293b; text-align: left;">{ds.metric}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{ds.count}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 500;">{ds.mean:.2f}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; color: #64748b;">{ds.std:.2f}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{ds.median:.2f}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{ds.iqr:.2f}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; color: #0284c7;">{slope_str}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{r2_str}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{p_str}</td>
  </tr>
""")
        rows_html = "".join(rows)

        return f"""
<div style="overflow-x: auto; margin: 20px 0 28px 0;">
  <table style="width: 100%; border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 0.92em; border-top: 2px solid #1e3a8a; border-bottom: 2px solid #1e3a8a;">
    <thead>
      <tr style="background-color: #f8fafc; border-bottom: 1px solid #cbd5e1; color: #1e3a8a;">
        <th style="padding: 12px 14px; text-align: left; font-weight: 700;">Metric Name</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">N</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">Mean</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">SD</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">Median</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">IQR</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">Slope (&beta;)</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">R&sup2;</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">p-value</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
  <div style="font-size: 0.82em; color: #64748b; margin-top: 6px; font-style: italic;">
    Note: N denotes sample observation waves. Slope (&beta;) and R&sup2; derived via ordinary least squares (OLS) longitudinal regression.
  </div>
</div>
"""
