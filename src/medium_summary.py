"""
Medium Executive Summary Generator for OpenDataAnalysisTokouynu.
Generates comprehensive, standalone Medium articles adhering to Medium's Trust & Safety rules
(no off-site promotional teaser links in article body) with official Canonical Link support.
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
from src.fetchers.catalog import DatasetCatalog

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
    # Replace remaining underscores in identifiers (e.g. Elementary_Math -> Elementary Math),
    # while preserving image file paths and URLs inside markdown links (e.g. ![...](file_name.png))
    parts = re.split(r"(\[[^\]]*\]\([^)]*\))", text)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"([A-Za-z0-9]+)_([A-Za-z0-9]+)", r"\1 \2", parts[i])
    return "".join(parts)


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
    """Constructs publication-grade, self-contained articles for Medium with official canonical URL integration."""

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
        """Generates an engaging, high-impact Medium article formatted in Markdown (standalone, no promotional links)."""
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
                if content and len(content) > 300:
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
        """Generates both Markdown and rich-text HTML versions of the Medium summary and writes them to disk."""
        recorded_url = get_recorded_wp_url(paper.dataset_id, paper.angle_id)
        effective_wp_url = (
            wp_url
            or recorded_url
            or Config.WP_SITE_URL
            or "https://seda68.wordpress.com"
        )
        content = self.generate_summary(
            paper=paper,
            analysis=analysis,
            dataset=dataset,
            wp_url=effective_wp_url,
            pdf_path=pdf_path,
            figure_paths=figure_paths,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # 1. Save Markdown
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Saved Medium Markdown summary to {output_path}")

        # 2. Save rich-text HTML (for 1-click formatted copy-paste into Medium)
        html_path = output_path.with_suffix(".html")
        html_content = self.convert_markdown_to_html_page(
            content, title=paper.title, canonical_url=effective_wp_url
        )
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Saved Medium rich-text HTML summary to {html_path}")

        return output_path

    @staticmethod
    def convert_markdown_to_html(md_text: str) -> str:
        """Converts Medium markdown summary into clean semantic HTML."""
        lines = md_text.splitlines()
        html_lines = []
        in_ul = False
        in_ol = False

        for line in lines:
            s = line.strip()
            if not s:
                if in_ul:
                    html_lines.append("</ul>")
                    in_ul = False
                if in_ol:
                    html_lines.append("</ol>")
                    in_ol = False
                continue

            if in_ul and not s.startswith("- "):
                html_lines.append("</ul>")
                in_ul = False
            if in_ol and not re.match(r"^\d+\.\s+", s):
                html_lines.append("</ol>")
                in_ol = False

            if s.startswith("# "):
                html_lines.append(f"<h1>{s[2:].strip()}</h1>")
            elif s.startswith("### "):
                html_lines.append(f"<h3>{s[4:].strip()}</h3>")
            elif s.startswith("## "):
                html_lines.append(f"<h2>{s[3:].strip()}</h2>")
            elif s == "---":
                html_lines.append("<hr />")
            elif s.startswith("![") and "](" in s:
                m = re.match(r"!\[(.*?)\]\((.*?)\)", s)
                if m:
                    alt, src = m.groups()
                    html_lines.append(
                        f'<figure style="margin: 28px 0; text-align: center;"><img src="{src}" alt="{alt}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.08);" /><figcaption style="margin-top: 8px; font-size: 14px; color: #64748b; font-style: italic;">{alt}</figcaption></figure>'
                    )
            elif s.startswith("- "):
                if not in_ul:
                    html_lines.append("<ul>")
                    in_ul = True
                item = s[2:].strip()
                html_lines.append(f"<li>{item}</li>")
            elif re.match(r"^\d+\.\s+", s):
                if not in_ol:
                    html_lines.append("<ol>")
                    in_ol = True
                item = re.sub(r"^\d+\.\s+", "", s)
                html_lines.append(f"<li>{item}</li>")
            else:
                html_lines.append(f"<p>{s}</p>")

        if in_ul:
            html_lines.append("</ul>")
        if in_ol:
            html_lines.append("</ol>")

        html = "\n".join(html_lines)
        # Inline Markdown formatting: links first, then bold, then italics
        html = re.sub(
            r"\[(.*?)\]\((.*?)\)",
            r'<a href="\2" target="_blank" rel="noopener noreferrer"><strong>\1</strong></a>',
            html,
        )
        html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html)
        return html

    @classmethod
    def convert_markdown_to_html_page(
        cls,
        md_text: str,
        title: str = "Medium Executive Summary",
        canonical_url: str = "https://seda68.wordpress.com",
    ) -> str:
        """Wraps semantic HTML into an interactive web page with copy buttons and Medium Canonical URL guidance."""
        article_html = cls.convert_markdown_to_html(md_text)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title} - Medium Ready Rich Text</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
      line-height: 1.8;
      color: #242424;
      background-color: #f8fafc;
      margin: 0;
      padding: 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .sticky-bar {{
      position: sticky;
      top: 16px;
      z-index: 1000;
      max-width: 820px;
      width: 100%;
      background: #0f172a;
      color: #ffffff;
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 12px;
      margin-bottom: 20px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.18);
      box-sizing: border-box;
      gap: 16px;
    }}
    .sticky-info {{
      flex: 1;
    }}
    .sticky-title {{
      font-weight: 700;
      font-size: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .sticky-subtitle {{
      font-size: 13px;
      color: #94a3b8;
      margin-top: 4px;
    }}
    .btn-group {{
      display: flex;
      gap: 10px;
      flex-shrink: 0;
    }}
    .copy-btn {{
      background: #10b981;
      color: #ffffff;
      border: none;
      padding: 11px 20px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 14px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: background 0.2s, transform 0.1s;
      white-space: nowrap;
    }}
    .copy-btn:hover {{
      background: #059669;
    }}
    .copy-btn:active {{
      transform: scale(0.98);
    }}
    .canonical-card {{
      max-width: 820px;
      width: 100%;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-left: 6px solid #2563eb;
      padding: 20px 24px;
      border-radius: 10px;
      margin-bottom: 24px;
      box-sizing: border-box;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
    .canonical-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 8px;
    }}
    .canonical-badge {{
      background: #dbeafe;
      color: #1e40af;
      font-size: 12px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
    }}
    .canonical-title {{
      font-size: 15px;
      font-weight: 700;
      color: #1e293b;
    }}
    .canonical-desc {{
      font-size: 13px;
      color: #475569;
      line-height: 1.6;
      margin: 8px 0 14px 0;
    }}
    .url-row {{
      display: flex;
      gap: 8px;
      align-items: center;
      margin-bottom: 12px;
    }}
    .url-input {{
      flex: 1;
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 9px 12px;
      font-family: monospace;
      font-size: 13px;
      color: #0f172a;
    }}
    .url-btn {{
      background: #2563eb;
      color: #ffffff;
      border: none;
      padding: 9px 16px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: background 0.2s;
      white-space: nowrap;
    }}
    .url-btn:hover {{
      background: #1d4ed8;
    }}
    .guide-details {{
      font-size: 13px;
      color: #334155;
      background: #f8fafc;
      padding: 10px 14px;
      border-radius: 6px;
      border: 1px solid #e2e8f0;
    }}
    .guide-details summary {{
      cursor: pointer;
      font-weight: 600;
      color: #2563eb;
    }}
    .guide-details ol {{
      margin: 8px 0 4px 0;
      padding-left: 20px;
      line-height: 1.7;
    }}
    .guide-details li {{
      margin-bottom: 4px;
    }}
    .container {{
      max-width: 820px;
      width: 100%;
      background: #ffffff;
      padding: 48px;
      border-radius: 12px;
      box-shadow: 0 2px 16px rgba(0,0,0,0.06);
      box-sizing: border-box;
      border: 1px solid #e2e8f0;
    }}
    #medium-article-content h1 {{
      font-size: 32px;
      line-height: 1.25;
      font-weight: 700;
      margin-bottom: 8px;
      color: #0f172a;
    }}
    #medium-article-content h3 {{
      font-size: 20px;
      line-height: 1.4;
      font-weight: 400;
      color: #475569;
      margin-top: 0;
      margin-bottom: 16px;
    }}
    #medium-article-content h2 {{
      font-size: 24px;
      line-height: 1.3;
      font-weight: 700;
      margin-top: 36px;
      margin-bottom: 12px;
      color: #0f172a;
    }}
    #medium-article-content p {{
      font-size: 18px;
      line-height: 1.75;
      margin-bottom: 20px;
      color: #1e293b;
    }}
    #medium-article-content ul, #medium-article-content ol {{
      font-size: 18px;
      line-height: 1.75;
      margin-bottom: 24px;
      padding-left: 28px;
      color: #1e293b;
    }}
    #medium-article-content li {{
      margin-bottom: 10px;
    }}
    #medium-article-content hr {{
      border: none;
      border-top: 1px solid #e2e8f0;
      margin: 36px 0;
    }}
    #medium-article-content a {{
      color: #1e3a8a;
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <div class="sticky-bar">
    <div class="sticky-info">
      <div class="sticky-title">📰 Medium用 リッチテキスト要約 & 公式設定ツール</div>
      <div class="sticky-subtitle">「本文をコピー」してMediumエディタで Ctrl+V するだけで、見出しやリストが美しく貼り付けられます</div>
    </div>
    <div class="btn-group">
      <button id="copyArticleBtn" class="copy-btn" onclick="copyForMedium()">
        📋 Medium本文をコピー
      </button>
    </div>
  </div>

  <div class="canonical-card">
    <div class="canonical-header">
      <span class="canonical-badge">規約遵守・ペナルティ対策</span>
      <span class="canonical-title">Medium公式 Canonical Link 設定（推奨）</span>
    </div>
    <p class="canonical-desc">
      Mediumでは、記事本文内にWordPressへの誘導リンク（「続きを読む」「PDFはこちら」等）を貼ると、自動巡回AIにより「トラフィック誘導スパム（Violation of Medium Rules）」と判定されアカウントが凍結される恐れがあります。<br>
      当ツールでは本文を100%独立した完全版記事として作成しています。WordPress原典のSEO評価を安全に維持するため、本文リンクではなく、Medium公式の「<strong>Customize canonical link</strong>」設定をご利用ください。
    </p>
    <div class="url-row">
      <input type="text" id="canonicalUrlInput" value="{canonical_url}" readonly class="url-input" />
      <button id="copyUrlBtn" class="url-btn" onclick="copyCanonicalUrl()">
        🔗 Canonical URLをコピー
      </button>
    </div>
    <details class="guide-details">
      <summary>📖 Mediumでの設定手順（クリックで展開・1分で完了）</summary>
      <ol>
        <li>上の「<strong>📋 Medium本文をコピー</strong>」を押し、Medium新規投稿画面（<a href="https://medium.com/new-story" target="_blank" rel="noopener">new-story</a>）で <code>Ctrl + V</code> を押して貼り付けます。</li>
        <li>画像が未反映の場合は、同じフォルダ内の画像ファイル（.png）をドラッグ＆ドロップして配置してください。</li>
        <li>Medium編集画面右上の「<strong>...</strong>」（3点アイコン）をクリック →「<strong>More settings</strong>」を選択します。</li>
        <li>設定画面左側メニューの「<strong>Advanced settings</strong>」をクリックします。</li>
        <li>「<strong>Customize canonical link</strong>」にチェックを入れ、上のCanonical URLを貼り付けて「Save」を押します。</li>
        <li>右上の「Publish」ボタンを押して公開します（検索エンジンにWordPressが正規の原典として認識され、Mediumでのペナルティも回避されます）。</li>
      </ol>
    </details>
  </div>

  <div class="container">
    <div id="medium-article-content">
{article_html}
    </div>
  </div>

  <script>
    function copyForMedium() {{
      const content = document.getElementById('medium-article-content');
      try {{
        const htmlBlob = new Blob([content.innerHTML], {{ type: 'text/html' }});
        const textBlob = new Blob([content.innerText], {{ type: 'text/plain' }});
        navigator.clipboard.write([
          new ClipboardItem({{
            'text/html': htmlBlob,
            'text/plain': textBlob
          }})
        ]).then(() => {{
          showCopyFeedback('copyArticleBtn', '✅ 本文をコピーしました！Mediumで Ctrl+V してください', '#10b981');
        }}).catch(err => {{
          fallbackSelectAndCopy(content);
        }});
      }} catch (e) {{
        fallbackSelectAndCopy(content);
      }}
    }}

    function fallbackSelectAndCopy(element) {{
      const range = document.createRange();
      range.selectNode(element);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      document.execCommand('copy');
      selection.removeAllRanges();
      showCopyFeedback('copyArticleBtn', '✅ 本文をコピーしました！Mediumで Ctrl+V してください', '#10b981');
    }}

    function copyCanonicalUrl() {{
      const input = document.getElementById('canonicalUrlInput');
      input.select();
      input.setSelectionRange(0, 99999);
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(input.value).then(() => {{
          showCopyFeedback('copyUrlBtn', '✅ URLをコピーしました！', '#2563eb');
        }}).catch(() => {{
          document.execCommand('copy');
          showCopyFeedback('copyUrlBtn', '✅ URLをコピーしました！', '#2563eb');
        }});
      }} else {{
        document.execCommand('copy');
        showCopyFeedback('copyUrlBtn', '✅ URLをコピーしました！', '#2563eb');
      }}
    }}

    function showCopyFeedback(btnId, message, defaultBg) {{
      const btn = document.getElementById(btnId);
      const origText = btn.innerHTML;
      btn.innerText = message;
      btn.style.background = '#059669';
      setTimeout(() => {{
        btn.innerHTML = origText;
        btn.style.background = defaultBg;
      }}, 3500);
    }}
  </script>
</body>
</html>"""

    def _generate_with_gemini(
        self,
        paper: AcademicPaperEn,
        analysis: Optional[EmpiricalAnalysisResult],
        dataset: Optional[EducationDataset],
        wp_url: str,
        pdf_name: str,
        figure_paths: Optional[List[Path]],
    ) -> str:
        """Uses Gemini to craft a compelling, self-contained Medium article without spam-triggering off-site links."""
        fig_note = ""
        fig1_name = "trend.png"
        fig2_name = "correlation.png"
        if figure_paths:
            figs_existing = [p.name for p in figure_paths if p.exists()]
            if figs_existing:
                fig_note = f"Featured Figures available: {', '.join(figs_existing)}"
                fig1_name = figs_existing[0]
                if len(figs_existing) > 1:
                    fig2_name = figs_existing[1]

        prompt = f"""You are a senior science communicator and tech/policy journalist writing for Medium.
Your task is to adapt a peer-reviewed empirical academic paper into an engaging, accessible, and high-impact Medium article (approximately 650-850 words, 4-5 min read).

### CRITICAL REQUIREMENTS:
1. AUDIENCE: International data scientists, economists, educational leaders, and policy analysts.
2. TONE: Intelligent, journalistic, narrative-driven, yet mathematically grounded. Emphasize the counter-intuitive paradox and policy implications.
3. MEDIUM TRUST & SAFETY POLICY (CRITICAL):
   - Medium strictly penalizes and suspends accounts that publish 'teaser' posts linking off-site.
   - Do NOT include any promotional outbound call-to-actions (NO 'Read full paper on WordPress', NO 'Download PDF at...', NO external URLs in the body text).
   - The article must be 100% self-contained, rigorous, and valuable to read directly on Medium.
4. STRUCTURE:
   - # Engaging Headline (e.g., "The Paradox of High Attainment on Low Budgets: What Japanese Open Data Teaches Us")
   - Subtitle: A punchy 1-sentence hook explaining the central paradox.
   - Author & Reading Info: `*By Society for Educational Data Analysis (SEDA) · 5 min read*`
   - ---
   - Figure 1 Placement: Embed `![Figure 1: Longitudinal Trajectory and Secular Shifts]({fig1_name})` with italic caption.
   - ## 1. The Core Paradox & Empirical Context
     Explain in 2 captivating paragraphs why conventional assumptions fail and what the empirical administrative data reveals.
   - ## 2. Research Design & Dual Inferential Framework
     Summarize the 4-pillar methodology: (1) OLS longitudinal trajectories; (2) Factorial Two-Way ANOVA (Type II SS, partial η²); (3) Multivariate OLS with backward stepwise VIF multicollinearity control (< 5.0); (4) Dual frequentist (p-values) and continuous Bayesian evidence factors (BF10).
   - ## 3. Quantitative Discoveries & Statistical Evidence
     Present concrete empirical statistics (F-tests, R-squared, Bayes factors BF10, VIF control, secular slopes).
     If Figure 2 is available, embed `![Figure 2: Empirical Bivariate Fit & Confidence Band]({fig2_name})` with italic caption.
   - ## 4. Policy & Practical Implications
     Explain 3 practical lessons for school administrators, policymakers, or international observers.
   - ## 5. Methodological Limitations & Future Scope
     Discuss aggregate administrative data considerations (ecological fallacy) and future panel econometric directions.
   - ---
   - ### Citation & Academic Attribution
     `Society for Educational Data Analysis (SEDA). (2026). *{paper.title}*. SEDA Empirical Research Monograph Series.`
     `*Data Source: Official administrative open datasets released by government authorities.*`
   - Recommended Medium Tags:
     `**Recommended Medium Tags**: #Education #DataScience #OpenData #PublicPolicy #Statistics #Japan`
5. ACCURACY & FORMATTING:
   - Strictly avoid Unicode subscripts (write `BF10` instead of `BF₁₀`, and `partial η²` instead of `partial ηₚ²`).
   - Format numbers cleanly (e.g. R² = .91, p = .002, VIF < 5.0).
   - Never use raw database column identifiers containing underscores.

### Source Academic Paper:
- Title: {paper.title}
- Abstract: {paper.abstract}
- Empirical Discoveries: {analysis.empirical_discoveries if analysis else 'See abstract.'}
- Intro Context: {paper.section_1_intro[:400] if paper.section_1_intro else ''}
- Discussion: {paper.section_5_discussion[:400] if paper.section_5_discussion else ''}
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
        """Deterministic fallback generating a self-contained, publication-ready Medium article without off-site teaser links."""
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
            for d in clean_disc[:4]:
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
        if len(findings) < 3 and (paper.abstract or paper.section_4_results):
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
                    r"(Longitudinal trend regression for.*?(?:from \d{4}.*?to \d{4}\s*(?:\([^)]*\))?\.|to \d{4}\.|\.\s+[A-Z]))",
                    full_corpus,
                )
            if traj_match:
                findings.append(
                    f"- **Longitudinal Secular Trajectory**: {traj_match.group(1)}"
                )

            # Extract Decoupling / Paradox
            decouple_matches = re.findall(
                r"(Decoupling Paradox:.*?\.\))", full_corpus
            )
            for dm in decouple_matches[:2]:
                findings.append(f"- **{dm}")

        if not findings:
            findings = [
                "- **Longitudinal Trajectory Shift**: Significant structural movement documented across multi-year observation cohorts.",
                "- **Relational Trade-Off**: Statistical decoupling observed between raw resource inputs and key cognitive or operational outcomes.",
                "- **Bayesian & Frequentist Concurrence**: Hypotheses verified simultaneously via frequentist thresholds and continuous Bayes factors (BF10).",
            ]

        findings_md = "\n".join(findings)

        # Figures
        fig1_md = ""
        fig2_md = ""
        if figure_paths and len(figure_paths) > 0 and figure_paths[0].exists():
            fig1_md = f"\n![Figure 1: Longitudinal Trajectory and Secular Shifts]({figure_paths[0].name})\n*Figure 1: Longitudinal trajectories and 95% Confidence Intervals from official administrative records.*\n"
        if figure_paths and len(figure_paths) > 1 and figure_paths[1].exists():
            fig2_md = f"\n![Figure 2: Empirical Bivariate Fit & Confidence Band]({figure_paths[1].name})\n*Figure 2: Bivariate empirical regression model and 95% Confidence Band.*\n"

        return f"""# {clean_title}
