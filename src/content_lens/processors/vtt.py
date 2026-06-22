from __future__ import annotations

import html
import re
from pathlib import Path

from content_lens.models import TranscriptTurn

TIMING_RE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})\s+-->\s+(?P<end>\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})"
)
TAG_RE = re.compile(r"<[^>]+>")


def parse_vtt(path: Path) -> list[TranscriptTurn]:
    lines = path.read_text(encoding="utf-8").splitlines()
    turns: list[TranscriptTurn] = []
    idx = 0
    while idx < len(lines):
        match = TIMING_RE.search(lines[idx])
        if not match:
            idx += 1
            continue
        start = parse_timestamp(match.group("start"))
        end = parse_timestamp(match.group("end"))
        idx += 1
        text_lines: list[str] = []
        while idx < len(lines) and lines[idx].strip():
            text_lines.append(clean_caption_line(lines[idx]))
            idx += 1
        text = dedupe_cumulative(" ".join(x for x in text_lines if x).strip())
        if text:
            turns.append(TranscriptTurn(start=start, end=end, text=text))
        idx += 1
    return merge_repeated_turns(turns)


def parse_timestamp(value: str) -> float:
    parts = value.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    hours, minutes, seconds = parts
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def clean_caption_line(line: str) -> str:
    line = html.unescape(line)
    line = TAG_RE.sub("", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def dedupe_cumulative(text: str) -> str:
    # YouTube auto-captions often emit cumulative lines: "hello" then "hello world".
    chunks = [chunk.strip() for chunk in re.split(r"\s{2,}| \| ", text) if chunk.strip()]
    if len(chunks) <= 1:
        return text
    result: list[str] = []
    for chunk in chunks:
        if result and chunk.startswith(result[-1]):
            result[-1] = chunk
        elif not result or chunk != result[-1]:
            result.append(chunk)
    return " ".join(result)


def merge_repeated_turns(turns: list[TranscriptTurn]) -> list[TranscriptTurn]:
    merged: list[TranscriptTurn] = []
    for turn in turns:
        if merged and merged[-1].text == turn.text:
            merged[-1].end = max(merged[-1].end, turn.end)
        else:
            merged.append(turn)
    return merged
