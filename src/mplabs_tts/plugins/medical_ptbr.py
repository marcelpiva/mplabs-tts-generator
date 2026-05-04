"""Medical pt-BR plugin — abbreviations, units, prescription notation.

Add this plugin when synthesizing medical content (prescriptions, diagnoses,
patient records). It expands SI/medical units, prescription abbreviations
(b.i.d., t.i.d.), and reads acronyms (Rx, Dx, BPM, SpO2) by their meaning
instead of letter-by-letter.
"""

from __future__ import annotations

import re
from typing import Iterable

from mplabs_tts.core.prosody import PronunciationRule
from mplabs_tts.plugins.base import Plugin

_RULES: list[PronunciationRule] = [
    # Unidades de massa, volume, pressão
    (re.compile(r"(?<=\d)mg\b"), " miligramas"),
    (re.compile(r"\bmg\b"), "miligramas"),
    (re.compile(r"(?<=\d)ml\b"), " mililitros"),
    (re.compile(r"\bml\b"), "mililitros"),
    (re.compile(r"(?<=\d)kg\b"), " quilogramas"),
    (re.compile(r"\bkg\b"), "quilogramas"),
    (re.compile(r"\bmmHg\b"), "milímetros de mercúrio"),
    (re.compile(r"\bmmol/L\b"), "milimóis por litro"),
    (re.compile(r"\bmEq/L\b"), "miliequivalentes por litro"),
    (re.compile(r"\bg/dL\b"), "gramas por decilitro"),

    # Sinais vitais
    (re.compile(r"\bSpO2\b"), "saturação de oxigênio"),
    (re.compile(r"\bBPM\b"), "batimentos por minuto"),

    # Posologia
    (re.compile(r"(?<!\w)b\.i\.d\.(?!\w)"), "duas vezes ao dia"),
    (re.compile(r"(?<!\w)t\.i\.d\.(?!\w)"), "três vezes ao dia"),
    (re.compile(r"(?<!\w)q\.i\.d\.(?!\w)"), "quatro vezes ao dia"),
    (re.compile(r"(?<!\w)q\.d\.(?!\w)"), "uma vez ao dia"),
    (re.compile(r"(?<!\w)p\.r\.n\.(?!\w)"), "quando necessário"),

    # Abreviações médicas
    (re.compile(r"\bRx\b"), "receita médica"),
    (re.compile(r"\bDx\b"), "diagnóstico"),
    (re.compile(r"\bHx\b"), "história clínica"),
    (re.compile(r"\bTx\b"), "tratamento"),
    (re.compile(r"\bSx\b"), "sintomas"),

    # Vias de administração
    (re.compile(r"\bVO\b"), "via oral"),
    (re.compile(r"\bIM\b"), "intramuscular"),
    (re.compile(r"\bIV\b"), "intravenosa"),
    (re.compile(r"\bSC\b"), "subcutânea"),

    # Setores e órgãos
    (re.compile(r"\bUTI\b"), "unidade de terapia intensiva"),
    (re.compile(r"\bOMS\b"), "Organização Mundial da Saúde"),

    # Exames
    (re.compile(r"\bEKG\b"), "eletrocardiograma"),
    (re.compile(r"\bECG\b"), "eletrocardiograma"),
    (re.compile(r"\bCBC\b"), "hemograma completo"),
    (re.compile(r"\bICD-10\b"), "Cê Í Dê dez"),
]

# Nota: oxítonas em -ol/-il (paracetamol, captopril, omeprazol, etc.) saem da
# pronúncia universal pt-BR e ficam em `languages/pt_br/pronunciation.py`. Aqui
# ficam apenas regras estritamente de domínio médico (unidades, posologia,
# acrônimos clínicos, vias de administração).

_EXTRA_ACCENTS: dict[str, str] = {
    # Termos médicos especializados não cobertos no léxico geral
    "epidemiologico": "epidemiológico", "epidemiologica": "epidemiológica",
    "neurologico": "neurológico", "neurologica": "neurológica",
    "cardiologico": "cardiológico",
    "oncologico": "oncológico",
    "ortopedico": "ortopédico",
    "oftalmologico": "oftalmológico",
    "psiquiatrico": "psiquiátrico",
    "pediatrico": "pediátrico",
    "prontuario": "prontuário", "Prontuario": "Prontuário",
    "laboratorio": "laboratório", "Laboratorio": "Laboratório",
    "ambulatorio": "ambulatório",
    "consultorio": "consultório",
    "oxigenio": "oxigênio",
    "calcio": "cálcio",
    "potassio": "potássio",
    "sodio": "sódio",
    "magnesio": "magnésio",
    "leucocitos": "leucócitos",
    "eritrocitos": "eritrócitos",
    "ulcera": "úlcera",
    "valvula": "válvula",
    "capsulas": "cápsulas", "capsula": "cápsula",
    "protese": "prótese",
    "estetoscopio": "estetoscópio",
    "termometro": "termômetro",
    "oximetro": "oxímetro",
    "dosificacao": "dosificação",
}

_KEEP_UPPER = {
    "EKG", "ECG", "ICD", "ICU", "UTI", "SpO2", "BPM", "WHO", "OMS",
    "PCR", "CPR", "RCP", "CPK", "LDH", "ALT", "AST", "HDL", "LDL",
    "IM", "IV", "VO", "SC", "CBC", "BMP",
}


class MedicalPtBrPlugin(Plugin):
    name = "medical_ptbr"

    def fix_accents(self, text: str) -> str:
        for old, new in _EXTRA_ACCENTS.items():
            text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
        return text

    def prosody_rules(self) -> Iterable[PronunciationRule]:
        return _RULES

    def extra_keep_upper(self) -> Iterable[str]:
        return _KEEP_UPPER
