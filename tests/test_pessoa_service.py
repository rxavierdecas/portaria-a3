from datetime import datetime

import pytest

from portaria.exceptions import DuplicadoError, ValidacaoError
from portaria.models import Situacao
from tests.conftest import CPF_VALIDO_2, Ambiente, dados_cadastro


def test_cadastro_valido_gera_codigo_e_primeira_entrada(amb: Ambiente) -> None:
    pessoa = amb.pessoas.cadastrar(dados_cadastro())
    assert pessoa.id == 1
    assert pessoa.codigo == "001"
    assert pessoa.cpf == "52998224725"
    assert pessoa.telefone == "31988887777"

    [registro] = amb.acesso.listar_controle()
    assert registro.situacao is Situacao.DENTRO
    assert registro.movimentacao is not None
    assert registro.movimentacao.entrada == datetime(2026, 11, 16, 8, 15)


def test_campos_obrigatorios(amb: Ambiente) -> None:
    with pytest.raises(ValidacaoError) as erro:
        amb.pessoas.cadastrar(dados_cadastro(nome="", empresa=" "))
    assert "Nome completo" in str(erro.value)
    assert "Empresa" in str(erro.value)


@pytest.mark.parametrize(
    "campo",
    [
        {"cpf": "111.111.111-11"},
        {"telefone": "(31) 1234"},
        {"tipo_acesso": "Selecione..."},
        {"data_entrada": "31/02/2026"},
        {"horario_entrada": "25:00"},
        {"nome": "Maria"},
    ],
)
def test_dados_invalidos(amb: Ambiente, campo: dict[str, str]) -> None:
    with pytest.raises(ValidacaoError):
        amb.pessoas.cadastrar(dados_cadastro(**campo))


def test_entrada_no_futuro(amb: Ambiente) -> None:
    with pytest.raises(ValidacaoError):
        amb.pessoas.cadastrar(dados_cadastro(horario_entrada="11:00"))


def test_cpf_duplicado(amb: Ambiente) -> None:
    amb.pessoas.cadastrar(dados_cadastro())
    with pytest.raises(DuplicadoError):
        amb.pessoas.cadastrar(dados_cadastro(nome="Outra Pessoa", cpf="52998224725"))
    amb.pessoas.cadastrar(dados_cadastro(nome="Outra Pessoa", cpf=CPF_VALIDO_2))
    assert len(amb.pessoas.listar()) == 2
