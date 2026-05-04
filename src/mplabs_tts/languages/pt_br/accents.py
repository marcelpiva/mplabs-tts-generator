"""Brazilian Portuguese accent correction.

Two-layer approach:

1. WORD_MAP — unambiguous word-level fixes. Always applied.
2. PHRASE_RULES — contextual fixes for ambiguous tokens (e.g. "e" → "é" only
   in specific phrases where it's surely a verb).

Domain-specific terms (e.g. brand names, custom jargon) belong in plugins,
not here.
"""

from __future__ import annotations

import re

# =============================================================================
# Unambiguous word replacements
# =============================================================================
WORD_MAP: dict[str, str] = {
    # -ão / -ões
    "Guardiao": "Guardião", "guardiao": "guardião",
    "Divisao": "Divisão", "divisao": "divisão",
    "Expansao": "Expansão", "expansao": "expansão",
    "comeco": "começo", "Comeco": "Começo",
    "comecar": "começar",
    "comecou": "começou",
    "comecaram": "começaram",
    "portao": "portão", "Portao": "Portão",
    "portoes": "portões",
    "inversao": "inversão",
    "direcao": "direção",
    "intencao": "intenção",
    "conclusao": "conclusão",
    "proporcao": "proporção",
    "compreensao": "compreensão",
    "questao": "questão",
    "visao": "visão",
    "Salao": "Salão", "salao": "salão",
    "missao": "missão",
    "traicao": "traição",
    "revelacao": "revelação",
    "proporcoes": "proporções", "Proporcoes": "Proporções",
    "versoes": "versões",
    "bilhoes": "bilhões",

    # -ção / -ções
    "operacao": "operação", "Operacao": "Operação",
    "falsificacao": "falsificação",
    "comunicacao": "comunicação",
    "organizacao": "organização",
    "classificacao": "classificação",
    "transmissao": "transmissão",
    "interceptacao": "interceptação",
    "decodificacao": "decodificação",
    "codificacao": "codificação",
    "substituicao": "substituição",

    # -ência / -ância
    "silencio": "silêncio", "Silencio": "Silêncio",
    "Silicio": "Silício",

    # Proparoxítonas
    "mitica": "mítica",
    "milenios": "milênios",
    "subterraneo": "subterrâneo",
    "hieroglificos": "hieroglíficos",
    "hieroglificas": "hieroglíficas",
    "arquitetonico": "arquitetônico",
    "geotermica": "geotérmica",
    "logicos": "lógicos", "Logicas": "Lógicas", "logicas": "lógicas",
    "logico": "lógico", "logica": "lógica", "Logico": "Lógico", "Logica": "Lógica",
    "cosmico": "cósmico",
    "ordinario": "ordinário",
    "intermediario": "intermediário",
    "intermediaria": "intermediária",
    "penultimo": "penúltimo",
    "quantica": "quântica",
    "especificas": "específicas", "especifico": "específico",
    "binarias": "binárias", "binaria": "binária",
    "indivisiveis": "indivisíveis",
    "divisiveis": "divisíveis",
    "inabalavel": "inabalável",
    "inquebravel": "inquebrável",
    "maiusculas": "maiúsculas",

    # Substantivos / adjetivos comuns
    "superficie": "superfície",
    "ruinas": "ruínas", "Ruinas": "Ruínas",
    "arvores": "árvores",
    "botanico": "botânico", "Botanico": "Botânico",
    "Botanica": "Botânica", "botanica": "botânica",
    "fisica": "física", "Fisica": "Física",
    "oleo": "óleo",
    "lagrimas": "lágrimas",
    "maos": "mãos",
    "manha": "manhã",
    "ceu": "céu", "ceus": "céus",
    "solida": "sólida",
    "tracos": "traços",
    "camaras": "câmaras",
    "tabuas": "tábuas",
    "espacamento": "espaçamento",
    "orcamento": "orçamento",
    "gramatica": "gramática",
    "digitos": "dígitos",
    "espacos": "espaços",
    "raciocinio": "raciocínio",
    "ingles": "inglês",
    "portugues": "português",
    "Bussola": "Bússola", "bussola": "bússola",
    "diaria": "diária",
    "joia": "jóia",
    "critico": "crítico", "critica": "crítica",
    "comite": "comitê",
    "maquina": "máquina",
    "insignia": "insígnia",
    "contrario": "contrário",
    "secundario": "secundário",
    "acessivel": "acessível",
    "senior": "sênior",
    "estagio": "estágio", "estagios": "estágios",
    "mantem": "mantém",
    "obtem": "obtém",
    "revelara": "revelará",
    "construida": "construída",
    "reconstruidas": "reconstruídas",
    "alcancar": "alcançar",
    "substituida": "substituída",
    "atraves": "através",
    "suico": "suíço", "suica": "suíça",
    "Suico": "Suíço", "Suica": "Suíça",

    # Verbos inequívocos
    "sera": "será",
    "serao": "serão",

    # Misc
    "tao ": "tão ",
    "explica-la": "explicá-la",
    "parametro": "parâmetro", "parametros": "parâmetros",
    "cirilico": "cirílico",
    "pedacos": "pedaços",
    "executavel": "executável",
    "clausula": "cláusula",
    "obvia": "óbvia",
    "identicos": "idênticos",
    "identicas": "idênticas",
    "leiloes": "leilões",
    "matematicos": "matemáticos",
    "caracteristicos": "característicos",
    "ciberseguranca": "cibersegurança",
    "lideranca": "liderança",
    "seguranca": "segurança",
    "confianca": "confiança",
    "alianca": "aliança",
    "vizinhanca": "vizinhança",
    "Cerimonia": "Cerimônia", "cerimonia": "cerimônia",
    "atomico": "atômico",
    "espaco": "espaço",
    "imperio": "império", "Imperio": "Império",
    "frances": "francês",
    "uniao": "união", "Uniao": "União",
    "limao": "limão",
    "nucleo": "núcleo",

    # Termos médicos comuns (também são pt-BR padrão fora de contexto médico)
    "diagnostico": "diagnóstico", "Diagnostico": "Diagnóstico",
    "diagnosticos": "diagnósticos",
    "prognostico": "prognóstico", "Prognostico": "Prognóstico",
    "sintomatico": "sintomático",
    "assintomatico": "assintomático",
    "patologico": "patológico", "patologica": "patológica",
    "clinico": "clínico", "clinica": "clínica",
    "cronico": "crônico", "cronica": "crônica",
    "toxico": "tóxico", "toxica": "tóxica",
    "genetico": "genético", "genetica": "genética",
    "terapeutico": "terapêutico", "terapeutica": "terapêutica",
    "farmaceutico": "farmacêutico", "farmaceutica": "farmacêutica",
    "antibiotico": "antibiótico", "antibioticos": "antibióticos",
    "anestesico": "anestésico",
    "analgesico": "analgésico",
    "metabolico": "metabólico", "metabolica": "metabólica",
    "cirurgico": "cirúrgico", "cirurgica": "cirúrgica",
    "sistolico": "sistólico",
    "diastolico": "diastólico",
    "prescricao": "prescrição", "Prescricao": "Prescrição",
    "infeccao": "infecção", "infeccoes": "infecções",
    "medicacao": "medicação",
    "administracao": "administração",
    "reabilitacao": "reabilitação",
    "hospitalizacao": "hospitalização",
    "transfusao": "transfusão",
    "incubacao": "incubação",
    "vacinacao": "vacinação",
    "desidratacao": "desidratação",
    "intoxicacao": "intoxicação",
    "contaminacao": "contaminação",
    "esterilizacao": "esterilização",
    "emergencia": "emergência", "Emergencia": "Emergência",
    "frequencia": "frequência",
    "resistencia": "resistência",
    "incidencia": "incidência",
    "prevalencia": "prevalência",
    "convalescencia": "convalescência",
    "deficiencia": "deficiência",
    "insuficiencia": "insuficiência",
    "vigilancia": "vigilância",
    "tolerancia": "tolerância",
    "substancia": "substância",
    "medico": "médico", "Medico": "Médico",
    "medica": "médica", "Medica": "Médica",
    "medicos": "médicos",
    "farmacia": "farmácia", "Farmacia": "Farmácia",
    "ciencia": "ciência",
    "virus": "vírus", "Virus": "Vírus",
    "analise": "análise", "Analise": "Análise",
    "analises": "análises",
    "orgao": "órgão", "orgaos": "órgãos",
    "obito": "óbito",
    "celula": "célula", "celulas": "células",
    "bacterias": "bactérias", "bacteria": "bactéria",
    "sindrome": "síndrome", "Sindrome": "Síndrome",
}

