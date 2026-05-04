"""Command-line interface: `mplabs-tts {synth,batch,normalize,download-models}`."""

from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

import click

from mplabs_tts.core.batch import BatchRunner
from mplabs_tts.core.models import TTSItem
from mplabs_tts.core.pipeline import TTSPipeline
from mplabs_tts.languages.pt_br import PtBrLanguage
from mplabs_tts.plugins.base import Plugin

# Built-in plugin registry: name → "module:Class"
_PLUGIN_REGISTRY: dict[str, str] = {
    "medical_ptbr": "mplabs_tts.plugins.medical_ptbr:MedicalPtBrPlugin",
    "coconut3301": "mplabs_tts.plugins.coconut3301:Coconut3301Plugin",
}

_LANGUAGES = {
    "pt_BR": PtBrLanguage,
}


def _load_plugin(spec: str) -> Plugin:
    """Resolve a plugin spec.

    Accepts either a built-in name (e.g. `medical_ptbr`) or a fully-qualified
    `module:ClassName` import path for user-defined plugins.
    """
    spec = _PLUGIN_REGISTRY.get(spec, spec)
    if ":" not in spec:
        raise click.BadParameter(
            f"Unknown plugin '{spec}'. Use a built-in name "
            f"({', '.join(_PLUGIN_REGISTRY)}) or 'module.path:ClassName'."
        )
    module_name, class_name = spec.split(":", 1)
    try:
        mod = importlib.import_module(module_name)
        cls = getattr(mod, class_name)
    except (ImportError, AttributeError) as e:
        raise click.BadParameter(f"Could not load plugin '{spec}': {e}") from e
    return cls()


def _build_pipeline(
    language_code: str,
    plugin_specs: tuple[str, ...],
    model_path: str | None,
    vocab_path: str | None,
    voice_wav: str | None,
    voice_text: str | None,
    device: str,
    require_synth: bool,
) -> TTSPipeline:
    if language_code not in _LANGUAGES:
        raise click.BadParameter(
            f"Language '{language_code}' not built in. Available: {', '.join(_LANGUAGES)}"
        )
    language = _LANGUAGES[language_code]()
    plugins = [_load_plugin(s) for s in plugin_specs]

    if require_synth:
        if not all([model_path, vocab_path, voice_wav, voice_text is not None]):
            raise click.BadParameter(
                "Missing model/vocab/voice for synthesis. "
                "Provide --model, --vocab, --voice, --voice-text "
                "(or set MPLABS_TTS_MODEL / MPLABS_TTS_VOCAB / MPLABS_TTS_VOICE / MPLABS_TTS_VOICE_TEXT)."
            )
        return TTSPipeline(
            language=language,
            plugins=plugins,
            model_path=model_path,
            vocab_path=vocab_path,
            ref_voice_wav=voice_wav,
            ref_voice_text=voice_text or "",
            device=device,
        )
    return TTSPipeline(language=language, plugins=plugins)


# --- shared options decorator -------------------------------------------------


def _synth_options(f):
    f = click.option("--model", "model_path", default=lambda: os.getenv("MPLABS_TTS_MODEL"),
                     help="Path to F5-TTS .safetensors checkpoint.")(f)
    f = click.option("--vocab", "vocab_path", default=lambda: os.getenv("MPLABS_TTS_VOCAB"),
                     help="Path to F5-TTS vocab.txt.")(f)
    f = click.option("--voice", "voice_wav", default=lambda: os.getenv("MPLABS_TTS_VOICE"),
                     help="Reference voice WAV file.")(f)
    f = click.option("--voice-text", default=lambda: os.getenv("MPLABS_TTS_VOICE_TEXT"),
                     help="Transcript of the reference voice WAV.")(f)
    f = click.option("--device", default=lambda: os.getenv("MPLABS_TTS_DEVICE", "mps"),
                     show_default="mps", help="Torch device: mps | cuda | cpu.")(f)
    return f


def _common_options(f):
    f = click.option("--language", "-l", default="pt_BR", show_default=True,
                     help="Language module to load.")(f)
    f = click.option("--plugin", "-p", multiple=True,
                     help="Plugin to enable (built-in name or module:Class). Repeatable.")(f)
    return f


# --- CLI ----------------------------------------------------------------------


@click.group()
@click.version_option()
def cli() -> None:
    """Generic, plugin-based TTS pipeline built on F5-TTS."""


@cli.command()
@click.argument("text")
@click.option("--output", "-o", required=True, type=click.Path(dir_okay=False),
              help="Output file (.mp3 or .wav).")
