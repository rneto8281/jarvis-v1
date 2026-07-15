"""
Autenticação local do JarvisAI.

Modelo de ameaça: este é um assistente pessoal rodando em
``127.0.0.1``. O objetivo não é proteger contra atacantes remotos
sofisticados, e sim impedir que qualquer processo/aba do navegador na
mesma máquina controle o Jarvis sem uma senha explícita — por exemplo,
outro site aberto no navegador não deve conseguir chamar a API.

A senha nunca é armazenada em texto puro: apenas seu hash (PBKDF2-HMAC
com salt aleatório) é persistido em disco. Tokens de sessão são
aleatórios, mantidos em memória e expiram quando o servidor reinicia.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path

from backend.config.settings import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_CREDENCIAIS_PATH = settings.database.sqlite_path.parent / ".credentials.json"
_SENHA_PADRAO = os.getenv("JARVIS_PASSWORD", "jarvis")
_ITERACOES_PBKDF2 = 200_000


def _hash_senha(senha: str, salt: bytes) -> str:
    """Deriva um hash seguro da senha usando PBKDF2-HMAC-SHA256."""

    derivado = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, _ITERACOES_PBKDF2)
    return derivado.hex()


class AuthService:
    """Gerencia a senha local (hash em disco) e os tokens de sessão
    ativos (mantidos em memória)."""

    def __init__(self) -> None:
        self._tokens_ativos: set[str] = set()
        self._garantir_credenciais()

    def _garantir_credenciais(self) -> None:
        """Cria o arquivo de credenciais na primeira execução, usando a
        senha padrão (env var ``JARVIS_PASSWORD`` ou "jarvis"), com um
        aviso claro para o usuário trocar depois."""

        if _CREDENCIAIS_PATH.exists():
            return

        _CREDENCIAIS_PATH.parent.mkdir(parents=True, exist_ok=True)
        salt = secrets.token_bytes(16)
        dados = {"salt": salt.hex(), "hash": _hash_senha(_SENHA_PADRAO, salt)}
        _CREDENCIAIS_PATH.write_text(json.dumps(dados), encoding="utf-8")

        logger.warning(
            "Nenhuma credencial encontrada. Senha padrão definida como '%s'. "
            "Troque definindo a variável de ambiente JARVIS_PASSWORD e apagando "
            "o arquivo %s antes de reiniciar o servidor.",
            _SENHA_PADRAO,
            _CREDENCIAIS_PATH,
        )

    def verificar_senha(self, senha_tentativa: str) -> bool:
        """Verifica se a senha informada corresponde à armazenada,
        usando comparação de tempo constante (evita timing attacks)."""

        dados = json.loads(_CREDENCIAIS_PATH.read_text(encoding="utf-8"))
        salt = bytes.fromhex(dados["salt"])
        hash_calculado = _hash_senha(senha_tentativa, salt)

        return hmac.compare_digest(hash_calculado, dados["hash"])

    def emitir_token(self) -> str:
        """Gera e registra um novo token de sessão após login bem-sucedido."""

        token = secrets.token_urlsafe(32)
        self._tokens_ativos.add(token)
        return token

    def validar_token(self, token: str | None) -> bool:
        """Verifica se um token de sessão é válido e está ativo."""

        return token is not None and token in self._tokens_ativos

    def revogar_token(self, token: str) -> None:
        """Invalida um token de sessão (logout)."""

        self._tokens_ativos.discard(token)
