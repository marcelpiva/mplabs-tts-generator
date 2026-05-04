"""Abstract base class for language modules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from mplabs_tts.core.prosody import PronunciationRule


class LanguageModule(ABC):
    """A language module supplies the language-specific pieces of the pipeline.

    Implementations must override `code`, `fix_accents`, `normalize_values`,
    and `prosody_rules`. `extra_keep_upper` is optional.
    """

    code: str = "und"  # ISO-ish locale code, e.g. "pt_BR"

    @abstractmethod
    def fix_accents(self, text: str) -> str:
        """Layer 1: correct missing diacritics in raw text."""

    @abstractmethod
    def normalize_values(self, text: str) -> str:
        """Layer 2: language-specific value expansion (numbers, currency, abbr, ordinals)."""

    @abstractmethod
    def prosody_rules(self) -> Iterable[PronunciationRule]:
        """Layer 3: phonetic respelling rules applied in order."""

    def extra_keep_upper(self) -> Iterable[str]:
        """Acronyms that must stay uppercase during ALL-CAPS handling."""
        return ()
