"""Brazilian Portuguese language module (pt_BR)."""

from __future__ import annotations

from typing import Iterable

from mplabs_tts.core.prosody import PronunciationRule
from mplabs_tts.languages.base import LanguageModule
from mplabs_tts.languages.pt_br.accents import (
    apply_phrase_replacements,
    apply_word_replacements,
)
from mplabs_tts.languages.pt_br.numbers import normalize_pt_br_values
from mplabs_tts.languages.pt_br.prosody import PT_BR_PROSODY_RULES


class PtBrLanguage(LanguageModule):
    """Brazilian Portuguese — accents, numbers, ordinals, currency, common abbreviations."""

    code = "pt_BR"

    def fix_accents(self, text: str) -> str:
        text = apply_word_replacements(text)
        text = apply_phrase_replacements(text)
        return text

    def normalize_values(self, text: str) -> str:
        return normalize_pt_br_values(text)

    def prosody_rules(self) -> Iterable[PronunciationRule]:
        return PT_BR_PROSODY_RULES

    def extra_keep_upper(self) -> Iterable[str]:
        return ("PIB", "OMS")


__all__ = ["PtBrLanguage"]
