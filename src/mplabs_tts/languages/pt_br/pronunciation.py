"""pt-BR pronunciation hints for F5-TTS — the place to fix systematic errors
the model makes on regular Brazilian Portuguese words.

These rules are applied to ALL pt-BR text (no plugin needed). Each rule must
have HIGH CONFIDENCE — i.e., the spelling shipped to the model must produce a
better F5-TTS reading than the original AND must not break in any context.

Domain-specific jargon (medical units, brand names, niche acronyms) belongs
in plugins, not here.

Categories
----------
- TITULOS_EXTRA           — abbreviations of professional titles (Eng., Adv., Pe.)
- OXITONAS_FORCADAS       — words that follow pt-BR oxítona rules but aren't
                            graphically accented; F5-TTS reads them as
                            paroxítonas. We add an explicit acute accent on
                            the tonic vowel to force correct stress.
- ANGLICISMOS_CONSAGRADOS — established loanwords with standard pt-BR readings
                            the model often gets wrong.
- LETRAS_ISOLADAS         — single-letter spell-outs when surrounded by spaces
                            or punctuation (e.g. "letra x" → "letra xis").
"""

from __future__ import annotations

import re

from mplabs_tts.core.prosody import PronunciationRule

# =============================================================================
# Títulos profissionais comuns (alta confiança)
# =============================================================================
TITULOS_EXTRA: list[PronunciationRule] = [
    (re.compile(r"\bDr\.\s*"), "Doutor "),
    (re.compile(r"\bDr\b"), "Doutor"),
    (re.compile(r"\bDra\.\s*"), "Doutora "),
    (re.compile(r"\bDra\b"), "Doutora"),
    (re.compile(r"\bSr\.\s*"), "Senhor "),
    (re.compile(r"\bSra\.\s*"), "Senhora "),
    (re.compile(r"\bSrta\.\s*"), "Senhorita "),
    (re.compile(r"\bProf\.\s*"), "Professor "),
    (re.compile(r"\bProfa\.\s*"), "Professora "),
    (re.compile(r"\bEng\.\s*"), "Engenheiro "),
    (re.compile(r"\bEnga\.\s*"), "Engenheira "),
    (re.compile(r"\bAdv\.\s*"), "Advogado "),
    (re.compile(r"\bPe\.\s*"), "Padre "),
    (re.compile(r"\bSta\.\s*"), "Santa "),
    (re.compile(r"\bSto\.\s*"), "Santo "),
    (re.compile(r"\bAv\.\s*"), "Avenida "),
    (re.compile(r"\bR\.\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])"), "Rua "),
]


# =============================================================================
# Oxítonas terminadas em vogal+L que o F5-TTS lê como paroxítonas
# =============================================================================
# Lista curada de palavras pt-BR onde:
#   1. A regra é oxítona (tônica na última sílaba) — pt-BR padrão para
#      palavras polissílabas terminadas em -L sem acento gráfico.
#   2. F5-TTS treinado em corpus genérico tende a errar (lê como paroxítona).
#
# Estratégia: substituir a vogal tônica pela versão acentuada. O texto NUNCA é
# exibido ao usuário — só vai pro modelo TTS. O acento força a tonicidade.
#
# IMPORTANTE: não inclua palavras curtas (sol, mel, mal, fel, tal) — o modelo
# acerta. Não inclua palavras já com acento gráfico (fácil, móvel, túnel).

