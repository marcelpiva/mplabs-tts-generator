"""Layer 3 — prosody / pronunciation rule application.

Languages and plugins both contribute prosody rules; this module just runs
them in order. Each rule is `(pattern, replacement)` where `pattern` is either
a string (literal substring) or a compiled `re.Pattern`.
"""

from __future__ import annotations

import re
from typing import Iterable, Tuple, Union

PronunciationRule = Tuple[Union[str, re.Pattern[str]], str]


def apply_rules(text: str, rules: Iterable[PronunciationRule]) -> str:
    """Apply a sequence of pronunciation rules in order."""
    for pattern, replacement in rules:
        if isinstance(pattern, re.Pattern):
            text = pattern.sub(replacement, text)
        else:
            text = text.replace(pattern, replacement)
    return text
