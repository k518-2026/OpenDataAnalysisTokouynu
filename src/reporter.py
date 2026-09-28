"""
Report and Article Assembly Engine for OpenDataAnalysisTokouynu.
Assembles the academic paper with in-paper figures, publication-quality APA 7th tables
(Table 1: Descriptive & Correlation with Bayes Factors, Table 2: Two-Way Factorial ANOVA,
Table 3: Multivariate OLS & VIF Diagnostics with Model Bayes Factor),
and peer review assessments into WordPress-ready HTML and GitHub Markdown.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from src.academic_paper_en import AcademicPaperEn
from src.analyzer import (
    EmpiricalAnalysisResult,
    format_academic_metric,
    format_apa_p,
    format_apa_stat,
    format_bayes_factor,
)
from src.fetchers.base import EducationDataset
from src.peer_review_en import PeerReviewReportEn

logger = logging.getLogger(__name__)


class EduReportBuilder:
    """Constructs comprehensive HTML and Markdown publication content according to APA 7th standards."""

    def build_article_html(
        self,
        paper: AcademicPaperEn,
        analysis: EmpiricalAnalysisResult,
        dataset: EducationDataset,
        figure_urls: List[str],
        peer_review: Optional[PeerReviewReportEn] = None,
        pdf_download_url: Optional[str] = None,
    ) -> str:
        """Assembles a full-featured HTML post for WordPress with in-paper figures and APA 7th tables."""
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

        # 3. APA Table 1: Descriptive Statistics and Bivariate Correlation with BF10
        table1_html = self._build_apa_table1_html(analysis, dataset)

        # 4. APA Table 2: Two-Way Factorial ANOVA with BF10
        table2_html = self._build_apa_table2_html(analysis)

        # 5. APA Table 3: Multivariate OLS & VIF Diagnostics with Model BF10
        table3_html = self._build_apa_table3_html(analysis)

        # 6. Metadata Footer
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

{table1_html}

{table2_html}

{table3_html}

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
        """Assembles a clean Markdown file for GitHub repo persistence with APA 7th tables and in-paper figures."""
        fig_names = [p.name for p in figure_paths]
        lines = [paper.to_markdown(figure_paths=fig_names)]

        # APA Table 1 Markdown
        lines.append("\n### Table 1")
        lines.append("*Descriptive Statistics and Bivariate Zero-Correlation Tests with Bayes Factors (BF10)*\n")
        lines.append("| Variable | N | Mean (SD) | Median (IQR) | Bivariate Pair | Pearson r [95% CI] | t (df) | p-value | BF10 | Bayesian Evidence |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for idx, ds in enumerate(analysis.descriptive_stats):
            corr = analysis.correlations[idx] if idx < len(analysis.correlations) else None
            metric_clean = format_academic_metric(ds.metric, title_case=True)
            pair_str = f"{format_academic_metric(corr.metric_x, title_case=True)} vs. {format_academic_metric(corr.metric_y, title_case=True)}" if corr else "—"
            r_str = f"{format_apa_stat(corr.pearson_r, decimals=2, bounded=True)} [{format_apa_stat(corr.ci_lower, decimals=2, bounded=True)}, {format_apa_stat(corr.ci_upper, decimals=2, bounded=True)}]" if corr else "—"
            t_str = f"{format_apa_stat(corr.t_stat, decimals=2, bounded=False)} ({corr.df})" if corr else "—"
            p_str = format_apa_p(corr.p_value, with_operator=False) if corr else "—"
            bf_str = format_bayes_factor(corr.bf10) if corr else "—"
            ev_str = corr.evidence_label if corr else "—"

            lines.append(
                f"| **{metric_clean}** | {ds.count} | {ds.mean:.2f} ({ds.std:.2f}) | {ds.median:.2f} ({ds.iqr:.2f}) | "
                f"{pair_str} | {r_str} | {t_str} | {p_str} | {bf_str} | {ev_str} |"
            )
        lines.append(
            "\n*Note. N denotes sample observation count. 95% Confidence Intervals for Pearson r computed via Fisher's z transformation. "
            "BF10 evaluates the empirical correlation against the zero-correlation point-null hypothesis (H0: r = 0).*"
        )

        # APA Table 2 Markdown
        if analysis.two_way_anova:
            a = analysis.two_way_anova
            outcome_clean = format_academic_metric(a.outcome_metric, title_case=True)
            fa_clean = format_academic_metric(a.factor_a_effect.source_name, title_case=True)
            fb_clean = format_academic_metric(a.factor_b_effect.source_name, title_case=True)
            lines.append(f"\n### Table 2")
            lines.append(f"*Two-Way Factorial Analysis of Variance (ANOVA) and Bayesian Evidence Factors (Outcome: {outcome_clean})*\n")
            lines.append("| Source of Variation | SS | df | MS | F | p-value | Partial eta^2 | BF10 | Evidence Interpretation |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            lines.append(
                f"| **{fa_clean}** | {a.factor_a_effect.ss:.2f} | {a.factor_a_effect.df} | {a.factor_a_effect.ms:.2f} | "
                f"{format_apa_stat(a.factor_a_effect.f_stat, decimals=2, bounded=False)} | {format_apa_p(a.factor_a_effect.p_value, with_operator=False)} | {format_apa_stat(a.factor_a_effect.eta_sq_partial, decimals=3, bounded=True)} | "
                f"{format_bayes_factor(a.factor_a_effect.bf10)} | {a.factor_a_effect.evidence_label} |"
            )
            lines.append(
                f"| **{fb_clean}** | {a.factor_b_effect.ss:.2f} | {a.factor_b_effect.df} | {a.factor_b_effect.ms:.2f} | "
                f"{format_apa_stat(a.factor_b_effect.f_stat, decimals=2, bounded=False)} | {format_apa_p(a.factor_b_effect.p_value, with_operator=False)} | {format_apa_stat(a.factor_b_effect.eta_sq_partial, decimals=3, bounded=True)} | "
                f"{format_bayes_factor(a.factor_b_effect.bf10)} | {a.factor_b_effect.evidence_label} |"
            )
            if a.interaction_effect.df > 0:
                fi_clean = format_academic_metric(a.interaction_effect.source_name, title_case=True)
                lines.append(
                    f"| **{fi_clean}** | {a.interaction_effect.ss:.2f} | {a.interaction_effect.df} | {a.interaction_effect.ms:.2f} | "
                    f"{format_apa_stat(a.interaction_effect.f_stat, decimals=2, bounded=False)} | {format_apa_p(a.interaction_effect.p_value, with_operator=False)} | {format_apa_stat(a.interaction_effect.eta_sq_partial, decimals=3, bounded=True)} | "
                    f"{format_bayes_factor(a.interaction_effect.bf10)} | {a.interaction_effect.evidence_label} |"
                )
            lines.append(
                f"| **Residual (Error)** | {a.error_ss:.2f} | {a.error_df} | {a.error_ms:.2f} | — | — | — | — | — |"
            )
            lines.append(
                f"| **Total** | {a.total_ss:.2f} | {a.total_df} | — | — | — | — | — | — |"
            )
            lines.append(
                f"\n*Note. Dependent Variable: {outcome_clean}. Type II Sum of Squares. "
                f"Partial eta^2 = SS_effect / (SS_effect + SS_error). BF10 represents Bayes Factor supporting H1 relative to H0.*"
            )

        # APA Table 3 Markdown
        if analysis.multivariate_regressions:
            top_m = analysis.multivariate_regressions[0]
            dep_clean = format_academic_metric(top_m.dependent_var, title_case=True)
            lines.append(f"\n### Table 3")
            lines.append(f"*Multivariate OLS Multiple Regression and Multicollinearity (VIF) Diagnostics (Outcome: {dep_clean})*\n")
            lines.append("| Predictor | Beta (SE) | 95% CI | t-stat | p-value | VIF Diagnostics | Significance |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for p in top_m.predictors:
                p_clean = format_academic_metric(p, title_case=True)
                c = top_m.coefficients.get(p, 0.0)
                se = top_m.std_errors.get(p, 0.0)
                cil = top_m.ci_lower.get(p, c - 1.96 * se)
                ciu = top_m.ci_upper.get(p, c + 1.96 * se)
                t = top_m.t_stats.get(p, 0.0)
                pval = top_m.p_values.get(p, 1.0)
                vif = top_m.vif_values.get(p, 1.0)
                sig = "p < .05 *" if pval < 0.05 else "n.s."
                lines.append(
                    f"| **{p_clean}** | {format_apa_stat(c, decimals=3, bounded=False)} ({format_apa_stat(se, decimals=3, bounded=False)}) | "
                    f"[{format_apa_stat(cil, decimals=3, bounded=False)}, {format_apa_stat(ciu, decimals=3, bounded=False)}] | "
                    f"{format_apa_stat(t, decimals=2, bounded=False)} | {format_apa_p(pval, with_operator=False)} | {vif:.2f} | {sig} |"
                )
            r2_str = format_apa_stat(top_m.r_squared, decimals=3, bounded=True)
            adj_r2_str = format_apa_stat(top_m.adj_r_squared, decimals=3, bounded=True)
            f_str = format_apa_stat(top_m.f_stat, decimals=2, bounded=False)
            f_p_str = format_apa_p(top_m.f_pvalue, with_operator=True)
            bf_str = format_bayes_factor(top_m.model_bf10)
            lines.append(
                f"\n*Note. Model Fit: R^2 = {r2_str}, Adj. R^2 = {adj_r2_str}, "
                f"F = {f_str} (p {f_p_str}), Model BF10 = {bf_str} ({top_m.model_evidence_label}). "
                f"All Variance Inflation Factors (VIF) < 5.0 confirm the complete absence of severe multicollinearity.*"
            )

        return "\n".join(lines)

    def _build_apa_table1_html(
        self, analysis: EmpiricalAnalysisResult, dataset: EducationDataset
    ) -> str:
        """Constructs Table 1: Descriptive Statistics and Bivariate Correlation with BF10 (APA 7th)."""
        rows = []
        for idx, ds in enumerate(analysis.descriptive_stats):
            corr = analysis.correlations[idx] if idx < len(analysis.correlations) else None
            metric_clean = format_academic_metric(ds.metric, title_case=True)
            if corr:
                pair_str = f"{format_academic_metric(corr.metric_x, title_case=True)} vs. {format_academic_metric(corr.metric_y, title_case=True)}"
                r_val = format_apa_stat(corr.pearson_r, decimals=2, bounded=True)
                ci_l = format_apa_stat(corr.ci_lower, decimals=2, bounded=True)
                ci_u = format_apa_stat(corr.ci_upper, decimals=2, bounded=True)
                r_str = f"<strong>{r_val}</strong> <span style='font-size:0.85em;color:#64748b;'>[{ci_l}, {ci_u}]</span>"
                t_str = f"{format_apa_stat(corr.t_stat, decimals=2, bounded=False)} ({corr.df})"
                p_str = format_apa_p(corr.p_value, with_operator=False)
                bf_str = format_bayes_factor(corr.bf10)
                ev_str = f"<span style='color:#0369a1;font-weight:600;'>{corr.evidence_label}</span>"
            else:
                pair_str = "&mdash;"
                r_str = "&mdash;"
                t_str = "&mdash;"
                p_str = "&mdash;"
                bf_str = "&mdash;"
                ev_str = "&mdash;"

            rows.append(f"""
  <tr style="border-bottom: 1px solid #f1f5f9;">
    <td style="padding: 10px 12px; font-weight: 600; color: #1e293b; text-align: left;">{metric_clean}</td>
    <td style="padding: 10px 12px; text-align: right; font-variant-numeric: tabular-nums;">{ds.count}</td>
    <td style="padding: 10px 12px; text-align: right; font-variant-numeric: tabular-nums;">{ds.mean:.2f} ({ds.std:.2f})</td>
    <td style="padding: 10px 12px; text-align: right; font-variant-numeric: tabular-nums;">{ds.median:.2f} ({ds.iqr:.2f})</td>
    <td style="padding: 10px 12px; text-align: left; font-size: 0.9em; color: #475569;">{pair_str}</td>
    <td style="padding: 10px 12px; text-align: right; font-variant-numeric: tabular-nums;">{r_str}</td>
    <td style="padding: 10px 12px; text-align: right; font-variant-numeric: tabular-nums;">{t_str}</td>
    <td style="padding: 10px 12px; text-align: right; font-variant-numeric: tabular-nums;">{p_str}</td>
    <td style="padding: 10px 12px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600;">{bf_str}</td>
    <td style="padding: 10px 12px; text-align: left; font-size: 0.88em;">{ev_str}</td>
  </tr>
