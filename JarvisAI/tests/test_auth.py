"""Testes unitários do serviço de autenticação local."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.security.auth import AuthService


def test_senha_correta_autentica():
    auth = AuthService()
    assert auth.verificar_senha("jarvis") is True


def test_senha_incorreta_nao_autentica():
    auth = AuthService()
    assert auth.verificar_senha("senha_errada") is False


def test_token_emitido_e_valido():
    auth = AuthService()
    token = auth.emitir_token()
    assert auth.validar_token(token) is True


def test_token_revogado_fica_invalido():
    auth = AuthService()
    token = auth.emitir_token()
    auth.revogar_token(token)
    assert auth.validar_token(token) is False


def test_token_desconhecido_e_invalido():
    auth = AuthService()
    assert auth.validar_token("token-que-nunca-existiu") is False
