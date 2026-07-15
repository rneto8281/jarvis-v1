"""
Sistema de logs centralizado do JarvisAI.

Fornece uma factory de loggers configurados de forma consistente em
toda a aplicação, evitando duplicação de configuração de handlers e
formatação (princípio DRY).
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from backend.config.settings import settings


def get_logger(name: str) -> logging.Logger:
    """Cria (ou reutiliza) um logger configurado para o módulo informado.

    Args:
        name: Nome do módulo solicitante, normalmente ``__name__``.

    Returns:
        Uma instância de ``logging.Logger`` pronta para uso, com saída
        simultânea em console e em arquivo rotativo.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        # Evita adicionar handlers duplicados quando o logger já existe.
        return logger

    logger.setLevel(settings.logging.level)

    settings.logging.log_dir.mkdir(parents=True, exist_ok=True)
    log_path = settings.logging.log_dir / settings.logging.log_file

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_path, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
