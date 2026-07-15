"""Plugin de data e hora."""

from __future__ import annotations

import datetime

from backend.core.intent_engine import IntentDefinition
from backend.plugins.base_plugin import BasePlugin, PluginContext


class DateTimePlugin(BasePlugin):
    """Responde perguntas sobre a hora e a data atuais."""

    nome = "datetime"
    descricao = "Informa a hora e a data atuais."

    def intents_suportadas(self) -> list[IntentDefinition]:
        return [
            IntentDefinition(
                nome="consultar_hora",
                frases_exemplo=["que horas são", "me diz a hora", "horas agora"],
                palavras_chave=["que horas", "hora atual", "horas sao"],
            ),
            IntentDefinition(
                nome="consultar_data",
                frases_exemplo=["que dia é hoje", "qual a data de hoje"],
                palavras_chave=["que dia", "data de hoje", "qual data"],
            ),
        ]

    def executar(self, contexto: PluginContext) -> str:
        agora = datetime.datetime.now()

        if "hora" in contexto.texto_original.lower():
            return f"Agora são {agora.strftime('%H:%M:%S')}."
        return f"Hoje é {agora.strftime('%d/%m/%Y')}."
