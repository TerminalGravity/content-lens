from content_lens.models import (
    SpeakerProfile,
    TopicSegment,
    TranscriptTurn,
    VideoMetadata,
    VisualObservation,
)
from content_lens.reporters.html import render_report


def test_html_reporter_lightweight():
    metadata = VideoMetadata(
        source="youtube", url="https://youtube.com/watch?v=123", title="Test Video", duration=120
    )
    turns = [
        TranscriptTurn(start=0.0, end=5.0, text="Hello world", speaker="SPEAKER_00"),
        TranscriptTurn(start=5.0, end=10.0, text="How are you", speaker="SPEAKER_01"),
    ]
    speakers = {
        "SPEAKER_00": SpeakerProfile(speaker_id="SPEAKER_00", name="Alice", talk_time_seconds=5.0),
        "SPEAKER_01": SpeakerProfile(speaker_id="SPEAKER_01", name="Bob", talk_time_seconds=5.0),
    }
    topics = [
        TopicSegment(
            start=0.0,
            end=10.0,
            title="Intro",
            summary="Greetings",
            speakers=["SPEAKER_00", "SPEAKER_01"],
        )
    ]
    visuals = [VisualObservation(time=0.0, description="Title screen", asset_path="frame_0.jpg")]
    html_output = render_report(metadata, turns, speakers, topics, visuals)

    assert "Test Video" in html_output
    assert "frame_0.jpg" in html_output
    assert "Alice" in html_output
    assert "SPEAKER_01" in html_output  # HTML rendering of speaker
    assert "Title screen" in html_output
