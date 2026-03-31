"""PDF report generator using ReportLab."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .gemini_client import generate_structured
from .prompts import PDF_PROMPT
from .schemas import PdfContent


def generate_pdf(
    report_text: str, output_dir: Path, model: str = "gemini-2.0-flash"
) -> Path:
    """Generate a PDF report from a trading analysis report.

    Args:
        report_text: The complete trading analysis report markdown.
        output_dir: Directory to save the PDF.
        model: Gemini model to use.

    Returns:
        Path to the generated .pdf file.
    """
    content: PdfContent = generate_structured(
        report_text=report_text,
        prompt=PDF_PROMPT,
        response_schema=PdfContent,
        model=model,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "trading_report.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"),
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#555555"),
        spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=16,
        spaceBefore=16,
        spaceAfter=8,
        textColor=colors.HexColor("#1a1a2e"),
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        spaceAfter=8,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["BodyText"],
        fontSize=8,
        textColor=colors.grey,
        spaceBefore=20,
    )

    story = []

    # Title
    story.append(Paragraph(content["title"], title_style))
    story.append(Paragraph(content["subtitle"], subtitle_style))
    story.append(Spacer(1, 12))

    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(content["executive_summary"], body_style))
    story.append(Spacer(1, 12))

    # Sections
    for section in content["sections"]:
        story.append(Paragraph(section["heading"], heading_style))

        # Clean body text for ReportLab (strip markdown)
        body = section["body"].replace("**", "").replace("*", "")
        for paragraph in body.split("\n\n"):
            paragraph = paragraph.strip()
            if paragraph:
                story.append(Paragraph(paragraph, body_style))

        # Add table if present
        if section.get("table_data"):
            table_data = section["table_data"]
            table = Table(table_data, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(Spacer(1, 8))
            story.append(table)

        story.append(Spacer(1, 8))

    # Disclaimer
    story.append(Paragraph(content["disclaimer"], disclaimer_style))

    doc.build(story)
    return output_path
