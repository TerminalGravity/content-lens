from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class VideoMetadata:
    source: str
    url: str
    title: str = ""
    channel: str = ""
    duration: float | None = None
    description: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TranscriptTurn:
    start: float
    end: float
    text: str
    speaker: str | None = None
    confidence: float | None = None


@dataclass(slots=True)
class DiarizationSegment:
    start: float
    end: float
    speaker: str
    confidence: float | None = None


@dataclass(slots=True)
class SpeakerProfile:
    speaker_id: str
    name: str | None = None
    role: str | None = None
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
    talk_time_seconds: float = 0.0


@dataclass(slots=True)
class TopicSegment:
    start: float
    end: float
    title: str
    summary: str
    speakers: list[str] = field(default_factory=list)


@dataclass(slots=True)
class VisualObservation:
    time: float
    description: str
    asset_path: str | None = None
    confidence: float | None = None


@dataclass(slots=True)
class ExtractionResult:
    metadata: VideoMetadata
    transcript: list[TranscriptTurn] = field(default_factory=list)
    diarization: list[DiarizationSegment] = field(default_factory=list)
    visuals: list[VisualObservation] = field(default_factory=list)
    assets: dict[str, str] = field(default_factory=dict)


def dataclass_to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {k: dataclass_to_jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, list):
        return [dataclass_to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: dataclass_to_jsonable(v) for k, v in value.items()}
    if isinstance(value, Path):
        return str(value)
    return value
