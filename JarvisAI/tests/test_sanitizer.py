"""Testes unitários da sanitização de entrada."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from backend.security.sanitizer import EntradaInvalida, sanitizar_texto


def test_remove_tags_html():
    resultado = sanitizar_texto("<script>alert(1)</script> oi tudo bem")
    assert "<script>" not in resultado
    assert "oi tudo bem" in resultado


def test_rejeita_entrada_vazia_apos_limpeza():
    with pytest.raises(EntradaInvalida):
        sanitizar_texto("   ")


def test_rejeita_entrada_excessivamente_longa():
    with pytest.raises(EntradaInvalida):
        sanitizar_texto("a" * 1000)


def test_preserva_acentuacao_normal():
    resultado = sanitizar_texto("pesquise sobre a história do café")
    assert resultado == "pesquise sobre a história do café"
