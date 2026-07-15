"""Plugin de agenda/tarefas: permite lembrar compromissos e afazeres."""

from __future__ import annotations

from backend.core.intent_engine import IntentDefinition
from backend.memory.memory_manager import MemoryManager
from backend.plugins.base_plugin import BasePlugin, PluginContext


class TarefasPlugin(BasePlugin):
    """Adiciona e lista tarefas/lembretes persistidos na memória de
    longo prazo do usuário."""

    nome = "tarefas"
    descricao = "Adiciona e lista tarefas/lembretes do usuário."

    def __init__(self, memory: MemoryManager) -> None:
        self._memory = memory

    def intents_suportadas(self) -> list[IntentDefinition]:
        return [
            IntentDefinition(
                nome="adicionar_tarefa",
                frases_exemplo=[
                    "me lembre de",
                    "adicionar tarefa",
                    "criar lembrete",
                    "anote que preciso",
                    "nao deixa eu esquecer de",
                    "preciso lembrar de",
                    "coloca na minha lista",
                ],
                palavras_chave=[
                    "me lembre", "adicionar tarefa", "criar lembrete",
                    "nao deixa eu esquecer", "preciso lembrar", "minha lista",
                ],
            ),
            IntentDefinition(
                nome="listar_tarefas",
                frases_exemplo=["quais são minhas tarefas", "minha agenda", "listar tarefas"],
                palavras_chave=["minhas tarefas", "minha agenda", "listar tarefas"],
            ),
        ]

    def executar(self, contexto: PluginContext) -> str:
        texto = contexto.texto_original.lower()

        if "listar" in texto or "quais" in texto or "agenda" in texto:
            tarefas = self._memory.listar_tarefas()
            if not tarefas:
                return "Você não tem tarefas pendentes."

            linhas = [f"- {t['descricao']}" for t in tarefas]
            return "Suas tarefas pendentes:\n" + "\n".join(linhas)

        if not contexto.entidade:
            return "O que você gostaria que eu anotasse?"

        self._memory.adicionar_tarefa(contexto.entidade)
        return f"Anotado: '{contexto.entidade}'."
