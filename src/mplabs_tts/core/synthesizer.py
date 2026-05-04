"""Layer 4 — audio synthesis. F5-TTS implementation + abstract base."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Protocol


class Synthesizer(Protocol):
    """Minimal contract a synthesis backend must satisfy."""

    def synthesize(self, text: str, seed: int = 42) -> tuple[Any, int]:
        """Run inference and return `(audio_array, sample_rate)`."""
        ...


class F5TTSSynthesizer:
    """F5-TTS backend with voice cloning via reference WAV."""

    def __init__(
        self,
        model_path: str | Path,
        vocab_path: str | Path,
        ref_voice_wav: str | Path,
        ref_voice_text: str,
        device: str = "mps",
        model_name: str = "F5TTS_v1_Base",
    ):
        self.model_path = str(model_path)
        self.vocab_path = str(vocab_path)
        self.ref_voice_wav = str(ref_voice_wav)
        self.ref_voice_text = ref_voice_text
        self.device = device
        self.model_name = model_name
        self._tts = None

    def _ensure_loaded(self) -> None:
        if self._tts is not None:
            return
        # Imported lazily so importing the package doesn't pull in torch.
        from f5_tts.api import F5TTS

        self._tts = F5TTS(
            model=self.model_name,
            ckpt_file=self.model_path,
            vocab_file=self.vocab_path,
            device=self.device,
        )

    def synthesize(self, text: str, seed: int = 42) -> tuple[Any, int]:
        self._ensure_loaded()
        wav, sr, _ = self._tts.infer(  # type: ignore[union-attr]
            ref_file=self.ref_voice_wav,
            ref_text=self.ref_voice_text,
            gen_text=text,
            seed=seed,
            show_info=lambda *a, **kw: None,
        )
        return wav, sr


def wav_to_mp3(wav_path: Path, mp3_path: Path, bitrate: str = "64k", sample_rate: int = 24000) -> None:
    """Convert WAV to MP3 via ffmpeg. Requires `ffmpeg` on PATH."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH — install it to enable MP3 output.")
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(wav_path),
            "-b:a", bitrate, "-ar", str(sample_rate),
            str(mp3_path),
        ],
        capture_output=True,
        check=True,
    )
