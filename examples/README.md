# Examples

| File | What it shows |
|------|---------------|
| `batch_input.json` | Input format the CLI's `batch` command expects (array of `{id, text, metadata}`). |
| `synth_single.py` | Minimal programmatic use — one item to one MP3. |
| `batch_with_plugin.py` | Batch run with `Coconut3301Plugin` enabled. |

## Running

Install in editable mode and download a model first:

```bash
pip install -e .
python scripts/download_models.py --variant base
```

Then either of:

```bash
# CLI
mplabs-tts batch examples/batch_input.json -o output/demo \
    --voice voices/male_narrator.wav \
    --voice-text "$(cat voices/male_narrator.txt)" \
    --model models/model_last.safetensors \
    --vocab models/vocab.txt

# Or programmatic
python examples/synth_single.py
python examples/batch_with_plugin.py
```

## Normalization preview (no model needed)

```bash
mplabs-tts normalize "O 1o passo custa R$ 1.500,00 — pague em b.i.d." \
    --plugin medical_ptbr
```
