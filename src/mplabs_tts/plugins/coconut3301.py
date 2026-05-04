"""Coconut 3301 brand plugin — example of a domain-specific plugin.

Use this when narrating Coconut 3301 content. It teaches the pipeline that
"cocada" should sound like "cocáda" (tonic accent shift), "coco" → "côco",
and that "Cococentrica" is a proper noun that needs an accent.

Use it as a reference template for your own brand/domain plugins.
"""

from __future__ import annotations

import re
from typing import Iterable

from mplabs_tts.core.prosody import PronunciationRule
from mplabs_tts.plugins.base import Plugin

_PROSODY: list[PronunciationRule] = [
    # Marca: Cocada → Cocáda (sílaba tônica deslocada)
    (re.compile(r"\bcocadas\b"), "cocádas"),
    (re.compile(r"\bCocadas\b"), "Cocádas"),
    (re.compile(r"\bcocada\b"), "cocáda"),
    (re.compile(r"\bCocada\b"), "Cocáda"),

    # Coco → Côco (vogal fechada)
    (re.compile(r"\bcocos\b"), "côcos"),
    (re.compile(r"\bCocos\b"), "Côcos"),
    (re.compile(r"\bcoco\b"), "côco"),
    (re.compile(r"\bCoco\b"), "Côco"),

    # Domínios fictícios pronunciados por extenso
    ("receitadavovo.com.br", "receita da vovó ponto com ponto bê érre"),
]

_ACCENT_FIXES: dict[str, str] = {
    "Cococentrica": "Cococêntrica",
    "Arqueologica": "Arqueológica",
    "Teorica": "Teórica",
    "Filosofica": "Filosófica",
    "Metaforas": "Metáforas",
    "Poeticos": "Poéticos",
    "Nostalgica": "Nostálgica",
    "Epicas": "Épicas",
    "Comecos": "Começos",
    "Criptograficas": "Criptográficas",
    "Criptograficos": "Criptográficos",
    "Numerica": "Numérica",
    "Matematica": "Matemática",
}

_KEEP_UPPER = {"QG", "CORP", "CNUT"}


class Coconut3301Plugin(Plugin):
    name = "coconut3301"

    def fix_accents(self, text: str) -> str:
        for old, new in _ACCENT_FIXES.items():
            text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
        return text

    def prosody_rules(self) -> Iterable[PronunciationRule]:
        return _PROSODY

    def extra_keep_upper(self) -> Iterable[str]:
        return _KEEP_UPPER
