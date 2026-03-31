"""Gemini API wrapper for content generation and TTS."""

import json
import os
import struct
import wave
from pathlib import Path
from typing import Any, Optional

from google import genai
from google.genai import types


def _get_client() -> genai.Client:
    """Create a Gemini API client using the Google API key."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not set. Add it to your .env or environment."
        )
    return genai.Client(api_key=api_key)


def generate_structured(
    report_text: str,
    prompt: str,
    response_schema: Any,
    model: str = "gemini-2.5-flash",
) -> dict:
    """Generate structured JSON output from a report using Gemini.

    Args:
        report_text: The complete trading analysis report text.
        prompt: System prompt describing the desired output.
        response_schema: TypedDict or Pydantic schema for structured output.
        model: Gemini model to use.

    Returns:
        Parsed JSON matching the response_schema.
    """
    client = _get_client()
    full_prompt = prompt + report_text

    response = client.models.generate_content(
        model=model,
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
        ),
    )
    return json.loads(response.text)


def generate_text(
    report_text: str,
    prompt: str,
    model: str = "gemini-2.5-flash",
) -> str:
    """Generate plain text output from a report using Gemini.

    Args:
        report_text: The complete trading analysis report text.
        prompt: System prompt describing the desired output.
        model: Gemini model to use.

    Returns:
        Generated text string.
    """
    client = _get_client()
    full_prompt = prompt + report_text

    response = client.models.generate_content(
        model=model,
        contents=full_prompt,
    )
    return response.text


def generate_audio_tts(
    script_text: str,
    output_path: Path,
    model: str = "gemini-2.5-flash-preview-tts",
    speaker_a: str = "Kore",
    speaker_b: str = "Puck",
) -> Path:
    """Generate audio from a two-speaker script using Gemini TTS.

    Args:
        script_text: The podcast script text with speaker labels.
        output_path: Path to save the output .wav file.
        model: Gemini TTS model to use.
        speaker_a: Voice name for first speaker.
        speaker_b: Voice name for second speaker.

    Returns:
        Path to the generated audio file.
    """
    client = _get_client()

    response = client.models.generate_content(
        model=model,
        contents=script_text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker="Alex",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=speaker_a,
                                ),
                            ),
                        ),
                        types.SpeakerVoiceConfig(
                            speaker="Sam",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=speaker_b,
                                ),
                            ),
                        ),
                    ],
                ),
            ),
        ),
    )

    # Extract audio data from response
    audio_data = response.candidates[0].content.parts[0].inline_data.data
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write as WAV (24kHz, 16-bit, mono)
    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_data)

    return output_path
