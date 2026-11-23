"""Criação das tabelas e dados iniciais."""

from portaria import config
from portaria.database.connection import Database
from portaria.utils.security import hash_senha

_SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT NOT NULL UNIQUE,
    senha_hash  TEXT NOT NULL,
    salt        TEXT NOT NULL,
    nome        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pessoas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT NOT NULL,
    cpf          TEXT NOT NULL UNIQUE,
    telefone     TEXT NOT NULL,
    empresa      TEXT NOT NULL,
    tipo_acesso  TEXT NOT NULL,
    motivo       TEXT NOT NULL,
    criado_em    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    pessoa_id  INTEGER NOT NULL REFERENCES pessoas(id) ON DELETE CASCADE,
    entrada    TEXT NOT NULL,
    saida      TEXT
);
CREATE INDEX IF NOT EXISTS idx_mov_pessoa ON movimentacoes(pessoa_id);

CREATE TABLE IF NOT EXISTS veiculos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    pessoa_id  INTEGER NOT NULL REFERENCES pessoas(id) ON DELETE CASCADE,
    placa      TEXT NOT NULL UNIQUE,
    modelo     TEXT NOT NULL,
    cor        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ocorrencias (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    data_hora       TEXT NOT NULL,
    tipo            TEXT NOT NULL,
    descricao       TEXT NOT NULL,
    pessoa_id       INTEGER REFERENCES pessoas(id) ON DELETE SET NULL,
    registrado_por  INTEGER NOT NULL REFERENCES usuarios(id)
);
"""


def inicializar_banco(db: Database) -> None:
    """Cria as tabelas (se necessário) e o usuário administrador padrão."""
    with db.connect() as conn:
        conn.executescript(_SCHEMA)
        total = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        if total == 0:
            senha_hash, salt = hash_senha(config.ADMIN_SENHA)
            conn.execute(
                "INSERT INTO usuarios (username, senha_hash, salt, nome) VALUES (?, ?, ?, ?)",
                (config.ADMIN_USERNAME, senha_hash, salt, config.ADMIN_NOME),
            )
