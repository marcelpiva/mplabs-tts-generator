"""Tests for the orchestrating TTSPipeline. Synthesizer is mocked out."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from mplabs_tts.core.batch import BatchRunner
from mplabs_tts.core.models import TTSItem
from mplabs_tts.core.pipeline import TTSPipeline
from mplabs_tts.languages.pt_br import PtBrLanguage
from mplabs_tts.plugins.coconut3301 import Coconut3301Plugin
from mplabs_tts.plugins.medical_ptbr import MedicalPtBrPlugin


class FakeSynth:
    """Returns 1 second of silence at 24kHz, ignoring input text."""

    def __init__(self):
        self.calls: list[str] = []

    def synthesize(self, text: str, seed: int = 42):
        self.calls.append(text)
        return np.zeros(24_000, dtype=np.float32), 24_000


# --- normalize() integration ---------------------------------------------


def test_normalize_runs_all_layers_with_pt_br():
    pipeline = TTSPipeline(language=PtBrLanguage(), synthesizer=FakeSynth())
    out = pipeline.normalize("a operacao tem 1o passo e esta sendo executada")
    assert "operação" in out
    assert "primeiro" in out
    assert "está sendo" in out


def test_normalize_with_coconut_plugin_applies_brand_prosody():
    pipeline = TTSPipeline(
        language=PtBrLanguage(),
        plugins=[Coconut3301Plugin()],
        synthesizer=FakeSynth(),
    )
    out = pipeline.normalize("A cocada e o coco")
    assert "cocáda" in out
    assert "côco" in out


def test_normalize_with_medical_plugin_expands_units():
    pipeline = TTSPipeline(
        language=PtBrLanguage(),
        plugins=[MedicalPtBrPlugin()],
        synthesizer=FakeSynth(),
    )
    out = pipeline.normalize("administre 500 mg b.i.d.")
    assert "miligramas" in out
    assert "duas vezes ao dia" in out


def test_pt_br_forces_drug_oxitona_accent_without_plugin():
    """F5-TTS reads 'paracetamol' as paroxítona by default; the core pt-BR
    pronunciation rules force the explicit oxítona accent on common -ol/-il
    drug names. No medical plugin needed — these are universal pt-BR words.
    """
    pipeline = TTSPipeline(language=PtBrLanguage(), synthesizer=FakeSynth())
    out = pipeline.normalize(
        "Prescrever paracetamol, omeprazol e captopril; Atenolol após refeição."
    )
    assert "paracetamól" in out
    assert "omeprazól" in out
    assert "captopríl" in out
    assert "Atenolól" in out


def test_pt_br_forces_oxitona_plural():
    """Plurais de oxítonas em -ol também precisam do acento (paracetamóis,
    fenóis). O expansor gera as formas plurais automaticamente.
    """
    pipeline = TTSPipeline(language=PtBrLanguage(), synthesizer=FakeSynth())
    out = pipeline.normalize("paracetamóis e fenóis")
    # plural já vem com acento; basta garantir que não foi quebrado
    assert "paracetamóis" in out
    assert "fenóis" in out


def test_normalize_preserves_acronyms_added_by_plugin():
    pipeline = TTSPipeline(
        language=PtBrLanguage(),
        plugins=[MedicalPtBrPlugin()],
        synthesizer=FakeSynth(),
    )
    out = pipeline.normalize("LDL e HDL elevados")
    # LDL/HDL come from medical plugin's keep_upper — should NOT be titlecased
    assert "LDL" in out
    assert "HDL" in out


# --- synthesize() with mock ---------------------------------------------


def test_synthesize_writes_wav_when_output_is_wav(tmp_path: Path):
    synth = FakeSynth()
    pipeline = TTSPipeline(language=PtBrLanguage(), synthesizer=synth)
    out = tmp_path / "x.wav"
    result = pipeline.synthesize(TTSItem(id="x", text="olá mundo"), out, as_mp3=False)
    assert out.exists()
    assert result.duration_s == pytest.approx(1.0, abs=0.05)
    assert result.sample_rate == 24_000
    assert synth.calls and "olá" in synth.calls[0]


def test_synthesize_raises_when_no_synthesizer():
    pipeline = TTSPipeline(language=PtBrLanguage())  # no synth
    with pytest.raises(RuntimeError, match="no synthesizer"):
        pipeline.synthesize("texto", "/tmp/out.wav")


# --- batch runner with mock ---------------------------------------------


def test_batch_runner_skips_already_generated(tmp_path: Path):
    synth = FakeSynth()
    pipeline = TTSPipeline(language=PtBrLanguage(), synthesizer=synth)
    runner = BatchRunner(pipeline, tmp_path)
    items = [TTSItem(id="a", text="texto a"), TTSItem(id="b", text="texto b")]

    runner.run(items, as_mp3=False)
    assert len(synth.calls) == 2

    # Re-run — should skip both
    runner.run(items, as_mp3=False)
    assert len(synth.calls) == 2  # no new calls


def test_batch_runner_force_regenerates(tmp_path: Path):
    synth = FakeSynth()
    pipeline = TTSPipeline(language=PtBrLanguage(), synthesizer=synth)
    runner = BatchRunner(pipeline, tmp_path)
    items = [TTSItem(id="a", text="texto a")]

    runner.run(items, as_mp3=False)
    runner.run(items, as_mp3=False, force=True)
    assert len(synth.calls) == 2


def test_batch_runner_writes_manifest(tmp_path: Path):
    pipeline = TTSPipeline(language=PtBrLanguage(), synthesizer=FakeSynth())
    runner = BatchRunner(pipeline, tmp_path)
    items = [TTSItem(id="a", text="texto a", metadata={"tag": "demo"})]

    runner.run(items, as_mp3=False)
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["total_items"] == 1
    assert manifest["generated"] == 1
    assert manifest["items"][0]["id"] == "a"
    assert manifest["items"][0]["metadata"]["tag"] == "demo"
    assert manifest["items"][0]["duration_s"] == pytest.approx(1.0, abs=0.05)


def test_ttsitem_from_dict_separates_metadata():
    item = TTSItem.from_dict({"id": "x", "text": "olá", "section": "intro", "tag": "a"})
    assert item.id == "x"
    assert item.text == "olá"
    assert item.metadata == {"section": "intro", "tag": "a"}