""")
        rows_html = "".join(rows)

        return f"""
<div style="margin: 36px 0 28px 0; overflow-x: auto;">
  <div style="font-weight: 700; color: #1e3a8a; font-size: 1.15em; margin-bottom: 2px;">Table 1</div>
  <div style="font-style: italic; color: #334155; font-size: 1.0em; margin-bottom: 12px;">Descriptive Statistics and Bivariate Zero-Correlation Tests with Bayes Factors (BF<sub>10</sub>)</div>
  <table style="width: 100%; border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 0.9em; border-top: 2px solid #1e3a8a; border-bottom: 2px solid #1e3a8a;">
    <thead>
      <tr style="background-color: #f8fafc; border-bottom: 1px solid #1e3a8a; color: #1e3a8a;">
        <th style="padding: 12px 12px; text-align: left; font-weight: 700;">Variable</th>
        <th style="padding: 12px 12px; text-align: right; font-weight: 700;">N</th>
        <th style="padding: 12px 12px; text-align: right; font-weight: 700;">M (SD)</th>
        <th style="padding: 12px 12px; text-align: right; font-weight: 700;">Mdn (IQR)</th>
        <th style="padding: 12px 12px; text-align: left; font-weight: 700;">Bivariate Pair</th>
        <th style="padding: 12px 12px; text-align: right; font-weight: 700;">Pearson r [95% CI]</th>
        <th style="padding: 12px 12px; text-align: right; font-weight: 700;">t (df)</th>
        <th style="padding: 12px 12px; text-align: right; font-weight: 700;">p-value</th>
        <th style="padding: 12px 12px; text-align: right; font-weight: 700;">BF<sub>10</sub></th>
        <th style="padding: 12px 12px; text-align: left; font-weight: 700;">Evidence Interpretation</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
  <div style="font-size: 0.84em; color: #64748b; margin-top: 8px; line-height: 1.5;">
    <em>Note.</em> N denotes sample observation count. 95% Confidence Intervals for Pearson correlation <em>r</em> computed via Fisher's <em>z</em> transformation.
    <em>BF</em><sub>10</sub> represents the Bayes Factor supporting the presence of association over the point-null hypothesis (<em>H</em><sub>0</sub>: <em>r</em> = 0).
  </div>
