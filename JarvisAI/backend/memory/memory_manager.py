"""
Gerenciador de memória de longo prazo do JarvisAI.

Fornece uma API de alto nível sobre a camada de banco de dados para
persistir e recuperar: dados do usuário, preferências, histórico de
conversas e tarefas. É a "memória" que sobrevive entre reinicializações
da aplicação, sendo carregada automaticamente na inicialização.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.database.db import Database


@dataclass
class PerfilUsuario:
    """Representa os dados conhecidos sobre o usuário."""

    id: int
    nome: str
    idioma: str
    cidade: str | None


class MemoryManager:
    """Interface de alto nível para leitura/escrita da memória persistente."""

    def __init__(self, database: Database | None = None) -> None:
        self._db = database or Database()
        self._usuario_atual_id = self._garantir_usuario_padrao()

    def _garantir_usuario_padrao(self) -> int:
        """Garante que exista ao menos um usuário registrado, criando um
        perfil padrão na primeira execução (carregamento automático)."""

        with self._db.conexao() as conn:
            linha = conn.execute("SELECT id FROM usuario LIMIT 1").fetchone()
            if linha:
                return linha["id"]

            cursor = conn.execute(
                "INSERT INTO usuario (nome, idioma) VALUES (?, ?)",
                ("usuario", "pt"),
            )
            return cursor.lastrowid

    def obter_perfil(self) -> PerfilUsuario:
        """Retorna o perfil do usuário atual."""

        with self._db.conexao() as conn:
            linha = conn.execute(
                "SELECT id, nome, idioma, cidade FROM usuario WHERE id = ?",
                (self._usuario_atual_id,),
            ).fetchone()

        return PerfilUsuario(
            id=linha["id"], nome=linha["nome"], idioma=linha["idioma"], cidade=linha["cidade"]
        )

    def atualizar_nome(self, novo_nome: str) -> None:
        """Atualiza o nome do usuário armazenado."""

        with self._db.conexao() as conn:
            conn.execute(
                "UPDATE usuario SET nome = ? WHERE id = ?",
                (novo_nome, self._usuario_atual_id),
            )

    def definir_preferencia(self, chave: str, valor: str) -> None:
        """Salva (ou atualiza) uma preferência do usuário."""

        with self._db.conexao() as conn:
            conn.execute(
                """
                INSERT INTO preferencia (usuario_id, chave, valor)
                VALUES (?, ?, ?)
                ON CONFLICT(usuario_id, chave) DO UPDATE SET valor = excluded.valor
                """,
                (self._usuario_atual_id, chave, valor),
            )

    def obter_preferencia(self, chave: str) -> str | None:
        """Recupera o valor de uma preferência, se existir."""

        with self._db.conexao() as conn:
            linha = conn.execute(
                "SELECT valor FROM preferencia WHERE usuario_id = ? AND chave = ?",
                (self._usuario_atual_id, chave),
            ).fetchone()

        return linha["valor"] if linha else None

    def registrar_conversa(self, mensagem_usuario: str, intent: str, resposta: str) -> None:
        """Persiste um turno de conversa no histórico de longo prazo."""

        with self._db.conexao() as conn:
            conn.execute(
                """
                INSERT INTO conversa (usuario_id, mensagem_usuario, intent, resposta)
                VALUES (?, ?, ?, ?)
                """,
                (self._usuario_atual_id, mensagem_usuario, intent, resposta),
            )

    def historico_recente(self, limite: int = 20) -> list[dict]:
        """Retorna as últimas ``limite`` interações registradas."""

        with self._db.conexao() as conn:
            linhas = conn.execute(
                """
                SELECT mensagem_usuario, intent, resposta, criado_em
                FROM conversa
                WHERE usuario_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (self._usuario_atual_id, limite),
            ).fetchall()

        return [dict(linha) for linha in linhas]

    def adicionar_tarefa(self, descricao: str) -> int:
        """Adiciona uma nova tarefa/lembrete à agenda do usuário."""

        with self._db.conexao() as conn:
            cursor = conn.execute(
                "INSERT INTO tarefa (usuario_id, descricao) VALUES (?, ?)",
                (self._usuario_atual_id, descricao),
            )
            return cursor.lastrowid

    def listar_tarefas(self, apenas_pendentes: bool = True) -> list[dict]:
        """Lista as tarefas cadastradas, opcionalmente só as pendentes."""

        query = "SELECT id, descricao, concluida, criado_em FROM tarefa WHERE usuario_id = ?"
        params: list = [self._usuario_atual_id]

        if apenas_pendentes:
            query += " AND concluida = 0"

        query += " ORDER BY criado_em DESC"

        with self._db.conexao() as conn:
            linhas = conn.execute(query, params).fetchall()

        return [dict(linha) for linha in linhas]
