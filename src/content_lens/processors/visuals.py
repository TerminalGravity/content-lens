from __future__ import annotations

from pathlib import Path

from content_lens.models import VisualObservation


def frame_observations(frame_paths: list[Path], run_dir: Path) -> list[VisualObservation]:
    observations: list[VisualObservation] = []
    for index, frame in enumerate(sorted(frame_paths)):
        try:
            asset = str(frame.relative_to(run_dir))
        except ValueError:
            asset = str(frame)
        observations.append(
            VisualObservation(
                time=float(index * 30),
                description="Sampled video frame; run OCR/vision enrichment for semantic detail.",
                asset_path=asset,
                confidence=0.2,
            )
        )
    return observations


def build_contact_sheet(
    frame_paths: list[Path], output_path: Path, *, columns: int = 4
) -> Path | None:
    if not frame_paths:
        return None
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None

    images = []
    for frame in sorted(frame_paths):
        try:
            img = Image.open(frame).convert("RGB")
        except OSError:
            continue
        img.thumbnail((320, 180))
        images.append((frame, img.copy()))
        img.close()
    if not images:
        return None

    cell_w, cell_h = 340, 220
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    for index, (frame, img) in enumerate(images):
        x = (index % columns) * cell_w
        y = (index // columns) * cell_h
        sheet.paste(img, (x + 10, y + 10))
        draw.text((x + 10, y + 195), frame.name, fill=(20, 20, 20))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, quality=90)
    return output_path
