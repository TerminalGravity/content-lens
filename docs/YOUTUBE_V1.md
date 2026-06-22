# YouTube v1 workflow

```bash
content-lens analyze URL --out runs/video
```

Internally this uses `yt-dlp --ignore-config` to avoid stale global config, downloads English VTT captions when present, normalizes VTT into transcript turns, optionally downloads audio/low-res video, and writes canonical JSON artifacts.

## Diarization

Run pyannote directly when `pyannote.audio` is installed and `HUGGINGFACE_TOKEN` is set:

```bash
content-lens analyze URL --out runs/video --diarizer pyannote
```

Or run pyannote/another provider separately and pass its segments:

```bash
content-lens analyze URL --out runs/video --diarization-json pyannote_segments.json
```

Expected shape:

```json
[{"speaker":"SPEAKER_00","start":0.0,"end":3.1}]
```

## Next v1.x work

- WhisperX/faster-whisper transcription runner.
- Contact-sheet generation and OCR/vision summarization.
- HTML report.
