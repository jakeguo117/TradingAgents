"""Audio summary generator with NotebookLM and Gemini TTS backends."""

import json
from pathlib import Path

from .gemini_client import generate_structured, generate_audio_tts
from .prompts import AUDIO_SCRIPT_PROMPT
from .schemas import AudioScript


def _format_script_for_tts(script: AudioScript) -> str:
    """Format an AudioScript into speaker-labeled text for TTS."""
    lines = []
    for entry in script["dialogue"]:
        speaker = entry["speaker"]
        text = entry["text"]
        lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


def generate_audio_gemini(
    report_text: str,
    output_dir: Path,
    model: str = "gemini-2.0-flash",
    tts_model: str = "gemini-2.5-flash-preview-tts",
) -> Path:
    """Generate audio using Gemini (script generation + TTS).

    Args:
        report_text: The complete trading analysis report markdown.
        output_dir: Directory to save the audio.
        model: Model for script generation.
        tts_model: Model for text-to-speech.

    Returns:
        Path to the generated .wav file.
    """
    # Step 1: Generate podcast script
    script: AudioScript = generate_structured(
        report_text=report_text,
        prompt=AUDIO_SCRIPT_PROMPT,
        response_schema=AudioScript,
        model=model,
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save script for reference
    script_path = output_dir / "audio_script.json"
    script_path.write_text(json.dumps(script, indent=2))

    # Step 2: Convert to TTS input
    tts_input = _format_script_for_tts(script)

    # Step 3: Generate audio
    audio_path = output_dir / "audio_summary.wav"
    return generate_audio_tts(
        script_text=tts_input,
        output_path=audio_path,
        model=tts_model,
    )


def generate_audio_notebooklm(
    report_text: str,
    output_dir: Path,
) -> Path:
    """Generate audio using NotebookLM Enterprise API.

    Requires NotebookLM Enterprise access and gcloud authentication.

    Args:
        report_text: The complete trading analysis report markdown.
        output_dir: Directory to save the audio.

    Returns:
        Path to the generated audio file.
    """
    from .notebooklm_client import create_audio_overview

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save report as a temp file for upload
    temp_report = output_dir / "_temp_report.md"
    temp_report.write_text(report_text)

    try:
        audio_path = create_audio_overview(
            source_path=temp_report,
            output_dir=output_dir,
        )
    finally:
        temp_report.unlink(missing_ok=True)

    return audio_path


def generate_audio(
    report_text: str,
    output_dir: Path,
    provider: str = "notebooklm",
    model: str = "gemini-2.0-flash",
    tts_model: str = "gemini-2.5-flash-preview-tts",
) -> Path:
    """Generate audio summary using the configured provider.

    Falls back to Gemini TTS if NotebookLM fails or isn't configured.

    Args:
        report_text: The complete trading analysis report.
        output_dir: Directory to save the audio.
        provider: "notebooklm" or "gemini_tts".
        model: Gemini model for script generation (TTS fallback).
        tts_model: Gemini TTS model (TTS fallback).

    Returns:
        Path to the generated audio file.
    """
    if provider == "notebooklm":
        try:
            return generate_audio_notebooklm(report_text, output_dir)
        except Exception as e:
            print(f"NotebookLM audio failed ({e}), falling back to Gemini TTS...")

    return generate_audio_gemini(report_text, output_dir, model, tts_model)