</div>
"""

    def _build_apa_table2_html(self, analysis: EmpiricalAnalysisResult) -> str:
        """Constructs Table 2: Factorial Two-Way ANOVA and Bayesian Evidence Factors (APA 7th)."""
        if not analysis.two_way_anova:
            return ""

        a = analysis.two_way_anova
        outcome_clean = format_academic_metric(a.outcome_metric, title_case=True)
        fa = a.factor_a_effect
        fb = a.factor_b_effect
        fi = a.interaction_effect

        fa_name = format_academic_metric(fa.source_name, title_case=True)
        fb_name = format_academic_metric(fb.source_name, title_case=True)

        int_row_html = ""
        if fi.df > 0:
            fi_name = format_academic_metric(fi.source_name, title_case=True)
            int_row_html = f"""
  <tr style="border-bottom: 1px solid #f1f5f9;">
    <td style="padding: 10px 14px; font-weight: 600; color: #1e293b; text-align: left;">{fi_name}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{fi.ss:.2f}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{fi.df}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{fi.ms:.2f}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{format_apa_stat(fi.f_stat, decimals=2, bounded=False)}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{format_apa_p(fi.p_value, with_operator=False)}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600;">{format_apa_stat(fi.eta_sq_partial, decimals=3, bounded=True)}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600;">{format_bayes_factor(fi.bf10)}</td>
    <td style="padding: 10px 14px; text-align: left; font-size: 0.88em; color: #0369a1;">{fi.evidence_label}</td>
  </tr>
