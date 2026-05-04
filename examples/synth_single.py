#!/usr/bin/env python3
"""Minimal programmatic example: synthesize one phrase to MP3.

Run from the repo root after installing the package:
    pip install -e .
    python scripts/download_models.py --variant base
    python examples/synth_single.py
"""

from __future__ import annotations

import os
from pathlib import Path

from mplabs_tts import TTSItem, TTSPipeline
from mplabs_tts.languages.pt_br import PtBrLanguage

REPO = Path(__file__).resolve().parent.parent

pipeline = TTSPipeline(
    language=PtBrLanguage(),
    model_path=os.getenv("MPLABS_TTS_MODEL", REPO / "models" / "model_last.safetensors"),
    vocab_path=os.getenv("MPLABS_TTS_VOCAB", REPO / "models" / "vocab.txt"),
    ref_voice_wav=os.getenv("MPLABS_TTS_VOICE", REPO / "voices" / "male_narrator.wav"),
    ref_voice_text=os.getenv(
        "MPLABS_TTS_VOICE_TEXT",
        (REPO / "voices" / "male_narrator.txt").read_text().strip(),
    ),
    device=os.getenv("MPLABS_TTS_DEVICE", "mps"),
)

item = TTSItem(
    id="demo",
    text="Olá! Hoje é dia 5 de maio de 2026, e estamos rodando o mplabs-tts.",
)
out = REPO / "output" / "demo.mp3"
result = pipeline.synthesize(item, out)

print(f"Wrote {result.audio_path}")
print(f"Duration: {result.duration_s:.2f}s — generated in {result.gen_time_s:.2f}s")
print(f"Normalized text: {result.normalized_text}")
