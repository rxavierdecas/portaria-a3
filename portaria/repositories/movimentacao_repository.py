import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from portaria.database.connection import Database
from portaria.models.movimentacao import Movimentacao, RegistroAcesso
from portaria.models.pessoa import Pessoa
from portaria.repositories._datas import para_datetime, para_datetime_obrigatorio, para_texto
from portaria.repositories.pessoa_repository import PessoaRepository
from portaria.utils.validators import somente_digitos


@dataclass(slots=True)
class LinhaRelatorio:
    pessoa: Pessoa
    movimentacao: Movimentacao


class MovimentacaoRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    @staticmethod
    def _montar(row: sqlite3.Row) -> Movimentacao:
        return Movimentacao(
            id=row["mov_id"],
            pessoa_id=row["pessoa_id"],
            entrada=para_datetime_obrigatorio(row["entrada"]),
            saida=para_datetime(row["saida"]),
        )

    def buscar_aberta(self, pessoa_id: int) -> Movimentacao | None:
        """Movimentação sem saída registrada (pessoa está dentro)."""
        with self._db.connect() as conn:
            row = conn.execute(
                """
                SELECT id AS mov_id, pessoa_id, entrada, saida FROM movimentacoes
                WHERE pessoa_id = ? AND saida IS NULL
                ORDER BY entrada DESC LIMIT 1
                """,
                (pessoa_id,),
            ).fetchone()
        return None if row is None else self._montar(row)

    def inserir_entrada(self, pessoa_id: int, entrada: datetime) -> Movimentacao:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "INSERT INTO movimentacoes (pessoa_id, entrada) VALUES (?, ?)",
                (pessoa_id, para_texto(entrada)),
            )
        return Movimentacao(id=cursor.lastrowid, pessoa_id=pessoa_id, entrada=entrada)

    def registrar_saida(self, movimentacao_id: int, saida: datetime) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE movimentacoes SET saida = ? WHERE id = ?",
                (para_texto(saida), movimentacao_id),
            )

    def listar_controle(self, busca: str = "") -> list[RegistroAcesso]:
        """Cada pessoa com sua movimentação mais recente, filtrada por nome/CPF."""
        sql = """
            SELECT p.*, m.id AS mov_id, m.pessoa_id, m.entrada, m.saida
            FROM pessoas p
            LEFT JOIN movimentacoes m ON m.id = (
                SELECT id FROM movimentacoes
                WHERE pessoa_id = p.id
                ORDER BY entrada DESC, id DESC LIMIT 1
            )
        """
        parametros: list[str] = []
        busca = busca.strip()
        if busca:
            condicoes = ["p.nome LIKE ?"]
            parametros.append(f"%{busca}%")
            digitos = somente_digitos(busca)
            if digitos:
                condicoes.append("p.cpf LIKE ?")
                parametros.append(f"%{digitos}%")
            sql += " WHERE " + " OR ".join(condicoes)
        sql += " ORDER BY p.id"

        with self._db.connect() as conn:
            rows = conn.execute(sql, parametros).fetchall()

        registros: list[RegistroAcesso] = []
        for row in rows:
            movimentacao = None if row["mov_id"] is None else self._montar(row)
            registros.append(RegistroAcesso(PessoaRepository.montar(row), movimentacao))
        return registros

    def listar_periodo(self, inicio: date, fim: date) -> list[LinhaRelatorio]:
        """Movimentações cuja entrada ocorreu entre ``inicio`` e ``fim`` (inclusive)."""
        limite_inferior = datetime.combine(inicio, time.min)
        limite_superior = datetime.combine(fim + timedelta(days=1), time.min)
        with self._db.connect() as conn:
            rows = conn.execute(
                """
                SELECT p.*, m.id AS mov_id, m.pessoa_id, m.entrada, m.saida
                FROM movimentacoes m JOIN pessoas p ON p.id = m.pessoa_id
                WHERE m.entrada >= ? AND m.entrada < ?
                ORDER BY m.entrada
                """,
                (para_texto(limite_inferior), para_texto(limite_superior)),
            ).fetchall()
        return [LinhaRelatorio(PessoaRepository.montar(r), self._montar(r)) for r in rows]

    def contar_dentro(self) -> int:
        with self._db.connect() as conn:
            return int(
                conn.execute(
                    "SELECT COUNT(DISTINCT pessoa_id) FROM movimentacoes WHERE saida IS NULL"
                ).fetchone()[0]
            )

    def contar_entradas_no_dia(self, dia: date) -> int:
        return len(self.listar_periodo(dia, dia))
