from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from content_lens.models import ExtractionResult


class ContentApp(ABC):
    """Adapter boundary for source-specific extraction."""

    name: str

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Return whether this adapter can process the URL/source."""

    @abstractmethod
    def extract(
        self,
        url: str,
        out_dir: Path,
        *,
        download_audio: bool = False,
        sample_frames: bool = False,
    ) -> ExtractionResult:
        """Extract raw and normalized artifacts into out_dir."""
