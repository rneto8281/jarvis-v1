"""
Stemmer leve para português (sem dependências externas).

Não é uma implementação completa do algoritmo RSLP (que exige uma
tabela extensa de regras e exceções), mas cobre os casos mais comuns
de variação verbal e nominal em comandos falados/digitados — o
suficiente para melhorar a taxa de acerto do motor de similaridade
fuzzy sem adicionar uma dependência pesada como NLTK.

Se no futuro for necessário um stemming mais preciso, esta função pode
ser substituída por ``nltk.stem.RSLPStemmer`` sem alterar o restante
do sistema — a assinatura (``str -> str``) permanece igual.
"""

from __future__ import annotations

# Ordem importa: sufixos mais longos e específicos primeiro, para
# evitar que uma regra genérica "coma" um sufixo mais informativo.
_SUFIXOS_VERBAIS = [
    "ando", "endo", "indo",  # gerúndio
    "aram", "eram", "iram",  # pretérito perfeito (3ª pl.)
    "aria", "eria", "iria",  # futuro do pretérito
    "asse", "esse", "isse",  # subjuntivo imperfeito
    "arei", "erei", "irei",  # futuro do presente (1ª sing.)
    "ando", "endo",
    "ar", "er", "ir",  # infinitivo
    "ou", "eu", "iu",  # pretérito perfeito (3ª sing.)
]

_SUFIXOS_NOMINAIS = [
    "mente",  # advérbios de modo
    "ezinho", "ezinha",  # diminutivos
    "inho", "inha",
    "oes", "aes", "eis",  # pluralizações irregulares comuns
    "ais", "eis", "ois",
    "s",  # plural simples (regra mais genérica, aplicada por último)
]

_TAMANHO_MINIMO_RADICAL = 3


def stem(palavra: str) -> str:
    """Reduz uma palavra ao seu radical aproximado.

    Args:
        palavra: Palavra já normalizada (minúscula, sem acentos).

    Returns:
        O radical aproximado da palavra, ou a própria palavra se
        nenhuma regra se aplicar ou se a redução deixasse um radical
        curto demais para ser confiável.
    """

    for sufixo in _SUFIXOS_VERBAIS + _SUFIXOS_NOMINAIS:
        if palavra.endswith(sufixo) and len(palavra) - len(sufixo) >= _TAMANHO_MINIMO_RADICAL:
            return palavra[: -len(sufixo)]

    return palavra


def stem_frase(frase: str) -> str:
    """Aplica ``stem`` a cada palavra de uma frase já tokenizada por
    espaços, retornando a frase reduzida."""

    return " ".join(stem(p) for p in frase.split())
