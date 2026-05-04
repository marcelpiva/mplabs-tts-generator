"""Layer 2 — universal value normalization.

The pieces here are language-agnostic: emoji stripping, whitespace cleanup,
punctuation harmonization, ALL-CAPS handling. Anything language-specific
(numbers to words, currency, ordinals, abbreviations) lives in the active
LanguageModule and is invoked through it.
"""

from __future__ import annotations

import re

_EMOJI_RE = re.compile(
    "["
    "\U0001f300-\U0001faff"
    "\U00002702-\U000027b0"
    "\U0000fe00-\U0000fe0f"
    "\U0000200d"
    "]+",
    flags=re.UNICODE,
)

_ROMAN_NUMERALS = {
    "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII",
}

DEFAULT_KEEP_UPPER = _ROMAN_NUMERALS | {
    # Tech / crypto acronyms — almost always read as letters, not words.
    "MD5", "ROT13", "ASCII", "SHA256", "CEO", "XOR", "PIB", "DNA", "FBI",
    "CIA", "GPS", "USB", "PDF", "HTML", "CSS", "URL", "API", "RAM", "ROM",
    "LED", "PIN", "SOS", "VIP", "FAQ", "ID", "DNS", "TXT", "RSA", "RTLO",
    "DDOS", "TTS", "UTC", "MIT", "SSH", "IP",
}

_ALL_CAPS_WORD = re.compile(r"\b([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,}\d*)\b")
_MULTI_SPACES = re.compile(r" {2,}")


def strip_emoji(text: str) -> str:
    """Remove emoji-range Unicode characters."""
    return _EMOJI_RE.sub("", text)


def normalize_newlines(text: str) -> str:
    """Convert newlines into TTS-friendly punctuation."""
    text = re.sub(r"\n- ", "\n", text)
    text = text.replace("\n\n", ". ")
    text = text.replace("\n", " ")
    return text


def normalize_punctuation(text: str) -> str:
    """Convert visual separators into commas so the engine pauses appropriately."""
    text = text.replace(" -- ", ", ")
    text = text.replace(" — ", ", ")
    text = text.replace("—", ", ")
    text = text.replace(" // ", ", ")
    text = text.replace(" → ", ", ")
    text = text.replace("→", ", ")
    text = text.replace("...", ", ")
    return text


def lower_caps(text: str, keep_upper: set[str] | None = None) -> str:
    """Lowercase ALL-CAPS tokens unless they are in `keep_upper` (preserved as acronyms)."""
    keep = keep_upper if keep_upper is not None else DEFAULT_KEEP_UPPER

    def _replace(m: re.Match) -> str:
        word = m.group(1)
        if word in keep:
            return word
        return word.title()

    return _ALL_CAPS_WORD.sub(_replace, text)


def collapse_whitespace(text: str) -> str:
    """Collapse multiple consecutive spaces and trim."""
    return _MULTI_SPACES.sub(" ", text).strip()


def universal_normalize(text: str, keep_upper: set[str] | None = None) -> str:
    """Run the language-agnostic normalizations in order.

    Order matters: emoji first (so the punctuation step doesn't fight Unicode
    punctuation inside emoji sequences), then newlines, then visual separators.
    ALL-CAPS handling and whitespace collapse run last because the
    language-specific stage is expected to slot in before them.
    """
    text = strip_emoji(text)
    text = normalize_newlines(text)
    text = normalize_punctuation(text)
    text = lower_caps(text, keep_upper)
    text = collapse_whitespace(text)
    return text
