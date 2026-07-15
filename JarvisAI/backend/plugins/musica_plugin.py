"""Plugin de música: toca uma faixa no YouTube via pywhatkit."""

from __future__ import annotations

from backend.core.intent_engine import IntentDefinition
from backend.plugins.base_plugin import BasePlugin, PluginContext
from backend.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pywhatkit

    _PYWHATKIT_DISPONIVEL = True
except ImportError:  # pragma: no cover - dependência opcional
    _PYWHATKIT_DISPONIVEL = False


class MusicaPlugin(BasePlugin):
    """Reproduz uma música no YouTube a partir do nome informado."""

    nome = "musica"
    descricao = "Toca uma música no YouTube."

    def intents_suportadas(self) -> list[IntentDefinition]:
        return [
            IntentDefinition(
                nome="tocar_musica",
                frases_exemplo=["toque uma musica", "quero ouvir", "tocar musica"],
                palavras_chave=["tocar musica", "toque a musica", "quero ouvir", "toque", "tocar"],
            )
        ]

    def executar(self, contexto: PluginContext) -> str:
        musica = contexto.entidade

        if not musica:
            return "Qual música você gostaria de ouvir?"

        if not _PYWHATKIT_DISPONIVEL:
            return f"Eu tocaria '{musica}', mas o módulo de reprodução não está instalado."

        try:
            pywhatkit.playonyt(musica)
            return f"Tocando '{musica}' no YouTube."
        except Exception:
            logger.warning("Falha ao tocar a música '%s'", musica)
            return f"Não consegui tocar '{musica}' agora."
