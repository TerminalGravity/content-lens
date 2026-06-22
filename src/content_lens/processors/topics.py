from __future__ import annotations

from content_lens.models import TopicSegment, TranscriptTurn


def segment_topics(turns: list[TranscriptTurn], window_seconds: int = 300) -> list[TopicSegment]:
    if not turns:
        return []
    segments: list[TopicSegment] = []
    bucket: list[TranscriptTurn] = []
    bucket_start = turns[0].start
    for turn in turns:
        if bucket and turn.start - bucket_start >= window_seconds:
            segments.append(_summarize_bucket(bucket, len(segments) + 1))
            bucket = []
            bucket_start = turn.start
        bucket.append(turn)
    if bucket:
        segments.append(_summarize_bucket(bucket, len(segments) + 1))
    return segments


def _summarize_bucket(bucket: list[TranscriptTurn], index: int) -> TopicSegment:
    text = " ".join(t.text for t in bucket)
    words = text.split()
    summary = " ".join(words[:45]) + ("..." if len(words) > 45 else "")
    speakers = sorted({t.speaker for t in bucket if t.speaker})
    return TopicSegment(
        start=bucket[0].start,
        end=bucket[-1].end,
        title=f"Segment {index}",
        summary=summary,
        speakers=speakers,
    )


def extract_questions(turns: list[TranscriptTurn]) -> list[TranscriptTurn]:
    question_prefixes = ("why ", "how ", "what ", "when ", "where ")
    return [
        turn
        for turn in turns
        if "?" in turn.text or turn.text.lower().startswith(question_prefixes)
    ]
