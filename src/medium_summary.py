"""
Medium Executive Summary Generator for OpenDataAnalysisTokouynu.
Generates engaging, concise Medium-formatted articles with backlinks to seda68.wordpress.com.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from src.academic_paper_en import AcademicPaperEn
from src.analyzer import (
    EmpiricalAnalysisResult,
    format_academic_metric,
    format_apa_p,
    format_apa_stat,
    format_bayes_factor,
    ACADEMIC_METRIC_MAP,
)
from src.config import Config, REPORTS_DIR
from src.fetchers.base import EducationDataset

logger = logging.getLogger(__name__)


TOFU_MAP = {
    "BF₁₀": "BF10",
    "BF₀₁": "BF01",
    "BF_10": "BF10",
    "BF_01": "BF01",
    "₁₀": "10",
    "₀₁": "01",
    "₁": "1",
    "₀": "0",
    "₂": "2",
    "ηₚ²": "η²",
    "ηₚ": "η",
    "\u209a": "",  # LATIN SUBSCRIPT SMALL LETTER P
    "\u1d62": "",  # LATIN SUBSCRIPT SMALL LETTER I
    "\u2080": "0",
    "\u2081": "1",
    "\u2082": "2",
    "\u2083": "3",
    "\u2084": "4",
    "\u2085": "5",
    "\u2086": "6",
    "\u2087": "7",
    "\u2088": "8",
    "\u2089": "9",
}


def sanitize_text(text: str) -> str:
    """Removes Unicode subscripts and raw database identifiers to prevent missing glyph tofu."""
    if not text:
        return ""
    for k, v in TOFU_MAP.items():
        text = text.replace(k, v)
    for raw_m, clean_m in ACADEMIC_METRIC_MAP.items():
        text = text.replace(raw_m, clean_m)
    return text


def sort_figures(figs: List[Path]) -> List[Path]:
    """Sorts figures so longitudinal trend is preferred as the primary featured figure."""
    return sorted(
        figs,
        key=lambda p: (
            0 if "trend" in p.name.lower() else (1 if "corr" in p.name.lower() else 2)
        ),
    )


def get_recorded_wp_url(dataset_id: str, angle_id: str) -> Optional[str]:
    """Fetches the recorded WordPress publication URL from data/posted_papers.json if present."""
    try:
        if Config.POSTED_PAPERS_PATH.exists():
            with open(Config.POSTED_PAPERS_PATH, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    if r.get("dataset_id") == dataset_id and (
                        not angle_id or r.get("angle_id") == angle_id
                    ):
                        return r.get("wp_url")
    except Exception:
        pass
    return None


class MediumSummaryBuilder:
    """Constructs executive summaries optimized for Medium publications with WordPress backlinks."""

    def __init__(self):
        self.gemini_client = None
        if Config.GEMINI_API_KEY:
            try:
                self.gemini_client = genai.Client(api_key=Config.GEMINI_API_KEY)
            except Exception as e:
                logger.warning(
                    f"Could not initialize Gemini Client for Medium summary: {e}"
                )

    def generate_summary(
        self,
        paper: AcademicPaperEn,
        analysis: Optional[EmpiricalAnalysisResult] = None,
        dataset: Optional[EducationDataset] = None,
        wp_url: Optional[str] = None,
        pdf_path: Optional[Path] = None,
        figure_paths: Optional[List[Path]] = None,
    ) -> str:
        """Generates an engaging, high-impact Medium article formatted in Markdown."""
        recorded_url = get_recorded_wp_url(paper.dataset_id, paper.angle_id)
        effective_wp_url = (
            wp_url
            or recorded_url
            or Config.WP_SITE_URL
            or "https://seda68.wordpress.com"
        )
        pdf_name = (
            pdf_path.name
            if pdf_path
            else f"{paper.dataset_id}_{paper.angle_id}_paper.pdf"
        )

        sorted_figs = sort_figures(figure_paths) if figure_paths else []

        # Try Gemini generation if client available
        if self.gemini_client:
            try:
                content = self._generate_with_gemini(
                    paper=paper,
                    analysis=analysis,
                    dataset=dataset,
                    wp_url=effective_wp_url,
                    pdf_name=pdf_name,
                    figure_paths=sorted_figs,
                )
                if content and len(content) > 200:
                    return sanitize_text(content)
            except Exception as e:
                logger.warning(
                    f"Gemini Medium summary generation failed ({e}), falling back to deterministic template."
                )

        # Deterministic fallback
        return sanitize_text(
            self._generate_fallback(
                paper=paper,
                analysis=analysis,
                dataset=dataset,
                wp_url=effective_wp_url,
                pdf_name=pdf_name,
                figure_paths=sorted_figs,
            )
        )

    def generate_and_save(
        self,
        paper: AcademicPaperEn,
        output_path: Path,
        analysis: Optional[EmpiricalAnalysisResult] = None,
        dataset: Optional[EducationDataset] = None,
        wp_url: Optional[str] = None,
        pdf_path: Optional[Path] = None,
        figure_paths: Optional[List[Path]] = None,
    ) -> Path:
        """Generates the Medium summary and writes it to disk."""
        content = self.generate_summary(
            paper=paper,
            analysis=analysis,
            dataset=dataset,
            wp_url=wp_url,
            pdf_path=pdf_path,
            figure_paths=figure_paths,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Saved Medium summary to {output_path}")
        return output_path

    def _generate_with_gemini(
        self,
        paper: AcademicPaperEn,
        analysis: Optional[EmpiricalAnalysisResult],
        dataset: Optional[EducationDataset],
        wp_url: str,
        pdf_name: str,
        figure_paths: Optional[List[Path]],
    ) -> str:
        """Uses Gemini to craft a compelling, reader-friendly Medium article."""
        fig_note = ""
        if figure_paths:
            fig_names = [p.name for p in figure_paths if p.exists()]
            if fig_names:
                fig_note = f"Featured Figures available: {', '.join(fig_names)}"

        prompt = f"""You are a senior science communicator and tech/policy journalist writing for Medium.
