"""
Dependências de segurança compartilhadas pelas rotas da API.

Centraliza a verificação de token de sessão em um único ponto
(princípio DRY), aplicável via ``Depends(exigir_autenticacao)`` em
qualquer rota que precise de proteção.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from backend.bootstrap import obter_auth_service
from backend.security.auth import AuthService


def exigir_autenticacao(
    request: Request, auth: AuthService = Depends(obter_auth_service)
) -> None:
    """Verifica o token de sessão enviado no header ``Authorization``.

    Espera o formato ``Authorization: Bearer <token>``. Levanta 401 se
    o token estiver ausente ou inválido.
    """

    cabecalho = request.headers.get("Authorization", "")

    if not cabecalho.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de sessão ausente."
        )

    token = cabecalho.removeprefix("Bearer ").strip()

    if not auth.validar_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de sessão inválido ou expirado."
        )