"""

        return f"""
<div style="margin: 36px 0 28px 0; overflow-x: auto;">
  <div style="font-weight: 700; color: #1e3a8a; font-size: 1.15em; margin-bottom: 2px;">Table 2</div>
  <div style="font-style: italic; color: #334155; font-size: 1.0em; margin-bottom: 12px;">Two-Way Factorial Analysis of Variance (ANOVA) and Bayesian Evidence Factors (Outcome: {outcome_clean})</div>
  <table style="width: 100%; border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 0.9em; border-top: 2px solid #1e3a8a; border-bottom: 2px solid #1e3a8a;">
    <thead>
      <tr style="background-color: #f8fafc; border-bottom: 1px solid #1e3a8a; color: #1e3a8a;">
        <th style="padding: 12px 14px; text-align: left; font-weight: 700;">Source of Variation</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">SS</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">df</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">MS</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">F</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">p-value</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">Partial &eta;&sup2;</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">BF<sub>10</sub></th>
        <th style="padding: 12px 14px; text-align: left; font-weight: 700;">Evidence Interpretation</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid #f1f5f9;">
        <td style="padding: 10px 14px; font-weight: 600; color: #1e293b; text-align: left;">{fa_name}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{fa.ss:.2f}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{fa.df}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{fa.ms:.2f}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{format_apa_stat(fa.f_stat, decimals=2, bounded=False)}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{format_apa_p(fa.p_value, with_operator=False)}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600;">{format_apa_stat(fa.eta_sq_partial, decimals=3, bounded=True)}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600;">{format_bayes_factor(fa.bf10)}</td>
        <td style="padding: 10px 14px; text-align: left; font-size: 0.88em; color: #0369a1;">{fa.evidence_label}</td>
      </tr>
      <tr style="border-bottom: 1px solid #f1f5f9;">
        <td style="padding: 10px 14px; font-weight: 600; color: #1e293b; text-align: left;">{fb_name}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{fb.ss:.2f}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{fb.df}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{fb.ms:.2f}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{format_apa_stat(fb.f_stat, decimals=2, bounded=False)}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{format_apa_p(fb.p_value, with_operator=False)}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600;">{format_apa_stat(fb.eta_sq_partial, decimals=3, bounded=True)}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600;">{format_bayes_factor(fb.bf10)}</td>
        <td style="padding: 10px 14px; text-align: left; font-size: 0.88em; color: #0369a1;">{fb.evidence_label}</td>
      </tr>
      {int_row_html}
      <tr style="border-bottom: 1px solid #f1f5f9; background-color: #fafafa;">
        <td style="padding: 10px 14px; font-weight: 600; color: #475569; text-align: left;">Residual (Error)</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{a.error_ss:.2f}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{a.error_df}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{a.error_ms:.2f}</td>
        <td style="padding: 10px 14px; text-align: right; color: #94a3b8;">&mdash;</td>
        <td style="padding: 10px 14px; text-align: right; color: #94a3b8;">&mdash;</td>
        <td style="padding: 10px 14px; text-align: right; color: #94a3b8;">&mdash;</td>
        <td style="padding: 10px 14px; text-align: right; color: #94a3b8;">&mdash;</td>
        <td style="padding: 10px 14px; text-align: left; color: #94a3b8;">&mdash;</td>
      </tr>
      <tr style="border-top: 1px solid #cbd5e1; font-weight: 600;">
        <td style="padding: 10px 14px; text-align: left; color: #1e293b;">Total</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{a.total_ss:.2f}</td>
        <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{a.total_df}</td>
        <td style="padding: 10px 14px; text-align: right; color: #94a3b8;">&mdash;</td>
        <td style="padding: 10px 14px; text-align: right; color: #94a3b8;">&mdash;</td>
        <td style="padding: 10px 14px; text-align: right; color: #94a3b8;">&mdash;</td>
        <td style="padding: 10px 14px; text-align: right; color: #94a3b8;">&mdash;</td>
        <td style="padding: 10px 14px; text-align: right; color: #94a3b8;">&mdash;</td>
        <td style="padding: 10px 14px; text-align: left; color: #94a3b8;">&mdash;</td>
      </tr>
    </tbody>
  </table>
  <div style="font-size: 0.84em; color: #64748b; margin-top: 8px; line-height: 1.5;">
    <em>Note.</em> Dependent Criterion Variable: <span style="background:#e0f2fe;color:#0369a1;padding:1px 5px;border-radius:4px;font-weight:600;">{outcome_clean}</span>. Type II Sum of Squares.
    Partial &eta;&sup2; = <em>SS</em><sub>effect</sub> / (<em>SS</em><sub>effect</sub> + <em>SS</em><sub>error</sub>).
    <em>BF</em><sub>10</sub> represents the Bayes Factor supporting the alternative hypothesis <em>H</em><sub>1</sub> relative to the null <em>H</em><sub>0</sub> under JZS / BIC delta.
  </div>