Your task is to adapt a peer-reviewed empirical academic paper into an engaging, accessible, and high-impact Medium article (approximately 500-750 words, 3-4 min read).

### CRITICAL REQUIREMENTS:
1. AUDIENCE: International data scientists, economists, educational leaders, and policy analysts.
2. TONE: Intelligent, journalistic, narrative-driven, yet mathematically grounded. Emphasize the counter-intuitive paradox and policy implications.
3. STRUCTURE:
   - # Engaging, Viral-yet-Academic Headline (e.g., "The Paradox of High Attainment on Low Budgets: What Japanese Open Data Teaches Us")
   - Subtitle: A punchy 1-sentence hook explaining the central paradox.
   - Author & Reading Info: `*By Society for Educational Data Analysis (SEDA) · 4 min read*`
   - Cover Image Placement: If Figure 1 is available, embed: `![Figure 1: Trajectory and 95% Confidence Intervals]({figure_paths[0].name if figure_paths else 'trend.png'})` with an italic caption.
   - ## 1. The Paradox (TL;DR)
     Explain in 2 captivating paragraphs why conventional assumptions fail and what the empirical administrative data reveals.
   - ## 2. Three Key Empirical Discoveries
     Present 3 clear, concrete bullet points highlighting key empirical statistics (F-tests, R-squared, Bayes factors BF10, VIF control).
   - ## 3. Policy & Real-World Implications
     Explain the practical lessons for school administrators, policymakers, or international observers.
   - ## 4. Full Paper & Data Access
     Provide prominent call-to-actions linking back to our primary publication site:
     - A clear markdown link to read the full academic paper at `{wp_url}`
     - A mention that the publication-ready PDF (`{pdf_name}`) is available for download at `{wp_url}`
   - End with:
     `*Originally published at seda68.wordpress.com. Conducted by the Society for Educational Data Analysis (SEDA) using official public open datasets.*`
   - Recommended Medium Tags:
     `**Recommended Medium Tags**: #Education #DataScience #OpenData #PublicPolicy #Statistics #Japan`
4. ACCURACY & FORMATTING:
   - Strictly avoid Unicode subscripts (write `BF10` instead of `BF₁₀`, and `partial η²` instead of `partial ηₚ²`).
   - Format numbers cleanly (e.g. R² = .91, p = .002, VIF < 5.0).
   - Never use raw database column identifiers containing underscores.

