from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Ocorrencia:
    data_hora: datetime
    tipo: str
    descricao: str
    registrado_por: int
    pessoa_id: int | None = None
    id: int | None = None
    pessoa_nome: str = ""
    registrado_por_nome: str = ""
