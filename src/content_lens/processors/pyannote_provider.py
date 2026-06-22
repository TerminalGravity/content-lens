from __future__ import annotations

import os
from pathlib import Path

from content_lens.models import DiarizationSegment


class DiarizationProviderError(RuntimeError):
    """Raised when an optional diarization provider cannot run."""


def run_pyannote_diarization(
    audio_path: Path,
    *,
    hf_token: str | None = None,
    model: str = "pyannote/speaker-diarization-3.1",
) -> list[DiarizationSegment]:
    """Run pyannote.audio diarization and return canonical speaker segments.

    The import is intentionally lazy so Content Lens remains lightweight unless the
    user installs `content-lens[diarize]` and supplies a Hugging Face token accepted
    for the pyannote model.
    """
    token = hf_token or os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        raise DiarizationProviderError(
            "pyannote diarization requires a Hugging Face token. Set HUGGINGFACE_TOKEN "
            "or pass --hf-token-env pointing at an environment variable."
        )
    if not audio_path.exists():
        raise DiarizationProviderError(f"Audio file does not exist: {audio_path}")
    try:
        from pyannote.audio import Pipeline  # type: ignore[import-not-found]
    except ImportError as exc:
        raise DiarizationProviderError(
            "pyannote.audio is not installed. Install with `pip install -e '.[diarize]'`."
        ) from exc

    pipeline = Pipeline.from_pretrained(model, use_auth_token=token)
    diarization = pipeline(str(audio_path))
    segments: list[DiarizationSegment] = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append(
            DiarizationSegment(
                start=float(turn.start),
                end=float(turn.end),
                speaker=str(speaker),
            )
        )
    return segments
