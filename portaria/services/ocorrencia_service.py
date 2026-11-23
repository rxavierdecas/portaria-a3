from collections.abc import Callable
from datetime import datetime

from portaria import config
from portaria.exceptions import ValidacaoError
from portaria.models.ocorrencia import Ocorrencia
from portaria.repositories.ocorrencia_repository import OcorrenciaRepository

_MIN_DESCRICAO = 10


class OcorrenciaService:
    """Desafio extra: registro de ocorrências na portaria."""

    def __init__(
        self,
        ocorrencias: OcorrenciaRepository,
        relogio: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._ocorrencias = ocorrencias
        self._relogio = relogio

    def registrar(
        self,
        tipo: str,
        descricao: str,
        usuario_id: int,
        pessoa_id: int | None = None,
    ) -> Ocorrencia:
        if tipo not in config.TIPOS_OCORRENCIA:
            raise ValidacaoError("Selecione o tipo da ocorrência.")
        descricao = descricao.strip()
        if len(descricao) < _MIN_DESCRICAO:
            raise ValidacaoError(f"Descreva a ocorrência (mínimo de {_MIN_DESCRICAO} caracteres).")
        return self._ocorrencias.inserir(
            Ocorrencia(
                data_hora=self._relogio().replace(microsecond=0),
                tipo=tipo,
                descricao=descricao,
                registrado_por=usuario_id,
                pessoa_id=pessoa_id,
            )
        )

    def listar(self) -> list[Ocorrencia]:
        return self._ocorrencias.listar()
