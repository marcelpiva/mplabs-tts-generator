"""pt-BR prosody / pronunciation rules (Layer 3)."""

from __future__ import annotations

import re

from mplabs_tts.core.prosody import PronunciationRule

PT_BR_PROSODY_RULES: list[PronunciationRule] = [
    # Títulos comuns
    (re.compile(r"\bDr\.\s*"), "Doutor "),
    (re.compile(r"\bDr\b"), "Doutor"),
    (re.compile(r"\bDra\.\s*"), "Doutora "),
    (re.compile(r"\bDra\b"), "Doutora"),
    (re.compile(r"\bSr\.\s*"), "Senhor "),
    (re.compile(r"\bSra\.\s*"), "Senhora "),
    (re.compile(r"\bProf\.\s*"), "Professor "),
    (re.compile(r"\bProfa\.\s*"), "Professora "),

    # Termos técnicos lidos por extenso
    (re.compile(r"\b[Bb]ase64\b"), "base meia quatro"),

    # Paçoca — manter pronúncia tônica
    (re.compile(r"\bpaçocas\b"), "paçócas"),
    (re.compile(r"\bPaçocas\b"), "Paçócas"),
    (re.compile(r"\bpaçoca\b"), "paçóca"),
    (re.compile(r"\bPaçoca\b"), "Paçóca"),
]
