import sqlite3

from portaria.database.connection import Database
from portaria.exceptions import DuplicadoError
from portaria.models.veiculo import Veiculo


class VeiculoRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def inserir(self, veiculo: Veiculo) -> Veiculo:
        try:
            with self._db.connect() as conn:
                cursor = conn.execute(
                    "INSERT INTO veiculos (pessoa_id, placa, modelo, cor) VALUES (?, ?, ?, ?)",
                    (veiculo.pessoa_id, veiculo.placa, veiculo.modelo, veiculo.cor),
                )
        except sqlite3.IntegrityError as exc:
            raise DuplicadoError("Esta placa já está cadastrada.") from exc
        veiculo.id = cursor.lastrowid
        return veiculo

    def buscar_por_placa(self, placa: str) -> Veiculo | None:
        with self._db.connect() as conn:
            row = conn.execute(
                """
                SELECT v.*, p.nome AS pessoa_nome FROM veiculos v
                JOIN pessoas p ON p.id = v.pessoa_id WHERE v.placa = ?
                """,
                (placa,),
            ).fetchone()
        return None if row is None else self._montar(row)

    def listar(self) -> list[Veiculo]:
        with self._db.connect() as conn:
            rows = conn.execute(
                """
                SELECT v.*, p.nome AS pessoa_nome FROM veiculos v
                JOIN pessoas p ON p.id = v.pessoa_id ORDER BY v.id
                """
            ).fetchall()
        return [self._montar(row) for row in rows]

    def excluir(self, veiculo_id: int) -> bool:
        with self._db.connect() as conn:
            cursor = conn.execute("DELETE FROM veiculos WHERE id = ?", (veiculo_id,))
        return cursor.rowcount > 0

    @staticmethod
    def _montar(row: sqlite3.Row) -> Veiculo:
        return Veiculo(
            id=row["id"],
            pessoa_id=row["pessoa_id"],
            placa=row["placa"],
            modelo=row["modelo"],
            cor=row["cor"],
            pessoa_nome=row["pessoa_nome"],
        )
