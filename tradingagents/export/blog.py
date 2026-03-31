"""Blog post generator."""

from pathlib import Path

from .gemini_client import generate_structured
from .prompts import BLOG_PROMPT
from .schemas import BlogContent


def generate_blog(report_text: str, output_dir: Path, model: str = "gemini-2.0-flash") -> Path:
    """Generate a blog post from a trading analysis report.

    Args:
        report_text: The complete trading analysis report markdown.
        output_dir: Directory to save the blog post.
        model: Gemini model to use.

    Returns:
        Path to the generated blog post markdown file.
    """
    content: BlogContent = generate_structured(
        report_text=report_text,
        prompt=BLOG_PROMPT,
        response_schema=BlogContent,
        model=model,
    )

    # Build markdown document
    lines = [
        f"# {content['title']}",
        f"*{content['subtitle']}*",
        "",
        f"> {content['meta_description']}",
        "",
        content["body_markdown"],
        "",
        "---",
        f"**Tags:** {', '.join(content['tags'])}",
    ]
    markdown = "\n".join(lines)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "blog_post.md"
    output_path.write_text(markdown)

    return output_path
