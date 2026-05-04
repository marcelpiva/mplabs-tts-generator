# mplabs-tts

Generic, plugin-based pt-BR-first TTS pipeline built on
[F5-TTS](https://github.com/SWivid/F5-TTS).

Extracted from a production puzzle-game pipeline. Designed to be reusable
across projects (narrations, audiobook drafts, accessibility, voiceovers)
without dragging in any single project's domain knowledge.

## Why

F5-TTS produces excellent voice-cloned audio from a 5-15s reference WAV.
The hard part of getting good results isn't the model — it's preparing the
text: Portuguese accents, ordinals, currency, abbreviations, ALL-CAPS,
domain jargon. This package wraps F5-TTS with a 4-layer normalization
pipeline so the model sees clean, expanded text.

## The four layers

```
Raw text
   │
   ▼
1. Accent correction         ← LanguageModule.fix_accents + Plugin.fix_accents
   │
   ▼
2. Value normalization       ← universal cleanup (emoji, punctuation, ALL CAPS)
   │                           + LanguageModule.normalize_values (numbers, currency, ordinals)
   ▼
3. Prosody / pronunciation   ← LanguageModule.prosody_rules + Plugin.prosody_rules
   │
   ▼
4. Synthesis                 ← F5TTSSynthesizer (or any class implementing Synthesizer)
   │
   ▼
WAV → MP3 (ffmpeg)
```

## Install

```bash
git clone https://github.com/marcelpiva/mplabs-tts-generator.git
cd mplabs-tts-generator
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

System requirement: `ffmpeg` on PATH for MP3 output (`brew install ffmpeg`
on macOS).

Download the F5-TTS base model:

```bash
python scripts/download_models.py --variant base
# or for a pt-BR fine-tune:
python scripts/download_models.py --variant ptbr-multispeaker
```

## CLI

```bash
# Single phrase
mplabs-tts synth "Olá, mundo" -o /tmp/out.mp3

# Preview normalization (no model needed)
mplabs-tts normalize "O 1o passo custou R$ 1.500,00." 

# Batch from JSON
mplabs-tts batch examples/batch_input.json -o output/demo

# Batch with a plugin
mplabs-tts batch examples/batch_input.json -o output/medical \
    --plugin medical_ptbr

# Use your own plugin (module:Class)
mplabs-tts batch input.json -o output/ \
    --plugin myproject.tts_plugin:MyPlugin
```

All `synth` / `batch` commands honour these env vars (set in `.env` or
shell):

| Variable | Purpose |
|----------|---------|
| `MPLABS_TTS_MODEL` | F5-TTS `.safetensors` checkpoint |
| `MPLABS_TTS_VOCAB` | F5-TTS `vocab.txt` |
| `MPLABS_TTS_VOICE` | reference voice WAV |
| `MPLABS_TTS_VOICE_TEXT` | transcript of the reference voice |
| `MPLABS_TTS_DEVICE` | `mps` / `cuda` / `cpu` (default `mps`) |

## Programmatic use

```python
from mplabs_tts import TTSItem, TTSPipeline
from mplabs_tts.languages.pt_br import PtBrLanguage
from mplabs_tts.plugins.medical_ptbr import MedicalPtBrPlugin

pipeline = TTSPipeline(
    language=PtBrLanguage(),
    plugins=[MedicalPtBrPlugin()],
    model_path="models/model_last.safetensors",
    vocab_path="models/vocab.txt",
    ref_voice_wav="voices/male_narrator.wav",
    ref_voice_text="é muito emocionante os homens se encontrarem à noite no bosque",
    device="mps",
)

result = pipeline.synthesize(
    TTSItem(id="hello", text="Administre 500 mg b.i.d."),
    "out/hello.mp3",
)
print(result.normalized_text)  # "Administre quinhentos miligramas duas vezes ao dia."
print(result.audio_path, result.duration_s)
```

## Batch with resume + manifest

```python
from mplabs_tts.core.batch import BatchRunner

runner = BatchRunner(pipeline, output_dir="out/")
runner.run([
    TTSItem(id="intro", text="Olá!"),
    TTSItem(id="outro", text="Tchau!", metadata={"section": "ending"}),
])
# Writes:
#   out/intro.mp3
#   out/outro.mp3
#   out/progress.json   ← skip-list for resume
#   out/manifest.json   ← what was generated, with metadata + durations
```

Run twice — the second run is a no-op. Pass `force=True` to regenerate.

## Writing a plugin

Subclass `Plugin` and override what you need:

```python
import re
from mplabs_tts.plugins.base import Plugin

class MyBrandPlugin(Plugin):
    name = "mybrand"

    def fix_accents(self, text: str) -> str:
        return text.replace("MyBrand", "MyBränd")

    def prosody_rules(self):
        return [(re.compile(r"\bMyBrand\b"), "May Brand")]

    def extra_keep_upper(self):
        return {"MBR"}
```

Pass via `--plugin myproject.module:MyBrandPlugin` or
`TTSPipeline(plugins=[MyBrandPlugin()])`.

See `src/mplabs_tts/plugins/coconut3301.py` for a complete real-world
example.

## Adding a language module

Subclass `LanguageModule` and implement `fix_accents`,
`normalize_values`, and `prosody_rules`. Register it in
`src/mplabs_tts/cli.py:_LANGUAGES` to expose via `--language <code>`.

The pt-BR module under `src/mplabs_tts/languages/pt_br/` is the canonical
example. It splits accents, numbers, and prosody into separate files for
maintainability.

## Project layout

```
mplabs-tts-generator/
├── pyproject.toml            # build + CLI entry point
├── src/mplabs_tts/
│   ├── core/                 # pipeline, normalizer, synthesizer, batch
│   ├── languages/
│   │   ├── base.py
│   │   └── pt_br/            # built-in pt-BR module
│   ├── plugins/
│   │   ├── base.py
│   │   ├── medical_ptbr.py   # bundled plugin
│   │   └── coconut3301.py    # bundled plugin (reference example)
│   └── cli.py
├── voices/                   # reference WAVs + transcripts
├── scripts/download_models.py
├── examples/
└── tests/
```

## Tests

```bash
pytest                   # run everything
pytest tests/test_pt_br_accents.py -v
```

Tests mock the synthesizer so they run in seconds without loading the model.

## License

MIT — see [LICENSE](LICENSE).
