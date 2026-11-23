import sqlite3

from portaria.database.connection import Database
from portaria.models.ocorrencia import Ocorrencia
from portaria.repositories._datas import para_datetime_obrigatorio, para_texto


class OcorrenciaRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def inserir(self, ocorrencia: Ocorrencia) -> Ocorrencia:
        with self._db.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO ocorrencias (data_hora, tipo, descricao, pessoa_id, registrado_por)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    para_texto(ocorrencia.data_hora),
                    ocorrencia.tipo,
                    ocorrencia.descricao,
                    ocorrencia.pessoa_id,
                    ocorrencia.registrado_por,
                ),
            )
        ocorrencia.id = cursor.lastrowid
        return ocorrencia

    def listar(self) -> list[Ocorrencia]:
        with self._db.connect() as conn:
            rows = conn.execute(
                """
                SELECT o.*, COALESCE(p.nome, '') AS pessoa_nome, u.nome AS usuario_nome
                FROM ocorrencias o
                LEFT JOIN pessoas p ON p.id = o.pessoa_id
                JOIN usuarios u ON u.id = o.registrado_por
                ORDER BY o.data_hora DESC, o.id DESC
                """
            ).fetchall()
        return [self._montar(row) for row in rows]

    @staticmethod
    def _montar(row: sqlite3.Row) -> Ocorrencia:
        return Ocorrencia(
            id=row["id"],
            data_hora=para_datetime_obrigatorio(row["data_hora"]),
            tipo=row["tipo"],
            descricao=row["descricao"],
            pessoa_id=row["pessoa_id"],
            registrado_por=row["registrado_por"],
            pessoa_nome=row["pessoa_nome"],
            registrado_por_nome=row["usuario_nome"],
        )
