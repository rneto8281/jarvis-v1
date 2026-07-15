"""Rotas de autenticação: login local por senha e emissão de token."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.bootstrap import obter_auth_service
from backend.security.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginEntrada(BaseModel):
    """Corpo da requisição de login."""

    senha: str


class LoginSaida(BaseModel):
    """Corpo da resposta de login bem-sucedido."""

    token: str


@router.post("/login", response_model=LoginSaida)
def login(payload: LoginEntrada, auth: AuthService = Depends(obter_auth_service)) -> LoginSaida:
    """Autentica com a senha local e retorna um token de sessão."""

    if not auth.verificar_senha(payload.senha):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha incorreta.")

    return LoginSaida(token=auth.emitir_token())
