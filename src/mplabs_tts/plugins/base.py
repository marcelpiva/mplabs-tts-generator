"""Plugin contract.

Plugins layer additional rules on top of a `LanguageModule`. They run after
the language module in each layer (so plugin overrides win). Implement only
what you need — defaults are no-ops.
"""

from __future__ import annotations

from typing import Iterable

from mplabs_tts.core.prosody import PronunciationRule


class Plugin:
    """Base plugin. Subclass and override the layers you care about."""

    name: str = "plugin"

    def fix_accents(self, text: str) -> str:
        """Layer 1 — extra accent / spelling fixes."""
        return text

    def prosody_rules(self) -> Iterable[PronunciationRule]:
        """Layer 3 — extra phonetic rules."""
        return ()

    def extra_keep_upper(self) -> Iterable[str]:
        """Acronyms this plugin needs preserved during ALL-CAPS handling."""
        return ()