# Pares (forma_lower, forma_lower_com_acento) — geramos automaticamente as
# variações Title case e plural quando aplicável.
_OXITONAS_RAW: list[tuple[str, str]] = [
    # --- Medicamentos: -mol, -zol, -lol, -pril, -mal, -dol, -dal ---
    # Analgésicos / antitérmicos
    ("paracetamol", "paracetamól"),
    ("tramadol", "tramadól"),

    # Inibidores de bomba de prótons
    ("omeprazol", "omeprazól"),
    ("pantoprazol", "pantoprazól"),
    ("esomeprazol", "esomeprazól"),
    ("lansoprazol", "lansoprazól"),
    ("rabeprazol", "rabeprazól"),

    # Beta-bloqueadores
    ("atenolol", "atenolól"),
    ("metoprolol", "metoprolól"),
    ("propranolol", "propranolól"),
    ("carvedilol", "carvedilól"),
    ("bisoprolol", "bisoprolól"),
    ("nadolol", "nadolól"),
    ("nebivolol", "nebivolól"),

    # Inibidores ECA / antagonistas
    ("captopril", "captopríl"),
    ("enalapril", "enalapríl"),
    ("ramipril", "ramipríl"),
    ("lisinopril", "lisinopríl"),
    ("benazepril", "benazepríl"),
    ("perindopril", "perindopríl"),

    # Broncodilatadores
    ("salbutamol", "salbutamól"),
    ("albuterol", "albuteról"),
    ("formoterol", "formoteról"),

    # Antipsicóticos / sedativos / barbitúricos
    ("haloperidol", "haloperidól"),
    ("fenobarbital", "fenobarbitál"),
    ("tiopental", "tiopentál"),

    # Antifúngicos azólicos
    ("fluconazol", "fluconazól"),
    ("itraconazol", "itraconazól"),
    ("cetoconazol", "cetoconazól"),
    ("voriconazol", "voriconazól"),
    ("metronidazol", "metronidazól"),
    ("tinidazol", "tinidazól"),

    # --- Termos técnicos / químicos comuns oxítonos em -ol ---
    ("etanol", "etanól"),
    ("metanol", "metanól"),
    ("propanol", "propanól"),
    ("butanol", "butanól"),
    ("fenol", "fenól"),
    ("glicerol", "gliceról"),
    ("colesterol", "colesteról"),
    ("retinol", "retinól"),
    ("calciferol", "calciferól"),
    ("eucaliptol", "eucaliptól"),
    ("mentol", "mentól"),
]


def _expand_case_and_plural(pairs: list[tuple[str, str]]) -> list[PronunciationRule]:
    """Generate compiled regex rules for singular + plural, lowercase + Title case.

    pt-BR plural rules for words ending in vogal+L (oxítonas):
        -ol → -óis  (paracetamol → paracetamóis)
        -al → -ais  (carnaval → carnavais)
        -el → -éis  (anel → anéis)
        -ul → -uis  (rare)
        -il → -is   (captopril → captopris) — acento cai
    """
    plural_map = {"ol": "óis", "al": "ais", "el": "éis", "ul": "uis", "il": "is"}
    out: list[PronunciationRule] = []
    for lo, lo_acc in pairs:
        # singular
        out.append((re.compile(r"\b" + lo + r"\b"), lo_acc))
        out.append((re.compile(r"\b" + lo.capitalize() + r"\b"), lo_acc.capitalize()))

        # plural (somente se terminar em vogal+L)
        suffix = lo[-2:]
        if suffix in plural_map:
            plural = lo[:-2] + plural_map[suffix]
            # plural já tem acento gráfico onde precisa — basta deixar como está
            out.append((re.compile(r"\b" + plural + r"\b"), plural))
            out.append(
                (re.compile(r"\b" + plural.capitalize() + r"\b"), plural.capitalize())
            )
    return out


OXITONAS_FORCADAS: list[PronunciationRule] = _expand_case_and_plural(_OXITONAS_RAW)


# =============================================================================
# Anglicismos consagrados em pt-BR (alta confiança)
# =============================================================================
# Substituímos pela grafia que o F5-TTS lê com a fonética pt-BR mais próxima
# da pronúncia consagrada. Lista conservadora — só palavras universalmente
# pronunciadas dessa forma no Brasil.
ANGLICISMOS_CONSAGRADOS: list[PronunciationRule] = [
    # Termos técnicos comuns
    (re.compile(r"\b[Bb]ase64\b"), "base meia quatro"),
    (re.compile(r"\bUTF-?8\b"), "U T F oito"),
    (re.compile(r"\bUTF-?16\b"), "U T F dezesseis"),
    # Letras / siglas faladas
    (re.compile(r"\bPDF\b"), "P D F"),
    (re.compile(r"\bURL\b"), "U R L"),
    (re.compile(r"\bAPI\b"), "A P I"),
    (re.compile(r"\bCEP\b"), "cep"),  # lê como palavra
    (re.compile(r"\bCPF\b"), "C P F"),
    (re.compile(r"\bCNPJ\b"), "C N P J"),
    (re.compile(r"\bRG\b"), "R G"),
]


# =============================================================================
# Combinação final exportada
# =============================================================================
PT_BR_PRONUNCIATION_RULES: list[PronunciationRule] = (
    TITULOS_EXTRA + OXITONAS_FORCADAS + ANGLICISMOS_CONSAGRADOS
)
