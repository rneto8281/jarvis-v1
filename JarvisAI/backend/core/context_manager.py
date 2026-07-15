"""
Gerenciador de contexto de conversa (memória de curto prazo).

Mantém o histórico recente da conversa em memória volátil, permitindo
que a IA entenda referências implícitas ("e amanhã?", "repita isso")
sem precisar consultar o banco de dados a cada turno.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

from backend.config.settings import settings


@dataclass
class Turno:
    """Representa um único turno de conversa (usuário + resposta)."""

    mensagem_usuario: str
    intent: str
    resposta: str
    entidade: str | None
    timestamp: datetime = field(default_factory=datetime.now)


class ContextManager:
    """Mantém o estado da conversa atual em uma janela deslizante.

    Usa uma ``deque`` com tamanho máximo definido em configuração,
    descartando automaticamente os turnos mais antigos (política FIFO)
    para manter o consumo de memória previsível.
    """

    def __init__(self, max_turnos: int | None = None) -> None:
        self._max_turnos = max_turnos or settings.assistant.max_context_turns
        self._historico: deque[Turno] = deque(maxlen=self._max_turnos)
        self._ultimo_topico: str | None = None

    def registrar_turno(
        self, mensagem_usuario: str, intent: str, resposta: str, entidade: str | None
    ) -> None:
        """Adiciona um novo turno ao histórico de contexto."""

        turno = Turno(
            mensagem_usuario=mensagem_usuario,
            intent=intent,
            resposta=resposta,
            entidade=entidade,
        )
        self._historico.append(turno)

        if entidade:
            self._ultimo_topico = entidade

    @property
    def ultimo_topico(self) -> str | None:
        """Retorna o último assunto/entidade mencionado, útil para
        resolver referências implícitas em perguntas de acompanhamento."""

        return self._ultimo_topico

    @property
    def historico(self) -> list[Turno]:
        """Retorna o histórico de turnos em ordem cronológica."""

        return list(self._historico)

    def ultimo_intent(self) -> str | None:
        """Retorna o nome da última intenção reconhecida, se existir."""

        if not self._historico:
            return None
        return self._historico[-1].intent

    def limpar(self) -> None:
        """Reinicia o contexto da conversa atual."""

        self._historico.clear()
        self._ultimo_topico = None