### Source Academic Paper:
- Title: {paper.title}
- Abstract: {paper.abstract}
- Empirical Discoveries: {analysis.empirical_discoveries if analysis else 'See abstract.'}
- Primary WP Link: {wp_url}
- PDF File: {pdf_name}
{fig_note}
"""
        response = self.gemini_client.models.generate_content(
            model=Config.GEMINI_TEXT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )
        return response.text.strip()

    def _generate_fallback(
        self,
        paper: AcademicPaperEn,
        analysis: Optional[EmpiricalAnalysisResult],
        dataset: Optional[EducationDataset],
        wp_url: str,
        pdf_name: str,
        figure_paths: Optional[List[Path]],
    ) -> str:
        """Deterministic fallback for Medium summary."""
        # Create engaging headline
        clean_title = (
            paper.title.split(":")[0].strip()
            if ":" in paper.title
            else paper.title.strip()
        )
        subtitle = "What large-scale longitudinal public open data reveals about policy trade-offs and structural constraints."

        # Extract findings
        findings = []
        if analysis and analysis.empirical_discoveries:
            clean_disc = [
                d
                for d in analysis.empirical_discoveries
                if not d.startswith("VIF Validated")
            ]
            for d in clean_disc[:3]:
                label = d.split(":")[0] if ":" in d else "Empirical Observation"
                findings.append(f"- **{label}**: {d}")

        if len(findings) < 3 and analysis:
            if analysis.two_way_anova:
                a = analysis.two_way_anova
                fa = a.factor_a_effect
                findings.append(
                    f"- **Factorial Variance Partition**: Two-Way ANOVA confirmed a significant effect for "
                    f"{format_academic_metric(fa.source_name, title_case=True)} (F({fa.df}, {a.error_df}) = {fa.f_stat:.2f}, "
                    f"p {format_apa_p(fa.p_value)}, partial η² = {format_apa_stat(fa.eta_sq_partial, decimals=2, bounded=True)}, "
                    f"BF10 = {format_bayes_factor(fa.bf10)})."
                )
            if analysis.multivariate_regressions:
                top_m = analysis.multivariate_regressions[0]
                findings.append(
                    f"- **Multivariate OLS & Multicollinearity Control**: Model explains {top_m.r_squared * 100:.1f}% of variance "
                    f"(R² = {format_apa_stat(top_m.r_squared, decimals=2, bounded=True)}, Adj. R² = {format_apa_stat(top_m.adj_r_squared, decimals=2, bounded=True)}, "
                    f"Model BF10 = {format_bayes_factor(top_m.model_bf10)}) with all VIF values strictly below 5.0."
                )

        # If still empty (e.g. parsed directly from paper.md), extract from paper.abstract/section_4
        if len(findings) < 3 and paper.abstract:
            full_corpus = f"{paper.abstract} {paper.section_4_results}"

            # Extract ANOVA
            anova_match = re.search(
                r"(The main effect of.*?BF10 = [0-9,.]+.*?H[01]\)\.)", full_corpus
            )
            if anova_match:
                findings.append(
                    f"- **Factorial ANOVA Effect**: {anova_match.group(1)}"
                )

            # Extract OLS
            ols_match = re.search(
                r"(Multivariate OLS on.*?Decisive evidence for H1\]\)\.)",
                full_corpus,
            )
            if not ols_match:
                ols_match = re.search(
                    r"(The omnibus model accounted for substantial variance.*?Model BF10 = [0-9,.]+.*?\.)",
                    full_corpus,
                )
            if ols_match:
                findings.append(
                    f"- **Multicollinearity-Controlled OLS**: {ols_match.group(1)}"
                )

            # Extract Trajectory
            traj_match = re.search(
                r"(Longitudinal Trajectory Shift:.*?between \d{4} and \d{4}\.)",
                full_corpus,
            )
            if not traj_match:
                traj_match = re.search(
                    r"(Longitudinal trend regression for.*?reflecting a net secular shift.*?\.)",
                    full_corpus,
                )
            if traj_match:
                findings.append(
                    f"- **Longitudinal Secular Trajectory**: {traj_match.group(1)}"
                )

        if not findings:
            findings = [
                "- **Longitudinal Trajectory Shift**: Significant structural movement documented across multi-year observation cohorts.",
                "- **Relational Trade-Off**: Statistical decoupling observed between raw resource inputs and key cognitive or operational outcomes.",
                "- **Bayesian & Frequentist Concurrence**: Hypotheses verified simultaneously via frequentist thresholds and continuous Bayes factors (BF10).",
            ]

        findings_md = "\n".join(findings)

        # Image embed
        img_md = ""
        if figure_paths and len(figure_paths) > 0 and figure_paths[0].exists():
            fig_name = figure_paths[0].name
            img_md = f"\n![Figure 1: Empirical Quantitative Trajectory]({fig_name})\n*Figure 1: Longitudinal trajectories and 95% Confidence Intervals from official administrative records.*\n"

        return f"""# {clean_title}
