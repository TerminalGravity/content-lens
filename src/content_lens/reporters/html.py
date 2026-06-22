from __future__ import annotations

import html

from content_lens.models import (
    SpeakerProfile,
    TopicSegment,
    TranscriptTurn,
    VideoMetadata,
    VisualObservation,
)
from content_lens.processors.artifacts import extract_action_items, extract_claims, extract_quotes


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
    title = html.escape(metadata.title or "Untitled")
    duration = fmt_time(metadata.duration or 0) if metadata.duration else "unknown"
    claims = extract_claims(turns)
    actions = extract_action_items(turns)
    quotes = extract_quotes(turns)

    css = "\n".join(
        [
            ":root { color-scheme: light dark; }",
            "body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; "
            "color: #172033; max-width: 1120px; margin: 0 auto; padding: 2rem; "
            "background: #f6f7fb; }",
            "h1, h2, h3 { color: #0f172a; }",
            "a { color: #2454d6; }",
            ".panel { background: white; padding: 1.25rem; border-radius: 12px; "
            "box-shadow: 0 1px 8px rgba(15,23,42,0.08); margin-bottom: 1.25rem; }",
            ".grid { display: grid; gap: 1rem; "
            "grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }",
            ".card { background: white; padding: 1rem; border-radius: 12px; "
            "box-shadow: 0 1px 8px rgba(15,23,42,0.08); }",
            ".visual-card img { width: 100%; height: auto; border-radius: 8px; "
            "display: block; margin-bottom: 0.5rem; background: #e5e7eb; }",
            ".timestamp { font-family: ui-monospace, monospace; font-size: 0.85em; "
            "color: #64748b; font-weight: 700; }",
            ".speaker { font-weight: 700; color: #1d4ed8; }",
            ".transcript { background: white; padding: 1.25rem; border-radius: 12px; "
            "box-shadow: 0 1px 8px rgba(15,23,42,0.08); max-height: 700px; "
            "overflow-y: auto; }",
            ".turn { margin-bottom: 0.75rem; border-bottom: 1px solid #eef2f7; "
            "padding-bottom: 0.5rem; }",
            ".pill { display: inline-block; padding: 0.15rem 0.45rem; "
            "border-radius: 999px; background: #eef2ff; color: #3730a3; "
            "font-size: 0.8rem; margin-left: 0.25rem; }",
            "@media (prefers-color-scheme: dark) { body { background: #0f172a; "
            "color: #e2e8f0; } h1, h2, h3 { color: #f8fafc; } "
            ".panel, .card, .transcript { background: #172033; } "
            ".turn { border-color: #263248; } }",
        ]
    )

    parts = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        f"<head><meta charset='UTF-8'><title>{title}</title>",
        f"<style>{css}</style></head>",
        "<body>",
        f"<h1>{title}</h1>",
        render_metadata(metadata, duration),
        render_speakers(speakers),
        render_topics(topics),
        render_insight_list("Claims", [claim.text for claim in claims[:20]]),
        render_insight_list("Action items", [item.text for item in actions[:20]]),
        render_insight_list("Key quotes", [quote.text for quote in quotes[:20]]),
        render_visuals(visuals),
        render_transcript(turns),
        "</body></html>",
    ]
    return "\n".join(parts) + "\n"


def render_metadata(metadata: VideoMetadata, duration: str) -> str:
    url = html.escape(metadata.url)
    return (
        "<div class='panel'><h2>Metadata</h2><ul>"
        f"<li><strong>Source:</strong> {html.escape(metadata.source)}</li>"
        f"<li><strong>URL:</strong> <a href='{url}'>{url}</a></li>"
        f"<li><strong>Channel:</strong> {html.escape(metadata.channel or 'unknown')}</li>"
        f"<li><strong>Duration:</strong> {duration}</li>"
        "</ul></div>"
    )


def render_speakers(speakers: dict[str, SpeakerProfile]) -> str:
    if not speakers:
        return "<div class='panel'><h2>Speakers</h2><p>No diarization available.</p></div>"
    parts = ["<div class='panel'><h2>Speakers</h2><ul>"]
    for speaker in speakers.values():
        label = html.escape(speaker.name or speaker.speaker_id)
        role = html.escape(speaker.role or "unknown")
        parts.append(
            f"<li><strong>{label}</strong> &mdash; role: {role}, "
            f"talk time: {speaker.talk_time_seconds:.1f}s, "
            f"confidence: {speaker.confidence:.2f}</li>"
        )
    parts.append("</ul></div>")
    return "\n".join(parts)


def render_topics(topics: list[TopicSegment]) -> str:
    parts = ["<div class='panel'><h2>Topic timeline</h2><ul>"]
    if topics:
        for topic in topics:
            sp = (
                f" <span class='pill'>{html.escape(', '.join(topic.speakers))}</span>"
                if topic.speakers
                else ""
            )
            parts.append(
                f"<li><span class='timestamp'>{fmt_time(topic.start)}–{fmt_time(topic.end)}</span> "
                f"<strong>{html.escape(topic.title)}</strong>{sp}: "
                f"{html.escape(topic.summary)}</li>"
            )
    else:
        parts.append("<li>No topics available.</li>")
    parts.append("</ul></div>")
    return "\n".join(parts)


def render_insight_list(title: str, items: list[str]) -> str:
    parts = [f"<div class='panel'><h2>{html.escape(title)}</h2>"]
    if not items:
        parts.append("<p>None detected by the lightweight heuristic.</p></div>")
        return "\n".join(parts)
    parts.append("<ul>")
    for item in items:
        parts.append(f"<li>{html.escape(item)}</li>")
    parts.append("</ul></div>")
    return "\n".join(parts)


def render_visuals(visuals: list[VisualObservation]) -> str:
    parts = ["<h2>Visual observations / contact sheet</h2>"]
    if not visuals:
        parts.append("<div class='panel'><p>No visual observations generated.</p></div>")
        return "\n".join(parts)
    parts.append("<div class='grid'>")
    for visual in visuals:
        img_tag = (
            f"<img src='{html.escape(visual.asset_path)}' alt='Frame' loading='lazy'>"
            if visual.asset_path
            else ""
        )
        parts.append(
            "<div class='card visual-card'>"
            f"{img_tag}"
            f"<div><span class='timestamp'>{fmt_time(visual.time)}</span></div>"
            f"<div>{html.escape(visual.description)}</div>"
            "</div>"
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_transcript(turns: list[TranscriptTurn]) -> str:
    parts = ["<h2>Transcript</h2><div class='transcript'>"]
    if not turns:
        parts.append("<p>No transcript available.</p></div>")
        return "\n".join(parts)
    for turn in turns:
        speaker = (
            f"<span class='speaker'>{html.escape(turn.speaker)}</span>: " if turn.speaker else ""
        )
        parts.append(
            f"<div class='turn'><span class='timestamp'>{fmt_time(turn.start)}</span> "
            f"{speaker}{html.escape(turn.text)}</div>"
        )
    parts.append("</div>")
    return "\n".join(parts)
