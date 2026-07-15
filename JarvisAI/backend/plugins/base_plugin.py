"""
Contrato base para plugins do JarvisAI (padrão Plugin/Strategy).

Todo plugin deve herdar de :class:`BasePlugin` e implementar seus
métodos abstratos. Isso garante que o ``PluginManager`` possa carregar
e executar qualquer plugin de forma uniforme, sem conhecer detalhes
internos de cada um (princípio da inversão de dependência - SOLID).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.intent_engine import IntentDefinition


class PluginContext:
    """Objeto de contexto passado a cada execução de plugin.

    Encapsula tudo que um plugin pode precisar para responder,
    evitando que cada plugin receba uma lista longa e instável de
    parâmetros posicionais.
    """

    def __init__(
        self,
        texto_original: str,
        entidade: str | None,
        ultimo_topico: str | None,
        usuario: str = "usuario",
    ) -> None:
        self.texto_original = texto_original
        self.entidade = entidade
        self.ultimo_topico = ultimo_topico
        self.usuario = usuario


class BasePlugin(ABC):
    """Classe base abstrata que todo plugin do JarvisAI deve estender."""

    #: Nome único do plugin, usado em logs e no registro do gerenciador.
    nome: str = "plugin_base"

    #: Descrição curta exibida na ajuda/documentação automática.
    descricao: str = "Plugin não documentado."

    @abstractmethod
    def intents_suportadas(self) -> list[IntentDefinition]:
        """Retorna as definições de intenção que este plugin sabe tratar."""

        raise NotImplementedError

    @abstractmethod
    def executar(self, contexto: PluginContext) -> str:
        """Executa a ação do plugin e retorna a resposta textual da IA.

        Args:
            contexto: Dados da requisição atual (entidade, tópico, etc).

        Returns:
            Texto de resposta a ser enviado ao usuário.
        """

        raise NotImplementedError
