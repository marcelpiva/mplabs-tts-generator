"""Dataclasses describing TTS inputs and outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TTSItem:
    """A unit of text to synthesize.

    Attributes:
        id: Stable identifier — drives output filename and progress key.
        text: Raw text. Goes through the full normalization pipeline.
        metadata: Free-form dict carried through to the manifest. Use it for
            tags, source, hierarchy (series/season/etc.), or anything you want
            to round-trip into the output manifest.
    """

    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TTSItem:
        item_id = data["id"]
        text = data["text"]
        metadata = {k: v for k, v in data.items() if k not in ("id", "text")}
        return cls(id=item_id, text=text, metadata=metadata)


@dataclass
class GenerationResult:
    """Result of a single synthesis call."""

    item_id: str
    audio_path: Path
    duration_s: float
    gen_time_s: float
    normalized_text: str
    sample_rate: int
