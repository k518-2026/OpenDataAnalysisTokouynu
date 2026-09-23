"""
English Academic Paper PDF Generator using ReportLab.
Produces styled multi-page PDF documents for empirical working papers with embedded figures.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from src.academic_paper_en import AcademicPaperEn
from src.config import PDF_REPORTS_DIR

logger = logging.getLogger(__name__)


class AcademicPaperPdfGeneratorEn:
    """Generates PDF versions of English academic papers with in-paper figures."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or PDF_REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self, paper: AcademicPaperEn, figure_paths: Optional[List[Path]] = None
    ) -> Optional[Path]:
        """Creates a styled PDF document from the academic paper with embedded figures."""
        pdf_filename = f"{paper.dataset_id}_{paper.angle_id}_paper.pdf"
        output_path = self.output_dir / pdf_filename

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                HRFlowable,
                Image,
            )

            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=54,
                leftMargin=54,
                topMargin=54,
                bottomMargin=54,
            )

            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                "PaperTitle",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=18,
                leading=22,
                textColor=colors.HexColor("#1e3a8a"),
                spaceAfter=12,
            )
            meta_style = ParagraphStyle(
                "PaperMeta",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#475569"),
                spaceAfter=14,
            )
            abstract_heading = ParagraphStyle(
                "AbstractHead",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=16,
                textColor=colors.HexColor("#0369a1"),
                spaceAfter=6,
            )
            abstract_body = ParagraphStyle(
                "AbstractBody",
                parent=styles["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#334155"),
                spaceAfter=14,
            )
            h2_style = ParagraphStyle(
                "H2Style",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=13,
                leading=17,
                textColor=colors.HexColor("#1e3a8a"),
                spaceBefore=14,
                spaceAfter=8,
            )
            body_style = ParagraphStyle(
                "BodyTextCustom",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#1e293b"),
                spaceAfter=10,
            )
            caption_style = ParagraphStyle(
                "FigCaption",
                parent=styles["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=8.5,
                leading=12,
                textColor=colors.HexColor("#64748b"),
                alignment=1,  # Center
                spaceAfter=12,
            )

            story = []

            # Title & Meta
            story.append(Paragraph(paper.title, title_style))
            if paper.affiliation and paper.affiliation != paper.authors:
                story.append(Paragraph(f"<b>Authors:</b> {paper.authors} &bull; <i>{paper.affiliation}</i>", meta_style))
            else:
                story.append(Paragraph(f"<b>Authors / Organization:</b> {paper.authors}", meta_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=14))

            # Abstract
            story.append(Paragraph("Abstract", abstract_heading))
            story.append(Paragraph(paper.abstract, abstract_body))
            story.append(Paragraph(f"<b>Keywords:</b> {', '.join(paper.keywords)}", meta_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=14))

            # Sections
            sections = [
                ("1. Introduction & Background", paper.section_1_intro),
                ("2. Theoretical Framework & Hypotheses", paper.section_2_hypotheses),
                ("3. Methodology & Empirical Dataset", paper.section_3_method),
                ("4. Quantitative Results & Empirical Findings", paper.section_4_results),
                ("5. Discussion & Policy Implications", paper.section_5_discussion),
                ("6. Limitations & Future Directions", paper.section_6_limitations),
            ]

            for heading, content in sections:
                story.append(Paragraph(heading, h2_style))
                for p in content.split("\n\n"):
                    if p.strip():
                        story.append(Paragraph(p.strip(), body_style))

                # Embed Figures directly in Section 4: Quantitative Results
                if "4. Quantitative Results" in heading and figure_paths:
                    for idx, fig_path in enumerate(figure_paths):
                        if fig_path and Path(fig_path).exists():
                            try:
                                story.append(Spacer(1, 8))
                                # Width 460 pt, height 260 pt
                                story.append(Image(str(fig_path), width=460, height=260))
                                story.append(Spacer(1, 4))
                                caption = f"Figure {idx + 1}: Empirical Quantitative Trajectory & Relational Fit for {paper.dataset_id}."
                                story.append(Paragraph(caption, caption_style))
                                story.append(Spacer(1, 10))
                            except Exception as img_err:
                                logger.warning(f"Could not embed figure {fig_path} in PDF: {img_err}")

                story.append(Spacer(1, 8))

            # References
            story.append(Paragraph("7. References", h2_style))
            for ref in paper.references:
                story.append(Paragraph(f"&bull; {ref}", body_style))

            doc.build(story)
            logger.info(f"Successfully generated PDF with figures: {output_path.name}")
            return output_path

        except Exception as e:
            logger.warning(f"ReportLab PDF generation skipped or encountered error: {e}")
            return None
