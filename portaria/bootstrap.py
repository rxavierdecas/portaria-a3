"""Montagem das dependências (banco → repositórios → serviços)."""

from dataclasses import dataclass
from pathlib import Path

from portaria import config
from portaria.database import Database, inicializar_banco
from portaria.repositories import (
    MovimentacaoRepository,
    OcorrenciaRepository,
    PessoaRepository,
    UsuarioRepository,
    VeiculoRepository,
)
from portaria.services import (
    AcessoService,
    AuthService,
    OcorrenciaService,
    PessoaService,
    RelatorioService,
    VeiculoService,
)


@dataclass(slots=True, frozen=True)
class Servicos:
    auth: AuthService
    pessoas: PessoaService
    acesso: AcessoService
    relatorios: RelatorioService
    veiculos: VeiculoService
    ocorrencias: OcorrenciaService


def criar_servicos(db_path: Path = config.DB_PATH) -> Servicos:
    db = Database(db_path)
    inicializar_banco(db)

    usuarios = UsuarioRepository(db)
    pessoas = PessoaRepository(db)
    movimentacoes = MovimentacaoRepository(db)

    return Servicos(
        auth=AuthService(usuarios),
        pessoas=PessoaService(pessoas),
        acesso=AcessoService(movimentacoes, pessoas),
        relatorios=RelatorioService(movimentacoes),
        veiculos=VeiculoService(VeiculoRepository(db), pessoas),
        ocorrencias=OcorrenciaService(OcorrenciaRepository(db)),
    )
