from dataclasses import dataclass


@dataclass(slots=True)
class Usuario:
    id: int
    username: str
    nome: str
    senha_hash: str
    salt: str
