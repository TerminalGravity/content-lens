from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from content_lens.apps.base import ContentApp
from content_lens.models import ExtractionResult, TranscriptTurn, VideoMetadata
from content_lens.processors.visuals import build_contact_sheet, frame_observations
from content_lens.processors.vtt import parse_vtt


class ToolMissingError(RuntimeError):
    pass


class YouTubeApp(ContentApp):
    name = "youtube"

    def can_handle(self, url: str) -> bool:
        host = urlparse(url).netloc.lower()
        return "youtube.com" in host or "youtu.be" in host

    def extract(
        self,
        url: str,
        out_dir: Path,
        *,
        download_audio: bool = False,
        sample_frames: bool = False,
    ) -> ExtractionResult:
        out_dir.mkdir(parents=True, exist_ok=True)
        assets_dir = out_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        ytdlp = _require_tool("yt-dlp")

        raw = _run_json([ytdlp, "--ignore-config", "--dump-json", url])
        metadata = VideoMetadata(
            source=self.name,
            url=url,
            title=raw.get("title") or "",
            channel=raw.get("channel") or raw.get("uploader") or "",
            duration=raw.get("duration"),
            description=raw.get("description") or "",
            raw={
                k: raw.get(k)
                for k in ("id", "webpage_url", "upload_date", "chapters", "tags")
                if k in raw
            },
        )

        transcript: list[TranscriptTurn] = []
        subtitle_path = _download_subtitles(ytdlp, url, assets_dir)
        assets: dict[str, str] = {}
        if subtitle_path:
            assets["captions_vtt"] = str(subtitle_path)
            transcript = parse_vtt(subtitle_path)

        if download_audio:
            audio = _download_audio(ytdlp, url, assets_dir)
            if audio:
                assets["audio"] = str(audio)

        visuals = []
        if sample_frames:
            video = _download_lowres_video(ytdlp, url, assets_dir)
            if video:
                assets["video"] = str(video)
                frame_dir = assets_dir / "frames"
                sampled = _sample_frames(video, frame_dir)
                if sampled:
                    assets["frames_dir"] = str(frame_dir)
                    visuals = frame_observations(sampled, out_dir)
                    contact_sheet = build_contact_sheet(sampled, assets_dir / "contact_sheet.jpg")
                    if contact_sheet:
                        assets["contact_sheet"] = str(contact_sheet)

        return ExtractionResult(
            metadata=metadata,
            transcript=transcript,
            visuals=visuals,
            assets=assets,
        )


def _require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise ToolMissingError(
            f"Missing required tool {name!r}. Install with `pip install -e '.[youtube]'` "
            "or install yt-dlp on PATH."
        )
    return path


def _run_json(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return json.loads(proc.stdout)


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def _download_subtitles(ytdlp: str, url: str, assets_dir: Path) -> Path | None:
    cmd = [
        ytdlp,
        "--ignore-config",
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-lang",
        "en.*",
        "--sub-format",
        "vtt",
        "-o",
        str(assets_dir / "%(id)s.%(ext)s"),
        url,
    ]
    # yt-dlp can return non-zero for one subtitle variant while still writing a usable VTT.
    try:
        _run(cmd)
    except subprocess.CalledProcessError:
        pass
    candidates = sorted(
        assets_dir.glob("*.vtt"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return None
    preferred = [path for path in candidates if path.name.endswith(".en.vtt")]
    return preferred[0] if preferred else candidates[0]


def _download_audio(ytdlp: str, url: str, assets_dir: Path) -> Path | None:
    before = set(assets_dir.glob("audio.*"))
    cmd = [
        ytdlp,
        "--ignore-config",
        "-x",
        "--audio-format",
        "wav",
        "-o",
        str(assets_dir / "audio.%(ext)s"),
        url,
    ]
    _run(cmd)
    after = set(assets_dir.glob("audio.*")) - before
    return sorted(after)[0] if after else None


def _download_lowres_video(ytdlp: str, url: str, assets_dir: Path) -> Path | None:
    cmd = [
        ytdlp,
        "--ignore-config",
        "-f",
        "bestvideo[height<=360]+bestaudio/best[height<=360]",
        "--merge-output-format",
        "mp4",
        "-o",
        str(assets_dir / "video.%(ext)s"),
        url,
    ]
    _run(cmd)
    matches = sorted(assets_dir.glob("video.*"))
    return matches[0] if matches else None


def _sample_frames(video: Path, frame_dir: Path, every_seconds: int = 30) -> list[Path]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return []
    frame_dir.mkdir(exist_ok=True)
    pattern = frame_dir / "frame_%05d.jpg"
    _run([ffmpeg, "-y", "-i", str(video), "-vf", f"fps=1/{every_seconds}", str(pattern)])
    return sorted(frame_dir.glob("*.jpg"))
