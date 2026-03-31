"""NotebookLM Enterprise API client for audio overview generation.

Requires:
- NotebookLM Enterprise license ($9/user/month)
- gcloud CLI authenticated: `gcloud auth print-access-token`
- Google Cloud project with NotebookLM API enabled

If not configured, the audio exporter falls back to Gemini TTS.
"""

import json
import os
import subprocess
import time
from pathlib import Path

import requests


_BASE_URL = "https://notebooklm.googleapis.com/v1alpha"


def _get_access_token() -> str:
    """Get OAuth token via gcloud CLI."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError(
            "gcloud auth failed. Run 'gcloud auth login' first. "
            "NotebookLM Enterprise API requires Google Cloud authentication."
        ) from e


def _headers() -> dict:
    """Build authorization headers."""
    return {
        "Authorization": f"Bearer {_get_access_token()}",
        "Content-Type": "application/json",
    }


def _project_id() -> str:
    """Get the active Google Cloud project ID."""
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if project:
        return project
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError("No Google Cloud project configured.") from e


def create_audio_overview(
    source_path: Path,
    output_dir: Path,
    poll_interval: int = 15,
    max_wait: int = 600,
) -> Path:
    """Create a NotebookLM audio overview from a source file.

    Args:
        source_path: Path to the source file (markdown, PDF, etc.).
        output_dir: Directory to save the output.
        poll_interval: Seconds between status checks.
        max_wait: Maximum wait time in seconds.

    Returns:
        Path to the audio file (or raises if unavailable).
    """
    headers = _headers()

    # 1. Create notebook
    create_resp = requests.post(
        f"{_BASE_URL}/notebooks",
        headers=headers,
        json={"title": f"Trading Report - {source_path.stem}"},
    )
    create_resp.raise_for_status()
    notebook = create_resp.json()
    notebook_id = notebook["name"].split("/")[-1]

    # 2. Upload source
    with open(source_path, "rb") as f:
        upload_resp = requests.post(
            f"{_BASE_URL}/notebooks/{notebook_id}/sources:uploadFile",
            headers={"Authorization": headers["Authorization"]},
            files={"file": (source_path.name, f)},
        )
    upload_resp.raise_for_status()

    # 3. Trigger audio overview generation
    audio_resp = requests.post(
        f"{_BASE_URL}/notebooks/{notebook_id}/audioOverviews",
        headers=headers,
        json={},
    )
    audio_resp.raise_for_status()

    # 4. Poll for completion
    elapsed = 0
    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval

        status_resp = requests.get(
            f"{_BASE_URL}/notebooks/{notebook_id}/audioOverviews",
            headers=_headers(),  # Refresh token each poll
        )
        status_resp.raise_for_status()
        status = status_resp.json()

        if status.get("state") == "COMPLETED":
            # Audio is ready — save metadata
            output_dir.mkdir(parents=True, exist_ok=True)
            meta_path = output_dir / "notebooklm_audio_meta.json"
            meta_path.write_text(json.dumps(status, indent=2))

            # Note: Direct audio download may require Studio UI in alpha
            # Return metadata path; user can access audio via NotebookLM Studio
            return meta_path

        if status.get("state") == "FAILED":
            raise RuntimeError(
                f"NotebookLM audio generation failed: {status.get('error', 'Unknown')}"
            )

    raise TimeoutError(
        f"NotebookLM audio generation timed out after {max_wait}s. "
        f"Check notebook {notebook_id} in NotebookLM Studio."
    )
