from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from portaria import config
from portaria.exceptions import AcessoError, NaoEncontradoError
from portaria.models.movimentacao import Movimentacao, RegistroAcesso
from portaria.models.pessoa import Pessoa
from portaria.repositories.movimentacao_repository import MovimentacaoRepository
from portaria.repositories.pessoa_repository import PessoaRepository


@dataclass(slots=True, frozen=True)
class ResumoPortaria:
    pessoas_dentro: int
    entradas_hoje: int
    total_cadastrado: int


class AcessoService:
    """Regras de entrada e saída na portaria."""

    def __init__(
        self,
        movimentacoes: MovimentacaoRepository,
        pessoas: PessoaRepository,
        relogio: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._movimentacoes = movimentacoes
        self._pessoas = pessoas
        self._relogio = relogio

    def _agora(self) -> datetime:
        return self._relogio().replace(microsecond=0)

    def _obter_pessoa(self, pessoa_id: int) -> Pessoa:
        pessoa = self._pessoas.buscar_por_id(pessoa_id)
        if pessoa is None:
            raise NaoEncontradoError("Pessoa não encontrada.")
        return pessoa

    def registrar_entrada(self, pessoa_id: int) -> Movimentacao:
        pessoa = self._obter_pessoa(pessoa_id)
        if self._movimentacoes.buscar_aberta(pessoa_id) is not None:
            raise AcessoError(
                f"{pessoa.nome} já está dentro.\nRegistre a saída antes de uma nova entrada."
            )
        return self._movimentacoes.inserir_entrada(pessoa_id, self._agora())

    def registrar_saida(self, pessoa_id: int) -> Movimentacao:
        pessoa = self._obter_pessoa(pessoa_id)
        aberta = self._movimentacoes.buscar_aberta(pessoa_id)
        if aberta is None or aberta.id is None:
            raise AcessoError(f"{pessoa.nome} não possui entrada em aberto.")
        agora = self._agora()
        if agora < aberta.entrada:
            raise AcessoError("A saída não pode ser anterior ao horário de entrada.")
        self._movimentacoes.registrar_saida(aberta.id, agora)
        aberta.saida = agora
        return aberta

    def listar_controle(self, busca: str = "", filtro: str = config.FILTRO_TODOS) -> list[RegistroAcesso]:
        registros = self._movimentacoes.listar_controle(busca)
        if filtro == config.FILTRO_TODOS:
            return registros
        return [r for r in registros if r.situacao.value == filtro]

    def resumo(self) -> ResumoPortaria:
        return ResumoPortaria(
            pessoas_dentro=self._movimentacoes.contar_dentro(),
            entradas_hoje=self._movimentacoes.contar_entradas_no_dia(self._agora().date()),
            total_cadastrado=self._pessoas.contar(),
        )
