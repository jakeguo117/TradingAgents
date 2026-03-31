"""Social media post generator."""

import json
from pathlib import Path

from .gemini_client import generate_structured
from .prompts import SOCIAL_PROMPT
from .schemas import SocialPosts


def generate_social(
    report_text: str, output_dir: Path, model: str = "gemini-2.0-flash"
) -> tuple[SocialPosts, Path]:
    """Generate social media posts from a trading analysis report.

    Args:
        report_text: The complete trading analysis report markdown.
        output_dir: Directory to save the posts.
        model: Gemini model to use.

    Returns:
        Tuple of (SocialPosts dict, Path to saved JSON file).
    """
    posts: SocialPosts = generate_structured(
        report_text=report_text,
        prompt=SOCIAL_PROMPT,
        response_schema=SocialPosts,
        model=model,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "social_posts.json"
    output_path.write_text(json.dumps(posts, indent=2))

    # Also write human-readable versions
    readable_path = output_dir / "social_posts.md"
    lines = [
        "# Social Media Posts",
        "",
        "## Twitter/X Thread",
    ]
    for i, tweet in enumerate(posts["twitter_thread"], 1):
        lines.append(f"{i}. {tweet}")
    lines.extend([
        "",
        "## LinkedIn Post",
        posts["linkedin_post"],
        "",
        "## Instagram Caption",
        posts["instagram_caption"],
    ])
    readable_path.write_text("\n".join(lines))

    return posts, output_path
