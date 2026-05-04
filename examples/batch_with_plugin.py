#!/usr/bin/env python3
"""Batch synthesis with the Coconut3301 plugin loaded.

Demonstrates how a project-specific plugin slots into the pipeline:
"cocada" comes out as "cocáda" because of `Coconut3301Plugin.prosody_rules`.
"""

from __future__ import annotations

import os
from pathlib import Path

from mplabs_tts import TTSItem, TTSPipeline
from mplabs_tts.core.batch import BatchRunner
from mplabs_tts.languages.pt_br import PtBrLanguage
from mplabs_tts.plugins.coconut3301 import Coconut3301Plugin

REPO = Path(__file__).resolve().parent.parent

pipeline = TTSPipeline(
    language=PtBrLanguage(),
    plugins=[Coconut3301Plugin()],
    model_path=os.getenv("MPLABS_TTS_MODEL", REPO / "models" / "model_last.safetensors"),
    vocab_path=os.getenv("MPLABS_TTS_VOCAB", REPO / "models" / "vocab.txt"),
    ref_voice_wav=os.getenv("MPLABS_TTS_VOICE", REPO / "voices" / "male_narrator.wav"),
    ref_voice_text=os.getenv(
        "MPLABS_TTS_VOICE_TEXT",
        (REPO / "voices" / "male_narrator.txt").read_text().strip(),
    ),
    device=os.getenv("MPLABS_TTS_DEVICE", "mps"),
)

items = [
    TTSItem(id="cocada_demo", text="A Cocada é a marca registrada do cartel.",
            metadata={"section": "branding"}),
    TTSItem(id="coco_demo", text="O coco é firme; os cocos são misteriosos.",
            metadata={"section": "branding"}),
]

runner = BatchRunner(pipeline, REPO / "output" / "coconut_demo")
runner.run(items)
