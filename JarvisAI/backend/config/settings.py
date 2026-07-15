"""
Módulo de configuração central do JarvisAI.

Centraliza todos os parâmetros configuráveis da aplicação em um único
ponto, seguindo o princípio de responsabilidade única (SRP) e evitando
"magic numbers"/strings espalhados pelo código.

As configurações podem ser sobrescritas por variáveis de ambiente,
permitindo diferentes perfis (desenvolvimento, produção) sem alterar
o código-fonte.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class DatabaseSettings:
    """Configurações de acesso ao banco de dados."""

    engine: str = os.getenv("JARVIS_DB_ENGINE", "sqlite")
    sqlite_path: Path = BASE_DIR / "backend" / "database" / "jarvis.db"
    # Preparado para migração futura sem alterar o restante do código.
    postgres_dsn: str = os.getenv("JARVIS_POSTGRES_DSN", "")


@dataclass(frozen=True)
class ApiSettings:
    """Configurações do servidor de API local."""

    host: str = os.getenv("JARVIS_API_HOST", "127.0.0.1")
    port: int = int(os.getenv("JARVIS_API_PORT", "8000"))
    cors_origins: list = field(default_factory=lambda: ["*"])


@dataclass(frozen=True)
class AssistantSettings:
    """Configurações de comportamento e personalidade da IA."""

    nome: str = os.getenv("JARVIS_NOME", "Jarvis")
    idioma: str = os.getenv("JARVIS_IDIOMA", "pt")
    intent_confidence_threshold: float = 0.55
    max_context_turns: int = 12


@dataclass(frozen=True)
class LoggingSettings:
    """Configurações do sistema de logs."""

    log_dir: Path = BASE_DIR / "backend" / "logs"
    log_file: str = "jarvis.log"
    level: str = os.getenv("JARVIS_LOG_LEVEL", "INFO")


@dataclass(frozen=True)
class Settings:
    """Agrega todas as configurações da aplicação."""

    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    api: ApiSettings = field(default_factory=ApiSettings)
    assistant: AssistantSettings = field(default_factory=AssistantSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)


# Instância única (padrão Singleton simplificado via módulo Python).
settings = Settings()
