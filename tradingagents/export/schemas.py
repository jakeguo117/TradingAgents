"""Schemas for structured Gemini outputs and export results."""

from pathlib import Path
from typing import Optional

from typing_extensions import TypedDict


class SlideContent(TypedDict):
    title: str
    bullets: list[str]
    speaker_notes: str


class SocialPosts(TypedDict):
    twitter_thread: list[str]
    linkedin_post: str
    instagram_caption: str


class BlogContent(TypedDict):
    title: str
    subtitle: str
    body_markdown: str
    meta_description: str
    tags: list[str]


class PdfSection(TypedDict):
    heading: str
    body: str
    table_data: Optional[list[list[str]]]


class PdfContent(TypedDict):
    title: str
    subtitle: str
    executive_summary: str
    sections: list[PdfSection]
    disclaimer: str


class AudioScript(TypedDict):
    title: str
    dialogue: list[dict]  # [{"speaker": "Alex", "text": "..."}, ...]


class ExportResult(TypedDict, total=False):
    blog: Path
    pptx: Path
    pdf: Path
    social: SocialPosts
    social_json: Path
    audio: Path
