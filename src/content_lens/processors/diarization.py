from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from content_lens.models import DiarizationSegment, SpeakerProfile, TranscriptTurn


def load_diarization_json(path: Path) -> list[DiarizationSegment]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        DiarizationSegment(
            start=float(item["start"]),
            end=float(item["end"]),
            speaker=str(item["speaker"]),
            confidence=item.get("confidence"),
        )
        for item in raw
    ]


def align_speakers(
    turns: list[TranscriptTurn], segments: list[DiarizationSegment]
) -> list[TranscriptTurn]:
    if not segments:
        return turns
    aligned: list[TranscriptTurn] = []
    for turn in turns:
        scores: dict[str, float] = defaultdict(float)
        for segment in segments:
            overlap = max(0.0, min(turn.end, segment.end) - max(turn.start, segment.start))
            if overlap > 0:
                scores[segment.speaker] += overlap
        speaker = max(scores, key=scores.get) if scores else None
        aligned.append(
            TranscriptTurn(
                start=turn.start,
                end=turn.end,
                text=turn.text,
                speaker=speaker or turn.speaker,
                confidence=turn.confidence,
            )
        )
    return aligned


def infer_speaker_profiles(
    turns: list[TranscriptTurn], metadata_title: str = "", metadata_description: str = ""
) -> dict[str, SpeakerProfile]:
    profiles: dict[str, SpeakerProfile] = {}
    talk_time: dict[str, float] = defaultdict(float)
    for turn in turns:
        if turn.speaker:
            talk_time[turn.speaker] += max(0.0, turn.end - turn.start)
    for speaker_id, seconds in sorted(talk_time.items()):
        profiles[speaker_id] = SpeakerProfile(
            speaker_id=speaker_id,
            name=None,
            role="host/guest unknown",
            confidence=0.0,
            talk_time_seconds=round(seconds, 3),
        )
    text = f"{metadata_title}\n{metadata_description}".lower()
    if profiles and any(word in text for word in ["interview", "podcast", "with "]):
        ordered = sorted(profiles.values(), key=lambda p: p.talk_time_seconds, reverse=True)
        if ordered:
            ordered[0].role = "likely primary speaker/host or guest with most airtime"
            ordered[0].confidence = 0.25
            ordered[0].evidence.append(
                "Inferred from talk time and interview-like metadata; identity not confirmed"
            )
    return profiles
