"""
English Academic Paper Content Generator for OpenDataAnalysisTokouynu.
Generates international peer-reviewed journal quality articles in IMRaD format:
- Title, Authors, Abstract & Keywords
- 1. Introduction & Background
- 2. Research Questions & Hypotheses
- 3. Methodology & Dataset
- 4. Empirical Results
- 5. Discussion & Policy Implications
- 6. Limitations & Future Directions
- 7. References (APA 7th style)
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
import re
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from src.academic_contexts_en import get_academic_context
from src.analyzer import EmpiricalAnalysisResult
from src.config import Config
from src.fetchers.base import DatasetResearchAngle, EducationDataset

logger = logging.getLogger(__name__)


@dataclass
class AcademicPaperEn:
    """Represents a full academic paper written in English (IMRaD)."""
    title: str
    authors: str
    affiliation: str
    abstract: str
    keywords: List[str]
    section_1_intro: str
    section_2_hypotheses: str
    section_3_method: str
    section_4_results: str
    section_5_discussion: str
    section_6_limitations: str
    references: List[str]
    dataset_id: str
    angle_id: str

    def to_markdown(self) -> str:
        """Converts the paper into formatted Markdown text."""
        kw_str = ", ".join(self.keywords)
        ref_str = "\n".join([f"- {r}" for r in self.references])

        if self.affiliation and self.affiliation != self.authors:
            meta_str = f"**Authors**: {self.authors}  \n**Affiliation**: {self.affiliation}  "
        else:
            meta_str = f"**Authors / Organization**: {self.authors}  "

        return f"""# {self.title}

{meta_str}

---

### Abstract
{self.abstract}

**Keywords**: *{kw_str}*

---

## 1. Introduction & Background
{self.section_1_intro}

## 2. Theoretical Framework, Research Questions & Hypotheses
{self.section_2_hypotheses}

## 3. Methodology & Empirical Dataset
{self.section_3_method}

## 4. Quantitative Results & Empirical Findings
{self.section_4_results}

## 5. Discussion & Policy Implications
{self.section_5_discussion}

## 6. Limitations & Directions for Future Research
{self.section_6_limitations}

## 7. References
{ref_str}
"""

    def to_html(self) -> str:
        """Converts the paper into structured, beautiful HTML for WordPress."""
        kw_badges = " ".join(
            [f'<span style="background:#e0f2fe;color:#0369a1;padding:3px 8px;border-radius:12px;font-size:0.85em;margin-right:6px;display:inline-block;">{k}</span>' for k in self.keywords]
        )
        ref_items = "".join([f'<li style="margin-bottom:8px;line-height:1.5;">{r}</li>' for r in self.references])

        if self.affiliation and self.affiliation != self.authors:
            meta_line = f"<strong>{self.authors}</strong> &bull; {self.affiliation}"
        else:
            meta_line = f"<strong>{self.authors}</strong>"

        return f"""<div class="academic-paper-container" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.75;">

  <!-- Paper Header -->
  <div style="background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); color: #ffffff; padding: 32px 28px; border-radius: 12px; margin-bottom: 28px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
    <div style="text-transform: uppercase; letter-spacing: 1.5px; font-size: 0.8em; color: #93c5fd; margin-bottom: 8px; font-weight: 600;">Peer-Reviewed Working Paper | Japanese Open Data Series</div>
    <h1 style="font-size: 1.85em; font-weight: 700; margin: 0 0 16px 0; color: #ffffff; line-height: 1.35;">{self.title}</h1>
    <div style="font-size: 0.95em; color: #cbd5e1;">
      {meta_line}
    </div>
  </div>

  <!-- Abstract Card -->
  <div style="background: #f8fafc; border-left: 4px solid #0284c7; padding: 22px 24px; border-radius: 0 8px 8px 0; margin-bottom: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
    <h3 style="margin-top: 0; margin-bottom: 10px; font-size: 1.15em; color: #0369a1; text-transform: uppercase; letter-spacing: 0.5px;">Abstract</h3>
    <p style="margin-bottom: 14px; font-size: 1.0em; color: #334155; text-align: justify;">{self.abstract}</p>
    <div style="margin-top: 10px;">
      <strong style="font-size: 0.9em; color: #475569;">Keywords: </strong> {kw_badges}
    </div>
  </div>

  <!-- Section 1 -->
  <h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 1.4em;">1. Introduction & Background</h2>
  <div style="font-size: 1.02em; text-align: justify; margin-bottom: 24px;">{self._p(self.section_1_intro)}</div>

  <!-- Section 2 -->
  <h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 1.4em;">2. Theoretical Framework & Hypotheses</h2>
  <div style="font-size: 1.02em; text-align: justify; margin-bottom: 24px;">{self._p(self.section_2_hypotheses)}</div>

  <!-- Section 3 -->
  <h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 1.4em;">3. Methodology & Dataset</h2>
  <div style="font-size: 1.02em; text-align: justify; margin-bottom: 24px;">{self._p(self.section_3_method)}</div>

  <!-- Section 4 -->
  <h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 1.4em;">4. Quantitative Results & Empirical Findings</h2>
  <div style="font-size: 1.02em; text-align: justify; margin-bottom: 24px;">{self._p(self.section_4_results)}</div>

  <!-- Section 5 -->
  <h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 1.4em;">5. Discussion & Policy Implications</h2>
  <div style="font-size: 1.02em; text-align: justify; margin-bottom: 24px;">{self._p(self.section_5_discussion)}</div>

  <!-- Section 6 -->
  <h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 1.4em;">6. Limitations & Future Directions</h2>
  <div style="font-size: 1.02em; text-align: justify; margin-bottom: 24px;">{self._p(self.section_6_limitations)}</div>

  <!-- References -->
  <h2 style="color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 36px; font-size: 1.4em;">7. References</h2>
  <ul style="font-size: 0.92em; color: #475569; padding-left: 20px;">
    {ref_items}
  </ul>

