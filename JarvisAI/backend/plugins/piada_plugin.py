"""Plugin de entretenimento: conta piadas."""

from __future__ import annotations

from backend.core.intent_engine import IntentDefinition
from backend.plugins.base_plugin import BasePlugin, PluginContext

try:
    import pyjokes

    _PYJOKES_DISPONIVEL = True
except ImportError:  # pragma: no cover - dependência opcional
    _PYJOKES_DISPONIVEL = False


class PiadaPlugin(BasePlugin):
    """Conta uma piada para descontrair a conversa."""

    nome = "piada"
    descricao = "Conta uma piada."

    def intents_suportadas(self) -> list[IntentDefinition]:
        return [
            IntentDefinition(
                nome="contar_piada",
                frases_exemplo=["conte uma piada", "me conta uma piada", "quero rir"],
                palavras_chave=["piada", "quero rir"],
            )
        ]

    def executar(self, contexto: PluginContext) -> str:
        if not _PYJOKES_DISPONIVEL:
            return "Meu módulo de piadas está offline no momento."

        return pyjokes.get_joke(language="en")
