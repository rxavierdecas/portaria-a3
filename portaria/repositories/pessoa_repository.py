import sqlite3
from datetime import datetime

from portaria.database.connection import Database
from portaria.exceptions import DuplicadoError
from portaria.models.pessoa import Pessoa
from portaria.repositories._datas import para_datetime, para_texto


class PessoaRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    @staticmethod
    def montar(row: sqlite3.Row) -> Pessoa:
        return Pessoa(
            id=row["id"],
            nome=row["nome"],
            cpf=row["cpf"],
            telefone=row["telefone"],
            empresa=row["empresa"],
            tipo_acesso=row["tipo_acesso"],
            motivo=row["motivo"],
            criado_em=para_datetime(row["criado_em"]),
        )

    def inserir_com_entrada(self, pessoa: Pessoa, entrada: datetime) -> Pessoa:
        """Grava a pessoa e sua primeira entrada numa única transação."""
        criado_em = pessoa.criado_em or datetime.now()
        try:
            with self._db.connect() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO pessoas (nome, cpf, telefone, empresa, tipo_acesso, motivo, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        pessoa.nome,
                        pessoa.cpf,
                        pessoa.telefone,
                        pessoa.empresa,
                        pessoa.tipo_acesso,
                        pessoa.motivo,
                        para_texto(criado_em),
                    ),
                )
                pessoa_id = int(cursor.lastrowid or 0)
                conn.execute(
                    "INSERT INTO movimentacoes (pessoa_id, entrada) VALUES (?, ?)",
                    (pessoa_id, para_texto(entrada)),
                )
        except sqlite3.IntegrityError as exc:
            raise DuplicadoError("Já existe uma pessoa cadastrada com este CPF.") from exc
        pessoa.id = pessoa_id
        pessoa.criado_em = criado_em
        return pessoa

    def buscar_por_id(self, pessoa_id: int) -> Pessoa | None:
        with self._db.connect() as conn:
            row = conn.execute("SELECT * FROM pessoas WHERE id = ?", (pessoa_id,)).fetchone()
        return None if row is None else self.montar(row)

    def buscar_por_cpf(self, cpf: str) -> Pessoa | None:
        with self._db.connect() as conn:
            row = conn.execute("SELECT * FROM pessoas WHERE cpf = ?", (cpf,)).fetchone()
        return None if row is None else self.montar(row)

    def listar(self) -> list[Pessoa]:
        with self._db.connect() as conn:
            rows = conn.execute("SELECT * FROM pessoas ORDER BY nome").fetchall()
        return [self.montar(row) for row in rows]

    def contar(self) -> int:
        with self._db.connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM pessoas").fetchone()[0])