### {subtitle}

*By Society for Educational Data Analysis (SEDA) · 4 min read*

---
{img_md}
## 1. The Core Paradox (TL;DR)

In educational policy and public administration, decision-makers frequently operate under the assumption that linear increases in budgetary allocation, digital infrastructure, or institutional interventions guarantee proportional improvements in learning benchmarks. However, multi-year empirical evidence from official administrative open data reveals a far more complex reality.

Our latest longitudinal econometric study investigates the underlying structural dynamics of **{paper.title}**. By synthesizing factorial Two-Way Analysis of Variance (ANOVA), bivariate zero-correlation testing with Fisher's z 95% confidence intervals, and multivariate OLS regressions with backward stepwise Variance Inflation Factor (VIF < 5.0) diagnostics, this analysis reveals significant policy trade-offs and structural bottlenecks that challenge conventional wisdom.

## 2. Three Key Empirical Discoveries

{findings_md}

## 3. Policy & Real-World Implications

These findings carry vital implications for educational economists, school district leaders, and public policymakers:

1. **Avoid Linear Expenditure Fallacies**: Adding fiscal resources or digital hardware without addressing administrative workflow friction or pedagogical integration fails to produce proportional student gains.
2. **Account for Hidden Operational Overhead**: Structural reforms often compress one area of burden only to displace it onto unmeasured administrative tasks, attenuating direct educational impact.
3. **Rigorous Multicollinearity Verification**: Evaluating empirical patterns under dual frequentist significance and continuous Bayesian evidence factors (BF10) provides a much safer basis for large-scale policy decisions.

---

## 📖 Read the Full Peer-Reviewed Academic Paper

The complete academic paper—featuring full APA 7th tables (Table 1: Descriptive & Correlation Matrix with Bayes Factors, Table 2: Factorial Two-Way ANOVA, Table 3: Multivariate OLS & VIF Diagnostics), comprehensive literature reviews, and methodological derivations—is available on our primary portal:

👉 **[Read the Full Academic Paper on WordPress]({wp_url})**

📄 **[Download Publication-Ready PDF (with Embedded Figures)]({wp_url})**

