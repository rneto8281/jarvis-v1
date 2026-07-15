"""
Serviço de voz do JarvisAI: orquestra o ciclo escuta → intenção → fala.

Roda em uma thread própria (fila/loop contínuo), para não bloquear a
API HTTP nem a interface web. Reaproveita exatamente o mesmo
``JarvisEngine`` usado pelo chat de texto — ou seja, qualquer comando
que já funciona por texto passa a funcionar por voz automaticamente,
sem duplicar nenhuma lógica de intents.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

from backend.core.event_bus import event_bus
from backend.core.jarvis_engine import JarvisEngine
from backend.utils.logger import get_logger
from backend.voice.voice_recognizer import VoiceRecognizer
from backend.voice.voice_synthesizer import VoiceSynthesizer

logger = get_logger(__name__)


@dataclass
class VoiceStatus:
    """Estado atual do serviço de voz, exposto para a API/UI."""

    ativo: bool = False
    disponivel: bool = False
    ultima_transcricao: str | None = None
    ultimo_erro: str | None = None
    historico: list[str] = field(default_factory=list)


class VoiceService:
    """Gerencia o ciclo de vida da escuta contínua por voz.

    Implementa um padrão simples de "worker thread controlável": o
    loop de escuta roda em background e pode ser iniciado/parado a
    qualquer momento via API, sem reiniciar a aplicação.
    """

    def __init__(
        self,
        jarvis_engine: JarvisEngine,
        recognizer: VoiceRecognizer | None = None,
        synthesizer: VoiceSynthesizer | None = None,
        falar_respostas: bool = True,
    ) -> None:
        self._engine = jarvis_engine
        self._recognizer = recognizer or VoiceRecognizer()
        self._synthesizer = synthesizer or VoiceSynthesizer()
        self._falar_respostas = falar_respostas

        self._thread: threading.Thread | None = None
        self._parar = threading.Event()

        self._status = VoiceStatus(
            disponivel=self._recognizer.disponivel,
        )

    @property
    def status(self) -> VoiceStatus:
        """Retorna uma cópia do estado atual do serviço de voz."""

        return self._status

    def iniciar(self) -> bool:
        """Inicia a escuta contínua em uma thread de background.

        Returns:
            ``True`` se a escuta foi iniciada, ``False`` se as
            dependências de voz não estiverem instaladas ou se o
            serviço já estiver em execução.
        """

        if not self._recognizer.disponivel:
            self._status.ultimo_erro = "Dependências de voz não instaladas (speech_recognition/pyaudio)."
            return False

        if self._thread is not None and self._thread.is_alive():
            return True

        self._parar.clear()
        self._thread = threading.Thread(target=self._loop_escuta, daemon=True)
        self._thread.start()
        self._status.ativo = True

        event_bus.publicar("voz_iniciada")
        logger.info("Serviço de voz iniciado.")
        return True

    def parar(self) -> None:
        """Interrompe a escuta contínua (a thread atual finaliza sozinha
        assim que terminar o ciclo de escuta em andamento)."""

        self._parar.set()
        self._status.ativo = False
        event_bus.publicar("voz_parada")
        logger.info("Serviço de voz parado.")

    def _loop_escuta(self) -> None:
        """Loop principal: escuta uma frase, processa e fala a resposta,
        repetindo até que ``parar()`` seja chamado.

        Publica eventos granulares de estado (``voz_fase``) em cada
        etapa, permitindo que a interface sincronize as animações do
        núcleo central com o que está acontecendo de fato — escutando,
        processando ou falando — em vez de assumir um único estado
        genérico de "ativo"."""

        self._recognizer.calibrar_ruido_ambiente()

        while not self._parar.is_set():
            event_bus.publicar("voz_fase", fase="escutando")
            resultado = self._recognizer.escutar_uma_frase()

            if not resultado.sucesso:
                self._status.ultimo_erro = resultado.erro
                event_bus.publicar("voz_fase", fase="ociosa")
                time.sleep(0.3)
                continue

            texto = resultado.texto or ""
            self._status.ultima_transcricao = texto
            self._status.historico.append(texto)
            self._status.historico = self._status.historico[-20:]

            event_bus.publicar("voz_transcrita", texto=texto)
            event_bus.publicar("voz_fase", fase="processando")

            resposta = self._engine.processar_mensagem(texto)

            if self._falar_respostas:
                event_bus.publicar("voz_fase", fase="falando")
                self._synthesizer.falar(resposta.resposta)

            event_bus.publicar("voz_fase", fase="ociosa")
