"""
Esquemas (DTOs) de entrada e saída da API do JarvisAI.

Usar Pydantic garante validação automática de tipos e geração de
documentação OpenAPI, além de desacoplar o formato de rede da
implementação interna do backend.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MensagemEntrada(BaseModel):
    """Corpo da requisição de envio de mensagem ao Jarvis."""

    mensagem: str = Field(..., min_length=1, description="Texto enviado pelo usuário.")


class RespostaSaida(BaseModel):
    """Corpo da resposta retornada pelo Jarvis."""

    resposta: str
    intent: str
    confianca: float


class StatusSistemaSaida(BaseModel):
    """Corpo da resposta com métricas de hardware."""

    sistema_operacional: str
    cpu_percent: float
    ram_percent: float
    ram_usada_gb: float
    ram_total_gb: float
    disco_percent: float
    disco_usado_gb: float
    disco_total_gb: float
    rede_enviado_mb: float
    rede_recebido_mb: float
    bateria_percent: float | None
    bateria_carregando: bool | None


class TarefaSaida(BaseModel):
    """Representação de uma tarefa/lembrete."""

    id: int
    descricao: str
    concluida: int
    criado_em: str


class PluginInfo(BaseModel):
    """Metadados de um plugin carregado, para exibição na UI."""

    nome: str
    descricao: str