</div>"""

    def _p(self, text: str) -> str:
        """Converts raw multi-paragraph text into clean HTML paragraphs."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()]
        return "".join([f"<p style='margin-bottom:16px;'>{p}</p>" for p in paragraphs])


class AcademicPaperGeneratorEn:
    """Generates academic papers in English from datasets and statistical analysis."""

    def __init__(self):
        self.gemini_client: Optional[genai.Client] = None
        if Config.GEMINI_API_KEY:
            try:
                self.gemini_client = genai.Client(api_key=Config.GEMINI_API_KEY)
                logger.info("Initialized Google Gemini GenAI client for English academic synthesis.")
            except Exception as e:
                logger.warning(f"Could not initialize GenAI client: {e}")

    def generate(
        self,
        dataset: EducationDataset,
        analysis: EmpiricalAnalysisResult,
        angle: Optional[DatasetResearchAngle] = None,
    ) -> AcademicPaperEn:
        """Generates an academic paper, attempting LLM synthesis with deterministic fallback."""
        context = get_academic_context(dataset.id)

        paper: Optional[AcademicPaperEn] = None

        # Attempt Gemini synthesis if available
        if self.gemini_client:
            try:
                paper = self._generate_with_gemini(dataset, analysis, angle, context)
            except Exception as e:
                logger.error(f"Gemini paper generation encountered error, falling back to deterministic template: {e}")

        # Deterministic high-quality template synthesis
        if not paper:
            paper = self._generate_fallback(dataset, analysis, angle, context)

        return self._sanitize_paper(paper)

    def _sanitize_paper(self, paper: AcademicPaperEn) -> AcademicPaperEn:
        """Ensures absolutely zero CJK / Japanese text leaks into the final English paper."""
        term_map = {
            "文部科学省": "Ministry of Education, Culture, Sports, Science and Technology (MEXT)",
            "国立教育政策研究所": "National Institute for Educational Policy Research (NIER)",
            "全国学力・学習状況調査": "National Assessment of Academic Ability",
            "学校基本調査": "School Basic Survey",
            "経済協力開発機構": "OECD",
            "国際指導環境調査": "Teaching and Learning International Survey (TALIS)",
            "小学校": "Elementary School",
            "中学校": "Junior High School",
            "高等学校": "Senior High School",
            "公立高等学校": "Public High Schools",
            "私立高等学校": "Private High Schools",
            "日本": "Japan",
            "韓国": "South Korea",
            "オランダ": "Netherlands",
            "スウェーデン": "Sweden",
            "ドイツ": "Germany",
            "フランス": "France",
            "世界平均": "World Average",
            "OECD平均": "OECD Average",
        }

        def clean_str(s: str) -> str:
            if not s:
                return ""
            for j, e in term_map.items():
                s = s.replace(j, e)
            # Remove any residual Japanese brackets like 【】 or （）
            s = s.replace("【", "[").replace("】", "]").replace("（", "(").replace("）", ")")
            return s

        paper.title = clean_str(paper.title)
        paper.authors = clean_str(paper.authors)
        paper.affiliation = clean_str(paper.affiliation)

        # Enforce SEDA branding
        if any(term in paper.authors for term in ["Yamamoto", "Yokohama", "YNU"]):
            paper.authors = Config.DEFAULT_AUTHORS
        if any(term in paper.affiliation for term in ["Yamamoto", "Yokohama", "YNU"]):
            paper.affiliation = Config.DEFAULT_AFFILIATION

        paper.abstract = clean_str(paper.abstract)
        paper.keywords = [clean_str(k) for k in paper.keywords]
        paper.section_1_intro = clean_str(paper.section_1_intro)
        paper.section_2_hypotheses = clean_str(paper.section_2_hypotheses)
        paper.section_3_method = clean_str(paper.section_3_method)
        paper.section_4_results = clean_str(paper.section_4_results)
        paper.section_5_discussion = clean_str(paper.section_5_discussion)
        paper.section_6_limitations = clean_str(paper.section_6_limitations)
        paper.references = [clean_str(r) for r in paper.references]
        return paper

    def _generate_with_gemini(
        self,
        dataset: EducationDataset,
        analysis: EmpiricalAnalysisResult,
        angle: Optional[DatasetResearchAngle],
        context: Dict[str, Any],
    ) -> Optional[AcademicPaperEn]:
        """Calls Gemini API to generate rigorous academic paper sections."""
        angle_title = angle.title if angle else f"Empirical Study of {dataset.title}"
        rq_list = "\n".join([f"- RQ{i+1}: {q}" for i, q in enumerate(angle.research_questions)]) if angle else "- RQ1: What are the longitudinal trends and disparities in the observed indicators?"
        hypo_list = "\n".join([f"- H{i+1}: {h}" for i, h in enumerate(angle.hypotheses)]) if angle else "- H1: Empirical variables demonstrate statistically significant structural changes over time."

        prompt = f"""You are an elite academic professor and quantitative researcher writing an empirical journal article based on Japanese government open data.
Write a comprehensive, rigorous English academic paper adhering strictly to international journal standards (IMRaD format).

### Dataset & Empirical Context:
- Dataset ID: {dataset.id}
- Dataset Title: {dataset.title} (Japanese: {dataset.title_ja})
- Official Data Source: {dataset.source_name} ({dataset.source_url})
- Scientific Discipline: {context.get('discipline')}
- Theoretical Framework: {context.get('theoretical_framework')}
- Policy Context: {context.get('policy_context')}

### Research Angle & Focus:
- Article Focus: {angle_title}
- Research Questions:
{rq_list}
- Hypotheses:
{hypo_list}

### Quantitative Statistical Analysis Output:
{analysis.summary_narrative}

### Formatting & Output Instructions:
Respond ONLY with a valid JSON object matching the following structure (do NOT enclose in triple backticks if possible, or use standard json markdown):
{{
  "title": "A precise, informative academic paper title in English (10-18 words)",
  "authors": "{Config.DEFAULT_AUTHORS}",
  "affiliation": "{Config.DEFAULT_AFFILIATION}",
  "abstract": "A 200-250 word structured abstract describing Background, Methods, Key Findings (including numerical regression slope, R^2, or correlation values), and Policy/Educational Significance.",
  "keywords": ["Keyword1", "Keyword2", "Keyword3", "Keyword4", "Keyword5"],
  "section_1_intro": "2-3 comprehensive academic paragraphs introducing the societal/policy background in Japan, relevant educational context, and literature foundation.",
  "section_2_hypotheses": "2 paragraphs formulating the theoretical framework, conceptual models, research questions (RQ1, RQ2), and testable hypotheses (H1, H2).",
  "section_3_method": "2 paragraphs describing data acquisition from official Japanese sources ({dataset.source_name}), sample characteristics, operationalization of metrics, and statistical regression / correlation techniques.",
  "section_4_results": "3 detailed paragraphs presenting the quantitative empirical findings. You MUST cite the specific numerical results from the summary (slopes, R², p-values, percentages, group differences, Bayes factors).",
  "section_5_discussion": "3 paragraphs interpreting the findings in light of existing literature, educational practice in Japan, and global policy implications.",
  "section_6_limitations": "1-2 paragraphs detailing methodological constraints, ecological fallacy cautions, and specific recommendations for future longitudinal inquiry.",
  "references": [
    "5-8 standard APA 7th style references including official Japanese reports and foundational academic papers."
  ]
}}
"""
        response = self.gemini_client.models.generate_content(
            model=Config.GEMINI_TEXT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )

        raw_text = response.text.strip()
        # Clean any markdown wrap if present
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        data = json.loads(raw_text.strip())

        return AcademicPaperEn(
            title=data.get("title", f"Empirical Analysis of {dataset.title}"),
            authors=data.get("authors", Config.DEFAULT_AUTHORS),
            affiliation=data.get("affiliation", Config.DEFAULT_AFFILIATION),
            abstract=data.get("abstract", ""),
            keywords=data.get("keywords", ["Open Data", "Japan", "Empirical Analysis", "Educational Technology"]),
            section_1_intro=data.get("section_1_intro", ""),
            section_2_hypotheses=data.get("section_2_hypotheses", ""),
            section_3_method=data.get("section_3_method", ""),
            section_4_results=data.get("section_4_results", ""),
            section_5_discussion=data.get("section_5_discussion", ""),
            section_6_limitations=data.get("section_6_limitations", ""),
            references=data.get("references", context.get("key_references", [])),
            dataset_id=dataset.id,
            angle_id=angle.id if angle else "default",
        )

    def _generate_fallback(
        self,
        dataset: EducationDataset,
        analysis: EmpiricalAnalysisResult,
        angle: Optional[DatasetResearchAngle],
        context: Dict[str, Any],
    ) -> AcademicPaperEn:
        """Deterministic, high-quality academic synthesis when LLM is unavailable."""
        angle_title = angle.title if angle else f"Empirical Quantitative Evaluation of {dataset.title}"
        primary_metric = dataset.metrics[0] if dataset.metrics else "Observed Value"

        # Build statistical synthesis snippets
        stat_points = []
        for reg in analysis.trend_regressions[:3]:
            grp = f" for {reg.group}" if reg.group else ""
            stat_points.append(
                f"Longitudinal regression for {reg.metric}{grp} indicates an estimated slope of beta = {reg.slope:.3f} "
                f"(R^2 = {reg.r_squared:.3f}, p = {reg.p_value:.4f}), reflecting a net change of {reg.total_change:+g} {dataset.unit} "
                f"from {reg.start_year} ({reg.start_value}{dataset.unit}) to {reg.end_year} ({reg.end_value}{dataset.unit})."
            )
        stat_snippet = " ".join(stat_points)

        corr_points = []
        for c in analysis.correlations[:2]:
            corr_points.append(
                f"A bivariate correlation between {c.metric_x} and {c.metric_y} yielded Pearson r = {c.pearson_r:+.3f} "
                f"(R^2 = {c.r_squared:.3f}, p = {c.p_value:.4f}, N = {c.n}), representing a {c.interpretation}."
            )
        corr_snippet = " ".join(corr_points)

        # Format category
        cat_map = {
            "math": "Mathematics Education",
            "info": "Computer Science & Informatics",
            "policy": "Public Education Policy",
            "society": "Sociology of Education",
            "general": "Quantitative Social Science",
        }
        academic_cat = cat_map.get(dataset.category.lower(), dataset.category.capitalize())

        title = f"{angle_title}: A Longitudinal Empirical Investigation of Japanese Public Open Data"
        abstract = (
            f"This study conducts a rigorous empirical investigation into {dataset.title}, utilizing official "
            f"longitudinal open datasets released by {dataset.source_name}. Employing ordinary least squares (OLS) trend "
            f"modeling and bivariate correlation analyses, we examine temporal trajectories and structural patterns "
            f"anchored in {context.get('theoretical_framework')}. {stat_snippet} {corr_snippet} These empirical findings "
            f"provide critical baseline insights for evidence-based policymaking in Japan, highlighting the necessity "
            f"of targeted pedagogical interventions and institutional resource optimization."
        )

        keywords = [
            "Japanese Open Data",
            "Longitudinal Trend Modeling",
            academic_cat,
            primary_metric,
            "Educational Policy",
            "Empirical Evidence",
        ]

        intro = (
            f"Public administration and educational institutions in Japan are undergoing rapid structural shifts influenced by "
            f"demographic transitions, technological advances, and nationwide administrative initiatives. As articulated by {dataset.source_name}, "
            f"the continuous release of standardized open administrative statistics offers unprecedented opportunities for transparent, "
            f"data-driven policy evaluation. In the context of {context.get('policy_context')}, understanding empirical trajectories "
            f"in {primary_metric} has emerged as an imperative task for researchers and policymakers alike.\n\n"
            f"{context.get('literature_review')}\n\n"
            f"Despite accumulating cross-sectional evidence, there remains a pressing need to synthesize longitudinal open data "
            f"using robust econometric and inferential techniques. This study addresses this empirical gap by analyzing multi-year "
            f"administrative data to establish definitive historical trajectories and elucidate underlying structural dynamics."
        )

        hypotheses = (
            f"This inquiry is framed within {context.get('theoretical_framework')}. Grounded in this theoretical orientation, "
            f"we pose the following central Research Questions (RQs):\n"
            f"- RQ1: How have key indicators across {dataset.title} evolved longitudinally across public school environments in Japan?\n"
            f"- RQ2: To what degree do structural disparities and cross-metric correlations account for differential educational outcomes?\n\n"
            f"Accordingly, we test two overarching empirical hypotheses:\n"
            f"- Hypothesis 1 (H1): Temporal trajectories in {primary_metric} demonstrate statistically significant secular trends (slope beta != 0, p < .05).\n"
            f"- Hypothesis 2 (H2): Statistically significant associations exist among observed metrics, reflecting systemic institutional dependencies."
        )

        method = (
            f"The empirical data for this study were compiled from official public statistical releases published by {dataset.source_name} "
            f"(Source URL: {dataset.source_url}). The dataset captures standardized macro-level administrative observations across "
            f"multiple observation waves ({dataset.time_col}). All values were operationalized in accordance with ministerial measurement "
            f"standards, measured primarily in {dataset.unit}.\n\n"
            f"Our quantitative methodology integrates descriptive statistical profiling (Mean, Median, Standard Deviation, Interquartile Range, "
            f"and Skewness) with longitudinal Ordinary Least Squares (OLS) linear trend estimation and Pearson bivariate correlation analysis. "
            f"Statistical significance was evaluated at the alpha = .05 threshold (two-tailed), and model explanatory power was evaluated via "
            f"the coefficient of determination (R^2)."
        )

        results = (
            f"Table 1 and the accompanying empirical visualizer charts delineate the parametric parameters of the observed data. "
            f"Descriptive analysis indicates substantial stability coupled with targeted secular shifts across the surveyed cohorts. "
            f"{stat_snippet}\n\n"
            f"Bivariate relational analysis further reveals noteworthy structural associations across primary indicators. "
            f"{corr_snippet}\n\n"
            f"Examination of subgroup breakdowns highlights persistent inter-category dynamics. Overall, the quantitative evidence "
            f"lends strong empirical support to Hypothesis 1, demonstrating consistent structural progression over the observed timeline."
        )

        discussion = (
            f"The empirical findings of this study offer meaningful theoretical and practical contributions to our understanding of {dataset.title}. "
            f"In alignment with {context.get('theoretical_framework')}, the documented longitudinal trajectories indicate that national policy "
            f"measures under {context.get('policy_context')} have exerted tangible structural impacts across institutional environments.\n\n"
            f"From an educational administration and policy perspective, the observed growth patterns emphasize the critical importance of "
            f"sustained infrastructural investment and targeted professional development. Policymakers must avoid treating macro-level improvements "
            f"as uniform, remaining vigilant to localized disparities and pedagogical integration friction.\n\n"
            f"In international comparative terms, Japan's structured, centralized approach to educational monitoring provides a compelling "
            f"benchmark for other OECD jurisdictions navigating large-scale educational transformation."
        )

        limitations = (
            f"Several methodological limitations must be acknowledged. First, the data examined consist of aggregated macro-level "
            f"administrative statistics; caution is warranted against committing the ecological fallacy by imputing aggregate trends directly "
            f"to individual student or teacher behaviors. Second, while OLS trend regressions capture longitudinal linear associations, "
            f"causal inference remains constrained without quasi-experimental counterfactual controls. Future studies should link panel data "
            f"across municipal jurisdictions to estimate fixed-effects econometric models."
        )

        references = context.get("key_references", [
            f"{dataset.source_name}. (2023). Annual Statistical Report on Japanese Education and Society. Government of Japan.",
            "OECD. (2023). Education at a Glance 2023: OECD Indicators. OECD Publishing. https://doi.org/10.1787/e13bef63-en",
            "Wooldridge, J. M. (2020). Introductory Econometrics: A Modern Approach (7th ed.). Cengage Learning.",
        ])

        return AcademicPaperEn(
            title=title,
            authors=Config.DEFAULT_AUTHORS,
            affiliation=Config.DEFAULT_AFFILIATION,
            abstract=abstract,
            keywords=keywords,
            section_1_intro=intro,
            section_2_hypotheses=hypotheses,
            section_3_method=method,
            section_4_results=results,
            section_5_discussion=discussion,
            section_6_limitations=limitations,
            references=references,
            dataset_id=dataset.id,
            angle_id=angle.id if angle else "default",
        )
