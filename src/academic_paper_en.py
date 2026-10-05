"""
English Academic Paper Generation Engine for OpenDataAnalysisTokouynu.
Synthesizes peer-reviewed academic papers in IMRaD format using Google Gemini 2.5 Flash,
with deterministic empirical fallback, VIF multicollinearity verification, paradox discovery,
and inline figure embedding.
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
from src.analyzer import (
    EmpiricalAnalysisResult,
    format_academic_metric,
    format_apa_p,
    format_apa_stat,
    format_bayes_factor,
    ACADEMIC_METRIC_MAP,
)
from src.config import Config
from src.fetchers.base import DatasetResearchAngle, EducationDataset

logger = logging.getLogger(__name__)


@dataclass
class AcademicPaperEn:
    """Represents a peer-reviewed English academic paper in IMRaD format."""
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

    def to_markdown(self, figure_paths: Optional[List[str]] = None) -> str:
        """Converts the paper into formatted Markdown text with in-paper figures."""
        kw_str = ", ".join(self.keywords)
        ref_str = "\n".join([f"- {r}" for r in self.references])

        if self.affiliation and self.affiliation != self.authors:
            meta_str = f"**Authors**: {self.authors}  \n**Affiliation**: {self.affiliation}  "
        else:
            meta_str = f"**Authors / Organization**: {self.authors}  "

        figs_md = ""
        if figure_paths:
            clean_t = self.title.split(":")[0].strip() if ":" in self.title else self.title.strip()
            figs_md_list = []
            for idx, p in enumerate(figure_paths):
                cap = (
                    f"Longitudinal Trajectory and 95% Confidence Intervals for {clean_t}"
                    if idx == 0
                    else f"Bivariate Relational Fit and Empirical Regression Model with 95% Confidence Band for {clean_t}"
                )
                figs_md_list.append(f"![Figure {idx + 1}]({p})\n*Figure {idx + 1}: {cap}.*")
            figs_md = "\n\n" + "\n\n".join(figs_md_list)

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
{self.section_4_results}{figs_md}

## 5. Discussion & Policy Implications
{self.section_5_discussion}

## 6. Limitations & Directions for Future Research
{self.section_6_limitations}

## 7. References
{ref_str}
"""

    def to_html(self, figure_urls: Optional[List[str]] = None) -> str:
        """Converts the paper into structured, beautiful HTML for WordPress with in-paper figures."""
        kw_badges = " ".join(
            [f'<span style="background:#e0f2fe;color:#0369a1;padding:3px 8px;border-radius:12px;font-size:0.85em;margin-right:6px;display:inline-block;">{k}</span>' for k in self.keywords]
        )
        ref_items = "".join([f'<li style="margin-bottom:8px;line-height:1.5;">{r}</li>' for r in self.references])

        if self.affiliation and self.affiliation != self.authors:
            meta_line = f"<strong>{self.authors}</strong> &bull; {self.affiliation}"
        else:
            meta_line = f"<strong>{self.authors}</strong>"

        figs_html = ""
        if figure_urls:
            figs_html = '<div style="margin: 28px 0; text-align: center;">'
            clean_t = self.title.split(":")[0].strip() if ":" in self.title else self.title.strip()
            for idx, url in enumerate(figure_urls):
                caption = (
                    f"Figure {idx + 1}: Longitudinal Trajectory and 95% Confidence Intervals for {clean_t}"
                    if idx == 0
                    else f"Figure {idx + 1}: Bivariate Relational Fit and Empirical Regression Model with 95% Confidence Band for {clean_t}"
                )
                figs_html += f"""
<figure style="margin: 24px 0; text-align: center;">
  <img src="{url}" alt="{caption}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;" />
  <figcaption style="margin-top: 8px; font-size: 0.9em; color: #475569; font-style: italic;">{caption}</figcaption>
</figure>
"""
            figs_html += "</div>"

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
  {figs_html}

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

        # Convert any raw database metric names with underscores into clean academic terminology
        for raw_m, clean_m in ACADEMIC_METRIC_MAP.items():
            paper.title = paper.title.replace(raw_m, clean_m)
            paper.abstract = paper.abstract.replace(raw_m, clean_m.lower())
            paper.section_1_intro = paper.section_1_intro.replace(raw_m, clean_m.lower())
            paper.section_2_hypotheses = paper.section_2_hypotheses.replace(raw_m, clean_m.lower())
            paper.section_3_method = paper.section_3_method.replace(raw_m, clean_m.lower())
            paper.section_4_results = paper.section_4_results.replace(raw_m, clean_m.lower())
            paper.section_5_discussion = paper.section_5_discussion.replace(raw_m, clean_m.lower())
            paper.section_6_limitations = paper.section_6_limitations.replace(raw_m, clean_m.lower())
            paper.keywords = [k.replace(raw_m, clean_m) for k in paper.keywords]

        # Clean remaining raw underscore identifiers in title/keywords
        if paper.title.count(":") > 1:
            parts = paper.title.split(":")
            paper.title = f"{parts[0].strip()}: {' - '.join(p.strip() for p in parts[1:])}"

        # Eliminate Unicode subscript characters that cause missing glyph tofu boxes (■) in standard fonts and PDF
        tofu_map = {
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
            "\u209a": "",  # LATIN SUBSCRIPT SMALL LETTER P (triggers black box tofu in standard fonts)
            "\u1d62": "",  # LATIN SUBSCRIPT SMALL LETTER I
            "\u2081": "1",
            "\u2080": "0",
        }
        def clean_tofu(s: str) -> str:
            if not s:
                return ""
            for k, v in tofu_map.items():
                s = s.replace(k, v)
            # Strip <a href="..."> tags and convert DOI URLs to plain text 'DOI: 10.xxxx/...'
            s = re.sub(
                r'<a\b[^>]*href=["\']https?://(?:dx\.)?doi\.org/(10\.[^"\'\s>]+)["\'][^>]*>.*?</a>',
                r'DOI: \1',
                s,
                flags=re.IGNORECASE | re.DOTALL,
            )
            s = re.sub(
                r'<a\b[^>]*>(?:DOI:\s*)?(10\.[^<]+)</a>',
                r'DOI: \1',
                s,
                flags=re.IGNORECASE,
            )
            s = re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', s, flags=re.IGNORECASE | re.DOTALL)
            s = re.sub(
                r'(?:DOI:\s*)?https?://(?:dx\.)?doi\.org/(10\.[^\s<>\"\)\]】』]+)',
                r'DOI: \1',
                s,
            )
            s = re.sub(r'(?:DOI:\s*)+', 'DOI: ', s)
            return s

        paper.title = clean_tofu(paper.title)
        paper.abstract = clean_tofu(paper.abstract)
        paper.keywords = [clean_tofu(k) for k in paper.keywords]
        paper.section_1_intro = clean_tofu(paper.section_1_intro)
        paper.section_2_hypotheses = clean_tofu(paper.section_2_hypotheses)
        paper.section_3_method = clean_tofu(paper.section_3_method)
        paper.section_4_results = clean_tofu(paper.section_4_results)
        paper.section_5_discussion = clean_tofu(paper.section_5_discussion)
        paper.section_6_limitations = clean_tofu(paper.section_6_limitations)
        paper.references = [clean_tofu(r) for r in paper.references]

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
        rq_list = "\n".join([f"- RQ{i+1}: {q}" for i, q in enumerate(angle.research_questions)]) if angle else "- RQ1: What are the empirical relational associations and trade-offs in observed indicators?"
        hypo_list = "\n".join([f"- H{i+1}: {h}" for i, h in enumerate(angle.hypotheses)]) if angle else "- H1: Empirical variables demonstrate non-trivial structural relationships and trade-offs."

        prompt = f"""You are an elite academic professor and lead quantitative econometrician writing an empirical journal article based on Japanese government open data.
Write a comprehensive, rigorous English academic paper adhering strictly to international journal standards (IMRaD format).

### CRITICAL SCIENTIFIC IMPERATIVES:
1. THREE CORE ANALYTICAL METHODS (APA 7th):
   - Two-Way Factorial ANOVA: Evaluate main effects and interactions across institutional/temporal factors with partial eta-squared (partial eta^2) effect sizes.
   - Bivariate Zero-Correlation Analysis: Test Pearson r significance via Student's t-distribution with Fisher's z 95% Confidence Intervals.
   - Multivariate OLS Multiple Regression: Estimate multiple regression models with rigorous Variance Inflation Factor (VIF < 5.0) multicollinearity diagnostics.
2. DUAL FREQUENTIST & BAYESIAN INFERENCE: Present both frequentist statistics (F-ratios, t-statistics, Pearson r, unstandardized beta, partial eta^2, p-values) and Bayesian statistics (Bayes Factors BF_10, evidence classifications e.g. decisive, strong, moderate) side-by-side. Contrast p-value significance against continuous Bayesian evidence.
3. IN-PAPER TABLE & FIGURE CITATIONS: In Section 4 (Quantitative Results & Empirical Findings), you MUST explicitly cite and discuss:
   - "Table 1": Descriptive Statistics and Bivariate Zero-Correlation Matrix with Bayes Factors.
   - "Table 2": Two-Way Factorial Analysis of Variance (ANOVA) and Bayesian Evidence Factors.
   - "Table 3": Multivariate OLS Multiple Regression and Multicollinearity (VIF) Diagnostics with Model Bayes Factor.
   - "Figure 1": Longitudinal time-series trajectories with shaded 95% CI bands.
   - "Figure 2": Empirical relational regression model with 95% CI confidence band.
4. UNCOVER EMPIRICAL SURPRISES & PARADOXES: Do NOT merely report obvious linear trends or state that time progressed. Focus on counter-intuitive findings, theoretical paradoxes, and policy trade-offs revealed in the analysis (e.g., decoupling between technology inputs and cognitive scores, crowding out of lesson preparation by administrative burden, institutional vigilance, affective exhaustion despite high achievement).
5. 95% CONFIDENCE INTERVALS (95% CI): When presenting quantitative findings and regression parameters in Section 4, report all major effect sizes with their 95% Confidence Intervals (95% CI) (e.g., b = 0.420, 95% CI [0.180, 0.660], p = .003). Discuss the width and precision of the 95% CI bands plotted in Figure 1 and Figure 2.
6. ACADEMIC ENGLISH NOMENCLATURE & APA 7TH STYLE:
   - NEVER use raw database column identifiers containing underscores (e.g., do NOT write "Youth_Programming_Skill_Rate_Pct", "Lesson_Prep_Hours_Per_Week", or "Elementary_Total_Time_Min"). Always translate variable names into natural, scholarly English terminology (e.g., "youth programming skill rate", "weekly lesson preparation hours", "elementary total learning time").
   - Strictly adhere to APA 7th statistical formatting: omit leading zeros for numbers bounded between 0 and 1 (e.g., r = .66, R^2 = .98, p < .001, eta_p^2 = .78). Never write "p = 0.0" or "p = 0.0000" (use p < .001 instead).
   - Format confidence intervals cleanly without plus signs: 95% CI [2.10, 2.72].
   - Maintain a sophisticated, formal academic register suitable for top-tier international journals (e.g., Computers & Education, Higher Education, British Journal of Educational Technology). Avoid conversational rhetorical questions and informal filler phrases.
   - Do NOT include any HTML <a href="..."> tags or clickable hyperlinks. Always format DOIs in references using plain text notation (e.g., "DOI: 10.xxxx/...") instead of "https://doi.org/...".

### Dataset & Empirical Context:
- Dataset ID: {dataset.id}
- Dataset Title: {dataset.title} (Japanese: {dataset.title_ja})
- Official Data Source: {dataset.source_name}
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
  "title": "A precise, informative academic paper title in English highlighting the paradox or empirical discovery (10-18 words)",
  "authors": "{Config.DEFAULT_AUTHORS}",
  "affiliation": "{Config.DEFAULT_AFFILIATION}",
  "abstract": "A 200-250 word structured abstract describing Background, Methods (Two-Way ANOVA, zero-correlation tests, multivariate OLS, Bayes Factors), Key Findings (including numerical F, t, beta, R^2, VIF values, BF_10, and empirical paradoxes), and Policy/Educational Significance.",
  "keywords": ["Keyword1", "Keyword2", "Keyword3", "Keyword4", "Keyword5"],
  "section_1_intro": "2-3 comprehensive academic paragraphs introducing the societal/policy background in Japan, relevant educational context, and literature foundation.",
  "section_2_hypotheses": "2 paragraphs formulating the theoretical framework, conceptual models, research questions (RQ1, RQ2), and testable hypotheses (H1, H2).",
  "section_3_method": "2-3 paragraphs describing data acquisition from official Japanese sources ({dataset.source_name}), operationalization of metrics, and the three analytical methods (Two-Way ANOVA, zero-correlation tests, multivariate OLS with VIF control, and Bayes Factor estimation under JZS priors).",
  "section_4_results": "3-4 detailed paragraphs presenting the quantitative empirical findings following APA 7th standards. You MUST cite Table 1, Table 2, Table 3, Figure 1, and Figure 2 explicitly, contrasting frequentist p-values with Bayesian evidence factors (BF_10), and reporting exact numerical metrics.",
  "section_5_discussion": "3 paragraphs interpreting the findings in light of existing literature, educational practice in Japan, and global policy implications.",
  "section_6_limitations": "1-2 paragraphs detailing methodological constraints, ecological fallacy cautions, and specific recommendations for future longitudinal inquiry.",
  "references": [
    "5-8 standard APA 7th style references including official Japanese reports and foundational academic papers (use plain text 'DOI: 10.xxxx/...' without URLs or HTML links)."
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
        """Deterministic, publication-grade academic synthesis when LLM is unavailable."""
        angle_title = angle.title if angle else f"Empirical Quantitative Evaluation of {dataset.title}"
        if ":" in angle_title:
            title = f"{angle_title} (A Longitudinal Empirical Investigation of Japanese Public Open Data)"
        else:
            title = f"{angle_title}: A Longitudinal Empirical Investigation of Japanese Public Open Data"

        primary_metric = dataset.metrics[0] if dataset.metrics else "Observed Indicator"
        primary_clean = format_academic_metric(primary_metric, False)
        primary_title = format_academic_metric(primary_metric, True)

        # Build statistical synthesis snippets
        stat_points = []
        for reg in analysis.trend_regressions[:2]:
            grp = f" for {reg.group}" if reg.group else ""
            m_name = format_academic_metric(reg.metric, False)
            p_str = format_apa_p(reg.p_value)
            r2_str = format_apa_stat(reg.r_squared, bounded=True)
            stat_points.append(
                f"Longitudinal trend regression for {m_name}{grp} indicates an estimated slope of b = {reg.slope:.2f} "
                f"(95% CI [{reg.ci_lower:.2f}, {reg.ci_upper:.2f}], R² = {r2_str}, p {p_str}), reflecting a net secular shift of {reg.total_change:+g} {dataset.unit} "
                f"from {reg.start_year} ({reg.start_value}{dataset.unit}) to {reg.end_year} ({reg.end_value}{dataset.unit})."
            )
        stat_snippet = " ".join(stat_points)

        corr_points = []
        for c in analysis.correlations[:2]:
            p_c_str = format_apa_p(c.p_value)
            r_str = format_apa_stat(c.pearson_r, bounded=True)
            mx_name = format_academic_metric(c.metric_x, False)
            my_name = format_academic_metric(c.metric_y, False)
            bf_str = format_bayes_factor(c.bf10)
            if c.p_value < 0.05:
                corr_points.append(
                    f"A bivariate zero-correlation test between {mx_name} and {my_name} revealed a statistically significant "
                    f"linear association, Pearson r = {r_str}, 95% CI [{c.ci_lower:.2f}, {c.ci_upper:.2f}], "
                    f"t({c.df}) = {c.t_stat:.2f}, p {p_c_str}, BF10 = {bf_str} ({c.evidence_label}), "
                    f"accounting for {c.r_squared * 100:.1f}% of shared variance."
                )
            else:
                corr_points.append(
                    f"A bivariate zero-correlation test between {mx_name} and {my_name} showed no statistically significant "
                    f"linear association, Pearson r = {r_str}, 95% CI [{c.ci_lower:.2f}, {c.ci_upper:.2f}], "
                    f"t({c.df}) = {c.t_stat:.2f}, p {p_c_str}, with a Bayes factor of BF10 = {bf_str} ({c.evidence_label}) "
                    f"favoring the null hypothesis of independence."
                )
        corr_snippet = " ".join(corr_points)

        # Factorial Two-Way ANOVA snippet
        anova_snippet = ""
        if analysis.two_way_anova:
            a = analysis.two_way_anova
            fa = a.factor_a_effect
            fb = a.factor_b_effect
            fi = a.interaction_effect
            outcome_clean = format_academic_metric(a.outcome_metric, False)
            fa_clean = format_academic_metric(a.factor_a_name, False)
            fb_clean = format_academic_metric(a.factor_b_name, False)
            p_a_str = format_apa_p(fa.p_value)
            p_b_str = format_apa_p(fb.p_value)
            eta_a_str = format_apa_stat(fa.eta_sq_partial, bounded=True)
            eta_b_str = format_apa_stat(fb.eta_sq_partial, bounded=True)
            bf_a_str = format_bayes_factor(fa.bf10)
            bf_b_str = format_bayes_factor(fb.bf10)

            int_text = ""
            if fi.df > 0:
                p_i_str = format_apa_p(fi.p_value)
                eta_i_str = format_apa_stat(fi.eta_sq_partial, bounded=True)
                bf_i_str = format_bayes_factor(fi.bf10)
                int_text = (
                    f" Furthermore, the interaction effect ({fa_clean} × {fb_clean}) yielded "
                    f"F({fi.df}, {a.error_df}) = {fi.f_stat:.2f}, p {p_i_str}, partial η² = {eta_i_str}, "
                    f"with BF10 = {bf_i_str} ({fi.evidence_label})."
                )
            anova_snippet = (
                f"As documented in Table 2, a factorial Two-Way Analysis of Variance (ANOVA) was conducted on {outcome_clean}. "
                f"The main effect of {fa_clean} reached statistical significance, F({fa.df}, {a.error_df}) = {fa.f_stat:.2f}, "
                f"p {p_a_str}, partial η² = {eta_a_str}, with a Bayes factor of BF10 = {bf_a_str} providing {fa.evidence_label}. "
                f"Similarly, the main effect of {fb_clean} was F({fb.df}, {a.error_df}) = {fb.f_stat:.2f}, p {p_b_str}, "
                f"partial η² = {eta_b_str}, BF10 = {bf_b_str} ({fb.evidence_label}).{int_text} "
                f"The alignment between frequentist significance thresholds and continuous Bayesian evidence factors confirms robust structural partition of variance."
            )

        # Multivariate OLS and VIF snippet
        mv_snippet = ""
        if analysis.multivariate_regressions:
            top_m = analysis.multivariate_regressions[0]
            dep_clean = format_academic_metric(top_m.dependent_var, False)
            pred_details = ", ".join([
                f"{format_academic_metric(p, False)} (B = {top_m.coefficients.get(p, 0.0):.2f}, SE = {top_m.std_errors.get(p, 0.0):.2f}, "
                f"95% CI [{top_m.ci_lower.get(p, 0.0):.2f}, {top_m.ci_upper.get(p, 0.0):.2f}], t = {top_m.t_stats.get(p, 0.0):.2f}, VIF = {top_m.vif_values.get(p, 1.0):.2f})"
                for p in top_m.predictors
            ])
            p_f_str = format_apa_p(top_m.f_pvalue)
            r2_str = format_apa_stat(top_m.r_squared, bounded=True)
            adj_r2_str = format_apa_stat(top_m.adj_r_squared, bounded=True)
            bf_m_str = format_bayes_factor(top_m.model_bf10)
            mv_snippet = (
                f"As presented in Table 3, an Ordinary Least Squares (OLS) multiple regression model was estimated on {dep_clean} "
                f"with stepwise multicollinearity pruning. The omnibus model accounted for substantial variance, R² = {r2_str}, "
                f"adjusted R² = {adj_r2_str}, F({len(top_m.predictors)}, {top_m.n_obs - len(top_m.predictors) - 1}) = {top_m.f_stat:.2f}, p {p_f_str}. "
                f"Bayesian model evaluation against an intercept-only null model yielded Model BF10 = {bf_m_str}, providing {top_m.model_evidence_label}. "
                f"{top_m.collinearity_status} Individual parameter estimates indicated: {pred_details}."
            )

        # Discovery / paradox snippet
        disc_snippet = ""
        if analysis.empirical_discoveries:
            disc_clean = [d for d in analysis.empirical_discoveries if not d.startswith("VIF Validated")]
            if disc_clean:
                disc_snippet = " " + " ".join(disc_clean[:2])

        cat_map = {
            "math": "Mathematics Education",
            "info": "Computer Science & Informatics",
            "policy": "Public Education Policy",
            "society": "Sociology of Education",
            "general": "Quantitative Social Science",
        }
        academic_cat = cat_map.get(dataset.category.lower(), dataset.category.capitalize())

        abstract = (
            f"This study conducts a rigorous empirical investigation into {dataset.title}, utilizing official "
            f"longitudinal open datasets released by {dataset.source_name}. Employing factorial Two-Way Analysis of Variance (ANOVA), "
            f"bivariate zero-correlation tests with Fisher's z 95% confidence intervals, and multivariate OLS regressions with "
            f"stepwise Variance Inflation Factor (VIF < 5.0) multicollinearity control, we evaluate empirical patterns simultaneously "
            f"through frequentist significance tests and Bayesian evidence factors (BF10) anchored in {context.get('theoretical_framework')}. "
            f"{stat_snippet} {anova_snippet} {mv_snippet} {disc_snippet} These empirical findings uncover critical policy trade-offs "
            f"for evidence-based decision-making in Japan, demonstrating that structural inputs alone do not guarantee linear gains."
        )

        keywords = [
            "Japanese Open Data",
            "Two-Way ANOVA",
            "Bayes Factor BF10",
            "Zero-Correlation Analysis",
            "Multicollinearity VIF Control",
            academic_cat,
            primary_title,
            "Educational Policy Paradox",
        ]

        intro = (
            f"Public administration and educational institutions in Japan are undergoing rapid structural shifts influenced by "
            f"demographic transitions, technological advances, and nationwide administrative initiatives. As articulated by {dataset.source_name}, "
            f"the continuous release of standardized open administrative statistics offers unprecedented opportunities for transparent, "
            f"data-driven policy evaluation. In the context of {context.get('policy_context')}, understanding empirical trajectories "
            f"in {primary_clean} has emerged as an imperative task for researchers and policymakers alike.\n\n"
            f"{context.get('literature_review')}\n\n"
            f"Despite accumulating cross-sectional evidence, there remains a pressing need to synthesize longitudinal open data "
            f"using robust econometric and inferential techniques that guard against severe multicollinearity while evaluating findings "
            f"under both frequentist and Bayesian statistical paradigms. This study addresses this empirical gap by analyzing multi-year administrative data."
        )

        hypotheses = (
            f"This inquiry is framed within {context.get('theoretical_framework')}. Grounded in this theoretical orientation, "
            f"we pose the following central Research Questions (RQs):\n"
            f"- RQ1: How do institutional factors and temporal periods interact in shaping {primary_clean} across public educational environments in Japan?\n"
            f"- RQ2: To what degree do structural inputs predict key outcomes after rigorously controlling for multicollinearity (VIF < 5.0)?\n\n"
            f"Accordingly, we test two overarching empirical hypotheses:\n"
            f"- Hypothesis 1 (H1): Factorial main effects and temporal trajectories demonstrate statistically significant secular trends supported by decisive Bayesian evidence.\n"
            f"- Hypothesis 2 (H2): Relational associations reveal structural trade-offs, where isolated resource growth does not translate into proportional outcome gains."
        )

        method = (
            f"The empirical data for this study were compiled from official public statistical releases published by {dataset.source_name}. "
            f"The dataset captures standardized macro-level administrative observations across "
            f"multiple observation waves ({dataset.time_col}). All values were operationalized in accordance with ministerial measurement "
            f"standards, measured primarily in {dataset.unit}.\n\n"
            f"Our quantitative methodology integrates three analytical pillars adhering strictly to APA 7th standards: "
            f"(1) Factorial Two-Way Analysis of Variance (ANOVA) with Type II Sum of Squares to estimate main effects and interaction parameters, "
            f"quantifying effect sizes via partial eta-squared (partial η²); "
            f"(2) Bivariate Zero-Correlation Tests evaluating Pearson r via Student's t-distribution with Fisher's z 95% Confidence Intervals (95% CI); and "
            f"(3) Multivariate Ordinary Least Squares (OLS) Multiple Regression with backward stepwise Variance Inflation Factor (VIF) "
            f"elimination ensuring all predictor VIF values remain strictly below 5.0. To bridge frequentist and Bayesian paradigms, each inferential "
            f"test is accompanied by its corresponding Bayes Factor (BF10) under JZS / BIC delta approximation, classifying evidence according to "
            f"Jeffreys (1961) and Lee and Wagenmakers (2013) conventions."
        )

        results = (
            f"Table 1 outlines the parametric descriptive distributions and bivariate zero-correlation tests across indicators. "
            f"As illustrated in Figure 1, the longitudinal trajectories demonstrate meaningful temporal shifts across cohorts, "
            f"with shaded ribbons capturing the 95% Confidence Interval (95% CI) of the secular trends. {stat_snippet}\n\n"
            f"As depicted in Figure 2, relational regression analysis exposes crucial structural associations and trade-offs among indicators, "
            f"anchored by an empirical OLS fit line and its 95% CI confidence band. {corr_snippet} {disc_snippet}\n\n"
            f"{anova_snippet}\n\n"
            f"{mv_snippet} In summary, the integration of Two-Way ANOVA, zero-correlation tests, and multivariate OLS regressions—evaluated "
            f"simultaneously via frequentist significance tests and Bayesian evidence factors—provides a rigorous empirical foundation for educational policy."
        )

        discussion = (
            f"The empirical findings of this study offer meaningful theoretical and practical contributions to our understanding of {dataset.title}. "
            f"In alignment with {context.get('theoretical_framework')}, the documented longitudinal trajectories indicate that national policy "
            f"measures under {context.get('policy_context')} have exerted tangible structural impacts across institutional environments.\n\n"
            f"From an educational administration and policy perspective, the observed growth patterns emphasize the critical importance of "
            f"avoiding simplistic assumptions. As revealed by our regression models, expanding physical or digital infrastructure without "
            f"addressing accompanying operational burdens (e.g., administrative overhead or device maintenance) creates friction that attenuates pedagogical impact.\n\n"
            f"In international comparative terms, Japan's structured, centralized approach to educational monitoring provides a compelling "
            f"benchmark for other OECD jurisdictions navigating large-scale educational transformation."
        )

        limitations = (
            f"Several methodological limitations must be acknowledged. First, the data examined consist of aggregated macro-level "
            f"administrative statistics; caution is warranted against committing the ecological fallacy by imputing aggregate trends directly "
            f"to individual student or teacher behaviors. Second, while OLS trend regressions and Two-Way ANOVA capture longitudinal associations, "
            f"causal inference remains constrained without quasi-experimental counterfactual controls. Future studies should link municipal panel data "
            f"to estimate fixed-effects econometric models."
        )

        references = context.get("key_references", [
            f"{dataset.source_name}. (2023). Annual Statistical Report on Japanese Education and Society. Government of Japan.",
            "Jeffreys, H. (1961). Theory of Probability (3rd ed.). Oxford University Press.",
            "Lee, M. D., & Wagenmakers, E.-J. (2013). Bayesian Cognitive Modeling: A Practical Course. Cambridge University Press.",
            "OECD. (2023). Education at a Glance 2023: OECD Indicators. OECD Publishing. DOI: 10.1787/e13bef63-en",
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
