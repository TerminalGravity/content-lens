from __future__ import annotations

import re
from collections import Counter

from content_lens.models import ActionItem, Claim, Quote, SpeakerProfile, TranscriptTurn

ACTION_RE = re.compile(
    r"(?i)\b("
    r"i will|we will|we should|you should|let's|need to|needs to|"
    r"have to|make sure|start by|run|install|create|build"
    r")\b[^.!?]*[.!?]?"
)
QUOTE_RE = re.compile(r'"([^"]+)"')
CLAIM_MARKERS = (
    "because ",
    "therefore ",
    "that means ",
    "the reason ",
    "i think ",
    "we think ",
    "we believe ",
    "this is ",
    "these are ",
    "will ",
    "should ",
    "must ",
    "need to ",
)
STOPWORDS = {
    "the",
    "and",
    "that",
    "this",
    "with",
    "you",
    "for",
    "are",
    "but",
    "not",
    "have",
    "was",
    "from",
    "they",
    "your",
    "just",
    "like",
    "what",
    "when",
    "how",
}


def extract_quotes(turns: list[TranscriptTurn], limit: int = 20) -> list[Quote]:
    quotes: list[Quote] = []
    for turn in turns:
        for match in QUOTE_RE.findall(turn.text):
            if len(match.split()) >= 4:
                quotes.append(
                    Quote(
                        text=normalize_text(match),
                        speaker=turn.speaker,
                        start=turn.start,
                        end=turn.end,
                    )
                )
        if len(quotes) >= limit:
            break
    if quotes:
        return quotes[:limit]

    # Fallback: select substantial high-signal turns as quote candidates.
    scored = sorted(
        (
            (quote_score(turn), turn)
            for turn in turns
            if len(turn.text.split()) >= 8 and not is_music_or_noise(turn.text)
        ),
        key=lambda item: (-item[0], item[1].start),
    )
    return [
        Quote(text=normalize_text(turn.text), speaker=turn.speaker, start=turn.start, end=turn.end)
        for _, turn in scored[:limit]
    ]


def extract_claims(turns: list[TranscriptTurn], limit: int = 30) -> list[Claim]:
    claims: list[Claim] = []
    for turn in turns:
        text = normalize_text(turn.text)
        lowered = text.lower()
        if len(text.split()) < 5 or is_music_or_noise(text):
            continue
        if any(marker in lowered for marker in CLAIM_MARKERS):
            claims.append(
                Claim(
                    text=text,
                    speaker=turn.speaker,
                    start=turn.start,
                    end=turn.end,
                    confidence=0.35,
                )
            )
        if len(claims) >= limit:
            break
    return claims


def extract_action_items(turns: list[TranscriptTurn], limit: int = 30) -> list[ActionItem]:
    action_items: list[ActionItem] = []
    for turn in turns:
        for match in ACTION_RE.finditer(turn.text):
            text = normalize_text(match.group(0))
            if text:
                action_items.append(
                    ActionItem(text=text, owner=turn.speaker, start=turn.start, end=turn.end)
                )
        if len(action_items) >= limit:
            break
    return action_items[:limit]


def calculate_speaker_stats(turns: list[TranscriptTurn]) -> dict[str, SpeakerProfile]:
    speakers: dict[str, SpeakerProfile] = {}
    for turn in turns:
        speaker_id = turn.speaker or "UNKNOWN"
        if speaker_id not in speakers:
            speakers[speaker_id] = SpeakerProfile(speaker_id=speaker_id)
        speakers[speaker_id].talk_time_seconds += max(0.0, turn.end - turn.start)
    for profile in speakers.values():
        profile.talk_time_seconds = round(profile.talk_time_seconds, 3)
    return speakers


def calculate_speaker_metrics(turns: list[TranscriptTurn]) -> dict[str, dict[str, int | float]]:
    metrics: dict[str, dict[str, int | float]] = {}
    for turn in turns:
        speaker_id = turn.speaker or "UNKNOWN"
        bucket = metrics.setdefault(
            speaker_id, {"turns": 0, "words": 0, "questions": 0, "talk_time_seconds": 0.0}
        )
        bucket["turns"] = int(bucket["turns"]) + 1
        bucket["words"] = int(bucket["words"]) + len(turn.text.split())
        bucket["questions"] = int(bucket["questions"]) + (1 if "?" in turn.text else 0)
        bucket["talk_time_seconds"] = round(
            float(bucket["talk_time_seconds"]) + max(0.0, turn.end - turn.start), 3
        )
    return metrics


def extract_top_terms(turns: list[TranscriptTurn], limit: int = 20) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for turn in turns:
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", turn.text.lower()):
            if word not in STOPWORDS:
                counter[word] += 1
    return counter.most_common(limit)


def quote_score(turn: TranscriptTurn) -> float:
    words = turn.text.split()
    score = min(len(words), 45) / 45
    lowered = turn.text.lower()
    if any(marker in lowered for marker in ["important", "key", "remember", "the point"]):
        score += 0.4
    if "?" in turn.text:
        score += 0.2
    return score


def is_music_or_noise(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("[") or stripped.startswith("♪") or stripped.endswith("♪")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
