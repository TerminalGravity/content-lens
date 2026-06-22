from __future__ import annotations

from content_lens.models import (
    SpeakerProfile,
    TopicSegment,
    TranscriptTurn,
    VideoMetadata,
    VisualObservation,
)
from content_lens.processors.topics import extract_questions


def fmt_time(seconds: float) -> str:
    seconds_i = int(seconds)
    h, rem = divmod(seconds_i, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def render_report(
    metadata: VideoMetadata,
    turns: list[TranscriptTurn],
    speakers: dict[str, SpeakerProfile],
    topics: list[TopicSegment],
    visuals: list[VisualObservation],
) -> str:
    duration_line = (
        f"- Duration: {fmt_time(metadata.duration or 0)}"
        if metadata.duration
        else "- Duration: unknown"
    )
    lines = [
        f"# {metadata.title or 'Untitled'}",
        "",
        f"- Source: {metadata.source}",
        f"- URL: {metadata.url}",
        f"- Channel: {metadata.channel or 'unknown'}",
        duration_line,
        "",
        "## Speakers",
    ]
    if speakers:
        for speaker in speakers.values():
            label = speaker.name or speaker.speaker_id
            lines.append(
                f"- **{label}** — role: {speaker.role or 'unknown'}, "
                f"talk time: {speaker.talk_time_seconds:.1f}s, "
                f"confidence: {speaker.confidence:.2f}"
            )
            for evidence in speaker.evidence:
                lines.append(f"  - evidence: {evidence}")
    else:
        lines.append("- No diarization available; transcript is speaker-agnostic.")

    lines.extend(["", "## Topic timeline"])
    if topics:
        for topic in topics:
            sp = f" ({', '.join(topic.speakers)})" if topic.speakers else ""
            lines.append(
                f"- **{fmt_time(topic.start)}–{fmt_time(topic.end)} "
                f"{topic.title}**{sp}: {topic.summary}"
            )
    else:
        lines.append("- No transcript topics available.")

    questions = extract_questions(turns)[:20]
    lines.extend(["", "## Questions / prompts detected"])
    if questions:
        for q in questions:
            speaker = f" {q.speaker}:" if q.speaker else ""
            lines.append(f"- {fmt_time(q.start)}{speaker} {q.text}")
    else:
        lines.append("- None detected by the lightweight heuristic.")

    lines.extend(["", "## Visual observations"])
    if visuals:
        for visual in visuals:
            lines.append(f"- {fmt_time(visual.time)}: {visual.description}")
    else:
        lines.append(
            "- No visual observations generated yet. "
            "Run with `--sample-frames` and a vision/OCR pass."
        )

    lines.extend(["", "## Transcript sample"])
    for turn in turns[:30]:
        speaker = f" {turn.speaker}:" if turn.speaker else ""
        lines.append(f"- {fmt_time(turn.start)}{speaker} {turn.text}")
    return "\n".join(lines) + "\n"