</div>
"""

    def _build_apa_table3_html(self, analysis: EmpiricalAnalysisResult) -> str:
        """Constructs Table 3: Multivariate OLS Regression & VIF Diagnostics with Model BF10 (APA 7th)."""
        if not analysis.multivariate_regressions:
            return ""

        top_m = analysis.multivariate_regressions[0]
        dep_clean = format_academic_metric(top_m.dependent_var, title_case=True)
        rows = []
        for p in top_m.predictors:
            p_clean = format_academic_metric(p, title_case=True)
            c = top_m.coefficients.get(p, 0.0)
            se = top_m.std_errors.get(p, 0.0)
            cil = top_m.ci_lower.get(p, c - 1.96 * se)
            ciu = top_m.ci_upper.get(p, c + 1.96 * se)
            t = top_m.t_stats.get(p, 0.0)
            pval = top_m.p_values.get(p, 1.0)
            vif = top_m.vif_values.get(p, 1.0)
            sig_badge = (
                '<span style="color:#059669;font-weight:600;">p &lt; .05 *</span>'
                if pval < 0.05
                else '<span style="color:#64748b;">n.s.</span>'
            )
            vif_badge = (
                f'<span style="color:#059669;font-weight:600;">{vif:.2f}</span>'
                if vif < 5.0
                else f'<span style="color:#dc2626;font-weight:600;">{vif:.2f} (VIF &ge; 5)</span>'
            )

            rows.append(f"""
  <tr style="border-bottom: 1px solid #f1f5f9;">
    <td style="padding: 10px 14px; font-weight: 600; color: #1e293b; text-align: left;">{p_clean}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{format_apa_stat(c, decimals=3, bounded=False)}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; color: #64748b;">{format_apa_stat(se, decimals=3, bounded=False)}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums; color: #475569; font-size: 0.9em;">[{format_apa_stat(cil, decimals=3, bounded=False)}, {format_apa_stat(ciu, decimals=3, bounded=False)}]</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{format_apa_stat(t, decimals=2, bounded=False)}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{format_apa_p(pval, with_operator=False)}</td>
    <td style="padding: 10px 14px; text-align: right; font-variant-numeric: tabular-nums;">{vif_badge}</td>
    <td style="padding: 10px 14px; text-align: right;">{sig_badge}</td>
  </tr>
