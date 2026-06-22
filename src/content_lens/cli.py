from __future__ import annotations

import argparse
import json
from pathlib import Path

from content_lens.apps.registry import AppRegistry
from content_lens.models import dataclass_to_jsonable
from content_lens.processors.diarization import (
    align_speakers,
    infer_speaker_profiles,
    load_diarization_json,
)
from content_lens.processors.topics import segment_topics
from content_lens.reporters.markdown import render_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="content-lens")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze a URL/source into structured artifacts")
    analyze.add_argument("url")
    analyze.add_argument("--app", default="auto", help="App adapter name, or auto")
    analyze.add_argument("--out", type=Path, default=Path("content-lens-run"))
    analyze.add_argument("--download-audio", action="store_true")
    analyze.add_argument("--sample-frames", action="store_true")
    analyze.add_argument(
        "--diarization-json",
        type=Path,
        help="pyannote-like JSON segments to align",
    )
    analyze.add_argument("--topic-window-seconds", type=int, default=300)
    apps = sub.add_parser("apps", help="List registered source apps")
    apps.set_defaults(command="apps")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry = AppRegistry()
    if args.command == "apps":
        for name in registry.names():
            print(name)
        return 0
    if args.command == "analyze":
        app = registry.for_url(args.url) if args.app == "auto" else registry.by_name(args.app)
        args.out.mkdir(parents=True, exist_ok=True)
        result = app.extract(
            args.url,
            args.out,
            download_audio=args.download_audio,
            sample_frames=args.sample_frames,
        )
        diarization = (
            load_diarization_json(args.diarization_json)
            if args.diarization_json
            else result.diarization
        )
        turns = align_speakers(result.transcript, diarization)
        speakers = infer_speaker_profiles(turns, result.metadata.title, result.metadata.description)
        topics = segment_topics(turns, window_seconds=args.topic_window_seconds)

        write_json(args.out / "metadata.json", result.metadata)
        write_json(args.out / "transcript.json", turns)
        write_json(args.out / "diarization.json", diarization)
        write_json(args.out / "speakers.json", speakers)
        write_json(args.out / "topics.json", topics)
        write_json(
            args.out / "timeline.json",
            {
                "metadata": result.metadata,
                "speakers": speakers,
                "topics": topics,
                "turns": turns,
                "visuals": result.visuals,
                "assets": result.assets,
            },
        )
        (args.out / "report.md").write_text(
            render_report(result.metadata, turns, speakers, topics, result.visuals),
            encoding="utf-8",
        )
        print(f"Wrote artifacts to {args.out}")
        return 0
    return 2


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(dataclass_to_jsonable(value), indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
