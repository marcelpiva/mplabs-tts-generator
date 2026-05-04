"""mplabs-tts: generic, plugin-based TTS pipeline built on F5-TTS."""

from mplabs_tts.core.models import GenerationResult, TTSItem
from mplabs_tts.core.pipeline import TTSPipeline

__all__ = ["TTSPipeline", "TTSItem", "GenerationResult"]
__version__ = "0.1.0"
