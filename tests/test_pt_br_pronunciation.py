"""Tests for the universal pt-BR pronunciation rules in pronunciation.py.

These rules are applied to ALL pt-BR text without any plugin. They cover:
- Title abbreviations (Dr, Dra, Sr, Sra, Prof, Eng, Adv, Pe, Sta, Sto, Av, R)
- Oxítonas em -ol/-il/-al that F5-TTS reads as paroxítonas
- Anglicismos consagrados / siglas técnicas
"""

from __future__ import annotations

import pytest

from mplabs_tts.languages.pt_br.pronunciation import (
    OXITONAS_FORCADAS,
    PT_BR_PRONUNCIATION_RULES,
    TITULOS_EXTRA,
    ANGLICISMOS_CONSAGRADOS,
)
from mplabs_tts.core.prosody import apply_rules


# --- Títulos ---------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_substr",
    [
        ("Dr. Silva chegou", "Doutor Silva"),
        ("Dra. Costa atende", "Doutora Costa"),
        ("Sr. Almeida", "Senhor Almeida"),
        ("Sra. Pereira", "Senhora Pereira"),
        ("Srta. Lima", "Senhorita Lima"),
        ("Prof. Andrade", "Professor Andrade"),
        ("Profa. Silva", "Professora Silva"),
        ("Eng. Rocha", "Engenheiro Rocha"),
        ("Enga. Souza", "Engenheira Souza"),
        ("Adv. Mello", "Advogado Mello"),
        ("Pe. João", "Padre João"),
        ("Sta. Maria", "Santa Maria"),
        ("Sto. Antônio", "Santo Antônio"),
        ("Av. Paulista", "Avenida Paulista"),
    ],
)
def test_titulos_expand(raw: str, expected_substr: str):
    out = apply_rules(raw, TITULOS_EXTRA)
    assert expected_substr in out


# --- Oxítonas em -L --------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_substr",
    [
        # -ol
        ("paracetamol", "paracetamól"),
        ("omeprazol", "omeprazól"),
        ("atenolol", "atenolól"),
        ("salbutamol", "salbutamól"),
        ("haloperidol", "haloperidól"),
        ("fluconazol", "fluconazól"),
        ("metronidazol", "metronidazól"),
        ("etanol", "etanól"),
        ("colesterol", "colesteról"),
        ("mentol", "mentól"),
        # -il
        ("captopril", "captopríl"),
        ("enalapril", "enalapríl"),
        # -al
        ("fenobarbital", "fenobarbitál"),
    ],
)
def test_oxitona_singular(raw: str, expected_substr: str):
    out = apply_rules(raw, OXITONAS_FORCADAS)
    assert expected_substr in out


def test_oxitona_title_case_preserved():
    out = apply_rules("Atenolol", OXITONAS_FORCADAS)
    assert "Atenolól" in out


def test_oxitona_word_boundary_isolated():
    """Não deve substituir dentro de palavra maior."""
    out = apply_rules("paracetamoldemoxítona", OXITONAS_FORCADAS)
    # palavra inventada — não bate em \b
    assert "paracetamól" not in out


def test_oxitona_in_sentence():
    raw = "Prescrever paracetamol e captopril após refeição."
    out = apply_rules(raw, OXITONAS_FORCADAS)
    assert "paracetamól" in out
    assert "captopríl" in out
    assert "após refeição" in out  # não estraga o resto


# --- Plurais geradas automaticamente --------------------------------------


@pytest.mark.parametrize(
    "raw,expected_substr",
    [
        ("paracetamóis", "paracetamóis"),
        ("fenóis", "fenóis"),
        ("etanóis", "etanóis"),
    ],
)
def test_oxitona_plural_preserves_accent(raw: str, expected_substr: str):
    """Os plurais já estão acentuados na saída — confirmamos que as regras não
    quebram quem já está correto."""
    out = apply_rules(raw, OXITONAS_FORCADAS)
    assert expected_substr in out


# --- Anglicismos / siglas --------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_substr",
    [
        ("formato base64", "base meia quatro"),
        ("UTF-8 codificado", "U T F oito"),
        ("UTF8", "U T F oito"),
        ("PDF anexado", "P D F"),
        ("URL inválida", "U R L"),
        ("API REST", "A P I"),
        ("CEP do destinatário", "cep"),
        ("CPF e CNPJ", "C P F"),
        ("número do RG", "R G"),
    ],
)
def test_anglicismos_e_siglas(raw: str, expected_substr: str):
    out = apply_rules(raw, ANGLICISMOS_CONSAGRADOS)
    assert expected_substr in out


# --- Composição final ------------------------------------------------------


def test_full_pronunciation_rules_compose_titles_and_oxitonas():
    raw = "Dr. Silva prescreveu paracetamol e omeprazol via VO."
    out = apply_rules(raw, PT_BR_PRONUNCIATION_RULES)
    assert "Doutor Silva" in out
    assert "paracetamól" in out
    assert "omeprazól" in out
