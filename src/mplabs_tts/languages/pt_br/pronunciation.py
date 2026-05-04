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
    # IA tem que ser case-sensitive (\bIA\b com flag default não basta — Python
    # re é case-sensitive por padrão, então `IA` ≠ `ia`/`Ia`. Bom.) "ia" lower
    # é pretérito do verbo "ir" e NÃO deve virar "I A".
    (re.compile(r"\bIA\b"), "I A"),
    (re.compile(r"\bIoT\b"), "I O T"),
]


# =============================================================================
# Nomes próprios pt-BR oxítonos terminados em consoante (sem acento gráfico)
# =============================================================================
# F5-TTS tende a ler como paroxítona (Éster, Ráfael) quando a tônica deveria
# ficar na última sílaba (Estér, Rafaél). Forçamos o acento agudo na última
# vogal pra guiar o modelo. Aplica-se SOMENTE quando capitalizado (nome
# próprio) — "ester" minúsculo é químico (éster) com acento próprio.
NOMES_OXITONOS: list[PronunciationRule] = [
    # Bíblicos / clássicos terminados em -er
    (re.compile(r"\bEster\b"), "Estér"),
    # Terminados em -el (oxítonos pt-BR)
    (re.compile(r"\bRafael\b"), "Rafaél"),
    (re.compile(r"\bGabriel\b"), "Gabriél"),
    (re.compile(r"\bDaniel\b"), "Daniél"),
    (re.compile(r"\bMiguel\b"), "Miguél"),
    (re.compile(r"\bManuel\b"), "Manuél"),
    (re.compile(r"\bManoel\b"), "Manoél"),
    (re.compile(r"\bJoel\b"), "Joél"),
    (re.compile(r"\bIsrael\b"), "Israél"),
    (re.compile(r"\bRaquel\b"), "Raquél"),
    (re.compile(r"\bIsabel\b"), "Isabél"),
    (re.compile(r"\bMabel\b"), "Mabél"),
    (re.compile(r"\bEzequiel\b"), "Ezequiél"),
    (re.compile(r"\bNoel\b"), "Noél"),
    # Terminados em -or (já tônicos por regra, mas reforça)
    # (intencionalmente vazio — "Heitor", "Cristóvão" geralmente saem ok)
]


# =============================================================================
# Vogais médias com timbre fechado (F5 lê com vogal aberta)
# =============================================================================
# Palavras pt-BR onde a vogal tônica é fechada (/e/, /o/) mas o modelo F5-TTS
# lê com vogal aberta (/ɛ/, /ɔ/). Forçamos o circunflexo (ê, ô) pra guiar.
VOGAIS_FECHADAS: list[PronunciationRule] = [
    # neutro/neutra — diphthong "eu" closed in pt-BR
    (re.compile(r"\bneutra\b"), "nêutra"),
    (re.compile(r"\bNeutra\b"), "Nêutra"),
    (re.compile(r"\bneutro\b"), "nêutro"),
    (re.compile(r"\bNeutro\b"), "Nêutro"),
    (re.compile(r"\bneutras\b"), "nêutras"),
    (re.compile(r"\bNeutras\b"), "Nêutras"),
    (re.compile(r"\bneutros\b"), "nêutros"),
    (re.compile(r"\bNeutros\b"), "Nêutros"),
]


# =============================================================================
# Monossílabos tônicos com vogal aberta (F5 atenua)
# =============================================================================
# Lista mínima — só onde o modelo realmente subentona. Cuidado: monossílabos
# muito comuns (mar, sol, fé, pé) geralmente saem corretos. Adicionar só
# quando confirmado em smoke test acústico.
MONOSSILABOS_TONICOS: list[PronunciationRule] = [
    (re.compile(r"\bvoz\b"), "vóz"),
    (re.compile(r"\bVoz\b"), "Vóz"),
    (re.compile(r"\bvozes\b"), "vózes"),
    (re.compile(r"\bVozes\b"), "Vózes"),
]


# =============================================================================
# Combinação final exportada
# =============================================================================
PT_BR_PRONUNCIATION_RULES: list[PronunciationRule] = (
    TITULOS_EXTRA
    + OXITONAS_FORCADAS
    + NOMES_OXITONOS
    + VOGAIS_FECHADAS
    + MONOSSILABOS_TONICOS
    + ANGLICISMOS_CONSAGRADOS
)
