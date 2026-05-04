"""Tests for pt-BR accent correction."""

from mplabs_tts.languages.pt_br.accents import (
    apply_phrase_replacements,
    apply_word_replacements,
)


def test_word_replacement_basic_ao_words():
    assert apply_word_replacements("a operacao foi um sucesso") == "a operação foi um sucesso"


def test_word_replacement_keeps_word_boundaries():
    # "comeco" inside another word should NOT be replaced
    text = "uma palavraderoga"
    assert apply_word_replacements(text) == text


def test_word_replacement_preserves_capitalization_via_keys():
    assert apply_word_replacements("Operacao XYZ") == "Operação XYZ"


def test_word_replacement_proparoxitona():
    assert apply_word_replacements("a logica binaria") == "a lógica binária"  # binaria via WORD_MAP


def test_phrase_replacement_e_to_acute():
    # PHRASE_RULES are case-sensitive — "Isto e" matches, "isto e" doesn't.
    assert apply_phrase_replacements("Isto e simples") == "Isto é simples"


def test_phrase_replacement_does_not_overcorrect_e_as_conjunction():
    # "café e açúcar" — here "e" is conjunction, NOT verb. Should be untouched.
    text = "café e açúcar"
    assert apply_phrase_replacements(text) == text


def test_phrase_replacement_esta_to_acute():
    assert apply_phrase_replacements("voce esta sendo observado") == "voce está sendo observado"
    # "voce" itself isn't in this phrase rule (that's a separate rule).


def test_phrase_replacement_la_to_acute_in_safe_phrase():
    assert apply_phrase_replacements("vamos la dentro") == "vamos lá dentro"


def test_phrase_replacement_does_not_break_la_as_article():
    # "à la mode" — French phrase. "la" not in any safe rule, should stay.
    text = "à la mode"
    assert apply_phrase_replacements(text) == text
