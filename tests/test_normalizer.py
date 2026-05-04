"""Tests for the universal normalization layer."""

from mplabs_tts.core.normalizer import (
    DEFAULT_KEEP_UPPER,
    collapse_whitespace,
    lower_caps,
    normalize_newlines,
    normalize_punctuation,
    strip_emoji,
    universal_normalize,
)


def test_strip_emoji_removes_basic_and_skin_tones():
    assert strip_emoji("Olá 👋🏼 mundo 🌍!") == "Olá  mundo !"


def test_strip_emoji_preserves_letters_and_punctuation():
    text = "Texto sem emoji aqui."
    assert strip_emoji(text) == text


def test_normalize_newlines_double_becomes_period():
    assert normalize_newlines("linha um\n\nlinha dois") == "linha um. linha dois"


def test_normalize_newlines_single_becomes_space():
    assert normalize_newlines("linha um\nlinha dois") == "linha um linha dois"


def test_normalize_newlines_strips_bullet_dash():
    assert normalize_newlines("intro\n- item um\n- item dois") == "intro item um item dois"


def test_normalize_punctuation_em_dash_becomes_comma():
    assert normalize_punctuation("um — dois — três") == "um, dois, três"


def test_normalize_punctuation_arrow_becomes_comma():
    assert normalize_punctuation("a → b → c") == "a, b, c"


def test_normalize_punctuation_ellipsis_becomes_comma():
    assert normalize_punctuation("aguarde...vamos") == "aguarde, vamos"


def test_lower_caps_keeps_known_acronyms():
    assert lower_caps("O algoritmo usa SHA256 e MD5") == "O algoritmo usa SHA256 e MD5"


def test_lower_caps_titlecases_unknown_caps():
    assert lower_caps("BRASIL") == "Brasil"


def test_lower_caps_respects_custom_keep_upper():
    keep = DEFAULT_KEEP_UPPER | {"FOOBAR"}
    assert lower_caps("FOOBAR é único", keep) == "FOOBAR é único"


def test_collapse_whitespace_squashes_runs():
    assert collapse_whitespace("a   b   c  ") == "a b c"


def test_universal_normalize_pipeline_runs_in_order():
    text = "Linha 1 — com EMOJI 🎉\n\nLinha 2"
    result = universal_normalize(text)
    assert "🎉" not in result
    assert "—" not in result
    assert "Emoji" in result  # ALL CAPS got titlecased
    assert "Linha 2" in result
