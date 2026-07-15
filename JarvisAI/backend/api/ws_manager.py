"""
Gerenciador de conexões WebSocket do JarvisAI.

Substitui o polling do frontend por push em tempo real: qualquer
evento relevante do sistema (mensagens, transcrições de voz, status)
é transmitido instantaneamente a todos os clientes conectados.

Importante: o motor do Jarvis e o serviço de voz publicam eventos de
forma síncrona, e o serviço de voz roda em uma *thread* separada do
loop de eventos do asyncio usado pelo FastAPI. Por isso, o broadcast
a partir de threads de background precisa ser agendado no loop
principal via ``asyncio.run_coroutine_threadsafe`` — ver `routes/ws.py`.
"""

from __future__ import annotations

import asyncio
import json

from fastapi import WebSocket

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Mantém a lista de clientes WebSocket ativos e transmite eventos."""

    def __init__(self) -> None:
        self._conexoes: list[WebSocket] = []
        self.loop_principal: asyncio.AbstractEventLoop | None = None

    async def conectar(self, websocket: WebSocket) -> None:
        """Aceita e registra uma nova conexão WebSocket."""

        await websocket.accept()
        self._conexoes.append(websocket)
        logger.info("Cliente WebSocket conectado (%d ativos).", len(self._conexoes))

    def desconectar(self, websocket: WebSocket) -> None:
        """Remove uma conexão encerrada da lista de ativos."""

        if websocket in self._conexoes:
            self._conexoes.remove(websocket)
        logger.info("Cliente WebSocket desconectado (%d ativos).", len(self._conexoes))

    async def transmitir(self, evento: dict) -> None:
        """Envia um evento (dict serializável em JSON) a todos os clientes
        conectados. Conexões mortas são removidas silenciosamente."""

        payload = json.dumps(evento, ensure_ascii=False)
        mortas: list[WebSocket] = []

        for conexao in self._conexoes:
            try:
                await conexao.send_text(payload)
            except Exception:  # noqa: BLE001 - conexão pode ter caído
                mortas.append(conexao)

        for conexao in mortas:
            self.desconectar(conexao)

    def transmitir_thread_safe(self, evento: dict) -> None:
        """Agenda uma transmissão a partir de uma thread que não é a do
        loop principal do asyncio (ex.: a thread de escuta de voz).

        Se o loop principal ainda não foi capturado (app não iniciado
        totalmente) ou não há conexões, a chamada é ignorada com segurança.
        """

        if self.loop_principal is None:
            return

        asyncio.run_coroutine_threadsafe(self.transmitir(evento), self.loop_principal)


# Instância compartilhada da aplicação.
connection_manager = ConnectionManager()
