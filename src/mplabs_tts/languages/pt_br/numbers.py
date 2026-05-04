"""pt-BR number-to-words and value normalization (Layer 2)."""

from __future__ import annotations

import re

_NUM_UNITS = [
    "zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete",
    "oito", "nove", "dez", "onze", "doze", "treze", "quatorze",
    "quinze", "dezesseis", "dezessete", "dezoito", "dezenove",
]
_NUM_TENS = [
    "", "", "vinte", "trinta", "quarenta", "cinquenta",
    "sessenta", "setenta", "oitenta", "noventa",
]
_NUM_HUNDREDS = [
    "", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos",
    "seiscentos", "setecentos", "oitocentos", "novecentos",
]

_ORDINALS_M = {
    "1o": "primeiro", "2o": "segundo", "3o": "terceiro", "4o": "quarto",
    "5o": "quinto", "6o": "sexto", "7o": "sétimo", "8o": "oitavo",
    "9o": "nono", "10o": "décimo",
}
_ORDINALS_F = {
    "1a": "primeira", "2a": "segunda", "3a": "terceira", "4a": "quarta",
    "5a": "quinta", "6a": "sexta", "7a": "sétima", "8a": "oitava",
    "9a": "nona", "10a": "décima",
}

_DOC_NUMBER = re.compile(r"#(\d+)")

# Patterns we deliberately do NOT expand — they're better read as digits.
_PROTECT_HEX_PAIRS = re.compile(r"(?:[0-9a-fA-F]{2} ){2,}[0-9a-fA-F]{2}")
_PROTECT_BINARY = re.compile(r"\b[01]{8,}\b")
_PROTECT_HEX_PREFIX = re.compile(r"0x[0-9a-fA-F]+")
_PROTECT_COORD = re.compile(r"\d+\.\d+[NSEW]")
_PROTECT_ASCII_SEQ = re.compile(r"\d{2,3}(?:,\s*\d{2,3}){2,}")
_PROTECT_ALPHANUM_ID = re.compile(r"\b[A-Za-z]+\d+[A-Za-z]*\b|\b\w+-\d+\b")


def number_to_words(n: int) -> str:
    """Convert integer 0-999_999 to Brazilian Portuguese words."""
    if n < 0 or n > 999_999:
        return str(n)
    if n == 0:
        return "zero"
    if n == 100:
        return "cem"

    if n >= 1000:
        thousands, remainder = divmod(n, 1000)
        if thousands == 1:
            parts = ["mil"]
        else:
            parts = [number_to_words(thousands) + " mil"]
        if remainder > 0:
            if remainder < 100:
                parts.append("e")
            parts.append(number_to_words(remainder))
        return " ".join(parts)

    if n >= 100:
        h, remainder = divmod(n, 100)
        if remainder == 0:
            return _NUM_HUNDREDS[h] if h > 1 else "cem"
        return f"{_NUM_HUNDREDS[h]} e {number_to_words(remainder)}"

    if n >= 20:
        t, u = divmod(n, 10)
        if u == 0:
            return _NUM_TENS[t]
        return f"{_NUM_TENS[t]} e {_NUM_UNITS[u]}"

    return _NUM_UNITS[n]


def normalize_pt_br_values(text: str) -> str:
    """Apply pt-BR specific value normalizations.

    Includes: document numbers (#N → "número N"), pt-BR abbreviations
    (P.S., a.C., R$, 24/7), ordinals (1o-10o / 1a-10a), percentages,
    decimals with comma, and full integer expansion. Hex/binary/coordinate
    sequences are preserved as digits.
    """
    # Document numbers
    text = _DOC_NUMBER.sub(lambda m: f"número {int(m.group(1))}", text)

    # Common pt-BR abbreviations
    text = text.replace("P.P.S.:", "pós-pós-escrito:")
    text = text.replace("P.P.S.", "pós-pós-escrito")
    text = text.replace("P.S.:", "pós-escrito:")
    text = text.replace("P.S.", "pós-escrito")
    text = text.replace("a.C.", "antes de Cristo")
    text = text.replace("24/7", "24 horas por dia")
    text = re.sub(r"R\$\s*", "reais ", text)

    # Strip stray dollar prefixes that aren't currency
    text = re.sub(r"\$(\d)", r"\1", text)
    text = re.sub(r"\$([A-Z])", r"\1", text)

    # Ordinals
    text = re.sub(
        r"\b(\d+)o\b",
        lambda m: _ORDINALS_M.get(m.group(0), m.group(0)),
        text,
    )
    text = re.sub(
        r"\b(\d+)a\b",
        lambda m: _ORDINALS_F.get(m.group(0), m.group(0)),
        text,
    )

    # Percentages with decimals
    def _pct_decimal(m: re.Match) -> str:
        integer = int(m.group(1))
        decimals = m.group(2)
        dec_words = " ".join(number_to_words(int(d)) for d in decimals)
        return f"{number_to_words(integer)} vírgula {dec_words} por cento"

    text = re.sub(r"\b(\d+)[.,](\d+)%", _pct_decimal, text)
    text = re.sub(
        r"\b(\d+)%",
        lambda m: f"{number_to_words(int(m.group(1)))} por cento",
        text,
    )

    # Protect IDs / hex / binary so they're not converted to words.
    protected: dict[str, str] = {}
    counter = [0]

    def _protect(m: re.Match) -> str:
        key = chr(0xE000 + counter[0])
        protected[key] = m.group(0)
        counter[0] += 1
        return key

    for pat in (
        _PROTECT_HEX_PAIRS,
        _PROTECT_BINARY,
        _PROTECT_HEX_PREFIX,
        _PROTECT_COORD,
        _PROTECT_ASCII_SEQ,
        _PROTECT_ALPHANUM_ID,
    ):
        text = pat.sub(_protect, text)

    # Thousands separators (pt-BR uses dots): 12.345 → "doze mil trezentos e quarenta e cinco"
    text = re.sub(
        r"\b\d{1,3}(?:\.\d{3})+\b",
        lambda m: number_to_words(int(m.group(0).replace(".", ""))),
        text,
    )

    # Decimal commas
    def _decimal_comma(m: re.Match) -> str:
        integer = int(m.group(1))
        decimals = m.group(2)
        dec_words = " ".join(number_to_words(int(d)) for d in decimals)
        return f"{number_to_words(integer)} vírgula {dec_words}"

    text = re.sub(r"\b(\d+),(\d+)\b", _decimal_comma, text)

    # Plain integers
    text = re.sub(
        r"\b(\d+)\b",
        lambda m: number_to_words(int(m.group(1))) if int(m.group(1)) <= 999_999 else m.group(0),
        text,
    )

    # Restore protected sequences
    for key, val in protected.items():
        text = text.replace(key, val)

    return text
