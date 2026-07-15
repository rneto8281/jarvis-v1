"""
Detector de palmas do JarvisAI.

Monitora o microfone continuamente em uma thread de background,
procurando por dois picos de volume (palmas) em uma janela curta de
tempo. Ao detectar o padrão, dispara exatamente a mesma rotina do
comando de voz "papai chegou" via ``JarvisEngine.disparar_intent``.

Implementado com PCM bruto via PyAudio (mesma dependência já usada
pelo reconhecimento de voz), evitando bibliotecas extras de DSP.
"""

from __future__ import annotations

import audioop
import threading
import time
from dataclasses import dataclass

from backend.core.jarvis_engine import JarvisEngine
from backend.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pyaudio

    _PYAUDIO_DISPONIVEL = True
except ImportError:  # pragma: no cover - dependência opcional
    _PYAUDIO_DISPONIVEL = False


@dataclass
class ConfiguracaoPalmas:
    """Parâmetros ajustáveis da detecção de palmas."""

    limiar_volume: int = 3200  # amplitude RMS mínima para contar como "pico"
    janela_entre_palmas_seg: float = 1.2  # tempo máximo entre a 1ª e a 2ª palma
    intervalo_minimo_entre_picos_seg: float = 0.15  # evita contar o mesmo som 2x
    taxa_amostragem: int = 16000
    tamanho_bloco: int = 1024


class ClapDetector:
    """Escuta o microfone e dispara a rotina especial ao detectar duas
    palmas consecutivas."""

    def __init__(
        self,
        jarvis_engine: JarvisEngine,
        config: ConfiguracaoPalmas | None = None,
    ) -> None:
        self._engine = jarvis_engine
        self._config = config or ConfiguracaoPalmas()
        self._disponivel = _PYAUDIO_DISPONIVEL

        self._thread: threading.Thread | None = None
        self._parar = threading.Event()
        self._ativo = False

    @property
    def disponivel(self) -> bool:
        """Indica se o PyAudio está instalado (pré-requisito do detector)."""

        return self._disponivel

    @property
    def ativo(self) -> bool:
        """Indica se a detecção de palmas está em execução."""

        return self._ativo

    def iniciar(self) -> bool:
        """Inicia o monitoramento contínuo do microfone em background."""

        if not self._disponivel:
            logger.warning("PyAudio não instalado; detecção de palmas indisponível.")
            return False

        if self._thread is not None and self._thread.is_alive():
            return True

        self._parar.clear()
        self._thread = threading.Thread(target=self._loop_monitoramento, daemon=True)
        self._thread.start()
        self._ativo = True
        logger.info("Detector de palmas iniciado.")
        return True

    def parar(self) -> None:
        """Interrompe o monitoramento do microfone."""

        self._parar.set()
        self._ativo = False
        logger.info("Detector de palmas parado.")

    def _loop_monitoramento(self) -> None:
        """Lê blocos de áudio continuamente e aplica a máquina de estados
        de detecção de dois picos consecutivos de volume."""

        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._config.taxa_amostragem,
            input=True,
            frames_per_buffer=self._config.tamanho_bloco,
        )

        primeira_palma_em: float | None = None
        ultimo_pico_em: float = 0.0

        try:
            while not self._parar.is_set():
                bloco = stream.read(self._config.tamanho_bloco, exception_on_overflow=False)
                volume = audioop.rms(bloco, 2)
                agora = time.monotonic()

                pico_detectado = (
                    volume >= self._config.limiar_volume
                    and (agora - ultimo_pico_em) >= self._config.intervalo_minimo_entre_picos_seg
                )

                if not pico_detectado:
                    continue

                ultimo_pico_em = agora

                if primeira_palma_em is None:
                    primeira_palma_em = agora
                    continue

                dentro_da_janela = (agora - primeira_palma_em) <= self._config.janela_entre_palmas_seg

                if dentro_da_janela:
                    logger.info("Duas palmas detectadas — disparando rotina 'papai chegou'.")
                    self._engine.disparar_intent("papai_chegou", texto_referencia="[duas palmas detectadas]")

                primeira_palma_em = None
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
