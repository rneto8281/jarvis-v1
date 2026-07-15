"""
Sistema de eventos (padrão Observer) do JarvisAI.

Permite que módulos distintos (voz, interface, plugins, monitoramento)
se comuniquem de forma desacoplada: quem produz um evento não precisa
conhecer quem o consome.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from backend.utils.logger import get_logger

logger = get_logger(__name__)

Callback = Callable[..., None]


class EventBus:
    """Barramento de eventos simples em memória, síncrono.

    Implementa o padrão Observer: componentes se inscrevem em nomes de
    evento (`str`) e são notificados quando o evento é publicado.
    """

    def __init__(self) -> None:
        self._assinantes: dict[str, list[Callback]] = defaultdict(list)

    def assinar(self, evento: str, callback: Callback) -> None:
        """Registra um callback para ser chamado quando ``evento`` ocorrer."""

        self._assinantes[evento].append(callback)

    def publicar(self, evento: str, **dados) -> None:
        """Notifica todos os assinantes de um evento, passando ``dados``
        como argumentos nomeados.

        Falhas em um assinante são isoladas e logadas, para que um
        listener com erro não derrube o restante do sistema.
        """

        for callback in self._assinantes.get(evento, []):
            try:
                callback(**dados)
            except Exception:  # noqa: BLE001 - isolamento intencional
                logger.exception("Falha ao processar evento '%s'", evento)


# Instância compartilhada da aplicação (Singleton simplificado).
event_bus = EventBus()
