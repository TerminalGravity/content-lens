from pathlib import Path

import pytest

from content_lens.processors.pyannote_provider import (
    DiarizationProviderError,
    run_pyannote_diarization,
)


def test_pyannote_requires_token(tmp_path, monkeypatch):
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"fake")
    monkeypatch.delenv("HUGGINGFACE_TOKEN", raising=False)

    with pytest.raises(DiarizationProviderError, match="Hugging Face token"):
        run_pyannote_diarization(audio)


def test_pyannote_checks_audio_exists(monkeypatch):
    monkeypatch.setenv("HUGGINGFACE_TOKEN", "fake")

    with pytest.raises(DiarizationProviderError, match="does not exist"):
        run_pyannote_diarization(Path("/missing/audio.wav"))