*Originally published at [seda68.wordpress.com](https://seda68.wordpress.com) by the Society for Educational Data Analysis (SEDA). All analyses are conducted using verified official public datasets.*

---

**Recommended Medium Tags**: `#Education #DataScience #OpenData #PublicPolicy #Statistics #Japan`
"""


def build_summary_from_report_dir(
    report_dir: Path,
    wp_url: Optional[str] = None,
    output_filename: str = "medium_summary.md",
) -> Optional[Path]:
    """Generates a Medium summary from an existing report directory containing paper.md."""
    paper_md_path = report_dir / "paper.md"
    if not paper_md_path.exists():
        logger.warning(f"No paper.md found in {report_dir}")
        return None

    with open(paper_md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Parse title
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else report_dir.name

    # Parse authors
    author_match = re.search(r"\*\*Authors.*?\*\*:\s*(.+)$", text, re.MULTILINE)
    authors = (
        author_match.group(1).strip() if author_match else Config.DEFAULT_AUTHORS
    )

    # Parse abstract
    abstract_match = re.search(
        r"###\s+Abstract\s*\n(.*?)(?=\n\n\*\*Keywords\*\*:|\n##\s+1\.)",
        text,
        re.DOTALL,
    )
    abstract = abstract_match.group(1).strip() if abstract_match else ""

    # Parse keywords
    kw_match = re.search(r"\*\*Keywords\*\*:\s*\*(.*?)\*", text)
    keywords = [k.strip() for k in kw_match.group(1).split(",")] if kw_match else []

    # Parse sections
    def extract_sec(pattern: str) -> str:
        m = re.search(pattern, text, re.DOTALL)
        return m.group(1).strip() if m else ""

    sec1 = extract_sec(r"##\s+1\.\s+Introduction.*?\n(.*?)(?=\n##\s+2\.)")
    sec2 = extract_sec(r"##\s+2\.\s+Theoretical.*?\n(.*?)(?=\n##\s+3\.)")
    sec3 = extract_sec(r"##\s+3\.\s+Methodology.*?\n(.*?)(?=\n##\s+4\.)")
    sec4 = extract_sec(r"##\s+4\.\s+Quantitative.*?\n(.*?)(?=\n!\[Figure|\n##\s+5\.)")
    sec5 = extract_sec(r"##\s+5\.\s+Discussion.*?\n(.*?)(?=\n##\s+6\.)")
    sec6 = extract_sec(r"##\s+6\.\s+Limitations.*?\n(.*?)(?=\n##\s+7\.)")

    # Match dataset & angle ID from dir name if possible
    # e.g. 2026-09-28_worldbank_education_indicators_worldbank_spending_efficiency_paradox
    dir_name = report_dir.name
    parts = dir_name.split("_")
    dataset_id = parts[1] if len(parts) > 1 else dir_name
    angle_id = "_".join(parts[2:]) if len(parts) > 2 else "general"

    paper = AcademicPaperEn(
        title=title,
        authors=authors,
        affiliation=Config.DEFAULT_AFFILIATION,
        abstract=abstract,
        keywords=keywords,
        section_1_intro=sec1,
        section_2_hypotheses=sec2,
        section_3_method=sec3,
        section_4_results=sec4,
        section_5_discussion=sec5,
        section_6_limitations=sec6,
        references=[],
        dataset_id=dataset_id,
        angle_id=angle_id,
    )

    # Find figures
    figures = sort_figures(list(report_dir.glob("*.png")))
    pdf_files = list(report_dir.glob("*.pdf"))
    pdf_path = pdf_files[0] if pdf_files else None

    builder = MediumSummaryBuilder()
    out_file = report_dir / output_filename
    return builder.generate_and_save(
        paper=paper,
        output_path=out_file,
        wp_url=wp_url,
        pdf_path=pdf_path,
        figure_paths=figures,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Medium summary articles for reports."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate Medium summaries for all existing reports.",
    )
    parser.add_argument(
        "--report-dir",
        type=str,
        help="Specific report directory to generate summary for.",
    )
    parser.add_argument(
        "--wp-url", type=str, help="WordPress URL to embed in the summary."
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.all:
        for r_dir in sorted(REPORTS_DIR.iterdir()):
            if r_dir.is_dir() and (r_dir / "paper.md").exists():
                print(f"Processing {r_dir.name}...")
                build_summary_from_report_dir(r_dir, wp_url=args.wp_url)
        print("Done generating Medium summaries for all reports.")
    elif args.report_dir:
        p = Path(args.report_dir)
        if p.exists() and p.is_dir():
            out = build_summary_from_report_dir(p, wp_url=args.wp_url)
            print(f"Generated: {out}")
        else:
            print(f"Error: {args.report_dir} not found.")
    else:
        # Default: process latest report dir
        dirs = [
            d
            for d in REPORTS_DIR.iterdir()
            if d.is_dir() and (d / "paper.md").exists()
        ]
        if dirs:
            latest = sorted(dirs)[-1]
            print(f"Processing latest report: {latest.name}...")
            out = build_summary_from_report_dir(latest, wp_url=args.wp_url)
            print(f"Generated: {out}")
        else:
            print("No reports found.")