@click.option("--seed", default=42, show_default=True, type=int)
@_common_options
@_synth_options
def synth(
    text: str,
    output: str,
    seed: int,
    language: str,
    plugin: tuple[str, ...],
    model_path: str | None,
    vocab_path: str | None,
    voice_wav: str | None,
    voice_text: str | None,
    device: str,
) -> None:
    """Synthesize a single TEXT and write it to --output."""
    pipeline = _build_pipeline(language, plugin, model_path, vocab_path,
                                voice_wav, voice_text, device, require_synth=True)
    out = Path(output)
    as_mp3 = out.suffix.lower() == ".mp3"
    result = pipeline.synthesize(text, out, seed=seed, as_mp3=as_mp3)
    click.echo(f"OK  {result.audio_path}  {result.duration_s:.1f}s audio in {result.gen_time_s:.1f}s")
    click.echo(f"     normalized: {result.normalized_text[:120]}")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--output-dir", "-o", required=True, type=click.Path(file_okay=False),
              help="Directory for MP3 outputs.")
@click.option("--force", is_flag=True, help="Regenerate even items already in progress.json.")
@click.option("--seed", default=42, show_default=True, type=int)
@click.option("--wav", "as_wav", is_flag=True, help="Output WAV instead of MP3.")
@_common_options
@_synth_options
def batch(
    input_file: str,
    output_dir: str,
    force: bool,
    seed: int,
    as_wav: bool,
    language: str,
    plugin: tuple[str, ...],
    model_path: str | None,
    vocab_path: str | None,
    voice_wav: str | None,
    voice_text: str | None,
    device: str,
) -> None:
    """Synthesize all items from INPUT_FILE (a JSON array of {id, text, ...})."""
    with open(input_file, encoding="utf-8") as f:
        raw = json.load(f)
    items = [TTSItem.from_dict(d) for d in raw]
    click.echo(f"Loaded {len(items)} item(s) from {input_file}")

    pipeline = _build_pipeline(language, plugin, model_path, vocab_path,
                                voice_wav, voice_text, device, require_synth=True)
    runner = BatchRunner(pipeline, output_dir)
    runner.run(items, force=force, seed=seed, as_mp3=not as_wav)


@cli.command()
@click.argument("text")
@_common_options
def normalize(text: str, language: str, plugin: tuple[str, ...]) -> None:
    """Run only the text normalization layers (1-3) and print the result.

    Useful for previewing what the synthesizer will see, without loading the model.
    """
    pipeline = _build_pipeline(language, plugin, None, None, None, None,
                                "cpu", require_synth=False)
    click.echo(pipeline.normalize(text))


@cli.command("download-models")
@click.option("--repo", default="SWivid/F5-TTS", show_default=True,
              help="HuggingFace repo to pull from.")
@click.option("--filename", default=None,
              help="Specific filename to download (e.g. model_1200000.safetensors).")
@click.option("--output-dir", "-o", default="./models", show_default=True,
              type=click.Path(file_okay=False))
@click.option("--variant", type=click.Choice(["base", "ptbr-multispeaker", "ptbr-firstpixel"]),
              default=None, help="Convenience preset that picks a known repo.")
def download_models(repo: str, filename: str | None, output_dir: str, variant: str | None) -> None:
    """Download F5-TTS model weights from HuggingFace.

    Examples:
        mplabs-tts download-models --variant base
        mplabs-tts download-models --variant ptbr-multispeaker
        mplabs-tts download-models --repo myorg/myrepo --filename model.safetensors
    """
    if variant == "base":
        repo = "SWivid/F5-TTS"
    elif variant == "ptbr-multispeaker":
        repo = "Tharyck/multispeaker-ptbr-f5tts"
    elif variant == "ptbr-firstpixel":
        repo = "FirstPixel/F5-TTS-pt-br"

    try:
        from huggingface_hub import snapshot_download, hf_hub_download
    except ImportError as e:
        raise click.ClickException("huggingface_hub not installed. `pip install huggingface_hub`.") from e

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    click.echo(f"Downloading from {repo} → {out}")

    if filename:
        path = hf_hub_download(repo_id=repo, filename=filename, local_dir=str(out))
        click.echo(f"Downloaded: {path}")
    else:
        path = snapshot_download(repo_id=repo, local_dir=str(out))
        click.echo(f"Downloaded snapshot to: {path}")


def main() -> None:  # pragma: no cover
    cli()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(cli())