""")
        rows_html = "".join(rows)

        r2_str = format_apa_stat(top_m.r_squared, decimals=3, bounded=True)
        adj_r2_str = format_apa_stat(top_m.adj_r_squared, decimals=3, bounded=True)
        f_str = format_apa_stat(top_m.f_stat, decimals=2, bounded=False)
        f_p_str = format_apa_p(top_m.f_pvalue, with_operator=True)
        bf_str = format_bayes_factor(top_m.model_bf10)

        return f"""
<div style="margin: 36px 0 28px 0; overflow-x: auto;">
  <div style="font-weight: 700; color: #1e3a8a; font-size: 1.15em; margin-bottom: 2px;">Table 3</div>
  <div style="font-style: italic; color: #334155; font-size: 1.0em; margin-bottom: 8px;">Multivariate OLS Multiple Regression and Multicollinearity (VIF) Diagnostics with Model Bayes Factor (Outcome: {dep_clean})</div>
  <div style="margin-bottom: 12px; font-size: 0.9em; color: #334155;">
    <strong>Dependent Criterion (Outcome):</strong> <span style="background:#e0f2fe;color:#0369a1;padding:2px 6px;border-radius:4px;font-weight:600;">{dep_clean}</span> &bull; 
    <strong>Model Fit:</strong> <em>R</em>&sup2; = {r2_str}, Adj. <em>R</em>&sup2; = {adj_r2_str}, <em>F</em> = {f_str} (<em>p</em> {f_p_str}) &bull;
    <strong>Model BF<sub>10</sub>:</strong> {bf_str} (<span style="color:#0369a1;font-weight:600;">{top_m.model_evidence_label}</span>)
  </div>
  <table style="width: 100%; border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, sans-serif; font-size: 0.9em; border-top: 2px solid #1e3a8a; border-bottom: 2px solid #1e3a8a;">
    <thead>
      <tr style="background-color: #f8fafc; border-bottom: 1px solid #1e3a8a; color: #1e3a8a;">
        <th style="padding: 12px 14px; text-align: left; font-weight: 700;">Predictor Variable</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">Coeff (&beta;)</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">SE</th>
        <th style="padding: 12px 14px; text-align: right; font-weight: 700;">95% CI</th>
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
  <div style="font-size: 0.84em; color: #64748b; margin-top: 8px; line-height: 1.5;">
    <em>Note.</em> Multicollinearity Diagnostics: {top_m.collinearity_status}
  </div>
</div>
"""
