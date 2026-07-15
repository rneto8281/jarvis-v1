"""Rotas de controle do serviço de reconhecimento de voz e da detecção
de palmas."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.bootstrap import obter_clap_detector, obter_voice_service
from backend.voice.clap_detector import ClapDetector
from backend.voice.voice_service import VoiceService

router = APIRouter(prefix="/api/voice", tags=["voice"])


class VoiceStatusSaida(BaseModel):
    """Estado atual do serviço de voz e da detecção de palmas."""

    ativo: bool
    disponivel: bool
    ultima_transcricao: str | None
    ultimo_erro: str | None
    palmas_ativo: bool
    palmas_disponivel: bool


def _montar_status(voice: VoiceService, palmas: ClapDetector) -> VoiceStatusSaida:
    return VoiceStatusSaida(
        ativo=voice.status.ativo,
        disponivel=voice.status.disponivel,
        ultima_transcricao=voice.status.ultima_transcricao,
        ultimo_erro=voice.status.ultimo_erro,
        palmas_ativo=palmas.ativo,
        palmas_disponivel=palmas.disponivel,
    )


@router.post("/start", response_model=VoiceStatusSaida)
def iniciar_voz(
    voice: VoiceService = Depends(obter_voice_service),
    palmas: ClapDetector = Depends(obter_clap_detector),
) -> VoiceStatusSaida:
    """Inicia a escuta contínua por voz (a detecção de palmas roda
    independentemente, controlada por `/palmas/start`)."""

    voice.iniciar()
    return _montar_status(voice, palmas)


@router.post("/stop", response_model=VoiceStatusSaida)
def parar_voz(
    voice: VoiceService = Depends(obter_voice_service),
    palmas: ClapDetector = Depends(obter_clap_detector),
) -> VoiceStatusSaida:
    """Interrompe a escuta contínua por voz."""

    voice.parar()
    return _montar_status(voice, palmas)


@router.get("/status", response_model=VoiceStatusSaida)
def status_voz(
    voice: VoiceService = Depends(obter_voice_service),
    palmas: ClapDetector = Depends(obter_clap_detector),
) -> VoiceStatusSaida:
    """Retorna o estado atual do serviço de voz e da detecção de palmas."""

    return _montar_status(voice, palmas)


@router.post("/palmas/start", response_model=VoiceStatusSaida)
def iniciar_palmas(
    voice: VoiceService = Depends(obter_voice_service),
    palmas: ClapDetector = Depends(obter_clap_detector),
) -> VoiceStatusSaida:
    """Inicia o monitoramento de palmas em background (funciona mesmo
    com a escuta de voz contínua desligada)."""

    palmas.iniciar()
    return _montar_status(voice, palmas)


@router.post("/palmas/stop", response_model=VoiceStatusSaida)
def parar_palmas(
    voice: VoiceService = Depends(obter_voice_service),
    palmas: ClapDetector = Depends(obter_clap_detector),
) -> VoiceStatusSaida:
    """Interrompe o monitoramento de palmas."""

    palmas.parar()
    return _montar_status(voice, palmas)
