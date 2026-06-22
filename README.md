# Content Lens

[![CI](https://github.com/TerminalGravity/content-lens/actions/workflows/ci.yml/badge.svg)](https://github.com/TerminalGravity/content-lens/actions/workflows/ci.yml)

Content Lens is a public, app-extensible post-processing pipeline for turning public content into structured, evidence-backed analysis artifacts. **v1 focuses on YouTube**: metadata, captions/transcripts, optional audio extraction, optional frame sampling, speaker diarization alignment, speaker identity hints, topic chunks, and Markdown/JSON reports.

The design separates extraction from interpretation:

```text
source app -> raw assets -> canonical timeline -> speakers/topics/claims/visuals -> reports
```

## v1 features

- YouTube adapter using `yt-dlp` when available.
- VTT caption normalization with duplicate cumulative-caption cleanup.
- Canonical JSON artifact format for downstream LLM analysis.
- Speaker-turn assignment from diarization segments.
- Optional hooks for `faster-whisper`/WhisperX-style transcripts and `pyannote.audio` diarization output.
- Built-in optional pyannote diarization runner via `--diarizer pyannote`.
- Frame sampling hook via `ffmpeg`.
- Markdown and HTML reports with timestamps, speakers, topics, questions, claims,
  action items, quotes, and visual evidence slots.
- App registry so X, Reddit, podcasts, or webpages can be added without changing core processors.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,youtube]'
```

Optional heavy extras:

```bash
pip install -e '.[transcribe,diarize,visual]'
```

## Quick start

```bash
content-lens analyze 'https://www.youtube.com/watch?v=VIDEO_ID' --out runs/my-video
```

With visual/audio assets when local tools are installed:

```bash
content-lens analyze URL --out runs/deep --download-audio --sample-frames
```

With local pyannote speaker diarization:

```bash
export HUGGINGFACE_TOKEN=...
pip install -e '.[youtube,diarize]'
content-lens analyze URL --out runs/speakers --diarizer pyannote
```

Outputs:

```text
runs/deep/
  metadata.json
  transcript.json
  diarization.json
  speakers.json
  speaker_metrics.json
  topics.json
  claims.json
  action_items.json
  quotes.json
  terms.json
  timeline.json
  report.md
  report.html
  assets/
```

## Speaker diarization

Content Lens intentionally keeps diarization provider-specific code behind a small boundary.
v1 can run pyannote locally when installed, or consume diarization JSON from pyannote-like segments:

```json
[{"speaker":"SPEAKER_00","start":0.0,"end":4.2}]
```

and align those segments to transcript turns. This lets users run local pyannote or hosted APIs and keep the same downstream report format.

## App/plugin contract

New apps implement `ContentApp` and return an `ExtractionResult`. See `src/content_lens/apps/base.py` and `docs/ADDING_APPS.md`.

## Design notes

- v1 keeps the CLI synchronous and simple. Long downloads, Whisper/WhisperX, pyannote,
  and frame extraction are intentionally exposed as explicit steps/artifacts first; progress
  callbacks and async/job-queue execution are good follow-up work once the artifact contract
  stabilizes.
- The YouTube adapter shells out to `yt-dlp --ignore-config` so CLI behavior matches the
  proven terminal workflow and avoids stale global config. A future adapter can swap in the
  `yt_dlp` Python API behind the same `ContentApp` boundary.
- Models are small slotted dataclasses for a stable v1 JSON shape. Extensions should add
  fields deliberately through the canonical artifacts rather than mutating objects at runtime.

## Status

This is v1 infrastructure: reliable artifact plumbing, CLI, tests, and YouTube adapter. Heavy ML models are optional so the project remains usable on normal laptops and CI.
