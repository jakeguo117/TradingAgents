"""PDF report generator using ReportLab — Sun Life brand style."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .gemini_client import generate_structured
from .prompts import PDF_PROMPT
from .schemas import PdfContent

# Sun Life brand colors
TEAL_DARK = colors.HexColor("#003946")
GOLD = colors.HexColor("#FEBE10")
BODY_COLOR = colors.HexColor("#222222")
GRAY_TEXT = colors.HexColor("#5B5E5E")
LIGHT_GRAY = colors.HexColor("#F5F5F5")


def generate_pdf(
    report_text: str, output_dir: Path, model: str = "gemini-2.5-flash"
) -> Path:
    """Generate a Sun Life-styled PDF report from a trading analysis report.

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

    # Sun Life-styled paragraph styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        spaceAfter=4,
        textColor=TEAL_DARK,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=13,
        textColor=GRAY_TEXT,
        spaceAfter=6,
        fontName="Helvetica",
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=16,
        spaceBefore=18,
        spaceAfter=8,
        textColor=TEAL_DARK,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        spaceAfter=8,
        textColor=BODY_COLOR,
        fontName="Helvetica",
    )
    summary_style = ParagraphStyle(
        "Summary",
        parent=body_style,
        fontSize=11,
        leading=16,
        leftIndent=12,
        borderLeftWidth=3,
        borderLeftColor=GOLD,
        borderPadding=8,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["BodyText"],
        fontSize=7.5,
        textColor=GRAY_TEXT,
        spaceBefore=24,
        fontName="Helvetica",
    )

    story = []

    # Gold accent bar at top
    story.append(HRFlowable(
        width="100%", thickness=4, color=GOLD,
        spaceAfter=16, spaceBefore=0,
    ))

    # Title + subtitle
    story.append(Paragraph(content["title"], title_style))
    story.append(Paragraph(content["subtitle"], subtitle_style))

    # Teal divider
    story.append(HRFlowable(
        width="30%", thickness=2, color=TEAL_DARK,
        spaceAfter=16, spaceBefore=8,
    ))

    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(content["executive_summary"], summary_style))
    story.append(Spacer(1, 12))

    # Sections
    for section in content["sections"]:
        story.append(Paragraph(section["heading"], heading_style))

        # Gold accent under section heading
        story.append(HRFlowable(
            width="15%", thickness=2, color=GOLD,
            spaceAfter=8, spaceBefore=0,
        ))

        # Clean body text for ReportLab (strip markdown)
        body = section["body"].replace("**", "").replace("*", "")
        for paragraph_text in body.split("\n\n"):
            paragraph_text = paragraph_text.strip()
            if paragraph_text:
                story.append(Paragraph(paragraph_text, body_style))

        # Add table if present
        if section.get("table_data"):
            table_data = section["table_data"]
            table = Table(table_data, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(Spacer(1, 8))
            story.append(table)

        story.append(Spacer(1, 8))

    # Bottom gold bar + disclaimer
    story.append(HRFlowable(
        width="100%", thickness=2, color=GOLD,
        spaceAfter=8, spaceBefore=16,
    ))
    story.append(Paragraph(content["disclaimer"], disclaimer_style))

    doc.build(story)
    return output_path
