"""TTSPipeline — orchestrates language module + plugins + synthesizer."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Iterable

from mplabs_tts.core.models import GenerationResult, TTSItem
from mplabs_tts.core.normalizer import (
    DEFAULT_KEEP_UPPER,
    collapse_whitespace,
    lower_caps,
    normalize_newlines,
    normalize_punctuation,
    strip_emoji,
)
from mplabs_tts.core.prosody import apply_rules
from mplabs_tts.core.synthesizer import F5TTSSynthesizer, Synthesizer, wav_to_mp3
from mplabs_tts.languages.base import LanguageModule
from mplabs_tts.plugins.base import Plugin


class TTSPipeline:
    """4-layer text-to-speech pipeline.

    Layers:
        1. Accent correction       — language module + plugin overrides
        2. Value normalization     — universal cleanup + language number/abbr expansion
        3. Prosody / pronunciation — language rules + plugin rules
        4. Synthesis               — synthesizer backend (F5-TTS by default)
    """

    def __init__(
        self,
        language: LanguageModule,
        synthesizer: Synthesizer | None = None,
        plugins: Iterable[Plugin] | None = None,
        keep_upper: set[str] | None = None,
        # F5TTS convenience constructor args (ignored if `synthesizer` is provided)
        model_path: str | Path | None = None,
        vocab_path: str | Path | None = None,
        ref_voice_wav: str | Path | None = None,
        ref_voice_text: str | None = None,
        device: str = "mps",
    ):
        self.language = language
        self.plugins: list[Plugin] = list(plugins or [])
        self.keep_upper = self._build_keep_upper(keep_upper)

        if synthesizer is not None:
            self.synthesizer = synthesizer
        elif all([model_path, vocab_path, ref_voice_wav, ref_voice_text is not None]):
            self.synthesizer = F5TTSSynthesizer(
                model_path=model_path,  # type: ignore[arg-type]
                vocab_path=vocab_path,  # type: ignore[arg-type]
                ref_voice_wav=ref_voice_wav,  # type: ignore[arg-type]
                ref_voice_text=ref_voice_text,  # type: ignore[arg-type]
                device=device,
            )
        else:
            self.synthesizer = None  # normalize-only mode is fine for testing

    def _build_keep_upper(self, override: set[str] | None) -> set[str]:
        keep = set(DEFAULT_KEEP_UPPER) | set(self.language.extra_keep_upper())
        for plugin in self.plugins:
            keep |= set(plugin.extra_keep_upper())
        if override:
            keep |= override
        return keep

    # --- Normalization layers ---------------------------------------------

    def normalize(self, text: str) -> str:
        """Run layers 1-3 only. Useful for previews and tests."""
        # Layer 1 — accents
        text = self.language.fix_accents(text)
        for plugin in self.plugins:
            text = plugin.fix_accents(text)

        # Layer 2 — universal + language-specific value normalization
        text = strip_emoji(text)
        text = normalize_newlines(text)
        text = normalize_punctuation(text)
        text = self.language.normalize_values(text)
        text = lower_caps(text, self.keep_upper)
        text = collapse_whitespace(text)

        # Layer 3 — prosody (language first, then each plugin in order)
        text = apply_rules(text, self.language.prosody_rules())
        for plugin in self.plugins:
            text = apply_rules(text, plugin.prosody_rules())

        return text

    # --- Synthesis --------------------------------------------------------

    def synthesize(
        self,
        item: TTSItem | str,
        output_path: str | Path,
        seed: int = 42,
        as_mp3: bool = True,
    ) -> GenerationResult:
        """Synthesize a single item and write it to `output_path`.

        If `output_path` ends in `.mp3`, the result is converted via ffmpeg.
        Otherwise it's written as a WAV.
        """
        if self.synthesizer is None:
            raise RuntimeError(
                "Pipeline has no synthesizer — provide model/voice args or pass a Synthesizer."
            )

        if isinstance(item, str):
            item = TTSItem(id=Path(output_path).stem, text=item)

        normalized = self.normalize(item.text)

        import soundfile as sf  # lazy

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        t0 = time.time()
        wav, sr = self.synthesizer.synthesize(normalized, seed=seed)
        gen_time = time.time() - t0

        if as_mp3 and out.suffix.lower() == ".mp3":
            wav_tmp = out.with_suffix(".wav.tmp")
            sf.write(str(wav_tmp), wav, sr)
            try:
                wav_to_mp3(wav_tmp, out)
            finally:
                wav_tmp.unlink(missing_ok=True)
        else:
            sf.write(str(out), wav, sr)

        duration = float(len(wav)) / float(sr)
        return GenerationResult(
            item_id=item.id,
            audio_path=out,
            duration_s=round(duration, 2),
            gen_time_s=round(gen_time, 2),
            normalized_text=normalized,
            sample_rate=sr,
        )