# =============================================================================
# Contextual phrase replacements
# =============================================================================

# "e" → "é" (verb ser/estar) — only in safe contexts
_E_VERB_PHRASES: list[tuple[str, str]] = [
    (r"\bnão e\b", "não é"),
    (r"\bque e\b", "que é"),
    (r"\bEste e\b", "Este é"),
    (r"\beste e\b", "este é"),
    (r"\bEsta e\b", "Esta é"),
    (r"\bEsse e\b", "Esse é"),
    (r"\bIsto e\b", "Isto é"),
    (r"\bIsso e\b", "Isso é"),
    (r"\bTudo e\b", "Tudo é"),
    (r"\btudo e\b", "tudo é"),
    (r"\bNem tudo e\b", "Nem tudo é"),
    (r"\bporque e\b", "porque é"),
    (r"\btambém e\b", "também é"),
    (r" e seu\b", " é seu"),
    (r" e sua\b", " é sua"),
    (r" e um termo\b", " é um termo"),
    (r" e um caso\b", " é um caso"),
    (r" e um número\b", " é um número"),
    (r" e uma operação\b", " é uma operação"),
    (r" e uma palavra\b", " é uma palavra"),
    (r" e sempre\b", " é sempre"),
    (r" e perfeita\b", " é perfeita"),
    (r" e protegida\b", " é protegida"),
    (r" e invertida\b", " é invertida"),
    (r" e considerada\b", " é considerada"),
    (r" e visível\b", " é visível"),
    (r" e sagrado\b", " é sagrado"),
    (r" e digno\b", " é digno"),
    (r" e marcado\b", " é marcado"),
    (r"\bA resposta e\b", "A resposta é"),
    (r"\bA chave e\b", "A chave é"),
]

