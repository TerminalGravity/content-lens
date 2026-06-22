from content_lens.models import TranscriptTurn
from content_lens.processors.artifacts import (
    calculate_speaker_stats,
    extract_action_items,
    extract_claims,
    extract_quotes,
    extract_top_terms,
)


def test_extract_quotes():
    turns = [
        TranscriptTurn(
            start=0.0,
            end=2.0,
            text='He said "this is a very important quote" yesterday.',
            speaker="SPEAKER_01",
        ),
        TranscriptTurn(start=2.0, end=4.0, text='Just a "short" quote.', speaker="SPEAKER_02"),
    ]
    quotes = extract_quotes(turns)
    assert len(quotes) == 1
    assert quotes[0].text == "this is a very important quote"
    assert quotes[0].speaker == "SPEAKER_01"


def test_extract_action_items():
    turns = [
        TranscriptTurn(
            start=0.0, end=2.0, text="I think we should look into this later.", speaker="SPEAKER_01"
        ),
        TranscriptTurn(start=2.0, end=4.0, text="No actions here.", speaker="SPEAKER_02"),
        TranscriptTurn(
            start=4.0, end=6.0, text="I will send out the calendar invite!", speaker="SPEAKER_01"
        ),
    ]
    actions = extract_action_items(turns)
    assert len(actions) == 2
    assert actions[0].text == "we should look into this later."
    assert actions[1].text == "I will send out the calendar invite!"
    assert actions[0].owner == "SPEAKER_01"


def test_extract_claims_and_terms():
    turns = [
        TranscriptTurn(
            start=0.0,
            end=2.0,
            text="This is useful because speaker-aware analysis improves summaries.",
            speaker="SPEAKER_01",
        ),
        TranscriptTurn(
            start=2.0, end=4.0, text="Speaker analysis helps analysis.", speaker="SPEAKER_02"
        ),
    ]
    claims = extract_claims(turns)
    terms = extract_top_terms(turns, limit=3)

    assert len(claims) == 1
    assert claims[0].speaker == "SPEAKER_01"
    assert terms[0][0] == "analysis"


def test_calculate_speaker_stats():
    turns = [
        TranscriptTurn(start=0.0, end=2.5, text="Hello", speaker="SPEAKER_01"),
        TranscriptTurn(start=3.0, end=4.0, text="Hi", speaker="SPEAKER_02"),
        TranscriptTurn(start=4.0, end=5.0, text="How are you?", speaker="SPEAKER_01"),
    ]
    stats = calculate_speaker_stats(turns)
    assert len(stats) == 2
    assert "SPEAKER_01" in stats
    assert stats["SPEAKER_01"].talk_time_seconds == 3.5
    assert stats["SPEAKER_02"].talk_time_seconds == 1.0
