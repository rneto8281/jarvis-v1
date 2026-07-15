"""Testes unitários do stemmer leve em português."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.utils.stemmer import stem, stem_frase


def test_reduz_infinitivo_verbal():
    assert stem("pesquisar") == "pesquis"
    assert stem("abrir") == "abr"


def test_reduz_gerundio():
    assert stem("pesquisando") == "pesquis"


def test_nao_reduz_palavras_curtas_demais():
    # Radical resultante ficaria menor que o mínimo confiável.
    assert stem("ir") == "ir"


def test_stem_frase_aplica_a_cada_palavra():
    resultado = stem_frase("pesquisando sobre buracos negros")
    assert "pesquis" in resultado
