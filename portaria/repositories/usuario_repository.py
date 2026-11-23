import sqlite3

from portaria.database.connection import Database
from portaria.exceptions import DuplicadoError
from portaria.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    @staticmethod
    def _montar(row: sqlite3.Row) -> Usuario:
        return Usuario(
            id=row["id"],
            username=row["username"],
            nome=row["nome"],
            senha_hash=row["senha_hash"],
            salt=row["salt"],
        )

    def buscar_por_username(self, username: str) -> Usuario | None:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM usuarios WHERE username = ?", (username,)
            ).fetchone()
        return None if row is None else self._montar(row)

    def inserir(self, username: str, nome: str, senha_hash: str, salt: str) -> int:
        try:
            with self._db.connect() as conn:
                cursor = conn.execute(
                    "INSERT INTO usuarios (username, senha_hash, salt, nome) VALUES (?, ?, ?, ?)",
                    (username, senha_hash, salt, nome),
                )
                return int(cursor.lastrowid or 0)
        except sqlite3.IntegrityError as exc:
            raise DuplicadoError(f"O usuário '{username}' já existe.") from exc
