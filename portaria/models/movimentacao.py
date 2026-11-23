from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from portaria.models.pessoa import Pessoa


class Situacao(StrEnum):
    DENTRO = "Dentro"
    SAIU = "Saiu"


@dataclass(slots=True)
class Movimentacao:
    pessoa_id: int
    entrada: datetime
    saida: datetime | None = None
    id: int | None = None

    @property
    def aberta(self) -> bool:
        return self.saida is None

    @property
    def situacao(self) -> Situacao:
        return Situacao.DENTRO if self.aberta else Situacao.SAIU


@dataclass(slots=True)
class RegistroAcesso:
    """Linha da tela de Controle: a pessoa e sua movimentação mais recente."""

    pessoa: Pessoa
    movimentacao: Movimentacao | None

    @property
    def situacao(self) -> Situacao:
        if self.movimentacao is None:
            return Situacao.SAIU
        return self.movimentacao.situacao
