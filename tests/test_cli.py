from pathlib import Path

from content_lens import cli
from content_lens.apps.youtube import YouTubeApp
from content_lens.models import ExtractionResult, TranscriptTurn, VideoMetadata


def test_cli_writes_artifacts_with_diarization(monkeypatch, tmp_path):
    def fake_extract(self, url: str, out_dir: Path, **kwargs):
        return ExtractionResult(
            metadata=VideoMetadata(
                source="youtube",
                url=url,
                title="Interview with Builder",
                duration=65,
            ),
            transcript=[
                TranscriptTurn(0, 2, "Hello"),
                TranscriptTurn(2, 5, "How do we find speakers?"),
                TranscriptTurn(5, 8, "This is useful because it improves analysis."),
                TranscriptTurn(8, 11, "We should ship the pipeline."),
            ],
        )

    monkeypatch.setattr(YouTubeApp, "extract", fake_extract)
    diar = tmp_path / "diar.json"
    diar.write_text(
        '[{"speaker":"SPEAKER_00","start":0,"end":2.5},'
        '{"speaker":"SPEAKER_01","start":2.5,"end":5}]',
        encoding="utf-8",
    )
    out = tmp_path / "out"

    assert (
        cli.main(
            [
                "analyze",
                "https://www.youtube.com/watch?v=test",
                "--out",
                str(out),
                "--diarization-json",
                str(diar),
            ]
        )
        == 0
    )
    assert (out / "timeline.json").exists()
    assert (out / "report.html").exists()
    assert (out / "claims.json").exists()
    assert (out / "action_items.json").exists()
    assert (out / "speaker_metrics.json").exists()
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "SPEAKER_00" in report
    assert "How do we find speakers?" in report
    assert "This is useful because it improves analysis." in report
