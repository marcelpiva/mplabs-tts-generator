"""pt-BR prosody / pronunciation rules (Layer 3).

This module is the entry point for the language module. It composes:
- High-confidence pt-BR pronunciation rules from `pronunciation.py` (titles,
  oxítonas em -L, anglicismos consagrados).
- Project-specific prosody fixes that apply universally (rare — most
  domain-specific stuff belongs in plugins).

Domain-specific or brand-specific overrides MUST go in plugins, not here.
"""

from __future__ import annotations

import re

from mplabs_tts.core.prosody import PronunciationRule
from mplabs_tts.languages.pt_br.pronunciation import PT_BR_PRONUNCIATION_RULES

# Regras especiais que não cabem nas categorias genéricas de pronunciation.py
# mas ainda são pt-BR universais (não-domínio).
_EXTRAS: list[PronunciationRule] = [
    # Paçoca — manter pronúncia tônica (oxítona em vogal nasal sem acento gráfico)
    (re.compile(r"\bpaçocas\b"), "paçócas"),
    (re.compile(r"\bPaçocas\b"), "Paçócas"),
    (re.compile(r"\bpaçoca\b"), "paçóca"),
    (re.compile(r"\bPaçoca\b"), "Paçóca"),
]

PT_BR_PROSODY_RULES: list[PronunciationRule] = PT_BR_PRONUNCIATION_RULES + _EXTRAS
