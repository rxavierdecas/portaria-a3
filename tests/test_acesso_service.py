from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from portaria.exceptions import AcessoError, DuplicadoError, NaoEncontradoError, ValidacaoError
from portaria.models import Situacao
from tests.conftest import CPF_VALIDO_2, Ambiente, dados_cadastro


def test_impede_segunda_entrada_sem_saida(amb: Ambiente) -> None:
    pessoa = amb.pessoas.cadastrar(dados_cadastro())
    assert pessoa.id is not None
    with pytest.raises(AcessoError):
        amb.acesso.registrar_entrada(pessoa.id)


def test_ciclo_saida_e_nova_entrada(amb: Ambiente) -> None:
    pessoa = amb.pessoas.cadastrar(dados_cadastro())
    assert pessoa.id is not None

    amb.relogio.agora = datetime(2026, 11, 16, 12, 30, 45, 999)
    saida = amb.acesso.registrar_saida(pessoa.id)
    assert saida.saida == datetime(2026, 11, 16, 12, 30, 45)
    assert amb.acesso.listar_controle()[0].situacao is Situacao.SAIU

    with pytest.raises(AcessoError):
        amb.acesso.registrar_saida(pessoa.id)

    amb.relogio.agora = datetime(2026, 11, 16, 14, 0)
    amb.acesso.registrar_entrada(pessoa.id)
    registro = amb.acesso.listar_controle()[0]
    assert registro.situacao is Situacao.DENTRO
    assert registro.movimentacao is not None
    assert registro.movimentacao.entrada == datetime(2026, 11, 16, 14, 0)


def test_pessoa_inexistente(amb: Ambiente) -> None:
    with pytest.raises(NaoEncontradoError):
        amb.acesso.registrar_entrada(999)


def test_busca_e_filtro(amb: Ambiente) -> None:
    maria = amb.pessoas.cadastrar(dados_cadastro())
    amb.pessoas.cadastrar(dados_cadastro(nome="João Pereira", cpf=CPF_VALIDO_2))
    assert maria.id is not None
    amb.acesso.registrar_saida(maria.id)

    assert [r.pessoa.nome for r in amb.acesso.listar_controle(busca="joão")] == ["João Pereira"]
    assert [r.pessoa.nome for r in amb.acesso.listar_controle(busca="529.982")] == ["Maria Silva"]
    assert [r.pessoa.nome for r in amb.acesso.listar_controle(filtro="Saiu")] == ["Maria Silva"]
    assert [r.pessoa.nome for r in amb.acesso.listar_controle(filtro="Dentro")] == ["João Pereira"]

    resumo = amb.acesso.resumo()
    assert (resumo.pessoas_dentro, resumo.entradas_hoje, resumo.total_cadastrado) == (1, 2, 2)


def test_relatorio_e_csv(amb: Ambiente, tmp_path: Path) -> None:
    pessoa = amb.pessoas.cadastrar(dados_cadastro())
    assert pessoa.id is not None
    amb.relogio.agora = datetime(2026, 11, 16, 9, 15)
    amb.acesso.registrar_saida(pessoa.id)

    inicio, fim = date(2026, 11, 14), date(2026, 11, 16)
    df = amb.relatorios.movimentacoes_periodo(inicio, fim)
    assert len(df) == 1
    assert df.iloc[0]["Permanência (min)"] == 60

    por_dia = amb.relatorios.entradas_por_dia(df, inicio, fim)
    assert por_dia.tolist() == [0, 0, 1]
    assert amb.relatorios.entradas_por_tipo(df).to_dict() == {"Visitante": 1}

    caminho = tmp_path / "relatorio.csv"
    amb.relatorios.exportar_csv(df, caminho)
    linhas = caminho.read_text(encoding="utf-8-sig").splitlines()
    assert linhas[1] == "001;Maria Silva;529.982.247-25;Visitante;16/11/2026 08:15;16/11/2026 09:15;60"

    with pytest.raises(ValidacaoError):
        amb.relatorios.movimentacoes_periodo(fim, inicio)
    vazio = amb.relatorios.movimentacoes_periodo(inicio - timedelta(days=30), inicio)
    assert vazio.empty


def test_veiculos(amb: Ambiente) -> None:
    pessoa = amb.pessoas.cadastrar(dados_cadastro())
    veiculo = amb.veiculos.cadastrar(pessoa.id, "bra-2e19", "Gol", "Prata")
    assert veiculo.placa == "BRA2E19"
    with pytest.raises(DuplicadoError):
        amb.veiculos.cadastrar(pessoa.id, "BRA2E19", "Uno", "Branco")
    with pytest.raises(ValidacaoError):
        amb.veiculos.cadastrar(None, "ABC1234", "Uno", "Branco")
    with pytest.raises(ValidacaoError):
        amb.veiculos.cadastrar(pessoa.id, "XX123", "Uno", "Branco")
    [listado] = amb.veiculos.listar()
    assert listado.pessoa_nome == "Maria Silva"
    assert veiculo.id is not None
    amb.veiculos.excluir(veiculo.id)
    assert amb.veiculos.listar() == []


def test_ocorrencias(amb: Ambiente) -> None:
    with pytest.raises(ValidacaoError):
        amb.ocorrencias.registrar("Outros", "curta", usuario_id=1)
    amb.ocorrencias.registrar("Objeto esquecido", "Guarda-chuva deixado na recepção", usuario_id=1)
    [ocorrencia] = amb.ocorrencias.listar()
    assert ocorrencia.registrado_por_nome == "Administrador"
    assert ocorrencia.pessoa_nome == ""