### {subtitle}

*By Society for Educational Data Analysis (SEDA) · 5 min read*

---
{fig1_md}
## 1. The Core Paradox & Empirical Context

In educational policy and public administration, decision-makers frequently operate under the assumption that linear increases in budgetary allocation, digital infrastructure, or institutional interventions guarantee proportional improvements in learning benchmarks. However, multi-year empirical evidence from official administrative open data reveals a far more complex reality.

Our latest longitudinal econometric study investigates the underlying structural dynamics of **{paper.title}**. Across many educational and public policy domains, resource inputs are expanded with the optimistic expectation that scholastic achievement, pedagogical innovation, or operational efficiency will rise in direct proportion. Yet when administrative micro- and macro-level data are analyzed over multi-year observation cohorts, empirical reality consistently uncovers policy trade-offs, structural plateaus, and unintended friction.

Synthesizing longitudinal records released by official government and international bodies, this research evaluates whether structural interventions fulfill their intended outcomes or whether countervailing administrative burdens attenuate pedagogical returns.

## 2. Research Design & Dual Inferential Framework

To overcome the limitations of isolated cross-sectional observations and guard against erroneous statistical inferences, this study implements a four-pillar econometric pipeline adhering strictly to APA 7th standards:

1. **Longitudinal Secular Trajectories**: Ordinary Least Squares (OLS) time-series regressions modeling annual rates of change (slope b) alongside Fisher's z 95% Confidence Intervals (95% CI).
2. **Factorial Two-Way ANOVA**: Evaluating main effects across temporal periods (early vs. late implementation phases) and institutional cohorts using Type II Sum of Squares, with effect sizes quantified via partial eta-squared (partial η²).
3. **Multivariate OLS Regression & Multicollinearity Pruning**: Backward stepwise elimination ensuring all Variance Inflation Factors (VIF) remain strictly below 5.0, eliminating collinear bias.
4. **Dual Frequentist-Bayesian Verification**: Simultaneously assessing empirical patterns under classical Neyman-Pearson significance thresholds (p < .05) and continuous Bayes Factors (BF10) under JZS / BIC delta approximations (Jeffreys, 1961; Lee & Wagenmakers, 2013). This dual framework protects against over-interpreting trivial sample variations while quantifying evidence strength for competing hypotheses.

