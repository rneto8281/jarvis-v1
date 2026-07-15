"""
Endpoint WebSocket do JarvisAI.

Este é o canal único de comunicação em tempo real entre backend e
frontend: mensagens de chat (texto ou voz), transcrições, mudanças de
estado da escuta e métricas de sistema trafegam todas aqui, eliminando
o polling usado na versão anterior.

Protocolo (mensagens JSON):

Cliente → Servidor:
    {"tipo": "chat", "mensagem": "..."}

Servidor → Cliente:
    {"tipo": "mensagem_usuario", "texto": "..."}
    {"tipo": "resposta", "texto": "...", "intent": "..."}
    {"tipo": "voz_transcrita", "texto": "..."}
    {"tipo": "voz_estado", "ativo": true|false}
    {"tipo": "status_sistema", ...métricas...}
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from backend.api.ws_manager import connection_manager
from backend.bootstrap import obter_auth_service, obter_jarvis_engine, obter_voice_service
from backend.core.event_bus import event_bus
from backend.core.jarvis_engine import JarvisEngine
from backend.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


def _acionar_gatilhos_especiais(texto: str, intent: str) -> None:
    """Reage a intenções que exigem um comportamento além de apenas
    responder: no caso de "papai_chegou", dispara um efeito visual no
    HUD e liga o modo de conversa contínua automaticamente, exatamente
    como pedido — a rotina é idêntica não importa se o gatilho veio de
    texto, voz ou duas palmas, já que todos passam por este mesmo evento.
    """

    if intent != "papai_chegou":
        return

    connection_manager.transmitir_thread_safe({"tipo": "efeito_visual", "efeito": "papai_chegou"})

    voice = obter_voice_service()
    if voice.status.disponivel and not voice.status.ativo:
        voice.iniciar()


def _registrar_pontes_de_evento() -> None:
    """Liga o barramento de eventos síncrono (usado pelo motor central e
    pelo serviço de voz) ao broadcast assíncrono do WebSocket.

    Registrado uma única vez, na importação deste módulo — o
    ``EventBus`` é um singleton compartilhado por toda a aplicação.
    """

    event_bus.assinar(
        "mensagem_recebida",
        lambda texto: connection_manager.transmitir_thread_safe(
            {"tipo": "mensagem_usuario", "texto": texto}
        ),
    )
    event_bus.assinar(
        "resposta_gerada",
        lambda texto, intent: connection_manager.transmitir_thread_safe(
            {"tipo": "resposta", "texto": texto, "intent": intent}
        ),
    )
    event_bus.assinar("resposta_gerada", _acionar_gatilhos_especiais)
    event_bus.assinar(
        "voz_transcrita",
        lambda texto: connection_manager.transmitir_thread_safe(
            {"tipo": "voz_transcrita", "texto": texto}
        ),
    )
    event_bus.assinar(
        "voz_iniciada",
        lambda: connection_manager.transmitir_thread_safe({"tipo": "voz_estado", "ativo": True}),
    )
    event_bus.assinar(
        "voz_parada",
        lambda: connection_manager.transmitir_thread_safe({"tipo": "voz_estado", "ativo": False}),
    )
    event_bus.assinar(
        "voz_fase",
        lambda fase: connection_manager.transmitir_thread_safe({"tipo": "voz_fase", "fase": fase}),
    )


_registrar_pontes_de_evento()


@router.websocket("/ws")
async def canal_tempo_real(websocket: WebSocket, token: str = Query(default="")) -> None:
    """Canal WebSocket principal. Exige um token de sessão válido (obtido
    via ``POST /api/auth/login``) como query param ``?token=``."""

    auth = obter_auth_service()

    if not auth.validar_token(token):
        await websocket.close(code=4401)
        return

    # Captura o loop de eventos em execução para que threads de
    # background (voz, futura detecção de palmas) possam transmitir
    # eventos com segurança via `run_coroutine_threadsafe`.
    connection_manager.loop_principal = asyncio.get_running_loop()

    await connection_manager.conectar(websocket)
    engine: JarvisEngine = obter_jarvis_engine()

    try:
        while True:
            bruto = await websocket.receive_json()

            if bruto.get("tipo") == "chat":
                mensagem = str(bruto.get("mensagem", ""))
                # Processamento roda em thread separada para não bloquear
                # o loop de eventos (chamadas de plugin podem ser lentas,
                # ex.: abrir navegador, consultar Wikipedia).
                await asyncio.to_thread(engine.processar_mensagem, mensagem)

    except WebSocketDisconnect:
        connection_manager.desconectar(websocket)
