"""Tests for pt-BR number-to-words and value normalization."""

import pytest

from mplabs_tts.languages.pt_br.numbers import normalize_pt_br_values, number_to_words


@pytest.mark.parametrize(
    "n,expected",
    [
        (0, "zero"),
        (1, "um"),
        (15, "quinze"),
        (21, "vinte e um"),
        (100, "cem"),
        (101, "cento e um"),
        (200, "duzentos"),
        (999, "novecentos e noventa e nove"),
        (1000, "mil"),
        (1001, "mil e um"),
        (2000, "dois mil"),
        (12345, "doze mil trezentos e quarenta e cinco"),
    ],
)
def test_number_to_words(n, expected):
    assert number_to_words(n) == expected


def test_normalize_pt_br_values_doc_number():
    assert normalize_pt_br_values("ver #42") == "ver número quarenta e dois"


def test_normalize_pt_br_values_currency():
    assert normalize_pt_br_values("custo R$ 5") == "custo reais cinco"


def test_normalize_pt_br_values_24_7():
    # 24/7 → "24 horas por dia", and the chained number pass then expands "24" itself.
    assert normalize_pt_br_values("aberto 24/7") == "aberto vinte e quatro horas por dia"


def test_normalize_pt_br_values_ordinals_masculine():
    assert "primeiro" in normalize_pt_br_values("o 1o lugar")


def test_normalize_pt_br_values_ordinals_feminine():
    assert "segunda" in normalize_pt_br_values("a 2a etapa")


def test_normalize_pt_br_values_percent():
    assert "por cento" in normalize_pt_br_values("crescimento de 10%")


def test_normalize_pt_br_values_decimal_comma():
    assert "vírgula" in normalize_pt_br_values("custou 4,5 reais")


def test_normalize_pt_br_values_thousands_separator():
    out = normalize_pt_br_values("população de 12.345 pessoas")
    assert "doze mil" in out


def test_normalize_pt_br_values_protects_hex_prefix():
    out = normalize_pt_br_values("o byte 0xff")
    assert "0xff" in out  # not converted


def test_normalize_pt_br_values_protects_long_binary():
    out = normalize_pt_br_values("o código 11010110")
    assert "11010110" in out


def test_normalize_pt_br_values_ps_abbreviation():
    assert normalize_pt_br_values("P.S. importante") == "pós-escrito importante"