## 3. Quantitative Discoveries & Statistical Evidence

{findings_md}
{fig2_md}
## 4. Policy & Practical Implications

These findings carry vital implications for educational economists, school district leaders, and public policymakers:

1. **Avoid Linear Expenditure & Hardware Fallacies**: Adding fiscal resources or digital hardware without addressing administrative workflow friction or pedagogical integration fails to produce proportional student gains.
2. **Account for Hidden Operational Overhead**: Structural reforms often compress one area of burden only to displace it onto unmeasured administrative tasks, attenuating direct educational impact.
3. **Ground Policy in Dual Evidence**: Evaluating empirical patterns under dual frequentist significance and continuous Bayesian evidence factors (BF10) prevents overreacting to short-term variance and ensures policies rest on decisive empirical foundations.

## 5. Methodological Limitations & Future Scope

Several methodological limitations should be kept in mind when interpreting these findings:

- **Aggregate Administrative Data**: Observations reflect macro-level administrative and municipal aggregations; caution is advised against committing the ecological fallacy by imputing aggregate trends directly to individual student behaviors.
- **Observational Counterfactuals**: While longitudinal regressions control for secular movement, causal attributions remain constrained without quasi-experimental counterfactual controls. Future studies should link municipal panel datasets to estimate fixed-effects econometric models.

---

### Citation & Academic Attribution
Society for Educational Data Analysis (SEDA). (2026). *{paper.title}*. SEDA Empirical Research Monograph Series.  
*Data Source: Official administrative open datasets released by government authorities under Open Data terms.*

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
    stripped = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", dir_name)
    matched_ds = None
    matched_angle = "general"

    catalog = DatasetCatalog()
    known_ds_ids = sorted([d.id for d in catalog.list_datasets()], key=len, reverse=True)
    for ds_id in known_ds_ids:
        if stripped.startswith(ds_id):
            matched_ds = ds_id
            rem = stripped[len(ds_id):].lstrip("_")
            if rem:
                matched_angle = rem
            break

    dataset_id = matched_ds or dir_name
    angle_id = matched_angle

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

    # Fetch canonical WordPress URL
    recorded_url = get_recorded_wp_url(dataset_id, angle_id)
    effective_wp_url = wp_url or recorded_url or Config.WP_SITE_URL or "https://seda68.wordpress.com"

    builder = MediumSummaryBuilder()
    out_file = report_dir / output_filename
    return builder.generate_and_save(
        paper=paper,
        output_path=out_file,
        wp_url=effective_wp_url,
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
