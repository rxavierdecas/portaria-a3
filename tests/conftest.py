from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pytest

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
    DadosCadastro,
    OcorrenciaService,
    PessoaService,
    RelatorioService,
    VeiculoService,
)

CPF_VALIDO = "529.982.247-25"
CPF_VALIDO_2 = "111.444.777-35"


@dataclass
class RelogioFalso:
    """Relógio controlável para testes determinísticos."""

    agora: datetime = field(default_factory=lambda: datetime(2026, 11, 16, 10, 0))

    def __call__(self) -> datetime:
        return self.agora


@dataclass
class Ambiente:
    db: Database
    relogio: RelogioFalso
    auth: AuthService
    pessoas: PessoaService
    acesso: AcessoService
    relatorios: RelatorioService
    veiculos: VeiculoService
    ocorrencias: OcorrenciaService


@pytest.fixture
def amb(tmp_path: Path) -> Ambiente:
    db = Database(tmp_path / "teste.db")
    inicializar_banco(db)
    relogio = RelogioFalso()
    pessoas_repo = PessoaRepository(db)
    mov_repo = MovimentacaoRepository(db)
    return Ambiente(
        db=db,
        relogio=relogio,
        auth=AuthService(UsuarioRepository(db)),
        pessoas=PessoaService(pessoas_repo, relogio),
        acesso=AcessoService(mov_repo, pessoas_repo, relogio),
        relatorios=RelatorioService(mov_repo),
        veiculos=VeiculoService(VeiculoRepository(db), pessoas_repo),
        ocorrencias=OcorrenciaService(OcorrenciaRepository(db), relogio),
    )


def dados_cadastro(**alteracoes: str) -> DadosCadastro:
    base = {
        "nome": "Maria Silva",
        "cpf": CPF_VALIDO,
        "telefone": "(31) 98888-7777",
        "empresa": "ACME",
        "tipo_acesso": "Visitante",
        "data_entrada": "16/11/2026",
        "horario_entrada": "08:15",
        "motivo": "Reunião comercial",
    }
    base.update(alteracoes)
    return DadosCadastro(**base)
