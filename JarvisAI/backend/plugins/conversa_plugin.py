"""Plugin de conversação social: saudações e cortesias básicas."""

from __future__ import annotations

import random

from backend.core.intent_engine import IntentDefinition
from backend.memory.memory_manager import MemoryManager
from backend.plugins.base_plugin import BasePlugin, PluginContext


class ConversaPlugin(BasePlugin):
    """Trata saudações e small talk para tornar a interação mais natural."""

    nome = "conversa"
    descricao = "Responde saudações e cortesias (oi, obrigado, tudo bem)."

    _SAUDACOES = [
        "Olá! Como posso ajudar?",
        "Oi! Em que posso ser útil hoje?",
        "Estou aqui. O que você precisa?",
    ]

    def __init__(self, memory: MemoryManager) -> None:
        self._memory = memory

    def intents_suportadas(self) -> list[IntentDefinition]:
        return [
            IntentDefinition(
                nome="saudacao",
                frases_exemplo=["oi", "ola", "e ai", "bom dia", "boa tarde", "boa noite"],
                palavras_chave=["oi", "ola", "bom dia", "boa tarde", "boa noite"],
            ),
            IntentDefinition(
                nome="agradecimento",
                frases_exemplo=["obrigado", "obrigada", "valeu", "muito obrigado"],
                palavras_chave=["obrigad", "valeu"],
            ),
        ]

    def executar(self, contexto: PluginContext) -> str:
        texto = contexto.texto_original.lower()

        if any(p in texto for p in ("obrigad", "valeu")):
            return "Disponha! Estou aqui se precisar de mais alguma coisa."

        nome = self._memory.obter_perfil().nome
        prefixo = f"{nome}, " if nome and nome != "usuario" else ""
        return prefixo + random.choice(self._SAUDACOES)