# "esta" → "está" (verb estar) — only in safe contexts
_ESTA_VERB_PHRASES: list[tuple[str, str]] = [
    (r"\besta sendo\b", "está sendo"),
    (r"\besta lendo\b", "está lendo"),
    (r"\besta prestes\b", "está prestes"),
    (r"\besta diante\b", "está diante"),
    (r"\besta codificada\b", "está codificada"),
    (r"\besta codificado\b", "está codificado"),
    (r"\besta inscrita\b", "está inscrita"),
    (r"\besta inscrito\b", "está inscrito"),
    (r"\besta enterrada\b", "está enterrada"),
    (r"\besta emoldurada\b", "está emoldurada"),
    (r"\besta escondida\b", "está escondida"),
    (r"\besta escondido\b", "está escondido"),
    (r"\besta escrita\b", "está escrita"),
    (r"\besta selado\b", "está selado"),
    (r"\besta relacionada\b", "está relacionada"),
    (r"\besta quase\b", "está quase"),
    (r"\besta completa\b", "está completa"),
    (r"\besta pensando\b", "está pensando"),
    (r"\besta ao\b", "está ao"),
    (r"\bVocê esta\b", "Você está"),
    (r"\bvocê esta\b", "você está"),
    (r"\bjá esta\b", "já está"),
    (r"\bnão esta\b", "não está"),
]

# "la" → "lá" (adverb) — only in safe contexts
_LA_PHRASES: list[tuple[str, str]] = [
    (r"\bla na\b", "lá na"),
    (r"\bla no\b", "lá no"),
    (r"\bla dentro\b", "lá dentro"),
    (r"\bLa dentro\b", "Lá dentro"),
    (r"\bestamos la\b", "estamos lá"),
    (r"\bestaremos la\b", "estaremos lá"),
    (r"\bcolocado la\b", "colocado lá"),
    (r"\bcolocados la\b", "colocados lá"),
    (r"\bquase la\b", "quase lá"),
]

# "nos" → "nós" (pronoun) — only in safe contexts
_NOS_PHRASES: list[tuple[str, str]] = [
    (r"\bnos fizemos\b", "nós fizemos"),
    (r"\bnos estaremos\b", "nós estaremos"),
    (r"\bantes de nos\b", "antes de nós"),
]

# "contem" → "contém" — verb conter
_CONTEM_PHRASES: list[tuple[str, str]] = [
    (r"\bcontem um\b", "contém um"),
    (r"\bcontem uma\b", "contém uma"),
    (r"\bcontem dados\b", "contém dados"),
    (r"\bcontem fragmentos\b", "contém fragmentos"),
    (r"\bcontem as\b", "contém as"),
    (r"\bcontem os\b", "contém os"),
    (r"\bcontem registros\b", "contém registros"),
    (r"\bcontem informações\b", "contém informações"),
]

PHRASE_RULES: list[tuple[str, str]] = (
    _E_VERB_PHRASES
    + _ESTA_VERB_PHRASES
    + _LA_PHRASES
    + _NOS_PHRASES
    + _CONTEM_PHRASES
)


def apply_word_replacements(text: str) -> str:
    """Apply unambiguous word-level replacements with word-boundary matching."""
    for old, new in WORD_MAP.items():
        if old.endswith(" "):
            text = text.replace(old, new)
        else:
            pattern = r"\b" + re.escape(old) + r"\b"
            text = re.sub(pattern, new, text)
    return text


def apply_phrase_replacements(text: str) -> str:
    """Apply contextual phrase replacements for ambiguous words."""
    for pattern, replacement in PHRASE_RULES:
        text = re.sub(pattern, replacement, text)
    return text
