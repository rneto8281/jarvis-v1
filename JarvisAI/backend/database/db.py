"""
Camada de conexão com o banco de dados.

Implementa o padrão Repository de forma minimalista: encapsula todo o
SQL da aplicação, para que o restante do sistema nunca precise
conhecer detalhes de armazenamento. A escolha de motor (SQLite hoje,
PostgreSQL futuramente) fica isolada aqui — ``settings.database.engine``
decide a implementação sem afetar quem consome o repositório.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from backend.config.settings import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL DEFAULT 'usuario',
    idioma TEXT NOT NULL DEFAULT 'pt',
    cidade TEXT
);

CREATE TABLE IF NOT EXISTS preferencia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    chave TEXT NOT NULL,
    valor TEXT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id),
    UNIQUE(usuario_id, chave)
);

CREATE TABLE IF NOT EXISTS conversa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    mensagem_usuario TEXT NOT NULL,
    intent TEXT,
    resposta TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

CREATE TABLE IF NOT EXISTS tarefa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    concluida INTEGER NOT NULL DEFAULT 0,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);
"""


class Database:
    """Gerencia a conexão e a inicialização do esquema do banco."""

    def __init__(self, caminho: Path | None = None) -> None:
        self._caminho = caminho or settings.database.sqlite_path
        self._caminho.parent.mkdir(parents=True, exist_ok=True)
        self._inicializar_esquema()

    @contextmanager
    def conexao(self):
        """Fornece uma conexão SQLite com ``row_factory`` configurado,
        garantindo fechamento automático via ``with``."""

        conn = sqlite3.connect(self._caminho)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _inicializar_esquema(self) -> None:
        """Cria as tabelas do banco caso ainda não existam (idempotente)."""

        with self.conexao() as conn:
            conn.executescript(_SCHEMA)
