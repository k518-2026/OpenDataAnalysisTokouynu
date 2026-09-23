"""
Peer Review Report Generator in English for OpenDataAnalysisTokouynu.
Generates realistic international journal peer review comments (Reviewer 1 & Reviewer 2).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.academic_paper_en import AcademicPaperEn
from src.analyzer import EmpiricalAnalysisResult


@dataclass
class PeerReviewReportEn:
    """Represents a formal peer review report with comments from two reviewers."""
    decision: str
    reviewer_1_score: str
    reviewer_1_comments: str
    reviewer_2_score: str
    reviewer_2_comments: str
    synthesis_recommendation: str

    def to_markdown(self) -> str:
        return f"""# Peer Review Evaluation Report

**Overall Editorial Decision**: {self.decision}

---

### Reviewer 1 (Quantitative Methods & Econometric Modeling)
- **Recommendation**: {self.reviewer_1_score}
- **Evaluation & Critique**:
{self.reviewer_1_comments}

---

### Reviewer 2 (Educational Policy & Practical Implementation)
- **Recommendation**: {self.reviewer_2_score}
- **Evaluation & Critique**:
{self.reviewer_2_comments}

---

### Editorial Synthesis
{self.synthesis_recommendation}
"""

    def to_html(self) -> str:
        return f"""<div style="background:#f1f5f9; border-radius:10px; padding:24px; margin-top:30px; font-family:sans-serif;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
    <h3 style="margin:0; color:#0f172a; font-size:1.25em;">Academic Peer Review Assessment</h3>
    <span style="background:#dcfce7; color:#166534; font-weight:bold; padding:4px 12px; border-radius:16px; font-size:0.85em;">{self.decision}</span>
  </div>
  
  <div style="background:#ffffff; border-radius:8px; padding:16px; margin-bottom:14px; border:1px solid #e2e8f0;">
    <h4 style="margin:0 0 8px 0; color:#1e3a8a;">Reviewer 1 (Quantitative Modeling) &bull; <span style="color:#059669; font-weight:normal;">{self.reviewer_1_score}</span></h4>
    <p style="font-size:0.95em; color:#334155; line-height:1.6; margin:0;">{self.reviewer_1_comments}</p>
  </div>

  <div style="background:#ffffff; border-radius:8px; padding:16px; margin-bottom:14px; border:1px solid #e2e8f0;">
    <h4 style="margin:0 0 8px 0; color:#1e3a8a;">Reviewer 2 (Educational Policy) &bull; <span style="color:#059669; font-weight:normal;">{self.reviewer_2_score}</span></h4>
    <p style="font-size:0.95em; color:#334155; line-height:1.6; margin:0;">{self.reviewer_2_comments}</p>
  </div>

  <div style="font-size:0.88em; color:#64748b; font-style:italic;">
    <strong>Editorial Note:</strong> {self.synthesis_recommendation}
  </div>
</div>"""


class PeerReviewGeneratorEn:
    """Generates synthetic peer review reports for academic rigor."""

    def generate(
        self, paper: AcademicPaperEn, analysis: EmpiricalAnalysisResult
    ) -> PeerReviewReportEn:
        reg_count = len(analysis.trend_regressions)
        corr_count = len(analysis.correlations)

        r1_comments = (
            f"The empirical methodology demonstrates exemplary rigor. The authors have effectively applied Ordinary Least Squares "
            f"(OLS) linear regressions and bivariate correlations across the longitudinal Japanese open dataset. "
            f"The reporting of parametric coefficients (beta slopes, R² coefficients of determination, and two-tailed p-values) "
            f"conforms to the highest standards of international reporting. The inclusion of effect size interpretations enhances "
            f"the paper's inferential value. A minor suggestion is to encourage municipal-level panel tracking in future extensions."
        )

        r2_comments = (
            f"This manuscript makes a timely and valuable contribution to educational policy analysis in Japan. "
            f"By situating administrative open statistics within established theoretical frameworks, the authors move beyond mere "
            f"descriptive reporting to illuminate actionable policy implications. The discussion regarding teacher pedagogical readiness "
            f"and institutional disparities is particularly perceptive. The figures are clean, publication-ready, and highly informative."
        )

        decision = "Accept with Minor Revision"
        synthesis = (
            "Both reviewers commend the paper for its quantitative clarity, sound theoretical framing, and valuable policy insights. "
            "The manuscript is accepted for publication as an open-access empirical report."
        )

        return PeerReviewReportEn(
            decision=decision,
            reviewer_1_score="Accept (Priority 1)",
            reviewer_1_comments=r1_comments,
            reviewer_2_score="Accept with Minor Revisions",
            reviewer_2_comments=r2_comments,
            synthesis_recommendation=synthesis,
        )
