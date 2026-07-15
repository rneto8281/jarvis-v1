"""
Utilitários de processamento de texto usados pelo motor de intenções.

Contém funções puras (sem efeitos colaterais) de normalização e
comparação de strings, o que facilita testes unitários isolados.
"""

from __future__ import annotations

import difflib
import re
import unicodedata


def normalizar(texto: str) -> str:
    """Normaliza um texto para comparação: minúsculas, sem acentos e
    sem pontuação supérflua.

    Args:
        texto: Texto de entrada, tipicamente a fala do usuário.

    Returns:
        Texto normalizado, pronto para tokenização ou comparação fuzzy.
    """

    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def similaridade(a: str, b: str) -> float:
    """Calcula a similaridade entre duas strings normalizadas.

    Usa ``difflib.SequenceMatcher``, que é suficientemente robusto para
    corrigir pequenas variações e erros de digitação sem exigir
    dependências pesadas de NLP.

    Returns:
        Valor entre 0.0 (nenhuma similaridade) e 1.0 (idênticas).
    """

    return difflib.SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()


def contem_palavra(texto: str, palavras: list[str]) -> bool:
    """Verifica se alguma das palavras/expressões está contida no texto
    normalizado (usado para expansão de sinônimos)."""

    texto_norm = normalizar(texto)
    return any(normalizar(p) in texto_norm for p in palavras)
