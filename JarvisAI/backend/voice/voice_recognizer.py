"""
Reconhecimento de fala (Speech-to-Text) do JarvisAI.

Encapsula a biblioteca ``SpeechRecognition`` atrás de uma interface
própria (Adapter), para que o restante do sistema nunca dependa
diretamente da API de terceiros — se no futuro trocarmos por outro
motor de reconhecimento (ex.: um modelo local via Vosk/Whisper), só
esta classe precisa mudar.

Dependência opcional: se ``speech_recognition`` ou ``pyaudio`` não
estiverem instalados, o serviço reporta indisponibilidade de forma
controlada, sem derrubar o restante da aplicação.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import speech_recognition as sr

    _SR_DISPONIVEL = True
except ImportError:  # pragma: no cover - dependência opcional
    _SR_DISPONIVEL = False


@dataclass
class ResultadoEscuta:
    """Resultado de uma tentativa de captura e transcrição de áudio."""

    sucesso: bool
    texto: str | None = None
    erro: str | None = None


class VoiceRecognizer:
    """Captura áudio do microfone padrão e transcreve para texto em pt-BR."""

    def __init__(self, idioma: str = "pt-BR") -> None:
        self._idioma = idioma
        self._disponivel = _SR_DISPONIVEL

        if self._disponivel:
            self._reconhecedor = sr.Recognizer()
            self._reconhecedor.pause_threshold = 0.8
        else:
            logger.warning(
                "speech_recognition/pyaudio não instalados. "
                "Reconhecimento de voz operará em modo indisponível."
            )

    @property
    def disponivel(self) -> bool:
        """Indica se as dependências de reconhecimento estão instaladas."""

        return self._disponivel

    def calibrar_ruido_ambiente(self, duracao: float = 1.0) -> None:
        """Ajusta o limiar de energia do microfone ao ruído ambiente atual."""

        if not self._disponivel:
            return

        with sr.Microphone() as fonte:
            self._reconhecedor.adjust_for_ambient_noise(fonte, duration=duracao)

    def escutar_uma_frase(self, timeout: float = 5.0, limite_frase: float = 8.0) -> ResultadoEscuta:
        """Escuta o microfone até detectar uma frase completa (ou expirar).

        Args:
            timeout: Segundos de silêncio inicial tolerados antes de desistir.
            limite_frase: Duração máxima de uma única frase capturada.

        Returns:
            Um :class:`ResultadoEscuta` com o texto transcrito, ou o
            motivo da falha (silêncio, fala incompreensível, etc).
        """

        if not self._disponivel:
            return ResultadoEscuta(
                sucesso=False,
                erro="Módulo de reconhecimento de voz não está instalado.",
            )

        try:
            with sr.Microphone() as fonte:
                audio = self._reconhecedor.listen(
                    fonte, timeout=timeout, phrase_time_limit=limite_frase
                )
        except sr.WaitTimeoutError:
            return ResultadoEscuta(sucesso=False, erro="Nenhuma fala detectada.")

        try:
            texto = self._reconhecedor.recognize_google(audio, language=self._idioma)
            return ResultadoEscuta(sucesso=True, texto=texto)
        except sr.UnknownValueError:
            return ResultadoEscuta(sucesso=False, erro="Não entendi o que foi dito.")
        except sr.RequestError as exc:
            logger.warning("Falha no serviço de reconhecimento de voz: %s", exc)
            return ResultadoEscuta(
                sucesso=False, erro="Serviço de reconhecimento indisponível (verifique a internet)."
            )
