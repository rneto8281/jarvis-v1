"""
Síntese de voz (Text-to-Speech) do JarvisAI.

Encapsula ``pyttsx3`` (motor de TTS offline, multiplataforma) atrás de
uma interface própria, seguindo o mesmo princípio de isolamento de
dependência de terceiros usado em ``voice_recognizer.py``.
"""

from __future__ import annotations

from backend.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pyttsx3

    _PYTTSX3_DISPONIVEL = True
except ImportError:  # pragma: no cover - dependência opcional
    _PYTTSX3_DISPONIVEL = False


class VoiceSynthesizer:
    """Converte texto em fala usando o motor TTS offline do sistema.

    Ponto de extensão: para uma voz mais próxima da estética do
    J.A.R.V.I.S. dos filmes (o que o motor offline `pyttsx3` não
    consegue reproduzir fielmente), esta classe pode ser substituída
    por um adaptador equivalente que chame um serviço de TTS premium
    (ex.: ElevenLabs, Azure Neural TTS) — a interface pública
    (``falar(texto)``) permaneceria a mesma, mantendo o restante do
    sistema (voice_service, plugins) inalterado.
    """

    def __init__(self, velocidade: int = 175) -> None:
        self._disponivel = _PYTTSX3_DISPONIVEL

        if self._disponivel:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", velocidade)
            self._preferir_voz_grave()
        else:
            logger.warning("pyttsx3 não instalado. Síntese de voz operará em modo indisponível.")

    @property
    def disponivel(self) -> bool:
        """Indica se o motor de síntese de voz está disponível."""

        return self._disponivel

    def _preferir_voz_grave(self) -> None:
        """Tenta selecionar uma voz em português (ou, na ausência dela,
        uma voz masculina/grave em qualquer idioma disponível), buscando
        aproximar o timbre calmo e grave associado ao J.A.R.V.I.S.

        Isto é uma heurística sobre as vozes instaladas no sistema
        operacional — a qualidade final depende do que o Windows/Linux
        tiver disponível localmente."""

        try:
            vozes = self._engine.getProperty("voices")

            voz_pt = next(
                (v for v in vozes if "pt" in v.id.lower() or "brazil" in v.name.lower()), None
            )
            if voz_pt:
                self._engine.setProperty("voice", voz_pt.id)
                return

            voz_grave = next(
                (v for v in vozes if "male" in (getattr(v, "gender", "") or "").lower()
                 or "male" in v.name.lower()),
                None,
            )
            if voz_grave:
                self._engine.setProperty("voice", voz_grave.id)
        except Exception:
            logger.debug("Não foi possível listar vozes do sistema; usando padrão.")

    def falar(self, texto: str) -> None:
        """Sintetiza e reproduz o texto informado em áudio.

        Chamada bloqueante (roda até terminar de falar) — deve ser
        executada em uma thread separada do loop principal da API.
        """

        if not self._disponivel:
            logger.info("[TTS indisponível] %s", texto)
            return

        self._engine.say(texto)
        self._engine.runAndWait()
