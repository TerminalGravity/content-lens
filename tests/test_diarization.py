from content_lens.models import DiarizationSegment, TranscriptTurn
from content_lens.processors.diarization import align_speakers, infer_speaker_profiles


def test_align_speakers_by_overlap():
    turns = [TranscriptTurn(0, 2, "hello"), TranscriptTurn(2, 4, "there")]
    diar = [DiarizationSegment(0, 2.5, "SPEAKER_00"), DiarizationSegment(2.5, 4, "SPEAKER_01")]
    aligned = align_speakers(turns, diar)
    assert aligned[0].speaker == "SPEAKER_00"
    assert aligned[1].speaker == "SPEAKER_01"


def test_infer_profiles_talk_time():
    turns = [TranscriptTurn(0, 3, "a", "S0"), TranscriptTurn(3, 4, "b", "S1")]
    profiles = infer_speaker_profiles(turns, "Interview with someone", "")
    assert profiles["S0"].talk_time_seconds == 3
    assert profiles["S0"].confidence == 0.25
