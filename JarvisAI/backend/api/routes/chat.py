"""Rotas relacionadas à conversa com o Jarvis."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.schemas import MensagemEntrada, RespostaSaida
from backend.bootstrap import obter_jarvis_engine
from backend.core.jarvis_engine import JarvisEngine

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=RespostaSaida)
def enviar_mensagem(
    payload: MensagemEntrada,
    engine: JarvisEngine = Depends(obter_jarvis_engine),
) -> RespostaSaida:
    """Recebe uma mensagem do usuário e retorna a resposta do Jarvis."""

    resultado = engine.processar_mensagem(payload.mensagem)

    return RespostaSaida(
        resposta=resultado.resposta,
        intent=resultado.intent,
        confianca=resultado.confianca,
    )


@router.get("/historico")
def obter_historico(
    limite: int = 20,
    engine: JarvisEngine = Depends(obter_jarvis_engine),
) -> list[dict]:
    """Retorna o histórico recente de conversas (memória de longo prazo)."""

    return engine.memory.historico_recente(limite)
