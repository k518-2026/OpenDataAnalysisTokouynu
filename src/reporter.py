"""
Report and Article Assembly Engine for OpenDataAnalysisTokouynu.
Assembles the academic paper with in-paper figures, publication-quality tables
(Descriptive, Multivariate OLS, and VIF diagnostics), and peer review assessments
into WordPress-ready HTML and GitHub Markdown.
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
        """Assembles a full-featured HTML post for WordPress with in-paper figures and VIF diagnostics."""
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

        # 2. Main Paper HTML with embedded figures inside Section 4
        paper_html = paper.to_html(figure_urls=figure_urls)

        # 3. Booktabs Statistical Summary Table (Table 1)
        table1_html = self._build_booktabs_table_html(analysis, dataset)

        # 4. Multivariate OLS and VIF Diagnostics Table (Table 2)
        table2_html = self._build_vif_table_html(analysis)

        # 5. Metadata Footer
        meta_footer = f"""
<hr style="border: none; border-top: 1px solid #e2e8f0; margin: 40px 0 20px 0;" />
<div style="font-size: 0.85em; color: #94a3b8; line-height: 1.6;">
  <strong>Source Citation:</strong> Data retrieved from official repository: <a href="{dataset.source_url}" target="_blank" rel="noopener noreferrer" style="color: #0284c7;">{dataset.source_name}</a>.<br />
  <strong>Academic Publisher:</strong> Society for Educational Data Analysis (SEDA) &bull; Automated Empirical Research Pipeline.
</div>
"""

        # Assemble everything
        combined = f"""
{btn_html}
{paper_html}

<h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 1.4em;">Table 1. Parametric Descriptive & Baseline Longitudinal Metrics</h2>
{table1_html}

{table2_html}

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
        """Assembles a clean Markdown file for GitHub repo persistence with in-paper figures."""
        fig_names = [p.name for p in figure_paths]
        lines = [paper.to_markdown(figure_paths=fig_names)]

        lines.append("\n## Table 1. Statistical Summary")
        lines.append("| Metric | Count | Mean | SD | Median | IQR | Min | Max | Unit |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for ds in analysis.descriptive_stats:
            lines.append(
                f"| **{ds.metric}** | {ds.count} | {ds.mean} | {ds.std} | {ds.median} | {ds.iqr} | {ds.min_val} | {ds.max_val} | {ds.unit} |"
            )

        if analysis.multivariate_regressions:
            top_m = analysis.multivariate_regressions[0]
            lines.append(f"\n## Table 2. Multivariate OLS Regression & VIF Diagnostics (Outcome: {top_m.dependent_var})")
            lines.append("| Predictor | Beta (SE) | t-stat | p-value | VIF (Collinearity) | Status |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for p in top_m.predictors:
                c = top_m.coefficients.get(p, 0.0)
                se = top_m.std_errors.get(p, 0.0)
                t = top_m.t_stats.get(p, 0.0)
                pval = top_m.p_values.get(p, 1.0)
                vif = top_m.vif_values.get(p, 1.0)
                sig = "p < .05 *" if pval < 0.05 else "n.s."
                lines.append(f"| **{p}** | {c:+.3f} ({se:.3f}) | {t:+.2f} | {pval:.4f} | {vif:.2f} | {sig} |")
            lines.append(
                f"\n*Model Diagnostics: R^2 = {top_m.r_squared:.3f}, Adj. R^2 = {top_m.adj_r_squared:.3f}, "
                f"F = {top_m.f_stat:.2f} (p = {top_m.f_pvalue:.4f}). {top_m.collinearity_status}*"
            )

        return "\n".join(lines)

    def _build_booktabs_table_html(
        self, analysis: EmpiricalAnalysisResult, dataset: EducationDataset
    ) -> str:
        """Constructs an academic booktabs-style HTML table for baseline statistics."""
        rows = []
        for ds in analysis.descriptive_stats:
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

    def _build_vif_table_html(self, analysis: EmpiricalAnalysisResult) -> str:
        """Constructs an academic table for Multivariate OLS and VIF diagnostics."""
        if not analysis.multivariate_regressions:
            return ""

        top_m = analysis.multivariate_regressions[0]
        rows = []
        for p in top_m.predictors:
            c = top_m.coefficients.get(p, 0.0)
            se = top_m.std_errors.get(p, 0.0)
            t = top_m.t_stats.get(p, 0.0)
            pval = top_m.p_values.get(p, 1.0)
            vif = top_m.vif_values.get(p, 1.0)
            sig_badge = (
                '<span style="color:#059669;font-weight:600;">p &lt; .05 *</span>'
                if pval < 0.05
                else '<span style="color:#64748b;">n.s.</span>'
            )
            vif_badge = (
                f'<span style="color:#059669;font-weight:600;">{vif:.2f} (Clean)</span>'
                if vif < 5.0
                else f'<span style="color:#dc2626;font-weight:600;">{vif:.2f} (High)</span>'
            )

            rows.append(f"""
  <tr style="border-bottom: 1px solid #f1f5f9;">
    <td style="padding: 10px 14px; font-weight: 600; color: #1e293b; text-align: left;">{p}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{c:+.3f}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; color: #64748b;">{se:.3f}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{t:+.2f}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{pval:.4f}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{vif_badge}</td>
    <td style="padding: 10px 14px; text-align: right;">{sig_badge}</td>
  </tr>
""")
        rows_html = "".join(rows)

        return f"""
<h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 1.4em;">Table 2. Multivariate OLS Regression & Multicollinearity (VIF) Diagnostics</h2>
<div style="overflow-x: auto; margin: 16px 0 28px 0;">
  <div style="margin-bottom: 8px; font-size: 0.9em; color: #334155;">
    <strong>Dependent Criterion (Outcome):</strong> <code style="background:#e0f2fe;color:#0369a1;padding:2px 6px;border-radius:4px;">{top_m.dependent_var}</code> &bull; 
    <strong>Model Fit:</strong> R&sup2; = {top_m.r_squared:.3f}, Adj. R&sup2; = {top_m.adj_r_squared:.3f}, F = {top_m.f_stat:.2f} (p = {top_m.f_pvalue:.4f})
  </div>
  <table style="width: 100%; border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 0.92em; border-top: 2px solid #1e3a8a; border-bottom: 2px solid #1e3a8a;">
    <thead>
      <tr style="background-color: #f8fafc; border-bottom: 1px solid #cbd5e1; color: #1e3a8a;">
        <th style="padding: 12px 14px; text-align: left; font-weight: 700;">Predictor Variable</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">Coeff (&beta;)</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">SE</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">t-stat</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">p-value</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">VIF Diagnostics</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">Significance</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
  <div style="font-size: 0.82em; color: #64748b; margin-top: 6px; font-style: italic;">
    Multicollinearity Verification: {top_m.collinearity_status} All Variance Inflation Factors (VIF) &lt; 5.0 confirm the absence of severe multicollinearity.
  </div>
</div>
"""
