"""
Construtor de respostas do JarvisAI.

Centraliza mensagens padrão (saudação, incompreensão, ajuda) para que
o tom da IA seja consistente e fácil de ajustar em um único lugar.
"""

from __future__ import annotations

from backend.config.settings import settings


class ResponseBuilder:
    """Fábrica de respostas textuais padronizadas da IA."""

    def saudacao(self) -> str:
        return f"{settings.assistant.nome} iniciado. Como posso ajudar?"

    def nao_compreendido(self, texto_original: str) -> str:
        return (
            "Não tenho certeza do que você quis dizer com "
            f"\"{texto_original}\". Pode reformular?"
        )

    def erro_interno(self) -> str:
        return "Encontrei um problema ao processar seu pedido. Já registrei o ocorrido nos logs."

    def despedida(self) -> str:
        return "Até logo!"
