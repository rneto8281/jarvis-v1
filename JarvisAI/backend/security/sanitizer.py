"""
Sanitização de entrada de texto.

Toda mensagem vinda do usuário (texto ou transcrição de voz) passa por
aqui antes de chegar ao motor de intents, reduzindo a superfície de
ataque (injeção de caracteres de controle, payloads absurdamente
longos, marcação HTML/script) sem impedir o uso normal em português.
"""

from __future__ import annotations

import re

_TAMANHO_MAXIMO = 500

# Remove tags HTML/script e caracteres de controle não imprimíveis,
# mas preserva acentuação e pontuação normal do português.
_PADRAO_TAG_HTML = re.compile(r"<[^>]*>")
_PADRAO_CONTROLE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class EntradaInvalida(ValueError):
    """Levantada quando a entrada do usuário não pode ser sanitizada
    para um uso seguro (ex.: vazia após limpeza, ou excede o limite)."""


def sanitizar_texto(texto: str) -> str:
    """Limpa e valida uma string de entrada do usuário.

    Args:
        texto: Texto bruto vindo do chat, da API ou da transcrição de voz.

    Returns:
        Texto limpo, pronto para ser processado pelo motor de intents.

    Raises:
        EntradaInvalida: se o texto ficar vazio após a limpeza ou
            exceder o tamanho máximo permitido.
    """

    if len(texto) > _TAMANHO_MAXIMO:
        raise EntradaInvalida(f"Mensagem excede o limite de {_TAMANHO_MAXIMO} caracteres.")

    limpo = _PADRAO_TAG_HTML.sub(" ", texto)
    limpo = _PADRAO_CONTROLE.sub("", limpo)
    limpo = limpo.strip()

    if not limpo:
        raise EntradaInvalida("Mensagem vazia após sanitização.")

    return limpo
