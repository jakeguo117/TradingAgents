"""PowerPoint presentation generator."""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt

from .gemini_client import generate_structured
from .prompts import PPTX_PROMPT
from .schemas import SlideContent


def generate_pptx(
    report_text: str, output_dir: Path, model: str = "gemini-2.0-flash"
) -> Path:
    """Generate a PowerPoint deck from a trading analysis report.

    Args:
        report_text: The complete trading analysis report markdown.
        output_dir: Directory to save the presentation.
        model: Gemini model to use.

    Returns:
        Path to the generated .pptx file.
    """
    slides_data: list[SlideContent] = generate_structured(
        report_text=report_text,
        prompt=PPTX_PROMPT,
        response_schema=list[SlideContent],
        model=model,
    )

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    for i, slide_data in enumerate(slides_data):
        if i == 0:
            layout = prs.slide_layouts[0]  # Title slide
        else:
            layout = prs.slide_layouts[1]  # Title + content

        slide = prs.slides.add_slide(layout)

        # Set title
        if slide.shapes.title:
            slide.shapes.title.text = slide_data["title"]
            for paragraph in slide.shapes.title.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(28) if i == 0 else Pt(24)

        # Set bullet content
        if len(slide.placeholders) > 1:
            body = slide.placeholders[1]
            tf = body.text_frame
            tf.clear()

            for j, bullet in enumerate(slide_data["bullets"]):
                if j == 0:
                    tf.paragraphs[0].text = bullet
                else:
                    p = tf.add_paragraph()
                    p.text = bullet
                for paragraph in tf.paragraphs:
                    paragraph.font.size = Pt(18)

        # Add speaker notes
        notes_slide = slide.notes_slide
        notes_slide.notes_text_frame.text = slide_data.get("speaker_notes", "")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "trading_report.pptx"
    prs.save(str(output_path))

    return output_path
